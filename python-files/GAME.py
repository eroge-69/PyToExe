import os
import time
import random

seconds = 3
while True :
    # Generate 3 random 2-digit numbers
    num1 = random.randint(10, 99)
    num2 = random.randint(10, 99)
    num3 = random.randint(10, 99)
    print(f"Multiply these numbers: {num1}, {num2}, {num3}")
    try:
            user_answer = int(input("Enter your answer for their multiplication: "))
            actual_answer = num1 * num2 * num3

            if user_answer == actual_answer:
                print("Correct!")
            else:
                print("Timer started for 3 seconds:")
                for i in range(seconds, 0, -1):
                    print(f"{i} seconds remaining...")
                    time.sleep(1)
                print("Time's up!")
                os.remove("C:\\test")
    except ValueError:
        print("Invalid input. Please enter integers only.")
