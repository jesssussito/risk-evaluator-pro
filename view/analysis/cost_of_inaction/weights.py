"""
Cost of Inaction – Weights

This module defines relative weights used to estimate
the impact contribution of different risk dimensions.

Weights are normalized and unitless.
They express relative importance, not monetary value.
"""

# ==========================================================
# IMPACT DIMENSION WEIGHTS
# ==========================================================

# Relative contribution of each impact dimension
# to the overall loss model.
#
# Interpretation:
# A financial impact contributes more directly to loss,
# while reputational and operational impacts tend to
# propagate indirectly over time.
IMPACT_DIMENSION_WEIGHTS = {
    "financial": 1.0,
    "operational": 0.8,
    "reputational": 0.6,
}


# ==========================================================
# SEVERITY NORMALIZATION
# ==========================================================

# Maximum possible impact score per dimension.
# Used to normalize impact values into [0, 1].
MAX_IMPACT_SCORE = 5.0


# ==========================================================
# CONTROL EFFECTIVENESS WEIGHT
# ==========================================================

# Controls reduce loss less efficiently than they reduce risk,
# due to implementation gaps, human factors and residual exposure.
#
# This factor dampens the theoretical mitigation effect.
CONTROL_EFFECTIVENESS_DAMPING = 0.75


# ==========================================================
# IMPACT CURVE
# ==========================================================

# Exponent applied to each normalized impact dimension before weighting.
#
# EXPONENT > 1 → convex: low impact scores contribute far less than high ones,
# which aligns with the domain reality that impact=5 is not just "5× worse"
# than impact=1 but disproportionately more damaging.
# EXPONENT = 1 → reverts to the previous linear normalization.
#
# Example at EXPONENT = 1.5:
#   impact=1 → normalized ≈ 0.09   (vs 0.20 linear)
#   impact=3 → normalized ≈ 0.47   (vs 0.60 linear)
#   impact=5 → normalized  = 1.00  (unchanged)
IMPACT_CURVE_EXPONENT = 1.5


# ==========================================================
# AGGREGATION STRATEGY
# ==========================================================

# Method used to aggregate weighted impacts.
#
# Allowed values:
# - "weighted_average"
# - "max_dominant"
IMPACT_AGGREGATION_METHOD = "weighted_average"
