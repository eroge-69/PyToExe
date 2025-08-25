import random
import string
import os

HISTORY_FILE = "password_history.txt"

def generate_password():
    print("\n=== Create New Password ===")
    
    # Asking for details
    name = input("Enter your first name: ").strip()
    dob = input("Enter your date of birth (DDMMYYYY): ").strip()
    fav_word = input("Enter your favorite word: ").strip()
    pet_name = input("Enter your pet's name (or anything you like): ").strip()
    
    # Combine details
    base = name + dob + fav_word + pet_name
    
    # Shuffle the base string
    base_list = list(base)
    random.shuffle(base_list)
    base_mixed = "".join(base_list)
    
    # Add strong random characters
    random_chars = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=8))
    
    # Final password
    password = base_mixed[:6] + random_chars + base_mixed[-4:]
    
    print("\n Your Strong Generated Password is:")
    print(password)
    
    # Save to history file
    with open(HISTORY_FILE, "a") as f:
        f.write(password + "\n")
    
    print(" Password saved to history.\n")

def show_history():
    print("\n=== Password History ===")
    
    if not os.path.exists(HISTORY_FILE) or os.path.getsize(HISTORY_FILE) == 0:
        print(" No history found.\n")
        return
    
    with open(HISTORY_FILE, "r") as f:
        history = f.readlines()
    
    for i, pwd in enumerate(history, 1):
        print(f"{i}. {pwd.strip()}")
    print()

def dashboard():
    while True:
        print("=== Password Generator Dashboard ===")
        print("1. Create New Password")
        print("2. My History")
        print("3. Exit")
        
        choice = input("Choose an option (1/2/3): ").strip()
        
        if choice == "1":
            generate_password()
        elif choice == "2":
            show_history()
        elif choice == "3":
            print("\n Exiting... Stay secure!")
            break
        else:
            print(" Invalid choice. Please try again.\n")

# Run the dashboard
dashboard()
