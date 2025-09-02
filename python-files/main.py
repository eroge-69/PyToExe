import random
# Global variables
first_player = ""
second_player = ""
third_player = ""
fourth_player = ""
player = ""
first_score = 0
second_score = 0
third_score = 0
fourth_score = 0
round_count = 0
count_players = 0

def Single():
    single = input("Enter your Name: ").capitalize()
    print(f"Welcome {single} to the game!")
    while True:
        if round_count == 0:
            print("Choose Topic from the following: ")
            print(f"\nRound {round_count + 1}/10")
            print("1. Animals")
            print("2. Fruits")
            print("3. Car Brands")
            choice = input("Entar your choice: ")
            if choice == "1":
                global count_players
                count_players = 1
                Animals()
                while True:
                        print(f"\nRound {round_count + 1}/10")
                        Animals()
                        if round_count == 10:
                            end_game()
                            choose = input("1 to play again or 2 to exit: ")
                            if choose == "1":
                                PlayGame()
                            if choose == "2":
                                print("Goodbye!")
                                exit()
            elif choice == "2":
                count_players = 1
                Fruits()
                while True:
                    print(f"\nRound {round_count + 1}/10")
                    Fruits()
                    if round_count == 10:
                        end_game()
                        choose = input("1 to play again or 2 to exit: ")
                        if choose == "1":
                            PlayGame()
                        if choose == "2":
                            print("Goodbye!")
                            exit()
            elif choice == "3":
                count_players = 1
                CarBrands()
                while True:
                    print(f"\nRound {round_count + 1}/10")
                    CarBrands()
                    if round_count == 10:
                        end_game()
                        choose = input("1 to play again or 2 to exit: ")
                        if choose == "1":
                            PlayGame()
                        if choose == "2":
                            print("Goodbye!")
                            exit()
def duo():
    global first_player
    global second_player
    first_player = input("Enter first player's name: ").capitalize()
    second_player = input("Enter second player's name: ").capitalize()
    print(f"Welcome {first_player} and {second_player} to the game!")
    while True:
        if round_count == 0:
            print("Choose Topic from the following: ")
            print(f"\nRound {round_count + 1}/10")
            print("1. Animals")
            print("2. Fruits")
            print("3. Car Brands")
            choice = input("Entar your choice: ")
            if choice == "1":
                global count_players
                count_players = 2
                Animals()
                while True:
                    print(f"\nRound {round_count + 1}/10")
                    Animals()
                    if round_count == 10:
                        end_game()
                        choose = input("1 to play again or 2 to exit: ")
                        if choose == "1":
                            PlayGame()
                        if choose == "2":
                            print("Goodbye!")
                            exit()
            elif choice == "2":
                count_players = 2
                Fruits()
                while True:
                    print(f"\nRound {round_count + 1}/10")
                    Fruits()
                    if round_count == 10:
                        end_game()
                        choose = input("1 to play again or 2 to exit: ")
                        if choose == "1":
                            PlayGame()
                        if choose == "2":
                            print("Goodbye!")
                            exit()
            elif choice == "3":
                count_players = 2
                CarBrands()
                while True:
                    print(f"\nRound {round_count + 1}/10")
                    CarBrands()
                    if round_count == 10:
                        end_game()
                        choose = input("1 to play again or 2 to exit: ")
                        if choose == "1":
                            PlayGame()
                        if choose == "2":
                            print("Goodbye!")
                            exit()
def triple():
    global first_player
    global second_player
    global third_player
    first_player = input("Enter first player's name: ").capitalize()
    second_player = input("Enter second player's name: ").capitalize()
    third_player = input("Enter third player's name: ").capitalize()
    print(f"Welcome {first_player} and {second_player} and {third_player} to the game!")
    while True:
        if round_count == 0:
            print("Choose Topic from the following: ")
            print(f"\nRound {round_count + 1}/10")
            print("1. Animals")
            print("2. Fruits")
            print("3. Car Brands")
            choice = input("Entar your choice: ")
            if choice == "1":
                global count_players
                count_players = 3
                Animals()
                while True:
                    print(f"\nRound {round_count + 1}/10")
                    Animals()
                    if round_count == 10:
                        end_game()
                        choose = input("1 to play again or 2 to exit: ")
                        if choose == "1":
                            PlayGame()
                        if choose == "2":
                            print("Goodbye!")
                            exit()
            elif choice == "2":
                count_players = 3
                Fruits()
                while True:
                    print(f"\nRound {round_count + 1}/10")
                    Fruits()
                    if round_count == 10:
                        end_game()
                        choose = input("1 to play again or 2 to exit: ")
                        if choose == "1":
                            PlayGame()
                        if choose == "2":
                            print("Goodbye!")
                            exit()
            elif choice == "3":
                count_players = 3
                CarBrands()
                while True:
                    print(f"\nRound {round_count + 1}/10")
                    CarBrands()
                    if round_count == 10:
                        end_game()
                        choose = input("1 to play again or 2 to exit: ")
                        if choose == "1":
                            PlayGame()
                        if choose == "2":
                            print("Goodbye!")
                            exit()
def quadruple():
    global first_player
    global second_player
    global third_player
    global fourth_player
    first_player = input("Enter first player's name: ").capitalize()
    second_player = input("Enter second player's name: ").capitalize()
    third_player = input("Enter third player's name: ").capitalize()
    fourth_player = input("Enter fourth player's name: ").capitalize()
    print(f"Welcome {first_player} and {second_player} and {third_player} and {fourth_player} to the game!")
    while True:
        if round_count == 0:
            print("Choose Topic from the following: ")
            print(f"\nRound {round_count + 1}/10")
            print("1. Animals")
            print("2. Fruits")
            print("3. Car Brands")
            choice = input("Entar your choice: ")
            if choice == "1":
                global count_players
                count_players = 4
                Animals()
                while True:
                    print(f"\nRound {round_count + 1}/10")
                    Animals()
                    if round_count == 10:
                        end_game()
                        choose = input("1 to play again or 2 to exit: ")
                        if choose == "1":
                            PlayGame()
                        if choose == "2":
                            print("Goodbye!")
                            exit()
            elif choice == "2":
                count_players = 4
                Fruits()
                while True:
                    print(f"\nRound {round_count + 1}/10")
                    Fruits()
                    if round_count == 10:
                        end_game()
                        choose = input("1 to play again or 2 to exit: ")
                        if choose == "1":
                            PlayGame()
                        if choose == "2":
                            print("Goodbye!")
                            exit()
            elif choice == "3":
                count_players = 4
                CarBrands()
                while True:
                    print(f"\nRound {round_count + 1}/10")
                    CarBrands()
                    if round_count == 10:
                        end_game()
                        choose = input("1 to play again or 2 to exit: ")
                        if choose == "1":
                            PlayGame()
                        if choose == "2":
                            print("Goodbye!")
                            exit()
def Animals():
    global first_player, second_player, third_player, fourth_player, first_score, second_score, third_score, fourth_score, round_count, player
    print("===>(Topic: Animals)<===")
    animals = ["Dog", "Cat", "Elephant", "Lion", "Tiger", "Monkey", "Giraffe", "Zebra", "Kangaroo", "Koala", "Bear", "Rabbit", "Cow", "Pig", "Sheep", "Horse", "Chicken", "Duck", "Goose", "Turkey", "Deer", "Fox", "Wolf", "Mouse", "Rat", "Hamster", "Mole", "Otter", "Seal", "Polar Bear", "Panda", "Gorilla", "Chimpanzee", "Sloth", "Raccoon", "Mink", "Ferret", "Bobcat", "Cougar", "Leopard", "Jaguar", "Cheetah", "Jackal", "Donkey", "Mule", "Llama", "Camel", "Hippopotamus", "Buffalo", "Bison", "Gazelle", "Antelope", "Goat", "Ox", "Yak", "Moose", "Porcupine", "Opossum", "Bat", "Sea Lion", "Dolphin", "Turtle", "Crocodile", "Frog", "Lizard", "Snake", "Eagle", "Hawk", "Falcon", "Owl", "Penguin", "Ostrich", "Emu", "Swan", "Robin", "Orangutan", "Goldfish", "Canary", "Gerbil", "Cobra", "Shark", "Octopus"]

    if not hasattr(Animals, 'already_chosen_animals'):
        Animals.already_chosen_animals = set()
    available_animals = [animal for animal in animals if animal not in Animals.already_chosen_animals]

    if not available_animals:
        print("All animals have already been chosen.")
        return

    animal = random.choice(available_animals)
    animal = animal.capitalize()
    Animals.already_chosen_animals.add(animal)
    word = list(animal)
    random.shuffle(word)
    scrambled_word = ''.join(word)
    print("The scrambled word is: " + scrambled_word)
    if count_players == 1:
        while True:
            v = input("Enter 1 to guess or 2 to give up: ")
            if v == "2":
                print("Your word was: " + animal)
                round_count += 1
                return
            elif v == "1":
                guess = input("Enter your guess: ").capitalize()
                if guess == animal:
                    print("Correct!")
                    first_score += 1
                    print(f"your score: {first_score}")
                    round_count += 1
                    return
                else:
                    print("Incorrect")
                    if first_score > 0:
                        first_score -= 1
                        print(f"your score: {first_score}")
                        while True:
                            break
                    else:
                        print("You have no points to lose")
                        print(f"your score: {first_score}") 
                        while True:
                            break
            else:
                print("Invalid Input,try again")
    elif count_players == 2:
        while True:
            print("Which one will guess?")
            print("Players: " + first_player + " or " + second_player)
            print("Give up: 1")
            print("New Game: 2")
            player_name = input("Enter your choice: ").capitalize()
            #global player
            if player_name == first_player:
                player = first_player
                #break
            elif player_name == second_player:
                player = second_player
                #break
            elif player_name == "1":
                print("Your word was: " + animal)
                round_count += 1
                #if round_count == 10:
                    #end_game()
                return
            elif player_name == "2":
                print("New Game")
                Main()
            else:
                player = None
                print("Invalid Input,try again")
                continue
                #return A3333333333
            while True:
                if player == first_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == animal:
                        print("Correct!")
                        first_score += 1
                        print(f"{first_player} score: {first_score}")
                        print(f"{second_player} score: {second_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if first_score > 0:
                            first_score -= 1
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            while True: 
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    player = second_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + animal)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                    #break
                                else:
                                    print("Invalid Input")
                elif player == second_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == animal:
                        print("Correct!")
                        second_score += 1
                        print(f"{second_player} score: {second_score}")
                        print(f"{first_player} score: {first_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if second_score > 0:
                            second_score -= 1
                            print(f"{second_player} score: {second_score}")
                            print(f"{first_player} score: {first_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{second_player} score: {second_score}")
                            print(f"{first_player} score: {first_score}")
                            while True:
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    player = first_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + animal)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                else:
                                    print("Invalid Input")
    elif count_players == 3:
        while True:
            print("Which one will guess?")
            print("Players: " + first_player + " , " + second_player + " or " + third_player)
            print("Give up: 1")
            print("New Game: 2")
            player_name = input("Enter your choice: ").capitalize()
            if player_name == first_player:
                player = first_player
                #break
            elif player_name == second_player:
                player = second_player
                #break
            elif player_name == third_player:
                player = third_player
            elif player_name == "1":
                print("Your word was: " + animal)
                round_count += 1
                #if round_count == 10:
                    #end_game()
                return
            elif player_name == "2":
                print("New Game")
                Main()
            else:
                player = None
                print("Invalid Input,try again")
                continue
                #return A3333333333
            while True:
                if player == first_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == animal:
                        print("Correct!")
                        first_score += 1
                        print(f"{first_player} score: {first_score}")
                        print(f"{second_player} score: {second_score}")
                        print(f"{third_player} score: {third_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if first_score > 0:
                            first_score -= 1
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            while True: 
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    if player == first_player:
                                        player = second_player
                                    elif player == second_player:
                                        player = third_player
                                    elif player == third_player:
                                        player = first_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + animal)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                    #break
                                else:
                                    print("Invalid Input")
                elif player == second_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == animal:
                        print("Correct!")
                        second_score += 1
                        print(f"{second_player} score: {second_score}")
                        print(f"{first_player} score: {first_score}")
                        print(f"{third_player} score: {third_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if second_score > 0:
                            second_score -= 1
                            print(f"{second_player} score: {second_score}")
                            print(f"{first_player} score: {first_score}")
                            print(f"{third_player} score: {third_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{second_player} score: {second_score}")
                            print(f"{first_player} score: {first_score}")
                            print(f"{third_player} score: {third_score}")
                            while True:
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    if player == first_player:
                                        player = second_player
                                    elif player == second_player:
                                        player = third_player
                                    elif player == third_player:
                                        player = first_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + animal)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                else:
                                    print("Invalid Input")
                elif player == third_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == animal:
                        print("Correct!")
                        third_score += 1
                        print(f"{first_player} score: {first_score}")
                        print(f"{second_player} score: {second_score}")
                        print(f"{third_player} score: {third_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if third_score > 0:
                            third_score -= 1
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            while True: 
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    if player == first_player:
                                        player = second_player
                                    elif player == second_player:
                                        player = third_player
                                    elif player == third_player:
                                        player = first_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + animal)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                    #break
                                else:
                                    print("Invalid Input")
    elif count_players == 4:
        while True:
            print("Which one will guess?")
            print("Players: " + first_player + " , " + second_player + " , " + third_player + " or " + fourth_player)
            print("Give up: 1")
            print("New Game: 2")
            player_name = input("Enter your choice: ").capitalize()
            if player_name == first_player:
                player = first_player
                #break
            elif player_name == second_player:
                player = second_player
                #break
            elif player_name == third_player:
                player = third_player
            elif player_name == fourth_player:
                player = fourth_player
            elif player_name == "1":
                print("Your word was: " + animal)
                round_count += 1
                #if round_count == 10:
                    #end_game()
                return
            elif player_name == "2":
                print("New Game")
                Main()
            else:
                player = None
                print("Invalid Input,try again")
                continue
                #return A3333333333
            while True:
                if player == first_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == animal:
                        print("Correct!")
                        first_score += 1
                        print(f"{first_player} score: {first_score}")
                        print(f"{second_player} score: {second_score}")
                        print(f"{third_player} score: {third_score}")
                        print(f"{fourth_player} score: {fourth_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if first_score > 0:
                            first_score -= 1
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            print(f"{fourth_player} score: {fourth_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            print(f"{fourth_player} score: {fourth_score}")
                            while True: 
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    if player == first_player:
                                        player = second_player
                                    elif player == second_player:
                                        player = third_player
                                    elif player == third_player:
                                        player = fourth_player
                                    elif player == fourth_player:
                                        player = first_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + animal)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                    #break
                                else:
                                    print("Invalid Input")
                elif player == second_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == animal:
                        print("Correct!")
                        second_score += 1
                        print(f"{second_player} score: {second_score}")
                        print(f"{first_player} score: {first_score}")
                        print(f"{third_player} score: {third_score}")
                        print(f"{fourth_player} score: {fourth_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if second_score > 0:
                            second_score -= 1
                            print(f"{second_player} score: {second_score}")
                            print(f"{first_player} score: {first_score}")
                            print(f"{third_player} score: {third_score}")
                            print(f"{fourth_player} score: {fourth_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{second_player} score: {second_score}")
                            print(f"{first_player} score: {first_score}")
                            print(f"{third_player} score: {third_score}")
                            print(f"{fourth_player} score: {fourth_score}")
                            while True:
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    if player == first_player:
                                        player = second_player
                                    elif player == second_player:
                                        player = third_player
                                    elif player == third_player:
                                        player = fourth_player
                                    elif player == fourth_player:
                                        player = first_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + animal)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                else:
                                    print("Invalid Input")
                elif player == third_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == animal:
                        print("Correct!")
                        third_score += 1
                        print(f"{first_player} score: {first_score}")
                        print(f"{second_player} score: {second_score}")
                        print(f"{third_player} score: {third_score}")
                        print(f"{fourth_player} score: {fourth_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if third_score > 0:
                            third_score -= 1
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            print(f"{fourth_player} score: {fourth_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            print(f"{fourth_player} score: {fourth_score}")
                            while True: 
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    if player == first_player:
                                        player = second_player
                                    elif player == second_player:
                                        player = third_player
                                    elif player == third_player:
                                        player = fourth_player
                                    elif player == fourth_player:
                                        player = first_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + animal)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                    #break
                                else:
                                    print("Invalid Input")
                elif player == fourth_player:
                        guess = input("Enter your guess: ").capitalize()
                        if guess == animal:
                            print("Correct!")
                            fourth_score += 1
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            print(f"{fourth_player} score: {fourth_score}")
                            round_count += 1
                            #if round_count == 10:
                                #end_game()
                            return
                        else:
                            print("Incorrect")
                            if fourth_score > 0:
                                fourth_score -= 1
                                print(f"{first_player} score: {first_score}")
                                print(f"{second_player} score: {second_score}")
                                print(f"{third_player} score: {third_score}")
                                print(f"{fourth_player} score: {fourth_score}")
                                round_count += 1
                                return
                            else:
                                print("You have no points to lose")
                                print(f"{first_player} score: {first_score}")
                                print(f"{second_player} score: {second_score}")
                                print(f"{third_player} score: {third_score}")
                                print(f"{fourth_player} score: {fourth_score}")
                                while True: 
                                    choice = input("Choose 1 to switch player or 2 to give up: ")
                                    if choice == "1":
                                        if player == first_player:
                                            player = second_player
                                        elif player == second_player:
                                            player = third_player
                                        elif player == third_player:
                                            player = fourth_player
                                        elif player == fourth_player:
                                            player = first_player
                                        break
                                    elif choice == "2":
                                        print("Your word was: " + animal)
                                        round_count += 1
                                        #if round_count == 10:
                                            #end_game()
                                        return
                                        #break
                                    else:
                                        print("Invalid Input")
def Fruits():
    global first_player, second_player, third_player, fourth_player, first_score, second_score, third_score, fourth_score, round_count, player
    print("===>(Topic: Fruits)<===")
    fruits = ["Apple", "Banana", "Orange", "Grapes", "Strawberry", "Watermelon", "Pineapple", "Mango", "Kiwi", "Blueberry", "Raspberry", "Peach", "Pear", "Plum", "Cherry", "Lemon", "Lime", "Coconut", "Avocado", "Pomegranate"]

    if not hasattr(Fruits, 'already_chosen_fruits'):
        Fruits.already_chosen_fruits = set()
    available_fruits = [fruit for fruit in fruits if fruit not in Fruits.already_chosen_fruits]

    if not available_fruits:
        print("All fruits have already been chosen.")
        return

    fruit = random.choice(available_fruits)
    fruit = fruit.capitalize()
    Fruits.already_chosen_fruits.add(fruit)
    word = list(fruit)
    random.shuffle(word)
    scrambled_word = ''.join(word)
    print("The scrambled word is: " + scrambled_word)
    if count_players == 1:
        while True:
            v = input("Enter 1 to guess or 2 to give up: ")
            if v == "2":
                print("Your word was: " + fruit)
                round_count += 1
                return
            elif v == "1":
                guess = input("Enter your guess: ").capitalize()
                if guess == fruit:
                    print("Correct!")
                    first_score += 1
                    print(f"your score: {first_score}")
                    round_count += 1
                    return
                else:
                    print("Incorrect")
                    if first_score > 0:
                        first_score -= 1
                        print(f"your score: {first_score}")
                        while True:
                            break
                    else:
                        print("You have no points to lose")
                        print(f"your score: {first_score}") 
                        while True:
                            break
            else:
                print("Invalid Input,try again")
    elif count_players == 2:
        while True:
            print("Which one will guess?")
            print("Players: " + first_player + " or " + second_player)
            print("Give up: 1")
            print("New Game: 2")
            player_name = input("Enter your choice: ").capitalize()
            #global player
            if player_name == first_player:
                player = first_player
                #break
            elif player_name == second_player:
                player = second_player
                #break
            elif player_name == "1":
                print("Your word was: " + fruit)
                round_count += 1
                #if round_count == 10:
                    #end_game()
                return
            elif player_name == "2":
                print("New Game")
                Main()
            else:
                player = None
                print("Invalid Input,try again")
                continue
                #return A3333333333
            while True:
                if player == first_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == fruit:
                        print("Correct!")
                        first_score += 1
                        print(f"{first_player} score: {first_score}")
                        print(f"{second_player} score: {second_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if first_score > 0:
                            first_score -= 1
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            while True: 
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    player = second_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + fruit)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                    #break
                                else:
                                    print("Invalid Input")
                elif player == second_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == fruit:
                        print("Correct!")
                        second_score += 1
                        print(f"{second_player} score: {second_score}")
                        print(f"{first_player} score: {first_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if second_score > 0:
                            second_score -= 1
                            print(f"{second_player} score: {second_score}")
                            print(f"{first_player} score: {first_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{second_player} score: {second_score}")
                            print(f"{first_player} score: {first_score}")
                            while True:
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    player = first_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + fruit)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                else:
                                    print("Invalid Input")
    elif count_players == 3:
        while True:
            print("Which one will guess?")
            print("Players: " + first_player + " , " + second_player + " or " + third_player)
            print("Give up: 1")
            print("New Game: 2")
            player_name = input("Enter your choice: ").capitalize()
            if player_name == first_player:
                player = first_player
                #break
            elif player_name == second_player:
                player = second_player
                #break
            elif player_name == third_player:
                player = third_player
            elif player_name == "1":
                print("Your word was: " + fruit)
                round_count += 1
                #if round_count == 10:
                    #end_game()
                return
            elif player_name == "2":
                print("New Game")
                Main()
            else:
                player = None
                print("Invalid Input,try again")
                continue
                #return A3333333333
            while True:
                if player == first_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == fruit:
                        print("Correct!")
                        first_score += 1
                        print(f"{first_player} score: {first_score}")
                        print(f"{second_player} score: {second_score}")
                        print(f"{third_player} score: {third_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if first_score > 0:
                            first_score -= 1
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            while True: 
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    if player == first_player:
                                        player = second_player
                                    elif player == second_player:
                                        player = third_player
                                    elif player == third_player:
                                        player = first_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + fruit)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                    #break
                                else:
                                    print("Invalid Input")
                elif player == second_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == fruit:
                        print("Correct!")
                        second_score += 1
                        print(f"{second_player} score: {second_score}")
                        print(f"{first_player} score: {first_score}")
                        print(f"{third_player} score: {third_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if second_score > 0:
                            second_score -= 1
                            print(f"{second_player} score: {second_score}")
                            print(f"{first_player} score: {first_score}")
                            print(f"{third_player} score: {third_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{second_player} score: {second_score}")
                            print(f"{first_player} score: {first_score}")
                            print(f"{third_player} score: {third_score}")
                            while True:
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    if player == first_player:
                                        player = second_player
                                    elif player == second_player:
                                        player = third_player
                                    elif player == third_player:
                                        player = first_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + fruit)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                else:
                                    print("Invalid Input")
                elif player == third_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == fruit:
                        print("Correct!")
                        third_score += 1
                        print(f"{first_player} score: {first_score}")
                        print(f"{second_player} score: {second_score}")
                        print(f"{third_player} score: {third_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if third_score > 0:
                            third_score -= 1
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            while True: 
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    if player == first_player:
                                        player = second_player
                                    elif player == second_player:
                                        player = third_player
                                    elif player == third_player:
                                        player = first_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + fruit)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                    #break
                                else:
                                    print("Invalid Input")
    elif count_players == 4:
        while True:
            print("Which one will guess?")
            print("Players: " + first_player + " , " + second_player + " , " + third_player + " or " + fourth_player)
            print("Give up: 1")
            print("New Game: 2")
            player_name = input("Enter your choice: ").capitalize()
            if player_name == first_player:
                player = first_player
                #break
            elif player_name == second_player:
                player = second_player
                #break
            elif player_name == third_player:
                player = third_player
            elif player_name == fourth_player:
                player = fourth_player
            elif player_name == "1":
                print("Your word was: " + fruit)
                round_count += 1
                #if round_count == 10:
                    #end_game()
                return
            elif player_name == "2":
                print("New Game")
                Main()
            else:
                player = None
                print("Invalid Input,try again")
                continue
                #return A3333333333
            while True:
                if player == first_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == fruit:
                        print("Correct!")
                        first_score += 1
                        print(f"{first_player} score: {first_score}")
                        print(f"{second_player} score: {second_score}")
                        print(f"{third_player} score: {third_score}")
                        print(f"{fourth_player} score: {fourth_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if first_score > 0:
                            first_score -= 1
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            print(f"{fourth_player} score: {fourth_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            print(f"{fourth_player} score: {fourth_score}")
                            while True: 
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    if player == first_player:
                                        player = second_player
                                    elif player == second_player:
                                        player = third_player
                                    elif player == third_player:
                                        player = fourth_player
                                    elif player == fourth_player:
                                        player = first_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + fruit)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                    #break
                                else:
                                    print("Invalid Input")
                elif player == second_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == fruit:
                        print("Correct!")
                        second_score += 1
                        print(f"{second_player} score: {second_score}")
                        print(f"{first_player} score: {first_score}")
                        print(f"{third_player} score: {third_score}")
                        print(f"{fourth_player} score: {fourth_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if second_score > 0:
                            second_score -= 1
                            print(f"{second_player} score: {second_score}")
                            print(f"{first_player} score: {first_score}")
                            print(f"{third_player} score: {third_score}")
                            print(f"{fourth_player} score: {fourth_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{second_player} score: {second_score}")
                            print(f"{first_player} score: {first_score}")
                            print(f"{third_player} score: {third_score}")
                            print(f"{fourth_player} score: {fourth_score}")
                            while True:
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    if player == first_player:
                                        player = second_player
                                    elif player == second_player:
                                        player = third_player
                                    elif player == third_player:
                                        player = fourth_player
                                    elif player == fourth_player:
                                        player = first_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + fruit)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                else:
                                    print("Invalid Input")
                elif player == third_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == fruit:
                        print("Correct!")
                        third_score += 1
                        print(f"{first_player} score: {first_score}")
                        print(f"{second_player} score: {second_score}")
                        print(f"{third_player} score: {third_score}")
                        print(f"{fourth_player} score: {fourth_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if third_score > 0:
                            third_score -= 1
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            print(f"{fourth_player} score: {fourth_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            print(f"{fourth_player} score: {fourth_score}")
                            while True: 
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    if player == first_player:
                                        player = second_player
                                    elif player == second_player:
                                        player = third_player
                                    elif player == third_player:
                                        player = fourth_player
                                    elif player == fourth_player:
                                        player = first_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + fruit)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                    #break
                                else:
                                    print("Invalid Input")
                elif player == fourth_player:
                        guess = input("Enter your guess: ").capitalize()
                        if guess == fruit:
                            print("Correct!")
                            fourth_score += 1
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            print(f"{fourth_player} score: {fourth_score}")
                            round_count += 1
                            #if round_count == 10:
                                #end_game()
                            return
                        else:
                            print("Incorrect")
                            if fourth_score > 0:
                                fourth_score -= 1
                                print(f"{first_player} score: {first_score}")
                                print(f"{second_player} score: {second_score}")
                                print(f"{third_player} score: {third_score}")
                                print(f"{fourth_player} score: {fourth_score}")
                                round_count += 1
                                return
                            else:
                                print("You have no points to lose")
                                print(f"{first_player} score: {first_score}")
                                print(f"{second_player} score: {second_score}")
                                print(f"{third_player} score: {third_score}")
                                print(f"{fourth_player} score: {fourth_score}")
                                while True: 
                                    choice = input("Choose 1 to switch player or 2 to give up: ")
                                    if choice == "1":
                                        if player == first_player:
                                            player = second_player
                                        elif player == second_player:
                                            player = third_player
                                        elif player == third_player:
                                            player = fourth_player
                                        elif player == fourth_player:
                                            player = first_player
                                        break
                                    elif choice == "2":
                                        print("Your word was: " + fruit)
                                        round_count += 1
                                        #if round_count == 10:
                                            #end_game()
                                        return
                                        #break
                                    else:
                                        print("Invalid Input")
def CarBrands():
    global first_player, second_player, third_player, fourth_player, first_score, second_score, third_score, fourth_score, round_count, player
    print("===>(Topic: Car Brands)<===")
    car_brands = ["Toyota", "Honda", "Ford", "Chevrolet", "BMW", "Mercedes", "Audi", "Nissan", "Hyundai", "Kia", "Volkswagen", "Renault", "Peugeot", "Fiat", "Volvo", "Tesla", "Mazda", "Subaru", "Suzuki", "Mitsubishi"]

    if not hasattr(CarBrands, 'already_chosen_car_brands'):
        CarBrands.already_chosen_car_brands = set()
    available_car_brands = [car_brand for car_brand in car_brands if car_brand not in CarBrands.already_chosen_car_brands]

    if not available_car_brands:
        print("All car brands have already been chosen.")
        return

    car_brand = random.choice(available_car_brands)
    car_brand = car_brand.capitalize()
    CarBrands.already_chosen_car_brands.add(car_brand)
    word = list(car_brand)
    random.shuffle(word)
    scrambled_word = ''.join(word)
    print("The scrambled word is: " + scrambled_word)
    if count_players == 1:
        while True:
            v = input("Enter 1 to guess or 2 to give up: ")
            if v == "2":
                print("Your word was: " + car_brand)
                round_count += 1
                return
            elif v == "1":
                guess = input("Enter your guess: ").capitalize()
                if guess == car_brand:
                    print("Correct!")
                    first_score += 1
                    print(f"your score: {first_score}")
                    round_count += 1
                    return
                else:
                    print("Incorrect")
                    if first_score > 0:
                        first_score -= 1
                        print(f"your score: {first_score}")
                        while True:
                            break
                    else:
                        print("You have no points to lose")
                        print(f"your score: {first_score}") 
                        while True:
                            break
            else:
                print("Invalid Input,try again")
    elif count_players == 2:
        while True:
            print("Which one will guess?")
            print("Players: " + first_player + " or " + second_player)
            print("Give up: 1")
            print("New Game: 2")
            player_name = input("Enter your choice: ").capitalize()
            #global player
            if player_name == first_player:
                player = first_player
                #break
            elif player_name == second_player:
                player = second_player
                #break
            elif player_name == "1":
                print("Your word was: " + car_brand)
                round_count += 1
                #if round_count == 10:
                    #end_game()
                return
            elif player_name == "2":
                print("New Game")
                Main()
            else:
                player = None
                print("Invalid Input,try again")
                continue
                #return A3333333333
            while True:
                if player == first_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == car_brand:
                        print("Correct!")
                        first_score += 1
                        print(f"{first_player} score: {first_score}")
                        print(f"{second_player} score: {second_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if first_score > 0:
                            first_score -= 1
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            while True: 
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    player = second_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + car_brand)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                    #break
                                else:
                                    print("Invalid Input")
                elif player == second_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == car_brand:
                        print("Correct!")
                        second_score += 1
                        print(f"{second_player} score: {second_score}")
                        print(f"{first_player} score: {first_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if second_score > 0:
                            second_score -= 1
                            print(f"{second_player} score: {second_score}")
                            print(f"{first_player} score: {first_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{second_player} score: {second_score}")
                            print(f"{first_player} score: {first_score}")
                            while True:
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    player = first_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + car_brand)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                else:
                                    print("Invalid Input")
    elif count_players == 3:
        while True:
            print("Which one will guess?")
            print("Players: " + first_player + " , " + second_player + " or " + third_player)
            print("Give up: 1")
            print("New Game: 2")
            player_name = input("Enter your choice: ").capitalize()
            if player_name == first_player:
                player = first_player
                #break
            elif player_name == second_player:
                player = second_player
                #break
            elif player_name == third_player:
                player = third_player
            elif player_name == "1":
                print("Your word was: " + car_brand)
                round_count += 1
                #if round_count == 10:
                    #end_game()
                return
            elif player_name == "2":
                print("New Game")
                Main()
            else:
                player = None
                print("Invalid Input,try again")
                continue
                #return A3333333333
            while True:
                if player == first_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == car_brand:
                        print("Correct!")
                        first_score += 1
                        print(f"{first_player} score: {first_score}")
                        print(f"{second_player} score: {second_score}")
                        print(f"{third_player} score: {third_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if first_score > 0:
                            first_score -= 1
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            while True: 
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    if player == first_player:
                                        player = second_player
                                    elif player == second_player:
                                        player = third_player
                                    elif player == third_player:
                                        player = first_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + car_brand)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                    #break
                                else:
                                    print("Invalid Input")
                elif player == second_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == car_brand:
                        print("Correct!")
                        second_score += 1
                        print(f"{second_player} score: {second_score}")
                        print(f"{first_player} score: {first_score}")
                        print(f"{third_player} score: {third_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if second_score > 0:
                            second_score -= 1
                            print(f"{second_player} score: {second_score}")
                            print(f"{first_player} score: {first_score}")
                            print(f"{third_player} score: {third_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{second_player} score: {second_score}")
                            print(f"{first_player} score: {first_score}")
                            print(f"{third_player} score: {third_score}")
                            while True:
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    if player == first_player:
                                        player = second_player
                                    elif player == second_player:
                                        player = third_player
                                    elif player == third_player:
                                        player = first_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + car_brand)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                else:
                                    print("Invalid Input")
                elif player == third_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == car_brand:
                        print("Correct!")
                        third_score += 1
                        print(f"{first_player} score: {first_score}")
                        print(f"{second_player} score: {second_score}")
                        print(f"{third_player} score: {third_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if third_score > 0:
                            third_score -= 1
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            while True: 
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    if player == first_player:
                                        player = second_player
                                    elif player == second_player:
                                        player = third_player
                                    elif player == third_player:
                                        player = first_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + car_brand)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                    #break
                                else:
                                    print("Invalid Input")
    elif count_players == 4:
        while True:
            print("Which one will guess?")
            print("Players: " + first_player + " , " + second_player + " , " + third_player + " or " + fourth_player)
            print("Give up: 1")
            print("New Game: 2")
            player_name = input("Enter your choice: ").capitalize()
            if player_name == first_player:
                player = first_player
                #break
            elif player_name == second_player:
                player = second_player
                #break
            elif player_name == third_player:
                player = third_player
            elif player_name == fourth_player:
                player = fourth_player
            elif player_name == "1":
                print("Your word was: " + car_brand)
                round_count += 1
                #if round_count == 10:
                    #end_game()
                return
            elif player_name == "2":
                print("New Game")
                Main()
            else:
                player = None
                print("Invalid Input,try again")
                continue
                #return A3333333333
            while True:
                if player == first_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == car_brand:
                        print("Correct!")
                        first_score += 1
                        print(f"{first_player} score: {first_score}")
                        print(f"{second_player} score: {second_score}")
                        print(f"{third_player} score: {third_score}")
                        print(f"{fourth_player} score: {fourth_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if first_score > 0:
                            first_score -= 1
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            print(f"{fourth_player} score: {fourth_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            print(f"{fourth_player} score: {fourth_score}")
                            while True: 
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    if player == first_player:
                                        player = second_player
                                    elif player == second_player:
                                        player = third_player
                                    elif player == third_player:
                                        player = fourth_player
                                    elif player == fourth_player:
                                        player = first_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + car_brand)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                    #break
                                else:
                                    print("Invalid Input")
                elif player == second_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == car_brand:
                        print("Correct!")
                        second_score += 1
                        print(f"{second_player} score: {second_score}")
                        print(f"{first_player} score: {first_score}")
                        print(f"{third_player} score: {third_score}")
                        print(f"{fourth_player} score: {fourth_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if second_score > 0:
                            second_score -= 1
                            print(f"{second_player} score: {second_score}")
                            print(f"{first_player} score: {first_score}")
                            print(f"{third_player} score: {third_score}")
                            print(f"{fourth_player} score: {fourth_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{second_player} score: {second_score}")
                            print(f"{first_player} score: {first_score}")
                            print(f"{third_player} score: {third_score}")
                            print(f"{fourth_player} score: {fourth_score}")
                            while True:
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    if player == first_player:
                                        player = second_player
                                    elif player == second_player:
                                        player = third_player
                                    elif player == third_player:
                                        player = fourth_player
                                    elif player == fourth_player:
                                        player = first_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + car_brand)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                else:
                                    print("Invalid Input")
                elif player == third_player:
                    guess = input("Enter your guess: ").capitalize()
                    if guess == car_brand:
                        print("Correct!")
                        third_score += 1
                        print(f"{first_player} score: {first_score}")
                        print(f"{second_player} score: {second_score}")
                        print(f"{third_player} score: {third_score}")
                        print(f"{fourth_player} score: {fourth_score}")
                        round_count += 1
                        #if round_count == 10:
                            #end_game()
                        return
                    else:
                        print("Incorrect")
                        if third_score > 0:
                            third_score -= 1
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            print(f"{fourth_player} score: {fourth_score}")
                            round_count += 1
                            return
                        else:
                            print("You have no points to lose")
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            print(f"{fourth_player} score: {fourth_score}")
                            while True: 
                                choice = input("Choose 1 to switch player or 2 to give up: ")
                                if choice == "1":
                                    if player == first_player:
                                        player = second_player
                                    elif player == second_player:
                                        player = third_player
                                    elif player == third_player:
                                        player = fourth_player
                                    elif player == fourth_player:
                                        player = first_player
                                    break
                                elif choice == "2":
                                    print("Your word was: " + car_brand)
                                    round_count += 1
                                    #if round_count == 10:
                                        #end_game()
                                    return
                                    #break
                                else:
                                    print("Invalid Input")
                elif player == fourth_player:
                        guess = input("Enter your guess: ").capitalize()
                        if guess == car_brand:
                            print("Correct!")
                            fourth_score += 1
                            print(f"{first_player} score: {first_score}")
                            print(f"{second_player} score: {second_score}")
                            print(f"{third_player} score: {third_score}")
                            print(f"{fourth_player} score: {fourth_score}")
                            round_count += 1
                            #if round_count == 10:
                                #end_game()
                            return
                        else:
                            print("Incorrect")
                            if fourth_score > 0:
                                fourth_score -= 1
                                print(f"{first_player} score: {first_score}")
                                print(f"{second_player} score: {second_score}")
                                print(f"{third_player} score: {third_score}")
                                print(f"{fourth_player} score: {fourth_score}")
                                round_count += 1
                                return
                            else:
                                print("You have no points to lose")
                                print(f"{first_player} score: {first_score}")
                                print(f"{second_player} score: {second_score}")
                                print(f"{third_player} score: {third_score}")
                                print(f"{fourth_player} score: {fourth_score}")
                                while True: 
                                    choice = input("Choose 1 to switch player or 2 to give up: ")
                                    if choice == "1":
                                        if player == first_player:
                                            player = second_player
                                        elif player == second_player:
                                            player = third_player
                                        elif player == third_player:
                                            player = fourth_player
                                        elif player == fourth_player:
                                            player = first_player
                                        break
                                    elif choice == "2":
                                        print("Your word was: " + car_brand)
                                        round_count += 1
                                        #if round_count == 10:
                                            #end_game()
                                        return
                                        #break
                                    else:
                                        print("Invalid Input")    
def end_game():
    if count_players == 1:
        print("===>(Game Over!)<===")
        print(f"Your final score is: {first_score}/10")
        if first_score >= 5:
            print("You win!")
        else:
            print("You lose!")
    elif count_players == 2:
        print("===>(Game Over!)<===")
        print("The final scores are: ")
        print(f"{first_player}: {first_score}/10")
        print(f"{second_player}: {second_score}/10")
        if first_score > second_score:
            print(f"{first_player} wins!")
        elif second_score > first_score:
            print(f"{second_player} wins!")
        else:
            print("It's a tie!")
    elif count_players == 3:
        print("===>(Game Over!)<===")
        print("The final scores are: ")
        print(f"{first_player}: {first_score}/10")
        print(f"{second_player}: {second_score}/10")
        print(f"{third_player}: {third_score}/10")
        if first_score > second_score and first_score > third_score:
            print(f"{first_player} wins!")
        elif second_score > first_score and second_score > third_score:
            print(f"{second_player} wins!")
        elif third_score > first_score and third_score > second_score:
            print(f"{third_player} wins!")
        elif first_score == second_score:
            print(f"{first_player} and {second_player} win!")
        elif second_score == third_score:
            print(f"{second_player} and {third_player} win!")
        elif first_score == third_score:
            print(f"{first_player} and {third_player} win!")
        else:
            print("It's a tie!")
    elif count_players == 4:
        print("===>(Game Over!)<===")
        print("The final scores are: ")
        print(f"{first_player}: {first_score}/10")
        print(f"{second_player}: {second_score}/10")
        print(f"{third_player}: {third_score}/10")
        print(f"{fourth_player}: {fourth_score}/10")
        if first_score > second_score and first_score > third_score and first_score > fourth_score:
            print(f"{first_player} wins!")
        elif second_score > first_score and second_score > third_score and second_score > fourth_score:
            print(f"{second_player} wins!")
        elif third_score > first_score and third_score > second_score and third_score > fourth_score:
            print(f"{third_player} wins!")
        elif fourth_score > first_score and fourth_score > second_score and fourth_score > third_score:
            print(f"{fourth_player} wins!")
        elif first_score == second_score:
            print(f"{first_player} and {second_player} win!")
        elif second_score == third_score:
            print(f"{second_player} and {third_player} win!")
        elif third_score == fourth_score:
            print(f"{third_player} and {fourth_player} win!")
        elif first_score == fourth_score:
            print(f"{first_player} and {fourth_player} win!")
        elif first_score == third_score:
            print(f"{first_player} and {third_player} win!")
        elif second_score == fourth_score:
            print(f"{second_player} and {fourth_player} win!")
        elif first_score == second_score == third_score:
            print(f"{first_player}, {second_player} and {third_player} win!")
        elif second_score == third_score == fourth_score:
            print(f"{second_player}, {third_player} and {fourth_player} win!")
        elif first_score == third_score == fourth_score:
            print(f"{first_player}, {third_player} and {fourth_player} win!")
        elif first_score == second_score == fourth_score:
            print(f"{first_player}, {second_player} and {fourth_player} win!")
        else:
            print("It's a tie!")
def PlayGame():
    global single 
    #global first_player
    #global second_player
    global first_score
    global second_score
    global round_count
    global third_player
    global fourth_player
    global count_players
    count_players = 0
    round_count = 0
    first_score = 0
    second_score = 0
    while True:
        count_players = input("Enter number of players(1-4): ")
        if count_players == "1":
            Single()
        elif count_players == "2":
            duo()
        elif count_players == "3":
            triple()
        elif count_players == "4":
            quadruple()
        else:
            print("Invalid Input,try again")
            continue
def Main():
    print("===>(Welcome to Scrambling Game!)<===")
    while True:
        print("\n1. Play Game")
        print("2. Quit")
        choice = input("Enter your choice: ")
        if choice == "1":
            PlayGame()
        elif choice == "2":
            print("Goodbye!")
            exit()
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    Main()