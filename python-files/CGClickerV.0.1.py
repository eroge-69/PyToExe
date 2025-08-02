import random
import time

score = 0
goal = 1000

# Jeff the Killer ASCII
cursed_jeff = """
        .-"      "-.
       /            \\
      |              |
      |,  .-.  .-.  ,|
      | )(_o/  \\o_)( |
      |/     /\\     \\|
      (_     ^^     _)
       \\__|IIIIII|__/
        | \\IIIIII/ |
        \\          /
         `--------`
     Jeff: Go to sleep...
"""

# DSCI_0000 Glitch ASCII
dsci_ascii = """
[DSCI_0000.JPG]
█▓▒░ Static █▓▒░
👁 You shouldn't have opened this.
Filename cannot be deleted.
Timecode mismatch.
---
ERROR: Subject is looking back.
"""

# Random cursed faces
cursed_faces = [
    "( ͡° ͜ʖ ͡°)",
    "☠️👁👄👁☠️",
    "(╯°□°）╯︵ ┻━┻",
    "༼ つ ◕_◕ ༽つ",
    "👁🩸👁",
    cursed_jeff,
    dsci_ascii,
]

print("🔴 WELCOME TO: FUCK CHICKENGUN 🔴")
print("Type 'click' 1000 times to win... if you even survive.\n")

while score < goal:
    user_input = input("Type 'click': ").strip().lower()

    if user_input == "click":
        score += 1
        print(f"Score: {score} | FUCK CHICKENGUN 💢")

        # Cursed events trigger at these milestones or randomly
        if score in [10, 66, 100, 200, 420, 666] or random.randint(1, 25) == 13:
            print("\n👻 CURSED EVENT UNLOCKED:")
            print(random.choice(cursed_faces))
            print()

    elif user_input == "i won't click":
        print("☠️ THEN SUFFER THE CURSE ☠️")
        for i in range(10):
            print("👁", end="", flush=True)
            time.sleep(0.2)
        print("\nThe room feels colder now...")

    else:
        print("🚫 INVALID COMMAND. Type 'click' or suffer...")

print("\n🎉 YOU CLICKED 1000 TIMES. THE GAME IS OVER.")
print("...Or is it? 🤫")