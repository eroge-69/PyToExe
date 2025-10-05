# Ask the user if they want OPSEC
choice = input("Do you want OPSEC? Type 1 for Yes or 2 for No: ")

if choice == "1":
    print("OPSEC valid.")
elif choice == "2":
    print("OPSEC disabled.1")
else:
    print("Invalid input. Please type 1 or 2.")
