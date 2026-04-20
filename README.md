# 🤖 Job Agent — AI-Powered Job Application Automation

A personal AI tool that reads job descriptions, matches your best resume, writes tailored emails, and sends them directly from your Gmail — all in one click.

---

## ✨ Features

- 📋 **JD Parser** — Paste text or upload PDF job descriptions
- 🧠 **Smart Resume Matching** — AI scores and ranks your resumes against the JD
- ✉️ **AI Email Writer** — Generates professional, tailored job application emails
- 📎 **Auto Attachment** — Automatically attaches the best matched resume
- 📤 **Gmail Integration** — Sends directly from your Gmail account
- 📁 **Resume Manager** — Upload, view and delete resumes from the UI

---
## UI Output

### Main Application Interface
<img width="1251" height="895" alt="Job Agent Main Interface - Step-by-step application workflow with progress bar" src="https://github.com/user-attachments/assets/ddc147fa-8686-4e9f-ac55-35a5b8a8de3e" />

### Job Description Input Step
<img width="1027" height="917" alt="JD Input Form - Paste job description text or upload PDF" src="https://github.com/user-attachments/assets/0aad1234-d7a6-49d4-84bd-d1943029a2c7" />

### Resume Matching Step
<img width="964" height="870" alt="Resume Selection - AI-ranked resume matches with scores" src="https://github.com/user-attachments/assets/8d802758-1916-4293-ae18-7adb4356329e" />

### Email Preview Step
<img width="1046" height="802" alt="Email Preview - Review AI-generated application email before sending" src="https://github.com/user-attachments/assets/9325fbe0-b85c-409e-b489-0bf4b76aafb8" />

### Success Confirmation
<img width="1390" height="684" alt="Application Sent - Success confirmation with next steps" src="https://github.com/user-attachments/assets/83b18dac-8916-4838-b959-0c28268ffe30" />

## 🔧 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React.js |
| Backend | FastAPI (Python) |
| AI / LLM | Groq API (Llama 3.3 70B) |
| Embeddings | HuggingFace Sentence Transformers |
| Vector Store | FAISS |
| Email | Gmail API (OAuth2) |

---

## 🗂️ Project Structure

```
job-agent/
│
├── backend/
│   ├── main.py              # All API routes
│   ├── jd_parser.py         # Extract HR email, company, role from JD
│   ├── rag.py               # Resume matching with FAISS + Groq scoring
│   ├── email_gen.py         # AI email generation using Groq
│   ├── gmail_send.py        # Gmail API integration
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # API keys and personal details
│   ├── credentials.json     # Gmail OAuth credentials
│   ├── resumes/             # Your resume PDFs
│   └── vector_store/        # Auto-generated FAISS embeddings
│
└── frontend/
    ├── src/
    │   ├── App.js
    │   └── components/
    │       ├── JDInput.js        # Step 1 - Paste or upload JD
    │       ├── ResumeSelector.js # Step 2 - AI resume suggestions
    │       ├── EmailPreview.js   # Step 3 - Review and send email
    │       ├── Success.js        # Step 4 - Confirmation
    │       └── Resumes.js        # Resume management modal
    └── package.json
```

---

## 🔄 How It Works

```
┌─────────────────────────────────────────────────────┐
│                    YOUR APP (React)                 │
│                                                     │
│  Step 1: Paste JD text OR upload JD as PDF          │
│  Step 2: AI shows resume match scores               │
│  Step 3: Review AI-generated email                  │
│  Step 4: One click → Email sent with resume!        │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                  FASTAPI BACKEND                    │
│                                                     │
│  /parse-jd       → Extract HR email, company, role  │
│  /match-resumes  → Score resumes against JD         │
│  /generate-email → Write tailored email with AI     │
│  /send-email     → Send via Gmail API               │
│  /resumes        → List all uploaded resumes        │
│  /upload-resume  → Upload new resume PDF            │
│  /resume/{name}  → Delete a resume                  │
└───────┬──────────────────────┬──────────────────────┘
        │                      │
        ▼                      ▼
┌──────────────┐    ┌─────────────────────┐
│  GROQ API    │    │     GMAIL API       │
│              │    │                     │
│ jd_parser    │    │  OAuth2 token saved │
│ rag scoring  │    │  Sends from your    │
│ email writer │    │  Gmail account      │
└──────┬───────┘    └─────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│                   RAG PIPELINE                      │
│                                                     │
│  resume_1.pdf  →  chunks  →  FAISS embeddings       │
│  resume_2.pdf  →  chunks  →  FAISS embeddings       │
│  resume_3.pdf  →  chunks  →  FAISS embeddings       │
│                                                     │
│  JD comes in → Groq AI scores each resume           │
│  Returns ranked list with match percentages         │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Setup & Installation

### Prerequisites

- Python 3.10+
- Node.js 16+
- A Gmail account
- Groq API key (free at console.groq.com)

---

### 1. Clone the Repository

```bash
git clone https://github.com/mmanikandan281/Job-agent.git
cd job-agent
```

---

### 2. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install fastapi uvicorn python-dotenv langchain langchain-google-genai langchain-community faiss-cpu sentence-transformers pypdf google-auth google-auth-oauthlib google-api-python-client groq python-multipart
```

---

### 3. Configure Environment Variables

Create a `.env` file inside `backend/`:

```env
GROQ_API_KEY=your_groq_api_key_here

YOUR_NAME=Your Full Name
GMAIL_ADDRESS=your@gmail.com
YOUR_PHONE=+91 XXXXXXXXXX

GITHUB_URL=https://github.com/yourusername
LINKEDIN_URL=https://linkedin.com/in/yourusername
PORTFOLIO_URL=https://yourportfolio.com
```

---

### 4. Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable **Gmail API**
4. Create **OAuth 2.0 credentials** (Desktop App)
5. Download the JSON file
6. Rename it to `credentials.json`
7. Place it inside the `backend/` folder

---

### 5. Add Your Resumes

Place your resume PDFs inside `backend/resumes/`:

```
backend/resumes/
├── resume_fullstack.pdf
├── resume_python.pdf
├── resume_backend.pdf
└── resume_general.pdf
```

---

### 6. Frontend Setup

```bash
cd ../frontend
npm install
npm install axios
```

---

### 7. Run the App

**Start Backend:**
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload
```

**Start Frontend (new terminal):**
```bash
cd frontend
npm start
```

Or use the one-click startup bat file (Windows):

```bash
# Double click start.bat in the root folder
```

---

## 📱 Usage

1. **Open** `http://localhost:3000` in your browser
2. **Paste** a job description or **upload** a JD PDF
3. **Click** "Analyse JD" — AI extracts HR email, company and role
4. **View** resume match scores — AI ranks your resumes
5. **Select** the best resume (or override AI suggestion)
6. **Click** "Generate Email" — AI writes a tailored email
7. **Review** the email and edit if needed
8. **Click** "Send Email" — email sent with resume attached!

---

## 🔑 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/parse-jd` | Extract details from JD text |
| POST | `/parse-jd-pdf` | Extract details from JD PDF |
| POST | `/match-resumes` | Score resumes against JD |
| POST | `/generate-email` | Generate tailored email |
| POST | `/send-email` | Send email via Gmail |
| GET | `/resumes` | List all resumes |
| POST | `/upload-resume` | Upload new resume PDF |
| DELETE | `/resume/{name}` | Delete a resume |

---

## 🤖 AI Models Used

| Task | Model | Why |
|---|---|---|
| JD Parsing | `llama-3.1-8b-instant` | Fast, simple extraction |
| Resume Scoring | `llama-3.3-70b-versatile` | Smart understanding needed |
| Email Writing | `llama-3.3-70b-versatile` | Best quality output |

---

## ⚠️ Important Notes

- **Token Limits** — Free Groq tier allows ~100K tokens/day (~30 applications)
- **Gmail OAuth** — First run opens browser for permission, saved after that
- **Resume Storage** — Resumes stored locally in `backend/resumes/`
- **Vector Store** — Auto-generated in `backend/vector_store/` on first run

---


Add these to your `.gitignore`:

```gitignore
.env
credentials.json
token.pkl
venv/
vector_store/
node_modules/
```

---

## 🛣️ Roadmap

- [ ] Application tracker (log sent emails)
- [ ] Email reply detection
- [ ] Job board API integration
- [ ] Mobile app (Capacitor)
- [ ] Cloud deployment

---

## 👨‍💻 Built By

**Manikandan M**
| MCA Student | Software Developer

🔗 [GitHub](https://github.com/mmanikandan281) | [LinkedIn](https://linkedin.com/in/mmanikandan281) | [Portfolio](https://portfolio-manikandan-m.vercel.app/)
