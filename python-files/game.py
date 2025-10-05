import random
import time

lanes = ["Left", "Middle", "Right"]
car_lane = "Middle"

print("🚗 Car Game — Drive Safely!")
print("Use L for Left, M for Middle, R for Right")
print("-----------------------------------------")

while True:
    obstacle = random.choice(lanes)
    print(f"\nObstacle in {obstacle} lane!")

    move = input("Move (L/M/R): ").upper()
    if move == "L":
        car_lane = "Left"
    elif move == "M":
        car_lane = "Middle"
    elif move == "R":
        car_lane = "Right"

    if car_lane == obstacle:
        print("💥 You crashed!")
        break
    else:
        print("✅ Safe! Keep going...")
    time.sleep(1)
