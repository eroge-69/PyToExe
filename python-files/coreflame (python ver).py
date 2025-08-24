# intro function:

def intro():
    print(" ⋆ ⁺   ₊  ⋆  ☾  ⋆ ⁺   ₊  ⋆  \n")
    print("   Greetings, Deliverer.\n")
    print(" ⋆ ⁺   ₊  ⋆  ☾  ⋆ ⁺   ₊  ⋆  \n")
    
# get input
# let user type a cycle from 0 to 33 550 336
    while True:
        print("Input a cycle index from 0 to 33, 550, 336. : \n")
        cycle = input("Input a cycle index from 0 to 33, 550, 336. : ")
        # if cycle is within number bound, display value
        if int(cycle) >= 0 and int(cycle) <= 33550336:
            display_value(cycle)
            break
        elif int(cycle) == 33550337:
            print(" ⋆ ⁺   ₊  ⋆  ☾  ⋆ ⁺   ₊  ⋆  \n")
            print("██████ Where ██ ████████ are ██████ you, ██ ██████ Khaslana █")
            break
        else:
            pass

def display_value(cycle):
    print(" ⋆ ⁺   ₊  ⋆  ☾  ⋆ ⁺   ₊  ⋆  \n")
    # print cycle number
    if cycle.endswith("1"):
        if cycle.endswith("11"):
            print(f"The {cycle}th Eternal Recurrence")
        else:
            print(f"The {cycle}st Eternal Recurrence")
    elif cycle.endswith("2"):
        if cycle.endswith("12"):
            print(f"The {cycle}th Eternal Recurrence")
        else:
            print(f"The {cycle}nd Eternal Recurrence")
    elif cycle.endswith("3"):
        if cycle.endswith("13"):
            print(f"The {cycle}th Eternal Recurrence")
        else:
            print(f"The {cycle}rd Eternal Recurrence")
    else:
        print(f"The {cycle}th Eternal Recurrence")
        
    calculate(cycle)
    
def calculate(cycle):
    
    # display cycles until end of the world
    left = 33550336 - int(cycle)
    print(f"{left:,} cycles left until the end of the world")
    
    if int(cycle) != 0:
        coreflame = (int(cycle) - 1) * 12
        print(f"You have shouldered the weight of {coreflame:,} coreflames.")
    else:
        print(f"You have not yet triggered Era Nova for the first time.")
    
intro()
