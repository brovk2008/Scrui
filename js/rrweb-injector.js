/**
 * UI Cloner — rrweb Injector
 * Initializes rrweb 2.x recorder for temporal DOM mutation capture.
 * Injected via CDP Page.addScriptToEvaluateOnNewDocument.
 * 
 * Note: rrweb itself must be loaded from CDN or bundled separately.
 * This script sets up the recording after rrweb is available.
 */
(function () {
    'use strict';

    window.__rrweb_events = [];
    window.__rrweb_recording = false;

    function startRecording() {
        if (window.__rrweb_recording || !window.rrweb) return;
        window.__rrweb_recording = true;

        try {
            const stopFn = window.rrweb.record({
                emit(event, isCheckout) {
                    window.__rrweb_events.push(event);
                    // Keep last 5000 events to avoid memory explosion
                    if (window.__rrweb_events.length > 5000) {
                        window.__rrweb_events.splice(0, 1000);
                    }
                },
                // rrweb 2.x: Shadow DOM support
                shadowDomRecording: true,
                // Canvas recording (expensive — enable per config)
                recordCanvas: false,
                // Collect fonts
                collectFonts: true,
                // Mask sensitive inputs
                maskInputOptions: {
                    password: true,
                    email: false,
                    tel: false,
                    credit_card: true,
                },
                // Block recording of certain elements
                blockClass: 'rr-block',
                ignoreClass: 'rr-ignore',
                // Sampling for high-frequency mutations
                sampling: {
                    mousemove: 50,    // one mousemove event per 50ms
                    scroll: 150,      // one scroll event per 150ms
                    mouseInteraction: true,
                    input: 'last',    // capture final value only
                },
            });

            window.__rrweb_stop = stopFn;
            console.debug('[UICloner] rrweb recording started');
        } catch (e) {
            console.warn('[UICloner] rrweb failed to start:', e);
            window.__rrweb_recording = false;
        }
    }

    // Wait for rrweb to be loaded (may be injected dynamically)
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(startRecording, 500);
        });
    } else {
        setTimeout(startRecording, 100);
    }

    // Expose control API
    window.__uiclone_rrweb = {
        start: startRecording,
        stop: () => { if (window.__rrweb_stop) window.__rrweb_stop(); },
        getEvents: () => window.__rrweb_events,
        clear: () => { window.__rrweb_events = []; },
        eventCount: () => window.__rrweb_events.length,
    };
})();
