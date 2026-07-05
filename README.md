# 🤖 AI-Powered Codeforces Coach

A personal competitive programming mentor. Enter a Codeforces handle and get a data-driven breakdown of strengths and weaknesses, a personalized AI-generated coaching report, and a curated list of practice problems targeted at your current level.

**Live demo:** _coming soon_

---

## Features

- **Performance analysis** — pulls a user's full submission history from the Codeforces API and computes per-tag success rates to surface genuine strengths and weaknesses.
- **Smart problem recommendations** — selects practice problems slightly above the user's current rating, prioritized by their weak tags, while excluding problems already solved.
- **AI coaching report** — an LLM (via Groq + LangChain) turns the raw statistics into a readable, encouraging, and actionable report explaining *why* certain tags are difficult and what to focus on next.
- **Decoupled architecture** — a FastAPI backend handles all data fetching, analysis, and LLM calls; a Streamlit frontend handles the UI, talking to the backend over HTTP.

---

## Architecture

```
┌─────────────────┐        HTTP         ┌──────────────────┐
│  Streamlit UI    │  ───────────────►  │  FastAPI backend  │
│  (app.py)        │  ◄───────────────  │  (main.py)         │
└─────────────────┘                     └──────────┬────────┘
                                                     │
                       ┌─────────────────────────────┼───────────────────────┐
                       │                             │                       │
                ┌──────▼──────┐            ┌─────────▼────────┐    ┌─────────▼────────┐
                │ Codeforces   │            │  Analysis /       │    │  Groq LLM         │
                │ API          │            │  Recommendation    │    │  (via LangChain)   │
                │ (cf_api.py)  │            │  (analyzer.py,      │    │  (ai_coach.py)     │
                └──────────────┘            │   recommender.py)   │    └────────────────────┘
                                             └─────────────────────┘
```

The frontend has no direct knowledge of Codeforces, the analysis logic, or the LLM — it only knows the backend's URL and the shape of the JSON it returns. This means the backend could serve any other frontend (a future React app, a CLI, etc.) without modification.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI + Uvicorn |
| LLM orchestration | LangChain |
| LLM provider | Groq |
| External data | Codeforces public API |

---

## Project Structure

```
.
├── app.py            # Streamlit frontend
├── main.py           # FastAPI backend — exposes /analyze/{handle}
├── cf_api.py         # Codeforces API client
├── analyzer.py       # Tag-based strength/weakness analysis
├── recommender.py    # Problem recommendation logic
├── ai_coach.py       # LLM prompt construction + Groq call
├── requirements.txt
└── .gitignore
```

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/Codeforces-Coach.git
cd Codeforces-Coach
```

### 2. Create a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set environment variables
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Run the backend
```bash
uvicorn main:app --reload
```

### 6. Run the frontend (in a separate terminal)
```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`, talking to the backend at `http://127.0.0.1:8000`.

---

## How It Works

1. The user enters a Codeforces handle in the Streamlit UI.
2. The frontend sends a request to the backend's `/analyze/{handle}` endpoint.
3. The backend fetches the user's profile, rating history, and full submission history from the Codeforces API.
4. `analyzer.py` computes per-tag success rates across all submissions, filtering out tags with too few attempts to be statistically meaningful, and ranks the top and bottom performing tags.
5. `recommender.py` filters the global problem set to unsolved problems within a target rating window, prioritizing the user's weak tags.
6. `ai_coach.py` builds a structured prompt from the statistics and sends it to Groq via LangChain, generating a Markdown-formatted coaching report.
7. The backend returns everything as one JSON response; the frontend renders the profile metrics, the AI report, and the recommended problems.

---

## Known Limitations / Future Work

- Tag success rates are computed per **submission**, not per **problem** — a problem solved after several failed attempts currently drags down that tag's success rate more than it should.
- No caching yet — the global problem set (`problemset.problems`) is re-fetched on every analysis.
- No persistence — nothing is saved between sessions; re-analyzing a handle re-runs the full pipeline from scratch.
- Planned: a RAG-based concept explainer, using local sentence-transformer embeddings and a ChromaDB vector store, to ground topic explanations in a curated knowledge base rather than relying purely on the LLM's parametric memory.

---

## License

MIT
