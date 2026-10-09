import io
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import streamlit as st
import pandas as pd

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

st.set_page_config(page_title="Vaccine Chart Generator", layout="centered")

st.title("Vaccination Chart Generator")
st.caption("National Immunisation Schedule — India")

# Input
with st.container():
    c1, c2 = st.columns(2)
    with c1:
        dob_input = st.date_input("Baby's Date of Birth (DOB)*", value=date.today(), format="DD/MM/YYYY")
        child_name = st.text_input("Child Name (Optional)", "")
    with c2:
        address = st.text_input("Address / Hospital Reg. No. (Optional)", "")

def format_dt(dt):
    return dt.strftime("%d-%b-%Y")

# Schedule intervals matching the clinical card
schedule_data = [
    {"age": "Birth", "due": format_dt(dob_input), "vaccines": ["BCG", "HepB0", "bOPV-0"]},
    {"age": "6 Weeks", "due": format_dt(dob_input + timedelta(days=42)), "vaccines": ["bOPV-1", "Penta-1", "f-IPV-1", "RVV-1", "PCV-1"]},
    {"age": "10 Weeks", "due": format_dt(dob_input + timedelta(days=70)), "vaccines": ["bOPV-2", "Penta-2", "RVV-2"]},
    {"age": "14 Weeks", "due": format_dt(dob_input + timedelta(days=98)), "vaccines": ["bOPV-3", "Penta-3", "f-IPV-2", "RVV-3", "PCV-2"]},
    {"age": "9-12 Months", "due": format_dt(dob_input + relativedelta(months=9)), "vaccines": ["Measles-Rubella-1", "Vit-A", "JE-1*", "PCV-Booster", "f-IPV-3"]},
    {"age": "16-24 Months", "due": format_dt(dob_input + relativedelta(months=16)), "vaccines": ["DPT-Booster-1", "bOPV-Booster", "Vit-A", "Measles-Rubella-2", "JE-2*"]},
    {"age": "5-6 Years", "due": format_dt(dob_input + relativedelta(years=5)), "vaccines": ["DPT-Booster-2"]}
]

# Display table cleanly on screen
screen_rows = []
for item in schedule_data:
    for vac in item["vaccines"]:
        screen_rows.append({
            "Age": item["age"],
            "Vaccine": vac,
            "Due Date": item["due"],
            "Given Date": "",
            "Remarks": ""
        })

df = pd.DataFrame(screen_rows)
st.dataframe(df, use_container_width=True, hide_index=True)

# Generate PDF Binary (Single-page A4)
def generate_pdf(child_name, address, dob_val, schedule_list):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=25,
        leftMargin=25,
        topMargin=20,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        alignment=1,
        spaceAfter=2
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        alignment=1,
        spaceAfter=10
    )
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        spaceAfter=10
    )

    elements = []
    elements.append(Paragraph("VACCINATION CHART OF CHILD", title_style))
    elements.append(Paragraph("National Immunisation Schedule (India)", subtitle_style))

    c_name = child_name.strip() if child_name.strip() else "_" * 25
    c_addr = address.strip() if address.strip() else "_" * 30
    meta_text = f"<b>Name:</b> {c_name} &nbsp;&nbsp;&nbsp;&nbsp; <b>D.O.B:</b> {format_dt(dob_val)} &nbsp;&nbsp;&nbsp;&nbsp; <b>Address:</b> {c_addr}"
    elements.append(Paragraph(meta_text, meta_style))

    # Build Table with exact Spanning & Borders
    table_data = [["Age", "Vaccine", "Due Date", "Given Date", "Remarks"]]
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F2F2F2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        ('TOPPADDING', (0, 0), (-1, 0), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8.5),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
    ]

    current_row = 1
    for block in schedule_list:
        v_count = len(block["vaccines"])
        start_row = current_row
        end_row = current_row + v_count - 1

        for i, vac in enumerate(block["vaccines"]):
            if i == 0:
                table_data.append([block["age"], vac, block["due"], "", ""])
            else:
                table_data.append(["", vac, block["due"], "", ""])
            current_row += 1

        # Span Age across all vaccines in that group
        table_style.append(('SPAN', (0, start_row), (0, end_row)))

    col_widths = [80, 130, 95, 110, 130]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle(table_style))
    elements.append(t)

    note_style = ParagraphStyle(
        'NoteText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        spaceBefore=6
    )
    elements.append(Paragraph("*JE (Japanese Encephalitis) vaccine is introduced in select endemic districts.", note_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# Trigger PDF Download
pdf_data = generate_pdf(child_name, address, dob_input, schedule_data)
file_label = f"Vaccination_Chart_{child_name.replace(' ', '_') or 'Child'}.pdf"

st.download_button(
    label="📄 Download Ready-to-Print PDF",
    data=pdf_data,
    file_name=file_label,
    mime="application/pdf",
    type="primary",
    use_container_width=True
)
