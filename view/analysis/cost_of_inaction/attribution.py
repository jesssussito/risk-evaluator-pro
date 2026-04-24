"""
Cost of Inaction – Risk Attribution

This module identifies which risks contribute most
to the expected cost of inaction.
"""

from typing import List, Dict

from .theorical_model import estimate_relative_loss


def rank_risks_by_loss(assessment) -> List[Dict]:
    """
    Rank active risks by their contribution to relative loss.
    """

    contributions = []

    for cr in assessment.get_active_risks():
        residual = cr.calculate_residual_risk()

        loss = estimate_relative_loss(
            residual_risk=residual,
            financial_impact=cr.custom_impact_financial,
            operational_impact=cr.custom_impact_operational,
            reputational_impact=cr.custom_impact_reputational,
            control_effectiveness=cr.get_control_coverage() / 100,
        )

        contributions.append({
            "risk": cr.base_risk.name,
            "relative_loss_k": round(loss, 2),
        })

    return sorted(
        contributions,
        key=lambda x: x["relative_loss_k"],
        reverse=True,
    )
