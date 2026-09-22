"""
Animation Extraction Pipeline
Captures CSS animations, WAAPI, GSAP timelines, Framer Motion, and bakes them
into static CSS @keyframes for self-contained replay.
"""
from __future__ import annotations

import asyncio
import logging
import math
from typing import Optional

logger = logging.getLogger(__name__)


async def extract_all_animations(cdp, page) -> dict:
    """
    Master animation extractor — captures all sources:
    1. WAAPI (document.getAnimations)
    2. GSAP globalTimeline & ScrollTrigger
    3. CSS via computed style scrubbing & @keyframes
    4. CSS transitions
    5. Lottie animations (bodymovin, lottie-player, dotlottie)
    6. Scroll-triggered animations (AOS, wow, in-view, intersection observers)
    """
    waapi = await _extract_waapi_animations(cdp)
    gsap = await _extract_gsap_timelines(cdp)
    css_keyframes = await _extract_css_keyframes(cdp)
    transitions = await _extract_css_transitions(cdp)
    lottie_anims = await _extract_lottie_animations(cdp)
    scroll_triggers = await _extract_scroll_triggers(cdp)

    # Try CDP Animation domain (timeline scrubbing)
    scrubbed = await _scrub_animation_timeline(cdp)

    scroll_rebind_js = build_scroll_rebind_runtime_js(scroll_triggers)
    lottie_runtime_js = build_lottie_runtime_js(lottie_anims)

    return {
        "waapi_animations": waapi,
        "gsap_timelines": gsap,
        "css_keyframes": css_keyframes,
        "css_transitions": transitions,
        "lottie_animations": lottie_anims,
        "scroll_triggers": scroll_triggers,
        "scrubbed_frames": scrubbed,
        "baked_css": _bake_all_to_css(waapi, gsap, css_keyframes),
        "scroll_rebind_js": scroll_rebind_js,
        "lottie_runtime_js": lottie_runtime_js,
    }


async def _extract_waapi_animations(cdp) -> list[dict]:
    """Extract via Web Animations API (document.getAnimations)."""
    try:
        result = await cdp.send("Runtime.evaluate", {
            "expression": """
                (() => {
                    const anims = document.getAnimations();
                    return anims.map(a => {
                        const effect = a.effect;
                        const timing = effect ? effect.getTiming() : {};
                        const keyframes = effect ? (effect.getKeyframes ? effect.getKeyframes() : []) : [];
                        const target = effect?.target;
                        return {
                            id: a.id,
                            playState: a.playState,
                            currentTime: a.currentTime,
                            startTime: a.startTime,
                            playbackRate: a.playbackRate,
                            type: a instanceof CSSAnimation ? 'css' :
                                  a instanceof CSSTransition ? 'transition' : 'waapi',
                            animationName: a instanceof CSSAnimation ? a.animationName : null,
                            propertyName: a instanceof CSSTransition ? a.transitionProperty : null,
                            timing: {
                                duration: timing.duration,
                                delay: timing.delay,
                                easing: timing.easing,
                                fill: timing.fill,
                                iterations: timing.iterations,
                                direction: timing.direction,
                            },
                            keyframes: keyframes,
                            targetSelector: target ?
                                (target.id ? '#' + target.id :
                                 target.className ? '.' + target.className.split(' ')[0] :
                                 target.tagName?.toLowerCase()) : null,
                        };
                    });
                })()
            """,
            "returnByValue": True,
            "timeout": 10000,
        })
        return result.get("result", {}).get("value", []) or []
    except Exception as e:
        logger.debug(f"WAAPI extraction failed: {e}")
        return []


async def _extract_gsap_timelines(cdp) -> dict:
    """Extract GSAP timeline data when gsap is exposed on window."""
    try:
        result = await cdp.send("Runtime.evaluate", {
            "expression": """
                (() => {
                    if (!window.gsap) return null;
                    const timeline = gsap.globalTimeline;
                    if (!timeline) return null;
                    const children = timeline.getChildren(true, true, true, 0);
                    return children.slice(0, 200).map(tween => ({
                        targets: (tween.targets?.() || []).slice(0, 5).map(t => ({
                            tagName: t.tagName,
                            id: t.id,
                            className: typeof t.className === 'string' ? t.className.split(' ')[0] : '',
                        })),
                        duration: tween.duration?.(),
                        delay: tween.delay?.(),
                        ease: tween.vars?.ease?.toString?.() || 'none',
                        stagger: tween.vars?.stagger,
                        repeat: tween.vars?.repeat || 0,
                        yoyo: tween.vars?.yoyo || false,
                        vars: (() => {
                            const v = {};
                            const skip = ['ease','stagger','repeat','onComplete','onUpdate','onStart'];
                            Object.keys(tween.vars || {}).forEach(k => {
                                if (!skip.includes(k) && typeof tween.vars[k] !== 'function') {
                                    v[k] = tween.vars[k];
                                }
                            });
                            return v;
                        })(),
                    }));
                })()
            """,
            "returnByValue": True,
            "timeout": 5000,
        })
        return result.get("result", {}).get("value") or {}
    except Exception as e:
        logger.debug(f"GSAP extraction failed: {e}")
        return {}


async def _extract_css_keyframes(cdp) -> list[dict]:
    """Extract all @keyframes rules from stylesheets."""
    try:
        result = await cdp.send("Runtime.evaluate", {
            "expression": """
                (() => {
                    const keyframes = [];
                    for (const sheet of document.styleSheets) {
                        try {
                            for (const rule of sheet.cssRules || []) {
                                if (rule.type === CSSRule.KEYFRAMES_RULE) {
                                    const kfs = [];
                                    for (const kf of rule.cssRules) {
                                        kfs.push({ offset: kf.keyText, style: kf.style.cssText });
                                    }
                                    keyframes.push({ name: rule.name, keyframes: kfs });
                                }
                            }
                        } catch(e) {}
                    }
                    return keyframes;
                })()
            """,
            "returnByValue": True,
        })
        return result.get("result", {}).get("value", []) or []
    except Exception as e:
        logger.debug(f"CSS keyframe extraction failed: {e}")
        return []


async def _extract_css_transitions(cdp) -> list[dict]:
    """Extract elements with CSS transitions defined."""
    try:
        result = await cdp.send("Runtime.evaluate", {
            "expression": """
                (() => {
                    const transitions = [];
                    const all = document.querySelectorAll('*');
                    for (const el of all) {
                        const style = window.getComputedStyle(el);
                        const prop = style.transitionProperty;
                        if (prop && prop !== 'none' && prop !== 'all') {
                            const sel = el.id ? '#' + el.id :
                                        el.className ? '.' + el.className.split(' ')[0] :
                                        el.tagName.toLowerCase();
                            transitions.push({
                                selector: sel,
                                property: prop,
                                duration: style.transitionDuration,
                                timing: style.transitionTimingFunction,
                                delay: style.transitionDelay,
                            });
                        }
                    }
                    return transitions.slice(0, 300);
                })()
            """,
            "returnByValue": True,
            "timeout": 15000,
        })
        return result.get("result", {}).get("value", []) or []
    except Exception as e:
        logger.debug(f"CSS transition extraction failed: {e}")
        return []


async def _scrub_animation_timeline(cdp) -> list[dict]:
    """
    Enable CDP Animation domain and scrub through timeline to capture states.
    """
    scrubbed_states = []
    try:
        await cdp.send("Animation.enable")
        # Get all animations
        result = await cdp.send("Runtime.evaluate", {
            "expression": "document.getAnimations().map(a => a.id)",
            "returnByValue": True,
        })
        anim_ids = result.get("result", {}).get("value", []) or []

        if not anim_ids:
            return []

        # Pause all animations
        await cdp.send("Animation.setPaused", {
            "animations": [str(i) for i in anim_ids],
            "paused": True,
        })

        # Scrub 60 frames over 3 seconds
        for step in range(60):
            t = (step / 60) * 3000
            try:
                await cdp.send("Animation.seekAnimations", {
                    "animations": [str(i) for i in anim_ids],
                    "currentTime": t,
                })
                scrubbed_states.append({"step": step, "time_ms": t})
            except Exception:
                pass

    except Exception as e:
        logger.debug(f"CDP animation scrubbing failed: {e}")
    finally:
        try:
            await cdp.send("Animation.disable")
        except Exception:
            pass

    return scrubbed_states


def _bake_all_to_css(waapi: list, gsap: dict, keyframes: list) -> str:
    """
    Bake extracted animation data into static CSS @keyframes strings.
    """
    css_parts = []

    # Re-emit captured @keyframes directly
    for kf in keyframes:
        name = kf.get("name", "unnamed")
        frames = kf.get("keyframes", [])
        rules = "\n".join(
            f"  {f.get('offset', '0%')} {{ {f.get('style', '')} }}"
            for f in frames
        )
        css_parts.append(f"@keyframes {name} {{\n{rules}\n}}")

    # Convert WAAPI keyframes to @keyframes
    seen_waapi = set()
    for anim in waapi:
        anim_name = anim.get("animationName") or f"waapi-{hash(str(anim)) & 0xFFFF:04x}"
        if anim_name in seen_waapi:
            continue
        seen_waapi.add(anim_name)
        kfs = anim.get("keyframes", [])
        if kfs:
            rules = "\n".join(
                f"  {int(float(k.get('offset', 0)) * 100)}% {{ "
                + "; ".join(f"{p}: {v}" for p, v in k.items() if p != "offset" and p != "easing")
                + " }}"
                for k in kfs
            )
            css_parts.append(f"@keyframes {anim_name} {{\n{rules}\n}}")

    return "\n\n".join(css_parts)


async def _extract_lottie_animations(cdp) -> list[dict]:
    """
    Detects and extracts Lottie / Bodymovin animations:
    - <lottie-player> elements (src or data)
    - <dotlottie-player> elements
    - Elements initialized with window.lottie or window.bodymovin
    """
    try:
        result = await cdp.send("Runtime.evaluate", {
            "expression": """
                (() => {
                    const lotties = [];
                    // Check lottie-player custom elements
                    const players = document.querySelectorAll('lottie-player, dotlottie-player, [data-animation-path]');
                    players.forEach((p, idx) => {
                        const src = p.getAttribute('src') || p.getAttribute('data-animation-path') || '';
                        let data = null;
                        try {
                            if (p.getLottie) {
                                const anim = p.getLottie();
                                data = anim ? anim.animationData : null;
                            }
                        } catch (_) {}
                        lotties.push({
                            id: p.id || `lottie-player-${idx}`,
                            tag: p.tagName.toLowerCase(),
                            src: src,
                            has_embedded_data: !!data,
                            data: data,
                            loop: p.hasAttribute('loop'),
                            autoplay: p.hasAttribute('autoplay'),
                            selector: p.id ? '#' + p.id : (p.className ? '.' + p.className.split(' ')[0] : 'lottie-player'),
                        });
                    });

                    // Check window.bodymovin / window.lottie registered animations
                    if (window.lottie && window.lottie.getRegisteredAnimations) {
                        try {
                            const registered = window.lottie.getRegisteredAnimations();
                            registered.forEach((a, idx) => {
                                lotties.push({
                                    id: `lottie-registered-${idx}`,
                                    tag: 'bodymovin-instance',
                                    src: '',
                                    has_embedded_data: !!a.animationData,
                                    data: a.animationData,
                                    loop: a.loop,
                                    autoplay: a.autoplay,
                                    selector: a.wrapper ? (a.wrapper.id ? '#' + a.wrapper.id : '.' + (a.wrapper.className || '').split(' ')[0]) : 'unknown',
                                });
                            });
                        } catch (_) {}
                    }
                    return lotties;
                })()
            """,
            "returnByValue": True,
            "timeout": 10000,
        })
        return result.get("result", {}).get("value", []) or []
    except Exception as e:
        logger.debug(f"Lottie extraction failed: {e}")
        return []


async def _extract_scroll_triggers(cdp) -> list[dict]:
    """
    Detects elements that use scroll-triggered animations:
    - AOS attributes (data-aos)
    - GSAP ScrollTrigger
    - Elements with [data-scroll], [data-reveal], [data-animate]
    - Elements with transition and initially hidden styling
    """
    try:
        result = await cdp.send("Runtime.evaluate", {
            "expression": """
                (() => {
                    const triggers = [];
                    // 1. Common scroll animation data-attributes
                    const attrSelectors = [
                        '[data-aos]', '[data-scroll]', '[data-reveal]',
                        '[data-animate]', '[data-sal]', '[data-wow-delay]',
                        '[data-framer-name]'
                    ];
                    const attrEls = document.querySelectorAll(attrSelectors.join(','));
                    attrEls.forEach((el, idx) => {
                        const style = window.getComputedStyle(el);
                        triggers.push({
                            id: el.id || `scroll-trigger-${idx}`,
                            selector: el.id ? '#' + el.id : (el.className ? '.' + el.className.split(' ')[0] : el.tagName.toLowerCase()),
                            aos_animation: el.getAttribute('data-aos') || '',
                            aos_delay: el.getAttribute('data-aos-delay') || '0',
                            aos_duration: el.getAttribute('data-aos-duration') || '400',
                            type: 'attribute_trigger',
                            initial_opacity: style.opacity,
                            initial_transform: style.transform !== 'none' ? style.transform : '',
                        });
                    });

                    // 2. GSAP ScrollTrigger if active
                    if (window.ScrollTrigger && window.ScrollTrigger.getAll) {
                        try {
                            const stList = window.ScrollTrigger.getAll();
                            stList.forEach((st, idx) => {
                                const trig = st.trigger;
                                triggers.push({
                                    id: `gsap-scroll-trigger-${idx}`,
                                    selector: trig ? (trig.id ? '#' + trig.id : '.' + (trig.className || '').split(' ')[0]) : 'unknown',
                                    start: st.start,
                                    end: st.end,
                                    type: 'gsap_scrolltrigger',
                                });
                            });
                        } catch (_) {}
                    }

                    return triggers.slice(0, 100);
                })()
            """,
            "returnByValue": True,
            "timeout": 8000,
        })
        return result.get("result", {}).get("value", []) or []
    except Exception as e:
        logger.debug(f"Scroll-trigger extraction failed: {e}")
        return []


def build_scroll_rebind_runtime_js(scroll_triggers: list[dict]) -> str:
    """
    Generates a lightweight, resilient IntersectionObserver runtime script
    that ensures all scroll-triggered elements animate into view when scrolled
    in the cloned HTML document, and never stay stuck at opacity:0.
    """
    return """
<!-- UI Cloner Scroll Animation Runtime -->
<script id="uiclone-scroll-runtime">
(() => {
    function initScrollTriggers() {
        const observerOptions = {
            root: null,
            rootMargin: '0px 0px -50px 0px',
            threshold: 0.1
        };

        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    // Trigger AOS classes
                    if (el.hasAttribute('data-aos')) {
                        el.classList.add('aos-animate');
                    }
                    // Trigger generic reveal
                    el.classList.add('uiclone-revealed', 'in-view');
                    el.style.opacity = '1';
                    el.style.transform = 'none';
                    el.style.visibility = 'visible';
                    obs.unobserve(el);
                }
            });
        }, observerOptions);

        // Observe elements with animation data-attributes
        const selectors = [
            '[data-aos]', '[data-scroll]', '[data-reveal]',
            '[data-animate]', '[data-sal]', '.animate-on-scroll'
        ];
        document.querySelectorAll(selectors.join(',')).forEach(el => {
            observer.observe(el);
        });

        // Safety fallback: Ensure any initially hidden elements are revealed if stuck
        setTimeout(() => {
            document.querySelectorAll(selectors.join(',')).forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.top < window.innerHeight && rect.bottom > 0) {
                    el.classList.add('aos-animate', 'uiclone-revealed');
                    el.style.opacity = '1';
                    el.style.transform = 'none';
                    el.style.visibility = 'visible';
                }
            });
        }, 1200);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initScrollTriggers);
    } else {
        initScrollTriggers();
    }
})();
</script>
"""


def build_lottie_runtime_js(lottie_items: list[dict]) -> str:
    """
    Generates an embedded Lottie offline player runtime with inlined animation data.
    """
    if not lottie_items:
        return ""

    import json
    data_map = {}
    for item in lottie_items:
        if item.get("data"):
            data_map[item["id"]] = item["data"]

    data_json = json.dumps(data_map)

    template = """
<!-- UI Cloner Embedded Lottie Runtime -->
<script id="uiclone-lottie-data" type="application/json">
__LOTTIE_DATA__
</script>
<script id="uiclone-lottie-runtime">
(() => {
    // If lottie-player or bodymovin is present, rebind embedded animation data
    function mountLotties() {
        try {
            const raw = document.getElementById('uiclone-lottie-data');
            if (!raw) return;
            const animations = JSON.parse(raw.textContent || '{}');
            Object.keys(animations).forEach(id => {
                const el = document.getElementById(id);
                if (el && el.load && animations[id]) {
                    el.load(animations[id]);
                }
            });
        } catch(e) {
            console.debug('Lottie mount note:', e);
        }
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', mountLotties);
    } else {
        mountLotties();
    }
})();
</script>
"""
    return template.replace("__LOTTIE_DATA__", data_json)
