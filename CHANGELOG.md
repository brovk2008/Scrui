# Changelog

All notable changes to **Scrui** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-09-22

### Added
- **Layer -1: Pre-Flight Profiler & Predictive Telemetry Oracle**:
  - Fast zero-browser async edge network probe measuring round-trip latency (RTT ms) and host resolution.
  - Edge CDN & WAF fingerprinting (Cloudflare cf-ray, Akamai, CloudFront, Fastly, Imperva, DataDome).
  - Rapid HTML structural parsing for resource volumes (scripts, styles, media, forms, buttons).
  - Frontend technology stack detection (Next.js, React, Vue, Nuxt, Angular, Svelte, Tailwind CSS, GSAP, Lottie, Webflow, Shopify, WordPress).
  - Dynamic SPA index and 1-10 DOM complexity scoring.
  - Multi-phase execution timeline estimator allocating dynamic durations and progress weights.
  - Real-time `TelemetryOracle` tracking dynamic ETA countdown (`~00:18 left`), % completed, active layer, and granular human-readable operational status.
  - Export of `preflight.json` into `data_structure/`.
- **Cyberpunk Branding & UI Theme**:
  - Official brand asset `image.png` embedded in `README.md`.
  - 8-bit retro block pixel logo in bold electric blue (`#00a2ff`) for CMD/PowerShell.
  - Cyberpunk pink UI theme (`#ff2a85`) across all panels, progress bars, tables, borders, and spinners.
  - Windows UTF-8 console stream reconfiguring.
- **Layer 0: Anti-Bot Evasion & Fingerprinting**:
  - TLS JA3/JA4/HTTP2/HTTP3 fingerprint impersonation (Chrome 131 profile via `curl_cffi`).
  - BrowserForge statistically realistic browser fingerprints.
  - Canvas 2D per-session noise injection and WebGL GPU vendor/renderer spoofing.
  - WebRTC local IP leak prevention and Bézier mouse trajectory generation.
- **Layer 1: Stealth Browser Orchestration**:
  - Autonomous fallback chain: `nodriver` (CDP direct) → `Patchright` → `Camoufox`.
  - CDP WebSocket session lifecycle management.
- **Layer 2: Extraction & Reverse-Engineering**:
  - DOM tree snapshotting with CSS and scripts extraction.
  - Declarative Shadow DOM (DSD) `getHTML()` extraction with CDP recursive piercing fallback.
  - 3-step `BackendNodeId` → `RemoteObject` → `DOMDebugger` event listener resolution.
  - Framework event recovery for React (`__reactFiber$`), Vue (`__vue_app__`), and Angular.
  - Animation extraction: CSS keyframes, WAAPI, GSAP, Lottie inlining with automated scroll-rebind runtime generation.
- **Layer 2.5: UI Element Dismantler**:
  - Full element cataloging, button visual states, form control analysis, accessibility contrast audit, and design token extraction.
- **Layer 2.6: Behavioral State Explorer**:
  - Interactive state exploration mining hover transitions, focus rings, and accordion disclosures.
- **Layer 3: Asset Deduplication & SQLite Indexing**:
  - SHA-256 asset content-hash deduplication.
  - Searchable SQLite index (`assets.db`) and streaming JSONL metadata.
  - JavaScript debundling (`webcrack`) and Qwen2.5-Coder identifier renaming.
- **Layer 4: Assembly & Visual Auto-Correction**:
  - Standalone single-file HTML packing with inlined runtimes.
  - Closed-loop visual auto-correction optimizer using pixel diff and VLM guidance.
- **Community Standards**:
  - Contributor Covenant v2.1 `CODE_OF_CONDUCT.md`.
  - Responsible disclosure `SECURITY.md`.
  - Community `SUPPORT.md`.
  - GitHub Issue Forms for bugs and feature requests.
  - Pull Request template with engineering checklist.
  - GitHub Actions CI workflow for test and linting.
- **License**: Apache License 2.0.
