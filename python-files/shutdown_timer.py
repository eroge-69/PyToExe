#!/usr/bin/env python
# -*- coding: utf8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os

def is_admin():
    """Cek sudah run as Administrator?"""
    try:
        return os.getuid() == 0
    except AttributeError:
        return subprocess.run(
            ["net", "session"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        ).returncode == 0

def schedule_shutdown(minutes: int):
    """Jalankan shutdown /s /t <detik>"""
    if minutes <= 0:
        messagebox.showerror("Error", "Waktu harus lebih dari 0 menit!")
        return
    detik = int(minutes * 60)
    try:
        subprocess.run(["shutdown", "/s", "/t", str(detik)], check=True)
        messagebox.showinfo(
            "Sukses",
            f"Komputer akan dimatikan dalam {minutes} menit.\n\n"
            "Gunakan tombol Batal untuk membatalkan.",
        )
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Gagal", f"Shutdown gagal:\n{e}\n\nCoba Run as Administrator.")

def cancel_shutdown():
    """Batalkan shutdown"""
    try:
        subprocess.run(["shutdown", "/a"], check=True)
        messagebox.showinfo("Sukses", "Jadwal shutdown dibatalkan.")
    except subprocess.CalledProcessError:
        messagebox.showinfo("Info", "Tidak ada jadwal shutdown yg aktif.")

def build_gui():
    root = tk.Tk()
    root.title("Shutdown Timer – Windows 10/11")
    root.geometry("380x220")
    root.resizable(False, False)

    ttk.Label(root, text="Jadwalkan shutdown dalam", font=("Segoe UI", 12)).pack(pady=12)

    spin = ttk.Spinbox(root, from_=1, to=720, width=10, font=("Segoe UI", 11))
    spin.set(30)  # default 30 menit
    spin.pack()

    ttk.Label(root, text="menit", font=("Segoe UI", 10)).pack()

    btn_bar = ttk.Frame(root)
    btn_bar.pack(pady=20)

    ttk.Button(
        btn_bar,
        text="OK – Jadwalkan Shutdown",
        command=lambda: schedule_shutdown(int(spin.get())),
    ).pack(side="left", padx=8)

    ttk.Button(btn_bar, text="Batal", command=cancel_shutdown).pack(side="left", padx=8)

    status = ttk.Label(root, text="Tips: Jalankan sebagai Administrator jika gagal.", foreground="gray")
    status.pack(side="bottom", pady=6)

    root.mainloop()

if __name__ == "__main__":
    if not is_admin():
        # Opsional: otomatis UAC-elevation
        script = os.path.abspath(sys.argv[0])
        proc = subprocess.run(
            ["powershell", "-Command", f"Start-Process python -ArgumentList '\"{script}\"' -Verb RunAs"],
            capture_output=True,
        )
        sys.exit()
    build_gui()