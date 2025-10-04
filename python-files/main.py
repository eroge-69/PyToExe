import xml.etree.ElementTree as ET
import pandas as pd
import csv
import random
from datetime import datetime

class TimetableConverter:
    def __init__(self):
        self.lesson_id_counter = 1
        
    def parse_complex_xml(self, xml_file):
        """
        Парсит сложную структуру XML расписания
        """
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            print("XML файл успешно загружен")
        except FileNotFoundError:
            print("XML файл не найден, создаем демо-данные...")
            return self.create_complex_demo_timetable()
        except ET.ParseError:
            print("Ошибка парсинга XML, создаем демо-данные...")
            return self.create_complex_demo_timetable()
        
        timetable_data = []
        
        # Обрабатываем различные возможные структуры XML
        for class_elem in root.findall('.//class') + root.findall('.//grade') + root.findall('.//group'):
            class_name = class_elem.get('name') or class_elem.get('id') or 'Unknown'
            
            for day_elem in class_elem.findall('day') + class_elem.findall('weekday'):
                day_name = day_elem.get('name') or day_elem.get('day') or 'Unknown'
                
                for lesson_elem in day_elem.findall('lesson') + day_elem.findall('subject'):
                    lesson_data = self.extract_lesson_data(lesson_elem, class_name, day_name)
                    if lesson_data:
                        timetable_data.append(lesson_data)
        
        return timetable_data
    
    def extract_lesson_data(self, lesson_elem, class_name, day_name):
        """Извлекает данные урока из XML элемента"""
        lesson_number = lesson_elem.get('number') or lesson_elem.get('order') or '1'
        subject = lesson_elem.get('subject') or lesson_elem.get('name') or 'Предмет'
        teacher = lesson_elem.get('teacher') or lesson_elem.get('teacher_name') or 'Учитель'
        classroom = lesson_elem.get('classroom') or lesson_elem.get('room') or '101'
        
        return {
            'Урок_ID': self.lesson_id_counter,
            'Класс': class_name,
            'День': day_name,
            'Урок': lesson_number,
            'Предмет': subject,
            'Учитель': teacher,
            'Кабинет': classroom
        }
        self.lesson_id_counter += 1
    
    def create_complex_demo_timetable(self):
        """Создает комплексное демо-расписание"""
        demo_data = []
        
        classes = ["5А", "5Б", "6А", "6Б", "7А", "7Б", "8А", "8Б", "9А", "9Б", "10А", "10Б", "11А", "11Б"]
        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]
        subjects = [
            "Математика", "Русский язык", "Физика", "Химия", "История", 
            "География", "Биология", "Английский язык", "Информатика", 
            "Физкультура", "Литература", "Обществознание"
        ]
        teachers = [
            "Иванова А.П.", "Петров С.И.", "Сидорова М.В.", "Козлов Д.Н.", 
            "Николаева Е.С.", "Федоров П.К.", "Морозова О.Л.", "Волков А.М."
        ]
        classrooms = ["101", "102", "103", "104", "201", "202", "203", "204", "301", "302", "спортзал", "комп. класс"]
        
        self.lesson_id_counter = 1
        
        for class_name in classes:
            for day in days:
                lessons_per_day = random.randint(5, 7)
                
                for lesson_num in range(1, lessons_per_day + 1):
                    subject = random.choice(subjects)
                    teacher = random.choice(teachers)
                    classroom = random.choice(classrooms)
                    
                    demo_data.append({
                        'Урок_ID': self.lesson_id_counter,
                        'Класс': class_name,
                        'День': day,
                        'Урок': lesson_num,
                        'Предмет': subject,
                        'Учитель': teacher,
                        'Кабинет': classroom
                    })
                    self.lesson_id_counter += 1
        
        return demo_data
    
    def generate_csv_timetable(self, xml_file="timetable.xml", output_file="timetable_complete.csv"):
        """Основная функция генерации CSV расписания"""
        
        # Парсим XML
        timetable_data = self.parse_complex_xml(xml_file)
        
        # Создаем CSV данные
        csv_data = []
        headers = [
            "Урок_ID", "Предмет", "Классы", "Группы", "Учителя", "Кабинеты",
            "Периодов_в_карточке", "Периодов_в_неделю", "Дни", "Недели", "Семестры", "Вместимость"
        ]
        csv_data.append(headers)
        
        for lesson in timetable_data:
            csv_row = [
                lesson.get('Урок_ID', ''),
                lesson.get('Предмет', ''),
                lesson.get('Класс', ''),
                "",  # Группы
                lesson.get('Учитель', ''),
                lesson.get('Кабинет', ''),  # Кабинет после каждого урока
                1,   # Периодов_в_карточке
                random.randint(1, 3),  # Периодов_в_неделю
                lesson.get('День', ''),
                random.randint(1, 4),  # Недели
                random.choice([1, 2]),  # Семестры
                random.randint(20, 30)  # Вместимость
            ]
            csv_data.append(csv_row)
        
        # Сохраняем CSV
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerows(csv_data)
        
        print(f"\n✅ Расписание сохранено в: {output_file}")
        print(f"📊 Обработано уроков: {len(timetable_data)}")
        
        # Выводим статистику
        self.print_statistics(timetable_data)
        
        return output_file
    
    def print_statistics(self, timetable_data):
        """Выводит статистику расписания"""
        if not timetable_data:
            return
            
        classes = set(lesson['Класс'] for lesson in timetable_data if 'Класс' in lesson)
        days = set(lesson['День'] for lesson in timetable_data if 'День' in lesson)
        subjects = set(lesson['Предмет'] for lesson in timetable_data if 'Предмет' in lesson)
        
        print(f"\n📈 Статистика расписания:")
        print(f"• Классы: {len(classes)}")
        print(f"• Дни недели: {', '.join(sorted(days))}")
        print(f"• Предметы: {len(subjects)}")
        print(f"• Всего уроков: {len(timetable_data)}")

# Запуск программы
if __name__ == "__main__":
    converter = TimetableConverter()
    converter.generate_csv_timetable()
