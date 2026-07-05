import random

def get_recommendations(problemset, user_summary, count=10):
    """Selects `count` problems for the user based on their weaknesses and rating."""
    if not problemset or 'problems' not in problemset:
        return []

    problems = problemset['problems']
    solved = set(user_summary.get('solved_problems_set', []))
    
    # Determine target rating range
    user_rating = user_summary.get('rating', 800)
    if not isinstance(user_rating, int):
        # No contest rating available — fall back to average rating of solved problems
        rating_lookup = {
            f"{p.get('contestId')}{p.get('index')}": p.get('rating')
            for p in problems
        }
        solved_ratings = [rating_lookup.get(pid) for pid in solved]
        solved_ratings = [r for r in solved_ratings if r]  # drop None/0

        if solved_ratings:
            user_rating = round(sum(solved_ratings) / len(solved_ratings))
        else:
            user_rating = 800

    min_rating = user_rating
    max_rating = user_rating + 300

    weak_tags = [w['tag'] for w in user_summary.get('weaknesses', [])]
    if not weak_tags:
        # If no weaknesses identified (e.g. new user), just pick general problems
        weak_tags = ['implementation', 'math', 'greedy', 'brute force']

    recommended = []
    
    # Filter problems
    for p in problems:
        prob_id = f"{p.get('contestId')}{p.get('index')}"
        if prob_id in solved:
            continue
            
        rating = p.get('rating')
        if not rating or not (min_rating <= rating <= max_rating):
            continue
            
        tags = p.get('tags', [])
        # If problem has at least one tag from weak_tags
        if any(tag in weak_tags for tag in tags):
            recommended.append(p)
            
    # If we don't have enough problems, relax the rating constraint slightly
    if len(recommended) < count:
        for p in problems:
            prob_id = f"{p.get('contestId')}{p.get('index')}"
            if prob_id in solved or p in recommended:
                continue
            rating = p.get('rating')
            if not rating or not (min_rating - 200 <= rating <= max_rating + 200):
                continue
            tags = p.get('tags', [])
            if any(tag in weak_tags for tag in tags):
                recommended.append(p)

    # Randomly select `count` problems
    if len(recommended) > count:
        return random.sample(recommended, count)
    return recommended
