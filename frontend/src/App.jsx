import { useState } from "react";
import axios from "axios";
import "./App.css";
import ReactMarkdown from "react-markdown";

const initialForm = {
  checking_status: "A11",
  duration_months: 6,
  city: "Hyderabad",
  credit_history: "A34",
  purpose: "A43",
  credit_amount: 1169,
  savings_status: "A65",
  employment_status: "A75",
  installment_rate: 4,
  personal_status: "A93",
  other_debtors: "A101",
  residence_duration: 4,
  property: "A121",
  age: 67,
  other_installment_plans: "A143",
  housing: "A152",
  existing_credits: 2,
  job: "A173",
  dependents: 1,
  telephone: "A192",
  foreign_worker: "A201",
};
const demoProfiles = {
  custom: {
    label: "Custom Applicant",
    form: initialForm,
  },

  government_employee: {
    label: "Government Employee",
    form: {
      ...initialForm,
      checking_status: "A13",
      duration_months: 12,
      city: "Hyderabad",
      credit_history: "A32",
      credit_amount: 3000,
      savings_status: "A64",
      employment_status: "A75",
      installment_rate: 2,
      age: 42,
      housing: "A152",
      existing_credits: 1,
      dependents: 2,
    },
  },

  street_vendor: {
    label: "Street Vendor",
    form: {
      ...initialForm,
      checking_status: "A11",
      duration_months: 24,
      city: "Chennai",
      credit_history: "A30",
      credit_amount: 4500,
      savings_status: "A61",
      employment_status: "A73",
      installment_rate: 4,
      age: 34,
      housing: "A151",
      existing_credits: 1,
      dependents: 2,
    },
  },

  doctor_private_practice: {
    label: "Doctor – Private Practice",
    form: {
      ...initialForm,
      checking_status: "A13",
      duration_months: 18,
      city: "Bengaluru",
      credit_history: "A32",
      credit_amount: 8000,
      savings_status: "A64",
      employment_status: "A75",
      installment_rate: 2,
      age: 45,
      housing: "A152",
      existing_credits: 2,
      dependents: 2,
    },
  },

  delivery_worker: {
    label: "Delivery Worker",
    form: {
      ...initialForm,
      checking_status: "A12",
      duration_months: 18,
      city: "Pune",
      credit_history: "A32",
      credit_amount: 2500,
      savings_status: "A62",
      employment_status: "A73",
      installment_rate: 3,
      age: 27,
      housing: "A151",
      existing_credits: 1,
      dependents: 1,
    },
  },

  textile_worker: {
    label: "Textile Shop Worker",
    form: {
      ...initialForm,
      checking_status: "A12",
      duration_months: 12,
      city: "Hyderabad",
      credit_history: "A32",
      credit_amount: 2000,
      savings_status: "A62",
      employment_status: "A74",
      installment_rate: 3,
      age: 36,
      housing: "A151",
      existing_credits: 1,
      dependents: 2,
    },
  },
};

const SelectField = ({ label, name, value, options, onChange }) => (
  <div className="field">
    <label>{label}</label>
    <select name={name} value={value} onChange={onChange}>
      {options.map(([code, text]) => (
        <option key={code} value={code}>
          {text}
        </option>
      ))}
    </select>
  </div>
);

const NumberField = ({ label, name, value, onChange, min = 1 }) => (
  <div className="field">
    <label>{label}</label>
    <input
      type="number"
      name={name}
      value={value}
      min={min}
      onChange={onChange}
    />
  </div>
);

function App() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [transactionFile, setTransactionFile] = useState(null);
  const [behaviorResult, setBehaviorResult] = useState(null);
  const [behaviorLoading, setBehaviorLoading] = useState(false);
  const [behaviorError, setBehaviorError] = useState("");
  const [affordabilityResult, setAffordabilityResult] = useState(null);
  const [affordabilityLoading, setAffordabilityLoading] = useState(false);
  const [affordabilityError, setAffordabilityError] = useState("");
  const [aiExplanation, setAiExplanation] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState("");
  const [documentFile, setDocumentFile] = useState(null);
  const [documentResult, setDocumentResult] = useState(null);
  const [documentLoading, setDocumentLoading] = useState(false);
  const [documentError, setDocumentError] = useState("");
  const [selectedProfile, setSelectedProfile] = useState("custom");
  const [email, setEmail] = useState("analyst@demo.com");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState(
    localStorage.getItem("access_token") || ""
  );
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState("");
  const [inputsModified, setInputsModified] = useState(false);

  const login = async () => {
    setLoginLoading(true);
    setLoginError("");

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/auth/login",
        {
          email,
          password,
        }
      );

      const accessToken = response.data.access_token;

      localStorage.setItem("access_token", accessToken);
      setToken(accessToken);
      setPassword("");
    } catch (err) {
      console.error(err);

      setLoginError(
        err.response?.data?.detail ||
          "Unable to sign in."
      );
    } finally {
      setLoginLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    setToken("");
    setPassword("");

    setResult(null);
    setBehaviorResult(null);
    setAffordabilityResult(null);
    setDocumentResult(null);
    setAiExplanation("");
  };

  const authConfig = {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };

  const handleChange = (event) => {
    const { name, value, type } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: type === "number" ? Number(value) : value,
    }));

    if (result) setInputsModified(true);
  };

  const handleDemoProfileChange = (event) => {
    const profileKey = event.target.value;

    setSelectedProfile(profileKey);
    setForm({ ...demoProfiles[profileKey].form });
    setInputsModified(false);

    // Clear old results when applicant changes
    setResult(null);
    setBehaviorResult(null);
    setDocumentResult(null);
    setAiExplanation("");

    setError("");
    setBehaviorError("");
    setDocumentError("");
    setAiError("");
  };

  const runAssessment = async () => {
    setLoading(true);
    setError("");
    setAiExplanation("");
    setAiError("");

    // City is used by the affordability engine,
    // not by the trained credit-risk model.
    const { city, ...predictionPayload } = form;

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/predict",
        predictionPayload,
        authConfig
      );

      setResult(response.data);
      setInputsModified(false);
    } catch (err) {
      console.error(err);
      setError(
        "Unable to complete assessment. Check that the API is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const analyzeTransactions = async () => {
    if (!transactionFile) {
      setBehaviorError("Please select a CSV transaction statement.");
      return;
    }

    setBehaviorLoading(true);
    setBehaviorError("");
    setAiExplanation("");
    setAiError("");

    const formData = new FormData();
    formData.append("file", transactionFile);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/behavior/analyze",
        formData,
        authConfig
      );

      setBehaviorResult(response.data);
    } catch (err) {
      console.error(err);
      setBehaviorError(
        err.response?.data?.detail ||
          "Unable to analyze transaction statement."
      );
    } finally {
      setBehaviorLoading(false);
    }
  };

  const analyzeAffordability = async () => {
    if (!result) {
      setAffordabilityError(
        "Run the credit risk assessment first."
      );
      return;
    }
    if (!behaviorResult) {
      setAffordabilityError(
        "Analyze the transaction statement first."
      );
      return;
    }

    setAffordabilityLoading(true);
    setAffordabilityError("");
    setAffordabilityResult(null);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/affordability/analyze",
        {
          stable_monthly_income:
            behaviorResult.stable_monthly_income,

          observed_monthly_expenses:
            behaviorResult.observed_monthly_expenses,

          city: form.city,

          existing_monthly_obligations: 0,
          risk_band: result.risk_level,
          duration_months: form.duration_months,
        },
        authConfig
      );

      setAffordabilityResult(response.data);
    } catch (err) {
      console.error(err);

      setAffordabilityError(
        err.response?.data?.detail ||
          "Unable to calculate repayment capacity."
      );
    } finally {
      setAffordabilityLoading(false);
    }
  };

  const indexDocument = async () => {
    if (!documentFile) {
      setDocumentError("Please select a supporting PDF.");
      return;
    }

    setDocumentLoading(true);
    setDocumentError("");
    setDocumentResult(null);

    const formData = new FormData();
    formData.append("file", documentFile);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/documents/index",
        formData,
        authConfig
      );

      setDocumentResult(response.data);
    } catch (err) {
      console.error(err);

      setDocumentError(
        err.response?.data?.detail ||
          "Unable to process supporting document."
      );
    } finally {
      setDocumentLoading(false);
    }
  };

  const generateAIExplanation = async () => {
    if (!result) {
      setAiError("Run the credit risk assessment first.");
      return;
    }

    if (!behaviorResult) {
      setAiError("Analyze the transaction statement first.");
      return;
    }

    if (!documentResult) {
      setAiError("Process the supporting financial document first.");
      return;
    }

    setAiLoading(true);
    setAiError("");
    setAiExplanation("");

    try {
      console.log(
        "SENDING DOCUMENT NAME:",
        documentResult?.document_name
      );
      const response = await axios.post(
        "http://127.0.0.1:8000/intelligence/explain",
        {
          risk_probability: result.risk_probability,
          risk_band: result.risk_level,

          shap_factors: result.top_factors.map((factor) => ({
            feature: factor.feature,
            shap_value: factor.impact,
          })),

          behavioral_data: {
            income_stability: behaviorResult.income_stability,
            cashflow_consistency: behaviorResult.cashflow_consistency,
            spending_volatility: behaviorResult.spending_volatility,
            spending_volatility_score:
              behaviorResult.spending_volatility_score,
            average_savings_rate: behaviorResult.average_savings_rate,
          },
          document_name: documentResult.filename,
          query:
            "What evidence describes the applicant's income stability, financial obligations, payment behavior and cash flow?",
        },
        authConfig
      );

      setAiExplanation(response.data.explanation);
    } catch (err) {
      console.error("AI ERROR:", err);
      console.error("STATUS:", err.response?.status);
      console.error("RESPONSE:", err.response?.data);

      setAiError(
        JSON.stringify(err.response?.data?.detail) ||
          "Unable to generate AI explanation."
      );
    } finally {
      setAiLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="app login-page">
        <div className="login-orb orb-one"></div><div className="login-orb orb-two"></div>
        <section className="login-shell">
          <div className="login-brand-panel">
            <div className="brand-lockup"><span className="brand-mark">CI</span><span>CREDIT INTELLIGENCE</span></div>
            <div className="login-copy">
              <span className="hero-kicker">EXPLAINABLE · MULTI-MODAL · GROUNDED</span>
              <h1>Decision intelligence<br/>for modern credit.</h1>
              <p>Risk modeling, behavioral signals and grounded evidence — unified in one analyst workspace.</p>
              <div className="login-feature-row"><span>◈ ML + SHAP</span><span>◈ pgvector RAG</span><span>◈ Guardrailed AI</span></div>
            </div>
            <div className="login-security">● Secure prototype workspace <span>JWT protected</span></div>
          </div>
          <div className="login-card">
            <div className="login-card-icon">↗</div><p className="eyebrow">ANALYST WORKSPACE</p><h2>Analyst sign in</h2>
            <p className="muted">Secure access to the underwriting decision-support workspace.</p>
            <div className="field"><label>Work email</label><input type="email" value={email} onChange={(e)=>setEmail(e.target.value)} /></div>
            <div className="field"><label>Password</label><input type="password" value={password} onChange={(e)=>setPassword(e.target.value)} onKeyDown={(e)=>{if(e.key==="Enter") login();}} /></div>
            <button className="primary-button" onClick={login} disabled={loginLoading}>{loginLoading ? "Authenticating..." : "Sign in to workspace  →"}</button>
            {loginError && <div className="error">{loginError}</div>}
            <div className="security-line">◉ JWT bearer authentication · Role protected</div>
          </div>
        </section>
      </div>
    );
  }

  const riskClass = result ? result.risk_level.toLowerCase() : "";
  const profileLabel = demoProfiles[selectedProfile]?.label || "Custom Applicant";

  return (
    <div className="app dashboard-app">
      <header className="topbar">
        <div className="brand-lockup"><span className="brand-mark">CI</span><div><strong>CREDIT INTELLIGENCE</strong><small>UNDERWRITING CONSOLE</small></div></div>
        <div className="topbar-center"><span className="live-dot"></span> Decision Engine Online <span className="topbar-divider"></span> <span>Prototype Environment</span></div>
        <div className="analyst-actions"><div className="analyst-avatar">A</div><div><strong>Analyst</strong><small>Authenticated</small></div><button className="ghost-button" onClick={logout}>Logout</button></div>
      </header>

      <div className="hero-strip">
        <div><p className="eyebrow light">UNDERWRITING INTELLIGENCE PLATFORM</p><h1>Credit decisions, explained with evidence</h1><p>A unified analyst workspace for model risk, cash-flow signals, affordability and grounded evidence.</p></div>
        <div className="hero-pills"><span>ML Risk</span><span>SHAP</span><span>Alternative Data</span><span>RAG</span><span>Gemini</span></div>
      </div>

      <div className="workflow-bar">
        {[['01','Applicant'],['02','Risk'],['03','Behavior'],['04','Capacity'],['05','Evidence'],['06','AI Insight']].map(([n,t],i)=><div className="workflow-step" key={n}><span>{n}</span><strong>{t}</strong>{i<5 && <i>→</i>}</div>)}
      </div>

      <main className="workspace">
        <section className="panel applicant-panel premium-panel">
          <div className="panel-heading"><div><p className="eyebrow">01 · APPLICATION</p><h2>Applicant Workspace</h2><p>Load a synthetic profile or edit any field before assessment.</p></div><span className="profile-chip">{profileLabel}</span></div>
          <div className="demo-selector"><div><strong>Demo Applicant</strong><small>Prefills editable model attributes</small></div><select value={selectedProfile} onChange={handleDemoProfileChange}>{Object.entries(demoProfiles).map(([key,p])=><option key={key} value={key}>{p.label}</option>)}</select></div>
          <div className="form-grid">
            <NumberField label="Credit Amount" name="credit_amount" value={form.credit_amount} onChange={handleChange}/>
            <NumberField label="Duration (months)" name="duration_months" value={form.duration_months} onChange={handleChange}/>
            <SelectField label="City" name="city" value={form.city} onChange={handleChange} options={[["Hyderabad","Hyderabad"],["Bengaluru","Bengaluru"],["Chennai","Chennai"],["Mumbai","Mumbai"],["Delhi","Delhi"],["Pune","Pune"]]}/>
            <NumberField label="Age" name="age" value={form.age} min={18} onChange={handleChange}/>
            <NumberField label="Installment Rate" name="installment_rate" value={form.installment_rate} onChange={handleChange}/>
            <SelectField label="Checking Account" name="checking_status" value={form.checking_status} onChange={handleChange} options={[["A11","Below 0 DM"],["A12","0–200 DM"],["A13","200+ DM"],["A14","No checking account"]]}/>
            <SelectField label="Credit History" name="credit_history" value={form.credit_history} onChange={handleChange} options={[["A30","No previous credit"],["A31","All credits paid"],["A32","Credits paid properly"],["A33","Payment delays"],["A34","Critical / other credits"]]}/>
            <SelectField label="Purpose" name="purpose" value={form.purpose} onChange={handleChange} options={[["A40","New car"],["A41","Used car"],["A42","Furniture / equipment"],["A43","Radio / television"],["A44","Domestic appliances"],["A45","Repairs"],["A46","Education"],["A48","Retraining"],["A49","Business"],["A410","Other"]]}/>
            <SelectField label="Savings" name="savings_status" value={form.savings_status} onChange={handleChange} options={[["A61","Below 100 DM"],["A62","100–500 DM"],["A63","500–1000 DM"],["A64","1000+ DM"],["A65","Unknown / no savings"]]}/>
            <SelectField label="Employment" name="employment_status" value={form.employment_status} onChange={handleChange} options={[["A71","Unemployed"],["A72","Less than 1 year"],["A73","1–4 years"],["A74","4–7 years"],["A75","7+ years"]]}/>
            <SelectField label="Housing" name="housing" value={form.housing} onChange={handleChange} options={[["A151","Rent"],["A152","Own"],["A153","Free"]]}/>
            <NumberField label="Existing Credits" name="existing_credits" value={form.existing_credits} onChange={handleChange}/>
            <NumberField label="Dependents" name="dependents" value={form.dependents} onChange={handleChange}/>
          </div>
          <div className="info-strip">ⓘ Occupation labels are demo context only; the model uses the editable credit attributes above.</div>
          {inputsModified && <div className="stale-warning">↻ Applicant inputs modified <strong>Re-run assessment to refresh risk & SHAP</strong></div>}
          <button className="primary-button assess-button" onClick={runAssessment} disabled={loading}>{loading ? "Running risk model..." : inputsModified ? "Re-run Risk Assessment  →" : "Run Risk Assessment  →"}</button>
          {error && <div className="error">{error}</div>}
        </section>

        <section className="panel risk-panel premium-panel">
          <div className="panel-heading"><div><p className="eyebrow">02 · DECISION SUPPORT</p><h2>Risk Intelligence</h2><p>Model probability with local SHAP attribution.</p></div><span className="model-chip">RF · v{result?.model_version || '—'}</span></div>
          {!result ? <div className="empty-state"><div className="radar-icon"><span></span></div><h3>Ready for assessment</h3><p>Run the applicant through the trained credit-risk model to reveal probability and contributing factors.</p></div> : <>
            <div className={`risk-hero ${riskClass} ${inputsModified ? 'stale' : ''}`}>
              <div className="risk-ring" style={{'--risk': `${result.risk_percentage * 3.6}deg`}}><div><span>BAD-RISK<br/>PROBABILITY</span><strong>{result.risk_percentage}%</strong><em>{result.risk_level} RISK</em></div></div>
              <div className="risk-copy"><span className={`risk-badge ${riskClass}`}>● {result.risk_level} RISK BAND</span><h3>Model assessment</h3><p>Estimated probability from the trained Random Forest credit-risk pipeline.</p><div className="risk-scale"><i></i><span>0%</span><span>30%</span><span>60%</span><span>100%</span></div></div>
            </div>
            {inputsModified && <div className="stale-overlay-note">Displayed result reflects the previous inputs.</div>}
            <div className="shap-block"><div className="section-minihead"><div><p className="eyebrow">EXPLAINABILITY · SHAP</p><h3>Key model drivers</h3></div><span>Contribution to prediction</span></div>
              <div className="factor-list">{result.top_factors?.map((f)=><div className="factor" key={f.feature}><div className={`factor-icon ${f.impact>0?'risk-up-bg':'risk-down-bg'}`}>{f.impact>0?'↑':'↓'}</div><div className="factor-main"><strong>{f.feature.replaceAll('_',' ').replace(/\b\w/g,c=>c.toUpperCase())}</strong><small>{f.impact>0?'Pushes toward higher modeled risk':'Pushes toward lower modeled risk'}</small></div><span className={f.impact>0?'risk-up':'risk-down'}>{f.direction}</span></div>)}</div>
              <p className="micro-note">SHAP describes model influence, not causation. The output is decision support and not an automated approval or denial.</p>
            </div>
          </>}
        </section>
      </main>

      <section className="full-section intelligence-section">
        <div className="section-header"><div><p className="eyebrow">03 · ALTERNATIVE DATA INTELLIGENCE</p><h2>Transaction Behavior</h2><p>Supplementary signals derived from synthetic transaction history.</p></div><span className="synthetic-badge">SYNTHETIC · DEMO DATA</span></div>
        <div className="split-layout"><div className="upload-card premium-upload"><div className="upload-icon">⇧</div><h3>Transaction Statement</h3><p>CSV with date, description, amount and transaction type.</p><label className="file-upload"><span>{transactionFile ? transactionFile.name : "Drop or choose transaction CSV"}</span><small>CSV · validated before analysis</small><input type="file" accept=".csv" onChange={(e)=>{setTransactionFile(e.target.files[0]);setBehaviorResult(null);setBehaviorError("");}}/></label><button className="secondary-button" onClick={analyzeTransactions} disabled={behaviorLoading}>{behaviorLoading?"Analyzing cash flows...":"Analyze Transactions  →"}</button>{behaviorError&&<div className="error">{behaviorError}</div>}</div>
          <div className="behavior-results">{!behaviorResult?<div className="empty-inline"><span>⌁</span><div><h3>Behavioral signals awaiting data</h3><p>Upload the matching synthetic transaction history to activate alternative-data intelligence.</p></div></div>:<><div className="analysis-success"><span>✓</span><div><strong>Behavioral analysis complete</strong><small>{behaviorResult.months_analyzed} months · {behaviorResult.total_transactions} transactions</small></div></div><div className="metric-grid">
            <MetricCard label="Income Stability" value={`${behaviorResult.income_stability}%`} pct={behaviorResult.income_stability}/><MetricCard label="Cash-flow Consistency" value={`${behaviorResult.cashflow_consistency}%`} pct={behaviorResult.cashflow_consistency}/><MetricCard label="Average Savings Rate" value={`${behaviorResult.average_savings_rate}%`} pct={Math.max(0,behaviorResult.average_savings_rate)}/><MetricCard label="Spending Volatility" value={behaviorResult.spending_volatility} sub={`Score ${behaviorResult.spending_volatility_score}`} pct={Math.max(0,100-behaviorResult.spending_volatility_score)}/>
          </div><p className="micro-note">Behavioral indicators are supplementary and are not incorporated into the trained risk probability.</p></>}</div></div>
      </section>

      <section className="full-section capacity-section">
        <div className="section-header"><div><p className="eyebrow">04 · REPAYMENT CAPACITY</p><h2>Affordability Intelligence</h2><p>Illustrative capacity analysis using observed cash flow and city living-cost reference.</p></div><button className="secondary-button compact" onClick={analyzeAffordability} disabled={affordabilityLoading||!result||!behaviorResult}>{affordabilityLoading?"Calculating...": affordabilityResult ? "↻ Recalculate Capacity": "Calculate Capacity  →"}</button></div>
        {affordabilityError&&<div className="error">{affordabilityError}</div>}
        {!affordabilityResult?<div className="empty-inline centered"><span>₹</span><div><h3>Capacity model ready</h3><p>Complete risk and transaction analysis to calculate repayment capacity.</p></div></div>:<><div className="capacity-grid"><StatCard label="Stable Monthly Income" value={`₹${affordabilityResult.stable_monthly_income.toLocaleString()}`} /><StatCard label="Living Expense Used" value={`₹${affordabilityResult.living_expense_used.toLocaleString()}`} sub={`${form.city} reference considered`} /><StatCard label="Repayment Surplus" value={`₹${affordabilityResult.repayment_surplus.toLocaleString()}`} /><StatCard label="Safety Buffer" value={`₹${affordabilityResult.safety_buffer.toLocaleString()}`} /></div><div className="capacity-hero"><div><span>AFFORDABLE EMI</span><strong>₹{affordabilityResult.affordable_emi.toLocaleString()}</strong><small>Illustrative monthly capacity</small></div><i></i><div><span>INDICATIVE LOAN CAPACITY</span><strong>₹{affordabilityResult.indicative_loan_capacity.toLocaleString()}</strong><small>{affordabilityResult.duration_months} months · {affordabilityResult.estimated_apr}% prototype APR</small></div></div><p className="micro-note">City references, safety buffer, APR and capacity are prototype assumptions — not a lending offer, approval or actual lender pricing.</p></>}
      </section>

      <section className="full-section evidence-section">
        <div className="section-header"><div><p className="eyebrow">05 · SUPPORTING EVIDENCE · RAG</p><h2>Document Intelligence</h2><p>Turn supporting financial documents into retrievable, grounded evidence.</p></div><span className="synthetic-badge">SYNTHETIC · DEMO DATA</span></div>
        <div className="document-layout"><div className="upload-card premium-upload"><div className="upload-icon">▤</div><h3>Supporting Financial Document</h3><p>Text-based PDF with synthetic income, obligations, payment or cash-flow evidence.</p><label className="file-upload"><span>{documentFile?documentFile.name:"Drop or choose supporting PDF"}</span><small>PDF · max 5 MB · validated</small><input type="file" accept=".pdf,application/pdf" onChange={(e)=>{setDocumentFile(e.target.files[0]);setDocumentResult(null);setDocumentError("");setAiExplanation("");setAiError("");}}/></label><button className="secondary-button" onClick={indexDocument} disabled={documentLoading}>{documentLoading?"Extracting & indexing...":"Process & Index Document  →"}</button>{documentError&&<div className="error">{documentError}</div>}</div>
          <div className="pipeline-card"><div className="pipeline-title"><div><span>RAG PROCESSING PIPELINE</span><h3>{documentResult?"Document intelligence ready":"Awaiting document"}</h3></div><span className={documentResult?'ready-pill':'waiting-pill'}>{documentResult?'● READY':'○ WAITING'}</span></div><div className="pipeline-flow"><PipelineStep done={!!documentResult} icon="01" title="Extracted" meta={documentResult?`${documentResult.page_count} page${documentResult.page_count===1?'':'s'}`:'PDF text'}/><b>→</b><PipelineStep done={!!documentResult} icon="02" title="Chunked" meta={documentResult?`${documentResult.chunks_stored} chunks`:'500 chars'}/><b>→</b><PipelineStep done={!!documentResult} icon="03" title="Embedded" meta="384-D vectors"/><b>→</b><PipelineStep done={!!documentResult} icon="04" title="Indexed" meta="Postgres · pgvector"/></div>{documentResult&&<div className="document-success">✓ {documentResult.filename} · {documentResult.character_count.toLocaleString()} characters · ready for semantic retrieval</div>}</div></div>
      </section>

      <section className="full-section ai-section">
        <div className="ai-glow"></div><div className="section-header ai-header"><div><p className="eyebrow light">06 · GENERATIVE AI · GROUNDED RAG</p><h2>Credit Intelligence Explanation</h2><p>One grounded narrative across model output, SHAP, behavioral signals and retrieved evidence.</p></div><span className="guardrail-badge">◆ GUARDRAILED · EXPLAINABILITY ONLY</span></div>
        <div className="readiness-row"><ReadyItem ready={!!result} label="Risk assessment"/><ReadyItem ready={!!behaviorResult} label="Behavioral signals"/><ReadyItem ready={!!documentResult} label="Document evidence"/><ReadyItem ready={!!(result&&behaviorResult&&documentResult)} label="Ready for synthesis"/></div>
        <button className="ai-button" onClick={generateAIExplanation} disabled={aiLoading||!result||!behaviorResult||!documentResult}>{aiLoading?<><span className="spinner"></span> Synthesizing grounded intelligence...</>:"✦ Generate Grounded Intelligence  →"}</button>
        {aiLoading&&<div className="ai-loading"><div><span>✓</span> Risk assessment available</div><div><span>✓</span> Behavioral signals incorporated</div><div><span>✓</span> Supporting evidence retrieved</div><div className="active"><span>◉</span> Generating grounded explanation...</div></div>}
        {aiError&&<div className="error dark-error">{aiError}</div>}
        {aiExplanation&&<div className="ai-output"><div className="ai-output-head"><span>✦</span><div><small>GROUNDED AI EXPLANATION</small><strong>Evidence-backed decision support</strong></div><em>Generated</em></div><ReactMarkdown>{aiExplanation}</ReactMarkdown></div>}
        <p className="ai-disclaimer">Gemini explains supplied model outputs and synthetic evidence only. It does not calculate risk probability, approve/reject credit, or determine lender pricing.</p>
      </section>

      <footer><div className="brand-lockup"><span className="brand-mark small">CI</span><strong>Credit Intelligence</strong></div><span>Prototype decision-support system · Explainability by design · Synthetic alternative data</span></footer>
    </div>
  );
}

const MetricCard=({label,value,pct,sub})=><div className="metric-card"><span>{label}</span><strong>{value}</strong>{sub&&<small>{sub}</small>}<div className="metric-track"><i style={{width:`${Math.min(100,Math.max(0,pct))}%`}}></i></div></div>;
const StatCard=({label,value,sub})=><div className="stat-card"><span>{label}</span><strong>{value}</strong>{sub&&<small>{sub}</small>}</div>;
const PipelineStep=({done,icon,title,meta})=><div className={`pipeline-step ${done?'done':''}`}><span>{done?'✓':icon}</span><strong>{title}</strong><small>{meta}</small></div>;
const ReadyItem=({ready,label})=><div className={ready?'ready-item ready':'ready-item'}><span>{ready?'✓':'○'}</span>{label}</div>;

export default App;
