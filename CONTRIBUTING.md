# Contributing to Scrui v2.0

Thank you for your interest in contributing to **Scrui** — the production-grade, high-fidelity reverse engineering, DOM snapshotting, predictive telemetry, and stealth UI cloning engine.

This document provides complete guidelines for setting up your development environment, understanding the architecture, extending layers, writing tests, and submitting pull requests.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Architecture Overview](#architecture-overview)
3. [Development Environment Setup](#development-environment-setup)
4. [Project Structure](#project-structure)
5. [Core Design Principles](#core-design-principles)
6. [How to Extend Scrui](#how-to-extend-scrui)
   - [Adding Pre-Flight Probers (Layer -1)](#adding-pre-flight-probers-layer--1)
   - [Adding a New Browser Engine (Layer 1)](#adding-a-new-browser-engine-layer-1)
   - [Adding Evasion Patches (Layer 0)](#adding-evasion-patches-layer-0)
   - [Adding UI Analyzers & Classifiers (Layer 2)](#adding-ui-analyzers--classifiers-layer-2)
   - [Adding Animation & Motion Hooks](#adding-animation--motion-hooks)
   - [Adding CAPTCHA Solvers](#adding-captcha-solvers)
   - [Extending Storage & Serializers](#extending-storage--serializers)
7. [Coding Standards & Tooling](#coding-standards--tooling)
8. [Testing Guidelines](#testing-guidelines)
9. [Submitting a Pull Request](#submitting-a-pull-request)
10. [Security & Responsible Disclosure](#security--responsible-disclosure)

---

## Code of Conduct

We are committed to providing a welcoming, inclusive, and harassment-free experience for everyone. All contributors and maintainers are expected to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please report any violations to [security@scrui.dev](mailto:security@scrui.dev).

---

## Architecture Overview

Scrui is structured into 7 specialized pipeline layers:

```
┌────────────────────────────────────────────────────────┐
│  LAYER -1: Pre-Flight Profiler & Telemetry Oracle      │
│  Fast Edge Probe · WAF Detect · Dynamic ETA Countdown  │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│  LAYER 0: Anti-Detection & Network Evasion             │
│  TLS JA3/JA4 · HTTP/2/3 · WebGL · Canvas · CDP Cloak   │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│  LAYER 1: Stealth Browser Orchestration                │
│  nodriver · Patchright · Camoufox Fallback Chain       │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│  LAYER 2: Deep Extraction & Dismantling                │
│  DOM Snapshot · Shadow DOM · WAAPI/GSAP/Lottie         │
│  UI Element Analyzer · Component & Design Token Engine │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│  LAYER 3: Post-Processing & Code Recovery              │
│  JS Deobfuscation · WASM · Canvas 2D/WebGL Serializer  │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│  LAYER 4: Validation & Closed-Loop Auto-Correction     │
│  Pixel Diff · Closed-Loop Visual Optimizer · SQLite DB │
│  Dual Output: <site_name>/ & data_structure/           │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│  LAYER 5: UI-to-Prompt Synthesizer (Optional)          │
│  Design Tokens · Component AST · Copy Matrix · State   │
│  Outputs: PROMPT.md · SPEC.md · components_schema.json │
└────────────────────────────────────────────────────────┘
```

---

## Development Environment Setup

### Prerequisites

- **Python**: `>= 3.10` (tested on 3.10, 3.11, 3.12)
- **Node.js**: `>= 18.0.0` (optional, for Webpack/rrweb bundling)
- **Git**
- Google Chrome or Chromium installed locally

### Step-by-Step Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/ui-scrapper.git
   cd ui-scrapper
   ```

2. **Create a virtual environment:**
   ```bash
   # Using standard venv
   python -m venv .venv

   # Activate virtualenv
   # On Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   # On Linux/macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies in editable development mode:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install browser binaries (for Patchright / Playwright):**
   ```bash
   patchright install chromium
   ```

5. **Verify your installation:**
   ```bash
   uiclone --help
   uiclone config
   ```

---

## Project Structure

```
ui-scrapper/
├── config.yaml                    # Master runtime configuration
├── pyproject.toml                 # Build system & dependencies
├── README.md                      # Project documentation
├── CONTRIBUTING.md                # Contributor guide (this file)
├── js/                            # Injected browser scripts
│   ├── stealth-patches.js         # Runtime evasion monkey-patches
│   ├── webgl-hook.js              # Canvas/WebGL readback interrupter
│   ├── event-extractor.js         # Event listener discovery script
│   └── rrweb-injector.js          # DOM mutation recorder
└── uicloner/                      # Core Python package
    ├── config.py                  # Pydantic v2 master configuration models
    ├── orchestrator.py            # End-to-end pipeline coordinator
    ├── cli.py                     # Typer CLI application
    ├── analyzer/                  # Element dismantler & token extractor
    │   ├── dismantler.py          # Deep UI element & button classifier
    │   └── __init__.py
    ├── crawler/                   # Multi-page crawler & sitemap builder
    │   ├── site_crawler.py        # BFS crawler with robots.txt & XML sitemap
    │   └── __init__.py
    ├── layers/
    │   ├── layer0_evasion/        # TLS fingerprinting & evasion
    │   ├── layer1_browser/        # Multi-engine browser controllers
    │   ├── layer2_extract/        # DOM, Shadow DOM, Animations, Events
    │   ├── layer3_process/        # Canvas, WebGL, JS deobfuscation
    │   └── layer4_validate/       # Visual diff & VLM validation
    ├── output/                    # Serializer, packer, SQLite indexer
    │   ├── serializer.py          # Dual-folder output & dedupe engine
    │   └── packer.py              # Self-contained HTML assembler
    ├── captcha/                   # 2Captcha solver & detector
    └── tui/                       # Textual terminal user interface
```

---

## Core Design Principles

1. **Evasion First**: Never leak automation traces. All browser interactions, CDP commands, and script injections must remain undetectable by Cloudflare Turnstile, Datadome, Akamai, and Kasada.
2. **Deterministic Output**: Clones must be runnable offline and self-contained with no external CDN dependencies when requested.
3. **Structured Introspection**: Every element, button, color, and interaction must be queryable via JSON/JSONL and SQLite.
4. **Resilient Fallbacks**: If an extraction method fails (e.g. WAAPI empty), fail gracefully to CSS keyframes and computed style scrubbing without breaking the clone pipeline.

---

## How to Extend UI Cloner

### Adding a New Browser Engine (Layer 1)

All browser engines implement the `BrowserSession` protocol defined in [`uicloner/layers/layer1_browser/base.py`](uicloner/layers/layer1_browser/base.py):

```python
class CustomBrowserSession(BrowserSession):
    async def goto(self, url: str) -> None:
        ...

    async def evaluate(self, script: str) -> Any:
        ...

    async def screenshot(self) -> bytes:
        ...

    async def close(self) -> None:
        ...
```

Register your new engine in [`uicloner/layers/layer1_browser/engine_selector.py`](uicloner/layers/layer1_browser/engine_selector.py) and update the `BrowserEngine` enum in [`uicloner/config.py`](uicloner/config.py).

### Adding Evasion Patches (Layer 0)

To add new anti-fingerprint patches:
1. Edit [`js/stealth-patches.js`](js/stealth-patches.js) for client-side JavaScript overrides.
2. Ensure patches hide native function modification (`toString()` protection).
3. Add Python-side hooks to [`uicloner/layers/layer0_evasion/`](uicloner/layers/layer0_evasion/).

### Adding UI Analyzers & Classifiers (Layer 2)

Component classification logic lives in [`uicloner/analyzer/dismantler.py`](uicloner/analyzer/dismantler.py).
To add detection for a new component (e.g. `stepper` or `pricing_card`):
1. Add heuristics to `classifyComponent()` in `DISMANTLE_JS`.
2. Add dedicated attribute extractors if applicable.
3. Ensure the output maps cleanly into the `DismantledElement` dataclass.

### Adding Animation & Motion Hooks

Animation handling is in [`uicloner/layers/layer2_extract/animation_extractor.py`](uicloner/layers/layer2_extract/animation_extractor.py).
- For scroll animations, update `build_scroll_rebind_runtime_js()`.
- For vector/canvas animations, update `_extract_lottie_animations()` or add a new framework extractor (e.g. Rive runtime).

### Extending Storage & Serializers

Asset storage, content hashing, and SQLite schema live in [`uicloner/output/serializer.py`](uicloner/output/serializer.py):
- Keep the clean dual-folder output: `<site_name>/` and `data_structure/`.
- Ensure new data types update both the JSON/JSONL writer and SQLite tables.

---

## Coding Standards & Tooling

We adhere to modern Python standards:

- **Type Annotations**: All functions must have complete type signatures (`from __future__ import annotations`).
- **Pydantic v2**: All configuration and validation models use Pydantic v2.
- **Formatting**: Format code with **Black** (line length 100).
- **Linting**: Check code with **Ruff**:
  ```bash
  ruff check uicloner/
  black --check uicloner/
  ```

---

## Testing Guidelines

Run tests using `pytest`:

```bash
# Run all tests
pytest tests/ -v

# Run only unit tests
pytest tests/test_unit.py -v

# Test with headless browser
pytest tests/test_browser.py -k "nodriver"
```

When contributing new features:
1. Add corresponding test cases in `tests/`.
2. Verify that existing tests pass without regressions.
3. Verify that the CLI continues to execute cleanly: `uiclone --help`.

---

## Submitting a Pull Request

1. **Fork the repository** on GitHub.
2. **Create a topic branch**:
   ```bash
   git checkout -b feat/enhance-lottie-inlining
   ```
3. **Commit your changes** using conventional commit messages:
   - `feat: add Rive animation extraction support`
   - `fix: prevent layout shift on scroll-rebind`
   - `docs: improve contributing guidelines`
   - `perf: optimize SHA-256 asset deduplication`
4. **Push to your fork**:
   ```bash
   git push origin feat/enhance-lottie-inlining
   ```
5. **Open a Pull Request** against the `main` branch with a clear description of the problem solved, changes made, and test validation results.

---

## Security & Responsible Disclosure

If you discover a security vulnerability or sensitive evasion leak, please **do not open a public issue**. Follow our [Security Policy](SECURITY.md) to submit a confidential report or email [security@scrui.dev](mailto:security@scrui.dev).

---

## Community & Support

Have questions, ideas, or feedback? Check out our [Support Guide](SUPPORT.md) or start a conversation on [GitHub Discussions](https://github.com/brovk2008/Scrui/discussions).

---

Thank you for helping make Scrui the most capable, high-fidelity UI cloning platform!
