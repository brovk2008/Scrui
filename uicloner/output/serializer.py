"""
Output Serializer — Structured JSON/JSONL data writer and storage manager.
Produces clean dual-folder layout:
  <site_name>/       — Live, self-contained frontend clone
  data_structure/    — Complete dismantled data, JSON/JSONL records, and SQLite index
Supports SHA-256 content deduplication and SQLite querying.
"""
from __future__ import annotations

import base64
import hashlib
import json
import logging
import mimetypes
import os
import re
import sqlite3
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urljoin, urlparse

from uicloner.config import (
    ImageStorageFormat, FontStorageFormat, VideoStorageFormat,
    OutputDataFormat, UICloneConfig,
)

logger = logging.getLogger(__name__)

# MIME type → category mapping
MIME_CATEGORIES = {
    "image": ["image/png", "image/jpeg", "image/webp", "image/gif", "image/svg+xml", "image/avif"],
    "font": ["font/woff", "font/woff2", "font/ttf", "font/otf", "application/font-woff",
             "application/font-woff2", "application/x-font-ttf"],
    "video": ["video/mp4", "video/webm", "video/ogg"],
    "audio": ["audio/mpeg", "audio/ogg", "audio/wav", "audio/webm"],
    "script": ["text/javascript", "application/javascript", "module"],
    "style": ["text/css"],
    "wasm": ["application/wasm"],
    "data": ["application/json", "application/xml", "text/plain"],
}


class OutputSerializer:
    """
    Serializes all extracted and dismantled data into the structured output folders.

    Output layout:
    clones/
    └── site_cloned_<site-name>_<timestamp>/
        ├── <site-name>/              # Clean browsable cloned website
        │   ├── index.html
        │   └── assets/
        │       ├── images/
        │       ├── fonts/
        │       ├── videos/
        │       ├── css/
        │       └── js/
        └── data_structure/           # Comprehensive reverse-engineered data
            ├── manifest.json
            ├── elements.jsonl        # Each dismantled element on one line
            ├── components.json       # Categorized components
            ├── design_system.json    # Colors, fonts, spacings, tokens
            ├── sitemap.json          # Complete site map & link graph
            ├── dom_tree.json
            ├── styles.json
            ├── scripts.json
            ├── assets.jsonl          # Assets catalog with hashes & sizes
            ├── assets.db             # Searchable SQLite database
            ├── events.json
            ├── animations.json
            ├── shadow_dom.json
            ├── canvas.json
            └── validation.json
    """

    def __init__(self, clone_root: Path, config: UICloneConfig, site_name: str = "site"):
        self.root = clone_root
        self.config = config
        self.site_name = site_name

        # Resolve directory names based on user configuration
        site_folder_name = config.output.site_folder_name or site_name
        data_folder_name = config.output.data_folder_name or "data_structure"

        self.site_dir = clone_root / site_folder_name
        self.data_dir = clone_root / data_folder_name
        self.assets_dir = self.site_dir / "assets"

        # Create directories
        self.site_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        (self.assets_dir / "images").mkdir(exist_ok=True)
        (self.assets_dir / "fonts").mkdir(exist_ok=True)
        (self.assets_dir / "videos").mkdir(exist_ok=True)
        (self.assets_dir / "audio").mkdir(exist_ok=True)
        (self.assets_dir / "wasm").mkdir(exist_ok=True)
        (self.assets_dir / "css").mkdir(exist_ok=True)
        (self.assets_dir / "js").mkdir(exist_ok=True)

        # Asset deduplication cache: content_hash -> dict(local_path, site_path)
        self._seen_content_hashes: dict[str, dict[str, str]] = {}

        # SQLite database path
        self.sqlite_db_path = self.data_dir / "assets.db"
        if self.config.storage.build_sqlite_index:
            self._init_sqlite_tables()

    # -----------------------------------------------------------------------
    # SQLite Database Initializer & Methods
    # -----------------------------------------------------------------------

    def _init_sqlite_tables(self) -> None:
        """Initializes tables for searchable querying of elements, assets, and sitemap."""
        try:
            with sqlite3.connect(self.sqlite_db_path) as conn:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS assets (
                        hash TEXT PRIMARY KEY,
                        url TEXT,
                        category TEXT,
                        mime TEXT,
                        size_bytes INTEGER,
                        local_path TEXT,
                        site_relative_path TEXT,
                        deduplicated INTEGER,
                        stored_at TEXT
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS elements (
                        id TEXT PRIMARY KEY,
                        tag TEXT,
                        role TEXT,
                        component_type TEXT,
                        text TEXT,
                        selector TEXT,
                        xpath TEXT,
                        bbox_x REAL,
                        bbox_y REAL,
                        bbox_w REAL,
                        bbox_h REAL,
                        is_interactive INTEGER,
                        is_visible INTEGER,
                        is_in_viewport INTEGER,
                        depth INTEGER
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS sitemap (
                        url TEXT PRIMARY KEY,
                        title TEXT,
                        depth INTEGER,
                        status INTEGER,
                        internal_links_count INTEGER,
                        external_links_count INTEGER,
                        h1 TEXT,
                        meta_description TEXT
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS design_tokens (
                        category TEXT,
                        token_value TEXT,
                        usage_count INTEGER
                    )
                """)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_elem_type ON elements(component_type)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_elem_tag ON elements(tag)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_asset_cat ON assets(category)")
                conn.commit()
        except Exception as e:
            logger.warning(f"SQLite initialization warning: {e}")

    def index_assets_sqlite(self, asset_records: list[dict]) -> None:
        """Populates SQLite assets table for instant SQL searches."""
        if not self.config.storage.build_sqlite_index:
            return
        try:
            now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            with sqlite3.connect(self.sqlite_db_path) as conn:
                cur = conn.cursor()
                for a in asset_records:
                    cur.execute("""
                        INSERT OR REPLACE INTO assets 
                        (hash, url, category, mime, size_bytes, local_path, site_relative_path, deduplicated, stored_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        a.get("hash", ""),
                        a.get("url", ""),
                        a.get("category", ""),
                        a.get("mime", ""),
                        a.get("size_bytes", 0),
                        a.get("local_path", ""),
                        a.get("site_relative_path", ""),
                        1 if a.get("deduplicated") else 0,
                        now,
                    ))
                conn.commit()
        except Exception as e:
            logger.warning(f"Failed to index assets in SQLite: {e}")

    def index_elements_sqlite(self, elements: list[Any]) -> None:
        """Populates SQLite elements table for instant SQL searches."""
        if not self.config.storage.build_sqlite_index:
            return
        try:
            with sqlite3.connect(self.sqlite_db_path) as conn:
                cur = conn.cursor()
                for el in elements:
                    # Support both dict and DismantledElement dataclass
                    if hasattr(el, "id"):
                        eid, tag, role = el.id, el.tag, el.accessibility.get("role", "")
                        ctype = el.component_type
                        text = el.text
                        sel, xp = el.selector, el.xpath
                        bx, by, bw, bh = el.box.x, el.box.y, el.box.width, el.box.height
                        is_inter = 1 if el.is_interactive else 0
                        is_vis = 1 if el.is_visible else 0
                        is_vp = 1 if el.is_in_viewport else 0
                        depth = el.depth
                    else:
                        eid = el.get("id", "")
                        tag = el.get("tag", "")
                        role = el.get("accessibility", {}).get("role", "")
                        ctype = el.get("component_type", "")
                        text = el.get("text", "")
                        sel = el.get("selector", "")
                        xp = el.get("xpath", "")
                        box = el.get("box", {})
                        bx, by, bw, bh = box.get("x", 0), box.get("y", 0), box.get("width", 0), box.get("height", 0)
                        is_inter = 1 if el.get("is_interactive") else 0
                        is_vis = 1 if el.get("is_visible") else 0
                        is_vp = 1 if el.get("is_in_viewport") else 0
                        depth = el.get("depth", 0)

                    cur.execute("""
                        INSERT OR REPLACE INTO elements
                        (id, tag, role, component_type, text, selector, xpath, bbox_x, bbox_y, bbox_w, bbox_h, is_interactive, is_visible, is_in_viewport, depth)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (eid, tag, role, ctype, text, sel, xp, bx, by, bw, bh, is_inter, is_vis, is_vp, depth))
                conn.commit()
        except Exception as e:
            logger.warning(f"Failed to index elements in SQLite: {e}")

    def index_sitemap_sqlite(self, pages: list[Any]) -> None:
        """Populates SQLite sitemap table."""
        if not self.config.storage.build_sqlite_index:
            return
        try:
            with sqlite3.connect(self.sqlite_db_path) as conn:
                cur = conn.cursor()
                for p in pages:
                    if hasattr(p, "url"):
                        url = p.url
                        title = p.title
                        depth = p.depth
                        status = p.status_code
                        in_links = len(p.internal_links)
                        ex_links = len(p.external_links)
                        h1 = p.h1
                        desc = p.meta_description
                    else:
                        url = p.get("url", "")
                        title = p.get("title", "")
                        depth = p.get("depth", 0)
                        status = p.get("status", 200)
                        in_links = p.get("internal_links", 0)
                        ex_links = p.get("external_links", 0)
                        h1 = p.get("h1", "")
                        desc = p.get("meta_description", "")

                    cur.execute("""
                        INSERT OR REPLACE INTO sitemap
                        (url, title, depth, status, internal_links_count, external_links_count, h1, meta_description)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (url, title, depth, status, in_links, ex_links, h1, desc))
                conn.commit()
        except Exception as e:
            logger.warning(f"Failed to index sitemap in SQLite: {e}")

    # -----------------------------------------------------------------------
    # Asset storage & Content Deduplication
    # -----------------------------------------------------------------------

    def _asset_category(self, mime: str) -> str:
        mime_lower = mime.lower().split(";")[0].strip()
        for cat, mimes in MIME_CATEGORIES.items():
            if mime_lower in mimes:
                return cat
        if mime_lower.startswith("image/"):
            return "image"
        if mime_lower.startswith("font/"):
            return "font"
        if mime_lower.startswith("video/"):
            return "video"
        if mime_lower.startswith("audio/"):
            return "audio"
        return "other"

    def _ext_from_mime(self, mime: str) -> str:
        ext = mimetypes.guess_extension(mime.split(";")[0].strip())
        if ext in (".jpe", ".jpeg"):
            ext = ".jpg"
        return ext or ".bin"

    def process_asset(self, url: str, body: str, base64_encoded: bool,
                      mime: str, base_url: str = "") -> dict:
        """
        Process an asset with SHA-256 content deduplication and user format preferences.
        """
        category = self._asset_category(mime)

        # Decode body to raw bytes
        if base64_encoded:
            try:
                raw_bytes = base64.b64decode(body)
            except Exception:
                raw_bytes = body.encode("latin-1", errors="replace")
        else:
            raw_bytes = body.encode("utf-8", errors="replace")

        # SHA-256 hash of content
        content_hash = hashlib.sha256(raw_bytes).hexdigest()[:16]
        ext = self._ext_from_mime(mime)
        filename = f"{content_hash}{ext}"

        record = {
            "url": url,
            "category": category,
            "mime": mime,
            "size_bytes": len(raw_bytes),
            "hash": content_hash,
            "filename": filename,
            "deduplicated": False,
        }

        storage_fmt = self._get_storage_format(category)

        # Content-hash deduplication: check if identical asset content already exists
        if self.config.storage.deduplicate_assets and content_hash in self._seen_content_hashes:
            cached = self._seen_content_hashes[content_hash]
            record["local_path"] = cached["local_path"]
            record["site_relative_path"] = cached["site_relative_path"]
            record["deduplicated"] = True
            logger.debug(f"Asset deduplicated: {url} -> {filename}")
        elif storage_fmt in ("raw", "both"):
            cat_folder = category + "s" if not category.endswith("s") else category
            cat_dir = self.assets_dir / cat_folder
            cat_dir.mkdir(exist_ok=True)
            file_path = cat_dir / filename
            file_path.write_bytes(raw_bytes)

            local_path = str(file_path.relative_to(self.root)).replace("\\", "/")
            site_rel_path = f"assets/{cat_folder}/{filename}"
            record["local_path"] = local_path
            record["site_relative_path"] = site_rel_path

            self._seen_content_hashes[content_hash] = {
                "local_path": local_path,
                "site_relative_path": site_rel_path,
            }

        if storage_fmt in ("base64", "both"):
            b64 = base64.b64encode(raw_bytes).decode()
            record["data_uri"] = f"data:{mime};base64,{b64}"
            record["base64"] = b64

        if storage_fmt == "url":
            record["external_url"] = url
            record["data_uri"] = url

        return record

    def _get_storage_format(self, category: str) -> str:
        cfg = self.config.storage
        if category == "image":
            return cfg.images.value
        if category == "font":
            return cfg.fonts.value
        if category == "video":
            return cfg.videos.value
        return "base64"

    # -----------------------------------------------------------------------
    # File Writers
    # -----------------------------------------------------------------------

    def write_json(self, name: str, data: Any) -> Path:
        """Write a JSON file to the data_structure directory."""
        path = self.data_dir / f"{name}.json"
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        return path

    def write_jsonl(self, name: str, records: list[Any]) -> Path:
        """Write a JSONL file (one record per line) to the data_structure directory."""
        path = self.data_dir / f"{name}.jsonl"
        lines = []
        for r in records:
            if hasattr(r, "__dataclass_fields__"):
                r_dict = asdict(r)
            elif isinstance(r, dict):
                r_dict = r
            else:
                r_dict = getattr(r, "__dict__", str(r))
            lines.append(json.dumps(r_dict, ensure_ascii=False, default=str))

        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    def write_data(self, name: str, data: Any) -> list[Path]:
        """Write data in the configured format (json, jsonl, or both)."""
        fmt = self.config.storage.data_format
        paths = []
        records = data if isinstance(data, list) else [data]
        if fmt.value in ("json", "both"):
            paths.append(self.write_json(name, data))
        if fmt.value in ("jsonl", "both"):
            paths.append(self.write_jsonl(name, records))
        return paths

    def write_manifest(self, meta: dict, url: str, elapsed_sec: float,
                       asset_count: int, fidelity: Optional[dict] = None,
                       analysis_summary: Optional[dict] = None) -> Path:
        """Write the manifest.json with clone metadata."""
        manifest = {
            "version": "2.0",
            "cloned_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "target_url": url,
            "site_folder": str(self.site_dir.relative_to(self.root)).replace("\\", "/"),
            "data_folder": str(self.data_dir.relative_to(self.root)).replace("\\", "/"),
            "elapsed_seconds": round(elapsed_sec, 2),
            "asset_count": asset_count,
            "page_title": meta.get("title", ""),
            "page_lang": meta.get("lang", ""),
            "canonical": meta.get("canonical", ""),
            "favicon": meta.get("favicon", ""),
            "fidelity": fidelity,
            "analysis": analysis_summary or {},
            "storage": {
                "images": self.config.storage.images.value,
                "fonts": self.config.storage.fonts.value,
                "videos": self.config.storage.videos.value,
                "data_format": self.config.storage.data_format.value,
                "deduplicate_assets": self.config.storage.deduplicate_assets,
                "sqlite_indexed": self.config.storage.build_sqlite_index,
            },
            "engine": self.config.browser.primary_engine.value,
        }
        path = self.data_dir / "manifest.json"
        path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return path

    def write_html(self, html: str, filename: str = "index.html") -> Path:
        """Write the main cloned HTML file into the site folder."""
        path = self.site_dir / filename
        path.write_text(html, encoding="utf-8")
        return path
