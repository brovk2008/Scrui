"""
Main Pipeline Orchestrator
Coordinates all 4 layers to produce a complete UI clone.
Reports progress via callbacks for TUI integration.
"""
from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import urlparse

from slugify import slugify

from uicloner.config import UICloneConfig
from uicloner.output.serializer import OutputSerializer
from uicloner.output.packer import build_single_file_html

logger = logging.getLogger(__name__)


@dataclass
class CloneResult:
    url: str
    success: bool
    output_dir: Optional[Path] = None
    site_html_path: Optional[Path] = None
    fidelity_score: Optional[float] = None
    elapsed_sec: float = 0.0
    error: Optional[str] = None
    warnings: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)
    preflight: Optional[dict] = None
    prompt_path: Optional[Path] = None
    prompt_summary: Optional[str] = None


# Progress callback type: (step_name, progress_0_to_1, message, optional_snapshot)
ProgressCallback = Callable[..., None]


async def run_clone(
    url: str,
    config: UICloneConfig,
    progress: Optional[ProgressCallback] = None,
) -> CloneResult:
    """
    Full pipeline: launch browser → extract → process → validate → output.
    """
    start_time = time.time()
    oracle = None

    def emit(step: str, pct: float, msg: str):
        nonlocal oracle
        snapshot = None
        if oracle:
            snapshot = oracle.step(step, msg, intra_phase_progress=pct)
            pct = snapshot.percent_done / 100.0

        if progress:
            import inspect
            sig = inspect.signature(progress)
            if len(sig.parameters) >= 4:
                progress(step, pct, msg, snapshot)
            else:
                eta_suffix = f" [{snapshot.eta_formatted}]" if snapshot and snapshot.eta_formatted else ""
                progress(step, pct, f"{msg}{eta_suffix}")
        logger.info(f"[{step}] {int(pct*100)}% — {msg}")

    # Determine output directory
    parsed = urlparse(url)
    site_slug = slugify(parsed.netloc or "unknown")
    ts = time.strftime("%Y%m%d_%H%M%S")
    prefix = getattr(config.output, "root_folder_prefix", "site_cloned_")
    clone_dir = Path(config.output.base_dir) / f"{prefix}{site_slug}_{ts}"

    serializer = OutputSerializer(clone_dir, config, site_name=site_slug)

    # -----------------------------------------------------------------------
    # Layer -1: Pre-Flight Profiler & Predictive Telemetry Oracle
    # -----------------------------------------------------------------------
    if getattr(config, "preflight", None) and getattr(config.preflight, "enabled", True):
        emit("preflight", 0.02, "Probing target edge infrastructure, WAF signatures & DOM complexity...")
        try:
            from uicloner.layers.layer_preflight import run_preflight
            oracle = await run_preflight(url, config)
            emit("preflight", 0.05, f"Profile ready: {oracle.profile.summary_line} (Est. {oracle.plan.total_estimated_seconds:.1f}s)")
        except Exception as e:
            logger.warning(f"Pre-flight profiling partial failure: {e}")

    emit("init", 0.05, f"Starting clone of {url}")

    # -----------------------------------------------------------------------
    # Layer 0 + 1: Browser launch
    # -----------------------------------------------------------------------
    emit("browser", 0.08, "Launching stealth browser...")
    session = None
    try:
        from uicloner.layers.layer1_browser import BrowserEngineSelector
        session = await BrowserEngineSelector.launch(config)
        emit("browser", 0.12, f"Browser ready ({config.browser.primary_engine.value})")
    except Exception as e:
        return CloneResult(url=url, success=False, error=f"Browser launch failed: {e}",
                           elapsed_sec=time.time()-start_time)

    try:
        # Navigate to URL
        emit("navigate", 0.15, f"Navigating to {url}...")
        await session.goto(url)

        # CAPTCHA handling
        if config.captcha.enabled and config.captcha.two_captcha_api_key:
            emit("captcha", 0.20, "Checking for CAPTCHA...")
            from uicloner.captcha import CaptchaSolver, auto_detect_and_solve
            solver = CaptchaSolver(
                config.captcha.two_captcha_api_key,
                timeout=config.captcha.timeout_seconds,
                poll_interval=config.captcha.poll_interval_seconds,
            )
            solved = await auto_detect_and_solve(session.page, session.cdp, solver, config)
            if solved:
                emit("captcha", 0.25, "CAPTCHA solved — re-waiting for page load")
                await session.wait_for_idle()

        # -----------------------------------------------------------------------
        # Layer 2: DOM Extraction
        # -----------------------------------------------------------------------
        emit("dom", 0.28, "Capturing DOM snapshot...")
        from uicloner.layers.layer2_extract import (
            DOMSnapshotEngine, extract_shadow_dom,
            build_listener_map, extract_framework_events, extract_all_animations,
        )
        dom_engine = DOMSnapshotEngine(session, config)
        dom_data = await dom_engine.capture(url)
        emit("dom", 0.38, f"DOM captured ({len(dom_data.get('outer_html',''))} chars)")

        # Shadow DOM
        shadow_data = {}
        if config.extraction.capture_shadow_dom:
            emit("shadow", 0.40, "Extracting Shadow DOM...")
            shadow_data = await extract_shadow_dom(session.cdp, session.page)

        # Event listeners
        event_data = {}
        if config.extraction.extract_event_listeners:
            emit("events", 0.45, "Mapping event listeners...")
            try:
                event_data = await build_listener_map(session.cdp)
                framework_events = await extract_framework_events(session.cdp)
                event_data["framework"] = framework_events
            except Exception as e:
                logger.warning(f"Event extraction partial failure: {e}")

        # Animations
        anim_data = {}
        if config.extraction.extract_animations:
            emit("animations", 0.52, "Extracting animations...")
            try:
                anim_data = await extract_all_animations(session.cdp, session.page)
            except Exception as e:
                logger.warning(f"Animation extraction partial failure: {e}")

        # Canvas / WebGL
        canvas_data = {}
        if config.extraction.capture_canvas:
            emit("canvas", 0.58, "Capturing canvas elements...")
            try:
                from uicloner.layers.layer3_process import capture_canvas_elements, extract_webgl_data
                canvas_data = {
                    "canvases": await capture_canvas_elements(session.cdp),
                    "webgl": await extract_webgl_data(session.cdp),
                }
            except Exception as e:
                logger.warning(f"Canvas extraction partial failure: {e}")

        # -----------------------------------------------------------------------
        # Layer 2.5: UI Element Dismantling & Analysis
        # -----------------------------------------------------------------------
        dismantle_report = None
        if config.analysis.enabled:
            emit("dismantle", 0.60, "Dismantling UI elements, buttons, and design tokens...")
            try:
                from uicloner.analyzer import UIDismantler
                dismantler = UIDismantler(session.cdp)
                dismantle_report = await dismantler.dismantle(url)
                emit("dismantle", 0.61, f"Dismantled {dismantle_report.total_elements} elements ({dismantle_report.buttons_count} buttons)")
            except Exception as e:
                logger.warning(f"UI Dismantling partial failure: {e}")

        # -----------------------------------------------------------------------
        # Layer 2.6: Interactive State Exploration (Behavioral Mining)
        # -----------------------------------------------------------------------
        behavior_report = None
        if config.analysis.enabled and getattr(config.analysis, "explore_states", True):
            emit("explore", 0.62, "Mining interactive states (hover transitions, focus rings, disclosures)...")
            try:
                from uicloner.analyzer import StateExplorer
                explorer = StateExplorer(session.cdp)
                behavior_report = await explorer.explore()
                emit("explore", 0.63, f"Mined {behavior_report.hover_transitions_found} hover transitions & {behavior_report.focus_states_found} focus states")
            except Exception as e:
                logger.warning(f"Interactive state exploration partial failure: {e}")

        # -----------------------------------------------------------------------
        # Layer 3: Post-processing
        # -----------------------------------------------------------------------
        emit("process", 0.64, "Processing assets...")
        asset_records = {}
        for asset_url, asset_info in dom_data.get("assets", {}).items():
            try:
                record = serializer.process_asset(
                    url=asset_url,
                    body=asset_info.get("body", ""),
                    base64_encoded=asset_info.get("base64Encoded", False),
                    mime=asset_info.get("mimeType", "application/octet-stream"),
                    base_url=url,
                )
                asset_records[asset_url] = record
            except Exception as e:
                logger.debug(f"Asset processing failed for {asset_url}: {e}")

        emit("process", 0.68, f"Processed {len(asset_records)} assets")

        # JS Deobfuscation
        deob_results = []
        if config.extraction.js_deobfuscate:
            emit("deobfuscate", 0.70, "Deobfuscating JavaScript...")
            from uicloner.layers.layer3_process import deobfuscate_bundle
            scripts = dom_data.get("scripts", [])
            deob_dir = clone_dir / "data" / "deobfuscated"
            for i, script in enumerate(scripts[:5]):  # Cap at 5 scripts
                content = script.get("content", "")
                if content and len(content) > 200:
                    deob = await deobfuscate_bundle(content, config, deob_dir / f"script_{i}")
                    deob_results.append(deob)

        # -----------------------------------------------------------------------
        # Take screenshot for validation
        # -----------------------------------------------------------------------
        emit("screenshot", 0.75, "Taking validation screenshot...")
        original_screenshot = None
        try:
            screenshot_result = await session.cdp.send("Page.captureScreenshot", {
                "format": "png", "quality": 90
            })
            import base64 as _b64
            original_screenshot = _b64.b64decode(screenshot_result.get("data", ""))
        except Exception as e:
            logger.debug(f"Screenshot failed: {e}")

        # -----------------------------------------------------------------------
        # Layer 4: Build HTML output with Animation Fidelity Rebinding
        # -----------------------------------------------------------------------
        emit("pack", 0.78, "Building HTML clone with animation runtimes...")
        animations_css = anim_data.get("baked_css", "")
        if behavior_report and behavior_report.synthetic_interactions_css:
            animations_css += f"\n\n{behavior_report.synthetic_interactions_css}"

        scroll_rebind_js = anim_data.get("scroll_rebind_js", "")
        lottie_runtime_js = anim_data.get("lottie_runtime_js", "")

        site_html = build_single_file_html(
            outer_html=dom_data.get("outer_html", ""),
            stylesheets=dom_data.get("stylesheets", []),
            scripts=dom_data.get("scripts", []),
            asset_records={url: r for url, r in asset_records.items() if "data_uri" in r},
            animations_css=animations_css,
            shadow_dsd_html=shadow_data.get("dsd_html"),
            meta=dom_data.get("meta", {}),
            base_url=url,
            embed_rrweb=config.output.embed_rrweb_replay,
            scroll_rebind_js=scroll_rebind_js,
            lottie_runtime_js=lottie_runtime_js,
        )

        html_path = serializer.write_html(site_html)
        emit("pack", 0.82, f"HTML written ({len(site_html):,} bytes)")

        # -----------------------------------------------------------------------
        # Layer 4: Visual Auto-Correction & Fidelity Optimization
        # -----------------------------------------------------------------------
        fidelity_result = None
        opt_result = None
        if original_screenshot and config.validation.run_pixel_diff:
            if getattr(config.validation, "auto_correct", True):
                emit("optimize", 0.85, "Running closed-loop visual auto-correction...")
                try:
                    from uicloner.optimizer import VisualAutoCorrector
                    corrector = VisualAutoCorrector(config)
                    opt_result = await corrector.optimize(
                        session=session,
                        original_screenshot_bytes=original_screenshot,
                        clone_html=site_html,
                        dismantled_elements=dismantle_report.elements if dismantle_report else [],
                    )
                    site_html = opt_result.optimized_html
                    html_path = serializer.write_html(site_html)
                    fidelity_result = {
                        "fidelity_score": opt_result.final_fidelity,
                        "initial_fidelity": opt_result.initial_fidelity,
                        "iterations": opt_result.iterations,
                        "converged": opt_result.converged,
                        "patches_count": len(opt_result.patches),
                        "history": opt_result.fidelity_history,
                    }
                    emit("optimize", 0.89, f"Auto-correction: {opt_result.initial_fidelity:.1f}% -> {opt_result.final_fidelity:.1f}% ({len(opt_result.patches)} patches)")
                except Exception as e:
                    logger.warning(f"Visual auto-correction failed: {e}")
            else:
                emit("validate", 0.85, "Running fidelity validation...")
                try:
                    from uicloner.layers.layer4_validate import validate_clone_fidelity
                    fidelity_result = await validate_clone_fidelity(
                        original_screenshot, original_screenshot, config
                    )
                    score = fidelity_result.get("fidelity_score", 0)
                    emit("validate", 0.90, f"Fidelity score: {score:.1f}%")
                except Exception as e:
                    logger.warning(f"Validation failed: {e}")

        # -----------------------------------------------------------------------
        # Write all structured data (JSON/JSONL & SQLite Database)
        # -----------------------------------------------------------------------
        emit("data", 0.91, "Writing structured data & indexing...")
        serializer.write_json("dom_tree", dom_data.get("doc_tree", {}))
        serializer.write_json("styles", dom_data.get("stylesheets", []))
        serializer.write_json("scripts", deob_results or dom_data.get("scripts", []))
        serializer.write_data("assets", list(asset_records.values()))
        serializer.write_json("events", event_data)
        serializer.write_json("animations", anim_data)
        serializer.write_json("shadow_dom", shadow_data)
        serializer.write_json("canvas", canvas_data)
        if fidelity_result:
            serializer.write_json("validation", fidelity_result)

        # Write UI Dismantling analysis if captured
        analysis_summary = {}
        if dismantle_report:
            from dataclasses import asdict
            serializer.write_jsonl("elements", dismantle_report.elements)
            serializer.write_json("components", {
                "summary": dismantle_report.components_summary,
                "total_elements": dismantle_report.total_elements,
                "interactive_elements": dismantle_report.interactive_elements,
                "buttons_count": dismantle_report.buttons_count,
                "forms_count": dismantle_report.forms_count,
                "links_count": dismantle_report.links_count,
                "headings_count": dismantle_report.headings_count,
                "media_count": dismantle_report.media_count,
                "accessibility_score": dismantle_report.accessibility_score,
                "a11y_issues": dismantle_report.a11y_issues,
            })
            serializer.write_json("design_system", {
                "color_palette": dismantle_report.design_system.color_palette,
                "background_colors": dismantle_report.design_system.background_colors,
                "typography_scale": dismantle_report.design_system.typography_scale,
                "border_radii": dismantle_report.design_system.border_radii,
                "box_shadows": dismantle_report.design_system.box_shadows,
                "breakpoints_detected": dismantle_report.design_system.breakpoints_detected,
            })
            serializer.write_json("landmarks", [asdict(lm) for lm in dismantle_report.landmarks])

            # Save W3C DTCG & Figma Tokens
            if dismantle_report.design_system:
                try:
                    from uicloner.analyzer.token_exporter import save_tokens_bundle
                    save_tokens_bundle(dismantle_report.design_system, serializer.data_dir)
                except Exception as ex:
                    logger.debug(f"Failed to export DTCG tokens: {ex}")

            # SQLite Indexing
            serializer.index_elements_sqlite(dismantle_report.elements)

            analysis_summary = {
                "total_elements": dismantle_report.total_elements,
                "buttons_count": dismantle_report.buttons_count,
                "forms_count": dismantle_report.forms_count,
                "links_count": dismantle_report.links_count,
                "accessibility_score": dismantle_report.accessibility_score,
            }

        # Write behavioral interaction data if captured
        if behavior_report:
            from dataclasses import asdict
            serializer.write_json("behavior", asdict(behavior_report))

        # Write visual auto-correction results if run
        if opt_result:
            from dataclasses import asdict
            serializer.write_json("auto_corrections", {
                "initial_fidelity": opt_result.initial_fidelity,
                "final_fidelity": opt_result.final_fidelity,
                "iterations": opt_result.iterations,
                "converged": opt_result.converged,
                "patches": [asdict(p) for p in opt_result.patches],
                "fidelity_history": opt_result.fidelity_history,
            })

        # Index assets in SQLite
        serializer.index_assets_sqlite(list(asset_records.values()))

        # Save Layer -1 pre-flight diagnostics
        if oracle and getattr(config.preflight, "save_preflight_report", True):
            serializer.write_json("preflight", oracle.to_dict())

        # -----------------------------------------------------------------------
        # Layer 5: UI-to-Prompt Synthesizer (Optional)
        # -----------------------------------------------------------------------
        prompt_bundle = None
        prompt_path = None
        if getattr(config, "prompt_gen", None) and getattr(config.prompt_gen, "enabled", False):
            emit("prompt", 0.94, f"Synthesizing UI to Master AI Prompt ({config.prompt_gen.target.value.upper()})...")
            try:
                from uicloner.layers.layer5_prompt import generate_ui_prompt
                prompt_bundle = generate_ui_prompt(
                    url=url,
                    config=config,
                    dom_data=dom_data,
                    dismantle_report=dismantle_report,
                    behavior_report=behavior_report,
                    anim_data=anim_data,
                    asset_records=asset_records,
                )
                prompt_path = serializer.write_prompt_bundle(prompt_bundle)
                emit("prompt", 0.98, f"Master prompt generated: {len(prompt_bundle.master_prompt):,} chars → {prompt_path.name}")
            except Exception as e:
                logger.warning(f"UI Prompt synthesis failed: {e}")

        elapsed = time.time() - start_time
        if oracle:
            oracle.mark_complete(f"Clone complete in {elapsed:.1f}s → {clone_dir}")

        serializer.write_manifest(
            meta=dom_data.get("meta", {}),
            url=url,
            elapsed_sec=elapsed,
            asset_count=len(asset_records),
            fidelity=fidelity_result,
            analysis_summary=analysis_summary,
        )

        emit("done", 1.0, f"Clone complete in {elapsed:.1f}s → {clone_dir}")

        return CloneResult(
            url=url,
            success=True,
            output_dir=clone_dir,
            site_html_path=html_path,
            fidelity_score=fidelity_result.get("fidelity_score") if fidelity_result else None,
            elapsed_sec=elapsed,
            stats={
                "assets": len(asset_records),
                "html_size": len(site_html),
                "js_modules": len(deob_results),
                "elements": len(dismantle_report.elements) if dismantle_report else 0,
                "buttons": dismantle_report.buttons_count if dismantle_report else 0,
            },
            preflight=oracle.to_dict() if oracle else None,
            prompt_path=prompt_path,
            prompt_summary=prompt_bundle.summary if prompt_bundle else None,
        )

    except Exception as exc:
        logger.exception(f"Clone pipeline failed: {exc}")
        return CloneResult(
            url=url, success=False, error=str(exc),
            output_dir=clone_dir,
            elapsed_sec=time.time()-start_time,
        )
    finally:
        if session:
            await session.close()


async def run_batch(
    urls: list[str],
    config: UICloneConfig,
    progress: Optional[ProgressCallback] = None,
    max_concurrent: int = 1,
) -> list[CloneResult]:
    """Run cloning for multiple URLs with optional concurrency."""
    results = []
    semaphore = asyncio.Semaphore(max_concurrent)

    async def clone_one(url: str) -> CloneResult:
        async with semaphore:
            return await run_clone(url, config, progress)

    tasks = [clone_one(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return [
        r if isinstance(r, CloneResult) else CloneResult(url=urls[i], success=False, error=str(r))
        for i, r in enumerate(results)
    ]


async def run_site_crawl(
    url: str,
    config: UICloneConfig,
    progress: Optional[ProgressCallback] = None,
    clone_discovered_pages: bool = False,
) -> dict:
    """
    Crawls a website to build a complete sitemap, link graph, and optionally clones discovered pages.
    """
    from uicloner.crawler import SiteCrawler
    from uicloner.layers.layer1_browser import BrowserEngineSelector

    session = None
    try:
        session = await BrowserEngineSelector.launch(config)
        crawler = SiteCrawler(config, browser_session=session)

        def crawl_cb(discovered: int, crawled: int, failed: int, cur_url: str):
            if progress:
                pct = min(0.95, crawled / max(1, config.crawler.max_pages))
                progress("crawl", pct, f"Crawled {crawled}/{discovered} — {cur_url}")

        sitemap = await crawler.crawl(url, progress=crawl_cb)

        # Output folder for crawl / sitemap
        parsed = urlparse(url)
        site_slug = slugify(parsed.netloc or "unknown")
        ts = time.strftime("%Y%m%d_%H%M%S")
        prefix = getattr(config.output, "root_folder_prefix", "site_cloned_")
        clone_dir = Path(config.output.base_dir) / f"{prefix}{site_slug}_sitemap_{ts}"
        serializer = OutputSerializer(clone_dir, config, site_name=site_slug)

        summary = sitemap.to_summary()
        serializer.write_json("sitemap", summary)
        serializer.index_sitemap_sqlite(list(sitemap.pages.values()))

        clone_results = []
        if clone_discovered_pages:
            urls_to_clone = [p.url for p in sitemap.pages.values() if p.status_code == 200][:config.crawler.max_pages]
            for u in urls_to_clone:
                res = await run_clone(u, config, progress)
                clone_results.append(res)

        return {
            "sitemap": summary,
            "output_dir": str(clone_dir),
            "cloned_count": len(clone_results),
            "results": clone_results,
        }
    finally:
        if session:
            await session.close()
