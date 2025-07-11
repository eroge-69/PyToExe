import requests
from win10toast import ToastNotifier

#       API key
RAWG_API_KEY = "18ac49cd174d492bb1e387fc6301562a"

def get_free_games():
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    params = {"locale": "en-US", "country": "US", "allowCountries": "US"}
    response = requests.get(url, params=params)
    elements = response.json()['data']['Catalog']['searchStore']['elements']
    
    free_games = []
    for game in elements:
        price_info = game.get('price', {}).get('totalPrice', {})
        if price_info.get('discountPrice', 1) == 0:
            title = game['title']
            free_games.append(title)
    return free_games

def get_game_score(title):
    try:
        query_url = f"https://api.rawg.io/api/games"
        params = {"search": title, "key": RAWG_API_KEY}
        response = requests.get(query_url, params=params)
        results = response.json().get("results", [])
        if results:
            score = results[0].get("rating", 0)
            if score == 0:
                return None  # Treat 0 as no rating
            return score
    except Exception as e:
        print(f"Error fetching score for {title}: {e}")
    return None  # No rating found or error

def score_to_stars(score):
    if score is None:
        return "Unrated"
    rounded = round(score)
    return "★" * rounded + "☆" * (5 - rounded)

def notify_user():
    toaster = ToastNotifier()
    free_games = get_free_games()

    if not free_games:
        toaster.show_toast("Epic Games", "No free games found this week.", duration=10)
        return

    message_lines = []
    for title in free_games:
        score = get_game_score(title)
        stars = score_to_stars(score)
        if stars == "Unrated":
            message_lines.append(f"{title} — Unrated")
        else:
            message_lines.append(f"{title} — {stars} ({score:.1f}/5)")

    full_message = "\n".join(message_lines)
    toaster.show_toast("Epic Games Free Games 🎮", full_message, duration=15)

if __name__ == "__main__":
    notify_user()
