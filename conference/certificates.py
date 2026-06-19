import io
import os
from datetime import date

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

# Palette matching the email templates
TEAL = colors.HexColor("#1b6b6b")
TEAL_LIGHT = colors.HexColor("#eef6f3")
GOLD = colors.HexColor("#c8a84b")
DARK = colors.HexColor("#1f1c17")
MUTED = colors.HexColor("#5c5146")
BORDER = colors.HexColor("#e2ece8")

LOGO_PATH = os.path.join(settings.BASE_DIR, "static", "img", "logo.png")

PAGE_W, PAGE_H = landscape(A4)  # 297 x 210 mm in points (841.89 x 595.28 pt)


def _draw_border(c):
    margin = 18 * mm
    # Outer gold border
    c.setStrokeColor(GOLD)
    c.setLineWidth(3)
    c.rect(margin, margin, PAGE_W - 2 * margin, PAGE_H - 2 * margin)
    # Inner teal border
    inner = margin + 4 * mm
    c.setStrokeColor(TEAL)
    c.setLineWidth(0.8)
    c.rect(inner, inner, PAGE_W - 2 * inner, PAGE_H - 2 * inner)


def _draw_corner_ornaments(c):
    size = 10 * mm
    margin = 18 * mm
    positions = [
        (margin, margin),
        (PAGE_W - margin, margin),
        (margin, PAGE_H - margin),
        (PAGE_W - margin, PAGE_H - margin),
    ]
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    for x, y in positions:
        # Small square ornament at each corner
        c.rect(x - size / 2, y - size / 2, size, size)


def _draw_header(c):
    # Logo
    logo_size = 28 * mm
    logo_x = (PAGE_W - logo_size) / 2
    logo_y = PAGE_H - 38 * mm
    if os.path.exists(LOGO_PATH):
        c.drawImage(LOGO_PATH, logo_x, logo_y, width=logo_size, height=logo_size, preserveAspectRatio=True, mask="auto")

    # LUD CMT label
    c.setFont("Helvetica", 9)
    c.setFillColor(TEAL)
    label = "LET US DREAM  ·  CONFERENCE MANAGEMENT"
    c.drawCentredString(PAGE_W / 2, logo_y - 8 * mm, label)

    # Horizontal rule under header
    rule_y = logo_y - 13 * mm
    c.setStrokeColor(GOLD)
    c.setLineWidth(1)
    c.line(55 * mm, rule_y, PAGE_W - 55 * mm, rule_y)


def _draw_body(c, full_name, conference):
    center_y = PAGE_H / 2 + 2 * mm

    # "CERTIFICATE OF PARTICIPATION"
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(TEAL)
    c.drawCentredString(PAGE_W / 2, center_y + 38 * mm, "CERTIFICATE OF PARTICIPATION")

    # Thin decorative line under title
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.line(100 * mm, center_y + 35 * mm, PAGE_W - 100 * mm, center_y + 35 * mm)

    # "This is to certify that"
    c.setFont("Helvetica", 11)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W / 2, center_y + 26 * mm, "This is to certify that")

    # Participant name
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(DARK)
    c.drawCentredString(PAGE_W / 2, center_y + 13 * mm, full_name)

    # Name underline
    name_width = c.stringWidth(full_name, "Helvetica-Bold", 28)
    line_x1 = PAGE_W / 2 - name_width / 2 - 10
    line_x2 = PAGE_W / 2 + name_width / 2 + 10
    c.setStrokeColor(TEAL)
    c.setLineWidth(0.8)
    c.line(line_x1, center_y + 10 * mm, line_x2, center_y + 10 * mm)

    # "has participated in"
    c.setFont("Helvetica", 11)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W / 2, center_y + 3 * mm, "has participated in")

    # Conference title
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(TEAL)
    c.drawCentredString(PAGE_W / 2, center_y - 8 * mm, conference.title)

    # Venue & dates
    venue_line = f"{conference.venue}, {conference.location}"
    date_line = (
        f"{conference.start_date.strftime('%B %d, %Y')}  –  "
        f"{conference.end_date.strftime('%B %d, %Y')}"
    )
    c.setFont("Helvetica", 10)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W / 2, center_y - 16 * mm, venue_line)
    c.drawCentredString(PAGE_W / 2, center_y - 22 * mm, date_line)


def _draw_footer(c):
    footer_y = 30 * mm

    # Horizontal rule
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.line(55 * mm, footer_y + 8 * mm, PAGE_W - 55 * mm, footer_y + 8 * mm)

    # Issue date
    c.setFont("Helvetica", 9)
    c.setFillColor(MUTED)
    issued = f"Issued on {date.today().strftime('%B %d, %Y')}"
    c.drawCentredString(PAGE_W / 2, footer_y, issued)


def generate_certificate_pdf(full_name, conference):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))

    # Light teal background wash
    c.setFillColor(colors.HexColor("#f9fdfc"))
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    _draw_border(c)
    _draw_corner_ornaments(c)
    _draw_header(c)
    _draw_body(c, full_name, conference)
    _draw_footer(c)

    c.save()
    buffer.seek(0)
    return buffer.read()
