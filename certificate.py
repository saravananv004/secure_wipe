from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


BASE_DIR = Path(__file__).resolve().parent
CERT_DIR = BASE_DIR / "certificates"


def format_size(size_bytes):
    if size_bytes is None:
        return "0 B"

    try:
        size_bytes = float(size_bytes)
    except Exception:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    for unit in units:
        if size_bytes < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size_bytes)} {unit}"
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024


def fit_text_line(c, text, max_width, font_name="Helvetica", font_size=10):
    text = str(text)
    if c.stringWidth(text, font_name, font_size) <= max_width:
        return [text]

    parts = []
    current = ""

    for chunk in text.replace("\\", "\\ ").split():
        candidate = f"{current} {chunk}".strip()
        candidate_clean = candidate.replace("\\ ", "\\")
        if c.stringWidth(candidate_clean, font_name, font_size) <= max_width:
            current = candidate
        else:
            if current:
                parts.append(current.replace("\\ ", "\\"))
            current = chunk

    if current:
        parts.append(current.replace("\\ ", "\\"))

    return parts


def draw_gold_badge(c, center_x, center_y):
    gold_outer = colors.HexColor("#A16207")
    gold_mid = colors.HexColor("#D4AF37")
    gold_inner = colors.HexColor("#F8E7A2")
    maroon = colors.HexColor("#7F1D1D")

    c.setStrokeColor(gold_outer)
    c.setFillColor(gold_mid)
    c.setLineWidth(1.5)
    c.circle(center_x, center_y, 14 * mm, fill=1, stroke=1)

    c.setFillColor(gold_inner)
    c.setStrokeColor(gold_outer)
    c.setLineWidth(1)
    c.circle(center_x, center_y, 10.5 * mm, fill=1, stroke=1)

    c.setFillColor(gold_mid)
    c.circle(center_x, center_y, 7.5 * mm, fill=1, stroke=0)

    c.setFillColor(maroon)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(center_x, center_y + 2.2 * mm, "CERTIFIED")
    c.setFont("Helvetica-Bold", 6.2)
    c.drawCentredString(center_x, center_y - 1.8 * mm, "SECURE WIPE")


def generate_certificate(
    target_path=None,
    passes=0,
    files_wiped=0,
    bytes_wiped=0,
    verification=False,
    **kwargs
):
    CERT_DIR.mkdir(parents=True, exist_ok=True)

    certificate_id = f"SW-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    output_path = str(CERT_DIR / f"{certificate_id}.pdf")

    final_target = target_path or "Not Provided"
    generated_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    verification_text = "SUCCESSFUL" if str(verification).lower() in ["true", "successful", "success", "1"] else "FAILED"

    navy = colors.HexColor("#0B1736")
    deep_navy = colors.HexColor("#081127")
    slate = colors.HexColor("#334155")
    text_dark = colors.HexColor("#111827")
    muted = colors.HexColor("#64748B")
    soft_line = colors.HexColor("#CBD5E1")
    soft_fill = colors.HexColor("#F8FAFC")
    parchment = colors.HexColor("#FFFCF5")
    gold = colors.HexColor("#D4AF37")
    gold_dark = colors.HexColor("#A16207")

    success_fill = colors.HexColor("#ECFDF5")
    success_border = colors.HexColor("#86EFAC")
    success_text = colors.HexColor("#166534")

    fail_fill = colors.HexColor("#FEF2F2")
    fail_border = colors.HexColor("#FCA5A5")
    fail_text = colors.HexColor("#991B1B")

    note_fill = colors.HexColor("#FFF7ED")
    note_border = colors.HexColor("#FDBA74")
    note_text = colors.HexColor("#9A3412")

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # Background
    c.setFillColor(parchment)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Triple border
    c.setStrokeColor(gold_dark)
    c.setLineWidth(2)
    c.rect(10 * mm, 10 * mm, width - 20 * mm, height - 20 * mm)

    c.setStrokeColor(gold)
    c.setLineWidth(0.8)
    c.rect(13 * mm, 13 * mm, width - 26 * mm, height - 26 * mm)

    c.setStrokeColor(soft_line)
    c.setLineWidth(0.8)
    c.rect(17 * mm, 17 * mm, width - 34 * mm, height - 34 * mm)

    # Header band
    header_x = 22 * mm
    header_y = height - 44 * mm
    header_w = width - 44 * mm
    header_h = 18 * mm

    c.setFillColor(deep_navy)
    c.roundRect(header_x, header_y, header_w, header_h, 4 * mm, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 19)
    c.drawCentredString(width / 2, header_y + 10.2 * mm, "SECURE DATA WIPING CERTIFICATE")

    # Subtitle
    c.setFillColor(slate)
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, height - 50.5 * mm, "Corporate Record of Software-Based Secure Wiping Execution")

    # Meta strip
    meta_x = 22 * mm
    meta_y = height - 69 * mm
    meta_w = width - 44 * mm
    meta_h = 12 * mm

    c.setFillColor(colors.white)
    c.setStrokeColor(soft_line)
    c.setLineWidth(1)
    c.roundRect(meta_x, meta_y, meta_w, meta_h, 2.5 * mm, fill=1, stroke=1)

    c.setFillColor(navy)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(meta_x + 5 * mm, meta_y + 4.2 * mm, f"Certificate ID: {certificate_id}")
    c.drawRightString(meta_x + meta_w - 5 * mm, meta_y + 4.2 * mm, f"Generated On: {generated_on}")

    # Seal and statement aligned properly
    statement_x = 22 * mm
    statement_y = height - 102 * mm
    statement_w = 132 * mm
    statement_h = 22 * mm

    c.setFillColor(colors.white)
    c.setStrokeColor(gold)
    c.setLineWidth(1)
    c.roundRect(statement_x, statement_y, statement_w, statement_h, 3 * mm, fill=1, stroke=1)

    c.setFillColor(slate)
    c.setFont("Helvetica-Oblique", 9.2)
    c.drawCentredString(
        statement_x + statement_w / 2,
        statement_y + 12.2 * mm,
        "This certifies that the selected folder was processed"
    )
    c.drawCentredString(
        statement_x + statement_w / 2,
        statement_y + 7.0 * mm,
        "through the configured secure wiping workflow."
    )

    draw_gold_badge(c, width - 36 * mm, statement_y + statement_h / 2)

    # Main panel
    panel_x = 22 * mm
    panel_y = 58 * mm
    panel_w = width - 44 * mm
    panel_h = 128 * mm

    c.setFillColor(colors.white)
    c.setStrokeColor(soft_line)
    c.setLineWidth(1)
    c.roundRect(panel_x, panel_y, panel_w, panel_h, 4 * mm, fill=1, stroke=1)

    # Section bar
    bar_x = panel_x + 6 * mm
    bar_y = panel_y + panel_h - 16 * mm
    bar_w = panel_w - 12 * mm
    bar_h = 9 * mm

    c.setFillColor(navy)
    c.roundRect(bar_x, bar_y, bar_w, bar_h, 2 * mm, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 11.5)
    c.drawString(bar_x + 4 * mm, bar_y + 3.1 * mm, "CORPORATE WIPE EXECUTION SUMMARY")

    # Detail rows
    table_x = panel_x + 10 * mm
    table_y_top = panel_y + panel_h - 27 * mm
    label_w = 48 * mm
    value_w = panel_w - 26 * mm - label_w
    row_h = 10 * mm

    rows = [
        ("System Name", "Secure Data Wiping System"),
        ("Target Folder", str(final_target)),
        ("Overwrite Passes", str(passes)),
        ("Files Wiped", str(files_wiped)),
        ("Estimated Data Wiped", format_size(bytes_wiped)),
        ("Verification Status", verification_text),
        ("Wipe Method", "Multi-pass software overwrite"),
    ]

    current_y = table_y_top

    for i, (label, value) in enumerate(rows):
        row_x = table_x
        row_y = current_y - row_h + 1.5 * mm
        row_w = panel_w - 20 * mm

        if i % 2 == 0:
            c.setFillColor(soft_fill)
            c.roundRect(row_x, row_y, row_w, row_h, 1.8 * mm, fill=1, stroke=0)

        c.setFillColor(slate)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(row_x + 3 * mm, current_y - 2.3 * mm, label)

        c.setFillColor(text_dark)
        c.setFont("Helvetica", 10)

        if label == "Target Folder":
            lines = fit_text_line(c, value, value_w - 8 * mm, "Helvetica", 10)
            display_lines = lines[:2]

            if len(display_lines) == 1:
                c.drawString(row_x + label_w, current_y - 2.3 * mm, display_lines[0])
                current_y -= row_h
            else:
                c.drawString(row_x + label_w, current_y - 1.3 * mm, display_lines[0])
                c.drawString(row_x + label_w, current_y - 5.8 * mm, display_lines[1])
                current_y -= 12 * mm
        else:
            c.drawString(row_x + label_w, current_y - 2.3 * mm, value)
            current_y -= row_h

    # Verification card
    verify_x = panel_x + 10 * mm
    verify_y = panel_y + 34 * mm
    verify_w = panel_w - 20 * mm
    verify_h = 16 * mm

    if verification_text == "SUCCESSFUL":
        c.setFillColor(success_fill)
        c.setStrokeColor(success_border)
        verify_color = success_text
    else:
        c.setFillColor(fail_fill)
        c.setStrokeColor(fail_border)
        verify_color = fail_text

    # c.roundRect(verify_x, verify_y, verify_w, verify_h, 3 * mm, fill=1, stroke=1)
    #
    # c.setFillColor(verify_color)
    # c.setFont("Helvetica-Bold", 11)
    # c.drawString(verify_x + 4 * mm, verify_y + 9.5 * mm, f"Verification Result: {verification_text}")

    # c.setFillColor(slate)
    # c.setFont("Helvetica", 8.5)
    # c.drawString(verify_x + 4 * mm, verify_y + 4.2 * mm, "Post-wipe validation status was recorded for the selected folder.")

    # Compliance note
    note_x = panel_x + 10 * mm
    note_y = panel_y + 10 * mm
    note_w = panel_w - 20 * mm
    note_h = 18 * mm

    c.setFillColor(note_fill)
    c.setStrokeColor(note_border)
    c.roundRect(note_x, note_y, note_w, note_h, 3 * mm, fill=1, stroke=1)

    c.setFillColor(note_text)
    c.setFont("Helvetica-Bold", 9.7)
    c.drawString(note_x + 4 * mm, note_y + 12.2 * mm, "Compliance Note")

    c.setFont("Helvetica", 8.1)
    c.drawString(note_x + 4 * mm, note_y + 7.2 * mm, "This certificate confirms a software-based overwrite workflow for academic and project demonstration.")
    c.drawString(note_x + 4 * mm, note_y + 3.0 * mm, "Results on SSDs may vary because of wear leveling, controller firmware, and storage architecture behavior.")

    # Signature section
    sign_y = 31 * mm

    c.setStrokeColor(gold_dark)
    c.setLineWidth(1)
    c.line(38 * mm, sign_y, 88 * mm, sign_y)
    c.line(width - 88 * mm, sign_y, width - 38 * mm, sign_y)

    c.setFillColor(navy)
    c.setFont("Helvetica-Bold", 9.5)
    c.drawCentredString(63 * mm, sign_y - 4.8 * mm, "Authorized By")
    c.drawCentredString(width - 63 * mm, sign_y - 4.8 * mm, "Issued By")

    c.setFillColor(muted)
    c.setFont("Helvetica", 8.4)
    c.drawCentredString(63 * mm, sign_y - 9.6 * mm, "Secure Wipe Administrator")
    c.drawCentredString(width - 63 * mm, sign_y - 9.6 * mm, "Secure Data Wiping System")

    # Footer
    c.setFillColor(muted)
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width / 2, 17 * mm, "Electronically generated corporate certificate for secure data wiping workflow")

    c.save()
    return output_path