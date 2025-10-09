import customtkinter as ctk
import tkinter as tk
from bs4 import BeautifulSoup
import requests
from PIL import Image

# ===== تنظیم تم اولیه =====
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("manimvf.com")
root.geometry("500x400")
root.resizable(False, False)

# ===== عنوان صفحه اصلی =====
title_label = ctk.CTkLabel(root, text="Home Page",
                           font=ctk.CTkFont(size=15, weight="bold"))
title_label.pack(pady=20)

# ===== بارگذاری عکس برای دکمه‌ها =====
img = ctk.CTkImage(light_image=Image.open("سکه.png"),
                   dark_image=Image.open("سکه.png"), size=(180, 220))
img1 = ctk.CTkImage(light_image=Image.open("ui.png"),
                    dark_image=Image.open("ui.png"), size=(180, 220))

# ===== صفحه دوم/سوم =====
label = tk.Label(root, text="", font=("kalameh", 20),
                 justify="center", anchor="center", bg="#1f1f1f", fg="white")
back_button = ctk.CTkButton(root, text="back", width=180, height=60,
                            fg_color="#555555", hover_color="#777777")

# ===== انیمیشن کلیک =====


def button_click_animation(btn, callback):
    original_width = btn.cget("width")
    original_height = btn.cget("height")

    btn.configure(width=int(original_width * 0.9),
                  height=int(original_height * 0.9))
    root.update()

    def reset_button():
        btn.configure(width=original_width, height=original_height)
        root.update()
        callback()

    root.after(100, reset_button)

# ===== بازگشت به صفحه اصلی =====


def go_home():
    button_click_animation(back_button, lambda: [
        label.pack_forget(),
        back_button.place_forget(),
        title_label.pack(pady=20),
        dollar_button.pack(side="left", padx=20, pady=50),
        gold_button.pack(side="right", padx=20, pady=50),
        theme_switch.pack(pady=(0, 10))  # ✅ برگرداندن سوئیچ
    ])


back_button.configure(command=go_home)

# ===== توابع گرفتن نرخ =====


def get_dollar_rate():
    url = "https://www.tgju.org/profile/price_dollar_rl"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    text = None
    for h3 in soup.find_all("h3"):
        if "نرخ فعلی" in h3.get_text():
            text = h3.get_text()
            break
    return text or "هیچی پیدا نشد 😐"


def get_gold_rate():
    url = "https://www.tgju.org/profile/sekee"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    text = None
    for h3 in soup.find_all("h3"):
        if "نرخ فعلی" in h3.get_text():
            text = h3.get_text()
            break
    return text or "هیچی پیدا نشد 😐"

# ===== نمایش صفحه دلار =====


def show_dollar():
    title_label.pack_forget()
    dollar_button.pack_forget()
    gold_button.pack_forget()
    theme_switch.pack_forget()  # ✅ مخفی کردن سوئیچ

    text = get_dollar_rate()
    label.configure(text=text)
    label.pack(pady=20, fill="both")
    back_button.place(x=160, y=300)
    back_button.lift()

# ===== نمایش صفحه طلا =====


def show_gold():
    title_label.pack_forget()
    dollar_button.pack_forget()
    gold_button.pack_forget()
    theme_switch.pack_forget()  # ✅ مخفی کردن سوئیچ

    text = get_gold_rate()
    label.configure(text=text)
    label.pack(pady=20, fill="both")
    back_button.place(x=160, y=300)
    back_button.lift()


# ===== دکمه‌های اصلی کنار هم =====
dollar_button = ctk.CTkButton(root, image=img1, text="", command=show_dollar,
                              fg_color="transparent", hover_color="#333333", width=140, height=160)
gold_button = ctk.CTkButton(root, image=img, text="", command=show_gold,
                            fg_color="transparent", hover_color="#333333", width=140, height=160)

dollar_button.pack(side="left", padx=15, pady=50)
gold_button.pack(side="right", padx=20, pady=50)

# ===== ✅ سوئیچ تغییر تم =====


def toggle_theme():
    current = ctk.get_appearance_mode().lower()
    if current == "dark":
        ctk.set_appearance_mode("light")
        theme_switch.configure(text_color="black")  # متن مشکی در حالت روشن
    else:
        ctk.set_appearance_mode("dark")
        theme_switch.configure(text_color="white")  # متن سفید در حالت تیره


theme_switch = ctk.CTkSwitch(
    root,
    text="🌓 تغییر حالت تم",
    text_color="white",
    font=ctk.CTkFont(size=14),  # افزایش سایز متن
    command=toggle_theme
)
theme_switch.pack(pady=(10, 20))


root.mainloop()
