from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import base64
import os
import uuid
from datetime import datetime
from xhtml2pdf import pisa
import io

# Create the FastAPI app
app = FastAPI(title="Passport Declaration API")

# Configure CORS to allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories for storing files
os.makedirs("pdf_files", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Set up templates
templates = Jinja2Templates(directory="templates")

# Define the data model for the form submission
class PassportDeclaration(BaseModel):
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
    signature: str  # Base64 encoded signature

# Serve the HTML form
@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("passport.html", {"request": request})

# API endpoint to handle form submission and PDF generation
@app.post("/api/passport")
async def submit_passport_declaration(request: Request):
    try:
        # Parse the JSON data from the request body
        form_data = await request.json()
        
        # Create declaration object
        declaration = PassportDeclaration(**form_data)
        
        # Generate a unique filename
        filename = f"passport_declaration_{declaration.employeeCode}_{uuid.uuid4().hex[:8]}.pdf"
        filepath = os.path.join("pdf_files", filename)
        
        # Create HTML content for PDF
        html_content = generate_pdf_html(declaration)
        
        # Generate PDF using xhtml2pdf
        with open(filepath, "wb") as f:
            pisa_status = pisa.CreatePDF(html_content, dest=f)
        
        if pisa_status.err:
            raise HTTPException(status_code=500, detail="PDF generation failed")
        
        # Return the PDF file path for download
        return {
            "message": "Passport declaration submitted successfully",
            "pdf_file": filename,
            "download_url": f"/download/{filename}",
            "view_url": f"/view/{filename}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

# Endpoint to download the generated PDF
@app.get("/download/{filename}")
async def download_pdf(filename: str):
    filepath = os.path.join("pdf_files", filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=filepath,
        filename=f"passport_declaration_{datetime.now().strftime('%Y%m%d')}.pdf",
        media_type="application/pdf"
    )

# Endpoint to view the generated PDF in browser
@app.get("/view/{filename}")
async def view_pdf(filename: str):
    filepath = os.path.join("pdf_files", filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=filepath,
        media_type="application/pdf"
    )

# Function to generate HTML for PDF conversion
def generate_pdf_html(declaration: PassportDeclaration) -> str:
    # Format dates for display
    def format_date(date_str):
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%d %B, %Y")
        except:
            return date_str
    
    # Create the HTML content for the PDF
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Passport Declaration - {declaration.employeeName}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                border-bottom: 2px solid #1a5ca3;
                padding-bottom: 20px;
            }}
            .company-name {{
                font-size: 24px;
                font-weight: bold;
                color: #1a5ca3;
            }}
            .document-title {{
                font-size: 20px;
                margin-top: 10px;
            }}
            .section {{
                margin-bottom: 20px;
            }}
            .section-title {{
                font-size: 18px;
                color: #1a5ca3;
                border-bottom: 1px solid #ddd;
                padding-bottom: 5px;
                margin-bottom: 10px;
            }}
            .info-row {{
                display: flex;
                margin-bottom: 8px;
            }}
            .info-label {{
                width: 200px;
                font-weight: bold;
            }}
            .info-value {{
                flex: 1;
            }}
            .signature-area {{
                margin-top: 40px;
                text-align: center;
            }}
            .signature-img {{
                max-width: 300px;
                border: 1px solid #ddd;
                margin-bottom: 10px;
            }}
            .footer {{
                margin-top: 50px;
                text-align: center;
                font-size: 14px;
                color: #777;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="company-name">Indus Technical Services LLC</div>
            <div class="document-title">PASSPORT DECLARATION</div>
        </div>
        
        <div class="section">
            <div class="info-row">
                <div class="info-label">Date:</div>
                <div class="info-value">{format_date(declaration.date)}</div>
            </div>
        </div>
        
        <div class="section">
            <p>Dear Sir/Madam,</p>
            <p>I have joined Indus Technical Services LLC as a {declaration.designation} (Designation) on {format_date(declaration.joiningDate)} (Date of Joining).</p>
            <p>I request the company to retain my passport for safekeeping. The details of my passport are as follows;</p>
        </div>
        
        <div class="section">
            <div class="section-title">Passport Details</div>
            <div class="info-row">
                <div class="info-label">Nationality:</div>
                <div class="info-value">{declaration.nationality}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Passport Number:</div>
                <div class="info-value">{declaration.passportNumber}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Issued Location:</div>
                <div class="info-value">{declaration.issueLocation}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Date of Issue:</div>
                <div class="info-value">{format_date(declaration.issueDate)}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Date of Expiry:</div>
                <div class="info-value">{format_date(declaration.expiryDate)}</div>
            </div>
        </div>
        
        <div class="section">
            <p>I agree that my passport will be handed over to me whenever required by me as per my request and same will be returned to the company on the mentioned date.</p>
        </div>
        
        <div class="section">
            <div class="section-title">Employee Information</div>
            <div class="info-row">
                <div class="info-label">Employee Name:</div>
                <div class="info-value">{declaration.employeeName}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Employee Code:</div>
                <div class="info-value">{declaration.employeeCode}</div>
            </div>
        </div>
        
        <div class="signature-area">
            <div>Signature:</div>
            <img class="signature-img" src="{declaration.signature}" alt="Signature">
        </div>
        
        <div class="footer">
            <p>Indus Technical Services LLC &copy; {datetime.now().year}. All rights reserved.</p>
            <p>P.O. Box 241075 Dubai, UAE</p>
        </div>
    </body>
    </html>
    """
    
    return html

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)