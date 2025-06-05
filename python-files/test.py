import tkinter as tk
import random


def baslangic():
    for widget in pencere.winfo_children():
        widget.destroy()

    global etiket
    etiket = tk.Label(pencere, text="are u gae?", font=("Arial", 14))
    etiket.pack(side="top", pady=50)

    global initial_x, initial_y
    initial_x = 30
    initial_y = 170

    global hayir_buton
    hayir_buton = tk.Button(
        pencere,
        text="hayır",
        bg="gray",
        fg="white",
        width=10
    )
    hayir_buton.place(x=initial_x, y=initial_y)
    hayir_buton.bind("<Enter>", tasin)

    global evet_buton
    evet_buton = tk.Button(
        pencere,
        text="evet",
        bg="gray",
        fg="white",
        width=10,
        command=evet_tikla
    )
    evet_buton.place(x=evet_x, y=evet_y)

def is_cakisma(x1, y1, w1, h1, x2, y2, w2, h2):
    return not (x1 + w1 < x2 or x1 > x2 + w2 or y1 + h1 < y2 or y1 > y2 + h2)

def tasin(event):
    max_x = win_width - button_width_px
    max_y = win_height - button_height_px
    while True:
        yeni_x = random.randint(0, max_x)
        yeni_y = random.randint(50, max_y)
        if (not is_cakisma(yeni_x, yeni_y, button_width_px, button_height_px, evet_x, evet_y, evet_width, evet_height) and
            not is_cakisma(yeni_x, yeni_y, button_width_px, button_height_px, metin_x, metin_y, metin_width, metin_height)):
            break
    hayir_buton.place(x=yeni_x, y=yeni_y)

def evet_tikla():
    for widget in pencere.winfo_children():
        widget.destroy()
    tebrik_etiket = tk.Label(pencere, text="congratulations", font=("Arial", 24, "bold"), fg="blue")
    # Alt boşluğu azaltarak yazıyı biraz yukarı taşıyoruz
    tebrik_etiket.pack(expand=True, pady=(10,5))

    tekrar_buton = tk.Button(
        pencere,
        text="testi tekrar başlat",
        bg="gray",
        fg="white",
        width=15,
        command=baslangic
    )
    # Üst ve alt boşlukları çok küçük yapıyoruz, böylece buton yazıya yakın olur
    tekrar_buton.pack(pady=(0,10))

pencere = tk.Tk()
pencere.title(" gae test game.jpg.mp4.pkk")
pencere.geometry("300x300")

win_width = 300
win_height = 300

button_width_px = 10 * 7
button_height_px = 30

evet_x = 180
evet_y = 170
evet_width = button_width_px
evet_height = button_height_px

metin_x = 0
metin_y = 50
metin_width = win_width
metin_height = 40

baslangic()

pencere.mainloop()
