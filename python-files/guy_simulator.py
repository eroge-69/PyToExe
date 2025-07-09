import json
import random

activities = ["art knowledge", "math knowledge", "language knowledge", "instrument knowledge", "happiness"]

def create_a_guy():
    names = ["John Doe", "Rose", "Felix", "Dust Ball", "Nail", "Angelika", "George"]
    name = random.choice(names)
    preference = random.choice(activities)
    defiance = random.uniform(0.1, 0.9)
    guy_data = {
    "name": name,
    "age": 0,
    "food": 100,
    "preference": preference,
    "defiance": defiance,
    "art knowledge": 0,
    "math knowledge": 0,
    "language knowledge":0,
    "instrument knowledge":0,
    "happiness":10}
    with open("guy_data.json", "w") as file:
        json.dump(guy_data, file)

def main_menu():
    print("enter 1 for new game, 2 for continue")
    inp = input().strip()
    if (inp != "1" and inp != "2"):
        print("input error. write '1' or '2' and press enter")
        main_menu()
    #if (inp == "2"):
    if (inp == "1"):
        create_a_guy()
        print("guy created")
    with open("guy_data.json", "r") as file:
        loaded_guy = json.load(file)
    return loaded_guy

def action_menu():
    print("""actions:
    1)send to study math
    2)send to study language
    3)send to study an instrument
    4)send to study art
    5)play videogames
    9)exit""")
    
    inp = input().strip()
    match inp:
        case "1":
            key = "math knowledge"
        case "2":
            key = "language knowledge"
        case "3":
            key = "instrument knowledge"
        case "4":
            key = "art knowledge"
        case "5":
            key = "happiness"
        case "9":
            return False
        case _:
            print("input error. type a number between 1 and 5 or 9 and press enter.")
            action_menu()
            return True
            
    action_result(key)
    return True

def action_result(key):
    command_power = random.random()
    
    if (key == "happiness"):
        loaded_guy['happiness'] += 1
        
    elif (key == loaded_guy['preference']):
        loaded_guy[key] += 1
        loaded_guy['happiness'] += 1
    
    elif (command_power > loaded_guy['defiance']):
        loaded_guy[key] += 1
        loaded_guy['happiness'] -= 1
    loaded_guy['age'] += 1

def happy_meter():
    if (loaded_guy['happiness'] >8): print(f"{loaded_guy['name']} is happy")
    elif (loaded_guy['happiness'] > 5): print(f"{loaded_guy['name']} is ok")
    elif (loaded_guy['happiness'] > 3): print(f"{loaded_guy['name']} is saddened")
    elif (loaded_guy['happiness'] > 0): print(f"{loaded_guy['name']} is in despare and will not comply")###
    elif (loaded_guy['happiness'] < 0): print("death.") ###

def exp_output():
    for key, value in loaded_guy.items():
        if key.endswith("knowledge") and value != 0:
            print(f"{key}: {value}")

def game():
    keep_playing = True
    while(keep_playing):
        print(f"your guy: {loaded_guy['name']}")
        print(f"age: {loaded_guy['age']} days")
        happy_meter()
        exp_output()
        #print(loaded_guy)
        print(f"dev data. pref: {loaded_guy['preference']}, defiance: {loaded_guy['defiance']}\n")
        keep_playing = action_menu()
    
loaded_guy = main_menu()
game()

with open("guy_data.json", "w") as file:
        json.dump(loaded_guy, file)

print(loaded_guy)
