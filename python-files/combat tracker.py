


def get_initiative():
    print("Roll initative!")
    output = []
    still_going = True
    while still_going:
        print("Input name (or hit ENTER if finished):")
        name = input("> ")
        if name == "":
            still_going = False
        else:
            valid_in = False
            while valid_in == False:
                print(f"Enter {name}'s initiative roll:")
                roll = input("> ")
                valid_in = True
                try:
                    roll_int = int(roll)
                except:
                    valid_in = False
                    print("Please input a number for initative.")
            output.append((roll_int, name))
    return output

def sort_list(initative_list):
    for n in range(len(initative_list) - 1, 0, -1):
        swapped = False  
        for i in range(n):
            if initative_list[i][0] < initative_list[i + 1][0]:
                initative_list[i], initative_list[i + 1] = initative_list[i + 1], initative_list[i]
                swapped = True
        if not swapped:
            break
    out = []
    for (num, creature) in initative_list:
        out.append(creature)
    # print(out)
    return out

def print_initiative(initiative_list):
    print("==============")
    for (number, name) in initiative_list:
        if (number > -1) & (number < 10):
            print(f" {number}  {name}")
        else:
            print(f"{number}  {name}")
    print("==============")


def do_combat(initiative_list):
    turn_order = []
    for (number, name) in initiative_list:
        turn_order.append(name)
    still_going = True
    conditions = []
    while still_going:
        current = turn_order[0]
        print(f"It is {current}'s turn. (type \"help\" for options)")
        print_conditions(current, conditions)
        i = input("> ").lower()
        match i:
        ## HELP
            case "help":
                print_options()
            ## PASS
            case "pass":
                done = turn_order.pop(0)
                turn_order.append(done)
                print("--------------")
            ## END COMBAT
            case "end combat":
                still_going = False
            case "":
                pass
            case _:
                i_start = i.split()[0]
                match i_start:
                ## KILL
                    case "kill":
                        x = i.split()
                        if len(x) < 2:
                            print("not enough arguments. use \"kill [creature]\".")
                        print(f"{" ".join(x[1:])} is dead")
                        turn_order.remove(" ".join(x[1:]))
                    ## CONDITION
                    case "condition":
                        x = i.split()
                        if len(x) < 3:
                            print("not enough arguments. use \"condition [condition] [creature]\".")
                        else:
                            conditions = do_condition(" ".join(x[2:]), x[1], conditions)
                    case _:
                        print("invalid input. please try again.")
        if len(turn_order) < 1:
            still_going = False

def do_condition(creature, condition, conditions):
    for (name, cons) in conditions:
        if creature == name:
            if condition in cons:
                cons.remove(condition)
                print(f"{creature} is no longer {condition}.")
            else:
                cons.append(condition)
                print(f"{creature} is now {condition}.")
            return conditions
    conditions.append((creature, [condition]))
    print(f"{creature} is now {condition}.")
    return conditions


def print_conditions(name, conditions):
    for (cr, conds) in conditions:
        if cr == name:
            for cond in conds:
                print(f"{name} is {cond}.")
            return
    print(f"{name} has no conditions.")
    return


def print_options():
    print("================================================")
    print("\"pass\"")
    print("          moves to next creature in initative.")
    print("\"end combat\"")
    print("          ends the combat tracker.")
    print("\"kill [creature]\"")
    print("          removes the specified creature from initiative.")
    print("\"condition [condition] [creature]\"")
    print("          applies a condition to a creature, or removes the condition if already applied. conditions must be 1 word.")
    print("================================================")



if __name__ == '__main__':
    initiative_list = get_initiative()
    
    sort_list(initiative_list)

    print_initiative(initiative_list)

    do_combat(initiative_list)