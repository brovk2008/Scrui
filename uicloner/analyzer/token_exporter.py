"""
Scrui W3C DTCG & Figma Tokens Studio Exporter.
Converts extracted color ramps, font stacks, radii, line-heights, and box-shadows
into the official W3C Design Tokens Community Group (DTCG) specification and
Tokens Studio for Figma format.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


def export_dtcg_tokens(design_tokens: Any) -> Dict[str, Any]:
    """
    Format extracted tokens into the official W3C DTCG specification:
    https://design-tokens.github.io/community-group/format/
    """
    # Normalize input
    if hasattr(design_tokens, "to_dict"):
        raw = design_tokens.to_dict()
    elif hasattr(design_tokens, "__dict__"):
        raw = design_tokens.__dict__
    elif isinstance(design_tokens, dict):
        raw = design_tokens
    else:
        raw = {}

    dtcg: Dict[str, Any] = {
        "$description": "Extracted with Scrui Design Token Engine",
        "color": {},
        "fontFamily": {},
        "borderRadius": {},
        "dimension": {},
        "shadow": {},
    }

    # 1. Colors
    palette = raw.get("color_palette", {})
    if palette:
        for idx, col in enumerate(palette.get("dominant_colors", [])):
            dtcg["color"][f"brand-{idx+1}"] = {
                "$type": "color",
                "$value": col,
                "$description": f"Dominant color {idx+1}",
            }
        if palette.get("backgrounds"):
            for idx, bg in enumerate(palette["backgrounds"]):
                dtcg["color"][f"background-{idx+1}"] = {
                    "$type": "color",
                    "$value": bg,
                }
        if palette.get("texts"):
            for idx, txt in enumerate(palette["texts"]):
                dtcg["color"][f"text-{idx+1}"] = {
                    "$type": "color",
                    "$value": txt,
                }
    else:
        # Fallback default semantic keys if direct palette is provided
        for k in ["primary", "secondary", "background", "surface", "text", "border"]:
            if k in raw:
                dtcg["color"][k] = {"$type": "color", "$value": raw[k]}

    # 2. Typography
    typo = raw.get("typography", {})
    if typo:
        for idx, fam in enumerate(typo.get("font_families", [])):
            clean_name = fam.replace('"', '').replace("'", '').split(",")[0].strip()
            key = "heading" if idx == 0 else ("body" if idx == 1 else f"font-{idx+1}")
            dtcg["fontFamily"][key] = {
                "$type": "fontFamily",
                "$value": clean_name,
            }
    elif "font_sans" in raw or "font_heading" in raw:
        if "font_heading" in raw:
            dtcg["fontFamily"]["heading"] = {"$type": "fontFamily", "$value": raw["font_heading"]}
        if "font_sans" in raw:
            dtcg["fontFamily"]["body"] = {"$type": "fontFamily", "$value": raw["font_sans"]}

    # 3. Border Radii
    radii = raw.get("border_radii", [])
    if radii:
        for idx, rad in enumerate(radii):
            dtcg["borderRadius"][f"radius-{idx+1}"] = {
                "$type": "dimension",
                "$value": rad,
            }
    elif "radius" in raw or "border_radius" in raw:
        dtcg["borderRadius"]["base"] = {
            "$type": "dimension",
            "$value": raw.get("radius") or raw.get("border_radius", "8px"),
        }

    # 4. Box Shadows / Elevation
    shadows = raw.get("box_shadows", [])
    if shadows:
        for idx, sh in enumerate(shadows):
            dtcg["shadow"][f"elevation-{idx+1}"] = {
                "$type": "shadow",
                "$value": sh,
            }

    return dtcg


def export_figma_tokens(design_tokens: Any) -> Dict[str, Any]:
    """
    Format tokens for Figma Tokens Studio plugin:
    Nested token structure organized under a 'global' theme set.
    """
    dtcg = export_dtcg_tokens(design_tokens)
    figma_tree: Dict[str, Any] = {
        "global": {
            "colors": {},
            "fontFamilies": {},
            "borderRadius": {},
            "boxShadow": {},
        }
    }

    # Map colors
    for k, v in dtcg.get("color", {}).items():
        figma_tree["global"]["colors"][k] = {
            "value": v["$value"],
            "type": "color",
        }

    # Map fonts
    for k, v in dtcg.get("fontFamily", {}).items():
        figma_tree["global"]["fontFamilies"][k] = {
            "value": v["$value"],
            "type": "fontFamilies",
        }

    # Map radii
    for k, v in dtcg.get("borderRadius", {}).items():
        figma_tree["global"]["borderRadius"][k] = {
            "value": v["$value"],
            "type": "borderRadius",
        }

    # Map shadows
    for k, v in dtcg.get("shadow", {}).items():
        figma_tree["global"]["boxShadow"][k] = {
            "value": v["$value"],
            "type": "boxShadow",
        }

    return figma_tree


def save_tokens_bundle(design_tokens: Any, output_dir: Path) -> Dict[str, Path]:
    """
    Save both tokens.json (W3C DTCG) and figma_tokens.json to the output directory.
    Returns dictionary mapping token format name to absolute Path.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    dtcg_data = export_dtcg_tokens(design_tokens)
    figma_data = export_figma_tokens(design_tokens)

    dtcg_path = output_dir / "tokens.json"
    figma_path = output_dir / "figma_tokens.json"

    with open(dtcg_path, "w", encoding="utf-8") as f:
        json.dump(dtcg_data, f, indent=2)

    with open(figma_path, "w", encoding="utf-8") as f:
        json.dump(figma_data, f, indent=2)

    return {
        "dtcg": dtcg_path,
        "figma": figma_path,
    }
