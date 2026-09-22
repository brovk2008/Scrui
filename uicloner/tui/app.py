"""
UI Cloner — Interactive Terminal UI
Built with Textual. Navigate with keyboard:
  Tab / Arrow keys — navigate
  Enter — select / confirm
  S — settings
  Q / Ctrl+C — quit
"""
from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path
from typing import Optional

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.reactive import reactive
from textual.widgets import (
    Button, DataTable, Footer, Header, Input, Label,
    ProgressBar, RichLog, Select, Static, Switch, TabbedContent,
    TabPane,
)
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.console import Console


BANNER = r"""
 ▄███████▄   ▄███████▄  ████████▄   ██      ██  ██
 ██▀     ▀   ██▀     ▀  ██     ██   ██      ██  ██
 ████████▄   ██         ████████▀   ██      ██  ██
       ▀██   ██▄     ▄  ██   ▀██▄   ██      ██  ██
 ████████▀   ▀███████▀  ██     ██▄  ▀████████▀  ██
       S C R U I — Predictive UI Extraction & Cloning Engine v2.0
"""


class URLInputPanel(Static):
    """URL input and quick-launch panel."""

    DEFAULT_CSS = """
    URLInputPanel {
        border: solid $accent;
        padding: 1 2;
        margin: 0 0 1 0;
    }
    URLInputPanel #url-label { color: $accent; text-style: bold; }
    URLInputPanel #url-input { margin: 1 0; }
    URLInputPanel #batch-label { color: $text-muted; }
    """

    def compose(self) -> ComposeResult:
        yield Label("🌐  Target URL", id="url-label")
        yield Input(
            placeholder="https://example.com",
            id="url-input",
        )
        yield Horizontal(
            Button("⚡ Clone Now", id="btn-clone", variant="primary"),
            Button("📂 Batch File...", id="btn-batch", variant="default"),
            Button("📋 History", id="btn-history", variant="default"),
            id="url-actions",
        )
        yield Label("", id="batch-label")

    def get_url(self) -> str:
        return self.query_one("#url-input", Input).value.strip()

    def set_batch_label(self, text: str) -> None:
        self.query_one("#batch-label", Label).update(text)


class ProgressPanel(Static):
    """Shows current clone progress across all pipeline stages."""

    STAGES = [
        ("init",         "Init"),
        ("browser",      "Browser"),
        ("navigate",     "Navigate"),
        ("captcha",      "CAPTCHA"),
        ("dom",          "DOM Capture"),
        ("shadow",       "Shadow DOM"),
        ("events",       "Events"),
        ("animations",   "Animations"),
        ("canvas",       "Canvas/WebGL"),
        ("process",      "Assets"),
        ("deobfuscate",  "Deobfuscation"),
        ("screenshot",   "Screenshot"),
        ("pack",         "HTML Pack"),
        ("validate",     "Validation"),
        ("data",         "Data Write"),
        ("done",         "Complete"),
    ]

    DEFAULT_CSS = """
    ProgressPanel {
        border: solid $success;
        padding: 1 2;
        display: none;
    }
    ProgressPanel.active { display: block; }
    ProgressPanel .stage-label { color: $text-muted; }
    ProgressPanel .stage-label.current { color: $warning; text-style: bold; }
    ProgressPanel .stage-label.done { color: $success; }
    ProgressPanel #main-progress { margin: 1 0; }
    """

    current_step: reactive[str] = reactive("")
    current_msg: reactive[str] = reactive("")

    def compose(self) -> ComposeResult:
        yield Label("⚡ Cloning in progress...", id="progress-title")
        yield ProgressBar(total=100, show_eta=False, id="main-progress")
        yield Label("", id="step-label")
        yield RichLog(id="progress-log", max_lines=12, markup=True, highlight=True)

    def update_progress(self, step: str, pct: float, msg: str) -> None:
        try:
            bar = self.query_one("#main-progress", ProgressBar)
            bar.update(progress=int(pct * 100))
            self.query_one("#step-label", Label).update(f"→ {step.upper()}: {msg}")
            log = self.query_one("#progress-log", RichLog)
            color = "green" if pct >= 1.0 else "yellow" if pct > 0.5 else "cyan"
            log.write(f"[{color}]{step:15}[/{color}] [white]{msg}[/white]")
        except Exception:
            pass


class ResultsPanel(Static):
    """Display results of completed clones."""

    DEFAULT_CSS = """
    ResultsPanel {
        border: solid $primary;
        padding: 1 2;
        display: none;
    }
    ResultsPanel.visible { display: block; }
    ResultsPanel .score-good { color: $success; text-style: bold; }
    ResultsPanel .score-bad { color: $error; text-style: bold; }
    """

    def compose(self) -> ComposeResult:
        yield Label("✅ Clone Results", id="results-title")
        yield DataTable(id="results-table")

    def on_mount(self) -> None:
        table = self.query_one("#results-table", DataTable)
        table.add_columns("URL", "Status", "Fidelity", "Assets", "Time", "Output")

    def add_result(self, result) -> None:
        table = self.query_one("#results-table", DataTable)
        status = "✅ Done" if result.success else "❌ Failed"
        fidelity = f"{result.fidelity_score:.1f}%" if result.fidelity_score else "—"
        assets = str(result.stats.get("assets", 0)) if result.success else "—"
        elapsed = f"{result.elapsed_sec:.1f}s"
        output = str(result.output_dir) if result.output_dir else "—"
        url_short = result.url[:40] + "…" if len(result.url) > 40 else result.url
        table.add_row(url_short, status, fidelity, assets, elapsed, output)
        self.add_class("visible")


class SettingsScreen(Static):
    """Settings panel for all configurable options."""

    DEFAULT_CSS = """
    SettingsScreen {
        border: solid $accent;
        padding: 1 2;
        height: auto;
    }
    SettingsScreen .section-title {
        color: $accent; text-style: bold; margin: 1 0 0 0;
    }
    SettingsScreen .setting-row { margin: 0 0 1 0; }
    """

    def compose(self) -> ComposeResult:
        from uicloner.config import get_config
        cfg = get_config()

        yield Label("⚙️  Settings", classes="section-title")
        yield Label("──────── Browser ────────", classes="section-title")

        yield Horizontal(
            Label("Primary Engine:", classes="setting-row"),
            Select(
                [("nodriver", "nodriver"), ("patchright", "patchright"), ("camoufox", "camoufox")],
                value=cfg.browser.primary_engine.value,
                id="sel-engine",
            ),
        )
        yield Horizontal(
            Label("Headless:"),
            Switch(value=cfg.browser.headless, id="sw-headless"),
        )

        yield Label("──────── Storage ────────", classes="section-title")
        yield Horizontal(
            Label("Images:"),
            Select(
                [("base64", "Base64 inline"), ("raw", "Raw files"), ("both", "Both"), ("url", "Keep URL")],
                value=cfg.storage.images.value, id="sel-images",
            ),
        )
        yield Horizontal(
            Label("Fonts:"),
            Select(
                [("base64", "Base64 inline"), ("raw", "Raw files"), ("url", "Keep URL")],
                value=cfg.storage.fonts.value, id="sel-fonts",
            ),
        )
        yield Horizontal(
            Label("Videos:"),
            Select(
                [("raw", "Raw files"), ("url", "Keep URL")],
                value=cfg.storage.videos.value, id="sel-videos",
            ),
        )
        yield Horizontal(
            Label("Data Format:"),
            Select(
                [("jsonl", "JSONL (streaming)"), ("json", "JSON"), ("both", "Both")],
                value=cfg.storage.data_format.value, id="sel-data-fmt",
            ),
        )

        yield Label("──────── Network ────────", classes="section-title")
        yield Horizontal(
            Label("Proxy Tier:"),
            Select(
                [("none", "None (direct)"), ("residential", "Residential"), ("isp", "ISP"), ("datacenter", "Datacenter")],
                value=cfg.network.proxy_tier.value, id="sel-proxy",
            ),
        )
        yield Horizontal(
            Label("Proxy List (host:port or host:port:user:pass, one per line):"),
        )
        yield Input(placeholder="proxy1:port\nproxy2:port:user:pass", id="inp-proxies")

        yield Label("──────── APIs ────────", classes="section-title")
        yield Horizontal(
            Label("HuggingFace API Key:"),
            Input(placeholder="hf_...", password=True, id="inp-hf-key"),
        )
        yield Horizontal(
            Label("2captcha Key:"),
            Input(placeholder="your_key", password=True, id="inp-2captcha"),
        )
        yield Horizontal(
            Label("Enable CAPTCHA solving:"),
            Switch(id="sw-captcha"),
        )

        yield Label("──────── Extraction ────────", classes="section-title")
        yield Horizontal(Label("Shadow DOM:"), Switch(value=True, id="sw-shadow"))
        yield Horizontal(Label("Event Listeners:"), Switch(value=True, id="sw-events"))
        yield Horizontal(Label("Animations:"), Switch(value=True, id="sw-anim"))
        yield Horizontal(Label("Canvas/WebGL:"), Switch(value=True, id="sw-canvas"))
        yield Horizontal(Label("JS Deobfuscation:"), Switch(value=True, id="sw-deob"))

        yield Label("──────── Output ────────", classes="section-title")
        yield Horizontal(
            Label("Output Directory:"),
            Input(placeholder="./clones", value=str(cfg.output.base_dir), id="inp-output-dir"),
        )
        yield Horizontal(Label("Embed rrweb replay:"), Switch(value=True, id="sw-rrweb"))
        yield Horizontal(Label("Run VLM check:"), Switch(value=False, id="sw-vlm"))

        yield Button("💾 Save Settings", id="btn-save-settings", variant="success")

    def collect_config_updates(self) -> dict:
        """Collect all widget values for config update."""
        def val(widget_id: str, default=None):
            try:
                w = self.query_one(f"#{widget_id}")
                if isinstance(w, Select):
                    return w.value
                if isinstance(w, Switch):
                    return w.value
                if isinstance(w, Input):
                    return w.value.strip()
                return default
            except Exception:
                return default

        return {
            "engine": val("sel-engine", "nodriver"),
            "headless": val("sw-headless", False),
            "images": val("sel-images", "base64"),
            "fonts": val("sel-fonts", "base64"),
            "videos": val("sel-videos", "raw"),
            "data_format": val("sel-data-fmt", "jsonl"),
            "proxy_tier": val("sel-proxy", "none"),
            "proxies": val("inp-proxies", ""),
            "hf_key": val("inp-hf-key", ""),
            "two_captcha": val("inp-2captcha", ""),
            "captcha_enabled": val("sw-captcha", False),
            "shadow": val("sw-shadow", True),
            "events": val("sw-events", True),
            "anim": val("sw-anim", True),
            "canvas": val("sw-canvas", True),
            "deob": val("sw-deob", True),
            "output_dir": val("inp-output-dir", "./clones"),
            "rrweb": val("sw-rrweb", True),
            "vlm": val("sw-vlm", False),
        }


class UICloneApp(App):
    """Main Textual TUI Application."""

    TITLE = "UI Cloner v2.0"
    CSS_PATH = None
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("ctrl+s", "save_settings", "Save Settings"),
        Binding("f1", "show_help", "Help"),
        Binding("escape", "back", "Back", show=False),
    ]

    CSS = """
    Screen {
        background: $background;
    }
    .banner {
        color: $accent;
        text-style: bold;
        text-align: center;
        padding: 0 0 1 0;
    }
    #main-tabs {
        height: 1fr;
    }
    #tab-clone {
        padding: 1;
    }
    #tab-settings {
        padding: 1;
    }
    #tab-results {
        padding: 1;
    }
    #batch-status {
        color: $warning;
        padding: 0 0 1 0;
    }
    .section-sep {
        color: $accent-darken-2;
        height: 1;
        margin: 1 0;
    }
    Button {
        margin: 0 1;
    }
    """

    _batch_urls: list[str] = []
    _config = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield ScrollableContainer(
            Static(BANNER, classes="banner"),
            TabbedContent(
                TabPane("🎯 Clone", id="tab-clone"),
                TabPane("⚙️ Settings", id="tab-settings"),
                TabPane("📊 Results", id="tab-results"),
                id="main-tabs",
            ),
        )
        yield Footer()

    def _compose_clone_tab(self):
        return [
            URLInputPanel(id="url-panel"),
            Label("", id="batch-status"),
            ProgressPanel(id="progress-panel"),
        ]

    def on_mount(self) -> None:
        from uicloner.config import get_config
        self._config = get_config()
        self.title = "UI Cloner v2.0 — High-Fidelity Extraction Engine"
        self.sub_title = "nodriver | Patchright | Camoufox | HuggingFace | 2captcha"

        # Populate tab content after mount (TabbedContent limitation workaround)
        clone_tab = self.query_one("#tab-clone", TabPane)
        clone_tab.mount(URLInputPanel(id="url-panel"))
        clone_tab.mount(Label("", id="batch-status"))
        clone_tab.mount(ProgressPanel(id="progress-panel"))

        settings_tab = self.query_one("#tab-settings", TabPane)
        settings_tab.mount(ScrollableContainer(SettingsScreen(id="settings-panel")))

        results_tab = self.query_one("#tab-results", TabPane)
        results_tab.mount(ResultsPanel(id="results-panel"))

    @on(Button.Pressed, "#btn-clone")
    def clone_now(self) -> None:
        url_panel = self.query_one("#url-panel", URLInputPanel)
        url = url_panel.get_url()
        if url:
            self._start_clone([url])
        else:
            self.notify("Please enter a URL", severity="warning")

    @on(Button.Pressed, "#btn-batch")
    def open_batch(self) -> None:
        self.notify("Enter path to .txt file with URLs (one per line):", severity="information")
        # Show input dialog (simplified - use notification for now)
        # In production this would open a file picker
        self.app.push_screen(BatchFileDialog(callback=self._load_batch_file))

    @on(Button.Pressed, "#btn-history")
    def show_history(self) -> None:
        self.query_one("#main-tabs").active = "tab-results"

    @on(Button.Pressed, "#btn-save-settings")
    def save_settings(self) -> None:
        settings = self.query_one("#settings-panel", SettingsScreen)
        updates = settings.collect_config_updates()
        self._apply_config_updates(updates)
        self.notify("✅ Settings saved!", severity="information")

    def _apply_config_updates(self, updates: dict) -> None:
        from uicloner.config import (
            UICloneConfig, BrowserEngine, ProxyTier,
            ImageStorageFormat, FontStorageFormat, VideoStorageFormat, OutputDataFormat,
            set_config,
        )
        cfg = self._config

        cfg.browser.primary_engine = BrowserEngine(updates["engine"])
        cfg.browser.headless = updates["headless"]
        cfg.storage.images = ImageStorageFormat(updates["images"])
        cfg.storage.fonts = FontStorageFormat(updates["fonts"])
        cfg.storage.videos = VideoStorageFormat(updates["videos"])
        cfg.storage.data_format = OutputDataFormat(updates["data_format"])
        cfg.network.proxy_tier = ProxyTier(updates["proxy_tier"])

        proxies = [p.strip() for p in updates["proxies"].split("\n") if p.strip()]
        cfg.network.proxy_list = proxies

        if updates["hf_key"]:
            cfg.huggingface.api_key = updates["hf_key"]
        if updates["two_captcha"]:
            cfg.captcha.two_captcha_api_key = updates["two_captcha"]
        cfg.captcha.enabled = updates["captcha_enabled"]

        cfg.extraction.capture_shadow_dom = updates["shadow"]
        cfg.extraction.extract_event_listeners = updates["events"]
        cfg.extraction.extract_animations = updates["anim"]
        cfg.extraction.capture_canvas = updates["canvas"]
        cfg.extraction.js_deobfuscate = updates["deob"]
        cfg.output.base_dir = Path(updates["output_dir"])
        cfg.output.embed_rrweb_replay = updates["rrweb"]
        cfg.validation.run_vlm_check = updates["vlm"]

        set_config(cfg)
        cfg.save_yaml(Path("config.yaml"))

    def _load_batch_file(self, filepath: str) -> None:
        try:
            p = Path(filepath)
            if p.exists():
                urls = [line.strip() for line in p.read_text().splitlines()
                        if line.strip() and not line.startswith("#")]
                self._batch_urls = urls
                self.query_one("#url-panel", URLInputPanel).set_batch_label(
                    f"📋 Batch loaded: {len(urls)} URLs from {p.name}"
                )
                self.notify(f"Loaded {len(urls)} URLs", severity="information")
        except Exception as e:
            self.notify(f"Failed to load batch file: {e}", severity="error")

    @work(exclusive=False, thread=False)
    async def _start_clone(self, urls: list[str]) -> None:
        from uicloner.orchestrator import run_clone, run_batch

        progress_panel = self.query_one("#progress-panel", ProgressPanel)
        progress_panel.add_class("active")

        def on_progress(step: str, pct: float, msg: str):
            self.call_from_thread(progress_panel.update_progress, step, pct, msg)

        if len(urls) == 1:
            result = await run_clone(urls[0], self._config, on_progress)
            results = [result]
        else:
            results = await run_batch(urls, self._config, on_progress)

        # Show results
        results_panel = self.query_one("#results-panel", ResultsPanel)
        for r in results:
            results_panel.add_result(r)

        # Show notification
        success_count = sum(1 for r in results if r.success)
        if success_count == len(results):
            self.notify(f"✅ {success_count} clone(s) complete!", severity="information")
        else:
            self.notify(
                f"⚠️ {success_count}/{len(results)} succeeded",
                severity="warning"
            )

        # Switch to results tab
        self.query_one("#main-tabs").active = "tab-results"
        progress_panel.remove_class("active")

    def action_show_help(self) -> None:
        self.notify(
            "Tab: navigate | Enter: select | Ctrl+S: save settings | Ctrl+Q: quit",
            severity="information", timeout=5,
        )

    def action_back(self) -> None:
        pass

    def action_save_settings(self) -> None:
        try:
            settings = self.query_one("#settings-panel", SettingsScreen)
            updates = settings.collect_config_updates()
            self._apply_config_updates(updates)
            self.notify("✅ Settings saved!", severity="information")
        except Exception as e:
            self.notify(f"Save failed: {e}", severity="error")


class BatchFileDialog(App):
    """Simple inline dialog for batch file path input."""

    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self._callback = callback

    def compose(self) -> ComposeResult:
        yield Label("Enter path to batch URL file (.txt):")
        yield Input(placeholder="/path/to/urls.txt", id="filepath-input")
        yield Horizontal(
            Button("Open", id="btn-open", variant="primary"),
            Button("Cancel", id="btn-cancel"),
        )

    @on(Button.Pressed, "#btn-open")
    def do_open(self) -> None:
        path = self.query_one("#filepath-input", Input).value
        self._callback(path)
        self.app.pop_screen()

    @on(Button.Pressed, "#btn-cancel")
    def do_cancel(self) -> None:
        self.app.pop_screen()


def run_tui():
    """Launch the Textual TUI."""
    app = UICloneApp()
    app.run()
