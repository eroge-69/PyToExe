import random
import sys

# --- Constants ---

LANGUAGES = {
    '1': 'English',
    '2': 'Turkish'
}

SHIP_TYPES = {
    '1': {
        'name': 'Voyager III',
        'type': 'Trading Vessel',
        'bonus': '+1 reputation per 500 Solaris spent',
        'penalty': 'Marine wages are doubled',
    },
    '2': {
        'name': 'Drillmaster',
        'type': 'Mining Vessel',
        'bonus': 'Salvage missions give 50% more Solaris',
        'penalty': 'Crew loyalty decreases by 1 per normal wage payment',
    },
    '3': {
        'name': 'Devastator',
        'type': 'Combat Vessel',
        'bonus': 'Marines get +5% health and damage in combat',
        'penalty': '50% chance trading offers fail; factions may refuse trade',
    },
    '4': {
        'name': 'Ranger 101',
        'type': 'Recon Vessel',
        'bonus': 'One extra mission offered each turn',
        'penalty': 'Fuel and food capacity reduced by 40%',
    }
}

CREW_CATEGORIES = {
    'Marines': {'count': 6, 'wage': 80},
    'Engineers': {'count': 8, 'wage': 70},
    'Scientists': {'count': 4, 'wage': 60},
    'Pilots': {'count': 4, 'wage': 60},
    'Medical': {'count': 3, 'wage': 50},
}

MISSION_TYPES = {
    'Recon': {'combat_chance': 0.20, 'reward_range': (150, 250), 'rep_gain': 3},
    'Salvage': {'combat_chance': 0.40, 'reward_range': (200, 300), 'rep_gain': 0},
    'Cargo Transfer': {'combat_chance': 0.25, 'reward_range': (150, 300), 'rep_gain': 0},
    'Escort': {'combat_chance': 0.75, 'reward_range': (300, 400), 'rep_gain': 0},
    'Diplomatic': {'combat_chance': 0.05, 'reward_range': (200, 300), 'rep_gain': 10},
    'Invasion': {'combat_chance': 1.00, 'reward_range': (350, 450), 'rep_gain': 0},
}

DIFFICULTY_MODIFIERS = {
    'Easy': {'reward_mod': 0.75, 'marine_bonus': 1.3, 'enemy_bonus': 1.0},
    'Medium': {'reward_mod': 1.0, 'marine_bonus': 1.1, 'enemy_bonus': 1.0},
    'Hard': {'reward_mod': 1.25, 'marine_bonus': 1.0, 'enemy_bonus': 1.1},
    'Legendary': {'reward_mod': 1.5, 'marine_bonus': 1.0, 'enemy_bonus': 1.25},
}

STARTING_SOLARIS = 2500
STARTING_FUEL = 100
STARTING_FOOD = 100
STARTING_REPUTATION = 50
STARTING_LOYALTY = 70

# --- Classes and Game Logic ---

class Game:
    def __init__(self):
        self.language = None
        self.ship_choice = None
        self.ship = None
        self.solaris = STARTING_SOLARIS
        self.fuel = STARTING_FUEL
        self.food = STARTING_FOOD
        self.reputation = STARTING_REPUTATION
        self.crew_loyalty = STARTING_LOYALTY
        self.crew_skipped_wage_turns = 0
        self.crew_skipped_wage_total = 0
        self.wages_paid_consecutive = 0
        self.turn = 0
        self.haldun_recruited = False
        self.haldun_loyalty_bonus_active = False
        self.mission_types = list(MISSION_TYPES.keys())
        self.mission_offer_count = 2
        self.unique_items = []
        self.game_over = False

        # Setup crew wage totals
        self.crew_counts = {k: v['count'] for k, v in CREW_CATEGORIES.items()}
        self.crew_wages = {k: v['wage'] for k, v in CREW_CATEGORIES.items()}

    def start(self):
        self.select_language()
        self.show_intro()
        self.select_ship()
        self.adjust_starting_resources()
        self.main_loop()

    def select_language(self):
        while True:
            print("Select language / Dil seçiniz:")
            print("1. English")
            print("2. Türkçe")
            choice = input("> ").strip()
            if choice in LANGUAGES:
                self.language = LANGUAGES[choice]
                print(f"Language set to {self.language}\n")
                break
            else:
                print("Invalid choice, try again.")

    def show_intro(self):
        # Brief intro without ship name per rules
        if self.language == 'English':
            print("You are a commander in the RMA Federation Fleet.")
            print("Your task is to explore unknown sectors, protect Federation interests,")
            print("and balance diplomacy and combat in a fragile galaxy.")
            print("Mysterious entities and hostile forces threaten peace.")
            print("Trust your crew, manage resources wisely, and prepare for unknown dangers.\n")
        else:
            print("RMA Federasyon Filosu'nda bir komutansınız.")
            print("Göreviniz bilinmeyen bölgeleri keşfetmek, Federasyon çıkarlarını korumak,")
            print("ve diplomasi ile savaşı dengelemektir.")
            print("Gizemli varlıklar ve düşman güçler barışı tehdit ediyor.")
            print("Mürettebatınıza güvenin, kaynakları iyi yönetin ve bilinmezlere hazırlanın.\n")

    def select_ship(self):
        print("Select your ship type / Gemi tipinizi seçiniz:\n")
        for key, ship in SHIP_TYPES.items():
            print(f"{key}. {ship['type']} ({ship['name']})")
            print(f"   Bonus: {ship['bonus']}")
            print(f"   Penalty: {ship['penalty']}\n")
        while True:
            choice = input("> ").strip()
            if choice in SHIP_TYPES:
                self.ship_choice = choice
                self.ship = SHIP_TYPES[choice]
                print(f"You selected: {self.ship['type']} ({self.ship['name']})\n")
                break
            else:
                print("Invalid choice, try again.")

    def adjust_starting_resources(self):
        # Adjust fuel and food for recon penalty
        if self.ship_choice == '4':  # Recon Vessel
            self.fuel = int(self.fuel * 0.6)
            self.food = int(self.food * 0.6)

    def total_crew_wages(self):
        total = 0
        for ctype, count in self.crew_counts.items():
            wage = self.crew_wages[ctype]
            if ctype == 'Marines' and self.ship_choice == '1':  # Trading Vessel penalty: double marine wages
                wage *= 2
            total += wage * count
        return total

    def pay_crew_wages(self):
        total_wages = self.total_crew_wages()
        print(f"Crew wages due: {total_wages} Solaris.")
        print("Choose payment option:")
        print("1. Standard Wages")
        print("2. 50% Extra Wages (+5 loyalty)")
        print("3. Skip Payment (-5 loyalty, mutiny risk)")
        while True:
            choice = input("> ").strip()
            if choice == '1':
                if self.solaris >= total_wages:
                    self.solaris -= total_wages
                    self.crew_skipped_wage_turns = 0
                    self.crew_skipped_wage_total = 0
                    print(f"Paid standard wages: {total_wages} Solaris.")
                    return 0  # no loyalty change
                else:
                    print("Not enough Solaris! Choose another option.")
            elif choice == '2':
                extra_wages = int(total_wages * 1.5)
                if self.solaris >= extra_wages:
                    self.solaris -= extra_wages
                    self.crew_skipped_wage_turns = 0
                    self.crew_skipped_wage_total = 0
                    print(f"Paid extra wages: {extra_wages} Solaris. Loyalty +5.")
                    return +5
                else:
                    print("Not enough Solaris! Choose another option.")
            elif choice == '3':
                print("Skipped payment. Loyalty -5.")
                self.crew_skipped_wage_turns += 1
                self.crew_skipped_wage_total += 1
                return -5
            else:
                print("Invalid choice, try again.")

    def apply_loyalty_penalties(self):
        # Apply skipping penalties over total game
        if self.crew_skipped_wage_total == 2 and self.crew_loyalty > 30:
            print("Due to skipped wages twice, crew loyalty dropped to 30.")
            self.crew_loyalty = 30
        elif self.crew_skipped_wage_total >= 3 and self.crew_loyalty > 0:
            print("Due to skipped wages thrice, crew loyalty dropped to 0.")
            self.crew_loyalty = 0

    def update_loyalty(self, change):
        self.crew_loyalty += change
        if self.haldun_recruited and self.haldun_loyalty_bonus_active and self.crew_loyalty < 50:
            self.crew_loyalty += 1  # Haldun loyalty bonus
        # Clamp between 0-100
        if self.crew_loyalty > 100:
            self.crew_loyalty = 100
        elif self.crew_loyalty < 0:
            self.crew_loyalty = 0

    def check_mutiny(self):
        if self.crew_loyalty < 30:
            # 33% chance assassination/mutiny attempt
            if random.random() < 0.33:
                print("\n*** You were a victim of a conspiracy. Your journey ends now. ***")
                print("GAME OVER.")
                self.game_over = True

    def show_status(self):
        print("\n--- Status Summary ---")
        print(f"Solaris: {self.solaris}")
        print(f"Crew Loyalty (avg): {self.crew_loyalty}")
        print(f"Reputation: {self.reputation}")
        print(f"Fuel: {self.fuel}")
        print(f"Food: {self.food}")
        print("-----------------------\n")

    def generate_missions(self):
        count = self.mission_offer_count
        if self.ship_choice == '4':  # Recon Vessel bonus: +1 mission
            count += 1

        # Filter mission types based on reputation and diplomatic rules
        missions_pool = []
        for mtype, details in MISSION_TYPES.items():
            if mtype == 'Diplomatic' and self.reputation >= 70:
                continue
            if mtype == 'Diplomatic' and self.reputation < 30:
                # always offer diplomatic missions when reputation < 30
                missions_pool.append(mtype)
            else:
                missions_pool.append(mtype)

        # Pick random mission types weighted by appearance chance
        mission_choices = []
        while len(mission_choices) < count and missions_pool:
            candidate = random.choice(missions_pool)
            if candidate not in mission_choices:
                mission_choices.append(candidate)

        return mission_choices

    def mission_story(self, mission_type):
        # Simple generic story examples
        stories = {
            'Recon': "Scout an uncharted sector rumored to harbor alien artifacts.",
            'Salvage': "Retrieve valuable wreckage from a derelict space station.",
            'Cargo Transfer': "Deliver critical supplies to a distant colony.",
            'Escort': "Protect a high-value cargo shipment through hostile territory.",
            'Diplomatic': "Negotiate trade agreements with a newly discovered faction.",
            'Invasion': "Lead an assault on a hostile outpost threatening Federation security.",
        }
        return stories.get(mission_type, "A mission of unknown parameters.")

    def mission_minor_event(self, mission_type):
        # Minor event choices based on mission
        events = {
            'Recon': ["Sensor malfunction delays scan.", "Unexpected energy readings detected."],
            'Salvage': ["Radiation leak found in salvage site.", "Hostile scavengers nearby."],
            'Cargo Transfer': ["Cargo hold breach threatens supplies.", "Pirate activity reported ahead."],
            'Escort': ["Ambush attempt detected.", "Crew member falls ill during transit."],
            'Diplomatic': ["Faction leader is wary and untrusting.", "Cultural misunderstanding arises."],
            'Invasion': ["Enemy reinforcements arriving.", "Saboteur onboard your ship."],
        }
        return random.choice(events.get(mission_type, []))

    def mission_rewards(self, mission_type, difficulty):
        base_min, base_max = MISSION_TYPES[mission_type]['reward_range']
        mod = DIFFICULTY_MODIFIERS[difficulty]['reward_mod']
        reward = int(random.randint(base_min, base_max) * mod)
        return reward

    def run_mission(self, mission_type):
        print(f"\nMission: {mission_type}")
        print(self.mission_story(mission_type))
        print(f"Minor event: {self.mission_minor_event(mission_type)}")

        # Choose difficulty for mission
        difficulties = list(DIFFICULTY_MODIFIERS.keys())
        print("Select difficulty:")
        for idx, diff in enumerate(difficulties, 1):
            print(f"{idx}. {diff}")
        while True:
            choice = input("> ").strip()
            if choice in [str(i) for i in range(1, len(difficulties)+1)]:
                difficulty = difficulties[int(choice)-1]
                break
            else:
                print("Invalid choice, try again.")

        # Combat chance check
        combat_chance = MISSION_TYPES[mission_type]['combat_chance']
        if random.random() < combat_chance:
            print("\nCombat encounter triggered!")
            combat_success = self.simulate_combat(difficulty)
            if not combat_success:
                # Mission failure
                print("Mission failed!")
                self.reputation = max(0, self.reputation - 10)
                self.update_loyalty(-5)
                return False
            else:
                print("Mission successful after combat.")
        else:
            print("No combat this mission.")

        # Calculate reward
        reward = self.mission_rewards(mission_type, difficulty)
        print(f"Mission reward: {reward} Solaris")
        self.solaris += reward

        # Update reputation
        self.reputation += MISSION_TYPES[mission_type]['rep_gain']
        if self.reputation > 100:
            self.reputation = 100

        # Success effect on loyalty (optional)
        self.update_loyalty(+2)

        return True

    def simulate_combat(self, difficulty):
        # Simple combat simulation: chance of success depends on difficulty and marine bonuses
        base_success_chance = {
            'Easy': 0.85,
            'Medium': 0.70,
            'Hard': 0.50,
            'Legendary': 0.30,
        }[difficulty]

        marine_bonus = 1.0
        if self.ship_choice == '3':  # Combat Vessel: +5% health/damage = +5% success chance
            marine_bonus = 1.05
        elif difficulty == 'Easy':
            marine_bonus = 1.3
        elif difficulty == 'Medium':
            marine_bonus = 1.1

        success_chance = base_success_chance * marine_bonus

        # Enemy difficulty bonus applies by reducing success chance
        enemy_bonus = DIFFICULTY_MODIFIERS[difficulty]['enemy_bonus']
        success_chance /= enemy_bonus

        roll = random.random()
        # Debug:
        # print(f"Combat success chance: {success_chance:.2f}, roll: {roll:.2f}")

        return roll < success_chance

    def strange_signal_event(self):
        # 5% chance per turn
        if self.haldun_recruited:
            return  # Already recruited, no event
        if random.random() < 0.05:
            print("\nYou receive a strange, mysterious signal from deep space.")
            print("Options:")
            print("1. Investigate the signal")
            print("2. Ignore the signal")
            while True:
                choice = input("> ").strip()
                if choice == '1':
                    # Encounter Haldun
                    print("\nEncounter with entity 'Haldun'!")
                    print("Haldun can mimic and transform living beings.")
                    print("Choose your action:")
                    print("1. Attack (Legendary difficulty)")
                    print("2. Recruit for 5000 Solaris")
                    while True:
                        c2 = input("> ").strip()
                        if c2 == '1':
                            success = self.simulate_combat('Legendary')
                            if success:
                                print("You defeated Haldun. No reward.")
                            else:
                                print("You were defeated by Haldun. Game over.")
                                self.game_over = True
                            return
                        elif c2 == '2':
                            if self.solaris >= 5000:
                                self.solaris -= 5000
                                self.haldun_recruited = True
                                self.haldun_loyalty_bonus_active = True
                                print("Haldun recruited! You gain +1 crew loyalty each wage payment as long as loyalty < 50.")
                            else:
                                print("Not enough Solaris to recruit.")
                            return
                        else:
                            print("Invalid choice.")
                    return
                elif choice == '2':
                    print("You ignore the strange signal and continue.")
                    return
                else:
                    print("Invalid choice.")

    def check_sponsorship_event(self):
        # Trigger once if Solaris drops below 0
        if self.solaris < 0 and not hasattr(self, 'sponsorship_triggered'):
            self.sponsorship_triggered = True
            print("\nYour Solaris balance is below zero!")
            print("Special mission 'Paid Sponsorship' available:")
            print("1. Medium difficulty combat mission, reward 1000 Solaris")
            print("2. Take a loan of 1500 Solaris, repay 2250 in 3 turns (fail to repay = game over)")
            while True:
                choice = input("> ").strip()
                if choice == '1':
                    success = self.simulate_combat('Medium')
                    if success:
                        print("Mission successful! You receive 1000 Solaris.")
                        self.solaris += 1000
                    else:
                        print("Mission failed! No reward.")
                    break
                elif choice == '2':
                    self.loan_amount = 1500
                    self.loan_due = 2250
                    self.loan_turns_left = 3
                    self.solaris += 1500
                    print("Loan taken. You have 3 turns to repay 2250 Solaris or lose your ship.")
                    break
                else:
                    print("Invalid choice.")

    def handle_loan(self):
        if hasattr(self, 'loan_turns_left'):
            self.loan_turns_left -= 1
            if self.loan_turns_left <= 0:
                if self.solaris >= self.loan_due:
                    self.solaris -= self.loan_due
                    print(f"Loan of {self.loan_due} Solaris repaid successfully.")
                    del self.loan_turns_left
                    del self.loan_amount
                    del self.loan_due
                else:
                    print("Failed to repay loan! Your ship has been seized. GAME OVER.")
                    self.game_over = True
            else:
                print(f"Loan repayment due in {self.loan_turns_left} turns.")

    def main_loop(self):
        while not self.game_over:
            self.turn += 1
            print(f"\n=== TURN {self.turn} ===")

            self.show_status()

            self.check_mutiny()
            if self.game_over:
                break

            self.strange_signal_event()
            if self.game_over:
                break

            self.check_sponsorship_event()
            if self.game_over:
                break

            self.handle_loan()
            if self.game_over:
                break

            # Crew wages payment & loyalty update
            loyalty_change = self.pay_crew_wages()
            self.update_loyalty(loyalty_change)
            self.apply_loyalty_penalties()

            if self.crew_loyalty == 0:
                print("Crew loyalty dropped to zero. Mutiny is certain. GAME OVER.")
                self.game_over = True
                break

            # Show missions
            mission_choices = self.generate_missions()
            print("Available missions:")
            for idx, m in enumerate(mission_choices, 1):
                print(f"{idx}. {m}")

            print("Choose a mission to undertake (or type 0 to skip):")
            while True:
                choice = input("> ").strip()
                if choice == '0':
                    print("Skipping mission this turn.")
                    break
                elif choice.isdigit() and 1 <= int(choice) <= len(mission_choices):
                    mission = mission_choices[int(choice)-1]
                    success = self.run_mission(mission)
                    break
                else:
                    print("Invalid choice.")

            # Fuel and food consumption
            self.fuel -= 5
            self.food -= 5
            if self.fuel < 0:
                print("Fuel depleted. You are stranded. GAME OVER.")
                self.game_over = True
            if self.food < 0:
                print("Food supplies exhausted. Crew starved. GAME OVER.")
                self.game_over = True

            # Reputation decay per turn
            self.reputation -= 2
            if self.reputation < 0:
                self.reputation = 0

        print("Thank you for playing!")

if __name__ == "__main__":
    game = Game()
    game.start()
