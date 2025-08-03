import os
import time


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_word(target, guessLetters):
    for letter in target:
        if letter in guessLetters:
            print(" ".join(letter), end=" ")
        else:
            print(" ".join("#"), end=" ")


def check_guess(guess, target):

    return guess == target


def check_guess_letter(letterGuess, guessLetters, target):
    if letterGuess in target and letterGuess not in guessLetters:
        guessLetters.append(letterGuess)
        return True
    return False


def check_letters(guessLetters, target):
    count = 0
    for letter in target:
        if letter in guessLetters:
            count += 1
    return count == len(target)


def count_characters(s):
    return len(s)


def hang_man():
    guess = " "
    letterGuess = " "
    target = "crowbar"
    guessLetters = []
    wrong_count = 0

    while True:
        print_word(target, guessLetters)
        print("\n")
        if not check_letters(guessLetters, target):
            guess = input("Enter your guess, you have" + str(5 - wrong_count) +
                          " guesses left")

        if wrong_count == 5:
            break

        lengthGuess = count_characters(guess)
        if lengthGuess == 1:
            letterGuess = guess

        if check_guess(guess, target):
            print("Correct!" + target + "is right.")
            print("\n")
            break
        elif check_letters(guessLetters, target):
            print("Correct!" + target + "is right.")
            print("\n")
            break
        elif check_guess_letter(letterGuess, guessLetters, target):
            clear_console()
            print("Correct!" + letterGuess + "is in the word.")
            print("\n")
        else:
            clear_console()
            wrong_count += 1
            print("Incorrect! Try again." + str(wrong_count))
            print("\n")

        print_word(target, guessLetters)
        print("\n")

    if wrong_count == 5:
        print("You got hung, but then again you wake...")
        time.sleep(3)
        prison_room()
    else:
        print("You got the crowbar and were able to break free from jail")


def prison_room():
    clear_console()
    print(
        "you wake up in a prison. you're condemned to be hung soon. What do you do?"
    )
    print("\n1 = go to the window. 2 = go to the crack in the wall")
    choice = input("Enter your choice: ")
    if choice == "1":
        window_scene()
    elif choice == "2":
        crack_wall()
    else:
        print("Invalid choice.")
        prison_room()  # Stay in the same room if input is bad


def window_scene():
    clear_console()
    print("you see a beautiful sky")
    print("\n 1 = go back to the cell. 2 = go to the crack in the wall")
    choice = input("Enter your choice: ")
    if choice == "1":
        prison_room()
    elif choice == "2":
        crack_wall()
    else:
        print("Invalid choice.")
        window_scene()


def crack_wall():
    clear_console()
    print(
        "you talk to a man who tells you it's obvious how you can get out and he won't tell you unless you guess the word."
    )
    print("\n 1 = play his game. 2 = go back to the cell")
    choice = input("Enter your choice: ")
    if choice == "1":
        hang_man()
    elif choice == "2":
        prison_room()
    else:
        print("Invalid choice.")
        crack_wall()


def main():
    prison_room()


if __name__ == "__main__":
    main()
