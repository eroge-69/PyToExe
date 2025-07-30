import random
import tkinter as tk
from tkinter import ttk

def get_answer():
    try:
        # Списки ответов с правильным форматированием
        positive = ("Определённо да", "Без сомнения да",
                   "Предсказание благоприятное", "Вы можете на это рассчитывать")
        hesitant = ("Вероятнее всего да", "Признаки говорят 'да'",
                   "Перспективы хорошие", "Я так думаю")
        neutral = ("Спросите позже", "Сейчас я не могу дать ответ",
                  "Сосредоточьтесь и спросите снова", "Перспективы неопределённые")
        negative = ("Нет", "Мой ответ — нет",
                   "Очень сомнительно", "Не рассчитывайте на это")
        
        # Объединение ответов
        all_responses = positive + hesitant + neutral + negative
        response = random.choice(all_responses)
        
        # Определение цвета
        color = "black"
        if response in positive:
            color = "green"
        elif response in hesitant:
            color = "#FFA500"
        elif response in negative:
            color = "red"
        
        # Обновление интерфейса
        answer_label.config(text=response, foreground=color)
        
    except Exception as e:
        answer_label.config(text=f"Ошибка: {str(e)}", foreground="red")

# Создание интерфейса
root = tk.Tk()
root.title("Магический шар 8")
root.geometry("400x300")
root.resizable(False, False)

style = ttk.Style()
style.configure("TButton", font=("Arial", 12), padding=10)
style.configure("TLabel", font=("Arial", 14))

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(expand=True, fill="both")

ttk.Label(main_frame, 
         text="Задайте вопрос Магическому шару:", 
         wraplength=300).pack(pady=10)

ttk.Entry(main_frame, width=30, font=("Arial", 12)).pack(pady=5)

ttk.Button(main_frame, 
          text="Получить ответ", 
          command=get_answer).pack(pady=15)

answer_label = ttk.Label(main_frame, 
                        text="", 
                        font=("Arial", 14, "bold"),
                        wraplength=350)
answer_label.pack()

root.mainloop()
