import streamlit as st
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Immunisation Schedule Generator", layout="centered")

# Custom CSS for screen display and print styling (fitted strictly for single-page A4)
st.markdown("""
<style>
@media print {
    @page {
        size: A4 portrait;
        margin: 10mm;
    }
    header, footer, nav, [data-testid="stSidebar"], [data-testid="stToolbar"], .no-print {
        display: none !important;
    }
    .print-container {
        display: block !important;
        width: 100% !important;
    }
    body {
        font-family: Arial, sans-serif;
        color: #000;
        background: #fff;
    }
    table {
        width: 100% !important;
        border-collapse: collapse !important;
    }
    th, td {
        border: 1px solid #000 !important;
        padding: 5px 8px !important;
        font-size: 13px !important;
    }
}

.vaccine-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
    background-color: #fff;
}
.vaccine-table th {
    background-color: #f1f3f4;
    border: 1px solid #333;
    padding: 8px 10px;
    text-align: left;
    font-size: 14px;
    font-weight: 600;
}
.vaccine-table td {
    border: 1px solid #333;
    padding: 6px 10px;
    font-size: 13px;
    vertical-align: middle;
}
.header-box {
    margin-bottom: 12px;
    font-size: 14px;
    line-height: 1.8;
}
</style>
""", unsafe_allow_html=True)

# App UI Header
st.title("Vaccination Chart Generator")
st.caption("National Immunisation Schedule — India")

# Input Form
with st.container():
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        dob_input = st.date_input("Baby's Date of Birth (DOB)*", value=date.today(), format="DD/MM/YYYY")
        child_name = st.text_input("Child Name (Optional)", "")
    with c2:
        address = st.text_input("Address / Hospital Reg. No. (Optional)", "")
        st.write("")
        st.write("")
        # JavaScript triggers native browser print dialog (Save as PDF)
        print_btn = st.button("🖨️ Print / Save as PDF", use_container_width=True, type="primary")
        if print_btn:
            st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
    
    st.divider()
    st.markdown('</div>', unsafe_allow_html=True)

# Schedule Calculation Logic
def format_dt(dt):
    return dt.strftime("%d-%b-%Y")

# Schedule groups matching the clinical chart format
schedule = [
    {
        "age": "Birth",
        "due": format_dt(dob_input),
        "vaccines": ["BCG", "HepB0", "bOPV-0"]
    },
    {
        "age": "6 Weeks",
        "due": format_dt(dob_input + timedelta(days=42)),
        "vaccines": ["bOPV-1", "Penta-1", "f-IPV-1", "RVV-1", "PCV-1"]
    },
    {
        "age": "10 Weeks",
        "due": format_dt(dob_input + timedelta(days=70)),
        "vaccines": ["bOPV-2", "Penta-2", "RVV-2"]
    },
    {
        "age": "14 Weeks",
        "due": format_dt(dob_input + timedelta(days=98)),
        "vaccines": ["bOPV-3", "Penta-3", "f-IPV-2", "RVV-3", "PCV-2"]
    },
    {
        "age": "9-12 Months",
        "due": format_dt(dob_input + relativedelta(months=9)),
        "vaccines": ["Measles-Rubella-1", "Vit-A", "JE-1*", "PCV-Booster", "f-IPV-3"]
    },
    {
        "age": "16-24 Months",
        "due": format_dt(dob_input + relativedelta(months=16)),
        "vaccines": ["DPT-Booster-1", "bOPV-Booster", "Vit-A", "Measles-Rubella-2", "JE-2*"]
    },
    {
        "age": "5-6 Years",
        "due": format_dt(dob_input + relativedelta(years=5)),
        "vaccines": ["DPT-Booster-2"]
    }
]

# Generate Printable Chart HTML
name_display = child_name if child_name.strip() else "&emsp;" * 15
addr_display = address if address.strip() else "&emsp;" * 20
dob_display = format_dt(dob_input)

html_rows = ""
for item in schedule:
    rowspan = len(item["vaccines"])
    for i, vac in enumerate(item["vaccines"]):
        if i == 0:
            html_rows += f"""
            <tr>
                <td rowspan="{rowspan}" style="font-weight:600; width:15%;">{item['age']}</td>
                <td style="width:25%;">{vac}</td>
                <td style="width:18%; font-weight:500;">{item['due']}</td>
                <td style="width:18%;"></td>
                <td style="width:24%;"></td>
            </tr>
            """
        else:
            html_rows += f"""
            <tr>
                <td>{vac}</td>
                <td style="font-weight:500;">{item['due']}</td>
                <td></td>
                <td></td>
            </tr>
            """

printable_content = f"""
<div class="print-container">
    <div style="text-align: center; margin-bottom: 10px;">
        <h3 style="margin: 0; padding: 0; text-transform: uppercase;">Vaccination Chart of Child</h3>
        <p style="margin: 3px 0 0 0; font-size: 13px; color: #555;">National Immunisation Schedule (India)</p>
    </div>

    <div class="header-box">
        <strong>Name:</strong> {name_display} &emsp;&emsp;
        <strong>D.O.B:</strong> {dob_display} &emsp;&emsp;
        <strong>Address:</strong> {addr_display}
    </div>

    <table class="vaccine-table">
        <thead>
            <tr>
                <th>Age</th>
                <th>Vaccine</th>
                <th>Due Date</th>
                <th>Given Date</th>
                <th>Remarks</th>
            </tr>
        </thead>
        <tbody>
            {html_rows}
        </tbody>
    </table>
    <div style="font-size: 11px; margin-top: 8px; color: #333;">
        *JE (Japanese Encephalitis) vaccine is introduced in select endemic districts.
    </div>
</div>
"""

st.markdown(printable_content, unsafe_allow_html=True)
