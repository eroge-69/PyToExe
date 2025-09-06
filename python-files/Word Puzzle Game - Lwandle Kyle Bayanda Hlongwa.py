secret_word = "immortal"
guess_count = 0

print("Welcome to the word guessing game!")

while True:
    guess = input("Guess the word. ")
    guess_count += 1
    
    if len(guess) != len(secret_word):
        print(f"Your guess must be {len(secret_word)} letters.")
        continue

    if guess.lower() == secret_word:
        print(secret_word.upper())
        print("Congratulations! You guessed the word!")
        print(f"It took you {guess_count} guesses.")
        break

    hint = ""
    for i in range(len(secret_word)):
        if guess[i].lower() == secret_word[i]:
            hint += guess[i].upper() + " "
        elif guess[i].lower() in secret_word:
            hint += guess[i].lower() + " " 
        else:
            hint += "_"
    print("Your hint is:", hint.strip())