import tkinter as tk
from tkinter import ttk, messagebox
import requests
import datetime
import time
import json
import os
import sys

# ---- APPDATA CONFIG ----
APPDATA = os.getenv("APPDATA")
APP_DIR = os.path.join(APPDATA, "MovieAnnouncer")
os.makedirs(APP_DIR, exist_ok=True)

SETTINGS_PATH = os.path.join(APP_DIR, "settings.json")

# ---- LOAD OR CREATE SETTINGS ----
if not os.path.exists(SETTINGS_PATH):
    template = {
        "WEBHOOK_URL": "",
        "ROLE_ID": "",
        "TMDB_API_KEY": ""
    }
    with open(SETTINGS_PATH, "w") as f:
        json.dump(template, f, indent=4)
    messagebox.showinfo("Settings Created",
                        f"A template settings.json was created at:\n{SETTINGS_PATH}\n\nFill it and restart the app.")
    sys.exit()

with open(SETTINGS_PATH, "r") as f:
    settings = json.load(f)

WEBHOOK_URL = settings.get("WEBHOOK_URL", "")
ROLE_ID = settings.get("ROLE_ID", "")
TMDB_API_KEY = settings.get("TMDB_API_KEY", "")

if not WEBHOOK_URL or not ROLE_ID or not TMDB_API_KEY:
    messagebox.showerror("Error", f"settings.json is missing values.\nPlease edit {SETTINGS_PATH}")
    sys.exit()

# ---- CONSTANTS ----
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_ORIGINAL_IMAGE_URL = "https://image.tmdb.org/t/p/original"

# ---- GLOBAL ----
movie_data = {}
selected_tmdb_id = None

# ---- HELPER FUNCTIONS ----
def format_runtime(runtime, lang="en-US"):
    if runtime == "N/A" or not isinstance(runtime, int):
        return "N/A"
    hours = runtime // 60
    minutes = runtime % 60
    if lang.startswith("fr"):
        if hours > 0 and minutes > 0:
            return f"{hours}h {minutes}min"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{minutes}min"
    else:
        return f"{runtime} min"


def get_letterboxd_link(tmdb_id):
    try:
        resp = requests.get(f"https://letterboxd.com/tmdb/{tmdb_id}", allow_redirects=True)
        if resp.status_code == 200:
            slug = resp.url.rstrip("/").split("/")[-1]
            return f"https://letterboxd.com/film/{slug}/"
    except Exception as e:
        print("Error getting Letterboxd link:", e)
    return None


# ---- TMDB FUNCTIONS ----
def search_movie():
    query = search_entry.get().strip()
    if not query:
        messagebox.showerror("Error", "Please enter a search term")
        return

    params = {"api_key": TMDB_API_KEY, "query": query, "language": selected_language.get()}
    r = requests.get(TMDB_SEARCH_URL, params=params)
    if r.status_code != 200:
        messagebox.showerror("TMDB Error", f"Status: {r.status_code}\n{r.text}")
        return

    data = r.json()
    results = data.get("results", [])

    movie_list.delete(0, tk.END)
    for movie in results[:10]:
        title = movie['title']
        release = movie.get('release_date', 'N/A')
        if release != "N/A":
            try:
                release = datetime.datetime.strptime(release, "%Y-%m-%d").strftime("%d/%m/%Y")
            except Exception:
                pass
        movie_list.insert(tk.END, f"{title} ({release}) - {movie['id']}")

    if not results:
        messagebox.showinfo("No results", "No movies found. Check console for debug.")


def select_movie(event):
    global movie_data, selected_tmdb_id
    if not movie_list.curselection():
        return

    selection = movie_list.get(movie_list.curselection())
    selected_tmdb_id = selection.split("-")[-1].strip()

    details_url = f"https://api.themoviedb.org/3/movie/{selected_tmdb_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "append_to_response": "credits",
        "language": selected_language.get()
    }
    r = requests.get(details_url, params=params)
    if r.status_code != 200:
        messagebox.showerror("TMDB Error", f"Failed to fetch movie details.\n{r.text}")
        return

    movie = r.json()

    # Autofill GUI
    title_var.set(movie.get("title", ""))
    overview_text.delete("1.0", tk.END)
    overview_text.insert(tk.END, movie.get("overview", ""))

    release_date = movie.get("release_date", "N/A")
    if release_date != "N/A":
        try:
            release_date = datetime.datetime.strptime(release_date, "%Y-%m-%d").strftime("%d/%m/%Y")
        except Exception:
            pass
    release_var.set(release_date)

    # Save movie data
    directors = [c["name"] for c in movie.get("credits", {}).get("crew", []) if c["job"] == "Director"]
    cast = [c["name"] for c in movie.get("credits", {}).get("cast", [])[:5]]

    movie_data = {
        "title": movie.get("title", ""),
        "overview": movie.get("overview", ""),
        "release_date": release_date,
        "runtime": movie.get("runtime", "N/A"),
        "rating": movie.get("vote_average", "N/A"),
        "genres": [g["name"] for g in movie.get("genres", [])],
        "poster_url": TMDB_IMAGE_URL + movie["poster_path"] if movie.get("poster_path") else "",
        "backdrop_url": TMDB_ORIGINAL_IMAGE_URL + movie["backdrop_path"] if movie.get("backdrop_path") else "",
        "director": directors[0] if directors else "Unknown",
        "cast": cast,
        "tmdb_id": selected_tmdb_id
    }


# ---- WEBHOOK FUNCTION ----
def send_announcement():
    if not movie_data or not selected_tmdb_id:
        messagebox.showerror("Error", "Please select a movie first")
        return

    # Parse event date
    try:
        picked_date = datetime.datetime.strptime(date_entry.get(), "%d/%m/%Y %H:%M")
        unix_ts = int(time.mktime(picked_date.timetuple()))
        discord_time = f"<t:{unix_ts}:F> • <t:{unix_ts}:R>"
    except Exception:
        messagebox.showerror("Error", "Invalid date format (DD/MM/YYYY HH:MM)")
        return

    # Letterboxd link
    letterboxd_link = get_letterboxd_link(selected_tmdb_id)
    letterboxd_preview_link = letterboxd_link.rstrip("/") + "/review/" if letterboxd_link else None

    # Build embed
    embed = {
        "title": movie_data["title"],
        "url": f"https://www.themoviedb.org/movie/{selected_tmdb_id}?language={selected_language.get()}",
        "description": f"_{movie_data['overview']}_",
        "color": 0xCA0000,
        "thumbnail": {"url": movie_data["poster_url"]},
        "image": {"url": movie_data["backdrop_url"]},
        "fields": [
            {"name": "📅 Date de sortie", "value": movie_data["release_date"], "inline": True},
            {"name": "⏱ Durée", "value": f"{movie_data['runtime']} min", "inline": True},
            {"name": "⭐ Note", "value": f"{movie_data['rating']}/10", "inline": True},
            {"name": "🎭 Genres", "value": ", ".join(movie_data["genres"]), "inline": False},
            {"name": "🎬 Réalisateur", "value": movie_data["director"], "inline": True},
            {"name": "👥 Acteurs Principaux", "value": ", ".join(movie_data["cast"]), "inline": True},
            {"name": "🕒 Event", "value": discord_time, "inline": False},
        ],
        "footer": {
            "text": "meewey's movie embed • TMDB",
        },
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

    # Add Letterboxd field under Event with emoji ID and preview link
    if letterboxd_preview_link:
        embed["fields"].append({
            "name": "<:letterboxd:1418339144660156567> Letterboxd",
            "value": f"[Log sur Letterboxd]({letterboxd_preview_link})",
            "inline": False
        })

    data = {
        "content": f"<@&{ROLE_ID}> 🎬 **Annonce Film!**",
        "embeds": [embed]
    }

    r = requests.post(WEBHOOK_URL, json=data)
    if r.status_code == 204:
        messagebox.showinfo("Success", "Announcement sent!")
    else:
        messagebox.showerror("Error", f"Failed: {r.status_code}\n{r.text}")


# ---- GUI ----
root = tk.Tk()
root.title("Movie Announcer")

# Language selector
selected_language = tk.StringVar(root, value="en-US")
tk.Label(root, text="Language:").pack()
lang_box = ttk.Combobox(root, textvariable=selected_language, values=[
    "en-US", "fr-FR", "de-DE", "es-ES", "it-IT", "ja-JP"
], width=10)
lang_box.pack()
lang_box.current(0)

# Search
tk.Label(root, text="Search Movie:").pack()
search_entry = tk.Entry(root, width=40)
search_entry.pack()
tk.Button(root, text="Search", command=search_movie).pack()

# Results
movie_list = tk.Listbox(root, width=60, height=10)
movie_list.pack()
movie_list.bind("<<ListboxSelect>>", select_movie)

# Movie info preview
title_var = tk.StringVar(root)
release_var = tk.StringVar(root)

tk.Label(root, text="Title:").pack()
tk.Entry(root, textvariable=title_var, width=50).pack()

tk.Label(root, text="Overview:").pack()
overview_text = tk.Text(root, width=60, height=5)
overview_text.pack()

tk.Label(root, text="Release Date:").pack()
tk.Entry(root, textvariable=release_var, width=50).pack()

# Date Picker
tk.Label(root, text="Event Date (DD/MM/YYYY HH:MM):").pack()
date_entry = tk.Entry(root, width=50)
date_entry.insert(0, "31/12/2025 20:00")
date_entry.pack()

# Send button
tk.Button(root, text="Send Announcement", command=send_announcement, bg="green", fg="white").pack(pady=10)

root.mainloop()
