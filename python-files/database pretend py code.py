def easton_menu():
    password = input("Password:\n")
    if password != "VerySecurePassword.2011":
        print("Incorrect password. Returning to login screen.\n")
        return  # Return to main() — acts like 'go to login screen'

    while True:
        print(f"Hello Easton, welcome to the database.")
        resp2 = input("Please choose one of the following options:\n1. User Info\n2. Database\n3. Settings\n")

        if resp2 == "1":
            print("Name: Easton Lock\nDOB: 28/06/11\nDatabase join-date: 29/06/13")
            resp3 = input("Say 'Back' to return to the home screen.\n")
            if resp3 == "Back":
                continue
        elif resp2 == "2":
            print("Welcome to the Database!\nHere you can find the files in our Database stored confidentially.")
            resp3 = input("Say 'Back' to return to the home screen.\n")
            if resp3 == "Back":
                continue
        elif resp2 == "3":
            print("Settings are currently unavailable.")
            resp3 = input("Say 'Back' to return to the home screen.\n")
            if resp3 == "Back":
                continue
        else:
            print("Invalid option. Try again.")

        break  # Exit Easton menu loop


def brandon_menu():
    password = input("Password:\n")
    if password != "BrandonSuperSecret":
        print("Incorrect password. Returning to login screen.\n")
        return  # Return to main()

    while True:
        print(f"Hello Brandon, welcome to the database.")
        resp2 = input("Please choose one of the following options:\n1. User Info\n2. Database\n3. Settings\n")
        
        if resp2 == "1":
            print("Name: Brandon\nDOB: idk\nDatabase join-date: 12/09/25")
            resp3 = input("Say 'Back' to return to the home screen.\n")
            if resp3 == "Back":
                continue
        elif resp2 == "2":
            print("Database access unavailable.")
            resp3 = input("Say 'Back' to return to the home screen.\n")
            if resp3 == "Back":
                continue
        elif resp2 == "3":
            print("Settings are currently unavailable.")
            resp3 = input("Say 'Back' to return to the home screen.\n")
            if resp3 == "Back":
                continue
        else:
            print("Invalid option. Try again.")

        break  # Exit Brandon menu loop


def main():
    while True:
        resp1 = input("Hello! What is your name?\n")

        if resp1 == "Easton":
            easton_menu()
        elif resp1 == "Callum":
            print("CALLUM KNEEN HAS NO SPLEEN!!")
        elif resp1 == "Brandon":
            brandon_menu()
        else:
            print(f"Hello {resp1}, your details haven't checked out. Please leave or try again.")
        
        # Ask if user wants to try again
        again = input("\nWould you like to log in again? (yes/no)\n")
        if again.lower() != "yes":
            print("Goodbye!")
            break


# Start the program
main()
