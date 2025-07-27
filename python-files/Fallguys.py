import tkinter as tk
from tkinter import messagebox, scrolledtext
import asyncio
import aiohttp
import threading
import time
import math

# Globale Zähler
timeout_count = 0
error_count = 0

def start_attack():
    global timeout_count, error_count
    timeout_count = 0
    error_count = 0

    url = entry_url.get()
    port = entry_port.get()

    use_fixed_mode = var_mode.get() == 1

    if not url or not port:
        messagebox.showerror("Fehler", "IP/Hostname und Port müssen ausgefüllt sein.")
        return

    try:
        full_url = f"http://{url}:{int(port)}"
    except ValueError:
        messagebox.showerror("Fehler", "Ungültiger Port.")
        return

    # Modus 1: Feste Anzahl Anfragen
    if use_fixed_mode:
        try:
            total_requests = int(entry_total.get())
            concurrent_requests = int(entry_concurrent.get())
        except ValueError:
            messagebox.showerror("Fehler", "Ungültige Anzahl oder Threads.")
            return
    else:
        try:
            duration = float(entry_duration.get())
            rate = float(entry_rate.get())
            total_requests = math.ceil(duration * rate)
            concurrent_requests = int(rate)
        except ValueError:
            messagebox.showerror("Fehler", "Ungültige Zeit oder Rate.")
            return

    log_text.delete(1.0, tk.END)
    status_var.set(f"Starte Test auf {full_url}...")

    # Hintergrund-Thread starten
    thread = threading.Thread(target=run_async_attack, args=(full_url, total_requests, concurrent_requests))
    thread.start()

def run_async_attack(url, total_requests, concurrent_requests):
    asyncio.run(attack(url, total_requests, concurrent_requests))

async def attack(url, total_requests, concurrent_requests):
    global timeout_count, error_count
    start_time = time.time()
    connector = aiohttp.TCPConnector(limit=concurrent_requests)

    async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=5)) as session:
        tasks = []
        for i in range(total_requests):
            task = send_request(session, url, i)
            tasks.append(task)

            # Optional: kleine Pause, wenn gewünscht (hier deaktiviert)
            # await asyncio.sleep(1 / concurrent_requests)

        await asyncio.gather(*tasks)

    duration = time.time() - start_time
    log_text.insert(tk.END, f"\nTest abgeschlossen in {duration:.2f} Sekunden.\n")
    status_var.set(f"Fertig – Fehler: {error_count} | Timeouts: {timeout_count}")

async def send_request(session, url, i):
    global timeout_count, error_count
    try:
        async with session.get(url) as response:
            log_text.insert(tk.END, f"[{i}] Status: {response.status}\n")
    except asyncio.TimeoutError:
        log_text.insert(tk.END, f"[{i}] Fehler: Zeitüberschreitung\n")
        timeout_count += 1
    except Exception as e:
        log_text.insert(tk.END, f"[{i}] Fehler: {e}\n")
        error_count += 1

# GUI aufbauen
root = tk.Tk()
root.title("Lasttest Tool (GUI erweitert)")
root.geometry("700x600")

tk.Label(root, text="Ziel-IP / Hostname:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
entry_url = tk.Entry(root, width=40)
entry_url.grid(row=0, column=1, padx=5, pady=2)

tk.Label(root, text="Port:").grid(row=1, column=0, sticky="e", padx=5)
entry_port = tk.Entry(root)
entry_port.grid(row=1, column=1, padx=5)

# Moduswahl
var_mode = tk.IntVar(value=1)

tk.Radiobutton(root, text="Feste Anzahl Anfragen", variable=var_mode, value=1).grid(row=2, column=0, sticky="e", padx=5, pady=5)
tk.Radiobutton(root, text="Dauer & Rate", variable=var_mode, value=2).grid(row=2, column=1, sticky="w", padx=5, pady=5)

# Modus 1 Felder
tk.Label(root, text="Anzahl Anfragen:").grid(row=3, column=0, sticky="e", padx=5)
entry_total = tk.Entry(root)
entry_total.grid(row=3, column=1, padx=5)

tk.Label(root, text="Gleichzeitige Anfragen:").grid(row=4, column=0, sticky="e", padx=5)
entry_concurrent = tk.Entry(root)
entry_concurrent.grid(row=4, column=1, padx=5)

# Modus 2 Felder
tk.Label(root, text="Dauer (Sekunden):").grid(row=5, column=0, sticky="e", padx=5)
entry_duration = tk.Entry(root)
entry_duration.grid(row=5, column=1, padx=5)

tk.Label(root, text="Anfragen pro Sekunde:").grid(row=6, column=0, sticky="e", padx=5)
entry_rate = tk.Entry(root)
entry_rate.grid(row=6, column=1, padx=5)

start_button = tk.Button(root, text="Test starten", command=start_attack, bg="lightgreen")
start_button.grid(row=7, column=0, columnspan=2, pady=10)

log_text = scrolledtext.ScrolledText(root, height=20, width=80)
log_text.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor="w")
status_label.grid(row=9, column=0, columnspan=2, sticky="we")

root.mainloop()
