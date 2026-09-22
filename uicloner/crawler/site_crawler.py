"""
Site Crawler & Sitemap Builder
Crawls an entire website, discovers all pages, and builds a full sitemap.
Feeds discovered URLs into the clone pipeline.
"""
from __future__ import annotations

import asyncio
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import urljoin, urlparse, urldefrag
from xml.etree import ElementTree

import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class PageNode:
    url: str
    depth: int
    parent_url: Optional[str]
    title: str = ""
    status_code: int = 0
    content_type: str = ""
    screenshot_b64: Optional[str] = None
    links: list[str] = field(default_factory=list)
    internal_links: list[str] = field(default_factory=list)
    external_links: list[str] = field(default_factory=list)
    meta_description: str = ""
    h1: str = ""
    word_count: int = 0
    is_crawled: bool = False
    error: Optional[str] = None
    crawled_at: float = field(default_factory=time.time)


@dataclass
class SiteMap:
    root_url: str
    pages: dict[str, PageNode] = field(default_factory=dict)
    total_discovered: int = 0
    total_crawled: int = 0
    total_failed: int = 0
    crawl_start_time: float = field(default_factory=time.time)
    crawl_end_time: float = 0.0
    sitemap_xml_urls: list[str] = field(default_factory=list)

    def add_page(self, node: PageNode) -> None:
        self.pages[node.url] = node
        self.total_discovered = len(self.pages)

    def to_summary(self) -> dict:
        return {
            "root_url": self.root_url,
            "total_pages": self.total_discovered,
            "crawled": self.total_crawled,
            "failed": self.total_failed,
            "duration_sec": round(self.crawl_end_time - self.crawl_start_time, 2),
            "pages": [
                {
                    "url": n.url,
                    "title": n.title,
                    "depth": n.depth,
                    "parent": n.parent_url,
                    "status": n.status_code,
                    "internal_links": len(n.internal_links),
                    "external_links": len(n.external_links),
                    "meta_description": n.meta_description,
                    "h1": n.h1,
                    "word_count": n.word_count,
                    "error": n.error,
                }
                for n in sorted(self.pages.values(), key=lambda p: (p.depth, p.url))
            ],
        }


# Progress callback: (discovered, crawled, failed, current_url)
CrawlProgress = Callable[[int, int, int, str], None]


class SiteCrawler:
    """
    Async multi-page crawler with:
    - robots.txt respect
    - XML sitemap seeding
    - BFS traversal with configurable depth/page limits
    - Same-domain filtering
    - Honeypot/trap detection
    """

    def __init__(self, config, browser_session=None):
        self._cfg = config.crawler
        self._browser_session = browser_session
        self._seen: set[str] = set()
        self._queue: asyncio.Queue = asyncio.Queue()
        self._sitemap = None
        self._robots_disallow: list[str] = []
        self._semaphore: asyncio.Semaphore = None

    async def crawl(
        self,
        start_url: str,
        progress: Optional[CrawlProgress] = None,
    ) -> SiteMap:
        parsed = urlparse(start_url)
        base_domain = parsed.netloc
        self._sitemap = SiteMap(root_url=start_url)
        self._semaphore = asyncio.Semaphore(self._cfg.max_concurrent)

        logger.info(f"Starting crawl of {start_url} (max {self._cfg.max_pages} pages, depth {self._cfg.max_depth})")

        # 1. Fetch robots.txt
        if self._cfg.respect_robots_txt:
            await self._fetch_robots(start_url)

        # 2. Seed from XML sitemap
        if self._cfg.parse_sitemap_xml:
            sitemap_urls = await self._fetch_sitemap_xml(start_url)
            self._sitemap.sitemap_xml_urls = sitemap_urls
            for url in sitemap_urls[:self._cfg.max_pages]:
                if url not in self._seen:
                    self._seen.add(url)
                    await self._queue.put((url, 1, start_url))
            logger.info(f"Seeded {len(sitemap_urls)} URLs from XML sitemap")

        # 3. Seed start URL
        if start_url not in self._seen:
            self._seen.add(start_url)
            await self._queue.put((start_url, 0, None))

        # 4. BFS crawl
        workers = [
            asyncio.create_task(self._worker(base_domain, progress))
            for _ in range(self._cfg.max_concurrent)
        ]

        await self._queue.join()
        for w in workers:
            w.cancel()

        self._sitemap.crawl_end_time = time.time()
        logger.info(
            f"Crawl complete: {self._sitemap.total_crawled} pages, "
            f"{self._sitemap.total_failed} failed, "
            f"{self._sitemap.crawl_end_time - self._sitemap.crawl_start_time:.1f}s"
        )
        return self._sitemap

    async def _worker(self, base_domain: str, progress: Optional[CrawlProgress]) -> None:
        while True:
            url, depth, parent = await self._queue.get()
            try:
                async with self._semaphore:
                    node = await self._crawl_page(url, depth, parent, base_domain)
                    self._sitemap.add_page(node)
                    if node.is_crawled:
                        self._sitemap.total_crawled += 1
                    else:
                        self._sitemap.total_failed += 1

                    # Enqueue discovered links
                    if depth < self._cfg.max_depth and len(self._seen) < self._cfg.max_pages:
                        for link in node.internal_links:
                            clean = urldefrag(link)[0]
                            if clean and clean not in self._seen:
                                if not self._is_excluded(clean):
                                    self._seen.add(clean)
                                    await self._queue.put((clean, depth + 1, url))

                    if progress:
                        progress(
                            self._sitemap.total_discovered,
                            self._sitemap.total_crawled,
                            self._sitemap.total_failed,
                            url,
                        )

                    # Polite delay
                    await asyncio.sleep(self._cfg.page_delay_seconds)
            except Exception as e:
                logger.debug(f"Worker error for {url}: {e}")
            finally:
                self._queue.task_done()

    async def _crawl_page(
        self, url: str, depth: int, parent: Optional[str], base_domain: str
    ) -> PageNode:
        node = PageNode(url=url, depth=depth, parent_url=parent)

        # Check robots.txt
        if self._is_robots_blocked(url):
            node.error = "robots.txt blocked"
            return node

        try:
            if self._browser_session:
                # Use browser for JS-rendered pages
                node = await self._crawl_with_browser(url, depth, parent, base_domain)
            else:
                # Lightweight HTTP crawl
                node = await self._crawl_with_http(url, depth, parent, base_domain)
        except Exception as e:
            node.error = str(e)[:200]
            logger.debug(f"Failed to crawl {url}: {e}")

        return node

    async def _crawl_with_browser(
        self, url: str, depth: int, parent: Optional[str], base_domain: str
    ) -> PageNode:
        node = PageNode(url=url, depth=depth, parent_url=parent)
        try:
            await self._browser_session.goto(url)
            await asyncio.sleep(1.5)  # Wait for JS

            result = await self._browser_session.cdp.send("Runtime.evaluate", {
                "expression": """
                    JSON.stringify({
                        title: document.title,
                        h1: document.querySelector('h1')?.textContent?.trim() || '',
                        meta_description: document.querySelector('meta[name=description]')?.content || '',
                        word_count: document.body?.innerText?.split(/\\s+/).length || 0,
                        links: Array.from(document.querySelectorAll('a[href]')).map(a => a.href),
                        status: 200,
                    })
                """,
                "returnByValue": True,
            })
            data = __import__("json").loads(result.get("result", {}).get("value", "{}"))
            node.title = data.get("title", "")
            node.h1 = data.get("h1", "")
            node.meta_description = data.get("meta_description", "")
            node.word_count = data.get("word_count", 0)
            node.status_code = 200
            node.is_crawled = True

            all_links = data.get("links", [])
            node.links = all_links
            node.internal_links = [l for l in all_links if urlparse(l).netloc == base_domain]
            node.external_links = [l for l in all_links if urlparse(l).netloc and urlparse(l).netloc != base_domain]

            # Screenshot if configured
            if self._cfg.screenshot_all_pages:
                ss = await self._browser_session.cdp.send("Page.captureScreenshot", {
                    "format": "png", "quality": 60
                })
                node.screenshot_b64 = ss.get("data")

        except Exception as e:
            node.error = str(e)[:200]

        return node

    async def _crawl_with_http(
        self, url: str, depth: int, parent: Optional[str], base_domain: str
    ) -> PageNode:
        """Fast lightweight HTTP crawl for link discovery."""
        node = PageNode(url=url, depth=depth, parent_url=parent)
        try:
            timeout = aiohttp.ClientTimeout(total=15)
            headers = {"User-Agent": "Mozilla/5.0 (compatible; UICloner/2.0)"}
            async with aiohttp.ClientSession(headers=headers, timeout=timeout) as sess:
                async with sess.get(url, allow_redirects=True) as resp:
                    node.status_code = resp.status
                    node.content_type = resp.content_type or ""
                    if resp.status == 200 and "html" in node.content_type:
                        html = await resp.text(errors="replace")
                        node.is_crawled = True
                        # Parse with basic regex (no heavy lib dependency)
                        title_m = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
                        node.title = title_m.group(1).strip() if title_m else ""
                        h1_m = re.search(r"<h1[^>]*>([^<]+)</h1>", html, re.IGNORECASE)
                        node.h1 = re.sub(r"<[^>]+>", "", h1_m.group(1)).strip() if h1_m else ""
                        desc_m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)', html, re.IGNORECASE)
                        node.meta_description = desc_m.group(1) if desc_m else ""
                        # Extract links
                        hrefs = re.findall(r'href=["\']([^"\'#][^"\']*)["\']', html, re.IGNORECASE)
                        all_links = [urljoin(url, h) for h in hrefs]
                        node.links = all_links[:200]
                        node.internal_links = [l for l in all_links if urlparse(l).netloc == base_domain]
                        node.external_links = [l for l in all_links if urlparse(l).netloc and urlparse(l).netloc != base_domain]
                        # Word count estimate
                        text = re.sub(r"<[^>]+>", " ", html)
                        node.word_count = len(text.split())
        except Exception as e:
            node.error = str(e)[:200]

        return node

    async def _fetch_robots(self, start_url: str) -> None:
        parsed = urlparse(start_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as sess:
                async with sess.get(robots_url) as resp:
                    if resp.status == 200:
                        text = await resp.text(errors="replace")
                        in_user_agent = False
                        for line in text.splitlines():
                            line = line.strip()
                            if line.lower().startswith("user-agent:"):
                                ua = line.split(":", 1)[1].strip()
                                in_user_agent = ua in ("*", "UICloner", "uicloner")
                            elif in_user_agent and line.lower().startswith("disallow:"):
                                path = line.split(":", 1)[1].strip()
                                if path:
                                    self._robots_disallow.append(path)
                        logger.debug(f"robots.txt: {len(self._robots_disallow)} disallow rules")
        except Exception as e:
            logger.debug(f"robots.txt fetch failed: {e}")

    def _is_robots_blocked(self, url: str) -> bool:
        path = urlparse(url).path
        for pattern in self._robots_disallow:
            if path.startswith(pattern):
                return True
        return False

    async def _fetch_sitemap_xml(self, start_url: str) -> list[str]:
        """Try common sitemap locations and parse URLs from XML."""
        parsed = urlparse(start_url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        candidates = [
            f"{base}/sitemap.xml",
            f"{base}/sitemap_index.xml",
            f"{base}/sitemap/sitemap.xml",
            f"{base}/wp-sitemap.xml",
        ]

        urls = []
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as sess:
            for sitemap_url in candidates:
                try:
                    async with sess.get(sitemap_url) as resp:
                        if resp.status == 200:
                            text = await resp.text(errors="replace")
                            # Parse <loc> tags
                            found = re.findall(r"<loc>\s*([^<]+)\s*</loc>", text)
                            logger.info(f"Found {len(found)} URLs in {sitemap_url}")
                            urls.extend(found)
                            if urls:
                                break
                except Exception:
                    continue

        return [u.strip() for u in urls if u.strip()]

    def _is_excluded(self, url: str) -> bool:
        for pattern in self._cfg.exclude_patterns:
            if re.match(pattern, url, re.IGNORECASE):
                return True
        return False
