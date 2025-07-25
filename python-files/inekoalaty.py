import math

def play_inekoalaty_game():
    print("Welcome to the Inekoalaty Game!")
    print("Based on IMO 2025 Problem 5.")
    print("Alice and Bazza are trying to outmaneuver each other with numbers.")
    print("-" * 40)

    # Get lambda from the user
    while True:
        try:
            lambda_val_str = input("Enter the value for lambda (a positive real number): ")
            lambda_val = float(lambda_val_str)
            if lambda_val <= 0:
                print("Lambda must be a positive real number. Please try again.")
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a valid number for lambda.")

    print(f"\nLambda is set to: {lambda_val:.4f}")
    print("Game Start!")
    print("-" * 40)

    # Game state variables
    x_values = []
    current_sum_x = 0.0
    current_sum_x_squared = 0.0
    max_turns = 100  # Set a practical maximum number of turns for the game

    for n in range(1, max_turns + 1):
        if n % 2 != 0:  # Odd turn: Alice's turn
            player_name = "Alice"
            target_sum_x = lambda_val * n
            print(f"\n--- Turn {n}: Alice's Turn ---")
            print(f"Current sum of x values: {current_sum_x:.4f}")
            print(f"Alice must choose x_{n} such that x_1 + ... + x_{n} <= {target_sum_x:.4f}")

            while True:
                try:
                    x_n_str = input(f"Alice, enter your non-negative x_{n}: ")
                    x_n = float(x_n_str)
                    if x_n < 0:
                        print("x_n must be a non-negative number. Please try again.")
                    elif current_sum_x + x_n > target_sum_x:
                        print(f"Adding {x_n:.4f} would exceed the limit ({current_sum_x + x_n:.4f} > {target_sum_x:.4f}).")
                        print("Please choose a smaller x_n.")
                    else:
                        break
                except ValueError:
                    print("Invalid input. Please enter a valid non-negative number.")

            x_values.append(x_n)
            current_sum_x += x_n
            current_sum_x_squared += x_n**2
            print(f"Alice chose x_{n} = {x_n:.4f}. New sum of x: {current_sum_x:.4f}")
            print(f"Current sum of x squared: {current_sum_x_squared:.4f}")

        else:  # Even turn: Bazza's turn
            player_name = "Bazza"
            target_sum_x_squared = float(n) # The problem states 'n'
            print(f"\n--- Turn {n}: Bazza's Turn ---")
            print(f"Current sum of x squared values: {current_sum_x_squared:.4f}")
            print(f"Bazza must choose x_{n} such that x_1^2 + ... + x_{n}^2 <= {target_sum_x_squared:.4f}")

            while True:
                try:
                    x_n_str = input(f"Bazza, enter your non-negative x_{n}: ")
                    x_n = float(x_n_str)
                    if x_n < 0:
                        print("x_n must be a non-negative number. Please try again.")
                    elif current_sum_x_squared + x_n**2 > target_sum_x_squared:
                        print(f"Adding x_{n}^2 ({x_n**2:.4f}) would exceed the limit ({current_sum_x_squared + x_n**2:.4f} > {target_sum_x_squared:.4f}).")
                        print("Please choose a smaller x_n.")
                    else:
                        break
                except ValueError:
                    print("Invalid input. Please enter a valid non-negative number.")

            x_values.append(x_n)
            current_sum_x += x_n
            current_sum_x_squared += x_n**2
            print(f"Bazza chose x_{n} = {x_n:.4f}. New sum of x: {current_sum_x:.4f}")
            print(f"New sum of x squared: {current_sum_x_squared:.4f}")

        # Check for immediate loss condition for the *next* player
        # If the current player has no valid move for their current turn, the *other* player wins
        # This check is implicitly handled by the input loop - if they can't make a valid move, they're stuck.
        # We need to think about future moves. If the allowed range for x_n is negative, then it's impossible.
        # For Alice (odd turn n+1): Check if lambda_val * (n+1) - current_sum_x is negative.
        # For Bazza (even turn n+1): Check if (n+1) - current_sum_x_squared is negative.

        # Let's add an explicit check to see if the next player is *forced* to lose
        # This is more complex as it depends on whether *any* valid non-negative x_n exists.
        # A player cannot choose x_n if the remaining allowed value is less than 0.
        # For Alice's turn (n+1, odd): If current_sum_x > lambda_val * (n+1), Alice cannot choose x_{n+1} >= 0.
        # For Bazza's turn (n+1, even): If current_sum_x_squared > (n+1), Bazza cannot choose x_{n+1} >= 0.

        # Check if the *next* player is immediately stuck (cannot choose any non-negative x_n)
        if n % 2 != 0: # Alice just played, it's Bazza's turn (n+1, even) next
            next_n = n + 1
            if current_sum_x_squared > next_n:
                print(f"\n--- Game Over ---")
                print(f"Bazza cannot make a valid move on turn {next_n} (required sum of squares {current_sum_x_squared:.4f} would exceed {next_n}).")
                print("Alice wins!")
                break
        else: # Bazza just played, it's Alice's turn (n+1, odd) next
            next_n = n + 1
            if current_sum_x > lambda_val * next_n:
                print(f"\n--- Game Over ---")
                print(f"Alice cannot make a valid move on turn {next_n} (required sum of x {current_sum_x:.4f} would exceed {lambda_val * next_n:.4f}).")
                print("Bazza wins!")
                break

        if n == max_turns:
            print(f"\n--- Game Over ---")
            print(f"Maximum turns ({max_turns}) reached. Neither player wins (draw).")

    print("\n--- Game Summary ---")
    print(f"Final x_values: {x_values}")
    print(f"Final sum of x: {current_sum_x:.4f}")
    print(f"Final sum of x squared: {current_sum_x_squared:.4f}")
    print("-" * 40)
    print("Thanks for playing!")

if __name__ == "__main__":
    play_inekoalaty_game()