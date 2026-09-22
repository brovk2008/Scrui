"""
Layer 3 — JavaScript Deobfuscation Pipeline
Stages: webcrack debundling → AST unminification → HuggingFace LLM renaming.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Known library structural signatures to strip
KNOWN_LIB_PATTERNS = [
    "react", "react-dom", "vue", "angular", "lodash", "jquery",
    "moment", "axios", "redux", "rxjs", "d3", "three", "gsap",
]


async def deobfuscate_bundle(bundle_js: str, config, output_dir: Path) -> dict:
    """
    Full deobfuscation pipeline:
    1. Write bundle to temp file
    2. webcrack debundling
    3. HF LLM semantic renaming
    Returns: dict with readable_code, modules_dir, summary
    """
    result = {
        "original_size": len(bundle_js),
        "modules": [],
        "readable_code": bundle_js,  # fallback
        "error": None,
    }

    if not config.extraction.js_deobfuscate:
        return result

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        bundle_path = tmp_path / "bundle.js"
        bundle_path.write_text(bundle_js, encoding="utf-8")

        # Stage 1: webcrack debundling
        modules_dir = tmp_path / "modules"
        modules_dir.mkdir()
        debundled = await _run_webcrack(bundle_path, modules_dir)

        if not debundled:
            logger.debug("webcrack failed or not installed — using raw bundle")
            readable = bundle_js
        else:
            # Stage 2: LLM renaming per module
            module_files = list(modules_dir.glob("*.js"))
            readable_parts = []
            for module_file in module_files[:10]:  # cap at 10 modules
                module_code = module_file.read_text(encoding="utf-8", errors="replace")
                renamed = await _llm_rename(module_code, config)
                readable_parts.append(f"// Module: {module_file.name}\n{renamed}")
                result["modules"].append({
                    "name": module_file.name,
                    "size": len(module_code),
                })
            readable = "\n\n".join(readable_parts) if readable_parts else bundle_js

        result["readable_code"] = readable
        result["readable_size"] = len(readable)

        # Save to output dir
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "deobfuscated.js").write_text(readable, encoding="utf-8")

    return result


async def _run_webcrack(bundle_path: Path, output_dir: Path) -> bool:
    """Run webcrack to debundle webpack/Vite/Browserify bundles."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "npx", "--yes", "webcrack",
            str(bundle_path),
            "--output", str(output_dir),
            "--quiet",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
        if proc.returncode == 0:
            logger.debug("webcrack succeeded")
            return True
        else:
            logger.debug(f"webcrack returned {proc.returncode}: {stderr.decode()[:200]}")
            return False
    except FileNotFoundError:
        logger.debug("webcrack/npx not found in PATH")
        return False
    except asyncio.TimeoutError:
        logger.warning("webcrack timed out")
        return False
    except Exception as e:
        logger.debug(f"webcrack error: {e}")
        return False


async def _llm_rename(code: str, config) -> str:
    """
    Use HuggingFace Inference API to rename minified identifiers semantically.
    Uses Qwen2.5-Coder-7B-Instruct by default.
    """
    if not config.extraction.js_deobfuscate:
        return code

    # Limit code size to ~6000 chars for API efficiency
    chunk = code[:6000]
    if len(chunk) < 100:
        return code

    try:
        from huggingface_hub import InferenceClient

        api_key = config.huggingface.api_key
        model = config.huggingface.code_model

        client = InferenceClient(token=api_key) if api_key else InferenceClient()

        prompt = f"""You are a JavaScript deobfuscation expert. Below is minified/obfuscated JavaScript.
Rename all single-letter and obfuscated variables to meaningful semantic names based on context.
Keep the logic identical. Output only valid JavaScript, no explanation.

```javascript
{chunk}
```

Renamed JavaScript:
```javascript"""

        response = client.text_generation(
            prompt,
            model=model,
            max_new_tokens=min(config.huggingface.max_new_tokens, 4096),
            temperature=0.1,
            stop=["```"],
        )
        renamed = response.strip()
        logger.debug(f"LLM renaming: {len(code)} → {len(renamed)} chars")
        return renamed if renamed else code

    except ImportError:
        logger.warning("huggingface_hub not installed — skipping LLM renaming")
        return code
    except Exception as e:
        logger.warning(f"LLM renaming failed: {e}")
        return code
