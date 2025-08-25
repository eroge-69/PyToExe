import keyboard
import time

paused = False

# F9 za pauzu/nastavak
def toggle_pause():
    global paused
    paused = not paused
    print("\nSkripta pauzirana!" if paused else "\nSkripta nastavlja...")

keyboard.add_hotkey('f9', toggle_pause)

def wait_for(duration, message=None):
    """Čeka odabrani broj sekundi, prikazuje brojač u jednoj liniji"""
    end_time = time.time() + duration
    while time.time() < end_time:
        if paused:
            while paused:
                time.sleep(0.1)
            # resetuj end_time tako da preostalo vreme nastavi normalno
            end_time = time.time() + (end_time - time.time())
        else:
            if message:
                remaining = int(end_time - time.time())
                print(f"{message} {remaining}s preostalo...", end="\r")
            time.sleep(0.1)
    if message:
        print(" " * 50, end="\r")  # očisti liniju

def press_n_realistic(clicks=14, hold_time=0.05, interval=0.1):
    """Simulira N taster, brojač u jednoj liniji"""
    for i in range(1, clicks + 1):
        while paused:
            time.sleep(0.05)
        keyboard.press('n')
        time.sleep(hold_time)
        keyboard.release('n')
        print(f"Pokusavam da upecam ribu... {i}/{clicks}", end="\r")
        time.sleep(interval)
    print(" " * 50, end="\r")  # očisti liniju nakon završetka

def main_loop():
    # Dizajn sa slovima C L A P Z
    print("  C   L   A   P   Z  ")
    print("=====================")
    
    print("Pokreni SAMP i prebaci fokus na prozor igre.")
    print("F9 za pauziranje/nastavljanje tool-a.")
    print("Imate 5 sekundi da pripremite prozor SAMP-a...")
    time.sleep(5)

    print("Zapocinjem pecanje i ponavljam ciklus...")  # stalna poruka u istom delu terminala

    while True:
        while paused:
            time.sleep(0.1)

        # Otvori chat pritiskom na T
        keyboard.send('t')
        time.sleep(0.1)

        # Ukucaj /pecaj
        keyboard.write('/pecaj')
        keyboard.send('enter')

        # Čekanje 16 sekundi sa brojačem u jednoj liniji
        wait_for(16, message="Pokusavam da pecam ribu...")

        # Spam N 14 puta sa brojačem u jednoj liniji
        press_n_realistic(clicks=14, hold_time=0.05, interval=0.1)

        # Nakon završetka ciklusa, terminal ostaje u istom delu
        print("Zapocinjem pecanje i ponavljam ciklus...", end="\r")

        time.sleep(0.5)  # kratka pauza pre sledećeg ciklusa

if __name__ == "__main__":
    main_loop()
