import time

name = "Emina"
heart = "🩵"
special_date = "26 August"

print(f"\nHello {name}! 💫")
time.sleep(1.5)
print("Welcome to our test!")
time.sleep(1.5)
print("As an introduction: This is a safe and controlled environment and this test is made only for fun.")

# --- First set: Custom questions with custom replies ---
custom_questions = {
    "Do you think this test is safe? (Y/N): ": "Good, as you should.",
    "Do you like surprises? (Y/N): ": "Good! Because this is one just for you.",
    "Do you find this test a bit odd? (Y/N): ": "It's nothing you should fear.",
    "Do you think this test will make you laugh? (Y/N): ": "Hehe, I promise to always make you laugh!",
    "Is there someone you wish lived in your city (Y/N): ": "Sounds interesting, as always, you are always interesting.",
    "Do you miss me right now? (Y/N): ": "Aww, I miss you too already, wish I didn't have to stay muted.",
}

for q, reply in custom_questions.items():
    answer = input("\n" + q).strip().upper()
    time.sleep(1)
    if answer == "Y":
        print(reply)
    elif answer == "N":
        print("Hmm... Interesting... Moving on.")
    else:
        print("Not Y or N… but I’ll take it as a yes anyway.")

time.sleep(2)

# --- Second set: Romantic dialogue with Y/N answers ---
print(f"\nCongratulations user, {name}.")
time.sleep(2)
print("You finished the first part of the test.")
time.sleep(2)
print("We will now move on to the second part of this test.")
time.sleep(2)

questions = [
    f"Do you remember {special_date}, when we first slept on call? (Y/N): ",
    f"Since that night, did your days also feel brighter? (Y/N): ",
    f"And did your nights feel warmer too? (Y/N): ",
    f"Do you know that you live in my heart {heart}? (Y/N): ",
    f"Will you keep our love safe forever {heart}? (Y/N): "
]

for q in questions:
    answer = input("\n" + q).strip().upper()
    time.sleep(1)
    if answer == "Y":
        print("Aww, I knew it! " + heart)
    elif answer == "N":
        print("Oh no 😢 but I still adore you " + heart)
    else:
        print("Hehe, I’ll take that as a YES 😉 " + heart)

time.sleep(2)
print(f"\nI love you, {name}! Forever yours {heart}")
