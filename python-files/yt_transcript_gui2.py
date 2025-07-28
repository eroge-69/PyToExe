import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar, END
import subprocess
import os
import glob
import platform
import time

# Podesi put do skripte ako se ne nalazi u istom folderu
#SCRIPT_PATH = r'C:\Users\zrinko.gracanin\Desktop\yt_transcript\bin\yt_transcript.py'
#TRANSCRIPT_DIR = r'C:\Users\zrinko.gracanin\Desktop\yt_transcript'  # Folder gdje se spremaju .txt transkripti
# Bazni folder gde se nalazi ova skripta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Putanja do yt_transcript.py u istom folderu
SCRIPT_PATH = os.path.join(BASE_DIR, 'yt_transcript.py')
# Podfolder "transcripts" unutar istog direktorijuma
TRANSCRIPT_DIR = os.path.dirname(BASE_DIR)

def run_transcription():
    global timer_running, start_time
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Greška", "Unesite YouTube URL.")
        return
    # Onemogući dugme dok traje transkripcija
    transcribe_button.config(state=tk.DISABLED)

    timer_running = True
    start_time = time.time()
    update_timer()

    def task():
        global timer_running 
        try:
            subprocess.run(
                ["python", SCRIPT_PATH, "-v", url, "-t", TRANSCRIPT_DIR],
                check=True,
            )
            root.after(0, lambda: messagebox.showinfo("Uspjeh", "Transkripcija završena!"))
            root.after(0, update_listbox)
        except subprocess.CalledProcessError as e:
            root.after(0, lambda: messagebox.showerror("Greška u skripti", f"Dogodila se greška: {e}"))
        finally:
            timer_running = False
            timer_label.config(text=f"")
            # Omogući dugme kad završi
            root.after(0, lambda: transcribe_button.config(state=tk.NORMAL))

    import threading
    threading.Thread(target=task).start()


def update_listbox():
    listbox.delete(0, END)
    txt_files = glob.glob(os.path.join(TRANSCRIPT_DIR, "*.txt"))
    for file in sorted(txt_files):
        listbox.insert(END, os.path.basename(file))

def open_file_location(event):
    selected = listbox.curselection()
    if not selected:
        return
    file_name = listbox.get(selected[0])
    file_path = os.path.abspath(os.path.join(TRANSCRIPT_DIR, file_name))

    try:
        system_os = platform.system()
        if system_os == "Windows":
            subprocess.run(["explorer", "/select,", os.path.normpath(file_path)])
        elif system_os == "Darwin":  # macOS
            subprocess.run(["open", "-R", file_path])
        elif system_os == "Linux":
            folder = os.path.dirname(file_path)
            subprocess.run(["xdg-open", folder])
        else:
            messagebox.showinfo("Nepoznat OS", f"Nepodržan OS: {system_os}")
    except Exception as e:
        messagebox.showerror("Greška", f"Ne mogu otvoriti folder: {e}")

def update_timer():
    if timer_running:
        elapsed = int(time.time() - start_time)
        timer_label.config(text=f"Trajanje: {elapsed} sekundi")
        root.after(1000, update_timer)


# --- GUI setup ---
#root = tk.Tk()
#root.title("YouTube Transcriber")
if __name__ == "__main__":
    root = tk.Tk()
    # Sve tvoje GUI komponente idu ovde direktno, ili ih već imaš iznad
#    root.mainloop()

#timer
timer_running = False
start_time = None
timer_label = tk.Label(root, text="", fg="blue")
timer_label.pack(pady=5)

# Unos za URL
tk.Label(root, text="YouTube URL:").pack(pady=5)
url_entry = tk.Entry(root, width=60)
url_entry.pack(padx=10)

# Gumb za transkripciju
transcribe_button = tk.Button(root, text="Transkribiraj", command=run_transcription)
transcribe_button.pack(pady=10)

# Labela i listbox za transkripte
tk.Label(root, text="Transkripti u mapi:").pack()
frame = tk.Frame(root)
frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=False)

scrollbar = Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox = Listbox(frame, width=80, height=10, yscrollcommand=scrollbar.set)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=listbox.yview)

# Bind dvostruki klik (double-click)
listbox.bind("<Double-Button-1>", open_file_location)

# Učitaj postojeće .txt fajlove pri pokretanju
update_listbox()

root.mainloop()
