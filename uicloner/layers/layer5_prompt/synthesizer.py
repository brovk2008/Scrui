"""
UI-to-Prompt Synthesizer (Layer 5)
Compiles all reverse-engineered telemetry into a Master LLM Prompt and
Technical Specification designed for Claude 3.7 Sonnet, GPT-4o, Cursor, v0.dev, and Lovable.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Any, Optional
from urllib.parse import urlparse

from uicloner.config import PromptTarget
from uicloner.layers.layer5_prompt.ast_reducer import reduce_dom_to_components, SemanticSection, ComponentSpec
from uicloner.layers.layer5_prompt.token_compiler import compile_design_tokens, DesignTokenSpec
from uicloner.layers.layer5_prompt.state_compiler import compile_state_machine, StateMachineSpec
from uicloner.layers.layer5_prompt.motion_compiler import compile_motion_specs, MotionSpec


@dataclass
class PromptBundle:
    """Complete bundle of generated prompt artifacts."""
    target_framework: str
    master_prompt: str
    technical_spec: str
    components_schema: dict[str, Any]
    summary: str


class UIPromptSynthesizer:
    """
    Master prompt compiler. Transforms raw DOM, styles, states, and animations
    into an exact prompt for AI coding models.
    """

    def __init__(self, config=None):
        self.config = config
        target = PromptTarget.NEXTJS
        if config and hasattr(config, "prompt_gen") and hasattr(config.prompt_gen, "target"):
            target = config.prompt_gen.target
        self.target = target

    def synthesize(
        self,
        url: str,
        dom_data: dict,
        dismantle_report: Any = None,
        behavior_report: Any = None,
        anim_data: Optional[dict] = None,
        asset_records: Optional[dict] = None,
    ) -> PromptBundle:
        """Generate master prompt and supporting specifications."""
        parsed = urlparse(url)
        host = parsed.netloc or "Target Application"

        # 1. Run Sub-Compilers
        outer_html = dom_data.get("outer_html", "")
        sections, components = reduce_dom_to_components(outer_html, dismantle_report, dom_data.get("doc_tree"))
        tokens = compile_design_tokens(dismantle_report, dom_data)
        state_spec = compile_state_machine(behavior_report, dom_data.get("events"))
        motion_spec = compile_motion_specs(anim_data, behavior_report)

        # 2. Build Schema Dictionary
        components_schema = {
            "source_url": url,
            "target_framework": self.target.value,
            "design_tokens": {
                "primary": tokens.primary_color,
                "secondary": tokens.secondary_color,
                "background": tokens.background_color,
                "surface": tokens.surface_color,
                "text": tokens.text_color,
                "font_sans": tokens.font_sans,
                "font_heading": tokens.font_heading,
                "radius": tokens.border_radius,
            },
            "sections": [
                {
                    "id": s.section_id,
                    "name": s.section_name,
                    "headline": s.headline,
                    "subheadline": s.subheadline,
                    "layout": s.layout,
                    "components": [c.name for c in s.components],
                    "copy_sample": s.raw_copy[:5],
                }
                for s in sections
            ],
            "reusable_components": [
                {
                    "name": c.name,
                    "category": c.category,
                    "props": c.props,
                    "layout": c.layout_type,
                    "interactive_behavior": c.interactive_behavior,
                }
                for c in components
            ],
            "state_hooks": [asdict(h) for h in state_spec.contracts],
        }

        # 3. Assemble Technical Specification (SPEC.md)
        technical_spec = self._build_technical_spec(host, url, sections, components, tokens, state_spec, motion_spec)

        # 4. Assemble Master Prompt (PROMPT.md) based on Target
        master_prompt = self._build_master_prompt(host, url, sections, components, tokens, state_spec, motion_spec)

        summary = (
            f"Synthesized {len(sections)} semantic sections, {len(components)} reusable components, "
            f"and full interactive state machine for target {self.target.value.upper()}."
        )

        return PromptBundle(
            target_framework=self.target.value,
            master_prompt=master_prompt,
            technical_spec=technical_spec,
            components_schema=components_schema,
            summary=summary,
        )

    def _build_master_prompt(
        self,
        host: str,
        url: str,
        sections: list[SemanticSection],
        components: list[ComponentSpec],
        tokens: DesignTokenSpec,
        state_spec: StateMachineSpec,
        motion_spec: MotionSpec,
    ) -> str:
        """Build the master copy-paste markdown prompt."""
        framework_instructions = self._get_framework_instructions()

        # Build Section Checklist
        sections_md = ""
        for i, s in enumerate(sections, 1):
            sections_md += f"\n### {i}. {s.section_name} (`#{s.section_id}`)\n"
            if s.headline:
                sections_md += f"- **Headline**: \"{s.headline}\"\n"
            if s.subheadline:
                sections_md += f"- **Subheadline**: \"{s.subheadline}\"\n"
            if s.cta_buttons:
                ctas_str = ", ".join(f"`{b['label']}` ({b['variant']})" for b in s.cta_buttons)
                sections_md += f"- **Action Buttons**: {ctas_str}\n"
            sections_md += f"- **Layout Structure**: `{s.layout}`\n"
            if s.raw_copy:
                copy_preview = " | ".join(f'"{c}"' for c in s.raw_copy[:4])
                sections_md += f"- **Exact Copy**: {copy_preview}\n"

        # Build Component Breakdown
        components_md = ""
        for c in components:
            components_md += f"\n#### `<{c.name} />`\n"
            components_md += f"- **Description**: {c.description}\n"
            components_md += f"- **Props Interface**:\n```typescript\ninterface {c.name}Props {{\n"
            for p_name, p_type in c.props.items():
                components_md += f"  {p_name}: {p_type};\n"
            components_md += "}\n```\n"
            components_md += f"- **Tailwind Hint**: `{c.tailwind_classes_hint}`\n"
            if c.interactive_behavior:
                components_md += f"- **Micro-Interaction**: {c.interactive_behavior}\n"

        return f"""# Master AI Prompt: Build Pixel-Identical Frontend for {host}

> **Directive**: You are an elite principal frontend engineer. Build an exact, production-ready, pixel-identical frontend reproducing the interface of **{host}** ({url}).
> **Target Toolchain**: {framework_instructions['toolchain_header']}

---

## 🎯 Architecture & Design Requirements

1. **Pixel-Perfect Aesthetic**:
   - Primary Brand Color: `{tokens.primary_color}`
   - Secondary / Accent Color: `{tokens.secondary_color}`
   - Canvas / Background: `{tokens.background_color}`
   - Card / Surface Elevation: `{tokens.surface_color}`
   - Border Contrast: `{tokens.border_color}`
   - Typography: Heading font `{tokens.font_heading.split(',')[0]}`, Body font `{tokens.font_sans.split(',')[0]}`
   - Border Radius: `{tokens.border_radius}`

2. **Tailwind CSS Configuration**:
```typescript
{tokens.tailwind_theme_snippet}
```

3. **Motion & Framer Motion Presets**:
```tsx
{motion_spec.framer_motion_variants_snippet}
```

---

## 🧩 Section-by-Section Implementation Blueprint

{sections_md}

---

## 🛠️ Reusable Component Specifications

{components_md}

---

## ⚡ Interactive State Machine & Logic Contracts

Ensure the application is fully interactive and functional:

```tsx
{state_spec.state_logic_snippet}
```

### Accessibility & Interaction Checklist:
{chr(10).join(f"- [ ] {rule}" for rule in state_spec.accessibility_rules)}

---

## 📦 Deliverables & File Structure

{framework_instructions['deliverables_guide']}

---

**Execution Rule**: Do NOT use placeholder text or generic lorem ipsum. Use the exact verbatim headlines, body copy, and button labels documented in the blueprint above. Make the interface responsive across mobile (375px), tablet (768px), and desktop (1280px+). Deliver complete, fully-implemented, compile-ready code.
"""

    def _build_technical_spec(
        self,
        host: str,
        url: str,
        sections: list[SemanticSection],
        components: list[ComponentSpec],
        tokens: DesignTokenSpec,
        state_spec: StateMachineSpec,
        motion_spec: MotionSpec,
    ) -> str:
        """Build the supporting SPEC.md technical reference."""
        return f"""# Technical Specification: {host}

**Source URL**: {url}  
**Engine**: Scrui Layer 5 UI-to-Prompt Synthesizer  
**Target Format**: {self.target.value}

---

## 1. Design System Tokens

### 1.1 Colors
- **Primary**: `{tokens.primary_color}`
- **Secondary**: `{tokens.secondary_color}`
- **Background**: `{tokens.background_color}`
- **Surface**: `{tokens.surface_color}`
- **Text**: `{tokens.text_color}`
- **Muted Text**: `{tokens.text_muted_color}`
- **Border**: `{tokens.border_color}`

### 1.2 CSS Variables
```css
{tokens.css_variables_snippet}
```

---

## 2. Layout Hierarchy
{chr(10).join(f"- `{s.section_id}`: {s.section_name} ({s.layout})" for s in sections)}

---

## 3. Interactive State Contracts
{chr(10).join(f"- `{c.name}` ({c.state_type}): {c.purpose}" for c in state_spec.contracts)}
"""

    def _get_framework_instructions(self) -> dict[str, str]:
        """Provide target-specific setup guides."""
        if self.target == PromptTarget.V0:
            return {
                "toolchain_header": "v0.dev / Lovable Single-File Next.js + Tailwind + Lucide React Component",
                "deliverables_guide": (
                    "Write a single, self-contained Next.js page component (`page.tsx`) that includes all sections, "
                    "reusable sub-components, and Lucide React icons inlined. Make it ready to paste directly into v0.dev."
                ),
            }
        elif self.target == PromptTarget.CURSOR:
            return {
                "toolchain_header": "Cursor / Windsurf AI IDE (.cursorrules + Next.js 15 App Router)",
                "deliverables_guide": (
                    "Scaffold a complete Next.js 15 project with TypeScript, Tailwind CSS, Lucide React, and Framer Motion.\n"
                    "Output files in logical order:\n"
                    "1. `tailwind.config.ts`\n"
                    "2. `components/ui/` (base components: Button, Card, Badge)\n"
                    "3. `components/sections/` (Navbar, Hero, Features, CTA, Footer)\n"
                    "4. `app/page.tsx` (Root page composing all sections)"
                ),
            }
        elif self.target == PromptTarget.REACT:
            return {
                "toolchain_header": "React 19 + Vite + Tailwind CSS + Lucide Icons",
                "deliverables_guide": (
                    "Deliver modular React components with TypeScript props interfaces and Tailwind CSS styling."
                ),
            }
        elif self.target == PromptTarget.VUE:
            return {
                "toolchain_header": "Vue 3 Composition API (`<script setup lang='ts'>`) + Tailwind CSS",
                "deliverables_guide": (
                    "Deliver clean Single File Components (.vue) utilizing Vue 3 Composition API and Tailwind."
                ),
            }
        else:
            # Default: Next.js App Router
            return {
                "toolchain_header": "Next.js 15 App Router + TypeScript + Tailwind CSS + Framer Motion + Lucide React",
                "deliverables_guide": (
                    "Scaffold a complete production-grade Next.js App Router structure:\n"
                    "├── `app/page.tsx` (Main landing page)\n"
                    "├── `components/Navbar.tsx` (Responsive header)\n"
                    "├── `components/Hero.tsx` (Hero banner with CTAs)\n"
                    "├── `components/Features.tsx` (Feature cards grid)\n"
                    "├── `components/CallToAction.tsx` (Conversion banner)\n"
                    "├── `components/Footer.tsx` (Footer navigation)\n"
                    "└── `lib/animations.ts` (Framer motion presets)"
                ),
            }


def generate_ui_prompt(
    url: str,
    config: Any,
    dom_data: dict,
    dismantle_report: Any = None,
    behavior_report: Any = None,
    anim_data: Optional[dict] = None,
    asset_records: Optional[dict] = None,
) -> PromptBundle:
    """Convenience function to synthesize a full prompt bundle."""
    synthesizer = UIPromptSynthesizer(config)
    return synthesizer.synthesize(
        url=url,
        dom_data=dom_data,
        dismantle_report=dismantle_report,
        behavior_report=behavior_report,
        anim_data=anim_data,
        asset_records=asset_records,
    )
