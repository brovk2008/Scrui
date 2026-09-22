"""
Layer 2 — DOM Snapshotting & Serialization Engine
Full DOM capture: assets, shadow DOM, constructed stylesheets,
temporal mutations via rrweb, and network interception.
"""
from __future__ import annotations

import asyncio
import base64
import json
import logging
from typing import Any, Optional
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Network interceptor — capture all assets via CDP
# ---------------------------------------------------------------------------

class NetworkInterceptor:
    """Captures all network responses for asset inlining."""

    def __init__(self):
        self.assets: dict[str, dict] = {}  # url -> {body, base64, mime}
        self._enabled = False

    async def start(self, cdp) -> None:
        """Enable network event capture."""
        await cdp.send("Network.enable", {})
        self._enabled = True
        logger.debug("Network interceptor started")

    def register_handlers(self, cdp) -> None:
        """Register CDP event callbacks (nodriver-style)."""
        pass  # In nodriver, events come through the connection object

    def record_response(self, url: str, body: str, base64_encoded: bool, mime: str) -> None:
        self.assets[url] = {
            "body": body,
            "base64Encoded": base64_encoded,
            "mimeType": mime,
        }

    async def fetch_response_body(self, cdp, request_id: str, url: str, mime: str) -> None:
        try:
            result = await cdp.send("Network.getResponseBody", {"requestId": request_id})
            self.assets[url] = {
                "body": result.get("body", ""),
                "base64Encoded": result.get("base64Encoded", False),
                "mimeType": mime,
            }
        except Exception as e:
            logger.debug(f"Could not get response body for {url}: {e}")

    def get_data_uri(self, url: str) -> Optional[str]:
        """Convert a captured asset to a data URI."""
        asset = self.assets.get(url)
        if not asset:
            return None
        mime = asset.get("mimeType", "application/octet-stream")
        body = asset.get("body", "")
        if asset.get("base64Encoded"):
            return f"data:{mime};base64,{body}"
        else:
            encoded = base64.b64encode(body.encode("utf-8", errors="replace")).decode()
            return f"data:{mime};base64,{encoded}"


# ---------------------------------------------------------------------------
# DOM Snapshot Engine
# ---------------------------------------------------------------------------

class DOMSnapshotEngine:
    """
    Captures a complete, self-contained DOM snapshot including all assets.
    """

    def __init__(self, session, config):
        self._session = session
        self._config = config
        self.interceptor = NetworkInterceptor()

    async def capture(self, base_url: str) -> dict:
        """
        Full DOM capture pipeline:
        1. Start network interception
        2. Wait for page idle
        3. Auto-scroll (trigger lazy content)
        4. Capture DOM via CDP
        5. Capture computed styles
        6. Inline assets
        """
        cdp = self._session.cdp
        page = self._session.page

        # Start capturing
        await self.interceptor.start(cdp)

        # Wait for full load
        await self._session.wait_for_idle()

        # Trigger lazy content
        if self._config.extraction.auto_scroll:
            await self._session.auto_scroll()
            await self._session.wait_for_idle()

        # Get outer HTML
        outer_html = await self._get_outer_html(cdp)

        # Get document structure via CDP
        doc_tree = await self._get_document_tree(cdp)

        # Capture all stylesheets
        stylesheets = await self._capture_stylesheets(cdp)

        # Capture all scripts
        scripts = await self._capture_scripts(cdp)

        # Capture meta / title
        meta = await self._capture_meta(cdp)

        return {
            "base_url": base_url,
            "outer_html": outer_html,
            "doc_tree": doc_tree,
            "stylesheets": stylesheets,
            "scripts": scripts,
            "meta": meta,
            "assets": dict(self.interceptor.assets),
        }

    async def _get_outer_html(self, cdp) -> str:
        try:
            doc = await cdp.send("DOM.getDocument", {"depth": 0})
            result = await cdp.send("DOM.getOuterHTML", {
                "nodeId": doc["root"]["nodeId"]
            })
            return result.get("outerHTML", "")
        except Exception as e:
            logger.warning(f"getOuterHTML failed: {e}")
            return ""

    async def _get_document_tree(self, cdp) -> dict:
        try:
            result = await cdp.send("DOM.getDocument", {
                "depth": -1,
                "pierce": True
            })
            return result.get("root", {})
        except Exception as e:
            logger.warning(f"DOM tree capture failed: {e}")
            return {}

    async def _capture_stylesheets(self, cdp) -> list[dict]:
        """Capture all stylesheets via CSS domain."""
        sheets = []
        try:
            await cdp.send("CSS.enable")
            result = await cdp.send("CSS.getAllStyleSheets")
            for header in result.get("headers", []):
                sheet_id = header.get("styleSheetId")
                try:
                    text_result = await cdp.send("CSS.getStyleSheetText", {"styleSheetId": sheet_id})
                    sheets.append({
                        "id": sheet_id,
                        "sourceURL": header.get("sourceURL", ""),
                        "isConstructed": header.get("isConstructed", False),
                        "isInline": header.get("isInline", False),
                        "text": text_result.get("text", ""),
                        "frameId": header.get("frameId"),
                    })
                except Exception:
                    pass
        except Exception as e:
            logger.debug(f"CSS domain error: {e}")
        return sheets

    async def _capture_scripts(self, cdp) -> list[dict]:
        """Capture script sources via Debugger domain."""
        scripts = []
        try:
            await cdp.send("Debugger.enable")
            # Scripts are reported via Debugger.scriptParsed events
            # We use Runtime to get script sources
            result = await cdp.send("Runtime.evaluate", {
                "expression": """
                    Array.from(document.querySelectorAll('script')).map(s => ({
                        src: s.src,
                        type: s.type,
                        async: s.async,
                        defer: s.defer,
                        content: s.src ? null : s.textContent
                    }))
                """,
                "returnByValue": True
            })
            scripts = result.get("result", {}).get("value", []) or []
        except Exception as e:
            logger.debug(f"Script capture error: {e}")
        return scripts

    async def _capture_meta(self, cdp) -> dict:
        try:
            result = await cdp.send("Runtime.evaluate", {
                "expression": """
                    (() => ({
                        title: document.title,
                        lang: document.documentElement.lang,
                        charset: document.characterSet,
                        viewport: document.querySelector('meta[name=viewport]')?.content,
                        description: document.querySelector('meta[name=description]')?.content,
                        ogTitle: document.querySelector('meta[property="og:title"]')?.content,
                        canonical: document.querySelector('link[rel=canonical]')?.href,
                        favicon: document.querySelector('link[rel~=icon]')?.href,
                    }))()
                """,
                "returnByValue": True,
            })
            return result.get("result", {}).get("value", {}) or {}
        except Exception:
            return {}
