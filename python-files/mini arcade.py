import random
import time
import sys
import os
import msvcrt
from colorama import Fore, Style, init
init(autoreset=True)
# Game mode selection
print(Fore.MAGENTA + "🎮 Welcome to Mini Arcade! 🎮" + Style.RESET_ALL)
print(Fore.CYAN + "if you are new i would recommend checking the help section!" + Style.RESET_ALL)
print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)
print(Fore.YELLOW + "💡 Tip: Enter '6' for help, '7' or 'quit' to exit anytime!" + Style.RESET_ALL)
print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)
print()

def show_main_help():
    print(Fore.GREEN + "🎮 Mini Arcade - Help Menu" + Style.RESET_ALL)
    print("========================================")
    print(Fore.CYAN + "Available Games:" + Style.RESET_ALL)
    print(" 1. Rock, Paper, Scissors - Classic 3-choice game")
    print(" 2. Rock, Paper, Scissors, Lizard, Spock - 5-choice variation")
    print(" 3. Tic Tac Toe - Play against CPU on a 3x3 grid")
    print(" 4. Number Guessing Game - Guess the secret number")
    print(" 5. Hangman - Word guessing game with categories")
    print(" 6. Help - Show this help menu")
    print(" 7. Exit - Quit the arcade")
    print(" 8. Creator Signature - View the creator's ASCII signature")
    print()
    print(Fore.YELLOW + "Game Features:" + Style.RESET_ALL)
    print(" • Colorful interface with custom themes")
    print(" • Multiple difficulty levels")
    print(" • Score tracking and statistics")
    print(" • User-friendly help systems")
    print()
    print(Fore.MAGENTA + "Tips:" + Style.RESET_ALL)
    print(" • Type 'help' in most games for game-specific help")
    print(" • Type 'clear' to clear the screen")
    print(" • Type 'menu' to return to main menu")
    print(" • Look for hidden commands and easter eggs!")
    print()
    print(Fore.CYAN + "Created by Noahw1567" + Style.RESET_ALL)
    print(Fore.MAGENTA + "{:^40}".format("Have fun! ^_^") + Style.RESET_ALL)
    print("========================================")

while True:  # Main menu loop
    print(Fore.CYAN + "🎮 Mini Arcade - Choose your game mode:" + Style.RESET_ALL)
    print(" 1. Rock, Paper, Scissors")
    print(" 2. Rock, Paper, Scissors, Lizard, Spock")
    print(" 3. Tic Tac Toe")
    print(" 4. Number Guessing Game")
    print(" 5. Hangman")
    print(" 6. Help")
    print(" 7. Exit")
    print(" 8. Creator Signature")
    mode = input(Fore.GREEN + "Enter 1, 2, 3, 4, 5, 6, 7, 8, or 'quit': " + Style.RESET_ALL).strip()
    # Handle help and exit options first
    if mode == '6':
        show_main_help()
        continue
    elif mode == '7' or mode.lower() == 'quit':
        print(Fore.CYAN + "Thanks for playing Mini Arcade!" + Style.RESET_ALL)
        print(Fore.YELLOW + "Created by Noahw1567" + Style.RESET_ALL)
        print(Fore.MAGENTA + "Goodbye! 👋" + Style.RESET_ALL)
        exit(0)
    elif mode == '8':
        # Creator Signature
        def show_creator_signature():
            print(Fore.CYAN + "=" * 60 + Style.RESET_ALL)
            print(Fore.MAGENTA + "✨ Creator Signature ✨" + Style.RESET_ALL)
            print(Fore.CYAN + "=" * 60 + Style.RESET_ALL)
            print()
            
            # Your ASCII signature
            signature = r"""          
 |  \| | ___   __ _| |__    \ \  /\  / /__  ___| | ___ _   _ 
 | . ` |/ _ \ / _` | '_ \    \ \/  \/ / _ \/ __| |/ _ \ | | |
 | |\  | (_) | (_| | | | |    \  /\  /  __/\__ \ |  __/ |_| |
 |_| \_|\___/ \__,_|_| |_|     \/  \/ \___||___/_|\___|\__, |
                                                        __/ |
                                                       |___/ 
 
"""
            
            # Display the signature with color
            for line in signature.split('\n'):
                print(Fore.GREEN + line.center(60) + Style.RESET_ALL)
            
            print()
            print(Fore.YELLOW + "Created with ❤️ by Noahw1567" + Style.RESET_ALL)
            print(Fore.CYAN + "Mini Arcade - A collection of classic games" + Style.RESET_ALL)
            print(Fore.MAGENTA + "Hope you have fun playing! 🎮" + Style.RESET_ALL)
            print()
            print(Fore.CYAN + "=" * 60 + Style.RESET_ALL)
            
            # Wait for user to continue
            input(Fore.YELLOW + "Press Enter to return to main menu..." + Style.RESET_ALL)
            os.system('cls' if os.name == 'nt' else 'clear')
        
        show_creator_signature()
        continue  # Go back to main menu
    
    # Ask for username at the start of each game
    if mode in ['1', '2', '3', '4', '5']:
        username = input(Fore.YELLOW + "Enter your username (or 'quit' to return to menu): " + Fore.RED + Style.RESET_ALL).strip()
        if username.lower() == 'quit':
            continue  # Go back to main menu
        if not username:
            username = "Player"
        print(Fore.GREEN + f"Welcome, {username}!" + Style.RESET_ALL)
        print("========================================")
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
            print(Fore.BLUE + f"Playing as: {username}" + Style.RESET_ALL)
            print(Fore.CYAN + "Type 'help' for commands and game info." + Style.RESET_ALL)
            print("========================================")
            # Prompt user for X or O
            while True:
                player_symbol = input(Fore.CYAN + "Do you want to be X or O? (X goes first, or 'quit' to exit): " + Fore.RED + Style.RESET_ALL).strip().upper()
                if player_symbol == 'QUIT':
                    return "quit"
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
                print(Fore.GREEN + "🎯 Tic Tac Toe Help:" + Style.RESET_ALL)
                print("========================================")
                print(Fore.CYAN + "Objective:" + Style.RESET_ALL)
                print("  Get three of your symbols in a row, column, or diagonal")
                print("  Block the CPU from getting three in a row!")
                print()
                print(Fore.YELLOW + "How to Play:" + Style.RESET_ALL)
                print("  • Enter a number 1-9 to place your symbol")
                print("  • Numbers correspond to positions on the board:")
                print("    7 | 8 | 9")
                print("    ---------")
                print("    4 | 5 | 6")
                print("    ---------")
                print("    1 | 2 | 3")
                print()
                print(Fore.CYAN + "Commands:" + Style.RESET_ALL)
                print("  • 1-9 - Place your symbol at that position")
                print("  • 'help' - Show this help menu")
                print("  • 'clear' - Clear the screen")
                print("  • 'quit' - Show stats and return to main menu")
                print("  • 'help++' - Advanced cheat options (password required)")
                print("  • 'menu' - Return to main menu after game ends")
                print()
                print(Fore.MAGENTA + "Strategy Tips:" + Style.RESET_ALL)
                print("  • Control the center (position 5) when possible")
                print("  • Watch for two in a row to block or win")
                print("  • Corners are strong positions")
                print()
                print(Fore.GREEN + "Created by Noahw1567" + Style.RESET_ALL)
                print(Fore.MAGENTA + "{:^40}".format("Have fun! 🎮") + Style.RESET_ALL)
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
                        # Clear, show leaving message, then exit cheat codes menu (let main loop handle UI)
                        import os
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print(Fore.YELLOW + "Leaving cheat codes menu..." + Style.RESET_ALL)
                        time.sleep(1.5)
                        os.system('cls' if os.name == 'nt' else 'clear')
                        break
                    if cmd == 'bomb':
                        bomb_password = getpass_asterisk(Fore.GREEN + "Enter password to detonate the bomb:" + Style.RESET_ALL + " ")
                        if bomb_password != 'cessna172':
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
                        move = input(Fore.RED + "Choose your move (1-9): " + Style.RESET_ALL).strip().lower()
                        if move == 'help':
                            ttt_help()
                            continue
                        if move == 'quit':
                            os.system('cls' if os.name == 'nt' else 'clear')
                            print(Fore.CYAN + "Quitting Tic Tac Toe..." + Style.RESET_ALL)
                            print(Fore.YELLOW + f"Game Statistics:" + Style.RESET_ALL)
                            print(f"  • You are playing as: {player_symbol}")
                            print(f"  • CPU is playing as: {cpu_symbol}")
                            print(f"  • Current turn: {turn + 1}/9")
                            print("========================================")
                            return "quit"
                        if move == 'clear':
                            ttt_clear()
                            continue
                        if move == 'help++':
                            try:
                                password = getpass_asterisk(Fore.GREEN + "Enter password to access cheat codes:" + Style.RESET_ALL + " ")
                            except Exception as e:
                                print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)
                                continue
                            if password == 'cessna172':
                                ttt_cheat_menu(board)
                                # After leaving cheat menu, restore TTT UI
                                ttt_clear()
                                print(Fore.CYAN + "Tic Tac Toe" + Style.RESET_ALL)
                                print_board(board)
                                continue  # Prompt for move again
                            else:
                                print(Fore.RED + "Incorrect password!" + Style.RESET_ALL)
                            continue
                        if move == 'bomb':
                            bomb_password = getpass_asterisk(Fore.GREEN + "Enter password to detonate the bomb:" + Style.RESET_ALL + " ")
                            if bomb_password != 'cessna172':
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
                        print(Fore.GREEN + f"{username} wins!" + Style.RESET_ALL)
                    else:
                        print(Fore.RED + "CPU wins!" + Style.RESET_ALL)
                    return
                current = cpu_symbol if current == player_symbol else player_symbol
            else:
                print_board(board)
                print(Fore.YELLOW + "It's a tie!" + Style.RESET_ALL)
        while True:
            result = ttt()
            if result == "quit":
                break  # Go back to main menu
            while True:
                again = input(Fore.CYAN + "Play again? (y/n) or type 'menu' for main menu: " + Fore.RED + Style.RESET_ALL).strip().lower()
                if again == 'y':
                    break  # break inner loop, play again
                elif again == 'menu':
                    break  # break inner loop, go to main menu
                elif again == 'n':
                    break  # break inner loop, exit game
                else:
                    print(Fore.RED + "Please enter 'y', 'n', or 'menu'." + Style.RESET_ALL)
            if again == 'y':
                continue  # play again
            elif again == 'menu':
                break  # Exit the TTT loop to go back to main menu
            elif again == 'n':
                exit(0)  # exit the entire program
        # Break out of TTT and continue to main menu
        continue  # This will go back to the main game mode selection
    elif mode == '4':
        # Number Guessing Game
        def number_guessing_game():
            print(Fore.BLUE + f"Playing as: {username}" + Style.RESET_ALL)
            print("========================================")
            
            # Choose difficulty
            while True:
                print(Fore.CYAN + "Choose difficulty:" + Style.RESET_ALL)
                print(" 1. Easy (1-10)")
                print(" 2. Medium (1-50)")
                print(" 3. Hard (1-100)")
                print(" 4. Extreme (1-1000)")
                difficulty = input(Fore.RED + "Enter 1, 2, 3, 4, 'help', or 'quit': " + Style.RESET_ALL).strip()
                
                if difficulty.lower() == 'quit':
                    return "quit"
                if difficulty.lower() == 'help':
                    print(Fore.GREEN + "🎯 Number Guessing Game - Difficulty Help:" + Style.RESET_ALL)
                    print("========================================")
                    print(Fore.CYAN + "Choose your difficulty level:" + Style.RESET_ALL)
                    print("  1. Easy (1-10) - 5 attempts, great for beginners")
                    print("  2. Medium (1-50) - 7 attempts, moderate challenge")
                    print("  3. Hard (1-100) - 10 attempts, for experienced players")
                    print("  4. Extreme (1-1000) - 31 attempts, ultimate challenge")
                    print()
                    print(Fore.YELLOW + "Tip:" + Style.RESET_ALL)
                    print("  Higher difficulty = more possible numbers but more attempts!")
                    print("========================================")
                    continue
                elif difficulty == '1':
                    max_num = 10
                    difficulty_name = "Easy"
                    break
                elif difficulty == '2':
                    max_num = 50
                    difficulty_name = "Medium"
                    break
                elif difficulty == '3':
                    max_num = 100
                    difficulty_name = "Hard"
                    break
                elif difficulty == '4':
                    max_num = 1000
                    difficulty_name = "Extreme"
                    break
                else:
                    print(Fore.RED + "Invalid selection. Please enter 1, 2, 3, or 4." + Style.RESET_ALL)
            
            secret_number = random.randint(1, max_num)
            attempts = 0
            max_attempts = max(5, int(max_num ** 0.5))  # Scale attempts with difficulty
            
            print(Fore.GREEN + f"Difficulty: {difficulty_name} (1-{max_num})" + Style.RESET_ALL)
            print(Fore.YELLOW + f"You have {max_attempts} attempts to guess the number!" + Style.RESET_ALL)
            print("========================================")
            
            def number_help():
                print(Fore.GREEN + "🎯 Number Guessing Game Help:" + Style.RESET_ALL)
                print("========================================")
                print(Fore.CYAN + "Objective:" + Style.RESET_ALL)
                print(f"  Guess the secret number between 1 and {max_num}")
                print(f"  You have {max_attempts} attempts to find it!")
                print()
                print(Fore.YELLOW + "Commands:" + Style.RESET_ALL)
                print(f"  • Enter a number (1-{max_num}) - Make a guess")
                print("  • 'help' - Show this help menu")
                print("  • 'clear' - Clear the screen")
                print("  • 'give up' - Reveal the answer and end game")
                print("  • 'quit' - Show stats and return to main menu")
                print()
                print(Fore.CYAN + "Feedback System:" + Style.RESET_ALL)
                print("  • 'Too high!' - Your guess was above the secret number")
                print("  • 'Too low!' - Your guess was below the secret number")
                print("  • Green text - Correct guess!")
                print()
                print(Fore.MAGENTA + "Scoring:" + Style.RESET_ALL)
                print("  • Fewer attempts = Higher score")
                print("  • Try to guess efficiently!")
                print()
                print(Fore.GREEN + "Created by Noahw1567" + Style.RESET_ALL)
                print(Fore.MAGENTA + "{:^40}".format("Good luck! 🍀") + Style.RESET_ALL)
                print("========================================")
            
            print(Fore.CYAN + "Type 'help' for commands and game info." + Style.RESET_ALL)
            print("========================================")
            
            while attempts < max_attempts:
                try:
                    guess_input = input(Fore.RED + f"Guess #{attempts + 1}: Enter a number (1-{max_num}): " + Style.RESET_ALL).strip().lower()
                    
                    if guess_input == 'help':
                        number_help()
                        continue
                    elif guess_input == 'quit':
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print(Fore.CYAN + "Quitting Number Guessing Game..." + Style.RESET_ALL)
                        print(Fore.YELLOW + f"Game Statistics:" + Style.RESET_ALL)
                        print(f"  • Difficulty: {difficulty_name}")
                        print(f"  • Attempts used: {attempts}/{max_attempts}")
                        print(f"  • Secret number was: {secret_number}")
                        print("========================================")
                        return "quit"
                    elif guess_input == 'help++':
                        try:
                            password = getpass_asterisk(Fore.GREEN + "Enter password to access cheat codes:" + Style.RESET_ALL + " ")
                        except Exception as e:
                            print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)
                            continue
                        if password == 'cessna172':
                            # NGG Cheat Menu
                            cheat_menu_color = Fore.GREEN
                            blink_underscore = '\033[5m_\033[0m'
                            cheat_msg = f"Number Guessing Game Cheat Codes:{blink_underscore}\n  reveal - Show the secret number\n  skip - Skip to win instantly\n  +attempts - Add 5 more attempts\n  color <color> - Set text color\n  list - List cheat commands\n  list all - List all commands\n  clear - Clear the screen\n  leave - Exit cheat codes menu."
                            total_chars = len(cheat_msg)
                            delay = 2.0 / max(total_chars, 1)
                            for i, c in enumerate(cheat_msg):
                                import sys
                                sys.stdout.write(cheat_menu_color + c + Style.RESET_ALL)
                                sys.stdout.flush()
                                import time
                                time.sleep(delay)
                            print()
                            print("========================================")
                            
                            while True:
                                cmd = input(cheat_menu_color + "NGG Cheat menu> " + Style.RESET_ALL).strip().lower()
                                if cmd == 'reveal':
                                    print(Fore.YELLOW + f"🔍 The secret number is: {secret_number}" + Style.RESET_ALL)
                                    print("========================================")
                                    continue
                                elif cmd == 'skip':
                                    print(Fore.GREEN + "🎉 Cheat activated! You win instantly!" + Style.RESET_ALL)
                                    return True
                                elif cmd == '+attempts':
                                    max_attempts += 5
                                    print(Fore.CYAN + f"Added 5 attempts! You now have {max_attempts - attempts} attempts left." + Style.RESET_ALL)
                                    print("========================================")
                                    continue
                                elif cmd.startswith('color '):
                                    parts = cmd.split()
                                    if len(parts) == 2:
                                        color_name = parts[1].upper()
                                        color_map = {
                                            'RED': Fore.RED, 'GREEN': Fore.GREEN, 'YELLOW': Fore.YELLOW,
                                            'BLUE': Fore.BLUE, 'MAGENTA': Fore.MAGENTA, 'CYAN': Fore.CYAN, 'WHITE': Fore.WHITE
                                        }
                                        if color_name in color_map:
                                            cheat_menu_color = color_map[color_name]
                                            print(cheat_menu_color + f"Cheat menu color set to {color_name}" + Style.RESET_ALL)
                                        else:
                                            print(Fore.RED + "Invalid color! Use: red, green, yellow, blue, magenta, cyan, white" + Style.RESET_ALL)
                                    else:
                                        print(Fore.RED + "Usage: color <color>" + Style.RESET_ALL)
                                    print("========================================")
                                    continue
                                elif cmd == 'list':
                                    print(Fore.CYAN + "NGG Cheat Commands:" + Style.RESET_ALL)
                                    cheats = ["reveal - Show the secret number", "+attempts - Add 5 more attempts", "skip - Skip to win instantly", "color <color> - Set text color", "list - List cheat commands", "list all - List all commands", "clear - Clear the screen", "leave - Exit cheat menu"]
                                    for cheat in cheats:
                                        print(cheat_menu_color + cheat + Style.RESET_ALL)
                                    print("========================================")
                                    continue
                                elif cmd == 'list all':
                                    print(Fore.CYAN + "All Commands (Normal + Cheat):" + Style.RESET_ALL)
                                    print(cheat_menu_color + "Normal Commands:" + Style.RESET_ALL)
                                    print(cheat_menu_color + f"  Enter a number between 1 and {max_num}" + Style.RESET_ALL)
                                    print(cheat_menu_color + "  help - Show help menu" + Style.RESET_ALL)
                                    print(cheat_menu_color + "  clear - Clear the screen" + Style.RESET_ALL)
                                    print(cheat_menu_color + "  give up - Reveal the answer" + Style.RESET_ALL)
                                    print(cheat_menu_color + "Cheat Commands:" + Style.RESET_ALL)
                                    cheats = ["reveal - Show the secret number", "+attempts - Add 5 more attempts", "skip - Skip to win instantly", "color <color> - Set text color", "list - List cheat commands", "list all - List all commands", "clear - Clear the screen", "leave - Exit cheat menu"]
                                    for cheat in cheats:
                                        print(cheat_menu_color + cheat + Style.RESET_ALL)
                                    print("========================================")
                                    continue
                                elif cmd == 'clear':
                                    import os
                                    os.system('cls' if os.name == 'nt' else 'clear')
                                    print(Fore.CYAN + "Screen cleared!" + Style.RESET_ALL)
                                    print("========================================")
                                    continue
                                elif cmd == 'leave':
                                    import os
                                    os.system('cls' if os.name == 'nt' else 'clear')
                                    print(Fore.YELLOW + "Leaving cheat codes menu..." + Style.RESET_ALL)
                                    import time
                                    time.sleep(1.5)
                                    os.system('cls' if os.name == 'nt' else 'clear')
                                    break
                                else:
                                    print(Fore.RED + "Unknown command. Type 'list' to see cheat commands or 'leave' to exit." + Style.RESET_ALL)
                                    print("========================================")
                                    continue
                            continue
                        else:
                            print(Fore.RED + "Incorrect password!" + Style.RESET_ALL)
                        continue
                    elif guess_input == 'clear':
                        import os
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print(Fore.GREEN + f"Attempts left: {max_attempts - attempts}" + Style.RESET_ALL)
                        print("========================================")
                        continue
                    elif guess_input == 'give up':
                        print(Fore.RED + f"You gave up! The number was {secret_number}" + Style.RESET_ALL)
                        return False
                    
                    guess = int(guess_input)
                    attempts += 1
                    
                    if guess < 1 or guess > max_num:
                        print(Fore.RED + f"Please enter a number between 1 and {max_num}!" + Style.RESET_ALL)
                        attempts -= 1  # Don't count invalid guesses
                        continue
                    
                    if guess == secret_number:
                        print(Fore.GREEN + f"🎉 Congratulations! You guessed it in {attempts} attempts!" + Style.RESET_ALL)
                        # Scoring based on efficiency
                        score = max(1, max_attempts - attempts + 1)
                        print(Fore.CYAN + f"Score earned: {score} points!" + Style.RESET_ALL)
                        return True
                    elif guess < secret_number:
                        remaining = max_attempts - attempts
                        if remaining > 0:
                            print(Fore.YELLOW + f"Too low! {remaining} attempts remaining." + Style.RESET_ALL)
                        else:
                            print(Fore.YELLOW + "Too low!" + Style.RESET_ALL)
                    else:
                        remaining = max_attempts - attempts
                        if remaining > 0:
                            print(Fore.YELLOW + f"Too high! {remaining} attempts remaining." + Style.RESET_ALL)
                        else:
                            print(Fore.YELLOW + "Too high!" + Style.RESET_ALL)
                    
                    print("========================================")
                    
                except ValueError:
                    print(Fore.RED + "Please enter a valid number!" + Style.RESET_ALL)
                    continue
            
            print(Fore.RED + f"💥 Game Over! The number was {secret_number}" + Style.RESET_ALL)
            return False
        
        while True:
            result = number_guessing_game()
            if result == "quit":
                break  # Go back to main menu
            won = result
            while True:
                again = input(Fore.CYAN + "Play again? (y/n) or type 'menu' for main menu: " + Fore.RED + Style.RESET_ALL).strip().lower()
                if again == 'y':
                    break  # break inner loop, play again
                elif again == 'menu':
                    break  # break inner loop, go to main menu
                elif again == 'n':
                    break  # break inner loop, exit game
                else:
                    print(Fore.RED + "Please enter 'y', 'n', or 'menu'." + Style.RESET_ALL)
            if again == 'y':
                continue  # play again
            elif again == 'menu':
                break  # Exit to go back to main menu
            elif again == 'n':
                exit(0)  # exit the entire program
        continue  # This will go back to the main game mode selection
    elif mode == '5':
        # Hangman Game
        def hangman_game():
            # Word lists by category
            word_categories = {
                "Animals": ["elephant", "giraffe", "penguin", "dolphin", "kangaroo", "butterfly", "crocodile", "octopus", 
                           "cheetah", "rhinoceros", "hippopotamus", "zebra", "gorilla", "chimpanzee", "orangutan", "leopard",
                           "jaguar", "panther", "tiger", "lion", "bear", "wolf", "fox", "rabbit", "squirrel", "raccoon",
                           "skunk", "beaver", "otter", "seal", "whale", "shark", "stingray", "jellyfish", "starfish",
                           "seahorse", "turtle", "lizard", "snake", "iguana", "chameleon", "gecko", "salamander", "frog",
                           "eagle", "hawk", "owl", "parrot", "flamingo", "peacock", "ostrich", "toucan", "hummingbird"],
                "Movies": ["inception", "avatar", "titanic", "jaws", "frozen", "shrek", "matrix", "batman", "superman",
                          "spiderman", "ironman", "avengers", "jurassic", "gladiator", "casablanca", "godfather", "scarface",
                          "goodfellas", "pulpfiction", "django", "inglourious", "reservoir", "killbill", "rocky", "rambo",
                          "terminator", "alien", "predator", "robocop", "blade", "highlander", "conan", "300", "troy",
                          "braveheart", "kingdom", "pirates", "transformers", "starwars", "startrek", "dune", "arrival",
                          "interstellar", "gravity", "martian", "prometheus", "blade2049", "minority", "total", "demolition"],
                "Countries": ["australia", "canada", "brazil", "japan", "egypt", "france", "mexico", "russia", "china",
                             "india", "germany", "italy", "spain", "portugal", "greece", "turkey", "poland", "norway",
                             "sweden", "finland", "denmark", "netherlands", "belgium", "switzerland", "austria", "hungary",
                             "romania", "bulgaria", "croatia", "serbia", "ukraine", "belarus", "lithuania", "latvia",
                             "estonia", "ireland", "scotland", "wales", "england", "iceland", "argentina", "chile",
                             "colombia", "venezuela", "peru", "bolivia", "uruguay", "paraguay", "ecuador", "panama"],
                "Food": ["pizza", "burger", "sushi", "tacos", "pasta", "cookie", "sandwich", "chocolate", "icecream",
                        "pancakes", "waffles", "donuts", "bagels", "croissant", "muffin", "cupcake", "brownie", "cheesecake",
                        "tiramisu", "pudding", "yogurt", "cereal", "oatmeal", "granola", "smoothie", "milkshake", "coffee",
                        "cappuccino", "espresso", "latte", "mocha", "frappuccino", "lasagna", "spaghetti", "ravioli",
                        "gnocchi", "risotto", "paella", "tempura", "ramen", "pho", "curry", "biryani", "kebab", "falafel",
                        "hummus", "guacamole", "salsa", "nachos", "quesadilla", "burrito", "enchilada", "chimichanga"],
                "Random": ["computer", "rainbow", "treasure", "adventure", "mystery", "journey", "diamond", "wizard",
                          "castle", "dragon", "knight", "princess", "magic", "spell", "potion", "crystal", "sword",
                          "shield", "armor", "helmet", "crown", "throne", "kingdom", "empire", "fortress", "tower",
                          "bridge", "mountain", "valley", "forest", "desert", "ocean", "island", "volcano", "earthquake",
                          "thunder", "lightning", "hurricane", "tornado", "blizzard", "avalanche", "glacier", "comet",
                          "asteroid", "galaxy", "universe", "planet", "satellite", "telescope", "microscope", "laboratory"]
            }
            
            print(Fore.BLUE + f"Playing as: {username}" + Style.RESET_ALL)
            print("========================================")
            
            # Choose category
            while True:
                print(Fore.CYAN + "Choose a category:" + Style.RESET_ALL)
                categories = list(word_categories.keys())
                for i, category in enumerate(categories, 1):
                    print(f" {i}. {category}")
                print(f" {len(categories) + 1}. Random (any category)")
                
                choice = input(Fore.RED + f"Enter 1-{len(categories) + 1}, 'help', or 'quit': " + Style.RESET_ALL).strip()
                
                if choice.lower() == 'quit':
                    return "quit"
                if choice.lower() == 'help':
                    print(Fore.GREEN + "🎪 Hangman - Category Help:" + Style.RESET_ALL)
                    print("========================================")
                    print(Fore.CYAN + "Available Categories:" + Style.RESET_ALL)
                    print("  1. Animals - Various animals from around the world")
                    print("  2. Movies - Popular films and cinema")
                    print("  3. Countries - Nations from all continents")
                    print("  4. Food - Delicious dishes and cuisine")
                    print("  5. Random - Mix of different categories")
                    print("  6. Random (any category) - Words from all categories")
                    print()
                    print(Fore.YELLOW + "Tip:" + Style.RESET_ALL)
                    print("  Each category has different difficulty levels!")
                    print("  Animals and Food tend to be easier than Movies.")
                    print("========================================")
                    continue
                
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(categories):
                        selected_category = categories[choice_num - 1]
                        word_list = word_categories[selected_category]
                        break
                    elif choice_num == len(categories) + 1:
                        selected_category = "Random"
                        word_list = [word for words in word_categories.values() for word in words]
                        break
                    else:
                        print(Fore.RED + f"Please enter a number between 1 and {len(categories) + 1}." + Style.RESET_ALL)
                except ValueError:
                    print(Fore.RED + "Please enter a valid number!" + Style.RESET_ALL)
            
            word = random.choice(word_list).upper()
            guessed_letters = set()
            wrong_guesses = []
            max_wrong = 6
            
            print(Fore.GREEN + f"Category: {selected_category}" + Style.RESET_ALL)
            print(Fore.YELLOW + f"Word has {len(word)} letters" + Style.RESET_ALL)
            print(Fore.CYAN + "Type 'help' for commands and game info." + Style.RESET_ALL)
            print("========================================")
            
            def draw_hangman(wrong_count):
                hangman_stages = [
                    "",  # 0 wrong
                    "  ___\n  |  |\n  |\n  |\n  |\n__|__",  # 1 wrong
                    "  ___\n  |  |\n  |  O\n  |\n  |\n__|__",  # 2 wrong
                    "  ___\n  |  |\n  |  O\n  |  |\n  |\n__|__",  # 3 wrong
                    "  ___\n  |  |\n  |  O\n  | /|\n  |\n__|__",  # 4 wrong
                    "  ___\n  |  |\n  |  O\n  | /|\\\n  |\n__|__",  # 5 wrong
                    "  ___\n  |  |\n  |  O\n  | /|\\\n  | / \\\n__|__",  # 6 wrong (both legs)
                ]
                if wrong_count < len(hangman_stages):
                    return hangman_stages[wrong_count]
                return hangman_stages[-1]
            
            def display_word():
                display = ""
                for letter in word:
                    if letter in guessed_letters:
                        display += Fore.GREEN + letter + Style.RESET_ALL + " "
                    else:
                        display += "_ "
                return display.strip()
            
            def hangman_help():
                print(Fore.GREEN + "🎪 Hangman Game Help:" + Style.RESET_ALL)
                print("========================================")
                print(Fore.CYAN + "Objective:" + Style.RESET_ALL)
                print(f"  Guess the secret word from the '{selected_category}' category")
                print(f"  You have {max_wrong} wrong guesses before the hangman is complete!")
                print()
                print(Fore.YELLOW + "Commands:" + Style.RESET_ALL)
                print("  • Enter a letter (A-Z) - Make a guess")
                print("  • 'help' - Show this help menu")
                print("  • 'clear' - Clear the screen")
                print("  • 'give up' - Reveal the answer and end game")
                print("  • 'quit' - Show stats and return to main menu")
                print()
                print(Fore.CYAN + "How to Play:" + Style.RESET_ALL)
                print("  • Correct letters will appear in the word")
                print("  • Wrong letters will be listed and add to the hangman")
                print("  • Win by guessing all letters before hangman is complete")
                print("  • Letters are not case-sensitive")
                print()
                print(Fore.MAGENTA + "Visual Guide:" + Style.RESET_ALL)
                print("  • Green letters = Correctly guessed")
                print("  • Underscores (_) = Letters not yet guessed")
                print("  • Hangman drawing shows remaining chances")
                print()
                print(Fore.GREEN + "Created by Noahw1567" + Style.RESET_ALL)
                print(Fore.MAGENTA + "{:^40}".format("Good luck! 🎯") + Style.RESET_ALL)
                print("========================================")
            
            while len(wrong_guesses) < max_wrong:
                # Display current state
                print(Fore.CYAN + draw_hangman(len(wrong_guesses)) + Style.RESET_ALL)
                print(f"\nWord: {display_word()}")
                print(f"Wrong guesses: {', '.join(wrong_guesses) if wrong_guesses else 'None'}")
                print(f"Remaining tries: {max_wrong - len(wrong_guesses)}")
                print("========================================")
                
                # Check win condition
                if all(letter in guessed_letters for letter in word):
                    print(Fore.GREEN + f"🎉 Congratulations! You guessed '{word}' correctly!" + Style.RESET_ALL)
                    return True
                
                # Get user input
                guess_input = input(Fore.RED + "Enter a letter: " + Style.RESET_ALL).strip().lower()
                
                if guess_input == 'help':
                    hangman_help()
                    continue
                elif guess_input == 'quit':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(Fore.CYAN + "Quitting Hangman..." + Style.RESET_ALL)
                    print(Fore.YELLOW + f"Game Statistics:" + Style.RESET_ALL)
                    print(f"  • Category: {selected_category}")
                    print(f"  • Word was: {word}")
                    print(f"  • Letters guessed: {', '.join(sorted(guessed_letters)) if guessed_letters else 'None'}")
                    print(f"  • Wrong guesses: {', '.join(wrong_guesses) if wrong_guesses else 'None'}")
                    print(f"  • Tries remaining: {max_wrong - len(wrong_guesses)}")
                    print("========================================")
                    return "quit"
                elif guess_input == 'help++':
                    try:
                        password = getpass_asterisk(Fore.GREEN + "Enter password to access cheat codes:" + Style.RESET_ALL + " ")
                    except Exception as e:
                        print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)
                        continue
                    if password == 'cessna172':
                        # Hangman Cheat Menu
                        cheat_menu_color = Fore.GREEN
                        blink_underscore = '\033[5m_\033[0m'
                        cheat_msg = f"Hangman Cheat Codes:{blink_underscore}\n  reveal - Show the secret word\n  hint - Show a random letter\n  skip - Skip to win instantly\n  +tries - Add 3 more tries\n  color <color> - Set text color\n  list - List cheat commands\n  list all - List all commands\n  clear - Clear the screen\n  leave - Exit cheat codes menu."
                        total_chars = len(cheat_msg)
                        delay = 2.0 / max(total_chars, 1)
                        for i, c in enumerate(cheat_msg):
                            import sys
                            sys.stdout.write(cheat_menu_color + c + Style.RESET_ALL)
                            sys.stdout.flush()
                            import time
                            time.sleep(delay)
                        print()
                        print("========================================")
                        
                        while True:
                            cmd = input(cheat_menu_color + "Hangman Cheat menu> " + Style.RESET_ALL).strip().lower()
                            if cmd == 'reveal':
                                print(Fore.YELLOW + f"🔍 The secret word is: {word}" + Style.RESET_ALL)
                                print("========================================")
                                continue
                            elif cmd == 'hint':
                                # Add a random letter from the word that hasn't been guessed
                                unguessed = [letter for letter in set(word) if letter not in guessed_letters]
                                if unguessed:
                                    hint_letter = random.choice(unguessed)
                                    guessed_letters.add(hint_letter)
                                    print(Fore.CYAN + f"💡 Hint: The letter '{hint_letter}' is in the word!" + Style.RESET_ALL)
                                else:
                                    print(Fore.YELLOW + "No more hints available - you've found all letters!" + Style.RESET_ALL)
                                print("========================================")
                                continue
                            elif cmd == 'skip':
                                print(Fore.GREEN + "🎉 Cheat activated! You win instantly!" + Style.RESET_ALL)
                                return True
                            elif cmd == '+tries':
                                max_wrong += 3
                                print(Fore.CYAN + f"Added 3 tries! You now have {max_wrong - len(wrong_guesses)} tries left." + Style.RESET_ALL)
                                print("========================================")
                                continue
                            elif cmd.startswith('color '):
                                parts = cmd.split()
                                if len(parts) == 2:
                                    color_name = parts[1].upper()
                                    color_map = {
                                        'RED': Fore.RED, 'GREEN': Fore.GREEN, 'YELLOW': Fore.YELLOW,
                                        'BLUE': Fore.BLUE, 'MAGENTA': Fore.MAGENTA, 'CYAN': Fore.CYAN, 'WHITE': Fore.WHITE
                                    }
                                    if color_name in color_map:
                                        cheat_menu_color = color_map[color_name]
                                        print(cheat_menu_color + f"Cheat menu color set to {color_name}" + Style.RESET_ALL)
                                    else:
                                        print(Fore.RED + "Invalid color! Use: red, green, yellow, blue, magenta, cyan, white" + Style.RESET_ALL)
                                else:
                                    print(Fore.RED + "Usage: color <color>" + Style.RESET_ALL)
                                print("========================================")
                                continue
                            elif cmd == 'list':
                                print(Fore.CYAN + "Hangman Cheat Commands:" + Style.RESET_ALL)
                                cheats = ["reveal - Show the secret word", "hint - Show a random letter", "skip - Skip to win instantly", "+tries - Add 3 more tries", "color <color> - Set text color", "list - List cheat commands", "list all - List all commands", "clear - Clear the screen", "leave - Exit cheat menu"]
                                for cheat in cheats:
                                    print(cheat_menu_color + cheat + Style.RESET_ALL)
                                print("========================================")
                                continue
                            elif cmd == 'list all':
                                print(Fore.CYAN + "All Commands (Normal + Cheat):" + Style.RESET_ALL)
                                print(cheat_menu_color + "Normal Commands:" + Style.RESET_ALL)
                                print(cheat_menu_color + "  Enter a letter to guess" + Style.RESET_ALL)
                                print(cheat_menu_color + "  help - Show help menu" + Style.RESET_ALL)
                                print(cheat_menu_color + "  clear - Clear the screen" + Style.RESET_ALL)
                                print(cheat_menu_color + "  give up - Reveal the answer" + Style.RESET_ALL)
                                print(cheat_menu_color + "Cheat Commands:" + Style.RESET_ALL)
                                cheats = ["reveal - Show the secret word", "hint - Show a random letter", "skip - Skip to win instantly", "+tries - Add 3 more tries", "color <color> - Set text color", "list - List cheat commands", "list all - List all commands", "clear - Clear the screen", "leave - Exit cheat menu"]
                                for cheat in cheats:
                                    print(cheat_menu_color + cheat + Style.RESET_ALL)
                                print("========================================")
                                continue
                            elif cmd == 'clear':
                                import os
                                os.system('cls' if os.name == 'nt' else 'clear')
                                print(Fore.CYAN + "Screen cleared!" + Style.RESET_ALL)
                                print("========================================")
                                continue
                            elif cmd == 'leave':
                                import os
                                os.system('cls' if os.name == 'nt' else 'clear')
                                print(Fore.YELLOW + "Leaving cheat codes menu..." + Style.RESET_ALL)
                                import time
                                time.sleep(1.5)
                                os.system('cls' if os.name == 'nt' else 'clear')
                                break
                            else:
                                print(Fore.RED + "Unknown command. Type 'list' to see cheat commands or 'leave' to exit." + Style.RESET_ALL)
                                print("========================================")
                                continue
                        continue
                    else:
                        print(Fore.RED + "Incorrect password!" + Style.RESET_ALL)
                    continue
                elif guess_input == 'clear':
                    import os
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                elif guess_input == 'give up':
                    print(Fore.RED + f"You gave up! The word was '{word}'" + Style.RESET_ALL)
                    return False
                
                if len(guess_input) != 1 or not guess_input.isalpha():
                    print(Fore.RED + "Please enter a single letter!" + Style.RESET_ALL)
                    continue
                
                guess = guess_input.upper()
                
                if guess in guessed_letters or guess in [g.upper() for g in wrong_guesses]:
                    print(Fore.YELLOW + f"You already guessed '{guess}'" + Style.RESET_ALL)
                    continue
                
                if guess in word:
                    guessed_letters.add(guess)
                    print(Fore.GREEN + f"Good guess! '{guess}' is in the word!" + Style.RESET_ALL)
                    # Don't add to wrong_guesses, so remaining tries stay the same
                else:
                    wrong_guesses.append(guess)
                    remaining_tries = max_wrong - len(wrong_guesses)
                    print(Fore.RED + f"Sorry, '{guess}' is not in the word." + Style.RESET_ALL)
                    if remaining_tries > 0:
                        print(Fore.YELLOW + f"Remaining tries: {remaining_tries}" + Style.RESET_ALL)
                
                print("========================================")
            
            # Game over
            print(Fore.CYAN + draw_hangman(len(wrong_guesses)) + Style.RESET_ALL)
            print(Fore.RED + f"💀 Game Over! The word was '{word}'" + Style.RESET_ALL)
            return False
        
        while True:
            result = hangman_game()
            if result == "quit":
                break  # Go back to main menu
            won = result
            while True:
                again = input(Fore.CYAN + "Play again? (y/n) or type 'menu' for main menu: " + Fore.RED + Style.RESET_ALL).strip().lower()
                if again == 'y':
                    break  # break inner loop, play again
                elif again == 'menu':
                    break  # break inner loop, go to main menu
                elif again == 'n':
                    break  # break inner loop, exit game
                else:
                    print(Fore.RED + "Please enter 'y', 'n', or 'menu'." + Style.RESET_ALL)
            if again == 'y':
                continue  # play again
            elif again == 'menu':
                break  # Exit to go back to main menu
            elif again == 'n':
                exit(0)  # exit the entire program
        continue  # This will go back to the main game mode selection
    else:
        print(Fore.RED + "Invalid selection. Please enter 1, 2, 3, 4, 5, 6, 7, 8, or 'quit'." + Style.RESET_ALL)
        print(Fore.YELLOW + "Tip: Enter 6 for help, 7 to exit, 8 for creator signature, or 'quit' to exit." + Style.RESET_ALL)
        continue  # Go back to main menu selection

# This section will only execute for Rock Paper Scissors modes (1 or 2)

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
print(Fore.BLUE + f"Playing as: {username}" + Style.RESET_ALL)
print("========================================")
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
        prompt_text = "Rock, Paper or Scissors? (or 'quit' to exit): "
    else:
        prompt_text = "Rock, Paper, Scissors, Lizard or Spock? (or 'quit' to exit): "
    player = input(prompt_text).strip()  # <-- remove .capitalize()
    print("----------------------------------------")  # Add dashes after input
    if player.lower() == 'bomb':
        bomb_password = getpass_asterisk(Fore.GREEN + "Enter password to detonate the bomb:" + Style.RESET_ALL + " ")
        if bomb_password != 'cessna172':
            print(Fore.RED + "Incorrect password! Bomb not detonated." + Style.RESET_ALL)
            print("========================================")
            continue
        for i in range(3, 0, -1):
            print(Fore.RED + f"Detonating in {i}..." + Style.RESET_ALL)
            time.sleep(1)
        print(Fore.RED + "BOOM! The game has been destroyed!" + Style.RESET_ALL)
        print("========================================")
        time.sleep(3)
        exit(0)
    if player.lower() == 'help':
        if len(choices) == 3:
            print(Fore.GREEN + "✂️ Rock Paper Scissors Help:" + Style.RESET_ALL)
            print("========================================")
            print(Fore.CYAN + "Objective:" + Style.RESET_ALL)
            print("  Beat the CPU by choosing the winning option!")
            print()
            print(Fore.YELLOW + "Game Rules:" + Style.RESET_ALL)
            print("  • Rock crushes Scissors")
            print("  • Paper covers Rock")
            print("  • Scissors cut Paper")
            print()
        else:
            print(Fore.GREEN + "🖖 Rock Paper Scissors Lizard Spock Help:" + Style.RESET_ALL)
            print("========================================")
            print(Fore.CYAN + "Objective:" + Style.RESET_ALL)
            print("  Beat the CPU in this expanded version!")
            print()
            print(Fore.YELLOW + "Game Rules:" + Style.RESET_ALL)
            print("  • Rock crushes Scissors & Lizard")
            print("  • Paper covers Rock & disproves Spock")
            print("  • Scissors cut Paper & decapitate Lizard")
            print("  • Lizard poisons Spock & eats Paper")
            print("  • Spock vaporizes Rock & smashes Scissors")
            print()
        print(Fore.MAGENTA + "Commands:" + Style.RESET_ALL)
        print("  • Rock/Paper/Scissors" + ("/Lizard/Spock" if len(choices) == 5 else "") + " - Make your choice")
        print("  • 'help' - Show this help menu")
        print("  • 'score' - Show current scores")
        print("  • 'clear' - Clear screen and show score")
        print("  • 'end' - Finish game and show final scores")
        print("  • 'quit' - Show scores and return to main menu")
        print("  • 'help++' - Advanced cheat options (password required)")
        print()
        print(Fore.CYAN + "Scoring:" + Style.RESET_ALL)
        print("  • Win = +1 point for you")
        print("  • Lose = +1 point for CPU")
        print("  • Tie = No points awarded")
        print()
        print(Fore.GREEN + "Created by Noahw1567" + Style.RESET_ALL)
        print(Fore.MAGENTA + "{:^40}".format("Have fun! 🎮") + Style.RESET_ALL)
        print("========================================")
        continue
    if player.lower() == 'quit':
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.CYAN + f"Quitting {' & '.join(choices)} game..." + Style.RESET_ALL)
        print(Fore.YELLOW + f"Final Scores:" + Style.RESET_ALL)
        print(Fore.GREEN + f"{username}: {player_score} | CPU: {cpu_score}" + Style.RESET_ALL)
        if player_score > cpu_score:
            print(Fore.GREEN + f"🎉 {username} wins overall!" + Style.RESET_ALL)
        elif cpu_score > player_score:
            print(Fore.RED + "💻 CPU wins overall!" + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + "🤝 It's a tie overall!" + Style.RESET_ALL)
        print("========================================")
        break  # Exit the main RPS loop to go back to main menu
    if player.lower() == 'score':
        print(Fore.GREEN + f"Current Score -> {username}: {player_score} | CPU: {cpu_score}" + Style.RESET_ALL)
        print("========================================")
        continue
    if player.lower() == 'clear':
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.GREEN + f"Current Score -> {username}: {player_score} | CPU: {cpu_score}" + Style.RESET_ALL)
        print("========================================")
        continue
    if player.lower() == 'end':
        print(Fore.CYAN + "Final Scores:" + Style.RESET_ALL)
        print(Fore.GREEN + f"{username}: {player_score} | CPU: {cpu_score}" + Style.RESET_ALL)
        if player_score > cpu_score:
            print(Fore.GREEN + f"{username} wins overall! Congratulations!" + Style.RESET_ALL)
        elif cpu_score > player_score:
            print(Fore.RED + f"CPU wins overall! Better luck next time, {username}!" + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + f"It's a tie overall! Great game, {username}!" + Style.RESET_ALL)
        print("========================================")
        print(Fore.MAGENTA + f"Thanks for playing, {username}!" + Style.RESET_ALL)
        exit(0)
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
            if password != 'cessna172':
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
            cheat_msg = f"Cheat Codes:{blink_underscore}\n  #09 - Adds 10 points to your score! ^_^\n  #10 - Removes 1 point from the CPU!\n  color <color> - Set all colors in color_list\n  cc color <color|rainbow> - Set the cheat code menu color\n  cc norainbow - Disable cheat code menu rainbow mode\n  rainbow - Set all choices to rainbow colors\n  norainbow - Disable rainbow mode\n  resetcheats - Remove all points added/removed by cheats (normal scores stay)\n  bomb - Destroys everything (secret)\n  list - List cheat commands\n  list all - List all commands\n  clear - Clear the screen\n  leave - Exit cheat codes menu."
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
            print(Fore.CYAN + f"Current Score -> {username}: {player_score} | CPU: {cpu_score}" + Style.RESET_ALL)
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
            print(Fore.CYAN + f"Current Score -> {username}: {player_score} | CPU: {cpu_score}" + Style.RESET_ALL)
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
                # --- Begin all cheat commands in original order ---
                if cmd == '#09':
                    player_score += 10
                    cheat_points_added += 10
                    cheat_msg = "Cheat code activated! +10 points! ^_^"
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
                            print(rainbow_text("Cheat code menu prompt set to RAINBOW"))
                        elif color_name in color_map:
                            cheat_menu_color = color_map[color_name]
                            cheat_menu_rainbow = False
                            print(cheat_menu_color + f"Cheat code menu prompt set to {color_name}" + Style.RESET_ALL)
                        else:
                            print(Fore.RED + "Invalid color name!" + Style.RESET_ALL)
                    else:
                        print(Fore.RED + "Usage: cc color <color|rainbow>" + Style.RESET_ALL)
                    print("========================================")
                    continue
                if cmd.lower() == 'cc norainbow':
                    cheat_menu_rainbow = False
                    print(Fore.YELLOW + "Cheat code menu rainbow prompt disabled. Menu will use the selected color." + Style.RESET_ALL)
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
                if cmd.lower() == 'resetcheats':
                    reset_all_cheats()
                    print(Fore.CYAN + "All cheat points have been removed! (Normal scores remain)" + Style.RESET_ALL)
                    print("========================================")
                    continue
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
                if cmd.lower() == 'clear':
                    import os
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(Fore.CYAN + "Screen cleared!" + Style.RESET_ALL)
                    print("========================================")
                    continue
                if cmd.lower() == 'leave':
                    import os
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(Fore.YELLOW + "Leaving cheat codes menu..." + Style.RESET_ALL)
                    time.sleep(1.5)
                    os.system('cls' if os.name == 'nt' else 'clear')
                    exit_cheat_menu = True
                    break
                if cmd.lower() == 'bomb':
                    bomb_password = getpass_asterisk(Fore.GREEN + "Enter password to detonate the bomb:" + Style.RESET_ALL + " ")
                    if bomb_password != 'cessna172':
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
                # Unknown command
                print(Fore.YELLOW + "Unknown command. Type 'leave' to exit cheat codes menu." + Style.RESET_ALL)
                print("========================================")
                continue
        continue  # Skip the rest of the game logic after exiting cheat menu

    # Ensure player is capitalized to match choices for game logic
    if player.lower() in [c.lower() for c in choices]:
        for c in choices:
            if player.lower() == c.lower():
                player = c
                break
    else:
        print(Fore.RED + "Command not found!" + Style.RESET_ALL)
        print("========================================")
        continue
    ## Conditions of Rock,Paper,Scissors,Lizard,Spock
    if player == computer:
        print(Fore.YELLOW + "It's a draw!" + Style.RESET_ALL)
        print("========================================")
    elif computer in defeats.get(player, []):
        verb = defeat_verbs.get((player, computer), "beats")
        print(Fore.GREEN + f"You win! {player} {verb} {computer}!" + Style.RESET_ALL)
        player_score += 1
    elif player in defeats.get(computer, []):
        verb = defeat_verbs.get((computer, player), "beats")
        print(Fore.RED + f"You lose! {computer} {verb} {player}!" + Style.RESET_ALL)
        cpu_score += 1
    print(Fore.CYAN + f"Score -> {username}: {player_score} | CPU: {cpu_score}" + Style.RESET_ALL)
    print("========================================")