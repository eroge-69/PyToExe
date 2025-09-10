# main.py - Smith GTA Full Python Prototype
import time
import random

# Game Data
zones = {
    "Neon City": {"safe": True, "loot": ["Cash", "Ammo"], "hostile": ["Gangsters"]},
    "Vice Shores": {"safe": True, "loot": ["Jewels", "Cash"], "hostile": ["Security"]},
    "Industrial Docks": {"safe": False, "loot": ["Contraband", "Tools"], "hostile": ["Rival Smugglers"]},
    "Old Town": {"safe": True, "loot": ["Cash", "Gadgets"], "hostile": ["Thieves"]},
    "Dustlands": {"safe": False, "loot": ["Weapons", "Fuel"], "hostile": ["Raiders"]},
    "Green Hills": {"safe": True, "loot": ["Food", "Supplies"], "hostile": ["Wild Animals"]}
}

vehicles = {
    "Sports Car": {"speed": 120, "fuel": 100, "plate": "SMITH"},
    "Motorcycle": {"speed": 100, "fuel": 80, "plate": "SMITH"},
    "Helicopter": {"speed": 200, "fuel": 150, "plate": "SMITH"}
}

missions = {
    "High Roller Heist": {"zone": "Vice Shores", "reward": 5000, "type": "Heist", "difficulty": 3},
    "Smuggler's Run": {"zone": "Industrial Docks", "reward": 3000, "type": "Delivery", "difficulty": 2},
    "Neon Nights": {"zone": "Neon City", "reward": 4000, "type": "Chase", "difficulty": 3},
    "Desert Storm": {"zone": "Dustlands", "reward": 4500, "type": "Raid", "difficulty": 4},
    "Last Passenger": {"zone": "Green Hills", "reward": 3500, "type": "Escort", "difficulty": 2}
}

player = {
    "name": "Player1",
    "cash": 0,
    "inventory": [],
    "vehicle": None,
    "location": "Neon City",
    "health": 100,
    "time_of_day": "Day"
}

# Helper Functions
def show_intro():
    print("=== Smith GTA Prototype ===")
    print("Represented by Smith Makwana")
    print("All vehicles have number plate: SMITH\n")
    time.sleep(2)

def show_zones():
    print("Zones and Info:")
    for z, info in zones.items():
        print(f"- {z}: Safe={info['safe']}, Loot types={info['loot']}, Hostile={info['hostile']}")
    print()

def choose_vehicle():
    print("Available Vehicles:")
    for i, v in enumerate(vehicles.keys(), 1):
        stats = vehicles[v]
        print(f"{i}. {v} (Plate: {stats['plate']}, Speed: {stats['speed']}, Fuel: {stats['fuel']})")
    choice = int(input("Select vehicle number: ")) - 1
    vehicle_name = list(vehicles.keys())[choice]
    player["vehicle"] = vehicle_name
    print(f"You are now using {vehicle_name}.\n")

def player_status():
    print("\nPlayer Status:")
    for key, value in player.items():
        print(f"{key}: {value}")
    print()

def loot_zone(zone):
    loot = zones[zone]["loot"]
    found = random.choice(loot)
    player["inventory"].append(found)
    print(f"You searched the zone and found: {found}!")

def day_night_cycle():
    player["time_of_day"] = "Night" if player["time_of_day"]=="Day" else "Day"
    print(f"\nTime changed. It's now {player['time_of_day']}.\n")

def choose_mission():
    print("Available Missions:")
    for i, m in enumerate(missions.keys(), 1):
        mission = missions[m]
        print(f"{i}. {m} - Zone: {mission['zone']}, Type: {mission['type']}, Reward: ${mission['reward']}")
    choice = int(input("Select mission number: ")) - 1
    mission_name = list(missions.keys())[choice]
    start_mission(mission_name)

def start_mission(mission_name):
    mission = missions[mission_name]
    zone_info = zones[mission["zone"]]
    print(f"\nStarting mission: {mission_name} in {mission['zone']}")
    print(f"Mission Type: {mission['type']}, Difficulty: {mission['difficulty']}")
    print("Mission in progress...")
    time.sleep(2)

    # Random outcome based on difficulty and time of day
    success_chance = 80 - mission["difficulty"]*10
    if player["time_of_day"] == "Night":
        success_chance -= 10

    outcome = random.randint(1,100)
    if outcome <= success_chance:
        print("Mission completed successfully!")
        player["cash"] += mission["reward"]
        loot_zone(mission["zone"])
    else:
        damage = random.randint(5, 30)
        player["health"] -= damage
        print(f"Mission failed! You took {damage} damage.")
        if player["health"] <= 0:
            print("You have died! Game over.")
            exit()
    day_night_cycle()
    print(f"Current Cash: ${player['cash']}\n")

# Game Loop
def main():
    show_intro()
    while True:
        print("1. Show Zones")
        print("2. Choose Vehicle")
        print("3. Choose Mission")
        print("4. Player Status")
        print("5. Quit")
        option = input("Select option: ")
        if option == "1":
            show_zones()
        elif option == "2":
            choose_vehicle()
        elif option == "3":
            choose_mission()
        elif option == "4":
            player_status()
        elif option == "5":
            print("Exiting game. Goodbye!")
            break
        else:
            print("Invalid option.\n")

if __name__ == "__main__":
    main()
