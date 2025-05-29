questions_and_answers = [
    {"question": "Лиза,что делаешь сейчес?",
     "options": ["хуйней страдаю", "Думаю насколько тебе делать нехуй", "План по работе"],
     "next_state": lambda answer: {"Я так и знал": answer}},

    {"question": "Будешь со мной смотреть как сносят Циганские дома?",
     "options": ["Да", "Нет"],
     "next_state": lambda answer: {"О как!! Ок!": True if answer.lower() == "да" else False}}
]

def run_dialog():
    state = {}
    for question_data in questions_and_answers:
        print(question_data["question"])
        options = question_data["options"]
        for idx, option in enumerate(options):
            print(f"{idx + 1}: {option}")
            
        while True:
            user_input = input("Ваш выбор: ").strip()
            if not user_input.isdigit() or int(user_input) < 1 or int(user_input) > len(options):
                print("Некорректный выбор. Попробуйте снова.")
            else:
                break
                
        selected_option = options[int(user_input)-1]
        next_state = question_data["next_state"](selected_option)
        state.update(next_state)
    
    print("\nИтоги:")
    for key, value in state.items():
        print(f"- {key.capitalize()}: {value}")

run_dialog()
print("Лиз,а теперь узбогойся и доверься мне")
input("Нажми Enter для выхода...")