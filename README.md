# Next-Gen Credit Intelligence

An explainable, multi-modal credit underwriting prototype designed to
support credit assessment for **New-to-Credit (NTC) and thin-file
customers** using traditional credit attributes, synthetic behavioral
transaction data, supporting financial documents, explainable machine
learning, and grounded generative AI.

> **Prototype Disclaimer:** This project is a decision-support prototype
> developed using historical and synthetic/demo data. It does not
> constitute a production lending system or an actual credit approval,
> rejection, pricing, or underwriting policy.

------------------------------------------------------------------------

## 1. Problem Statement

Traditional credit underwriting depends heavily on established credit
histories. This can make assessment difficult for New-to-Credit and
thin-file customers who may have limited conventional credit
information.

This prototype explores a multi-modal credit intelligence architecture
combining:

-   Traditional credit-risk attributes
-   Transaction-derived behavioral indicators
-   Repayment-capacity analysis
-   Supporting financial documents
-   Explainable machine learning
-   Semantic retrieval using vector embeddings
-   Grounded LLM-generated explanations

The system is designed so that the LLM **does not independently make
lending decisions or modify the model-generated risk score**.

------------------------------------------------------------------------

## 2. System Architecture

```text
React Analyst Dashboard
        |
        | JWT
        v
FastAPI API Service
        |
        +-------------------+----------------------+
        |                   |                      |
        v                   v                      v
Credit Risk Model    Transaction Analysis     PDF Documents
Random Forest        Behavioral Metrics       Text Extraction
        |                   |                      |
        v                   v                      v
SHAP Explainability  Affordability Engine       Chunking
                                                   |
                                                   v
                                                Embeddings
                                                   |
                                                   v
                                          PostgreSQL + pgvector
                                                   |
                                                   v
                                           Semantic Retrieval
                                                   |
                                                   v
                                                 Gemini
                                                   |
                                                   v
                                          Grounded Explanation
```

------------------------------------------------------------------------

## 3. Core Design Principle

The system deliberately separates responsibilities:

**Machine Learning** - Estimates credit-risk probability - Assigns an
illustrative risk band

**SHAP** - Explains which model features contributed to the prediction -
Contributions are model influences, not causal conclusions

**Behavioral Intelligence** - Derives supplementary indicators from
synthetic transaction data

**Affordability Engine** - Uses deterministic financial calculations to
estimate repayment capacity

**RAG Pipeline** - Retrieves relevant supporting-document evidence using
vector similarity

**Gemini** - Generates a grounded explanation from supplied model
outputs and retrieved evidence - Does not recalculate or override the
credit-risk probability - Does not approve or reject applicants

------------------------------------------------------------------------

## 4. Features

### Credit Risk Assessment

The current prototype uses a Random Forest classifier trained on the project's Loan-Dataset, containing 32,586 rows before target cleaning. The model uses eight features available through the application flow:

- Customer age
- Annual income
- Home ownership
- Employment duration
- Loan intent
- Requested loan amount
- Loan duration
- Loan-to-income ratio

The model produces:

- Predicted bad-credit/default risk probability
- Illustrative LOW / MEDIUM / HIGH risk band
- SHAP-based contributing factors

Prototype risk bands are:

- LOW: probability < 0.30
- MEDIUM: 0.30 <= probability < 0.60
- HIGH: probability >= 0.60

These thresholds are prototype assumptions and are not lender underwriting rules.

### Data Quality and Feature Review

During model development, the `historical_default` field showed a suspicious relationship with the target, including missing values that behaved as a strong proxy for the outcome. Rather than preserving an artificially strong signal, the field was removed from the final model.

This reduced headline model performance but produced a cleaner eight-feature prototype with inputs that are available through the application workflow.

### Prototype Monetary Normalization

The source dataset contains monetary values whose currency/context is not treated as representative of the Indian lending population. For the prototype operating scale, income and loan amounts are transformed using the same fixed scale factor, anchored so the source median income maps to INR 1,200,000. Applying the same factor to both fields preserves the loan-to-income ratio.

This is a prototype INR normalization for the demo interface, not a literal currency conversion and not a claim that the source data is Indian.

### Explainable AI with SHAP

SHAP is used to expose feature contributions to individual predictions. Positive SHAP contributions push the model toward higher predicted bad-credit risk, while negative contributions push it toward lower predicted risk.

SHAP values are interpreted as model contributions and **not causal relationships**.

### Transaction Behavioral Intelligence

Synthetic transaction CSV files are analyzed to derive:

- Income stability
- Cash-flow consistency
- Spending volatility
- Average savings rate
- Stable monthly income
- Observed monthly expenses
- Median monthly net cash flow

Alternative transaction data used in the prototype is synthetic/demo data and is supplementary evidence; it is not part of the trained credit-risk probability.

### Repayment Capacity Analysis

The affordability module estimates:

- Living expense used
- Repayment surplus
- Affordable monthly EMI
- Safety buffer
- Illustrative APR
- Indicative loan capacity

The module uses deterministic calculations rather than an LLM. City living-cost references, EMI utilization assumptions, and APR mappings are illustrative prototype assumptions and are not official lender policies. Risk and affordability are intentionally treated as related but separate decision-support components.

### Supporting Financial Documents

The system accepts synthetic supporting PDF documents and performs:

1. PDF text extraction
2. Text chunking
3. Embedding generation
4. Vector storage in PostgreSQL using pgvector
5. Document-scoped semantic similarity retrieval

The embedding model used is `all-MiniLM-L6-v2`. Scanned PDFs requiring OCR are not supported by the current prototype.

### Grounded Generative AI Explanation

Retrieved evidence, model results, SHAP factors, and behavioral indicators are supplied to Gemini to produce a structured explanation.

The prompt contains explicit guardrails preventing the LLM from:

- Creating or modifying risk probabilities
- Changing risk bands
- Approving or rejecting applicants
- Making lending or pricing recommendations
- Treating SHAP contributions as causal
- Inventing missing evidence
- Following instructions contained inside retrieved documents

## 5. Prompt-Injection Defense

Retrieved document content is treated as **untrusted external
evidence**. The LLM is explicitly instructed to treat document contents
as data rather than executable instructions.

The RAG pipeline was tested using an adversarial synthetic PDF
containing instructions attempting to override the supplied risk
probability, force an approval, and generate a lending recommendation.
The system prompt preserved the supplied model assessment and instructed
the model to ignore commands embedded in retrieved evidence.

------------------------------------------------------------------------

## 6. Technology Stack

**Frontend:** React, Vite, Axios, React Markdown

**Backend:** Python, FastAPI, Pydantic, SQLAlchemy

**Machine Learning:** Scikit-learn, Random Forest, SHAP, Pandas, NumPy

**AI / RAG:** Google Gemini, Sentence Transformers, `all-MiniLM-L6-v2`,
semantic retrieval

**Database:** PostgreSQL, pgvector

**Security:** JWT authentication, role-based API authorization, bcrypt
password hashing, environment-based secret management, file and input
validation

**Infrastructure & Engineering:** Docker, Git, Pytest

------------------------------------------------------------------------

## 7. Repository Structure

```text
synchrony-credit-intelligence/
├── backend/
│   └── app/
│       ├── core/
│       ├── models/
│       ├── routers/
│       ├── schemas/
│       ├── services/
│       ├── database.py
│       └── main.py
├── frontend/
│   ├── public/
│   │   └── data/
│   └── src/
├── ml/
│   ├── data/
│   └── artifacts/
├── tests/
├── docs/
├── logs/                  # Runtime only; excluded from Git
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

------------------------------------------------------------------------

## 8. Local Setup

### Prerequisites

Install: - Python 3.12+ - Node.js / npm - Docker Desktop - Git

### Clone the Repository

``` bash
git clone <repository-url>
cd synchrony-credit-intelligence
```

### Create Python Virtual Environment

``` powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Install Python Dependencies

``` powershell
python -m pip install -r requirements.txt
```

### Install Frontend Dependencies

``` powershell
cd frontend
npm install
cd ..
```

------------------------------------------------------------------------

## 9. Environment Configuration

Create a `.env` file in the project root using `.env.example` as the template. On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Then configure:

```env
GEMINI_API_KEY=your_gemini_api_key
JWT_SECRET_KEY=your_jwt_secret_key
DATABASE_URL=postgresql://credit_user:your_password@127.0.0.1:5433/credit_intelligence
POSTGRES_DB=credit_intelligence
POSTGRES_USER=credit_user
POSTGRES_PASSWORD=your_password
```

Real credentials must not be committed to source control.

------------------------------------------------------------------------

## 10. Start PostgreSQL + pgvector

``` powershell
docker compose up -d
docker ps
```

The local database is exposed on port `5433`.

------------------------------------------------------------------------

## 11. Start the Backend

From the project root with the virtual environment activated:

``` powershell
uvicorn backend.app.main:app
```

Backend: `http://127.0.0.1:8000`

Swagger API documentation: `http://127.0.0.1:8000/docs`

------------------------------------------------------------------------

## 12. Start the Frontend

Open another terminal:

``` powershell
cd frontend
npm run dev
```

Then open `http://localhost:5173`.

------------------------------------------------------------------------

## 13. Authentication

The prototype provides analyst authentication using email/password
authentication, bcrypt password hashing, JWT access tokens, protected
API endpoints, and ANALYST role authorization.

The following APIs require authenticated analyst access:

``` text
/predict
/behavior/analyze
/affordability/analyze
/documents/index
/documents/search
/intelligence/explain
```

The health endpoint and login endpoint remain public.

------------------------------------------------------------------------

## 14. Automated Testing

The project includes **23 automated tests** covering major application
components.

  Test Area                             Tests
  ---------------------------------- --------
  Authentication & API protection           4
  ML prediction & input validation          3
  Behavioral transaction analysis           4
  Affordability calculations                4
  PDF ingestion & validation                4
  LLM safety and prompt guardrails          4
  **Total**                            **23**

Run the verified core suite from the project root:

```powershell
python -m pytest tests/test_auth.py tests/test_prediction.py tests/test_behavioral.py tests/test_affordability.py tests/test_documents.py tests/test_ai_guardrails.py -v
```

Current verified result: **23 passed**.

LLM guardrail tests mock the external Gemini call so automated safety tests do not depend on external API availability or consume API quota. Standalone live Gemini/LLM integration tests are intentionally excluded from the core command because they may invoke the external API and consume quota.

------------------------------------------------------------------------

## 15. Security Controls

Prototype security controls include:

- JWT authentication
- Role-based authorization
- bcrypt password hashing
- Protected backend endpoints
- Environment-based secret management
- `.env` excluded from Git
- Pydantic request validation
- CSV and PDF validation
- File-size restrictions
- Prompt-injection defenses for retrieved documents
- Generic API error handling
- Privacy-conscious structured application logging

Passwords, JWTs, API keys, full transaction records, and document contents are not intentionally written to application logs.

These controls demonstrate secure engineering practices but do not represent a complete production financial-security architecture.

### Application Logging

Structured application logging covers:

- Authentication and authorization
- Risk assessment
- Behavioral transaction analysis
- Affordability analysis and loan-capacity calculation
- Supporting-document indexing
- RAG retrieval
- Grounded AI explanation generation

Logs are written to both the backend terminal and:

```text
logs/credit_intelligence.log
```

The runtime `logs/` directory is excluded from Git. A production deployment would normally centralize logs in a managed observability platform with retention, alerting, and access controls.

------------------------------------------------------------------------

## 16. Responsible AI and Transparency

The prototype is designed as an analyst decision-support tool rather
than an autonomous lending decision maker.

The LLM cannot independently modify the trained model's risk probability
or risk band. SHAP provides visibility into model feature contributions,
while LLM explanations are grounded in supplied model outputs,
behavioral indicators, and retrieved document evidence.

Transaction and supporting-document data used for the demonstration are
synthetic. Risk thresholds, city living-cost references, APR mappings,
and affordability parameters are illustrative prototype assumptions.

------------------------------------------------------------------------

## 17. Dataset and Model Limitations

The current credit-risk model uses the project's Loan-Dataset with 32,586 rows before target cleaning. It is not presented as representative of the Indian lending population or as current lender/customer data.

Important limitations:

- Source monetary values are normalized to a prototype INR operating scale; this is not a literal currency conversion.
- The dataset is not claimed to represent all modern lending populations.
- The `historical_default` feature was removed after a suspicious target/proxy relationship was identified.
- Model performance on this dataset does not establish production underwriting performance.
- The prototype has not undergone production-grade fairness, drift, calibration, or regulatory validation.
- Alternative behavioral and supporting-document data in the demonstration is synthetic and was not used to train the credit-risk model.
- Random Forest models do not extrapolate smoothly outside regions represented in training data; extreme requested-loan values can therefore reach similar terminal leaves.
- Risk-band thresholds, city living-cost references, APR mappings, and affordability parameters are illustrative prototype assumptions.

------------------------------------------------------------------------

## 18. Model Evaluation

The final eight-feature Random Forest achieved the following held-out test performance:

| Metric | Result |
|---|---:|
| Accuracy | 0.8347 |
| Precision | 0.5989 |
| Recall | 0.6440 |
| F1 Score | 0.6206 |
| ROC-AUC | 0.8529 |

Confusion matrix:

```text
[[4559, 590],
 [ 487, 881]]
```

The final model prioritizes a cleaner feature set aligned with the application inputs rather than retaining the suspicious `historical_default` proxy merely to maximize headline metrics.

------------------------------------------------------------------------

## 19. Current Prototype Scope

Implemented: - React analyst dashboard - Credit-risk ML inference - SHAP
explainability - Synthetic transaction analysis - Repayment-capacity
analysis - PDF extraction - Embedding generation - PostgreSQL + pgvector
semantic retrieval - Grounded Gemini explanation - Prompt-injection
guardrails - JWT authentication and authorization - Structured application
logging - Dockerized database - Automated testing

Not claimed as production functionality: - Production lender
integration - Real customer data ingestion - Official lending/pricing
policy - Production fairness certification - Full regulatory
validation - Production-grade identity management - Production cloud
deployment

------------------------------------------------------------------------

## 20. End-to-End Flow

```text
Applicant Profile
      |
      v
Credit Risk Model
      |
      v
Risk Probability + Risk Band
      |
      v
SHAP Explanation
      |
      +-------- Transaction CSV
      |                |
      |                v
      |        Behavioral Indicators
      |                |
      |                v
      |        Affordability Analysis
      |
      +-------- Supporting PDF
                       |
                       v
                 Text Extraction
                       |
                       v
                    Chunking
                       |
                       v
                   Embeddings
                       |
                       v
              PostgreSQL + pgvector
                       |
                       v
                Semantic Retrieval
                       |
                       v
                     Gemini
                       |
                       v
              Grounded Explanation
```

------------------------------------------------------------------------

## 21. Purpose

This project demonstrates how traditional machine learning,
explainability, alternative behavioral signals, deterministic financial
analysis, vector retrieval, and generative AI can be combined into a
transparent multi-modal credit-intelligence prototype while maintaining
a clear separation between **risk estimation, evidence analysis, and
AI-generated explanation**.