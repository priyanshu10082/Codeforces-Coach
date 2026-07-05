from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from cf_api import get_user_info, get_user_rating_history, get_user_submissions, get_problemset
from analyzer import analyze_user_data
from recommender import get_recommendations
from ai_coach import get_coach_insights

load_dotenv()

app = FastAPI(title="AI Codeforces Coach API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/analyze/{handle}")
def analyze(handle: str):
    info = get_user_info(handle)
    if not info:
        raise HTTPException(status_code=404, detail=f"Could not fetch profile for handle: {handle}")

    history = get_user_rating_history(handle)
    submissions = get_user_submissions(handle)
    problemset = get_problemset()

    user_summary = analyze_user_data(info, history, submissions)
    if "error" in user_summary:
        raise HTTPException(status_code=400, detail=user_summary["error"])

    recommended_problems = get_recommendations(problemset, user_summary, count=10)
    ai_report = get_coach_insights(user_summary, recommended_problems)

    return {
        "info": info,
        "user_summary": user_summary,
        "recommended_problems": recommended_problems,
        "ai_report": ai_report,
    }