#!/usr/bin/env python3
# Word Definition Quiz Game v4
# Přidané funkce:
# - Vylepšené menu (větší a přehlednější)
# - Leaderboard (žebříček časů z hry "Spojování")
# - Nová hra "Šibenice" (Hangman)

import tkinter as tk
from tkinter import messagebox
import random, time, os

WORD_DEFS = [
    ("happening", "an event; something taking place"),
    ("right now", "at this moment; currently"),
    ("country", "a nation; a land"),
    ("parts", "pieces; sections; components"),
    ("getting up", "rising from bed; waking up"),
    ("getting married", "becoming husband and wife"),
    ("introduction", "the beginning; a presentation"),
    ("compare", "to find similarities/differences"),
    ("discuss", "to talk about; debate"),
    ("statistic", "numerical data; a figure"),
    ("idea", "a thought; concept; plan"),
    ("nearly", "almost"),
    ("worldwide", "global; everywhere in the world"),
    ("marriage", "the legal union of two people"),
    ("couple", "two people together; pair"),
    ("average", "typical; the mean number"),
    ("employ", "to give work; hire"),
    ("rubbish", "trash; garbage; waste"),
    ("lightning", "a flash of electricity in the sky"),
    ("strike", "to hit; or workers' protest"),
    ("extinct", "no longer existing (e.g., species)"),
    ("surprised", "amazed; shocked; astonished"),
    ("reason", "cause; explanation"),
    ("unfair", "unjust; not equal"),
    ("waste", "to use badly; also: rubbish"),
    ("almost", "nearly"),
    ("seem", "to appear; give the impression"),
    ("soundly", "deeply or firmly (e.g., sleep soundly)"),
    ("download", "to transfer data from the internet to a device"),
]

SCORES_FILE = "scores.txt"
TITLE = "Kvíz se slovíčky v4"

class QuizGame:
    def __init__(self, master):
        self.master = master
        master.title(TITLE)
        master.resizable(False, False)
        self.frame = tk.Frame(master, padx=20, pady=20)
        self.frame.pack()
        self.show_menu()

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def show_menu(self):
        self.clear_frame()
        lbl = tk.Label(self.frame, text=TITLE, font=("Helvetica", 18, "bold"), fg="navy")
        lbl.pack(pady=15)
        tk.Button(self.frame, text="Definice ➝ Slovo", width=30, height=2, command=lambda: self.start_quiz(mode="def2word")).pack(pady=5)
        tk.Button(self.frame, text="Slovo ➝ Definice", width=30, height=2, command=lambda: self.start_quiz(mode="word2def")).pack(pady=5)
        tk.Button(self.frame, text="Učení (flashcards)", width=30, height=2, command=lambda: self.start_flashcards()).pack(pady=5)
        tk.Button(self.frame, text="Hra (spojování)", width=30, height=2, command=lambda: self.start_matchgame()).pack(pady=5)
        tk.Button(self.frame, text="Šibenice", width=30, height=2, command=self.start_hangman).pack(pady=5)
        tk.Button(self.frame, text="Žebříček", width=30, height=2, command=self.show_leaderboard).pack(pady=10)

    # ====== QUIZ MODES ======
    def start_quiz(self, mode="def2word"):
        self.clear_frame()
        self.mode = mode
        self.total_questions = 10
        self.score = 0
        self.q_number = 0

        self.def_text = tk.StringVar()
        self.lbl_def = tk.Label(self.frame, textvariable=self.def_text, wraplength=400, font=("Helvetica", 12))
        self.lbl_def.pack(pady=(0,12))

        self.buttons = []
        for i in range(4):
            b = tk.Button(self.frame, text=f"Option {i+1}", width=40, command=lambda i=i: self.check_answer(i))
            b.pack(pady=3)
            self.buttons.append(b)

        self.score_text = tk.StringVar(value=f"Skóre: {self.score}/{self.q_number}")
        self.lbl_score = tk.Label(self.frame, textvariable=self.score_text, font=("Helvetica", 10, "italic"))
        self.lbl_score.pack(pady=(10,0))

        tk.Button(self.frame, text="Zpět do menu", command=self.show_menu).pack(pady=(8,0))
        self.next_question()

    def next_question(self):
        if self.q_number >= self.total_questions:
            self.end_quiz()
            return
        self.q_number += 1
        correct = random.choice(WORD_DEFS)
        if self.mode == "def2word":
            self.def_text.set(f"Otázka {self.q_number}: {correct[1]}")
            choices = [w for (w, d) in WORD_DEFS if w != correct[0]]
            choice_words = random.sample(choices, 3) + [correct[0]]
            random.shuffle(choice_words)
            self.current_answer = correct[0]
            for i, w in enumerate(choice_words):
                self.buttons[i].config(text=w, state=tk.NORMAL, bg=None)
        elif self.mode == "word2def":
            self.def_text.set(f"Otázka {self.q_number}: {correct[0]}")
            choices = [d for (w, d) in WORD_DEFS if w != correct[0]]
            choice_defs = random.sample(choices, 3) + [correct[1]]
            random.shuffle(choice_defs)
            self.current_answer = correct[1]
            for i, d in enumerate(choice_defs):
                self.buttons[i].config(text=d, state=tk.NORMAL, bg=None)
        self.score_text.set(f"Skóre: {self.score}/{self.q_number}")

    def check_answer(self, idx):
        picked = self.buttons[idx].cget("text")
        if picked == self.current_answer:
            self.score += 1
            self.buttons[idx].config(bg="lightgreen")
        else:
            self.buttons[idx].config(bg="tomato")
            for b in self.buttons:
                if b.cget("text") == self.current_answer:
                    b.config(bg="lightgreen")
        for b in self.buttons:
            b.config(state=tk.DISABLED)
        self.master.after(900, self.next_question)

    def end_quiz(self):
        if messagebox.askyesno("Konec hry", f"Konec! Skóre: {self.score}/{self.total_questions}\nHrát znovu?"):
            self.show_menu()
        else:
            self.master.quit()

    # ====== FLASHCARDS ======
    def start_flashcards(self):
        self.clear_frame()
        self.cards = WORD_DEFS.copy()
        random.shuffle(self.cards)
        self.current_card = None
        self.card_label = tk.Label(self.frame, text="", wraplength=400, font=("Helvetica", 13))
        self.card_label.pack(pady=15)
        self.btn_show = tk.Button(self.frame, text="Odhalit odpověď", command=self.show_answer)
        self.btn_show.pack(pady=5)
        self.btn_vim = tk.Button(self.frame, text="Vím", command=lambda: self.next_flashcard(True))
        self.btn_repeat = tk.Button(self.frame, text="Opakovat", command=lambda: self.next_flashcard(False))
        self.btn_vim.pack(pady=3)
        self.btn_repeat.pack(pady=3)
        tk.Button(self.frame, text="Zpět do menu", command=self.show_menu).pack(pady=10)
        self.next_flashcard()

    def next_flashcard(self, know=None):
        if know is not None and self.current_card:
            if know:
                if self.current_card in self.cards:
                    self.cards.remove(self.current_card)
            else:
                if self.current_card not in self.cards:
                    self.cards.append(self.current_card)
        if not self.cards:
            messagebox.showinfo("Hotovo", "Prošli jste všechny kartičky!")
            self.show_menu()
            return
        self.current_card = random.choice(self.cards)
        if random.choice([True, False]):
            self.card_label.config(text=f"Slovo: {self.current_card[0]}")
            self.answer_side = self.current_card[1]
        else:
            self.card_label.config(text=f"Definice: {self.current_card[1]}")
            self.answer_side = self.current_card[0]
        self.btn_show.config(state=tk.NORMAL)

    def show_answer(self):
        self.card_label.config(text=self.card_label.cget("text") + "\n\nOdpověď: " + self.answer_side)
        self.btn_show.config(state=tk.DISABLED)

    # ====== MATCHING GAME ======
    def start_matchgame(self):
        self.clear_frame()
        self.start_time = time.time()
        self.selected_word = None
        self.selected_def = None

        sample = random.sample(WORD_DEFS, 4)
        self.words = [w for w,d in sample]
        self.defs = [d for w,d in sample]
        random.shuffle(self.words)
        random.shuffle(self.defs)

        tk.Label(self.frame, text="Spoj slova s definicemi", font=("Helvetica", 13, "bold")).pack(pady=10)
        self.word_buttons = []
        self.def_buttons = []
        word_frame = tk.Frame(self.frame)
        word_frame.pack(side="left", padx=20)
        def_frame = tk.Frame(self.frame)
        def_frame.pack(side="right", padx=20)
        tk.Label(word_frame, text="Slova").pack()
        for w in self.words:
            b = tk.Button(word_frame, text=w, width=20, command=lambda w=w: self.select_word(w))
            b.pack(pady=3)
            self.word_buttons.append(b)
        tk.Label(def_frame, text="Definice").pack()
        for d in self.defs:
            b = tk.Button(def_frame, text=d, wraplength=200, width=30, command=lambda d=d: self.select_def(d))
            b.pack(pady=3)
            self.def_buttons.append(b)
        tk.Button(self.frame, text="Zpět do menu", command=self.show_menu).pack(pady=10)
        self.matches = {}

    def select_word(self, w):
        self.selected_word = w
        self.check_match()

    def select_def(self, d):
        self.selected_def = d
        self.check_match()

    def check_match(self):
        if self.selected_word and self.selected_def:
            pair = (self.selected_word, self.selected_def)
            if pair in WORD_DEFS:
                self.matches[self.selected_word] = self.selected_def
                for b in self.word_buttons:
                    if b.cget("text") == self.selected_word:
                        b.config(state=tk.DISABLED, bg="lightgreen")
                for b in self.def_buttons:
                    if b.cget("text") == self.selected_def:
                        b.config(state=tk.DISABLED, bg="lightgreen")
            else:
                messagebox.showinfo("Špatně", "Nesprávná dvojice!")
            self.selected_word = None
            self.selected_def = None
            if len(self.matches) == 4:
                elapsed = time.time() - self.start_time
                self.save_score(elapsed)
                messagebox.showinfo("Hotovo", f"Dokončeno! Čas: {elapsed:.2f} s")
                self.show_menu()

    def save_score(self, elapsed):
        try:
            with open(SCORES_FILE, "a") as f:
                f.write(f"{elapsed:.2f}\n")
        except:
            pass

    def show_leaderboard(self):
        self.clear_frame()
        tk.Label(self.frame, text="Žebříček nejlepších časů", font=("Helvetica", 14, "bold")).pack(pady=10)
        scores = []
        if os.path.exists(SCORES_FILE):
            with open(SCORES_FILE) as f:
                for line in f:
                    try:
                        scores.append(float(line.strip()))
                    except:
                        pass
        scores = sorted(scores)[:10]
        if scores:
            for i, s in enumerate(scores, 1):
                tk.Label(self.frame, text=f"{i}. {s:.2f} s").pack()
        else:
            tk.Label(self.frame, text="Žádné záznamy").pack()
        tk.Button(self.frame, text="Zpět do menu", command=self.show_menu).pack(pady=15)

    # ====== HANGMAN ======
    def start_hangman(self):
        self.clear_frame()
        self.word = random.choice([w for w,d in WORD_DEFS])
        self.guessed = set()
        self.tries = 6

        self.lbl_word = tk.Label(self.frame, text=self.get_display_word(), font=("Helvetica", 16))
        self.lbl_word.pack(pady=10)

        self.lbl_info = tk.Label(self.frame, text=f"Zbývá pokusů: {self.tries}", font=("Helvetica", 12))
        self.lbl_info.pack(pady=5)

        self.entry = tk.Entry(self.frame)
        self.entry.pack(pady=5)
        tk.Button(self.frame, text="Hádej", command=self.make_guess).pack(pady=5)
        tk.Button(self.frame, text="Zpět do menu", command=self.show_menu).pack(pady=10)

    def get_display_word(self):
        return " ".join([c if c in self.guessed else "_" for c in self.word])

    def make_guess(self):
        guess = self.entry.get().lower().strip()
        self.entry.delete(0, tk.END)
        if not guess:
            return
        if len(guess) == 1:
            if guess in self.word:
                self.guessed.add(guess)
            else:
                self.tries -= 1
        else:
            if guess == self.word:
                self.guessed.update(set(self.word))
            else:
                self.tries -= 1
        self.lbl_word.config(text=self.get_display_word())
        self.lbl_info.config(text=f"Zbývá pokusů: {self.tries}")
        if set(self.word).issubset(self.guessed):
            messagebox.showinfo("Výhra", f"Uhodl jsi slovo: {self.word}")
            self.show_menu()
        elif self.tries <= 0:
            messagebox.showinfo("Prohra", f"Došly pokusy! Slovo bylo: {self.word}")
            self.show_menu()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizGame(root)
    root.mainloop()
