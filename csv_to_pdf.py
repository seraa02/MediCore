import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# -----------------------------
# CONFIG
# -----------------------------
PATIENTS_CSV = "patients.csv"
OBSERVATIONS_CSV = "observations.csv"
OUTPUT_DIR = "reports"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------
# LOAD DATA
# -----------------------------
patients = pd.read_csv(PATIENTS_CSV)
observations = pd.read_csv(OBSERVATIONS_CSV)

# -----------------------------
# FILTER LAB OBSERVATIONS
# -----------------------------
# Keep only rows that have numeric values
observations = observations[observations["VALUE"].notna()]

# -----------------------------
# STYLES
# -----------------------------
styles = getSampleStyleSheet()

# -----------------------------
# GENERATE REPORTS
# -----------------------------
for _, patient in patients.iterrows():

    patient_id = patient["Id"]

    patient_obs = observations[observations["PATIENT"] == patient_id]

    # Skip patients with no observations
    if patient_obs.empty:
        continue

    # Patient Info
    first_name = str(patient.get("FIRST", ""))
    last_name = str(patient.get("LAST", ""))
    gender = str(patient.get("GENDER", ""))
    birthdate = str(patient.get("BIRTHDATE", ""))

    filename = os.path.join(
        OUTPUT_DIR,
        f"{patient_id}.pdf"
    )

    doc = SimpleDocTemplate(
        filename,
        pagesize=letter
    )

    elements = []

    # -----------------------------
    # HEADER
    # -----------------------------
    title = Paragraph(
        "<b>SYNTHETIC LAB REPORT</b>",
        styles["Title"]
    )

    elements.append(title)
    elements.append(Spacer(1, 20))

    # -----------------------------
    # PATIENT DETAILS
    # -----------------------------
    patient_details = f"""
    <b>Patient ID:</b> {patient_id}<br/>
    <b>Name:</b> {first_name} {last_name}<br/>
    <b>Gender:</b> {gender}<br/>
    <b>Date of Birth:</b> {birthdate}<br/>
    """

    elements.append(
        Paragraph(patient_details, styles["BodyText"])
    )

    elements.append(Spacer(1, 20))

    # -----------------------------
    # LAB TABLE
    # -----------------------------
    table_data = [
        ["Test", "Value", "Units", "Date"]
    ]

    for _, obs in patient_obs.iterrows():

        test_name = str(obs.get("DESCRIPTION", "Unknown"))
        value = str(obs.get("VALUE", ""))
        units = str(obs.get("UNITS", ""))
        date = str(obs.get("DATE", ""))

        table_data.append([
            test_name,
            value,
            units,
            date
        ])

    table = Table(table_data, repeatRows=1)

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ])
    )

    elements.append(table)

    elements.append(Spacer(1, 20))

    # -----------------------------
    # FOOTER
    # -----------------------------
    footer = Paragraph(
        "This is a synthetic lab report generated using Synthea data.",
        styles["Italic"]
    )

    elements.append(footer)

    # -----------------------------
    # BUILD PDF
    # -----------------------------
    doc.build(elements)

print(f"Lab reports generated in: {OUTPUT_DIR}")