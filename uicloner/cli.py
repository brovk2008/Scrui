"""
UI Cloner CLI — Typer-based command-line interface.
Brand: Scrui (High-Fidelity Predictive UI Extraction & Cloning Engine v2.0)
Theme: 8-bit Electric Blue Logo + Neon Pink UI Cyber Aesthetic
Entry point: `uiclone`
"""
from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Optional

# Ensure standard UTF-8 console output for Windows cmd/powershell
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

# Color constants
COLOR_BLUE = "#00a2ff"     # 8-bit Electric Blue
COLOR_PINK = "#ff2a85"     # Cyber Neon Pink
COLOR_PINK_DIM = "#881a4a" # Muted Pink border/track

SCRUI_8BIT_BANNER = r"""
 ▄███████▄   ▄███████▄  ████████▄   ██      ██  ██
 ██▀     ▀   ██▀     ▀  ██     ██   ██      ██  ██
 ████████▄   ██         ████████▀   ██      ██  ██
       ▀██   ██▄     ▄  ██   ▀██▄   ██      ██  ██
 ████████▀   ▀███████▀  ██     ██▄  ▀████████▀  ██
"""

app = typer.Typer(
    name="uiclone",
    help="Scrui — High-Fidelity Predictive UI Extraction & Cloning Engine v2.0",
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console()


def print_banner() -> None:
    """Render the official Scrui 8-bit blue logo and pink tagline."""
    console.print(SCRUI_8BIT_BANNER, style=f"bold {COLOR_BLUE}")
    console.print(
        f"[bold {COLOR_BLUE}]   S   C   R   U   I[/bold {COLOR_BLUE}]  "
        f"[bold {COLOR_PINK}]■  PREDICTIVE UI EXTRACTION & CLONING ENGINE v2.0[/bold {COLOR_PINK}]\n"
    )


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s %(name)s: %(message)s")


@app.command("tui")
def launch_tui():
    """[bold #ff2a85]Launch the interactive Terminal UI.[/bold #ff2a85]"""
    print_banner()
    from uicloner.tui.app import run_tui
    run_tui()


@app.command("clone")
def clone_url(
    url: str = typer.Argument(..., help="Target URL to clone"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Config YAML path"),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
    engine: Optional[str] = typer.Option(None, "--engine", "-e", help="Browser engine (nodriver/patchright/camoufox)"),
    images: Optional[str] = typer.Option(None, "--images", help="Image storage: base64/raw/both/url"),
    fonts: Optional[str] = typer.Option(None, "--fonts", help="Font storage: base64/raw/url"),
    data_format: Optional[str] = typer.Option(None, "--data-format", "-f", help="Data format: jsonl/json/both"),
    no_shadow: bool = typer.Option(False, "--no-shadow", help="Skip Shadow DOM extraction"),
    no_events: bool = typer.Option(False, "--no-events", help="Skip event listener extraction"),
    no_animations: bool = typer.Option(False, "--no-animations", help="Skip animation extraction"),
    no_deob: bool = typer.Option(False, "--no-deob", help="Skip JS deobfuscation"),
    no_auto_correct: bool = typer.Option(False, "--no-auto-correct", help="Skip closed-loop visual auto-correction"),
    no_explore: bool = typer.Option(False, "--no-explore", help="Skip interactive behavioral state exploration"),
    no_preflight: bool = typer.Option(False, "--no-preflight", help="Skip Layer -1 pre-flight target profiling"),
    prompt: bool = typer.Option(False, "--prompt", help="Enable Layer 5: UI-to-Prompt synthesis"),
    prompt_target: Optional[str] = typer.Option(None, "--prompt-target", help="Prompt target: nextjs/react/v0/cursor/vue/svelte"),
    llm_provider: Optional[str] = typer.Option(None, "--llm-provider", help="LLM provider: groq/openrouter/gemini/huggingface/ollama"),
    hf_key: Optional[str] = typer.Option(None, "--hf-key", envvar="HF_API_KEY", help="HuggingFace API key"),
    captcha_key: Optional[str] = typer.Option(None, "--captcha-key", envvar="TWO_CAPTCHA_KEY", help="2captcha API key"),
    proxy: Optional[str] = typer.Option(None, "--proxy", "-p", help="Proxy: host:port or host:port:user:pass"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging"),
):
    """[bold #ff2a85]Clone a target URL with full UI fidelity and live predictive telemetry.[/bold #ff2a85]"""
    _setup_logging(verbose)
    print_banner()

    from uicloner.config import UICloneConfig, BrowserEngine, ImageStorageFormat, FontStorageFormat, OutputDataFormat, PromptTarget
    from uicloner.orchestrator import run_clone

    cfg = UICloneConfig.from_yaml(config_file) if config_file else UICloneConfig.default()

    # Apply CLI overrides
    if prompt:
        cfg.prompt_gen.enabled = True
    if prompt_target:
        cfg.prompt_gen.target = PromptTarget(prompt_target)
        cfg.prompt_gen.enabled = True
    if engine:
        cfg.browser.primary_engine = BrowserEngine(engine)
    if output_dir:
        cfg.output.base_dir = output_dir
    if images:
        cfg.storage.images = ImageStorageFormat(images)
    if fonts:
        cfg.storage.fonts = FontStorageFormat(fonts)
    if data_format:
        cfg.storage.data_format = OutputDataFormat(data_format)
    if no_shadow:
        cfg.extraction.capture_shadow_dom = False
    if no_events:
        cfg.extraction.extract_event_listeners = False
    if no_animations:
        cfg.extraction.extract_animations = False
    if no_deob:
        cfg.extraction.js_deobfuscate = False
    if no_auto_correct:
        cfg.validation.auto_correct = False
    if no_explore:
        cfg.analysis.explore_states = False
    if no_preflight:
        cfg.preflight.enabled = False
    if llm_provider:
        cfg.huggingface.provider = llm_provider
    if hf_key:
        cfg.huggingface.api_key = hf_key
    if captcha_key:
        cfg.captcha.two_captcha_api_key = captcha_key
        cfg.captcha.enabled = True
    if proxy:
        cfg.network.proxy_list = [proxy]

    # Pre-Flight profiling display
    if cfg.preflight.enabled:
        with console.status(f"[bold {COLOR_PINK}]Probing target & building predictive telemetry...[/bold {COLOR_PINK}]", spinner="dots", spinner_style=COLOR_PINK):
            from uicloner.layers.layer_preflight import PreflightProfiler, ExecutionTimelineEstimator
            profiler = PreflightProfiler(cfg)
            profile = asyncio.run(profiler.probe(url))
            estimator = ExecutionTimelineEstimator(cfg)
            plan = estimator.estimate(profile)

        # Print sleek pink preflight profile card
        pf_table = Table(
            title=f"[bold {COLOR_PINK}]⚡ LAYER -1: PRE-FLIGHT TELEMETRY PROFILE[/bold {COLOR_PINK}]",
            border_style=COLOR_PINK,
            header_style=f"bold {COLOR_PINK}",
        )
        pf_table.add_column("Diagnostic Metric", style=COLOR_PINK, width=24)
        pf_table.add_column("Detected Value / Prediction", style="white")

        pf_table.add_row("Target Host", f"{profile.host} (Latency: {profile.latency_ms:.0f}ms)")
        waf_style = "red" if profile.is_waf_protected else "green"
        pf_table.add_row("WAF / Edge CDN", f"[{waf_style}]{profile.cdn_waf}[/{waf_style}]")
        stack_str = ", ".join(profile.detected_frameworks) if profile.detected_frameworks else "Vanilla Web"
        pf_table.add_row("Detected Tech Stack", stack_str)
        pf_table.add_row(
            "Estimated Resources",
            f"~{profile.estimated_dom_nodes:,} nodes ({profile.scripts_count} scripts, {profile.styles_count} styles, {profile.images_count} media)"
        )
        pf_table.add_row(
            "Predicted Execution Time",
            f"[bold {COLOR_PINK}]~{plan.total_estimated_seconds:.1f}s[/bold {COLOR_PINK}] ({plan.complexity_level} Complexity, {len(plan.phases)} phases)"
        )
        console.print(pf_table)
        console.print()
    else:
        console.print(Panel.fit(
            f"[bold {COLOR_BLUE}]Target:[/bold {COLOR_BLUE}] {url}",
            border_style=COLOR_PINK,
        ))

    # Real-time progress bar with live ETA, % done, and granular operation tracking
    progress = Progress(
        SpinnerColumn(spinner_name="dots", style=COLOR_PINK),
        BarColumn(bar_width=32, style=COLOR_PINK_DIM, complete_style=COLOR_PINK, finished_style=f"bold {COLOR_PINK}"),
        TextColumn(f"[bold {COLOR_PINK}]{{task.percentage:>3.0f}}%[/bold {COLOR_PINK}]"),
        TimeElapsedColumn(),
        TextColumn(f"[bold {COLOR_PINK}]{{task.fields[eta]}}[/bold {COLOR_PINK}]"),
        TextColumn(f"[bold {COLOR_BLUE}]{{task.fields[layer]}}[/bold {COLOR_BLUE}] [white]{{task.fields[op]}}[/white]"),
        console=console,
    )

    with progress:
        task = progress.add_task(
            "Cloning",
            total=100,
            eta="Estimating...",
            layer="[Init]",
            op="Initializing engine...",
        )

        def on_progress(step: str, pct: float, msg: str, snapshot=None):
            if snapshot:
                progress.update(
                    task,
                    completed=int(snapshot.percent_done),
                    eta=snapshot.eta_formatted,
                    layer=f"[{snapshot.active_layer.split(':')[0]}]",
                    op=snapshot.current_operation,
                )
            else:
                progress.update(
                    task,
                    completed=int(pct * 100),
                    eta="",
                    layer=f"[{step}]",
                    op=msg,
                )

        result = asyncio.run(run_clone(url, cfg, on_progress))

    _print_result(result)


@app.command("batch")
def batch_clone(
    urls_file: Path = typer.Argument(..., help="Path to .txt file with one URL per line"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c"),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o"),
    concurrent: int = typer.Option(1, "--concurrent", "-n", help="Concurrent clones"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    """[bold #ff2a85]Clone multiple URLs from a text file.[/bold #ff2a85]"""
    _setup_logging(verbose)
    print_banner()

    if not urls_file.exists():
        console.print(f"[red]File not found: {urls_file}[/red]")
        raise typer.Exit(1)

    urls = [line.strip() for line in urls_file.read_text().splitlines()
            if line.strip() and not line.strip().startswith("#")]

    console.print(Panel.fit(
        f"[bold {COLOR_PINK}]Batch Cloning Pipeline[/bold {COLOR_PINK}]\n[dim]{len(urls)} URLs queued[/dim]",
        border_style=COLOR_PINK,
    ))

    from uicloner.config import UICloneConfig
    from uicloner.orchestrator import run_batch

    cfg = UICloneConfig.from_yaml(config_file) if config_file else UICloneConfig.default()
    if output_dir:
        cfg.output.base_dir = output_dir

    results = asyncio.run(run_batch(urls, cfg, max_concurrent=concurrent))

    table = Table(title="Batch Results", show_header=True, border_style=COLOR_PINK, header_style=f"bold {COLOR_PINK}")
    table.add_column("URL", overflow="fold", max_width=40)
    table.add_column("Status", justify="center")
    table.add_column("Fidelity", justify="right")
    table.add_column("Assets", justify="right")
    table.add_column("Time", justify="right")
    table.add_column("Output")

    for r in results:
        status = "[green]✅[/green]" if r.success else "[red]❌[/red]"
        fidelity = f"{r.fidelity_score:.1f}%" if r.fidelity_score else "—"
        assets = str(r.stats.get("assets", 0)) if r.success else "—"
        elapsed = f"{r.elapsed_sec:.1f}s"
        out = str(r.output_dir)[-40:] if r.output_dir else (r.error or "—")[:40]
        table.add_row(r.url[:40], status, fidelity, assets, elapsed, out)

    console.print(table)


@app.command("crawl")
def crawl_site(
    url: str = typer.Argument(..., help="Root URL to crawl"),
    max_pages: int = typer.Option(50, "--max-pages", "-m", help="Maximum pages to crawl"),
    max_depth: int = typer.Option(3, "--depth", "-d", help="Maximum crawl depth"),
    clone_all: bool = typer.Option(False, "--clone-all", help="Clone all discovered pages"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    """[bold #ff2a85]Crawl an entire site and build a comprehensive sitemap.[/bold #ff2a85]"""
    _setup_logging(verbose)
    print_banner()

    from uicloner.config import UICloneConfig
    from uicloner.orchestrator import run_site_crawl

    cfg = UICloneConfig.from_yaml(config_file) if config_file else UICloneConfig.default()
    cfg.crawler.enabled = True
    cfg.crawler.max_pages = max_pages
    cfg.crawler.max_depth = max_depth

    console.print(Panel.fit(
        f"[bold {COLOR_PINK}]Site Crawler & Sitemap Builder[/bold {COLOR_PINK}]\n"
        f"[dim]Root URL:[/dim] {url}\n"
        f"[dim]Max Pages:[/dim] {max_pages}  |  [dim]Max Depth:[/dim] {max_depth}  |  [dim]Clone All:[/dim] {clone_all}",
        border_style=COLOR_PINK,
    ))

    with Progress(
        SpinnerColumn(spinner_name="dots", style=COLOR_PINK),
        BarColumn(bar_width=32, style=COLOR_PINK_DIM, complete_style=COLOR_PINK, finished_style=f"bold {COLOR_PINK}"),
        TextColumn(f"[bold {COLOR_PINK}]{{task.percentage:>3.0f}}%[/bold {COLOR_PINK}]"),
        TimeElapsedColumn(),
        TextColumn("[white]{task.description}[/white]"),
        console=console,
    ) as progress:
        task = progress.add_task("Crawling...", total=100)

        def on_progress(step: str, pct: float, msg: str, snapshot=None):
            progress.update(task, completed=int(pct * 100),
                            description=f"[bold {COLOR_BLUE}]{step:10}[/bold {COLOR_BLUE}] {msg}")

        result = asyncio.run(run_site_crawl(url, cfg, on_progress, clone_discovered_pages=clone_all))

    sitemap_data = result.get("sitemap", {})
    pages = sitemap_data.get("pages", [])

    table = Table(title=f"Sitemap: {url} ({len(pages)} Pages Discovered)", border_style=COLOR_PINK, header_style=f"bold {COLOR_PINK}")
    table.add_column("URL", overflow="fold", max_width=50)
    table.add_column("Depth", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Title", overflow="fold", max_width=30)
    table.add_column("Internal Links", justify="right")

    for p in pages[:25]:
        status_color = "green" if p.get("status") == 200 else "yellow"
        table.add_row(
            p.get("url", "")[:50],
            str(p.get("depth", 0)),
            f"[{status_color}]{p.get('status', '—')}[/{status_color}]",
            (p.get("title") or "—")[:30],
            str(p.get("internal_links", 0)),
        )

    console.print(table)
    if len(pages) > 25:
        console.print(f"[dim]... and {len(pages) - 25} more pages saved in sitemap.json[/dim]")
    console.print(f"[green]✅ Full sitemap saved in: {result.get('output_dir')}[/green]")


@app.command("dismantle")
def dismantle_site(
    url: str = typer.Argument(..., help="Target URL to dismantle and analyze"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    """[bold #ff2a85]Dismantle and analyze each element, button, and design token on a site.[/bold #ff2a85]"""
    _setup_logging(verbose)
    print_banner()

    from uicloner.config import UICloneConfig
    from uicloner.orchestrator import run_clone

    cfg = UICloneConfig.from_yaml(config_file) if config_file else UICloneConfig.default()
    cfg.analysis.enabled = True

    console.print(Panel.fit(
        f"[bold {COLOR_PINK}]UI Element Dismantler & Reverse-Engineering Engine[/bold {COLOR_PINK}]\n[dim]Target:[/dim] {url}",
        border_style=COLOR_PINK,
    ))

    with Progress(
        SpinnerColumn(spinner_name="dots", style=COLOR_PINK),
        BarColumn(bar_width=32, style=COLOR_PINK_DIM, complete_style=COLOR_PINK, finished_style=f"bold {COLOR_PINK}"),
        TextColumn(f"[bold {COLOR_PINK}]{{task.percentage:>3.0f}}%[/bold {COLOR_PINK}]"),
        TimeElapsedColumn(),
        TextColumn(f"[bold {COLOR_BLUE}]{{task.description}}[/bold {COLOR_BLUE}]"),
        console=console,
    ) as progress:
        task = progress.add_task("Dismantling UI...", total=100)

        def on_progress(step: str, pct: float, msg: str, snapshot=None):
            progress.update(task, completed=int(pct * 100),
                            description=f"[{step:12}] {msg}")

        result = asyncio.run(run_clone(url, cfg, on_progress))

    _print_result(result)


@app.command("sitemap")
def build_sitemap(
    url: str = typer.Argument(..., help="Target URL to generate sitemap for"),
    max_pages: int = typer.Option(100, "--max-pages", "-m"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c"),
):
    """[bold #ff2a85]Generate full sitemap & link hierarchy for a site.[/bold #ff2a85]"""
    print_banner()
    from uicloner.config import UICloneConfig
    from uicloner.orchestrator import run_site_crawl

    cfg = UICloneConfig.from_yaml(config_file) if config_file else UICloneConfig.default()
    cfg.crawler.enabled = True
    cfg.crawler.max_pages = max_pages

    result = asyncio.run(run_site_crawl(url, cfg, None, clone_discovered_pages=False))
    console.print(f"[green]✅ Sitemap generated: {result.get('output_dir')}[/green]")


@app.command("prompt")
def prompt_site(
    url: str = typer.Argument(..., help="Target URL to synthesize into a Master AI Prompt"),
    target: str = typer.Option("nextjs", "--target", "-t", help="Target framework: nextjs/react/v0/cursor/vue/svelte"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Config YAML path"),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging"),
):
    """[bold #ff2a85]Synthesize any website UI into a Master Prompt for AI coding models (v0, Cursor, Next.js).[/bold #ff2a85]"""
    _setup_logging(verbose)
    print_banner()

    from uicloner.config import UICloneConfig, PromptTarget
    from uicloner.orchestrator import run_clone

    cfg = UICloneConfig.from_yaml(config_file) if config_file else UICloneConfig.default()
    cfg.prompt_gen.enabled = True
    cfg.prompt_gen.target = PromptTarget(target)
    if output_dir:
        cfg.output.base_dir = output_dir

    console.print(Panel.fit(
        f"[bold {COLOR_PINK}]UI-to-Prompt Synthesizer (Layer 5)[/bold {COLOR_PINK}]\n"
        f"[dim]Target:[/dim] {url}  |  [dim]Framework:[/dim] [bold {COLOR_BLUE}]{target.upper()}[/bold {COLOR_BLUE}]",
        border_style=COLOR_PINK,
    ))

    progress = Progress(
        SpinnerColumn(spinner_name="dots", style=COLOR_PINK),
        BarColumn(bar_width=32, style=COLOR_PINK_DIM, complete_style=COLOR_PINK, finished_style=f"bold {COLOR_PINK}"),
        TextColumn(f"[bold {COLOR_PINK}]{{task.percentage:>3.0f}}%[/bold {COLOR_PINK}]"),
        TimeElapsedColumn(),
        TextColumn(f"[bold {COLOR_PINK}]{{task.fields[eta]}}[/bold {COLOR_PINK}]"),
        TextColumn(f"[bold {COLOR_BLUE}]{{task.fields[layer]}}[/bold {COLOR_BLUE}] [white]{{task.fields[op]}}[/white]"),
        console=console,
    )

    with progress:
        task = progress.add_task(
            "Synthesizing",
            total=100,
            eta="Estimating...",
            layer="[Init]",
            op="Analyzing target UI...",
        )

        def on_progress(step: str, pct: float, msg: str, snapshot=None):
            if snapshot:
                progress.update(
                    task,
                    completed=int(snapshot.percent_done),
                    eta=snapshot.eta_formatted,
                    layer=f"[{snapshot.active_layer.split(':')[0]}]",
                    op=snapshot.current_operation,
                )
            else:
                progress.update(
                    task,
                    completed=int(pct * 100),
                    eta="",
                    layer=f"[{step}]",
                    op=msg,
                )

        result = asyncio.run(run_clone(url, cfg, on_progress))

    _print_result(result)


@app.command("config")
def show_config(
    config_file: Optional[Path] = typer.Option(None, "--config", "-c"),
    export: Optional[Path] = typer.Option(None, "--export", help="Export default config to file"),
):
    """[bold #ff2a85]Show or export Scrui configuration.[/bold #ff2a85]"""
    print_banner()
    from uicloner.config import UICloneConfig

    cfg = UICloneConfig.from_yaml(config_file) if config_file else UICloneConfig.default()

    if export:
        cfg.save_yaml(export)
        console.print(f"[green]✅ Config exported to {export}[/green]")
        return

    table = Table(title="Scrui Engine Configuration", show_header=True, border_style=COLOR_PINK, header_style=f"bold {COLOR_PINK}")
    table.add_column("Setting", style=COLOR_PINK)
    table.add_column("Value", style="white")

    table.add_row("Pre-Flight Layer (-1)", str(cfg.preflight.enabled))
    table.add_row("UI-to-Prompt (Layer 5)", str(cfg.prompt_gen.enabled))
    table.add_row("Prompt Target Framework", cfg.prompt_gen.target.value)
    table.add_row("Browser Engine", cfg.browser.primary_engine.value)
    table.add_row("Headless Mode", str(cfg.browser.headless))
    table.add_row("Image Storage", cfg.storage.images.value)
    table.add_row("Font Storage", cfg.storage.fonts.value)
    table.add_row("Video Storage", cfg.storage.videos.value)
    table.add_row("Data Format", cfg.storage.data_format.value)
    table.add_row("Deduplicate Assets", str(cfg.storage.deduplicate_assets))
    table.add_row("SQLite Indexing", str(cfg.storage.build_sqlite_index))
    table.add_row("Root Prefix", cfg.output.root_folder_prefix)
    table.add_row("Data Folder Name", cfg.output.data_folder_name)
    table.add_row("UI Element Analysis", str(cfg.analysis.enabled))
    table.add_row("State Exploration", str(cfg.analysis.explore_states))
    table.add_row("Crawler Enabled", str(cfg.crawler.enabled))
    table.add_row("Proxy Tier", cfg.network.proxy_tier.value)
    table.add_row("TLS Impersonate", cfg.network.tls_impersonate.value)
    table.add_row("Shadow DOM", str(cfg.extraction.capture_shadow_dom))
    table.add_row("Event Listeners", str(cfg.extraction.extract_event_listeners))
    table.add_row("Animations", str(cfg.extraction.extract_animations))
    table.add_row("Scroll Rebinding", str(cfg.extraction.rebind_scroll_animations))
    table.add_row("Lottie Inlining", str(cfg.extraction.inline_lottie))
    table.add_row("JS Deobfuscation", str(cfg.extraction.js_deobfuscate))
    table.add_row("Auto-Correction", str(cfg.validation.auto_correct))
    table.add_row("HF Model (VLM)", cfg.huggingface.vlm_model)
    table.add_row("CAPTCHA Enabled", str(cfg.captcha.enabled))
    table.add_row("Output Dir", str(cfg.output.base_dir))
    table.add_row("Fidelity Threshold", f"{cfg.validation.fidelity_threshold_percent}%")

    console.print(table)


def _print_result(result) -> None:
    if result.success:
        table = Table(
            title="[bold green]✅ Clone Complete & Verified[/bold green]",
            border_style=COLOR_PINK,
            header_style=f"bold {COLOR_PINK}",
        )
        table.add_column("Metric", style=COLOR_PINK, width=22)
        table.add_column("Value", style="white")
        table.add_row("URL", result.url)
        table.add_row("Output Directory", str(result.output_dir))
        table.add_row("Cloned HTML File", str(result.site_html_path))
        table.add_row("Assets Captured", str(result.stats.get("assets", 0)))
        table.add_row("HTML Byte Size", f"{result.stats.get('html_size', 0):,} bytes")
        if "elements" in result.stats and result.stats["elements"] > 0:
            table.add_row("Dismantled Elements", f"{result.stats.get('elements', 0):,}")
            table.add_row("Buttons Reverse-Engineered", f"{result.stats.get('buttons', 0):,}")
        table.add_row("Execution Time", f"[bold {COLOR_PINK}]{result.elapsed_sec:.2f}s[/bold {COLOR_PINK}]")
        if result.fidelity_score is not None:
            color = "green" if result.fidelity_score >= 92 else "yellow"
            table.add_row("Fidelity Score", f"[{color}]{result.fidelity_score:.1f}%[/{color}]")

        if result.preflight:
            pf = result.preflight.get("target_profile", {})
            waf = pf.get("cdn_waf", "None")
            stack = ", ".join(pf.get("detected_frameworks", [])) or "Vanilla"
            table.add_row("Pre-Flight WAF Profile", f"{waf} | Stack: {stack}")

        if result.prompt_path:
            table.add_row("Master AI Prompt", f"[bold {COLOR_BLUE}]{result.prompt_path}[/bold {COLOR_BLUE}]")
            if result.prompt_summary:
                table.add_row("Prompt Architecture", str(result.prompt_summary))

        console.print(table)

        if result.prompt_path and Path(result.prompt_path).exists():
            console.print(Panel(
                f"[bold {COLOR_BLUE}]🚀 Master AI Prompt Ready![/bold {COLOR_BLUE}]\n"
                f"[white]Path:[/white] [bold {COLOR_PINK}]{result.prompt_path}[/bold {COLOR_PINK}]\n\n"
                f"[dim]Copy the contents of [/dim][bold {COLOR_PINK}]PROMPT.md[/bold {COLOR_PINK}][dim] and paste into Claude 3.7 Sonnet, Cursor, v0.dev, or Lovable to build the exact frontend![/dim]",
                border_style=COLOR_PINK,
                title=f"[bold {COLOR_PINK}]Layer 5: UI-to-Prompt Synthesizer[/bold {COLOR_PINK}]",
            ))
    else:
        console.print(Panel(
            f"[red]Clone failed:[/red]\n{result.error}",
            border_style="red",
            title="❌ Error",
        ))


def main():
    app()


if __name__ == "__main__":
    main()
