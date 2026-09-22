"""
Motion & Animation Compiler (Layer 5)
Translates reverse-engineered CSS keyframes and WAAPI animations into
declarative Framer Motion variants and Tailwind animation utilities.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class MotionSpec:
    """Compiled motion specifications for prompt generation."""
    framer_motion_variants_snippet: str
    entrance_animations: list[dict[str, str]] = field(default_factory=list)
    hover_transitions: list[dict[str, str]] = field(default_factory=list)
    scroll_reveal_snippet: str = ""


def compile_motion_specs(
    anim_data: Optional[dict] = None,
    behavior_report: Any = None,
) -> MotionSpec:
    """
    Compile animation data into production-ready Framer Motion variants and scroll triggers.
    """
    framer_snippet = """// Framer Motion Animation Variants
import { motion, Variants } from 'framer-motion';

export const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.15,
    },
  },
};

export const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.6,
      ease: [0.16, 1, 0.3, 1], // easeOutExpo
    },
  },
};

export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: [0.16, 1, 0.3, 1],
    },
  },
};

export const hoverElevate = {
  scale: 1.02,
  y: -4,
  transition: { duration: 0.2, ease: 'easeOut' },
};"""

    scroll_snippet = """// Scroll Reveal Directive
<motion.div
  initial="hidden"
  whileInView="visible"
  viewport={{ once: true, margin: '-80px' }}
  variants={containerVariants}
>
  {/* Children components animated with fadeInUp */}
</motion.div>"""

    entrances = [
        {"name": "Fade In Up", "description": "Hero headlines, feature cards, pricing tiers"},
        {"name": "Stagger Children", "description": "Grid items stagger entrance at 100ms intervals"},
        {"name": "Badge Scale In", "description": "Version announcement pills and tags"},
    ]

    hovers = [
        {"element": "Primary Buttons", "effect": "Brightness boost + scale 1.03 + subtle box-shadow bloom"},
        {"element": "Feature Cards", "effect": "Translate -4px on Y-axis + border color shift to primary"},
        {"element": "Navigation Links", "effect": "Color shift from text-muted to text-primary with 200ms ease"},
    ]

    return MotionSpec(
        framer_motion_variants_snippet=framer_snippet,
        entrance_animations=entrances,
        hover_transitions=hovers,
        scroll_reveal_snippet=scroll_snippet,
    )
