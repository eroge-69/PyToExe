import subprocess
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

# Spustí příkaz a získá jeho výstup
result = subprocess.run('netsh wlan show profiles', shell=True, capture_output=True, text=True)

# Vytvoří okno s výstupem
root = tk.Tk()
root.title('Výpis WiFi profilů')
root.geometry('700x400')

text_area = ScrolledText(root, wrap=tk.WORD, font=("Consolas", 10))
text_area.pack(expand=True, fill='both')
text_area.insert('1.0', result.stdout)
text_area.configure(state='disabled')

root.mainloop() 