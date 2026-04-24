from typing import List, Dict


# -------------------------
# Risk Type
# -------------------------

class RiskType:
    def __init__(self, type_id: str, name: str, description: str):
        if not type_id:
            raise ValueError("type_id no puede estar vacío")
        if not name:
            raise ValueError("name no puede estar vacío")

        self.type_id = type_id
        self.name = name
        self.description = description

    def __eq__(self, other):
        return isinstance(other, RiskType) and self.type_id == other.type_id

    def __hash__(self):
        return hash(self.type_id)

    def __repr__(self):
        return f"RiskType({self.name})"


# -------------------------
# Control
# -------------------------

class Control:
    def __init__(self, control_id: str, name: str, base_effectiveness: float,description=""):
        if not control_id:
            raise ValueError("control_id no puede estar vacío")
        if not name:
            raise ValueError("name no puede estar vacío")
        if not 0.0 <= base_effectiveness <= 1.0:
            raise ValueError("La eficacia base debe estar entre 0.0 y 1.0")

        self.control_id = control_id
        self.name = name
        self.base_effectiveness = base_effectiveness
        self.adjusted_effectiveness = base_effectiveness
        self.description = description

    def set_effectiveness(self, value: float):
        if not 0.0 <= value <= 1.0:
            raise ValueError("La eficacia debe estar entre 0.0 y 1.0")
        self.adjusted_effectiveness = value

    def reset_effectiveness(self):
        self.adjusted_effectiveness = self.base_effectiveness

    def __eq__(self, other):
        return isinstance(other, Control) and self.control_id == other.control_id

    def __hash__(self):
        return hash(self.control_id)

    def __repr__(self):
        return f"Control({self.name}, eff={self.adjusted_effectiveness})"


# -------------------------
# Risk
# -------------------------

class Risk:
    SCALE_MIN: int = 1
    SCALE_MAX: int = 5

    # Mantenidos por compatibilidad con código existente que los importe
    IMPACT_RANGE = range(SCALE_MIN, SCALE_MAX + 1)
    PROBABILITY_RANGE = range(SCALE_MIN, SCALE_MAX + 1)

    DEFAULT_IMPACT_WEIGHTS: Dict[str, float] = {
        "financial": 0.4,
        "operational": 0.3,
        "reputational": 0.3
    }

    def __init__(
        self,
        risk_id: str,
        name: str,
        risk_type: RiskType,
        base_probability: int,
        base_impact_financial: int,
        base_impact_operational: int,
        base_impact_reputational: int,
        impact_weights: Dict[str, float] = None
    ):
        if not risk_id:
            raise ValueError("risk_id no puede estar vacío")
        if not name:
            raise ValueError("name no puede estar vacío")
        if not isinstance(risk_type, RiskType):
            raise ValueError("risk_type debe ser una instancia de RiskType")

        self.risk_id = risk_id
        self.name = name
        self.risk_type = risk_type

        self._validate_probability(base_probability)
        self._validate_impact(base_impact_financial)
        self._validate_impact(base_impact_operational)
        self._validate_impact(base_impact_reputational)

        # Valores base
        self.base_probability = base_probability
        self.base_impact_financial = base_impact_financial
        self.base_impact_operational = base_impact_operational
        self.base_impact_reputational = base_impact_reputational

        # Valores ajustados
        self.adjusted_probability = base_probability
        self.adjusted_impact_financial = base_impact_financial
        self.adjusted_impact_operational = base_impact_operational
        self.adjusted_impact_reputational = base_impact_reputational

        self.impact_weights = impact_weights or self.DEFAULT_IMPACT_WEIGHTS.copy()
        self._validate_weights(self.impact_weights)

        # Cada riesgo tiene SUS propias instancias de control
        self.controls: Dict[str, Control] = {}

    # ---------- Validaciones ----------

    def _validate_probability(self, value) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError(
                f"Probabilidad debe ser numérica, recibido: {type(value).__name__}"
            )
        if not (self.SCALE_MIN <= value <= self.SCALE_MAX):
            raise ValueError(
                f"Probabilidad fuera de rango ({self.SCALE_MIN}–{self.SCALE_MAX}): {value}"
            )

    def _validate_impact(self, value) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError(
                f"Impacto debe ser numérico, recibido: {type(value).__name__}"
            )
        if not (self.SCALE_MIN <= value <= self.SCALE_MAX):
            raise ValueError(
                f"Impacto fuera de rango ({self.SCALE_MIN}–{self.SCALE_MAX}): {value}"
            )

    def _validate_weights(self, weights: Dict[str, float]) -> None:
        required = set(self.DEFAULT_IMPACT_WEIGHTS)
        missing = required - set(weights)
        if missing:
            raise ValueError(f"Faltan claves de peso requeridas: {missing}")
        if not all(w >= 0 for w in weights.values()):
            raise ValueError("Los pesos no pueden ser negativos")
        if abs(sum(weights.values()) - 1.0) > 0.01:
            raise ValueError("Los pesos deben sumar 1.0")

    # ---------- Ajustes por usuario ----------

    def adjust_probability(self, value: int):
        self._validate_probability(value)
        self.adjusted_probability = value

    def adjust_impact(self, financial: int, operational: int, reputational: int):
        self._validate_impact(financial)
        self._validate_impact(operational)
        self._validate_impact(reputational)

        self.adjusted_impact_financial = financial
        self.adjusted_impact_operational = operational
        self.adjusted_impact_reputational = reputational

    # ---------- Controles ----------

    def add_control(self, control: Control):
        """
        Asocia un control del catálogo al riesgo.
        NO se crea una nueva instancia.
        """
        self.controls[control.control_id] = control

    # ---------- Cálculos ----------

    def inherent_risk(self) -> float:
        weighted_impact = (
            self.adjusted_impact_financial * self.impact_weights["financial"] +
            self.adjusted_impact_operational * self.impact_weights["operational"] +
            self.adjusted_impact_reputational * self.impact_weights["reputational"]
        )
        return self.adjusted_probability * weighted_impact

    def residual_risk(self) -> float:
        """Modelo multiplicativo: cada control reduce el riesgo remanente."""
        remaining = 1.0
        for c in self.controls.values():
            remaining *= (1.0 - c.adjusted_effectiveness)
        return self.inherent_risk() * remaining

    # ---------- Normalización (base para extensión probabilística) ----------

    def normalized_probability(self) -> float:
        """
        Probabilidad ajustada normalizada a [0.0, 1.0].
        Permite sustituir la escala discreta 1–5 por una distribución continua
        sin cambiar los cálculos downstream que consuman este valor.
        """
        scale = self.SCALE_MAX - self.SCALE_MIN
        return (self.adjusted_probability - self.SCALE_MIN) / scale

    def normalized_impact(self) -> float:
        """
        Impacto ponderado normalizado a [0.0, 1.0].
        Mismo propósito que normalized_probability(): desacopla la escala
        interna de cualquier modelo probabilístico futuro.
        """
        weighted = (
            self.adjusted_impact_financial   * self.impact_weights["financial"] +
            self.adjusted_impact_operational * self.impact_weights["operational"] +
            self.adjusted_impact_reputational * self.impact_weights["reputational"]
        )
        scale = self.SCALE_MAX - self.SCALE_MIN
        return (weighted - self.SCALE_MIN) / scale

    # ---------- Clasificación ----------

    def risk_level(self) -> str:
        value = self.residual_risk()

        if value < 0:
            raise ValueError("El riesgo residual no puede ser negativo")
        if value > 25:
            raise ValueError("Riesgo fuera de rango esperado")

        if value >= 15:
            return "CRÍTICO"
        elif value >= 10:
            return "ALTO"
        elif value >= 5:
            return "MEDIO"
        else:
            return "BAJO"

    def __eq__(self, other):
        return isinstance(other, Risk) and self.risk_id == other.risk_id

    def __hash__(self):
        return hash(self.risk_id)

    def __repr__(self):
        return f"Risk({self.name}, type={self.risk_type.name})"


# -------------------------
# Risk Assessment
# -------------------------

class RiskAssessment:
    def __init__(self, risks: List[Risk]):
        self.risks = list(risks)  # copia defensiva

    def sort_by_residual_risk(self) -> List[Risk]:
        return sorted(
            self.risks,
            key=lambda r: r.residual_risk(),
            reverse=True
        )

    def filter_by_type(self, risk_type: RiskType) -> List[Risk]:
        return [r for r in self.risks if r.risk_type == risk_type]
