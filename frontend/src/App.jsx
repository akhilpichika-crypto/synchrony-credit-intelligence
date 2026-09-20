import { useState } from "react";
import axios from "axios";
import "./App.css";

const initialForm = {
  checking_status: "A11",
  duration_months: 6,
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
  const [aiExplanation, setAiExplanation] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState("");

  const handleChange = (event) => {
    const { name, value, type } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: type === "number" ? Number(value) : value,
    }));
  };

  const runAssessment = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/predict",
        form
      );

      setResult(response.data);
    } catch (err) {
      console.error(err);
      setError("Unable to complete assessment. Check that the API is running.");
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

    const formData = new FormData();
    formData.append("file", transactionFile);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/behavior/analyze",
        formData
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

  const generateAIExplanation = async () => {
    if (!result) {
      setAiError("Run the credit risk assessment first.");
      return;
    }

    if (!behaviorResult) {
      setAiError("Analyze the transaction statement first.");
      return;
    }

    setAiLoading(true);
    setAiError("");
    setAiExplanation("");

    try {
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

          query:
            "What evidence describes the applicant's income stability, financial obligations, payment behavior and cash flow?",
        }
      );

      setAiExplanation(response.data.explanation);
    } catch (err) {
      console.error(err);

      setAiError(
        err.response?.data?.detail ||
          "Unable to generate AI explanation."
      );
    } finally {
      setAiLoading(false);
    }
  };

  const riskClass = result
    ? result.risk_level.toLowerCase()
    : "";

  return (
    <div className="app">
      <header>
        <div>
          <div className="brand">CREDIT INTELLIGENCE</div>
          <h1>Next-Gen Underwriting Engine</h1>
          <p>
            Explainable AI-powered credit risk assessment for
            new-to-credit and thin-file applicants.
          </p>
        </div>

        <div className="status">
          <span></span>
          Model Online
        </div>
      </header>

      <main>
        <section className="panel applicant-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">APPLICATION</p>
              <h2>Applicant Profile</h2>
            </div>
            <div className="step">01</div>
          </div>

          <div className="form-grid">
            <NumberField
              label="Credit Amount"
              name="credit_amount"
              value={form.credit_amount}
              onChange={handleChange}
            />

            <NumberField
              label="Duration (months)"
              name="duration_months"
              value={form.duration_months}
              onChange={handleChange}
            />

            <NumberField
              label="Age"
              name="age"
              value={form.age}
              min={18}
              onChange={handleChange}
            />

            <NumberField
              label="Installment Rate"
              name="installment_rate"
              value={form.installment_rate}
              onChange={handleChange}
            />

            <SelectField
              label="Checking Account"
              name="checking_status"
              value={form.checking_status}
              onChange={handleChange}
              options={[
                ["A11", "Below 0 DM"],
                ["A12", "0–200 DM"],
                ["A13", "200+ DM"],
                ["A14", "No checking account"],
              ]}
            />

            <SelectField
              label="Credit History"
              name="credit_history"
              value={form.credit_history}
              onChange={handleChange}
              options={[
                ["A30", "No previous credit"],
                ["A31", "All credits paid"],
                ["A32", "Credits paid properly"],
                ["A33", "Payment delays"],
                ["A34", "Critical / other credits"],
              ]}
            />

            <SelectField
              label="Purpose"
              name="purpose"
              value={form.purpose}
              onChange={handleChange}
              options={[
                ["A40", "New car"],
                ["A41", "Used car"],
                ["A42", "Furniture / equipment"],
                ["A43", "Radio / television"],
                ["A44", "Domestic appliances"],
                ["A45", "Repairs"],
                ["A46", "Education"],
                ["A48", "Retraining"],
                ["A49", "Business"],
                ["A410", "Other"],
              ]}
            />

            <SelectField
              label="Savings"
              name="savings_status"
              value={form.savings_status}
              onChange={handleChange}
              options={[
                ["A61", "Below 100 DM"],
                ["A62", "100–500 DM"],
                ["A63", "500–1000 DM"],
                ["A64", "1000+ DM"],
                ["A65", "Unknown / no savings"],
              ]}
            />

            <SelectField
              label="Employment"
              name="employment_status"
              value={form.employment_status}
              onChange={handleChange}
              options={[
                ["A71", "Unemployed"],
                ["A72", "Less than 1 year"],
                ["A73", "1–4 years"],
                ["A74", "4–7 years"],
                ["A75", "7+ years"],
              ]}
            />

            <SelectField
              label="Housing"
              name="housing"
              value={form.housing}
              onChange={handleChange}
              options={[
                ["A151", "Rent"],
                ["A152", "Own"],
                ["A153", "Free"],
              ]}
            />

            <NumberField
              label="Existing Credits"
              name="existing_credits"
              value={form.existing_credits}
              onChange={handleChange}
            />

            <NumberField
              label="Dependents"
              name="dependents"
              value={form.dependents}
              onChange={handleChange}
            />
          </div>

          <div className="advanced-note">
            Additional model attributes are populated from the complete
            applicant profile for this prototype.
          </div>

          <button
            className="assess-button"
            onClick={runAssessment}
            disabled={loading}
          >
            {loading ? "Analyzing Applicant..." : "Run Risk Assessment"}
          </button>

          {error && <div className="error">{error}</div>}
        </section>

        <section className="panel result-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">DECISION SUPPORT</p>
              <h2>Risk Assessment</h2>
            </div>
            <div className="step">02</div>
          </div>

          {!result ? (
            <div className="empty-result">
              <div className="empty-icon">◎</div>
              <h3>Awaiting assessment</h3>
              <p>
                Complete the applicant profile and run the model to
                generate a credit-risk assessment.
              </p>
            </div>
          ) : (
            <div className="result-content">
              <p className="result-label">ESTIMATED BAD-RISK PROBABILITY</p>

              <div className={`score ${riskClass}`}>
                {result.risk_percentage}%
              </div>

              <div className={`risk-badge ${riskClass}`}>
                {result.risk_level} RISK
              </div>

              <div className="meter">
                <div
                  className={`meter-fill ${riskClass}`}
                  style={{ width: `${result.risk_percentage}%` }}
                />
              </div>

              <div className="range-labels">
                <span>Lower risk</span>
                <span>Higher risk</span>
              </div>

              <div className="summary-card">
                <div>
                  <span>Model</span>
                  <strong>Credit Risk v{result.model_version}</strong>
                </div>

                <div>
                  <span>Assessment</span>
                  <strong>Decision Support</strong>
                </div>

                <div>
                  <span>Probability</span>
                  <strong>{result.risk_probability}</strong>
                </div>
              </div>

              <div className="explanation-placeholder">
                <p className="eyebrow">EXPLAINABILITY · SHAP</p>
                <h3>Key contributing factors</h3>

                <div className="factor-list">
                  {result.top_factors?.map((factor) => (
                    <div className="factor" key={factor.feature}>
                      <div className="factor-info">
                        <span
                          className={
                            factor.impact > 0
                              ? "factor-arrow risk-up"
                              : "factor-arrow risk-down"
                          }
                        >
                          {factor.impact > 0 ? "↑" : "↓"}
                        </span>

                        <span className="factor-name">
                          {factor.feature
                            .replaceAll("_", " ")
                            .replace(/\b\w/g, (c) => c.toUpperCase())}
                        </span>
                      </div>

                      <span
                        className={
                          factor.impact > 0
                            ? "factor-direction risk-up"
                            : "factor-direction risk-down"
                        }
                      >
                        {factor.direction}
                      </span>
                    </div>
                  ))}
                </div>

                <p className="shap-note">
                  SHAP values indicate how each feature influenced this model
                  prediction and do not imply causation.
                </p>
              </div>
            </div>
          )}

          <div className="disclaimer">
            Prototype decision-support system. The model output is not
            an automated credit approval or denial.
          </div>
        </section>
      </main>
      <section className="behavior-section">
        <div className="behavior-header">
          <div>
            <p className="eyebrow">ALTERNATIVE DATA INTELLIGENCE</p>
            <h2>Transaction Behavior Analysis</h2>
            <p className="behavior-description">
              Supplement the traditional credit model with behavioral signals
              derived from transaction history.
            </p>
          </div>

          <span className="synthetic-badge">
            SYNTHETIC / DEMO DATA
          </span>
        </div>

        <div className="behavior-grid">
          <div className="upload-card">
            <h3>Transaction Statement</h3>

            <p>
              Upload a synthetic CSV containing transaction date,
              description, amount and type.
            </p>

            <label className="file-upload">
              <span>
                {transactionFile
                  ? transactionFile.name
                  : "Choose transaction CSV"}
              </span>

              <input
                type="file"
                accept=".csv"
                onChange={(event) => {
                  setTransactionFile(event.target.files[0]);
                  setBehaviorResult(null);
                  setBehaviorError("");
                }}
              />
            </label>

            <button
              className="analyze-button"
              onClick={analyzeTransactions}
              disabled={behaviorLoading}
            >
              {behaviorLoading
                ? "Analyzing Transactions..."
                : "Analyze Transactions"}
            </button>

            {behaviorError && (
              <div className="error">{behaviorError}</div>
            )}
          </div>

          <div className="behavior-results">
            {!behaviorResult ? (
              <div className="behavior-empty">
                <div className="empty-icon">◎</div>
                <h3>Awaiting transaction data</h3>
                <p>
                  Behavioral indicators will appear after the
                  synthetic transaction statement is analyzed.
                </p>
              </div>
            ) : (
              <>
                <div className="analysis-meta">
                  <strong>Analysis complete</strong>
                  <span>
                    {behaviorResult.months_analyzed} months ·{" "}
                    {behaviorResult.total_transactions} transactions
                  </span>
                </div>

                <div className="metric">
                  <div>
                    <span>Income Stability</span>
                    <strong>
                      {behaviorResult.income_stability}%
                    </strong>
                  </div>

                  <div className="metric-bar">
                    <div
                      style={{
                        width: `${behaviorResult.income_stability}%`,
                      }}
                    />
                  </div>
                </div>

                <div className="metric">
                  <div>
                    <span>Cash-flow Consistency</span>
                    <strong>
                      {behaviorResult.cashflow_consistency}%
                    </strong>
                  </div>

                  <div className="metric-bar">
                    <div
                      style={{
                        width: `${behaviorResult.cashflow_consistency}%`,
                      }}
                    />
                  </div>
                </div>

                <div className="metric">
                  <div>
                    <span>Average Savings Rate</span>
                    <strong>
                      {behaviorResult.average_savings_rate}%
                    </strong>
                  </div>

                  <div className="metric-bar">
                    <div
                      style={{
                        width: `${Math.max(
                          0,
                          behaviorResult.average_savings_rate
                        )}%`,
                      }}
                    />
                  </div>
                </div>

                <div className="volatility-card">
                  <span>Spending Volatility</span>

                  <strong>
                    {behaviorResult.spending_volatility}
                  </strong>

                  <small>
                    Variability score:{" "}
                    {behaviorResult.spending_volatility_score}
                  </small>
                </div>

                <p className="behavior-note">
                  Behavioral indicators supplement the model assessment
                  and are not incorporated into the trained credit-risk
                  probability.
                </p>
              </>
            )}
          </div>
        </div>
      </section>
      <section className="behavior-section">
        <div className="behavior-header">
          <div>
            <p className="eyebrow">GENERATIVE AI · GROUNDED RAG</p>
            <h2>Credit Intelligence Explanation</h2>

            <p className="behavior-description">
              Generate a grounded explanation using the model assessment,
              SHAP contributions, behavioral indicators and retrieved
              supporting-document evidence.
            </p>
          </div>

          <span className="synthetic-badge">
            EXPLAINABILITY ONLY
          </span>
        </div>

        <button
          className="analyze-button"
          onClick={generateAIExplanation}
          disabled={aiLoading || !result || !behaviorResult}
        >
          {aiLoading
            ? "Generating Explanation..."
            : "Generate AI Explanation"}
        </button>

        {aiError && (
          <div className="error">{aiError}</div>
        )}

        {aiExplanation && (
          <div className="ai-explanation">
            <pre>{aiExplanation}</pre>
          </div>
        )}

        <p className="behavior-note">
          Gemini explains the supplied model and synthetic evidence.
          It does not calculate the risk probability or make a credit
          approval or rejection decision.
        </p>
      </section>
    </div>
  );
}

export default App;