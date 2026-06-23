def analyze_user_data(info, history, submissions):
    """
    Analyzes raw Codeforces data to generate a structured summary of the user's performance.
    """
    if not submissions:
        return {"error": "No submissions found."}

    total_submissions = len(submissions)
    solved_problems = set()
    attempted_problems = set()
    tag_stats = {} # Format: { 'tag_name': {'ok': 0, 'failed': 0} }

    for sub in submissions:
        prob = sub.get("problem", {})
        prob_id = f"{prob.get('contestId')}{prob.get('index')}"
        verdict = sub.get("verdict")
        tags = prob.get("tags", [])
        
        attempted_problems.add(prob_id)
        
        for tag in tags:
            if tag not in tag_stats:
                tag_stats[tag] = {'ok': 0, 'failed': 0}
                
            if verdict == "OK":
                tag_stats[tag]['ok'] += 1
            else:
                tag_stats[tag]['failed'] += 1
                
        if verdict == "OK":
            solved_problems.add(prob_id)

    # Calculate success rates and filter tags with meaningful attempts
    processed_tags = []
    for tag, stats in tag_stats.items():
        total = stats['ok'] + stats['failed']
        if total >= 5: # Minimum attempts to consider
            success_rate = stats['ok'] / total if total > 0 else 0
            processed_tags.append({
                "tag": tag,
                "total_attempts": total,
                "success_rate": success_rate,
                "solved": stats['ok']
            })
            
    # Sort by success rate
    processed_tags.sort(key=lambda x: x['success_rate'])
    
    weaknesses = processed_tags[:5] # Bottom 5
    strengths = sorted(processed_tags, key=lambda x: x['success_rate'], reverse=True)[:5]

    # Progression Analysis
    contests_participated = len(history) if history else 0
    rating = info.get("rating", "Unrated")
    max_rating = info.get("maxRating", "Unrated")
    
    summary = {
        "handle": info.get("handle"),
        "rating": rating,
        "max_rating": max_rating,
        "contests_participated": contests_participated,
        "total_submissions": total_submissions,
        "unique_problems_attempted": len(attempted_problems),
        "unique_problems_solved": len(solved_problems),
        "weaknesses": weaknesses,
        "strengths": strengths,
        "solved_problems_set": list(solved_problems) # To exclude from recommendations
    }
    
    return summary
