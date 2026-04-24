"""
Cost of Inaction – Investment Scenarios

This module defines strategic cybersecurity investment scenarios.
All values are expressed relative to K.
"""

# ==========================================================
# SCENARIO DEFINITIONS
# ==========================================================

SCENARIOS = {
    "no_investment": {
        "label": "No Investment",
        "description": (
            "No additional cybersecurity investment. "
            "The organization maintains its current risk posture."
        ),
        # Investment expressed as a fraction of K
        "investment_k": 0.0,

        # Expected proportional reduction applied to probability proxy
        "probability_reduction": 0.0,

        # Expected proportional reduction applied to impact severity
        "impact_reduction": 0.0,
    },

    "partial_investment": {
        "label": "Partial Investment",
        "description": (
            "Targeted cybersecurity improvements focused on high-risk areas. "
            "Reduces likelihood but leaves structural exposure."
        ),
        # ~40% of the ideal investment
        "investment_k": 0.4,

        # Moderate reduction in probability
        "probability_reduction": 0.25,

        # Minor reduction in impact
        "impact_reduction": 0.10,
    },

    "strategic_investment": {
        "label": "Strategic Investment",
        "description": (
            "Comprehensive cybersecurity program aligned with the risk profile. "
            "Addresses both likelihood and impact across the organization."
        ),
        # Full reference investment
        "investment_k": 1.0,

        # Strong reduction in probability
        "probability_reduction": 0.55,

        # Significant reduction in impact
        "impact_reduction": 0.35,
    },
}
