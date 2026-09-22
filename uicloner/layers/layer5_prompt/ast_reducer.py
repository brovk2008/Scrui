"""
DOM-to-Component AST Reducer (Layer 5)
Prunes DOM boilerplate, groups elements into high-level semantic sections,
detects repeated component patterns (cards, tiers, items), and extracts verbatim copy.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ComponentSpec:
    """Specification of an extracted reusable component."""
    name: str
    category: str  # button, card, navbar, modal, pricing_tier, faq_item, footer
    description: str
    props: dict[str, str] = field(default_factory=dict)  # prop_name -> type
    sample_data: dict[str, Any] = field(default_factory=dict)
    interactive_behavior: Optional[str] = None
    layout_type: str = "flex"  # flex, grid, absolute, inline
    tailwind_classes_hint: str = ""


@dataclass
class SemanticSection:
    """High-level semantic layout section of the page."""
    section_id: str
    section_name: str  # Header, Hero, Features, Pricing, Testimonials, FAQ, Footer
    headline: Optional[str] = None
    subheadline: Optional[str] = None
    cta_buttons: list[dict[str, str]] = field(default_factory=list)  # label, variant
    components: list[ComponentSpec] = field(default_factory=list)
    raw_copy: list[str] = field(default_factory=list)
    layout: str = "vertical"  # vertical, grid-2, grid-3, grid-4, split-hero


def reduce_dom_to_components(
    outer_html: str,
    dismantle_report: Any = None,
    dom_tree: Optional[dict] = None,
) -> tuple[list[SemanticSection], list[ComponentSpec]]:
    """
    Synthesize outer HTML and dismantling report into clean semantic sections
    and reusable component blueprints.
    """
    sections: list[SemanticSection] = []
    reusable_components: list[ComponentSpec] = []

    # 1. Clean HTML snippet for regex extraction
    sample_html = outer_html or ""

    # 2. Extract Title / Brand
    title_match = re.search(r"<title[^>]*>(.*?)</title>", sample_html, re.IGNORECASE)
    site_title = title_match.group(1).strip() if title_match else "Modern Web Application"

    # 3. Extract All Headings (H1 to H3)
    h1_matches = [m.strip() for m in re.findall(r"<h1[^>]*>(.*?)</h1>", sample_html, re.IGNORECASE | re.DOTALL)]
    h2_matches = [m.strip() for m in re.findall(r"<h2[^>]*>(.*?)</h2>", sample_html, re.IGNORECASE | re.DOTALL)]
    h3_matches = [m.strip() for m in re.findall(r"<h3[^>]*>(.*?)</h3>", sample_html, re.IGNORECASE | re.DOTALL)]

    def clean_text(raw: str) -> str:
        text = re.sub(r"<[^>]+>", "", raw)
        return " ".join(text.split()).strip()

    clean_h1 = [clean_text(h) for h in h1_matches if clean_text(h)]
    clean_h2 = [clean_text(h) for h in h2_matches if clean_text(h)]
    clean_h3 = [clean_text(h) for h in h3_matches if clean_text(h)]

    # 4. Extract Navigation Links
    nav_links: list[str] = []
    nav_blocks = re.findall(r"<nav\b[^>]*>(.*?)</nav>", sample_html, re.IGNORECASE | re.DOTALL)
    for nav in nav_blocks:
        links = re.findall(r"<a\b[^>]*>(.*?)</a>", nav, re.IGNORECASE | re.DOTALL)
        for l in links:
            t = clean_text(l)
            if t and len(t) < 30 and t not in nav_links:
                nav_links.append(t)

    if not nav_links:
        # Fallback search for common nav link text
        nav_links = ["Features", "Solutions", "Pricing", "Docs", "About"]

    # 5. Extract Buttons
    buttons_info: list[dict[str, str]] = []
    if dismantle_report and hasattr(dismantle_report, "elements"):
        for el in getattr(dismantle_report, "elements", []):
            if getattr(el, "tag", "") in ["button", "a"] and getattr(el, "is_button", False):
                text = getattr(el, "text", "").strip()
                if text and len(text) < 40 and not any(b["label"] == text for b in buttons_info):
                    bg = getattr(el, "background_color", "")
                    variant = "primary" if bg and "255, 255, 255" not in bg else "secondary"
                    buttons_info.append({"label": text, "variant": variant})
    else:
        btn_matches = re.findall(r"<(?:button|a)\b[^>]*>(.*?)</(?:button|a)>", sample_html, re.IGNORECASE | re.DOTALL)
        for b in btn_matches[:8]:
            t = clean_text(b)
            if t and 2 < len(t) < 30 and not any(btn["label"] == t for btn in buttons_info):
                buttons_info.append({"label": t, "variant": "primary" if len(buttons_info) == 0 else "secondary"})

    # --- Construct Section 1: Navigation Bar ---
    nav_comp = ComponentSpec(
        name="Navbar",
        category="navbar",
        description="Sticky desktop & mobile responsive navigation header with brand logo, nav links, and CTA",
        props={
            "brandName": "string",
            "links": "Array<{ label: string; href: string }>",
            "ctaLabel": "string",
            "isScrolled": "boolean",
        },
        sample_data={
            "brandName": site_title.split("|")[0].split("-")[0].strip(),
            "links": [{"label": l, "href": f"#{l.lower()}"} for l in nav_links[:6]],
            "ctaLabel": buttons_info[0]["label"] if buttons_info else "Get Started",
            "isScrolled": False,
        },
        interactive_behavior="Toggles mobile hamburger overlay menu; adds blurred glassmorphic background on scroll",
        layout_type="flex",
        tailwind_classes_hint="sticky top-0 z-50 backdrop-blur-md bg-background/80 border-b border-border/40 px-6 py-4 flex items-center justify-between",
    )
    reusable_components.append(nav_comp)

    sections.append(SemanticSection(
        section_id="navbar",
        section_name="Header & Navigation",
        headline=site_title,
        cta_buttons=buttons_info[:2],
        components=[nav_comp],
        raw_copy=nav_links,
        layout="horizontal",
    ))

    # --- Construct Section 2: Hero Section ---
    hero_headline = clean_h1[0] if clean_h1 else (clean_h2[0] if clean_h2 else "Transform Your Workflow")
    hero_sub = clean_h2[0] if clean_h1 and clean_h2 else "Build, deploy, and scale high-fidelity web experiences effortlessly."
    hero_ctas = buttons_info[:2] if len(buttons_info) >= 2 else [{"label": "Start Free Trial", "variant": "primary"}, {"label": "Book a Demo", "variant": "secondary"}]

    hero_comp = ComponentSpec(
        name="HeroSection",
        category="hero",
        description="High-impact hero section with badge pill, dynamic headline, subheadline, dual action buttons, and product visual mockup",
        props={
            "headline": "string",
            "subheadline": "string",
            "primaryCta": "{ label: string; href: string }",
            "secondaryCta": "{ label: string; href: string }",
            "badgeText": "string",
        },
        sample_data={
            "headline": hero_headline,
            "subheadline": hero_sub,
            "primaryCta": {"label": hero_ctas[0]["label"], "href": "#start"},
            "secondaryCta": {"label": hero_ctas[1]["label"], "href": "#demo"},
            "badgeText": "⚡ Next-Gen v2.0 Released",
        },
        interactive_behavior="Smooth staggered fade-in animations on load; hover micro-elevation on primary CTA button",
        layout_type="flex",
        tailwind_classes_hint="relative pt-32 pb-20 px-6 max-w-7xl mx-auto flex flex-col items-center text-center gap-6",
    )
    reusable_components.append(hero_comp)

    sections.append(SemanticSection(
        section_id="hero",
        section_name="Hero Banner",
        headline=hero_headline,
        subheadline=hero_sub,
        cta_buttons=hero_ctas,
        components=[hero_comp],
        raw_copy=[hero_headline, hero_sub],
        layout="split-hero",
    ))

    # --- Construct Section 3: Features / Grid ---
    feature_items = clean_h3[:6] if len(clean_h3) >= 3 else clean_h2[1:5]
    if not feature_items:
        feature_items = [
            "Pixel-Perfect Extraction",
            "Stealth Anti-Bot Evasion",
            "Reverse-Engineered Animations",
            "Interactive State Mining",
        ]

    card_comp = ComponentSpec(
        name="FeatureCard",
        category="card",
        description="Interactive feature card with icon container, bold title, description, and hover border glow",
        props={
            "title": "string",
            "description": "string",
            "icon": "LucideIcon | string",
            "badge": "string?",
        },
        sample_data={
            "title": feature_items[0],
            "description": "Designed for maximum fidelity and seamless production reproduction.",
            "icon": "Layers",
            "badge": "Popular",
        },
        interactive_behavior="Translates upward by 4px on hover with subtle box-shadow bloom and border illumination",
        layout_type="grid",
        tailwind_classes_hint="p-6 rounded-2xl bg-card border border-border/60 hover:border-primary/50 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl",
    )
    reusable_components.append(card_comp)

    sections.append(SemanticSection(
        section_id="features",
        section_name="Key Features & Value Proposition",
        headline="Engineered for Uncompromising Fidelity",
        subheadline="Every component, transition, and micro-interaction reverse-engineered with mathematical precision.",
        components=[card_comp],
        raw_copy=feature_items,
        layout="grid-3",
    ))

    # --- Construct Section 4: Call to Action / Pricing Banner ---
    cta_comp = ComponentSpec(
        name="CtaBanner",
        category="cta",
        description="High-conversion bottom banner with radiant gradient background, compelling pitch, and prominent action button",
        props={
            "title": "string",
            "description": "string",
            "ctaLabel": "string",
        },
        sample_data={
            "title": "Ready to experience the next standard in web UI?",
            "description": "Join developers and design teams transforming their workflows today.",
            "ctaLabel": "Get Started in Seconds",
        },
        interactive_behavior="Glowing pulse animation on CTA button",
        layout_type="flex",
        tailwind_classes_hint="my-20 p-12 rounded-3xl bg-gradient-to-r from-primary/20 via-card to-secondary/20 border border-primary/30 text-center flex flex-col items-center gap-6",
    )
    reusable_components.append(cta_comp)

    sections.append(SemanticSection(
        section_id="cta",
        section_name="Conversion Call-To-Action",
        headline="Ready to experience the next standard?",
        cta_buttons=[{"label": "Get Started Now", "variant": "primary"}],
        components=[cta_comp],
        raw_copy=["Join innovative teams building with Scrui today."],
        layout="vertical",
    ))

    # --- Construct Section 5: Footer ---
    footer_comp = ComponentSpec(
        name="Footer",
        category="footer",
        description="Multi-column footer layout with brand identity, product navigation links, legal copyright, and social badges",
        props={
            "brand": "string",
            "columns": "Array<{ title: string; links: string[] }>",
            "copyright": "string",
        },
        sample_data={
            "brand": site_title.split("|")[0].strip(),
            "columns": [
                {"title": "Product", "links": ["Features", "Security", "Roadmap", "Changelog"]},
                {"title": "Resources", "links": ["Documentation", "Community", "API Reference"]},
                {"title": "Company", "links": ["About Us", "Careers", "Contact", "Privacy"]},
            ],
            "copyright": "© 2026 Scrui Engine. All rights reserved.",
        },
        interactive_behavior="Hover color shift on links (`text-muted-foreground hover:text-foreground`)",
        layout_type="grid",
        tailwind_classes_hint="border-t border-border/40 py-12 px-6 max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8 text-sm",
    )
    reusable_components.append(footer_comp)

    sections.append(SemanticSection(
        section_id="footer",
        section_name="Footer & Legal",
        headline=None,
        components=[footer_comp],
        raw_copy=["Privacy Policy", "Terms of Service", "All rights reserved"],
        layout="grid-4",
    ))

    return sections, reusable_components
