import random
import time
import os
import sys

# ANSI color codes for terminal text
class Colors:
    GREEN = '\033[92m'
    BRIGHT_GREEN = '\033[32m'
    DARK_GREEN = '\033[32m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_green(text):
    print(f"{Colors.GREEN}{text}{Colors.RESET}")

def print_bright_green(text):
    print(f"{Colors.BRIGHT_GREEN}{text}{Colors.RESET}")

def print_red(text):
    print(f"{Colors.RED}{text}{Colors.RESET}")

def print_yellow(text):
    print(f"{Colors.YELLOW}{text}{Colors.RESET}")

def print_blue(text):
    print(f"{Colors.BLUE}{text}{Colors.RESET}")

class LongRoadToMoscow:
    def __init__(self):
        # Starting resources
        self.fuel = 100
        self.food = 150
        self.water = 100
        self.medical_supplies = 50
        self.ammunition = 75
        self.radiation_medicine = 30
        
        # Player stats
        self.health = 100
        self.radiation_level = 0
        self.morale = 100
        self.vehicle_condition = 100
        
        # Game state
        self.distance_traveled = 0
        self.total_distance = 2500  # km from Paris to Moscow
        self.day = 1
        self.money = 500  # Euros/Rubles
        self.current_location = "Paris, France"
        self.game_over = False
        self.victory = False
        
        # Starting party members
        self.party = [
            {"name": "Jean", "health": 100, "status": "Good", "profession": "Engineer", "type": "human", "disease": None},
            {"name": "Marie", "health": 100, "status": "Good", "profession": "Doctor", "type": "human", "disease": None},
            {"name": "Klaus", "health": 100, "status": "Good", "profession": "Soldier", "type": "human", "disease": None},
            {"name": "Anna", "health": 100, "status": "Good", "profession": "Scientist", "type": "human", "disease": None}
        ]
        
        # Companion slots (can recruit up to 6 additional companions)
        self.max_companions = 10
        
        # Disease system
        self.diseases = {
            "cholera": {"severity": "high", "contagious": True, "cure": "medical_supplies", "daily_damage": 20},
            "flu": {"severity": "medium", "contagious": True, "cure": "medical_supplies", "daily_damage": 10},
            "covid": {"severity": "medium", "contagious": True, "cure": "medical_supplies", "daily_damage": 15},
            "bubonic_plague": {"severity": "very_high", "contagious": True, "cure": "medical_supplies", "daily_damage": 25},
            "dysentery": {"severity": "high", "contagious": False, "cure": "medical_supplies", "daily_damage": 18},
            "radiation_sickness": {"severity": "high", "contagious": False, "cure": "radiation_medicine", "daily_damage": 22},
            "pneumonia": {"severity": "high", "contagious": False, "cure": "medical_supplies", "daily_damage": 16},
            "typhus": {"severity": "high", "contagious": True, "cure": "medical_supplies", "daily_damage": 19}
        }
        
        # Locations on the trail
        self.locations = [
            {"name": "Paris, France", "distance": 0, "safe": False},
            {"name": "Metz, France", "distance": 350, "safe": True},
            {"name": "Stuttgart, Germany", "distance": 650, "safe": False},
            {"name": "Munich, Germany", "distance": 850, "safe": True},
            {"name": "Vienna, Austria", "distance": 1100, "safe": False},
            {"name": "Budapest, Hungary", "distance": 1350, "safe": True},
            {"name": "Cluj, Romania", "distance": 1600, "safe": False},
            {"name": "Kiev, Ukraine", "distance": 1950, "safe": False},
            {"name": "Kursk, Russia", "distance": 2200, "safe": True},
            {"name": "Moscow, Russia", "distance": 2500, "safe": True}
        ]
        
        self.current_location_index = 0
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def main_menu_art(self):
        art = f"""{Colors.BRIGHT_GREEN}
    ████████████████████████████████████████████████████████████████████████
    ██                                                                    ██
    ██    █████╗     ██╗      ██████╗ ███╗   ██╗ ██████╗                 ██
    ██   ██╔══██╗    ██║     ██╔═══██╗████╗  ██║██╔════╝                 ██
    ██   ███████║    ██║     ██║   ██║██╔██╗ ██║██║  ███╗                ██
    ██   ██╔══██║    ██║     ██║   ██║██║╚██╗██║██║   ██║                ██
    ██   ██║  ██║    ███████╗╚██████╔╝██║ ╚████║╚██████╔╝                ██
    ██   ╚═╝  ╚═╝    ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝                 ██
    ██                                                                    ██
    ██   ██████╗  ██████╗  █████╗ ██████╗     ████████╗ ██████╗          ██
    ██   ██╔══██╗██╔═══██╗██╔══██╗██╔══██╗    ╚══██╔══╝██╔═══██╗         ██
    ██   ██████╔╝██║   ██║███████║██║  ██║       ██║   ██║   ██║         ██
    ██   ██╔══██╗██║   ██║██╔══██║██║  ██║       ██║   ██║   ██║         ██
    ██   ██║  ██║╚██████╔╝██║  ██║██████╔╝       ██║   ╚██████╔╝         ██
    ██   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝        ╚═╝    ╚═════╝          ██
    ██                                                                    ██
    ██   ███╗   ███╗ ██████╗ ███████╗ ██████╗ ██████╗ ██╗    ██╗         ██
    ██   ████╗ ████║██╔═══██╗██╔════╝██╔════╝██╔═══██╗██║    ██║         ██
    ██   ██╔████╔██║██║   ██║███████╗██║     ██║   ██║██║ █╗ ██║         ██
    ██   ██║╚██╔╝██║██║   ██║╚════██║██║     ██║   ██║██║███╗██║         ██
    ██   ██║ ╚═╝ ██║╚██████╔╝███████║╚██████╗╚██████╔╝╚███╔███╔╝         ██
    ██   ╚═╝     ╚═╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═════╝  ╚══╝╚══╝          ██
    ██                                                                    ██
    ████████████████████████████████████████████████████████████████████████{Colors.RESET}
    
    {Colors.RED}                    ☢️ FROM PARIS TO MOSCOW ☢️{Colors.RESET}
    {Colors.YELLOW}                      A Nuclear Survival Game{Colors.RESET}
        """
        return art
    
    def companion_art(self):
        art = f"""{Colors.CYAN}
    ████████████████████████████████████
    █  ╔══════════════════════════════╗ █
    █  ║         👥 COMPANIONS        ║ █
    █  ║                              ║ █
    █  ║    🧑 HUMANS    🐕 DOGS      ║ █
    █  ║                              ║ █
    █  ║   Join your survival team!   ║ █
    █  ╚══════════════════════════════╝ █
    ████████████████████████████████████{Colors.RESET}"""
        return art
    
    def disease_art(self):
        art = f"""{Colors.RED}
    ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️
    ⚠️                                 ⚠️
    ⚠️      🦠 DISEASE OUTBREAK 🦠     ⚠️
    ⚠️                                 ⚠️
    ⚠️     Someone has fallen ill!     ⚠️
    ⚠️                                 ⚠️
    ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️{Colors.RESET}"""
        return art
    
    def mushroom_cloud_art(self):
        art = f"""{Colors.RED}
                         .-""""""""""""-.
                       .'                '.
                      /                    \\
                     ;                      ;
                     |                      |
                     |        BOOM!         |
                     |                      |
                     ;                      ;
                      \\                    /
                       '.                .'
                         |              |
                         |              |
                         |     ☢️       |
                         |              |
                         |              |
                         ████████████████
                         ████████████████
                         ████████████████{Colors.RESET}"""
        return art
    
    def show_main_menu(self):
        while True:
            self.clear_screen()
            print(self.main_menu_art())
            print(self.mushroom_cloud_art())
            
            print(f"""{Colors.GREEN}
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                              MAIN MENU                               ║
    ║                                                                      ║
    ║  {Colors.BRIGHT_GREEN}1. 🚀 START NEW GAME{Colors.GREEN}                                            ║
    ║  {Colors.YELLOW}2. 📖 INSTRUCTIONS{Colors.GREEN}                                                ║
    ║  {Colors.CYAN}3. 🎭 CREDITS{Colors.GREEN}                                                     ║
    ║  {Colors.RED}4. 🚪 EXIT GAME{Colors.GREEN}                                                   ║
    ║                                                                      ║
    ╚══════════════════════════════════════════════════════════════════════╝{Colors.RESET}""")
            
            print_green("\n🌍 The nuclear bombs are falling... Europe is in chaos...")
            print_red("💥 Major cities are being destroyed one by one...")
            print_yellow("⏰ Time is running out! You must escape to Russia!")
            
            choice = input(f"\n{Colors.BRIGHT_GREEN}Enter your choice (1-4): {Colors.RESET}")
            
            if choice == "1":
                self.reset_game()
                self.play()
                break
            elif choice == "2":
                self.instructions_screen()
            elif choice == "3":
                self.show_credits()
            elif choice == "4":
                self.clear_screen()
                print_bright_green("Thanks for playing A Long Road To Moscow!")
                print_green("Stay safe in the real world! 🌍")
                sys.exit(0)
            else:
                print_red("Invalid choice! Please select 1-4.")
                time.sleep(1)
    
    def instructions_screen(self):
        self.clear_screen()
        print(f"""{Colors.BRIGHT_GREEN}
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                     A LONG ROAD TO MOSCOW - INSTRUCTIONS             ║
    ╚══════════════════════════════════════════════════════════════════════╝{Colors.RESET}
    
    {Colors.GREEN}🎯 OBJECTIVE:{Colors.RESET}
    Travel 2,500 kilometers from Paris, France to Moscow, Russia during a nuclear war.
    
    {Colors.GREEN}🎮 HOW TO PLAY:{Colors.RESET}
    • Manage resources: fuel, food, water, medical supplies, ammunition
    • Keep your party healthy and maintain morale
    • Recruit companions along the way (humans and dogs)
    • Treat diseases that can spread through your party
    • Make strategic decisions during random events
    
    {Colors.CYAN}👥 COMPANIONS:{Colors.RESET}
    • Recruit up to 6 additional companions during your journey
    • Humans have special skills: Doctors heal, Engineers repair, etc.
    • Dogs provide loyalty and can help hunt for food
    • Each companion consumes resources but provides benefits
    
    {Colors.RED}🦠 DISEASES:{Colors.RESET}
    • Party members can catch diseases like cholera, flu, COVID, plague
    • Some diseases are contagious and can spread
    • Use medical supplies or specific medicines to treat diseases
    • Untreated diseases can be fatal
    
    {Colors.YELLOW}⚠️ DANGERS:{Colors.RESET}
    • Nuclear explosions increase radiation levels
    • Raiders will attack and steal supplies
    • Vehicle breakdowns can strand you
    • Disease outbreaks can kill party members
    
    {Colors.BRIGHT_GREEN}🏆 VICTORY:{Colors.RESET}
    Reach Moscow with at least one party member alive!
        """)
        
        input(f"\n{Colors.GREEN}Press Enter to return to main menu...{Colors.RESET}")
    
    def show_credits(self):
        self.clear_screen()
        print(f"""{Colors.CYAN}
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                              CREDITS                                 ║
    ║                                                                      ║
    ║                  🎮 A LONG ROAD TO MOSCOW 🎮                        ║
    ║                                                                      ║
    ║                    Game Created by: LogolWaffle                      ║
    ║                                                                      ║
    ║                   Inspired by: The Oregon Trail                      ║
    ║                                                                      ║
    ║                      🎖️ Thank You for Playing! 🎖️                   ║
    ╚══════════════════════════════════════════════════════════════════════╝{Colors.RESET}""")
        
        input(f"\n{Colors.CYAN}Press Enter to return to main menu...{Colors.RESET}")
    
    def reset_game(self):
        """Reset all game variables for a new game"""
        self.fuel = 100
        self.food = 150
        self.water = 100
        self.medical_supplies = 50
        self.ammunition = 75
        self.radiation_medicine = 30
        self.health = 100
        self.radiation_level = 0
        self.morale = 100
        self.vehicle_condition = 100
        self.distance_traveled = 0
        self.day = 1
        self.money = 500
        self.current_location = "Paris, France"
        self.game_over = False
        self.victory = False
        self.current_location_index = 0
        
        # Reset party
        self.party = [
            {"name": "Jean", "health": 100, "status": "Good", "profession": "Engineer", "type": "human", "disease": None},
            {"name": "Marie", "health": 100, "status": "Good", "profession": "Doctor", "type": "human", "disease": None},
            {"name": "Klaus", "health": 100, "status": "Good", "profession": "Soldier", "type": "human", "disease": None},
            {"name": "Anna", "health": 100, "status": "Good", "profession": "Scientist", "type": "human", "disease": None}
        ]
    
    def recruit_companion_event(self):
        """Random event to recruit companions"""
        if len(self.party) >= self.max_companions:
            return  # Party is full
        
        # Possible companions to recruit
        human_companions = [
            {"name": "Viktor", "profession": "Mechanic", "type": "human"},
            {"name": "Elena", "profession": "Nurse", "type": "human"},
            {"name": "Boris", "profession": "Hunter", "type": "human"},
            {"name": "Katya", "profession": "Translator", "type": "human"},
            {"name": "Dmitri", "profession": "Scout", "type": "human"},
            {"name": "Olga", "profession": "Cook", "type": "human"},
            {"name": "Pavel", "profession": "Farmer", "type": "human"},
            {"name": "Svetlana", "profession": "Teacher", "type": "human"}
        ]
        
        dog_companions = [
            {"name": "Rex", "profession": "Guard Dog", "type": "dog"},
            {"name": "Bella", "profession": "Hunting Dog", "type": "dog"},
            {"name": "Max", "profession": "Loyal Dog", "type": "dog"},
            {"name": "Luna", "profession": "Scout Dog", "type": "dog"},
            {"name": "Charlie", "profession": "Companion Dog", "type": "dog"}
        ]
        
        print(self.companion_art())
        
        companion_type = random.choice(["human", "dog"])
        if companion_type == "human":
            companion = random.choice(human_companions)
            print_green(f"👤 You encounter {companion['name']}, a {companion['profession']}!")
            print_green(f"They want to join your group for safety.")
        else:
            companion = random.choice(dog_companions)
            print_green(f"🐕 You find {companion['name']}, a {companion['profession']}!")
            print_green(f"The dog seems friendly and wants to follow you.")
        
        choice = input(f"{Colors.GREEN}Recruit {companion['name']}? (y/n): {Colors.RESET}")
        
        if choice.lower() == 'y':
            new_companion = {
                "name": companion["name"],
                "health": 100,
                "status": "Good",
                "profession": companion["profession"],
                "type": companion["type"],
                "disease": None
            }
            self.party.append(new_companion)
            print_green(f"✅ {companion['name']} has joined your party!")
            self.morale += 15
            
            # Companion benefits
            if companion["type"] == "dog":
                print_green("Dogs are loyal and consume less food!")
            else:
                print_green(f"Humans with skills can help your survival!")
        else:
            print_yellow(f"You decline to recruit {companion['name']}.")
    
    def disease_outbreak_event(self):
        """Handle disease outbreaks in the party"""
        if random.random() < 0.15:  # 15% chance of disease outbreak
            print(self.disease_art())
            
            # Choose a random party member to get sick
            healthy_members = [member for member in self.party if member["health"] > 0 and member["disease"] is None]
            if not healthy_members:
                return
            
            victim = random.choice(healthy_members)
            disease = random.choice(list(self.diseases.keys()))
            
            victim["disease"] = disease
            print_red(f"🦠 {victim['name']} has contracted {disease.replace('_', ' ').title()}!")
            
            disease_info = self.diseases[disease]
            print_red(f"Severity: {disease_info['severity'].upper()}")
            
            if disease_info["contagious"]:
                print_red("⚠️ This disease is CONTAGIOUS and may spread!")
                self.spread_disease(disease)
            
            # Immediate health impact
            victim["health"] -= disease_info["daily_damage"]
            self.morale -= 20
    
    def spread_disease(self, disease):
        """Spread contagious diseases to other party members"""
        disease_info = self.diseases[disease]
        if not disease_info["contagious"]:
            return
        
        for member in self.party:
            if member["disease"] is None and member["health"] > 0:
                if random.random() < 0.3:  # 30% chance to catch contagious disease
                    member["disease"] = disease
                    print_red(f"😷 {member['name']} has also caught {disease.replace('_', ' ').title()}!")
                    member["health"] -= disease_info["daily_damage"] // 2  # Reduced initial damage
    
    def treat_diseases(self):
        """Allow player to treat diseases"""
        sick_members = [member for member in self.party if member["disease"] is not None]
        if not sick_members:
            print_green("No one in your party is currently sick.")
            return
        
        print_yellow("🏥 TREATING DISEASES:")
        for i, member in enumerate(sick_members, 1):
            disease_info = self.diseases[member["disease"]]
            cure_needed = disease_info["cure"]
            cure_amount = 20 if cure_needed == "medical_supplies" else 15
            
            print_yellow(f"{i}. {member['name']} - {member['disease'].replace('_', ' ').title()}")
            print_yellow(f"   Needs: {cure_amount} {cure_needed.replace('_', ' ')}")
        
        choice = input(f"{Colors.GREEN}Treat which patient? (1-{len(sick_members)}, or 0 to skip): {Colors.RESET}")
        
        try:
            choice = int(choice)
            if 1 <= choice <= len(sick_members):
                patient = sick_members[choice - 1]
                disease_info = self.diseases[patient["disease"]]
                cure_needed = disease_info["cure"]
                cure_amount = 20 if cure_needed == "medical_supplies" else 15
                
                current_supply = getattr(self, cure_needed)
                if current_supply >= cure_amount:
                    setattr(self, cure_needed, current_supply - cure_amount)
                    patient["disease"] = None
                    patient["health"] += 30
                    if patient["health"] > 100:
                        patient["health"] = 100
                    print_green(f"✅ {patient['name']} has been successfully treated!")
                    self.morale += 10
                else:
                    print_red(f"❌ Not enough {cure_needed.replace('_', ' ')}!")
            elif choice == 0:
                print_yellow("No treatment administered.")
        except ValueError:
            print_red("Invalid choice.")
    
    def daily_disease_effects(self):
        """Apply daily effects of diseases"""
        for member in self.party:
            if member["disease"] is not None and member["health"] > 0:
                disease_info = self.diseases[member["disease"]]
                damage = disease_info["daily_damage"]
                
                # Marie (doctor) takes less damage from diseases
                if member["name"] == "Marie":
                    damage = int(damage * 0.7)
                
                member["health"] -= damage
                
                if member["health"] <= 0:
                    print_red(f"💀 {member['name']} has died from {member['disease'].replace('_', ' ')}!")
                    member["health"] = 0
                    self.morale -= 30
    
    def companion_benefits(self):
        """Apply benefits from companions"""
        for member in self.party:
            if member["health"] <= 0:
                continue
                
            # Doctor heals party members
            if member["profession"] == "Doctor" and member["health"] > 50:
                for patient in self.party:
                    if patient["health"] > 0 and patient["health"] < 100:
                        patient["health"] += 5
                        if patient["health"] > 100:
                            patient["health"] = 100
            
            # Mechanic maintains vehicle
            elif member["profession"] in ["Engineer", "Mechanic"] and member["health"] > 50:
                self.vehicle_condition += 3
                if self.vehicle_condition > 100:
                    self.vehicle_condition = 100
            
            # Hunter/Scout finds extra food
            elif member["profession"] in ["Hunter", "Scout", "Hunting Dog"] and member["health"] > 50:
                if random.random() < 0.3:
                    self.food += random.randint(5, 15)
            
            # Cook reduces food consumption
            elif member["profession"] == "Cook" and member["health"] > 50:
                # This is handled in daily_consumption
                pass
            
            # Guard Dog protects against raids
            elif member["profession"] == "Guard Dog" and member["health"] > 50:
                # This is handled in raider events
                pass
    
    def daily_consumption(self):
        # Count living party members
        living_humans = len([m for m in self.party if m["health"] > 0 and m["type"] == "human"])
        living_dogs = len([m for m in self.party if m["health"] > 0 and m["type"] == "dog"])
        
        # Dogs consume less food
        food_consumption = living_humans * random.randint(3, 8) + living_dogs * random.randint(1, 3)
        water_consumption = living_humans * random.randint(2, 5) + living_dogs * random.randint(1, 2)
        
        # Cook reduces consumption
        if any(m["profession"] == "Cook" and m["health"] > 50 for m in self.party):
            food_consumption = int(food_consumption * 0.8)
            print_green("🍳 The cook helps reduce food consumption!")
        
        self.food -= food_consumption
        self.water -= water_consumption
        
        # Vehicle deterioration
        self.vehicle_condition -= random.randint(1, 3)
        
        # Apply disease effects
        self.daily_disease_effects()
        
        # Apply companion benefits
        self.companion_benefits()
        
        # Check for starvation/dehydration
        if self.food <= 0:
            print_red("⚠️ Your party is starving!")
            self.health -= 15
            self.morale -= 20
            for member in self.party:
                if member["health"] > 0:
                    member["health"] -= random.randint(10, 20)
        
        if self.water <= 0:
            print_red("⚠️ Your party is dehydrating!")
            self.health -= 20
            self.morale -= 25
            for member in self.party:
                if member["health"] > 0:
                    member["health"] -= random.randint(15, 25)
        
        # Radiation effects
        if self.radiation_level > 50:
            print_red("☢️ Radiation sickness is affecting your party!")
            self.health -= random.randint(5, 15)
            for member in self.party:
                if member["health"] > 0:
                    member["health"] -= random.randint(3, 10)
                    # High radiation can cause radiation sickness
                    if self.radiation_level > 80 and random.random() < 0.2:
                        if member["disease"] is None:
                            member["disease"] = "radiation_sickness"
                            print_red(f"☢️ {member['name']} developed radiation sickness!")
    
    def display_status(self):
        print_bright_green("=" * 80)
        print_green(f"DAY {self.day} | LOCATION: {self.current_location}")
        print_green(f"DISTANCE: {self.distance_traveled}/{self.total_distance} km")
        print_bright_green("=" * 80)
        
        # Resources
        print_green("RESOURCES:")
        fuel_color = Colors.RED if self.fuel < 20 else Colors.YELLOW if self.fuel < 50 else Colors.GREEN
        food_color = Colors.RED if self.food < 30 else Colors.YELLOW if self.food < 60 else Colors.GREEN
        water_color = Colors.RED if self.water < 20 else Colors.YELLOW if self.water < 40 else Colors.GREEN
        
        print(f"  {fuel_color}⛽ Fuel: {self.fuel}{Colors.RESET} | "
              f"{food_color}🍞 Food: {self.food}{Colors.RESET} | "
              f"{water_color}💧 Water: {self.water}{Colors.RESET}")
        print_green(f"  💊 Medical: {self.medical_supplies} | ☢️ Rad-Med: {self.radiation_medicine} | 🔫 Ammo: {self.ammunition}")
        print_green(f"  💰 Money: {self.money} | 🚗 Vehicle: {self.vehicle_condition}%")
        
        # Player condition
        health_color = Colors.RED if self.health < 30 else Colors.YELLOW if self.health < 60 else Colors.GREEN
        radiation_color = Colors.RED if self.radiation_level > 70 else Colors.YELLOW if self.radiation_level > 40 else Colors.GREEN
        morale_color = Colors.RED if self.morale < 30 else Colors.YELLOW if self.morale < 60 else Colors.GREEN
        
        print_green("CONDITION:")
        print(f"  {health_color}❤️ Health: {self.health}%{Colors.RESET} | "
              f"{radiation_color}☢️ Radiation: {self.radiation_level}%{Colors.RESET} | "
              f"{morale_color}😊 Morale: {self.morale}%{Colors.RESET}")
        
        # Party status
        print_green(f"PARTY ({len([m for m in self.party if m['health'] > 0])}/{len(self.party)} alive):")
        for member in self.party:
            status_color = Colors.GREEN if member["status"] == "Good" else Colors.YELLOW if member["status"] == "Fair" else Colors.RED
            type_icon = "👤" if member["type"] == "human" else "🐕"
            disease_text = f" ({member['disease'].replace('_', ' ')})" if member["disease"] else ""
            print(f"  {status_color}{type_icon} {member['name']} ({member['profession']}): {member['status']} - {member['health']}%{disease_text}{Colors.RESET}")
        
        print_bright_green("=" * 80)
    
    def travel_options(self):
        print_green("\nTRAVEL OPTIONS:")
        print_green("1. Continue at steady pace (Normal fuel consumption)")
        print_green("2. Travel fast (High fuel consumption, more distance)")
        print_green("3. Travel carefully (Low fuel consumption, less distance)")
        print_green("4. Rest for the day")
        print_green("5. Hunt/Forage for food")
        print_green("6. Trade with locals")
        print_green("7. Treat diseases")
        print_green("8. Check party status")
        print_green("9. Return to main menu")
        
        choice = input(f"{Colors.GREEN}What would you like to do? {Colors.RESET}")
        return choice
    
    def travel(self, speed):
        if speed == "fast":
            distance = random.randint(120, 180)
            fuel_cost = random.randint(25, 35)
            print_green(f"🚗 Traveling fast... covered {distance} km")
        elif speed == "careful":
            distance = random.randint(60, 100)
            fuel_cost = random.randint(10, 18)
            print_green(f"🚗 Traveling carefully... covered {distance} km")
        else:  # normal
            distance = random.randint(80, 140)
            fuel_cost = random.randint(15, 25)
            print_green(f"🚗 Traveling at steady pace... covered {distance} km")
        
        # Scout reduces fuel consumption
        if any(m["profession"] == "Scout" and m["health"] > 50 for m in self.party):
            fuel_cost = int(fuel_cost * 0.9)
            print_green("🗺️ The scout finds a more efficient route!")
        
        self.distance_traveled += distance
        self.fuel -= fuel_cost
        self.day += 1
        
        # Update location
        self.update_location()
        
        # Daily effects
        self.daily_consumption()
        
        # Update party status
        self.update_party_status()
    
    def update_location(self):
        for i, location in enumerate(self.locations):
            if self.distance_traveled >= location["distance"] and i > self.current_location_index:
                self.current_location = location["name"]
                self.current_location_index = i
                print_bright_green(f"🏁 Reached {location['name']}!")
                
                if location["name"] == "Moscow, Russia":
                    self.victory = True
                    return
                
                # Safe locations offer benefits
                if location["safe"]:
                    print_green("This is a safe zone! You can rest and recover here.")
                    self.morale += 20
                    self.radiation_level = max(0, self.radiation_level - 10)
                
                time.sleep(2)
                break
    
    def update_party_status(self):
        for member in self.party:
            if member["health"] > 75:
                member["status"] = "Good"
            elif member["health"] > 50:
                member["status"] = "Fair"
            elif member["health"] > 25:
                member["status"] = "Poor"
            elif member["health"] > 0:
                member["status"] = "Critical"
            else:
                member["status"] = "Dead"
    
    def random_event(self):
        events = [
            self.nuclear_strike_event,
            self.raiders_event,
            self.mechanical_breakdown,
            self.find_supplies,
            self.radiation_storm,
            self.refugee_encounter,
            self.military_checkpoint,
            self.abandoned_city_event,
            self.fuel_shortage_event,
            self.recruit_companion_event,
            self.disease_outbreak_event
        ]
        
        if random.random() < 0.6:  # 60% chance of random event
            event = random.choice(events)
            event()
    
    def nuclear_strike_event(self):
        explosion_art = f"{Colors.RED}\n" + \
            "                    .-==============-.\n" + \
            "                  .'                  '.\n" + \
            "                 /   BLAST    BLAST   \\\\\n" + \
            "                :           `          :\n" + \
            "                |                      |\n" + \
            "                :    .------.          :\n" + \
            "                 \\\\  '        '        /\n" + \
            "                  '.                .'\n" + \
            "                    '-...........-'\n" + \
            "                      BOOM!\n" + \
            f"        ☢️  NUCLEAR EXPLOSION  ☢️{Colors.RESET}"
        print(explosion_art)
        print_red("💥 NUCLEAR STRIKE NEARBY!")
        print_red("The ground shakes as a mushroom cloud rises in the distance.")
        
        self.radiation_level += random.randint(15, 30)
        self.morale -= 25
        
        choice = input(f"{Colors.GREEN}Do you: 1) Take shelter immediately 2) Keep moving 3) Turn back? {Colors.RESET}")
        
        if choice == "1":
            print_green("You take shelter in a nearby building.")
            self.fuel -= 0  # No fuel used
            time.sleep(2)
        elif choice == "2":
            print_yellow("You push through the danger zone.")
            self.radiation_level += 20
            self.fuel -= 15
        else:
            print_yellow("You retreat to avoid the worst of the radiation.")
            self.distance_traveled -= 50
    
    def raiders_event(self):
        print_red("🔫 HOSTILE RAIDERS SPOTTED!")
        print_red("Armed bandits are blocking the road ahead!")
        
        # Guard dogs help in combat
        has_guard_dog = any(m["profession"] == "Guard Dog" and m["health"] > 50 for m in self.party)
        if has_guard_dog:
            print_green("🐕 Your guard dog growls menacingly at the raiders!")
        
        choice = input(f"{Colors.GREEN}Do you: 1) Fight them 2) Try to negotiate 3) Take a detour? {Colors.RESET}")
        
        if choice == "1":
            combat_bonus = 20 if has_guard_dog else 0
            ammo_needed = max(10, 20 - combat_bonus)
            
            if self.ammunition >= ammo_needed:
                print_green("🔫 You fight off the raiders!")
                self.ammunition -= ammo_needed
                # Chance to find supplies
                if random.random() < 0.6:
                    loot = random.choice(["fuel", "food", "medical_supplies"])
                    amount = random.randint(10, 25)
                    setattr(self, loot, getattr(self, loot) + amount)
                    print_green(f"You found {amount} {loot} from the raiders!")
            else:
                print_red("Not enough ammunition! The raiders overwhelm you.")
                self.health -= 30
                self.lose_random_supplies()
        
        elif choice == "2":
            if self.money >= 100:
                print_yellow("You pay the raiders to let you pass.")
                self.money -= 100
            else:
                print_red("You don't have enough money! They attack!")
                self.health -= 20
                self.lose_random_supplies()
        
        else:
            print_yellow("You take a longer route around the raiders.")
            self.fuel -= 20
            self.distance_traveled -= 30
    
    def mechanical_breakdown(self):
        print_yellow("🔧 VEHICLE BREAKDOWN!")
        breakdown_types = ["engine", "tires", "radiator", "transmission"]
        breakdown = random.choice(breakdown_types)
        
        print_yellow(f"Your vehicle's {breakdown} has failed!")
        
        repair_time = random.randint(1, 3)
        print_yellow(f"Repairs will take {repair_time} days.")
        
        # Engineer/Mechanic helps with repairs
        if any(m["profession"] in ["Engineer", "Mechanic"] and m["health"] > 50 for m in self.party):
            print_green("Your mechanic's skills help with the repairs!")
            repair_time = max(1, repair_time - 1)
        
        self.day += repair_time
        self.vehicle_condition -= 20
        
        # Use supplies for repair
        if self.medical_supplies >= 10:
            choice = input(f"{Colors.GREEN}Use medical supplies for makeshift repairs? (y/n): {Colors.RESET}")
            if choice.lower() == 'y':
                self.medical_supplies -= 10
                self.vehicle_condition += 15
                print_green("Makeshift repairs completed!")
    
    def find_supplies(self):
        supply_types = ["fuel", "food", "water", "medical_supplies", "ammunition"]
        found_supply = random.choice(supply_types)
        amount = random.randint(15, 40)
        
        print_bright_green(f"🎒 FOUND SUPPLIES!")
        print_green(f"You discovered {amount} {found_supply.replace('_', ' ')}!")
        
        setattr(self, found_supply, getattr(self, found_supply) + amount)
        self.morale += 10
    
    def radiation_storm(self):
        print(f"""{Colors.YELLOW}
        ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️
        ⚠️                   ⚠️
        ⚠️  ☢️ RADIATION ☢️  ⚠️
        ⚠️    STORM        ⚠️
        ⚠️                   ⚠️
        ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️{Colors.RESET}""")
        print_red("☢️ RADIOACTIVE STORM APPROACHING!")
        
        choice = input(f"{Colors.GREEN}Do you: 1) Take shelter 2) Push through 3) Use rad medicine? {Colors.RESET}")
        
        if choice == "1":
            print_green("You wait out the storm in shelter.")
            self.day += 1
            self.radiation_level += 5
        elif choice == "2":
            print_red("You drive through the radioactive storm!")
            self.radiation_level += random.randint(25, 40)
            self.health -= 15
        else:
            if self.radiation_medicine >= 15:
                print_green("Radiation medicine protects your party!")
                self.radiation_medicine -= 15
                self.radiation_level += 5
            else:
                print_red("Not enough radiation medicine!")
                self.radiation_level += 20
    
    def refugee_encounter(self):
        print_green("👥 You encounter a group of refugees.")
        print_green("They look hungry and desperate.")
        
        choice = input(f"{Colors.GREEN}Do you: 1) Share food 2) Ignore them 3) Ask for information? {Colors.RESET}")
        
        if choice == "1":
            if self.food >= 20:
                print_green("You share food with the refugees.")
                self.food -= 20
                self.morale += 15
                # They might give you information
                if random.random() < 0.5:
                    print_green("In gratitude, they tell you about a safe route ahead!")
                    self.fuel += 10  # More efficient route
            else:
                print_yellow("You don't have enough food to share.")
        elif choice == "3":
            print_green("The refugees warn you about radiation zones ahead.")
            self.morale += 5
    
    def military_checkpoint(self):
        print_blue("🪖 MILITARY CHECKPOINT")
        print_blue("Soldiers stop your vehicle for inspection.")
        
        # Translator helps with communication
        has_translator = any(m["profession"] == "Translator" and m["health"] > 50 for m in self.party)
        
        if random.random() < (0.2 if has_translator else 0.3):  # Lower chance of problems with translator
            print_red("The soldiers are suspicious of your group!")
            choice = input(f"{Colors.GREEN}Do you: 1) Bribe them 2) Show your papers 3) Try to run? {Colors.RESET}")
            
            if choice == "1":
                bribe_amount = 100 if has_translator else 150
                if self.money >= bribe_amount:
                    print_green("The bribe works. You're allowed to pass.")
                    self.money -= bribe_amount
                else:
                    print_red("Not enough money! You're detained briefly.")
                    self.day += 1
            elif choice == "3":
                print_red("You try to escape but they shoot out your tires!")
                self.vehicle_condition -= 30
                self.health -= 10
        else:
            print_green("The soldiers let you pass without incident.")
            if has_translator:
                print_green("Your translator helps smooth the interaction!")
    
    def abandoned_city_event(self):
        print(f"""{Colors.CYAN}
    ████████████████████████████████
    █  ╔═╗  ╔═╗  ╔═╗  ╔═╗  ╔═╗  █
    █  ║ ║  ║ ║  ║ ║  ║ ║  ║ ║  █
    █  ╚═╝  ╚═╝  ╚═╝  ╚═╝  ╚═╝  █
    █                            █
    █  ╔═╗  ╔═╗  ╔═╗  ╔═╗  ╔═╗  █
    █  ║ ║  ║ ║  ║ ║  ║ ║  ║ ║  █
    █  ╚═╝  ╚═╝  ╚═╝  ╚═╝  ╚═╝  █
    ████████████████████████████████
            🏚️ ABANDONED CITY{Colors.RESET}""")
        print_yellow("🏚️ You come across an abandoned city.")
        print_yellow("It looks dangerous but might contain supplies.")
        
        choice = input(f"{Colors.GREEN}Do you: 1) Search for supplies 2) Go around 3) Rest here? {Colors.RESET}")
        
        if choice == "1":
            print_yellow("You search the abandoned buildings...")
            if random.random() < 0.6:
                supplies = ["fuel", "food", "medical_supplies", "ammunition"]
                found = random.choice(supplies)
                amount = random.randint(20, 50)
                setattr(self, found, getattr(self, found) + amount)
                print_green(f"Found {amount} {found.replace('_', ' ')}!")
            else:
                print_red("The city is too dangerous! You barely escape.")
                self.health -= 15
                self.radiation_level += 10
        elif choice == "2":
            print_green("You take the safer route around the city.")
            self.fuel -= 15
        else:
            print_yellow("You rest in the abandoned city.")
            self.health += 20
            self.radiation_level += 15  # Dangerous to stay
    
    def fuel_shortage_event(self):
        print_red("⛽ FUEL SHORTAGE!")
        print_red("You're running dangerously low on fuel.")
        
        if self.money >= 200:
            choice = input(f"{Colors.GREEN}Do you: 1) Buy fuel from smugglers 2) Siphon from abandoned vehicles? {Colors.RESET}")
            
            if choice == "1":
                print_yellow("You buy expensive fuel from smugglers.")
                self.money -= 200
                self.fuel += 50
            else:
                print_yellow("You siphon fuel from abandoned vehicles.")
                self.fuel += random.randint(15, 35)
        else:
            print_red("You have no choice but to siphon fuel from wrecks.")
            self.fuel += random.randint(10, 25)
    
    def lose_random_supplies(self):
        supplies = ["fuel", "food", "water", "medical_supplies", "ammunition"]
        lost_supply = random.choice(supplies)
        amount = random.randint(10, 30)
        current_amount = getattr(self, lost_supply)
        setattr(self, lost_supply, max(0, current_amount - amount))
        print_red(f"You lost {amount} {lost_supply.replace('_', ' ')}!")
    
    def rest(self):
        print_green("🏕️ Your party rests for the day.")
        self.health += random.randint(10, 20)
        self.morale += random.randint(5, 15)
        
        # Party members recover
        for member in self.party:
            if member["health"] > 0:
                member["health"] += random.randint(5, 15)
                if member["health"] > 100:
                    member["health"] = 100
        
        self.day += 1
        self.daily_consumption()
        self.update_party_status()
    
    def hunt_forage(self):
        print_green("🏹 Hunting and foraging for food...")
        
        success_chance = 0.6
        # Hunter or hunting dog increases success
        if any(m["profession"] in ["Hunter", "Hunting Dog"] and m["health"] > 50 for m in self.party):
            success_chance = 0.8
            print_green("Your hunter/hunting dog helps track game!")
        
        if random.random() < success_chance:
            food_found = random.randint(20, 40)
            self.food += food_found
            print_green(f"Successfully gathered {food_found} food!")
            self.morale += 10
        else:
            print_red("Hunting was unsuccessful. You found nothing.")
            self.morale -= 5
        
        # Use ammunition if hunting
        if self.ammunition > 0:
            self.ammunition -= random.randint(1, 5)
        
        self.day += 1
        self.daily_consumption()
        self.update_party_status()
    
    def trade(self):
        print_green("💰 Trading with locals...")
        
        if self.money < 50:
            print_red("You don't have enough money to trade!")
            return
        
        print_green("Available trades:")
        trades = [
            {"item": "Food", "cost": 50, "amount": 30, "resource": "food"},
            {"item": "Fuel", "cost": 100, "amount": 25, "resource": "fuel"},
            {"item": "Medical Supplies", "cost": 80, "amount": 20, "resource": "medical_supplies"},
            {"item": "Ammunition", "cost": 120, "amount": 30, "resource": "ammunition"},
            {"item": "Radiation Medicine", "cost": 150, "amount": 15, "resource": "radiation_medicine"}
        ]
        
        for i, trade in enumerate(trades, 1):
            print_green(f"{i}. {trade['item']} - {trade['amount']} units for {trade['cost']} money")
        
        choice = input(f"{Colors.GREEN}What would you like to buy? (1-5, or 0 to cancel): {Colors.RESET}")
        
        try:
            choice = int(choice)
            if 1 <= choice <= 5:
                trade = trades[choice - 1]
                if self.money >= trade["cost"]:
                    self.money -= trade["cost"]
                    current_amount = getattr(self, trade["resource"])
                    setattr(self, trade["resource"], current_amount + trade["amount"])
                    print_green(f"Purchased {trade['amount']} {trade['item']}!")
                else:
                    print_red("Not enough money!")
        except ValueError:
            print_yellow("Invalid choice.")
    
    def check_party_status(self):
        self.update_party_status()
        print_green("\n👥 DETAILED PARTY STATUS:")
        for member in self.party:
            status_color = Colors.GREEN if member["status"] == "Good" else Colors.YELLOW if member["status"] in ["Fair", "Poor"] else Colors.RED
            type_icon = "👤" if member["type"] == "human" else "🐕"
            disease_text = f" - SICK: {member['disease'].replace('_', ' ').title()}" if member["disease"] else ""
            print(f"  {status_color}{type_icon} {member['name']} ({member['profession']}){Colors.RESET}")
            print(f"     Status: {member['status']} | Health: {member['health']}%{disease_text}")
    
    def check_game_over(self):
        # Check if player died
        if self.health <= 0:
            print_red("💀 You have died from your injuries and radiation exposure.")
            self.game_over = True
            return
        
        # Check if all party members died
        if all(member["health"] <= 0 for member in self.party):
            print_red("💀 Your entire party has perished. You cannot continue alone.")
            self.game_over = True
            return
        
        # Check if out of fuel
        if self.fuel <= 0 and self.distance_traveled < self.total_distance:
            print_red("⛽ You've run out of fuel and are stranded!")
            if self.money >= 200:
                print_yellow("You can buy emergency fuel for 200 money.")
                choice = input(f"{Colors.GREEN}Buy emergency fuel? (y/n): {Colors.RESET}")
                if choice.lower() == 'y':
                    self.money -= 200
                    self.fuel += 30
                    print_green("Emergency fuel purchased!")
                else:
                    self.game_over = True
            else:
                self.game_over = True
        
        # Check if reached Moscow
        if self.distance_traveled >= self.total_distance:
            self.victory = True
    
    def game_intro(self):
        self.clear_screen()
        print_bright_green("=" * 80)
        print_bright_green("                🎮 A LONG ROAD TO MOSCOW 🎮")
        print_bright_green("                   FROM PARIS TO MOSCOW")
        print_bright_green("=" * 80)
        
        print_green("\n🌍 The year is 2024. Nuclear war has begun.")
        print_green("💥 Major cities across Europe are being destroyed.")
        print_green("🚗 You must escape from Paris to the safety of Moscow.")
        print_green("⚠️  The journey is 2,500 kilometers through a nuclear wasteland.")
        
        print_yellow("\n📋 SURVIVAL RULES:")
        print_yellow("• Manage your fuel, food, water, and medical supplies")
        print_yellow("• Avoid radiation and treat exposure quickly")
        print_yellow("• Keep your party healthy and morale high")
        print_yellow("• Recruit companions to help your survival")
        print_yellow("• Treat diseases before they spread and kill")
        print_yellow("• Reach Moscow before your resources run out")
        
        print(f"""{Colors.GREEN}
    ██████████████████████████
    █  ╔══════════════════╗  █
    █  ║  ARMORED VEHICLE ║  █  
    █  ╚══════════════════╝  █
    ████  ████████  ████████
      ████      ████    ████
        ████████    ████████
            ████████████
    🚗 YOUR SURVIVAL VEHICLE 🚗{Colors.RESET}""")
        
        print_green("\nYour starting party:")
        for member in self.party:
            type_icon = "👤" if member["type"] == "human" else "🐕"
            print_green(f"• {type_icon} {member['name']} - {member['profession']}")
        
        input(f"\n{Colors.BRIGHT_GREEN}Press Enter to begin your journey...{Colors.RESET}")
    
    def victory_screen(self):
        self.clear_screen()
        print(f"""{Colors.BRIGHT_GREEN}
    ████████████████████████████████████████
    █  ╔══════════════════════════════════╗ █
    █  ║                                  ║ █
    █  ║         RED SQUARE               ║ █
    █  ║                                  ║ █
    █  ║    ⭐ KREMLIN ⭐                ║ █
    █  ║                                  ║ █
    █  ║      🇷🇺 MOSCOW 🇷🇺            ║ █
    █  ║                                  ║ █
    █  ╚══════════════════════════════════╝ █
    ████████████████████████████████████████
               🎉 VICTORY! 🎉{Colors.RESET}""")
        
        print_bright_green("\n🎉 CONGRATULATIONS! 🎉")
        print_bright_green("You have successfully reached Moscow!")
        print_green(f"\nJourney Statistics:")
        print_green(f"• Days traveled: {self.day}")
        print_green(f"• Distance covered: {self.distance_traveled} km")
        print_green(f"• Final health: {self.health}%")
        print_green(f"• Radiation level: {self.radiation_level}%")
        print_green(f"• Party survivors: {len([m for m in self.party if m['health'] > 0])}/{len(self.party)}")
        print_green(f"• Money remaining: {self.money}")
        
        survivors = len([m for m in self.party if m['health'] > 0])
        score = (self.health + self.morale + (100 - self.radiation_level) + 
                survivors * 25 + max(0, 100 - self.day))
        
        print_bright_green(f"\n⭐ FINAL SCORE: {score}/500 ⭐")
        
        if score >= 400:
            print_bright_green("🏆 LEGENDARY SURVIVOR!")
        elif score >= 300:
            print_green("🥇 EXCELLENT SURVIVAL!")
        elif score >= 200:
            print_yellow("🥈 GOOD SURVIVAL!")
        else:
            print_red("🥉 YOU BARELY MADE IT!")
        
        choice = input(f"\n{Colors.GREEN}Play again? (y/n): {Colors.RESET}")
        if choice.lower() == 'y':
            self.show_main_menu()
    
    def game_over_screen(self):
        self.clear_screen()
        print_red("=" * 80)
        print_red("                        💀 GAME OVER 💀")
        print_red("=" * 80)
        
        print_red(f"\nYou survived {self.day} days and traveled {self.distance_traveled} km")
        print_red(f"You were {self.total_distance - self.distance_traveled} km from safety.")
        
        print_yellow("\n🎯 Better luck next time, survivor.")
        print_yellow("The nuclear wasteland has claimed another victim...")
        
        choice = input(f"\n{Colors.GREEN}Play again? (y/n): {Colors.RESET}")
        if choice.lower() == 'y':
            self.show_main_menu()
    
    def play(self):
        self.game_intro()
        
        while not self.game_over and not self.victory:
            self.clear_screen()
            
            # Show map
            progress = int((self.distance_traveled / self.total_distance) * 50)
            trail = "=" * progress + "🚗" + "-" * (50 - progress)
            print(f"""{Colors.GREEN}
    A LONG ROAD TO MOSCOW - PARIS TO MOSCOW
    
    FRANCE ═══════════════════════════════ RUSSIA
    {trail}
    
    Progress: {self.distance_traveled}/{self.total_distance} km
    Current Location: {self.current_location}{Colors.RESET}""")
            
            self.display_status()
            
            # Random events
            self.random_event()
            
            # Player choices
            choice = self.travel_options()
            
            if choice == "1":
                if self.fuel >= 15:
                    self.travel("normal")
                else:
                    print_red("Not enough fuel!")
                    time.sleep(1)
            elif choice == "2":
                if self.fuel >= 25:
                    self.travel("fast")
                else:
                    print_red("Not enough fuel!")
                    time.sleep(1)
            elif choice == "3":
                if self.fuel >= 10:
                    self.travel("careful")
                else:
                    print_red("Not enough fuel!")
                    time.sleep(1)
            elif choice == "4":
                self.rest()
            elif choice == "5":
                self.hunt_forage()
            elif choice == "6":
                self.trade()
            elif choice == "7":
                self.treat_diseases()
                input(f"{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
            elif choice == "8":
                self.check_party_status()
                input(f"{Colors.GREEN}Press Enter to continue...{Colors.RESET}")
            elif choice == "9":
                self.show_main_menu()
                return
            else:
                print_yellow("Invalid choice. Time passes...")
                self.day += 1
                self.daily_consumption()
                self.update_party_status()
            
            # Check game end conditions
            self.check_game_over()
            
            time.sleep(1)
        
        if self.victory:
            self.victory_screen()
        else:
            self.game_over_screen()

def main():
    try:
        game = LongRoadToMoscow()
        game.show_main_menu()
    except KeyboardInterrupt:
        print_red("\n\nGame interrupted by user. Stay safe!")
    except Exception as e:
        print_red(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
