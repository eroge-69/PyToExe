# Interactive Adventure Game
#  Item Classes 
class ItemBase:
    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    def __str__(self):
        return f"{self.name} - {self.description}"

class Key(ItemBase): pass
class Coin(ItemBase): pass
class PassCard(ItemBase): pass
class Torch(ItemBase): pass
class Gem(ItemBase): pass
class Map(ItemBase): pass
class Potion(ItemBase): pass
class Sword(ItemBase): pass
class Shield(ItemBase): pass
class Crown(ItemBase): pass

#  Game Rooms 
rooms = {
    "Start": {"desc": "You are at the start of your journey.", "moves": {"forward": "Forest", "right": "Village"}},
    "Forest": {"desc": "You are in a dark forest.", "moves": {"left": "Start", "forward": "Cave"}, "item": Key("Key", "Opens locked doors")},
    "Village": {"desc": "You are in a quiet village.", "moves": {"left": "Start", "forward": "Market"}, "item": Coin("Coin", "Can be traded")},
    "Market": {"desc": "You are at the village market.", "moves": {"back": "Village", "right": "Castle Gate"}, "item": PassCard("PassCard", "Lets you into the castle")},
    "Castle Gate": {"desc": "A guard blocks the gate. You need a PassCard.", "moves": {"left": "Market", "forward": "Castle"}, "item": Torch("Torch", "Lights dark areas")},
    "Castle": {"desc": "Inside the castle hall.", "moves": {"back": "Castle Gate", "forward": "Throne Room"}, "item": Crown("Crown", "Symbol of royalty")},
    "Throne Room": {"desc": "A majestic throne room.", "moves": {"back": "Castle", "forward": "Temple"}},
    "Cave": {"desc": "A dark cave.", "moves": {"back": "Forest", "forward": "Mountain"}, "item": Map("Map", "Shows hidden paths")},
    "Mountain": {"desc": "At the mountain peak.", "moves": {"back": "Cave", "right": "Lake"}, "item": Gem("Gem", "A precious gem")},
    "Lake": {"desc": "A calm lake.", "moves": {"left": "Mountain", "forward": "Temple"}, "item": Potion("Potion", "Restores strength")},
    "Temple": {"desc": "Ancient temple ruins.", "moves": {"back": "Lake", "forward": "Dungeon Entrance"}},
    "Dungeon Entrance": {"desc": "Entrance to a dark dungeon.", "moves": {"back": "Temple", "forward": "Dungeon"}, "item": Sword("Sword", "A sharp weapon")},
    "Dungeon": {"desc": "Inside the dungeon.", "moves": {"back": "Dungeon Entrance", "forward": "Armory"}, "item": Shield("Shield", "Protects you")},
    "Armory": {"desc": "Old castle armory.", "moves": {"back": "Dungeon", "forward": "Secret Tunnel"}},
    "Secret Tunnel": {"desc": "A hidden underground tunnel.", "moves": {"back": "Armory", "forward": "Treasure Room"}},
    "Treasure Room": {"desc": "You have reached the treasure room! The game ends here.", "moves": {}}
}

# Player Data 
player_name = ""
current_room = "Start"
bag = []
BAG_CAPACITY = 4

#  Helper Functions
def show_status():
    print(f"\n Location: {current_room}")
    print(rooms[current_room]["desc"])
    if "item" in rooms[current_room]:
        print(f" You see an item: {rooms[current_room]['item']}")
    print(" Bag:", ", ".join([item.name for item in bag]) if bag else "Empty")

def move():
    global current_room
    moves = rooms[current_room]["moves"]
    if not moves:
        print(" No more moves from here.")
        return
    
    print("\nAvailable directions:")
    for i, direction in enumerate(moves.keys(), 1):
        print(f"{i}. {direction.capitalize()} -> {moves[direction]}")
    
    choice = input("Choose direction number: ")
    try:
        choice_num = int(choice)
        if 1 <= choice_num <= len(moves):
            direction = list(moves.keys())[choice_num-1]
            # Castle Gate restriction
            if current_room == "Castle Gate" and direction == "forward" and not any(isinstance(i, PassCard) for i in bag):
                print(" The guard stops you: 'You cannot enter without a PassCard!'")
                return
            current_room = moves[direction]
        else:
            print(" Invalid direction choice.")
    except ValueError:
        print("Please enter a valid number.")

def pick_item():
    if "item" in rooms[current_room]:
        if len(bag) < BAG_CAPACITY:
            bag.append(rooms[current_room]["item"])
            print(f" You picked up: {rooms[current_room]['item'].name}")
            del rooms[current_room]["item"]
        else:
            print(" Your bag is full! (Max 4 items)")
    else:
        print(" No item here.")

def check_bag():
    if bag:
        print("\n Bag Contents:")
        for i, item in enumerate(bag, 1):
            print(f"{i}. {item}")
    else:
        print("\n Your bag is empty.")

# Main Game Loop 
def start_game():
    global player_name
    player_name = input("Enter your character name: ") or "Player1"
    print(f"\nWelcome, {player_name}! Your adventure begins.")
    
    while current_room != "Treasure Room":
        show_status()
        print("\nChoose an action:")
        print("1. Move")
        print("2. Pick up item")
        print("3. Check bag")
        print("4. Quit")
        while True:
            action = input("Please choose action 1 to 4: ")
        
            if action == "1":
                move()
            elif action == "2":
                pick_item()
            elif action == "3":
                check_bag()
            elif action == "4":
                print(" Thanks for playing!")
                break
            else:
                print(" Invalid choice.")
                print("Invalid input. Please choose action 1 to 4.")
    
    if current_room == "Treasure Room":
        print("\n Congratulations! You reached the treasure room and completed the game!")

# Start the Game 
if __name__ == "__main__":
    start_game()

    