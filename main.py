from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from cf_api import get_user_info, get_user_rating_history, get_user_submissions, get_problemset
from analyzer import analyze_user_data
from recommender import get_recommendations
from ai_coach import get_coach_insights
from db import create_checkpoints_table, save_checkpoint, get_last_two_checkpoints

load_dotenv()

app = FastAPI(title="AI Codeforces Coach API")

try:
    create_checkpoints_table()
except Exception as e:
    print(f"Warning: could not initialize checkpoints table: {e}")

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

    # Save a progress checkpoint — rating can be "Unrated" (str) or an int
    rating_value = user_summary.get("rating")
    rating_to_store = rating_value if isinstance(rating_value, int) else None

    save_checkpoint(
        handle,
        rating_to_store,
        user_summary.get("unique_problems_solved", 0),
        user_summary.get("weaknesses", []),
        user_summary.get("strengths", []),
    )

    recommended_problems = get_recommendations(problemset, user_summary, count=10)
    ai_report = get_coach_insights(user_summary, recommended_problems)

    return {
        "info": info,
        "user_summary": user_summary,
        "recommended_problems": recommended_problems,
        "ai_report": ai_report,
    }

@app.get("/progress/{handle}")
def progress(handle: str):
    checkpoints = get_last_two_checkpoints(handle)

    if len(checkpoints) < 2:
        return {"handle": handle, "has_previous": False, "message": "Not enough history yet."}

    latest, previous = checkpoints[0], checkpoints[1]

    rating_delta = None
    if latest["rating"] is not None and previous["rating"] is not None:
        rating_delta = latest["rating"] - previous["rating"]

    solved_delta = latest["unique_problems_solved"] - previous["unique_problems_solved"]

    return {
        "handle": handle,
        "has_previous": True,
        "latest_checkpoint": latest["created_at"].isoformat(),
        "previous_checkpoint": previous["created_at"].isoformat(),
        "rating_delta": rating_delta,
        "solved_delta": solved_delta,
        "latest_weaknesses": latest["weaknesses"],
        "previous_weaknesses": previous["weaknesses"],
    }