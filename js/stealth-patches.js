/**
 * UI Cloner — Stealth Patches
 * Applied before ANY page script runs via CDP Page.addScriptToEvaluateOnNewDocument.
 * This is the baseline anti-detection layer.
 * 
 * WARNING: Do NOT modify the noise seed calculation — it must be
 * deterministic per session (seeded, not random per call).
 */
(function () {
    'use strict';

    // SESSION_NOISE_SEED is injected by Python at runtime
    const SESSION_NOISE_SEED = window.__uiclone_session_seed || 0x5A3F;
    const SESSION_NOISE_BYTE = SESSION_NOISE_SEED & 0xFF;

    // ── 1. Remove webdriver flag ─────────────────────────────────────────────
    try {
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
            configurable: true,
        });
    } catch (e) {}

    // ── 2. Chromium runtime mock ─────────────────────────────────────────────
    if (!window.chrome) {
        window.chrome = {};
    }
    if (!window.chrome.runtime) {
        window.chrome.runtime = {
            id: undefined,
            connect: () => {},
            sendMessage: () => {},
            onMessage: { addListener: () => {}, removeListener: () => {} },
        };
    }
    if (!window.chrome.app) {
        window.chrome.app = {
            isInstalled: false,
            InstallState: { DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed' },
            RunningState: { CANNOT_RUN: 'cannot_run', READY_TO_RUN: 'ready_to_run', RUNNING: 'running' },
            getDetails: () => null,
            getIsInstalled: () => false,
            runningState: () => 'cannot_run',
        };
    }

    // ── 3. Realistic plugin array ────────────────────────────────────────────
    try {
        const fakePlugins = [
            { name: 'Chrome PDF Plugin', description: 'Portable Document Format', filename: 'internal-pdf-viewer', length: 1 },
            { name: 'Chrome PDF Viewer', description: '', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', length: 1 },
            { name: 'Native Client', description: '', filename: 'internal-nacl-plugin', length: 2 },
        ];
        Object.defineProperty(navigator, 'plugins', {
            get: () => {
                const arr = Object.create(PluginArray.prototype);
                fakePlugins.forEach((p, i) => { arr[i] = p; });
                arr.length = fakePlugins.length;
                arr.item = i => fakePlugins[i];
                arr.namedItem = name => fakePlugins.find(p => p.name === name) || null;
                arr.refresh = () => {};
                return arr;
            },
        });
        Object.defineProperty(navigator, 'mimeTypes', {
            get: () => {
                const mt = Object.create(MimeTypeArray.prototype);
                mt.length = 2;
                return mt;
            },
        });
    } catch (e) {}

    // ── 4. Permissions API normalization ─────────────────────────────────────
    if (navigator.permissions && navigator.permissions.query) {
        const origQuery = navigator.permissions.query.bind(navigator.permissions);
        navigator.permissions.query = params => {
            if (['notifications', 'push', 'midi', 'camera', 'microphone'].includes(params.name)) {
                return Promise.resolve({ state: 'prompt', onchange: null });
            }
            return origQuery(params);
        };
    }

    // ── 5. WebRTC disable (prevent IP leak) ──────────────────────────────────
    try {
        const RTCPeerConnection = window.RTCPeerConnection || window.webkitRTCPeerConnection;
        if (RTCPeerConnection) {
            const OrigRTC = RTCPeerConnection;
            window.RTCPeerConnection = function (config) {
                if (config && config.iceServers) {
                    config = Object.assign({}, config, { iceServers: [] });
                }
                return new OrigRTC(config || {});
            };
            window.RTCPeerConnection.prototype = OrigRTC.prototype;
        }
    } catch (e) {}

    // ── 6. Screen / window dimension normalization ───────────────────────────
    try {
        // Ensure non-zero, realistic values
        if (screen.width === 0) {
            Object.defineProperty(screen, 'width', { get: () => 1920 });
            Object.defineProperty(screen, 'height', { get: () => 1080 });
            Object.defineProperty(screen, 'availWidth', { get: () => 1920 });
            Object.defineProperty(screen, 'availHeight', { get: () => 1040 });
        }
    } catch (e) {}

    // ── 7. Languages normalization ───────────────────────────────────────────
    try {
        if (!navigator.languages || navigator.languages.length === 0) {
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
        }
    } catch (e) {}

    // ── 8. Canvas fingerprint noise ──────────────────────────────────────────
    // Sub-perceptual, deterministic noise seeded by session ID
    (function patchCanvas() {
        const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
        const origToBlob = HTMLCanvasElement.prototype.toBlob;

        HTMLCanvasElement.prototype.toDataURL = function (type, quality) {
            _addNoise(this);
            return origToDataURL.apply(this, arguments);
        };

        HTMLCanvasElement.prototype.toBlob = function (callback, type, quality) {
            _addNoise(this);
            return origToBlob.apply(this, arguments);
        };

        function _addNoise(canvas) {
            const ctx = canvas.getContext('2d');
            if (!ctx || canvas.width === 0 || canvas.height === 0) return;
            try {
                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                const data = imageData.data;
                for (let i = 0; i < data.length; i += 4) {
                    // XOR with session-seeded pattern — sub-1-unit per channel
                    data[i]     ^= (SESSION_NOISE_SEED >> (i % 7)) & 0x01;
                    data[i + 1] ^= (SESSION_NOISE_SEED >> ((i + 1) % 7)) & 0x01;
                    // Leave alpha intact to avoid visual artifacts
                }
                ctx.putImageData(imageData, 0, 0);
            } catch (e) {
                // SecurityError if cross-origin canvas — expected, ignore
            }
        }
    })();

    // ── 9. WebGL GPU spoof ───────────────────────────────────────────────────
    (function patchWebGL() {
        const origGetContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function (type, attrs) {
            const ctx = origGetContext.apply(this, arguments);
            if (!ctx || (type !== 'webgl' && type !== 'webgl2') || ctx.__spoofed) return ctx;
            ctx.__spoofed = true;

            const origGetParam = ctx.getParameter.bind(ctx);
            ctx.getParameter = function (pname) {
                // RENDERER
                if (pname === ctx.RENDERER || pname === 37446) {
                    return 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0)';
                }
                // VENDOR
                if (pname === ctx.VENDOR || pname === 37445) {
                    return 'Google Inc. (NVIDIA)';
                }
                return origGetParam(pname);
            };

            const origReadPixels = ctx.readPixels.bind(ctx);
            ctx.readPixels = function (x, y, w, h, format, type, pixels) {
                origReadPixels(x, y, w, h, format, type, pixels);
                if (pixels && pixels.length > 0) {
                    for (let i = 0; i < Math.min(pixels.length, 256); i += 4) {
                        pixels[i]     ^= SESSION_NOISE_BYTE;
                        pixels[i + 1] ^= (SESSION_NOISE_BYTE >> 1) & 0xFF;
                    }
                }
            };

            return ctx;
        };
    })();

    // ── 10. Audio context fingerprint normalization ──────────────────────────
    (function patchAudio() {
        if (!window.AudioContext && !window.webkitAudioContext) return;
        const OrigAudio = (window.AudioContext || window.webkitAudioContext);
        const OrigAnalyser = OrigAudio.prototype.createAnalyser;
        OrigAudio.prototype.createAnalyser = function () {
            const analyser = OrigAnalyser.call(this);
            const origGetFloatFreq = analyser.getFloatFrequencyData.bind(analyser);
            analyser.getFloatFrequencyData = function (array) {
                origGetFloatFreq(array);
                // Add sub-perceptual noise to audio fingerprint
                for (let i = 0; i < array.length; i++) {
                    array[i] += (SESSION_NOISE_BYTE / 10000) * ((i % 3) - 1);
                }
            };
            return analyser;
        };
    })();

    console.debug('[UICloner] All stealth patches applied');
})();
