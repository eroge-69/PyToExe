import time
from colorama import init, Fore, Style

init()

def slow_print(text, delay=0.05):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

# начало
slow_print(Fore.LIGHTBLUE_EX + "Ancient Library, Midnight")
print(Style.RESET_ALL)
time.sleep(1)

slow_print("You find a strange glowing artifact on the table...")
time.sleep(1)

print(Fore.YELLOW + "Mentor: 'You must be careful. The artifact could bring knowledge, but it might also bring disaster.'")
print(Style.RESET_ALL)
time.sleep(2)

choice = input("\nChoose:\n1) Open the artifact\n2) Leave it sealed\n> ")

if choice == "1":
    slow_print(Fore.RED + "You touch the artifact. It bursts with dark light!")
    time.sleep(2)
    slow_print("Mentor: 'You should not have done this! Now the world will suffer…'")
    time.sleep(2)
    slow_print("The darkness spreads across the library. You can feel the end is near.")
    print(Fore.RED + "\n--- BAD ENDING ---")
    print(Style.RESET_ALL)

elif choice == "2":
    slow_print(Fore.GREEN + "You step back and shake your head.")
    time.sleep(2)
    slow_print("Mentor: 'Wise choice. You may not gain the knowledge today, but you will live to protect it tomorrow.'")
    time.sleep(2)
    slow_print("The artifact remains silent, but hope stays alive.")
    print(Fore.GREEN + "\n--- GOOD ENDING ---")
    print(Style.RESET_ALL)

else:
    print("error")
