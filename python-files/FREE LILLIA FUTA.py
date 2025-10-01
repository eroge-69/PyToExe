import sys

blocked_names = ["babaru", "Dragos", "Babaru", "BABARU", "dragos", "DRAGOS", "daam", "dam", "Daam"]
allowed_names = ["mango", "japan", "japonezu", "tudi", "Tudi", "nigger"]

name = input("Enter your name: ")

if name.lower() in blocked_names:
    input("Gtfo boi u aint tuff")
    sys.exit()

if name.lower() in allowed_names:
    print("Welcome, tuff boi!")

age = int(input("Enter your age: "))

print(f'name: {name}, age: {age}')

if age == 67:
    print(f"boii ts so tuff mango, {age}!")
    input("You are so tuff! Press Enter to enter heaven")
elif age < 67:
    print("-boi u aint tuff like mango")
    input("You are not tuff enough! Press Enter to go to hell")  
else:
    print("-boi u aint tuff like mango")
    input("You are not tuff enough! Press Enter to go to hell")

