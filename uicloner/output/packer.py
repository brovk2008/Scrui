"""
HTML Packer — Produces a self-contained single-file HTML clone.
Inlines all CSS, fonts, images, and scripts as data URIs or base64.
Optionally embeds rrweb replay player.
"""
from __future__ import annotations

import base64
import logging
import re
from typing import Optional
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


def build_single_file_html(
    outer_html: str,
    stylesheets: list[dict],
    scripts: list[dict],
    asset_records: dict[str, dict],  # url -> asset record with data_uri
    animations_css: str,
    shadow_dsd_html: Optional[str],
    meta: dict,
    base_url: str,
    embed_rrweb: bool = True,
    scroll_rebind_js: str = "",
    lottie_runtime_js: str = "",
) -> str:
    """
    Assembles a self-contained single-file HTML document.
    All external assets are replaced with data URIs.
    """
    html = shadow_dsd_html or outer_html

    # Step 1: Inline all stylesheets
    for sheet in stylesheets:
        css_text = sheet.get("text", "")
        source_url = sheet.get("sourceURL", "")
        if source_url and not sheet.get("isInline"):
            # Replace external <link> with <style>
            html = _replace_link_with_style(html, source_url, css_text)

    # Step 2: Inline animation CSS
    if animations_css.strip():
        html = _inject_before_body_close(html, f"<style id='uiclone-animations'>\n{animations_css}\n</style>")

    # Step 3: Replace all asset URLs with data URIs
    html = _inline_assets(html, asset_records, base_url)

    # Step 4: Inject Lottie offline runtime if present
    if lottie_runtime_js.strip():
        html = _inject_before_body_close(html, lottie_runtime_js)

    # Step 5: Inject scroll-trigger rebind runtime if present
    if scroll_rebind_js.strip():
        html = _inject_before_body_close(html, scroll_rebind_js)

    # Step 6: Inject rrweb replay UI (if requested and events available)
    if embed_rrweb:
        rrweb_player = _build_rrweb_replay_bar()
        html = _inject_before_body_close(html, rrweb_player)

    # Step 5: Inject uiclone metadata comment
    header = f"""<!--
  Cloned by UI Cloner v2.0
  Source: {base_url}
  Format: Single-file HTML
  Assets: Inlined as data URIs
-->
"""
    html = header + html

    return html


def _replace_link_with_style(html: str, source_url: str, css_text: str) -> str:
    """Replace <link href="source_url"> with an inline <style>."""
    # Normalize URL for matching
    filename = source_url.split("/")[-1].split("?")[0]
    pattern = re.compile(
        r'<link[^>]*href=["\'][^"\']*' + re.escape(filename) + r'[^"\']*["\'][^>]*/?>',
        re.IGNORECASE,
    )
    style_tag = f'<style data-source="{source_url}">\n{css_text}\n</style>'
    result, count = pattern.subn(style_tag, html, count=1)
    if count == 0:
        # Fallback: inject at end of <head>
        html = html.replace("</head>", f"{style_tag}\n</head>", 1)
        return html
    return result


def _inline_assets(html: str, asset_records: dict, base_url: str) -> str:
    """Replace all asset URLs (src, href, url()) with data URIs."""
    def replace_url(match):
        url = match.group(1) or match.group(2) or match.group(3)
        if not url:
            return match.group(0)
        # Try exact match
        record = asset_records.get(url)
        if not record:
            # Try absolute URL
            abs_url = urljoin(base_url, url)
            record = asset_records.get(abs_url)
        if record and record.get("data_uri"):
            original = match.group(0)
            return original.replace(url, record["data_uri"])
        return match.group(0)

    # Match src="...", href="...", url(...)
    html = re.sub(r'src=["\']([^"\']+)["\']', replace_url, html)
    html = re.sub(r'href=["\']([^"\'#?][^"\']*\.(css|woff2?|ttf|otf))["\']',
                  replace_url, html, flags=re.IGNORECASE)
    # CSS url() references
    html = re.sub(r'url\(["\']?([^)"\']+)["\']?\)', replace_url, html)

    return html


def _inject_before_body_close(html: str, content: str) -> str:
    """Inject content just before </body>."""
    if "</body>" in html:
        return html.replace("</body>", f"{content}\n</body>", 1)
    return html + "\n" + content


def _build_rrweb_replay_bar() -> str:
    """Minimal rrweb replay controls injected into the clone."""
    return """
<div id="uiclone-replay-bar" style="
    position: fixed; bottom: 0; left: 0; right: 0; z-index: 999999;
    background: rgba(10,10,20,0.92); backdrop-filter: blur(8px);
    color: #e2e8f0; font-family: system-ui,sans-serif; font-size: 12px;
    padding: 8px 16px; display: flex; align-items: center; gap: 12px;
    border-top: 1px solid rgba(255,255,255,0.1);
">
    <span style="font-weight:700; color:#7c3aed; letter-spacing:.05em">⬡ UI CLONE</span>
    <span style="opacity:.5;">|</span>
    <span id="uiclone-url" style="opacity:.7; flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;"></span>
    <span style="opacity:.5; font-size:10px;">Cloned with UI Cloner v2.0</span>
    <button onclick="document.getElementById('uiclone-replay-bar').style.display='none'"
            style="background:none;border:1px solid rgba(255,255,255,.2);color:#94a3b8;
                   padding:2px 8px;border-radius:4px;cursor:pointer;font-size:10px;">✕</button>
</div>
<script>
    try {
        document.getElementById('uiclone-url').textContent = document.referrer || location.href;
    } catch(e) {}
</script>
"""
