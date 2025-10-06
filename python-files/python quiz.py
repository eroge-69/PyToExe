import tkinter as tk
from tkinter import messagebox
import os
import platform

class DeathQuiz:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ВИКТОРИНА СМЕРТИ")
        self.root.geometry("500x300")
        self.root.configure(bg='black')
        
        self.questions = [
            {"question": "Составьте слово из букв: НКУЛО ТЙПУО", "answer": "КЛОУН ТУПОЙ"},
            {"question": "49620+34456=?(без калькулятора)", "answer": "84076"},
            {"question": "Сколько строчек в этом коде?", "answer": "106"}
        ]
        self.current_question = 0
        
        self.create_widgets()
    
    def create_widgets(self):
        self.label = tk.Label(
            self.root, 
            text=self.questions[self.current_question]["question"],
            font=("Arial", 16),
            fg='red',
            bg='black'
        )
        self.label.pack(pady=20)
        
        self.entry = tk.Entry(
            self.root,
            font=("Arial", 14),
            justify='center'
        )
        self.entry.pack(pady=10)
        self.entry.bind('<Return>', self.check_answer)
        
        self.button = tk.Button(
            self.root,
            text="ОТВЕТИТЬ",
            font=("Arial", 14),
            command=self.check_answer,
            bg='red',
            fg='white'
        )
        self.button.pack(pady=10)
        
        self.warning_label = tk.Label(
            self.root,
            text="НЕПРАВИЛЬНЫЙ ОТВЕТ = УДАЛЮ МАЙН!",
            font=("Arial", 10),
            fg='yellow',
            bg='black'
        )
        self.warning_label.pack(pady=20)
    
    def shutdown(self):
        system = platform.system()
        if system == "Windows":
            os.system("shutdown /s /t 5")
        elif system == "Linux":
            os.system("shutdown -h now")
        elif system == "Darwin":
            os.system("sudo shutdown -h now")
    
    def check_answer(self, event=None):
        user_answer = self.entry.get().strip()
        correct_answer = self.questions[self.current_question]["answer"]
        
        if user_answer.lower() != correct_answer.lower():
            messagebox.showerror("НЕВЕРНО!", f"Правильный ответ: {correct_answer}\nКомпьютер выключится через 5 секунд!")
            self.shutdown()
            return
        
        self.current_question += 1
        
        if self.current_question < len(self.questions):
            self.label.config(text=self.questions[self.current_question]["question"])
            self.entry.delete(0, tk.END)
        else:
            messagebox.showinfo("ПОБЕДА!", "Ты читер ебаный учись играть!")
            self.root.destroy()
    
    def run(self):
        self.root.mainloop()

# ЗАПУСК ПРОГРАММЫ
if __name__ == "__main__":
    # Предварительное окно для предупреждения
    pre_root = tk.Tk()
    pre_root.withdraw()
    
    if messagebox.askokcancel("ТОЧНО ХОЧЕШЬ ПОИГРАТЬ?", 
        "ВЫ ДАУН ЕСЛИ НЕ ПРОЙДЕТЕ ЭТО!\n\n"
        "Ты точно не проёбанный даун и хочешь это запустить?"):
        
        pre_root.destroy()
        quiz = DeathQuiz()
        quiz.run()
    else:
        messagebox.showinfo("Отменено", "Иди нахуй, трус!")
        pre_root.destroy()
