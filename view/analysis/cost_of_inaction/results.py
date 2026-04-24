"""
Cost of Inaction – Results Interpretation

Interprets the numerical outputs of the cost-of-inaction calculator and
derives executive-level insights, risk rankings, and portfolio metrics.

All values are expressed in multiples of K.
"""

from typing import Dict, List

from models.companyRisk import CompanyAssessment, CompanyRisk

from .theorical_model import estimate_relative_loss
from .scenarios import SCENARIOS


# ==========================================================
# SCENARIO COMPARISON  (existing – unchanged)
# ==========================================================

def rank_scenarios(results: Dict[str, Dict[str, float]]) -> List[str]:
    """
    Rank scenarios by total relative cost (loss + investment).
    Lower is better.
    """
    return sorted(
        results.keys(),
        key=lambda k: results[k]["total_cost_k"]
    )


def get_best_scenario(results: Dict[str, Dict[str, float]]) -> str:
    """
    Return the scenario with the lowest total cost.
    """
    ranked = rank_scenarios(results)
    return ranked[0] if ranked else ""


# ==========================================================
# EXECUTIVE METRICS  (existing – unchanged)
# ==========================================================

def calculate_avoided_loss(
    results: Dict[str, Dict[str, float]],
    baseline: str = "no_investment",
) -> Dict[str, float]:
    """
    Calculate avoided loss compared to a baseline scenario.
    """
    baseline_loss = results[baseline]["expected_loss_k"]
    avoided = {}

    for key, data in results.items():
        avoided[key] = round(baseline_loss - data["expected_loss_k"], 2)

    return avoided


# ==========================================================
# EXECUTIVE SUMMARY  (existing – unchanged)
# ==========================================================

def build_executive_summary(
    results: Dict[str, Dict[str, float]],
) -> List[str]:
    """
    Generate executive-level conclusions from the analysis.
    """

    summary = []

    ranked = rank_scenarios(results)
    best = ranked[0]
    worst = ranked[-1]

    best_data = results[best]
    worst_data = results[worst]

    # Key conclusion 1: cost of inaction
    summary.append(
        f"Maintaining the current security posture results in an expected "
        f"relative loss of approximately {results['no_investment']['expected_loss_k']}K "
        f"over the analysis horizon."
    )

    # Key conclusion 2: efficiency of investment
    summary.append(
        f"The '{best}' scenario minimizes the total relative cost "
        f"({best_data['total_cost_k']}K), combining both residual loss "
        f"and required investment."
    )

    # Key conclusion 3: comparative impact
    delta = round(
        worst_data["total_cost_k"] - best_data["total_cost_k"], 2
    )
    summary.append(
        f"The difference between the most and least effective scenarios "
        f"represents a relative impact of {delta}K."
    )

    # Key conclusion 4: systemic exposure
    risk_count = results["no_investment"]["risk_count"]
    summary.append(
        f"The current risk profile includes {risk_count} material risks, "
        f"indicating potential systemic exposure if no action is taken."
    )

    return summary


# ==========================================================
# PERCENTILE SUMMARY  (new)
# ==========================================================

def get_percentile_summary(
    results: Dict[str, Dict[str, float]],
) -> Dict[str, Dict[str, float]]:
    """
    Extract the P50 and P90 loss estimates per scenario from the simulation
    output produced by calculate_scenario_loss.

    P50 (median): the loss value exceeded in half of simulated iterations.
        Because loss distributions are right-skewed, P50 < mean; it
        represents the most likely single outcome rather than the average.

    P90: the loss value exceeded in only 10% of iterations.
        Useful for stress-testing and capital reservation decisions.

    Falls back to expected_loss_k if percentile keys are absent (e.g. when
    called with results from an older version of the calculator).

    Returns:
        {scenario_key: {"p50_k": float, "p90_k": float}}
    """
    summary = {}
    for key, data in results.items():
        summary[key] = {
            "p50_k": data.get("p50_loss_k", data["expected_loss_k"]),
            "p90_k": data.get("p90_loss_k", data["expected_loss_k"]),
        }
    return summary


# ==========================================================
# RISK RANKING BY ECONOMIC IMPACT  (new)
# ==========================================================

def rank_risks_by_economic_impact(
    assessment: CompanyAssessment,
    scenario_key: str = "no_investment",
) -> List[Dict]:
    """
    Rank every active risk by its individual deterministic economic loss
    contribution under the given scenario.

    The loss is computed using the same theoretical model as the calculator
    but without Monte Carlo noise, so the ranking is stable across calls and
    comparable across scenarios.

    Each entry contains:
        risk_id         — unique identifier of the risk
        name            — human-readable label
        risk_level      — qualitative level (BAJO / MEDIO / ALTO / CRÍTICO)
        residual_risk   — current residual risk score (0–25)
        expected_loss_k — individual deterministic loss in multiples of K

    The list is ordered from highest to lowest expected_loss_k.
    """
    scenario      = SCENARIOS[scenario_key]
    prob_factor   = 1 - scenario["probability_reduction"]
    impact_factor = 1 - scenario["impact_reduction"]

    entries = []

    for cr in assessment.get_active_risks():
        residual = cr.calculate_residual_risk()
        coverage = cr.get_control_coverage() / 100.0

        loss = estimate_relative_loss(
            residual_risk=residual * prob_factor,
            financial_impact=cr.custom_impact_financial * impact_factor,
            operational_impact=cr.custom_impact_operational * impact_factor,
            reputational_impact=cr.custom_impact_reputational * impact_factor,
            control_effectiveness=coverage,
        )

        entries.append({
            "risk_id":         cr.base_risk.risk_id,
            "name":            cr.base_risk.name,
            "risk_level":      CompanyRisk.risk_level(residual),
            "residual_risk":   round(residual, 2),
            "expected_loss_k": round(loss, 3),
        })

    return sorted(entries, key=lambda x: x["expected_loss_k"], reverse=True)


# ==========================================================
# PORTFOLIO METRICS  (new)
# ==========================================================

def get_portfolio_metrics(
    results: Dict[str, Dict[str, float]],
    baseline: str = "no_investment",
) -> Dict:
    """
    Aggregate portfolio-level KPIs derived from the scenario analysis.

    Metrics returned:

        cost_of_inaction_k      — baseline expected loss (no investment)
        p90_exposure_k          — P90 loss under baseline (worst-decile estimate)
        best_scenario           — scenario key with lowest total cost
        best_total_cost_k       — total cost (loss + investment) of best scenario
        avoided_loss_k          — expected loss saved vs baseline in best scenario
        investment_k            — investment required for best scenario
        net_benefit_k           — avoided_loss − investment (positive = worth it)
        loss_reduction_pct      — percentage reduction in expected loss vs baseline
        worst_scenario          — scenario key with highest total cost
        material_risk_count     — number of contributing risks in baseline

    All monetary values are in multiples of K.
    """
    baseline_data = results[baseline]
    best_key      = get_best_scenario(results)
    worst_key     = rank_scenarios(results)[-1]
    best_data     = results[best_key]

    cost_of_inaction = baseline_data["expected_loss_k"]
    p90_exposure     = baseline_data.get("p90_loss_k", cost_of_inaction)

    avoided_by_scenario = calculate_avoided_loss(results, baseline)
    avoided_loss        = avoided_by_scenario.get(best_key, 0.0)
    investment          = best_data["investment_k"]
    net_benefit         = round(avoided_loss - investment, 2)

    loss_reduction_pct = 0.0
    if cost_of_inaction > 0:
        loss_reduction_pct = round(
            avoided_loss / cost_of_inaction * 100, 1
        )

    return {
        "cost_of_inaction_k":  cost_of_inaction,
        "p90_exposure_k":      round(p90_exposure, 2),
        "best_scenario":       best_key,
        "best_total_cost_k":   best_data["total_cost_k"],
        "avoided_loss_k":      avoided_loss,
        "investment_k":        investment,
        "net_benefit_k":       net_benefit,
        "loss_reduction_pct":  loss_reduction_pct,
        "worst_scenario":      worst_key,
        "material_risk_count": baseline_data["risk_count"],
    }
