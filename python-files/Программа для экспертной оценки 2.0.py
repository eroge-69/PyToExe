import tkinter as tk
from tkinter import messagebox

class ExpertRatingApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Экспертная оценка программного продукта")

        self.num_experts = 0
        self.num_criteria = 0
        self.ratings = []

        tk.Label(master, text="Количество экспертов:").grid(row=0, column=0)
        self.experts_entry = tk.Entry(master)
        self.experts_entry.grid(row=0, column=1)

        tk.Label(master, text="Количество критериев:").grid(row=1, column=0)
        self.criteria_entry = tk.Entry(master)
        self.criteria_entry.grid(row=1, column=1)

        self.start_button = tk.Button(master, text="Начать", command=self.start)
        self.start_button.grid(row=2, columnspan=2)

        self.rating_frame = None

    def start(self):
        try:
            self.num_experts = int(self.experts_entry.get())
            self.num_criteria = int(self.criteria_entry.get())
            if self.num_experts <= 0 or self.num_criteria <= 0:
                raise ValueError("Число экспертов и критериев должно быть положительным.")
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
            return

        self.ratings = []
        self.rating_frame = tk.Frame(self.master)
        self.rating_frame.grid(row=3, columnspan=2)

        for i in range(self.num_experts):
            tk.Label(self.rating_frame, text=f"Эксперт {i + 1}:").grid(row=i, column=0)
            expert_ratings = []
            for j in range(self.num_criteria):
                entry = tk.Entry(self.rating_frame, validate="key")
                entry['validatecommand'] = (entry.register(self.validate_float), '%P')
                entry.grid(row=i, column=j + 1)
                expert_ratings.append(entry)
            self.ratings.append(expert_ratings)

        submit_button = tk.Button(self.rating_frame, text="Подсчитать веса", command=self.calculate_weights)
        submit_button.grid(row=self.num_experts, columnspan=self.num_criteria + 1)

    def validate_float(self, text):
        if text == "":
            return True
        try:
            float(text)
            return True
        except ValueError:
            return False

    def calculate_weights(self):
        try:
            ratings = []
            for expert_ratings in self.ratings:
                expert_scores = []
                for entry in expert_ratings:
                    score = float(entry.get())
                    if score < 1 or score > 10:
                        raise ValueError("Оценка должна быть от 1 до 10.")
                    expert_scores.append(score)
                ratings.append(expert_scores)

            weights = self.get_weights(ratings)
            self.display_weights(weights)
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))

    def get_weights(self, ratings):
        num_experts = len(ratings)
        num_criteria = len(ratings[0])
        
        total_ratings = [0.0] * num_criteria
        for expert_ratings in ratings:
            for j in range(num_criteria):
                total_ratings[j] += expert_ratings[j]

        weights = [total / (num_experts * 10) for total in total_ratings]
        return weights

    def display_weights(self, weights):
        result_window = tk.Toplevel(self.master)
        result_window.title("Итоговые веса")

        tk.Label(result_window, text="Итоговые веса (экспертные оценки) для каждого критерия:").pack()
        for i, weight in enumerate(weights):
            tk.Label(result_window, text=f"Критерий {i + 1}: {weight:.4f}").pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpertRatingApp(root)
    root.mainloop()
