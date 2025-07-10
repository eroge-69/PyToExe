import os

def clear_screen():
    # Clear the terminal screen based on the OS
    os.system('cls' if os.name == 'nt' else 'clear')

def calculate_siga_dina_percentage():
    print("---------------------------------------------------------|")
    print("|                                                        |")
    print("|                                                        |")
    print("|  Church Members Statistics Calculator                  |")
    print("|  This tool calculates the percentage of church members |")
    print("|  Enter the values below:                               |")
    print("|                                                        |")
    print("|                                                        |")
    print("----------------------------------------------------------")

    while True:
        try:
            # User inputs
            total_siga_dina = int(input("Enter total Church Siga Dina: "))
            total_church_members = int(input("Enter total Church Members: "))

            # Validate input
            if total_church_members == 0:
                print("Total Church Members cannot be zero. Please try again.\n")
                continue

            # Calculate percentage
            percentage = (total_siga_dina / total_church_members) * 100
            print(f"\nPercentage of Siga Dina: {percentage:.2f}%\n")

        except ValueError:
            print("Invalid input. Please enter whole numbers only.\n")
            continue

        # Ask if user wants to calculate again
        repeat = input("🔁 Do you want to calculate again? (Press Enter to continue or type 'x' to exit): ").strip().lower()
        if repeat == 'x':
            print("\n👋 Thank you for using the Church Members Statistics Calculator. Goodbye!")
            break
        else:
            clear_screen()
            print("--- Church Members Statistics Calculator ---")
            print("New calculation:\n")

# Run the calculator
calculate_siga_dina_percentage()

