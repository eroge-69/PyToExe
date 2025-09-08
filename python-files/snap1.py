import tkinter as tk
from datetime import datetime, timedelta

# --- Configurazione orari ---
WORK_HOURS = {
    0: [("08:30", "13:00"), ("14:30", "18:00")],  # Lunedì
    1: [("08:30", "13:00"), ("14:30", "18:00")],  # Martedì
    2: [("08:30", "13:00"), ("14:30", "18:00")],  # Mercoledì
    3: [("08:30", "13:00"), ("14:30", "18:00")],  # Giovedì
    4: [("08:30", "13:00"), ("14:30", "17:00")],  # Venerdì
}

def parse_time(day: datetime, timestr: str) -> datetime:
    """Converte 'HH:MM' in datetime dello stesso giorno."""
    h, m = map(int, timestr.split(":"))
    return day.replace(hour=h, minute=m, second=0, microsecond=0)

def next_work_period(now: datetime):
    """Restituisce il prossimo intervallo lavorativo attivo (start, end)."""
    day = now.weekday()
    # Scorri fino a venerdì
    for d in range(day, 5):
        date = now + timedelta(days=(d - day))
        for start, end in WORK_HOURS[d]:
            s, e = parse_time(date, start), parse_time(date, end)
            if now < s:      # ancora prima di un intervallo
                return s, e
            if s <= now < e: # dentro un intervallo
                return now, e
    return None, None  # oltre il venerdì sera

def time_to_weekend(now: datetime):
    """Calcola il tempo lavorativo residuo fino a venerdì sera."""
    total = timedelta()
    for d in range(now.weekday(), 5):
        date = now + timedelta(days=(d - now.weekday()))
        for start, end in WORK_HOURS[d]:
            s, e = parse_time(date, start), parse_time(date, end)
            if d == now.weekday():
                if now < s:
                    total += e - s
                elif s <= now < e:
                    total += e - now
            else:
                total += e - s
    return total

def to_snap(td: timedelta) -> int:
    """Arrotonda per eccesso in blocchi da 15 min."""
    minutes = int(td.total_seconds() // 60)
    snaps = -(-minutes // 15)  # ceiling division
    return snaps

def format_td(td: timedelta):
    """Rende ore:minuti leggibili."""
    total_minutes = int(td.total_seconds() // 60)
    h, m = divmod(total_minutes, 60)
    return f"{h:02d}:{m:02d}"

# --- GUI ---
root = tk.Tk()
root.title("SNAP Timer")

labels = {
    "Tempo alla pausa": tk.Label(root, font=("Helvetica", 16)),
    "Tempo al WE": tk.Label(root, font=("Helvetica", 16)),
    "SNAP alla pausa": tk.Label(root, font=("Helvetica", 16)),
    "SNAP al WE": tk.Label(root, font=("Helvetica", 16)),
}

for i, (k, lbl) in enumerate(labels.items()):
    tk.Label(root, text=k, font=("Helvetica", 14, "bold")).grid(row=i, column=0, sticky="w", padx=10, pady=5)
    lbl.grid(row=i, column=1, sticky="e", padx=10, pady=5)

def update_labels():
    now = datetime.now()
    start, end = next_work_period(now)
    if not start:  # oltre venerdì sera
        pausa_td = timedelta(0)
        we_td = timedelta(0)
    else:
        pausa_td = end - now if now < end else timedelta(0)
        we_td = time_to_weekend(now)

    labels["Tempo alla pausa"].config(text=format_td(pausa_td))
    labels["Tempo al WE"].config(text=format_td(we_td))
    labels["SNAP alla pausa"].config(text=f"{to_snap(pausa_td)} SNAP")
    labels["SNAP al WE"].config(text=f"{to_snap(we_td)} SNAP")

    root.after(60 * 1000, update_labels)  # aggiorna ogni minuto

update_labels()
root.mainloop()