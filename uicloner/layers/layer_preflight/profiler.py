"""
Pre-Flight Target Profiler (Layer -1)
Performs zero-browser network inspection, CDN/WAF detection,
DOM complexity estimation, and technology stack fingerprinting.
"""
from __future__ import annotations

import logging
import re
import socket
import time
from dataclasses import dataclass, field, asdict
from typing import Optional
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)


@dataclass
class TargetProfile:
    """Diagnostic profile of the target website extracted during pre-flight."""
    url: str
    host: str
    ip: Optional[str] = None
    latency_ms: float = 0.0
    http_status: int = 200
    server_header: str = "Unknown"
    cdn_waf: str = "None detected"
    is_waf_protected: bool = False
    content_encoding: str = "identity"
    http_version: str = "HTTP/1.1"
    html_bytes: int = 0
    scripts_count: int = 0
    styles_count: int = 0
    images_count: int = 0
    forms_count: int = 0
    buttons_count: int = 0
    detected_frameworks: list[str] = field(default_factory=list)
    has_shadow_dom: bool = False
    has_canvas: bool = False
    dynamic_spa_index: float = 0.0  # 0.0 = static SSR, 1.0 = heavy client-side SPA
    complexity_score: int = 1       # 1 to 10 scale
    estimated_dom_nodes: int = 100
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def summary_line(self) -> str:
        frameworks_str = ", ".join(self.detected_frameworks[:3]) if self.detected_frameworks else "Vanilla Web"
        return (
            f"{self.host} ({self.latency_ms:.0f}ms) | WAF: {self.cdn_waf} | "
            f"Stack: {frameworks_str} | Complexity: {self.complexity_score}/10"
        )


class PreflightProfiler:
    """
    Rapid non-browser inspection engine. Sends lightweight probe requests
    to analyze network latency, edge infrastructure, and document structure.
    """

    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )

    def __init__(self, config=None):
        self.config = config
        timeout = 6.0
        if config and hasattr(config, "preflight") and hasattr(config.preflight, "probe_timeout_seconds"):
            timeout = config.preflight.probe_timeout_seconds
        self.timeout = timeout

    async def probe(self, url: str) -> TargetProfile:
        """
        Execute pre-flight probe and return comprehensive TargetProfile.
        """
        parsed = urlparse(url)
        host = parsed.netloc or "unknown"
        # Strip port if present
        hostname = host.split(":")[0]

        # 1. DNS / IP resolution & Latency check
        resolved_ip = None
        try:
            resolved_ip = socket.gethostbyname(hostname)
        except Exception:
            pass

        start_time = time.perf_counter()
        http_status = 200
        headers_dict: dict[str, str] = {}
        body_text = ""
        http_version = "HTTP/1.1"

        headers = {
            "User-Agent": self.DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }

        # 2. Async HTTP probe
        latency_ms = 0.0
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                verify=False,
                http2=True,
            ) as client:
                resp = await client.get(url, headers=headers)
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                http_status = resp.status_code
                http_version = f"HTTP/{resp.http_version}"
                for k, v in resp.headers.items():
                    headers_dict[k.lower()] = v
                body_text = resp.text
        except Exception as e:
            logger.debug(f"Preflight HTTP probe fallback due to: {e}")
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            # Fallback using urllib if httpx fails
            try:
                import urllib.request
                req = urllib.request.Request(url, headers={"User-Agent": self.DEFAULT_USER_AGENT})
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    http_status = response.status
                    for k, v in response.getheaders():
                        headers_dict[k.lower()] = v
                    body_text = response.read().decode("utf-8", errors="ignore")
            except Exception:
                pass

        # 3. CDN & WAF Analysis
        cdn_waf, is_waf = self._detect_cdn_waf(headers_dict, body_text)
        server_hdr = headers_dict.get("server", "Unknown")
        content_encoding = headers_dict.get("content-encoding", "identity")

        # 4. HTML Structural Profiling
        html_bytes = len(body_text.encode("utf-8", errors="ignore"))
        scripts_count = len(re.findall(r"<script\b", body_text, re.IGNORECASE))
        styles_count = len(re.findall(r"<link\b[^>]*rel=[\"']stylesheet[\"']|<style\b", body_text, re.IGNORECASE))
        images_count = len(re.findall(r"<img\b|<svg\b|<picture\b|<video\b", body_text, re.IGNORECASE))
        forms_count = len(re.findall(r"<form\b", body_text, re.IGNORECASE))
        buttons_count = len(re.findall(r"<button\b|type=[\"']button[\"']|type=[\"']submit[\"']", body_text, re.IGNORECASE))
        has_shadow_dom = bool(re.search(r"shadowrootmode|shadowroot|<template\s+shadow", body_text, re.IGNORECASE))
        has_canvas = bool(re.search(r"<canvas\b", body_text, re.IGNORECASE))

        # 5. Technology Stack Detection
        frameworks = self._detect_frameworks(body_text, headers_dict)

        # 6. Dynamic SPA Index & Complexity Score
        spa_index = self._calculate_spa_index(body_text, scripts_count)
        complexity_score = self._calculate_complexity(
            html_bytes=html_bytes,
            scripts_count=scripts_count,
            styles_count=styles_count,
            frameworks=frameworks,
            is_waf=is_waf,
            has_shadow=has_shadow_dom,
            has_canvas=has_canvas,
        )
        estimated_nodes = max(50, int(html_bytes / 80) + scripts_count * 15 + styles_count * 10)

        return TargetProfile(
            url=url,
            host=host,
            ip=resolved_ip,
            latency_ms=round(latency_ms, 1),
            http_status=http_status,
            server_header=server_hdr,
            cdn_waf=cdn_waf,
            is_waf_protected=is_waf,
            content_encoding=content_encoding,
            http_version=http_version,
            html_bytes=html_bytes,
            scripts_count=scripts_count,
            styles_count=styles_count,
            images_count=images_count,
            forms_count=forms_count,
            buttons_count=buttons_count,
            detected_frameworks=frameworks,
            has_shadow_dom=has_shadow_dom,
            has_canvas=has_canvas,
            dynamic_spa_index=round(spa_index, 2),
            complexity_score=complexity_score,
            estimated_dom_nodes=estimated_nodes,
        )

    def _detect_cdn_waf(self, headers: dict[str, str], body: str) -> tuple[str, bool]:
        """Detect CDN, Edge Proxy, and WAF providers from headers and response markers."""
        # Cloudflare
        if "cf-ray" in headers or "cf-cache-status" in headers or "cloudflare" in headers.get("server", "").lower():
            return "Cloudflare (cf-ray)", True
        # Akamai
        if any(k.startswith("x-akamai") or k.startswith("akamai") for k in headers):
            return "Akamai Edge", True
        # AWS CloudFront
        if "x-amz-cf-id" in headers or "x-amz-cf-pop" in headers:
            return "AWS CloudFront", False
        # Fastly
        if "x-fastly-request-id" in headers or "fastly-restarts" in headers:
            return "Fastly CDN", False
        # Imperva / Incapsula
        if "x-iinfo" in headers or "visid_incap" in headers.get("set-cookie", "").lower():
            return "Imperva Incapsula", True
        # DataDome
        if "x-datadome" in headers or "datadome=" in headers.get("set-cookie", "").lower():
            return "DataDome Shield", True
        # Sucuri
        if "x-sucuri-id" in headers:
            return "Sucuri WAF", True
        # Varnish
        if "x-varnish" in headers:
            return "Varnish Cache", False

        # Body checks
        body_lower = body[:10000].lower()
        if "cf-browser-verification" in body_lower or "challenge-running" in body_lower:
            return "Cloudflare Challenge", True
        if "perimeterx" in body_lower or "_px3" in body_lower:
            return "HUMAN / PerimeterX", True

        return "None detected", False

    def _detect_frameworks(self, body: str, headers: dict[str, str]) -> list[str]:
        """Identify frontend frameworks and design systems from HTML markers."""
        frameworks: list[str] = []
        body_sample = body[:50000]

        # Next.js
        if "__NEXT_DATA__" in body_sample or "/_next/" in body_sample:
            frameworks.append("Next.js")
        # React (if not already labeled Next.js or present independently)
        if "data-reactroot" in body_sample or "react" in body_sample:
            if "Next.js" not in frameworks:
                frameworks.append("React")

        # Nuxt.js
        if "__NUXT__" in body_sample or "/_nuxt/" in body_sample:
            frameworks.append("Nuxt.js")
        # Vue
        if "data-v-" in body_sample or "v-if" in body_sample or "__vue_app__" in body_sample:
            if "Nuxt.js" not in frameworks:
                frameworks.append("Vue.js")

        # Angular
        if "ng-version" in body_sample or "ng-app" in body_sample:
            frameworks.append("Angular")

        # Svelte
        if "svelte-" in body_sample:
            frameworks.append("Svelte")

        # Tailwind CSS
        if "tw-" in body_sample or re.search(r'class=[\'"][^\'"]*\b(flex|grid|relative|absolute|text-|bg-)[^\'"]*[\'"]', body_sample):
            frameworks.append("Tailwind CSS")

        # GSAP / Animation Libraries
        if "gsap" in body_sample.lower() or "scrolltrigger" in body_sample.lower():
            frameworks.append("GSAP")
        if "lottie" in body_sample.lower() or "bodymovin" in body_sample.lower():
            frameworks.append("Lottie")

        # Webflow
        if "data-wf-page" in body_sample or "webflow" in body_sample.lower():
            frameworks.append("Webflow")

        # Shopify
        if "cdn.shopify.com" in body_sample or "Shopify." in body_sample:
            frameworks.append("Shopify")

        # WordPress
        if "wp-content" in body_sample or "wp-includes" in body_sample:
            frameworks.append("WordPress")

        # Bootstrap
        if "bootstrap" in body_sample.lower():
            frameworks.append("Bootstrap")

        return frameworks

    def _calculate_spa_index(self, body: str, scripts_count: int) -> float:
        """Estimate dynamic client-rendering index from 0.0 (static) to 1.0 (heavy SPA)."""
        body_len = len(body)
        if body_len < 1000:
            return 0.9  # Tiny shell with JS loader
        # Strip script tags to measure static visible text density
        stripped = re.sub(r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>", "", body, flags=re.IGNORECASE)
        static_ratio = len(stripped) / max(1, body_len)

        if scripts_count > 25 and static_ratio < 0.4:
            return 0.85
        elif scripts_count > 15 and static_ratio < 0.6:
            return 0.65
        elif scripts_count > 5:
            return 0.40
        return 0.15

    def _calculate_complexity(
        self,
        html_bytes: int,
        scripts_count: int,
        styles_count: int,
        frameworks: list[str],
        is_waf: bool,
        has_shadow: bool,
        has_canvas: bool,
    ) -> int:
        """Calculate overall UI complexity score on a scale of 1 to 10."""
        score = 2

        if html_bytes > 200_000:
            score += 2
        elif html_bytes > 50_000:
            score += 1

        if scripts_count > 30:
            score += 2
        elif scripts_count > 12:
            score += 1

        if is_waf:
            score += 1
        if has_shadow:
            score += 1
        if has_canvas:
            score += 1
        if any(f in frameworks for f in ["GSAP", "Lottie", "Next.js", "Angular"]):
            score += 1

        return min(10, max(1, score))
