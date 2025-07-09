import math
import time
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def bounce_animation(duration=10, speed=0.5, amplitude=5):
    """
    Symuluje odbijanie się czegoś (np. piersi) przez `duration` sekund.
    - `speed`: szybkość oscylacji
    - `amplitude`: amplituda ruchu (w ilości linii)
    """
    start_time = time.time()
    
    while time.time() - start_time < duration:
        t = time.time()  # Czas bieżący
        # Oblicz pozycję Y na podstawie funkcji sinusoidalnej
        y = int(amplitude * math.sin(2 * math.pi * t / speed))
        
        clear_screen()
        print(" Anime Girl ".center(30, "-"))
        print("   O     O   ")
        print("   |     |   ")
        
        # Rysowanie "cycków" przesuwających się w pionie
        for i in range(abs(y)):
            print()  # Puste linie jako odstęp
        
        print(f"  {'_'*6}  ")  # Dolna granica "cycków"
        print(f"  \\    /")      # Górna część
        print(f"   \\  / ")      # Środek
        print(f"    \\/  ")      # Spodek

        time.sleep(0.05)

try:
    print("Symulacja odbijania się... (Ctrl+C by zakończyć)")
    while True:
        bounce_animation(duration=3, speed=0.5, amplitude=4)
        time.sleep(0.5)  # Krótkie wstrzymanie między cyklami
except KeyboardInterrupt:
    print("\nKoniec animacji.")