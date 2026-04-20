import { useState } from "react";
import axios from "axios";

const API = "http://127.0.0.1:8000";

export default function EmailPreview({ emailData, jdData, selectedResume, onNext, onBack }) {
  const [subject, setSubject] = useState(emailData?.subject || "");
  const [body, setBody] = useState(emailData?.body || "");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  const handleSend = async () => {
    setSending(true);
    setError("");

    try {
      const res = await axios.post(`${API}/send-email`, {
        to: jdData.hr_email,
        subject: subject,
        body: body,
        resume_path: selectedResume.path
      });

      if (res.data.success) {
        onNext();
      } else {
        setError(res.data.error || "Failed to send email");
      }
    } catch (err) {
      setError("Failed to send email. Check backend!");
    }

    setSending(false);
  };

  return (
    <div className="card">
      <div className="card-title">Email Preview</div>
      <div className="card-sub">Review and edit before sending</div>

      {/* Meta info */}
      <div style={{
        background: 'var(--surface2)',
        borderRadius: '10px',
        padding: '16px',
        marginBottom: '24px',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
          <span style={{ color: 'var(--muted)' }}>To:</span>
          <span style={{ color: 'var(--success)' }}>{jdData?.hr_email}</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
          <span style={{ color: 'var(--muted)' }}>Attachment:</span>
          <span style={{ color: 'var(--accent)' }}>📎 {selectedResume?.resume}.pdf</span>
        </div>
      </div>

      {/* Subject */}
      <div style={{ marginBottom: '16px' }}>
        <label style={{ fontSize: '12px', color: 'var(--muted)', display: 'block', marginBottom: '6px', fontFamily: 'Syne' }}>
          SUBJECT
        </label>
        <input
          value={subject}
          onChange={e => setSubject(e.target.value)}
        />
      </div>

      {/* Body */}
      <div>
        <label style={{ fontSize: '12px', color: 'var(--muted)', display: 'block', marginBottom: '6px', fontFamily: 'Syne' }}>
          EMAIL BODY
        </label>
        <textarea
          rows={16}
          value={body}
          onChange={e => setBody(e.target.value)}
        />
      </div>

      {error && <div style={{color:'var(--accent2)', fontSize:'13px', marginTop:'12px'}}>⚠️ {error}</div>}

      <div className="btn-row">
        <button className="btn-secondary" onClick={onBack}>← Back</button>
        <button
          className="btn-success"
          onClick={handleSend}
          disabled={sending}
        >
          {sending ? "Sending..." : "Send Email ✉️"}
        </button>
      </div>

      {sending && (
        <div className="loading"><div className="spinner"/>Sending via Gmail...</div>
      )}
    </div>
  );
}
