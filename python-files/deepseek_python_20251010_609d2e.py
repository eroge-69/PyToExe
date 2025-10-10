import os
import re
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
import argparse

class HTMLExtractor:
    def __init__(self):
        self.results = []
    
    def extract_from_file(self, file_path, patterns):
        """
        Извлекает данные из одного HTML файла
        
        Args:
            file_path: путь к HTML файлу
            patterns: словарь с паттернами для поиска
                     {'название_поля': 'css_селектор или regex'}
        
        Returns:
            словарь с найденными значениями
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='cp1251') as file:
                content = file.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        extracted_data = {'file_name': os.path.basename(file_path)}
        
        for field_name, pattern in patterns.items():
            # Если паттерн - CSS селектор
            if pattern.startswith('//') or pattern.startswith('.') or pattern.startswith('#'):
                elements = soup.select(pattern)
                if elements:
                    extracted_data[field_name] = elements[0].get_text(strip=True)
                else:
                    extracted_data[field_name] = None
            # Если паттерн - регулярное выражение
            else:
                match = re.search(pattern, content)
                if match:
                    extracted_data[field_name] = match.group(1) if match.groups() else match.group(0)
                else:
                    extracted_data[field_name] = None
        
        return extracted_data
    
    def extract_from_directory(self, directory, patterns, file_extension='.html'):
        """
        Извлекает данные из всех HTML файлов в директории
        """
        directory_path = Path(directory)
        html_files = list(directory_path.glob(f'*{file_extension}'))
        
        print(f"Найдено {len(html_files)} файлов для обработки...")
        
        for file_path in html_files:
            print(f"Обрабатывается: {file_path.name}")
            result = self.extract_from_file(file_path, patterns)
            self.results.append(result)
        
        return self.results
    
    def save_to_csv(self, output_file='extracted_data.csv'):
        """Сохраняет результаты в CSV файл"""
        if self.results:
            df = pd.DataFrame(self.results)
            df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"Результаты сохранены в {output_file}")
        else:
            print("Нет данных для сохранения")
    
    def save_to_excel(self, output_file='extracted_data.xlsx'):
        """Сохраняет результаты в Excel файл"""
        if self.results:
            df = pd.DataFrame(self.results)
            df.to_excel(output_file, index=False)
            print(f"Результаты сохранены в {output_file}")
        else:
            print("Нет данных для сохранения")

# Примеры паттернов для разных задач
PATTERN_EXAMPLES = {
    # Пример 1: Извлечение заголовков
    'title_extraction': {
        'title': 'title',
        'h1': 'h1',
        'meta_title': 'meta[name="title"]'
    },
    
    # Пример 2: Извлечение мета-тегов
    'meta_extraction': {
        'description': 'meta[name="description"]',
        'keywords': 'meta[name="keywords"]',
        'viewport': 'meta[name="viewport"]'
    },
    
    # Пример 3: Извлечение ссылок
    'links_extraction': {
        'all_links': 'a[href]'
    },
    
    # Пример 4: Извлечение с помощью регулярных выражений
    'regex_extraction': {
        'emails': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phones': r'[\+]?[7-8]?[\(]?[0-9]{3}[\)]?[-\s]?[0-9]{3}[-\s]?[0-9]{2}[-\s]?[0-9]{2}',
        'prices': r'(\d+[\,\.]?\d*)\s*(руб|р|USD|\$)'
    }
}

def main():
    parser = argparse.ArgumentParser(description='Извлечение данных из HTML файлов')
    parser.add_argument('directory', help='Директория с HTML файлами')
    parser.add_argument('--output', '-o', default='extracted_data', help='Имя выходного файла (без расширения)')
    parser.add_argument('--pattern', '-p', choices=list(PATTERN_EXAMPLES.keys()), 
                       help='Предустановленные паттерны для извлечения')
    
    args = parser.parse_args()
    
    extractor = HTMLExtractor()
    
    # Выбор паттернов
    if args.pattern:
        patterns = PATTERN_EXAMPLES[args.pattern]
        print(f"Используется предустановленный паттерн: {args.pattern}")
    else:
        # Создайте свои паттерны здесь
        patterns = {
            'title': 'title',
            'h1': 'h1',
            'description': 'meta[name="description"]'
        }
        print("Используются стандартные паттерны")
    
    # Извлечение данных
    results = extractor.extract_from_directory(args.directory, patterns)
    
    # Сохранение результатов
    extractor.save_to_csv(f"{args.output}.csv")
    extractor.save_to_excel(f"{args.output}.xlsx")
    
    # Вывод статистики
    print(f"\nОбработано файлов: {len(results)}")
    if results:
        print("Пример извлеченных данных:")
        for key, value in results[0].items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    main()