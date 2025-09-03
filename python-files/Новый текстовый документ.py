def conduct_survey():
    print("Добро пожаловать в опрос!\n")
    
    questions = [
        "Шкурка от какого овоща была на залупе?",
        "За сколько рублей Павел Депутат дал в рот бомжихе?",
        "Чего нет в московском метро?",
        "Что случилось с мужиком в московском метро?",
        "Сколько лет было на самом деле проститутке которая говорила что ей 45, и обосрала диван?"
    ]
    
    answers = []
    
    for i, question in enumerate(questions, 1):
        print(f"{i}. {question}")
        answer = input("Ваш ответ: ")
        answers.append(answer)
        print()
    
    # Вывод результатов
    print("\n" + "="*50)
    print("Результаты опроса:")
    print("="*50)
    
    for i, (question, answer) in enumerate(zip(questions, answers), 1):
        print(f"{i}. {question}")
        print(f"   Ответ: {answer}\n")

if __name__ == "__main__":
    conduct_survey()
