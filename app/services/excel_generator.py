import io

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


HEADER_FONT = Font(name="Cambria", size=14, bold=True, color="000000")
HEADER_FILL = PatternFill(start_color="00B0F0", end_color="00B0F0", fill_type="solid")
TITLE_FONT = Font(name="Cambria", size=28, bold=False)
SUBTITLE_FONT = Font(name="Cambria", size=16, bold=False)
CENTER_ALIGN = Alignment(horizontal="center", vertical="center", wrap_text=True)


def _add_title_rows(ws, title: str, subtitle: str, max_col: int) -> int:
    title_row = 1
    subtitle_row = 2
    header_row = 3

    ws.merge_cells(start_row=title_row, start_column=1, end_row=title_row, end_column=max_col)
    cell = ws.cell(row=title_row, column=1, value=title)
    cell.font = TITLE_FONT
    cell.alignment = Alignment(horizontal="center", vertical="center")

    ws.merge_cells(start_row=subtitle_row, start_column=1, end_row=subtitle_row, end_column=max_col)
    cell = ws.cell(row=subtitle_row, column=1, value=subtitle)
    cell.font = SUBTITLE_FONT
    cell.alignment = Alignment(horizontal="center", vertical="center")

    return header_row


def _style_header(ws, headers: list[str], header_row: int = 3) -> None:
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=header_row, column=col, value=header)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = CENTER_ALIGN


def _auto_width(ws) -> None:
    for col in ws.columns:
        max_length = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except Exception:
                pass
        ws.column_dimensions[col_letter].width = min(max_length + 2, 50)


def _get(d, key, default=""):
    val = d.get(key) if isinstance(d, dict) else getattr(d, key, default)
    return val if val is not None else default


def generate_candidatos_excel(candidatos: list[dict]) -> io.BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = "Candidatos"

    headers = [
        "No.", "Reg/Dist", "Cédula", "Nombre Completo", "Sexo",
        "Cargo Solicitado", "Escolaridad", "En Sustitución De",
        "Cédula No.", "Fecha Ingreso", "Centro", "Referido Por", "Teléfono",
    ]
    header_row = _add_title_rows(ws, "DIRECCIÓN DE RECURSOS HUMANOS", "CANDIDATOS", len(headers))
    _style_header(ws, headers, header_row)

    for row_idx, c in enumerate(candidatos, header_row + 1):
        dc = c.get("datos_crudos", {}) or {}
        ws.cell(row=row_idx, column=1, value=dc.get("no", ""))
        ws.cell(row=row_idx, column=2, value=dc.get("reg_dist", ""))
        ws.cell(row=row_idx, column=3, value=dc.get("cedula", ""))
        ws.cell(row=row_idx, column=4, value=_get(c, "nombre"))
        ws.cell(row=row_idx, column=5, value=dc.get("sexo", ""))
        ws.cell(row=row_idx, column=6, value=dc.get("cargo_solicitado", ""))
        ws.cell(row=row_idx, column=7, value=dc.get("escolaridad", "") or _get(c, "educacion"))
        ws.cell(row=row_idx, column=8, value=dc.get("en_sustitucion_de", ""))
        ws.cell(row=row_idx, column=9, value=dc.get("cedula_no", ""))
        ws.cell(row=row_idx, column=10, value=dc.get("fecha_ingreso", ""))
        ws.cell(row=row_idx, column=11, value=dc.get("centro", ""))
        ws.cell(row=row_idx, column=12, value=dc.get("referido_por", ""))
        ws.cell(row=row_idx, column=13, value=_get(c, "telefono"))

    _auto_width(ws)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def generate_propuestas_excel(propuestas: list[dict]) -> io.BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = "Propuestas"

    headers = [
        "No.", "Reg/Dist", "Cédula", "Nombre Completo", "Sexo",
        "Cargo Solicitado", "Escolaridad", "En Sustitución De",
        "Cédula No.", "Fecha Ingreso", "Centro", "Referido Por", "Teléfono",
    ]
    header_row = _add_title_rows(ws, "DIRECCIÓN DE RECURSOS HUMANOS", "PROPUESTAS REGIONAL 2025", len(headers))
    _style_header(ws, headers, header_row)

    for row_idx, p in enumerate(propuestas, header_row + 1):
        ws.cell(row=row_idx, column=1, value=_get(p, "no"))
        ws.cell(row=row_idx, column=2, value=_get(p, "reg_dist"))
        ws.cell(row=row_idx, column=3, value=_get(p, "cedula"))
        ws.cell(row=row_idx, column=4, value=_get(p, "nombre_completo"))
        ws.cell(row=row_idx, column=5, value=_get(p, "sexo"))
        ws.cell(row=row_idx, column=6, value=_get(p, "cargo_solicitado"))
        ws.cell(row=row_idx, column=7, value=_get(p, "escolaridad"))
        ws.cell(row=row_idx, column=8, value=_get(p, "en_sustitucion_de"))
        ws.cell(row=row_idx, column=9, value=_get(p, "cedula_no"))
        fecha = _get(p, "fecha_ingreso", "")
        if hasattr(fecha, "strftime"):
            fecha = fecha.strftime("%Y-%m-%d")
        ws.cell(row=row_idx, column=10, value=fecha)
        ws.cell(row=row_idx, column=11, value=_get(p, "centro"))
        ws.cell(row=row_idx, column=12, value=_get(p, "referido_por"))
        ws.cell(row=row_idx, column=13, value=_get(p, "telefono"))

    _auto_width(ws)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def generate_reajustes_excel(reajustes: list[dict]) -> io.BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = "Reajustes"

    headers = [
        "Cédula", "Nombre Completo", "Grupo Ocupacional", "Cargo",
        "Salario Actual", "Salario Solicitado", "Diferencia",
        "% Incremento", "Observación", "Fecha Efectividad",
    ]
    header_row = _add_title_rows(ws, "DIRECCIÓN DE RECURSOS HUMANOS", "REAJUSTE SALARIAL", len(headers))
    _style_header(ws, headers, header_row)

    for row_idx, r in enumerate(reajustes, header_row + 1):
        ws.cell(row=row_idx, column=1, value=_get(r, "cedula"))
        ws.cell(row=row_idx, column=2, value=_get(r, "nombre_completo"))
        ws.cell(row=row_idx, column=3, value=_get(r, "grupo_ocupacional"))
        ws.cell(row=row_idx, column=4, value=_get(r, "cargo"))
        ws.cell(row=row_idx, column=5, value=_get(r, "salario_actual", 0))
        ws.cell(row=row_idx, column=6, value=_get(r, "salario_solicitado", 0))
        ws.cell(row=row_idx, column=7, value=_get(r, "diferencia_salarial", 0))
        ws.cell(row=row_idx, column=8, value=_get(r, "porcentaje_incremento", 0))
        ws.cell(row=row_idx, column=9, value=_get(r, "observacion"))
        fecha = _get(r, "fecha_efectividad", "")
        if hasattr(fecha, "strftime"):
            fecha = fecha.strftime("%Y-%m-%d")
        ws.cell(row=row_idx, column=10, value=fecha)

    _auto_width(ws)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def generate_no_proceden_excel(no_proceden: list[dict]) -> io.BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = "No Proceden"

    headers = [
        "No.", "Reg/Dist", "Cédula", "Nombre Completo", "Sexo",
        "Cargo Solicitado", "Salario Solicitado", "Escolaridad",
        "Observación", "Referido Por", "Teléfono",
    ]
    header_row = _add_title_rows(ws, "DIRECCIÓN DE RECURSOS HUMANOS", "NO PROCEDEN 2025", len(headers))
    _style_header(ws, headers, header_row)

    for row_idx, np in enumerate(no_proceden, header_row + 1):
        ws.cell(row=row_idx, column=1, value=_get(np, "no"))
        ws.cell(row=row_idx, column=2, value=_get(np, "reg_dist"))
        ws.cell(row=row_idx, column=3, value=_get(np, "cedula"))
        ws.cell(row=row_idx, column=4, value=_get(np, "nombre_completo"))
        ws.cell(row=row_idx, column=5, value=_get(np, "sexo"))
        ws.cell(row=row_idx, column=6, value=_get(np, "cargo_solicitado"))
        ws.cell(row=row_idx, column=7, value=_get(np, "salario_solicitado", 0))
        ws.cell(row=row_idx, column=8, value=_get(np, "escolaridad"))
        ws.cell(row=row_idx, column=9, value=_get(np, "observacion"))
        ws.cell(row=row_idx, column=10, value=_get(np, "referido_por"))
        ws.cell(row=row_idx, column=11, value=_get(np, "telefono"))

    _auto_width(ws)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output
