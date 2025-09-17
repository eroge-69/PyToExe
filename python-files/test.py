import os
import random
import time

print("🎮 Welcome to 'Guess to Sleep'! 🌙")
print("Guess the secret number between 1 and 5. Win, and bedtime comes early!")

secret = random.randint(1, 5)
guess = int(input("Your guess: "))

if guess == secret:
    print("🎉 Correct! Sleep mode activated...")
    for i in range(5, 0, -1):
        print(f"Shutting down in {i} seconds...")
        time.sleep(1)
    os.system("shutdown /s /t 1")  # Windows
    # os.system("shutdown now")    # Linux
else:
    print(f"❌ Wrong! The number was {secret}. No shutdown tonight 😎")
