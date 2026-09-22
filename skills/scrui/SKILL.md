---
name: scrui
description: High-fidelity predictive UI extraction, reverse-engineering, pixel-identical cloning, and AI prompt synthesis. Use when the user asks to clone, scrape, copy, dismantle, extract design tokens from, inspect, or synthesize a website UI into production code (Next.js 15, React 19, Tailwind CSS) or AI prompts for Claude 3.7, Cursor, or v0.dev.
---

# Scrui Agent Skill

Scrui is an autonomous frontend reverse-engineering and UI cloning engine. It extracts live DOM trees, pierced Shadow DOMs, computed CSS styles, design tokens, micro-interactions, and animations, and can synthesize entire websites into **Next.js 15 / React codebases** or **Master AI Prompts** for Claude 3.7 Sonnet, Cursor, and v0.dev.

---

## ⚡ When to Use This Skill

Activate and use Scrui whenever the user says:
- *"Clone this website..."* or *"Make an exact copy of..."*
- *"Convert this site into a prompt for Claude / Cursor / v0..."*
- *"Generate a Next.js 15 project reproducing this site..."*
- *"Extract the color palette, fonts, and design tokens from..."*
- *"Dismantle all elements, buttons, and navigation from..."*
- *"Compare this clone against the original site..."*

---

## 🛠️ CLI Quick Reference for Agents

Always run commands via terminal in the workspace directory:

### 1. Synthesize UI to Master AI Prompt (Fastest)
Converts a website into a structured `PROMPT.md`, `SPEC.md`, and `components_schema.json` with Lucide icons and Tailwind tokens:
```bash
scrui prompt <url> --target nextjs
```
Supported targets: `nextjs`, `v0`, `cursor`, `react`, `vue`, `svelte`.

### 2. Scaffold a Complete Next.js 15 Project Directly to Disk
Generates a runnable Next.js 15 App Router project (`package.json`, `tailwind.config.ts`, `app/page.tsx`, `components/`):
```bash
scrui generate <url> --out ./my_app --target nextjs
```
After running, advise the user:
```bash
cd my_app && npm install && npm run dev
```

### 3. Full Pixel-Identical Clone with Visual Auto-Correction
Clones the site into a standalone single-file HTML clone with inlined fonts, images, and baked animation runtimes:
```bash
scrui clone <url>
```
To also generate the Master Prompt in the same pass:
```bash
scrui clone <url> --prompt --prompt-target nextjs
```

### 4. Extract Design Tokens & W3C DTCG / Figma Tokens
Dismantles the site and extracts all tokens into `data_structure/tokens.json` and `data_structure/figma_tokens.json`:
```bash
scrui dismantle <url>
```

### 5. Launch Visual Diff & Telemetry Inspector
Opens the interactive web dashboard on `http://127.0.0.1:3888` for split-screen visual diffs and token inspection:
```bash
scrui inspect [clone_dir]
```

### 6. Listen for Authenticated Tab Captures (Chrome Extension)
Starts the local relay daemon on port 9222 for 1-click captures of logged-in sessions:
```bash
scrui listen --port 9222
```

---

## 📂 Output Directory Schema

Every run creates a folder in `./clones/`:
```
clones/site_cloned_<slug>_<timestamp>/
├── <slug>/
│   ├── index.html                    # Single-file interactive HTML clone
│   └── assets/                       # SHA-256 deduplicated assets
└── data_structure/
    ├── prompt/
    │   ├── PROMPT.md                 # Master prompt for LLMs
    │   ├── SPEC.md                   # Technical design specification
    │   └── components_schema.json    # Typed component interfaces & prop types
    ├── tokens.json                   # W3C DTCG format tokens
    ├── figma_tokens.json             # Tokens Studio for Figma format
    ├── preflight.json                # Layer -1 WAF, CDN & tech stack profile
    ├── assets.db                     # SQLite index of all assets
    ├── elements.jsonl                # Dismantled UI elements with computed styles
    ├── components.json               # Button/form/navigation inventory & a11y audit
    ├── design_system.json            # Extracted palette and typography scale
    └── behavior.json                 # Mined hover transitions & disclosures
```

---

## 🤖 Agent Autonomous Code-Generation Workflow

When an agent is asked to **recreate a website in code**:
1. Run `scrui prompt <url> --target nextjs` or `scrui generate <url> --out ./clone`.
2. Inspect `data_structure/prompt/components_schema.json` to read the exact component hierarchy, prop contracts, and Lucide icon imports.
3. Read `data_structure/prompt/PROMPT.md` to get verbatim headlines, body copy, and CTA button labels so no text is hallucinated.
4. Read `data_structure/tokens.json` to get exact primary, secondary, background, and surface hex codes.
5. Generate the frontend files according to the specification.
