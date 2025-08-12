import keyboard
import time
i = input("Enter text: ")
it = float(input("Enter number: "))
print("Starting in 5 seconds...")
time.sleep(5)
while True:
    keyboard.write(i)
    keyboard.send("enter")
    time.sleep(it)
