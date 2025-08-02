import random

print("Welcome to the world of Minecraft")

PlainsDig = ["Grass",
             "Rock",
             "Dirt",
             "Pebble",
             "Plank",
             "Sapling",
             "Lake",
             "Tree"]

PlainsExplore = ["Caves"]

CavesDig = ["Rock",
            "Dirt",
            "Bedrock",
            "Lava",
            "Coal"]

CavesExplore = ["Plains"]

Inventory = []
SpawnBiomes = ["Plains"]

Biome = random.choice(SpawnBiomes)

def Dig(Biome, Inventory):
    if Biome == "Plains":
        Dug = random.choice(PlainsDig)
    elif Biome == "Caves":
        Dug = random.choice(CavesDig)
    else:
        print("uhm, I think smth went wrong :/ (Error code: 324)")
    if Dug == "Grass":
        print("You found some grass")
        if Inventory.count("Sapling") > 0:
            while True:
                Input = input("Would you like to (1) dig it, or (2) plant your sapling in here? ")
                if Input == "1":
                    print("Dirt was added to inventory")
                    Inventory.append("Dirt")
                    print("You have", Inventory.count("Dirt"), "dirt(s) in your inventory")
                    break
                elif Input == "2":
                    print("You plant the sapling")
                    print("Trees will generate more frequently now")
                    Inventory.remove("Sapling")
                    PlainsDig.append("Tree")
                    print("You have", Inventory.count("Sapling"), "Sapling(s) in your inventory")
                    break
                else:
                    print("Invalid choice. Please enter 1 or 2.")
        else:
            textbox = input("Dirt was added to inventory")
            Inventory.append("Dirt")
            print("You have ",(Inventory.count("Dirt")), "dirt(s) in your inventory")
    if Dug == "Dirt":
        print("You found some dirt")
        textbox = input("dirt was added to inventory")
        Inventory.append("Dirt")
        print("You have ",(Inventory.count("Dirt")), "dirt(s) in your inventory")        
    if Dug == "Rock":
        print("You found some stone")
        if "wooden pickaxe" in Inventory:
            Inventory.append("stone")
            textbox = input("You broke the rock and collected Stone")
            print("You have", Inventory.count("stone"), "stone(s) in your inventory")
        else:
            textbox = input("You do not yet have the tools to break it")
    if  Dug == "Pebble":
        print("You found a pebble")
        textbox = input("stone was added to inventory")
        Inventory.append("stone")
        print("You have ",(Inventory.count("stone")), "stone(s) in your inventory")
    if Dug == "Plank":
        print("You found a lone plank")
        textbox = input("Oak Plank was added to inventory")
        Inventory.append("oak plank")
        print("You have ",(Inventory.count("oak plank")), "Oak Plank(s) in your inventory")
    if Dug == "Sapling":
        print("You found a sapling")
        print("You could plant this in some grass if you found some")
        textbox = input("Sapling was added to inventory")
        Inventory.append("Sapling")
        print("You have ",(Inventory.count("Sapling")), "Sapling(s) in your inventory")
    if Dug == "Bedrock":
        print("You found bedrock at the bottom of the cave")
        textbox = input("There's nothing else left in the cave, you decide to leave")
        Biome = Explore(Biome)
    if Dug == "Lava":
        print("You dug into lava")
        textbox = input("You died lulz")
        quit()
    if Dug == "Lake":
        print("You found a lake")
        textbox = input("Neat")
    if Dug == "Tree":
        print("You found a tree")
        log_count = random.randint(4,9)
        print(log_count, "oak logs were added to inventory")
        for x in range(log_count):
            Inventory.append("oak log")
        print("You have ",(Inventory.count("oak log")), "oak log(s) in your inventory")
    if Dug == "Coal":
        print("You found some Coal")
        if "wooden pickaxe" in Inventory:
            Inventory.append("Coal")
            textbox = input("You broke the rock and collected Coal")
            print("You have", Inventory.count("Coal"), "Coal(s) in your inventory")
        else:
            textbox = input("You do not yet have the tools to break it")

    return(Biome)

def Craft(Inventory):
    recipes = {"oak plank": ({"oak log": 1}, 4),
               "stick": ({"oak plank": 1}, 4),
               "crafting table": ({"oak plank": 4}, 1),
               "wooden pickaxe": ({"stick": 2, "oak plank": 3}, 1),
               "stone pickaxe": ({"stick": 2, "stone": 3}, 1)}

    requires_table = ["wooden pickaxe",
                      "stone pickaxe"]

    craftable = []
    for item, (ingredients, amount) in recipes.items():
        if item in requires_table and "crafting table" not in Inventory:
            continue

        can_craft = all(Inventory.count(ing) >= amt for ing, amt in ingredients.items())
        if can_craft:
            craftable.append(item)

    if not craftable:
        print("You don't have enough materials to craft anything.")
        return

    print("You can craft:")
    for i, item in enumerate(craftable):
        ingredients, amount = recipes[item]
        ing_list = ", ".join(f"{amt} {ing}" for ing, amt in ingredients.items())
        print(f"{i + 1}. {item} (x{amount}) — Requires: {ing_list}")

    try:
        choice = int(input("Choose an item to craft by number: ")) - 1
        if choice < 0 or choice >= len(craftable):
            print("Invalid choice.")
            return

        selected = craftable[choice]
        ingredients, amount = recipes[selected]
        
        for ing, amt in ingredients.items():
            for _ in range(amt):
                Inventory.remove(ing)

        for _ in range(amount):
            Inventory.append(selected)

        print(f"You crafted {amount} {selected}(s)!")
        print(f"You now have: {Inventory.count(selected)} {selected}(s)")

    except ValueError:
        print("Please enter a valid number.")

def Explore(Biome):
    if Biome == "Plains":
        Biome = random.choice(PlainsExplore)
    elif Biome == "Caves":
        Biome = random.choice(CavesExplore)

    if Biome == "Plains":
        print("You find yourself in a flat grassland, welcome to the plains biome")
    if Biome == "Caves":
        print("You find yourself in a dark cold cave")

    return(Biome)

while True:
    Input = input("What will you do? - (1) Mine, (2) Craft, (3) Explore, (4) Inventory")
    try:
        if int(Input) == 1:
            Biome = Dig(Biome, Inventory)
        if int(Input) == 2:
            Craft(Inventory)
        if int(Input) == 3:
            Biome = Explore(Biome)
        if int(Input) == 4:
            if not Inventory:
                print("Your inventory is empty.")
            else:
                print("Your inventory:")
                counted = {}
                for item in Inventory:
                    counted[item] = counted.get(item, 0) + 1
                for item, count in counted.items():
                    print(f"{item}: {count}")
    except ValueError:
        print("Please enter a number.")
