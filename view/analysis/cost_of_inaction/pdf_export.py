from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    HRFlowable,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from datetime import datetime

# ---------------------------------------------------------------------------
# COLOR PALETTE
# ---------------------------------------------------------------------------
_BLUE       = colors.HexColor("#1565C0")
_BLUE_LIGHT = colors.HexColor("#E8F0FE")
_BLUE_RULE  = colors.HexColor("#90CAF9")
_DARK       = colors.HexColor("#0D1B2A")
_TEXT       = colors.HexColor("#212121")
_MUTED      = colors.HexColor("#757575")
_WHITE      = colors.white

# A4 content width (595.27 - 55 left - 55 right)
_CONTENT_W = 485


# ---------------------------------------------------------------------------
# STYLES
# ---------------------------------------------------------------------------
def _build_styles() -> dict:
    base = getSampleStyleSheet()

    return {
        "cover_title": ParagraphStyle(
            "CoverTitle",
            parent=base["Title"],
            fontSize=26,
            textColor=_WHITE,
            alignment=TA_CENTER,
            spaceAfter=10,
            leading=34,
            fontName="Helvetica-Bold",
        ),
        "cover_subtitle": ParagraphStyle(
            "CoverSubtitle",
            parent=base["Normal"],
            fontSize=12,
            textColor=colors.HexColor("#BBDEFB"),
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "cover_date": ParagraphStyle(
            "CoverDate",
            parent=base["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#90CAF9"),
            alignment=TA_CENTER,
        ),
        "cover_note": ParagraphStyle(
            "CoverNote",
            parent=base["Normal"],
            fontSize=9,
            textColor=_MUTED,
            alignment=TA_CENTER,
        ),
        "section_header": ParagraphStyle(
            "SectionHeader",
            parent=base["Heading1"],
            fontSize=14,
            textColor=_BLUE,
            spaceBefore=6,
            spaceAfter=8,
            leading=20,
            fontName="Helvetica-Bold",
        ),
        "subsection": ParagraphStyle(
            "Subsection",
            parent=base["Heading2"],
            fontSize=11,
            textColor=_TEXT,
            spaceBefore=12,
            spaceAfter=4,
            fontName="Helvetica-Bold",
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontSize=10,
            textColor=_TEXT,
            spaceAfter=7,
            leading=15,
            alignment=TA_JUSTIFY,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["Normal"],
            fontSize=10,
            textColor=_TEXT,
            spaceAfter=4,
            leading=14,
            leftIndent=18,
        ),
        "metric": ParagraphStyle(
            "Metric",
            parent=base["Normal"],
            fontSize=11,
            textColor=_BLUE,
            leading=16,
            fontName="Helvetica-Bold",
        ),
    }


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def _metric_box(text: str, styles: dict) -> Table:
    """Renders a [KEY] line as a highlighted callout box."""
    clean = text[6:]  # strip "[KEY] "
    cell  = Paragraph(clean, styles["metric"])
    tbl   = Table([[cell]], colWidths=[_CONTENT_W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), _BLUE_LIGHT),
        ("TOPPADDING",    (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
        ("BOX",           (0, 0), (-1, -1), 1.5, _BLUE),
    ]))
    return tbl


def _render_line(line: str, styles: dict):
    """Maps a single report line to its appropriate flowable."""
    if line.startswith("[KEY] "):
        return _metric_box(line, styles)
    if line.startswith("## "):
        return Paragraph(line[3:], styles["subsection"])
    if line.startswith("  "):
        return Paragraph(line.strip(), styles["bullet"])
    return Paragraph(line, styles["body"])


def _cover_banner(styles: dict) -> Table:
    """Dark-background title banner for the cover page."""
    rows = [
        [Paragraph("Cost of Inaction", styles["cover_title"])],
        [Paragraph("Cybersecurity Risk &amp; Economic Impact Analysis", styles["cover_subtitle"])],
        [Spacer(1, 6)],
        [Paragraph(f"Prepared {datetime.now().strftime('%B %d, %Y')}", styles["cover_date"])],
    ]
    tbl = Table(rows, colWidths=[_CONTENT_W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), _DARK),
        ("TOPPADDING",    (0, 0), (-1, -1), 36),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 36),
        ("LEFTPADDING",   (0, 0), (-1, -1), 28),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 28),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return tbl


# ---------------------------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------------------------
def export_report_to_pdf(
    report_sections: dict,
    output_path: str = "Cost_of_Inaction_Report.pdf",
):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=55,
        leftMargin=55,
        topMargin=55,
        bottomMargin=55,
    )

    styles   = _build_styles()
    elements = []

    # --------------------------------------------------
    # COVER PAGE
    # --------------------------------------------------
    elements.append(Spacer(1, 80))
    elements.append(_cover_banner(styles))
    elements.append(Spacer(1, 32))
    elements.append(
        Paragraph("Executive document — for internal use only.", styles["cover_note"])
    )
    elements.append(PageBreak())

    # --------------------------------------------------
    # CONTENT SECTIONS
    # --------------------------------------------------
    for section_title, lines in report_sections.items():
        elements.append(
            HRFlowable(
                width="100%",
                thickness=2,
                color=_BLUE,
                spaceBefore=4,
                spaceAfter=6,
            )
        )
        elements.append(Paragraph(section_title, styles["section_header"]))

        for line in lines:
            if not line.strip():
                elements.append(Spacer(1, 6))
                continue

            flowable = _render_line(line, styles)
            elements.append(flowable)

            if line.startswith("[KEY] "):
                elements.append(Spacer(1, 8))

        elements.append(Spacer(1, 14))

    doc.build(elements)
