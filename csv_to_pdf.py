import os
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet

# ==================================================
# PATHS
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

PATIENTS_CSV = os.path.join(
    PROJECT_ROOT,
    "synthea",
    "output",
    "csv",
    "patients.csv"
)

OBSERVATIONS_CSV = os.path.join(
    PROJECT_ROOT,
    "synthea",
    "output",
    "csv",
    "observations.csv"
)

REPORTS_DIR = os.path.join(
    BASE_DIR,
    "reports"
)

os.makedirs(REPORTS_DIR, exist_ok=True)

# ==================================================
# LOAD DATA
# ==================================================

print("Loading patients...")
patients = pd.read_csv(PATIENTS_CSV)

print("Loading observations...")
observations = pd.read_csv(
    OBSERVATIONS_CSV,
    low_memory=False
)

print(f"Patients loaded: {len(patients)}")
print(f"Observations loaded: {len(observations)}")

styles = getSampleStyleSheet()

# ==================================================
# GENERATE ONE PDF PER PATIENT
# ==================================================

for index, patient in patients.iterrows():

    patient_id = patient["Id"]

    first_name = str(patient.get("FIRST", ""))
    last_name = str(patient.get("LAST", ""))

    patient_name = f"{first_name} {last_name}".strip()

    print(
        f"Generating {index+1}/{len(patients)} : {patient_name}"
    )

    # ------------------------------------------
    # Create PDF file
    # ------------------------------------------

    pdf_path = os.path.join(
        REPORTS_DIR,
        f"{patient_id}.pdf"
    )

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter
    )

    elements = []

    # ------------------------------------------
    # Hospital Header
    # ------------------------------------------

    elements.append(
        Paragraph(
            "MediCore Diagnostic Laboratory",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            "Comprehensive Patient Laboratory Report",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 20))

    # ------------------------------------------
    # Patient Information
    # ------------------------------------------

    elements.append(
        Paragraph(
            "<b>PATIENT INFORMATION</b>",
            styles["Heading2"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Name:</b> {patient_name}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Patient ID:</b> {patient_id}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Gender:</b> {patient.get('GENDER','')}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Date of Birth:</b> {patient.get('BIRTHDATE','')}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 20))

    # ------------------------------------------
    # Clinical Summary
    # ------------------------------------------

    elements.append(
        Paragraph(
            "<b>CLINICAL SUMMARY</b>",
            styles["Heading2"]
        )
    )

    summary = f"""
    This laboratory report contains all recorded observations
    and measurements available for patient {patient_name}.
    Results should be interpreted in conjunction with clinical
    history, physician evaluation, and other diagnostic findings.
    """

    elements.append(
        Paragraph(summary, styles["Normal"])
    )

    elements.append(Spacer(1, 20))

    # ------------------------------------------
    # Lab Results
    # ------------------------------------------

    patient_obs = observations[
        observations["PATIENT"] == patient_id
    ]

    if len(patient_obs) > 0:

        elements.append(
            Paragraph(
                "<b>LABORATORY RESULTS</b>",
                styles["Heading2"]
            )
        )

        elements.append(Spacer(1, 10))

        table_data = [
            [
                "Date",
                "Test Name",
                "Result",
                "Units"
            ]
        ]

        for _, row in patient_obs.iterrows():

            table_data.append([
                str(row.get("DATE", ""))[:10],
                str(row.get("DESCRIPTION", "")),
                str(row.get("VALUE", "")),
                str(row.get("UNITS", ""))
            ])

        table = Table(
            table_data,
            colWidths=[70, 280, 80, 80]
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0,0),
                    (-1,0),
                    colors.lightgrey
                ),
                (
                    "GRID",
                    (0,0),
                    (-1,-1),
                    1,
                    colors.black
                ),
                (
                    "FONTNAME",
                    (0,0),
                    (-1,0),
                    "Helvetica-Bold"
                ),
                (
                    "VALIGN",
                    (0,0),
                    (-1,-1),
                    "TOP"
                ),
            ])
        )

        elements.append(table)

    else:

        elements.append(
            Paragraph(
                "No observations found.",
                styles["Normal"]
            )
        )

    # ------------------------------------------
    # Footer
    # ------------------------------------------

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            "Electronically Generated Report - MediCore",
            styles["Italic"]
        )
    )

    # ------------------------------------------
    # Save PDF
    # ------------------------------------------

    doc.build(elements)

print()
print("DONE")
print(f"Reports saved to: {REPORTS_DIR}")

# pip3 install pandas reportlab
# pip3 show reportlab
# pip3 show pandas

# python3 csv_to_pdf.py