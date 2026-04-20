import { useState, useEffect } from "react";
import axios from "axios";

const API = "http://127.0.0.1:8000";

export default function ResumeSelector({ jdText, jdData, onNext, onBack }) {
  const [matches, setMatches] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchMatches();
  }, []);

  const fetchMatches = async () => {
    try {
      const res = await axios.post(`${API}/match-resumes`, { jd_text: jdText });
      if (res.data.success) {
        setMatches(res.data.matches);
        setSelected(res.data.matches[0]);
      }
    } catch (err) {
      setError("Failed to match resumes");
    }
    setLoading(false);
  };

  const handleNext = async () => {
    setGenerating(true);
    try {
      const res = await axios.post(`${API}/generate-email`, {
        jd_text: jdText,
        company: jdData.company,
        role: jdData.role,
        resume_name: selected.resume
      });

      if (res.data.success) {
        onNext(selected, res.data);
      } else {
        setError(res.data.error);
      }
    } catch (err) {
      setError("Failed to generate email");
    }
    setGenerating(false);
  };

  return (
    <div className="card">
      <div className="card-title">Resume Match</div>
      <div className="card-sub">
        AI ranked your resumes for <strong style={{color:'var(--accent)'}}>{jdData?.role}</strong> at <strong style={{color:'var(--accent)'}}>{jdData?.company}</strong>
      </div>

      {/* Extracted Info */}
      <div style={{
        background: 'var(--surface2)',
        borderRadius: '10px',
        padding: '16px',
        marginBottom: '24px',
        display: 'flex',
        gap: '16px',
        flexWrap: 'wrap'
      }}>
        <div><span className="tag tag-muted">HR Email</span><br/>
          <span style={{fontSize:'13px', marginTop:'4px', display:'block'}}>{jdData?.hr_email}</span>
        </div>
        <div><span className="tag tag-muted">Company</span><br/>
          <span style={{fontSize:'13px', marginTop:'4px', display:'block'}}>{jdData?.company}</span>
        </div>
        <div><span className="tag tag-muted">Role</span><br/>
          <span style={{fontSize:'13px', marginTop:'4px', display:'block'}}>{jdData?.role}</span>
        </div>
      </div>

      {loading ? (
        <div className="loading"><div className="spinner"/>Matching resumes...</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {matches.map((match, i) => (
            <div
              key={match.resume}
              onClick={() => setSelected(match)}
              style={{
                background: selected?.resume === match.resume ? 'rgba(108,99,255,0.1)' : 'var(--surface2)',
                border: `1px solid ${selected?.resume === match.resume ? 'var(--accent)' : 'var(--border)'}`,
                borderRadius: '12px',
                padding: '16px 20px',
                cursor: 'pointer',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                transition: 'all 0.2s'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span style={{ fontSize: '20px' }}>📄</span>
                <div>
                  <div style={{fontSize:'14px', fontWeight:'500'}}>{match.resume}</div>
                  <div style={{fontSize:'12px', color:'var(--muted)'}} >{match.score}% match</div>
                </div>
              </div>
              <div style={{fontSize:'20px'}}>
                {selected?.resume === match.resume ? '✓' : ''}
              </div>
            </div>
          ))}
        </div>
      )}

      {error && <div style={{color:'var(--accent2)', fontSize:'13px', marginTop:'12px'}}>⚠️ {error}</div>}

      <div className="btn-row">
        <button className="btn-secondary" onClick={onBack}>← Back</button>
        <button
          className="btn-primary"
          onClick={handleNext}
          disabled={generating || !selected}
        >
          {generating ? "Generating..." : "Generate Email →"}
        </button>
      </div>

      {generating && (
        <div className="loading"><div className="spinner"/>Generating personalized email...</div>
      )}
    </div>
  );
}
