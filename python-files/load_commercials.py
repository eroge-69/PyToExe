import datetime
import mysql.connector
import requests

# === Konfiguration ===
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "12345678",
    "database": "oe3",
    "charset": "utf8mb4",
    "collation": "utf8mb4_general_ci"
}

RADIO_DJ_URL = "http://127.0.0.1:3300/opt"
RADIO_DJ_AUTH = "12345678"
CATEGORY_NAME = "Werbung"
BLIP_TRACK_ID = 207  # Blip-Sound vor Werbung

# === Spaltenindizes aus Tabelle 'songs' ===
IDX_ID = 0
IDX_ARTIST = 35
IDX_TITLE = 38
IDX_DURATION = 20

# === Berechne Sekunden bis zur nächsten vollen Stunde ===
def get_remaining_time():
    now = datetime.datetime.now()
    next_hour = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
    #next_hour = now .replace(minute=18, second=0, microsecond=0)	
    return int((next_hour - now).total_seconds())

# === Hole passende Songs anhand der Kategorie ===
def get_tracks_from_category(category_name):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT songs.*
        FROM songs
        JOIN subcategory ON songs.id_subcat = subcategory.ID
        JOIN category ON subcategory.parentid = category.ID
        WHERE category.name = %s;
    """, (category_name,))
    results = cursor.fetchall()
    conn.close()
    return results

# === Wähle so viele Tracks wie in die verbleibende Zeit passen ===
def select_tracks_to_fill(tracks, total_seconds):
    tracks_sorted = sorted(tracks, key=lambda x: x[IDX_DURATION], reverse=True)
    selected = []
    total = 0

    for track in tracks_sorted:
        duration = track[IDX_DURATION]
        if isinstance(duration, datetime.datetime):
            duration = duration.second + duration.minute * 60 + duration.hour * 3600
        if total + duration <= total_seconds:
            selected.append(track)
            total += duration
        if total >= total_seconds:
            break

    return selected

# === Universelle HTTP-Befehl-Funktion an RadioDJ ===
def send_radiodj_command(command, arg=None):
    params = {
        "auth": RADIO_DJ_AUTH,
        "command": command
    }
    if arg is not None:
        params["arg"] = str(arg)

    try:
        response = requests.get(RADIO_DJ_URL, params=params)
        if response.status_code == 200:
            print(f"✅ Befehl '{command}' erfolgreich ausgeführt.")
        else:
            print(f"❌ Fehler bei Befehl '{command}': {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Verbindungsfehler bei Befehl '{command}': {e}")

# === Hauptfunktion ===
def main():
    remaining = get_remaining_time()
    print(f"🕒 Verbleibende Zeit bis zur vollen Stunde: {remaining} Sekunden(~ {remaining/60} Minuten)")

    all_tracks = get_tracks_from_category(CATEGORY_NAME)
    selected = select_tracks_to_fill(all_tracks, remaining)

    if not selected:
        print("⚠️ Keine passenden Tracks gefunden.")
        return

    print("🎵 Ausgewählte Tracks:")
    for track in selected:
        artist = track[IDX_ARTIST]
        title = track[IDX_TITLE]
        duration = track[IDX_DURATION]
        if isinstance(duration, datetime.datetime):
            duration = duration.second + duration.minute * 60 + duration.hour * 3600
        print(f" - {title} – {artist} ({duration:.1f} Sek)")

    # === RADIO DJ STEUERUNG ===
    send_radiodj_command("ClearPlaylist")
    send_radiodj_command("LoadTrackToBottom", BLIP_TRACK_ID)

    for track in selected:
        send_radiodj_command("LoadTrackToBottom", track[IDX_ID])

    send_radiodj_command("StopPlayer")
    send_radiodj_command("PlayPlaylistTrack")

    print("✅ Werbeblock erfolgreich geladen und gestartet.")

if __name__ == "__main__":
    main()
