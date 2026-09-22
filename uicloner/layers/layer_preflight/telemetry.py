"""
Telemetry Oracle (Layer -1)
Real-time progress oracle providing dynamic ETA calculations,
percentage completion metrics, and human-readable operational tracking.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict
from typing import Optional

from uicloner.layers.layer_preflight.estimator import ExecutionPlan
from uicloner.layers.layer_preflight.profiler import TargetProfile


@dataclass
class TelemetrySnapshot:
    """Instantaneous snapshot of execution telemetry."""
    elapsed_seconds: float
    elapsed_formatted: str
    estimated_total_seconds: float
    eta_seconds_left: float
    eta_formatted: str
    percent_done: float
    active_layer: str
    active_phase_id: str
    current_operation: str
    is_complete: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


class TelemetryOracle:
    """
    Live state engine tracking progress across all layers.
    Computes time remaining, % done, and human-readable active task status.
    """

    def __init__(self, profile: TargetProfile, plan: ExecutionPlan):
        self.profile = profile
        self.plan = plan
        self.start_time: float = 0.0
        self.current_phase_id: str = "preflight"
        self.current_operation: str = "Initializing Pre-Flight analysis..."
        self.completed_phases: dict[str, float] = {}  # phase_id -> actual_duration
        self.cumulative_weight_done: float = 0.0
        self._is_complete: bool = False

    def start(self) -> None:
        """Mark pipeline start time."""
        self.start_time = time.time()

    @property
    def elapsed_seconds(self) -> float:
        if self.start_time == 0.0:
            return 0.0
        return time.time() - self.start_time

    def step(
        self,
        phase_id: str,
        operation_description: Optional[str] = None,
        intra_phase_progress: float = 0.0,
    ) -> TelemetrySnapshot:
        """
        Record a step transition or sub-operation update.
        `intra_phase_progress`: float from 0.0 to 1.0 within the current phase.
        """
        now = time.time()
        if self.start_time == 0.0:
            self.start_time = now

        elapsed = now - self.start_time

        # Calculate completed phases weight
        phases = self.plan.phases
        current_idx = 0
        weight_before_current = 0.0

        for i, p in enumerate(phases):
            if p.phase_id == phase_id:
                current_idx = i
                break
            weight_before_current += p.weight_pct

        current_phase = phases[current_idx] if current_idx < len(phases) else phases[-1]
        self.current_phase_id = phase_id

        if operation_description:
            self.current_operation = operation_description
        else:
            self.current_operation = current_phase.description

        # Compute dynamic progress percentage (0 to 100)
        current_phase_progress = min(1.0, max(0.0, intra_phase_progress))
        pct_done = weight_before_current + (current_phase.weight_pct * current_phase_progress)
        pct_done = min(99.0, max(0.0, pct_done))

        # Dynamic ETA recalibration:
        # Based on average pace vs expected pace so far
        expected_time_so_far = sum(p.estimated_seconds for p in phases[:current_idx])
        expected_time_so_far += current_phase.estimated_seconds * current_phase_progress

        if expected_time_so_far > 0.5 and elapsed > 0.5:
            pace_factor = elapsed / expected_time_so_far
        else:
            pace_factor = 1.0

        # Bound pace factor to avoid wild fluctuations
        pace_factor = max(0.5, min(2.5, pace_factor))

        remaining_expected = sum(p.estimated_seconds for p in phases[current_idx + 1:])
        remaining_expected += current_phase.estimated_seconds * (1.0 - current_phase_progress)
        eta_seconds_left = max(1.0, remaining_expected * pace_factor)

        total_est = elapsed + eta_seconds_left

        return TelemetrySnapshot(
            elapsed_seconds=round(elapsed, 1),
            elapsed_formatted=self._format_duration(elapsed),
            estimated_total_seconds=round(total_est, 1),
            eta_seconds_left=round(eta_seconds_left, 1),
            eta_formatted=f"~{self._format_duration(eta_seconds_left)} left",
            percent_done=round(pct_done, 1),
            active_layer=current_phase.layer_name,
            active_phase_id=phase_id,
            current_operation=self.current_operation,
            is_complete=False,
        )

    def mark_complete(self, final_operation: str = "Clone complete & verified") -> TelemetrySnapshot:
        """Mark pipeline as 100% complete."""
        self._is_complete = True
        elapsed = time.time() - self.start_time
        return TelemetrySnapshot(
            elapsed_seconds=round(elapsed, 1),
            elapsed_formatted=self._format_duration(elapsed),
            estimated_total_seconds=round(elapsed, 1),
            eta_seconds_left=0.0,
            eta_formatted="Completed",
            percent_done=100.0,
            active_layer="Complete",
            active_phase_id="complete",
            current_operation=final_operation,
            is_complete=True,
        )

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format seconds into MM:SS or Xs."""
        sec_int = int(round(seconds))
        mins, secs = divmod(sec_int, 60)
        if mins > 0:
            return f"{mins:02d}:{secs:02d}"
        return f"00:{secs:02d}"

    def to_dict(self) -> dict:
        """Export complete preflight diagnostics and timeline structure."""
        return {
            "target_profile": self.profile.to_dict(),
            "execution_plan": self.plan.to_dict(),
            "elapsed_seconds": round(self.elapsed_seconds, 2),
            "is_complete": self._is_complete,
        }
