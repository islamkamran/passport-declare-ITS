from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
import base64
import io

# ReportLab imports for better PDF layout
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

router = APIRouter()

# Create pdf_output folder if not exists
pdf_folder = Path("pdf_output")
pdf_folder.mkdir(exist_ok=True)


# Pydantic schema for validation
class PassportForm(BaseModel):
    date: str
    designation: str
    joiningDate: str
    nationality: str
    passportNumber: str
    issueLocation: str
    issueDate: str
    expiryDate: str
    employeeName: str
    employeeCode: str
    signature: str   # Base64 encoded string (from canvas)


@router.post("/api/passport")
async def create_passport(form: PassportForm, request: Request):
    """
    Accepts passport form data, displays it, and stores a professional PDF in pdf_output.
    """
    try:
        # PDF file path
        filename = f"passport_{form.employeeCode}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        pdf_path = pdf_folder / filename

        # Setup document
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            rightMargin=50, leftMargin=50,
            topMargin=50, bottomMargin=50
        )
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            'title',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=1,  # center
            textColor=colors.HexColor("#0a4a82")
        )
        story.append(Paragraph("Passport Declaration Form", title_style))
        story.append(Spacer(1, 20))

        # Company Info
        story.append(Paragraph("<b>Indus Technical Services LLC</b>", styles['Normal']))
        story.append(Paragraph("P.O. Box 241075 Dubai, UAE", styles['Normal']))
        story.append(Spacer(1, 20))

        # Letter Content
        story.append(Paragraph(f"Date: <b>{form.date}</b>", styles['Normal']))
        story.append(Spacer(1, 10))

        story.append(Paragraph(
            f"I have joined Indus Technical Services LLC as a <b>{form.designation}</b> "
            f"on <b>{form.joiningDate}</b>.", styles['Normal']
        ))
        story.append(Spacer(1, 10))

        story.append(Paragraph(
            "I request the company to retain my passport for safekeeping. "
            "The details of my passport are as follows:",
            styles['Normal']
        ))
        story.append(Spacer(1, 15))

        # Passport details in a table
        data = [
            ["Nationality", form.nationality, "Passport Number", form.passportNumber],
            ["Issued Location", form.issueLocation, "Date of Issue", form.issueDate],
            ["Date of Expiry", form.expiryDate, "", ""],
        ]
        table = Table(data, colWidths=[100, 150, 120, 150])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
        ]))
        story.append(table)
        story.append(Spacer(1, 20))

        # Closing paragraph
        story.append(Paragraph(
            "I agree that my passport will be handed over to me whenever required by me "
            "as per my request and the same will be returned to the company on the mentioned date.",
            styles['Normal']
        ))
        story.append(Spacer(1, 40))

        # Employee details
        story.append(Paragraph(f"Employee Name: <b>{form.employeeName}</b>", styles['Normal']))
        story.append(Paragraph(f"Employee Code: <b>{form.employeeCode}</b>", styles['Normal']))
        story.append(Spacer(1, 20))

        # Signature
        signature_data = form.signature.split(",")[1]  # remove prefix
        signature_bytes = base64.b64decode(signature_data)
        signature_img = io.BytesIO(signature_bytes)

        img = Image(signature_img, width=120, height=60)
        story.append(Paragraph("Signature:", styles['Normal']))
        story.append(img)

        # Build PDF
        doc.build(story)

        return JSONResponse(
            content={
                "message": "Form data received and professional PDF generated",
                "data": form.dict(),
                "pdf_file": str(pdf_path)
            }
        )

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
