"""
Cost of Inaction – Model Validation

This module performs sanity checks and invariants
to validate the internal consistency of the model.
"""

from .calculator import run_cost_of_inaction_analysis


def validate_model(assessment) -> None:
    """
    Run internal consistency checks.
    Raises AssertionError if invariants are violated.
    """

    results = run_cost_of_inaction_analysis(assessment)

    # Invariant 1: No investment should not be cheaper than strategic
    assert (
        results["no_investment"]["total_cost_k"]
        >= results["strategic_investment"]["total_cost_k"]
    ), "No investment scenario should not outperform strategic investment."

    # Invariant 2: Loss must be non-negative
    for data in results.values():
        assert data["expected_loss_k"] >= 0, "Negative loss detected."

    # Invariant 3: Investing more should not increase expected loss.
    # expected_loss_k is now a simulation mean (300 iterations). The ordering
    # holds as long as SIMULATION_SEED is fixed — E[noise] = 1.0 ensures the
    # mean is unbiased, and the scenario reductions are large enough relative
    # to noise magnitude that violations are not expected. If SIMULATION_SEED
    # is set to None (non-deterministic), this assertion may occasionally fail.
    assert (
        results["strategic_investment"]["expected_loss_k"]
        <= results["partial_investment"]["expected_loss_k"]
        <= results["no_investment"]["expected_loss_k"]
    ), "Monotonicity violated. Check SIMULATION_SEED and scenario reduction parameters."
