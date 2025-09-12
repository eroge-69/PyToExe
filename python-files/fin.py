import tkinter as tk
from tkinter import messagebox
import webbrowser

SOCIAL_LINKS = {
    "YouTube": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "Instagram": "https://www.instagram.com/reel/CxL2XlPMrGA/",
    "Telegram": "https://t.me/rickroll_ru/5",
    "TikTok": "https://www.tiktok.com/@user1234567890/video/7213456789012345678",
    "VK": "https://vk.com/video?q=never+gonna+give+you+up&z=video123456789_456789012"
}

FINAL_MESSAGE = "Ты что, серьёзно подумала, что это реальность?\n\nЭто же пранк был 😼"

def start_paran():
    selected = listbox.curselection()
    if not selected:
        messagebox.showwarning("Подожди!", "Выбери свою соцсеть, чтобы продолжить!")
        return

    social = listbox.get(selected[0])
    chosen_url = SOCIAL_LINKS.get(social)

    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg="#000")

    loading = tk.Label(
        root,
        text=f"ЗАПУСКАЕМ В {social.upper()}...",
        font=("Courier", 14, "bold"),
        fg="#0f0",
        bg="#000"
    )
    loading.pack(pady=100)

    root.after(1500, lambda: webbrowser.open(chosen_url))
    root.after(2500, show_final_choice)

def show_final_choice():
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg="#1a1a1a")

    tk.Label(
        root,
        text="ПРАНК ЗАВЕРШЁН",
        font=("Courier", 16, "bold"),
        fg="#f00",
        bg="#1a1a1a"
    ).pack(pady=20)

    tk.Label(
        root,
        text=FINAL_MESSAGE,
        font=("Courier", 10),
        fg="#0f0",
        bg="#1a1a1a",
        justify="center",
        wraplength=400
    ).pack(pady=20)

    btn_frame = tk.Frame(root, bg="#1a1a1a")
    btn_frame.pack(pady=30)

    def exit_app():
        root.destroy()

    def stay_and_watch():
        webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        messagebox.showinfo("🎵", "Ты выбрал путь легенды…")
        root.destroy()

    tk.Button(
        btn_frame,
        text="Выйти",
        font=("Courier", 12, "bold"),
        bg="#f00",
        fg="#fff",
        command=exit_app,
        width=10,
        height=2
    ).pack(side="left", padx=20)

    tk.Button(
        btn_frame,
        text="Остаться",
        font=("Courier", 12, "bold"),
        bg="#00f",
        fg="#fff",
        command=stay_and_watch,
        width=10,
        height=2
    ).pack(side="right", padx=20)

    tk.Label(
        root,
        text="© Mixercaty.exe | Кот-хакер Корней, 2025",
        font=("Courier", 8),
        fg="#555",
        bg="#1a1a1a"
    ).pack(side="bottom", pady=10)

root = tk.Tk()
root.title("Выбор соцсети")
root.geometry("500x600")
root.resizable(False, False)
root.configure(bg="#1a1a1a")

title = tk.Label(
    root,
    text="СИСТЕМА ОПРЕДЕЛЕНИЯ",
    font=("Courier", 14, "bold"),
    fg="#00ff00",
    bg="#1a1a1a"
)
title.pack(pady=20)

subtitle = tk.Label(
    root,
    text="На какой платформе ты живёшь?",
    font=("Courier", 10),
    fg="#888",
    bg="#1a1a1a"
)
subtitle.pack(pady=5)

listbox = tk.Listbox(
    root,
    font=("Courier", 12),
    bg="#2a2a2a",
    fg="#00ff00",
    selectbackground="#00cc00",
    selectforeground="#000",
    height=5,
    width=30,
    justify="center"
)
for network in SOCIAL_LINKS.keys():
    listbox.insert(tk.END, network)
listbox.pack(pady=50)

btn = tk.Button(
    root,
    text="НАЧАТЬ",
    font=("Courier", 12, "bold"),
    bg="#00ff00",
    fg="#000",
    activebackground="#00cc00",
    command=start_paran,
    width=20,
    height=2
)
btn.pack(pady=10)

root.mainloop()
