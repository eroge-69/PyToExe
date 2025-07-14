import random
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_questions(filename="formatted_questions.txt"):
    questions_by_block = {}
    current_block = "Без блока"
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
        items = content.split('---')
        for item in items:
            item = item.strip()
            if not item:
                continue
            if item.startswith('### БЛОК:'):
                current_block = item.replace('### БЛОК:', '').replace('###', '').strip()
                if current_block not in questions_by_block:
                    questions_by_block[current_block] = []
            else:
                lines = item.split('\n')
                question = lines[0].replace('Вопрос:', '').strip()
                answer = '\n'.join(lines[1:]).replace('Ответ:', '').strip()
                if current_block not in questions_by_block:
                    questions_by_block[current_block] = []
                questions_by_block[current_block].append({'question': question, 'answer': answer})
    return questions_by_block

def choose_block(blocks):
    clear_screen()
    print("Выберите блок для тестирования:")
    block_names = list(blocks.keys())
    for i, name in enumerate(block_names):
        print(f"{i+1}. {name} ({len(blocks[name])} вопросов)")
    print(f"{len(block_names)+1}. Все вопросы")
    
    while True:
        try:
            choice = int(input(f"Введите номер (1-{len(block_names)+1}): "))
            if 1 <= choice <= len(block_names) + 1:
                if choice == len(block_names) + 1:
                    return [q for b in blocks.values() for q in b] # Flatten all questions
                return blocks[block_names[choice-1]]
        except ValueError:
            pass
        print("Неверный ввод. Пожалуйста, выберите номер из списка.")

def run_test(questions):
    incorrect_answers = []
    random.shuffle(questions)
    for i, q in enumerate(questions):
        clear_screen()
        print(f"Вопрос {i+1}/{len(questions)}")
        print("---")
        print(q['question'])
        print("---")
        input("Нажмите Enter, чтобы увидеть ответ...")
        print(f"Правильный ответ:\n{q['answer']}")
        print("---")
        while True:
            user_evaluation = input("Вы ответили правильно? (y/n): ").lower()
            if user_evaluation in ['y', 'n']:
                break
        if user_evaluation == 'n':
            incorrect_answers.append(q)
    return incorrect_answers

def main():
    base_path = os.path.join(os.path.expanduser("~"), "Desktop")
    questions_file = os.path.join(base_path, "formatted_questions.txt")

    if not os.path.exists(questions_file):
        print(f"Файл с вопросами не найден: {questions_file}")
        return

    questions_by_block = load_questions(questions_file)
    if not questions_by_block:
        print("Не удалось загрузить вопросы. Файл пуст или имеет неверный формат.")
        return

    while True:
        questions_to_test = choose_block(questions_by_block)
        
        while True:
            incorrect = run_test(questions_to_test)
            clear_screen()
            print("Тест завершен!")
            print(f"Всего вопросов: {len(questions_to_test)}")
            print(f"Правильных ответов: {len(questions_to_test) - len(incorrect)}")
            print(f"Неправильных ответов: {len(incorrect)}")

            if not incorrect:
                print("\nПоздравляю! Вы ответили на все вопросы правильно!")
                break
            
            while True:
                retry = input("\nХотите повторить тест только по неправильным ответам? (y/n): ").lower()
                if retry in ['y', 'n']:
                    break
            
            if retry == 'y':
                questions_to_test = incorrect
            else:
                break

        while True:
            another_round = input("\nХотите пройти другой блок? (y/n): ").lower()
            if another_round in ['y', 'n']:
                break
        if another_round == 'n':
            print("Спасибо за использование программы!")
            break

if __name__ == "__main__":
    main()