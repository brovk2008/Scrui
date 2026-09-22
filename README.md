<p align="center">
  <img src="image.png" alt="Scrui Logo" width="520" />
</p>

<h1 align="center">Scrui</h1>

<p align="center">
  <strong>High-Fidelity Predictive UI Extraction, Reverse-Engineering & Cloning Engine</strong><br/>
  <em>Production-grade browser orchestration, predictive timeline telemetry, animation rebinding, behavioral state mining & pixel-perfect reconstruction</em>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.10%2B-ff2a85.svg" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/UI_Theme-8--bit_Blue_|_Cyber_Pink-00a2ff.svg" alt="Theme"></a>
  <a href="#"><img src="https://img.shields.io/badge/Architecture-Layer--1_to_Layer_4-brightgreen.svg" alt="Architecture"></a>
</p>

---

## ⚡ Features & Capabilities

| Layer / Module | Capability |
|----------------|------------|
| **Layer -1: Pre-Flight Profiler** | Fast zero-browser edge probe, CDN/WAF detection (Cloudflare, Akamai, Imperva), tech stack fingerprinting & dynamic ETA / % timeline estimation |
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
| **CAPTCHA Solving** | 2captcha v2 API — reCAPTCHA v2/v3, hCaptcha, Turnstile, DataDome slider |
| **Site Crawler & Sitemap** | Async BFS crawler with robots.txt, sitemap.xml & interactive link hierarchy graph |
| **CLI & TUI Experience** | Retro 8-bit electric blue logo (`#00a2ff`), cyberpunk pink UI (`#ff2a85`), and real-time operational telemetry |

---

## 📂 Output Structure

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
uiclone clone https://stripe.com
```

Before launching the browser, **Layer -1** analyzes the target and displays a pre-flight profile:
- Target Host, IP, and round-trip network latency
- Edge CDN & WAF detection (Cloudflare cf-ray, Akamai, CloudFront)
- Technology stack (Next.js, React, Tailwind CSS, GSAP, etc.)
- Resource volume & DOM complexity score
- Predicted timeline and dynamic ETA countdown (`~00:24 left`)

### 2. Common Options
```bash
# High-speed clone saving assets both as files and embedded data
uiclone clone https://example.com --images both --fonts base64 --data-format jsonl

# With 2captcha API key
uiclone clone https://example.com --captcha-key YOUR_2CAPTCHA_KEY

# With proxy rotation
uiclone clone https://example.com --proxy proxy.host:8080:user:pass

# Using alternative browser engine (patchright or camoufox)
uiclone clone https://example.com --engine patchright
```

### 3. Dismantle UI Elements & Tokens
```bash
uiclone dismantle https://example.com
```
Reverse-engineers every button, form control, card, modal, typography rule, and color palette into `data_structure/`.

### 4. Crawl Site & Generate Comprehensive Sitemap
```bash
uiclone crawl https://example.com --max-pages 50 --depth 3
```

### 5. Interactive Terminal UI (TUI)
```bash
uiclone tui
```
Keyboard-driven dashboard built with Textual for live monitoring, setting configuration, and batch runs.

---

## ⚙️ Configuration

All settings can be configured via [`config.yaml`](./config.yaml) or CLI options:

```yaml
preflight:
  enabled: true                    # Run Layer -1 target profiler & ETA estimator
  probe_timeout_seconds: 6.0
  estimate_timeline: true
  save_preflight_report: true      # Saves data_structure/preflight.json

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
           ▼ OUTPUT
              ├── <site_name>/index.html (Single-file pixel-identical clone)
              └── data_structure/ (Preflight, SQLite index, JSONL datasets)
```

---

## 📄 License

This project is licensed under the **Apache License 2.0** — see the [LICENSE](LICENSE) file for details.
