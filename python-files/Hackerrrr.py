from time import sleep
sleep(1)

RED = "\033[31m"
GREEN = "\033[32m"
BLUE = "\033[34m"
RESET = "\033[0m"  # Reset to default color

# Set colour to green
print(GREEN)

print ("Welcome to the hacking terminal")
name = input ("What is your hacker name " + RESET)
print (GREEN + "Cool hacker name", name)
print("\n")

from time import sleep
sleep(3)


for i in range(3):
    print("!!!We are being hacked!!!")

    print(GREEN)

unhack = input("Type: (Unhack) to stop the hack " + RESET)
if unhack.lower() == "unhack":
    print("We have defeated the hackers. Mission sucsess.")
    
    from time import sleep
    sleep(3)

    print("More comeing soon.")


else:
    print(RED)
    print("Bro. are u dumb")

from time import sleep
sleep(3)

print("More comeing soon.")


























