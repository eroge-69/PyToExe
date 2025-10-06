import time
import os
import random

def clear_console():
    """Очищает консоль."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_tree(lights):
    """Отображает ёлку с гирляндами."""
    tree = [
        "       *       ",
        "      ***      ",
        "     *****     ",
        "    *******    ",
        "   *********   ",
        "  ***********  ",
        " ************* ",
        "***************",
        "      |||      ",
        "      |||      "
    ]

    colors = {
        'R': "\033[31m",  # Красный
        'G': "\033[32m",  # Зеленый
        'Y': "\033[33m",  # Желтый
        'B': "\033[34m",  # Синий
        'M': "\033[35m",  # Пурпурный
        'C': "\033[36m",  # Голубой
        'W': "\033[37m"   # Белый
    }
    RESET = "\033[0m"

    for i, row in enumerate(tree):
        line = ""
        for j, char in enumerate(row):
            if char == '*':
                if lights[i][j]:
                    light_color = random.choice(list(colors.keys()))
                    line += colors[light_color] + "*" + RESET
                else:
                    line += "*"
            else:
                line += char
        print(line)

def main():
    """Основная функция: анимация ёлки."""
    try:
        
        lights = [[False for _ in range(15)] for _ in range(8)]

        while True:
            clear_console()

            
            for i in range(8):
                for j in range(15):
                    if random.random() < 0.3:  
                        lights[i][j] = random.choice([True, False])

            print_tree(lights)
            time.sleep(0.2)  

    except KeyboardInterrupt:
        print("\nАнимация завершена.")

if __name__ == "__main__":
    
    if os.name == 'nt':
        os.system('color')

    main()
