from controller.csv_loader import (
    load_risk_types,
    load_controls,
    load_risks,
    load_risk_base_scores,
    load_risk_control_map,
)
from models.companyRisk import CompanyAssessment



class AppController:
    def __init__(self):
        self.risk_types = {}
        self.controls = {}
        self.risks = {}
        self.company_assessment = None
   
    def load_all_data(self):
        # 1. Cargar tipos de riesgo
        self.risk_types = load_risk_types("data/risk_types.csv")
        if not self.risk_types:
            raise RuntimeError("No risk was charged")

        # 2. Cargar controles
        self.controls = load_controls("data/controls.csv")
        if not self.controls:
            raise RuntimeError("No controls loaded")

        # 3. Cargar riesgos
        self.risks = load_risks("data/risks.csv", self.risk_types)
        if not self.risks:
            raise RuntimeError("No risk was charged")

        # 4. Cargar scores base
        load_risk_base_scores("data/risk_base_scores.csv", self.risks)
        
        # Comprobación: todos los riesgos deben tener probabilidad base válida
        for r in self.risks.values():
            if r.base_probability is None:
                raise RuntimeError(
                    f"Risk {r.risk_id} without base probability set"
                )
        self.company_assessment = CompanyAssessment(self.risks)

        # 5. Cargar relación riesgo–control
        load_risk_control_map(
            "data/risk_control_map.csv",
            self.risks,
            self.controls,
        )

        # Comprobación: todos los riesgos deben tener al menos un control
        for r in self.risks.values():
            if not r.controls:
                raise RuntimeError(
                    f"Risk {r.risk_id} without controls set"
                )
   
    def run(self):
        view = GuiView(self)
        view.run()

    def generate_cost_of_inaction_report(self, output_path: str):
        from view.analysis.cost_of_inaction.calculator import run_cost_of_inaction_analysis
        from view.analysis.cost_of_inaction.report import build_report_text
        from view.analysis.cost_of_inaction.pdf_export import export_report_to_pdf

        results = run_cost_of_inaction_analysis(self.company_assessment)
        report = build_report_text(self.company_assessment, results)
        export_report_to_pdf(report, output_path)

