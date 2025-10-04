import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import os

# ---------- Question loader ----------
def load_questions_from_file(filename="questions.txt"):
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read().strip()

    raw = [block.strip() for block in content.split("\n\n") if block.strip()]
    questions = []
    for block in raw:
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue
        qtext = lines[0]
        options = [ln for ln in lines[1:] if ln and (ln[0].upper() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" and ln[1:3] in [") ", ")"] or ln.startswith(("A)", "B)", "C)", "D)")))]
        # Alternative safer extraction: lines that contain ')' after a letter
        # find ANSWER:
        answer_line = next((ln for ln in lines if ln.upper().startswith("ANSWER:")), None)
        if not answer_line:
            continue
        correct = answer_line.split(":", 1)[1].strip().upper()
        # Normalize options to list of tuples like ("A","Berlin")
        normalized = []
        for opt in options:
            # remove leading "A) " or "A)"; accept "A)" or "A) "
            if len(opt) >= 2 and opt[1] == ")":
                key = opt[0].upper()
                text = opt[2:].strip()
                if text.startswith(")"):
                    text = text[1:].strip()
                normalized.append((key, text))
            else:
                # fallback: split by ')'
                if ')' in opt:
                    k, t = opt.split(')', 1)
                    normalized.append((k.strip().upper(), t.strip()))
                else:
                    # skip malformed
                    continue
        if not normalized:
            continue
        # If correct is a letter like "C", use as is. If user wrote full text, try to map.
        # Keep original raw for saving later too.
        questions.append({
            "question": qtext,
            "options": normalized,   # list of (key, text)
            "answer": correct
        })
    return questions

# ---------- GUI App ----------
class QuizApp(tk.Tk):
    def __init__(self, questions_file="questions.txt"):
        super().__init__()
        self.title("Quiz App")
        self.geometry("720x420")
        self.minsize(600, 360)
        self.questions_file = questions_file

        self.style = ttk.Style(self)
        # Use default theme; keep UI neutral
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self.container = ttk.Frame(self, padding=12)
        self.container.pack(fill="both", expand=True)

        # top menu
        self._build_menu()

        # variables
        self.all_questions = load_questions_from_file(self.questions_file)
        self.current_set = []       # currently active question set (shuffled)
        self.idx = 0
        self.score = 0
        self.user_choice = tk.StringVar()
        self.wrong_answers = []

        # UI
        self._build_ui()

        # keyboard bindings
        self.bind("<Key>", self._on_keypress)

        # start
        if not self.all_questions:
            messagebox.showwarning("No questions", f"No questions found in {self.questions_file}. Please create it and restart.")
        else:
            self.start_quiz(self.all_questions)

    def _build_menu(self):
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=False)
        filemenu.add_command(label="Load questions file...", command=self._ask_load_file)
        filemenu.add_command(label="Reload questions.txt", command=self._reload_questions)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = tk.Menu(menubar, tearoff=False)
        helpmenu.add_command(label="How to use", command=self._show_help)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.config(menu=menubar)

    def _build_ui(self):
        # Question frame
        qframe = ttk.Frame(self.container)
        qframe.pack(fill="both", expand=True)

        self.question_label = ttk.Label(qframe, text="", wraplength=660, font=("Segoe UI", 14))
        self.question_label.pack(pady=(6,12), anchor="w")

        # Options (radiobuttons)
        self.options_frame = ttk.Frame(qframe)
        self.options_frame.pack(anchor="w", pady=(0,12))

        # Score and progress
        status_frame = ttk.Frame(self.container)
        status_frame.pack(fill="x", pady=(4,6))

        self.progress_label = ttk.Label(status_frame, text="Question 0/0")
        self.progress_label.pack(side="left")

        self.score_label = ttk.Label(status_frame, text="Score: 0")
        self.score_label.pack(side="right")

        # Buttons
        btn_frame = ttk.Frame(self.container)
        btn_frame.pack(fill="x", pady=(12,0))

        self.submit_btn = ttk.Button(btn_frame, text="Submit (or press Enter)", command=self.submit_answer)
        self.submit_btn.pack(side="left")

        self.next_btn = ttk.Button(btn_frame, text="Next →", command=self.next_question, state="disabled")
        self.next_btn.pack(side="left", padx=(8,0))

        sep = ttk.Label(btn_frame, text="   ")
        sep.pack(side="left")

        self.restart_btn = ttk.Button(btn_frame, text="Restart (shuffle)", command=lambda: self.start_quiz(self.all_questions))
        self.restart_btn.pack(side="left")

        self.retry_wrong_btn = ttk.Button(btn_frame, text="Retry wrong questions", command=self.retry_wrong_questions, state="disabled")
        self.retry_wrong_btn.pack(side="right")

    def _show_help(self):
        text = (
            "How to use:\n\n"
            "- Prepare a file named questions.txt (same folder) with the format:\n"
            "  Question line, then lines like A) Option text, B) Option text, then ANSWER: <LETTER>\n\n"
            "- The app will shuffle questions. Select an option and press Submit (or Enter).\n"
            "- You can also press keys A/B/C/D to choose an answer quickly.\n"
            "- Wrong answers are saved to wrong_answers.txt automatically at the end.\n"
            "- Use 'Retry wrong questions' to practice missed ones only.\n"
        )
        messagebox.showinfo("How to use", text)

    def _ask_load_file(self):
        path = filedialog.askopenfilename(title="Select questions file", filetypes=[("Text files","*.txt"),("All files","*.*")])
        if path:
            self.questions_file = path
            self.all_questions = load_questions_from_file(self.questions_file)
            if not self.all_questions:
                messagebox.showwarning("No questions", f"No valid questions found in {self.questions_file}.")
            else:
                self.start_quiz(self.all_questions)

    def _reload_questions(self):
        self.all_questions = load_questions_from_file(self.questions_file)
        if not self.all_questions:
            messagebox.showwarning("No questions", f"No valid questions found in {self.questions_file}.")
        else:
            self.start_quiz(self.all_questions)

    def start_quiz(self, questions):
        self.current_set = questions.copy()
        random.shuffle(self.current_set)
        self.idx = 0
        self.score = 0
        self.wrong_answers = []
        self.user_choice.set("")
        self.update_status()
        self.retry_wrong_btn.config(state="disabled")
        self._show_current_question()

    def update_status(self):
        total = len(self.current_set)
        self.progress_label.config(text=f"Question {self.idx+1}/{total}" if total>0 else "Question 0/0")
        self.score_label.config(text=f"Score: {self.score}")

    def _clear_options(self):
        for widget in self.options_frame.winfo_children():
            widget.destroy()

    def _show_current_question(self):
        self._clear_options()
        if self.idx >= len(self.current_set):
            self._finish_quiz()
            return
        item = self.current_set[self.idx]
        self.question_label.config(text=item["question"])
        self.user_choice.set("")  # clear selection
        # Build radio buttons for options
        # Ensure options are ordered by their letter (A, B, C...)
        options = sorted(item["options"], key=lambda x: x[0])
        for key, text in options:
            rb = ttk.Radiobutton(self.options_frame, text=f"{key}) {text}", value=key.upper(), variable=self.user_choice)
            rb.pack(anchor="w", pady=2)
        # enable/disable buttons
        self.submit_btn.config(state="normal")
        self.next_btn.config(state="disabled")
        self.update_status()

    def submit_answer(self):
        if self.idx >= len(self.current_set):
            return
        selected = self.user_choice.get().strip().upper()
        if not selected:
            messagebox.showwarning("No answer", "Please select an option (or press A/B/C/D on the keyboard).")
            return
        item = self.current_set[self.idx]
        correct = item["answer"].strip().upper()
        # Accept cases where correct is letter or full text - prefer letter
        correct_letter = correct[0] if correct else ""
        if selected == correct_letter:
            messagebox.showinfo("Correct", "✅ Correct!")
            self.score += 1
        else:
            # find text for selected and for correct for saving
            selected_text = next((t for k,t in item["options"] if k.upper()==selected), selected)
            correct_text = next((t for k,t in item["options"] if k.upper()==correct_letter), correct)
            messagebox.showinfo("Wrong", f"❌ Wrong!\nYour answer: {selected}\nCorrect: {correct_letter}")
            self.wrong_answers.append({
                "question": item["question"],
                "options": item["options"],
                "your_answer": selected,
                "correct_answer": correct_letter
            })
        # lock submit, enable next
        self.submit_btn.config(state="disabled")
        self.next_btn.config(state="normal")
        self.update_status()

    def next_question(self):
        self.idx += 1
        if self.idx < len(self.current_set):
            self._show_current_question()
        else:
            self._finish_quiz()

    def _finish_quiz(self):
        total = len(self.current_set)
        summary = f"Quiz finished!\nScore: {self.score}/{total}"
        # Save wrong answers if any
        if self.wrong_answers:
            self.save_wrong_answers()
            summary += f"\n\nWrong answers saved to wrong_answers.txt ({len(self.wrong_answers)})."
        else:
            summary += "\n\nNo wrong answers — well done!"
        # Offer options
        if messagebox.askyesno("Finished", summary + "\n\nDo you want to retry only the wrong questions?"):
            self.retry_wrong_questions()
        else:
            # Ask if user wants to restart full quiz
            if messagebox.askyesno("Restart", "Restart full quiz (shuffle)?"):
                self.start_quiz(self.all_questions)
            else:
                # keep window open showing final state
                self.question_label.config(text="Quiz finished. Use Restart or Load new file from the File menu.")
                self._clear_options()
                self.submit_btn.config(state="disabled")
                self.next_btn.config(state="disabled")
                self.retry_wrong_btn.config(state=("normal" if self.wrong_answers else "disabled"))
                self.update_status()

    def save_wrong_answers(self, fname="wrong_answers.txt"):
        with open(fname, "w", encoding="utf-8") as f:
            for entry in self.wrong_answers:
                f.write(f"Question: {entry['question']}\n")
                for k, t in sorted(entry["options"], key=lambda x: x[0]):
                    f.write(f"{k}) {t}\n")
                f.write(f"Your answer: {entry['your_answer']}\n")
                f.write(f"Correct answer: {entry['correct_answer']}\n")
                f.write("-" * 40 + "\n\n")

    def retry_wrong_questions(self):
        if not self.wrong_answers:
            messagebox.showinfo("No wrong answers", "There are no wrong answers to retry.")
            return
        # Build a question set from wrong_answers
        questions = []
        for e in self.wrong_answers:
            questions.append({
                "question": e["question"],
                "options": e["options"],
                "answer": e["correct_answer"]
            })
        # reset and start these
        self.start_quiz(questions)
        self.retry_wrong_btn.config(state="disabled")

    def _on_keypress(self, event):
        # Accept A/B/C/D keys to select options, Enter to submit, Right arrow to next
        key = event.keysym.upper()
        if key in ("A","B","C","D","E","F"):
            # only set if such option exists
            # check if current options contain that letter
            if any(k.upper() == key for k,_ in (self.current_set[self.idx]["options"] if self.idx < len(self.current_set) else [])):
                self.user_choice.set(key)
        elif key in ("RETURN","KP_ENTER"):
            # Submit if submit enabled
            if self.submit_btn["state"] == "normal":
                self.submit_answer()
        elif key in ("RIGHT","NEXT"):
            if self.next_btn["state"] == "normal":
                self.next_question()

if __name__ == "__main__":
    app = QuizApp("questions.txt")
    app.mainloop()

