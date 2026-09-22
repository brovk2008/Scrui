"""
Visual Auto-Correction Optimizer — Closed-Loop Tuning Engine
Treats UI cloning as an iterative visual optimization problem:
  1. Render clone in browser → take screenshot
  2. Compute visual diff against original screenshot
  3. Locate localized error regions and map to DOM elements
  4. Synthesize corrective CSS patches (#uiclone-auto-corrections)
  5. Re-render, re-evaluate fidelity, and repeat until target score reached
"""
from __future__ import annotations

import asyncio
import io
import logging
import math
from dataclasses import dataclass, field
from typing import Any, Optional

from PIL import Image, ImageChops

logger = logging.getLogger(__name__)


@dataclass
class CorrectionPatch:
    iteration: int
    selector: str
    property_name: str
    patch_value: str
    reason: str
    css_rule: str


@dataclass
class OptimizationResult:
    initial_fidelity: float
    final_fidelity: float
    iterations: int
    converged: bool
    optimized_html: str
    patches: list[CorrectionPatch] = field(default_factory=list)
    fidelity_history: list[float] = field(default_factory=list)


class VisualAutoCorrector:
    """
    Closed-loop iterative visual optimizer that refines the cloned HTML
    by diagnosing pixel differences and injecting targeted CSS patches.
    """

    def __init__(self, config):
        self.config = config
        self.max_iterations = getattr(config.validation, "max_auto_correct_iterations", 3)
        self.target_fidelity = getattr(config.validation, "fidelity_threshold_percent", 95.0)

    async def optimize(
        self,
        session,
        original_screenshot_bytes: bytes,
        clone_html: str,
        dismantled_elements: list[Any],
    ) -> OptimizationResult:
        """
        Runs the closed-loop optimization cycle:
        Renders clone → Diff → Diagnose → Patch → Re-render.
        """
        logger.info(f"Starting Visual Auto-Correction Optimizer (Target: {self.target_fidelity}%)...")

        current_html = clone_html
        all_patches: list[CorrectionPatch] = []
        fidelity_history: list[float] = []

        initial_fidelity = 0.0
        final_fidelity = 0.0
        converged = False

        orig_img = Image.open(io.BytesIO(original_screenshot_bytes)).convert("RGB")

        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"[Auto-Corrector] Iteration {iteration}/{self.max_iterations}...")

            # 1. Render current clone HTML in session
            clone_screenshot_bytes = await self._render_html_and_screenshot(session, current_html)
            if not clone_screenshot_bytes:
                logger.warning("[Auto-Corrector] Failed to capture clone screenshot. Stopping loop.")
                break

            clone_img = Image.open(io.BytesIO(clone_screenshot_bytes)).convert("RGB")

            # 2. Compute visual fidelity and error regions
            fidelity, diff_regions = self._compute_visual_diff(orig_img, clone_img)
            fidelity_history.append(fidelity)

            if iteration == 1:
                initial_fidelity = fidelity

            final_fidelity = fidelity
            logger.info(f"[Auto-Corrector] Iteration {iteration} Fidelity: {fidelity:.2f}%")

            # Check convergence
            if fidelity >= self.target_fidelity:
                logger.info(f"[Auto-Corrector] Target fidelity ({self.target_fidelity}%) reached! Converged.")
                converged = True
                break

            # 3. Diagnose discrepancies and generate patches
            iteration_patches = self._diagnose_and_patch(diff_regions, dismantled_elements, iteration)
            if not iteration_patches:
                logger.info("[Auto-Corrector] No further actionable CSS corrections found.")
                break

            all_patches.extend(iteration_patches)

            # 4. Inject synthesized CSS patches into current HTML
            patch_css = "\n".join(p.css_rule for p in iteration_patches)
            style_injection = f"\n<style id='uiclone-auto-corrections-iter{iteration}'>\n{patch_css}\n</style>\n"

            if "</body>" in current_html:
                current_html = current_html.replace("</body>", f"{style_injection}</body>", 1)
            else:
                current_html += style_injection

        return OptimizationResult(
            initial_fidelity=initial_fidelity,
            final_fidelity=final_fidelity,
            iterations=len(fidelity_history),
            converged=converged,
            optimized_html=current_html,
            patches=all_patches,
            fidelity_history=fidelity_history,
        )

    async def _render_html_and_screenshot(self, session, html: str) -> Optional[bytes]:
        """Renders the HTML in the browser session via CDP Page.navigate or set_content."""
        try:
            import base64
            # Use data URI or Page evaluation to mount HTML
            b64_html = base64.b64encode(html.encode("utf-8")).decode("ascii")
            data_url = f"data:text/html;base64,{b64_html}"
            await session.goto(data_url)
            await asyncio.sleep(0.6)  # allow styles and layout to settle

            # Capture screenshot
            result = await session.cdp.send("Page.captureScreenshot", {
                "format": "png", "quality": 90
            })
            raw_b64 = result.get("data", "")
            return base64.b64decode(raw_b64)
        except Exception as e:
            logger.warning(f"Failed to render clone in browser: {e}")
            return None

    def _compute_visual_diff(
        self, orig: Image.Image, clone: Image.Image
    ) -> tuple[float, list[dict[str, Any]]]:
        """
        Calculates pixel difference and segments error into vertical bands/regions.
        Returns: (fidelity_percentage, error_regions)
        """
        # Resize clone to match original if minor dimensions drift
        if orig.size != clone.size:
            clone = clone.resize(orig.size, Image.Resampling.BILINEAR)

        diff = ImageChops.difference(orig, clone)
        gray_diff = diff.convert("L")

        # Threshold pixels differing by more than 15 values
        thresholded = gray_diff.point(lambda p: 255 if p > 15 else 0)

        # Calculate overall mismatch
        diff_pixels = sum(1 for p in thresholded.getdata() if p > 0)
        total_pixels = orig.width * orig.height
        error_ratio = diff_pixels / max(1, total_pixels)
        fidelity = max(0.0, min(100.0, (1.0 - error_ratio) * 100.0))

        # Segment image into 6 vertical regions to locate error clusters
        regions = []
        band_h = orig.height // 6
        for i in range(6):
            y_start = i * band_h
            y_end = (i + 1) * band_h if i < 5 else orig.height
            box = (0, y_start, orig.width, y_end)
            band = thresholded.crop(box)
            band_diff = sum(1 for p in band.getdata() if p > 0)
            band_total = orig.width * (y_end - y_start)
            band_error = band_diff / max(1, band_total)

            if band_error > 0.04:  # Region has >4% visual mismatch
                regions.append({
                    "band_index": i,
                    "y_start": y_start,
                    "y_end": y_end,
                    "error_ratio": band_error,
                })

        # Sort by worst error region first
        regions.sort(key=lambda r: r["error_ratio"], reverse=True)
        return fidelity, regions

    def _diagnose_and_patch(
        self,
        diff_regions: list[dict[str, Any]],
        elements: list[Any],
        iteration: int,
    ) -> list[CorrectionPatch]:
        """
        Maps high error regions to DOM elements and synthesizes corrective CSS rules.
        """
        patches: list[CorrectionPatch] = []
        patched_selectors = set()

        for region in diff_regions[:3]:  # Focus on top 3 worst regions per iteration
            y_start = region["y_start"]
            y_end = region["y_end"]

            # Find candidate elements located inside this vertical region
            candidates = []
            for el in elements:
                # Handle both dict and DismantledElement
                box = el.box if hasattr(el, "box") else el.get("box", {})
                by = box.y if hasattr(box, "y") else box.get("y", 0)
                bh = box.height if hasattr(box, "height") else box.get("height", 0)
                sel = el.selector if hasattr(el, "selector") else el.get("selector", "")
                tag = el.tag if hasattr(el, "tag") else el.get("tag", "")

                if not sel or sel in patched_selectors:
                    continue

                # Check vertical overlap
                if (by + bh) > y_start and by < y_end:
                    candidates.append((el, by, bh, sel, tag))

            if not candidates:
                continue

            # Prioritize structural headers, headings, buttons, and hero containers
            candidates.sort(
                key=lambda c: (
                    0 if c[4] in ("h1", "h2", "header", "nav") else
                    (1 if c[4] in ("button", ".btn") else 2)
                )
            )

            for el, by, bh, sel, tag in candidates[:2]:
                if sel in patched_selectors:
                    continue

                # Auto-correction heuristics:
                # 1. For headings and hero text: normalize line-height and margin collapse
                if tag in ("h1", "h2", "h3", "p"):
                    patch = CorrectionPatch(
                        iteration=iteration,
                        selector=sel,
                        property_name="margin / line-height",
                        patch_value="line-height: 1.25; margin-top: 0;",
                        reason="Compensate for fallback font metric and vertical drift",
                        css_rule=f"{sel} {{\n  line-height: 1.25 !important;\n  letter-spacing: -0.01em !important;\n}}",
                    )
                    patches.append(patch)
                    patched_selectors.add(sel)

                # 2. For containers / sections: enforce padding and box-sizing
                elif tag in ("section", "div", "header", "nav", "main"):
                    patch = CorrectionPatch(
                        iteration=iteration,
                        selector=sel,
                        property_name="box-sizing / padding",
                        patch_value="box-sizing: border-box;",
                        reason="Prevent layout box overflow and border drift",
                        css_rule=f"{sel} {{\n  box-sizing: border-box !important;\n  max-width: 100% !important;\n}}",
                    )
                    patches.append(patch)
                    patched_selectors.add(sel)

                # 3. For buttons / cards: restore borders and radii
                elif tag in ("button", "a") or "card" in sel:
                    patch = CorrectionPatch(
                        iteration=iteration,
                        selector=sel,
                        property_name="display / alignment",
                        patch_value="display: inline-flex; align-items: center;",
                        reason="Ensure button contents and icons are vertically centered",
                        css_rule=f"{sel} {{\n  display: inline-flex !important;\n  align-items: center !important;\n  justify-content: center !important;\n}}",
                    )
                    patches.append(patch)
                    patched_selectors.add(sel)

        return patches
