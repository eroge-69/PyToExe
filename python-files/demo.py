import tkinter as tk
from tkinter import messagebox, scrolledtext
import pyttsx3
import requests
import datetime
import sqlite3

# --- Voice Engine ---
engine = pyttsx3.init()
engine.setProperty('rate', 170)

def speak(text):
    engine.say(text)
    engine.runAndWait()

# --- Weather Function ---
def get_weather(city="London"):
    api_key = "YOUR_API_KEY_HERE"  # Replace this with your OpenWeatherMap API key
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()
        if data["cod"] != 200:
            return "Weather data unavailable"
        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return f"{city}: {weather.capitalize()}, {temp}°C"
    except Exception as e:
        return "Error getting weather"

# --- SQLite Setup ---
conn = sqlite3.connect("notes.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, content TEXT)")
conn.commit()

# --- Main Dashboard App ---
class SmartDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Dashboard")
        self.geometry("800x600")
        self.configure(bg="#202124")

        self.build_ui()
        self.refresh_time()
        self.load_notes()

    def build_ui(self):
        # Time Display
        self.time_label = tk.Label(self, font=("Segoe UI", 16), fg="white", bg="#202124")
        self.time_label.pack(pady=10)

        # Weather
        self.weather_label = tk.Label(self, text=get_weather(), font=("Segoe UI", 14), fg="#66c2ff", bg="#202124")
        self.weather_label.pack()

        # Note Area
        self.note_box = scrolledtext.ScrolledText(self, width=80, height=15, font=("Segoe UI", 12), wrap=tk.WORD)
        self.note_box.pack(pady=20)

        # Buttons
        button_frame = tk.Frame(self, bg="#202124")
        button_frame.pack()

        tk.Button(button_frame, text="Save Note", command=self.save_note, bg="#34a853", fg="white", width=15).grid(row=0, column=0, padx=10)
        tk.Button(button_frame, text="Clear", command=self.clear_notes, bg="#ea4335", fg="white", width=15).grid(row=0, column=1, padx=10)
        tk.Button(button_frame, text="Read Aloud", command=self.read_notes, bg="#fbbc05", fg="black", width=15).grid(row=0, column=2, padx=10)

    def refresh_time(self):
        now = datetime.datetime.now().strftime("%A, %d %B %Y | %H:%M:%S")
        self.time_label.config(text=now)
        self.after(1000, self.refresh_time)

    def save_note(self):
        text = self.note_box.get("1.0", tk.END).strip()
        if text:
            cursor.execute("INSERT INTO notes (content) VALUES (?)", (text,))
            conn.commit()
            messagebox.showinfo("Saved", "Note saved successfully.")
            self.note_box.delete("1.0", tk.END)
            self.load_notes()

    def load_notes(self):
        self.note_box.delete("1.0", tk.END)
        cursor.execute("SELECT content FROM notes ORDER BY id DESC LIMIT 5")
        notes = cursor.fetchall()
        for note in notes:
            self.note_box.insert(tk.END, f"- {note[0]}\n\n")

    def clear_notes(self):
        self.note_box.delete("1.0", tk.END)

    def read_notes(self):
        content = self.note_box.get("1.0", tk.END).strip()
        if content:
            speak(content)
        else:
            speak("There are no notes to read.")

# --- Run App ---
if __name__ == "__main__":
    app = SmartDashboard()
    app.mainloop()
