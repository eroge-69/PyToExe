import time
import random

memes = [
    "🚨 Suspicious vibes detected...\n\"Me clicking random popups like: I'M FEELING LUCKY 💀\"",
    "😬 Laptop acting sus?\n\"You downloaded 'free_ram_installer.zip'? Bro...\"",
    "🕵️‍♂️ \"That one antivirus that asks for your credit card: I'm here to protect you, and rob you.\"",
    "🤖 \"When you Google ‘how to remove virus’ using the infected device: Big Brain moves 🧠\"",
    "📉 \"Your laptop’s performance graph just flatlined. RIP.\"",
    "🧙‍♂️ \"You clicked on a link promising ‘Free Hogwarts Admission’? Expecto Malware!\"",
]

print("🤔 Hello user, a quick question...")
response = input("Do you *feel* like there’s a virus lurking in your laptop? (yes/no): ").strip().lower()

if response == "yes":
    print("\nHmm...Analyzing mysterious laptop vibes... 🔍")
    time.sleep(5)
    print("\n💡 After five seconds of intense reflection...")
    print(random.choice(memes))
    print("🧠 Pro tip: Ask ChatGPT. That entity probably has antivirus in its brain. 😄")
else:
    print("\n🎉 Awesome! Your cyber chi is balanced. May your bandwidth be fast and your cookies non-tracking.")
