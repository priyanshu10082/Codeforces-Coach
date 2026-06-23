import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

def get_coach_insights(user_summary, recommended_problems):
    """
    Uses LangChain and Groq LLM to generate a personalized coaching report.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "Error: GROQ_API_KEY not found in environment variables."

    try:
        llm = ChatGroq(
            temperature=0.7,
            model_name="llama-3.3-70b-versatile", # Using the latest Llama 3.3 70B model supported by Groq
            groq_api_key=api_key
        )
    except Exception as e:
        return f"Error initializing LLM: {str(e)}"

    template = """
    You are an expert Competitive Programming (CP) Coach. You are mentoring a student on Codeforces.
    Your goal is to act as a personal mentor, providing encouraging, deep, and actionable insights.

    Here is the student's statistical profile:
    - Handle: {handle}
    - Current Rating: {rating} (Max: {max_rating})
    - Contests Participated: {contests_participated}
    - Total Submissions: {total_submissions}
    - Unique Problems Solved: {unique_problems_solved}

    Top Strengths (High success rate tags):
    {strengths}

    Top Weaknesses (Low success rate tags with many attempts):
    {weaknesses}

    I have also selected the following {num_problems} problems for them to practice based on their weaknesses and rating:
    {problems_list}

    Please write a personalized coaching report formatted in Markdown.
    Include:
    1. A warm, encouraging greeting and a brief analysis of their overall progression.
    2. High-level insights into their strengths and weaknesses (go beyond just listing the tags - explain what these tags mean in CP and why they might be struggling).
    3. A clear, actionable practice roadmap for the next few weeks.
    4. A brief note on why the selected problems are good for them right now.

    Keep it highly readable, structured, and genuinely helpful. Be direct but extremely encouraging.
    Do NOT output the actual list of recommended problems (the UI will display them separately), but do reference the *types* of problems you see in the list.
    """

    prompt = PromptTemplate(
        input_variables=["handle", "rating", "max_rating", "contests_participated", "total_submissions", 
                         "unique_problems_solved", "strengths", "weaknesses", "num_problems", "problems_list"],
        template=template
    )

    # Format data for prompt
    strengths_str = "\n".join([f"- {s['tag']}: {s['success_rate']:.1%} success ({s['solved']} solved)" for s in user_summary.get('strengths', [])])
    weaknesses_str = "\n".join([f"- {w['tag']}: {w['success_rate']:.1%} success ({w['total_attempts']} attempts)" for w in user_summary.get('weaknesses', [])])
    
    problems_str = "\n".join([f"- {p.get('name')} (Rating: {p.get('rating', 'N/A')}, Tags: {', '.join(p.get('tags', []))})" for p in recommended_problems])

    try:
        chain = prompt | llm
        response = chain.invoke({
            "handle": user_summary.get('handle'),
            "rating": user_summary.get('rating'),
            "max_rating": user_summary.get('max_rating'),
            "contests_participated": user_summary.get('contests_participated'),
            "total_submissions": user_summary.get('total_submissions'),
            "unique_problems_solved": user_summary.get('unique_problems_solved'),
            "strengths": strengths_str if strengths_str else "Not enough data",
            "weaknesses": weaknesses_str if weaknesses_str else "Not enough data",
            "num_problems": len(recommended_problems),
            "problems_list": problems_str if problems_str else "No specific problems found."
        })
        return response.content
    except Exception as e:
        return f"Error generating insights: {str(e)}"
