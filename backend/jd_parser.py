import os
from dotenv import load_dotenv
from groq import Groq
import json
import re
from pypdf import PdfReader

# Load your .env file
load_dotenv()

# Connect to Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def parse_jd(jd_text: str):
    prompt = f"""
    Read this job description carefully and extract the following information.
    Return ONLY a JSON object, nothing else, no extra text, no markdown.

    Extract:
    1. hr_email: the email address to send application to (if not found return "not_found")
    2. company: the company name
    3. role: the job role/position

    Job Description:
    {jd_text}

    Return format:
    {{
        "hr_email": "email here",
        "company": "company name here",
        "role": "role here"
    }}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    response_text = response.choices[0].message.content.strip()
    response_text = re.sub(r"```json|```", "", response_text).strip()
    result = json.loads(response_text)
    return result


def parse_jd_from_pdf(pdf_path: str):
    reader = PdfReader(pdf_path)
    extracted_text = ""

    for page in reader.pages:
        extracted_text += page.extract_text()

    if not extracted_text.strip():
        return {
            "hr_email": "not_found",
            "company": "not_found",
            "role": "not_found",
            "error": "PDF has no readable text"
        }

    return parse_jd(extracted_text)

# -----------------------Testing Dummy Details-----------------------

# if __name__ == "__main__":

#     print("=" * 40)
#     print("TEST 1 - Plain Text JD")
#     print("=" * 40)

#     test_jd = """
#     We are looking for a Full Stack Developer at TechCorp Solutions.
    
#     Requirements:
#     - 2+ years experience in React and Node.js
#     - Knowledge of MongoDB
#     - Good communication skills
    
#     About us:
#     TechCorp Solutions is a leading software company based in Bangalore.
    
#     To apply send your resume to careers@techcorp.com
#     """

#     result = parse_jd(test_jd)
#     print(f"HR Email  : {result['hr_email']}")
#     print(f"Company   : {result['company']}")
#     print(f"Role      : {result['role']}")

#     print()
#     print("=" * 40)
#     print("TEST 2 - PDF JD")
#     print("=" * 40)

#     pdf_path = "resumes/sample_jd.pdf"

#     if os.path.exists(pdf_path):
#         result2 = parse_jd_from_pdf(pdf_path)
#         print(f"HR Email  : {result2['hr_email']}")
#         print(f"Company   : {result2['company']}")
#         print(f"Role      : {result2['role']}")
#     else:
#         print("No sample PDF found, skipping PDF test")