"""
Trouve jusqu'à 100 comptes Roblox dont le pseudo contient "123"
et dont la date de création est entre 2019 et 2025 inclus.

Prérequis:
    pip install requests beautifulsoup4 python-dateutil

Usage:
    python find_roblox_123.py
"""

import requests
from bs4 import BeautifulSoup
from dateutil import parser
from datetime import datetime
import time
import csv

SEARCH_KEYWORD = "123"
MAX_RESULTS = 100
USER_AGENT = "Mozilla/5.0 (compatible; script/1.0)"
HEADERS = {"User-Agent": USER_AGENT}
OUTPUT_CSV = "roblox_123_2019_2025.csv"

# Plages de dates (incluses)
START = datetime(2019, 1, 1)
END = datetime(2025, 12, 31, 23, 59, 59)

def search_users_page(keyword, page=1):
    """
    Récupère la page de résultats de recherche d'utilisateurs Roblox.
    Note: Roblox peut changer son HTML. Le script essaie d'extraire les liens vers les profils.
    """
    url = f"https://www.roblox.com/search/users?keyword={keyword}&page={page}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.text

def parse_user_links(html):
    """
    Extrait tuples (username, profile_url) depuis la page HTML.
    """
    soup = BeautifulSoup(html, "html.parser")
    results = []
    # Les résultats utilisateurs sont souvent contenus dans des éléments <a> vers /users/<id>/profile
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/users/" in href and "/profile" in href:
            # exemple: /users/12345678/profile
            parts = href.split("/")
            try:
                idx = parts.index("users")
                user_id = parts[idx+1]
                username = a.get_text(strip=True)
                if username:
                    results.append((username, user_id))
            except Exception:
                continue
    return results

def get_user_info(user_id):
    """
    Interroge l'API officielle pour obtenir la date de création.
    """
    api_url = f"https://users.roblox.com/v1/users/{user_id}"
    resp = requests.get(api_url, headers=HEADERS, timeout=10)
    if resp.status_code != 200:
        return None
    return resp.json()

def main():
    found = []
    page = 1
    seen_ids = set()
    print("Démarrage de la recherche. Cela peut prendre quelques minutes selon la vitesse et les limites.")
    while len(found) < MAX_RESULTS and page <= 50:  # limite prudente de pages
        try:
            html = search_users_page(SEARCH_KEYWORD, page=page)
        except Exception as e:
            print(f"Erreur en récupérant la page {page}: {e}")
            break
        entries = parse_user_links(html)
        if not entries:
            print("Plus aucun résultat sur les pages suivantes — arrêt.")
            break
        for username, user_id in entries:
            if user_id in seen_ids:
                continue
            seen_ids.add(user_id)
            # on vérifie que "123" est bien dans le pseudo (sens case-insensitive)
            if "123" not in username.lower():
                continue
            try:
                info = get_user_info(user_id)
            except Exception as e:
                print(f"Erreur API pour {user_id}: {e}")
                continue
            if not info or "created" not in info:
                # si l'API ne retourne pas created, on ignore
                continue
            try:
                created = parser.isoparse(info["created"])
            except Exception:
                continue
            if START <= created <= END:
                found.append({
                    "user_id": user_id,
                    "username": username,
                    "created": created.isoformat()
                })
                print(f"Ajouté: {username} (id={user_id}) créé le {created.date()}")
                if len(found) >= MAX_RESULTS:
                    break
            # petite pause pour respecter le site / éviter ban
            time.sleep(0.4)
        page += 1
        # pause entre pages
        time.sleep(0.8)

    # Sauvegarde CSV
    if found:
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["user_id", "username", "created"])
            writer.writeheader()
            for r in found:
                writer.writerow(r)
        print(f"\nTerminé — {len(found)} comptes trouvés. Résultats enregistrés dans: {OUTPUT_CSV}")
    else:
        print("Aucun compte trouvé correspondant aux critères.")

if _name_ == "_main_":
    main()