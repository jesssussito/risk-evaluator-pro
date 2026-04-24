import csv
from dataclasses import dataclass
from datetime import datetime
from models.clases import RiskType, Control, Risk
import os
import sys


def resource_path(relative_path: str) -> str:
    """
    Devuelve la ruta correcta tanto en desarrollo
    como cuando la app está empaquetada con PyInstaller.
    """
    try:
        base_path = sys._MEIPASS  # PyInstaller temp dir
    except AttributeError:
        # csv_loader.py está en controller/ → subir un nivel da la raíz del proyecto
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# ---------------------------------------------------------------------------
# Error accumulation
# ---------------------------------------------------------------------------

@dataclass
class CsvError:
    """
    Contenedor estructurado para un único error de validación CSV.

    Campos:
        filename  – nombre del archivo CSV (ej. 'risks.csv')
        line_num  – número de fila (base 1), o None para problemas de archivo
        field     – nombre de la columna afectada, o None cuando el error es de fila o archivo
        value     – valor concreto que falló la validación, o None si no aplica
        message   – explicación legible de por qué el valor no es válido
    """
    filename: str
    line_num: int | None
    field:    str | None
    value:    str | None
    message:  str
    severity: str = "error"  # "error" | "warning"

    def __str__(self) -> str:
        label = "CRÍTICO" if self.severity == "error" else "ADVERTENCIA"
        parts = [f"file: {self.filename}"]
        parts.append(f"row: {self.line_num}" if self.line_num is not None else "row: —")
        parts.append(f"field: {self.field}"  if self.field    is not None else "field: —")
        parts.append(f"value: {self.value}"  if self.value    is not None else "value: —")
        return f"  [{label} | {' | '.join(parts)}] → {self.message}"


def _err(
    filename: str,
    line_num: int | None,
    field:    str | None,
    value:    str | None,
    message:  str,
) -> CsvError:
    """Atajo para construir un CsvError crítico."""
    return CsvError(
        filename=filename,
        line_num=line_num,
        field=field,
        value=value,
        message=message,
        severity="error",
    )


def _warn(
    filename: str,
    line_num: int | None,
    field:    str | None,
    value:    str | None,
    message:  str,
) -> CsvError:
    """Atajo para construir un CsvError de advertencia."""
    return CsvError(
        filename=filename,
        line_num=line_num,
        field=field,
        value=value,
        message=message,
        severity="warning",
    )


# Máximo de errores individuales mostrados antes de truncar el listado.
_MAX_ERRORS_SHOWN = 10

_SCORE_FIELDS = (
    "probability",
    "impact_financial",
    "impact_operational",
    "impact_reputational",
)


def _raise_if_errors(
    errors: list[CsvError],
    filename: str,
    process: str,
    warnings: list[CsvError] | None = None,
) -> None:
    """
    Reporta advertencias (sin bloquear) y lanza ValueError solo si hay errores críticos.

    Advertencias → impresas en stderr, ejecución continúa.
    Errores      → lanzan ValueError con encabezado de contexto.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prefix    = f"[{process} | {timestamp}]"

    if warnings:
        w_lines  = [f"{prefix} {len(warnings)} advertencia(s) en '{filename}':"]
        w_lines += [str(w) for w in warnings]
        print("\n".join(w_lines), file=sys.stderr)

    if not errors:
        return

    n     = len(errors)
    shown = errors[:_MAX_ERRORS_SHOWN]
    lines = [f"{prefix} Se encontraron {n} error(es) crítico(s) en '{filename}':"]
    lines += [str(e) for e in shown]

    if n > _MAX_ERRORS_SHOWN:
        remaining = n - _MAX_ERRORS_SHOWN
        lines.append(
            f"\n  ... y {remaining} error(es) más no mostrado(s). "
            f"Corrija los anteriores y vuelva a cargar."
        )

    raise ValueError("\n".join(lines))


def _validate_header(reader, filename: str, process: str, required: set[str]) -> None:
    """Valida cabecera del CSV; lanza inmediatamente con formato unificado."""
    if reader.fieldnames is None:
        _raise_if_errors(
            [_err(filename, None, None, None, "el archivo está vacío o no tiene cabecera")],
            filename, process,
        )
    missing = required - set(reader.fieldnames)
    if missing:
        _raise_if_errors(
            [_err(filename, None, None, None,
                  f"faltan columnas obligatorias: {', '.join(sorted(missing))}")],
            filename, process,
        )


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_risk_types(path: str) -> dict[str, RiskType]:
    filename = os.path.basename(path)
    risk_types: dict[str, RiskType] = {}
    path = resource_path(path)
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            _validate_header(reader, filename, "load_risk_types",
                             {"type_id", "name", "description"})

            errors: list[CsvError] = []

            for line_num, row in enumerate(reader, start=2):
                type_id = row["type_id"].strip()
                name    = row["name"].strip()
                row_ok  = True

                if not type_id:
                    errors.append(_err(filename, line_num, "type_id", "",
                                       "el valor está vacío"))
                    row_ok = False

                if not name:
                    errors.append(_err(filename, line_num, "name", "",
                                       "el valor está vacío"))
                    row_ok = False

                if row_ok and type_id in risk_types:
                    errors.append(_err(filename, line_num, "type_id", type_id,
                                       "ya existe en el archivo (duplicado)"))
                    row_ok = False

                if not row_ok:
                    continue

                risk_types[type_id] = RiskType(
                    type_id=type_id,
                    name=name,
                    description=row["description"].strip(),
                )

            _raise_if_errors(errors, filename, "load_risk_types")

    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo: {path}")

    return risk_types


def load_controls(path: str) -> dict[str, Control]:
    filename = os.path.basename(path)
    controls: dict[str, Control] = {}
    path = resource_path(path)
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            _validate_header(reader, filename, "load_controls",
                             {"control_id", "name", "base_effectiveness", "description"})

            errors: list[CsvError] = []

            for line_num, row in enumerate(reader, start=2):
                control_id = row["control_id"].strip()
                name       = row["name"].strip()
                eff_raw    = row["base_effectiveness"].strip()
                row_ok     = True

                if not control_id:
                    errors.append(_err(filename, line_num, "control_id", "",
                                       "el valor está vacío"))
                    row_ok = False

                if not name:
                    errors.append(_err(filename, line_num, "name", "",
                                       "el valor está vacío"))
                    row_ok = False

                effectiveness = None
                if not eff_raw:
                    errors.append(_err(filename, line_num, "base_effectiveness", "",
                                       "el valor está vacío"))
                    row_ok = False
                else:
                    try:
                        effectiveness = float(eff_raw)
                    except ValueError:
                        errors.append(_err(filename, line_num, "base_effectiveness", eff_raw,
                                           "no es un número válido; se esperaba un valor entre 0.0 y 1.0"))
                        row_ok = False
                    else:
                        if not (0.0 <= effectiveness <= 1.0):
                            errors.append(_err(filename, line_num, "base_effectiveness",
                                               str(effectiveness),
                                               "fuera del rango [0.0, 1.0]; un valor mayor que 1 "
                                               "reduciría más riesgo del existente"))
                            row_ok = False

                if row_ok and control_id in controls:
                    errors.append(_err(filename, line_num, "control_id", control_id,
                                       "ya existe en el archivo (duplicado)"))
                    row_ok = False

                if not row_ok:
                    continue

                controls[control_id] = Control(
                    control_id=control_id,
                    name=name,
                    base_effectiveness=effectiveness,
                    description=row["description"].strip(),
                )

            _raise_if_errors(errors, filename, "load_controls")

    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo: {path}")

    return controls


def load_risks(path: str, risk_types: dict[str, RiskType]) -> dict[str, Risk]:
    filename = os.path.basename(path)
    risks: dict[str, Risk] = {}
    path = resource_path(path)
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            _validate_header(reader, filename, "load_risks",
                             {"risk_id", "name", "type_id", "description"})

            errors: list[CsvError] = []

            for line_num, row in enumerate(reader, start=2):
                risk_id     = row["risk_id"].strip()
                name        = row["name"].strip()
                type_id     = row["type_id"].strip()
                description = row["description"].strip()
                row_ok      = True

                if not risk_id:
                    errors.append(_err(filename, line_num, "risk_id", "",
                                       "el valor está vacío"))
                    row_ok = False

                if not name:
                    errors.append(_err(filename, line_num, "name", "",
                                       "el valor está vacío"))
                    row_ok = False

                if not type_id:
                    errors.append(_err(filename, line_num, "type_id", "",
                                       "el valor está vacío"))
                    row_ok = False
                elif type_id not in risk_types:
                    errors.append(_err(filename, line_num, "type_id", type_id,
                                       "no existe en el catálogo de tipos de riesgo"))
                    row_ok = False

                if row_ok and risk_id in risks:
                    errors.append(_err(filename, line_num, "risk_id", risk_id,
                                       "ya existe en el archivo (duplicado)"))
                    row_ok = False

                if not row_ok:
                    continue

                risk = Risk(
                    risk_id=risk_id,
                    name=name,
                    risk_type=risk_types[type_id],
                    base_probability=1,
                    base_impact_financial=1,
                    base_impact_operational=1,
                    base_impact_reputational=1,
                )
                risk.description = description
                risks[risk_id] = risk

            _raise_if_errors(errors, filename, "load_risks")

    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo: {path}")

    return risks


def load_risk_base_scores(path: str, risks: dict[str, Risk]) -> None:
    filename = os.path.basename(path)
    path = resource_path(path)
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            _validate_header(reader, filename, "load_risk_base_scores",
                             {"risk_id", *_SCORE_FIELDS})

            errors:   list[CsvError] = []
            warnings: list[CsvError] = []
            field_stats: dict[str, list[float]] = {f: [] for f in _SCORE_FIELDS}

            for line_num, row in enumerate(reader, start=2):
                risk_id = row["risk_id"].strip()

                if not risk_id:
                    errors.append(_err(filename, line_num, "risk_id", "",
                                       "el valor está vacío"))
                    continue

                if risk_id not in risks:
                    errors.append(_err(filename, line_num, "risk_id", risk_id,
                                       "no existe en el catálogo de riesgos"))
                    continue

                parsed: dict[str, float] = {}
                row_ok = True

                for field in _SCORE_FIELDS:
                    raw = row[field].strip()
                    if not raw:
                        errors.append(_err(filename, line_num, field, "",
                                           "el valor está vacío"))
                        row_ok = False
                        continue
                    try:
                        val = float(raw)
                    except ValueError:
                        errors.append(_err(filename, line_num, field, raw,
                                           "no es un número válido; se esperaba un entero entre 1 y 5"))
                        row_ok = False
                        continue
                    if not (1.0 <= val <= 5.0):
                        boundary = "inferior al mínimo (1)" if val < 1 else "superior al máximo (5)"
                        errors.append(_err(filename, line_num, field, raw,
                                           f"está {boundary}; la escala válida es [1, 5]"))
                        row_ok = False
                        continue
                    parsed[field] = val

                if not row_ok:
                    continue

                # Coherence check: all fields simultaneously at maximum indicates
                # an unfilled assessment (default-fill pattern), not a real evaluation.
                if all(parsed[f] == 5.0 for f in _SCORE_FIELDS):
                    warnings.append(_warn(filename, line_num, None, "5",
                                          f"todos los campos del riesgo '{risk_id}' están al máximo; "
                                          f"esto indica valores por defecto sin evaluación real"))
                    continue

                for f in _SCORE_FIELDS:
                    field_stats[f].append(parsed[f])

                risk = risks[risk_id]
                risk.adjust_probability(int(parsed["probability"]))
                risk.adjust_impact(
                    financial=int(parsed["impact_financial"]),
                    operational=int(parsed["impact_operational"]),
                    reputational=int(parsed["impact_reputational"]),
                )

            # Dataset-level check: all risks sharing the same extreme value on any
            # field suggests default fill-in rather than a real assessment.
            if len(next(iter(field_stats.values()), [])) > 1:
                for field, values in field_stats.items():
                    unique = set(values)
                    if len(unique) == 1:
                        val = next(iter(unique))
                        if val in (1.0, 5.0):
                            label = "el máximo" if val == 5.0 else "el mínimo"
                            warnings.append(_warn(filename, None, field, str(int(val)),
                                                  f"todos los riesgos tienen este valor "
                                                  f"({label} de la escala); una distribución "
                                                  f"completamente uniforme en un extremo sugiere "
                                                  f"datos por defecto"))

            _raise_if_errors(errors, filename, "load_risk_base_scores", warnings)

    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo: {path}")


def load_risk_control_map(
    path: str,
    risks: dict[str, Risk],
    controls: dict[str, Control],
) -> None:
    filename = os.path.basename(path)
    path = resource_path(path)
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            _validate_header(reader, filename, "load_risk_control_map",
                             {"risk_id", "control_id"})

            errors: list[CsvError] = []
            seen_pairs: set[tuple[str, str]] = set()

            for line_num, row in enumerate(reader, start=2):
                risk_id    = row["risk_id"].strip()
                control_id = row["control_id"].strip()
                row_ok     = True

                if not risk_id:
                    errors.append(_err(filename, line_num, "risk_id", "",
                                       "el valor está vacío"))
                    row_ok = False

                if not control_id:
                    errors.append(_err(filename, line_num, "control_id", "",
                                       "el valor está vacío"))
                    row_ok = False

                if not row_ok:
                    continue

                if risk_id not in risks:
                    errors.append(_err(filename, line_num, "risk_id", risk_id,
                                       "no existe en el catálogo de riesgos"))
                    row_ok = False

                if control_id not in controls:
                    errors.append(_err(filename, line_num, "control_id", control_id,
                                       "no existe en el catálogo de controles"))
                    row_ok = False

                if not row_ok:
                    continue

                pair = (risk_id, control_id)
                if pair in seen_pairs:
                    errors.append(_err(filename, line_num, None,
                                       f"{risk_id}+{control_id}",
                                       f"la combinación (riesgo='{risk_id}', "
                                       f"control='{control_id}') ya existe (duplicado)"))
                    continue

                seen_pairs.add(pair)
                risks[risk_id].add_control(controls[control_id])

            _raise_if_errors(errors, filename, "load_risk_control_map")

    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo: {path}")


def validate_referential_integrity(risks: dict[str, "Risk"]) -> None:
    """
    Comprobación de integridad referencial post-carga.

    Verifica que cada riesgo cargado desde risks.csv tenga al menos un control
    asignado a través de risk_control_map.csv. Acumula todas las violaciones
    antes de lanzar, para que el llamador vea todos los problemas de una vez.

    Lanza ValueError con un informe estructurado si se detecta alguna violación.
    """
    errors = [
        _err("risk_control_map.csv", None, None, risk_id,
             f"el riesgo '{risk_id}' ({risk.name}) no tiene ningún control asignado")
        for risk_id, risk in risks.items()
        if not risk.controls
    ]
    _raise_if_errors(errors, "risk_control_map.csv", "validate_referential_integrity")
