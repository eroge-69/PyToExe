import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os

def json_to_m3u(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError("JSON must be an array of objects")

        m3u_lines = ["#EXTM3U"]
        for entry in data:
            title = entry.get("title", "Unknown")
            url = entry.get("url", "")
            if url:
                m3u_lines.append(f"#EXTINF:-1,{title}")
                m3u_lines.append(url)
        
        m3u_content = "\n".join(m3u_lines)
        m3u_path = os.path.splitext(json_path)[0] + ".m3u"

        with open(m3u_path, 'w', encoding='utf-8') as f:
            f.write(m3u_content)

        return m3u_path

    except Exception as e:
        return f"Error: {e}"

def on_drop(event=None):
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if not file_path:
        return

    result = json_to_m3u(file_path)

    if result.lower().endswith(".m3u"):
        messagebox.showinfo("Erfolg", f"M3U-Datei wurde gespeichert:\n{result}")
    else:
        messagebox.showerror("Fehler", result)

def create_gui():
    root = tk.Tk()
    root.title("JSON to M3U Converter")
    root.geometry("400x200")
    root.resizable(False, False)

    label = tk.Label(root, text="Ziehe eine .json-Datei hierher oder klicke auf 'Datei wählen'", wraplength=300, pady=20)
    label.pack()

    btn = tk.Button(root, text="Datei wählen", command=on_drop)
    btn.pack(pady=10)

    root.mainloop()

create_gui()
