import { useState, useEffect } from "react";
import axios from "axios";

const API = "http://127.0.0.1:8000";

export default function Resumes({ onClose }) {
  const [resumes, setResumes] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchResumes();
  }, []);

  const fetchResumes = async () => {
    const res = await axios.get(`${API}/resumes`);
    if (res.data.success) setResumes(res.data.resumes);
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post(`${API}/upload-resume`, formData);
      if (res.data.success) {
        setMessage(`✅ ${file.name} uploaded successfully!`);
        fetchResumes();
      }
    } catch (err) {
      setMessage("❌ Upload failed!");
    }
    setUploading(false);
  };

  const handleDelete = async (resumeName) => {
    if (!window.confirm(`Delete ${resumeName}?`)) return;

    try {
      const res = await axios.delete(`${API}/resume/${resumeName}`);
      if (res.data.success) {
        setMessage(`✅ ${resumeName} deleted!`);
        fetchResumes();
      }
    } catch (err) {
      setMessage("❌ Delete failed!");
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0,0,0,0.7)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div className="card" style={{ width: '500px', maxHeight: '80vh', overflowY: 'auto' }}>

        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <div className="card-title" style={{ marginBottom: 0 }}>My Resumes</div>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: 'var(--muted)', fontSize: '20px', cursor: 'pointer' }}
          >✕</button>
        </div>

        {/* Upload Button */}
        <div
          onClick={() => document.getElementById('resume-upload').click()}
          style={{
            border: '2px dashed var(--border)',
            borderRadius: '10px',
            padding: '20px',
            textAlign: 'center',
            cursor: 'pointer',
            color: 'var(--muted)',
            fontSize: '14px',
            marginBottom: '24px',
            transition: 'all 0.2s'
          }}
        >
          {uploading ? "Uploading..." : "📄 Click to upload new resume (PDF)"}
          <input
            id="resume-upload"
            type="file"
            accept=".pdf"
            style={{ display: 'none' }}
            onChange={handleUpload}
          />
        </div>

        {message && (
          <div style={{ fontSize: '13px', marginBottom: '16px', color: message.includes('✅') ? 'var(--success)' : 'var(--accent2)' }}>
            {message}
          </div>
        )}

        {/* Resume List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {resumes.length === 0 ? (
            <div style={{ color: 'var(--muted)', fontSize: '14px', textAlign: 'center', padding: '20px' }}>
              No resumes uploaded yet
            </div>
          ) : (
            resumes.map((resume) => (
              <div key={resume.name} style={{
                background: 'var(--surface2)',
                border: '1px solid var(--border)',
                borderRadius: '10px',
                padding: '14px 16px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span>📄</span>
                  <span style={{ fontFamily: 'Syne', fontWeight: 600, fontSize: '14px' }}>
                    {resume.name}
                  </span>
                </div>
                <button
                  onClick={() => handleDelete(resume.name)}
                  style={{
                    background: 'rgba(255,101,132,0.1)',
                    border: '1px solid rgba(255,101,132,0.3)',
                    color: 'var(--accent2)',
                    borderRadius: '6px',
                    padding: '6px 12px',
                    fontSize: '12px',
                    cursor: 'pointer',
                    fontFamily: 'Syne',
                    fontWeight: 600
                  }}
                >
                  Delete
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}