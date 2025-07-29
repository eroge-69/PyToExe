import tkinter as tk
from tkinter import messagebox
import random
import os
from datetime import datetime

class MathQuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mathe-Quiz für deine Tochter")

        self.total_questions = 100
        self.questions = []
        self.entries = []
        self.results_file = "ergebnisse.txt"
        self.max_saved_results = 10

        self.create_questions()
        self.create_ui()
        self.load_results()

    def create_questions(self):
        for _ in range(self.total_questions):
            kind = random.choice(['mult', 'add', 'sub'])
            if kind == 'mult':
                a = random.randint(1, 10)
                b = random.randint(1, 10)
                q = f"{a} x {b} = "
                a1 = a * b
            elif kind == 'add':
                a = random.randint(1, 100)
                b = random.randint(1, 100)
                q = f"{a} + {b} = "
                a1 = a + b
            else:  # sub
                a = random.randint(1, 100)
                b = random.randint(1, 100)
                if b > a:
                    a, b = b, a
                q = f"{a} - {b} = "
                a1 = a - b

            self.questions.append((q, a1))

    def create_ui(self):
        # Frame für Ergebnisse (letzte 10) oben
        self.results_frame = tk.Frame(self.root)
        self.results_frame.pack(pady=5)

        self.results_label = tk.Label(self.results_frame, text="Letzte 10 Ergebnisse:")
        self.results_label.pack()

        self.results_text = tk.Text(self.results_frame, height=10, width=40, state='disabled', bg='#f0f0f0')
        self.results_text.pack()

        # Canvas und scrollbar für Fragen
        canvas = tk.Canvas(self.root)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        self.frame = tk.Frame(canvas)

        self.frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for i, (q, _) in enumerate(self.questions):
            label = tk.Label(self.frame, text=f"{i+1}. {q}")
            label.grid(row=i, column=0, padx=5, pady=2, sticky='w')

            entry = tk.Entry(self.frame, width=10)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.entries.append(entry)

        btn = tk.Button(self.root, text="Ergebnisse auswerten", command=self.evaluate)
        btn.pack(side="bottom", pady=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def evaluate(self):
        correct = 0
        total = self.total_questions
        for i, entry in enumerate(self.entries):
            user_ans = entry.get()
            try:
                user_val = int(user_ans)
            except ValueError:
                user_val = None

            correct_ans = self.questions[i][1]
            if user_val == correct_ans:
                correct += 1
                entry.config(bg='lightgreen')
            else:
                entry.config(bg='salmon')

        messagebox.showinfo("Ergebnis", f"Du hast {correct} von {total} Aufgaben richtig gelöst.")
        self.save_result(correct)
        self.load_results()

    def save_result(self, correct):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_entry = f"{now} - {correct} von {self.total_questions} richtig\n"

        # Ergebnisse aus Datei laden
        results = []
        if os.path.isfile(self.results_file):
            with open(self.results_file, "r", encoding="utf-8") as f:
                results = f.readlines()

        # Neue Eintragung an Anfang setzen
        results.insert(0, new_entry)

        # Maximal 10 Ergebnisse behalten
        results = results[:self.max_saved_results]

        # Zurückschreiben
        with open(self.results_file, "w", encoding
