/**
 * UI Cloner — Event Extractor (Client-side helper)
 * Extracts React fiber, Vue, and Angular event maps from the page context.
 * Called via CDP Runtime.evaluate after page load.
 */
(function () {
    'use strict';

    window.__uiclone_events = {};

    // ── React Fiber Event Walker ─────────────────────────────────────────────
    function extractReactEvents() {
        const events = [];

        function walkFiber(fiber, depth) {
            if (!fiber || depth > 50) return;
            const props = fiber.memoizedProps || {};
            const handlers = Object.keys(props).filter(k =>
                k.startsWith('on') &&
                k.length > 2 &&
                typeof props[k] === 'function'
            );

            if (handlers.length > 0) {
                const node = fiber.stateNode;
                const isDOM = node && node.nodeType === 1;
                events.push({
                    component: fiber.type?.displayName || fiber.type?.name || (typeof fiber.type === 'string' ? fiber.type : 'Unknown'),
                    handlers,
                    isDOM,
                    tagName: isDOM ? node.tagName?.toLowerCase() : null,
                    id: isDOM ? node.id : null,
                    className: isDOM ? (typeof node.className === 'string' ? node.className.split(' ')[0] : null) : null,
                    text: isDOM && node.textContent ? node.textContent.slice(0, 50) : null,
                });
            }

            // Walk children and siblings
            walkFiber(fiber.child, depth + 1);
            walkFiber(fiber.sibling, depth + 1);
        }

        // Find React fiber root
        const candidates = [
            document.getElementById('root'),
            document.getElementById('app'),
            document.getElementById('__next'),
            document.querySelector('[data-reactroot]'),
            document.body,
        ].filter(Boolean);

        for (const el of candidates) {
            const key = Object.keys(el).find(k =>
                k.startsWith('__reactFiber') ||
                k.startsWith('__reactInternalInstance')
            );
            if (key) {
                walkFiber(el[key], 0);
                break;
            }
        }

        return events.slice(0, 1000);
    }

    // ── Vue 3 Component Tree ─────────────────────────────────────────────────
    function extractVueEvents() {
        const result = { version: null, components: [], emits: [] };

        if (window.__vue_app__) {
            result.version = 3;
            const ctx = window.__vue_app__._context;
            result.components = Object.keys(ctx?.components || {});
            result.directives = Object.keys(ctx?.directives || {});
        } else if (window.Vue) {
            result.version = 2;
        }
        return result;
    }

    // ── Angular Component Info ───────────────────────────────────────────────
    function extractAngularInfo() {
        const result = { detected: false };
        if (window.getAllAngularRootElements) {
            result.detected = true;
            result.roots = window.getAllAngularRootElements().length;
        }
        const ngVersion = document.querySelector('[ng-version]');
        if (ngVersion) {
            result.version = ngVersion.getAttribute('ng-version');
        }
        return result;
    }

    // ── Run detection ────────────────────────────────────────────────────────
    try {
        window.__uiclone_events.react = extractReactEvents();
    } catch (e) {
        window.__uiclone_events.react_error = e.message;
    }

    try {
        window.__uiclone_events.vue = extractVueEvents();
    } catch (e) {
        window.__uiclone_events.vue_error = e.message;
    }

    try {
        window.__uiclone_events.angular = extractAngularInfo();
    } catch (e) {
        window.__uiclone_events.angular_error = e.message;
    }

    // ── DOM attribute event detection ────────────────────────────────────────
    (function detectInlineEvents() {
        const inlineEvents = [];
        const all = document.querySelectorAll('[onclick],[onmouseover],[onmouseenter],[onkeydown],[onsubmit],[oninput],[onchange]');
        all.forEach(el => {
            const attrs = Array.from(el.attributes)
                .filter(a => a.name.startsWith('on'))
                .map(a => ({ attr: a.name, value: a.value.slice(0, 100) }));
            if (attrs.length > 0) {
                inlineEvents.push({
                    tag: el.tagName.toLowerCase(),
                    id: el.id,
                    class: el.className?.split?.(' ')?.[0],
                    events: attrs,
                });
            }
        });
        window.__uiclone_events.inline_dom = inlineEvents;
    })();

    console.debug('[UICloner] Event extraction complete:', {
        react: (window.__uiclone_events.react || []).length,
        vue: window.__uiclone_events.vue?.version,
        angular: window.__uiclone_events.angular?.detected,
    });
})();
