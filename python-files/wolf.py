import curses
from random import randrange

def main(stdscr):
    # Настройка окна
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    score = 0
    missed_eggs = 0
    wolf_pos = height // 2
    
    # Рисуем границу игрового поля
    for y in range(height):
        stdscr.addch(y, 0, '|')
        stdscr.addch(y, width - 1, '|')
        
    def draw_wolf():
        nonlocal wolf_pos
        if wolf_pos > 0:
            stdscr.addch(wolf_pos, width//2, 'W')  # Волк обозначается буквой W
            
    def drop_egg():
        egg_y = 0
        while True:
            stdscr.refresh()
            egg_x = randrange(width // 4, width * 3 // 4)
            try:
                stdscr.addch(egg_y, egg_x, '*')  # Яйцо обозначено звездочкой (*)
                stdscr.refresh()
                
                # Проверка столкновения яйца с волком
                if egg_y >= wolf_pos and abs(egg_x - width//2) <= 1:
                    return True
                    
                # Если яйцо упало мимо волка
                elif egg_y >= height - 1:
                    return False
                
                egg_y += 1
                stdscr.timeout(800)  # Скорость падения яйца
                key = stdscr.getch()
                if key != -1:
                    handle_key(key)
            except Exception as e:
                break
                
    def handle_key(key):
        nonlocal wolf_pos
        if key == ord('q'):
            exit_game()
        elif key == curses.KEY_UP and wolf_pos > 0:
            wolf_pos -= 1
        elif key == curses.KEY_DOWN and wolf_pos < height - 1:
            wolf_pos += 1
            
    def game_over():
        stdscr.clear()
        stdscr.addstr(height // 2, width // 2 - len("GAME OVER") // 2, "GAME OVER")
        stdscr.addstr(height // 2 + 1, width // 2 - len(f"SCORE: {score}") // 2, f"SCORE: {score}")
        stdscr.refresh()
        stdscr.getch()  # Ожидание нажатия клавиши перед выходом
        exit_game()

    def exit_game():
        curses.endwin()
        quit()

    # Основной цикл игры
    while True:
        draw_wolf()
        caught = drop_egg()
        if caught:
            score += 1
        else:
            missed_eggs += 1
            if missed_eggs >= 3:
                game_over()

if __name__ == "__main__":
    curses.wrapper(main)