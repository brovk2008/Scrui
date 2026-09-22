<p align="center">
  <img src="image.png" alt="Scrui Logo" width="520" />
</p>

<h1 align="center">Scrui</h1>

<p align="center">
  <strong>High-Fidelity Predictive UI Extraction, Reverse-Engineering & AI Prompt Engine</strong><br/>
  <em>Production-grade browser orchestration, predictive timeline telemetry, animation rebinding, behavioral state mining, pixel-perfect reconstruction & UI-to-Prompt synthesis</em>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.10%2B-ff2a85.svg" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/UI_Theme-8--bit_Blue_|_Cyber_Pink-00a2ff.svg" alt="Theme"></a>
  <a href="#"><img src="https://img.shields.io/badge/Architecture-Layer--1_to_Layer_5-brightgreen.svg" alt="Architecture"></a>
</p>

---

## ⚡ Features & Capabilities

| Layer / Module | Capability |
|----------------|------------|
| **Layer -1: Pre-Flight Profiler** | Fast zero-browser edge probe, CDN/WAF detection (Cloudflare, Akamai, Imperva), tech stack fingerprinting & dynamic countdown ETA / % estimation |
| **Layer 0: Stealth Evasion** | TLS JA3/JA4/HTTP2/HTTP3 impersonation (Chrome 131), BrowserForge fingerprinting, Canvas noise seeding & WebGL spoofing |
| **Layer 1: Browser Pool** | Autonomous fallback chain: `nodriver` (CDP-direct) → `Patchright` → `Camoufox` |
| **Layer 2: DOM & Shadow DOM** | Full DOM snapshot via CDP + Declarative Shadow DOM (DSD) `getHTML()` piercing fallback |
| **Layer 2: Event Listeners** | 3-step `BackendNodeId` → `RemoteObject` → `DOMDebugger` resolution + React/Vue/Angular framework events |
| **Layer 2: Animation Engine** | CSS keyframes, WAAPI, GSAP, and Lottie inlining with automated scroll-rebind runtime generation |
| **Layer 2.5: UI Dismantler** | Reverse-engineers all elements, buttons, forms, headings, a11y contrast audit & design tokens |
| **Layer 2.6: State Explorer** | Autonomous behavioral mining: discovers hover transitions, focus rings & accordion disclosures |
| **Layer 3: Asset & Deduplication** | SHA-256 asset content-hash deduplication + searchable SQLite index (`assets.db`) |
| **Layer 3: JS Deobfuscation** | webcrack debundling + Qwen2.5-Coder identifier renaming |
| **Layer 4: Assembly & Auto-Correct**| Self-contained single-file HTML clone + closed-loop visual auto-correction engine |
| **Layer 5: UI-to-Prompt Synthesizer**| **The Ultimate Feature**: Compiles the entire UI into an exact Master AI Prompt (`PROMPT.md`) for Claude 3.7 Sonnet, Cursor, v0.dev, and Lovable |
| **CAPTCHA Solving** | 2captcha v2 API — reCAPTCHA v2/v3, hCaptcha, Turnstile, DataDome slider |
| **Site Crawler & Sitemap** | Async BFS crawler with robots.txt, sitemap.xml & interactive link hierarchy graph |
| **CLI & TUI Experience** | Retro 8-bit electric blue logo (`#00a2ff`), cyberpunk pink UI (`#ff2a85`), and real-time operational telemetry |

---

## 🔮 Layer 5: UI-to-Prompt Synthesizer (The Ultimate Feature)

Have you ever tried pasting raw HTML into Claude, Cursor, or v0 to recreate a website?
- ❌ **30,000 lines of messy div-soup** exhausts the context window.
- ❌ **Legacy bundle classes and inline SVG blobs** cause the AI to hallucinate and copy old hacks.
- ❌ **No understanding of real design tokens or micro-interactions**.

### The Solution: Semantic Spec & Master Prompt Synthesis

Layer 5 turns Scrui into a **frontend compiler for AI models**. Instead of raw HTML, it synthesizes all reverse-engineered telemetry into a **structured, modular Master Prompt (`PROMPT.md`) and Technical Specification (`SPEC.md`)**:

1. **Normalized Design Tokens**: Extracts brand primaries, secondaries, surface elevations, radius scales, and generates production-ready Tailwind configs.
2. **Component AST Decomposition**: Groups the page into semantic sections (`Navbar`, `Hero`, `FeatureGrid`, `PricingTable`, `Testimonials`, `Footer`) and generates typed TypeScript prop interfaces (`interface FeatureCardProps`).
3. **Exact Copy & Content Matrix**: Extracts verbatim headlines, subheadings, paragraphs, and button labels so the LLM doesn't make up generic *Lorem Ipsum*.
4. **State Machine Blueprints**: Converts mined interactive behaviors into clean React hooks (`useState`, `useEffect`) for mobile menus, accordions, tabs, and modals.
5. **Declarative Motion Presets**: Converts WAAPI and CSS keyframes into Framer Motion variants and scroll reveals.

---

### How to Use UI-to-Prompt Synthesis

#### Method 1: Dedicated `prompt` CLI Command (Fastest)

```bash
# 1. Synthesize a Next.js 15 App Router + Tailwind Master Prompt
scrui prompt https://stripe.com

# 2. Synthesize a v0.dev / Lovable component prompt
scrui prompt https://linear.app --target v0

# 3. Synthesize Cursor / Windsurf rules (.cursorrules + task list)
scrui prompt https://airbnb.com --target cursor

# 4. Synthesize for React 19 or Vue 3
scrui prompt https://supabase.com --target react
scrui prompt https://vuejs.org --target vue
```

#### Method 2: Enable during full cloning

```bash
# Clone the site AND generate the Master Prompt in one pass
scrui clone https://example.com --prompt --prompt-target nextjs
```

#### Method 3: In `config.yaml`

```yaml
prompt_gen:
  enabled: true
  target: nextjs  # nextjs, react, v0, cursor, vue, svelte
```

---

### Supported Prompt Targets

| Target | Output Artifact | Optimized For |
| ------ | --------------- | ------------- |
| **`nextjs`** (Default) | Full Next.js 15 App Router architecture (`page.tsx`, `components/`, `tailwind.config.ts`, `lib/animations.ts`) | Production web applications, Next.js developers |
| **`v0`** | Single-file, ultra-dense component-first prompt with Lucide icons | [v0.dev](https://v0.dev), [Lovable.dev](https://lovable.dev), [Bolt.new](https://bolt.new) |
| **`cursor`** | `.cursorrules` + component specifications + progressive task checklist | Cursor AI IDE, Windsurf, Claude Code |
| **`react`** | Modular React 19 + TypeScript + Tailwind CSS structure | Vite / React SPAs |
| **`vue`** | Vue 3 Single File Components (`<script setup lang='ts'>`) | Nuxt.js / Vue projects |
| **`svelte`** | SvelteKit 2 + Tailwind component blueprints | Svelte developers |

---

### What Gets Generated?

Every prompt run outputs a dedicated `prompt/` directory inside `data_structure/`:

```
data_structure/
└── prompt/
    ├── PROMPT.md               ← The Master Copy-Paste Prompt for LLMs
    ├── SPEC.md                 ← Technical design specification & CSS variables
    └── components_schema.json  ← Formal JSON component hierarchy & prop types
```

### 📋 The 30-Second Workflow

1. Run:
   ```bash
   scrui prompt https://stripe.com
   ```
2. Open `clones/site_cloned_stripe_.../data_structure/prompt/PROMPT.md`.
3. Copy the entire file contents and paste them directly into **Claude 3.7 Sonnet**, **GPT-4o**, **Cursor**, or **v0.dev**.
4. The AI immediately writes the **exact**, production-ready, pixel-identical frontend from scratch!

---

## 📂 Complete Output Structure

Every clone produces a clean dual-folder layout separating the standalone cloned website from its reverse-engineered data structure:

```
clones/
└── site_cloned_example-com_20260922_183045/
    ├── example-com/               ← The cloned website (named after the target)
    │   ├── index.html             ← Self-contained, interactive single-file HTML clone
    │   └── assets/                ← Extracted and deduplicated assets
    │       ├── images/            ← Images (deduplicated by SHA-256)
    │       ├── fonts/             ← Web fonts (WOFF2/TTF)
    │       ├── videos/            ← Video media
    │       ├── css/               ← Extracted stylesheets
    │       └── js/                ← Scripts & runtime shims
    └── data_structure/            ← Comprehensive reverse-engineered data
        ├── prompt/                ← 🔮 Layer 5 Prompt Synthesis
        │   ├── PROMPT.md          ← Master copy-paste prompt for AI coding models
        │   ├── SPEC.md            ← Design system tokens & technical specification
        │   └── components_schema.json ← Typed component interfaces & section hierarchy
        ├── preflight.json         ← Layer -1 Target profile, WAF fingerprint & execution plan
        ├── manifest.json          ← Metadata, timing, engine & analysis summary
        ├── assets.db              ← SQLite database indexing all assets with SHA-256 hashes
        ├── assets.jsonl           ← Asset metadata stream (URL, hash, size, mime, path)
        ├── elements.jsonl         ← Dismantled UI elements with bounding boxes & computed styles
        ├── components.json        ← Button/form/navigation inventory & a11y audit
        ├── design_system.json     ← Extracted color palette, typography & design tokens
        ├── behavior.json          ← Mined hover transitions, focus rings & disclosures
        ├── auto_corrections.json  ← Visual optimizer iteration history & CSS patches
        ├── dom_tree.json          ← Complete serializable DOM tree
        ├── events.json            ← Event listeners & framework event mappings
        ├── animations.json        ← Extracted keyframes & synthetic GSAP timeline
        └── shadow_dom.json        ← Pierced Shadow DOM roots & slot maps
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/brovk2008/Scrui.git
cd Scrui

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Install browser runtimes
python -m playwright install chromium
python -m camoufox fetch  # Patched Firefox
```

---

## 💻 CLI Commands & UI Experience

When running Scrui in CMD or PowerShell, the interface displays the **8-bit Electric Blue Logo** (`#00a2ff`) with a **Neon Pink Theme** (`#ff2a85`) and live telemetry tracking.

### 1. Clone a Website (with Layer -1 Telemetry)
```bash
scrui clone https://stripe.com
```

Before launching the browser, **Layer -1** analyzes the target and displays a pre-flight profile:
- Target Host, IP, and round-trip network latency
- Edge CDN & WAF detection (Cloudflare cf-ray, Akamai, CloudFront)
- Technology stack (Next.js, React, Tailwind CSS, GSAP, etc.)
- Resource volume & DOM complexity score
- Predicted timeline and dynamic ETA countdown (`~00:24 left`)

### 2. Synthesize UI to Master AI Prompt
```bash
scrui prompt https://stripe.com --target nextjs
```

### 3. Dismantle UI Elements & Tokens
```bash
scrui dismantle https://example.com
```

### 4. Crawl Site & Generate Comprehensive Sitemap
```bash
scrui crawl https://example.com --max-pages 50 --depth 3
```

### 5. Interactive Terminal UI (TUI)
```bash
scrui tui
```

---

## ⚙️ Configuration

All settings can be configured via [`config.yaml`](./config.yaml) or CLI options:

```yaml
preflight:
  enabled: true                    # Run Layer -1 target profiler & ETA estimator
  probe_timeout_seconds: 6.0
  estimate_timeline: true
  save_preflight_report: true      # Saves data_structure/preflight.json

prompt_gen:
  enabled: false                   # Optional Layer 5: UI-to-Prompt Synthesizer
  target: nextjs                   # nextjs, react, v0, cursor, vue, svelte
  include_screenshot_context: true
  include_state_machine: true
  include_motion_specs: true
  include_copy_inventory: true

browser:
  primary_engine: nodriver         # nodriver, patchright, camoufox
  headless: false
  network_idle_timeout_ms: 2000

storage:
  images: base64                   # base64, raw, both, url
  fonts: base64                    # base64, raw, url
  data_format: jsonl               # jsonl, json, both
  deduplicate_assets: true         # SHA-256 deduplication
  build_sqlite_index: true         # Generates assets.db

analysis:
  enabled: true                    # UI element dismantler
  explore_states: true             # Hover/focus mining

validation:
  auto_correct: true               # Closed-loop visual optimizer
  fidelity_threshold_percent: 95.0
```

---

## 🏗️ Architecture Pipeline

```text
       TARGET URL
           │
           ▼ Layer -1 — Pre-Flight Profiler & Predictive Telemetry Oracle
           │  Fast edge probe · WAF detection · Tech stack fingerprinting
           │  Dynamic ETA countdown · % completed · Live operational tracking
           │
           ▼ Layer 0 — Anti-Bot Evasion & Fingerprinting
           │  TLS impersonation (Chrome 131) · BrowserForge profiles · Canvas noise
           │
           ▼ Layer 1 — Stealth Browser Orchestration Pool
           │  nodriver / Patchright / Camoufox · CDP connection · Stealth scripts
           │
           ▼ Layer 2 — DOM, Event & Animation Extraction
           │  DOM snapshotting · DSD Shadow DOM piercing · DOMDebugger listeners
           │  CSS Keyframes · WAAPI · GSAP timeline baking · Scroll drivers
           │
           ▼ Layer 2.5 & 2.6 — UI Dismantler & State Explorer
           │  Button & component breakdown · Contrast audit · Hover/focus mining
           │
           ▼ Layer 3 — Asset Pipeline, Deduplication & Deobfuscation
           │  SHA-256 deduplication · SQLite indexing (`assets.db`) · webcrack
           │
           ▼ Layer 4 — Single-File HTML Assembly & Visual Auto-Correction
           │  Single-file packaging · Inlined runtimes · Closed-loop pixel diff
           │
           ▼ Layer 5 — UI-to-Prompt Synthesizer (Optional)
           │  Design tokens · Component AST · Copy matrix · State machine · Motion
           │  Compiles PROMPT.md, SPEC.md & components_schema.json
           │
           ▼ OUTPUT
              ├── <site_name>/index.html (Single-file pixel-identical clone)
              └── data_structure/
                  ├── prompt/ (PROMPT.md for Claude, Cursor, v0.dev)
                  ├── preflight.json (Edge & WAF telemetry)
                  └── assets.db (Searchable SQLite index)
```

---

## 🤝 Community & Contributing

We welcome contributions to Scrui! Please review our community guidelines:

- **[Contributing Guide](CONTRIBUTING.md)** — Development setup, architecture guides, and PR checklist.
- **[Code of Conduct](CODE_OF_CONDUCT.md)** — Contributor Covenant v2.1 standards.
- **[Security Policy](SECURITY.md)** — Responsible vulnerability disclosure instructions.
- **[Support Guide](SUPPORT.md)** — Getting help, FAQs, and discussions.
- **[Changelog](CHANGELOG.md)** — Release history and feature breakdown.

---

## 📄 License

This project is licensed under the **Apache License 2.0** — see the [LICENSE](LICENSE) file for details.
