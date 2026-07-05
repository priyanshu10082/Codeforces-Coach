import streamlit as st
from dotenv import load_dotenv
import requests
import os

# Load environment variables
load_dotenv()

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Codeforces Coach", page_icon="🤖", layout="wide")

st.title("🤖 AI-Powered Codeforces Coach")
st.markdown("Your personal competitive programming mentor. Enter your handle to get deep insights and a personalized practice roadmap.")

# Sidebar for configuration
with st.sidebar:
    st.header("Settings")
    handle = st.text_input("Codeforces Handle", placeholder="e.g. tourist")
    analyze_btn = st.button("Analyze Profile")
    
    st.markdown("---")
    
if analyze_btn and handle:
    with st.spinner(f"Analyzing profile for {handle}..."):
        try:
            response = requests.get(f"{API_URL}/analyze/{handle}", timeout=60)
            # return {
            #     "info": info,
            #     "user_summary": user_summary,
            #     "recommended_problems": recommended_problems,
            #     "ai_report": ai_report,
            # }
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach the API. Is it running? ({e})")
            st.stop()

        if response.status_code != 200:
            detail = response.json().get("detail", "Something went wrong.")
            st.error(detail)
            st.stop()

        data = response.json()

    info = data["info"]
    user_summary = data["user_summary"]
    recommended_problems = data["recommended_problems"]
    ai_report = data["ai_report"]

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