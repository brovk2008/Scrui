"""
Canvas, WebGL & WASM Extraction Module
Handles pixel capture, WebGL API hooking, and WASM decompilation.
"""
from __future__ import annotations

import asyncio
import base64
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


async def capture_canvas_elements(cdp) -> list[dict]:
    """
    Detect all canvas elements and capture their visual state.
    Returns list of {nodeId, selector, screenshot_b64, width, height}
    """
    result = await cdp.send("Runtime.evaluate", {
        "expression": """
            Array.from(document.querySelectorAll('canvas')).map((c, i) => ({
                index: i,
                id: c.id,
                className: c.className,
                width: c.width,
                height: c.height,
                selector: c.id ? '#' + c.id : 'canvas:nth-of-type(' + (i+1) + ')',
                isVisible: c.offsetWidth > 0 && c.offsetHeight > 0,
            }))
        """,
        "returnByValue": True,
    })
    canvases = result.get("result", {}).get("value", []) or []

    captured = []
    for canvas in canvases:
        if not canvas.get("isVisible"):
            continue
        node_id = await _get_node_id_by_selector(cdp, canvas["selector"])
        if node_id:
            screenshot = await _screenshot_canvas(cdp, node_id)
            captured.append({
                **canvas,
                "nodeId": node_id,
                "screenshot_b64": screenshot,
            })

    return captured


async def _get_node_id_by_selector(cdp, selector: str) -> Optional[int]:
    try:
        doc = await cdp.send("DOM.getDocument", {"depth": 0})
        result = await cdp.send("DOM.querySelector", {
            "nodeId": doc["root"]["nodeId"],
            "selector": selector,
        })
        return result.get("nodeId")
    except Exception:
        return None


async def _screenshot_canvas(cdp, node_id: int) -> Optional[str]:
    """Capture a canvas element as a base64 PNG."""
    try:
        model = await cdp.send("DOM.getBoxModel", {"nodeId": node_id})
        content = model["model"]["content"]
        x, y = content[0], content[1]
        w = content[2] - content[0]
        h = content[5] - content[1]
        if w <= 0 or h <= 0:
            return None

        screenshot = await cdp.send("Page.captureScreenshot", {
            "format": "png",
            "clip": {"x": x, "y": y, "width": w, "height": h, "scale": 1},
        })
        return screenshot.get("data")
    except Exception as e:
        logger.debug(f"Canvas screenshot failed: {e}")
        return None


async def extract_webgl_data(cdp) -> dict:
    """
    Retrieve WebGL API capture data that was hooked during page load.
    Requires the webgl-hook.js pre-load script to have been injected.
    """
    try:
        result = await cdp.send("Runtime.evaluate", {
            "expression": """
                (() => {
                    const cap = window.__webgl_capture || [];
                    return {
                        callCount: cap.length,
                        drawCalls: cap.filter(c => c.method && c.method.startsWith('draw')).length,
                        calls: cap.slice(0, 100), // First 100 calls
                    };
                })()
            """,
            "returnByValue": True,
            "timeout": 5000,
        })
        return result.get("result", {}).get("value", {}) or {}
    except Exception as e:
        logger.debug(f"WebGL data retrieval failed: {e}")
        return {}


async def decompile_wasm(wasm_bytes: bytes, config, output_dir: Path) -> dict:
    """
    WASM decompilation pipeline:
    1. wasm2wat → WAT text format
    2. Optionally: LLM-assisted semantic recovery (WaDec approach)
    """
    result = {"wasm_size": len(wasm_bytes), "wat": None, "js_shim": None, "error": None}

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        wasm_file = tmp_path / "module.wasm"
        wasm_file.write_bytes(wasm_bytes)

        # Step 1: wasm2wat
        wat_file = tmp_path / "module.wat"
        try:
            proc = subprocess.run(
                ["wasm2wat", str(wasm_file), "-o", str(wat_file)],
                capture_output=True, timeout=60
            )
            if proc.returncode == 0:
                wat_text = wat_file.read_text(encoding="utf-8")
                result["wat"] = wat_text
                logger.debug(f"wasm2wat succeeded: {len(wat_text)} chars")
            else:
                result["error"] = proc.stderr.decode()[:500]
        except FileNotFoundError:
            result["error"] = "wasm2wat not found — install wabt toolkit"
        except subprocess.TimeoutExpired:
            result["error"] = "wasm2wat timed out"

        # Step 2: LLM semantic recovery if WAT was generated
        if result["wat"] and config.huggingface.api_key:
            result["js_shim"] = await _llm_wat_to_js(result["wat"], config)

        # Save output
        output_dir.mkdir(parents=True, exist_ok=True)
        if result["wat"]:
            (output_dir / "module.wat").write_text(result["wat"], encoding="utf-8")
        if result["js_shim"]:
            (output_dir / "module_shim.js").write_text(result["js_shim"], encoding="utf-8")

    return result


async def _llm_wat_to_js(wat_text: str, config) -> str:
    """
    WaDec approach: annotate WAT with stack state, then LLM decompiles to JS.
    """
    # Take first 4000 chars of WAT for LLM
    chunk = wat_text[:4000]
    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(token=config.huggingface.api_key)
        prompt = f"""You are a WebAssembly decompiler. Convert this WAT (WebAssembly Text) to readable JavaScript.
Name functions and variables semantically based on their operations.
Output only valid JavaScript. No explanations.

WAT:
{chunk}

JavaScript:"""
        response = client.text_generation(
            prompt,
            model=config.huggingface.code_model,
            max_new_tokens=2048,
            temperature=0.1,
        )
        return response.strip()
    except Exception as e:
        logger.warning(f"WASM LLM decompilation failed: {e}")
        return f"// WASM decompilation failed: {e}\n// Raw WAT length: {len(wat_text)} chars"
