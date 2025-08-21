import customtkinter as ctk
import sqlite3
import os
from datetime import date, datetime
import threading
import time
from plyer import notification
from tkinter import messagebox

# Datenbank-Setup
# Einen robusteren Pfad für die Datenbank verwenden
DB_FILE = os.path.join(os.path.expanduser("~"), "habit_tracker.db")

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Tabellen erstellen
cursor.execute("""
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    color TEXT NOT NULL,
    reminder_time TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER,
    date TEXT,
    UNIQUE(habit_id, date)
)
""")
conn.commit()

# --- Hauptanwendungsklasse ---
class HabitTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gewohnheiten-Tracker")
        self.geometry("800x600")
        
        # Icon für die App-Oberfläche setzen
        # WICHTIG: Sie müssen Ihre JPG-Datei in eine .ico-Datei umwandeln
        # und sie als 'habit_tracker_icon.ico' im selben Verzeichnis speichern.
        try:
            self.iconbitmap("habit_tracker_icon.ico")
        except:
            # Dies wird angezeigt, wenn das Icon nicht gefunden wird,
            # um zu verhindern, dass das Programm abstürzt.
            print("Warnung: Das Icon 'habit_tracker_icon.ico' wurde nicht gefunden. Die App wird ohne Icon gestartet.")
            
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # --- Frames ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.habit_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.habit_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(fill="x", pady=10)
        
        self.add_button = ctk.CTkButton(self.button_frame, text="Neue Gewohnheit hinzufügen", command=self.add_habit_dialog)
        self.add_button.pack(side="left", expand=True, padx=10)

        self.stats_button = ctk.CTkButton(self.button_frame, text="Statistiken anzeigen", command=self.view_stats)
        self.stats_button.pack(side="left", expand=True, padx=10)

        self.load_habits()
        
        # Erinnerungs-Thread starten
        threading.Thread(target=self.reminder_loop, daemon=True).start()

    # --- Laden und Anzeigen von Gewohnheiten ---
    def load_habits(self):
        for widget in self.habit_frame.winfo_children():
            widget.destroy()

        cursor.execute("SELECT id, name, color, reminder_time FROM habits")
        habits = cursor.fetchall()
        
        if not habits:
            no_habits_label = ctk.CTkLabel(self.habit_frame, text="Sie haben noch keine Gewohnheiten. Klicken Sie auf 'Neue Gewohnheit hinzufügen', um zu starten!", font=("Arial", 16))
            no_habits_label.pack(expand=True)
            return

        for habit_id, name, color, reminder_time in habits:
            self.create_habit_row(habit_id, name, color, reminder_time)

    def create_habit_row(self, habit_id, name, color, reminder_time):
        row_frame = ctk.CTkFrame(self.habit_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=5)

        # Gewohnheitsname und Farbanzeige
        name_label = ctk.CTkLabel(row_frame, text=name, font=("Arial", 18, "bold"))
        name_label.pack(side="left", padx=10, pady=5)
        
        color_label = ctk.CTkLabel(row_frame, text="", width=20, corner_radius=5, fg_color=color)
        color_label.pack(side="left", padx=5)
        
        # Checkbox für die Erledigung
        today = date.today().isoformat()
        cursor.execute("SELECT 1 FROM completions WHERE habit_id=? AND date=?", (habit_id, today))
        is_done = cursor.fetchone() is not None

        checkbox_var = ctk.StringVar(value="on" if is_done else "off")
        checkbox = ctk.CTkCheckBox(row_frame, text="Heute erledigt", variable=checkbox_var, onvalue="on", offvalue="off",
                                   command=lambda h_id=habit_id, var=checkbox_var: self.toggle_completion(h_id, var.get()))
        checkbox.pack(side="right", padx=10, pady=5)
        
        # Bearbeiten- und Löschen-Buttons
        delete_button = ctk.CTkButton(row_frame, text="Löschen", fg_color="red", hover_color="#8B0000", width=80,
                                     command=lambda h_id=habit_id: self.delete_habit(h_id))
        delete_button.pack(side="right", padx=5)

    def toggle_completion(self, habit_id, state):
        today = date.today().isoformat()
        if state == "on":
            try:
                cursor.execute("INSERT INTO completions (habit_id, date) VALUES (?, ?)", (habit_id, today))
                conn.commit()
            except sqlite3.IntegrityError:
                pass # Bereits als erledigt markiert
        else:
            cursor.execute("DELETE FROM completions WHERE habit_id=? AND date=?", (habit_id, today))
            conn.commit()
            
    def delete_habit(self, habit_id):
        if messagebox.askyesno("Gewohnheit löschen", "Sind Sie sicher, dass Sie diese Gewohnheit löschen möchten?"):
            cursor.execute("DELETE FROM habits WHERE id=?", (habit_id,))
            cursor.execute("DELETE FROM completions WHERE habit_id=?", (habit_id,))
            conn.commit()
            self.load_habits()
            
    # --- Dialog zum Hinzufügen einer Gewohnheit ---
    def add_habit_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Neue Gewohnheit hinzufügen")
        dialog.geometry("400x300")
        dialog.transient(self) # Dialog immer im Vordergrund halten
        
        ctk.CTkLabel(dialog, text="Name der Gewohnheit:").pack(pady=5)
        name_entry = ctk.CTkEntry(dialog)
        name_entry.pack(pady=5)
        
        color_var = ctk.StringVar(value="#2E86C1") # Standardfarbe
        color_button = ctk.CTkButton(dialog, text="Farbe wählen", command=lambda: self.choose_color(color_var))
        color_button.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Erinnerungszeit (HH:MM):").pack(pady=5)
        time_entry = ctk.CTkEntry(dialog, placeholder_text="z.B. 08:30")
        time_entry.pack(pady=5)
        
        def save_habit():
            name = name_entry.get().strip()
            color = color_var.get()
            reminder_time = time_entry.get().strip()
            
            if not name:
                messagebox.showerror("Fehler", "Der Name der Gewohnheit darf nicht leer sein.")
                return
            
            cursor.execute("INSERT INTO habits (name, color, reminder_time) VALUES (?, ?, ?)", (name, color, reminder_time))
            conn.commit()
            self.load_habits()
            dialog.destroy()
            
        save_button = ctk.CTkButton(dialog, text="Gewohnheit speichern", command=save_habit)
        save_button.pack(pady=10)

    def choose_color(self, color_var):
        from tkinter import colorchooser
        color_code = colorchooser.askcolor(title="Farbe wählen")[1]
        if color_code:
            color_var.set(color_code)
            
    # --- Statistikansicht ---
    def view_stats(self):
        stats_window = ctk.CTkToplevel(self)
        stats_window.title("Gewohnheiten-Statistiken")
        stats_window.geometry("600x400")
        stats_window.transient(self)
        
        stats_frame = ctk.CTkScrollableFrame(stats_window)
        stats_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        cursor.execute("SELECT id, name FROM habits")
        habits = cursor.fetchall()
        
        for habit_id, name in habits:
            self.display_streak(stats_frame, habit_id, name)
            
    def display_streak(self, parent_frame, habit_id, name):
        cursor.execute("SELECT date FROM completions WHERE habit_id=? ORDER BY date DESC", (habit_id,))
        completions = [d[0] for d in cursor.fetchall()]
        
        current_streak = 0
        if completions:
            last_date = datetime.strptime(completions[0], "%Y-%m-%d").date()
            if last_date == date.today():
                current_streak = 1
                
            for i in range(1, len(completions)):
                prev_date = datetime.strptime(completions[i-1], "%Y-%m-%d").date()
                curr_date = datetime.strptime(completions[i], "%Y-%m-%d").date()
                if (prev_date - curr_date).days == 1:
                    current_streak += 1
                else:
                    break

        ctk.CTkLabel(parent_frame, text=f"{name}: Strähne", font=("Arial", 16, "bold")).pack(anchor="w", pady=(10, 0))
        streak_label = ctk.CTkLabel(parent_frame, text=f"{current_streak} Tage in Folge!", font=("Arial", 14))
        streak_label.pack(anchor="w", padx=20)
        
    # --- Erinnerungssystem ---
    def reminder_loop(self):
        while True:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            today = date.today().isoformat()
            
            cursor.execute("SELECT id, name, reminder_time FROM habits WHERE reminder_time=?", (current_time,))
            habits_to_remind = cursor.fetchall()
            
            for habit_id, name, _ in habits_to_remind:
                cursor.execute("SELECT 1 FROM completions WHERE habit_id=? AND date=?", (habit_id, today))
                is_done = cursor.fetchone()
                
                if not is_done:
                    notification.notify(
                        title="Gewohnheits-Erinnerung",
                        message=f"Hey! Es ist Zeit für deine Gewohnheit: {name}",
                        app_name="Gewohnheiten-Tracker",
                        timeout=10
                    )
            time.sleep(60) # Alle Minute prüfen
            
if __name__ == "__main__":
    app = HabitTrackerApp()
    app.mainloop()
