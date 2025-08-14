"""
Auto-clicker z GUI w Pythonie (Tkinter) — plik: python_clicker_with_gui.py
Wymagane biblioteki:
    pip install pyautogui pynput pillow

Funkcje:
- GUI do ustawienia interwału (ms / kliknięć na sekundę)
- Wybór przycisku myszy (left/right/middle)
- Single / double click
- Opcjonalne losowe wahanie interwału
- Liczba kliknięć (0 = nieskończone)
- Globalny hotkey (domyślnie F8) do start/stop
- Przyciski Start / Stop w GUI

Uwaga: używaj odpowiedzialnie. Aby natychmiast przerwać program, przełącz fokus na terminal i zamknij proces, lub ustaw liczbę kliknięć / kliknij Stop.
"""

import threading
import time
import random
import sys
import tkinter as tk
from tkinter import ttk, messagebox

import pyautogui
from pynput import keyboard

pyautogui.FAILSAFE = True  # przesuń mysz w lewy górny róg, żeby przerwać

# --- Global state kontrolny ---
clicking_event = threading.Event()
should_exit = threading.Event()

# domyślny globalny hotkey
HOTKEY = keyboard.Key.f8

# --- Funkcja wykonująca klikanie w wątku ---

def click_worker(interval_sec, button, click_type, jitter, max_clicks):
    """Wykonuje klikanie aż clicking_event będzie wyczyszczony lub osiągnięty max_clicks.
    interval_sec: średni interwał między kliknięciami (sekundy)
    jitter: maksymalny ułamek losowego wahania (np. 0.2 = ±20%)
    max_clicks: 0 => nieskończone
    """
    count = 0
    try:
        while clicking_event.is_set() and not should_exit.is_set():
            # wykonaj kliknięcie
            if click_type == 'single':
                pyautogui.click(button=button)
            else:
                pyautogui.doubleClick(button=button)

            count += 1
            if max_clicks > 0 and count >= max_clicks:
                # osiągnięto limit
                clicking_event.clear()
                break

            # oblicz losowy interwał
            if jitter and jitter > 0:
                factor = 1 + random.uniform(-jitter, jitter)
            else:
                factor = 1.0
            sleep_time = max(0.001, interval_sec * factor)

            # czekaj z możliwym szybkim przerwaniem
            waited = 0.0
            step = 0.01
            while waited < sleep_time and clicking_event.is_set() and not should_exit.is_set():
                time.sleep(step)
                waited += step
    except Exception as e:
        # w wypadku błędu (np. zablokowane GUI) powiadom
        print('Błąd w wątku klikera:', e)
        clicking_event.clear()


# --- Globalny nasłuch klawisza (hotkey) ---

def start_global_hotkey(toggle_callback):
    # toggle_callback() — funkcja, która ma być wywołana przy naciśnięciu hotkey
    def on_press(key):
        try:
            if key == HOTKEY:
                toggle_callback()
        except Exception:
            pass

    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()
    return listener


# --- GUI ---

class ClickerGUI:
    def __init__(self, root):
        self.root = root
        root.title('Python Clicker — prosty GUI')
        root.resizable(False, False)

        main = ttk.Frame(root, padding=12)
        main.grid(row=0, column=0)

        # Interwał: ms lub CPS
        ttk.Label(main, text='Interwał (ms):').grid(row=0, column=0, sticky='w')
        self.interval_var = tk.IntVar(value=100)
        self.interval_entry = ttk.Entry(main, textvariable=self.interval_var, width=10)
        self.interval_entry.grid(row=0, column=1, sticky='w')

        ttk.Label(main, text='(albo wpisz CPS poniżej)').grid(row=0, column=2, sticky='w')

        ttk.Label(main, text='Kliknięć/s (CPS):').grid(row=1, column=0, sticky='w')
        self.cps_var = tk.DoubleVar(value=10.0)
        self.cps_entry = ttk.Entry(main, textvariable=self.cps_var, width=10)
        self.cps_entry.grid(row=1, column=1, sticky='w')

        # Przyciski myszy
        ttk.Label(main, text='Przycisk:').grid(row=2, column=0, sticky='w')
        self.button_var = tk.StringVar(value='left')
        ttk.OptionMenu(main, self.button_var, 'left', 'left', 'right', 'middle').grid(row=2, column=1, sticky='w')

        # Typ kliknięcia
        ttk.Label(main, text='Typ kliknięcia:').grid(row=3, column=0, sticky='w')
        self.click_type_var = tk.StringVar(value='single')
        ttk.OptionMenu(main, self.click_type_var, 'single', 'single', 'double').grid(row=3, column=1, sticky='w')

        # Jitter
        ttk.Label(main, text='Losowe wahanie interwału (%):').grid(row=4, column=0, sticky='w')
        self.jitter_var = tk.DoubleVar(value=0.0)
        ttk.Entry(main, textvariable=self.jitter_var, width=10).grid(row=4, column=1, sticky='w')

        # Liczba kliknięć
        ttk.Label(main, text='Liczba kliknięć (0 = nieskończone):').grid(row=5, column=0, sticky='w')
        self.count_var = tk.IntVar(value=0)
        ttk.Entry(main, textvariable=self.count_var, width=10).grid(row=5, column=1, sticky='w')

        # Hotkey info
        self.hotkey_label = ttk.Label(main, text=f'Hotkey: {HOTKEY} (F8) — przełącz start/stop')
        self.hotkey_label.grid(row=6, column=0, columnspan=3, pady=(6, 0), sticky='w')

        # Status
        self.status_var = tk.StringVar(value='Gotowy')
        ttk.Label(main, text='Status:').grid(row=7, column=0, sticky='w')
        self.status_display = ttk.Label(main, textvariable=self.status_var, foreground='blue')
        self.status_display.grid(row=7, column=1, sticky='w')

        # przyciski Start / Stop
        controls = ttk.Frame(main)
        controls.grid(row=8, column=0, columnspan=3, pady=(10, 0))
        self.start_btn = ttk.Button(controls, text='Start', command=self.start_clicking)
        self.start_btn.grid(row=0, column=0, padx=4)
        self.stop_btn = ttk.Button(controls, text='Stop', command=self.stop_clicking, state='disabled')
        self.stop_btn.grid(row=0, column=1, padx=4)

        # zamknięcie aplikacji
        root.protocol('WM_DELETE_WINDOW', self.on_close)

        # uruchom nasłuch hotkey globalnie
        self.hotkey_listener = start_global_hotkey(self.toggle_via_hotkey)

        # wątek klikera (będzie ustawiony przy starcie)
        self.worker_thread = None

    def get_interval_seconds(self):
        # prefer CPS jeśli podano > 0
        try:
            cps = float(self.cps_var.get())
            if cps > 0:
                return 1.0 / cps
        except Exception:
            pass
        # inaczej użyj ms
        ms = int(self.interval_var.get())
        return max(0.001, ms / 1000.0)

    def start_clicking(self):
        if clicking_event.is_set():
            return
        interval = self.get_interval_seconds()
        button = self.button_var.get()
        click_type = self.click_type_var.get()
        try:
            jitter_pct = float(self.jitter_var.get())
            jitter = max(0.0, jitter_pct / 100.0)
        except Exception:
            jitter = 0.0
        try:
            max_clicks = int(self.count_var.get())
            if max_clicks < 0:
                max_clicks = 0
        except Exception:
            max_clicks = 0

        # ustaw status i włącz event
        clicking_event.set()
        self.status_var.set('Klikanie — włączone')
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')

        # utwórz wątek
        self.worker_thread = threading.Thread(target=click_worker,
                                              args=(interval, button, click_type, jitter, max_clicks),
                                              daemon=True)
        self.worker_thread.start()

    def stop_clicking(self):
        if not clicking_event.is_set():
            return
        clicking_event.clear()
        self.status_var.set('Zatrzymywanie...')
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')

    def toggle_via_hotkey(self):
        # funkcja wywoływana z wątku Listener - musimy bezpiecznie zmienić GUI
        if clicking_event.is_set():
            # zatrzymaj
            self.root.after(0, self.stop_clicking)
        else:
            self.root.after(0, self.start_clicking)

    def on_close(self):
        # ustaw flagi wyjścia
        should_exit.set()
        clicking_event.clear()
        time.sleep(0.05)
        try:
            self.root.destroy()
        except Exception:
            pass


# --- Uruchomienie aplikacji ---

def main():
    root = tk.Tk()
    style = ttk.Style(root)
    # użyj domyślnego stylu platformy
    app = ClickerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
