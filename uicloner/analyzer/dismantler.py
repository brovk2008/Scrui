"""
UI Element Dismantler & Deep Analyzer
Reverse-engineers, categorizes, and analyzes every UI element, button,
form component, design token, accessibility metric, and page section.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes for structured dismantled output
# ---------------------------------------------------------------------------

@dataclass
class BoundingBox:
    x: float
    y: float
    width: float
    height: float
    top: float
    left: float
    bottom: float
    right: float


@dataclass
class DismantledElement:
    id: str
    tag: str
    selector: str
    xpath: str
    component_type: str  # button, input, navigation, card, modal, heading, etc.
    text: str
    text_full: str
    attributes: dict[str, str]
    box: BoundingBox
    is_visible: bool
    is_in_viewport: bool
    is_interactive: bool
    typography: dict[str, Any]
    styles: dict[str, Any]
    accessibility: dict[str, Any]
    interactions: dict[str, Any]
    button_details: Optional[dict[str, Any]] = None
    form_details: Optional[dict[str, Any]] = None
    depth: int = 0
    children_count: int = 0


@dataclass
class DesignSystemTokens:
    color_palette: list[dict[str, Any]] = field(default_factory=list)
    background_colors: list[dict[str, Any]] = field(default_factory=list)
    typography_scale: dict[str, Any] = field(default_factory=dict)
    border_radii: list[dict[str, Any]] = field(default_factory=list)
    box_shadows: list[dict[str, Any]] = field(default_factory=list)
    breakpoints_detected: list[int] = field(default_factory=list)


@dataclass
class SectionLandmark:
    id: str
    tag: str
    role: str
    title_or_heading: str
    element_count: int
    bounding_box: dict[str, float]
    subsections: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class DismantleReport:
    url: str
    total_elements: int
    interactive_elements: int
    buttons_count: int
    forms_count: int
    links_count: int
    headings_count: int
    media_count: int
    components_summary: dict[str, int]
    elements: list[DismantledElement]
    design_system: DesignSystemTokens
    landmarks: list[SectionLandmark]
    accessibility_score: float
    a11y_issues: list[dict[str, Any]]


# ---------------------------------------------------------------------------
# Deep In-Browser JavaScript Extractor
# ---------------------------------------------------------------------------

DISMANTLE_JS = """
(() => {
    const results = [];
    const colorUsage = {};
    const bgColorUsage = {};
    const fontUsage = {};
    const fontSizeUsage = {};
    const radiusUsage = {};
    const shadowUsage = {};
    const a11yIssues = [];

    const viewportW = window.innerWidth;
    const viewportH = window.innerHeight;

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
                    .filter(c => c && !c.includes(':') && !c.includes('/') && !c.startsWith('__') && c.length < 40);
                if (classes.length > 0) {
                    selector += '.' + CSS.escape(classes[0]);
                }
            }
            // Add nth-child if siblings match
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

    function getXPath(el) {
        if (!el || el.nodeType !== Node.ELEMENT_NODE) return '';
        if (el.id) return `//*[@id="${el.id}"]`;
        let parts = [];
        for (; el && el.nodeType === Node.ELEMENT_NODE; el = el.parentNode) {
            let idx = 1;
            for (let sib = el.previousSibling; sib; sib = sib.previousSibling) {
                if (sib.nodeType === Node.ELEMENT_NODE && sib.tagName === el.tagName) idx++;
            }
            parts.unshift(`${el.tagName.toLowerCase()}[${idx}]`);
        }
        return '/' + parts.join('/');
    }

    function classifyComponent(el, tag, role, style, rect) {
        // Tag based
        if (tag === 'button' || role === 'button' || (tag === 'input' && ['button', 'submit', 'reset'].includes(el.type))) {
            return 'button';
        }
        if (tag === 'a' && el.href) {
            // Check if styled like a button
            if (style.cursor === 'pointer' && (style.backgroundColor !== 'rgba(0, 0, 0, 0)' || style.borderWidth !== '0px') && rect.height > 24) {
                const cls = (el.className || '').toString().toLowerCase();
                if (cls.includes('btn') || cls.includes('button') || cls.includes('cta')) {
                    return 'button';
                }
            }
            return 'link';
        }
        if (['input', 'textarea', 'select'].includes(tag)) {
            return 'input';
        }
        if (['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes(tag) || role === 'heading') {
            return 'heading';
        }
        if (['nav'].includes(tag) || role === 'navigation') {
            return 'navigation';
        }
        if (tag === 'dialog' || role === 'dialog' || role === 'alertdialog') {
            return 'modal';
        }
        if (role === 'tab' || role === 'tabpanel' || role === 'tablist') {
            return 'tab';
        }
        if (tag === 'details' || role === 'region' && (el.className || '').toString().toLowerCase().includes('accordion')) {
            return 'accordion';
        }
        if (['img', 'picture', 'svg', 'canvas', 'video', 'audio'].includes(tag)) {
            return 'media';
        }
        if (['header', 'footer', 'main', 'aside', 'section', 'article'].includes(tag)) {
            return 'layout_section';
        }
        if (role === 'menu' || role === 'menubar' || role === 'menuitem') {
            return 'dropdown';
        }
        // Class heuristics
        const cls = (el.className || '').toString().toLowerCase();
        if (cls.includes('card') && rect.width > 100 && rect.height > 100) return 'card';
        if (cls.includes('modal') || cls.includes('popup') || cls.includes('drawer')) return 'modal';
        if (cls.includes('carousel') || cls.includes('slider') || cls.includes('swiper')) return 'carousel';
        if (cls.includes('dropdown') || cls.includes('select-menu')) return 'dropdown';
        if (cls.includes('tooltip')) return 'tooltip';
        if (cls.includes('badge') || cls.includes('chip') || cls.includes('pill') || cls.includes('tag')) return 'badge';
        if (cls.includes('avatar')) return 'avatar';
        if (cls.includes('nav') || cls.includes('navbar') || cls.includes('menu')) return 'navigation';

        // Check if clickable div/span
        if (style.cursor === 'pointer' && rect.width > 20 && rect.height > 20) {
            return 'interactive_container';
        }

        return 'generic';
    }

    function analyzeButton(el, tag, style, rect) {
        const text = (el.innerText || el.textContent || el.value || '').trim();
        const cls = (el.className || '').toString().toLowerCase();
        const hasSvg = !!el.querySelector('svg');
        const hasImg = !!el.querySelector('img');

        let variant = 'default';
        if (cls.includes('primary') || style.backgroundColor.includes('rgb(') && !style.backgroundColor.includes('255, 255, 255')) {
            variant = 'primary';
        } else if (cls.includes('secondary')) {
            variant = 'secondary';
        } else if (cls.includes('outline') || (style.borderWidth !== '0px' && style.backgroundColor === 'rgba(0, 0, 0, 0)')) {
            variant = 'outline';
        } else if (cls.includes('ghost') || (style.backgroundColor === 'rgba(0, 0, 0, 0)' && style.borderWidth === '0px')) {
            variant = 'ghost';
        } else if (cls.includes('danger') || cls.includes('destructive') || cls.includes('delete')) {
            variant = 'danger';
        }

        if (!text && (hasSvg || hasImg)) {
            variant = 'icon_only';
        }

        return {
            label: text,
            variant: variant,
            is_icon_only: !text && (hasSvg || hasImg),
            has_icon: hasSvg || hasImg,
            icon_type: hasSvg ? 'svg' : (hasImg ? 'image' : 'none'),
            is_disabled: el.disabled || el.getAttribute('aria-disabled') === 'true',
            form_type: el.type || 'button',
            size_category: rect.height < 32 ? 'small' : (rect.height > 48 ? 'large' : 'medium'),
        };
    }

    function analyzeForm(el, tag) {
        return {
            tag: tag,
            type: el.type || (tag === 'textarea' ? 'textarea' : (tag === 'select' ? 'select' : 'text')),
            name: el.name || '',
            placeholder: el.placeholder || '',
            required: el.required || el.getAttribute('aria-required') === 'true',
            disabled: el.disabled || el.getAttribute('aria-disabled') === 'true',
            autocomplete: el.autocomplete || '',
            pattern: el.pattern || '',
            has_label: !!(el.id && document.querySelector(`label[for="${CSS.escape(el.id)}"]`)) || !!el.closest('label'),
        };
    }

    // Traverse all elements
    const allEls = document.querySelectorAll('*');
    let elemIdx = 0;

    for (const el of allEls) {
        // Skip hidden script, style, head tags
        const tag = el.tagName.toLowerCase();
        if (['script', 'style', 'meta', 'link', 'noscript', 'template', 'head'].includes(tag)) {
            continue;
        }

        const rect = el.getBoundingClientRect();
        const style = window.getComputedStyle(el);

        const isVisible = !(
            style.display === 'none' ||
            style.visibility === 'hidden' ||
            parseFloat(style.opacity) === 0 ||
            (rect.width === 0 && rect.height === 0)
        );

        // Record design tokens
        if (isVisible) {
            const color = style.color;
            const bg = style.backgroundColor;
            const font = style.fontFamily;
            const size = style.fontSize;
            const radius = style.borderRadius;
            const shadow = style.boxShadow;

            if (color && color !== 'rgba(0, 0, 0, 0)') colorUsage[color] = (colorUsage[color] || 0) + 1;
            if (bg && bg !== 'rgba(0, 0, 0, 0)') bgColorUsage[bg] = (bgColorUsage[bg] || 0) + 1;
            if (font) fontUsage[font] = (fontUsage[font] || 0) + 1;
            if (size) fontSizeUsage[size] = (fontSizeUsage[size] || 0) + 1;
            if (radius && radius !== '0px') radiusUsage[radius] = (radiusUsage[radius] || 0) + 1;
            if (shadow && shadow !== 'none') shadowUsage[shadow] = (shadowUsage[shadow] || 0) + 1;
        }

        const isInViewport = (
            rect.bottom > 0 &&
            rect.right > 0 &&
            rect.top < viewportH &&
            rect.left < viewportW
        );

        const role = el.getAttribute('role') || '';
        const isInteractive = (
            ['button', 'a', 'input', 'select', 'textarea', 'details'].includes(tag) ||
            role === 'button' || role === 'link' || role === 'tab' || role === 'checkbox' ||
            role === 'menuitem' || style.cursor === 'pointer' ||
            el.hasAttribute('onclick') || el.hasAttribute('tabindex')
        );

        // Filter out deeply nested empty divs to keep memory clean, but retain structural / interactive elements
        const hasText = !!(el.textContent && el.textContent.trim());
        const hasChildren = el.children.length > 0;
        const isImportant = isInteractive || ['h1','h2','h3','h4','h5','h6','nav','header','footer','main','section','article','dialog','form','img','svg','canvas','video'].includes(tag) || (rect.width > 100 && rect.height > 100);

        if (!isImportant && !hasText && !hasChildren && rect.width === 0) {
            continue;
        }

        const compType = classifyComponent(el, tag, role, style, rect);

        // Extract attributes
        const attrs = {};
        for (const attr of el.attributes) {
            attrs[attr.name] = attr.value;
        }

        // Clean text
        let fullText = (el.innerText || el.textContent || '').trim();
        let previewText = fullText.slice(0, 160);

        // Accessibility checks
        const ariaLabel = el.getAttribute('aria-label') || el.getAttribute('aria-labelledby') || '';
        const alt = el.getAttribute('alt') || '';
        const title = el.getAttribute('title') || '';
        const tabindex = el.getAttribute('tabindex');

        const a11y = {
            role: role,
            aria_label: ariaLabel,
            alt: alt,
            title: title,
            tabindex: tabindex,
            is_focusable: el.tabIndex >= 0,
            aria_hidden: el.getAttribute('aria-hidden') === 'true',
            aria_expanded: el.getAttribute('aria-expanded'),
            aria_controls: el.getAttribute('aria-controls'),
        };

        // A11y violation audit
        if (tag === 'img' && !alt && !ariaLabel && role !== 'presentation') {
            a11yIssues.push({
                type: 'missing_alt',
                selector: getCssSelector(el),
                severity: 'medium',
                message: 'Image element is missing an alt attribute'
            });
        }
        if (compType === 'button' && !fullText && !ariaLabel && !title && !alt) {
            a11yIssues.push({
                type: 'empty_button',
                selector: getCssSelector(el),
                severity: 'high',
                message: 'Button has no readable text or aria-label'
            });
        }
        if (tag === 'a' && el.href && !fullText && !ariaLabel && !title) {
            a11yIssues.push({
                type: 'empty_link',
                selector: getCssSelector(el),
                severity: 'medium',
                message: 'Anchor link has no accessible text'
            });
        }

        // Specific component details
        let buttonDetails = null;
        if (compType === 'button') {
            buttonDetails = analyzeButton(el, tag, style, rect);
        }

        let formDetails = null;
        if (['input', 'select', 'textarea'].includes(tag) || compType === 'input') {
            formDetails = analyzeForm(el, tag);
        }

        // Calculate DOM depth
        let depth = 0;
        let p = el.parentElement;
        while (p) { depth++; p = p.parentElement; }

        elemIdx++;
        results.push({
            id: el.id || `uiel-${elemIdx}`,
            tag: tag,
            selector: getCssSelector(el),
            xpath: getXPath(el),
            component_type: compType,
            text: previewText,
            text_full: fullText.slice(0, 1000),
            attributes: attrs,
            box: {
                x: Math.round(rect.x),
                y: Math.round(rect.y),
                width: Math.round(rect.width),
                height: Math.round(rect.height),
                top: Math.round(rect.top),
                left: Math.round(rect.left),
                bottom: Math.round(rect.bottom),
                right: Math.round(rect.right),
            },
            is_visible: isVisible,
            is_in_viewport: isInViewport,
            is_interactive: isInteractive,
            typography: {
                font_family: style.fontFamily,
                font_size: style.fontSize,
                font_weight: style.fontWeight,
                line_height: style.lineHeight,
                letter_spacing: style.letterSpacing,
                color: style.color,
                text_align: style.textAlign,
            },
            styles: {
                background_color: style.backgroundColor,
                background_image: style.backgroundImage !== 'none' ? 'present' : 'none',
                border: `${style.borderWidth} ${style.borderStyle} ${style.borderColor}`,
                border_radius: style.borderRadius,
                box_shadow: style.boxShadow,
                padding: `${style.paddingTop} ${style.paddingRight} ${style.paddingBottom} ${style.paddingLeft}`,
                margin: `${style.marginTop} ${style.marginRight} ${style.marginBottom} ${style.marginLeft}`,
                display: style.display,
                position: style.position,
                z_index: style.zIndex,
                cursor: style.cursor,
                opacity: style.opacity,
            },
            accessibility: a11y,
            interactions: {
                has_hover_effect: style.cursor === 'pointer',
                is_clickable: isInteractive,
                href: el.href || null,
                action: el.action || null,
            },
            button_details: buttonDetails,
            form_details: formDetails,
            depth: depth,
            children_count: el.children.length,
        });
    }

    // Extract landmarks
    const landmarks = [];
    const landmarkTags = ['header', 'nav', 'main', 'aside', 'footer', 'section'];
    for (const ltag of landmarkTags) {
        const found = document.querySelectorAll(ltag);
        found.forEach((lm, idx) => {
            const h = lm.querySelector('h1, h2, h3, h4');
            const lrect = lm.getBoundingClientRect();
            landmarks.push({
                id: lm.id || `${ltag}-${idx+1}`,
                tag: ltag,
                role: lm.getAttribute('role') || ltag,
                title_or_heading: h ? (h.innerText || '').trim() : '',
                element_count: lm.querySelectorAll('*').length,
                bounding_box: {
                    x: Math.round(lrect.x),
                    y: Math.round(lrect.y),
                    width: Math.round(lrect.width),
                    height: Math.round(lrect.height),
                },
            });
        });
    }

    // Sort usage
    function sortedUsage(obj, limit = 15) {
        return Object.entries(obj)
            .sort((a, b) => b[1] - a[1])
            .slice(0, limit)
            .map(([value, count]) => ({ value, count }));
    }

    return {
        elements: results,
        landmarks: landmarks,
        a11y_issues: a11yIssues.slice(0, 100),
        design_system: {
            color_palette: sortedUsage(colorUsage, 12),
            background_colors: sortedUsage(bgColorUsage, 12),
            typography_scale: {
                font_families: sortedUsage(fontUsage, 5),
                font_sizes: sortedUsage(fontSizeUsage, 12),
            },
            border_radii: sortedUsage(radiusUsage, 8),
            box_shadows: sortedUsage(shadowUsage, 8),
            viewport: { width: viewportW, height: viewportH },
        }
    };
})()
"""


# ---------------------------------------------------------------------------
# Python Dismantler Engine
# ---------------------------------------------------------------------------

class UIDismantler:
    """
    Dismantles every element, button, form, section, and style token
    from a live browser session using Chrome DevTools Protocol.
    """

    def __init__(self, cdp_session):
        self._cdp = cdp_session

    async def dismantle(self, url: str) -> DismantleReport:
        """
        Executes deep DOM analysis and produces a comprehensive DismantleReport.
        """
        logger.info(f"Dismantling UI elements for {url}...")

        try:
            result = await self._cdp.send("Runtime.evaluate", {
                "expression": DISMANTLE_JS,
                "returnByValue": True,
                "timeout": 30000,
            })
            data = result.get("result", {}).get("value", {})
        except Exception as e:
            logger.error(f"UI Dismantling evaluation failed: {e}")
            data = {}

        raw_elements = data.get("elements", [])
        landmarks_raw = data.get("landmarks", [])
        a11y_issues = data.get("a11y_issues", [])
        design_data = data.get("design_system", {})

        elements: list[DismantledElement] = []
        components_summary: dict[str, int] = {}
        buttons_count = 0
        forms_count = 0
        links_count = 0
        headings_count = 0
        media_count = 0
        interactive_count = 0

        for r in raw_elements:
            ctype = r.get("component_type", "generic")
            components_summary[ctype] = components_summary.get(ctype, 0) + 1

            if ctype == "button":
                buttons_count += 1
            elif ctype in ("input", "form"):
                forms_count += 1
            elif ctype == "link":
                links_count += 1
            elif ctype == "heading":
                headings_count += 1
            elif ctype == "media":
                media_count += 1

            if r.get("is_interactive"):
                interactive_count += 1

            box_dict = r.get("box", {})
            box = BoundingBox(
                x=box_dict.get("x", 0),
                y=box_dict.get("y", 0),
                width=box_dict.get("width", 0),
                height=box_dict.get("height", 0),
                top=box_dict.get("top", 0),
                left=box_dict.get("left", 0),
                bottom=box_dict.get("bottom", 0),
                right=box_dict.get("right", 0),
            )

            elem = DismantledElement(
                id=r.get("id", ""),
                tag=r.get("tag", ""),
                selector=r.get("selector", ""),
                xpath=r.get("xpath", ""),
                component_type=ctype,
                text=r.get("text", ""),
                text_full=r.get("text_full", ""),
                attributes=r.get("attributes", {}),
                box=box,
                is_visible=r.get("is_visible", True),
                is_in_viewport=r.get("is_in_viewport", False),
                is_interactive=r.get("is_interactive", False),
                typography=r.get("typography", {}),
                styles=r.get("styles", {}),
                accessibility=r.get("accessibility", {}),
                interactions=r.get("interactions", {}),
                button_details=r.get("button_details"),
                form_details=r.get("form_details"),
                depth=r.get("depth", 0),
                children_count=r.get("children_count", 0),
            )
            elements.append(elem)

        landmarks = [
            SectionLandmark(
                id=lm.get("id", ""),
                tag=lm.get("tag", ""),
                role=lm.get("role", ""),
                title_or_heading=lm.get("title_or_heading", ""),
                element_count=lm.get("element_count", 0),
                bounding_box=lm.get("bounding_box", {}),
            )
            for lm in landmarks_raw
        ]

        design_system = DesignSystemTokens(
            color_palette=design_data.get("color_palette", []),
            background_colors=design_data.get("background_colors", []),
            typography_scale=design_data.get("typography_scale", {}),
            border_radii=design_data.get("border_radii", []),
            box_shadows=design_data.get("box_shadows", []),
            breakpoints_detected=[375, 768, 1024, 1280, 1440, 1920],
        )

        # Accessibility score out of 100 based on issues found
        issue_penalty = len(a11y_issues) * 2.5
        a11y_score = max(0.0, min(100.0, 100.0 - issue_penalty))

        logger.info(
            f"Dismantled {len(elements)} elements: {buttons_count} buttons, "
            f"{forms_count} inputs, {links_count} links, {len(landmarks)} landmarks"
        )

        return DismantleReport(
            url=url,
            total_elements=len(elements),
            interactive_elements=interactive_count,
            buttons_count=buttons_count,
            forms_count=forms_count,
            links_count=links_count,
            headings_count=headings_count,
            media_count=media_count,
            components_summary=components_summary,
            elements=elements,
            design_system=design_system,
            landmarks=landmarks,
            accessibility_score=round(a11y_score, 1),
            a11y_issues=a11y_issues,
        )
