# UI Cloner v2.0

> **High-Fidelity UI Extraction & Cloning Engine** — Production-grade system for pixel-identical, interactively-equivalent web UI cloning.

---

## Features

| Module | Capability |
|--------|-----------|
| **Stealth Browser** | nodriver → Patchright → Camoufox fallback chain |
| **TLS Impersonation** | JA3/JA4/HTTP2/HTTP3 via curl_cffi (Chrome131 profile) |
| **Fingerprinting** | BrowserForge statistically-realistic profiles per session |
| **DOM Capture** | Full DOM tree with CSS, scripts, meta — all via CDP |
| **UI Dismantler** | Reverse-engineers all elements, buttons, forms, a11y & design tokens |
| **Site Crawler** | Async BFS crawler with robots.txt, sitemap.xml & full link graph |
| **Animation Fidelity** | CSS keyframes, WAAPI, GSAP, Lottie inlining & scroll-rebind runtime |
| **Shadow DOM** | DSD `getHTML()` primary + CDP `pierce:true` recursive fallback |
| **Event Listeners** | 3-step BackendNodeId → RemoteObject → DOMDebugger resolution |
| **Framework Events** | React fiber, Vue `__vue_app__`, Angular `getAllAngularRootElements` |
| **Storage & Dedupe** | SHA-256 asset deduplication + searchable SQLite index (`assets.db`) |
| **Canvas/WebGL** | Screenshot capture + API hook capture + draw call recording |
| **WASM** | wasm2wat decompilation + HuggingFace LLM JS shim generation |
| **JS Deobfuscation** | webcrack debundling + Qwen2.5-Coder identifier renaming |
| **Anti-Bot** | Canvas noise, WebGL spoof, WebRTC disable, Bézier mouse, audio FP |
| **CAPTCHA** | 2captcha v2 API — reCAPTCHA v2/v3, hCaptcha, Turnstile, DataDome |
| **VLM Validation** | Qwen2.5-VL screenshot comparison + Pillow pixel diff |
| **Session** | Full cookie + localStorage + sessionStorage persistence |
| **TUI** | Textual interactive terminal with keyboard navigation |
| **CLI** | Typer CLI with `clone`, `dismantle`, `crawl`, `sitemap`, `batch` |

---

## Output Structure

Every clone produces a clean dual-folder layout:

```
clones/
└── site_cloned_example-com_20260922_183045/
    ├── example-com/               ← The cloned website (named after the site)
    │   ├── index.html             ← Self-contained, interactive single-file HTML
    │   └── assets/                ← Extracted and deduplicated assets
    │       ├── images/            ← Images (deduplicated by SHA-256)
    │       ├── fonts/             ← Web fonts (WOFF2/TTF)
    │       ├── videos/            ← Video media
    │       ├── css/               ← Stylesheets
    │       └── js/                ← Scripts
    └── data_structure/            ← Comprehensive reverse-engineered data
        ├── manifest.json          ← Metadata, timing, engine & analysis summary
        ├── elements.jsonl         ← Every dismantled element (box, styles, a11y, role)
        ├── components.json        ← Categorized components (buttons, forms, modals)
        ├── design_system.json     ← Color palette, typography scale & design tokens
        ├── sitemap.json           ← Complete page hierarchy & link graph
        ├── dom_tree.json          ← Full CDP DOM tree
        ├── styles.json            ← All extracted stylesheets & rules
        ├── scripts.json           ← Scripts (deobfuscated if enabled)
        ├── assets.jsonl           ← Asset catalog with MIME, sizes & SHA-256 hashes
        ├── assets.db              ← Searchable SQLite database (query elements & assets via SQL!)
        ├── events.json            ← Event listeners & framework triggers map
        ├── animations.json        ← WAAPI, GSAP, CSS keyframes, Lottie data
        ├── shadow_dom.json        ← Pierced Shadow DOM tree & DSD HTML
        ├── canvas.json            ← Canvas screenshots & WebGL draw calls
        └── validation.json        ← Pixel diff & VLM fidelity report
```

---

## Quick Start

### Installation

```bash
# Install Python package
pip install -e .

# Install Node.js tools (for JS deobfuscation)
npm install -g webcrack

# Install browsers
python -m playwright install chromium
python -m camoufox fetch  # Downloads patched Firefox

# Install WABT (for WASM decompilation)
# Windows: https://github.com/WebAssembly/wabt/releases
# Linux: apt-get install wabt
```

### Usage

#### Interactive TUI (recommended)
```bash
uiclone tui
```
Keyboard shortcuts:
- `Tab` / `Arrow keys` — navigate between elements
- `Enter` — select / confirm  
- `Ctrl+S` — save settings
- `Ctrl+Q` — quit

#### Clone a single URL
```bash
uiclone clone https://example.com

# With options
uiclone clone https://example.com \
  --engine nodriver \
  --images both \
  --fonts base64 \
  --data-format jsonl \
  --output ./my-clones

# With CAPTCHA solving
uiclone clone https://example.com --captcha-key YOUR_2CAPTCHA_KEY

# With proxy
uiclone clone https://example.com --proxy proxy.host:8080:user:pass
```

#### Batch clone from file
```bash
# urls.txt — one URL per line, # for comments
uiclone batch urls.txt --output ./clones --concurrent 2
```

#### View/export configuration
```bash
uiclone config                          # Show current settings
uiclone config --export my-config.yaml  # Export defaults to file
```

---

## Configuration

All settings are in [`config.yaml`](./config.yaml). Key options:

| Setting | Values | Default | Description |
|---------|--------|---------|-------------|
| `browser.primary_engine` | `nodriver` / `patchright` / `camoufox` | `nodriver` | Browser engine |
| `storage.images` | `base64` / `raw` / `both` / `url` | `base64` | Image storage format |
| `storage.fonts` | `base64` / `raw` / `url` | `base64` | Font storage format |
| `storage.videos` | `raw` / `url` | `raw` | Video storage format |
| `storage.data_format` | `jsonl` / `json` / `both` | `jsonl` | Data output format |
| `network.proxy_tier` | `none` / `residential` / `isp` / `datacenter` | `none` | Proxy tier |
| `extraction.js_deobfuscate` | `true` / `false` | `true` | JS deobfuscation |
| `captcha.enabled` | `true` / `false` | `false` | 2captcha solving |
| `validation.run_vlm_check` | `true` / `false` | `false` | VLM screenshot compare |

### Environment Variables

```bash
HF_API_KEY=hf_...              # HuggingFace API key (for VLM + code models)
TWO_CAPTCHA_KEY=...            # 2captcha API key
```

---

## Models Used

| Task | Model | Mode |
|------|-------|------|
| VLM Validation | `Qwen/Qwen2.5-VL-7B-Instruct` | HF Inference API |
| JS Deobfuscation | `Qwen/Qwen2.5-Coder-7B-Instruct` | HF Inference API |
| WASM Decompilation | `Qwen/Qwen2.5-Coder-7B-Instruct` | HF Inference API |

No local GPU required — all inference runs via the free HuggingFace Inference API.  
For local inference, install `pip install transformers torch accelerate` and set `huggingface.use_local: true`.

---

## CAPTCHA Support (2captcha)

Supported CAPTCHA types via [2captcha API v2](https://2captcha.com/api-docs):

| Type | Task Type |
|------|-----------|
| reCAPTCHA v2 | `RecaptchaV2TaskProxyless` |
| reCAPTCHA v3 | `RecaptchaV3TaskProxyless` |
| hCaptcha | `HCaptchaTaskProxyless` |
| Cloudflare Turnstile | `TurnstileTaskProxyless` |
| Image CAPTCHA | `ImageToTextTask` |
| DataDome | `DataDomeSliderTask` |

Auto-detection is on by default — the engine detects CAPTCHA type and solves it automatically.

---

## Anti-Detection Hardening Checklist

Before every session, the engine verifies:

- ✅ `navigator.webdriver` → `undefined`
- ✅ `chrome.runtime` → mock object present  
- ✅ `navigator.plugins` → min 3 entries
- ✅ `screen.width/height` → realistic non-zero values
- ✅ Canvas `toDataURL()` → session-seeded noise
- ✅ WebGL `RENDERER`/`VENDOR` → real GPU profile
- ✅ TLS JA3 → Chrome131 profile (curl_cffi)
- ✅ HTTP/3 ALPN → correct cipher suite ordering with GREASE
- ✅ WebRTC → disabled (no local IP leak)
- ✅ Mouse movements → Bézier curves, not straight lines
- ✅ Audio context → sub-perceptual noise normalization

---

## Architecture

```
TARGET URL
    │
    ▼ Layer 0 — Evasion & Ingress
    │  TLS impersonation · Proxy rotation · Honeypot detection
    │
    ▼ Layer 1 — Stealth Browser Pool
    │  nodriver/Patchright/Camoufox · BrowserForge fingerprints
    │  CDP WebSocket · Pre-load stealth scripts
    │
    ▼ Layer 2 — Extraction Orchestrator
    │  DOM snapshot · Shadow DOM · Event listeners
    │  Animations · Canvas/WebGL · Network interception
    │
    ▼ Layer 3 — Post-Processing
    │  JS deobfuscation · Asset processing · WASM decompilation
    │
    ▼ Layer 4 — VLM Validation
    │  Pixel diff · Qwen2.5-VL screenshot comparison
    │
    ▼ OUTPUT
       site/index.html (self-contained)
       data/*.jsonl (structured extraction data)
```

---

## Legal Notice

This tool must only be used on:
- Websites you own
- Websites you have explicit authorization to scrape
- Websites where scraping is permitted by their Terms of Service

Misuse for unauthorized access is strictly prohibited.
