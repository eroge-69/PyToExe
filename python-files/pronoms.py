import tkinter as tk
from tkinter import messagebox
import random

pronouns = [
    ["я", "мій", "моя", "моє", "мої"],
    ["ти", "твій", "твоя", "твоє", "твої"],
    ["він", "його", "його", "його", "його"],
    ["вона", "її", "її", "її", "її"],
    ["воно", "його", "його", "його", "його"],
    ["ми", "наш", "наша", "наше", "наші"],
    ["ви", "ваш", "ваша", "ваше", "ваші"],
    ["вони", "їхній", "їхня", "їхнє", "їхні"],
]

translations = {
    "я": ("je", ""),
    "ти": ("tu", ""),
    "він": ("il", ""),
    "вона": ("elle", ""),
    "воно": ("il/elle (neutre)", "depend du genre du nom remplase"),
    "ми": ("nous", ""),
    "ви": ("vous", ""),
    "вони": ("ils/elles", "comme They anglais"),

    "мій": ("mon", "masculin"),
    "моя": ("ma", "feminin"),
    "моє": ("mon", "neutre"),
    "мої": ("mes", "pluriel"),

    "твій": ("ton", "masculin"),
    "твоя": ("ta", "feminin"),
    "твоє": ("ton", "neutre"),
    "твої": ("tes", "pluriel"),

    "його": ("son / sa / ses", "garçon qui a cet objet"),
    "її": ("son / sa / ses", "fille qui a cet objet"),

    "наш": ("notre", "masculin"),
    "наша": ("notre", "feminin"),
    "наше": ("notre", "neutre"),
    "наші": ("nos", "pluriel"),

    "ваш": ("votre", "masculin"),
    "ваша": ("votre", "feminin"),
    "ваше": ("votre", "neutre"),
    "ваші": ("vos", "pluriel"),

    "їхній": ("leur", "masculin"),
    "їхня": ("leur", "feminin"),
    "їхнє": ("leur", "neutre"),
    "їхні": ("leurs", "pluriel"),
}


# === FLASHCARDS ===
# === FLASHCARDS ===
class Flashcards:
    def __init__(self, master):
        self.window = tk.Toplevel(master)
        self.window.title("Flashcards")
        self.window.geometry("700x400+50+150")
        self.window.configure(bg="green")

        self.words = list(translations.keys())
        random.shuffle(self.words)
        self.index = 0
        self.showing_translation = False

        # Контейнер-картка
        self.card_frame = tk.Frame(
            self.window, 
            bg="white", 
            highlightbackground="black", 
            highlightthickness=2, 
            width=400, 
            height=200
        )
        self.card_frame.pack(pady=40, expand=True)
        self.card_frame.pack_propagate(False)

        # Текст на картці
        self.card_label = tk.Label(
            self.card_frame, 
            text="", 
            font=("Arial", 28, "bold"), 
            bg="white", 
            wraplength=350
        )
        self.card_label.pack(expand=True)

        # Підпис з поясненням
        self.hint_label = tk.Label(
            self.window, 
            text="👉 Appuie sur la carte pour voir la trduction ou pour continuer", 
            font=("Arial", 12), 
            bg="white", 
            fg="gray"
        )
        self.hint_label.pack(pady=10)

        self.next_card()

        # Клік по всій картці
        self.card_frame.bind("<Button-1>", self.flip_card)
        self.card_label.bind("<Button-1>", self.flip_card)  # дублюємо, щоб спрацьовувало і по тексту

    def next_card(self):
        if self.index >= len(self.words):
            self.card_label.config(text="Кінець 🎉")
            return

        self.current_word = self.words[self.index]
        self.card_label.config(text=self.current_word)
        self.showing_translation = False

    def flip_card(self, event):
        if not self.showing_translation:
            fr, note = translations[self.current_word]
            text = f"{self.current_word} → {fr}"
            if note:
                text += f"\n({note})"
            self.card_label.config(text=text)
            self.showing_translation = True
        else:
            self.index += 1
            self.next_card()


# === ВІКНО З ТАБЛИЦЕЮ ===
def show_translation(word):
    if word in translations:
        fr, note = translations[word]
        text = f"{word} → {fr}"
        if note:
            text += f"\n\nExplication: {note}"
        messagebox.showinfo("Traduction", text)


def open_clavier():
    win = tk.Toplevel()
    win.title("Clavier — pronoms")
    win.geometry("700x400+50+150")
    win.configure(bg="white")

    headers = ["Personne", "Pos. (mas.)", "Pos. (fem.)", "Pos. (neu.)", "Pos. (plu.)"]

    for j, h in enumerate(headers):
        lbl = tk.Label(win, text=h, font=("Arial", 12, "bold"), bg="#d6eaf8", relief="ridge", width=18)
        lbl.grid(row=0, column=j, sticky="nsew")

    for i, row in enumerate(pronouns, start=1):
        for j, word in enumerate(row):
            btn = tk.Button(win, text=word, width=18, command=lambda w=word: show_translation(w))
            btn.grid(row=i, column=j, sticky="nsew")

    for j in range(len(headers)):
        win.grid_columnconfigure(j, weight=1)

def play_game(master):
    win = tk.Toplevel(master)
    win.title("Jeu — Devine un chiffre")
    win.geometry("700x400+50+150")
    win.configure(bg="yellow")

    instruction = tk.Label(win, text="Devine un chiffre entre 1 et 5", font=("Arial", 14), bg="#fff")
    instruction.pack(pady=20)

    result_label = tk.Label(win, text="", font=("Arial", 12), bg="#fff")
    result_label.pack(pady=10)

    # Контейнер для кнопок
    buttons_frame = tk.Frame(win, bg="#fff")
    buttons_frame.pack(pady=10)

    def check_guess(guess):
        secret = random.randint(1, 5)
        if guess == secret:
            result_label.config(text=f"🎉 Tu as gagne! j'ai pense a {secret}")
        else:
            result_label.config(text=f"😢 Tu as perdu car c'etait {secret}")

        # Показуємо випадковий займенник з шансом 1/2
        if random.random() < 0.5:
            word = random.choice(list(translations.keys()))
            fr, note = translations[word]
            msg = f"Maintenant n'oublie pas que:\n{word} → {fr}"
            if note:
                msg += f"\n({note})"
            messagebox.showinfo("Pronom", msg)

    # Створюємо кнопки від 1 до 5
    for i in range(1, 6):
        btn = tk.Button(buttons_frame, text=str(i), font=("Arial", 14), width=5, 
                        command=lambda n=i: check_guess(n), bg="#85c1e9", fg="white")
        btn.grid(row=0, column=i-1, padx=5, pady=5)
        
# === ГОЛОВНЕ ВІКНО ===
def main():
    root = tk.Tk()
    root.title("Pronoms")
    root.geometry("500x400+600+100")
    root.configure(bg="#f0f8ff")

    label = tk.Label(root, text="pronoms", font=("Arial", 28, "bold"), bg="#f0f8ff", fg="#2e4053")
    label.pack(pady=40)

    btn1 = tk.Button(root, text="clavier", font=("Arial", 16), width=20, bg="#85c1e9", fg="white",
                     activebackground="#2874a6", command=open_clavier)
    btn1.pack(pady=10)

    btn2 = tk.Button(root, text="flashcards", font=("Arial", 16), width=20, bg="#58d68d", fg="white",
                     activebackground="#1d8348", command=lambda: Flashcards(root))
    btn2.pack(pady=10)

    btn3 = tk.Button(root, text="jeu", font=("Arial", 16), width=20, bg="#f5b041", fg="white",
                 activebackground="#ca6f1e", command=lambda: play_game(root))
    btn3.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
