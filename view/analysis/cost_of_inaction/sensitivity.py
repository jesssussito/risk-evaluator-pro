"""
Cost of Inaction – Sensitivity Analysis

This module evaluates the robustness of the cost-of-inaction
conclusions under variations of key assumptions.

Note: only parameters held in mutable objects (dicts) can be varied
at runtime without re-importing modules. BASE_LOSS_MULTIPLIER is a
float constant and cannot be mutated across module boundaries, so
sensitivity is tested solely through impact-weight perturbation.
"""

from copy import deepcopy
from typing import Dict

from .calculator import run_cost_of_inaction_analysis
from .results import get_best_scenario
from .weights import IMPACT_DIMENSION_WEIGHTS


def run_sensitivity_analysis(
    assessment,
    variations: int = 10,
) -> Dict[str, float]:
    """
    Run sensitivity analysis by perturbing the financial impact weight.

    Alternates the weight up and down by ±5% per step and checks whether
    the best-scenario conclusion changes. Restores the original weight
    after the analysis to avoid polluting global model state.
    """

    baseline_results = run_cost_of_inaction_analysis(assessment)
    baseline_best    = get_best_scenario(baseline_results)

    original_financial_weight = IMPACT_DIMENSION_WEIGHTS["financial"]
    stable_count = 0

    try:
        for i in range(variations):
            IMPACT_DIMENSION_WEIGHTS["financial"] *= 1 + (0.05 * (-1) ** (i + 1))

            results = run_cost_of_inaction_analysis(assessment)
            best    = get_best_scenario(results)

            if best == baseline_best:
                stable_count += 1
    finally:
        # Always restore to avoid side-effects on subsequent calls
        IMPACT_DIMENSION_WEIGHTS["financial"] = original_financial_weight

    robustness = stable_count / variations
    return {
        "baseline_best":    baseline_best,
        "robustness_ratio": round(robustness, 2),
        "tests":            variations,
    }
