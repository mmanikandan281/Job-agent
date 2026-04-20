export default function Success({ onReset }) {
  return (
    <div className="card" style={{ textAlign: 'center', padding: '60px 32px' }}>
      <div style={{ fontSize: '64px', marginBottom: '24px' }}>🎉</div>
      <div className="card-title" style={{ textAlign: 'center', fontSize: '28px' }}>
        Email Sent!
      </div>
      <p style={{ color: 'var(--muted)', fontSize: '14px', marginTop: '12px', marginBottom: '40px' }}>
        Your application has been sent successfully.<br/>
        Good luck with your application!
      </p>
      <button className="btn-primary" onClick={onReset}>
        Apply to Another Job →
      </button>
    </div>
  );
}