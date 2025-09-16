import tkinter as tk
from tkinter import messagebox

class ResultTracker:
    def __init__(self):
        self.history = []
        self.previous = None
        self.best_accuracy = None
        self.best_hits = None
        self.best_reaction = None
        
        self.root = tk.Tk()
        self.root.title("Трекер результатов")
        self.root.configure(bg='white')
        
        self.create_widgets()
        
    def create_widgets(self):
        # Поля ввода
        tk.Label(self.root, text="Точность (%):", bg='white', fg='black').grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.accuracy_entry = tk.Entry(self.root)
        self.accuracy_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(self.root, text="Попадание:", bg='white', fg='black').grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.hits_entry = tk.Entry(self.root)
        self.hits_entry.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(self.root, text="Реакция (мс):", bg='white', fg='black').grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.reaction_entry = tk.Entry(self.root)
        self.reaction_entry.grid(row=2, column=1, padx=10, pady=5)
        
        # Кнопка сохранения
        save_btn = tk.Button(self.root, text="Сохранить", command=self.save_results, bg='white', fg='black')
        save_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Фрейм для лучших результатов
        best_frame = tk.LabelFrame(self.root, text="Лучшие результаты", bg='white', fg='black')
        best_frame.grid(row=0, column=2, rowspan=4, padx=10, pady=5, sticky='n')
        
        self.best_accuracy_label = tk.Label(best_frame, text="Точность: -", bg='white', fg='black')
        self.best_accuracy_label.pack(padx=10, pady=2, anchor='w')
        
        self.best_hits_label = tk.Label(best_frame, text="Попадания: -", bg='white', fg='black')
        self.best_hits_label.pack(padx=10, pady=2, anchor='w')
        
        self.best_reaction_label = tk.Label(best_frame, text="Реакция: -", bg='white', fg='black')
        self.best_reaction_label.pack(padx=10, pady=2, anchor='w')
        
        # Поле для истории
        self.history_text = tk.Text(self.root, height=15, width=70, bg='white', fg='black')
        self.history_text.grid(row=4, column=0, columnspan=3, padx=10, pady=10)
        
        # Кнопка сброса лучших результатов
        reset_btn = tk.Button(self.root, text="Сбросить лучшие результаты", command=self.reset_best_results, bg='white', fg='black')
        reset_btn.grid(row=5, column=0, columnspan=3, pady=5)
    
    def reset_best_results(self):
        self.best_accuracy = None
        self.best_hits = None
        self.best_reaction = None
        self.update_best_labels()
        messagebox.showinfo("Сброс", "Лучшие результаты сброшены!")
        
    def update_best_labels(self):
        # Обновляем метки лучших результатов
        accuracy_text = f"Точность: {self.best_accuracy}%" if self.best_accuracy is not None else "Точность: -"
        hits_text = f"Попадания: {self.best_hits}" if self.best_hits is not None else "Попадания: -"
        reaction_text = f"Реакция: {self.best_reaction} мс" if self.best_reaction is not None else "Реакция: -"
        
        self.best_accuracy_label.config(text=accuracy_text)
        self.best_hits_label.config(text=hits_text)
        self.best_reaction_label.config(text=reaction_text)
        
    def save_results(self):
        try:
            accuracy = int(self.accuracy_entry.get())
            hits = int(self.hits_entry.get())
            reaction = int(self.reaction_entry.get())
            
            # Проверяем на лучшие результаты
            if self.best_accuracy is None or accuracy > self.best_accuracy:
                self.best_accuracy = accuracy
                
            if self.best_hits is None or hits > self.best_hits:
                self.best_hits = hits
                
            if self.best_reaction is None or reaction < self.best_reaction:
                self.best_reaction = reaction
            
            current = (accuracy, hits, reaction)
            self.history.append(current)
            
            # Очистка полей ввода
            self.accuracy_entry.delete(0, tk.END)
            self.hits_entry.delete(0, tk.END)
            self.reaction_entry.delete(0, tk.END)
            
            self.update_display()
            self.update_best_labels()
            self.previous = current
            
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числовые значения")
    
    def update_display(self):
        self.history_text.delete(1.0, tk.END)
        
        for i, result in enumerate(self.history):
            acc, hits, react = result
            
            # Определяем, является ли результат лучшим
            is_best_acc = acc == self.best_accuracy
            is_best_hits = hits == self.best_hits
            is_best_react = react == self.best_reaction
            
            if i == 0:
                line = f"Точность - {acc}%"
                if is_best_acc:
                    line += " ★"  # Добавляем звездочку для лучшего результата
                
                line += f"\nПопадание - {hits}"
                if is_best_hits:
                    line += " ★"
                
                line += f"\nРеакция - {react} мс"
                if is_best_react:
                    line += " ★"
                
                self.history_text.insert(tk.END, line + "\n")
                self.history_text.insert(tk.END, "-" * 40 + "\n")
            else:
                prev_acc, prev_hits, prev_react = self.history[i-1]
                diff_acc = acc - prev_acc
                diff_hits = hits - prev_hits
                diff_react = react - prev_react
                
                line = f"Точность - {acc}% ({diff_acc:+}%)"
                if is_best_acc:
                    line += " ★"
                
                line += f"\nПопадание - {hits} ({diff_hits:+})"
                if is_best_hits:
                    line += " ★"
                
                line += f"\nРеакция - {react} мс ({diff_react:+} мс)"
                if is_best_react:
                    line += " ★"
                
                self.history_text.insert(tk.END, line + "\n")
                self.history_text.insert(tk.END, "-" * 40 + "\n")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ResultTracker()
    app.run()