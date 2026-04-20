import os
import json
import re
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
from dotenv import load_dotenv

load_dotenv()

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

RESUME_FOLDER = "resumes"
VECTOR_STORE_PATH = "vector_store"


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


def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def split_into_chunks(text: str, chunk_size: int = 100) -> list:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks


def setup_resumes():
    print("Scanning resumes folder...")
    resumes = get_all_resumes()

    if not resumes:
        return

    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

    for resume_name, resume_path in resumes.items():
        resume_store_path = os.path.join(VECTOR_STORE_PATH, resume_name)

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


def match_resumes(jd_text: str) -> list:
    from groq import Groq
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    resumes = get_all_resumes()
    if not resumes:
        return []

    # Build all resume summaries in one shot
    resume_summaries = ""
    resume_texts = {}

    for resume_name, resume_path in resumes.items():
        if not os.path.exists(resume_path):
            continue
        text = extract_text_from_pdf(resume_path)
        resume_texts[resume_name] = resume_path
        # Only send first 1500 chars per resume to save tokens
        resume_summaries += f"\n\nRESUME_NAME: {resume_name}\n{text[:1500]}\n---"

    # One single API call for all resumes
    prompt = f"""
    You are a recruiter. Score each resume against the job description.

    Score from 0-100 based on:
    - Skills match (35%)
    - How specifically resume targets this role (35%)
    - Project and experience relevance (30%)

    Job Description:
    {jd_text}

    Resumes to score:
    {resume_summaries}

    Return ONLY a JSON array, nothing else:
    [
        {{"resume": "resume_name", "score": 75, "reason": "one line reason"}},
        {{"resume": "resume_name2", "score": 60, "reason": "one line reason"}}
    ]
    """

    try:
        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response.choices[0].message.content.strip()

        cleaned = re.sub(r"```json|```", "", raw).strip()
        json_match = re.search(r'\[.*?\]', cleaned, re.DOTALL)
        if json_match:
            cleaned = json_match.group()

        data = json.loads(cleaned)

        results = []
        for item in data:
            resume_name = item.get("resume", "")
            results.append({
                "resume": resume_name,
                "score": float(item.get("score", 50)),
                "reason": item.get("reason", ""),
                "path": resume_texts.get(resume_name, "")
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    except Exception as e:
        print(f"Scoring error: {e}")
        # Fallback - return all resumes with 50% score
        return [
            {"resume": name, "score": 50.0, "reason": "Could not score", "path": path}
            for name, path in resume_texts.items()
        ]


def get_context(resume_name: str, jd_text: str, top_k: int = 8) -> str:
    resume_store_path = os.path.join(VECTOR_STORE_PATH, resume_name)

    index = faiss.read_index(os.path.join(resume_store_path, "index.faiss"))

    with open(os.path.join(resume_store_path, "chunks.pkl"), "rb") as f:
        chunks = pickle.load(f)

    jd_embedding = embedding_model.encode([jd_text])
    jd_embedding = np.array(jd_embedding).astype('float32')

    _, indices = index.search(jd_embedding, k=min(top_k, len(chunks)))
    relevant_chunks = [chunks[i] for i in indices[0] if i < len(chunks)]

    if len(chunks) <= 10:
        return "\n\n".join(chunks)

    return "\n\n".join(relevant_chunks)

# -----------------------Testing Dummy Details-----------------------
# if __name__ == "__main__":
#     print("=" * 40)
#     print("STEP 1 - Setting up resumes")
#     print("=" * 40)
#     setup_resumes()

#     print()
#     print("=" * 40)
#     print("STEP 2 - Matching resumes to a JD")
#     print("=" * 40)

#     test_jd = """
#     We are looking for a Full Stack Developer.
#     Skills required: React, Node.js, MongoDB, REST APIs.
#     Experience: 2+ years.
#     Send resume to hr@company.com
#     """

#     matches = match_resumes(test_jd)

#     if matches:
#         print("\nResume Match Results:")
#         for i, match in enumerate(matches):
#             print(f"{i+1}. {match['resume']} — {match['score']}% match — {match['reason']}")
#     else:
#         print("No resumes found!")