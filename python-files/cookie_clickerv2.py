import os
import keyboard
import time
##import DBPYC++ as  ##
developer_upgrades_auto = False
developer_mode = False
cookies = 0
auto_upgrade = False
auto_clicker = 0
click_power = 1
upgrades = 1
upgrade_cost = 10 *upgrades
game_running = True
terminal_running = False
name = " "

while game_running == True:
    cookies += auto_clicker
    print('''
          
          
          
          
          




        
  ''')
    while developer_upgrades_auto == True:
        time.sleep(20)
        upgrades = 0
        click_power += 999999999999999999999999999999999999


    print(f"{name}Cookies: {cookies}.press c to click. Devloper mode: {developer_mode} . press u to upgrade. press b to buy multiple upgrades and press a to buy all upgrades u can afford.press s to set cookies if developer mod is enabled")
    if keyboard.is_pressed('c'):    
        cookies += click_power
        time.sleep(0.1)
    elif keyboard.is_pressed('q'):
        print("Exiting game...")
        game_running = False
    elif keyboard.is_pressed('u'):
        if cookies >= upgrade_cost:
            cookies -= upgrade_cost
            upgrades += 1
            click_power += 1
            upgrade_cost = 10 * upgrades
            print(f"Upgraded! Click power is now {click_power}. Next upgrade costs {upgrade_cost} cookies.")
        else:
            print(f"Not enough cookies to upgrade! You need {upgrade_cost - cookies} more cookies.")
        time.sleep(0.5)
    elif keyboard.is_pressed('b'):
        num_upgrades = int(input("Enter how many upgrades you want to buy: "))
        total_cost = upgrade_cost * num_upgrades
        if cookies >= total_cost:
            cookies -= total_cost
            upgrades += num_upgrades
            click_power += num_upgrades
            upgrade_cost = 10 * upgrades
            print(f"Upgraded! Click power is now {click_power}. Next upgrade costs {upgrade_cost} cookies.")
        else:
            print(f"Not enough cookies to buy {num_upgrades} upgrades! You need {total_cost - cookies} more cookies.")
        time.sleep(0.5)
    elif keyboard.is_pressed('a'):
        max_upgrades = cookies // upgrade_cost
        if max_upgrades > 0:
            cookies -= upgrade_cost * max_upgrades
            upgrades += max_upgrades
            click_power += max_upgrades
            upgrade_cost = 10 * upgrades
            print(f"Bought {max_upgrades} upgrades! Click power is now {click_power}. Next upgrade costs {upgrade_cost} cookies.")
        else:
            print(f"Not enough cookies to buy any upgrades! You need {upgrade_cost - cookies} more cookies.")
        time.sleep(0.5)
    elif keyboard.is_pressed('d'):
        if keyboard.is_pressed('p'):
            developer_mode = True
            print("Developer mode activated!")
    elif keyboard.is_pressed('s'):
        if developer_mode == True:
            cookies = input("Enter the number of cookies you want to have: ")
            try:
                cookies = int(cookies)
                print(f"Cookies set to {cookies}.")
            except ValueError:
                print("Invalid input. Please enter a number.")
            except input:
                cookies = float('NaN')
                print("You now have NaN cookies!")
        elif developer_mode == False:
            print("Developer mode is not enabled. u cant access this feature. sorry!")
    elif keyboard.is_pressed('t'):
        if developer_mode == True:
            terminal_running = True
            game_running = False
            while terminal_running == True:
                print("Welcome to the terminal type help for a list of basic commands")
                terminal_command = input("Enter your command: ")
                if terminal_command == "help":
                    print("Commands:")
                    print("1. Set_var - Set a variable to a value")
                    print("2. Get_var - Get the value of a variable")
                    print("3. list_vars - List all variables")
                    print("4. exit - Exit the terminal and return to the game")
                elif terminal_command == "Set_var":
                    var_name = input("Enter the variable name: ")
                    var_value = input("Enter the variable value: ")
                    # Use globals() to set variables in the global scope
                    try:
                        # Safely evaluate the value to handle different types (int, float, bool, string)
                        # For boolean, check for 'True' or 'False' strings
                        globals()[var_name] = eval(var_value) if var_value.lower() in ['true', 'false'] else eval(var_value)
                        print(f"Variable {var_name} set to {var_value}")
                    except Exception as e:
                        print(f"Error setting variable: {e}")
                elif terminal_command == "Get_var":
                    var_name = input("Enter the variable name: ")
                    try:
                        var_value = eval(var_name)
                        print(f"Variable {var_name} has value {var_value}")
                    except Exception as e:
                        print(f"Error getting variable: {e}")
                elif terminal_command == "list_vars":
                    print("Listing all variables:")
                    for var in dir():
                        if not var.startswith("__"):
                            print(var)
                elif terminal_command == "exit":
                    terminal_running = False
                    game_running = True
    

while game_running == False:
    if terminal_running == False:
        print("ERORR REBOOTING GAME")
        terminal_running = True
        game_running = True
        os.system(r"python Games\cookie_clickerv2.py")
