import time
import os

def birthday_animation():
    message = [
        "Activating birthday mode... 🎉",
        "Loading version 19.0...",
        "Applying blessings: ☑️",
        "Injecting love and respect: ☑️",
        "Removing life bugs: ☑️",
        "Launching life.exe..."
    ]

    for line in message:
        print(line)
        time.sleep(1)

    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n" + "="*40)
    print("🎂 HAPPY BIRTHDAY, BRO! 🎂")
    print(">> You are officially upgraded to version 19.0 🚀")
    print(">> New Features: More power, deeper thoughts, and endless love 💙")
    print(">> From your #1 fan: Your sister ❤️")
    print("="*40 + "\n")

birthday_animation()
