"""
2captcha Integration — Supports all major CAPTCHA types.
API v2: createTask / getTaskResult pattern.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)

TWOCAPTCHA_BASE = "https://api.2captcha.com"


class CaptchaSolver:
    """
    2captcha API v2 client.
    Supports: reCAPTCHA v2/v3, hCaptcha, Turnstile, image CAPTCHA,
              Alibaba, DataDome, and more.
    """

    def __init__(self, api_key: str, timeout: int = 120, poll_interval: float = 3.0):
        self._key = api_key
        self._timeout = timeout
        self._poll_interval = poll_interval

    async def _create_task(self, task: dict) -> str:
        """Create a solve task. Returns task ID."""
        payload = {"clientKey": self._key, "task": task}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{TWOCAPTCHA_BASE}/createTask",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                data = await resp.json()
                if data.get("errorId", 0) != 0:
                    raise RuntimeError(f"2captcha createTask error: {data.get('errorDescription')}")
                return str(data["taskId"])

    async def _get_result(self, task_id: str) -> dict:
        """Poll for task result until solved or timeout."""
        payload = {"clientKey": self._key, "taskId": int(task_id)}
        elapsed = 0
        async with aiohttp.ClientSession() as session:
            while elapsed < self._timeout:
                await asyncio.sleep(self._poll_interval)
                elapsed += self._poll_interval
                async with session.post(
                    f"{TWOCAPTCHA_BASE}/getTaskResult",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    data = await resp.json()
                    if data.get("errorId", 0) != 0:
                        raise RuntimeError(f"2captcha getTaskResult error: {data.get('errorDescription')}")
                    if data.get("status") == "ready":
                        return data.get("solution", {})
        raise TimeoutError(f"2captcha solve timed out after {self._timeout}s")

    async def solve_recaptcha_v2(self, site_key: str, page_url: str, proxy: Optional[str] = None) -> str:
        """Solve reCAPTCHA v2 challenge. Returns gRecaptchaResponse token."""
        task = {
            "type": "RecaptchaV2TaskProxyless" if not proxy else "RecaptchaV2Task",
            "websiteURL": page_url,
            "websiteKey": site_key,
        }
        if proxy:
            task.update(self._parse_proxy(proxy))
        task_id = await self._create_task(task)
        solution = await self._get_result(task_id)
        return solution.get("gRecaptchaResponse", "")

    async def solve_recaptcha_v3(self, site_key: str, page_url: str,
                                  action: str = "verify", min_score: float = 0.3) -> str:
        """Solve reCAPTCHA v3. Returns token."""
        task = {
            "type": "RecaptchaV3TaskProxyless",
            "websiteURL": page_url,
            "websiteKey": site_key,
            "pageAction": action,
            "minScore": min_score,
        }
        task_id = await self._create_task(task)
        solution = await self._get_result(task_id)
        return solution.get("gRecaptchaResponse", "")

    async def solve_hcaptcha(self, site_key: str, page_url: str, proxy: Optional[str] = None) -> str:
        """Solve hCaptcha. Returns token."""
        task = {
            "type": "HCaptchaTaskProxyless" if not proxy else "HCaptchaTask",
            "websiteURL": page_url,
            "websiteKey": site_key,
        }
        if proxy:
            task.update(self._parse_proxy(proxy))
        task_id = await self._create_task(task)
        solution = await self._get_result(task_id)
        return solution.get("gRecaptchaResponse", "")

    async def solve_turnstile(self, site_key: str, page_url: str,
                               action: Optional[str] = None) -> str:
        """Solve Cloudflare Turnstile. Returns token."""
        task = {
            "type": "TurnstileTaskProxyless",
            "websiteURL": page_url,
            "websiteKey": site_key,
        }
        if action:
            task["action"] = action
        task_id = await self._create_task(task)
        solution = await self._get_result(task_id)
        return solution.get("token", "")

    async def solve_image_captcha(self, image_b64: str) -> str:
        """Solve image CAPTCHA. Returns text answer."""
        task = {
            "type": "ImageToTextTask",
            "body": image_b64,
        }
        task_id = await self._create_task(task)
        solution = await self._get_result(task_id)
        return solution.get("text", "")

    async def solve_data_dome(self, page_url: str, user_agent: str, captcha_url: str,
                               proxy: str) -> str:
        """Solve DataDome slider CAPTCHA."""
        task = {
            "type": "DataDomeSliderTask",
            "websiteURL": page_url,
            "captchaUrl": captcha_url,
            "userAgent": user_agent,
            **self._parse_proxy(proxy),
        }
        task_id = await self._create_task(task)
        solution = await self._get_result(task_id)
        return solution.get("cookie", "")

    def _parse_proxy(self, proxy_str: str) -> dict:
        """Parse 'host:port' or 'host:port:user:pass' into 2captcha proxy dict."""
        parts = proxy_str.split(":")
        result = {
            "proxyType": "http",
            "proxyAddress": parts[0],
            "proxyPort": int(parts[1]) if len(parts) > 1 else 80,
        }
        if len(parts) == 4:
            result["proxyLogin"] = parts[2]
            result["proxyPassword"] = parts[3]
        return result


async def auto_detect_and_solve(page, cdp, solver: CaptchaSolver, config) -> bool:
    """
    Auto-detect CAPTCHA on the current page and attempt to solve it.
    Returns True if a CAPTCHA was found and solved.
    """
    # Get current URL
    try:
        url_result = await cdp.send("Runtime.evaluate", {
            "expression": "location.href",
            "returnByValue": True,
        })
        page_url = url_result.get("result", {}).get("value", "")
    except Exception:
        page_url = ""

    # Detect Cloudflare Turnstile
    turnstile_check = await cdp.send("Runtime.evaluate", {
        "expression": """
            (() => {
                const frame = document.querySelector('iframe[src*="challenges.cloudflare.com"]');
                if (frame) {
                    const src = frame.src;
                    const match = src.match(/[?&]sitekey=([^&]+)/);
                    return match ? match[1] : 'unknown';
                }
                return null;
            })()
        """,
        "returnByValue": True,
    })
    turnstile_key = turnstile_check.get("result", {}).get("value")
    if turnstile_key:
        logger.info(f"Cloudflare Turnstile detected. Solving via 2captcha...")
        try:
            token = await solver.solve_turnstile(turnstile_key, page_url)
            # Inject token
            await cdp.send("Runtime.evaluate", {
                "expression": f"""
                    (() => {{
                        const cb = window.turnstileCallback || window.onTurnstileCallback;
                        if (cb) cb('{token}');
                        // Try injecting into hidden input
                        const input = document.querySelector('input[name="cf-turnstile-response"]');
                        if (input) {{ input.value = '{token}'; }}
                    }})()
                """,
            })
            logger.info("Turnstile token injected")
            return True
        except Exception as e:
            logger.error(f"Turnstile solve failed: {e}")
            return False

    # Detect reCAPTCHA v2
    recaptcha_check = await cdp.send("Runtime.evaluate", {
        "expression": """
            (() => {
                const el = document.querySelector('.g-recaptcha');
                if (el) return el.dataset.sitekey || 'unknown';
                const frame = document.querySelector('iframe[src*="recaptcha"]');
                if (frame) {
                    const match = frame.src.match(/[?&]k=([^&]+)/);
                    return match ? match[1] : 'unknown';
                }
                return null;
            })()
        """,
        "returnByValue": True,
    })
    recaptcha_key = recaptcha_check.get("result", {}).get("value")
    if recaptcha_key:
        logger.info(f"reCAPTCHA v2 detected. Solving via 2captcha...")
        try:
            token = await solver.solve_recaptcha_v2(recaptcha_key, page_url)
            await cdp.send("Runtime.evaluate", {
                "expression": f"document.getElementById('g-recaptcha-response').value = '{token}';",
            })
            return True
        except Exception as e:
            logger.error(f"reCAPTCHA solve failed: {e}")
            return False

    return False  # No CAPTCHA detected
