import streamlit as st
from dotenv import load_dotenv
import os

from cf_api import get_user_info, get_user_rating_history, get_user_submissions, get_problemset
from analyzer import analyze_user_data
from recommender import get_recommendations
from ai_coach import get_coach_insights

# Load environment variables
load_dotenv()

st.set_page_config(page_title="AI Codeforces Coach", page_icon="🤖", layout="wide")

st.title("🤖 AI-Powered Codeforces Coach")
st.markdown("Your personal competitive programming mentor. Enter your handle to get deep insights and a personalized practice roadmap.")

# Sidebar for configuration
with st.sidebar:
    st.header("Settings")
    handle = st.text_input("Codeforces Handle", placeholder="e.g. tourist")
    analyze_btn = st.button("Analyze Profile")
    
    st.markdown("---")
    st.markdown("**Note:** This app uses LangChain and Groq. Make sure your `.env` file has a valid `GROQ_API_KEY`.")

if analyze_btn and handle:
    if not os.environ.get("GROQ_API_KEY"):
        st.error("GROQ_API_KEY is missing. Please add it to your .env file.")
        st.stop()

    with st.spinner(f"Fetching data from Codeforces for {handle}..."):
        info = get_user_info(handle)
        if not info:
            st.error(f"Could not fetch profile for user: {handle}. Please check the handle.")
            st.stop()
            
        history = get_user_rating_history(handle)
        submissions = get_user_submissions(handle)
        problemset = get_problemset()

    with st.spinner("Analyzing performance patterns..."):
        user_summary = analyze_user_data(info, history, submissions)
        if "error" in user_summary:
            st.error(user_summary["error"])
            st.stop()

    with st.spinner("Selecting optimal practice problems..."):
        recommended_problems = get_recommendations(problemset, user_summary, count=10)

    with st.spinner("Your AI Mentor is reviewing your profile and writing a report..."):
        ai_report = get_coach_insights(user_summary, recommended_problems)

    # --- Display Results ---
    st.success("Analysis Complete!")
    
    # 1. Profile Overview
    st.subheader(f"Profile: {info.get('handle')}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Rating", info.get("rating", "Unrated"))
    col2.metric("Max Rating", info.get("maxRating", "Unrated"))
    col3.metric("Problems Solved", user_summary.get("unique_problems_solved", 0))
    col4.metric("Total Submissions", user_summary.get("total_submissions", 0))

    st.markdown("---")
    
    # 2. AI Coach Report
    st.subheader("🎓 Mentor's Analysis & Roadmap")
    st.markdown(ai_report)
    
    st.markdown("---")

    # 3. Recommended Problems
    st.subheader("🎯 Recommended Practice Problems")
    st.markdown("Based on your weaknesses, here are 10 specific problems slightly above your current level:")
    
    if not recommended_problems:
        st.info("No recommendations found. Try solving more problems first!")
    else:
        for idx, prob in enumerate(recommended_problems):
            prob_id = f"{prob.get('contestId')}{prob.get('index')}"
            url = f"https://codeforces.com/problemset/problem/{prob.get('contestId')}/{prob.get('index')}"
            rating = prob.get("rating", "Unrated")
            tags = ", ".join(prob.get("tags", []))
            
            with st.expander(f"{idx+1}. {prob.get('name')} (Rating: {rating})"):
                st.markdown(f"**Tags:** {tags}")
                st.markdown(f"[Solve on Codeforces ↗]({url})")
