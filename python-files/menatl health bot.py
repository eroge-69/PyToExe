import random

greetings = ["Hello! I'm your mental health buddy 💬", 
             "Hi there! I'm here to talk 💚", 
             "Hey! You're not alone 😊"]
farewells = ["Take care! 🌱", "You're doing great. Bye! 💖", "Stay strong! 💪"]

positive_quotes = [
    "You're stronger than you think.",
    "Every day may not be good, but there is something good in every day.",
    "Don't be afraid to ask for help.",
    "Your mental health matters.",
    "Take deep breaths, you're doing fine."
]

def chatbot():
    print(random.choice(greetings))
    print("You can talk to me about how you're feeling.")
    print("Type 'bye' to exit.\n")

    while True:
        user = input("You: ").lower()

        if "sad" in user or "depressed" in user:
            print("Bot: I'm really sorry you're feeling this way. Try talking to someone you trust. 💛")
        elif "stress" in user or "anxious" in user or "anxiety" in user:
            print("Bot: Try taking a few deep breaths... inhale... exhale. 🧘")
        elif "help" in user:
            print("Bot: You're not alone. Here’s a helpline: 9152987821 (India - iCall).")
        elif "happy" in user:
            print("Bot: That’s great to hear! 😄 Keep spreading joy.")
        elif "quote" in user or "motivate" in user:
            print("Bot:", random.choice(positive_quotes))
        elif user == "bye":
            print("Bot:", random.choice(farewells))
            break
        else:
            print("Bot: I'm listening. You can also say things like 'I'm sad', 'I need help', or 'tell me a quote'.")

chatbot()
