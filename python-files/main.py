
import random

class Player:
    def __init__(self, name="Player", health=100):
        self.name = name
        self.max_health = health
        self.health = health
    
    def take_damage(self, damage):
        self.health = max(0, self.health - damage)
    
    def is_alive(self):
        return self.health > 0
    
    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

class Boss:
    def __init__(self, name="Matthew", health=100):
        self.name = name
        self.max_health = health
        self.health = health
    
    def take_damage(self, damage):
        self.health = max(0, self.health - damage)
    
    def is_alive(self):
        return self.health > 0
    
    def attack(self):
        # Boss does random damage between 3-8
        return random.randint(3, 8)

class Game:
    def __init__(self):
        self.player = Player()
        self.boss = Boss()
        self.turn_count = 0
    
    def display_status(self):
        print(f"\n--- Turn {self.turn_count} ---")
        print(f"{self.player.name}: {self.player.health}/{self.player.max_health} HP")
        print(f"{self.boss.name}: {self.boss.health}/{self.boss.max_health} HP")
        print("-" * 30)
    
    def player_attack(self, attack_type):
        damage_dealt = 0
        
        if attack_type == "melee":
            damage_dealt = random.randint(8, 12)
            print(f"You swing your sword and hit {self.boss.name} for {damage_dealt} damage!")
        elif attack_type == "ranged":
            damage_dealt = random.randint(4, 8)
            print(f"You shoot an arrow and hit {self.boss.name} for {damage_dealt} damage!")
        elif attack_type == "magic":
            damage_dealt = random.randint(15, 25)
            print(f"You cast a spell and hit {self.boss.name} for {damage_dealt} damage!")
        elif attack_type == "heal":
            heal_amount = random.randint(10, 20)
            self.player.heal(heal_amount)
            print(f"You heal yourself for {heal_amount} health!")
            return True  # Successful turn, no damage dealt to boss
        else:
            print("You fumble and miss your attack!")
            return True  # Turn used but no damage
        
        self.boss.take_damage(damage_dealt)
        return True
    
    def boss_turn(self):
        if not self.boss.is_alive():
            return
        
        boss_damage = self.boss.attack()
        self.player.take_damage(boss_damage)
        print(f"{self.boss.name} attacks you for {boss_damage} damage!")
    
    def get_player_action(self):
        while True:
            print("\nChoose your action:")
            print("1. Melee attack (8-12 damage)")
            print("2. Ranged attack (4-8 damage)")
            print("3. Magic attack (15-25 damage)")
            print("4. Heal (10-20 health)")
            
            choice = input("Enter your choice (1-4 or type name): ").lower().strip()
            
            if choice in ["1", "melee"]:
                return "melee"
            elif choice in ["2", "ranged"]:
                return "ranged"
            elif choice in ["3", "magic"]:
                return "magic"
            elif choice in ["4", "heal"]:
                return "heal"
            else:
                print("Invalid choice! Please try again.")
    
    def play(self):
        print(f"🎮 BOSS BATTLE BEGINS! 🎮")
        print(f"You encounter {self.boss.name}, a fearsome boss!")
        print(f"{self.boss.name} has {self.boss.health} health points.")
        print("Prepare for battle!\n")
        
        while self.player.is_alive() and self.boss.is_alive():
            self.turn_count += 1
            self.display_status()
            
            # Player turn
            action = self.get_player_action()
            self.player_attack(action)
            
            # Check if boss is defeated
            if not self.boss.is_alive():
                break
            
            # Boss turn
            self.boss_turn()
        
        # Game over
        self.display_status()
        if self.player.is_alive():
            print(f"\n🎉 VICTORY! 🎉")
            print(f"You have defeated {self.boss.name}!")
            print(f"You won in {self.turn_count} turns with {self.player.health} health remaining!")
        else:
            print(f"\n💀 DEFEAT! 💀")
            print(f"{self.boss.name} has defeated you!")
            print("Better luck next time!")
        
        # Ask to play again
        play_again = input("\nWould you like to play again? (y/n): ").lower().strip()
        if play_again in ["y", "yes"]:
            print("\n" + "="*50 + "\n")
            Game().play()  # Start a new ga
def main():
    print("Welcome to Boss Battle!")
    player_name = input("Enter your name: ").strip()
    if player_name:
        game = Game()
        game.player.name = player_name
        game.play()
    else:
        Game().play()

if __name__ == "__main__":
    main()
