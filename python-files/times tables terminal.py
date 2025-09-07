# setup
import time
import random
import os

min_val = 1
max_val = 12

# defs
def show_menu(options):
    """Display a numbered menu and return the chosen option."""
    while True:
        print("========= Menu Selector =========")
        for i, option in enumerate(options, start=1):
            print(f"{i}. {option}")
        print("0. Quit")

        choice = input("Choose an option: ").strip()

        if choice == "0":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        else:
            os.system('cls')
            print("❌ Invalid choice, try again!")

# ui generation
print(" _______________________________")
print("|welcome to times table terminal|")
print("|          select one           |")
print("|_______________________________|")

# selector
items = ["*", "/", "-", "+"]
selected = show_menu(items)
if selected:
    print(f"\n✅ You chose: {selected}")
else:
    print("\n👋 Goodbye!")
    quit()

# ask for the times table (used for * and /)
while True:
    try:
        tt = int(input("times table (e.g., 2..12): "))
        break
    except ValueError:
        print("Please enter a number.")

time.sleep(1)

# ======== QUESTION GENERATION ========
# For multiplication/division, use the chosen times table.
# For addition/subtraction, just use two random numbers.
if selected == "*":
    num1 = tt
    num2 = random.randint(min_val, max_val)
    correct = num1 * num2

elif selected == "/":
    # Make sure division is exact: (tt * k) / tt = k (an integer)
    k = random.randint(min_val, max_val)
    num1 = tt * k       # dividend
    num2 = tt           # divisor
    correct = num1 // num2  # integer result, equals k

elif selected == "+":
    num1 = random.randint(min_val, max_val)
    num2 = random.randint(min_val, max_val)
    correct = num1 + num2

elif selected == "-":
    a = random.randint(min_val, max_val)
    b = random.randint(min_val, max_val)
    # Keep result non-negative for friendlier practice
    num1, num2 = max(a, b), min(a, b)
    correct = num1 - num2

# ======== ASK & CHECK ========
os.system('cls')
print(f"{num1} {selected} {num2}")

while True:
    ans_str = input("answer: ").strip()
    try:
        # Answers are integers in this game setup
        ans = int(ans_str)
        break
    except ValueError:
        print("Please enter a whole number.")

if ans == correct:
    print("you got it correctly")
    print("you have 1 point")  # plug your points counter here if you loop
else:
    print("you got it wrong try again")
    print(f"(correct answer was {correct})")