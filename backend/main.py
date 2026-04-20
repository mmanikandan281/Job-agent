import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from jd_parser import parse_jd, parse_jd_from_pdf
from rag import match_resumes, get_context, setup_resumes, process_new_resume
from email_gen import generate_email
from gmail_send import send_email

load_dotenv()

app = FastAPI()

# Allow React frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

RESUME_FOLDER = "resumes"


# ─────────────────────────────────────────
# Request models
# ─────────────────────────────────────────
class JDTextRequest(BaseModel):
    jd_text: str

class MatchResumeRequest(BaseModel):
    jd_text: str

class GenerateEmailRequest(BaseModel):
    jd_text: str
    company: str
    role: str
    resume_name: str

class SendEmailRequest(BaseModel):
    to: str
    subject: str
    body: str
    resume_path: str


# ─────────────────────────────────────────
# Health check
# ─────────────────────────────────────────
@app.get("/")
def home():
    return {"status": "Job Agent is running!"}


# ─────────────────────────────────────────
# Parse JD from text
# ─────────────────────────────────────────
@app.post("/parse-jd")
def parse_jd_endpoint(request: JDTextRequest):
    try:
        result = parse_jd(request.jd_text)
        return {
            "success": True,
            "hr_email": result.get("hr_email", "not_found"),
            "company": result.get("company", "not_found"),
            "role": result.get("role", "not_found")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─────────────────────────────────────────
# Parse JD from PDF file
# ─────────────────────────────────────────
@app.post("/parse-jd-pdf")
async def parse_jd_pdf_endpoint(file: UploadFile = File(...)):
    try:
        # Save uploaded PDF temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        # Parse the PDF
        result = parse_jd_from_pdf(temp_path)

        # Delete temp file
        os.remove(temp_path)

        return {
            "success": True,
            "hr_email": result.get("hr_email", "not_found"),
            "company": result.get("company", "not_found"),
            "role": result.get("role", "not_found")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─────────────────────────────────────────
# Match resumes against JD
# ─────────────────────────────────────────
@app.post("/match-resumes")
def match_resumes_endpoint(request: MatchResumeRequest):
    try:
        matches = match_resumes(request.jd_text)
        return {
            "success": True,
            "matches": matches
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─────────────────────────────────────────
# Generate email
# ─────────────────────────────────────────
@app.post("/generate-email")
def generate_email_endpoint(request: GenerateEmailRequest):
    try:
        # Get relevant context from matched resume
        context = get_context(request.resume_name, request.jd_text)

        # Generate email
        result = generate_email(
            jd_text=request.jd_text,
            company=request.company,
            role=request.role,
            resume_context=context
        )

        return {
            "success": True,
            "subject": result["subject"],
            "body": result["body"]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─────────────────────────────────────────
# Send email
# ─────────────────────────────────────────
@app.post("/send-email")
def send_email_endpoint(request: SendEmailRequest):
    try:
        result = send_email(
            to=request.to,
            subject=request.subject,
            body=request.body,
            resume_path=request.resume_path
        )
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─────────────────────────────────────────
# Get all resumes list
# ─────────────────────────────────────────
@app.get("/resumes")
def get_resumes():
    try:
        resumes = []
        if os.path.exists(RESUME_FOLDER):
            for file in os.listdir(RESUME_FOLDER):
                if file.endswith(".pdf"):
                    resumes.append({
                        "name": file.replace(".pdf", ""),
                        "filename": file,
                        "path": f"{RESUME_FOLDER}/{file}"
                    })
        return {
            "success": True,
            "resumes": resumes
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─────────────────────────────────────────
# Upload new resume
# ─────────────────────────────────────────
@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    try:
        os.makedirs(RESUME_FOLDER, exist_ok=True)

        # Save PDF to resumes folder
        file_path = os.path.join(RESUME_FOLDER, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Process it for RAG immediately
        resume_name = file.filename.replace(".pdf", "")
        process_new_resume(file_path, resume_name)

        return {
            "success": True,
            "message": f"{file.filename} uploaded and processed!",
            "resume_name": resume_name,
            "path": file_path
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    
# Delete resume endpoint
@app.delete("/resume/{resume_name}")
def delete_resume(resume_name: str):
    try:
        # Delete PDF file
        pdf_path = os.path.join(RESUME_FOLDER, f"{resume_name}.pdf")
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        # Delete vector store
        vector_path = os.path.join("vector_store", resume_name)
        if os.path.exists(vector_path):
            shutil.rmtree(vector_path)

        return {"success": True, "message": f"{resume_name} deleted!"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─────────────────────────────────────────
# Startup - process any unprocessed resumes
# ─────────────────────────────────────────
@app.on_event("startup")
def startup_event():
    print("Starting Job Agent API...")
    setup_resumes()
    print("Ready!")