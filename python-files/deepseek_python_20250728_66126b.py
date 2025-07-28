import re

def parse_info_file(file_path):
    items = []
    
    with open(file_path, 'rb') as file:
        content = file.read().decode('utf-8', errors='ignore')
        
        # Разделяем файл на блоки по двойным переводам строки
        blocks = re.split(r'\n\n+', content.strip())
        
        for block in blocks:
            if not block.strip():
                continue
            
            item = {}
            lines = block.split('\n')
            
            # Первая строка — название предмета
            item['name'] = lines[0].strip()
            
            # Вторая строка — описание (если есть)
            if len(lines) > 1:
                item['description'] = lines[1].strip()
            
            # Остальные строки — параметры
            if len(lines) > 2:
                item['stats'] = []
                for line in lines[2:]:
                    line = line.strip()
                    if line:
                        item['stats'].append(line)
            
            items.append(item)
    
    return items

# Пример использования
file_path = 'info.txt'
parsed_items = parse_info_file(file_path)

# Выводим первые 5 предметов для примера
for idx, item in enumerate(parsed_items[:5], 1):
    print(f"🔹 Предмет {idx}:")
    print(f"Название: {item.get('name', 'N/A')}")
    print(f"Описание: {item.get('description', 'N/A')}")
    if 'stats' in item:
        print("Параметры:")
        for stat in item['stats']:
            print(f"- {stat}")
    print("-" * 50)