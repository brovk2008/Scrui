"""
Design Token Compiler (Layer 5)
Compiles reverse-engineered colors, typography, elevations, and radii
into production-ready Tailwind CSS configurations and CSS variable design systems.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class DesignTokenSpec:
    """Compiled design system specification for prompt injection."""
    primary_color: str
    secondary_color: str
    background_color: str
    surface_color: str
    text_color: str
    text_muted_color: str
    border_color: str
    font_sans: str
    font_heading: str
    border_radius: str
    box_shadow: str
    tailwind_theme_snippet: str
    css_variables_snippet: str


def compile_design_tokens(
    dismantle_report: Any = None,
    dom_data: Optional[dict] = None,
) -> DesignTokenSpec:
    """
    Extract and normalize color tokens, typography scales, and elevations
    into a structured design token specification.
    """
    # Defaults
    primary = "#00a2ff"       # Electric Blue
    secondary = "#ff2a85"     # Neon Pink
    background = "#09090b"    # Zinc 950 Dark
    surface = "#18181b"       # Zinc 900
    text = "#fafafa"          # Zinc 50
    text_muted = "#a1a1aa"    # Zinc 400
    border = "#27272a"        # Zinc 800
    font_sans = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    font_heading = "Outfit, Inter, sans-serif"
    radius = "0.75rem"        # 12px / rounded-xl
    shadow = "0 10px 30px -10px rgba(0, 0, 0, 0.5)"

    # Extract from dismantle_report if available
    if dismantle_report and hasattr(dismantle_report, "design_system"):
        ds = dismantle_report.design_system
        colors = getattr(ds, "color_palette", [])
        bg_colors = getattr(ds, "background_colors", [])
        fonts = getattr(ds, "font_families", [])

        if colors:
            primary = colors[0]
            if len(colors) > 1:
                secondary = colors[1]
        if bg_colors:
            background = bg_colors[0]
            if len(bg_colors) > 1:
                surface = bg_colors[1]

        if fonts:
            font_sans = fonts[0]
            font_heading = fonts[0]
            if len(fonts) > 1:
                font_heading = fonts[1]

    # Tailwind configuration block
    tailwind_snippet = f"""// tailwind.config.ts
import type {{ Config }} from 'tailwindcss';

const config: Config = {{
  darkMode: ['class'],
  content: ['./pages/**/*.{{js,ts,jsx,tsx,mdx}}', './components/**/*.{{js,ts,jsx,tsx,mdx}}', './app/**/*.{{js,ts,jsx,tsx,mdx}}'],
  theme: {{
    extend: {{
      colors: {{
        primary: {{
          DEFAULT: '{primary}',
          foreground: '#ffffff',
        }},
        secondary: {{
          DEFAULT: '{secondary}',
          foreground: '#ffffff',
        }},
        background: '{background}',
        foreground: '{text}',
        card: {{
          DEFAULT: '{surface}',
          foreground: '{text}',
        }},
        muted: {{
          DEFAULT: '{surface}',
          foreground: '{text_muted}',
        }},
        border: '{border}',
      }},
      fontFamily: {{
        sans: ['{font_sans.split(",")[0].replace("'", "").strip()}', 'sans-serif'],
        heading: ['{font_heading.split(",")[0].replace("'", "").strip()}', 'sans-serif'],
      }},
      borderRadius: {{
        DEFAULT: '{radius}',
        lg: '{radius}',
        xl: '1rem',
        '2xl': '1.5rem',
      }},
      boxShadow: {{
        glow: '0 0 25px -5px {primary}40',
        card: '{shadow}',
      }},
    }},
  }},
  plugins: [],
}};
export default config;"""

    # CSS Variables snippet
    css_vars_snippet = f""":root {{
  --primary: {primary};
  --secondary: {secondary};
  --background: {background};
  --card: {surface};
  --foreground: {text};
  --muted: {text_muted};
  --border: {border};
  --radius: {radius};
  --font-sans: {font_sans};
  --font-heading: {font_heading};
}}"""

    return DesignTokenSpec(
        primary_color=primary,
        secondary_color=secondary,
        background_color=background,
        surface_color=surface,
        text_color=text,
        text_muted_color=text_muted,
        border_color=border,
        font_sans=font_sans,
        font_heading=font_heading,
        border_radius=radius,
        box_shadow=shadow,
        tailwind_theme_snippet=tailwind_snippet,
        css_variables_snippet=css_vars_snippet,
    )
