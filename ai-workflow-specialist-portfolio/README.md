# AI Workflow Specialist Portfolio

A practical portfolio of small automation systems demonstrating workflow design, AI-assisted processing, validation, integrations, and human-in-the-loop review.

## Projects

### 1. Job Application Assistant
Paste a job description and your CV to extract requirements, calculate a transparent keyword-overlap score, and draft a tailored cover letter. If an OpenAI API key is configured, the app can use an LLM for the draft; otherwise, it uses a deterministic template.

### 2. Support Ticket Triage
Classifies incoming support messages by category and urgency, recommends a team, and drafts a response. Rules-based triage works without an API key; optional AI drafting can be enabled.

### 3. CSV Operations Auditor
Upload an orders CSV to validate required fields, flag exceptions, calculate order totals, and download a cleaned report.

## Run locally

Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Optional AI integration:
1. Copy `.env.example` to `.env`.
2. Add your API key to `.env`.
3. Keep `.env` private; never commit secrets.

Without an API key, the core workflows still run using local rules and templates.

## Workflow architecture

```text
User input / uploaded file
          |
          v
Validation and normalization
          |
          v
Rules-based processing -----> Exception / confidence flags
          |
          +---- optional LLM API for drafting or summarization
          |
          v
Human review in Streamlit UI
          |
          v
Download / copy final output
```

## Safety and design choices

- No automatic sending of emails or external messages.
- AI-generated text is presented for human review before use.
- CSV validation flags questionable records instead of silently deleting them.
- API keys are read from environment variables.
- Demo data is fictional.

## Suggested demo walkthrough

1. Open the Job Application Assistant and paste a sample job description.
2. Open Support Ticket Triage and test an urgent access issue.
3. Upload `sample_orders.csv` in CSV Operations Auditor and download the exception report.

## Next improvements

- Add Gmail or Slack integrations with explicit user authorization.
- Add persistent audit logs and retry handling.
- Add automated tests and CI.
- Replace keyword overlap with semantic embeddings and evaluation.
- Deploy with Streamlit Community Cloud or another hosting platform.

## Portfolio note

This repository is a demonstrator. Describe it as a personal prototype and be clear about which integrations are implemented versus planned.
