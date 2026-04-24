class CompanyRisk:
    # max(probabilidad) × max(impacto_avg) = 5 × 5
    _INHERENT_SCALE_MAX: float = 25.0

    def __init__(self, base_risk):
        self.base_risk = base_risk  # Risk del catálogo

        # Selección del usuario
        self.active = False

        # Ajustes del usuario (inicialmente iguales al catálogo)
        self.custom_probability = base_risk.base_probability
        self.custom_impact_financial = base_risk.base_impact_financial
        self.custom_impact_operational = base_risk.base_impact_operational
        self.custom_impact_reputational = base_risk.base_impact_reputational

        # Controles realmente existentes en la empresa
        self.enabled_controls = {}

    # ---------- Estado ----------
    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def is_active(self) -> bool:
        return self.active

    # ---------- Ajustes ----------
    def set_custom_scores(self, p, ifin, iop, irep):
        self.custom_probability = p
        self.custom_impact_financial = ifin
        self.custom_impact_operational = iop
        self.custom_impact_reputational = irep

    def calculate_inherent_risk(self) -> float:
        """
        Calcula el riesgo inherente (sin controles).
        Usa los pesos definidos en el catálogo: financiero=0.4, operacional=0.3, reputacional=0.3.
        """
        weights = self.base_risk.impact_weights
        weighted_impact = (
            self.custom_impact_financial    * weights["financial"] +
            self.custom_impact_operational  * weights["operational"] +
            self.custom_impact_reputational * weights["reputational"]
        )
        return self.custom_probability * weighted_impact
    
    def _remaining_factor(self) -> float:
        """
        Factor multiplicativo conjunto de todos los controles activos,
        con penalización sublineal por número de controles.

        Base: modelo multiplicativo  ∏(1 − eᵢ)
        Penalización: se eleva el producto a 1/√n, reduciendo la efectividad
        marginal a medida que crece n.

            n=1 → exponente 1.0  (sin cambio)
            n=4 → exponente 0.50 (raíz cuadrada del producto)
            n=9 → exponente 0.33 (raíz cúbica del producto)

        El factor resultante es siempre > producto_puro para n > 1,
        devolviendo más riesgo residual y evitando la sobreestimación
        cuando se acumulan muchos controles.
        """
        n = len(self.enabled_controls)
        if n == 0:
            return 1.0

        factor = 1.0
        for control in self.enabled_controls.values():
            factor *= (1.0 - control.base_effectiveness)

        if n > 1:
            factor = factor ** (1.0 / n ** 0.5)

        return factor

    def calculate_residual_risk(self) -> float:
        """
        Calcula el riesgo residual con rendimientos decrecientes y
        penalización por saturación de controles.

            residual = inherente × _remaining_factor()
        """
        return self.calculate_inherent_risk() * self._remaining_factor()
    
    @staticmethod
    def risk_level(value: float) -> str:
        """
        Traduce un valor numérico de riesgo a nivel cualitativo.
        """
        if value < 5:
            return "BAJO"
        elif value < 10:
            return "MEDIO"
        elif value < 15:
            return "ALTO"
        else:
            return "CRÍTICO"
        
    def get_risk_reduction(self) -> float:
        return self.calculate_inherent_risk() - self.calculate_residual_risk()

    def get_risk_reduction_percent(self) -> float:
        inh = self.calculate_inherent_risk()
        if inh == 0:
            return 0.0
        return (1 - self.calculate_residual_risk() / inh) * 100
    def get_control_coverage(self) -> float:
        """
        Porcentaje de cobertura efectiva, consistente con calculate_residual_risk().
        """
        return (1.0 - self._remaining_factor()) * 100
    def get_risk_score(self) -> float:
        """
        Score normalizado 0–100 anclado al máximo teórico de la escala.

        Uso canónico para comparar riesgos entre sí o mostrar en dashboard.
        El denominador es _INHERENT_SCALE_MAX para evitar la constante mágica 25.
        """
        return (self.calculate_residual_risk() / self._INHERENT_SCALE_MAX) * 100

    def get_normalized_residual_risk(self) -> float:
        """Riesgo residual normalizado a escala 0–100. Delegación a get_risk_score()."""
        return self.get_risk_score()

    def get_risk_volatility(self) -> float:
        """
        Volatilidad aproximada del riesgo residual.

        Combina dos factores:
          · Asimetría del perfil de impacto (desviación estándar entre dimensiones).
            Un riesgo con impactos [1, 1, 5] es más imprevisible que [3, 3, 3].
          · Fracción expuesta sin cobertura de controles.
            Cuanto más expuesto, más se materializa esa asimetría.

        Rango orientativo: [0.0, ~1.88]
        """
        impacts = [
            self.custom_impact_financial,
            self.custom_impact_operational,
            self.custom_impact_reputational,
        ]
        mean = sum(impacts) / 3
        std_dev = (sum((x - mean) ** 2 for x in impacts) / 3) ** 0.5

        uncovered = 1.0 - self.get_control_coverage() / 100
        return std_dev * uncovered

    def get_uncertainty_margin(self) -> float:
        """
        Margen de incertidumbre del riesgo residual.

        Responde: "¿cuánto cambiaría el riesgo residual si nuestra estimación
        de probabilidad estuviera desviada ±0.5 puntos?"

        0.5 es la resolución natural de la escala discreta 1–5: cada nivel
        representa un rango continuo de anchura 1, luego el error típico de
        redondeo es ±0.5.

        Derivación:
            ∂(residual)/∂p = impacto_ponderado × factor_restante
            margen ≈ 0.5 × impacto_ponderado × factor_restante
        """
        inherent = self.calculate_inherent_risk()
        if inherent == 0 or self.custom_probability == 0:
            return 0.0

        weighted_impact = inherent / self.custom_probability
        remaining_factor = self.calculate_residual_risk() / inherent
        return 0.5 * weighted_impact * remaining_factor




    




class CompanyAssessment:
    def __init__(self, catalog_risks: dict):
        self.company_risks = {
            r_id: CompanyRisk(risk)
            for r_id, risk in catalog_risks.items()
        }

    # ---------- API para la vista / controlador ----------
    def set_risk_active(self, risk_id: str, active: bool):
        if risk_id not in self.company_risks:
            raise ValueError(f"Riesgo inexistente: {risk_id}")

        if active:
            self.company_risks[risk_id].activate()
        else:
            self.company_risks[risk_id].deactivate()

    def get_active_risks(self):
        return [
            cr for cr in self.company_risks.values()
            if cr.is_active()
        ]
    
    def get_risk_ranking(self, residual: bool = True):
        """
        Devuelve los riesgos activos ordenados por riesgo (residual o inherente).
        """
        active = self.get_active_risks()

        def risk_value(cr):
            return (
                cr.calculate_residual_risk()
                if residual
                else cr.calculate_inherent_risk()
            )

        return sorted(active, key=risk_value, reverse=True)
    
    def get_summary(self):
        """
        Métricas globales de riesgo residual.
        """
        values = [
            cr.calculate_residual_risk()
            for cr in self.get_active_risks()
        ]

        if not values:
            return {
                "count": 0,
                "avg": 0.0,
                "max": 0.0,
                "min": 0.0,
            }

        return {
            "count": len(values),
            "avg": sum(values) / len(values),
            "max": max(values),
            "min": min(values),
        }

    def get_company_risk_score(self) -> float:
        """
        Score global de riesgo de la empresa (media residual).
        """
        risks = self.get_active_risks()
        if not risks:
            return 0.0

        return sum(
            cr.calculate_residual_risk() for cr in risks
        ) / len(risks)
    
    def count_risks_by_level(self) -> dict:
        """
        Número de riesgos por nivel residual.
        """
        result = {"BAJO": 0, "MEDIO": 0, "ALTO": 0, "CRÍTICO": 0}

        for cr in self.get_active_risks():
            level = cr.risk_level(cr.calculate_residual_risk())
            result[level] += 1

        return result
    def get_risk_by_type(self) -> dict:
        """
        Riesgo residual agregado por tipo de riesgo.
        """
        result = {}

        for cr in self.get_active_risks():
            t = cr.base_risk.risk_type.name
            result.setdefault(t, 0.0)
            result[t] += cr.calculate_residual_risk()

        return result
    def get_unacceptable_risks(self):
        """
        Devuelve los riesgos con nivel ALTO o CRÍTICO.
        """
        result = []

        for cr in self.get_active_risks():
            value = cr.calculate_residual_risk()
            level = cr.risk_level(value)
            if level in ("ALTO", "CRÍTICO"):
                result.append(cr)

        return result
    def get_poorly_mitigated_risks(self):
        """
        Riesgos cuyo nivel residual sigue siendo ALTO o CRÍTICO
        y cuya reducción respecto al inherente es baja.
        """
        result = []

        for cr in self.get_active_risks():
            inherent = cr.calculate_inherent_risk()
            residual = cr.calculate_residual_risk()
            level = cr.risk_level(residual)

            if inherent == 0:
                continue

            reduction = inherent - residual

            # Definición ERM: alto residual + mitigación débil
            if level in ("ALTO", "CRÍTICO") and reduction < 1.0:
                result.append(cr)

        return result
    
    def get_security_maturity_index(self) -> float:
        """
        Índice de madurez basado en reducción media de riesgo.
        """
        risks = self.get_active_risks()
        if not risks:
            return 0.0

        reductions = [
            cr.get_risk_reduction_percent()
            for cr in risks
        ]

        return sum(reductions) / len(reductions)
    def get_kpis(self) -> dict:
        """
        Devuelve métricas ejecutivas agregadas.
        """
        active = self.get_active_risks()

        if not active:
            return {
                "max": 0.0,
                "avg": 0.0,
                "critical_count": 0,
                "reduction_pct": 0.0,
            }

        residuals = [cr.calculate_residual_risk() for cr in active]
        inherents = [cr.calculate_inherent_risk() for cr in active]

        max_residual = max(residuals)
        avg_residual = sum(residuals) / len(residuals)

        critical_count = sum(
            1 for r in residuals
            if CompanyRisk.risk_level(r) == "CRÍTICO"
        )

        avg_inherent = sum(inherents) / len(inherents)

        reduction_pct = 0.0
        if avg_inherent > 0:
            reduction_pct = (1 - avg_residual / avg_inherent) * 100

        return {
            "max": max_residual,
            "avg": avg_residual,
            "critical_count": critical_count,
            "reduction_pct": reduction_pct,
        }
    def get_priority_risks(self):
        """
        Riesgos ALTO que requieren seguimiento prioritario
        pero no están fuera de apetito ni mal mitigados.
        """
        result = []

        unacceptable = set(self.get_unacceptable_risks())
        poorly_mitigated = set(self.get_poorly_mitigated_risks())

        for cr in self.get_active_risks():
            if cr in unacceptable or cr in poorly_mitigated:
                continue

            residual = cr.calculate_residual_risk()
            level = cr.risk_level(residual)

            if level == "ALTO":
                result.append(cr)

        return result

    def get_portfolio_volatility(self) -> float:
        """
        Volatilidad media del portafolio: promedio de get_risk_volatility()
        sobre todos los riesgos activos.
        """
        risks = self.get_active_risks()
        if not risks:
            return 0.0
        return sum(cr.get_risk_volatility() for cr in risks) / len(risks)

    def get_portfolio_uncertainty(self) -> dict:
        """
        Resumen de incertidumbre del portafolio activo.

        Claves devueltas:
          · avg_margin     — margen de incertidumbre medio
          · max_margin     — margen máximo (peor caso)
          · most_uncertain — CompanyRisk con mayor margen
        """
        risks = self.get_active_risks()
        if not risks:
            return {"avg_margin": 0.0, "max_margin": 0.0, "most_uncertain": None}

        margins = [(cr, cr.get_uncertainty_margin()) for cr in risks]
        avg_margin = sum(m for _, m in margins) / len(margins)
        max_margin = max(m for _, m in margins)
        most_uncertain = max(margins, key=lambda x: x[1])[0]

        return {
            "avg_margin": avg_margin,
            "max_margin": max_margin,
            "most_uncertain": most_uncertain,
        }

