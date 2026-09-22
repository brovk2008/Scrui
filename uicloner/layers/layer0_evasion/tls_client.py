"""
Layer 0 — TLS Client & Proxy Manager
Handles all HTTP-level stealth: TLS/JA3/JA4/HTTP2/HTTP3 impersonation,
proxy rotation, rate limiting, and honeypot detection.
"""
from __future__ import annotations

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class ProxyRecord:
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    request_count: int = 0
    is_healthy: bool = True
    last_used: float = 0.0
    failures: int = 0

    @property
    def url(self) -> str:
        if self.username and self.password:
            return f"http://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"http://{self.host}:{self.port}"

    @classmethod
    def from_string(cls, s: str) -> "ProxyRecord":
        """Parse 'host:port' or 'host:port:user:pass'."""
        parts = s.strip().split(":")
        if len(parts) == 2:
            return cls(host=parts[0], port=int(parts[1]))
        elif len(parts) == 4:
            return cls(host=parts[0], port=int(parts[1]), username=parts[2], password=parts[3])
        raise ValueError(f"Invalid proxy string: {s!r}. Expected 'host:port' or 'host:port:user:pass'")


class ProxyManager:
    """Manages a pool of proxies with rotation and health tracking."""

    def __init__(self, proxies: list[str], rotate_after: int = 5):
        self._pool: list[ProxyRecord] = [ProxyRecord.from_string(p) for p in proxies]
        self._rotate_after = rotate_after
        self._current_index = 0
        self._lock = asyncio.Lock()

    async def get_proxy(self) -> Optional[ProxyRecord]:
        if not self._pool:
            return None
        async with self._lock:
            healthy = [p for p in self._pool if p.is_healthy]
            if not healthy:
                # Reset all to healthy and retry
                for p in self._pool:
                    p.is_healthy = True
                    p.failures = 0
                healthy = self._pool[:]
            proxy = healthy[self._current_index % len(healthy)]
            proxy.request_count += 1
            proxy.last_used = time.time()
            if proxy.request_count >= self._rotate_after:
                proxy.request_count = 0
                self._current_index = (self._current_index + 1) % len(healthy)
            return proxy

    async def mark_failed(self, proxy: ProxyRecord) -> None:
        async with self._lock:
            proxy.failures += 1
            if proxy.failures >= 3:
                proxy.is_healthy = False
                logger.warning(f"Proxy {proxy.host}:{proxy.port} marked unhealthy after 3 failures")

    def add_proxy(self, proxy_str: str) -> None:
        self._pool.append(ProxyRecord.from_string(proxy_str))


class TLSClient:
    """
    HTTP client with TLS/JA3/JA4/HTTP2/HTTP3 fingerprint impersonation.
    Uses curl_cffi for maximum stealth.
    """

    IMPERSONATE_MAP = {
        "chrome120": "chrome120",
        "chrome124": "chrome124",
        "chrome131": "chrome131",
        "firefox120": "firefox120",
        "safari18": "safari18_2",
    }

    def __init__(self, config):
        self._config = config
        self._proxy_manager = ProxyManager(
            config.network.proxy_list,
            rotate_after=config.network.rotate_proxy_after_n_requests,
        ) if config.network.proxy_list else None
        self._impersonate = self.IMPERSONATE_MAP.get(
            config.network.tls_impersonate.value, "chrome131"
        )
        self._session = None

    async def __aenter__(self):
        try:
            from curl_cffi.requests import AsyncSession
            self._session = AsyncSession(impersonate=self._impersonate)
            await self._session.__aenter__()
        except ImportError:
            logger.warning("curl_cffi not available — falling back to aiohttp (no TLS impersonation)")
            import aiohttp
            self._session = aiohttp.ClientSession()
            await self._session.__aenter__()
        return self

    async def __aexit__(self, *args):
        if self._session:
            await self._session.__aexit__(*args)

    async def get(self, url: str, **kwargs) -> dict:
        """Fetch URL with TLS impersonation, proxy rotation, and jitter."""
        proxy = await self._proxy_manager.get_proxy() if self._proxy_manager else None

        # Rate-limit jitter
        jitter_min, jitter_max = self._config.network.rate_limit_jitter_seconds
        await asyncio.sleep(random.uniform(jitter_min, jitter_max))

        attempt = 0
        last_exc = None
        while attempt < self._config.network.max_retries:
            try:
                kwargs_copy = dict(kwargs)
                if proxy:
                    kwargs_copy["proxy"] = proxy.url
                kwargs_copy.setdefault("timeout", self._config.network.request_timeout_seconds)

                resp = await self._session.get(url, **kwargs_copy)

                # Handle 429
                if hasattr(resp, "status_code") and resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", 60))
                    wait = retry_after + random.uniform(1, 10)
                    logger.info(f"Rate limited — sleeping {wait:.1f}s")
                    await asyncio.sleep(wait)
                    attempt += 1
                    continue

                return resp

            except Exception as exc:
                last_exc = exc
                if proxy:
                    await self._proxy_manager.mark_failed(proxy)
                    proxy = await self._proxy_manager.get_proxy() if self._proxy_manager else None

                backoff = self._config.network.retry_backoff_base ** attempt
                logger.warning(f"Request failed (attempt {attempt + 1}): {exc}. Retrying in {backoff:.1f}s")
                await asyncio.sleep(backoff)
                attempt += 1

        raise RuntimeError(f"All {self._config.network.max_retries} retries failed for {url}") from last_exc


async def is_honeypot_link(cdp, node_id: int) -> bool:
    """
    Checks if a link element is CSS-hidden — designed to trap blind scrapers.
    """
    try:
        styles = await cdp.send("CSS.getComputedStyleForNode", {"nodeId": node_id})
        computed = {s["name"]: s["value"] for s in styles.get("computedStyle", [])}
        return (
            computed.get("display") == "none"
            or computed.get("visibility") == "hidden"
            or computed.get("opacity") == "0"
            or (computed.get("color") == computed.get("background-color") and computed.get("color") is not None)
        )
    except Exception:
        return False
