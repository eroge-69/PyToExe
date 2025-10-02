from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.oxml.xmlchemy import OxmlElement
import os

def set_hyperlink(shape, url):
    """Устанавливает гиперссылку для фигуры"""
    part = shape.part
    r_id = part.relate_to(url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True)
    
    # Получаем XML элемент текста
    txBody = shape._element.get_or_add_txBody()
    p = txBody.get_or_add_p()
    r = p.get_or_add_r()
    
    # Создаем элемент гиперссылки
    hyperlink = OxmlElement('a:hlinkClick')
    hyperlink.set('xmlns:r', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships')
    hyperlink.set('r:id', r_id)
    
    # Добавляем гиперссылку к тексту
    rPr = r.get_or_add_rPr()
    rPr.append(hyperlink)

def add_hyperlink_to_text(shape, text, url):
    """Добавляет гиперссылку к определенному тексту в фигуре"""
    text_frame = shape.text_frame
    text_frame.text = text
    
    # Устанавливаем гиперссылку для всей фигуры
    set_hyperlink(shape, url)

class Question:
    def __init__(self, text, answer, points, category):
        self.text = text
        self.answer = answer
        self.points = points
        self.category = category

def create_quiz_presentation():
    # Создаем новую презентацию
    prs = Presentation()
    
    # Запрашиваем количество вопросов
    while True:
        try:
            num_questions = int(input("Введите количество вопросов для викторины: "))
            if num_questions > 0:
                break
            else:
                print("Количество вопросов должно быть положительным числом.")
        except ValueError:
            print("Пожалуйста, введите целое число.")
    
    questions = []
    categories = set()
    
    # Собираем вопросы и ответы
    print("\n" + "="*50)
    print("ВВОД ВОПРОСОВ И ОТВЕТОВ")
    print("="*50)
    
    for i in range(num_questions):
        print(f"\n--- Вопрос {i+1} ---")
        category = input("Введите тему/категорию вопроса: ")
        question_text = input("Введите вопрос: ")
        answer = input("Введите ответ: ")
        
        while True:
            try:
                points = int(input("Введите количество баллов за вопрос: "))
                if points > 0:
                    break
                else:
                    print("Количество баллов должно быть положительным числом.")
            except ValueError:
                print("Пожалуйста, введите целое число.")
        
        questions.append(Question(question_text, answer, points, category))
        categories.add(category)
    
    # Создаем титульный слайд
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    
    title.text = "ВИКТОРИНА"
    subtitle.text = f"Количество вопросов: {num_questions}\nОбщее количество баллов: {sum(q.points for q in questions)}\nУдачи!"
    
    # Создаем главный экран с содержанием
    content_slide_layout = prs.slide_layouts[1]
    content_slide = prs.slides.add_slide(content_slide_layout)
    content_title = content_slide.shapes.title
    content_title.text = "Содержание викторины"
    
    # Группируем вопросы по категориям
    questions_by_category = {}
    for question in questions:
        if question.category not in questions_by_category:
            questions_by_category[question.category] = []
        questions_by_category[question.category].append(question)
    
    # Создаем текст для содержания
    content_text = ""
    for category in sorted(questions_by_category.keys()):
        content_text += f"\n{category}:\n"
        for question in questions_by_category[category]:
            content_text += f"  • {question.text[:50]}... ({question.points} баллов)\n"
    
    content_body = content_slide.placeholders[1]
    content_body.text = content_text
    
    # Создаем слайды с вопросами и ответами
    question_slides = {}
    answer_slides = {}
    
    for i, question in enumerate(questions, 1):
        # Слайд с вопросом
        blank_slide_layout = prs.slide_layouts[6]
        question_slide = prs.slides.add_slide(blank_slide_layout)
        
        # Добавляем заголовок с номером вопроса
        title_box = question_slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.8))
        title_frame = title_box.text_frame
        title_frame.text = f"Вопрос {i} • {question.category} • {question.points} баллов"
        title_paragraph = title_frame.paragraphs[0]
        title_paragraph.font.size = Pt(20)
        title_paragraph.font.bold = True
        title_paragraph.font.color.rgb = RGBColor(0, 0, 128)
        title_paragraph.alignment = PP_ALIGN.CENTER
        
        # Добавляем вопрос
        question_box = question_slide.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(9), Inches(3))
        question_frame = question_box.text_frame
        question_frame.text = question.text
        question_paragraph = question_frame.paragraphs[0]
        question_paragraph.font.size = Pt(24)
        question_paragraph.font.bold = True
        question_paragraph.alignment = PP_ALIGN.CENTER
        
        # Добавляем кнопку "Показать ответ"
        answer_button = question_slide.shapes.add_textbox(Inches(3), Inches(4.5), Inches(3), Inches(0.6))
        answer_frame = answer_button.text_frame
        answer_frame.text = "Показать ответ"
        answer_paragraph = answer_frame.paragraphs[0]
        answer_paragraph.font.size = Pt(16)
        answer_paragraph.font.bold = True
        answer_paragraph.font.color.rgb = RGBColor(255, 255, 255)
        answer_paragraph.alignment = PP_ALIGN.CENTER
        
        # Заливаем кнопку цветом
        fill = answer_button.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(0, 100, 0)
        
        line = answer_button.line
        line.color.rgb = RGBColor(0, 80, 0)
        line.width = Pt(2)
        
        question_slides[i] = question_slide
        
        # Слайд с ответом
        answer_slide = prs.slides.add_slide(blank_slide_layout)
        
        # Добавляем заголовок
        title_box = answer_slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.8))
        title_frame = title_box.text_frame
        title_frame.text = f"Ответ на вопрос {i} • {question.points} баллов"
        title_paragraph = title_frame.paragraphs[0]
        title_paragraph.font.size = Pt(20)
        title_paragraph.font.bold = True
        title_paragraph.font.color.rgb = RGBColor(0, 100, 0)
        title_paragraph.alignment = PP_ALIGN.CENTER
        
        # Добавляем вопрос (для контекста)
        question_ref_box = answer_slide.shapes.add_textbox(Inches(0.5), Inches(1.1), Inches(9), Inches(1.2))
        question_ref_frame = question_ref_box.text_frame
        question_ref_frame.text = f"Вопрос: {question.text}"
        question_ref_paragraph = question_ref_frame.paragraphs[0]
        question_ref_paragraph.font.size = Pt(14)
        question_ref_paragraph.font.italic = True
        question_ref_paragraph.font.color.rgb = RGBColor(128, 128, 128)
        
        # Добавляем ответ
        answer_box = answer_slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(9), Inches(2))
        answer_frame = answer_box.text_frame
        answer_frame.text = question.answer
        answer_paragraph = answer_frame.paragraphs[0]
        answer_paragraph.font.size = Pt(28)
        answer_paragraph.font.bold = True
        answer_paragraph.font.color.rgb = RGBColor(0, 100, 0)
        answer_paragraph.alignment = PP_ALIGN.CENTER
        
        # Добавляем кнопку "Вернуться к вопросу"
        back_button = answer_slide.shapes.add_textbox(Inches(3), Inches(4.5), Inches(3), Inches(0.6))
        back_frame = back_button.text_frame
        back_frame.text = "Вернуться к вопросу"
        back_paragraph = back_frame.paragraphs[0]
        back_paragraph.font.size = Pt(14)
        back_paragraph.font.bold = True
        back_paragraph.font.color.rgb = RGBColor(255, 255, 255)
        back_paragraph.alignment = PP_ALIGN.CENTER
        
        # Заливаем кнопку цветом
        fill = back_button.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(0, 0, 128)
        
        line = back_button.line
        line.color.rgb = RGBColor(0, 0, 100)
        line.width = Pt(2)
        
        answer_slides[i] = answer_slide
    
    # Создаем слайд с таблицей баллов по категориям
    stats_slide_layout = prs.slide_layouts[1]
    stats_slide = prs.slides.add_slide(stats_slide_layout)
    stats_title = stats_slide.shapes.title
    stats_title.text = "Распределение баллов по категориям"
    
    # Считаем баллы по категориям
    category_points = {}
    for question in questions:
        if question.category not in category_points:
            category_points[question.category] = 0
        category_points[question.category] += question.points
    
    stats_text = ""
    total_points = sum(category_points.values())
    for category, points in sorted(category_points.items(), key=lambda x: x[1], reverse=True):
        percentage = (points / total_points) * 100
        stats_text += f"\n{category}: {points} баллов ({percentage:.1f}%)"
    
    stats_body = stats_slide.placeholders[1]
    stats_body.text = f"Всего баллов: {total_points}\n{stats_text}"
    
    # Создаем заключительный слайд
    final_slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(final_slide_layout)
    title = slide.shapes.title
    content = slide.placeholders[1]
    
    title.text = "Викторина завершена!"
    content.text = f"Поздравляем с завершением викторины!\n\nМаксимально возможный результат: {total_points} баллов\n\nСпасибо за участие!"
    
    # Сохраняем презентацию
    filename = "викторина_с_гиперссылками.pptx"
    prs.save(filename)
    
    print(f"\n" + "="*50)
    print(f"Презентация успешно создана!")
    print(f"Файл: {filename}")
    print(f"Расположение: {os.path.abspath(filename)}")
    print(f"Всего слайдов: {len(prs.slides)}")
    print(f"Категории: {', '.join(sorted(categories))}")
    print(f"Общее количество баллов: {total_points}")
    print("="*50)
    
    # Выводим инструкцию по использованию
    print("\nИНСТРУКЦИЯ:")
    print("1. Запустите презентацию в режиме показа слайдов")
    print("2. На главном экране вы увидите все вопросы по категориям")
    print("3. Используйте кнопки для навигации между вопросами и ответами")
    print("4. Каждый вопрос показывает количество баллов за правильный ответ")

def main():
    print("СОЗДАНИЕ ВИКТОРИНЫ С ГИПЕРССЫЛКАМИ И БАЛЛАМИ")
    print("=" * 50)
    
    try:
        create_quiz_presentation()
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        print("Убедитесь, что установлены все необходимые библиотеки:")
        print("pip install python-pptx")

if __name__ == "__main__":
    main()