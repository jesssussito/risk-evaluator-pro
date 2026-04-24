from models.companyRisk import CompanyRisk
from .results import (
    rank_scenarios,
    get_percentile_summary,
    rank_risks_by_economic_impact,
    get_portfolio_metrics,
)

_LEVEL_EN = {
    "BAJO":    "LOW",
    "MEDIO":   "MEDIUM",
    "ALTO":    "HIGH",
    "CRÍTICO": "CRITICAL",
}

_SCENARIO_INFO = {
    "no_investment": (
        "No Investment",
        "Current posture maintained. No additional controls or mitigation programs are applied. "
        "Exposure reflects the unmodified residual risk profile.",
    ),
    "partial_investment": (
        "Partial Investment",
        "Targeted improvements applied to the highest-risk areas. Reduces event likelihood on "
        "priority risks, but leaves structural gaps in place across the broader portfolio.",
    ),
    "strategic_investment": (
        "Strategic Investment",
        "Comprehensive program aligned with the full risk profile. Addresses both event "
        "likelihood and potential impact systematically across all identified risks.",
    ),
}


def _level(value: float) -> str:
    return _LEVEL_EN.get(CompanyRisk.risk_level(value), CompanyRisk.risk_level(value))


def build_report_text(assessment, results):
    sections = {}

    active_risks     = assessment.get_active_risks()
    ranked_scenarios = rank_scenarios(results)
    percentiles      = get_percentile_summary(results)
    portfolio        = get_portfolio_metrics(results)
    risk_ranking     = rank_risks_by_economic_impact(assessment, "no_investment") if active_risks else []

    best_key         = portfolio["best_scenario"]
    best_label       = _SCENARIO_INFO.get(best_key, (best_key,))[0]

    # ==================================================
    # 1. EXECUTIVE SUMMARY
    # ==================================================
    summary = []

    if not active_risks:
        summary.append(
            "No active risks have been selected for this assessment. "
            "The analysis cannot produce economic estimates without a defined risk scope."
        )
    else:
        critical_count = sum(
            1 for cr in active_risks
            if _level(cr.calculate_residual_risk()) in ("HIGH", "CRITICAL")
        )

        summary.append(
            f"This report assesses the economic cost of maintaining the current cybersecurity "
            f"posture across {len(active_risks)} active risk{'s' if len(active_risks) != 1 else ''}. "
            f"It compares three investment scenarios — no action, partial investment, and strategic "
            f"investment — and quantifies the financial difference between each path."
        )

        summary.append(
            f"[KEY] Cost of inaction (expected loss): {portfolio['cost_of_inaction_k']}K  "
            f"|  Worst-case stress scenario (P90): {portfolio['p90_exposure_k']}K"
        )

        if critical_count > 0:
            summary.append(
                f"{critical_count} risk{'s are' if critical_count != 1 else ' is'} currently "
                f"classified as HIGH or CRITICAL. These risks are the primary drivers of "
                f"expected loss and the first candidates for additional investment."
            )
        else:
            summary.append(
                "No risks are currently classified as HIGH or CRITICAL. The portfolio operates "
                "within moderate tolerance, though residual exposure still generates measurable "
                "expected loss under the current posture."
            )

        summary.append(
            f"[KEY] Best strategy: {best_label}  —  avoids {portfolio['avoided_loss_k']}K in "
            f"expected losses at a cost of {portfolio['investment_k']}K, delivering a net "
            f"benefit of {portfolio['net_benefit_k']}K and a {portfolio['loss_reduction_pct']}% "
            f"reduction in portfolio loss."
        )

        summary.append(
            "Cybersecurity investment should be understood as a value-preserving decision: "
            "the expected return exceeds the cost, and the alternative is accepting avoidable "
            "losses. The sections below provide the full evidence behind this conclusion."
        )

    sections["1. Executive Summary"] = summary

    # ==================================================
    # 2. RISK OVERVIEW
    # ==================================================
    overview = []

    if not active_risks:
        overview.append(
            "No active risks have been identified. The risk overview cannot be generated."
        )
    else:
        counts = assessment.count_risks_by_level()
        non_zero = {_LEVEL_EN.get(k, k): v for k, v in counts.items() if v > 0}

        overview.append(
            f"The assessment covers {len(active_risks)} active "
            f"risk{'s' if len(active_risks) != 1 else ''} evaluated on their residual "
            f"exposure — the remaining risk after applying existing controls. "
            f"Residual risk is the baseline for all economic estimates in this report."
        )

        if non_zero:
            dist_parts = [f"{v} {k}" for k, v in non_zero.items()]
            overview.append(f"## Distribution by level: {', '.join(dist_parts)}")

        overview.append(
            "Residual risk scores and individual economic loss contribution, "
            "ordered from highest to lowest impact:"
        )

        for entry in risk_ranking:
            lvl = _LEVEL_EN.get(entry["risk_level"], entry["risk_level"])
            overview.append(
                f"  • {entry['name']}: residual score {entry['residual_risk']:.2f} "
                f"({lvl})  —  expected loss {entry['expected_loss_k']}K"
            )

        high_critical = [
            cr for cr in active_risks
            if _level(cr.calculate_residual_risk()) in ("HIGH", "CRITICAL")
        ]

        if high_critical:
            overview.append(
                f"The {len(high_critical)} HIGH/CRITICAL "
                f"risk{'s' if len(high_critical) != 1 else ''} listed above account for a "
                f"disproportionate share of portfolio loss. Current controls reduce their "
                f"exposure, but residual levels remain above acceptable tolerance — indicating "
                f"a gap between existing mitigation and what is needed to reach a defensible posture."
            )
        else:
            overview.append(
                "All risks are currently at MEDIUM or below. While residual exposure still "
                "generates expected losses, the overall risk profile is within moderate tolerance "
                "under the existing control environment."
            )

    sections["2. Risk Overview"] = overview

    # ==================================================
    # 3. SCENARIO ANALYSIS
    # ==================================================
    scenario_section = []

    scenario_section.append(
        "This section compares three investment scenarios on expected loss, statistical "
        "outcome ranges, and total cost. The P50 figure is the median simulated outcome; "
        "P90 is the threshold exceeded only in the worst 10% of scenarios — the relevant "
        "benchmark for stress-testing organizational resilience and financial planning."
    )

    scenario_section.append(
        "Total expected cost (loss plus investment) is the most complete comparison basis. "
        "A scenario with higher upfront investment but lower total cost is financially "
        "superior when the avoided loss exceeds the additional spending."
    )

    scenario_section.append(
        "## How to read these figures"
    )
    scenario_section.append(
        "The risk scores and rankings in the previous section are calculated directly from "
        "the assessment model — each number is a fixed value derived from probability, impact, "
        "and control effectiveness. The figures below (expected loss, P50, P90) come from a "
        "different source: thousands of randomized what-if scenarios run against the same risk "
        "profile. They describe a range of plausible outcomes, not a single forecast. "
        "A higher P90 does not mean the risk scores were wrong — it means adverse outcomes, "
        "though unlikely, carry a larger financial consequence than the average suggests."
    )

    for key in ranked_scenarios:
        data  = results[key]
        pct   = percentiles[key]
        label, desc = _SCENARIO_INFO.get(key, (key, ""))
        spread = round(pct["p90_k"] - pct["p50_k"], 2)

        scenario_section.append(f"## {label}")
        scenario_section.append(desc)
        scenario_section.append(f"  • Expected loss (mean): {data['expected_loss_k']}K")
        scenario_section.append(f"  • Median outcome (P50): {pct['p50_k']}K")
        scenario_section.append(
            f"  • Stress scenario (P90): {pct['p90_k']}K  —  tail spread vs P50: {spread}K"
        )
        scenario_section.append(f"  • Investment required: {data['investment_k']}K")
        scenario_section.append(
            f"  • Total expected cost (loss + investment): {data['total_cost_k']}K"
        )

    scenario_section.append(
        "A wide P50-to-P90 spread signals high tail risk: while the typical outcome may be "
        "manageable, adverse scenarios carry disproportionately higher losses. Organizations "
        "with low risk tolerance should weight P90 more heavily when selecting a scenario."
    )

    scenario_section.append(
        f"[KEY] Lowest total expected cost: {best_label}"
    )

    sections["3. Scenario Analysis"] = scenario_section

    # ==================================================
    # 4. ECONOMIC IMPACT
    # ==================================================
    impact = []

    impact.append(
        "This section quantifies the total economic exposure of the portfolio and identifies "
        "which risks drive the largest share of expected losses. These figures directly "
        "inform prioritization decisions: where to invest first for maximum loss reduction."
    )

    no_inv_pct = percentiles.get("no_investment", {})

    impact.append(
        f"[KEY] Portfolio expected loss (current posture): {portfolio['cost_of_inaction_k']}K"
    )
    impact.append(
        f"  • Median simulated outcome (P50): {no_inv_pct.get('p50_k', 'N/A')}K"
    )
    impact.append(
        f"  • Stress scenario (P90): {portfolio['p90_exposure_k']}K  "
        f"— the organization should be financially prepared to absorb this amount"
    )

    if active_risks and risk_ranking:
        top_risks   = risk_ranking[:3]
        total_loss  = portfolio["cost_of_inaction_k"]

        impact.append("## Top risks by economic contribution")
        impact.append(
            "The three risks with the highest individual expected loss:"
        )

        top3_share = 0.0
        for i, entry in enumerate(top_risks, 1):
            lvl   = _LEVEL_EN.get(entry["risk_level"], entry["risk_level"])
            share = round(entry["expected_loss_k"] / total_loss * 100, 1) if total_loss > 0 else 0.0
            top3_share += share
            impact.append(
                f"  {i}. {entry['name']}  —  expected loss {entry['expected_loss_k']}K "
                f"({share}% of total)  [{lvl}]"
            )

        impact.append(
            f"These three risks account for approximately {top3_share:.0f}% of total portfolio "
            f"loss. Targeted investment here delivers the highest loss-reduction return "
            f"per unit of spending."
        )

    impact.append(
        f"[KEY] Avoided loss under {best_label}: {portfolio['avoided_loss_k']}K  "
        f"|  Net benefit after investment: {portfolio['net_benefit_k']}K"
    )

    impact.append(
        "All monetary figures use a normalized K-unit scale that enables scenario comparison "
        "without reference to absolute financial values. The proportional relationships "
        "between scenarios remain accurate regardless of the K denomination used."
    )

    sections["4. Economic Impact"] = impact

    # ==================================================
    # 5. RECOMMENDATIONS
    # ==================================================
    rec = []

    rec.append(
        f"[KEY] Primary recommendation: implement the {best_label} scenario."
    )

    rec.append(
        f"This strategy produces a net financial benefit of {portfolio['net_benefit_k']}K — "
        f"the expected losses avoided ({portfolio['avoided_loss_k']}K) exceed the investment "
        f"required ({portfolio['investment_k']}K). It reduces expected portfolio loss by "
        f"{portfolio['loss_reduction_pct']}% relative to the current posture."
    )

    rec.append("## Prioritization: where to invest first")

    if active_risks and risk_ranking:
        rec.append(
            "Based on economic impact analysis, investment should be concentrated on "
            "the following risks in order of priority:"
        )
        for i, entry in enumerate(risk_ranking[:3], 1):
            lvl = _LEVEL_EN.get(entry["risk_level"], entry["risk_level"])
            rec.append(
                f"  {i}. {entry['name']}  —  expected loss {entry['expected_loss_k']}K  [{lvl}]"
            )
        rec.append(
            "Improving controls on these risks delivers the greatest reduction in total "
            "portfolio loss. Remaining risks should be addressed in a subsequent phase "
            "once primary mitigations are confirmed effective."
        )
    else:
        rec.append(
            "Risk prioritization requires active risks to be defined. "
            "Activate relevant risks in the assessment to generate a prioritized action list."
        )

    rec.append("## Planning assumptions and limitations")

    rec.append(
        "These estimates are based on a Monte Carlo simulation with controlled uncertainty. "
        "Results represent the likely range of outcomes — they are not accounting forecasts. "
        "Material changes to the risk environment (new threats, regulatory changes, "
        "organizational restructuring) would warrant a revised assessment."
    )

    rec.append(
        f"The P90 exposure of {portfolio['p90_exposure_k']}K under the current posture should "
        f"be treated as a financial planning ceiling — a conservative buffer against adverse "
        f"scenarios. Organizations with low risk tolerance should ensure this amount is "
        f"available as a contingency reserve."
    )

    rec.append(
        "Investment decisions should be revisited on a regular cycle (at minimum annually) "
        "to reflect changes in the risk profile, control effectiveness, and strategic priorities."
    )

    sections["5. Recommendations"] = rec

    return sections
