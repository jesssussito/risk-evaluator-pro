Project Overview

Aplicación de evaluación de riesgos (ERM/GRC) en Python con arquitectura MVC.
Incluye scoring de riesgos, gestión de controles, dashboard analítico y módulo de Cost of Inaction con generación de PDF.

Active Architecture
Pattern: MVC (Model–View–Controller)
UI: PySide6 (Qt6) → activa
Legacy UI: Tkinter → no usar
Core Structure
controller/
app_controller.py: orquestación principal
csv_loader.py: carga y validación de datos
models/
clases.py: Risk, Control, RiskType
companyRisk.py: CompanyRisk, CompanyAssessment
view/
Qt UI principal y flujo de pasos
analysis/: dashboards y análisis
analysis/cost_of_inaction/: modelo de pérdidas + PDF
data/
CSVs como fuente de verdad (riesgos, controles, mappings)
Core Domain Logic
Riesgo inherente = probabilidad × impacto ponderado
Riesgo residual = inherente × (1 − efectividad controles)
Impactos: financiero (0.4), operacional (0.3), reputacional (0.3)
Escalas: probabilidad e impacto de 1 a 5
Clasificación: BAJO / MEDIO / ALTO / CRÍTICO
Key Constraints (CRITICAL)
NO explorar todo el proyecto automáticamente
NO hacer refactors globales
NO cambiar múltiples módulos sin necesidad explícita
NO romper compatibilidad con CSVs
NO renombrar clases o estructuras base
NO modificar lógica de negocio salvo que se solicite
Working Rules
Trabajar SIEMPRE sobre:
un archivo, o
un módulo concreto
Mantener compatibilidad con:
AppController
flujo UI existente
modelos actuales
Respetar separación MVC
Code Style Expectations
Código claro, modular y mantenible
Evitar sobreingeniería
Mantener nombres existentes salvo necesidad justificada
Cambios mínimos y controlados
Task Execution Protocol

Para cada tarea:

Limitar alcance al objetivo pedido
Usar solo contexto necesario
Evitar leer archivos no relevantes
Implementar solución directa y funcional
No introducir cambios colaterales
Output Requirements

Siempre devolver:

Archivos modificados
Explicación breve de cambios
Posibles impactos o dependencias
What NOT to do
No rediseñar toda la arquitectura
No “mejorar todo el sistema”
No introducir nuevas capas innecesarias
No duplicar lógica existente
Notes

El sistema ya está avanzado.
Las mejoras deben ser incrementales, no disruptivas.