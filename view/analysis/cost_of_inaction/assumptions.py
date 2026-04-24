"""
Cost of Inaction – Assumptions

This module defines the explicit assumptions used in the
relative cost-of-inaction analysis.

IMPORTANT:
- All values are normalized and expressed relative to K.
- No real financial figures are assumed.
- The goal is decision support, not accounting precision.
"""

# ==========================================================
# CORE CONCEPT
# ==========================================================

# K represents the normalized annual cybersecurity investment
# required to adequately cover the organization's current risk profile.
#
# K is NOT:
# - company revenue
# - IT budget
# - profit
#
# K IS:
# - a reference unit for relative comparison
# - scalable to any organization size
K_UNIT = 1.0


# ==========================================================
# TIME HORIZON
# ==========================================================

# Analysis horizon in years.
# Long enough to observe compounding risk effects,
# short enough to remain actionable.
TIME_HORIZON_YEARS = 3


# ==========================================================
# LOSS MULTIPLIER ASSUMPTIONS
# ==========================================================

# Baseline multiplier applied to residual risk
# to estimate expected relative loss.
#
# Interpretation:
# For each unit of residual risk, the organization
# is exposed to a multiple of K in expected losses.
BASE_LOSS_MULTIPLIER = 1.0


# ==========================================================
# SEVERITY ESCALATION (continuous)
# ==========================================================

# Severity is computed as a smooth power curve over normalized residual risk,
# from SEVERITY_SCALE_MIN (negligible risk) to SEVERITY_SCALE_MAX (worst case).
# This replaces the previous discrete level-multiplier lookup and eliminates
# abrupt jumps at level boundaries.
#
# Formula: severity = MIN + (MAX - MIN) × normalized_risk ^ EXPONENT
#
# EXPONENT > 1 → convex curve: severity stays moderate until risk is high,
# then escalates sharply.
SEVERITY_SCALE_MIN = 0.5
SEVERITY_SCALE_MAX = 3.0
SEVERITY_CURVE_EXPONENT = 1.8


# ==========================================================
# MINIMUM MATERIALITY THRESHOLD
# ==========================================================

# Very low residual risks below this threshold are considered
# economically negligible in relative terms.
MIN_EFFECTIVE_RISK = 0.5


# ==========================================================
# MODEL SCOPE LIMITS
# ==========================================================

# Upper bound to prevent unrealistic runaway estimates.
# This is a safety cap, not a prediction.
MAX_RELATIVE_LOSS = 10 * K_UNIT
# ==========================================================
# PROBABILITY NORMALIZATION
# ==========================================================

# Maximum possible residual risk score.
# Used to normalize residual risk into a probability proxy.
MAX_RESIDUAL_RISK_SCORE = 25.0

# Exponent for the probability proxy power curve.
#
# EXPONENT > 1 → convex: low residual risk yields a much lower probability
# proxy than a linear mapping would, making low risks genuinely negligible.
# EXPONENT = 1 → reverts to the previous linear mapping.
#
# Example at EXPONENT = 1.6:
#   residual=5  (BAJO)     → proxy ≈ 0.07   (vs 0.20 linear)
#   residual=10 (MEDIO)    → proxy ≈ 0.25   (vs 0.40 linear)
#   residual=15 (ALTO)     → proxy ≈ 0.48   (vs 0.60 linear)
#   residual=20 (CRÍTICO)  → proxy ≈ 0.73   (vs 0.80 linear)
PROBABILITY_CURVE_EXPONENT = 1.6


# ==========================================================
# RISK CORRELATION / ACCUMULATION
# ==========================================================

# Additional loss factor applied when multiple significant risks coexist.
# This reflects organizational overload and cascading failures.
RISK_CORRELATION_FACTOR = 0.15


# ==========================================================
# MONTE CARLO SIMULATION
# ==========================================================

# Number of iterations per scenario.
# 300 iterations balances stability of the mean with runtime.
SIMULATION_ITERATIONS = 300

# Relative noise applied to the probability axis on each iteration.
# Each risk's adjusted residual is multiplied by Uniform(1−δ, 1+δ).
# Probability is harder to estimate precisely → wider band.
SIMULATION_PROBABILITY_NOISE = 0.15   # ±15 %

# Relative noise applied to the impact axis on each iteration.
# Each risk's adjusted impact values are multiplied by Uniform(1−δ, 1+δ).
SIMULATION_IMPACT_NOISE = 0.10        # ±10 %

# Fixed seed for the RNG so dashboard results are reproducible.
# Set to None to get a different result on every run.
SIMULATION_SEED: int = 42
