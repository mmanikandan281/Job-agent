import { useState } from "react";
import axios from "axios";

const API = "http://127.0.0.1:8000";

export default function JDInput({ onNext }) {
  const [jdText, setJdText] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAnalyse = async () => {
    setError("");
    setLoading(true);

    try {
      let result;

      if (file) {
        // PDF upload
        const formData = new FormData();
        formData.append("file", file);
        const res = await axios.post(`${API}/parse-jd-pdf`, formData);
        result = res.data;
      } else if (jdText.trim()) {
        // Text input
        const res = await axios.post(`${API}/parse-jd`, { jd_text: jdText });
        result = res.data;
      } else {
        setError("Please paste a JD or upload a PDF first!");
        setLoading(false);
        return;
      }

      if (!result.success) {
        setError(result.error || "Something went wrong");
        setLoading(false);
        return;
      }

      onNext(result, file ? "" : jdText);

    } catch (err) {
      setError("Backend not reachable. Make sure FastAPI is running!");
    }

    setLoading(false);
  };

  return (
    <div className="card">
      <div className="card-title">Paste Job Description</div>
      <div className="card-sub">Add the full JD — AI will extract HR email, company and role automatically</div>

      {/* Text Input */}
      <textarea
        rows={10}
        placeholder="Paste the full job description here including HR email..."
        value={jdText}
        onChange={e => { setJdText(e.target.value); setFile(null); }}
      />

      <div className="divider">or upload PDF</div>

      {/* PDF Upload */}
      <div
        onClick={() => document.getElementById('pdf-upload').click()}
        style={{
          border: `2px dashed ${file ? 'var(--success)' : 'var(--border)'}`,
          borderRadius: '10px',
          padding: '24px',
          textAlign: 'center',
          cursor: 'pointer',
          color: file ? 'var(--success)' : 'var(--muted)',
          fontSize: '14px',
          transition: 'all 0.2s'
        }}
      >
        {file ? `✅ ${file.name}` : "📄 Click to upload JD as PDF"}
        <input
          id="pdf-upload"
          type="file"
          accept=".pdf"
          style={{ display: 'none' }}
          onChange={e => { setFile(e.target.files[0]); setJdText(""); }}
        />
      </div>

      {error && (
        <div style={{ color: 'var(--accent2)', fontSize: '13px', marginTop: '12px' }}>
          ⚠️ {error}
        </div>
      )}

      <div className="btn-row">
        <button
          className="btn-primary"
          onClick={handleAnalyse}
          disabled={loading || (!jdText.trim() && !file)}
        >
          {loading ? "Analysing..." : "Analyse JD →"}
        </button>
      </div>

      {loading && (
        <div className="loading">
          <div className="spinner" />
          Extracting details from JD...
        </div>
      )}
    </div>
  );
}