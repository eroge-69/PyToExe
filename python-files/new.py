import tkinter as tk
from tkinter import messagebox, scrolledtext
import webbrowser
import time
import threading

def open_links():
    raw_text = text_box.get("1.0", tk.END).strip()
    if not raw_text:
        messagebox.showerror("Error", "Please paste at least one link.")
        return

    try:
        delay = float(delay_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Delay must be a number.")
        return

    # Extract links (split by newline, comma, or space)
    links = [line.strip() for line in raw_text.replace(",", "\n").split("\n") if line.strip()]
    if not links:
        messagebox.showerror("Error", "No valid links found.")
        return

    def worker():
        for url in links:
            if not url.lower().startswith(("http://", "https://")):
                url = "https://" + url
            print(f"Opening: {url}")
            webbrowser.open_new_tab(url)
            time.sleep(delay)
        messagebox.showinfo("Done", "All links opened.")

    threading.Thread(target=worker, daemon=True).start()

# --- GUI ---
root = tk.Tk()
root.title("Open Multiple Links")
root.geometry("500x400")
root.resizable(False, False)

tk.Label(root, text="Paste your links below (one per line):").pack(pady=5)

text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=58, height=15)
text_box.pack(padx=10, pady=5)

frame = tk.Frame(root)
frame.pack(pady=5)

tk.Label(frame, text="Delay (seconds):").pack(side=tk.LEFT)
delay_entry = tk.Entry(frame, width=5)
delay_entry.insert(0, "0.5")
delay_entry.pack(side=tk.LEFT, padx=5)

open_button = tk.Button(root, text="Open All Links", command=open_links, bg="#4CAF50", fg="white", width=20)
open_button.pack(pady=10)

root.mainloop()
