import math

def get_int(prompt, default=None):
    while True:
        try:
            user_input = input(f"{prompt}: ")
            if user_input == "" and default is not None:
                return default
            return int(user_input)
        except ValueError:
            print("Please enter a valid number.")

def main():
    print("=== Necroplasm Ritual Cost Calculator ===")
    
    # --- Ritual Definitions ---
    ritual_types = {
        "Reagent I": {
            "durability": 6,
            "inks": {"basic": 2}
        },
        "Reagent II": {
            "durability": 12,
            "inks": {"regular": 2}
            #"basic": 3
        },
        "Reagent III": {
            "durability": 18,
            "inks": {"regular": 3, "greater": 2}
        },
        "Commune I": {
            "durability": 6,
            "inks": {"basic": 4}
        },
        "Commune II": {
            "durability": 12,
            "inks": {"greater": 4}
        },
        "Commune III": {
            "durability": 18,
            "inks": {"powerful": 4}
        },
        "Elemental I": {
            "durability": 6,
            "inks": {"basic": 3}
        },
        "Elemental II": {
            "durability": 12,
            "inks": {"regular": 3}
            #"basic": 2
        },
        "Elemental III": {
            "durability": 18,
            "inks": { "regular": 2, "greater": 3}
        },
        "Charge I": {
            "durability": 6,
            "inks": {"regular": 2}
            #"basic": 1
        },
        "Charge II": {
            "durability": 12,
            "inks": {"regular": 1, "greater": 2}
        },
        "Charge III": {
            "durability": 18,
            "inks": {"greater": 1, "powerful": 2}
        }
    }

    ink_costs = {
        "regular": 20,
        "greater": 40,
        "powerful": 80
    }
    
    # --- Crafting Options ---
    crafting_options = {
        1: {
            "name": "Lesser Ensoul Material (20)",
            "rituals_per_item": {
                "Charge I": 1
            }
        },
        2: {
            "name": "Ensoul Material (60)",
            "rituals_per_item": {
                "Elemental II": 2,
                "Charge II": 2
            }
        },
        3: {
            "name": "Greater Ensoul Material (80)",
            "rituals_per_item": {
                "Elemental II": 3,
                "Charge II": 2
            }
        },
        4: {
            "name": "Greater Communion (60)",
            "rituals_per_item": {
                "Elemental II": 2,
                "Commune II": 2
            }
        },
        5: {
            "name": "Powerful Communion (90)",
            "rituals_per_item": {
                "Elemental III": 4,
                "Commune II": 2,
                "Commune III": 2
            }
        },
        6: {
            "name": "Greater Necroplasm (60)",
            "rituals_per_item": {
                "Elemental II": 2,
                "Reagent II": 2
            }
        },
        7: {
            "name": "Powerful Necroplasm (90)",
            "rituals_per_item": {
                "Elemental II": 2,
                "Elemental III": 4,
                "Reagent III": 2
            }
        }
    }

    # --- Selection ---
    print("\n--- Select Item to Craft ---")
    for key in sorted(crafting_options):
        print(f"{key}: {crafting_options[key]['name']}")

    choice = get_int("Enter selection", default=1)
    if choice not in crafting_options:
        print("Invalid selection.")
        return

    selected = crafting_options[choice]
    items_to_craft = get_int(f"Number of {selected['name']} to craft")
    
    # --- Calculations ---
    total_inks = {"regular": 0, "greater": 0, "powerful": 0}
    ritual_summary = {}

    for ritual_name, per_item_count in selected["rituals_per_item"].items():
        ritual = ritual_types[ritual_name]
        rituals_needed = math.ceil(items_to_craft / ritual["durability"])
        ritual_summary[ritual_name] = rituals_needed

        for ink, qty in ritual["inks"].items():
            total_inks[ink] += rituals_needed * qty
            
    total_necroplasm = math.ceil(
        sum(total_inks[ink] * ink_costs[ink] for ink in total_inks) / 100) * 100

    # --- Output ---
    print("\n=== Results ===")
    print(f"  Total Weak Necroplasm needed: {total_necroplasm * 2}")
    
    print("\n=== Debug ===")
    print(total_inks)
    print(f"{selected['name']}: {items_to_craft} items → {items_to_craft} durability used / {ritual['durability']} durability → {rituals_needed} ritual items")

if __name__ == "__main__":
    main()  