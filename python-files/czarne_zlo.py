
import curses

def main(stdscr):
    curses.curs_set(0)  # Ukrywa kursor
    stdscr.clear()      # Czyści ekran
    height, width = stdscr.getmaxyx()
    message = "właściciel zamożnych ziem tu był"
    x = (width - len(message)) // 2
    y = height // 2
    stdscr.addstr(y, x, message, curses.A_BOLD)
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key == ord('n'):
            break

curses.wrapper(main)
