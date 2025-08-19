import json
import tkinter as tk
from tkinter import messagebox, ttk

class QuizGame:
    def __init__(self, master, questions):
        self.master = master
        self.questions = questions
        self.current_question = 0
        self.score = 0
        self.answered = [False] * len(questions)
        self.incorrect_answers = []
        
        master.title("Quiz Game")
        master.geometry("1000x600")
        
        # Question navigation frame
        self.nav_frame = tk.Frame(master)
        self.nav_frame.pack(pady=10)
        
        self.prev_btn = tk.Button(self.nav_frame, text="← Previous", command=self.prev_question)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = tk.Button(self.nav_frame, text="Next →", command=self.next_question)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        self.finish_btn = tk.Button(self.nav_frame, text="Finish Quiz", command=self.finish_quiz)
        self.finish_btn.pack(side=tk.LEFT, padx=5)
        
        # Question display
        self.question_label = tk.Label(master, text="", wraplength=550, font=('Arial', 12))
        self.question_label.pack(pady=20)
        
        # Answer buttons
        self.answer_buttons = []
        for i in range(4):
            btn = tk.Button(master, text="", command=lambda i=i: self.check_answer(i),
                          height=2, width=40)
            btn.pack(pady=5)
            self.answer_buttons.append(btn)
            
        # Progress and score
        self.progress_label = tk.Label(master, text=f"Question {self.current_question + 1} of {len(self.questions)}")
        self.progress_label.pack(pady=5)
        
        self.score_label = tk.Label(master, text=f"Score: {self.score}/{len(self.questions)}", font=('Arial', 12, 'bold'))
        self.score_label.pack(pady=10)
        
        self.update_question_display()
    
    def update_question_display(self):
        q = self.questions[self.current_question]
        self.question_label.config(text=q["question"])
        
        for i, btn in enumerate(self.answer_buttons):
            btn.config(text=q["answers"][i])
            
            # Change color if already answered
            if self.answered[self.current_question]:
                if i == q["correct"]:
                    btn.config(bg='#9fff9f')  # Light green
                elif btn['text'] == self.questions[self.current_question].get("selected_answer", ""):
                    btn.config(bg='#ff9f9f')  # Light red
                else:
                    btn.config(bg='#f0f0f0')  # Light gray
            else:
                btn.config(bg='#f0f0f0')  # Light gray
        
        self.progress_label.config(text=f"Question {self.current_question + 1} of {len(self.questions)}")
        self.score_label.config(text=f"Score: {self.score}/{len(self.questions)}")
        
        # Update nav button states
        self.prev_btn.config(state=tk.NORMAL if self.current_question > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.current_question < len(self.questions) - 1 else tk.DISABLED)
    
    def check_answer(self, choice):
        q = self.questions[self.current_question]
        
        # Store selected answer
        self.questions[self.current_question]["selected_answer"] = q["answers"][choice]
        
        if not self.answered[self.current_question]:
            if choice == q["correct"]:
                self.score += 1
                self.answered[self.current_question] = True
                self.update_question_display()
                # Auto-advance to next question if correct
                if self.current_question < len(self.questions) - 1:
                    self.master.after(1000, self.next_question)  # Advance after 1 second
            else:
                # Add to incorrect answers list
                self.incorrect_answers.append({
                    "question": q["question"],
                    "selected": q["answers"][choice],
                    "correct": q["answers"][q["correct"]]
                })
                self.answered[self.current_question] = True
                self.update_question_display()
        else:
            self.update_question_display()
    
    def next_question(self):
        if self.current_question < len(self.questions) - 1:
            self.current_question += 1
            self.update_question_display()
    
    def prev_question(self):
        if self.current_question > 0:
            self.current_question -= 1
            self.update_question_display()
    
    def finish_quiz(self):
        # Create review window
        review_win = tk.Toplevel(self.master)
        review_win.title("Quiz Results")
        review_win.geometry("700x500")
        
        # Score summary
        tk.Label(review_win, text=f"Final Score: {self.score}/{len(self.questions)}", 
                font=('Arial', 14, 'bold')).pack(pady=10)
        
        if not self.incorrect_answers:
            tk.Label(review_win, text="Congratulations! You got all answers correct!",
                    fg='green').pack(pady=20)
            return
        
        # Incorrect answers review
        tk.Label(review_win, text="Review your incorrect answers:", 
               font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Create a scrollable frame
        canvas = tk.Canvas(review_win)
        scrollbar = ttk.Scrollbar(review_win, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Display incorrect answers
        for i, item in enumerate(self.incorrect_answers):
            frame = tk.Frame(scrollable_frame, bd=2, relief=tk.GROOVE, padx=10, pady=10)
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(frame, text=f"Question {i+1}: {item['question']}", 
                    wraplength=550, justify=tk.LEFT).pack(anchor='w')
            tk.Label(frame, text=f"Your answer: {item['selected']}", 
                    fg='red', wraplength=550, justify=tk.LEFT).pack(anchor='w')
            tk.Label(frame, text=f"Correct answer: {item['correct']}", 
                    fg='green', wraplength=550, justify=tk.LEFT).pack(anchor='w')

# Load questions from JSON
with open('questions.json') as f:
    questions = json.load(f)["questions"]

root = tk.Tk()
app = QuizGame(root, questions)
root.mainloop()