import re
from collections import defaultdict

def parse_questions(text):
    questions = []
    current_question = None
    current_options = []
    current_answer = None
    question_num = 0
    
    # Предварительная обработка текста
    text = re.sub(r'===== Page \d+ =====', '', text)
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)  # Удаляем управляющие символы
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    for line in lines:
        # Определяем номер вопроса (новый вопрос)
        if re.match(r'^\d+\.', line):
            if current_question is not None:
                questions.append(create_question_dict(current_question, current_options, current_answer))
                current_options = []
            
            question_num += 1
            current_question = line
            current_answer = None
        
        # Варианты ответов (A. ... E.)
        elif re.match(r'^[A-E]\.', line):
            current_options.append(line)
        
        # Ответ (ANSWER: X)
        elif line.startswith('ANSWER:'):
            current_answer = line.split(':')[1].strip()
    
    # Добавляем последний вопрос
    if current_question is not None:
        questions.append(create_question_dict(current_question, current_options, current_answer))
    
    return questions

def create_question_dict(question, options, answer):
    return {
        'question': clean_text(question),
        'options': [clean_text(opt) for opt in options],
        'answer': answer,
        'category': determine_category(question)
    }

def clean_text(text):
    """Очистка текста от лишних пробелов и специальных символов"""
    text = re.sub(r'\s+', ' ', text)  # Заменяем множественные пробелы на один
    return text.strip()

# Словарь категорий с ключевыми словами
CATEGORIES = {
    'bioethics': ['биоэтик', 'эвтанази', 'пациент', 'эксперимент', 'согласие', 'кодекс', 'декларация', 'генн'],
    'medicine': ['медицин', 'врач', 'лечени', 'болезн', 'здоровь', 'больн', 'терапи', 'диагноз'],
    'history': ['истори', 'государств', 'войн', 'цар', 'революци', 'древн', 'средневеков', 'петр', 'иван'],
    'psychology': ['психологи', 'памят', 'мышлен', 'эмоци', 'темперамент', 'восприяти', 'ощущени', 'внимани'],
    'law': ['прав', 'закон', 'суд', 'преступлен', 'дееспособност', 'договор', 'собственност', 'ответственност'],
    'economics': ['экономик', 'рынок', 'товар', 'производств', 'финанс', 'бюджет', 'налог', 'банк'],
    'philosophy': ['философ', 'этик', 'морал', 'нравствен', 'познани', 'истин', 'сознани'],
    'latin': ['латинск', 'рецепт', 'медикамент', 'фармацевт']
}

def determine_category(question):
    """Определяет категорию вопроса на основе ключевых слов"""
    question_lower = question.lower()
    
    for category, keywords in CATEGORIES.items():
        if any(keyword in question_lower for keyword in keywords):
            return category
    
    return 'other'

def format_as_js_array(questions):
    """Форматирует вопросы как массив JavaScript с правильными отступами"""
    js_lines = []
    js_lines.append('const questions = [')
    
    for i, q in enumerate(questions):
        js_lines.append('    {')
        js_lines.append(f'        question: "{q["question"]}",')
        js_lines.append('        options: [')
        
        for opt in q['options']:
            js_lines.append(f'            "{opt}",')
        
        js_lines.append('        ],')
        js_lines.append(f'        answer: "{q["answer"]}",')
        js_lines.append(f'        category: "{q["category"]}"')
        
        # Добавляем запятую для всех элементов, кроме последнего
        js_lines.append('    }' + (',' if i < len(questions)-1 else ''))
    
    js_lines.append('];')
    js_lines.append('')
    js_lines.append(f'// Всего вопросов: {len(questions)}')
    
    return '\n'.join(js_lines)

def analyze_categories(questions):
    """Анализ распределения вопросов по категориям"""
    category_counts = defaultdict(int)
    for q in questions:
        category_counts[q['category']] += 1
    
    print("\nРаспределение вопросов по категориям:")
    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{cat}: {count} вопросов")

def save_to_file(questions, filename):
    """Сохраняет вопросы в файл"""
    js_code = format_as_js_array(questions)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(js_code)
    print(f"\nФайл сохранен: {filename}")

if __name__ == '__main__':
    # Чтение текста из файла
    input_file = 'test_questions.txt'
    output_file = 'questions.js'
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        questions = parse_questions(text)
        analyze_categories(questions)
        save_to_file(questions, output_file)
        
        print("\nПервые 5 вопросов для проверки:")
        for q in questions[:5]:
            print(f"\n{q['question']}")
            for opt in q['options']:
                print(f"  {opt}")
            print(f"Ответ: {q['answer']} | Категория: {q['category']}")
            
    except FileNotFoundError:
        print(f"Ошибка: файл '{input_file}' не найден")
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")