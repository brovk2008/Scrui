# Support & Community Resources

Thank you for using **Scrui**! Here is how to find help, report issues, and connect with the community.

---

## 🧭 Where to Go for Help

| Resource | Best For | Link |
| -------- | -------- | ---- |
| **Documentation** | Getting started, architecture, layer guides, CLI options | [README.md](README.md) & [CONTRIBUTING.md](CONTRIBUTING.md) |
| **GitHub Discussions** | Questions, ideas, showcase, and general chatter | [GitHub Discussions](https://github.com/brovk2008/Scrui/discussions) |
| **GitHub Issues** | Verified bugs, reproducible errors, and approved feature requests | [GitHub Issues](https://github.com/brovk2008/Scrui/issues) |
| **Security Advisories** | Private vulnerability reporting | [Security Policy](SECURITY.md) |

---

## ❓ Frequently Asked Questions

### 1. Which browser engine should I use?
- `nodriver`: Best default for stealth anti-bot evasion. Uses direct Chrome DevTools Protocol (CDP) WebSocket without standard webdriver flags.
- `patchright`: Excellent for complex multi-tab orchestration and network request rewriting.
- `camoufox`: Built on patched C++ Firefox binaries. Ideal for sites that aggressively fingerprint Chromium.

### 2. Can Scrui clone dynamic SPAs (React, Next.js, Vue)?
Yes. Scrui uses a live browser session with DOM snapshotting, event listener extraction, and animation runtime rebinding. Layer -1 dynamically detects SPA frameworks and adjusts hydration wait times accordingly.

### 3. How does Layer -1 Pre-Flight work?
Layer -1 probes the target before launching browser processes. It inspects edge CDN headers (Cloudflare, Akamai), detects WAF challenges, scans HTML for tech stacks, and calculates an execution timeline with real-time countdown ETA and % completion.

### 4. How can I contribute?
Check out our [Contributing Guide](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md).
