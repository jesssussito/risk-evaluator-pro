"""
Cost of Inaction – Theoretical Model

Core loss model: non-linear, normalized, unitless.
All outputs are expressed in multiples of K.

Non-linearity is introduced at three points:

  1. Probability proxy  — power curve over residual risk score.
     Low risks have a disproportionately lower probability of materializing
     than a linear mapping would suggest.

  2. Impact normalization — power curve per impact dimension.
     High impact scores (4–5) dominate; low scores (1–2) are genuinely
     negligible rather than just "less bad".

  3. Severity escalation — smooth power curve from SEVERITY_SCALE_MIN to
     SEVERITY_SCALE_MAX anchored to the residual risk value.
     Replaces the previous discrete level-multiplier lookup, which caused
     abrupt 2× jumps at level boundaries (e.g. 9.99 → 10.01).
"""

from .assumptions import (
    BASE_LOSS_MULTIPLIER,
    MIN_EFFECTIVE_RISK,
    MAX_RELATIVE_LOSS,
    MAX_RESIDUAL_RISK_SCORE,
    RISK_CORRELATION_FACTOR,
    PROBABILITY_CURVE_EXPONENT,
    SEVERITY_SCALE_MIN,
    SEVERITY_SCALE_MAX,
    SEVERITY_CURVE_EXPONENT,
)
from .weights import (
    IMPACT_DIMENSION_WEIGHTS,
    MAX_IMPACT_SCORE,
    CONTROL_EFFECTIVENESS_DAMPING,
    IMPACT_AGGREGATION_METHOD,
    IMPACT_CURVE_EXPONENT,
)


# ==========================================================
# IMPACT NORMALIZATION
# ==========================================================

def normalize_impact(value: float) -> float:
    """
    Normalize an impact score to [0, 1] with a convex power curve.

    The curve ensures that high impact scores (4–5) dominate the model
    while low scores contribute proportionally less than a linear mapping.
    """
    if value <= 0:
        return 0.0
    normalized = min(value / MAX_IMPACT_SCORE, 1.0)
    return normalized ** IMPACT_CURVE_EXPONENT


# ==========================================================
# PROBABILITY PROXY
# ==========================================================

def residual_risk_to_probability(residual_risk: float) -> float:
    """
    Convert residual risk score to a probability proxy in [0, 1].

    A convex power curve (EXPONENT > 1) ensures low-risk items have
    a much lower probability proxy than a linear mapping implies —
    aligning the model with the intuition that BAJO risks rarely
    produce material losses.
    """
    if residual_risk <= 0:
        return 0.0
    normalized = min(residual_risk / MAX_RESIDUAL_RISK_SCORE, 1.0)
    return normalized ** PROBABILITY_CURVE_EXPONENT


# ==========================================================
# IMPACT AGGREGATION
# ==========================================================

def aggregate_impacts(financial: float,
                      operational: float,
                      reputational: float) -> float:
    """
    Aggregate weighted impact dimensions into a single factor.
    Each dimension is individually normalized with the power curve
    before weighting.
    """
    weighted = {
        "financial":     normalize_impact(financial)     * IMPACT_DIMENSION_WEIGHTS["financial"],
        "operational":   normalize_impact(operational)   * IMPACT_DIMENSION_WEIGHTS["operational"],
        "reputational":  normalize_impact(reputational)  * IMPACT_DIMENSION_WEIGHTS["reputational"],
    }

    if IMPACT_AGGREGATION_METHOD == "max_dominant":
        return max(weighted.values())

    total_weight = sum(IMPACT_DIMENSION_WEIGHTS.values())
    return sum(weighted.values()) / total_weight


# ==========================================================
# SEVERITY ESCALATION
# ==========================================================

def _smooth_severity(residual_risk: float) -> float:
    """
    Continuous severity multiplier derived from the residual risk value.

    Formula: SEVERITY_SCALE_MIN + (MAX - MIN) × normalized ^ EXPONENT

    With EXPONENT > 1 the curve is convex: severity stays near its minimum
    for low risks and rises steeply only once the risk is genuinely high.
    No discrete thresholds → no jumps at level boundaries.
    """
    normalized = min(residual_risk / MAX_RESIDUAL_RISK_SCORE, 1.0)
    return SEVERITY_SCALE_MIN + (SEVERITY_SCALE_MAX - SEVERITY_SCALE_MIN) * (normalized ** SEVERITY_CURVE_EXPONENT)


# ==========================================================
# RELATIVE LOSS MODEL
# ==========================================================

def estimate_relative_loss(residual_risk: float,
                           financial_impact: float,
                           operational_impact: float,
                           reputational_impact: float,
                           control_effectiveness: float = 0.0) -> float:
    """
    Estimate relative economic loss for a single risk.

    All three non-linear components are combined:
      · probability proxy   — power curve over residual_risk
      · impact factor       — power-curve-normalized weighted aggregate
      · severity multiplier — smooth escalation from MIN to MAX

    Returns:
        Relative loss in multiples of K.
    """
    if residual_risk < MIN_EFFECTIVE_RISK:
        return 0.0

    probability      = residual_risk_to_probability(residual_risk)
    impact_factor    = aggregate_impacts(financial_impact, operational_impact, reputational_impact)
    severity         = _smooth_severity(residual_risk)

    mitigation_factor = 1.0 - (control_effectiveness * CONTROL_EFFECTIVENESS_DAMPING)
    mitigation_factor = max(mitigation_factor, 0.1)

    relative_loss = (
        probability
        * impact_factor
        * severity
        * BASE_LOSS_MULTIPLIER
        * mitigation_factor
    )

    return min(relative_loss, MAX_RELATIVE_LOSS)


# ==========================================================
# PORTFOLIO CORRELATION
# ==========================================================

# Soft ceiling on amplification. Does not change behavior for typical
# portfolios (n ≤ 7 at RISK_CORRELATION_FACTOR = 0.15 stays below 2.0),
# but prevents runaway multipliers for very large risk counts.
# Adjust here if organizational context warrants a wider or tighter cap.
_MAX_AMPLIFICATION: float = 2.0


def apply_correlation_effect(total_loss: float, risk_count: int) -> float:
    """
    Scale total portfolio loss upward to reflect accumulation effects
    when multiple risks coexist simultaneously.

    Rationale
    ---------
    When several risks materialize in the same period the organization faces
    compounded strain: response capacity is divided, costs overlap, and
    cascading failures become more likely. A single-risk expected loss does
    not capture this — summing individual losses underestimates the aggregate.
    This function applies a linear amplification to the sum to correct for it.

    Formula
    -------
        factor        = max(RISK_CORRELATION_FACTOR, 0.0)   # coherence guard
        amplification = 1 + (n − 1) × factor
        amplification = min(amplification, _MAX_AMPLIFICATION)
        output        = total_loss × amplification

    Behavior at RISK_CORRELATION_FACTOR = 0.15
    ------------------------------------------
        n = 1  →  amplification = 1.00  (no adjustment)
        n = 2  →  amplification = 1.15  (+15 %)
        n = 3  →  amplification = 1.30  (+30 %)
        n = 5  →  amplification = 1.60  (+60 %)
        n = 7  →  amplification = 1.90  (+90 %)
        n ≥ 8  →  amplification = 2.00  (capped)

    Coherence conditions
    --------------------
    · RISK_CORRELATION_FACTOR must be ≥ 0. A negative value would reduce
      aggregate loss as n grows, which contradicts the physical interpretation
      (more simultaneous risks → more strain, not less). The guard below
      clamps the factor to 0 if misconfigured, preserving the invariant that
      apply_correlation_effect(x, n) ≥ x for all valid inputs.
    · The _MAX_AMPLIFICATION cap prevents unrealistic multiples for large
      portfolios where the linear formula grows without bound.

    Configurable parameter
    ----------------------
    RISK_CORRELATION_FACTOR is defined in assumptions.py.
    Practical range: [0.05, 0.25]. Set to 0 to disable the effect entirely.
    """
    if risk_count <= 1:
        return total_loss

    # Coherence guard: a negative factor would reduce aggregate loss,
    # contradicting the accumulation-effect interpretation.
    factor = max(RISK_CORRELATION_FACTOR, 0.0)

    amplification = 1.0 + (risk_count - 1) * factor
    amplification = min(amplification, _MAX_AMPLIFICATION)

    return total_loss * amplification
