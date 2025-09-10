import time
import random
import os
import pyfiglet

hp = 20
max_hp = 50
weapon = "Fists"
inventory = []
buff = 1
money = 22
kindness = False
wincon = random.randint(1, 3)
visited = False
bought = False
spokento = False
comp1 = False
comp2 = False
comp3 = False

enemy_types = ["goblin", "giant spider", "orc", "wolf", "bandit"]
enemies = {
    "goblin": {"hp": 12, "attack": 4},
    "giant spider": {"hp": 40, "attack": 8},
    "orc": {"hp": 28, "attack": 6},
    "wolf": {"hp": 8, "attack": 4},
    "bandit": {"hp": 16, "attack": 6},
}

weapons = {
    "Fists": 4,
    "Dagger": 6,
    "Sword": 10,
    "Axe": 12,
    "Bow": 8,
}

def hpcheck():
    if hp <= 0:
        print("You died. Game over.")
        time.sleep(3)
        os.system('exit')
    else:
        print(f"You survived the battle! Your health is now {hp}.")

def roll_dice(sides):
    return random.randint(1, sides)

def inventory_check():
    global hp, buff  # Declare global variables to modify them inside the function

    if not inventory:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Your inventory is empty.")
        return None
    else:
        print("Your inventory contains:")
        for item in inventory:
            print(f"- {item}")
        choice = input("Use an item?: ").title()  # Capitalize the first letter for consistency
        if choice in inventory:
            if choice == "Potion":
                heal_amount = 25
                hp = min(hp + heal_amount, max_hp)  # Ensure hp does not exceed max_hp
                inventory.remove(choice)
            elif choice == "Smoke Bomb":
                print("You used a Smoke Bomb to escape!")
                inventory.remove(choice)  # Remove the item from inventory after use
                return "escape"  # Return "escape" to signal combat exit
            elif choice == "Throwing Knife":
                inventory.remove(choice)
                return "knife"  # Return "knife" to signal extra damage
                
        else:
            print("Item not found in inventory.")

def start_screen(): 
    print(pyfiglet.figlet_format("Text Adventure"))
    input("Press Enter to start...")
    os.system('cls' if os.name == 'nt' else 'clear')

def combat(enemy):
    global hp, weapon, buff  # Declare global variables to modify them inside the function
    enemy_health = enemies[enemy]["hp"]

    while hp > 0 and enemy_health > 0:
        print(f"\nYour Health: {hp} | {enemy} Health: {enemy_health}")
        action = input("Choose your action (attack/run/inventory): ").lower()

        if action == "attack":
            damage = roll_dice(weapons[weapon]) + buff
            enemy_health -= damage
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"You attacked the {enemy} for {damage} damage!")
        elif action == "run":
            if roll_dice(10) > 3:  # 70% chance to escape
                print("You managed to escape!")
                return
            else:
                print("You tried to run, but the enemy blocks your way!")
                
        elif action == "inventory":
            result = inventory_check()
            if result == "escape":
                print("You escaped the combat!")
                return
            elif result == "knife":
                dmg = random.randint(8, 11)
                enemy_health -= dmg
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"You dealt an extra {dmg} damage to the {enemy} with the Throwing Knife!")
            elif result is None:
                continue
        else:
            print("Invalid action. Try again.")
            continue

        if enemy_health > 0:
            enemy_damage = roll_dice(enemies[enemy]["attack"])
            hp -= enemy_damage
            print(f"The enemy attacked you for {enemy_damage} damage!")

    if hp <= 0:
        print("You have been defeated!")
    else:
        print("You defeated the enemy!")
    
def village():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\nYou are in the village of Eldoria. What would you like to do?")
        print("1. Visit the shop")
        print("2. Visit the tavern")
        print("3. Check the notice board")
        if kindness == True:
            print("4. Visit the stranger")
        if kindness == True:
            ans = input("Choose an option (1/2/3/4): ").strip()
        else:    
            ans = input("Choose an option (1/2/3): ").strip()

        if ans == "1":
            visit_shop()
        elif ans == "2":
            visit_tavern()
        elif ans == "3":
            check_notice_board()
        elif ans == "4" and kindness == True:
            visit_stranger()
        else:
            print("Invalid choice. Please try again.")

def visit_shop():
    global money, inventory
    instock = True
    os.system('cls' if os.name == 'nt' else 'clear')

    print("\nYou enter the shop. The shopkeeper greets you warmly.")
    print(f"You have {money} gold.")
    print("Available items:")
    print("1. Potion (10 gold)")
    print("2. Smoke Bomb (25 gold)")
    print("3. Throwing Knife (15 gold)")
    print("4. Sword (20 gold)")
    print("5. Bow (15 gold)")
    print("6. Leave the shop")
    ans = input("What would you like to buy? (1/2/3/4): ").strip()

    if ans == "1" and money >= 10:
        inventory.append("Potion")
        money -= 10
        print("You bought a Potion.")
    elif ans == "2" and money >= 25 and instock:
        inventory.append("Smoke Bomb")
        money -= 25
        print("You bought a Smoke Bomb.")
        instock = False
    elif ans == "3" and money >= 15:
        inventory.append("Throwing Knife")
        money -= 15
        print("You bought a Throwing Knife.")
    elif ans == "4":
        print("You leave the shop.")
    else:
        print("You don't have enough gold or entered an invalid option.")

def visit_tavern():
    global hp, money
    os.system('cls' if os.name == 'nt' else 'clear')

    print(f"You have {money} gold.")
    print("\nYou enter the tavern. The atmosphere is lively, with adventurers sharing stories.")
    print("You can:")
    print("1. Rest (5 gold, restores health)")
    print("2. Talk to the bartender")
    print("3. Leave the tavern")
    ans = input("What would you like to do? (1/2/3): ").strip()

    if ans == "1" and money >= 5:
        hp = max_hp
        money -= 5
        print("You rest at the tavern and restore your health to full.")
        time.sleep(2)
        visit_tavern()
    elif ans == "2":
        if not spokento:
            print('"Hello, adventurer! You must be new here. Welcome to our small village of Eldoria."')
            time.sleep(2)
            print('"Lately our village has been troubled by a curse put on us by a wicked sorcerer. Many adventurers have tried to lift the curse, but none have returned."')
            time.sleep(3)
            print('"If you are brave enough, you might want to check the notice board for quests that could help our village."')
            time.sleep(2)
            input('"Hopefully one of those will lead you to find a way to lift the curse... "')
            spokento = True
            visit_tavern()
        else:
            print('"Good to see you again, adventurer. Stay safe out there."')
            visit_tavern()
    elif ans == "3":
        print("You leave the tavern.")
    else:
        print("You don't have enough gold or entered an invalid option.")

def check_notice_board():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\nYou check the notice board. There are several quests posted:")
    if not comp1:
        print("1. Hunt the bandits in the forest")
    if not comp2:
        print("2. Find out what happened to the missing caravan")
    if not comp3:
        print("3. Kill the orcs terrorizing the nearby village")
    print("4. Leave the notice board")
    ans = input("Which quest would you like to take? (1/2/3/4): ").strip()

    if ans == "1" and not comp1:
        comp1 = True
        print("You accept the quest to hunt the bandits in the forest.")
        quest1()
    elif ans == "2" and not comp2:
        comp2 = True
        print("You accept the quest to find out what happened to the missing caravan.")
        quest2()
    elif ans == "3" and not comp3:
        comp3 = True
        print("You accept the quest to kill the orcs terrorizing the nearby village.")
        quest3()
    elif ans == "4":
        print("You leave the notice board.")
    else:
        print("Invalid choice. Please try again.")

def visit_stranger():
    global hp, weapon, buff, money, visited, bought
    os.system('cls' if os.name == 'nt' else 'clear')

    if visited and bought:
        print("The stranger is not here anymore.")
        return
    
    if not visited:
        print("\nYou approach the stranger you helped earlier. He looks at you with gratitude.")
        time.sleep(2)
        print('"Thank you for your kindness earlier. I want to repay you."')
        time.sleep(2)
        print("You feel a warm sensation as he touches your shoulder.")
        time.sleep(2)
        input("You have become stronger... ")
        buff = 2
        os.system('cls' if os.name == 'nt' else 'clear')
        visited = True
    else: 
        print('"Welcome back, kind adventurer"')

    if bought == False:
        print('"I will also allow you to buy a weapon of mine."')
        print("1. Axe (40 gold)")
        print("2. Leave")
        ans = input("What would you like to do? (1/2): ").strip()
        if ans == "1" and money >= 40:
            weapon = "Axe"
            money -= 40
            print("You bought an Axe.")
            bought = True
            return
        elif ans == "2":
            print("You leave the stranger.")
        else:
            print("You don't have enough gold or entered an invalid option.")



def quest1():
    global hp, money, inventory, weapon

    os.system('cls' if os.name == 'nt' else 'clear')
    print("You venture into the forest to hunt the bandits.")
    time.sleep(2)
    print("After a while, you spot a group of bandits up ahead, counting their loot.")
    time.sleep(2)

    ans = input("Do you want to sneak up on them or confront them head-on? (sneak/confront) ").strip().lower()
    luck = roll_dice(20)
    if ans == "sneak":
        if luck > 7:
            print("You successfully sneak up on the bandits and take them by surprise! You manage to kill one of them before the others can react.")
        else:
            print("The bandits catch you trying to sneak around them. Prepare for combat.")
    else: 
        print("You decide to confront the bandits head-on. They notice you and prepare to fight!")
        print("As they catch you sneaking they manage to hit you with a surprise attack!")
        hp -= 5
        print("You lose 5 health from the surprise attack.")
        combat("bandit")
        hpcheck()

    combat("bandit")
    hpcheck()
    combat("bandit")
    hpcheck()
    print("After defeating the bandits, you find a stash of gold and some supplies.")
    global money, inventory
    money += 20
    print("You picked up 20 gold.")
    inventory.append("Potion")
    time.sleep(2)
    if wincon == 1:
        print("As you search the bandits' belongings, you find a mysterious amulet that seems to glow with a faint light.")
        time.sleep(2)
        print("You have found the Amulet of Light, a powerful artifact that is said to have the ability to lift curses.")
        inventory.append("Amulet of Light")
        print("You return to the village and present the amulet to the villagers.")
        time.sleep(2)
        print("The curse is lifted, and the villagers celebrate your bravery and kindness.")
        time.sleep(2)
        print("Congratulations! You have completed your quest and saved the village of Eldoria!")
        time.sleep(5)
        os.system('exit')

def quest2():
    global hp, money, inventory, weapon

    os.system('cls' if os.name == 'nt' else 'clear')
    print("You set out to find the missing caravan.")
    time.sleep(2)
    print("After a few hours of searching, you find the remains of the caravan. It is covered by large spider webs, and there are no signs of any survivors.")
    time.sleep(2)
    print("As you investigate the area, you hear a rustling in the bushes.")
    time.sleep(2)
    print("2 giant spider emerges from the bushes, its eyes glinting in the dim light!")
    combat("giant spider")
    hpcheck()
    combat("giant spider")
    hpcheck()
    print("After defeating the spiders, you search the area and find some supplies that the caravan was carrying.")
    money += 15
    inventory.append("Potion")
    time.sleep(2)
    if wincon == 2:
        print("As you search the area, you find a hidden compartment in one of the wagons.")
        time.sleep(2)
        print("Inside, you find a mysterious amulet that seems to glow with a faint light.")
        time.sleep(2)
        print("You have found the Amulet of Light, a powerful artifact that is said to have the ability to lift curses.")
        inventory.append("Amulet of Light")
        print("You return to the village and present the amulet to the villagers.")
        time.sleep(2)
        print("The curse is lifted, and the villagers celebrate your bravery and kindness.")
        time.sleep(2)
        print("Congratulations! You have completed your quest and saved the village of Eldoria!")
        time.sleep(5)
        os.system('exit')

def quest3():
    global hp, money, inventory, weapon

    os.system('cls' if os.name == 'nt' else 'clear')
    print("You head to the nearby village to deal with the orcs.")
    time.sleep(2)
    print("Upon arriving, you find the village in ruins, with signs of a recent attack.")
    time.sleep(2)
    print("As you investigate, you hear a loud roar and see a group of orcs approaching!")
    time.sleep(2)
    horde = random.randint(2, 4)
    for _ in range(horde):
        combat("orc")
        hpcheck()
    print("After defeating the orcs, you search the area and find some supplies that the orcs had taken from the village.")
    money += random.randint(6, 13)
    inventory.append("Throwing Knife")
    time.sleep(2)
    if wincon == 3:
        print("As you search the area, you find a hidden compartment in one of the orc's bags.")
        time.sleep(2)
        print("Inside, you find a mysterious amulet that seems to glow with a faint light.")
        time.sleep(2)
        print("You have found the Amulet of Light, a powerful artifact that is said to have the ability to lift curses.")
        inventory.append("Amulet of Light")
        print("You return to the village and present the amulet to the villagers.")
        time.sleep(2)
        print("The curse is lifted, and the villagers celebrate your bravery and kindness.")
        time.sleep(2)
        print("Congratulations! You have completed your quest and saved the village of Eldoria!")
        time.sleep(5)
        os.system('exit')

#story from here
start_screen()
os.system('cls' if os.name == 'nt' else 'clear')

print("You find yourself in a dark forest, the trees towering above you. You can hear the sounds of creatures moving in the shadows just beyond your eyes' reach.")
time.sleep(4)
ans = input("Next to you on the ground you see a rusty dagger. Do you pick it up? (y/n) ")
if ans == "y":
    weapon = "Dagger"
    print("You pick up the dagger and feel a bit safer.")
    time.sleep(2)

print("As you tread along the forest path, you hear a rustling in the bushes ahead.")
time.sleep(3)
print("A goblin jumps out, brandishing a crude club!")
time.sleep(2)
combat("goblin")
hpcheck()

print("After defeating the goblin, you search its belongings and find a small pouch of gold coins.")
money += 10
time.sleep(2)
print("You continue down the path, reaching a fork in the road ahead of you.")
ans = input("Do you go left or right? (l/r) ")
os.system('cls' if os.name == 'nt' else 'clear')
if ans == "l":
    print("You take the left path, which leads you deeper into the forest.")
    time.sleep(2)
    print("Suddenly, two wolves descend from the trees above!")
    time.sleep(2)
    combat("wolf")
    hpcheck()
    combat("wolf")
    hpcheck()
    print("After defeating the wolves, you find a health potion among their belongings.")
    inventory.append("Potion")
    print("You also find a few scattered gold coins.")
    money += random.randint(5, 15)
    time.sleep(2)
elif ans == "r":
    print("You take the right path, which leads you to a small clearing.")
    time.sleep(2)
    print("Slumped against a tree in the clearing you see a robed figure.")
    time.sleep(2)
    print("As you approach, the figure looks up at you.")
    print('"Hello traveler, I am but a poor beggar lost in these woods. Could you spare me some gold?"')
    ans = input(f"You have {money} gold coins. How many do you give him? (0-{money}) ")
    if ans.isdigit() and 0 <= int(ans) <= money:
        gold_given = int(ans)
        money -= gold_given
        if gold_given >= 10:
            print('"Thank you so much! You truly are a kind man."')
            kindness = True
        else:
            print('"Thank you for your kindness."')

time.sleep(2)
os.system('cls' if os.name == 'nt' else 'clear')

print("You continue down the path, eventually reaching the edge of the forest.")
time.sleep(2)
print("Beyond the trees, you see a small village in the distance.")
time.sleep(2)
print("You have reached the village of Eldoria, a small town nestled between a mountain pass and the nearby forest.")
time.sleep(2)
print("As you enter the village, you notice a few shops and a tavern.")
time.sleep(1)
print("You also see a notice board with various quests posted on it.")
time.sleep(3)
input("continue...")
village()