import tkinter as tk
from tkinter import messagebox

BG_COLOR = "#222831"
WIDGET_BG = "#393e46"
FG_COLOR = "#eeeeee"
BAR_BG = "#393e46"
BAR_FILL = "#00adb5"

def start_zadani_okno():
    zadani_okno = tk.Tk()
    zadani_okno.title("Zadej svůj věk")
    zadani_okno.configure(bg=BG_COLOR)
    zadani_okno.geometry("350x200")
    zadani_okno.eval('tk::PlaceWindow . center')

    label = tk.Label(zadani_okno, text="Zadej svůj věk:", bg=BG_COLOR, fg=FG_COLOR, font=("Segoe UI", 12))
    label.pack(pady=10)

    entry = tk.Entry(zadani_okno, bg=WIDGET_BG, fg=FG_COLOR, insertbackground=FG_COLOR, font=("Segoe UI", 12))
    entry.pack(pady=10)

    def potvrdit():
        vek = entry.get()
        if not vek.isdigit():
            messagebox.showwarning("Chyba", "Zadej prosím číslo.")
            return
        zadani_okno.destroy()
        start_nacitani_okno(vek)

    button = tk.Button(
        zadani_okno,
        text="Potvrdit",
        command=potvrdit,
        bg=WIDGET_BG,
        fg=FG_COLOR,
        font=("Segoe UI", 12, "bold"),
        activebackground="#00adb5",
        activeforeground=FG_COLOR
    )
    button.pack(pady=20)

    zadani_okno.mainloop()

def start_nacitani_okno(vek):
    nacitani_okno = tk.Tk()
    nacitani_okno.title("Načítání")
    nacitani_okno.configure(bg=BG_COLOR)
    nacitani_okno.geometry("350x150")
    nacitani_okno.eval('tk::PlaceWindow . center')

    loading_label = tk.Label(nacitani_okno, text="Načítání...", bg=BG_COLOR, fg="#00adb5", font=("Segoe UI", 12, "italic"))
    loading_label.pack(pady=10)

    bar_canvas = tk.Canvas(nacitani_okno, width=300, height=20, bg=BAR_BG, highlightthickness=0)
    bar_canvas.pack(pady=10)

    def animate_bar(step=0):
        total_steps = 20
        bar_canvas.delete("bar")
        fill_width = int((step / total_steps) * 300)
        bar_canvas.create_rectangle(0, 0, fill_width, 20, fill=BAR_FILL, width=0, tags="bar")
        if step < total_steps:
            nacitani_okno.after(250, lambda: animate_bar(step + 1))
        else:
            nacitani_okno.destroy()
            start_vysledek_okno(vek)

    animate_bar()
    nacitani_okno.mainloop()

def start_vysledek_okno(vek):
    vysledek_okno = tk.Tk()
    vysledek_okno.title("Výsledek")
    vysledek_okno.configure(bg=BG_COLOR)
    vysledek_okno.geometry("350x200")
    vysledek_okno.eval('tk::PlaceWindow . center')
    vysledek_label = tk.Label(
        vysledek_okno,
        text=f"Tvůj věk je {vek}",
        bg=BG_COLOR,
        fg=FG_COLOR,
        font=("Segoe UI", 16, "bold")
    )
    vysledek_label.pack(pady=40)
    vysledek_okno.mainloop()

# Spusť aplikaci
start_zadani_okno()