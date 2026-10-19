# Poll Results Visualizer - Project Guide

## 1. What is it?
**Simple:** a tool that turns raw poll answers into charts and a short written summary so anyone can see "who voted for what, and why it matters".
**Technical:** an ETL + analytics + visualisation pipeline over survey data: ingest CSV -> clean/standardise -> aggregate (counts, shares, cross-tabs, rating stats) -> visualise -> auto-generate insights -> serve via Streamlit.

**Why it matters:** raw responses are unreadable and error-prone. Decision-makers need shares, comparisons and trends. Survey tools (Qualtrics, SurveyMonkey, YouGov) all run this same pipeline.

**Use cases:** election/opinion polls · customer feedback · employee satisfaction · product preference · classroom/event feedback.

**Workflow:** poll data input → preprocessing → analysis → visualization → insights → decision-making

## 2. Tech stack options
| | Stack | Dashboard | Difficulty |
|---|---|---|---|
| A (Easy) | Pandas + Matplotlib in Jupyter/Colab | No (static charts) | ⭐ |
| **B (Intermediate) ✅ chosen** | Pandas, NumPy, Seaborn, Plotly, WordCloud, **Streamlit** | Yes | ⭐⭐ |
| C (Advanced) | B + FastAPI + PostgreSQL + live Google Forms API + Docker + NLP models | Yes, live | ⭐⭐⭐⭐ |

**Why B:** employers see cleaning + analysis + a deployable dashboard, with no infrastructure to manage.

## 3. Architecture
```
 Google Forms CSV / Excel / Synthetic generator
                    │
                    ▼
        ┌──────────────────────┐
        │  src/generate_data   │  (or --input your.csv)
        └──────────┬───────────┘
                   ▼
        ┌──────────────────────┐
        │  src/cleaning        │  dedupe · standardise · validate 1-5 · missing · features
        └──────────┬───────────┘
                   ▼  data/poll_data_cleaned.csv
        ┌──────────────────────┐
        │  src/analysis        │  vote share · MoE · rating stats · cross-tabs · trend · sentiment
        └───────┬──────┬───────┘
                ▼      ▼
   src/visualize   src/insights
   (images/*.png)  (outputs/insights_report.md)
                └──────┬───────┘
                       ▼
            app.py  (Streamlit dashboard)
```

## 4. Phase-wise plan
| Phase | Do | Why | Output | Avoid |
|---|---|---|---|---|
| 1 Setup | venv, install, folders, `git init` | reproducible env | working `python -c "import pandas"` | installing globally |
| 2 Data | `python -m src.generate_data` or export a Google Form | need realistic input | `data/poll_data_raw.csv` | perfectly clean fake data |
| 3 Cleaning | `clean_poll_data()` | bad data = misleading charts | cleaning log + cleaned CSV | silently dropping rows (always log counts) |
| 4 EDA | `df.info()`, `value_counts()`, missing counts | understand before charting | notes/notebook | skipping this |
| 5 Analysis | vote share, MoE, cross-tabs | answer the business questions | `outputs/*.csv` | reporting counts without % or sample size |
| 6 Visualization | `save_all(df)` | communicate | `images/*.png` | 3D charts, unlabeled axes, pies with 10+ slices |
| 7 Insights | `generate_insights()` | decisions need words | `insights_report.md` | claiming causes from a poll |
| 8 GitHub | commit + push + README | proof of work | public repo | committing `venv/` |

## 5. Folder structure explained
- `data/` raw + cleaned CSVs · `notebooks/` exploration · `src/` reusable modules · `outputs/` result tables/report · `images/` charts for README · `docs/` guides · `tests/` pytest · `app.py` dashboard · `main.py` runs everything · `requirements.txt` dependencies · `.gitignore` keeps junk out of Git.

## 6. Installation
**Ubuntu/Mac**
```bash
python3 --version                 # 3.10+
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
**Windows (PowerShell)**
```powershell
python --version
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
If activation is blocked: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
**Colab:** `!pip install wordcloud streamlit plotly` (the rest is pre-installed).

## 7. Simulation - how the poll data is generated (`src/generate_data.py`)
1. **Respondents:** 600 rows; region, age group, gender drawn with fixed probabilities (seeded RNG → reproducible).
2. **Questions:** Preferred Tool (multiple choice, 6 options), Would Recommend (Yes/No), Satisfaction (Likert 1-5), Feedback (open text).
3. **Option probabilities:** a base share per tool, then *adjusted* per respondent: South/18-24 boost Python, West boosts Power BI/Tableau, North/45+ boosts Excel. → regional + demographic patterns.
4. **Ratings:** normal distribution around a per-tool mean (Python 4.1 … R 3.2), clipped to 1-5.
5. **Yes/No:** probability rises with rating (`0.15 + 0.16 × rating`).
6. **Feedback:** positive/neutral/negative sentence pools chosen by rating.
7. **Dates:** 30 days, with a ramp-up so the trend chart shows growth.
8. **Mess injected:** typos/casing, blanks, invalid ratings (`7`, `four`), variant yes/no, ~4% duplicate submissions.
9. **Leader detection:** `vote_share()` sorts options; `margin_of_error()` tells if the lead is real; `leader_by_group()` finds regional leaders.
10. **Insights:** `generate_insights()` fills sentence templates from those tables.

**Proof to save:** raw preview, cleaning log, vote table, all PNGs, `insights_report.md`, Streamlit screenshots, GitHub repo page.

## 8. How to run
```bash
python main.py             # prints cleaning log, tables, insights; saves 11 charts + CSVs + report
streamlit run app.py       # opens http://localhost:8501
```
Expected: `images/` has 00_dashboard.png + 10 charts; `outputs/` has 4 CSVs + `insights_report.md`.

## 9. GitHub upload
```bash
git init
git add .
git commit -m "feat: initial project structure and synthetic poll generator"
git branch -M main
git remote add origin https://github.com/arppitha-ai/Poll-Results-Visualizer.git
git push -u origin main
```
Create the empty repo first on github.com (no README/gitignore, since we already have them). If asked for a password use a **Personal Access Token** or SSH key.
- **Repo name:** `Poll-Results-Visualizer`
- **Description:** Survey/poll analytics pipeline in Python - cleaning, vote-share analysis, demographic comparisons, sentiment, charts and a Streamlit dashboard.
- **Topics:** `python` `data-analysis` `data-visualization` `streamlit` `pandas` `survey-analysis` `polls` `seaborn` `plotly` `portfolio-project`

**Commit message ideas:** `feat: add data cleaning pipeline` · `feat: add vote share and cross-tab analysis` · `feat: add charts` · `feat: add Streamlit dashboard` · `docs: add README and screenshots` · `test: add pytest tests`

## 10. 5-day proof plan
| Day | Work | Commits | Screenshots |
|---|---|---|---|
| 1 | venv, folders, config, generator | `chore: setup`, `feat: data generator` | raw dataset preview |
| 2 | dataset + EDA notebook | `feat: add raw dataset`, `docs: eda notebook` | `df.info()`, missing values |
| 3 | cleaning + analysis | `feat: cleaning`, `feat: analysis`, `test: add tests` | cleaning log, cleaned preview, vote table |
| 4 | charts + insights + Streamlit | `feat: visualizations`, `feat: dashboard` | bar, pie, region, age, dashboard |
| 5 | README, polish, push | `docs: README`, `chore: final cleanup` | GitHub repo page |

## 11. Screenshot checklist
1. Raw dataset preview (messy rows visible) 2. Cleaned dataset preview 3. Vote/share table 4. `01_vote_bar.png` 5. `02_vote_pie.png` 6. `06_region_stacked.png` 7. `07_age_heatmap.png` 8. Streamlit dashboard (full page, with a filter applied) 9. GitHub repo page 10. Terminal showing `pytest` passing. Save to `images/` with clear names.

## 12. Future improvements
Live Google Forms/Sheets API · VADER/transformer sentiment · Power BI/Looker Studio version · auto-refresh dashboard · chi-square significance tests · weighting by demographics · PDF export · Docker + Streamlit Cloud deployment.

## 13. Troubleshooting
| Error | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'wordcloud'` | `pip install wordcloud` (project falls back to a top-words chart) |
| `ModuleNotFoundError: No module named 'src'` | run from the project root folder |
| `externally-managed-environment` (Ubuntu) | use a venv: `python3 -m venv venv && source venv/bin/activate` |
| `KeyError: 'Preferred Tool'` | CSV headers differ; add them to `COLUMN_ALIASES` in `src/config.py` |
| `ValueError: time data ... doesn't match format` | check Timestamp format; cleaning uses `errors="coerce"` and drops bad rows |
| Charts don't pop up | by design, they are saved to `images/` |
| `streamlit: command not found` | activate venv, or `python -m streamlit run app.py` |
| wordcloud build fails | `sudo apt install build-essential python3-dev` then reinstall |
| Port 8501 busy | `streamlit run app.py --server.port 8502` |
| Git `Permission denied` / auth failed | use a Personal Access Token or SSH key |
| Git rejects push (non-empty remote) | `git pull origin main --rebase` then push |
| Empty charts after filtering | widen sidebar filters |
