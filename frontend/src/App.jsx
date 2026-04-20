import { useState } from "react";
import JDInput from "./components/JDInput";
import ResumeSelector from "./components/ResumeSelector";
import EmailPreview from "./components/EmailPreview";
import Success from "./components/Success";
import Resumes from "./components/Resumes";
import "./App.css";

export default function App() {
  const [step, setStep] = useState(1);
  const [jdData, setJdData] = useState(null);
  const [jdText, setJdText] = useState("");
  const [selectedResume, setSelectedResume] = useState(null);
  const [showResumes, setShowResumes] = useState(false);
  const [emailData, setEmailData] = useState(null);

  return (
    <div className="app">
          {/* Header */}
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
      <div style={{ fontFamily: 'Syne', fontWeight: 800, fontSize: '20px', color: 'var(--accent)' }}>
        Job Agent 🤖
      </div>
      <button className="btn-secondary" onClick={() => setShowResumes(true)}>
        📄 Manage Resumes
      </button>
    </div>

    {showResumes && <Resumes onClose={() => setShowResumes(false)} />}
      {/* Progress Bar */}
      <div className="progress-bar">
        {["JD Input", "Resume Match", "Email Preview", "Sent!"].map((label, i) => (
          <div key={i} className={`progress-step ${step > i + 1 ? "done" : ""} ${step === i + 1 ? "active" : ""}`}>
            <div className="step-circle">{step > i + 1 ? "✓" : i + 1}</div>
            <span>{label}</span>
          </div>
        ))}
      </div>

      {step === 1 && (
        <JDInput
          onNext={(jd, text) => {
            setJdData(jd);
            setJdText(text);
            setStep(2);
          }}
        />
      )}
      {step === 2 && (
        <ResumeSelector
          jdText={jdText}
          jdData={jdData}
          onNext={(resume, emailResult) => {
            setSelectedResume(resume);
            setEmailData(emailResult);
            setStep(3);
          }}
          onBack={() => setStep(1)}
        />
      )}
      {step === 3 && (
        <EmailPreview
          emailData={emailData}
          jdData={jdData}
          selectedResume={selectedResume}
          onNext={() => setStep(4)}
          onBack={() => setStep(2)}
        />
      )}
      {step === 4 && (
        <Success onReset={() => {
          setStep(1);
          setJdData(null);
          setJdText("");
          setSelectedResume(null);
          setEmailData(null);
        }} />
      )}
    </div>
  );
}