import random
import time
import os

# Добавляем цвета для Windows
if os.name == 'nt':
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def dice_roll():
    return random.randint(1, 4)

def draw_dice(number, color=Colors.WHITE):
    dice_faces = {
        1: [
            "┌─────────┐",
            "│         │",
            "│    ●    │",
            "│         │",
            "└─────────┘"
        ],
        2: [
            "┌─────────┐",
            "│ ●       │",
            "│         │",
            "│       ● │",
            "└─────────┘"
        ],
        3: [
            "┌─────────┐",
            "│ ●       │",
            "│    ●    │",
            "│       ● │",
            "└─────────┘"
        ],
        4: [
            "┌─────────┐",
            "│ ●     ● │",
            "│         │",
            "│ ●     ● │",
            "└─────────┘"
        ]
    }
    
    colored_face = []
    for line in dice_faces[number]:
        colored_face.append(color + line + Colors.RESET)
    return colored_face

def spinning_animation():
    """Анимация вращения"""
    symbols = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    for i in range(16):
        clear_screen()
        print(f"{Colors.CYAN}Бросаем кость... {symbols[i % len(symbols)]}{Colors.RESET}")
        time.sleep(0.1)

def real_time_dice_colored():
    while True:
        clear_screen()
        print(f"{Colors.BOLD}{Colors.CYAN}=== 🎲 ГЕНЕРАТОР ИГРАЛЬНОЙ КОСТИ D4 🎲 ==={Colors.RESET}")
        print(f"{Colors.YELLOW}Нажмите Enter для броска кости")
        print(f"{Colors.RED}Введите 'q' для выхода{Colors.RESET}")
        
        choice = input(f"\n{Colors.GREEN}Ваш выбор: {Colors.RESET}").strip().lower()
        
        if choice == 'q':
            print(f"{Colors.MAGENTA}До свидания!{Colors.RESET}")
            break
        elif choice == '':
            # Анимация броска
            spinning_animation()
            
            # Финальный результат
            result = dice_roll()
            colors = [Colors.RED, Colors.GREEN, Colors.YELLOW, Colors.BLUE]
            dice_color = colors[result - 1]
            
            clear_screen()
            print(f"{Colors.BOLD}{Colors.CYAN}=== 🎯 РЕЗУЛЬТАТ 🎯 ==={Colors.RESET}")
            print(f"{dice_color}Выпало: {result}{Colors.RESET}")
            print("\n".join(draw_dice(result, dice_color)))
            
            input(f"\n{Colors.YELLOW}🎲 Нажмите Enter для следующего броска...{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ Неверный ввод!{Colors.RESET}")
            time.sleep(1)

if __name__ == "__main__":
    real_time_dice_colored()