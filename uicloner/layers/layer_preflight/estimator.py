"""
Execution Timeline Estimator (Layer -1)
Synthesizes target profile metrics into a predictive execution plan,
allocating estimated durations and progress weights across all engine layers.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional

from uicloner.layers.layer_preflight.profiler import TargetProfile


@dataclass
class PhaseEstimate:
    """Estimated duration, weight, and operational description for a pipeline phase."""
    phase_id: str
    layer_name: str
    estimated_seconds: float
    weight_pct: float
    description: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ExecutionPlan:
    """Comprehensive predictive timeline for the entire cloning run."""
    url: str
    total_estimated_seconds: float
    phases: list[PhaseEstimate] = field(default_factory=list)
    complexity_level: str = "Medium"
    summary: str = ""

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "total_estimated_seconds": round(self.total_estimated_seconds, 1),
            "complexity_level": self.complexity_level,
            "summary": self.summary,
            "phases": [p.to_dict() for p in self.phases],
        }

    def get_phase(self, phase_id: str) -> Optional[PhaseEstimate]:
        for p in self.phases:
            if p.phase_id == phase_id:
                return p
        return None


class ExecutionTimelineEstimator:
    """
    Analyzes TargetProfile attributes (WAF presence, scripts count, asset count,
    complexity score, SPA dynamic index) to construct a realistic timeline.
    """

    def __init__(self, config=None):
        self.config = config

    def estimate(self, profile: TargetProfile) -> ExecutionPlan:
        phases: list[PhaseEstimate] = []

        # 1. Pre-Flight Layer (-1)
        phases.append(PhaseEstimate(
            phase_id="preflight",
            layer_name="Layer -1: Pre-Flight Profiler",
            estimated_seconds=0.8,
            weight_pct=4.0,
            description="Probing edge headers, WAF signatures, and DOM complexity",
        ))

        # 2. Evasion & Fingerprinting (Layer 0)
        phases.append(PhaseEstimate(
            phase_id="evasion",
            layer_name="Layer 0: Anti-Bot Evasion",
            estimated_seconds=1.2,
            weight_pct=5.0,
            description="Generating BrowserForge fingerprint & canvas noise seeds",
        ))

        # 3. Browser Launch (Layer 1)
        phases.append(PhaseEstimate(
            phase_id="browser",
            layer_name="Layer 1: Stealth Browser",
            estimated_seconds=2.2,
            weight_pct=7.0,
            description="Launching stealth engine & establishing CDP connection",
        ))

        # 4. Navigation & Stabilization
        nav_base = 2.0
        if profile.is_waf_protected:
            nav_base += 2.5  # Extra time for edge challenges / turnstile bypass
        if profile.dynamic_spa_index > 0.6:
            nav_base += 1.8  # Extra hydration wait for heavy SPAs
        nav_base += min(2.0, profile.latency_ms / 300.0)

        phases.append(PhaseEstimate(
            phase_id="navigate",
            layer_name="Layer 1: Stealth Browser",
            estimated_seconds=round(nav_base, 1),
            weight_pct=10.0,
            description=f"Navigating to {profile.host} & awaiting network idle",
        ))

        # 5. DOM Tree & Shadow DOM (Layer 2)
        dom_base = 1.5 + (profile.complexity_score * 0.15)
        if profile.has_shadow_dom:
            dom_base += 1.2
        phases.append(PhaseEstimate(
            phase_id="dom",
            layer_name="Layer 2: DOM Extraction",
            estimated_seconds=round(dom_base, 1),
            weight_pct=10.0,
            description=f"Capturing DOM tree (~{profile.estimated_dom_nodes} nodes) & piercing Shadow roots",
        ))

        # 6. Event Listeners & Framework Events (Layer 2)
        events_base = 1.4 + min(2.0, profile.scripts_count * 0.05)
        phases.append(PhaseEstimate(
            phase_id="events",
            layer_name="Layer 2: DOM Extraction",
            estimated_seconds=round(events_base, 1),
            weight_pct=8.0,
            description="Recovering DOMDebugger listeners & framework event roots",
        ))

        # 7. Animation Extraction (Layer 2)
        anim_base = 1.2
        if any(f in profile.detected_frameworks for f in ["GSAP", "Lottie"]):
            anim_base += 1.8
        phases.append(PhaseEstimate(
            phase_id="animations",
            layer_name="Layer 2: DOM Extraction",
            estimated_seconds=round(anim_base, 1),
            weight_pct=7.0,
            description="Extracting CSS keyframes, WAAPI animations & scroll drivers",
        ))

        # 8. UI Element Dismantling & Analysis (Layer 2.5)
        dismantle_base = 1.8 + min(2.5, profile.buttons_count * 0.1)
        phases.append(PhaseEstimate(
            phase_id="dismantle",
            layer_name="Layer 2.5: UI Dismantler",
            estimated_seconds=round(dismantle_base, 1),
            weight_pct=9.0,
            description=f"Dismantling buttons ({profile.buttons_count} est.) & design tokens",
        ))

        # 9. Behavioral State Exploration (Layer 2.6)
        explore_base = 2.4
        phases.append(PhaseEstimate(
            phase_id="explore",
            layer_name="Layer 2.6: State Explorer",
            estimated_seconds=round(explore_base, 1),
            weight_pct=10.0,
            description="Probing hover transitions, focus rings & interactive states",
        ))

        # 10. Asset Processing & Deduplication (Layer 3)
        total_assets = profile.scripts_count + profile.styles_count + profile.images_count
        assets_base = 1.5 + min(4.0, total_assets * 0.06)
        phases.append(PhaseEstimate(
            phase_id="process",
            layer_name="Layer 3: Asset Pipeline",
            estimated_seconds=round(assets_base, 1),
            weight_pct=12.0,
            description=f"Downloading ~{total_assets} assets with SHA-256 dedupe & SQLite indexing",
        ))

        # 11. Single-File HTML Assembly (Layer 4)
        phases.append(PhaseEstimate(
            phase_id="pack",
            layer_name="Layer 4: Assembly & Output",
            estimated_seconds=1.5,
            weight_pct=8.0,
            description="Assembling single-file HTML clone with inline runtimes",
        ))

        # 12. Visual Auto-Correction & Verification (Layer 4)
        val_base = 2.5
        phases.append(PhaseEstimate(
            phase_id="validate",
            layer_name="Layer 4: Assembly & Output",
            estimated_seconds=round(val_base, 1),
            weight_pct=10.0,
            description="Performing pixel diff & closed-loop visual auto-correction",
        ))

        total_sec = sum(p.estimated_seconds for p in phases)

        # Normalize weights to sum exactly to 100%
        weight_sum = sum(p.weight_pct for p in phases)
        for p in phases:
            p.weight_pct = round((p.weight_pct / weight_sum) * 100.0, 1)

        complexity_str = "Low"
        if profile.complexity_score >= 8:
            complexity_str = "High"
        elif profile.complexity_score >= 5:
            complexity_str = "Medium"

        summary = (
            f"Estimated total execution time: {total_sec:.1f}s across {len(phases)} phases "
            f"({complexity_str} complexity, ~{total_assets} assets, {profile.cdn_waf})"
        )

        return ExecutionPlan(
            url=profile.url,
            total_estimated_seconds=round(total_sec, 1),
            phases=phases,
            complexity_level=complexity_str,
            summary=summary,
        )
