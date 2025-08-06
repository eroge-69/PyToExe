import time
import random
import os
import sys

def clear_screen():
    """Очистить экран"""
    os.system('cls' if os.name == 'nt' else 'clear')

def type_text(text, delay=0.03):
    """Печать текста с эффектом печатной машинки"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def loading_bar(duration=3, description=""):
    """Реалистичная анимированная полоса загрузки с эффектами"""
    print(f"{description}")
    
    # Фаза 1: Медленный старт
    for i in range(15):
        progress = int((i / 15) * 30)
        bar = "█" * (progress // 3) + "▓" * min(2, 10 - progress // 3) + "░" * max(0, 8 - progress // 3)
        percentage = int((i / 15) * 30)
        
        # Добавляем мерцающий эффект
        if random.random() < 0.3:
            bar = bar.replace("▓", "▒")
        
        print(f"\r[{bar}] {percentage}% {'.' * (i % 4)}", end='', flush=True)
        time.sleep(duration / 40)
    
    # Фаза 2: Ускорение
    for i in range(15, 35):
        progress = 30 + int(((i - 15) / 20) * 50)
        bar_filled = progress // 5
        bar_loading = min(2, 20 - bar_filled) if bar_filled < 20 else 0
        bar_empty = max(0, 20 - bar_filled - bar_loading)
        
        bar = "█" * bar_filled + "▓" * bar_loading + "░" * bar_empty
        
        # Случайные глитчи
        if random.random() < 0.1:
            glitch_pos = random.randint(0, len(bar) - 1)
            bar = bar[:glitch_pos] + random.choice("▒▓█") + bar[glitch_pos + 1:]
        
        print(f"\r[{bar}] {progress}% {'▶' if i % 2 else '▷'}", end='', flush=True)
        time.sleep(duration / 50)
    
    # Фаза 3: Замедление и завершение
    for i in range(35, 45):
        progress = 80 + int(((i - 35) / 10) * 20)
        bar = "█" * (progress // 5) + "░" * (20 - progress // 5)
        
        # Эффект "подвисания" в конце
        if i > 40:
            time.sleep(duration / 25)
        
        spinner = "|/-\\"[i % 4]
        print(f"\r[{bar}] {progress}% {spinner}", end='', flush=True)
        time.sleep(duration / 60)
    
    # Финальный эффект
    final_bar = "█" * 20
    print(f"\r[{final_bar}] 100% ✓ ЗАВЕРШЕНО", flush=True)
    time.sleep(0.5)

def fake_ip_scan():
    """Имитация сканирования IP адресов с анимацией"""
    print("\n🔍 СКАНИРОВАНИЕ СЕТИ...")
    
    # Анимированная загрузка для сканирования
    loading_bar(2, "Инициализация сканера портов...")
    
    print("\n📡 Обнаруженные устройства:")
    for i in range(8):
        ip = f"192.168.1.{random.randint(1, 255)}"
        
        # Анимация сканирования каждого IP
        print(f"Сканирование {ip}...", end='', flush=True)
        for j in range(3):
            time.sleep(0.2)
            print(".", end='', flush=True)
        
        status = random.choice(["АКТИВЕН", "НЕАКТИВЕН", "ЗАЩИЩЕН"])
        color = "🟢" if status == "АКТИВЕН" else "🔴" if status == "НЕАКТИВЕН" else "🟡"
        print(f"\r{color} {ip} - {status}" + " " * 10)
        time.sleep(0.3)

def fake_password_crack():
    """Имитация взлома паролей с реалистичной анимацией"""
    print("\n🔐 АКТИВАЦИЯ МОДУЛЯ ВЗЛОМА ПАРОЛЕЙ...")
    loading_bar(2, "Загрузка словарей паролей...")
    
    passwords = [
        "admin123",
        "password", 
        "123456789",
        "qwerty2024",
        "secret_key",
        "user_password"
    ]
    
    print("\n💻 Запуск брутфорс атаки...")
    
    for pwd in passwords:
        masked_pwd = '*' * len(pwd)
        
        # Имитация подбора пароля
        attempts = random.randint(50, 200)
        print(f"\n🎯 Цель: {masked_pwd}")
        print("Попытки: ", end='', flush=True)
        
        for attempt in range(min(attempts, 20)):  # Показываем только первые 20 попыток
            if attempt % 5 == 0:
                print(f"\n   {attempt+1:3d}-{attempt+5:3d}: ", end='', flush=True)
            
            fake_attempt = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=len(pwd)))
            print(fake_attempt[:3] + "...", end=' ', flush=True)
            time.sleep(0.05)
        
        print(f"\n   ✓ УСПЕХ! Найден после {attempts} попыток: {pwd}")
        print(f"   🔓 Пароль взломан: {pwd}")
        time.sleep(1)

def fake_file_access():
    """Имитация доступа к файлам с детальной анимацией"""
    print("\n📁 ПОЛУЧЕНИЕ ДОСТУПА К ФАЙЛОВОЙ СИСТЕМЕ...")
    loading_bar(2, "Обход систем защиты...")
    
    funny_files = [
        ("🐱 секретные_котики.jpg", "2.3 MB"),
        ("🍕 заказы_пиццы_за_год.txt", "847 KB"), 
        ("🎮 сохранения_игр.zip", "15.7 MB"),
        ("📚 забытые_пароли.docx", "234 KB"),
        ("🎵 плейлист_для_душа.mp3", "67.4 MB"),
        ("💰 счета_за_интернет.pdf", "1.2 MB"),
        ("🤔 философские_мысли_в_3_ночи.txt", "45 KB"),
        ("📱 скриншоты_мемов.folder", "234.6 MB"),
        ("🍿 список_фильмов_на_выходные.xlsx", "89 KB"),
        ("🎯 планы_на_завтра.note", "12 KB")
    ]
    
    print("\n📂 Найденные файлы:")
    for filename, size in funny_files:
        print(f"\n📄 {filename} ({size})")
        
        # Анимация скачивания
        print("Скачивание: [", end='', flush=True)
        
        # Переменная скорость скачивания для реализма
        chunks = 25
        speeds = [0.02, 0.03, 0.01, 0.04, 0.02] * 5  # Различные скорости
        
        for i in range(chunks):
            if i < chunks * 0.7:  # Быстрое начало
                char = "█"
            elif i < chunks * 0.9:  # Замедление
                char = "▓"
            else:  # Медленное завершение
                char = "▒"
            
            print(char, end='', flush=True)
            time.sleep(speeds[i])
        
        print("] ✓ ЗАВЕРШЕНО")
        time.sleep(0.2)

def fake_system_control():
    """Имитация контроля системы"""
    print("\n⚙️ ЗАХВАТ УПРАВЛЕНИЯ СИСТЕМОЙ...")
    time.sleep(1)
    
    systems = [
        "Клавиатура",
        "Мышь", 
        "Веб-камера",
        "Микрофон",
        "Динамики",
        "WiFi модуль",
        "Холодильник"  # Забавное добавление
    ]
    
    for system in systems:
        print(f"Подключение к {system}...", end='')
        time.sleep(random.uniform(0.5, 1.5))
        print(" ✓ ЗАХВАЧЕН")

def dramatic_reveal():
    """Драматичное раскрытие"""
    print("\n" + "="*50)
    time.sleep(1)
    type_text("ВНИМАНИЕ! СИСТЕМА ПОЛНОСТЬЮ ВЗЛОМАНА!", 0.05)
    time.sleep(2)
    
    print("\n💀 ХАКЕР ПОЛУЧИЛ ДОСТУП КО ВСЕМУ:")
    time.sleep(1)
    
    access_list = [
        "✓ Все пароли",
        "✓ Банковские данные", 
        "✓ Личные фотографии",
        "✓ История браузера",
        "✓ Секретные рецепты бабушки",
        "✓ Коллекция мемов",
        "✓ Планы на отпуск"
    ]
    
    for item in access_list:
        print(f"  {item}")
        time.sleep(0.7)
    
    print("\n" + "="*50)

def countdown_to_reveal():
    """Обратный отсчет до раскрытия"""
    print("\n⏰ САМОУНИЧТОЖЕНИЕ ЧЕРЕЗ:")
    for i in range(5, 0, -1):
        print(f"\n        {i}", end='')
        for _ in range(3):
            print(".", end='', flush=True)
            time.sleep(0.3)
        time.sleep(0.4)
    
    clear_screen()

def final_reveal():
    """Финальное раскрытие пранка"""
    print("\n" + "🎉" * 20)
    print("\n")
    type_text("         РОЗЫГРЫШ! 😄", 0.1)
    print("\n")
    type_text("    Это был всего лишь пранк!", 0.05)
    type_text("    Твой компьютер в полной безопасности!", 0.05)
    type_text("    Никакой взлом не происходил! 🤪", 0.05)
    print("\n")
    type_text("    Надеемся, тебе понравилось! ❤️", 0.05)
    print("\n" + "🎉" * 20)

def main():
    """Основная функция пранка"""
    clear_screen()
    
    # Начальная заставка
    print("🚨" * 15)
    type_text("ВНИМАНИЕ! ОБНАРУЖЕНА ПОПЫТКА НЕСАНКЦИОНИРОВАННОГО ДОСТУПА!", 0.04)
    print("🚨" * 15)
    time.sleep(2)
    
    # Имитация инициализации
    type_text("\n🔴 АКТИВАЦИЯ ПРОТОКОЛОВ БЕЗОПАСНОСТИ...", 0.03)
    loading_bar(2, "Инициализация системы взлома")
    
    # Поддельные этапы взлома
    fake_ip_scan()
    time.sleep(1)
    
    fake_password_crack()
    time.sleep(1)
    
    fake_file_access()
    time.sleep(1)
    
    fake_system_control()
    time.sleep(2)
    
    # Драматичное раскрытие "взлома"
    dramatic_reveal()
    time.sleep(3)
    
    # Обратный отсчет
    countdown_to_reveal()
    
    # Раскрытие пранка
    final_reveal()
    
    # Завершение
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n😄 Пранк прерван! Это был розыгрыш!")
        sys.exit(0)