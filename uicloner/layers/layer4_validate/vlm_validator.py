"""
Layer 4 — VLM-Augmented Visual Validation
Uses HuggingFace Qwen2.5-VL for screenshot comparison and pixel diff for quantitative scoring.
"""
from __future__ import annotations

import base64
import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def validate_clone_fidelity(
    original_screenshot: bytes,
    clone_screenshot: bytes,
    config,
) -> dict:
    """
    Compare original and clone screenshots.
    Returns: {score, missing, style_diffs, layout_diffs, notes, diff_image_b64}
    """
    # Always run pixel diff
    pixel_result = pixel_diff_report(original_screenshot, clone_screenshot,
                                      threshold=config.validation.pixel_diff_threshold)

    vlm_result = {}
    if config.validation.run_vlm_check:
        vlm_result = await vlm_compare(original_screenshot, clone_screenshot, config)

    # Combine scores
    pixel_score = pixel_result.get("fidelity_percent", 0)
    vlm_score = vlm_result.get("score", pixel_score)  # fallback to pixel if no VLM

    combined_score = (pixel_score + vlm_score) / 2 if vlm_result else pixel_score

    return {
        "fidelity_score": round(combined_score, 2),
        "pixel_fidelity": pixel_score,
        "vlm_fidelity": vlm_score if vlm_result else None,
        "diff_pixels": pixel_result.get("diff_pixels", 0),
        "total_pixels": pixel_result.get("total_pixels", 0),
        "diff_image_b64": pixel_result.get("diff_image_b64"),
        "vlm_missing": vlm_result.get("missing", []),
        "vlm_style_diffs": vlm_result.get("style_diffs", []),
        "vlm_layout_diffs": vlm_result.get("layout_diffs", []),
        "vlm_notes": vlm_result.get("notes", ""),
        "passed": combined_score >= config.validation.fidelity_threshold_percent,
    }


def pixel_diff_report(original: bytes, clone: bytes, threshold: int = 5) -> dict:
    """
    Quantitative pixel-level fidelity measurement using Pillow.
    """
    try:
        from PIL import Image, ImageChops
        import numpy as np

        orig_img = Image.open(io.BytesIO(original)).convert("RGB")
        clone_img = Image.open(io.BytesIO(clone)).convert("RGB")

        # Normalize sizes
        if orig_img.size != clone_img.size:
            clone_img = clone_img.resize(orig_img.size, Image.LANCZOS)

        diff = ImageChops.difference(orig_img, clone_img)
        diff_array = np.array(diff)
        diff_pixels = int(np.sum(np.any(diff_array > threshold, axis=2)))
        total_pixels = orig_img.width * orig_img.height
        fidelity_pct = (1 - diff_pixels / total_pixels) * 100 if total_pixels > 0 else 0

        # Create diff visualization (amplified)
        diff_enhanced = Image.fromarray((diff_array * 10).clip(0, 255).astype('uint8'))
        buf = io.BytesIO()
        diff_enhanced.save(buf, format="PNG")
        diff_b64 = base64.b64encode(buf.getvalue()).decode()

        return {
            "fidelity_percent": round(fidelity_pct, 2),
            "diff_pixels": diff_pixels,
            "total_pixels": total_pixels,
            "diff_image_b64": diff_b64,
        }
    except ImportError:
        logger.warning("Pillow/numpy not installed — pixel diff unavailable")
        return {"fidelity_percent": 0.0, "diff_pixels": 0, "total_pixels": 0}
    except Exception as e:
        logger.warning(f"Pixel diff failed: {e}")
        return {"fidelity_percent": 0.0, "diff_pixels": 0, "total_pixels": 0}


async def vlm_compare(
    original: bytes,
    clone: bytes,
    config,
) -> dict:
    """
    Use HuggingFace Qwen2.5-VL to visually compare screenshots.
    """
    try:
        from huggingface_hub import InferenceClient

        orig_b64 = base64.b64encode(original).decode()
        clone_b64 = base64.b64encode(clone).decode()

        client = InferenceClient(token=config.huggingface.api_key)

        # Use vision-capable model
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{orig_b64}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{clone_b64}"}},
                    {"type": "text", "text": """Compare these two UI screenshots.
Image 1 = original. Image 2 = clone.
Respond ONLY with valid JSON matching this schema exactly:
{
  "score": <0-100 fidelity score>,
  "missing": ["<description of missing element>"],
  "style_diffs": ["<color/font/spacing difference>"],
  "layout_diffs": ["<layout/position difference>"],
  "notes": "<brief summary>"
}"""}
                ]
            }
        ]

        import json as _json
        response = client.chat_completion(
            messages=messages,
            model=config.huggingface.vlm_model,
            max_tokens=1024,
        )
        text = response.choices[0].message.content
        # Extract JSON from response
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return _json.loads(text[start:end])
        return {"score": 0, "notes": "JSON parse failed"}

    except ImportError:
        logger.warning("huggingface_hub not installed")
        return {}
    except Exception as e:
        logger.warning(f"VLM comparison failed: {e}")
        return {"score": 0, "notes": str(e)}
