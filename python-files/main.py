import random
import math


#displays the main menu
def disp_menu():
    print(" ")
    print("Main Menu")
    print("1. Start")
    print("2. Exit")
    option = input("pick an option: ")
    if option == "1":
        print("starting...\n")
        start_game()
    elif option == "2":
        print("exiting...")
        exit()
    else:
        print("invalid option, try again\n")
        run_menu()

#opens the difficulty selector
def start_game():
    mode()

#runs the easier mode
def easy_mode():
    num = random.randint(1, 10)
    choice = int(input("Pick a random number from 1-10: \n"))
    if choice == num:
        print("You got it right\n")
        run_menu()
    elif 11 > choice > 0:#if the user's choice was incorrect, this checks if it is in between the numbers specified. if so it tells the user they were wrong.
        print("You picked wrong\n")
        run_menu()
    else:
        print("invalid number, try again\n")
        easy_mode()

#runs the normal difficulty
def normal_mode():
    num = random.randint(1, 100)
    choice = int(input("Pick a random number from 1-100: \n"))
    if choice == num:
        print("You got it right\n")
        run_menu()
    elif 101 > choice > 0:
        print("You picked wrong\n")
        run_menu()
    else:
        print("invalid number, try again\n")
        normal_mode()

#runs the harder difficulty
def hard_mode():
    num = random.randint(1, 1000)
    choice = int(input("Pick a random number from 1-1000: \n"))
    if choice == num:
        print("You got it right\n")
        run_menu()
    elif 1001 > choice > 0:
        print("You picked wrong\n")
        run_menu()
    else:
        print("invalid number, try again\n")
        hard_mode()

#opens the difficulty selector
def mode():
    print("What difficulty do you want to play? \n")
    print("1. Easy")
    print("2. Normal")
    print("3. hard")
    print("4. go back")
    diff = input("pick one: \n")
    if diff == "1":
        easy_mode()
    elif diff == "2":
        normal_mode()
    elif diff == "3":
        hard_mode()
    elif diff == "4":
        run_menu()
    else:
        print("Invalid option, try again")
        mode()



#runs the main menu
def run_menu():
    disp_menu()

#runs the main menu when the program is opened
if __name__ == "__main__":
    run_menu()


