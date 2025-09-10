valid_classes = ["Warrior", "Mage", "Priest"]

while True:
    class_pick = input("Enter your class (Warrior, Mage, Priest): ").strip().capitalize()
    if class_pick not in valid_classes:
        print("Invalid class! Try again.\n")
        continue
    confirm = input(f"Are you sure you want to be a {class_pick}? (Y/N): ").upper()
    if confirm == "Y":
        print(f"You're now a {class_pick}. Let's start your adventure!")
        break
    elif confirm == "N":
        print("Okay, let's pick again.\n")
        continue
    else:
        print("Invalid input! Please type Y or N.\n")
        continue

import time
time.sleep(1)
print("When you were walking down the street you encounter a bard singing alone leaning against a wall. Do you want to greet him?")
input("Do you wish to aproach the bard? (Y/N): ")
if input().upper() == "Y":
    print("You approach the bard and he greets you warmly and asks you to retrive his guitar do you accept? (Y/N).")
    if input().upper() == "Y":
        print("You accept the quest and head towards the dark forest to find the guitar.")
    else:
        print("You decline the quest and continue on your way down the street.")