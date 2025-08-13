import os
from datetime import datetime, timedelta
from colorama import init, Fore, Style

init(autoreset=True)

os.system("title Time Calculator")  # Set CMD title

ASCII_ART = r"""
  _______ _                   _____      _            _       _             
 |__   __(_)                 / ____|    | |          | |     | |            
    | |   _ _ __ ___   ___  | |     __ _| | ___ _   _| | __ _| |_ ___  _ __ 
    | |  | | '_ ` _ \ / _ \ | |    / _` | |/ __| | | | |/ _` | __/ _ \| '__|
    | |  | | | | | | |  __/ | |___| (_| | | (__| |_| | | (_| | || (_) | |   
    |_|  |_|_| |_| |_|\___|  \_____\__,_|_|\___|\__,_|_|\__,_|\__\___/|_|    
"""

RESULT_ART = r"""
   _____      _            _       _           _ 
  / ____|    | |          | |     | |         | |
 | |     __ _| | ___ _   _| | __ _| |_ ___  __| |
 | |    / _` | |/ __| | | | |/ _` | __/ _ \/ _` |
 | |___| (_| | | (__| |_| | | (_| | ||  __/ (_| |
  \_____\__,_|\___|\__,_|\__,_|\__\___|\__,_|  
"""

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def input_time(prompt):
    clear()
    print(Fore.RED + ASCII_ART)
    return input(f"\n» {prompt}: ")

def print_result(delta):
    clear()
    print(Fore.GREEN + RESULT_ART)
    print(f"\n{' ' * 30}Time difference: {delta}")
    input("\nPress Enter to exit...")

def main():
    time_fmt = "%I:%M %p"
    t1_str = input_time("Type the first time here")
    t2_str = input_time("Type the second time here")

    t1 = datetime.strptime(t1_str, time_fmt)
    t2 = datetime.strptime(t2_str, time_fmt)
    delta = t2 - t1
    if delta.days < 0:
        delta = timedelta(days=0, seconds=delta.seconds)

    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    print_result(f"{hours} hours and {minutes} minutes")

if __name__ == "__main__":
    main()
