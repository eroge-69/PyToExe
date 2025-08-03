import os
import time

def get_desktop_path():
    return os.path.join(os.path.expanduser("~"), "Desktop")

def drop_bananas(amount=3000):
    desktop = get_desktop_path()
    print(f"\n🍌 Starte Banana.exe – {amount} Bananas incoming...\n")

    for i in range(1, amount + 1):
        filename = os.path.join(desktop, f"banana_{i}.txt")
        try:
            with open(filename, "w") as f:
                f.write(f"🍌 Banana Nummer {i} – frisch geliefert!")
        except Exception as e:
            print(f"⚠️ Fehler bei Banana {i}: {e}")
        if i % 500 == 0 or i == amount:
            print(f"✅ {i} Bananas erstellt...")

    print("\n🎉 Fertig! Dein Desktop ist jetzt offiziell eine Plantage!")

if __name__ == "__main__":
    drop_bananas()
