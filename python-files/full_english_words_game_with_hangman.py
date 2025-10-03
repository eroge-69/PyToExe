
#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, simpledialog, font
import random, json, time, os, sys

# ---------- Data ------------------------------------------------------------
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

LB_FILE = os.path.join(os.path.dirname(__file__), "matching_leaderboard.json")

def load_leaderboard():
    try:
        with open(LB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_leaderboard(lb):
    try:
        with open(LB_FILE, "w", encoding="utf-8") as f:
            json.dump(lb, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Could not save leaderboard:", e, file=sys.stderr)

# ----------------- App -----------------------------------------------------
class SimpleWordGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("English Words — Clean Game")
        self.geometry("1000x700")
        self.configure(bg="#f5f7fb")
        self.custom_font = font.Font(family="Helvetica", size=12)
        self.title_font = font.Font(family="Helvetica", size=20, weight="bold")
        self.small_font = font.Font(family="Helvetica", size=10)
        self.players = ["Hráč 1", "Hráč 2"]
        self.current_player = 0
        self.scores = [0, 0]
        self.container = tk.Frame(self, bg="#f5f7fb")
        self.container.pack(fill="both", expand=True, padx=12, pady=12)
        self.main_area = tk.Frame(self.container, bg="#f5f7fb")
        self.main_area.pack(fill="both", expand=True)
        self.build_menu()

    def clear_main(self):
        for w in self.main_area.winfo_children():
            w.destroy()

    def build_menu(self):
        self.clear_main()
        f = tk.Frame(self.main_area, bg="#f5f7fb")
        f.pack(expand=True)
        tk.Label(f, text="English Words Game", font=self.title_font, bg="#f5f7fb").pack(pady=(10,20))

        btncfg = dict(width=30, height=2, font=self.custom_font, bg="#ffffff", bd=1)
        tk.Button(f, text="Singleplayer", command=lambda: self.start_game(False), **btncfg).pack(pady=8)
        tk.Button(f, text="Multiplayer", command=lambda: self.start_game(True), **btncfg).pack(pady=8)
        tk.Button(f, text="Exit", command=self.quit, **btncfg).pack(pady=8)

        # small credits (non-essential)
        
    def start_game(self, two_player):
        self.two_player = two_player
        self.scores = [0,0]
        self.current_player = 0
        if two_player:
            self.show_multiplayer_menu()
        else:
            self.show_single_menu()

    # ----------------- Menus -----------------
    def show_single_menu(self):
        self.clear_main()
        f = tk.Frame(self.main_area, bg="#f5f7fb")
        f.pack(fill="both", expand=True, padx=12, pady=12)
        tk.Label(f, text="Singleplayer", font=self.title_font, bg="#f5f7fb").pack(pady=(6,12))

        btncfg = dict(width=40, height=2, font=self.custom_font, bg="#ffffff", bd=1)
        tk.Button(f, text="Definice → Slovo", command=lambda: QuizFrame(self.main_area, self, mode='def2word', two_player=False).pack(fill='both', expand=True), **btncfg).pack(pady=6)
        tk.Button(f, text="Slovo → Definice", command=lambda: QuizFrame(self.main_area, self, mode='word2def', two_player=False).pack(fill='both', expand=True), **btncfg).pack(pady=6)
        tk.Button(f, text="Učení (flesh cards)", command=lambda: FlashCards(self.main_area, self).pack(fill='both', expand=True), **btncfg).pack(pady=6)
        tk.Button(f, text="Hra (spojování)", command=lambda: MatchingFrame(self.main_area, self).pack(fill='both', expand=True), **btncfg).pack(pady=6)
        tk.Button(f, text="Šibenice", command=lambda: HangmanFrame(self.main_area, self, two_player=False).pack(fill='both', expand=True), **btncfg).pack(pady=6)
        tk.Button(f, text="Žebříček", command=lambda: LeaderboardFrame(self.main_area, self).pack(fill='both', expand=True), **btncfg).pack(pady=6)
        tk.Button(f, text="Zpět", command=self.build_menu, bg="#e9ecef", width=10).pack(pady=8)

    def show_multiplayer_menu(self):
        self.clear_main()
        f = tk.Frame(self.main_area, bg="#f5f7fb")
        f.pack(fill="both", expand=True, padx=12, pady=12)
        tk.Label(f, text="Multiplayer", font=self.title_font, bg="#f5f7fb").pack(pady=(6,12))

        btncfg = dict(width=40, height=2, font=self.custom_font, bg="#ffffff", bd=1)
        tk.Button(f, text="Definice → Slovo (20 otázek)", command=lambda: QuizFrame(self.main_area, self, mode='def2word', two_player=True).pack(fill='both', expand=True), **btncfg).pack(pady=6)
        tk.Button(f, text="Slovo → Definice (20 otázek)", command=lambda: QuizFrame(self.main_area, self, mode='word2def', two_player=True).pack(fill='both', expand=True), **btncfg).pack(pady=6)
        tk.Button(f, text="Hra (spojování) - Multiplayer", command=lambda: TwoPlayerMatching(self.main_area, self).pack(fill='both', expand=True), **btncfg).pack(pady=6)
        tk.Button(f, text="Šibenice (střídání)", command=lambda: HangmanFrame(self.main_area, self, two_player=True).pack(fill='both', expand=True), **btncfg).pack(pady=6)
        tk.Button(f, text="Zpět", command=self.build_menu, bg="#e9ecef", width=10).pack(pady=8)

# ----------------- Quiz Frame -----------------
class QuizFrame(tk.Frame):
    def __init__(self, parent, app, mode='def2word', two_player=False):
        super().__init__(parent, bg="#ffffff")
        self.app = app
        self.mode = mode
        self.two_player = two_player
        self.pairs = WORD_DEFS.copy()
        random.shuffle(self.pairs)
        self.index = 0
        self.correct = 0
        self.wrong = 0
        self.max_rounds = 20 if two_player else 10

        top = tk.Frame(self, bg="#ffffff"); top.pack(fill='x', pady=8, padx=12)
        title = "Definice → Slovo" if mode=='def2word' else "Slovo → Definice"
        tk.Label(top, text=f"{title} {'(Multiplayer)' if two_player else '(Single)'}", font=app.title_font, bg="#ffffff").pack(side='left')
        if two_player:
            tk.Label(top, text=f"Hraje hráč {self.app.current_player+1}", font=app.small_font, bg="#ffffff").pack(side='left', padx=10)
        tk.Button(top, text="Zpět", command=(app.show_multiplayer_menu if two_player else app.show_single_menu), bg="#e9ecef").pack(side='right', padx=6)

        body = tk.Frame(self, bg="#f8fafb", padx=12, pady=12); body.pack(fill='both', expand=True)
        self.qvar = tk.StringVar(value="")
        tk.Label(body, textvariable=self.qvar, font=app.custom_font, bg="#f8fafb", wraplength=800).pack(pady=8)
        self.option_frame = tk.Frame(body, bg="#f8fafb"); self.option_frame.pack(pady=6)
        self.info_var = tk.StringVar(value="")
        tk.Label(body, textvariable=self.info_var, font=app.small_font, bg="#f8fafb").pack(anchor='w', pady=4)
        self.build_question()

    def build_question(self):
        if self.index >= self.max_rounds:
            self.finish(); return
        if self.index >= len(self.pairs):
            self.index = 0
            random.shuffle(self.pairs)
        w,d = self.pairs[self.index]
        self.index += 1
        # options
        options = []
        if self.mode == 'word2def':
            question = f"Slovo:\\n{w}"
            correct = d
            pool = [dd for ww,dd in WORD_DEFS if dd!=d]
            options = random.sample(pool, min(len(pool),4)) + [d]
        else:
            question = f"Definice:\\n{d}"
            correct = w
            pool = [ww for ww,dd in WORD_DEFS if ww!=w]
            options = random.sample(pool, min(len(pool),4)) + [w]
        random.shuffle(options)
        self.qvar.set(question)
        # clear options
        for c in self.option_frame.winfo_children(): c.destroy()
        for opt in options:
            btn = tk.Button(self.option_frame, text=opt, wraplength=700, width=80, height=2,
                            command=lambda o=opt, c=correct: self.check(o,c), bg="#ffffff")
            btn.pack(pady=6)

        self.info_var.set(f"Round {self.index}/{self.max_rounds}  Correct: {self.correct}  Wrong: {self.wrong}")

    def check(self, picked, correct):
        if picked == correct:
            messagebox.showinfo("Správně", "Správně!")
            self.correct += 1
            if self.two_player:
                # add to current player's score
                self.app.scores[self.app.current_player] += 1
        else:
            messagebox.showinfo("Špatně", "Bohužel, špatně.")
            self.wrong += 1
        if self.two_player:
            self.app.current_player = 1 - self.app.current_player
        self.build_question()

    def finish(self):
        if self.two_player:
            p1, p2 = self.app.scores
            if p1>p2: res = "Hráč 1 vyhrál!"
            elif p2>p1: res = "Hráč 2 vyhrál!"
            else: res = "Remíza!"
            messagebox.showinfo("Hotovo", f"Konec.\nHráč 1: {p1}\nHráč 2: {p2}\n{res}")
            self.app.scores=[0,0]; self.app.current_player=0; self.app.show_multiplayer_menu()
        else:
            messagebox.showinfo("Hotovo", f"Konec.\nCorrect: {self.correct}\nWrong: {self.wrong}")
            self.app.show_single_menu()

# ----------------- Flashcards -----------------
class FlashCards(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#ffffff")
        self.app = app
        self.cards = WORD_DEFS.copy()
        random.shuffle(self.cards)
        self.index = 0
        self.showing_answer = False

        top = tk.Frame(self, bg="#ffffff"); top.pack(fill='x', pady=8, padx=12)
        tk.Label(top, text="Učení (flesh cards)", font=app.title_font, bg="#ffffff").pack(side='left')
        tk.Button(top, text="Zpět", command=app.show_single_menu, bg="#e9ecef").pack(side='right', padx=6)

        body = tk.Frame(self, bg="#f8fafb", padx=12, pady=12); body.pack(fill='both', expand=True)
        self.card_var = tk.StringVar(value="")
        tk.Label(body, textvariable=self.card_var, font=app.custom_font, bg="#f8fafb", wraplength=800).pack(pady=30)
        btns = tk.Frame(body, bg="#f8fafb"); btns.pack(pady=6)
        tk.Button(btns, text="Ukázat odpověď", command=self.toggle_answer, width=16).pack(side='left', padx=6)
        tk.Button(btns, text="Znám", command=lambda: self.known(True), width=12).pack(side='left', padx=6)
        tk.Button(btns, text="Neznám", command=lambda: self.known(False), width=12).pack(side='left', padx=6)
        self.show_card()

    def show_card(self):
        if not self.cards:
            messagebox.showinfo("Hotovo", "Prošli jste všechny karty.")
            self.app.show_single_menu(); return
        self.showing_answer = False
        self.current = self.cards[self.index % len(self.cards)]
        self.card_var.set(f"Slovo:\\n\\n{self.current[0]}")

    def toggle_answer(self):
        if not self.current: return
        if not self.showing_answer:
            self.card_var.set(f"Definice:\\n\\n{self.current[1]}")
            self.showing_answer = True
        else:
            self.card_var.set(f"Slovo:\\n\\n{self.current[0]}")
            self.showing_answer = False

    def known(self, knows):
        if knows:
            # remove this card from deck (if present)
            if self.current in self.cards:
                self.cards.remove(self.current)
            if not self.cards:
                messagebox.showinfo("Hotovo", "Prošli jste všechny karty.")
                self.app.show_single_menu(); return
            self.index = self.index % len(self.cards)
        else:
            # move to end
            if self.current in self.cards:
                self.cards.remove(self.current)
            self.cards.append(self.current)
            self.index = self.index % len(self.cards)
        self.show_card()

# ----------------- Matching (5 pairs) -----------------
class MatchingFrame(tk.Frame):
    def __init__(self, parent, app, two_player=False, callback=None):
        super().__init__(parent, bg="#ffffff")
        self.app = app
        self.two_player = two_player
        self.callback = callback
        self.start_time = time.time()
        self.penalty = 0.0
        self.matches_done = 0
        self.selected_word = None
        self.selected_def = None

        self.pairs = random.sample(WORD_DEFS, 5)
        self.words = [w for w,d in self.pairs]
        self.defs = [d for w,d in self.pairs]
        random.shuffle(self.words)
        random.shuffle(self.defs)

        top = tk.Frame(self, bg="#ffffff"); top.pack(fill='x', pady=8, padx=12)
        tk.Label(top, text="Hra (spojování)", font=app.title_font, bg="#ffffff").pack(side='left')
        tk.Button(top, text="Zpět", command=(app.show_multiplayer_menu if two_player else app.show_single_menu), bg="#e9ecef").pack(side='right', padx=6)

        body = tk.Frame(self, bg="#f8fafb", padx=12, pady=12); body.pack(fill='both', expand=True)
        self.timer_var = tk.StringVar(value="Čas: 0.0s  Penalizace: 0.0s")
        tk.Label(body, textvariable=self.timer_var, font=app.custom_font, bg="#f8fafb").pack(pady=4)
        grid = tk.Frame(body, bg="#f8fafb"); grid.pack(expand=True, fill='both')

        self.word_buttons = {}
        self.def_buttons = {}

        for i,w in enumerate(self.words):
            b = tk.Button(grid, text=w, width=25, command=lambda wi=w: self.select_word(wi), bg="#ffffff")
            b.grid(row=i, column=0, padx=10, pady=5, sticky='w')
            self.word_buttons[w] = b

        for i,d in enumerate(self.defs):
            b = tk.Button(grid, text=d, width=60, wraplength=500, command=lambda di=d: self.select_def(di), bg="#ffffff")
            b.grid(row=i, column=1, padx=10, pady=5, sticky='w')
            self.def_buttons[d] = b

        # status bar
        self.status_var = tk.StringVar(value="Spojeno: 0/5")
        tk.Label(body, textvariable=self.status_var, font=app.small_font, bg="#f8fafb").pack(pady=6)

        self.update_clock()

    def select_word(self, w):
        if w in self.word_buttons and self.word_buttons[w]['state']!='disabled':
            self.selected_word = w
            self.word_buttons[w].config(relief='sunken')

    def select_def(self, d):
        if d in self.def_buttons and self.def_buttons[d]['state']!='disabled':
            self.selected_def = d
            self.def_buttons[d].config(relief='sunken')
        if self.selected_word and self.selected_def:
            self.check_pair()

    def check_pair(self):
        w = self.selected_word; d = self.selected_def
        correct = dict(self.pairs)[w]
        if d == correct:
            self.word_buttons[w].config(state='disabled', bg='#d4edda', relief='raised')
            self.def_buttons[d].config(state='disabled', bg='#d4edda', relief='raised')
            self.matches_done += 1
        else:
            self.penalty += 3.0
            # flash red
            self.word_buttons[w].config(bg='#f8d7da', relief='raised')
            self.def_buttons[d].config(bg='#f8d7da', relief='raised')
            self.after(600, lambda: (self.word_buttons[w].config(bg='#ffffff'), self.def_buttons[d].config(bg='#ffffff')))

        self.selected_word = None; self.selected_def = None
        self.status_var.set(f"Spojeno: {self.matches_done}/5")

        if self.matches_done == 5:
            total_time = time.time() - self.start_time + self.penalty
            if self.two_player and self.callback:
                self.callback(total_time)
            else:
                messagebox.showinfo("Hotovo", f"Dokončeno! Čas: {total_time:.2f} s")
                name = simpledialog.askstring("Žebříček", "Zadej jméno:") or "Hráč"
                lb = load_leaderboard(); lb.append({"name": name, "time": total_time, "timestamp": time.time()}); lb = sorted(lb, key=lambda x: x['time'])[:50]; save_leaderboard(lb)
                self.app.show_single_menu()

    def update_clock(self):
        elapsed = time.time() - self.start_time + self.penalty
        self.timer_var.set(f"Čas: {elapsed:.1f}s  Penalizace: {self.penalty:.1f}s")
        if self.matches_done < 5:
            self.after(200, self.update_clock)

# ----------------- Two-player matching -----------------
class TwoPlayerMatching(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#ffffff")
        self.app = app
        self.times = [None, None]
        self.current = 0

        top = tk.Frame(self, bg="#ffffff"); top.pack(fill='x', pady=8, padx=12)
        tk.Label(top, text="Multiplayer – Hra (spojování)", font=app.title_font, bg="#ffffff").pack(side='left')
        tk.Button(top, text="Zpět", command=app.show_multiplayer_menu, bg="#e9ecef").pack(side='right', padx=6)

        self.body = tk.Frame(self, bg="#f8fafb", padx=12, pady=12); self.body.pack(fill='both', expand=True)
        self.start_player()

    def start_player(self):
        for w in self.body.winfo_children(): w.destroy()
        tk.Label(self.body, text=f"{self.app.players[self.current]} – tvůj pokus", font=self.app.custom_font, bg="#f8fafb").pack(pady=10)
        tk.Button(self.body, text="Start", command=self.run_game, width=20).pack(pady=6)

    def run_game(self):
        for w in self.body.winfo_children(): w.destroy()
        frame = MatchingFrame(self.body, self.app, two_player=True, callback=self.finish)
        frame.pack(fill='both', expand=True)

    def finish(self, t):
        self.times[self.current] = t
        self.current += 1
        if self.current < 2:
            self.start_player()
        else:
            self.show_result()

    def show_result(self):
        for w in self.body.winfo_children(): w.destroy()
        t1,t2 = self.times
        if t1 < t2: res = "Vyhrál Hráč 1!"
        elif t2 < t1: res = "Vyhrál Hráč 2!"
        else: res = "Remíza!"
        tk.Label(self.body, text=f"Hráč 1: {t1:.2f}s\\nHráč 2: {t2:.2f}s\\n\\n{res}", font=self.app.custom_font, bg="#f8fafb").pack(pady=10)
        tk.Button(self.body, text="Zpět do menu", command=self.app.show_multiplayer_menu, bg="#e9ecef").pack(pady=6)

# ----------------- Leaderboard -----------------
class LeaderboardFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#ffffff")
        self.app = app
        top = tk.Frame(self, bg="#ffffff"); top.pack(fill='x', pady=8, padx=12)
        tk.Label(top, text="Žebříček", font=app.title_font, bg="#ffffff").pack(side='left')
        tk.Button(top, text="Zpět", command=app.show_single_menu, bg="#e9ecef").pack(side='right', padx=6)
        body = tk.Frame(self, bg="#f8fafb", padx=12, pady=12); body.pack(fill='both', expand=True)
        lb = load_leaderboard()
        if not lb:
            tk.Label(body, text="Žádné záznamy", font=app.custom_font, bg="#f8fafb").pack(pady=10)
        else:
            for i, e in enumerate(lb[:20], start=1):
                tk.Label(body, text=f"{i}. {e['name']} — {e['time']:.2f}s", font=app.custom_font, bg="#f8fafb").pack(anchor='w', pady=2)

# ----------------- Hangman -----------------

class HangmanFrame(tk.Frame):
    def __init__(self, parent, app, two_player=False):
        super().__init__(parent, bg="#ffffff")
        self.app = app
        self.two_player = two_player
        self.word = random.choice([w for w,d in WORD_DEFS]).upper()
        self.masked = ['_' if c.isalpha() else c for c in self.word]
        self.errors = 0
        self.max_errors = 6

        top = tk.Frame(self, bg="#ffffff"); top.pack(fill='x', pady=8, padx=12)
        tk.Label(top, text="Šibenice", font=app.title_font, bg="#ffffff").pack(side='left')
        if self.two_player:
            self.turn_label = tk.Label(top, text=f"Hraje hráč {self.app.current_player+1}", font=app.small_font, bg="#ffffff")
            self.turn_label.pack(side='left', padx=10)
        tk.Button(top, text="Zpět", command=(app.show_multiplayer_menu if two_player else app.show_single_menu), bg="#e9ecef").pack(side='right', padx=6)

        body = tk.Frame(self, bg="#f8fafb", padx=12, pady=12); body.pack(fill='both', expand=True)
        self.word_var = tk.StringVar(value=' '.join(self.masked))
        tk.Label(body, textvariable=self.word_var, font=app.custom_font, bg="#f8fafb").pack(pady=6)

        # canvas pro kreslení šibenice
        self.canvas = tk.Canvas(body, width=200, height=200, bg="#f8fafb", highlightthickness=0)
        self.canvas.pack(pady=6)
        self.draw_gallows()

        self.kb = tk.Frame(body, bg='#f8fafb'); self.kb.pack(pady=8)
        self.build_kb()
        tk.Button(body, text="Nové slovo", command=self.new_round).pack(pady=6)

    def draw_gallows(self):
        self.canvas.delete("all")
        # základní konstrukce
        self.canvas.create_line(20,180,180,180,width=3)
        self.canvas.create_line(50,180,50,20,width=3)
        self.canvas.create_line(50,20,120,20,width=3)
        self.canvas.create_line(120,20,120,40,width=3)
        # panáček podle počtu chyb
        if self.errors>0: self.canvas.create_oval(100,40,140,80,width=2)       # hlava
        if self.errors>1: self.canvas.create_line(120,80,120,130,width=2)      # tělo
        if self.errors>2: self.canvas.create_line(120,90,100,110,width=2)      # levá ruka
        if self.errors>3: self.canvas.create_line(120,90,140,110,width=2)      # pravá ruka
        if self.errors>4: self.canvas.create_line(120,130,100,160,width=2)     # levá noha
        if self.errors>5: self.canvas.create_line(120,130,140,160,width=2)     # pravá noha

    def build_kb(self):
        for w in self.kb.winfo_children(): w.destroy()
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for i,ch in enumerate(letters):
            b = tk.Button(self.kb, text=ch, width=3, command=lambda c=ch: self.guess(c))
            b.grid(row=i//9, column=i%9, padx=2, pady=2)

    def guess(self, ch):
        if ch in self.word:
            for i,c in enumerate(self.word):
                if c==ch: self.masked[i]=ch
            self.word_var.set(' '.join(self.masked))
            if '_' not in self.masked:
                messagebox.showinfo("Výhra", f"Uhodl jsi: {self.word}")
                self.new_round()
        else:
            self.errors += 1
            self.draw_gallows()
            if self.errors>=self.max_errors:
                messagebox.showinfo("Prohra", f"Slovo bylo: {self.word}")
                self.new_round()
        # střídání hráčů po každém pokusu
        if self.two_player:
            self.app.current_player = 1 - self.app.current_player
            self.turn_label.config(text=f"Hraje hráč {self.app.current_player+1}")

    def new_round(self):
        self.word = random.choice([w for w,d in WORD_DEFS]).upper()
        self.masked = ['_' if c.isalpha() else c for c in self.word]
        self.errors = 0
        self.word_var.set(' '.join(self.masked))
        self.build_kb()
        self.draw_gallows()

# ----------------- Run -----------------
if __name__ == '__main__':
    app = SimpleWordGame()
    app.mainloop()
