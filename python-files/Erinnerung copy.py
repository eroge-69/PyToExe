import win32com.client
import pythoncom
import datetime
import threading
import queue
import time
import tkinter as tk

from dateutil import parser  # Für flexibles Parsen unterschiedlicher Datumsformate

def get_upcoming_events():
    """Holt Outlook-Termine zwischen jetzt und 16 Minuten später."""
    pythoncom.CoInitialize()  # COM-Bibliothek initialisieren (notwendig für Thread)
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    calendar = outlook.GetDefaultFolder(9)  # 9 steht für den Kalenderordner in Outlook

    now = datetime.datetime.now()
    later = now + datetime.timedelta(minutes=16)

    items = calendar.Items
    items.IncludeRecurrences = True  # Wiederkehrende Termine mit einschließen
    items.Sort("[Start]")  # Termine nach Startzeit sortieren

    # Termine filtern, die zwischen 'now' und 'later' liegen
    restriction = "[Start] >= '{}' AND [Start] <= '{}'".format(
        now.strftime("%m/%d/%Y %H:%M"), later.strftime("%m/%d/%Y %H:%M")
    )
    restricted_items = items.Restrict(restriction)

    events = []
    for item in restricted_items:
        start = item.Start
        subject = item.Subject
        
        # Startzeit robust parsen (kann String mit TZ oder datetime-Objekt sein)
        if isinstance(start, str):
            try:
                start_dt = parser.parse(start)
            except:
                start_dt = datetime.datetime.fromisoformat(start)
        else:
            start_dt = start
        
        # Zeitzoneninfo entfernen, um Vergleichbarkeit zu gewährleisten
        if hasattr(start_dt, 'tzinfo') and start_dt.tzinfo is not None:
            start_dt = start_dt.replace(tzinfo=None)
        
        # Termine nur hinzufügen, wenn sie in der Zeitspanne liegen
        if now < start_dt <= later:
            events.append((subject, start_dt))
    return events

def calendar_monitor(popup_queue):
    """
    Überwacht den Kalender in einem separaten Thread,
    sendet Popups bei Terminen in 15 Minuten.
    """
    shown = set()  # Verhindert mehrfaches Anzeigen desselben Termins
    while True:
        events = get_upcoming_events()
        now = datetime.datetime.now()
        for subject, start_dt in events:
            remaining_seconds = int((start_dt - now).total_seconds())
            minutes_left = remaining_seconds // 60

            # Popup nur auslösen, wenn noch genau 15 Minuten verbleiben
            if minutes_left == 15 and (subject, start_dt) not in shown:
                popup_queue.put((subject, remaining_seconds, start_dt))
                shown.add((subject, start_dt))
        time.sleep(60)  # Prüft alle 60 Sekunden

def show_popup(subject, remaining_seconds, start_dt, root):
    """
    Erstellt ein Popup-Fenster mit Termininfo und Countdown,
    aktualisiert die verbleibende Zeit jede Sekunde.
    """
    popup = tk.Toplevel(root)
    popup.title("Outlook Termin Erinnerung")
    popup.geometry("350x150")
    popup.configure(bg="#FF00FF")  # Magenta Hintergrundfarbe

    label = tk.Label(popup, text="", font=("Arial", 16, "bold"), bg="#FF00FF", fg="white")
    label.pack(padx=20, pady=20)

    def update():
        nonlocal remaining_seconds
        remaining_seconds = int((start_dt - datetime.datetime.now()).total_seconds())
        if remaining_seconds > 0:
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60
            label_text = f"Termin: {subject}\nVerbleibende Zeit: {minutes:02d}:{seconds:02d} Minuten"
            label.config(text=label_text)
            popup.after(1000, update)  # Aktualisiert alle 1000 ms (1 Sekunde)
        else:
            popup.destroy()  # Schließt das Popup bei 0 Sekunden

    update()  # Starte die Countdownfunktion

    btn = tk.Button(popup, text="Schließen", command=popup.destroy,
                    bg="#990099", fg="white", activebackground="#cc33cc",
                    relief="raised", bd=3, padx=10, pady=5)
    btn.pack(pady=10)

def main():
    """
    Hauptfunktion startet den Hintergrund-Thread zur Kalenderüberwachung,
    verwaltet die Popup-Anzeige und verbirgt das Hauptfenster.
    """
    popup_queue = queue.Queue()
    root = tk.Tk()
    root.withdraw()  # Versteckt das Hauptfenster

    def check_queue():
        """
        Prüft regelmäßig, ob neue Popup-Anzeigen in der Queue sind,
        und zeigt sie an.
        """
        try:
            while True:
                subject, remaining_seconds, start_dt = popup_queue.get_nowait()
                show_popup(subject, remaining_seconds, start_dt, root)
        except queue.Empty:
            pass
        root.after(1000, check_queue)  # Check alle 1000 ms

    # Starte Kalender-Überwachung im Hintergrund
    thread = threading.Thread(target=calendar_monitor, args=(popup_queue,), daemon=True)
    thread.start()

    check_queue()
    root.mainloop()

if __name__ == "__main__":
    main()