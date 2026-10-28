# 💰 AI Financial Advisor

A Streamlit web app for personal budgeting: track transactions, see analytics, get **explainable** budget
recommendations, plan savings goals, learn about investment options, and ask an AI assistant questions about
your own numbers. Amounts are in Indian rupees (₹).

> Educational project. Not a licensed financial adviser. No live market data is used.

## Quick start

```bash
python3 -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env                # Windows: copy .env.example .env   (AI key is optional)
streamlit run app.py
```

On first launch click **Load synthetic demo data**. The app works fully without any API key.

### Enable the AI assistant (optional)
Edit `.env` and set `LLM_API_KEY`, `LLM_BASE_URL` and `LLM_MODEL` for any OpenAI-compatible provider
(check your provider's docs for the values). Without them the assistant answers in **fallback mode** using the
same computed numbers.

### Run the tests
```bash
python -m pytest
```

## Pages
| Page | What it does |
|---|---|
| Home (`app.py`) | First-run setup, KPI cards, emergency-fund progress, charts, top suggestions |
| Transactions | Add / edit / delete, filters, validated CSV import |
| Budget Planner | Unusual-spending detection, month comparison, personalised budget, optional 50/30/20 |
| Analytics | Income vs expenses, savings-rate trend, category trends, budget vs actual |
| AI Assistant | Chat grounded in computed figures, usage limit, fallback mode |
| Savings Goals | Required monthly amount, time to goal, handles zero / past-deadline / completed |
| Investment Education | Static comparison, "what to learn about" questionnaire, labelled illustrative projection |
| Reports and Settings | Monthly summary, CSV export, PDF report, profile, demo data, privacy notice |

## Architecture
```
Streamlit pages (app.py, pages/)  ->  src/ui.py helpers
        |
Logic (no Streamlit): analytics, budget_engine, recommendations, goal_planner,
                      investment_education, summary, reports, visualizations
        |                         |
   database.py (SQLite)     llm_assistant.py (LLM or fallback)
```
The LLM never does arithmetic and never sees raw transactions. `summary.py` computes a small summary;
`llm_assistant.py` sends only the slice relevant to the question.

## What is AI, analytics, or rules? (be precise in your presentation)
| Component | Technique |
|---|---|
| Chatbot answers | **LLM** (when configured), grounded on computed figures |
| Chatbot fallback | Rule-based keyword routing over computed figures |
| KPIs, savings rate, goal maths, budget limits, projections | Formulas (rule-based) |
| Charts, trends, month-over-month | Pandas aggregation (data analytics) |
| "Unusually high" detection | Simple statistics (mean, % change, z-score), **not** machine learning |
| Category guess for CSV rows with no category | Keyword rules, **not** machine learning |

There is no trained machine-learning model in this project. A natural future step is a scikit-learn text
classifier for categories.

## Security and privacy
- API key only from environment variables; `.env` and `*.db` are git-ignored; `.env.example` has no secrets.
- All SQL is parameterised; inputs and CSV uploads are validated (size, rows, columns, amounts, dates, categories).
- CSV export neutralises spreadsheet formula injection.
- Error messages from the LLM path show only the exception class name.
- Only synthetic demo data is bundled; do not enter bank logins or card details.

## Tested vs not yet tested
**Covered by automated tests** (`tests/`, 89 test cases): formatting, validation (transactions, profile, goals, CSV),
database CRUD and injection safety, analytics, savings rate (incl. zero income), budget engine, recommendations,
goal maths (zero contribution, past deadline, completed, no deadline), investment maths, LLM fallback / error /
missing-key / usage-limit behaviour (with a fake client), CSV export.

**Not covered by automated tests:** the Streamlit pages and widgets, Plotly chart rendering, a real LLM API call,
and PDF generation (one test exists but is skipped unless `fpdf2` is installed). Check these by hand:
1. Load demo data, open every page, confirm no error banners.
2. Add, edit and delete a transaction; import `data/sample_transactions.csv`.
3. Ask the six example questions in fallback mode, then with a real key.
4. Download the CSV and PDF from Reports and Settings.

## Known limitations
- Goal maths ignores interest, tax and inflation.
- Spending analysis needs at least one earlier month; with none it uses clearly labelled rule-of-thumb shares of income.
- Single user, local SQLite. On Streamlit Community Cloud the file system is not permanent, so data can reset.
- Investment content is static and general; rates are intentionally not quoted.

## Deploy (Streamlit Community Cloud)
1. Push the project to a public GitHub repository (confirm `.env` is not committed).
2. On share.streamlit.io choose the repo and `app.py` as the main file.
3. Add `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL` under **Secrets / environment** (optional).
4. Deploy. Expect demo data to reload after restarts.

## Screenshots
Run the app, then capture: Home dashboard, Transactions table, Budget Planner (recommendation reasoning),
Analytics, AI Assistant (one answer in fallback mode), Savings Goals, Investment Education.
Use your OS screenshot tool, save as `docs/screenshots/<page>.png`, and reference them here.

## Project layout
`app.py`, `pages/`, `src/` (modules above plus `config.py`, `validation.py`, `formatting.py`, `demo_data.py`),
`data/sample_transactions.csv`, `scripts/generate_sample_csv.py`, `tests/`, `docs/PROJECT_REPORT.md`.
