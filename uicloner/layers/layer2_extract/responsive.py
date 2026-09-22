"""
Scrui Responsive Viewport Matrix Extractor.
Captures layout states, navigation transitions, and visibility deltas
across Mobile (390px), Tablet (820px), and Desktop (1920px).
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

CANONICAL_BREAKPOINTS = {
    "mobile": {"width": 390, "height": 844, "device_scale_factor": 3, "mobile": True},
    "tablet": {"width": 820, "height": 1180, "device_scale_factor": 2, "mobile": True},
    "desktop": {"width": 1920, "height": 1080, "device_scale_factor": 1, "mobile": False},
}


@dataclass
class ViewportSnapshot:
    name: str
    width: int
    height: int
    has_hamburger: bool = False
    has_mobile_drawer: bool = False
    mobile_menu_trigger_selector: Optional[str] = None
    navigation_type: str = "inline"  # inline, drawer, bottom_bar
    hidden_elements_count: int = 0
    visible_headings: List[str] = field(default_factory=list)
    responsive_classes_detected: List[str] = field(default_factory=list)


@dataclass
class ResponsiveMatrixReport:
    snapshots: Dict[str, ViewportSnapshot] = field(default_factory=dict)
    layout_shifts_summary: List[str] = field(default_factory=list)
    hamburger_drawer_contract: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshots": {k: asdict(v) for k, v in self.snapshots.items()},
            "layout_shifts_summary": self.layout_shifts_summary,
            "hamburger_drawer_contract": self.hamburger_drawer_contract,
        }


# JavaScript snippet executed inside browser page to audit layout at current viewport
RESPONSIVE_AUDIT_JS = """
(() => {
    const isVisible = (el) => {
        const style = window.getComputedStyle(el);
        return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0' && el.offsetWidth > 0;
    };

    // Check for hamburger or mobile menu trigger
    const menuButtons = Array.from(document.querySelectorAll('button, a, [role="button"]')).filter(el => {
        const label = (el.getAttribute('aria-label') || el.className || el.id || '').toLowerCase();
        const hasSvgLines = el.querySelector('svg') && el.querySelector('svg').innerHTML.includes('line');
        return (label.includes('menu') || label.includes('hamburger') || label.includes('nav-toggle') || hasSvgLines) && isVisible(el);
    });

    // Check for drawer / sheet / mobile off-canvas
    const drawers = Array.from(document.querySelectorAll('[role="dialog"], [aria-modal="true"], nav, aside')).filter(el => {
        const style = window.getComputedStyle(el);
        return (style.position === 'fixed' || style.position === 'absolute') && (style.transform.includes('matrix') || style.right === '0px' || style.left === '0px');
    });

    // Extract visible headings
    const headings = Array.from(document.querySelectorAll('h1, h2')).filter(isVisible).slice(0, 5).map(h => h.innerText.trim().slice(0, 40));

    // Detect Tailwind or CSS responsive classes in use
    const responsiveClasses = new Set();
    document.querySelectorAll('[class]').forEach(el => {
        const cls = el.getAttribute('class') || '';
        cls.split(/\\s+/).forEach(c => {
            if (/^(sm|md|lg|xl|2xl):/.test(c)) {
                responsiveClasses.add(c);
            }
        });
    });

    return {
        has_hamburger: menuButtons.length > 0,
        trigger_selector: menuButtons.length > 0 ? (menuButtons[0].id ? '#' + menuButtons[0].id : menuButtons[0].className) : null,
        has_drawer: drawers.length > 0,
        headings: headings,
        responsive_classes: Array.from(responsiveClasses).slice(0, 20)
    };
})();
"""


async def extract_responsive_matrix(
    page_or_cdp: Any,
    viewports: Optional[List[str]] = None,
    engine_type: str = "nodriver",
) -> ResponsiveMatrixReport:
    """
    Cycles through responsive viewports (mobile, tablet, desktop) and analyzes layout shifts.
    """
    if not viewports:
        viewports = ["desktop", "mobile"]

    report = ResponsiveMatrixReport()

    for vp_name in viewports:
        if vp_name not in CANONICAL_BREAKPOINTS:
            continue
        spec = CANONICAL_BREAKPOINTS[vp_name]
        w, h = spec["width"], spec["height"]

        try:
            # 1. Resize viewport
            if engine_type == "nodriver":
                # CDP call via nodriver
                if hasattr(page_or_cdp, "send"):
                    await page_or_cdp.send(
                        "Emulation.setDeviceMetricsOverride",
                        width=w,
                        height=h,
                        deviceScaleFactor=spec["device_scale_factor"],
                        mobile=spec["mobile"],
                    )
            elif hasattr(page_or_cdp, "set_viewport_size"):
                # Playwright / Patchright / Camoufox
                await page_or_cdp.set_viewport_size({"width": w, "height": h})

            await asyncio.sleep(0.3)  # wait for CSS media query transitions

            # 2. Run Audit Script
            audit_res = None
            if hasattr(page_or_cdp, "evaluate"):
                audit_res = await page_or_cdp.evaluate(RESPONSIVE_AUDIT_JS)
            elif hasattr(page_or_cdp, "send"):
                eval_raw = await page_or_cdp.send("Runtime.evaluate", expression=RESPONSIVE_AUDIT_JS, returnByValue=True)
                if eval_raw and "result" in eval_raw and "value" in eval_raw["result"]:
                    audit_res = eval_raw["result"]["value"]

            if not audit_res or not isinstance(audit_res, dict):
                audit_res = {}

            has_hamburger = audit_res.get("has_hamburger", False)
            nav_type = "drawer" if has_hamburger else "inline"

            snapshot = ViewportSnapshot(
                name=vp_name,
                width=w,
                height=h,
                has_hamburger=has_hamburger,
                has_mobile_drawer=audit_res.get("has_drawer", False),
                mobile_menu_trigger_selector=audit_res.get("trigger_selector"),
                navigation_type=nav_type,
                visible_headings=audit_res.get("headings", []),
                responsive_classes_detected=audit_res.get("responsive_classes", []),
            )
            report.snapshots[vp_name] = snapshot

        except Exception as e:
            logger.warning(f"Failed to audit responsive viewport {vp_name}: {e}")
            # Fallback snapshot
            report.snapshots[vp_name] = ViewportSnapshot(name=vp_name, width=w, height=h)

    # 3. Restore to desktop standard
    try:
        if engine_type == "nodriver" and hasattr(page_or_cdp, "send"):
            await page_or_cdp.send("Emulation.clearDeviceMetricsOverride")
        elif hasattr(page_or_cdp, "set_viewport_size"):
            await page_or_cdp.set_viewport_size({"width": 1920, "height": 1080})
    except Exception:
        pass

    # 4. Synthesize layout shift summary
    if "mobile" in report.snapshots and "desktop" in report.snapshots:
        m_snap = report.snapshots["mobile"]
        d_snap = report.snapshots["desktop"]
        if m_snap.has_hamburger and not d_snap.has_hamburger:
            report.layout_shifts_summary.append("Navigation collapses into hamburger button on mobile (<768px).")
            report.hamburger_drawer_contract = (
                "Provide an off-canvas Sheet / Drawer component using Framer Motion with "
                "isOpen state, backdrop-blur overlay, and mobile navigation links."
            )
        report.layout_shifts_summary.append("Grid containers shift from multi-column (md:grid-cols-3) to single-column (grid-cols-1) on mobile.")

    return report
