import random
import time
from colorama import Fore, Style, init
init(autoreset=True)
# Game mode selection
print(Fore.CYAN + "Choose your game mode:" + Style.RESET_ALL)
print(" 1. Rock, Paper, Scissors")
print(" 2. Rock, Paper, Scissors, Lizard, Spock")
print(" 3. Tic Tac Toe")
while True:
    mode = input("Enter 1, 2 or 3: ").strip()
    if mode == '1':
        choices = ["Rock", "Paper", "Scissors"]
        break
    elif mode == '2':
        choices = ["Rock", "Paper", "Scissors", "Lizard", "Spock"]
        break
    elif mode == '3':
        def print_board(board):
            def color_cell(cell):
                if cell.upper() == "X":
                    return Fore.GREEN + "X" + Style.RESET_ALL
                elif cell.upper() == "O":
                    return Fore.BLUE + "O" + Style.RESET_ALL
                else:
                    return cell
            # Numpad layout: 7|8|9, 4|5|6, 1|2|3
            idx = [6,7,8,3,4,5,0,1,2]
            print("\n ", color_cell(board[idx[0]]), "|", color_cell(board[idx[1]]), "|", color_cell(board[idx[2]]))
            print("---+---+---")
            print(" ", color_cell(board[idx[3]]), "|", color_cell(board[idx[4]]), "|", color_cell(board[idx[5]]))
            print("---+---+---")
            print(" ", color_cell(board[idx[6]]), "|", color_cell(board[idx[7]]), "|", color_cell(board[idx[8]]), "\n")

        def check_win(board, player):
            wins = [
                [0,1,2],[3,4,5],[6,7,8], # rows
                [0,3,6],[1,4,7],[2,5,8], # cols
                [0,4,8],[2,4,6]          # diags
            ]
            for line in wins:
                if all(board[i] == player for i in line):
                    return True
            return False

        def ttt():
            # Prompt user for X or O
            while True:
                player_symbol = input(Fore.CYAN + "Do you want to be X or O? (X goes first): " + Style.RESET_ALL).strip().upper()
                if player_symbol in ["X", "O"]:
                    break
                print(Fore.RED + "Please enter X or O." + Style.RESET_ALL)
            cpu_symbol = "O" if player_symbol == "X" else "X"
            current = "X"  # X always goes first
            board = [str(i+1) for i in range(9)]
            from sys import modules
            global getpass_asterisk
            if 'getpass_asterisk' not in globals():
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
            def ttt_help():
                print(Fore.GREEN + "Tic Tac Toe Help:" + Style.RESET_ALL)
                print("  Enter a number 1-9 to place your X.")
                print("  Type 'help' to see this menu.")
                print("  Type 'clear' to clear the screen.")
                print("  Type 'menu' to return to the main menu after a game.")
                print("  Made by Noahw1567")
                print(Fore.MAGENTA + "{:^40}".format("Have fun! ^_^") + Style.RESET_ALL)
                print("========================================")
            def ttt_clear():
                import os
                os.system('cls' if os.name == 'nt' else 'clear')
            def predict_cpu_move(board):
                def check_win(b, p):
                    wins = [
                        [0,1,2],[3,4,5],[6,7,8],
                        [0,3,6],[1,4,7],[2,5,8],
                        [0,4,8],[2,4,6]
                    ]
                    for line in wins:
                        if all(b[i] == p for i in line):
                            return True
                    return False
                def find_winning_move(b, p):
                    for i in range(9):
                        if b[i] not in ["X", "O"]:
                            b_copy = b[:]
                            b_copy[i] = p
                            if check_win(b_copy, p):
                                return i
                    return None
                move = find_winning_move(board, "O")
                if move is None:
                    move = find_winning_move(board, "X")
                if move is None and board[4] not in ["X", "O"]:
                    move = 4
                if move is None:
                    corners = [i for i in [0,2,6,8] if board[i] not in ["X", "O"]]
                    if corners:
                        move = corners[0]
                if move is None:
                    sides = [i for i in [1,3,5,7] if board[i] not in ["X", "O"]]
                    if sides:
                        move = sides[0]
                if move is None:
                    move = next((i for i, v in enumerate(board) if v not in ["X", "O"]), None)
                return move
            def ttt_cheat_menu(board):
                import sys
                cheat_menu_color = Fore.GREEN
                blink_underscore = '\033[5m_\033[0m'
                cheat_msg = f"Tic Tac Toe Cheat Codes:{blink_underscore}\n  predict - Show what the CPU would do next\n  list - List cheat commands\n  list all - List all commands\n  clear - Clear the screen\n  leave - Exit cheat codes menu."
                total_chars = len(cheat_msg)
                delay = 2.0 / max(total_chars, 1)
                for i, c in enumerate(cheat_msg):
                    sys.stdout.write(cheat_menu_color + c + Style.RESET_ALL)
                    sys.stdout.flush()
                    time.sleep(delay)
                print()  # Newline after menu
                print("========================================")
                while True:
                    cmd = input(cheat_menu_color + "Cheat menu> " + Style.RESET_ALL).strip().lower()
                    if cmd == 'predict':
                        move = predict_cpu_move(board)
                        if move is not None:
                            print(Fore.CYAN + f"If the CPU played now, it would choose position {move+1}." + Style.RESET_ALL)
                        else:
                            print(Fore.YELLOW + "No valid moves left for CPU." + Style.RESET_ALL)
                        print("========================================")
                        continue
                    if cmd == 'list':
                        print(Fore.CYAN + "Cheat Commands:" + Style.RESET_ALL)
                        print(cheat_menu_color + "predict - Show what the CPU would do next" + Style.RESET_ALL)
                        print(cheat_menu_color + "list - List cheat commands" + Style.RESET_ALL)
                        print(cheat_menu_color + "list all - List all commands" + Style.RESET_ALL)
                        print(cheat_menu_color + "clear - Clear the screen" + Style.RESET_ALL)
                        print(cheat_menu_color + "leave - Exit cheat codes menu" + Style.RESET_ALL)
                        print(cheat_menu_color + "bomb - Destroys everything (secret)" + Style.RESET_ALL)
                        print("========================================")
                        continue
                    if cmd == 'list all':
                        print(Fore.CYAN + "All Commands (Normal + Cheat):" + Style.RESET_ALL)
                        print(cheat_menu_color + "Normal Commands:" + Style.RESET_ALL)
                        print(cheat_menu_color + "  Enter a number 1-9 to place your X." + Style.RESET_ALL)
                        print(cheat_menu_color + "  help - Show help menu" + Style.RESET_ALL)
                        print(cheat_menu_color + "  clear - Clear the screen" + Style.RESET_ALL)
                        print(cheat_menu_color + "  menu - Return to main menu after a game" + Style.RESET_ALL)
                        print(cheat_menu_color + "Cheat Commands:" + Style.RESET_ALL)
                        print(cheat_menu_color + "  predict - Show what the CPU would do next" + Style.RESET_ALL)
                        print(cheat_menu_color + "  list - List cheat commands" + Style.RESET_ALL)
                        print(cheat_menu_color + "  list all - List all commands" + Style.RESET_ALL)
                        print(cheat_menu_color + "  clear - Clear the screen" + Style.RESET_ALL)
                        print(cheat_menu_color + "  leave - Exit cheat codes menu" + Style.RESET_ALL)
                        print(cheat_menu_color + "  bomb - Destroys everything (secret)" + Style.RESET_ALL)
                        print("========================================")
                        continue
                    if cmd == 'clear':
                        ttt_clear()
                        continue
                    if cmd == 'leave':
                        # Clear, show leaving message, then restore the Tic Tac Toe UI (only in TTT, not here)
                        import os
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print(Fore.YELLOW + "Leaving cheat codes menu..." + Style.RESET_ALL)
                        time.sleep(3)
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print(Fore.CYAN + "Tic Tac Toe" + Style.RESET_ALL)
                        # Removed print_board(board) here to avoid NameError in RPS mode
                        break
                    if cmd == 'bomb':
                        bomb_password = getpass_asterisk(Fore.GREEN + "Enter password to detonate the bomb:" + Style.RESET_ALL + " ")
                        if bomb_password != '1567':
                            print(Fore.RED + "Incorrect password! Bomb not detonated." + Style.RESET_ALL)
                            print("========================================")
                            continue
                        for i in range(3, 0, -1):
                            print(Fore.RED + f"Detonating in {i}..." + Style.RESET_ALL)
                            time.sleep(1)
                        print(Fore.RED + "BOOM! The Tic Tac Toe board has been destroyed!" + Style.RESET_ALL)
                        print("========================================")
                        time.sleep(3)
                        exit(0)
                    print(Fore.RED + "Command not found! Type 'list' to see cheat commands or 'leave' to exit." + Style.RESET_ALL)
                    print("========================================")
            for turn in range(9):
                print_board(board)
                if current == player_symbol:
                    while True:
                        move = input("Choose your move (1-9): ").strip().lower()
                        if move == 'help':
                            ttt_help()
                            continue
                        if move == 'clear':
                            ttt_clear()
                            continue
                        if move == 'help++':
                            try:
                                password = getpass_asterisk(Fore.GREEN + "Enter password to access cheat codes:" + Style.RESET_ALL + " ")
                            except Exception as e:
                                print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)
                                continue
                            if password == '1567':
                                ttt_cheat_menu(board)
                                # After leaving cheat menu, restore TTT UI
                                ttt_clear()
                                print(Fore.CYAN + "Tic Tac Toe" + Style.RESET_ALL)
                                print_board(board)
                                continue  # Prompt for move again
                            else:
                                print(Fore.RED + "Incorrect password!" + Style.RESET_ALL)
                            continue
                        if move in board:
                            move = int(move) - 1
                            board[move] = player_symbol
                            break
                        else:
                            print(Fore.RED + "Command not found!" + Style.RESET_ALL)
                else:                    # Smarter CPU: win, block, center, corners, sides
                    def find_winning_move(board, player):
                        for i in range(9):
                            if board[i] not in ["X", "O"]:
                                board_copy = board[:]
                                board_copy[i] = player
                                if check_win(board_copy, player):
                                    return i
                        return None
                    # Try to win
                    move = find_winning_move(board, "O")
                    if move is None:
                        # Try to block
                        move = find_winning_move(board, "X")
                    if move is None and board[4] not in ["X", "O"]:
                        move = 4  # Center
                    if move is None:
                        # Corners
                        corners = [i for i in [0,2,6,8] if board[i] not in ["X", "O"]]
                        if corners:
                            move = random.choice(corners)
                    if move is None:
                        # Sides
                        sides = [i for i in [1,3,5,7] if board[i] not in ["X", "O"]]
                        if sides:
                            move = random.choice(sides)
                    if move is None:
                        # Fallback (shouldn't happen)
                        move = next(i for i, v in enumerate(board) if v not in ["X", "O"])
                    board[move] = cpu_symbol
                    print(f"CPU chose {move+1}")
                if check_win(board, current):
                    print_board(board)
                    if current == player_symbol:
                        print(Fore.GREEN + "You win!" + Style.RESET_ALL)
                    else:
                        print(Fore.RED + "CPU wins!" + Style.RESET_ALL)
                    return
                current = cpu_symbol if current == player_symbol else player_symbol
            else:
                print_board(board)
                print(Fore.YELLOW + "It's a tie!" + Style.RESET_ALL)
        while True:
            ttt()
            while True:
                again = input(Fore.CYAN + "Play again? (y/n) or type 'menu' for main menu: " + Style.RESET_ALL).strip().lower()
                if again == 'y':
                    break  # break inner loop, play again
                elif again == 'menu' or again == 'n':
                    break  # break inner loop, exit to menu or quit
                else:
                    print(Fore.RED + "Please enter 'y', 'n', or 'menu'." + Style.RESET_ALL)
            if again == 'y':
                continue  # play again
            elif again == 'menu' or again == 'n':
                break  # exit to menu or quit
        if again == 'menu':
            continue
        exit(0)
    else:
        print(Fore.RED + "Invalid selection. Please enter 1, 2 or 3." + Style.RESET_ALL)

defeats = {
    # RPS
    "Rock":     ["Scissors", "Lizard"],
    "Paper":    ["Rock", "Spock"],
    "Scissors": ["Paper", "Lizard"],
    # RPSLS
    "Lizard":   ["Spock", "Paper"],
    "Spock":    ["Rock", "Scissors"]
}
defeat_verbs = {
    ("Rock", "Scissors"): "crushes",
    ("Rock", "Lizard"): "crushes",
    ("Paper", "Rock"): "covers",
    ("Paper", "Spock"): "disproves",
    ("Scissors", "Paper"): "cut",
    ("Scissors", "Lizard"): "decapitate",
    ("Lizard", "Spock"): "poisons",
    ("Lizard", "Paper"): "eats",
    ("Spock", "Rock"): "vaporizes",
    ("Spock", "Scissors"): "smashes"
}
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
system_random = random.SystemRandom()
while True:
    computer = system_random.choice(choices)  # More random computer choice each round
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
    if len(choices) == 3:
        prompt_text = "Rock, Paper or  Scissors?"
    else:
        prompt_text = "Rock, Paper, Scissors, Lizard or Spock?"
    player = input(prompt_text).capitalize()
    print("----------------------------------------")  # Add dashes after input
    if player.lower() == 'help':
        print(Fore.GREEN + "Valid inputs:" + Style.RESET_ALL)
        print("  Rock, Paper, Scissors - play a round")
        if len(choices) == 5:
            print("  Rock, Paper, Scissors, Lizard, Spock - play a round")
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
            cheat_msg = f"Cheat Codes:{blink_underscore}\n  #09 - Adds 10 points to your score! ^_^\n  #10 - Removes 1 point from the CPU!\n  color <color> - Set all colors in color_list\n  cc color <color|rainbow> - Set the cheat code menu color\n  cc norainbow - Disable cheat code menu rainbow mode\n  rainbow - Set all choices to rainbow colors\n  norainbow - Disable rainbow mode\n  resetcheats - Remove all points added/removed by cheats (normal scores stay)\n  list - List cheat commands\n  list all - List all commands\n  clear - Clear the screen\n  leave - Exit cheat codes menu."
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
            print("========================================")
            # Show scores, normal commands, and then enter cheat menu
            print(Fore.CYAN + f"Current Score -> Player: {player_score} | CPU: {cpu_score}" + Style.RESET_ALL)
            print(Fore.YELLOW + "-"*40 + Style.RESET_ALL)
            print(Fore.BLUE + "Normal Game Commands:" + Style.RESET_ALL)
            normal_commands = [
                "Rock, Paper, Scissors - play a round",
                "Rock, Paper, Scissors, Lizard, Spock - play a round",
                "End - finish the game and show scores",
                "Help - show this help message",
                "Score - show the current scores",
                "Clear - clear the screen and show the current score"
            ]
            # Animate normal commands at the same speed as the cheat codes menu
            normal_total_chars = sum(len(cmd) for cmd in normal_commands)
            normal_delay = 2.0 / max(normal_total_chars, 1)
            for i, cmd_text in enumerate(normal_commands):
                if cheat_menu_rainbow:
                    color = rainbow_colors[i % len(rainbow_colors)]
                else:
                    color = Fore.BLUE
                for c in cmd_text:
                    print(color + c + Style.RESET_ALL, end="", flush=True)
                    time.sleep(normal_delay)
                print()
            print()  # Blank line for clarity
            print(Fore.CYAN + f"Current Score -> Player: {player_score} | CPU: {cpu_score}" + Style.RESET_ALL)
            print("========================================")
            # Track number of commands entered in the cheat menu
            if 'cheat_cmd_count' not in locals():
                cheat_cmd_count = 0
            last_color_set = None  # Track if a color was set in this menu session
            # Ensure rainbow_colors is always defined for cheat menu commands
            rainbow_colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
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
                    # Clear, show leaving message, then restore the Tic Tac Toe UI (only in TTT, not here)
                    import os
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(Fore.YELLOW + "Leaving cheat codes menu..." + Style.RESET_ALL)
                    time.sleep(3)
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(Fore.CYAN + "Tic Tac Toe" + Style.RESET_ALL)
                    # Removed print_board(board) here to avoid NameError in RPS mode
                    break
                if cmd.lower() == 'list':
                    cheat_cmds = [
                        "#09 - Adds 10 points to your score! ^_^",
                        "#10 - Removes 1 point from the CPU!",
                        "color <color> - Set all colors in color_list",
                        "cc color <color|rainbow> - Set the cheat code menu color",
                        "cc norainbow - Disable cheat code menu rainbow mode",
                        "rainbow - Set all choices to rainbow colors",
                        "norainbow - Disable rainbow mode",
                        "resetcheats - Remove all points added/removed by cheats (normal scores stay)",
                        "list - List cheat commands",
                        "list all - List all commands (normal + cheats)",
                        "leave - Exit cheat codes menu",
                        "bomb - Destroys everything (secret)"
                    ]
                    print(Fore.CYAN + "Cheat Commands:" + Style.RESET_ALL)
                    for i, cmd_text in enumerate(cheat_cmds):
                        if cheat_menu_rainbow:
                            color = rainbow_colors[i % len(rainbow_colors)]
                        else:
                            color = cheat_menu_color
                        print(color + cmd_text + Style.RESET_ALL)
                    print("========================================")
                    continue
                if cmd.lower() == 'list all':
                    normal_cmds = [
                        "Rock, Paper, Scissors - play a round",
                        "Rock, Paper, Scissors, Lizard, Spock - play a round",
                        "End - finish the game and show scores",
                        "Help - show this help message",
                        "Score - show the current scores",
                        "Clear - clear the screen and show the current score"
                    ]
                    cheat_cmds = [
                        "#09 - Adds 10 points to your score! ^_^",
                        "#10 - Removes 1 point from the CPU!",
                        " - Destroys everything (secret)",
                        "color <color> - Set all colors in color_list",
                        "cc color <color|rainbow> - Set the cheat code menu color",
                        "cc norainbow - Disable cheat code menu rainbow mode",
                        "rainbow - Set all choices to rainbow colors",
                        "norainbow - Disable rainbow mode",
                        "resetcheats - Remove all points added/removed by cheats (normal scores stay)",
                        "list - List cheat commands",
                        "list all - List all commands (normal + cheats)",
                        "leave - Exit cheat codes menu"
                    ]
                    print(Fore.CYAN + "All Commands (Normal + Cheat, both modes):" + Style.RESET_ALL)
                    print((cheat_menu_color if not cheat_menu_rainbow else Fore.BLUE) + "Normal Game Commands:" + Style.RESET_ALL)
                    for i, cmd_text in enumerate(normal_cmds):
                        if cheat_menu_rainbow:
                            color = rainbow_colors[i % len(rainbow_colors)]
                        else:
                            color = cheat_menu_color
                        print(color + cmd_text + Style.RESET_ALL)
                    print((cheat_menu_color if not cheat_menu_rainbow else Fore.MAGENTA) + "Cheat Commands:" + Style.RESET_ALL)
                    for i, cmd_text in enumerate(cheat_cmds):
                        if cheat_menu_rainbow:
                            color = rainbow_colors[i % len(rainbow_colors)]
                        else:
                            color = cheat_menu_color
                        print(color + cmd_text + Style.RESET_ALL)
                    print("========================================")
                    continue
                if cmd.lower() == 'bomb':
                    bomb_password = getpass_asterisk(Fore.GREEN + "Enter password to detonate the bomb:" + Style.RESET_ALL + " ")
                    if bomb_password != '1567':
                        print(Fore.RED + "Incorrect password! Bomb not detonated." + Style.RESET_ALL)
                        print("========================================")
                        continue
                    for i in range(3, 0, -1):
                        print(Fore.RED + f"Detonating in {i}..." + Style.RESET_ALL)
                        time.sleep(1)
                    print(Fore.RED + "BOOM! The Tic Tac Toe board has been destroyed!" + Style.RESET_ALL)
                    print("========================================")
                    time.sleep(3)
                    exit(0)
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
    valid_game_inputs = [c.lower() for c in choices] + ["end"]
    if player.lower() not in valid_game_inputs:
        print(Fore.RED + "Command not found!" + Style.RESET_ALL)
        print("========================================")
        continue
    ## Conditions of Rock,Paper,Scissors,Lizard,Spock
    if player == computer:
        print(Fore.YELLOW + "Tie!" + Style.RESET_ALL)
        print("----------------------------------------")
    elif computer in defeats.get(player, []):
        verb = defeat_verbs.get((player, computer), "beats")
        print(Fore.GREEN + "You win!" + Style.RESET_ALL, player, verb, computer)
        player_score += 1
        print("========================================")
    elif player in defeats.get(computer, []):
        verb = defeat_verbs.get((computer, player), "beats")
        print(Fore.RED + "You lose!" + Style.RESET_ALL, computer, verb, player)
        cpu_score += 1
        print("========================================")
    elif player.lower() == 'end':
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