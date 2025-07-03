import random
import time 

items = ["rock", "paper","scissor"]
items_2 = ["scissor", "rock","paper","scissor"]

print("Welcome to rock paper scissor\n")
time.sleep(1.5)
for x in "MINUS ONE":
    print(x)
    time.sleep(.2)

while True:
    
    user_choices = []
    opponent_choices = []
    minus_acceptence = []
    needed = []
    one = False
    two = False

    print("\nyou will choose 2 item from: rock / paper / scissor")
    time.sleep(.3)
    first_choice = input("Enter the name of your first choice: ").lower()
    time.sleep(1)
    while not items.count(first_choice):
        print("\nInvalid entry")
        print("Please enter rock, paper or scissor")
        first_choice = input("Enter the name of your first choice: ").lower()
    second_choice = input("Second choice: ").lower()
    time.sleep(1)
    while not items.count(second_choice):
        print("\nInvalid entry")
        print("Please enter rock, paper or scissor")
        second_choice = input("Enter the name of your second choice: ").lower()

    print("\n---YOU---")
    time.sleep(.4)
    print(f"You have choosen {first_choice.upper()} and {second_choice.upper()}")
    time.sleep(.4)
    opponent_c_one = items[random.randint(0,2)]
    opponent_c_two = items[random.randint(0,2)]
    while opponent_c_one == opponent_c_two:
        opponent_c_two = items[random.randint(0,2)]
    print("-------------------------")
    time.sleep(.4)
    print("\n--YOUR OPPONENT--")
    time.sleep(.4)
    print(f"Your opponent have choosen {opponent_c_one.upper()} and {opponent_c_two.upper()}")
    time.sleep(.4)
    print("-------------------------")
    time.sleep(.4)

    print(f"\nSelect which item to remove from: ({first_choice.upper()} / {second_choice.upper()})")
    time.sleep(.4)
    minus_choice = (input("Enter your choice: ")).lower()
    
    
    while minus_choice != first_choice and minus_choice != second_choice:
        print("\nInvalid entry")
        print(f"Please enter {first_choice.upper()} or {second_choice.upper()}")
        minus_choice = (input("Enter your choice: ")).lower()
    
    time.sleep(2)

    user_choices.append(first_choice)
    user_choices.append(second_choice)

    opponent_choices.append(opponent_c_one)
    opponent_choices.append(opponent_c_two)

    user_choice1_index = (items_2.index(first_choice))
    user_choice2_index = (items_2.index(second_choice))


    needed.append(items[user_choice1_index])
    needed.append(items[user_choice2_index])



    for need in needed: 
        if need == opponent_c_one:
            one = True
        elif need == opponent_c_two:
            two = True

    if one and two:
        opponent_last = opponent_choices[random.randint(0,1)]
    elif one:
        opponent_last = opponent_c_one
    elif two:
        opponent_last = opponent_c_two

    user_choices.remove(minus_choice.lower())
    user_result = str(user_choices[0])

    print(f"\nYou last with: {user_result.upper()}")
    print(f"Your opponent last with: {opponent_last.upper()}")
    
    time.sleep(1)
    print()
    for i in range(10):
        print("." ,end="\n")
        time.sleep(.2)
            
    time.sleep(2)
    
    user_result_index = items.index(user_result)
    opponent_result_index = items.index(opponent_last)
    items[-1].__add__("scissor")

    if items[user_result_index -1] == items[opponent_result_index]:
        for i in "YOU WIN!":
            print(i)
            time.sleep(.4)
        print("YOUR OPPONENTS ODDS OF DEATH IS 1/6")
        input("\n(PRESS ANY KEY TO CONTINUE)")
        death = random.randint(1,6)
        if death == 4:
            print("💥💥💥")
            print("YOU WIN!")
            break
        print("Nothing happened")
    elif items[opponent_result_index -1] == items[user_result_index]:
        for i in "YOU LOSE!":
            print(i)
            time.sleep(.4)
        print("YOUR ODDS OF DEATH IS 1/6")
        input("\n(PRESS ANY KEY TO CONTINUE)")
        death = random.randint(1,6)
        if death == 4:
            break
        print("You got lucky...")

    else:
        for i in "TIE":
            print(i)
            time.sleep(.7)

