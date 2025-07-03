import random
import time
from colorama import Fore, Style, init
init(autoreset=True)
choices = ["Rock", "Paper", "Scissors"]
default_color_list = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]
color_list = default_color_list.copy()
cpu_score = 0
player_score = 0
rainbow_mode = False  # Global flag for rainbow mode
cheat_menu_color_default = Fore.GREEN
cheat_menu_rainbow_default = False
# Track cheat points
cheat_points_added = 0
cheat_points_removed = 0

def reset_all_cheats():
    global player_score, cpu_score, cheat_points_added, cheat_points_removed
    if cheat_points_added > 0:
        player_score -= cheat_points_added
        cheat_points_added = 0
    if cheat_points_removed > 0:
        cpu_score += cheat_points_removed
        cheat_points_removed = 0

def getpass_asterisk(prompt=""):
    import sys
    import msvcrt
    print(prompt, end="", flush=True)
    pw = ""
    while True:
        ch = msvcrt.getch()
        if ch in {b'\r', b'\n'}:
            print()
            break
        elif ch == b'\x08':  # Backspace
            if len(pw) > 0:
                pw = pw[:-1]
                print("\b \b", end="", flush=True)
        elif ch == b'\x03':  # Ctrl+C
            raise KeyboardInterrupt
        else:
            try:
                char = ch.decode('utf-8')
            except UnicodeDecodeError:
                continue
            pw += char
            print("*", end="", flush=True)
    return pw

print(Fore.CYAN + "Type 'help' for game info and binds." + Style.RESET_ALL)  # Show help prompt at the start
while True:
    computer = random.choice(choices)  # Randomize computer's choice each round
    # Assign a random color to each choice
    if rainbow_mode:
        rainbow_colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
        def rainbow_color_text(text):
            return ''.join(rainbow_colors[i % len(rainbow_colors)] + c for i, c in enumerate(text)) + Style.RESET_ALL
        colored_choices = [rainbow_color_text(choice) for choice in choices]
    else:
        colored_choices = [random.choice(color_list) + choice + Style.RESET_ALL for choice in choices]
    print(" - ".join(colored_choices))  # Print choices with dashes between them
    print("----------------------------------------")  # Add dashes before input
    player = input("Rock, Paper or  Scissors?").capitalize()
    print("----------------------------------------")  # Add dashes after input
    if player.lower() == 'help':
        print(Fore.GREEN + "Valid inputs:" + Style.RESET_ALL)
        print("  Rock, Paper, Scissors - play a round")
        print("  End - finish the game and show scores")
        print("  Help - show this help message")
        print("  Score - show the current scores")
        print("  Clear - clear the screen and show the current score")
        print("  Made by Noahw1567")
        print(Fore.MAGENTA + "{:^40}".format("Have fun! ^_^") + Style.RESET_ALL)
        print("========================================")
        continue
    if player.lower() == 'score':
        print(Fore.CYAN + f"Current Score -> Player: {player_score} | CPU: {cpu_score}" + Style.RESET_ALL)
        print("========================================")
        continue
    # Only allow normal game commands in the main loop
    # Remove handling for 'gun', color, rainbow, norainbow, cc color, resetcheats, #09, #10 from main loop
    if player.lower() == 'help++':
        password_lines = 0
        exit_cheat_menu = False
        while not exit_cheat_menu:
            password = getpass_asterisk(Fore.GREEN + "Enter password to access cheat codes:" + Style.RESET_ALL + " ")
            password_lines += 1
            if password.lower() == 'quit' or password.lower() == 'leave':
                # Clear the password prompt lines
                print("\033[F\033[K" * password_lines, end="")
                exit_cheat_menu = True
                break
            if password != '1567':
                print(Fore.RED + "Incorrect password! Type 'leave' to exit." + Style.RESET_ALL)
                print("========================================")
                password_lines += 2
                continue
            # Clear all password prompt and error lines
            print("\033[F\033[K" * password_lines, end="")
            # Blinking underscore using ANSI escape code \033[5m for blink
            blink_underscore = '\033[5m_\033[0m'
            global cheat_menu_color, cheat_menu_rainbow
            cheat_menu_color = cheat_menu_color_default  # Default cheat code color
            cheat_menu_rainbow = cheat_menu_rainbow_default     # Rainbow mode for cheat code menu
            # Print the cheat menu letter by letter over ~2 seconds
            import sys
            def rainbow_text(text):
                rainbow_colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
                return ''.join(rainbow_colors[i % len(rainbow_colors)] + c for i, c in enumerate(text)) + Style.RESET_ALL
            cheat_msg = f"Cheat Codes:{blink_underscore}\n  #09 - Adds 10 points to your score! ^_^\n  #10 - Removes 1 point from the CPU!\n  gun - Destroys everything (secret)\n  color <color> - Set all colors in color_list\n  cc color <color|rainbow> - Set the cheat code menu color\n  cc norainbow - Disable cheat code menu rainbow mode\n  rainbow - Set all choices to rainbow colors\n  norainbow - Disable rainbow mode\n  resetcheats - Remove all points added/removed by cheats (normal scores stay)\n  list - List all cheat codes\n  list all - List all cheat codes and normal commands\nType 'leave' to exit cheat codes menu."
            total_chars = len(cheat_msg)
            delay = 2.0 / max(total_chars, 1)
            for i, c in enumerate(cheat_msg):
                if cheat_menu_rainbow:
                    rainbow_colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
                    sys.stdout.write(rainbow_colors[i % len(rainbow_colors)] + c + Style.RESET_ALL)
                else:
                    sys.stdout.write(cheat_menu_color + c + Style.RESET_ALL)
                sys.stdout.flush()
                time.sleep(delay)
            print()  # Newline after menu
            rainbow_lines = cheat_msg.split('\n')
            print("========================================")
            # Track number of commands entered in the cheat menu
            if 'cheat_cmd_count' not in locals():
                cheat_cmd_count = 0
            last_color_set = None  # Track if a color was set in this menu session
            while True:
                # Rainbow prompt if enabled
                if cheat_menu_rainbow:
                    prompt = rainbow_text("Cheat menu> ")
                else:
                    prompt = cheat_menu_color + "Cheat menu> " + Style.RESET_ALL
                cmd = input(prompt).strip()
                cheat_cmd_count += 1
                # All cheat code handling ONLY in cheat menu
                if cmd == '#09':
                    player_score += 10
                    cheat_points_added += 10
                    cheat_msg = "Cheat code activated! +10 points! ^_^"
                    rainbow_colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
                    rainbow_cheat_text = "".join(rainbow_colors[i % len(rainbow_colors)] + c for i, c in enumerate(cheat_msg)) + Style.RESET_ALL
                    print(rainbow_cheat_text)
                    print(f"Your score: {player_score}")
                    print("=========================================")
                    time.sleep(2)
                    print("\033[F\033[K" * 3, end="")
                    continue
                if cmd == '#10':
                    cpu_score -= 1
                    cheat_points_removed += 1
                    print(Fore.MAGENTA + "Cheat code activated! -1 CPU point!" + Style.RESET_ALL)
                    print(f"CPU score: {cpu_score}")
                    print("=========================================")
                    time.sleep(2)
                    print("\033[F\033[K" * 3, end="")
                    continue
                if cmd.lower() == 'gun':
                    print(Fore.RED + "BOOM! (Rock, Paper, Scissors) have been destroyed!" + Style.RESET_ALL)
                    print("========================================")
                    time.sleep(3)
                    exit(0)
                if cmd.lower() == 'resetcheats':
                    reset_all_cheats()
                    print(Fore.CYAN + "All cheat points have been removed! (Normal scores remain)" + Style.RESET_ALL)
                    print("========================================")
                    continue
                if cmd.lower().startswith('cc norainbow'):
                    cheat_menu_rainbow = False
                    print(Fore.YELLOW + "Cheat code menu rainbow mode disabled. Menu will use the selected color." + Style.RESET_ALL)
                    print("========================================")
                    continue
                if cmd.lower().startswith('cc color '):
                    parts = cmd.split()
                    if len(parts) == 3:
                        color_name = parts[2].upper()
                        color_map = {
                            'RED': Fore.RED,
                            'GREEN': Fore.GREEN,
                            'YELLOW': Fore.YELLOW,
                            'BLUE': Fore.BLUE,
                            'MAGENTA': Fore.MAGENTA,
                            'CYAN': Fore.CYAN,
                            'WHITE': Fore.WHITE
                        }
                        if color_name == 'RAINBOW':
                            cheat_menu_rainbow = True
                            print(rainbow_text("Cheat code menu color set to RAINBOW"))
                        elif color_name in color_map:
                            cheat_menu_color = color_map[color_name]
                            cheat_menu_rainbow = False
                            print(cheat_menu_color + f"Cheat code menu color set to {color_name}" + Style.RESET_ALL)
                        else:
                            print(Fore.RED + "Invalid color name!" + Style.RESET_ALL)
                    else:
                        print(Fore.RED + "Usage: cc color <color|rainbow>" + Style.RESET_ALL)
                    print("========================================")
                    continue
                if cmd.lower().startswith('color '):
                    parts = cmd.split()
                    if len(parts) == 2:
                        color_name = parts[1].upper()
                        color_map = {
                            'RED': Fore.RED,
                            'GREEN': Fore.GREEN,
                            'YELLOW': Fore.YELLOW,
                            'BLUE': Fore.BLUE,
                            'MAGENTA': Fore.MAGENTA,
                            'CYAN': Fore.CYAN,
                            'WHITE': Fore.WHITE
                        }
                        if color_name in color_map:
                            for i in range(len(color_list)):
                                color_list[i] = color_map[color_name]
                            last_color_set = color_map[color_name]
                            print(Fore.YELLOW + f"All colors in color_list set to {color_name}" + Style.RESET_ALL)
                        else:
                            print(Fore.RED + "Invalid color name!" + Style.RESET_ALL)
                    else:
                        print(Fore.RED + "Usage: color <color>" + Style.RESET_ALL)
                    print("========================================")
                    continue
                if cmd.lower() == 'rainbow':
                    rainbow_mode = True
                    print(Fore.YELLOW + "All choices set to rainbow colors!" + Style.RESET_ALL)
                    print("========================================")
                    continue
                if cmd.lower() == 'norainbow':
                    rainbow_mode = False
                    print(Fore.YELLOW + "Rainbow mode disabled. Choices will use random colors." + Style.RESET_ALL)
                    print("========================================")
                    continue
                if cmd.lower() == 'leave':
                    # Use the clear command to clear the screen
                    import os
                    os.system('cls' if os.name == 'nt' else 'clear')
                    exit_cheat_menu = True
                    # After leaving, reprint the choices and prompt for seamless UI
                    if rainbow_mode:
                        rainbow_colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
                        def rainbow_color_text(text):
                            return ''.join(rainbow_colors[i % len(rainbow_colors)] + c for i, c in enumerate(text)) + Style.RESET_ALL
                        colored_choices = [rainbow_color_text(choice) for choice in choices]
                    elif last_color_set:
                        colored_choices = [last_color_set + choice + Style.RESET_ALL for choice in choices]
                    else:
                        colored_choices = [random.choice(color_list) + choice + Style.RESET_ALL for choice in choices]
                    print(" - ".join(colored_choices))
                    print("----------------------------------------")
                    # Don't prompt for input here, just restore the UI
                    break
                if cmd.lower() == 'list':
                    cheat_list = [
                        "#09 - Adds 10 points to your score! ^_^",
                        "#10 - Removes 1 point from the CPU!",
                        "gun - Destroys everything (secret)",
                        "color <color> - Set all colors in color_list",
                        "cc color <color|rainbow> - Set the cheat code menu color",
                        "cc norainbow - Disable cheat code menu rainbow mode",
                        "rainbow - Set all choices to rainbow colors",
                        "norainbow - Disable rainbow mode",
                        "resetcheats - Remove all points added/removed by cheats (normal scores stay)",
                        "leave - Exit cheat codes menu"
                    ]
                    print(Fore.GREEN + "Cheat Codes:" + Style.RESET_ALL)
                    if cheat_menu_rainbow:
                        rainbow_colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
                        for i, cheat in enumerate(cheat_list):
                            print(rainbow_colors[i % len(rainbow_colors)] + "  " + cheat + Style.RESET_ALL)
                    else:
                        cheat_color = cheat_menu_color if 'cheat_menu_color' in globals() else Fore.GREEN
                        for cheat in cheat_list:
                            print(cheat_color + "  " + cheat + Style.RESET_ALL)
                    print("========================================")
                    continue
                if cmd.lower() == 'list all':
                    cheat_list = [
                        "#09 - Adds 10 points to your score! ^_^",
                        "#10 - Removes 1 point from the CPU!",
                        "gun - Destroys everything (secret)",
                        "color <color> - Set all colors in color_list",
                        "cc color <color|rainbow> - Set the cheat code menu color",
                        "cc norainbow - Disable cheat code menu rainbow mode",
                        "rainbow - Set all choices to rainbow colors",
                        "norainbow - Disable rainbow mode",
                        "resetcheats - Remove all points added/removed by cheats (normal scores stay)",
                        "leave - Exit cheat codes menu"
                    ]
                    normal_commands = [
                        "Rock, Paper, Scissors - play a round",
                        "End - finish the game and show scores",
                        "Help - show this help message",
                        "Score - show the current scores",
                        "Clear - clear the screen and show the current score"
                    ]
                    print(Fore.GREEN + "Cheat Codes:" + Style.RESET_ALL)
                    if cheat_menu_rainbow:
                        rainbow_colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
                        for i, cheat in enumerate(cheat_list):
                            print(rainbow_colors[i % len(rainbow_colors)] + "  " + cheat + Style.RESET_ALL)
                    else:
                        cheat_color = cheat_menu_color if 'cheat_menu_color' in globals() else Fore.GREEN
                        for cheat in cheat_list:
                            print(cheat_color + "  " + cheat + Style.RESET_ALL)
                    print(Fore.YELLOW + "-"*40 + Style.RESET_ALL)
                    print(Fore.BLUE + "Normal Game:" + Style.RESET_ALL)
                    if cheat_menu_rainbow:
                        for i, cmd_text in enumerate(normal_commands):
                            print(rainbow_colors[i % len(rainbow_colors)] + "  " + cmd_text + Style.RESET_ALL)
                    else:
                        for cmd_text in normal_commands:
                            print(Fore.BLUE + "  " + cmd_text + Style.RESET_ALL)
                    print("========================================")
                    continue
                else:
                    print(Fore.YELLOW + "Unknown command. Type 'leave' to exit cheat codes menu." + Style.RESET_ALL)
                    print("========================================")
                    continue
        continue
    if player.lower() == 'clear':
        # Clear the terminal screen (works in most terminals)
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.CYAN + f"Screen cleared! Current Score -> Player: {player_score} | CPU: {cpu_score}" + Style.RESET_ALL)
        print("========================================")
        continue
    # Only allow valid game commands; if not recognized, print message
    valid_game_inputs = ["rock", "paper", "scissors", "end"]
    if player.lower() not in valid_game_inputs:
        print(Fore.RED + "Command not found!" + Style.RESET_ALL)
        print("========================================")
        continue
    ## Conditions of Rock,Paper and Scissors
    if player == computer:
        print(Fore.YELLOW + "Tie!" + Style.RESET_ALL)
        print("----------------------------------------")
    elif player == "Rock":
        if computer == "Paper":
            print(Fore.RED + "You lose!" + Style.RESET_ALL, computer, "covers", player)
            cpu_score+=1
            print("========================================")
        else:
            print(Fore.GREEN + "You win!" + Style.RESET_ALL, player, "smashes", computer)
            player_score+=1
            print("========================================")
    elif player == "Paper":
        if computer == "Scissors":
            print(Fore.RED + "You lose!" + Style.RESET_ALL, computer, "cut", player)
            cpu_score+=1
            print("========================================")
        else:
            print(Fore.GREEN + "You win!" + Style.RESET_ALL, player, "covers", computer)
            player_score+=1
            print("========================================")
    elif player == "Scissors":
        if computer == "Rock":
            print(Fore.RED + "You lose..." + Style.RESET_ALL, computer, "smashes", player)
            cpu_score+=1
            print("========================================")
        else:
            print(Fore.GREEN + "You win!" + Style.RESET_ALL, player, "cut", computer)
            player_score+=1
            print("========================================")
    elif player=='End':
        print("Final Scores:")
        if cpu_score > player_score:
            print(Fore.RED + f"Player:{player_score}" + Style.RESET_ALL)
            print(Fore.GREEN + f"CPU:{cpu_score}" + Style.RESET_ALL)
        elif player_score > cpu_score:
            print(Fore.GREEN + f"Player:{player_score}" + Style.RESET_ALL)
            print(Fore.RED + f"CPU:{cpu_score}" + Style.RESET_ALL)
        else:
            print(Fore.BLUE + f"tie! CPU:{cpu_score} Player:{player_score}" + Style.RESET_ALL)
            print("----------------------------------------")
        break