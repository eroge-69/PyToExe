import random

#Global Time 
current_day = 0

#ANSI Colors
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
PURPLE = "\033[0;35m"
RESET = "\033[0m"

#Item Class
class Item:
    def __init__(self, name, item_type, effect=None, damage_bonus=0):
        self.name = name
        self.type = item_type
        self.effect = effect
        self.damage_bonus = damage_bonus

    def __str__(self):
        return self.name

# Player Class
class Player:
    def __init__(self, name, health=100, x=0, y=0):
        self.name = name
        self.health = health
        self.age = 20
        self.x = x
        self.y = y
        self.inventory = []
        self.gold = 10
        self.strength = 5
        self.speed = 5
        self.fishing = 5
        self.hunting = 5
        self.diplomacy = 0
        self.reputation = 10
        self.crafting = 5
        self.exhaustion = 0
        self.happiness = 20
        self.intelligence = 5
        self.prestige = 0
        self.fame = 0
        

    def move(self, direction):
        if direction == "up":
            self.y -= 1
            self.health -= 2
        elif direction == "down":
            self.y += 1
            self.health -= 2
        elif direction == "left":
            self.x -= 1
            self.health -= 2
        elif direction == "right":
            self.x += 1
            self.health -= 2

    def take_damage(self, dmg):
        self.health = max(0, self.health - dmg)
        self.happiness -= 1

    def heal(self, amt):
        self.health = min(100, self.health + amt)

    def add_item(self, item):
        self.inventory.append(item)
        print(f"You received: {item.name}")

    def get_weapon(self):
        for item in self.inventory:
            if item.type == "weapon":
                return item
        return None

    def display_stats(self):
        weapon = self.get_weapon()
        print(f"{self.name} - Health: {self.health} | Age: {self.age} | Gold: {self.gold}")
        print(f"Strength: {self.strength} | Speed: {self.speed} | Fishing: {self.fishing} | Hunting: {self.hunting} | Exhaustion: {self.exhaustion} | Intelligence: {self.intelligence} | Happiness: {self.happiness} | ")
        print(f"Equipped Weapon: {weapon.name if weapon else 'None'} (Bonus: {weapon.damage_bonus if weapon else 0})")
        print("Inventory:")
        if self.inventory:
            for i, item in enumerate(self.inventory, 1):
                print(f"{i}. {item.name} ({item.type})")
        else:
            print("Empty")

#Enemy List
enemy_list = ["Goblin", "Zombie", "Feral Human", "Grey Humanoid", "Feral Dog", "Living Goo", "Spore Cloud", "A Desperate Family", "Stacey's Mom", "A Grue", "Lone Survivor", "Small Zombie Horde", "Confused Elder", "Billy Mitchell, Video Game Player of the Century", "Giant Frog" , "Giant Mosquito" , "Scavenger", "Silly Goose", "Giant Spider" , "Nervous Teen", "Pokémon Fanatic", "Armed Thug"]

#Enemy Class
class Enemy:
    def __init__(self, name, health, attack, gold_reward):
        self.name = name
        self.health = health
        self.attack = attack
        self.gold_reward = gold_reward

    def take_damage(self, dmg):
        self.health = max(0, self.health - dmg)

#Settlement Class
class Settlement:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.population = random.randint(2, 50000)
        self.resources = random.choice(["Iron", "Fish", "Wheat", "Wood", "Oil", "Technology"])
        self.government = random.choice(["Democracy", "Monarchy", "Tribal", "Republic"])
        self.jobs = ["Farmer", "Guard", "Trader", "Mayor", "Chef"]
        self.mayor = None
        self.at_war_with = None

    def display_info(self):
        print(f"\nSettlement: {self.name}")
        print(f"Location: ({self.x}, {self.y})")
        print(f"Population: {self.population}")
        print(f"Resources: {self.resources}")
        print(f"Government: {self.government}")
        print(f"Mayor: {self.mayor if self.mayor else 'None'}")
        print(f"War: {self.at_war_with}")

    def apply_for_job(self, player):
        print("\nAvailable Jobs:")
        for i, job in enumerate(self.jobs, 1):
            print(f"{i}. {job}")
        choice = input("Choose a job to apply for: ")
        try:
            index = int(choice) - 1
            job = self.jobs[index]
            if job == "Mayor":
                self.mayor = player.name
                print(f"You are now mayor of {self.name}!")
            else:
                print(f"You are now working as a {job} in {self.name}.")
        except:
            print("Invalid selection.")

#GameMap Class
class GameMap:
    def __init__(self, size=30):
        self.size = size
        self.base_grid = [['#' for _ in range(size)] for _ in range(size)]
        self.player = None
        self.settlements = []
        self.claimed_lands = []
        self.populate_map()

    def set_player(self, player):
        self.player = player

    def is_valid_position(self):
        return 0 <= self.player.x < self.size and 0 <= self.player.y < self.size

    def display_map(self):
        print("\nMap:")
        for y in range(self.size):
            row = ""
            for x in range(self.size):
                if self.player.x == x and self.player.y == y:
                    row += f"{GREEN}P{RESET}"
                else:
                    row += self.base_grid[y][x] + " "
            print(row)

    def move_player(self, direction):
        old_x, old_y = self.player.x, self.player.y
        self.player.move(direction)
        if not self.is_valid_position():
            print("Can't move there!")
            self.player.x, self.player.y = old_x, old_y

    def populate_map(self):
        for _ in range(self.size // 3):
            x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            #self.base_grid[y][x] = 'E'
        for i in range(10):
            while True:
                x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
                if self.base_grid[y][x] == '#':
                    s = Settlement(f"Town{i+1}", x, y)
                    self.settlements.append(s)
                    self.base_grid[y][x] = f"{PURPLE}S{RESET}"
                    break
                    
        for i in range(20):
            while True:
                x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
                if self.base_grid[y][x] == "#":
                    self.base_grid[y][x] = f"{BLUE}~{RESET}"  
                    break

    def claim_land(self, player):
        x, y = player.x, player.y
        if self.base_grid[y][x] != 'C' and (x, y) not in [(c[0], c[1]) for c in self.claimed_lands]:
            if player.gold >= 50:
                player.gold -= 50
                self.base_grid[y][x] = f"{GREEN}C{RESET}"
                self.claimed_lands.append([x, y, player.name, 10, 1])
                print(f"You claimed land at ({x},{y}) for 50 gold.")
            else:
                print("Not enough gold.")
        else:
            print("This land can't be claimed.")

    def update_claims(self):
        for i in range(len(self.claimed_lands)):
            x, y, owner, pop, res = self.claimed_lands[i]
            if random.random() < 0.05:
                attacker = random.choice(self.settlements)
                loss = random.randint(5, 10)
                print(f"⚠️ {attacker.name} raids your land at ({x},{y})! Loss: {loss} population.")
                pop = max(0, pop - loss)
                if pop == 0:
                    print(f"🔥 Your land at ({x},{y}) was lost!")
                    self.base_grid[y][x] = 'L'
                    self.claimed_lands[i] = None
                    continue
            else:
                pop += random.randint(0, 5)
                res += random.randint(0, 2)
            self.claimed_lands[i] = [x, y, owner, pop, res]
            if self.player.name == owner:
                income = pop // 10
                self.player.gold += income
                print(f"Tax income from ({x},{y}): {income} gold")
        self.claimed_lands = [c for c in self.claimed_lands if c]

    def interact_with_settlement(self):
        for s in self.settlements:
            if s.x == self.player.x and s.y == self.player.y:
                s.display_info()
                if input("Apply for job? (yes/no): ").lower() == "yes":
                    s.apply_for_job(self.player)
                return
        print("Not in a settlement.")

    def handle_war_tick(self):
        if random.random() < 0.1:
            s1, s2 = random.sample(self.settlements, 2)
            if s1.at_war_with is None and s2.at_war_with is None:
                s1.at_war_with = s2.name
                s2.at_war_with = s1.name
                print(f"\n⚔️ WAR DECLARED between {s1.name} and {s2.name}!")

        for s in self.settlements:
            if s.at_war_with:
                opponent = next((x for x in self.settlements if x.name == s.at_war_with), None)
                if opponent:
                    loss = random.randint(5, 15)
                    s.population = max(0, s.population - loss)
                    opponent.population = max(0, opponent.population - loss)
                    print(f"{s.name} and {opponent.name} lost {loss} pop in war.")
                    if s.population <= 0 or opponent.population <= 0:
                        winner = s if s.population > 0 else opponent
                        loser = opponent if winner == s else s
                        print(f"\n🏴 {loser.name} conquered by {winner.name}!")
                        winner.population += loser.population
                        winner.resources += f", {loser.resources}"
                        loser.population = 0
                        loser.resources = "None"
                        loser.at_war_with = None
                        winner.at_war_with = None

#Combat
def combat(player, enemy):
    weapon = player.get_weapon()
    weapon_bonus = weapon.damage_bonus if weapon else 0
    min_dmg = 5 + player.strength // 2 + weapon_bonus
    max_dmg = 10 + player.strength + weapon_bonus

    print(f"\nCombat: {player.name} vs {enemy.name}")
    while player.health > 0 and enemy.health > 0:
        player_first = random.random() < (0.5 + (player.speed - 5) * 0.05)
        order = ["player", "enemy"] if player_first else ["enemy", "player"]

        for turn in order:
            if turn == "player" and enemy.health > 0:
                dmg = random.randint(min_dmg, max_dmg)
                enemy.take_damage(dmg)
                print(f"You dealt {dmg} to {enemy.name}")
            elif turn == "enemy" and enemy.health > 0:
                if random.randint(1, 100) <= min(player.speed * 2, 50):
                    print("You dodged!")
                else:
                    dmg = random.randint(3, 10)
                    player.take_damage(dmg)
                    print(f"{enemy.name} hits for {dmg}")
        print(f"{player.name} HP: {player.health} | {enemy.name} HP: {enemy.health}")

    if player.health > 0:
        player.gold += enemy.gold_reward
        print(f"Victory! Earned {enemy.gold_reward} gold.")
    else:
        print("You died...")

#Events
def random_event(player, game_map):
    e = random.choice(["find_item", "find_potion", "encounter_enemy"])
    if e == "find_item":
        mat = random.choice(["Wood", "Stone", "Iron", "Water", "Hot Sauce", "Animal Hide", "Small Battery" , "Smart Phone", "Solar Panel" , "(Book) Farming 101", "String", "Bones"])
        player.add_item(Item(mat, "material"))
    elif e == "find_potion":
        player.add_item(Item("Herb", "material"))
    elif e == "encounter_enemy":
        enemy = Enemy(random.choice(enemy_list), 30, 5, 20)
        combat(player, enemy)

def craft_item(player):
    recipes = {
        "Wooden Spear": {"Wood": 2},
        "Healing Potion": {"Herb": 3, "Water": 1},
        "Stone Axe": {"Wood": 1, "Stone": 2},
        "Iron Axe": {"Wood": 1, "Iron": 2},
        "Iron Sword": {"Iron": 3, "Wood": 1},
        "Cooked Meat": {"Raw Meat": 2},
        "Cooked Fish": {"Raw Fish": 2},
        "Spicy Cooked Meat": {"Cooked Meat":1, "Hot Sauce": 1},
        "Fishing Pole": {"Wood": 1, "String": 2},
        
        
        
        
    }
    print("\nCraft Menu:")
    for i, r in enumerate(recipes, 1):
        print(f"{i}. {list(recipes.keys())[i-1]} - {recipes[list(recipes.keys())[i-1]]}")
    try:
        i = int(input("Choose a recipe: ")) - 1
        item_name = list(recipes.keys())[i]
        cost = recipes[item_name]
        inv = [x.name for x in player.inventory]
        if all(inv.count(mat) >= amt for mat, amt in cost.items()):
            for mat, amt in cost.items():
                for _ in range(amt):
                    for item in player.inventory:
                        if item.name == mat:
                            player.inventory.remove(item)
                            break
            if item_name == "Healing Potion":
                item = Item(item_name, "potion", effect={"heal": 25})
            elif item_name == "Cooked Meat":
                item = Item(item_name, "potion", effect={"heal": 20})
            elif item_name == "Spicy Cooked Meat":
            	item = Item(item_name, "potion", effect={"heal": 25})
            elif item_name == "Cooked Fish":
                item = Item(item_name, "potion", effect={"heal": 15})
            elif item_name == "Iron Sword":
                item = Item(item_name, "weapon", damage_bonus=5)
            elif item_name == "Wooden Spear":
                item = Item(item_name, "weapon", damage_bonus=2)
            elif item_name == "Stone Axe":
                item = Item(item_name, "weapon", damage_bonus=3)
            elif it_name == "Iron Axe":
            	item = Item(item_name, "weapon")
            else:
                item = Item(item_name, "tool")
            player.add_item(item)
        else:
            print("Not enough materials.")
    except:
        print("Invalid choice.")

def use_item(player):
    potions = [i for i in player.inventory if i.type == "potion"]
    if not potions:
        print("No usable items.")
        return
    for i, p in enumerate(potions, 1):
        print(f"{i}. {p.name}")
    try:
        i = int(input("Use which item? ")) - 1
        item = potions[i]
        if item.effect and "heal" in item.effect:
            player.heal(item.effect["heal"])
            player.inventory.remove(item)
            print(f"You healed for {item.effect['heal']}.")
    except:
        print("Invalid.")

def hunt(player):
    if random.randint(0, 100) < (50 + player.hunting * 3):
        amt = random.randint(1, player.hunting)
        for _ in range(amt):
            player.add_item(Item("Raw Meat", "material"))
        print(f"You got {amt} Raw Meat.")
    else:
        print("Hunt failed.")

def fish(player, game_map):
    tile = game_map.base_grid[player.y][player.x]
    if tile != f"{BLUE}~{RESET}":
        print("You must be near water (~) to fish.")
        return

    if random.randint(0, 100) < (50 + player.fishing * 3):
        amt = random.randint(1, player.fishing)
        for _ in range(amt):
            player.add_item(Item("Raw Fish", "material"))
        print(f"You caught {amt} Raw Fish.")
    else:
        print("Fishing failed.")


#Main
def main():
    global current_day
    print(f"{RED}Welcome to the world!  What will you do in it?{RESET}")
    player = Player(input("Enter your name: "))
    game_map = GameMap()
    game_map.set_player(player)
    

    while player.health > 0:
        game_map.display_map()
        print(f"\nDay {current_day} | Age: {player.age}")
        print("1. Move\n2. Claim Land\n3. View Stats\n4. Random Event")
        print("5. Visit Settlement\n6. Wait\n7. Craft Item\n8. Use Item")
        print("9. Hunt\n10. Fish\n11. Quit")
        action = input("Choose: ")

        if action == "1":
            direction = input("Direction (up/down/left/right): ")
            game_map.move_player(direction)
            current_day += 30
        elif action == "2":
            game_map.claim_land(player)
            current_day += 30
        elif action == "3":
            player.display_stats()
        elif action == "4":
            random_event(player, game_map)
            current_day += 30
        elif action == "5":
            game_map.interact_with_settlement()
        elif action == "6":
            print("You wait...")
            current_day += 7
        elif action == "7":
            craft_item(player)
        elif action == "8":
            use_item(player)
            current_day += 1
        elif action == "9":
            hunt(player)
            current_day += 1
        elif action == "10":
            fish(player, game_map)
            current_day += 1
        elif action == "11":
            print("You commit suicide.")
            break
        else:
            print("Invalid.")

        if current_day % 365 == 0:
            player.age += 1
            game_map.update_claims()
            game_map.handle_war_tick()

            # Chance of death after age 45
            if player.age >= 45:
                death_chance = (player.age - 44) * 0.01  # 1% at 45, 2% at 46, etc.
                if random.random() < death_chance:
                    print(f"{RED}You passed away peacefully at age {player.age}.{RESET}")
                    player.health = 0

if __name__ == "__main__":
    main()
