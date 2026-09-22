"""
Layer -1: Pre-Flight Profiler & Predictive Telemetry Oracle
Performs zero-browser rapid network probing, WAF/CDN detection,
DOM complexity estimation, technology stack fingerprinting, and
live predictive telemetry tracking (time left / ETA, % completed, active operations).
"""
from __future__ import annotations

from uicloner.layers.layer_preflight.profiler import PreflightProfiler, TargetProfile
from uicloner.layers.layer_preflight.estimator import ExecutionTimelineEstimator, ExecutionPlan, PhaseEstimate
from uicloner.layers.layer_preflight.telemetry import TelemetryOracle, TelemetrySnapshot

__all__ = [
    "PreflightProfiler",
    "TargetProfile",
    "ExecutionTimelineEstimator",
    "ExecutionPlan",
    "PhaseEstimate",
    "TelemetryOracle",
    "TelemetrySnapshot",
    "run_preflight",
]


async def run_preflight(url: str, config=None) -> TelemetryOracle:
    """
    Convenience function to run Layer -1 pre-flight profiling and initialize
    the predictive Telemetry Oracle.
    """
    profiler = PreflightProfiler(config=config)
    profile = await profiler.probe(url)

    estimator = ExecutionTimelineEstimator(config=config)
    plan = estimator.estimate(profile)

    oracle = TelemetryOracle(profile=profile, plan=plan)
    oracle.start()
    return oracle
