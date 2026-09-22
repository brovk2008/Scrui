"""
Scrui Local Relay Server.
Listens for 1-click DOM/CSS dumps sent by the Scrui Chrome Extension.
Allows instant cloning of authenticated dashboards and Cloudflare-protected web pages.
"""
from __future__ import annotations

import asyncio
import http.server
import json
import logging
import socketserver
import time
from pathlib import Path
from urllib.parse import urlparse
from typing import Any, Dict, Optional

from uicloner.config import UICloneConfig
from uicloner.output.serializer import OutputSerializer
from uicloner.output.packer import build_single_file_html
from uicloner.analyzer.dismantler import UIDismantler
from uicloner.analyzer.token_exporter import save_tokens_bundle
from uicloner.layers.layer5_prompt import generate_ui_prompt

logger = logging.getLogger(__name__)


class RelayHandler(http.server.BaseHTTPRequestHandler):
    """HTTP handler receiving extension payloads and triggering Scrui processing."""

    config: UICloneConfig
    on_payload_received: Optional[Any] = None

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/status" or self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "active", "engine": "Scrui Local Relay v2.5"}).encode("utf-8"))
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/relay" or self.path == "/api/dump":
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len)

            try:
                payload = json.loads(post_body.decode("utf-8"))
                target_url = payload.get("url", "https://authenticated-tab.local")
                outer_html = payload.get("html", "")
                title = payload.get("title", "Captured Tab")

                print(f"\n[Scrui Relay] Received 1-click tab capture from Chrome Extension!")
                print(f"[Scrui Relay] Target: {target_url} ({title})")
                print(f"[Scrui Relay] HTML Size: {len(outer_html):,} bytes")

                # Process dump through Scrui pipeline
                result = self._process_dump(target_url, outer_html, payload)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "success",
                    "output_dir": str(result.get("output_dir")),
                    "prompt_path": str(result.get("prompt_path")),
                }).encode("utf-8"))

            except Exception as e:
                logger.exception("Error processing relay payload")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
        else:
            self.send_error(404)

    def _process_dump(self, url: str, outer_html: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Scrui Layers on the received tab dump."""
        config = self.config
        serializer = OutputSerializer(config, url)

        # 1. Run Dismantler
        dismantler = UIDismantler(url, config)
        dismantle_report = dismantler.dismantle_html_string(outer_html)

        # 2. Package single-file HTML
        cloned_html = build_single_file_html(outer_html, [], {})

        # 3. Write site clone and data structure
        serializer.write_cloned_site(cloned_html)
        serializer.write_dismantle_report(dismantle_report)

        # 4. Save W3C DTCG / Figma Tokens
        if dismantle_report.design_system:
            save_tokens_bundle(dismantle_report.design_system, serializer.data_dir)

        # 5. Generate Master Prompt
        prompt_path = None
        bundle = generate_ui_prompt(
            url=url,
            config=config,
            dom_data={"outer_html": outer_html},
            dismantle_report=dismantle_report,
        )
        serializer.write_prompt_bundle(
            master_prompt=bundle.master_prompt,
            technical_spec=bundle.technical_spec,
            components_schema=bundle.components_schema,
        )
        prompt_path = serializer.prompt_dir / "PROMPT.md"

        print(f"[Scrui Relay] ✅ Processed successfully!")
        print(f"[Scrui Relay] Saved Clone: {serializer.site_dir / 'index.html'}")
        print(f"[Scrui Relay] Master Prompt: {prompt_path}\n")

        return {
            "output_dir": serializer.run_dir,
            "prompt_path": prompt_path,
        }


def start_relay_server(config: Optional[UICloneConfig] = None, port: int = 9222) -> None:
    """Run the Scrui Local Relay HTTP daemon."""
    if config is None:
        config = UICloneConfig.default()

    class ConfiguredRelay(RelayHandler):
        pass

    ConfiguredRelay.config = config

    print(f"\n========================================================")
    print(f" 🛰️  Scrui Extension Relay Server active on port {port}")
    print(f" Waiting for 1-click captures from Chrome/Brave Extension...")
    print(f" URL: http://127.0.0.1:{port}/relay")
    print(f" Press Ctrl+C to stop.")
    print(f"========================================================\n")

    with socketserver.TCPServer(("127.0.0.1", port), ConfiguredRelay) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[Scrui Relay] Stopped.")
            httpd.server_close()
