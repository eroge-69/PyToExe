import time
import math

block = "◻"

digits = {
    "0": ["◻◻◻", "◻  ◻", "◻  ◻", "◻  ◻", "◻◻◻"],
    "1": ["  ◻ ", "  ◻ ", "  ◻ ", "  ◻ ", "  ◻ "],
    "2": ["◻◻◻", "   ◻", "◻◻◻", "◻   ", "◻◻◻"],
    "3": ["◻◻◻", "   ◻", "◻◻◻", "   ◻", "◻◻◻"],
    "4": ["◻  ◻", "◻  ◻", "◻◻◻", "   ◻", "   ◻"],
    "5": ["◻◻◻", "◻   ", "◻◻◻", "   ◻", "◻◻◻"],
    "6": ["◻◻◻", "◻   ", "◻◻◻", "◻  ◻", "◻◻◻"],
    "7": ["◻◻◻", "   ◻", "   ◻", "   ◻", "   ◻"],
    "8": ["◻◻◻", "◻  ◻", "◻◻◻", "◻  ◻", "◻◻◻"],
    "9": ["◻◻◻", "◻  ◻", "◻◻◻", "   ◻", "◻◻◻"],
    ".": ["   ", "   ", "   ", "   ", " ◻ "]
}

while True:
    choice = input('Do you want to use Averager? (Y/N): ')
    if choice.lower() in ["yes", "y"]:
        name = input('What is your name? ')
        print('Saved...')

        Marks1 = int(input('How much marks did you get in Maths? '))
        print('Saved..')

        Marks2 = int(input('How much marks did you get in English? '))
        print('Saved....')

        Marks3 = int(input('How much marks did you get in Computer? '))
        print('Saved..')
        time.sleep(1.5)
        print('Finalizing...')
        time.sleep(0.5)

        Average = (Marks1 + Marks2 + Marks3) / 3
        formatted_avg = f"{Average:.2f}"

        print(f"\n{name} has gotten {formatted_avg} as the average.")

        print("\nVisual Representation:\n")
        for row in range(5):
            line = ""
            for char in formatted_avg:
                if char in digits:
                    line += digits[char][row] + "   "
            print(line)

        break

    elif choice.lower() in ["no", "n"]:
        print("Closing...")
        break
    else:
        print("Invalid input")
