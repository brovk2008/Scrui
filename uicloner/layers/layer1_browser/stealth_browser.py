"""
Layer 1 — Stealth Browser Orchestration Layer
Manages browser engine selection, CDP sessions, fingerprint generation,
stealth patches, and behavioral simulation.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import random
import secrets
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stealth JavaScript snippets (injected before page load)
# ---------------------------------------------------------------------------

def _build_stealth_script(session_noise_seed: int, config) -> str:
    """Build the pre-load stealth injection script."""
    renderer = config.evasion.webgl_renderer
    vendor = config.evasion.webgl_vendor
    return f"""
(function() {{
    'use strict';

    const SESSION_NOISE_SEED = {session_noise_seed};
    const SESSION_NOISE_BYTE = SESSION_NOISE_SEED & 0xFF;

    // --- 1. Remove webdriver flag ---
    Object.defineProperty(navigator, 'webdriver', {{
        get: () => undefined,
        configurable: true
    }});

    // --- 2. Mock chrome.runtime ---
    if (!window.chrome) {{
        Object.defineProperty(window, 'chrome', {{
            value: {{ runtime: {{}}, loadTimes: function(){{}}, csi: function(){{}}, app: {{}} }},
            writable: true, configurable: true
        }});
    }} else if (!window.chrome.runtime) {{
        window.chrome.runtime = {{}};
    }}

    // --- 3. Realistic plugins ---
    const pluginData = [
        {{ name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' }},
        {{ name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' }},
        {{ name: 'Native Client', filename: 'internal-nacl-plugin', description: '' }},
    ];
    const pluginArray = Object.assign(Object.create(PluginArray.prototype), {{
        length: pluginData.length,
        item: (i) => pluginData[i],
        namedItem: (name) => pluginData.find(p => p.name === name),
        refresh: () => {{}}
    }});
    pluginData.forEach((p, i) => {{ pluginArray[i] = p; }});
    Object.defineProperty(navigator, 'plugins', {{ get: () => pluginArray }});

    // --- 4. Canvas noise (deterministic per session) ---
    {_canvas_noise_script() if config.evasion.canvas_noise else ''}

    // --- 5. WebGL spoof ---
    {_webgl_spoof_script(renderer, vendor) if config.evasion.webgl_spoof else ''}

    // --- 6. Disable WebRTC leak ---
    {_webrtc_disable_script() if config.evasion.webrtc_disabled else ''}

    // --- 7. Permissions mock ---
    if (navigator.permissions) {{
        const origQuery = navigator.permissions.query.bind(navigator.permissions);
        navigator.permissions.query = (params) => {{
            if (params.name === 'notifications') {{
                return Promise.resolve({{ state: 'default', onchange: null }});
            }}
            return origQuery(params);
        }};
    }}

    console.debug('[UICloner] Stealth patches applied, session_seed=' + SESSION_NOISE_SEED);
}})();
"""


def _canvas_noise_script() -> str:
    return """
    const _origToDataURL = HTMLCanvasElement.prototype.toDataURL;
    const _origGetImageData = CanvasRenderingContext2D.prototype.getImageData;
    HTMLCanvasElement.prototype.toDataURL = function(type) {
        const ctx = this.getContext('2d');
        if (ctx && this.width > 0 && this.height > 0) {
            try {
                const imageData = ctx.getImageData(0, 0, this.width, this.height);
                for (let i = 0; i < imageData.data.length; i += 4) {
                    imageData.data[i]     ^= (SESSION_NOISE_SEED >> (i % 8)) & 0x01;
                    imageData.data[i + 1] ^= (SESSION_NOISE_SEED >> ((i + 1) % 8)) & 0x01;
                }
                ctx.putImageData(imageData, 0, 0);
            } catch(e) {}
        }
        return _origToDataURL.apply(this, arguments);
    };
    """


def _webgl_spoof_script(renderer: str, vendor: str) -> str:
    return f"""
    const _origGetContext = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function(type, attrs) {{
        const ctx = _origGetContext.apply(this, arguments);
        if ((type === 'webgl' || type === 'webgl2') && ctx) {{
            const _origGetParam = ctx.getParameter.bind(ctx);
            ctx.getParameter = function(pname) {{
                if (pname === ctx.RENDERER) return '{renderer}';
                if (pname === ctx.VENDOR) return '{vendor}';
                if (pname === 37445) return '{vendor}';
                if (pname === 37446) return '{renderer}';
                return _origGetParam(pname);
            }};
            const _origReadPixels = ctx.readPixels.bind(ctx);
            ctx.readPixels = function(x, y, w, h, format, type, pixels) {{
                _origReadPixels(x, y, w, h, format, type, pixels);
                if (pixels) {{
                    for (let i = 0; i < pixels.length; i += 4) {{
                        pixels[i]     ^= SESSION_NOISE_BYTE;
                        pixels[i + 1] ^= (SESSION_NOISE_BYTE >> 1) & 0xFF;
                    }}
                }}
            }};
        }}
        return ctx;
    }};
    """


def _webrtc_disable_script() -> str:
    return """
    if (typeof RTCPeerConnection !== 'undefined') {
        const _origRTC = RTCPeerConnection;
        RTCPeerConnection = function(config) {
            if (config && config.iceServers) { config.iceServers = []; }
            return new _origRTC(config || {});
        };
        RTCPeerConnection.prototype = _origRTC.prototype;
    }
    """


# ---------------------------------------------------------------------------
# Behavioral simulation (mouse, scroll, typing)
# ---------------------------------------------------------------------------

class BehavioralSimulator:
    """Simulates human-like mouse movements, scrolling, and typing."""

    def __init__(self, config):
        self._config = config

    async def human_mouse_move(self, page, start_x: float, start_y: float,
                                end_x: float, end_y: float) -> None:
        """Move mouse along a Bézier curve with organic jitter."""
        speed_min, speed_max = self._config.evasion.mouse_speed_ms_range
        duration_ms = random.randint(speed_min, speed_max)
        steps = max(20, duration_ms // 10)

        # Cubic Bézier control points
        cp1x = start_x + (end_x - start_x) * 0.3 + random.uniform(-50, 50)
        cp1y = start_y + (end_y - start_y) * 0.15 + random.uniform(-30, 30)
        cp2x = start_x + (end_x - start_x) * 0.7 + random.uniform(-50, 50)
        cp2y = start_y + (end_y - start_y) * 0.85 + random.uniform(-30, 30)

        for i in range(steps + 1):
            t = i / steps
            mt = 1 - t
            x = mt**3 * start_x + 3*mt**2*t * cp1x + 3*mt*t**2 * cp2x + t**3 * end_x
            y = mt**3 * start_y + 3*mt**2*t * cp1y + 3*mt*t**2 * cp2y + t**3 * end_y
            # Sub-pixel micro-jitter (human hand tremor)
            x += random.gauss(0, 0.4)
            y += random.gauss(0, 0.4)
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.008, 0.025))

    async def human_scroll(self, page, total_distance: int = 3000) -> None:
        """Scroll down the page in natural increments."""
        scrolled = 0
        while scrolled < total_distance:
            scroll_amount = random.randint(100, 400)
            await page.mouse.wheel(0, scroll_amount)
            scrolled += scroll_amount
            pause = random.uniform(0.3, 1.2)
            await asyncio.sleep(pause)
        # Small scroll back up (natural reading behavior)
        await page.mouse.wheel(0, -random.randint(50, 200))
        await asyncio.sleep(random.uniform(0.5, 1.5))

    async def human_type(self, page, selector: str, text: str) -> None:
        """Type text with human-like delays between keystrokes."""
        await page.click(selector)
        for char in text:
            await page.keyboard.type(char)
            await asyncio.sleep(random.uniform(0.05, 0.2))


# ---------------------------------------------------------------------------
# Browser session wrapper
# ---------------------------------------------------------------------------

class StealthSession:
    """
    Wraps a browser page with CDP access, stealth patches, and fingerprinting.
    Supports nodriver (primary), Patchright (fallback), Camoufox (second fallback).
    """

    def __init__(self, browser, page, cdp, config, session_id: str, noise_seed: int):
        self.browser = browser
        self.page = page
        self.cdp = cdp
        self.config = config
        self.session_id = session_id
        self.noise_seed = noise_seed
        self.behavior = BehavioralSimulator(config)
        self._assets: dict[str, dict] = {}

    async def goto(self, url: str) -> None:
        """Navigate with optional behavioral simulation."""
        await self.page.get(url) if hasattr(self.page, 'get') else await self.page.goto(url)

    async def wait_for_idle(self) -> None:
        """Multi-signal idle detection: network + rAF + readyState."""
        cfg = self.config.extraction
        try:
            if hasattr(self.page, 'wait_for_load_state'):
                await self.page.wait_for_load_state("networkidle")
        except Exception:
            pass

        # Wait for one animation frame + buffer
        try:
            await self.cdp.send("Runtime.evaluate", {
                "expression": f"""
                    new Promise(resolve => {{
                        requestAnimationFrame(() => setTimeout(resolve, {cfg.extra_wait_ms}));
                    }})
                """,
                "awaitPromise": True,
                "timeout": 15000
            })
        except Exception as e:
            logger.debug(f"rAF wait failed (non-critical): {e}")
            await asyncio.sleep(cfg.extra_wait_ms / 1000)

    async def auto_scroll(self) -> None:
        """Scroll to trigger lazy content."""
        if self.config.extraction.auto_scroll:
            await self.behavior.human_scroll(self.page)

    async def close(self) -> None:
        try:
            await self.browser.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Engine launcher
# ---------------------------------------------------------------------------

class BrowserEngineSelector:
    """Tries to launch the best available browser engine."""

    @staticmethod
    async def launch(config, profile_dir: Optional[Path] = None) -> StealthSession:
        engines = [config.browser.primary_engine.value] + [
            e.value for e in config.browser.fallback_chain
        ]
        last_exc = None
        for engine in engines:
            try:
                logger.info(f"Attempting to launch engine: {engine}")
                return await BrowserEngineSelector._launch_engine(engine, config, profile_dir)
            except Exception as exc:
                logger.warning(f"Engine {engine} failed: {exc}")
                last_exc = exc
        raise RuntimeError(f"All browser engines failed. Last error: {last_exc}")

    @staticmethod
    async def _launch_engine(engine: str, config, profile_dir: Optional[Path]) -> StealthSession:
        session_id = secrets.token_hex(8)
        noise_seed = int(hashlib.sha256(session_id.encode()).hexdigest()[:8], 16)

        if engine == "nodriver":
            return await BrowserEngineSelector._launch_nodriver(config, session_id, noise_seed, profile_dir)
        elif engine == "patchright":
            return await BrowserEngineSelector._launch_patchright(config, session_id, noise_seed, profile_dir)
        elif engine == "camoufox":
            return await BrowserEngineSelector._launch_camoufox(config, session_id, noise_seed, profile_dir)
        else:
            raise ValueError(f"Unknown engine: {engine}")

    @staticmethod
    async def _launch_nodriver(config, session_id, noise_seed, profile_dir) -> StealthSession:
        import nodriver as uc

        profile_path = str(profile_dir) if profile_dir else None
        browser = await uc.start(
            headless=config.browser.headless,
            user_data_dir=profile_path,
            lang="en-US",
        )
        page = await browser.get("about:blank")

        # Get CDP session
        cdp = page  # nodriver's page IS the CDP session

        # Inject stealth script
        stealth_js = _build_stealth_script(noise_seed, config)
        try:
            await browser.connection.send("Page.addScriptToEvaluateOnNewDocument", {
                "source": stealth_js
            })
        except Exception as e:
            logger.debug(f"Pre-load script injection warning: {e}")

        logger.info(f"nodriver session launched: {session_id}")
        return StealthSession(browser, page, page, config, session_id, noise_seed)

    @staticmethod
    async def _launch_patchright(config, session_id, noise_seed, profile_dir) -> StealthSession:
        try:
            from patchright.async_api import async_playwright
        except ImportError:
            from playwright.async_api import async_playwright

        pw = await async_playwright().__aenter__()
        launch_args = ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]

        browser = await pw.chromium.launch(
            headless=config.browser.headless,
            args=launch_args,
        )
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
        )
        page = await ctx.new_page()
        cdp = await ctx.new_cdp_session(page)

        stealth_js = _build_stealth_script(noise_seed, config)
        await ctx.add_init_script(stealth_js)

        logger.info(f"Patchright session launched: {session_id}")
        return StealthSession(browser, page, cdp, config, session_id, noise_seed)

    @staticmethod
    async def _launch_camoufox(config, session_id, noise_seed, profile_dir) -> StealthSession:
        try:
            from camoufox.async_api import AsyncCamoufox
            from browserforge.fingerprints import FingerprintGenerator, Screen

            fpc = config.fingerprint
            fg = FingerprintGenerator(
                browser=tuple(fpc.browser_distribution.keys()),
                os=tuple(fpc.os_distribution.keys()),
                device="desktop",
                locale=fpc.locale,
                screen=Screen(
                    min_width=fpc.screen_min[0], min_height=fpc.screen_min[1],
                    max_width=fpc.screen_max[0], max_height=fpc.screen_max[1],
                ),
            )
            fp = fg.generate()

            camoufox = AsyncCamoufox(fingerprint=fp, headless="virtual" if not config.browser.headless else True)
            browser = await camoufox.__aenter__()
            page = await browser.new_page()
            cdp = await page.context.new_cdp_session(page)
            logger.info(f"Camoufox session launched: {session_id}")
            return StealthSession(browser, page, cdp, config, session_id, noise_seed)
        except ImportError as e:
            raise ImportError(f"Camoufox/browserforge not installed: {e}")
