import os
import sys

def simple_ics_parser(filename):
    """Простой парсер ICS файлов"""
    if not os.path.exists(filename):
        return None, f"Файл {filename} не найден"
    
    events = []
    current_event = {}
    in_event = False
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                if line == 'BEGIN:VEVENT':
                    in_event = True
                    current_event = {}
                elif line == 'END:VEVENT':
                    if in_event and current_event:
                        events.append(current_event)
                    in_event = False
                elif in_event and ':' in line:
                    try:
                        key, value = line.split(':', 1)
                        key = key.split(';')[0]
                        if key in ['SUMMARY', 'DTSTART', 'DTEND', 'ORGANIZER', 'DESCRIPTION']:
                            current_event[key] = value.replace('\\n', ' ')
                    except:
                        continue
                        
    except Exception as e:
        return None, f"Ошибка чтения файла: {e}"
    
    return events, None

def format_date(date_str):
    """Форматирование даты"""
    if not date_str or len(date_str) < 8:
        return date_str
    
    try:
        if 'T' in date_str:
            date_part = date_str[:8]
            time_part = date_str[9:13]
            return f"{date_part[6:8]}.{date_part[4:6]}.{date_part[:4]} {time_part[:2]}:{time_part[2:4]}"
        else:
            return f"{date_str[6:8]}.{date_str[4:6]}.{date_str[:4]}"
    except:
        return date_str

def save_to_csv(events, output_file):
    """Сохранение в CSV без pandas"""
    try:
        with open(output_file, 'w', encoding='utf-8-sig') as f:
            # Заголовок
            f.write("Название;Дата начала;Дата окончания;Организатор;Описание\n")
            
            # Данные
            for event in events:
                title = event.get('SUMMARY', '').replace(';', ',').replace('\n', ' ')
                start = format_date(event.get('DTSTART', ''))
                end = format_date(event.get('DTEND', ''))
                organizer = event.get('ORGANIZER', '').replace('mailto:', '').split(';')[0]
                description = event.get('DESCRIPTION', '')[:100].replace(';', ',').replace('\n', ' ')
                
                f.write(f"{title};{start};{end};{organizer};{description}\n")
        return True
    except Exception as e:
        print(f"Ошибка сохранения: {e}")
        return False

def main():
    """Главная функция - консольная версия"""
    print("=" * 50)
    print("   📅 ICS Calendar Parser (Console)")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # Файл передан как аргумент
        input_file = sys.argv[1]
    else:
        # Запрос имени файла
        input_file = input("\nВведите путь к ICS файлу (или перетащите файл): ").strip('"')
    
    if not input_file:
        input_file = 'calendar.ics'  # По умолчанию
    
    print(f"\n🔍 Обработка файла: {input_file}")
    
    # Парсинг
    events, error = simple_ics_parser(input_file)
    
    if error:
        print(f"❌ {error}")
        input("\nНажмите Enter для выхода...")
        return
    
    print(f"\n✅ Найдено событий: {len(events)}")
    
    # Показываем первые 5 событий
    print(f"\n📋 Первые события:")
    print("-" * 50)
    
    for i, event in enumerate(events[:5], 1):
        title = event.get('SUMMARY', 'Без названия')[:50]
        date = format_date(event.get('DTSTART', ''))
        organizer = event.get('ORGANIZER', '').replace('mailto:', '').split('@')[0]
        
        print(f"{i}. {title}")
        print(f"   📅 {date}")
        if organizer:
            print(f"   👤 {organizer}")
        print()
    
    # Сохранение в CSV
    output_file = input_file.replace('.ics', '_parsed.csv')
    
    if save_to_csv(events, output_file):
        print(f"💾 Результат сохранен в: {output_file}")
    else:
        print("❌ Ошибка сохранения файла")
    
    print(f"\n✨ Обработка завершена!")
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()