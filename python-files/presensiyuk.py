import tkinter as tk
from datetime import datetime

PESAN = "Jangan lupa presensi pakai HP!"
UKURAN_JENDELA = (360, 140)

def main():
    root = tk.Tk()
    root.title("Pengingat Presensi")
    root.geometry(f"{UKURAN_JENDELA[0]}x{UKURAN_JENDELA[1]}")
    root.resizable(False, False)
    root.attributes('-topmost', True)

    # posisi tengah layar
    root.update_idletasks()
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    x, y = (sw - UKURAN_JENDELA[0]) // 2, (sh - UKURAN_JENDELA[1]) // 3
    root.geometry(f"{UKURAN_JENDELA[0]}x{UKURAN_JENDELA[1]}+{x}+{y}")

    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(frame, text=PESAN, font=("Segoe UI", 14, "bold")).pack(pady=(0, 10))
    tk.Label(frame, text="Sekarang: " + datetime.now().strftime('%H:%M')).pack()

    tk.Button(frame, text="OK", width=10, command=root.destroy).pack(pady=15)

    try:
        root.bell()
    except Exception:
        pass

    root.mainloop()

if __name__ == "__main__":
    main()
