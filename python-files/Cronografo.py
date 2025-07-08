import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, Toplevel
from tkcalendar import Calendar
import time
import json
import os
import pandas as pd

DATA_FILE = "time_tracking.json"

class TimeTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Cronógrafo Perpetuo")
        self.root.geometry("360x400")
        self.root.attributes('-topmost', True)

        self.current_activity = None
        self.start_time = None
        self.paused = False
        self.pause_accumulated = 0
        self.activities_by_date = self.load_data()

        # Fecha seleccionada
        self.date_selected = time.strftime("%Y-%m-%d")

        # Sección de fecha + botón calendario
        self.date_frame = tk.Frame(root)
        self.date_frame.pack(pady=5)

        self.date_label = tk.Label(self.date_frame, text=f"📅 {self.date_selected}", font=("Arial", 12))
        self.date_label.pack(side=tk.LEFT, padx=5)

        self.cal_button = tk.Button(self.date_frame, text="📆", command=self.show_calendar)
        self.cal_button.pack(side=tk.LEFT)

        # Contenedor cronómetro + iconos
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(pady=10)

        self.label = tk.Label(self.top_frame, text="Sin actividad", font=("Arial", 12))
        self.label.pack(side=tk.LEFT, padx=5)

        self.pause_button = tk.Button(self.top_frame, text="⏸️", command=self.pause_activity)
        self.pause_button.pack(side=tk.LEFT, padx=2)

        self.resume_button = tk.Button(self.top_frame, text="▶️", command=self.resume_activity)
        self.resume_button.pack(side=tk.LEFT, padx=2)

        # Renglón: Nueva + Swap
        self.row1 = tk.Frame(root)
        self.row1.pack(fill=tk.X, padx=5, pady=2)

        self.add_button = tk.Button(self.row1, text="+ Nueva Actividad", command=self.add_activity)
        self.add_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        self.swap_button = tk.Button(self.row1, text="Swap Actividad", command=self.swap_activity)
        self.swap_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        self.summary_button = tk.Button(root, text="📊 Darme Resumen", command=self.show_summary)
        self.summary_button.pack(fill=tk.X, padx=5, pady=5)

        # Renglón: Borrar tiempos + Borrar listado
        self.row2 = tk.Frame(root)
        self.row2.pack(fill=tk.X, padx=5, pady=2)

        self.clear_times_button = tk.Button(self.row2, text="🗑️ Borrar tiempos", command=self.clear_times)
        self.clear_times_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        self.clear_activities_button = tk.Button(self.row2, text="🔥 Borrar listado", command=self.clear_activities)
        self.clear_activities_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        self.update_timer()

    def show_calendar(self):
        win = Toplevel(self.root)
        win.title("Seleccionar fecha")

        cal = Calendar(win, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(padx=10, pady=10)

        def select_date():
            self.date_selected = cal.get_date()
            self.date_label.config(text=f"📅 {self.date_selected}")
            win.destroy()
            self.stop_current()  # guarda cualquier actividad actual

        confirm_btn = tk.Button(win, text="Seleccionar", command=select_date)
        confirm_btn.pack(pady=5)

    def add_activity(self):
        self.stop_current()
        name = simpledialog.askstring("Actividad", "Nombre de la nueva actividad:")
        if name:
            self.start_new_activity(name)

    def swap_activity(self):
        self.stop_current()
        self.show_activity_selector()

    def show_activity_selector(self):
        selector = Toplevel(self.root)
        selector.title("Selecciona actividad")

        tk.Label(selector, text="Haz clic para elegir:").pack(padx=10, pady=5)

        # Todas actividades de todas fechas
        all_activities = set()
        for day_acts in self.activities_by_date.values():
            all_activities.update(day_acts.keys())
        activities_list = list(all_activities) + ["[Nueva actividad]"]

        listbox = tk.Listbox(selector, width=30)
        for act in activities_list:
            listbox.insert(tk.END, act)
        listbox.pack(padx=10, pady=5)

        def on_select(event=None):
            selection = listbox.curselection()
            if selection:
                choice = listbox.get(selection)
                selector.destroy()
                if choice == "[Nueva actividad]":
                    self.add_activity()
                else:
                    self.start_new_activity(choice)

        listbox.bind('<Double-Button-1>', on_select)
        confirm_btn = tk.Button(selector, text="Seleccionar", command=on_select)
        confirm_btn.pack(pady=5)

    def start_new_activity(self, name):
        self.current_activity = name
        self.start_time = time.time()
        self.paused = False
        self.pause_accumulated = 0
        self.label.config(text=f"Actual: {self.current_activity}")

    def pause_activity(self):
        if self.current_activity and not self.paused:
            elapsed = time.time() - self.start_time
            self.pause_accumulated += elapsed
            self.paused = True
            self.label.config(text=f"PAUSADO: {self.current_activity}")

    def resume_activity(self):
        if self.current_activity and self.paused:
            self.start_time = time.time()
            self.paused = False
            self.label.config(text=f"Actual: {self.current_activity}")

    def stop_current(self):
        if self.current_activity:
            elapsed = 0
            if not self.paused:
                elapsed += time.time() - self.start_time
            elapsed += self.pause_accumulated

            day_key = self.date_selected
            self.activities_by_date.setdefault(day_key, {})
            self.activities_by_date[day_key].setdefault(self.current_activity, 0)
            self.activities_by_date[day_key][self.current_activity] += elapsed

            self.save_data()
            self.current_activity = None
            self.start_time = None
            self.paused = False
            self.pause_accumulated = 0
            self.label.config(text="Sin actividad")

    def show_summary(self):
        self.stop_current()
        date = self.date_selected
        acts = self.activities_by_date.get(date)
        if not acts:
            messagebox.showinfo("Resumen", f"No hay registros para {date}")
            return

        summary = f"Resumen {date}\n" + "\n".join([f"{k}: {self.format_duration(v)}" for k, v in acts.items()])
        messagebox.showinfo("Resumen", summary)

        save = messagebox.askyesno("Exportar", "¿Exportar a Excel?")
        if save:
            path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                filetypes=[("Excel files", "*.xlsx")])
            if path:
                self.export_to_excel(path, acts, date)

    def export_to_excel(self, path, acts, date):
        df = pd.DataFrame([
            {"Fecha": date, "Actividad": k, "Duración": self.format_duration(v)}
            for k, v in acts.items()
        ])
        df.to_excel(path, index=False)
        messagebox.showinfo("Exportado", f"Guardado en {path}")

    def clear_times(self):
        day_key = self.date_selected
        if day_key in self.activities_by_date:
            confirm = messagebox.askyesno("Confirmar", f"Borrar tiempos del {day_key}?")
            if confirm:
                self.activities_by_date[day_key] = {}
                self.save_data()
                messagebox.showinfo("Hecho", f"Tiempos del {day_key} borrados.")

    def clear_activities(self):
        confirm = messagebox.askyesno("Confirmar", "¿Borrar TODAS las actividades y tiempos?")
        if confirm:
            self.activities_by_date = {}
            self.save_data()
            messagebox.showinfo("Hecho", "Todo borrado.")

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.activities_by_date, f)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        return {}

    def format_duration(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def update_timer(self):
        if self.current_activity and not self.paused:
            elapsed = time.time() - self.start_time + self.pause_accumulated
            self.label.config(
                text=f"Actual: {self.current_activity} ({self.format_duration(elapsed)})"
            )
        elif self.current_activity and self.paused:
            self.label.config(
                text=f"PAUSADO: {self.current_activity} ({self.format_duration(self.pause_accumulated)})"
            )
        self.root.after(1000, self.update_timer)


if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTracker(root)
    root.mainloop()
