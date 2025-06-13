import tkinter as tk
import subprocess
import os

def close_window():
    MainGUI.destroy()

def open_in_chrome():
    url = "https://login.siemens.com/u/login/identifier?state=hKFo2SBvdnFCZnRVZ2xFVmxJUzYwSnpmQXZxa2FMVERGMmJWdaFur3VuaXZlcnNhbC1sb2dpbqN0aWTZIGh5b1plSGdURWJMbWdTREZ3Z1h1TlNicm1Femd5MVd4o2NpZNkgM1BoWXkwaHVQbEdVWTNqZnA5OThOdzJuS25vR21VTGU"  # Deine URL
    chrome_path = "C:\\Programme\\Google\\Chrome\\Application\\chrome.exe"
    
    if os.path.exists(chrome_path):
        subprocess.Popen([chrome_path, "--new-window", url])
        status_label.config(text="")  # Eventuell vorhandene Fehlermeldung leeren
        close_window()
    else:
        status_label.config(text="Chrome wurde nicht gefunden!", fg="red")

MainGUI = tk.Tk()
MainGUI.title("GUI V02")
window_width = 300
window_height = 200  # leicht erhöht wegen Label

# Bildschirmgröße ermitteln
screen_width = MainGUI.winfo_screenwidth()
screen_height = MainGUI.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
MainGUI.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Buttons
open_button = tk.Button(MainGUI, text="Einloggen", command=open_in_chrome)
open_button.pack(pady=30)

# Statuslabel
status_label = tk.Label(MainGUI, text="", fg="red")
status_label.pack(pady=5)

MainGUI.mainloop()

