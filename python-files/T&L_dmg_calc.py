import random

# --- Royal blue ASCII art ---
print("\033[38;2;65;105;225m")
print(r"""
  █████████  █████                █████      █████                                   
 ███░░░░░███░░███                ░░███      ░░███                                    
░███    ░░░  ░███████    ██████   ░███ █████ ░███ █████  ██████   ████████   ██████  
░░█████████  ░███░░███  ░░░░░███  ░███░░███  ░███░░███  ░░░░░███ ░░███░░███ ░░░░░███ 
 ░░░░░░░░███ ░███ ░███   ███████  ░██████░   ░██████░    ███████  ░███ ░░░   ███████ 
 ███    ░███ ░███ ░███  ███░░███  ░███░░███  ░███░░███  ███░░███  ░███      ███░░███ 
░░█████████  ████ █████░░████████ ████ █████ ████ █████░░████████ █████    ░░████████
 ░░░░░░░░░  ░░░░ ░░░░░  ░░░░░░░░ ░░░░ ░░░░░ ░░░░ ░░░░░  ░░░░░░░░ ░░░░░      ░░░░░░░░ 
                                                                                     
                                                                                     
                                                                                     
""")
print("\033[0m")  # reset color

print("Damage Calculator for Throne and Liberty by: Shakkara")
print("Before we continue, we need some information about the attacker's and the victim's stats.\n")

# --- User input ---
crit = float(input("Enter crit value: "))
endu = float(input("Enter endu value: "))
skill_dmg_boost = float(input("Enter skill_dmg_boost value: "))
skill_dmg_resist = float(input("Enter skill_dmg_resist value: "))
heavy_atk_chance = float(input("Enter heavy_atk_chance value: "))
heavy_atk_evasion = float(input("Enter heavy_atk_evasion value: "))
heavy_atk_dmg_bonus = float(input("Enter heavy_atk_dmg_bonus value: "))
heavy_atk_dmg_resist = float(input("Enter heavy_atk_dmg_resist value: "))
base_min = float(input("Enter base_min value (default 450): ") or 450)
base_max = float(input("Enter base_max value (default 1200): ") or 1200)
defense = float(input("Enter defense value: "))

# Calculate extra damage reduction from defense
extra_damage_reduction = defense / (defense + 2500)

def calculate_base_damage(
    crit, endu, base_min, base_max
):
    if crit > endu:
        chance = (crit - endu) / (crit - endu + 1000)
        if random.random() < chance:
            return base_max * 1.1
        else:
            return random.uniform(base_min, base_max)
    elif endu > crit:
        chance = (endu - crit) / (endu - crit + 1000)
        if random.random() < chance:
            return base_min
        else:
            return random.uniform(base_min, base_max)
    else:
        return random.uniform(base_min, base_max)

def apply_skill_formula(skill_choice, base_damage):
    if skill_choice == 1:
        # Phoenix Barrage: 10 x (73% of base dmg + 19)
        return 10 * (0.73 * base_damage + 19)
    elif skill_choice == 2:
        # Javelin Inferno: 257% of base dmg + 95
        return 2.57 * base_damage + 95
    elif skill_choice == 3:
        # Guillotine (Prone not active): 2 x (750% of base dmg + 111)
        return 2 * (7.5 * base_damage + 111)
    elif skill_choice == 4:
        # Guillotine (Prone active): 2 x (975% of base dmg + 144)
        return 2 * (9.75 * base_damage + 144)
    elif skill_choice == 5:
        # Focus Fire Bomb (charged): 1.2 x (510% of base dmg + 516)
        return 1.2 * (5.10 * base_damage + 516)
    elif skill_choice == 6:
        # Meteor: (666% of base dmg + 74) + 12 x (444% base dmg + 49)
        return (6.66 * base_damage + 74) + 12 * (4.44 * base_damage + 49)
    else:
        return base_damage  # fallback

def calculate_damage(
    crit, endu, skill_dmg_boost, skill_dmg_resist,
    heavy_atk_chance, heavy_atk_evasion, heavy_atk_dmg_bonus, heavy_atk_dmg_resist,
    base_min=450, base_max=1200,
    is_pvp=True, extra_damage_reduction=0.60,
    skill_choice=1
):
    # 1. Base damage calculation (crit vs endu)
    base_damage = calculate_base_damage(crit, endu, base_min, base_max)

    # 2. Apply skill formula BEFORE skill dmg modifier
    skill_damage = apply_skill_formula(skill_choice, base_damage)

    # 3. Skill damage modifier (two-branch logic)
    A = skill_dmg_boost - skill_dmg_resist
    if A >= 0:
        skill_modifier = 1 + (A / (A + 1000))
    else:
        skill_modifier = 1 + (A / (A - 1000))

    damage = skill_damage * skill_modifier

    # 4. Heavy attack logic
    heavy_modifier = 1
    if heavy_atk_chance > heavy_atk_evasion:
        heavy_chance = (heavy_atk_chance - heavy_atk_evasion) / (heavy_atk_chance - heavy_atk_evasion + 1000)
        if random.random() < heavy_chance:
            heavy_modifier = (heavy_atk_dmg_bonus - heavy_atk_dmg_resist + 200) / 100

    final_damage = damage * heavy_modifier

    # 5. PvP and extra damage reduction
    if is_pvp:
        final_damage *= (1 - 0.10)  # PvP reduction
    final_damage *= (1 - extra_damage_reduction)  # character extra reduction

    return final_damage

def skill_menu():
    print("\nChoose a skill to simulate:")
    print("1. Phoenix Barrage: 10 x (73% of base dmg + 19)")
    print("2. Javelin Inferno: 257% of base dmg + 95")
    print("3. Guillotine (Collision: Prone not active, fully charged): 2 x (750% of base dmg + 111)")
    print("4. Guillotine (Collision: Prone active, fully charged): 2 x (975% of base dmg + 144)")
    print("5. Focus Fire Bomb (charged): 1.2 x (510% of base dmg + 516)")
    print("6. Meteor (Fully stand in it): (666% of base dmg + 74) + 12 x (444% base dmg + 49)")

    while True:
        try:
            skill_choice = int(input("Enter the number of the skill (1-6): "))
            if 1 <= skill_choice <= 6:
                return skill_choice
            else:
                print("Please enter a number between 1 and 6.")
        except ValueError:
            print("Please enter a valid number.")

while True:
    runs = int(input("\nHow many times should the simulation run? "))
    skill_choice = skill_menu()

    # --- Run simulation ---
    results = []
    for _ in range(runs):
        dmg = calculate_damage(
            crit, endu, skill_dmg_boost, skill_dmg_resist,
            heavy_atk_chance, heavy_atk_evasion, heavy_atk_dmg_bonus, heavy_atk_dmg_resist,
            base_min, base_max,
            is_pvp=True,
            extra_damage_reduction=extra_damage_reduction,
            skill_choice=skill_choice
        )
        results.append(dmg)

    print(f"\nResults after {runs} runs:")
    print(f"Minimum damage: {min(results):.2f}")
    print(f"Average damage: {sum(results)/len(results):.2f}")
    print(f"Maximum damage: {max(results):.2f}")
    print(f"Total damage income: {sum(results):.2f}")
    print(f"Extra damage reduction (from defense): {extra_damage_reduction*100:.2f}%")

    again = input("\nWould you like to simulate another skill? (y/n): ").strip().lower()
    if again != 'y':
        print("Thank you for using the Damage Calculator! Goodbye.")
        break
