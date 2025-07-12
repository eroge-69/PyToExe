
import os
import random
import time
import sys

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_binary_line(width):
    return ''.join(random.choice(['0', '1']) for _ in range(width))

def main():
    width = 120
    height = 40
    progress = 0
    message = "HACKING IN PROGRESS..."

    while progress <= 100:
        clear()
        for i in range(height):
            if i == 18:
                pad = (width - len(message)) // 2
                print(print_binary_line(pad) + message + print_binary_line(width - pad - len(message)))
            elif i == 20:
                prog_text = f"PROGRESS: {progress}"
                pad = (width - len(prog_text)) // 2
                print(print_binary_line(pad) + prog_text + print_binary_line(width - pad - len(prog_text)))
            else:
                print(print_binary_line(width))
        time.sleep(0.3)
        progress += 5

    clear()
    print("\n\n" + " " * 30 + ">>>>>> ACCESS GRANTED <<<<<<\n\n")
    time.sleep(2)

    while True:
        print(print_binary_line(width))
        time.sleep(0.05)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
