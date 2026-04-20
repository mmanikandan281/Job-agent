import os
import base64
import pickle
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# Gmail API scope - only sending permission
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.pkl"


# ─────────────────────────────────────────
# Get Gmail service
# First time: opens browser for permission
# After that: uses saved token
# ─────────────────────────────────────────
def get_gmail_service():
    creds = None

    # Load saved token if exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    # If no valid token, get a new one
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh existing token
            creds.refresh(Request())
        else:
            # First time - open browser
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save token for next time
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    service = build('gmail', 'v1', credentials=creds)
    return service


# ─────────────────────────────────────────
# Build email with attachment
# ─────────────────────────────────────────
def build_email(to: str, subject: str, body: str, resume_path: str) -> str:
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = os.getenv("GMAIL_ADDRESS")
    message['subject'] = subject

    # Add email body
    import re
    body_formatted = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', body)

    paragraphs = body_formatted.split('\n\n')
    html_paragraphs = ""
    for para in paragraphs:
        para = para.replace('\n', '<br>')
        html_paragraphs += f'<p style="margin: 0 0 18px 0; text-align: left;">{para}</p>'

    html_body = f"""<html>
    <body style="font-family: Arial, sans-serif; font-size: 15px; line-height: 1.7; color: #222222; margin: 0; padding: 0;">
    <div style="padding: 10px 0;">
    {html_paragraphs}
    </div>
    </body>
    </html>"""
    message.attach(MIMEText(html_body, 'html'))

    # Attach resume PDF
    if resume_path and os.path.exists(resume_path):
        with open(resume_path, "rb") as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            filename = os.path.basename(resume_path)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={filename}'
            )
            message.attach(part)
        print(f"✅ Resume attached: {filename}")
    else:
        print("⚠️ No resume attached - file not found")

    # Encode to base64 for Gmail API
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return raw


# ─────────────────────────────────────────
# Send email
# ─────────────────────────────────────────
def send_email(
    to: str,
    subject: str,
    body: str,
    resume_path: str
) -> dict:
    try:
        service = get_gmail_service()

        raw_message = build_email(to, subject, body, resume_path)

        sent = service.users().messages().send(
            userId="me",
            body={"raw": raw_message}
        ).execute()

        print(f"✅ Email sent successfully!")
        print(f"Message ID: {sent['id']}")

        return {
            "success": True,
            "message_id": sent['id'],
            "sent_to": to
        }

    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


# ─────────────────────────────────────────
# TEST
# ─────────────────────────────────────────
if __name__ == "__main__":

    print("=" * 40)
    print("Testing Gmail Send")
    print("=" * 40)

    # Test email - sending to yourself first to verify
    test_to = os.getenv("GMAIL_ADDRESS")  # sends to yourself
    test_subject = "Test - Job Agent Email"
    test_body = """Dear Hiring Team,

This is a test email from my Job Agent app.

Kind regards,
Manikandan M"""

    # Use any resume from your resumes folder
    test_resume = "resumes/Res_Fullstack.pdf"

    print(f"Sending test email to: {test_to}")
    print("A browser will open first time for Google permission...")
    print()

    result = send_email(
        to=test_to,
        subject=test_subject,
        body=test_body,
        resume_path=test_resume
    )

    print()
    if result["success"]:
        print("✅ Check your Gmail inbox!")
    else:
        print(f"❌ Error: {result['error']}")