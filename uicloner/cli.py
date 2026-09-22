"""
UI Cloner CLI — Typer-based command-line interface.
Entry point: `uiclone`
"""
from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

app = typer.Typer(
    name="uiclone",
    help="High-Fidelity UI Extraction & Cloning Engine v2.0",
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console()


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s %(name)s: %(message)s")


@app.command("tui")
def launch_tui():
    """[bold cyan]Launch the interactive Terminal UI.[/bold cyan]"""
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
    llm_provider: Optional[str] = typer.Option(None, "--llm-provider", help="LLM provider: groq/openrouter/gemini/huggingface/ollama"),
    hf_key: Optional[str] = typer.Option(None, "--hf-key", envvar="HF_API_KEY", help="HuggingFace API key"),
    captcha_key: Optional[str] = typer.Option(None, "--captcha-key", envvar="TWO_CAPTCHA_KEY", help="2captcha API key"),
    proxy: Optional[str] = typer.Option(None, "--proxy", "-p", help="Proxy: host:port or host:port:user:pass"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging"),
):
    """[bold green]Clone a single URL.[/bold green]"""
    _setup_logging(verbose)

    from uicloner.config import UICloneConfig, BrowserEngine, ImageStorageFormat, FontStorageFormat, OutputDataFormat
    from uicloner.orchestrator import run_clone

    cfg = UICloneConfig.from_yaml(config_file) if config_file else UICloneConfig.default()

    # Apply CLI overrides
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
    if llm_provider:
        cfg.huggingface.provider = llm_provider
    if hf_key:
        cfg.huggingface.api_key = hf_key
    if captcha_key:
        cfg.captcha.two_captcha_api_key = captcha_key
        cfg.captcha.enabled = True
    if proxy:
        cfg.network.proxy_list = [proxy]

    console.print(Panel.fit(
        f"[bold cyan]UI Cloner v2.0[/bold cyan]\n[dim]Target:[/dim] {url}",
        border_style="cyan",
    ))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Starting...", total=100)

        def on_progress(step: str, pct: float, msg: str):
            progress.update(task, completed=int(pct * 100),
                          description=f"[cyan]{step:15}[/cyan] {msg}")

        result = asyncio.run(run_clone(url, cfg, on_progress))

    # Print result
    _print_result(result)


@app.command("batch")
def batch_clone(
    urls_file: Path = typer.Argument(..., help="Path to .txt file with one URL per line"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c"),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o"),
    concurrent: int = typer.Option(1, "--concurrent", "-n", help="Concurrent clones (be careful)"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    """[bold yellow]Clone multiple URLs from a text file.[/bold yellow]"""
    _setup_logging(verbose)

    if not urls_file.exists():
        console.print(f"[red]File not found: {urls_file}[/red]")
        raise typer.Exit(1)

    urls = [line.strip() for line in urls_file.read_text().splitlines()
            if line.strip() and not line.strip().startswith("#")]

    console.print(Panel.fit(
        f"[bold yellow]Batch Mode[/bold yellow]\n[dim]{len(urls)} URLs to clone[/dim]",
        border_style="yellow",
    ))

    from uicloner.config import UICloneConfig
    from uicloner.orchestrator import run_batch

    cfg = UICloneConfig.from_yaml(config_file) if config_file else UICloneConfig.default()
    if output_dir:
        cfg.output.base_dir = output_dir

    results = asyncio.run(run_batch(urls, cfg, max_concurrent=concurrent))

    table = Table(title="Batch Results", show_header=True, header_style="bold magenta")
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


@app.command("validate")
def validate(
    original_url: str = typer.Argument(..., help="Original URL"),
    clone_html: Path = typer.Argument(..., help="Path to cloned HTML file"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c"),
):
    """[bold magenta]Validate a clone against the original using pixel diff + VLM.[/bold magenta]"""
    console.print(f"[dim]Validating {clone_html.name} vs {original_url}...[/dim]")
    console.print("[yellow]Note: Full validation requires browser launch for screenshots.[/yellow]")


@app.command("crawl")
def crawl_site(
    url: str = typer.Argument(..., help="Root URL to crawl"),
    max_pages: int = typer.Option(50, "--max-pages", "-m", help="Maximum pages to crawl"),
    max_depth: int = typer.Option(3, "--depth", "-d", help="Maximum crawl depth"),
    clone_all: bool = typer.Option(False, "--clone-all", help="Clone all discovered pages"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    """[bold magenta]Crawl an entire site and build a comprehensive sitemap.[/bold magenta]"""
    _setup_logging(verbose)

    from uicloner.config import UICloneConfig
    from uicloner.orchestrator import run_site_crawl

    cfg = UICloneConfig.from_yaml(config_file) if config_file else UICloneConfig.default()
    cfg.crawler.enabled = True
    cfg.crawler.max_pages = max_pages
    cfg.crawler.max_depth = max_depth

    console.print(Panel.fit(
        f"[bold magenta]Site Crawler & Sitemap Builder[/bold magenta]\n"
        f"[dim]Root URL:[/dim] {url}\n"
        f"[dim]Max Pages:[/dim] {max_pages}  |  [dim]Max Depth:[/dim] {max_depth}  |  [dim]Clone All:[/dim] {clone_all}",
        border_style="magenta",
    ))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Crawling...", total=100)

        def on_progress(step: str, pct: float, msg: str):
            progress.update(task, completed=int(pct * 100),
                            description=f"[magenta]{step:10}[/magenta] {msg}")

        result = asyncio.run(run_site_crawl(url, cfg, on_progress, clone_discovered_pages=clone_all))

    sitemap_data = result.get("sitemap", {})
    pages = sitemap_data.get("pages", [])

    table = Table(title=f"Sitemap: {url} ({len(pages)} Pages Discovered)", border_style="magenta")
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
    """[bold cyan]Dismantle and analyze each and every element, button, and design token on a site.[/bold cyan]"""
    _setup_logging(verbose)

    from uicloner.config import UICloneConfig
    from uicloner.orchestrator import run_clone

    cfg = UICloneConfig.from_yaml(config_file) if config_file else UICloneConfig.default()
    cfg.analysis.enabled = True

    console.print(Panel.fit(
        f"[bold cyan]UI Element Dismantler[/bold cyan]\n[dim]Target:[/dim] {url}",
        border_style="cyan",
    ))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Dismantling UI...", total=100)

        def on_progress(step: str, pct: float, msg: str):
            progress.update(task, completed=int(pct * 100),
                            description=f"[cyan]{step:12}[/cyan] {msg}")

        result = asyncio.run(run_clone(url, cfg, on_progress))

    _print_result(result)


@app.command("sitemap")
def build_sitemap(
    url: str = typer.Argument(..., help="Target URL to generate sitemap for"),
    max_pages: int = typer.Option(100, "--max-pages", "-m"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c"),
):
    """[bold yellow]Generate full sitemap & link hierarchy for a site.[/bold yellow]"""
    from uicloner.config import UICloneConfig
    from uicloner.orchestrator import run_site_crawl

    cfg = UICloneConfig.from_yaml(config_file) if config_file else UICloneConfig.default()
    cfg.crawler.enabled = True
    cfg.crawler.max_pages = max_pages

    result = asyncio.run(run_site_crawl(url, cfg, None, clone_discovered_pages=False))
    console.print(f"[green]✅ Sitemap generated: {result.get('output_dir')}[/green]")


@app.command("config")
def show_config(
    config_file: Optional[Path] = typer.Option(None, "--config", "-c"),
    export: Optional[Path] = typer.Option(None, "--export", help="Export default config to file"),
):
    """[bold blue]Show or export configuration.[/bold blue]"""
    from uicloner.config import UICloneConfig

    cfg = UICloneConfig.from_yaml(config_file) if config_file else UICloneConfig.default()

    if export:
        cfg.save_yaml(export)
        console.print(f"[green]✅ Config exported to {export}[/green]")
        return

    table = Table(title="Current Configuration", show_header=True)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Browser Engine", cfg.browser.primary_engine.value)
    table.add_row("Headless", str(cfg.browser.headless))
    table.add_row("Image Storage", cfg.storage.images.value)
    table.add_row("Font Storage", cfg.storage.fonts.value)
    table.add_row("Video Storage", cfg.storage.videos.value)
    table.add_row("Data Format", cfg.storage.data_format.value)
    table.add_row("Deduplicate Assets", str(cfg.storage.deduplicate_assets))
    table.add_row("SQLite Indexing", str(cfg.storage.build_sqlite_index))
    table.add_row("Root Prefix", cfg.output.root_folder_prefix)
    table.add_row("Data Folder Name", cfg.output.data_folder_name)
    table.add_row("UI Element Analysis", str(cfg.analysis.enabled))
    table.add_row("Crawler Enabled", str(cfg.crawler.enabled))
    table.add_row("Proxy Tier", cfg.network.proxy_tier.value)
    table.add_row("TLS Impersonate", cfg.network.tls_impersonate.value)
    table.add_row("Shadow DOM", str(cfg.extraction.capture_shadow_dom))
    table.add_row("Event Listeners", str(cfg.extraction.extract_event_listeners))
    table.add_row("Animations", str(cfg.extraction.extract_animations))
    table.add_row("Scroll Rebinding", str(cfg.extraction.rebind_scroll_animations))
    table.add_row("Lottie Inlining", str(cfg.extraction.inline_lottie))
    table.add_row("JS Deobfuscation", str(cfg.extraction.js_deobfuscate))
    table.add_row("HF Model (VLM)", cfg.huggingface.vlm_model)
    table.add_row("CAPTCHA Enabled", str(cfg.captcha.enabled))
    table.add_row("Output Dir", str(cfg.output.base_dir))
    table.add_row("Fidelity Threshold", f"{cfg.validation.fidelity_threshold_percent}%")

    console.print(table)


def _print_result(result) -> None:
    if result.success:
        table = Table(title="✅ Clone Complete", border_style="green")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        table.add_row("URL", result.url)
        table.add_row("Output Dir", str(result.output_dir))
        table.add_row("HTML", str(result.site_html_path))
        table.add_row("Assets", str(result.stats.get("assets", 0)))
        table.add_row("HTML Size", f"{result.stats.get('html_size', 0):,} bytes")
        if "elements" in result.stats and result.stats["elements"] > 0:
            table.add_row("Dismantled Elements", f"{result.stats.get('elements', 0):,}")
            table.add_row("Buttons Analyzed", f"{result.stats.get('buttons', 0):,}")
        table.add_row("Time", f"{result.elapsed_sec:.2f}s")
        if result.fidelity_score is not None:
            color = "green" if result.fidelity_score >= 92 else "yellow"
            table.add_row("Fidelity", f"[{color}]{result.fidelity_score:.1f}%[/{color}]")
        console.print(table)
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
