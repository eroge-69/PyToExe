import time
import random
import os
import sys

# Установка зеленого хакерского цвета для Windows и Unix
def set_green_color():
    """Устанавливает зеленый цвет текста в консоли"""
    if os.name == 'nt':  # Windows
        os.system('color 0A')
    else:  # Unix/Linux/Mac
        print('\033[92m', end='')  # Ярко-зеленый

def reset_color():
    """Сбрасывает цвет консоли"""
    if os.name != 'nt':
        print('\033[0m', end='')

# Функции для цветного текста
def green_print(text, delay=0):
    """Печать зеленым цветом"""
    if os.name != 'nt':
        print(f'\033[92m{text}\033[0m', flush=True)
    else:
        print(text, flush=True)
    if delay:
        time.sleep(delay)

def bright_green_print(text, delay=0):
    """Печать ярко-зеленым цветом"""
    if os.name != 'nt':
        print(f'\033[32m{text}\033[0m', flush=True)
    else:
        print(text, flush=True)
    if delay:
        time.sleep(delay)

def clear_screen():
    """Очистить экран и установить зеленый цвет"""
    os.system('cls' if os.name == 'nt' else 'clear')
    set_green_color()

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
        bar = "#" * (progress // 3) + "%" * min(2, 10 - progress // 3) + "." * max(0, 8 - progress // 3)
        percentage = int((i / 15) * 30)
        
        # Добавляем мерцающий эффект
        if random.random() < 0.3:
            bar = bar.replace("%", ":")
        
        print(f"\r[{bar}] {percentage}% {'.' * (i % 4)}", end='', flush=True)
        time.sleep(duration / 40)
    
    # Фаза 2: Ускорение
    for i in range(15, 35):
        progress = 30 + int(((i - 15) / 20) * 50)
        bar_filled = progress // 5
        bar_loading = min(2, 20 - bar_filled) if bar_filled < 20 else 0
        bar_empty = max(0, 20 - bar_filled - bar_loading)
        
        bar = "#" * bar_filled + "%" * bar_loading + "." * bar_empty
        
        # Случайные глитчи
        if random.random() < 0.1:
            glitch_pos = random.randint(0, len(bar) - 1)
            bar = bar[:glitch_pos] + random.choice(":%#") + bar[glitch_pos + 1:]
        
        print(f"\r[{bar}] {progress}% {'>' if i % 2 else '>>'}", end='', flush=True)
        time.sleep(duration / 50)
    
    # Фаза 3: Замедление и завершение
    for i in range(35, 45):
        progress = 80 + int(((i - 35) / 10) * 20)
        bar = "#" * (progress // 5) + "." * (20 - progress // 5)
        
        # Эффект "подвисания" в конце
        if i > 40:
            time.sleep(duration / 25)
        
        spinner = "|/-\\"[i % 4]
        print(f"\r[{bar}] {progress}% {spinner}", end='', flush=True)
        time.sleep(duration / 60)
    
    # Финальный эффект
    final_bar = "#" * 20
    print(f"\r[{final_bar}] 100% COMPLETE", flush=True)
    time.sleep(0.5)

def fake_ip_scan():
    """Имитация сканирования IP адресов с анимацией"""
    print("\n[*] NETWORK SCANNING INITIATED...")
    
    # Анимированная загрузка для сканирования
    loading_bar(2, "Initializing port scanner...")
    
    print("\n[+] Detected devices:")
    for i in range(8):
        ip = f"192.168.1.{random.randint(1, 255)}"
        
        # Анимация сканирования каждого IP
        print(f"Scanning {ip}...", end='', flush=True)
        for j in range(3):
            time.sleep(0.2)
            print(".", end='', flush=True)
        
        status = random.choice(["ACTIVE", "INACTIVE", "PROTECTED"])
        symbol = "[+]" if status == "ACTIVE" else "[-]" if status == "INACTIVE" else "[!]"
        print(f"\r{symbol} {ip} - {status}" + " " * 10)
        time.sleep(0.3)

def fake_password_crack():
    """Имитация взлома паролей с реалистичной анимацией"""
    print("\n[*] ACTIVATING PASSWORD CRACKING MODULE...")
    loading_bar(2, "Loading password dictionaries...")
    
    passwords = [
        "admin123",
        "password", 
        "123456789",
        "qwerty2024",
        "secret_key",
        "user_password"
    ]
    
    print("\n[*] Starting brute force attack...")
    
    for pwd in passwords:
        masked_pwd = '*' * len(pwd)
        
        # Имитация подбора пароля
        attempts = random.randint(50, 200)
        print(f"\n[>] Target: {masked_pwd}")
        print("Attempts: ", end='', flush=True)
        
        for attempt in range(min(attempts, 20)):  # Показываем только первые 20 попыток
            if attempt % 5 == 0:
                print(f"\n   {attempt+1:3d}-{attempt+5:3d}: ", end='', flush=True)
            
            fake_attempt = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=len(pwd)))
            print(fake_attempt[:3] + "...", end=' ', flush=True)
            time.sleep(0.05)
        
        print(f"\n   [+] SUCCESS! Found after {attempts} attempts: {pwd}")
        print(f"   [!] Password cracked: {pwd}")
        time.sleep(1)

def fake_file_access():
    """Имитация доступа к файлам с детальной анимацией"""
    print("\n[*] ACCESSING FILE SYSTEM...")
    loading_bar(2, "Bypassing security protocols...")
    
    funny_files = [
        ("secret_cats.jpg", "2.3 MB"),
        ("pizza_orders_2024.txt", "847 KB"), 
        ("game_saves.zip", "15.7 MB"),
        ("forgotten_passwords.docx", "234 KB"),
        ("shower_playlist.mp3", "67.4 MB"),
        ("internet_bills.pdf", "1.2 MB"),
        ("3am_thoughts.txt", "45 KB"),
        ("meme_screenshots.folder", "234.6 MB"),
        ("weekend_movies.xlsx", "89 KB"),
        ("tomorrow_plans.note", "12 KB")
    ]
    
    print("\n[+] Files found:")
    for filename, size in funny_files:
        print(f"\n[>] {filename} ({size})")
        
        # Анимация скачивания
        print("Download: [", end='', flush=True)
        
        # Переменная скорость скачивания для реализма
        chunks = 25
        speeds = [0.02, 0.03, 0.01, 0.04, 0.02] * 5  # Различные скорости
        
        for i in range(chunks):
            if i < chunks * 0.7:  # Быстрое начало
                char = "#"
            elif i < chunks * 0.9:  # Замедление
                char = "%"
            else:  # Медленное завершение
                char = ":"
            
            print(char, end='', flush=True)
            time.sleep(speeds[i])
        
        print("] COMPLETE")
        time.sleep(0.2)

def fake_system_control():
    """Имитация контроля системы"""
    print("\n[*] GAINING SYSTEM CONTROL...")
    time.sleep(1)
    
    systems = [
        "Keyboard",
        "Mouse", 
        "Webcam",
        "Microphone",
        "Speakers",
        "WiFi module",
        "Refrigerator"  # Забавное добавление
    ]
    
    for system in systems:
        print(f"Connecting to {system}...", end='')
        time.sleep(random.uniform(0.5, 1.5))
        print(" [COMPROMISED]")

def dramatic_reveal():
    """Драматичное раскрытие"""
    print("\n" + "="*50)
    time.sleep(1)
    type_text("WARNING! SYSTEM FULLY COMPROMISED!", 0.05)
    time.sleep(2)
    
    print("\n[!] HACKER HAS ACCESS TO EVERYTHING:")
    time.sleep(1)
    
    access_list = [
        "[+] All passwords",
        "[+] Banking data", 
        "[+] Personal photos",
        "[+] Browser history",
        "[+] Grandma's secret recipes",
        "[+] Meme collection",
        "[+] Vacation plans"
    ]
    
    for item in access_list:
        print(f"  {item}")
        time.sleep(0.7)
    
    print("\n" + "="*50)

def countdown_to_reveal():
    """Обратный отсчет до раскрытия"""
    print("\n[!] SELF-DESTRUCTION IN:")
    for i in range(5, 0, -1):
        print(f"\n        {i}", end='')
        for _ in range(3):
            print(".", end='', flush=True)
            time.sleep(0.3)
        time.sleep(0.4)
    
    clear_screen()

def final_reveal():
    """Финальное раскрытие пранка"""
    print("\n" + "=" * 20)
    print("\n")
    type_text("         PRANKED!", 0.1)
    print("\n")
    type_text("    This was just a joke!", 0.05)
    type_text("    Your computer is completely safe!", 0.05)
    type_text("    No actual hacking occurred!", 0.05)
    print("\n")
    type_text("    Hope you enjoyed it!", 0.05)
    print("\n" + "=" * 20)

def main():
    """Основная функция пранка"""
    clear_screen()
    
    # Начальная заставка
    print("[!]" * 15)
    type_text("WARNING! UNAUTHORIZED ACCESS ATTEMPT DETECTED!", 0.04)
    print("[!]" * 15)
    time.sleep(2)
    
    # Имитация инициализации
    type_text("\n[*] ACTIVATING SECURITY PROTOCOLS...", 0.03)
    loading_bar(2, "Initializing hack system")
    
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
    input("\nPress Enter to exit...")
    reset_color()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrank interrupted! This was a joke!")
        reset_color()
        sys.exit(0)