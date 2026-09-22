"""
Scrui Vector & SVG Icon Classifier.
Analyzes extracted inline SVGs, path signatures, and semantic attributes,
mapping them to standard Lucide React / Heroicon components instead of
dumping 500-line SVG path blobs into prompts.
"""
from __future__ import annotations

import re
from typing import Optional, Dict, Any, List, Set
from dataclasses import dataclass


@dataclass
class MatchedIcon:
    name: str
    library: str
    jsx: str
    confidence: float
    original_size: Optional[str] = None


# Semantic keywords mapped to canonical Lucide React icon names
SEMANTIC_ICON_KEYWORDS = {
    # Navigation & Actions
    "search": "Search",
    "magnify": "Search",
    "find": "Search",
    "menu": "Menu",
    "hamburger": "Menu",
    "close": "X",
    "cross": "X",
    "dismiss": "X",
    "chevron-down": "ChevronDown",
    "arrow-down": "ArrowDown",
    "chevron-up": "ChevronUp",
    "arrow-up": "ArrowUp",
    "chevron-right": "ChevronRight",
    "arrow-right": "ArrowRight",
    "chevron-left": "ChevronLeft",
    "arrow-left": "ArrowLeft",
    "external": "ExternalLink",
    "outbound": "ExternalLink",
    "open-in-new": "ExternalLink",
    "refresh": "RotateCw",
    "reload": "RotateCw",
    "filter": "Filter",
    "sort": "ArrowUpDown",
    "download": "Download",
    "upload": "Upload",
    "copy": "Copy",
    "share": "Share2",

    # Status & Feedback
    "check": "Check",
    "success": "CheckCircle2",
    "alert": "AlertTriangle",
    "warning": "AlertTriangle",
    "error": "AlertCircle",
    "info": "Info",
    "help": "HelpCircle",
    "question": "HelpCircle",
    "loader": "Loader2",
    "spinner": "Loader2",

    # Commerce & Identity
    "user": "User",
    "profile": "User",
    "avatar": "User",
    "users": "Users",
    "team": "Users",
    "cart": "ShoppingCart",
    "basket": "ShoppingBag",
    "bag": "ShoppingBag",
    "heart": "Heart",
    "favorite": "Heart",
    "star": "Star",
    "rating": "Star",
    "bell": "Bell",
    "notification": "Bell",
    "mail": "Mail",
    "envelope": "Mail",
    "phone": "Phone",
    "lock": "Lock",
    "unlock": "Unlock",
    "shield": "ShieldCheck",
    "trash": "Trash2",
    "delete": "Trash2",
    "edit": "Pencil",
    "pencil": "Pencil",
    "plus": "Plus",
    "add": "Plus",
    "minus": "Minus",
    "eye": "Eye",
    "eye-off": "EyeOff",
    "calendar": "Calendar",
    "clock": "Clock",
    "time": "Clock",
    "settings": "Settings",
    "gear": "Settings",
    "globe": "Globe",
    "link": "Link",

    # Theme
    "moon": "Moon",
    "dark": "Moon",
    "sun": "Sun",
    "light": "Sun",

    # Social & Brands
    "github": "Github",
    "twitter": "Twitter",
    "x-logo": "Twitter",
    "linkedin": "Linkedin",
    "youtube": "Youtube",
    "discord": "MessageSquare",
    "slack": "Slack",
}


class IconMatcher:
    """Matches raw inline SVGs to clean Lucide React component imports."""

    def __init__(self, target_library: str = "lucide-react"):
        self.target_library = target_library
        self.imported_icons: Set[str] = set()

    def match_svg(self, svg_html: str, context_hint: str = "") -> Optional[MatchedIcon]:
        """
        Analyze an SVG HTML string and its context (class, parent button text, aria-label).
        Returns a MatchedIcon if a confident match is found, else None.
        """
        if not svg_html or "<svg" not in svg_html.lower():
            return None

        # 1. Attribute matching (aria-label, data-icon, title, class, id)
        attr_text = self._extract_attributes(svg_html) + " " + context_hint.lower()

        for keyword, icon_name in SEMANTIC_ICON_KEYWORDS.items():
            pattern = rf"(?:^|[\-_/\s\"']){re.escape(keyword)}(?:$|[\-_/\s\"'])"
            if re.search(pattern, attr_text):
                self.imported_icons.add(icon_name)
                jsx = f"<{icon_name} className=\"w-5 h-5\" />"
                return MatchedIcon(
                    name=icon_name,
                    library=self.target_library,
                    jsx=jsx,
                    confidence=0.92,
                )

        # 2. Geometric heuristic analysis on SVG <path d="...">
        path_match = self._geometric_classify(svg_html)
        if path_match:
            self.imported_icons.add(path_match.name)
            return path_match

        return None

    def _extract_attributes(self, svg_html: str) -> str:
        attrs = []
        for attr_name in ["aria-label", "data-icon", "data-name", "title", "id", "class", "name"]:
            m = re.search(rf'{attr_name}=["\']([^"\']+)["\']', svg_html, re.IGNORECASE)
            if m:
                attrs.append(m.group(1).lower())
        return " ".join(attrs)

    def _geometric_classify(self, svg_html: str) -> Optional[MatchedIcon]:
        """Classify simple common geometric icon patterns."""
        lower = svg_html.lower()

        # Hamburger Menu: 3 horizontal lines or path with multiple M...H
        if lower.count("<line") == 3 or re.search(r"m\d+\s+\d+h\d+.*m\d+\s+\d+h\d+.*m\d+\s+\d+h\d+", lower):
            return MatchedIcon(name="Menu", library=self.target_library, jsx='<Menu className="w-5 h-5" />', confidence=0.85)

        # Close / Cross: 2 intersecting diagonal lines
        if lower.count("<line") == 2 and ("x1=" in lower or "y1=" in lower):
            return MatchedIcon(name="X", library=self.target_library, jsx='<X className="w-5 h-5" />', confidence=0.85)

        # Search: Circle + diagonal line
        if "<circle" in lower and "<line" in lower:
            return MatchedIcon(name="Search", library=self.target_library, jsx='<Search className="w-5 h-5" />', confidence=0.88)

        # Checkmark: Polyline or single path with 3 points
        if "<polyline" in lower and ("points=" in lower or "20 6" in lower or "9 17" in lower):
            return MatchedIcon(name="Check", library=self.target_library, jsx='<Check className="w-5 h-5 text-green-500" />', confidence=0.82)

        return None

    def get_import_header(self) -> str:
        """Returns the consolidated ES module import statement for matched icons."""
        if not self.imported_icons:
            return ""
        icons_list = sorted(list(self.imported_icons))
        return f'import {{ {", ".join(icons_list)} }} from "{self.target_library}";'
