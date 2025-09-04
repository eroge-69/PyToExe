#!/usr/bin/evn python3

# parul_database_counter.py

def parul_database_counter():
    print("📚 Welcome to the Parul Database Counter!")
    print("Each time the professor says 'database', press Enter.")
    print("Type 'exit' and press Enter when you're done.\n")

    count = 0

    while True:
        user_input = input("Heard 'database'? (press Enter or type 'exit'): ").strip().lower()
        if user_input == "":
            count += 1
            print(f"✅ Count updated: 'database' has been said {count} times.")
        elif user_input == "exit":
            print(f"\n📊 Final count: The professor said 'database' {count} times.")
            print("Thanks for using Parul Database Counter!")
            break
        else:
            print("⚠️ Invalid input. Just press Enter or type 'exit'.")

if __name__ == "__main__":
    parul_database_counter()
