import random
import time

print("🎲 Welcome to the Coin Toss Game 🎲")

heads = 0
tails = 0

while True:
    choice = input("\nPress Enter to toss the coin or type 'quit' to stop: ")

    if choice.lower() == "quit":
        break

    print("Tossing the coin...")
    time.sleep(1)  # suspense ⏳
    
    toss = random.choice(["Heads", "Tails"])
    print("👉 The coin landed on:", toss)

    if toss == "Heads":
        heads += 1
    else:
        tails += 1

    print(f"📊 Score so far → Heads: {heads} | Tails: {tails}")

print("\n✅ Final Score:")
print(f"Heads: {heads}, Tails: {tails}")
print("Thanks for playing! 👋")
