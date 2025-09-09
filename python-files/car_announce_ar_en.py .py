import asyncio
import os
import tempfile
import threading
import tkinter as tk
from tkinter import ttk, messagebox

import edge_tts
from playsound import playsound

APP_TITLE = "Car Announcement (Arabic → English)"

# ---- Build the two messages ----
def build_messages(name: str, plate: str):
    name = name.strip()
    plate = plate.strip()

    # Arabic (Iraq-friendly)
    ar = (
        f"السيارة {name}، رقم اللوحة {plate}، "
        f"سيارتك قفلتس سيارات أخرى في الكراج. "
        f"يرجى نقل سيارتك إلى مكان اخر. شكراً ."
    )

    # English
    en = (
        f"Car {name}, plate number {plate}, your car has blocked other cars in the garage. "
        f"Please move your car to a better place. Thank you."
    )
    return ar, en

# ---- Voice helpers (pick a good voice automatically) ----
async def pick_voice(locale_prefs):
    """Return an Azure/Edge TTS voice ShortName that matches the first available locale."""
    try:
        vm = await edge_tts.VoicesManager.create()
        voices = vm.voices
        # Prefer Neural voices
        for pref in locale_prefs:
            for v in voices:
                if v.get("Locale","").startswith(pref) and "Neural" in v.get("ShortName",""):
                    return v["ShortName"]
        # Fallback: any matching locale
        for pref in locale_prefs:
            for v in voices:
                if v.get("Locale","").startswith(pref):
                    return v["ShortName"]
        # Last resort: English US
        for v in voices:
            if v.get("Locale","").startswith("en-US") and "Neural" in v.get("ShortName",""):
                return v["ShortName"]
        return "en-US-AriaNeural"
    except Exception:
        return "en-US-AriaNeural"

async def tts_to_file(text: str, voice_short_name: str, outfile: str):
    await edge_tts.Communicate(text=text, voice=voice_short_name).save(outfile)

def play(path: str):
    playsound(path)

# ---- Worker that runs in a background thread ----
def speak_sequence(name: str, plate: str, status: tk.StringVar, btn: ttk.Button):
    try:
        status.set("Preparing messages…")
        ar_msg, en_msg = build_messages(name, plate)
        tmp_files = []

        async def synth_all():
            status.set("Selecting Arabic voice…")
            ar_voice = await pick_voice(["ar-IQ", "ar-SA", "ar-EG", "ar"])
            fd1, ar_mp3 = tempfile.mkstemp(suffix=".mp3", prefix="ar_"); os.close(fd1)
            await tts_to_file(ar_msg, ar_voice, ar_mp3)
            tmp_files.append(("Arabic", ar_mp3))

            status.set("Selecting English voice…")
            en_voice = await pick_voice(["en-US", "en-GB", "en"])
            fd2, en_mp3 = tempfile.mkstemp(suffix=".mp3", prefix="en_"); os.close(fd2)
            await tts_to_file(en_msg, en_voice, en_mp3)
            tmp_files.append(("English", en_mp3))

        asyncio.run(synth_all())

        # Play Arabic then English
        for label, path in tmp_files:
            status.set(f"Playing: {label}")
            play(path)

        status.set("Done ✔")
    except Exception as e:
        messagebox.showerror("Error", f"{e}")
        status.set("Error")
    finally:
        btn.config(state=tk.NORMAL)

# ---- Simple Tkinter UI ----
def main():
    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry("560x300")

    frm = ttk.Frame(root, padding=16)
    frm.pack(fill="both", expand=True)

    ttk.Label(frm, text=APP_TITLE, font=("Segoe UI", 14, "bold")).pack(pady=(0,12))

    row1 = ttk.Frame(frm); row1.pack(fill="x", pady=6)
    ttk.Label(row1, text="Car name / type:").grid(row=0, column=0, sticky="w", padx=(0,8))
    name_var = tk.StringVar()
    ttk.Entry(row1, textvariable=name_var).grid(row=0, column=1, sticky="ew")
    row1.columnconfigure(1, weight=1)

    row2 = ttk.Frame(frm); row2.pack(fill="x", pady=6)
    ttk.Label(row2, text="Plate number:").grid(row=0, column=0, sticky="w", padx=(0,8))
    plate_var = tk.StringVar()
    ttk.Entry(row2, textvariable=plate_var).grid(row=0, column=1, sticky="ew")
    row2.columnconfigure(1, weight=1)

    status = tk.StringVar(value="Ready")
    ttk.Label(frm, textvariable=status, foreground="#0a6").pack(anchor="w", pady=8)

    def on_go():
        n, p = name_var.get().strip(), plate_var.get().strip()
        if not n or not p:
            messagebox.showwarning("Missing info", "Please enter both car name and plate number.")
            return
        btn.config(state=tk.DISABLED)
        threading.Thread(target=speak_sequence, args=(n, p, status, btn), daemon=True).start()

    btn = ttk.Button(frm, text="Announce (Arabic → English)", command=on_go)
    btn.pack(pady=10)

    note = ("Notes:\n"
            "• Uses Microsoft Edge online neural voices via edge-tts (requires internet).\n"
            "• The app auto-picks an Arabic (ar-IQ/SA/EG) voice and an English (en-US/GB) voice.")
    ttk.Label(frm, text=note, justify="left", wraplength=520).pack(anchor="w", pady=(6,0))

    root.mainloop()

if __name__ == "__main__":
    main()
