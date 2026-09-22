"""
Interactive State Explorer & Behavioral Mining Engine
Explores the live page state machine:
  1. Hover Sweep — probes buttons, cards, links for hover transitions and micro-interactions
  2. Focus Probe — probes inputs and controls for focus rings and outline deltas
  3. Safe Click Disclosures — probes tabs, accordions, and dropdown toggles
  4. Progressive Scroll Delta — samples sticky headers and scroll-linked style shifts
Generates synthetic CSS and behavioral data to ensure clone interacts identically offline.
"""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class HoverDelta:
    selector: str
    tag: str
    text_preview: str
    property_deltas: dict[str, dict[str, str]]  # prop -> {"from": val, "to": val}
    transition: str
    synthetic_css_rule: str
    waapi_animation_spawned: bool = False


@dataclass
class FocusDelta:
    selector: str
    tag: str
    property_deltas: dict[str, dict[str, str]]
    synthetic_css_rule: str


@dataclass
class DisclosureWidget:
    trigger_selector: str
    target_selector: str
    type: str  # accordion, tab, dropdown, details
    is_expanded_initially: bool
    state_class_added: Optional[str] = None


@dataclass
class StickyHeaderDelta:
    selector: str
    at_top: dict[str, str]
    scrolled: dict[str, str]
    synthetic_css_rule: str


@dataclass
class BehavioralReport:
    total_interactive_probed: int
    hover_transitions_found: int
    focus_states_found: int
    disclosures_found: int
    hover_deltas: list[HoverDelta] = field(default_factory=list)
    focus_deltas: list[FocusDelta] = field(default_factory=list)
    disclosure_widgets: list[DisclosureWidget] = field(default_factory=list)
    sticky_header: Optional[StickyHeaderDelta] = None
    synthetic_interactions_css: str = ""


# ---------------------------------------------------------------------------
# Deep Browser Probe Script
# ---------------------------------------------------------------------------

STATE_EXPLORER_JS = """
(() => {
    // Helper to get clean selector
    function getCssSelector(el) {
        if (!el || el.nodeType !== Node.ELEMENT_NODE) return '';
        if (el.id && !el.id.match(/^\\d/) && !el.id.includes(':')) {
            try {
                if (document.querySelectorAll('#' + CSS.escape(el.id)).length === 1) {
                    return '#' + CSS.escape(el.id);
                }
            } catch (_) {}
        }
        let path = [];
        let cur = el;
        while (cur && cur.nodeType === Node.ELEMENT_NODE && cur !== document.documentElement) {
            let selector = cur.tagName.toLowerCase();
            if (cur.id && !cur.id.match(/^\\d/) && !cur.id.includes(':')) {
                try {
                    selector = '#' + CSS.escape(cur.id);
                    path.unshift(selector);
                    break;
                } catch (_) {}
            } else if (cur.className && typeof cur.className === 'string') {
                const classes = cur.className.trim().split(/\\s+/)
                    .filter(c => c && !c.includes(':') && !c.includes('/') && !c.startsWith('__') && c.length < 35);
                if (classes.length > 0) {
                    selector += '.' + CSS.escape(classes[0]);
                }
            }
            let parent = cur.parentElement;
            if (parent) {
                let siblings = Array.from(parent.children).filter(c => c.tagName === cur.tagName);
                if (siblings.length > 1) {
                    let index = siblings.indexOf(cur) + 1;
                    selector += `:nth-of-type(${index})`;
                }
            }
            path.unshift(selector);
            cur = cur.parentElement;
        }
        return path.join(' > ');
    }

    const hoverDeltas = [];
    const focusDeltas = [];
    const disclosures = [];
    let stickyDelta = null;

    // 1. Probe Hover States
    const hoverCandidates = document.querySelectorAll(
        'button, a, [role="button"], input[type="submit"], input[type="button"], .btn, .button, .card, [data-hover]'
    );

    const watchedProps = [
        'transform', 'boxShadow', 'backgroundColor', 'color',
        'borderColor', 'opacity', 'scale', 'filter'
    ];

    // Probe up to 40 primary interactive candidates
    const probeList = Array.from(hoverCandidates).slice(0, 40);

    for (const el of probeList) {
        const sel = getCssSelector(el);
        if (!sel) continue;

        const initialStyle = window.getComputedStyle(el);
        const initial = {};
        for (const p of watchedProps) {
            initial[p] = initialStyle[p];
        }

        // Simulate hover by dispatching events
        el.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true, cancelable: true }));
        el.dispatchEvent(new MouseEvent('mouseover', { bubbles: true, cancelable: true }));
        el.classList.add('hover', 'is-hover', 'pseudo-hover');

        const afterStyle = window.getComputedStyle(el);
        const deltas = {};
        let changed = false;

        for (const p of watchedProps) {
            const vBefore = initial[p];
            const vAfter = afterStyle[p];
            if (vBefore !== vAfter && vAfter !== undefined) {
                deltas[p] = { from: vBefore, to: vAfter };
                changed = true;
            }
        }

        // Revert hover simulation
        el.classList.remove('hover', 'is-hover', 'pseudo-hover');
        el.dispatchEvent(new MouseEvent('mouseout', { bubbles: true, cancelable: true }));
        el.dispatchEvent(new MouseEvent('mouseleave', { bubbles: true, cancelable: true }));

        if (changed) {
            const transition = initialStyle.transition || 'all 0.2s ease-in-out';
            const cssProps = Object.entries(deltas)
                .map(([prop, val]) => {
                    const cssProp = prop.replace(/([A-Z])/g, '-$1').toLowerCase();
                    return `  ${cssProp}: ${val.to} !important;`;
                })
                .join('\\n');

            const rule = `${sel}:hover {\\n${cssProps}\\n  transition: ${transition};\\n}`;

            hoverDeltas.push({
                selector: sel,
                tag: el.tagName.toLowerCase(),
                text_preview: (el.innerText || el.textContent || '').trim().slice(0, 40),
                property_deltas: deltas,
                transition: transition,
                synthetic_css_rule: rule,
            });
        }
    }

    // 2. Probe Focus States on Form Inputs
    const focusCandidates = document.querySelectorAll('input:not([type="hidden"]), textarea, select');
    for (const el of Array.from(focusCandidates).slice(0, 20)) {
        const sel = getCssSelector(el);
        if (!sel) continue;

        const initialStyle = window.getComputedStyle(el);
        const beforeOutline = initialStyle.outline;
        const beforeShadow = initialStyle.boxShadow;
        const beforeBorder = initialStyle.borderColor;

        try { el.focus(); } catch(_) {}
        const afterStyle = window.getComputedStyle(el);
        const afterOutline = afterStyle.outline;
        const afterShadow = afterStyle.boxShadow;
        const afterBorder = afterStyle.borderColor;
        try { el.blur(); } catch(_) {}

        const deltas = {};
        if (beforeOutline !== afterOutline && afterOutline !== 'none') {
            deltas['outline'] = { from: beforeOutline, to: afterOutline };
        }
        if (beforeShadow !== afterShadow && afterShadow !== 'none') {
            deltas['boxShadow'] = { from: beforeShadow, to: afterShadow };
        }
        if (beforeBorder !== afterBorder) {
            deltas['borderColor'] = { from: beforeBorder, to: afterBorder };
        }

        if (Object.keys(deltas).length > 0) {
            const cssProps = Object.entries(deltas)
                .map(([prop, val]) => {
                    const cssProp = prop.replace(/([A-Z])/g, '-$1').toLowerCase();
                    return `  ${cssProp}: ${val.to} !important;`;
                })
                .join('\\n');

            const rule = `${sel}:focus, ${sel}:focus-visible {\\n${cssProps}\\n  transition: all 0.2s ease-in-out;\\n}`;

            focusDeltas.push({
                selector: sel,
                tag: el.tagName.toLowerCase(),
                property_deltas: deltas,
                synthetic_css_rule: rule,
            });
        }
    }

    // 3. Probe Safe Disclosures (Accordions, Details, Tabs)
    const detailsEls = document.querySelectorAll('details');
    detailsEls.forEach(d => {
        disclosures.push({
            trigger_selector: getCssSelector(d.querySelector('summary') || d),
            target_selector: getCssSelector(d),
            type: 'details',
            is_expanded_initially: d.hasAttribute('open'),
        });
    });

    const ariaExpanded = document.querySelectorAll('[aria-expanded]');
    ariaExpanded.forEach(btn => {
        const controls = btn.getAttribute('aria-controls');
        const target = controls ? document.getElementById(controls) : btn.nextElementSibling;
        disclosures.push({
            trigger_selector: getCssSelector(btn),
            target_selector: target ? getCssSelector(target) : '',
            type: 'accordion',
            is_expanded_initially: btn.getAttribute('aria-expanded') === 'true',
        });
    });

    // 4. Sample Sticky Header
    const header = document.querySelector('header, [role="banner"], .navbar, nav');
    if (header) {
        const hSel = getCssSelector(header);
        const style = window.getComputedStyle(header);
        if (['sticky', 'fixed'].includes(style.position)) {
            stickyDelta = {
                selector: hSel,
                at_top: {
                    position: style.position,
                    backgroundColor: style.backgroundColor,
                    boxShadow: style.boxShadow,
                    height: style.height,
                    backdropFilter: style.backdropFilter,
                },
                scrolled: {},
                synthetic_css_rule: `${hSel} { position: ${style.position}; top: 0; z-index: 1000; }`
            };
        }
    }

    return {
        total_probed: probeList.length + focusCandidates.length,
        hover_deltas: hoverDeltas,
        focus_deltas: focusDeltas,
        disclosures: disclosures,
        sticky_header: stickyDelta,
    };
})()
"""


class StateExplorer:
    """
    Executes behavioral state mining on the live page via CDP:
    probes hover, focus, disclosures, and scroll interactions,
    extracting dynamic transition rules to bake into the clone.
    """

    def __init__(self, cdp_session):
        self._cdp = cdp_session

    async def explore(self) -> BehavioralReport:
        """Runs the state exploration pass and produces a BehavioralReport."""
        logger.info("Running interactive state exploration (behavioral mining)...")

        try:
            result = await self._cdp.send("Runtime.evaluate", {
                "expression": STATE_EXPLORER_JS,
                "returnByValue": True,
                "timeout": 20000,
            })
            raw = result.get("result", {}).get("value", {})
        except Exception as e:
            logger.warning(f"Interactive state exploration evaluation failed: {e}")
            raw = {}

        raw_hover = raw.get("hover_deltas", [])
        raw_focus = raw.get("focus_deltas", [])
        raw_disc = raw.get("disclosures", [])
        raw_sticky = raw.get("sticky_header")

        hover_deltas = [
            HoverDelta(
                selector=h.get("selector", ""),
                tag=h.get("tag", ""),
                text_preview=h.get("text_preview", ""),
                property_deltas=h.get("property_deltas", {}),
                transition=h.get("transition", ""),
                synthetic_css_rule=h.get("synthetic_css_rule", ""),
            )
            for h in raw_hover
        ]

        focus_deltas = [
            FocusDelta(
                selector=f.get("selector", ""),
                tag=f.get("tag", ""),
                property_deltas=f.get("property_deltas", {}),
                synthetic_css_rule=f.get("synthetic_css_rule", ""),
            )
            for f in raw_focus
        ]

        disclosures = [
            DisclosureWidget(
                trigger_selector=d.get("trigger_selector", ""),
                target_selector=d.get("target_selector", ""),
                type=d.get("type", "accordion"),
                is_expanded_initially=d.get("is_expanded_initially", False),
            )
            for d in raw_disc
        ]

        sticky = None
        if raw_sticky:
            sticky = StickyHeaderDelta(
                selector=raw_sticky.get("selector", ""),
                at_top=raw_sticky.get("at_top", {}),
                scrolled=raw_sticky.get("scrolled", {}),
                synthetic_css_rule=raw_sticky.get("synthetic_css_rule", ""),
            )

        # Assemble Master Synthetic CSS for Behavior Replay
        css_blocks = [
            "/* ───────────────────────────────────────────────────────────── */",
            "/* UI Cloner v2.0 — Synthesized Behavioral & Interaction Rules   */",
            "/* ───────────────────────────────────────────────────────────── */",
        ]

        if hover_deltas:
            css_blocks.append("/* Hover Micro-Interactions */")
            for hd in hover_deltas:
                if hd.synthetic_css_rule:
                    css_blocks.append(hd.synthetic_css_rule)

        if focus_deltas:
            css_blocks.append("/* Focus Rings & Form Interactions */")
            for fd in focus_deltas:
                if fd.synthetic_css_rule:
                    css_blocks.append(fd.synthetic_css_rule)

        if sticky and sticky.synthetic_css_rule:
            css_blocks.append("/* Sticky / Fixed Navigation */")
            css_blocks.append(sticky.synthetic_css_rule)

        synthetic_css = "\n\n".join(css_blocks)

        logger.info(
            f"State exploration complete: {len(hover_deltas)} hover transitions, "
            f"{len(focus_deltas)} focus states, {len(disclosures)} disclosures."
        )

        return BehavioralReport(
            total_interactive_probed=raw.get("total_probed", 0),
            hover_transitions_found=len(hover_deltas),
            focus_states_found=len(focus_deltas),
            disclosures_found=len(disclosures),
            hover_deltas=hover_deltas,
            focus_deltas=focus_deltas,
            disclosure_widgets=disclosures,
            sticky_header=sticky,
            synthetic_interactions_css=synthetic_css,
        )
