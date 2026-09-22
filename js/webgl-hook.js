/**
 * UI Cloner — WebGL Hook
 * Injected before page load via CDP Page.addScriptToEvaluateOnNewDocument
 * Captures all WebGL draw calls, buffer uploads, and uniform state.
 */
(function () {
    'use strict';

    if (window.__uiclone_webgl_hooked) return;
    window.__uiclone_webgl_hooked = true;

    const capturedCalls = [];
    const MAX_CALLS = 5000;

    function captureWebGLState(ctx) {
        try {
            return {
                viewport: ctx.getParameter(ctx.VIEWPORT),
                activeTexture: ctx.getParameter(ctx.ACTIVE_TEXTURE),
                blendEnabled: ctx.isEnabled(ctx.BLEND),
                depthEnabled: ctx.isEnabled(ctx.DEPTH_TEST),
                cullEnabled: ctx.isEnabled(ctx.CULL_FACE),
            };
        } catch (e) {
            return {};
        }
    }

    const origGetContext = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function (type, attrs) {
        const ctx = origGetContext.apply(this, arguments);
        if ((type !== 'webgl' && type !== 'webgl2') || !ctx || ctx.__uiclone_hooked) {
            return ctx;
        }
        ctx.__uiclone_hooked = true;

        // Hook draw calls
        ['drawArrays', 'drawElements', 'drawArraysInstanced', 'drawElementsInstanced'].forEach(method => {
            if (!ctx[method]) return;
            const orig = ctx[method].bind(ctx);
            ctx[method] = function (...args) {
                if (capturedCalls.length < MAX_CALLS) {
                    capturedCalls.push({
                        method,
                        args: Array.from(args),
                        timestamp: performance.now(),
                        state: captureWebGLState(ctx),
                    });
                }
                return orig(...args);
            };
        });

        // Hook buffer uploads (geometry data)
        const origBufferData = ctx.bufferData.bind(ctx);
        ctx.bufferData = function (target, data, usage) {
            if (capturedCalls.length < MAX_CALLS && data) {
                capturedCalls.push({
                    method: 'bufferData',
                    target,
                    usage,
                    size: data.byteLength || data.length || 0,
                    // Store first 64 floats as geometry sample
                    sample: data instanceof Float32Array ? Array.from(data.slice(0, 64)) : null,
                });
            }
            return origBufferData(target, data, usage);
        };

        // Hook texture uploads
        const origTexImage2D = ctx.texImage2D.bind(ctx);
        ctx.texImage2D = function () {
            capturedCalls.push({
                method: 'texImage2D',
                timestamp: performance.now(),
            });
            return origTexImage2D.apply(ctx, arguments);
        };

        // Hook shader compilation (to capture GLSL source)
        const origShaderSource = ctx.shaderSource.bind(ctx);
        const shaders = {};
        ctx.shaderSource = function (shader, source) {
            shaders[performance.now()] = source;
            return origShaderSource.apply(ctx, arguments);
        };

        console.debug('[UICloner] WebGL hooks installed');
        return ctx;
    };

    window.__webgl_capture = capturedCalls;
    window.__webgl_shaders = {};
})();
