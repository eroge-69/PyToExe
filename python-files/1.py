import sys
import os
import tkinter as tk
import subprocess
from datetime import datetime

# Скрываем консольное окно
if sys.executable.endswith("pythonw.exe"):
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.path.join(os.getenv("TEMP"), "stderr-" + os.path.basename(sys.argv[0])), "w")

# ===================== НАСТРОЙКИ =====================
PATHS = {
    1: {'shortcut': r"C:\Script\1 ZAL.lnk", 'script': r"C:\Scripts\run_macro1zal.ps1"},
    2: {'shortcut': r"C:\Script\2 ZAL.lnk", 'script': r"C:\Scripts\run_macro.ps1"},
    3: {'shortcut': r"C:\Script\3 ZAL.lnk", 'script': r"C:\Scripts\run_macro3zal.ps1"}
}

VNC_PATH = r"C:\Program Files\RealVNC\VNC Viewer\vncviewer.exe"
VNC_SERVER = "192.168.1.100"
LOG_FILE = r"C:\Scripts\zal_log.txt"

# ===================== ОСТАЛЬНОЙ КОД БЕЗ ИЗМЕНЕНИЙ =====================
# ... (все ваши функции run_script, run_vnc и другие остаются точно такими же)
# ... (кроме блока запуска в конце)

if __name__ == "__main__":
    try:
        window = tk.Tk()
        window.title("Управление залами")
        window.geometry("600x400")
        window.configure(bg="#f0f0f0")

        button_style = {
            'font': ('Arial', 12),
            'width': 20,
            'height': 2,
            'borderwidth': 3
        }

        buttons = {
            1: tk.Button(window, text="ЗАЛ 1", command=lambda: run_script(1), bg="#4CAF50", fg="white", **button_style),
            2: tk.Button(window, text="ЗАЛ 2", command=lambda: run_script(2), bg="#2196F3", fg="white", **button_style),
            3: tk.Button(window, text="ЗАЛ 3", command=lambda: run_script(3), bg="#FF9800", fg="white", **button_style),
            4: tk.Button(window, text="ЗАЛ 4", command=run_vnc, bg="#9C27B0", fg="white", **button_style)
        }

        for btn in buttons.values():
            btn.pack(pady=10)

        window.mainloop()

    except Exception as e:
        with open(os.path.join(os.getenv("TEMP"), "cinema_error.log"), "a") as f:
            f.write(f"{datetime.now()}: {str(e)}\n")