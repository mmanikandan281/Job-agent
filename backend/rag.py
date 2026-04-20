import os
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
from dotenv import load_dotenv

load_dotenv()

# Free embedding model - downloads once, runs locally
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

RESUME_FOLDER = "resumes"
VECTOR_STORE_PATH = "vector_store"


# ─────────────────────────────────────────
# Auto scan resumes folder
# No hardcoding - just drop PDFs in folder
# ─────────────────────────────────────────
def get_all_resumes() -> dict:
    resumes = {}

    if not os.path.exists(RESUME_FOLDER):
        print("⚠️ resumes/ folder not found")
        return resumes

    for file in os.listdir(RESUME_FOLDER):
        if file.endswith(".pdf"):
            name = file.replace(".pdf", "")
            resumes[name] = os.path.join(RESUME_FOLDER, file)

    if not resumes:
        print("⚠️ No PDF files found in resumes/ folder")

    return resumes


# ─────────────────────────────────────────
# Read PDF and extract text
# ─────────────────────────────────────────
def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


# ─────────────────────────────────────────
# Split text into chunks
# ─────────────────────────────────────────
def split_into_chunks(text: str, chunk_size: int = 100) -> list:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks


# ─────────────────────────────────────────
# Setup - run once per resume
# Also runs when new resume is uploaded
# ─────────────────────────────────────────
def setup_resumes():
    print("Scanning resumes folder...")
    resumes = get_all_resumes()

    if not resumes:
        return

    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

    for resume_name, resume_path in resumes.items():
        resume_store_path = os.path.join(VECTOR_STORE_PATH, resume_name)

        # Skip if already processed
        if os.path.exists(os.path.join(resume_store_path, "index.faiss")):
            print(f"⏭️  {resume_name} already processed, skipping")
            continue

        print(f"Processing {resume_name}...")

        text = extract_text_from_pdf(resume_path)
        chunks = split_into_chunks(text)

        embeddings = embedding_model.encode(chunks)
        embeddings = np.array(embeddings).astype('float32')

        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)

        os.makedirs(resume_store_path, exist_ok=True)
        faiss.write_index(index, os.path.join(resume_store_path, "index.faiss"))

        with open(os.path.join(resume_store_path, "chunks.pkl"), "wb") as f:
            pickle.dump(chunks, f)

        print(f"✅ {resume_name} done — {len(chunks)} chunks created")

    print("\n✅ All resumes processed!")


# ─────────────────────────────────────────
# Process single new resume
# Called when user uploads from frontend
# ─────────────────────────────────────────
def process_new_resume(resume_path: str, resume_name: str):
    print(f"Processing new resume: {resume_name}")
    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

    text = extract_text_from_pdf(resume_path)
    chunks = split_into_chunks(text)

    embeddings = embedding_model.encode(chunks)
    embeddings = np.array(embeddings).astype('float32')

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    resume_store_path = os.path.join(VECTOR_STORE_PATH, resume_name)
    os.makedirs(resume_store_path, exist_ok=True)
    faiss.write_index(index, os.path.join(resume_store_path, "index.faiss"))

    with open(os.path.join(resume_store_path, "chunks.pkl"), "wb") as f:
        pickle.dump(chunks, f)

    print(f"✅ {resume_name} ready!")


# ─────────────────────────────────────────
# Match all resumes against JD
# ─────────────────────────────────────────
def match_resumes(jd_text: str) -> list:
    from groq import Groq
    import os
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    results = []
    resumes = get_all_resumes()

    for resume_name, resume_path in resumes.items():
        # Get full resume text
        if not os.path.exists(resume_path):
            continue
            
        full_text = extract_text_from_pdf(resume_path)

        # Ask Groq to score this resume against JD
        prompt = f"""
        You are a recruiter scoring a resume against a job description.
        
        Give a match score from 0 to 100 based on:
        - Skills match (40%)
        - Experience relevance (30%)
        - Project relevance (30%)
        
        Job Description:
        {jd_text}
        
        Resume:
        {full_text[:5000]}
        
        Return ONLY a JSON object like this, nothing else:
        {{"score": 75, "reason": "one line reason"}}
        """

        try:
            response = groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role": "user", "content": prompt}]
            )
            
            import json, re
            text = response.choices[0].message.content.strip()
            text = re.sub(r"```json|```", "", text).strip()
            data = json.loads(text)
            score = float(data.get("score", 0))
            reason = data.get("reason", "")
            
        except:
            score = 0.0
            reason = "Could not score"

        results.append({
            "resume": resume_name,
            "score": score,
            "reason": reason,
            "path": resume_path
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results
# ─────────────────────────────────────────
# Get relevant chunks from best resume
# ─────────────────────────────────────────
def get_context(resume_name: str, jd_text: str, top_k: int = 5) -> str:
    resume_store_path = os.path.join(VECTOR_STORE_PATH, resume_name)

    index = faiss.read_index(os.path.join(resume_store_path, "index.faiss"))

    with open(os.path.join(resume_store_path, "chunks.pkl"), "rb") as f:
        chunks = pickle.load(f)

    jd_embedding = embedding_model.encode([jd_text])
    jd_embedding = np.array(jd_embedding).astype('float32')

    _, indices = index.search(jd_embedding, k=top_k)

    relevant_chunks = [chunks[i] for i in indices[0] if i < len(chunks)]
    return "\n\n".join(relevant_chunks)


# ─────────────────────────────────────────
# TEST
# ─────────────────────────────────────────
if __name__ == "__main__":

    print("=" * 40)
    print("STEP 1 - Setting up resumes")
    print("=" * 40)
    setup_resumes()

    print()
    print("=" * 40)
    print("STEP 2 - Matching resumes to a JD")
    print("=" * 40)

    test_jd = """
    We are looking for a Full Stack Developer.
    Skills required: React, Node.js, MongoDB, REST APIs.
    Experience: 2+ years.
    Send resume to hr@company.com
    """

    matches = match_resumes(test_jd)

    if matches:
        print("\nResume Match Results:")
        for i, match in enumerate(matches):
            print(f"{i+1}. {match['resume']} — {match['score']}% match")

        print()
        print("=" * 40)
        print(f"Best match: {matches[0]['resume']}")
        print("=" * 40)
        context = get_context(matches[0]['resume'], test_jd)
        print(context[:500])
    else:
        print("No resumes found! Add PDFs to resumes/ folder first")