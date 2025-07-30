
import os
import time

def shutdown_timer():
    print("Zadaj čas, po ktorom sa má počítač vypnúť:")
    print("Formát: napr. '10m' pre 10 minút alebo '30s' pre 30 sekúnd")
    user_input = input("Čas: ").strip().lower()

    if user_input.endswith('m'):
        seconds = int(user_input[:-1]) * 60
    elif user_input.endswith('s'):
        seconds = int(user_input[:-1])
    else:
        print("Nesprávny formát. Použi '10m' alebo '30s'.")
        return

    print(f"Počítač sa vypne za {seconds} sekúnd.")
    time.sleep(seconds)
    os.system("shutdown /s /t 1")

shutdown_timer()
