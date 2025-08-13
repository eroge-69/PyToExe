# codewords.py
responses = {
    "banana": "🍌 You found the secret fruit!",
    "eagle": "🦅 The eagle has landed.",
    "midnight": "🌙 It's past your bedtime..."
}

print("Type something (or 'quit' to exit).")

while True:
    text = input("> ").strip().lower()
    if text == "quit":
        break
    elif text in responses:
        print(responses[text])
    else:
        print("No special codeword detected.")

input("\nPress Enter to exit...")