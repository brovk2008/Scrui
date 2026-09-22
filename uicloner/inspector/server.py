"""
Scrui Visual Diff & Telemetry Inspector Server.
Spins up a local Cyberpunk-themed dashboard to visually compare original vs. clone,
inspect extracted design tokens, preview pixel diffs, and browse generated prompts.
"""
from __future__ import annotations

import http.server
import json
import logging
import mimetypes
import os
import socketserver
import webbrowser
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class InspectorHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler serving the inspector dashboard and clone data."""

    clone_dir: Path
    html_template_path: Path

    def do_GET(self):
        url_path = self.path.split("?")[0]

        if url_path == "/" or url_path == "/index.html":
            self._serve_dashboard()
        elif url_path == "/api/data":
            self._serve_api_data()
        elif url_path == "/site" or url_path == "/preview":
            self._serve_cloned_site()
        else:
            # Fallback to serving assets from clone directory
            file_path = self.clone_dir / url_path.lstrip("/")
            if file_path.exists() and file_path.is_file():
                self._serve_file(file_path)
            else:
                self.send_error(404, f"File not found: {url_path}")

    def _serve_dashboard(self):
        try:
            with open(self.html_template_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        except Exception as e:
            self.send_error(500, f"Error rendering dashboard: {e}")

    def _serve_api_data(self):
        data: Dict[str, Any] = {
            "clone_dir": str(self.clone_dir),
            "manifest": self._load_json("data_structure/manifest.json"),
            "preflight": self._load_json("data_structure/preflight.json"),
            "design_system": self._load_json("data_structure/design_system.json"),
            "tokens": self._load_json("data_structure/tokens.json"),
            "components": self._load_json("data_structure/components.json"),
            "prompt": self._load_text("data_structure/prompt/PROMPT.md"),
            "spec": self._load_text("data_structure/prompt/SPEC.md"),
            "components_schema": self._load_json("data_structure/prompt/components_schema.json"),
        }

        # Find cloned HTML path
        cloned_html = list(self.clone_dir.glob("*/index.html"))
        if cloned_html:
            data["cloned_html_rel"] = f"/{cloned_html[0].parent.name}/index.html"

        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _serve_cloned_site(self):
        cloned_html = list(self.clone_dir.glob("*/index.html"))
        if cloned_html:
            self._serve_file(cloned_html[0])
        else:
            self.send_error(404, "No cloned index.html found in this directory.")

    def _serve_file(self, path: Path):
        mime, _ = mimetypes.guess_type(str(path))
        mime = mime or "application/octet-stream"
        try:
            with open(path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error reading file: {e}")

    def _load_json(self, rel_path: str) -> Optional[Dict[str, Any]]:
        p = self.clone_dir / rel_path
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return None

    def _load_text(self, rel_path: str) -> Optional[str]:
        p = self.clone_dir / rel_path
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
        return None


def resolve_clone_directory(target_path: Optional[Path] = None) -> Path:
    """Finds the most appropriate clone directory to inspect."""
    if target_path and target_path.exists():
        if (target_path / "data_structure").exists() or list(target_path.glob("*/index.html")):
            return target_path.resolve()
        # If target_path is the base 'clones/' folder, pick the most recent subfolder
        subfolders = sorted(
            [p for p in target_path.iterdir() if p.is_dir() and p.name.startswith("site_cloned_")],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if subfolders:
            return subfolders[0].resolve()

    # Search in default ./clones/
    default_base = Path("clones")
    if default_base.exists():
        subfolders = sorted(
            [p for p in default_base.iterdir() if p.is_dir() and p.name.startswith("site_cloned_")],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if subfolders:
            return subfolders[0].resolve()

    return Path(".").resolve()


def launch_inspector(
    target_dir: Optional[Path] = None,
    port: int = 3888,
    open_browser: bool = True,
) -> None:
    """Starts the Scrui Visual Inspector HTTP server."""
    clone_dir = resolve_clone_directory(target_dir)
    template_path = Path(__file__).parent / "templates" / "dashboard.html"

    # Configure handler
    class ConfiguredHandler(InspectorHandler):
        pass

    ConfiguredHandler.clone_dir = clone_dir
    ConfiguredHandler.html_template_path = template_path

    url = f"http://127.0.0.1:{port}"
    print(f"\n[Scrui Inspector] Serving dashboard for: {clone_dir.name}")
    print(f"[Scrui Inspector] Local URL: {url}\n")

    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    with socketserver.TCPServer(("127.0.0.1", port), ConfiguredHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[Scrui Inspector] Shutting down.")
            httpd.server_close()
