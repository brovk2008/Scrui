# Changelog

All notable changes to **Scrui** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.5.0] - 2026-09-22

### Added
- **AI Code Scaffolder (`scrui generate`)**:
  - One-command autonomous code generation from any website into a complete, runnable Next.js 15 App Router codebase.
  - Multi-provider LLM support: OpenRouter (Claude 3.7 Sonnet), Groq (Llama-3.3-70b), Gemini, and local Ollama.
  - Generates `package.json`, `tsconfig.json`, `tailwind.config.ts`, `app/layout.tsx`, `app/page.tsx`, and modular components (`Navbar.tsx`, `Hero.tsx`, `Features.tsx`, `Footer.tsx`).
- **Visual Diff & Telemetry Inspector Web UI (`scrui inspect`)**:
  - Built-in local HTTP dashboard on `localhost:3888` featuring Cyberpunk aesthetics.
  - Responsive viewport switcher (Desktop FHD, Tablet 820px, Mobile 390px).
  - Visual comparison slider, interactive token palette swatches, and DTCG schema viewer.
  - Section-by-section prompt copy button for instant AI workflow.
- **Chrome Extension & Local Relay Server (`scrui listen`)**:
  - Manifest V3 Chrome/Brave extension (`extension/`) for 1-click captures of authenticated dashboards (Stripe, Notion, Jira).
  - Local HTTP daemon on port 9222 accepting DOM/CSS dumps and executing Scrui extraction instantly.
- **Semantic Lucide React & Vector Icon Classifier**:
  - Vector signature and attribute classifier matching raw SVG paths to clean Lucide React component imports (`Search`, `Menu`, `ChevronRight`, `Github`, etc.).
  - Reduces prompt token consumption by 35-45% and eliminates 500-line SVG path blobs.
- **W3C DTCG & Figma Tokens Studio Exporter**:
  - Formats extracted tokens into official W3C Design Tokens Community Group specification (`tokens.json`).
  - Exports `figma_tokens.json` for 1-click import into Figma via Tokens Studio plugin.
- **Multi-Device Responsive Viewport Matrix**:
  - Dynamic breakpoint analysis (Mobile 390px, Tablet 820px, Desktop 1920px).
  - Detects mobile hamburger triggers, collapsible drawers, and responsive CSS grid shifts.
- **Universal AI Agent Skill (`skills/scrui/SKILL.md`)**:
  - Pre-built autonomous agent skill installed globally and locally for Claude Code, Cursor, Antigravity, and OpenAI agents.

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
- **Layer 5: UI-to-Prompt Synthesizer (The Ultimate Feature)**:
  - Compiles the entire reverse-engineered UI into an exact Master LLM Prompt (`PROMPT.md`), Technical Specification (`SPEC.md`), and typed component JSON schema (`components_schema.json`).
  - AST reducer prunes DOM boilerplate into clean semantic sections (`Navbar`, `Hero`, `Features`, `Pricing`, `Testimonials`, `Footer`) and typed TypeScript interfaces (`interface FeatureCardProps`).
  - Design token compiler normalizes raw colors and styles into production-ready Tailwind CSS configurations and CSS variable themes.
  - Interactive state compiler synthesizes mined behaviors into type-safe React state hooks (`useState`, `useEffect`) and accessibility contracts.
  - Motion compiler translates CSS keyframes and WAAPI animations into declarative Framer Motion variants and scroll reveals.
  - Supports multiple target prompt profiles: Next.js 15 App Router (`nextjs`), v0.dev / Lovable (`v0`), Cursor / Windsurf (`cursor`), React 19 (`react`), Vue 3 (`vue`), SvelteKit (`svelte`).
  - Dedicated CLI command `scrui prompt <url> --target <target>` and `--prompt` flag for `scrui clone`.
- **Community Standards**:
  - Contributor Covenant v2.1 `CODE_OF_CONDUCT.md`.
  - Responsible disclosure `SECURITY.md`.
  - Community `SUPPORT.md`.
  - GitHub Issue Forms for bugs and feature requests.
  - Pull Request template with engineering checklist.
  - GitHub Actions CI workflow for test and linting.
- **License**: Apache License 2.0.
