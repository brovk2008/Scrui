"""
Event Listener Extraction Module
Extracts all event listeners from the DOM via the 3-step BackendNodeId resolution,
plus framework synthetic event detection for React, Vue, and Angular.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def build_listener_map(cdp) -> dict[str, dict]:
    """
    Build a complete event listener map for the entire document.
    Handles React/Vue/Angular event delegation.
    """
    listener_map = {}

    # Get all element nodes
    doc = await cdp.send("DOM.getDocument", {"depth": -1, "pierce": True})
    all_nodes = _flatten_nodes(doc.get("root", {}))

    for node in all_nodes:
        if node.get("nodeType") != 1:
            continue  # Elements only

        backend_id = node.get("backendNodeId")
        node_id = node.get("nodeId")
        if not backend_id:
            continue

        try:
            listeners = await _get_element_listeners(cdp, backend_id)
            if listeners:
                selector = await _get_css_selector(cdp, node_id)
                listener_map[selector] = {
                    "nodeId": node_id,
                    "backendNodeId": backend_id,
                    "nodeName": node.get("nodeName", ""),
                    "listeners": listeners,
                }
        except Exception as e:
            logger.debug(f"Listener extraction failed for node {node_id}: {e}")

    return listener_map


async def _get_element_listeners(cdp, backend_node_id: int) -> list[dict]:
    """
    3-step resolution: BackendNodeId → RemoteObject → DOMDebugger.
    This is required because high-level wrapper IDs don't map to CDP object IDs.
    """
    # Step 1: Resolve BackendNodeId to RemoteObject
    try:
        remote_obj = await cdp.send("DOM.resolveNode", {
            "backendNodeId": backend_node_id,
            "objectGroup": "event-listener-extraction",
        })
    except Exception:
        return []

    object_id = remote_obj.get("object", {}).get("objectId")
    if not object_id:
        return []

    # Step 2: Query event listeners via DOMDebugger
    try:
        result = await cdp.send("DOMDebugger.getEventListeners", {
            "objectId": object_id,
            "depth": -1,
            "pierce": True,  # Include Shadow DOM listeners
        })
    except Exception:
        return []

    listeners = []
    for listener in result.get("listeners", []):
        listeners.append({
            "type": listener.get("type"),
            "scriptId": listener.get("scriptId"),
            "lineNumber": listener.get("lineNumber"),
            "columnNumber": listener.get("columnNumber"),
            "passive": listener.get("passive", False),
            "once": listener.get("once", False),
            "useCapture": listener.get("useCapture", False),
            "originalHandler": listener.get("originalHandler", {}).get("description", ""),
        })

    # Step 3: Release remote object to avoid memory leak
    try:
        await cdp.send("Runtime.releaseObject", {"objectId": object_id})
    except Exception:
        pass

    return listeners


async def _get_css_selector(cdp, node_id: int) -> str:
    """Get a CSS selector string for a node."""
    try:
        result = await cdp.send("DOM.querySelector", {"nodeId": node_id, "selector": "*"})
        # Fallback: build from node info
        node = await cdp.send("DOM.describeNode", {"nodeId": node_id, "depth": 0})
        n = node.get("node", {})
        tag = n.get("nodeName", "UNKNOWN").lower()
        attrs = {}
        attr_list = n.get("attributes", [])
        for i in range(0, len(attr_list) - 1, 2):
            attrs[attr_list[i]] = attr_list[i + 1]

        parts = [tag]
        if "id" in attrs:
            parts.append(f'#{attrs["id"]}')
        elif "class" in attrs:
            classes = attrs["class"].split()[:2]
            parts.append("." + ".".join(classes))
        parts.append(f"[data-nodeid='{node_id}']")
        return "".join(parts)
    except Exception:
        return f"[data-nodeid='{node_id}']"


def _flatten_nodes(node: dict, result: Optional[list] = None) -> list[dict]:
    """Flatten a CDP DOM tree into a flat list of nodes."""
    if result is None:
        result = []
    result.append(node)
    for child in node.get("children", []):
        _flatten_nodes(child, result)
    for shadow in node.get("shadowRoots", []):
        _flatten_nodes(shadow, result)
    return result


async def extract_framework_events(cdp) -> dict:
    """
    Detects the frontend framework and extracts its internal event registry.
    Handles React (fiber), Vue (__vue_app__), Angular (ng-version).
    """
    result = await cdp.send("Runtime.evaluate", {
        "expression": """
            (() => {
                // Detect React
                const root = document.querySelector('[data-reactroot]')
                    || document.querySelector('#root')
                    || document.querySelector('#app')
                    || document.body;
                if (root) {
                    const fiberKey = Object.keys(root).find(k =>
                        k.startsWith('__reactFiber') ||
                        k.startsWith('__reactInternalInstance')
                    );
                    if (fiberKey) return { framework: 'react', key: fiberKey };
                }
                // Detect Vue 3
                if (document.querySelector('[data-v-app]') || window.__vue_app__) {
                    return { framework: 'vue3' };
                }
                // Detect Angular
                if (document.querySelector('[ng-version]') || window.getAllAngularRootElements) {
                    return { framework: 'angular' };
                }
                // Detect Vue 2
                if (window.__vue__) {
                    return { framework: 'vue2' };
                }
                return { framework: null };
            })()
        """,
        "returnByValue": True,
    })

    framework_info = result.get("result", {}).get("value", {}) or {}
    framework = framework_info.get("framework")
    events = {"framework": framework, "event_map": {}}

    if framework == "react":
        events["event_map"] = await _extract_react_fiber_events(cdp, framework_info.get("key", ""))
    elif framework in ("vue3", "vue2"):
        events["event_map"] = await _extract_vue_events(cdp, framework)
    elif framework == "angular":
        events["event_map"] = await _extract_angular_events(cdp)

    return events


async def _extract_react_fiber_events(cdp, fiber_key: str) -> dict:
    """Walk React fiber tree to extract synthetic event handlers."""
    try:
        result = await cdp.send("Runtime.evaluate", {
            "expression": f"""
                (() => {{
                    const events = [];
                    function walkFiber(fiber) {{
                        if (!fiber) return;
                        const props = fiber.memoizedProps || {{}};
                        const handlers = Object.keys(props).filter(k =>
                            k.startsWith('on') && typeof props[k] === 'function'
                        );
                        if (handlers.length > 0) {{
                            const el = fiber.stateNode;
                            events.push({{
                                element: el ? (el.tagName || 'Component') : 'Unknown',
                                elementId: el ? el.id : '',
                                elementClass: el ? el.className : '',
                                handlers: handlers,
                                componentName: fiber.type?.displayName || fiber.type?.name || null,
                            }});
                        }}
                        walkFiber(fiber.child);
                        walkFiber(fiber.sibling);
                    }}
                    const root = document.querySelector('#root') || document.body;
                    if (root && root['{fiber_key}']) {{
                        walkFiber(root['{fiber_key}']);
                    }}
                    return events.slice(0, 500); // cap at 500
                }})()
            """,
            "returnByValue": True,
            "timeout": 10000,
        })
        return {"react_fibers": result.get("result", {}).get("value", []) or []}
    except Exception as e:
        logger.debug(f"React fiber extraction failed: {e}")
        return {}


async def _extract_vue_events(cdp, version: str) -> dict:
    try:
        result = await cdp.send("Runtime.evaluate", {
            "expression": """
                (() => {
                    const app = window.__vue_app__;
                    if (!app) return {};
                    return { vueVersion: app.version, components: Object.keys(app._context?.components || {}) };
                })()
            """,
            "returnByValue": True,
        })
        return result.get("result", {}).get("value", {}) or {}
    except Exception:
        return {}


async def _extract_angular_events(cdp) -> dict:
    try:
        result = await cdp.send("Runtime.evaluate", {
            "expression": """
                (() => {
                    const roots = window.getAllAngularRootElements?.() || [];
                    return { angularRoots: roots.length };
                })()
            """,
            "returnByValue": True,
        })
        return result.get("result", {}).get("value", {}) or {}
    except Exception:
        return {}
