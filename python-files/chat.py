import json
import os

try:
    import colorama
    colorama.init()
    YELLOW = colorama.Fore.YELLOW
    BLUE = colorama.Fore.CYAN
    RESET = colorama.Style.RESET_ALL
except:
    YELLOW = ""
    BLUE = ""
    RESET = ""

CHAT_FILE = os.path.join(os.path.dirname(__file__), "chat.json")

if os.path.exists(CHAT_FILE):
    with open(CHAT_FILE, "r") as f:
        messages = json.load(f)
else:
    messages = []

def show_messages():
    for msg in messages:
        print(f"{YELLOW}>>{RESET} {BLUE}{msg}{RESET}")

show_messages()
print(f"{YELLOW}Scrie mesaje (CTRL+C pentru iesire){RESET}")

try:
    while True:
        text = input("> ")
        if text.strip() == "":
            continue
        messages.append(text)
        with open(CHAT_FILE, "w") as f:
            json.dump(messages, f)
        print(f"{BLUE}{text}{RESET}")
except KeyboardInterrupt:
    print("\nIesire. Mesajele au fost salvate pe stick.")
