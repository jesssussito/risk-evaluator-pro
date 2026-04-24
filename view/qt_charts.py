from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel,QSizePolicy
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from models.companyRisk import CompanyRisk
import numpy as np
from matplotlib.lines import Line2D
from PySide6.QtCore import Signal
class InherentVsResidualChart(QWidget):
    """
    Gráfica de barras:
    Riesgo inherente vs riesgo residual por riesgo activo.

    RESPONSABILIDAD:
    - SOLO visualización
    - NO cálculos de negocio
    """
    
    def __init__(self, controller):
        super().__init__()

        self.controller = controller

        # ==================================================
        # LAYOUT DEL WIDGET
        # ==================================================
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        description = QLabel(
            "This chart compares the inherent risk level of each active risk "
            "against its residual risk after applying controls. "
            "Large gaps indicate strong mitigation, while small gaps highlight "
            "potentially ineffective or insufficient controls."
        )
        description.setWordWrap(True)
        description.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #bbb;
            }
        """)
        layout.addWidget(description)

        # ==================================================
        # TÍTULO
        # ==================================================
        title = QLabel("Inherent vs Residual Risk")
        title.setStyleSheet("font-size:14px; font-weight:bold;")
        layout.addWidget(title)

        # ==================================================
        # FIGURA MATPLOTLIB (CONTROLADA)
        # ==================================================
        self.figure = Figure(figsize=(7, 4))
        self.figure.tight_layout(pad=2.0)

        self.canvas = FigureCanvas(self.figure)

        # --- CONTROL DE TAMAÑO (CRÍTICO)
        self.canvas.setMinimumHeight(320)
        self.canvas.setMaximumHeight(320)
        self.canvas.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )
        self.insight_label = QLabel()
        self.insight_label.setWordWrap(True)
        self.insight_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #ddd;
                padding-top: 6px;
            }
        """)

        layout.addWidget(self.canvas)
        layout.addWidget(self.insight_label)

        self.refresh()

    # ==================================================
    # REFRESH
    # ==================================================

    def refresh(self):
        """
        Redibuja la gráfica usando el estado actual del modelo.
        """

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        active = sorted(
            self.controller.company_assessment.get_active_risks(),
            key=lambda cr: cr.calculate_residual_risk(),
            reverse=True,
        )
        TOP_N = 8  # configurable
        active = active[:TOP_N]
        if not active:
            ax.text(
                0.5,
                0.5,
                "No active risks",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            self.canvas.draw()
            return

        names = [cr.base_risk.name for cr in active]
        inherent = [cr.calculate_inherent_risk() for cr in active]
        residual = [cr.calculate_residual_risk() for cr in active]

        x = range(len(names))
        def level_color(value):
            level = CompanyRisk.risk_level(value)
            if level == "CRÍTICO":
                return "#c0392b"
            elif level == "ALTO":
                return "#e67e22"
            elif level == "MEDIO":
                return "#f1c40f"
            else:
                return "#2ecc71"
        ax.bar(
            x,
            inherent,
            label="Inherent",
            alpha=0.4,
            color=[level_color(v) for v in inherent],
        )

        ax.bar(
            x,
            residual,
            label="Residual",
            alpha=0.85,
            color=[level_color(v) for v in residual],
        )

        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha="right")

        ax.set_ylabel("Risk score")
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.4)

        self.figure.tight_layout()
        self.canvas.draw()
        # ==================================================
        # INSIGHT AUTOMÁTICO (LECTURA EJECUTIVA)
        # ==================================================
        if active:
            gaps = [
                inh - res
                for inh, res in zip(inherent, residual)
            ]

            avg_gap = sum(gaps) / len(gaps)

            if avg_gap >= 2.0:
                msg = (
                    "Overall, control measures are significantly reducing risk levels. "
                    "The mitigation strategy appears effective across most active risks."
                )
            elif avg_gap >= 1.0:
                msg = (
                    "Risk mitigation shows moderate effectiveness. "
                    "Some risks may require additional or stronger controls."
                )
            else:
                msg = (
                    "Residual risk remains close to inherent risk levels. "
                    "This may indicate weak, missing, or poorly designed controls."
                )

            self.insight_label.setText(f"<b>Interpretation:</b> {msg}")
        else:
            self.insight_label.setText("")
        
        
class RiskMatrixChart(QWidget):
    """
    Matriz de riesgo Impacto x Probabilidad (5x5).

    Cada punto representa un riesgo activo,
    coloreado según su nivel de riesgo residual.
    """
    riskClicked = Signal(object)
    def __init__(self, controller):
        super().__init__()

        self.controller = controller

        # ==================================================
        # LAYOUT DEL WIDGET
        # ==================================================
        layout = QVBoxLayout(self)
        layout.setSpacing(10)   
        layout.setContentsMargins(0, 0, 0, 0)

        # ==================================================
        # TÍTULO
        # ==================================================
        title = QLabel("Risk Heatmap (Impact × Likelihood)")
        title.setStyleSheet("font-size:14px; font-weight:bold;")
        layout.addWidget(title)

        # ==================================================
        # FIGURA MATPLOTLIB (CONTROLADA)
        # ==================================================
        self.figure = Figure(figsize=(8, 5))
        self.figure.tight_layout(pad=2.0)

        self.canvas = FigureCanvas(self.figure)

        # --- CONTROL DE TAMAÑO (CRÍTICO)
        self.canvas.setMinimumHeight(380)
        self.canvas.setMaximumHeight(420)
        self.canvas.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )
        

        layout.addWidget(self.canvas)

        self.refresh()
        self.canvas.mpl_connect("pick_event", self._on_pick)
        self._pick_map = {}

    def _on_pick(self, event):
        artist = event.artist
        cr = self._pick_map.get(artist)

        if cr is None:
            return

        self.riskClicked.emit(cr)
    # ==================================================
    # REFRESH
    # ==================================================

    def refresh(self):
        """
        Refresca la matriz de riesgo (Impacto × Probabilidad)
        siguiendo estándar ERM (matriz discreta + leyenda).
        """

        assessment = self.controller.company_assessment

        # Limpiar figura
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # ==================================================
        # CONFIGURACIÓN DE EJES (MATRIZ 5x5 REAL)
        # ==================================================
        ax.set_xlim(0.5, 5.5)
        ax.set_ylim(0.5, 5.5)

        ax.set_xticks(range(1, 6))
        ax.set_yticks(range(1, 6))

        ax.set_xlabel("Likelihood")
        ax.set_ylabel("Impact")
        ax.set_title("Risk Matrix (Impact × Likelihood)", pad=12)

        # Cuadrícula fuerte (celdas visibles)
        ax.set_xticks([i + 0.5 for i in range(0, 5)], minor=True)
        ax.set_yticks([i + 0.5 for i in range(0, 5)], minor=True)
        ax.grid(which="minor", color="black", linewidth=1)
        ax.grid(which="major", linestyle="--", alpha=0.2)

        # ==================================================
        # ZONAS DE RIESGO (POR CELDA)
        # ==================================================
        for x in range(1, 6):
            for y in range(1, 6):
                score = x * y
                if score < 6:
                    color = "#2ecc71"
                elif score < 12:
                    color = "#f1c40f"
                elif score < 18:
                    color = "#e67e22"
                else:
                    color = "#c0392b"

                ax.add_patch(
                    plt.Rectangle(
                        (x - 0.5, y - 0.5),
                        1,
                        1,
                        color=color,
                        alpha=0.08,
                        zorder=0,
                    )
                )

        # ==================================================
        # PLOTEO DE RIESGOS (SIN TEXTO LARGO)
        # ==================================================
        risks = assessment.get_active_risks()
        cell_occupancy = {}
        legend_items = []

        offsets = [
            (0.0, 0.0),
            (-0.15, 0.15),
            (0.15, 0.15),
            (-0.15, -0.15),
            (0.15, -0.15),
        ]

        for idx, cr in enumerate(risks, start=1):
            # ID corto ERM
            risk_id = f"R{idx}"

            x = cr.custom_probability
            y = (
                cr.custom_impact_financial +
                cr.custom_impact_operational +
                cr.custom_impact_reputational
            ) / 3

            cell_key = (int(x), int(y))
            occ = cell_occupancy.get(cell_key, 0)
            cell_occupancy[cell_key] = occ + 1

            dx, dy = offsets[occ % len(offsets)]
            px, py = x + dx, y + dy

            residual = cr.calculate_residual_risk()
            level = CompanyRisk.risk_level(residual)

            if level == "CRÍTICO":
                color = "#c0392b"
            elif level == "ALTO":
                color = "#e67e22"
            elif level == "MEDIO":
                color = "#f1c40f"
            else:
                color = "#2ecc71"

            point = ax.scatter(
                px,
                py,
                s=140,
                c=color,
                edgecolors="black",
                zorder=3,
                picker=True,
            )

            self._pick_map[point] = cr

            # SOLO ID CORTO
            ax.text(
                px,
                py,
                risk_id,
                ha="center",
                va="center",
                fontsize=9,
                color="black",
                weight="bold",
                zorder=4,
            )

            legend_items.append(f"{risk_id}: {cr.base_risk.name}")

        # ==================================================
        # LEYENDA EXTERNA (OBLIGATORIA)
        # ==================================================
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label='LOW',
                markerfacecolor='#2ecc71', markersize=10),
            Line2D([0], [0], marker='o', color='w', label='MEDIUM',
                markerfacecolor='#f1c40f', markersize=10),
            Line2D([0], [0], marker='o', color='w', label='HIGH',
                markerfacecolor='#e67e22', markersize=10),
            Line2D([0], [0], marker='o', color='w', label='CRITICAL',
                markerfacecolor='#c0392b', markersize=10),
        ]

        ax.legend(
            handles=legend_elements,
            title="Residual Risk Level",
            loc="upper left",
            bbox_to_anchor=(1.02, 1.0),
            frameon=False,
        )

  
        

        # ==================================================
        # AJUSTES FINALES
        # ==================================================
        self.figure.tight_layout(pad=2.0)
        self.canvas.draw_idle()


        
        
# Display-only translation for risk level labels from the domain model.
_LEVEL_EN = {"BAJO": "LOW", "MEDIO": "MEDIUM", "ALTO": "HIGH", "CRÍTICO": "CRITICAL"}


class RiskLevelDonutChart(QWidget):
    """
    Donut chart con la distribución de riesgos por nivel residual.
    """
    riskLevelClicked = Signal(str)  # "BAJO", "MEDIO", "ALTO", "CRÍTICO"
    def __init__(self, controller):
        super().__init__()

        self.controller = controller

        # ==================================================
        # LAYOUT DEL WIDGET
        # ==================================================
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        # ==================================================
        # FIGURA MATPLOTLIB (SECUNDARIA)
        # ==================================================
        self.figure = Figure(figsize=(4, 3))
        self.figure.tight_layout(pad=1.5)

        self.canvas = FigureCanvas(self.figure)

        # --- CONTROL DE TAMAÑO (CLAVE)
        self.canvas.setMinimumHeight(180)
        self.canvas.setMaximumHeight(220)
        self.canvas.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )
        self._wedge_map = {}
        self.canvas.mpl_connect("pick_event", self._on_pick)
        layout.addWidget(self.canvas)
        self._active_level = None     # Nivel actualmente filtrado
        self._hover_annotation = None
        self.canvas.mpl_connect("motion_notify_event", self._on_hover)
        self.refresh()
    def set_active_level(self, level: str | None):
        """
        Marca visualmente el nivel activo (cuando hay filtro).
        """
        self._active_level = level
        self.refresh()
 
    def _on_pick(self, event):
        wedge = event.artist
        level = self._wedge_map.get(wedge)

        if level is None:
            return

        # Emitimos señal (el filtrado vendrá después)
        self.riskLevelClicked.emit(level)
    def _on_hover(self, event):
        if event.inaxes is None:
            if self._hover_annotation:
                self._hover_annotation.set_visible(False)
                self.canvas.draw_idle()
            return

        for wedge, level in self._wedge_map.items():
            contains, _ = wedge.contains(event)
            if not contains:
                continue

            total = sum(self._level_counts.values())
            count = self._level_counts.get(level, 0)
            pct = (count / total) * 100 if total > 0 else 0

            text = f"{level}\n{count} risks ({pct:.1f}%)"

            if not self._hover_annotation:
                self._hover_annotation = event.inaxes.annotate(
                    text,
                    xy=(event.xdata, event.ydata),
                    xytext=(15, 15),
                    textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="#1f1f1f", ec="white"),
                    color="white",
                    fontsize=9,
                )
            else:
                self._hover_annotation.set_text(text)
                self._hover_annotation.xy = (event.xdata, event.ydata)
                self._hover_annotation.set_visible(True)

            self.canvas.draw_idle()
            return

        if self._hover_annotation:
            self._hover_annotation.set_visible(False)
            self.canvas.draw_idle()

    def refresh(self):
        """
        Donut de distribución de riesgos por nivel residual.
        Versión final: legible, sin solapamientos y con semántica ERM.
        """

        assessment = self.controller.company_assessment

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # ==================================================
        # DATOS
        # ==================================================
        levels = {
            "BAJO": 0,
            "MEDIO": 0,
            "ALTO": 0,
            "CRÍTICO": 0,
        }

        for cr in assessment.get_active_risks():
            value = cr.calculate_residual_risk()
            level = CompanyRisk.risk_level(value)
            levels[level] += 1
        self._level_counts = levels.copy()
        labels = list(levels.keys())
        values = list(levels.values())
        total = sum(values)

        if total == 0:
            ax.text(
                0.5, 0.5,
                "No risk data available",
                ha="center",
                va="center",
                fontsize=11,
                color="#666",
            )
            ax.axis("off")
            self.canvas.draw_idle()
            return

        # ==================================================
        # COLORES ERM
        # ==================================================
        colors = [
            "#2ecc71",  # BAJO
            "#f1c40f",  # MEDIO
            "#e67e22",  # ALTO
            "#c0392b",  # CRÍTICO
        ]

        # ==================================================
        # DONUT BASE
        # ==================================================
        wedges, _ = ax.pie(
            values,
            startangle=90,
            colors=colors,
            labels=None,              # SIN labels automáticos
            wedgeprops={
                "width": 0.35,
                "edgecolor": "white",
                "linewidth": 1.2,
            },
        )

        # ==================================================
        # MAPEO PARA CLICK
        # ==================================================
        self._wedge_map.clear()
        for wedge, label in zip(wedges, labels):
            wedge.set_picker(True)
            self._wedge_map[wedge] = label

            # -------------------------------
            # RESALTADO DEL NIVEL ACTIVO
            # -------------------------------
            if self._active_level == label:
                wedge.set_edgecolor("black")
                wedge.set_linewidth(3.0)
                wedge.set_alpha(1.0)
            else:
                wedge.set_edgecolor("white")
                wedge.set_linewidth(1.2)
                wedge.set_alpha(0.9 if self._active_level else 1.0)


        # ==================================================
        # TEXTO INTERIOR (PORCENTAJES BIEN POSICIONADOS)
        # ==================================================
        for wedge, value in zip(wedges, values):
            if value == 0:
                continue

            pct = (value / total) * 100
            angle = (wedge.theta1 + wedge.theta2) / 2.0

            # Posición radial óptima (no se pisa con el agujero)
            r = 0.78
            x = r * np.cos(np.deg2rad(angle))
            y = r * np.sin(np.deg2rad(angle))

            ax.text(
                x,
                y,
                f"{pct:.0f}%",
                ha="center",
                va="center",
                fontsize=10,
                fontweight="bold",
                color="white",
            )

        # ==================================================
        # TEXTO CENTRAL (CONTEXTO)
        # ==================================================
        ax.text(
            0, 0,
            f"{total}\nrisks",
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color="#333",
        )

        # ==================================================
        # LEYENDA COMPACTA Y ALINEADA
        # ==================================================
        legend_labels = [
            f"{_LEVEL_EN.get(label, label)} ({levels[label]})"
            for label in labels
        ]

        ax.legend(
            wedges,
            legend_labels,
            title="Residual risk level",
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            frameon=False,
            fontsize=9,
            title_fontsize=9,
        )

        # ==================================================
        # AJUSTES FINALES
        # ==================================================
        ax.set_title("Risk Distribution by Residual Level", pad=14)
        ax.axis("equal")

        self.figure.tight_layout(pad=1.5)
        self.canvas.draw_idle()
