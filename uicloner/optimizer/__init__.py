"""
Optimizer package for closed-loop visual auto-correction and fidelity tuning.
"""
from uicloner.optimizer.auto_corrector import (
    VisualAutoCorrector,
    OptimizationResult,
    CorrectionPatch,
)

__all__ = [
    "VisualAutoCorrector",
    "OptimizationResult",
    "CorrectionPatch",
]
