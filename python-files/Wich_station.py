import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import subprocess
import threading
import pystray
from itertools import count




def kill_all_customrp():
    try:
        subprocess.call('taskkill /F /IM CustomRP.exe', shell=True)
    except Exception as e:
        print("Nem sikerült leállítani:", e)


class AnimatedGIF:
    def __init__(self, label, gif_path, size=None):
        self.label = label
        self.gif = Image.open(gif_path)
        self.frames = []
        try:
            for i in count(1):
                frame = self.gif.copy()
                if size:
                    frame = frame.convert("RGBA")  # <-- ez biztosítja az átlátszóságot
                    frame = frame.resize(size, Image.LANCZOS)
                self.frames.append(ImageTk.PhotoImage(frame))
                self.gif.seek(i)
        except EOFError:
            pass
        self.idx = 0
        self.animate()

    def animate(self):
        if self.frames:
            self.label.config(image=self.frames[self.idx])
            self.label.image = self.frames[self.idx]
            self.idx = (self.idx + 1) % len(self.frames)
            self.label.after(10, self.animate)  # 100ms = 10fps

# Használat:
# refresh_icons[name] = tk.Label(frame, bg=None)
# refresh_icons[name].place(x=240, y=10)
# AnimatedGIF(refresh_icons[name], "refresh.gif")

root = tk.Tk()

# --- System tray funkció ---
def show_tray_icon():
    def on_show():
        icon.stop()
        root.after(0, root.deiconify)
    def on_exit():
        for name in processes:
            stop_script(name)
        icon.stop()
        root.after(0, root.destroy)
    image = Image.open("zalan.gif").resize((64, 64))
    icon = pystray.Icon("radio", image, "RÁDIÓVÁLASZTÓ", menu=pystray.Menu(
        pystray.MenuItem("Megjelenítés", on_show),
        pystray.MenuItem("Kilépés", on_exit)
    ))
    threading.Thread(target=icon.run, daemon=True).start()

def on_closing():
    for name in processes:
        stop_script(name)
    kill_all_customrp()
    root.withdraw()
    show_tray_icon()

file_paths = {

"CustomRP" : r"C:\Users\Pőtyögő\AppData\Roaming\CustomRP\CustomRP.exe",
"RockFM" : r"C:/Users/Pőtyögő/Documents/Discord/rockfm_2/rock_fm.py",
"BigRigFM" : r"C:/Users/Pőtyögő/Documents/Discord/bigrigfm/bigrigFM.py",
"TruckersFM" : r"C:/Users/Pőtyögő/Documents/Discord/truckersfm/truckersfm.py",
"Borsod Craft 2" : r"C:\Users\Pőtyögő\Documents\Discord\bmc 2 tps/import_requests_tps.py",
"RockFM HU" : r"C:\Users\Pőtyögő\Documents\Discord\rock_fm_hu/rock_fm_hu.py",
"Flask" : r"C:\Users\Pőtyögő\Documents\Discord\bmc 2 tps/flask.bat"
}


animated_gifs = {name: None for name in file_paths}

def open_file(path):
    if os.path.exists(path):
        os.startfile(path)
    else:
        messagebox.showerror("Hiba", f"A fájl nem található:\n{path}")

# ikonok
icon_on = ImageTk.PhotoImage(Image.open("icon_on.png").resize((40, 19)))
icon_off = ImageTk.PhotoImage(Image.open("icon_off.png").resize((40, 19)))
refresh_icon = ImageTk.PhotoImage(Image.open("refresh.gif").resize((20, 20)))

# folyamatok
processes = {
    "CustomRP": None,
    "RockFM": None,
    "BigRigFM": None,
    "TruckersFM": None,
    "Borsod Craft 2": None,
    "RockFM HU": None,
    "Flask": None
}

output_labels = {
    "CustomRP": None,
    "RockFM": None,
    "BigRigFM": None,
    "TruckersFM": None,
    "Borsod Craft 2": None,
    "RockFM HU": None,
    "Flask": None
}

status_icons = {
    "CustomRP": None,
    "RockFM": None,
    "BigRigFM": None,
    "TruckersFM": None,
    "Borsod Craft 2": None,
    "RockFM HU": None,
    "Flask": None
}

refresh_icons = {
    "CustomRP": None,
    "RockFM": None,
    "BigRigFM": None,
    "TruckersFM": None,
    "Borsod Craft 2": None,
    "RockFM HU": None,
    "Flask": None
}

def start_script(name, path):
    # Flask indítása, ha Borsod Craft 2-t indítunk
    if name == "Borsod Craft 2":
        # Flask csak egyszer induljon el!
        if processes.get("Flask") is None or processes["Flask"] is not None and processes["Flask"].poll() is not None:
            flask_path = file_paths["Flask"]
            flask_proc = subprocess.Popen(
                ["python", flask_path] if flask_path.endswith(".py") else [flask_path],
                stdout=subprocess.DEVNULL,  # Flask kimenet nem kell
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
                shell=True
            )
            processes["Flask"] = flask_proc

    # A fő script indítása (kimenetét mutatjuk)
    if processes[name] is None or processes[name].poll() is not None:
        proc = subprocess.Popen(
            ["python", path] if path.endswith(".py") else [path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",  # <-- EZ FONTOS!
            errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        processes[name] = proc
        status_icons[name].config(image=icon_on)
        threading.Thread(target=read_output, args=(name, proc), daemon=True).start()
    else:
        messagebox.showinfo("Info", f"{name} már fut!")


def stop_script(name):
    proc = processes.get(name)
    if proc and proc.poll() is None:
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except Exception:
            try:
                proc.kill()
                proc.wait(timeout=2)
            except Exception:
                # Utolsó esély: taskkill (csak Windows!)
                try:
                    os.system(f'taskkill /F /PID {proc.pid}')
                except Exception:
                    pass
        processes[name] = None
    # Flask leállítása, ha Borsod Craft 2-t állítjuk le
    if name == "Borsod Craft 2":
        flask_proc = processes.get("Flask")
        if flask_proc and flask_proc.poll() is None:
            flask_proc.terminate()
            processes["Flask"] = None

def read_output(name, proc):
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        # GUI frissítés főszálon
        root.after(0, update_output, name, line.strip())
    # Ha kilépett a script
    root.after(0, lambda: status_icons[name].config(image=icon_off))

def update_output(name, line):
    if "friss" in line.lower() or "újratölt" in line.lower():
        # Ha még nincs animáció, indítsd el
        if animated_gifs[name] is None:
            animated_gifs[name] = AnimatedGIF(refresh_icons[name], "refresh.gif", size=(32, 32))
    else:
        # Ha van animáció, tüntesd el
        if animated_gifs[name] is not None:
            refresh_icons[name].config(image="")
            refresh_icons[name].image = None
            animated_gifs[name] = None
    output_labels[name].config(text=line)


# --- Tkinter ablak ---
root.title("RÁDIÓVÁLASZTÓ - DESIGN CSONTOS")
root.geometry("700x500")
root.resizable(True, True)
root.protocol("WM_DELETE_WINDOW", on_closing)

# --- Füles (tabos) felület ---
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

for name in file_paths:
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=name)

    # HÁTTÉRKÉP minden tabra
    bg_img = Image.open("background.jpg").resize((700, 500))
    bg_photo = ImageTk.PhotoImage(bg_img)
    bg_label = tk.Label(frame, image=bg_photo)
    bg_label.image = bg_photo  # referenciát meg kell tartani!
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Vezérlők (a háttér fölé kerülnek)
    status_icons[name] = tk.Label(frame, image=icon_off, borderwidth=0, highlightthickness=0)
    status_icons[name].place(x=10, y=14)
    start_btn = tk.Button(frame, text=f"{name} indít", command=lambda n=name: start_script(n, file_paths[n]))
    start_btn.place(x=60, y=10, width=100, height=30)
    stop_btn = tk.Button(frame, text="Leállít", command=lambda n=name: stop_script(n), )
    stop_btn.place(x=170, y=10, width=80, height=30)
    refresh_icons[name] = tk.Label(frame,)
    refresh_icons[name].place(x=240, y=10)
    output_labels[name] = tk.Label(frame, text="", font=("Consolas", 10), bg=None, anchor="w", width=60, height=10, justify="left")
    output_labels[name].place(x=10, y=50)

root.mainloop() 