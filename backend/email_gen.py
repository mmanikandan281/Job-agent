import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Your personal details from .env
GITHUB_URL = os.getenv("GITHUB_URL")
LINKEDIN_URL = os.getenv("LINKEDIN_URL")
PORTFOLIO_URL = os.getenv("PORTFOLIO_URL")
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
YOUR_NAME = os.getenv("YOUR_NAME")
YOUR_PHONE = os.getenv("YOUR_PHONE")


def generate_email(
    jd_text: str,
    company: str,
    role: str,
    resume_context: str
) -> dict:
    """
    Generates a professional job application email.
    Returns subject and body separately.
    """

    prompt = f"""
You are a professional job application email writer.

Write a compelling job application email based on the following details.
The email should sound human, genuine, and confident — not robotic or generic.

STRICT RULES:
- Follow the exact structure below
- Keep it concise but impactful (250-300 words for body)
- Do NOT use buzzwords like "leverage", "synergy", "passionate", "excited"
- Do NOT start with "I'm excited" or "I hope this email finds you well"
- Open with a confident specific statement about the role or company
- Use short punchy sentences
- ALWAYS mention internship experience with company name and what was done there
- ALWAYS mention specific project names from the resume
- Show results and impact not just responsibilities
- Sound like a sharp developer who knows their worth
- Do NOT sound desperate or over-humble
- Do NOT explain internship tasks in detail, just mention company, role and overall impact in one line
- Keep internship section HIGH LEVEL — like a summary not a report
- End with the signature block exactly as shown

JOB DETAILS:
Company: {company}
Role: {role}
Job Description:
{jd_text}

CANDIDATE BACKGROUND (from resume):
{resume_context}

IMPORTANT EXTRACTION RULES:
- Look for any internship or work experience in the candidate background
- Extract the internship company name, role, and what they did
- Extract specific project names and technologies used
- Match these to the job requirements
- If internship is mentioned anywhere in background, ALWAYS include it

CANDIDATE PERSONAL DETAILS:
Name: {YOUR_NAME}
Email: {GMAIL_ADDRESS}
Phone: {YOUR_PHONE}
LinkedIn: {LINKEDIN_URL}
GitHub: {GITHUB_URL}
Portfolio: {PORTFOLIO_URL}

REQUIRED EMAIL STRUCTURE:
Subject: Application for [Role] at [Company] | {YOUR_NAME}

Dear Hiring Team,

[Opening - one confident sentence about the role, no "I'm excited"]

[Internship paragraph - mention internship company name and role briefly,
give ONE high level sentence about what kind of work you did overall,
DO NOT list every single task or bullet point,
keep it to 2-3 sentences maximum for ALL internships combined]

[Projects paragraph - mention 1-2 specific project names that match the JD,
what problem they solved, technologies used]

[Skills + closing - relevant technical skills matching JD, availability, thank them]

Kind regards,
{YOUR_NAME}
{GMAIL_ADDRESS}
{YOUR_PHONE}
LinkedIn: {LINKEDIN_URL}
GitHub: {GITHUB_URL}
Portfolio: {PORTFOLIO_URL}

FORMATTING RULES:
- Each paragraph MUST be separated by a blank line
- Maximum 4 paragraphs in body
- Maximum 3 sentences per paragraph
- Total email body under 200 words
- No bullet points inside email
- No sub-points or lists

Return the response in this exact format:
SUBJECT: [subject line here]
BODY:
[full email body here]
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    raw = response.choices[0].message.content.strip()

    # Split subject and body
    subject = ""
    body = ""

    if "SUBJECT:" in raw and "BODY:" in raw:
        parts = raw.split("BODY:")
        subject_part = parts[0].replace("SUBJECT:", "").strip()
        subject = subject_part
        body = parts[1].strip()
    else:
        # Fallback if model doesn't follow format
        subject = f"Application for {role} at {company}"
        body = raw

    return {
        "subject": subject,
        "body": body
    }


# ─────────────────────────────────────────
# TEST
# ─────────────────────────────────────────
if __name__ == "__main__":

    # Simulate data coming from jd_parser + rag
    test_company = "Google"
    test_role = "Full Stack Developer"

    test_jd = """
    We are hiring a Full Stack Developer.
    Requirements:
    - 1-2 years experience in React and Node.js
    - MongoDB or PostgreSQL
    - REST API development
    - Good problem solving skills
    Send resume to careers@google.com
    """

    test_resume_context = """
    Completed internship at Assimilate Technologies as Software Developer Intern.
    Worked on backend APIs using Node.js and database integration.
    Built projects using React, Tailwind CSS, MongoDB.
    Strong foundation in full stack development.
    Final year MCA student at Lead College of Management, Palakkad.
    """

    print("Generating email...")
    result = generate_email(
        jd_text=test_jd,
        company=test_company,
        role=test_role,
        resume_context=test_resume_context
    )

    print("\n" + "=" * 50)
    print("SUBJECT:", result["subject"])
    print("=" * 50)
    print(result["body"])
    print("=" * 50)