import time
import random

Score_1 = 0

def Main_game():
    global Score_1
    
    print("Welcome to Math Game")
    while True:
        level = input("Choose level:\n"
                      "1 = + (int), 2 = - (int), 3 = x (int), 4 = / (int)\n"
                      "5 = + (dec), 6 = - (dec), 7 = x (dec), 8 = / (dec)\n"
                      "Enter level (1-8): ")
        if level in [str(i) for i in range(1, 9)]:
            level = int(level)
            break
        else:
            print("Please enter a valid level number (1-8).")

    time.sleep(1)
    input("Press [enter] to start")
    time.sleep(1)

    while True:
        # Integer levels
        if level in [1, 2, 3, 4]:
            num1 = random.randint(0, 100)
            num2 = random.randint(1 if level == 4 else 0, 100)
        # Decimal levels
        else:
            num1 = round(random.uniform(0, 100), 2)
            num2 = round(random.uniform(1 if level == 8 else 0, 100), 2)

        if level == 1 or level == 5:
            symbol = "+"
            correct_answer = num1 + num2
        elif level == 2 or level == 6:
            symbol = "-"
            correct_answer = num1 - num2
        elif level == 3 or level == 7:
            symbol = "x"
            correct_answer = num1 * num2
        elif level == 4 or level == 8:
            symbol = "/"
            correct_answer = num1 / num2

        # Round answers for user input comparison (to 2 decimal places for decimal levels)
        is_decimal = level >= 5
        correct_answer = round(correct_answer, 2) if is_decimal else round(correct_answer)

        # Display formatted question
        display_num1 = f"{num1:.2f}" if is_decimal else str(num1)
        display_num2 = f"{num2:.2f}" if is_decimal else str(num2)
        print(f"{display_num1} {symbol} {display_num2}")
        if level == 4 or level == 8:
            print("(Round your answer to 2 decimal places)" if is_decimal else "(Round to nearest whole number)")

        try:
            answer = float(input("Enter answer: "))
            answer = round(answer, 2) if is_decimal else round(answer)
            if answer == correct_answer:
                Score_1 += 1
                print("Correct!")
            else:
                print("Incorrect!")
                print("GAME OVER!")
                print(f"Final Score: {Score_1}")
                break
        except ValueError:
            print("Please enter a valid number.")

Main_game()




#DON"T TOUCH THIS!!!