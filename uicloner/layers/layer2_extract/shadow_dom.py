"""
Shadow DOM Piercing & Extraction Module
Handles both modern DSD (Declarative Shadow DOM) and legacy imperative shadow roots.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def extract_shadow_dom(cdp, page) -> dict:
    """
    Primary: use getHTML({serializableShadowRoots: true}) for DSD support.
    Fallback: CDP recursive traversal with pierce:true for imperative roots.
    Returns both the full HTML string and a tree structure.
    """
    dsd_html = await _try_get_html_with_dsd(cdp)
    tree = await _extract_shadow_tree_via_cdp(cdp)
    sheets = await _extract_constructable_stylesheets(cdp)

    return {
        "dsd_html": dsd_html,
        "shadow_tree": tree,
        "constructable_stylesheets": sheets,
    }


async def _try_get_html_with_dsd(cdp) -> Optional[str]:
    """
    Use getHTML() with serializableShadowRoots flag (baseline since Feb 2024).
    Returns full HTML with <template shadowrootmode="..."> elements.
    """
    try:
        result = await cdp.send("Runtime.evaluate", {
            "expression": """
                (() => {
                    try {
                        return document.documentElement.getHTML({
                            serializableShadowRoots: true
                        });
                    } catch(e) {
                        return null;
                    }
                })()
            """,
            "returnByValue": True,
        })
        html = result.get("result", {}).get("value")
        if html:
            logger.debug("DSD getHTML() succeeded")
        return html
    except Exception as e:
        logger.debug(f"DSD getHTML() failed: {e}")
        return None


async def _extract_shadow_tree_via_cdp(cdp, node_id: Optional[int] = None, depth: int = 0) -> dict:
    """
    Recursively extracts shadow DOM content via CDP DOM domain.
    Works even for CLOSED shadow roots (CDP bypasses all JS encapsulation).
    """
    try:
        if node_id is None:
            doc = await cdp.send("DOM.getDocument", {"depth": 0})
            node_id = doc["root"]["nodeId"]

        node_info = await cdp.send("DOM.describeNode", {
            "nodeId": node_id,
            "depth": -1,
            "pierce": True,  # CRITICAL: pierces shadow boundaries
        })

        node = node_info.get("node", {})
        shadow_roots = []

        for shadow in node.get("shadowRoots", []):
            shadow_node_id = shadow.get("nodeId")
            if shadow_node_id:
                shadow_content = await _extract_shadow_tree_via_cdp(cdp, shadow_node_id, depth + 1)
                shadow_roots.append({
                    "mode": shadow.get("shadowRootType", "open"),
                    "nodeId": shadow_node_id,
                    "content": shadow_content,
                    "dsd_html": _serialize_shadow_root(shadow, depth),
                })

        # Process children recursively
        children = []
        for child in node.get("children", []):
            child_id = child.get("nodeId")
            if child_id and child.get("shadowRoots"):
                child_data = await _extract_shadow_tree_via_cdp(cdp, child_id, depth)
                children.append(child_data)

        return {
            "nodeId": node_id,
            "nodeName": node.get("nodeName", ""),
            "children": children,
            "shadowRoots": shadow_roots,
        }

    except Exception as e:
        logger.debug(f"Shadow tree extraction failed at node {node_id}: {e}")
        return {"nodeId": node_id, "error": str(e)}


def _serialize_shadow_root(shadow_node: dict, depth: int) -> str:
    """
    Converts CDP shadow root node data into Declarative Shadow DOM HTML.
    """
    mode = shadow_node.get("shadowRootType", "open")
    inner = _serialize_node_children(shadow_node)
    return f'<template shadowrootmode="{mode}" shadowrootserializable>\n{inner}\n</template>'


def _serialize_node_children(node: dict) -> str:
    """Serialize node children to HTML (simplified, for structural output)."""
    parts = []
    for child in node.get("children", []):
        name = child.get("nodeName", "")
        if name == "#text":
            parts.append(child.get("nodeValue", ""))
        elif name.startswith("#"):
            continue
        else:
            attrs = ""
            for attr in child.get("attributes", []):
                attrs += f' {attr.get("name", "")}="{attr.get("value", "")}"'
            inner = _serialize_node_children(child)
            parts.append(f"<{name.lower()}{attrs}>{inner}</{name.lower()}>")
    return "".join(parts)


async def _extract_constructable_stylesheets(cdp) -> list[dict]:
    """
    Extracts Constructable Stylesheets (new CSSStyleSheet()) which
    cannot be serialized by DSD — this is the known limitation workaround.
    """
    sheets = []
    try:
        await cdp.send("CSS.enable")
        result = await cdp.send("CSS.getAllStyleSheets")
        for header in result.get("headers", []):
            if header.get("isConstructed", False):
                sheet_id = header["styleSheetId"]
                try:
                    text_result = await cdp.send("CSS.getStyleSheetText", {
                        "styleSheetId": sheet_id
                    })
                    sheets.append({
                        "id": sheet_id,
                        "text": text_result.get("text", ""),
                        "frameId": header.get("frameId"),
                        "sourceURL": header.get("sourceURL", ""),
                    })
                except Exception:
                    pass
    except Exception as e:
        logger.debug(f"Constructable stylesheet extraction error: {e}")
    return sheets
