"""
Cost of Inaction – Calculator

Applies the theoretical loss model to the organization's current risk profile
under different investment scenarios, using a Monte Carlo simulation to
capture uncertainty in probability and impact estimates.

Internal structure:
  · Layer 1  – _base_loss_for_risk       : deterministic baseline, no scenario
  · Layer 2a – _scenario_loss_for_risk   : deterministic, scenario applied
  · Layer 2b – _perturbed_loss_for_risk  : stochastic, scenario + noise per risk
  · Layer 3  – _run_one_iteration        : one pass over the active portfolio
  · Simulation – _run_simulation         : N iterations → aggregated mean

All outputs are expressed in multiples of K.
"""

import random
from typing import Dict, List, Tuple

from models.companyRisk import CompanyAssessment, CompanyRisk

from .theorical_model import (
    estimate_relative_loss,
    apply_correlation_effect,
)
from .scenarios import SCENARIOS
from .assumptions import (
    SIMULATION_ITERATIONS,
    SIMULATION_PROBABILITY_NOISE,
    SIMULATION_IMPACT_NOISE,
    SIMULATION_SEED,
)


# ==========================================================
# LAYER 1 – BASE LOSS (no scenario adjustments)
# ==========================================================

def _base_loss_for_risk(cr: CompanyRisk) -> float:
    """
    Relative loss for a single risk using its current values as-is.
    No scenario probability/impact reductions are applied.
    """
    residual = cr.calculate_residual_risk()
    coverage = cr.get_control_coverage() / 100.0

    return estimate_relative_loss(
        residual_risk=residual,
        financial_impact=cr.custom_impact_financial,
        operational_impact=cr.custom_impact_operational,
        reputational_impact=cr.custom_impact_reputational,
        control_effectiveness=coverage,
    )


# ==========================================================
# LAYER 2 – SCENARIO APPLICATION
# ==========================================================

def _scenario_loss_for_risk(cr: CompanyRisk, scenario: dict) -> float:
    """
    Deterministic loss for one risk with scenario reductions applied.
    Used as a reference; the simulation uses the perturbed variant below.
    """
    residual = cr.calculate_residual_risk()
    coverage = cr.get_control_coverage() / 100.0

    adjusted_residual = residual * (1 - scenario["probability_reduction"])
    impact_factor     = 1 - scenario["impact_reduction"]

    return estimate_relative_loss(
        residual_risk=adjusted_residual,
        financial_impact=cr.custom_impact_financial * impact_factor,
        operational_impact=cr.custom_impact_operational * impact_factor,
        reputational_impact=cr.custom_impact_reputational * impact_factor,
        control_effectiveness=coverage,
    )


def _perturbed_loss_for_risk(
    cr: CompanyRisk,
    scenario: dict,
    rng: random.Random,
) -> float:
    """
    Stochastic loss for one risk: scenario reductions are applied first,
    then independent multiplicative noise is added to probability and impact.

    Noise model:
      · probability axis → adjusted_residual × Uniform(1−p_noise, 1+p_noise)
      · impact axis      → each impact dimension × Uniform(1−i_noise, 1+i_noise)

    The two noise draws are independent: a risk may face higher-than-expected
    probability without necessarily having higher-than-expected impact.
    The adjusted residual is clamped to ≥ 0 to prevent negative inputs.
    """
    residual = cr.calculate_residual_risk()
    coverage = cr.get_control_coverage() / 100.0

    prob_noise   = rng.uniform(1.0 - SIMULATION_PROBABILITY_NOISE,
                               1.0 + SIMULATION_PROBABILITY_NOISE)
    impact_noise = rng.uniform(1.0 - SIMULATION_IMPACT_NOISE,
                               1.0 + SIMULATION_IMPACT_NOISE)

    adjusted_residual = max(0.0, residual * (1 - scenario["probability_reduction"]) * prob_noise)
    impact_factor     = (1 - scenario["impact_reduction"]) * impact_noise

    return estimate_relative_loss(
        residual_risk=adjusted_residual,
        financial_impact=cr.custom_impact_financial * impact_factor,
        operational_impact=cr.custom_impact_operational * impact_factor,
        reputational_impact=cr.custom_impact_reputational * impact_factor,
        control_effectiveness=coverage,
    )


# ==========================================================
# LAYER 3 – SIMULATION
# ==========================================================

def _run_one_iteration(
    active_risks: list,
    scenario: dict,
    rng: random.Random,
) -> Tuple[float, int]:
    """
    One Monte Carlo iteration: aggregate perturbed losses across all active
    risks and apply the portfolio correlation effect.

    Returns:
        (total_loss_k, contributing_risk_count)
    """
    total_loss         = 0.0
    contributing_risks = 0

    for cr in active_risks:
        loss = _perturbed_loss_for_risk(cr, scenario, rng)
        if loss > 0:
            total_loss         += loss
            contributing_risks += 1

    total_loss = apply_correlation_effect(total_loss, contributing_risks)
    return total_loss, contributing_risks


def _percentile(sorted_values: List[float], p: float) -> float:
    """Return the p-th percentile (0–100) of a pre-sorted list."""
    idx = int(p / 100.0 * len(sorted_values))
    return sorted_values[min(idx, len(sorted_values) - 1)]


def _run_simulation(
    assessment: CompanyAssessment,
    scenario: dict,
) -> Tuple[float, float, float, int]:
    """
    Run SIMULATION_ITERATIONS Monte Carlo iterations for one scenario.

    Each iteration independently perturbs the probability and impact of every
    active risk, aggregates the portfolio loss, and records the result.

    Returns:
        (mean_loss_k, p50_loss_k, p90_loss_k, mean_contributing_risk_count)
    """
    rng          = random.Random(SIMULATION_SEED)
    active_risks = assessment.get_active_risks()

    losses: List[float] = []
    counts: List[int]   = []

    for _ in range(SIMULATION_ITERATIONS):
        loss, count = _run_one_iteration(active_risks, scenario, rng)
        losses.append(loss)
        counts.append(count)

    sorted_losses = sorted(losses)
    mean_loss     = sum(losses) / len(losses)
    p50           = _percentile(sorted_losses, 50)
    p90           = _percentile(sorted_losses, 90)
    mean_count    = round(sum(counts) / len(counts))

    return mean_loss, p50, p90, mean_count


# ==========================================================
# PUBLIC API – unchanged
# ==========================================================

def calculate_scenario_loss(
    assessment: CompanyAssessment,
    scenario_key: str,
) -> Dict[str, float]:
    """
    Calculate expected loss for a single scenario via Monte Carlo simulation.

    `expected_loss_k` is the mean loss across all iterations.
    The public interface is identical to the pre-simulation version.
    """
    scenario                     = SCENARIOS[scenario_key]
    mean_loss, p50, p90, mean_count = _run_simulation(assessment, scenario)

    return {
        "expected_loss_k": round(mean_loss, 2),
        "p50_loss_k":      round(p50, 2),
        "p90_loss_k":      round(p90, 2),
        "investment_k":    scenario["investment_k"],
        "total_cost_k":    round(mean_loss + scenario["investment_k"], 2),
        "risk_count":      mean_count,
    }


def run_cost_of_inaction_analysis(
    assessment: CompanyAssessment,
) -> Dict[str, Dict[str, float]]:
    """
    Run cost-of-inaction analysis for all defined scenarios.
    """
    return {
        key: calculate_scenario_loss(assessment, key)
        for key in SCENARIOS
    }
