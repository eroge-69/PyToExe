def skill_menu():
    print("\nChoose a skill to simulate:")
    print("1. Phoenix Barrage (10 hits)")
    print("2. Javelin Inferno (single hit)")
    print("3. Guillotine (Prone not active, fully charged, 2 hits)")
    print("4. Guillotine (Prone active, fully charged, 2 hits)")
    print("5. Focus Fire Bomb (charged, 1.2x multiplier)")
    print("6. Meteor (fully stand in it, multi-hit)")

    while True:
        try:
            skill_choice = int(input("Enter the number of the skill (1-6): "))
            if 1 <= skill_choice <= 6:
                return skill_choice
            else:
                print("Please enter a number between 1 and 6.")
        except ValueError:
            print("Please enter a valid number.")
