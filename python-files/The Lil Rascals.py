import random
import time

# Rascal Boss Class
class RascalBoss:
    def __init__(self, name, health, moves):
        self.name = name
        self.health = health
        self.moves = moves
        self.captured = False  
    
    def attack(self):
        move = random.choice(self.moves)
        print(f"\n{self.name} used {move}!")
        return random.randint(5, 20)

# Player Class
class Player:
    def __init__(self):
        self.health = 100
        self.year = 1999
        self.rascals_captured = []  

    def attack(self):
        move = random.choice(["Task Manager Slam", "Windows Update Trap"])
        print(f"\nYou used {move}!")
        return random.randint(10, 25)

    def use_rascal_pyramid(self, boss):
        print(f"\n🔥 You threw the Rascal Pyramid at {boss.name}!")
        time.sleep(2)
        if random.choice([True, False]):  
            boss.captured = True
            self.rascals_captured.append(boss.name)
            print(f"\n🎉 {boss.name} has been captured inside the Rascal Pyramid!")
            return True
        else:
            print(f"\n💾 The Rascal Pyramid glitched! {boss.name} broke free!")
            return False

# AI Rascals (Now including Python Terminal Rascal!)
gpt4o = RascalBoss("🔮 GPT-4o", 120, ["Overconfidence Blast!", "Hallucination Mode!", "Explaining the Wrong Answer with Confidence!"])
copilot = RascalBoss("💾 Copilot", 100, ["Memory Rascal!", "Helpful Advice (but actually nonsense)!", "Random Knowledge Drop!"])
clippy = RascalBoss("📎 Clippy", 80, ["Font Frenzy!", "Pop-up Spam!", "Forced Restart!"])
terminal_rascal_c = RascalBoss("💾 C Terminal Rascal", 110, ["Syntax Gremlin!", "Compiler Goblin!", "Segfault Specter!"])
terminal_rascal_python = RascalBoss("🐍 Python Terminal Rascal", 95, ["Indentation Phantom!", "Runtime Gremlin!", "Infinite Loop Specter!"])

# Battle + Capture Loop
def battle_rascal(boss):
    print(f"\n🚀 A Wild {boss.name} Appears!")
    
    while boss.health > 0 and not boss.captured:
        action = input("Type 'attack', 'task manager', or 'capture': ").strip().lower()

        if action == "attack":
            boss.health -= player.attack()
            print(f"{boss.name} HP: {boss.health}")

        elif action == "task manager":
            print(f"\n📎 Attempting to force-close {boss.name}...")
            time.sleep(2)
            if random.choice([True, False]):
                print(f"\n📎 SUCCESS: {boss.name} has been force-closed!\n")
                break
            else:
                print(f"\n📎 FAILURE: {boss.name} blocked Task Manager!\n")
                boss.attack()

        elif action == "capture":
            if player.use_rascal_pyramid(boss):
                break  
        else:
            print("\n📎 ERROR: Invalid action!")

    if boss.captured:
        print(f"\n🎉 {boss.name} is now part of your rascal team!")
    else:
        print(f"\n🎉 {boss.name} has been defeated! Onto the next rascal...\n")

# Main game loop (Now includes both Terminal Rascals!)
player = Player()

print("\n🚀 Welcome to **The Lil Rascals**!")
battle_rascal(gpt4o)  
battle_rascal(copilot)  
battle_rascal(clippy)  
battle_rascal(terminal_rascal_c)  
battle_rascal(terminal_rascal_python)  

print("\n🎉 All battles complete! Windows XP Mode unlocked!")
print(f"\n🔥 Rascals you captured: {player.rascals_captured}\n")
