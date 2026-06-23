import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://codeforces.com/api"

def fetch_from_api(endpoint, params=None):
    """Generic function to fetch data from Codeforces API."""
    url = f"{BASE_URL}/{endpoint}"
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "OK":
            return data.get("result")
        else:
            logger.error(f"Codeforces API error: {data.get('comment')}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None

def get_user_info(handle):
    """Fetches user profile information."""
    result = fetch_from_api("user.info", {"handles": handle})
    if result and len(result) > 0:
        return result[0]
    return None

def get_user_rating_history(handle):
    """Fetches user's contest rating history."""
    return fetch_from_api("user.rating", {"handle": handle})

def get_user_submissions(handle):
    """Fetches all submissions for a user."""
    return fetch_from_api("user.status", {"handle": handle})

def get_problemset():
    """Fetches the global problemset."""
    return fetch_from_api("problemset.problems")
