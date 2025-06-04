import time
import random

cave_score = 0  # Track cave score
village_visits = 0  # Track village visits
game_started = False  # tracks if the game has started or not.
total_score = 0  # Track the times you run from the dragon


def continue_game(has_sword=False, has_pistol=False):
    # Continues the game after running away from the dragon
    global game_started
    game_started = True  # Ensures intro won't show
    print_pause("After running away")
    print_pause("You find yourself back at the starting point.")
    print_pause("What would you like to do?")
    print_pause("1. Go to the village")
    print_pause("2. Go to the cave")
    print_pause("3. Return to the house (dragon's lair)")
    print(f"Your current score is: {total_score}")
    choice = input("> ")
    if choice in ["1", "2", "3"]:
        play_game(has_sword, has_pistol)
    else:
        print_pause("Invalid choice. Please try again.")
        continue_game(has_sword, has_pistol)


def print_pause(message, delay=0.5):  # delays the messages
    print(message)
    time.sleep(delay)


def check_run_count():
    #  checks if you run too away from the dragon alot
    #  and ends the game if you did.
    global total_score
    if total_score >= 3:
        print_pause("You have shown too much cowardice!")
        print_pause("The king flies down from the sky...")
        print_pause("and takes you to the dragon's lair.")
        print_pause("The dragon laughs at you and says:")
        print_pause("You are a coward!")
        print_pause("You have been defeated!")
        print_pause("The king is disappointed in you.")
        print_pause("You have been banished from the kingdom.")
        print_pause("Game Over - Too many retreats!")
        retry_game()


def intro():  # Introduction to the game..duh
    print_pause("The king sent you on a quest to kill the dragon")
    print_pause("that has been terrorizing the village.")
    print_pause("You have to find the dragon's lair")
    print_pause("and defeat it to save the village.")
    print_pause("You have three options to reach the dragon's lair:")
    print_pause("1. The village")
    print_pause("2. The cave")
    print_pause("3. The house that says 'beware of the dragon'")
    print_pause("Choose wisely, for your choice will determine your fate.")
    print(f"Your current score is: {total_score}")


def retry_game():  # retries the game if you want to play again
    global game_started, total_score
    choice = input("Do you want to play again? (yes/no) ").lower()
    if choice == "yes":
        game_started = False  # Resets the game_started flag
        total_score = 0  # Resets run counter
        play_game()
    elif choice == "no":
        print_pause("Thanks for playing! Goodbye, quitting the game now")
        print_pause("QUITTING GAME")
        exit
    else:
        print_pause("Invalid choice. Please type 'yes' or 'no'.")
        retry_game()


def fight_dragon(has_sword=False, has_pistol=False):
    # Handles the turn-based dragon fight
    # With different weapons, cool!
    print_pause("You prepare to fight the dragon!")
    player_health = 100
    dragon_health = 200  # makes the fight unfair if you dont have a sword.

    # Enhanced damage scaling with weapons
    base_damage = 15  # Increased from 5
    if has_sword:
        base_damage += 30  # Increased sword bonus from 10 to 30
        dragon_health -= 30  # Dragon is weaker against sword
        # it's made out of lead.
    if has_pistol:  # It's a pistol, do i need to say more?
        base_damage += 100

    while player_health > 0 and dragon_health > 0:
        # Players turn
        print_pause("\n=== Your Turn ===")
        print_pause(f"Your Health: {player_health}")
        print_pause(f"Dragon's Health: {dragon_health}")
        print_pause("Choose your action:")
        print_pause("1. Attack")
        print_pause("2. Defend")
        action = input("> ")

        if action == "1":
            # Increased damage range
            damage = random.randint(base_damage, base_damage + 15)
            if has_sword and not has_pistol:
                print_pause("You swing your mighty sword and deal")
                print_pause(f"{damage} damage!")
            elif has_pistol:
                print_pause("You pull the trigger and hit the dragon")
                print_pause(f"for {damage} damage!")
            else:  # no weapons
                print_pause(f"You attack the dragon and deal {damage} damage!")
            dragon_health -= damage
        elif action == "2":
            print_pause("You take a defensive stance!")

        if dragon_health <= 0:
            break

        # Dragon's turn
        print_pause("\n=== Dragon's Turn ===")
        dragon_decision = random.choice(["attack", "arrogant"])

        if dragon_decision == "attack":
            # Reduced dragon damage range
            dragon_damage = random.randint(15, 30)  # Reduced from 20-40
            if action == "2":  # Reduce damage if defending
                dragon_damage = int(dragon_damage * 0.5)
            print_pause("The dragon attacks and deals")
            print_pause(f"{dragon_damage} damage!")
            player_health -= dragon_damage
        else:
            print_pause("The dragon scoffs at you and")
            print_pause("chooses not to attack out of arrogance!")

    if player_health <= 0:
        print_pause("The dragon has defeated you. The village is doomed!")
        print_pause("Game Over!")
        retry_game()
    else:
        print_pause("Against all odds")
        print_pause("you have defeated the dragon!")
        print_pause("You have saved the village!")
        print_pause("Congratulations! You are a hero!")
        print_pause("YOU WIN!!")
        retry_game()


def enter_cave():  # Enters the cave and finds items
    global cave_score
    cave_score += 1

    print_pause(f"This is your visit #{cave_score} to the cave.")

    if cave_score == 1:
        print_pause("You find a treasure chest with a magical sword!")
        print_pause("You can take it or leave it.")
        while True:
            choice = input("Take the sword? (yes/no): ").lower()
            if choice in ["yes", "no"]:
                break
            print_pause("Please enter 'yes' or 'no'.")
        return "sword" if choice == "yes" else None
    elif cave_score == 2:
        print_pause("You discover a chest with- HOLY #@@! A PISTOL!")
        print_pause("You take the pistol without hesitation!")
        print_pause("You feel POWERFUL!")
        return "pistol"
    else:
        print_pause("The cave is empty now. Nothing more to find here.")
        print(f"Your current score is: {total_score}")
        return None


def play_game(has_sword=False, has_pistol=False):  # starts the game
    global village_visits, game_started, total_score

    if not game_started:
        intro()
        game_started = True
    choice = input("> ")  # user input for the choice
    if choice == "1":  # Village choice
        village_visits += 1
        if village_visits == 1:
            print_pause("You chose the village.")
            print_pause("You meet a villager who tells you")
            print_pause("about the dragon's weakness.")
            print_pause("The dragon is weak to lead and fire.")
            print_pause("You could also use a sword, which you DON'T HAVE")
            print_pause("The dragon is in that house.")
            print(f"Your current score is: {total_score}")
        else:
            print_pause("The villagers welcome you back with cheers!")
            print_pause("They are grateful for")
            print_pause("your bravery in facing the dragon.")
            print(f"Your current score is: {total_score}")
        print_pause("What would you like to do?")
        print_pause("1. Go to the cave")
        print_pause("2. Go to the dragon's lair")
        print_pause("3. Rest in the village")
        print(f"Your current score is: {total_score}")
        vilchoice = input("> ")  # user input for the choice of action
        if vilchoice == "1":
            print_pause("What would you like to do now?")
            print_pause("1. Return to the village")
            print_pause("2. Face the dragon")
            print(f"Your current score is: {total_score}")
            next_choice = input("> ")
            if next_choice == "1":
                play_game()
            else:
                fight_dragon(has_sword, has_pistol)
                print(f"Your current score is: {total_score}")
        elif vilchoice == "2":
            fight_dragon(has_sword, has_pistol)
            print(f"Your current score is: {total_score}")
        elif vilchoice == "3":
            print_pause("You rest in the village and recover your strength.")
            print_pause("The villagers share stories")
            print_pause("about the dragon's previous attacks.")
            print_pause("You run away quickly.")
            print(f"Your current score is: {total_score}")
            continue_game(has_sword, has_pistol)
        else:  # Invalid choice
            print_pause("Invalid choice. Please try again.")
            continue_game(has_sword, has_pistol)
    elif choice == "2":  # Cave choice
        item = enter_cave()
        if item == "sword":
            has_sword = True
        elif item == "pistol":
            has_pistol = True
        print_pause("You can either go back to the village")
        print_pause("or continue to the house.")
        print_pause("1. Go back to the village")
        print_pause("2. Go to the house")
        print(f"Your current score is: {total_score}")
        cavechoice = input("> ")
        if cavechoice == "1":
            print_pause("You go back to the village.")
            print_pause("You meet a villager who tells you")
            print_pause("about the dragon's weakness.")
            print_pause("The dragon is weak to lead and fire")
            if has_sword:
                print_pause("You could also use a sword, which you DO HAVE")
            else:
                print_pause("You could also use a sword, which you DON'T HAVE")
            print_pause("The dragon is in that house.")
            print_pause("You can either go back to the village")
            print_pause("continue to the dragon's lair.")
            print_pause("1. Go to the cave")
            print_pause("2. Go to the dragon's lair")
            print(f"Your current score is: {total_score}")
            vilchoice = input("> ")
            if vilchoice == "1":
                item = enter_cave()
                if item == "sword":
                    has_sword = True
                elif item == "pistol":
                    has_pistol = True
                housechoice = input("> ")
                if housechoice == "1":
                    fight_dragon(has_sword, has_pistol)
                elif housechoice == "2":
                    total_score += 1
                    print_pause("You run away from the dragon.")
                    print_pause(f"Times fled: {total_score}")
                    check_run_count()
                    print(f"Your current score is: {total_score}")
                    continue_game(has_sword, has_pistol)
                print_pause("What would you like to do now?")
                print_pause("1. Go back")
                print_pause("2. Face the dragon")
                print(f"Your current score is: {total_score}")
                choice = input("> ")
                if choice == "1":
                    play_game(has_sword, has_pistol)
                elif choice == "2":
                    fight_dragon(has_sword, has_pistol)
            elif vilchoice == "2":
                fight_dragon(has_sword, has_pistol)
        elif cavechoice == "2":
            print_pause("You chose the house.")
            print_pause("You- OH NO THE DRAGON!")
            print_pause("Do you wish to fight it? or run away?")
            print_pause("1. Fight")
            print_pause("2. Run away")
            print(f"Your current score is: {total_score}")
            dragon_choice = input("> ")
            if dragon_choice == "1":
                fight_dragon(has_sword, has_pistol)
            elif dragon_choice == "2":
                total_score += 1
                print_pause("You run away from the dragon.")
                print_pause(f"Times fled: {total_score}")
                print(f"Your current score is: {total_score}")
                check_run_count()
                continue_game(has_sword, has_pistol)
    elif choice == "3":  # House choice
        print_pause("You chose the house.")
        print_pause("You- OH NO THE DRAGON!")
        print_pause("Do you wish to fight it? or run away?")
        print_pause("1. Fight")
        print_pause("2. Run away")
        print(f"Your current score is: {total_score}")
        housechoice = input("> ")
        if housechoice == "1":
            fight_dragon(has_sword, has_pistol)
        elif housechoice == "2":
            total_score += 1
            print_pause("You run away from the dragon.")
            print_pause(f"Times fled: {total_score}")
            check_run_count()
            print(f"Your current score is: {total_score}")
            continue_game(has_sword, has_pistol)

    else:  # Invalid choice
        print_pause("Invalid choice. Please try again.")
        print(f"Your current score is: {total_score}")
        play_game()


if __name__ == "__main__":

    play_game()  # Starts the game
