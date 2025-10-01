import time
import random
import os
import sys

badger_art = """
      (\\__/)
     (•ㅅ•)
    / 　 づ
BADGER BADGER BADGER BADGER
"""

messages = [
    "Je had iets nuttigs kunnen doen...",
    "Waarom klikte je hierop?",
    "Dit programma doet echt niets.",
    "Afleiding geactiveerd!",
    "Badger overload incoming...",
    "Nog steeds hier? Fascinerend.",
    "Productiviteit = 0%",
]

def play_badger():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(badger_art)
        print(random.choice(messages))
        time.sleep(random.uniform(1.5, 3.5))

        # Random beep or fake alert
        if random.random() < 0.3:
            print("\a")  # Beep (works on some systems)
        if random.random() < 0.2:
            print("⚠️ Systeemfout: Badger overload.")
            time.sleep(1)

        # Escape trap
        if random.random() < 0.1:
            print("Probeer te sluiten... maar waarom zou je?")
            time.sleep(2)

try:
    play_badger()
except KeyboardInterrupt:
    print("\nJe dacht dat je kon ontsnappen. Maar de badgers blijven.")
    sys.exit(0)
