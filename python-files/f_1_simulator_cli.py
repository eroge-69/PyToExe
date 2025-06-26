import random
import numpy as np
from datetime import timedelta

# --- Konstanty ---
DRIVERS = [
    ("O. Piastri", "McLaren"),
    ("L. Norris", "McLaren"),
    ("M. Verstappen", "Red Bull Racing"),
    ("G. Russell", "Mercedes-AMG"),
    ("C. Leclerc", "Ferrari"),
    ("L. Hamilton", "Ferrari"),
    ("K. Antonelli", "Mercedes-AMG"),
    ("A. Albon", "Williams"),
    ("E. Ocon", "Haas"),
    ("I. Hadjar", "Racing Bulls"),
    ("N. Hulkenberg", "Sauber"),
    ("L. Stroll", "Aston Martin"),
    ("C. Sainz Jr.", "Williams"),
    ("P. Gasly", "Alpine"),
    ("Y. Tsunoda", "Red Bull Racing"),
    ("F. Alonso", "Aston Martin"),
    ("O. Bearman", "Haas"),
    ("L. Lawson", "Racing Bulls"),
    ("G. Bortoleto", "Sauber"),
    ("F. Colapinto", "Alpine")
]

# Výkonnostní rozdíly (v sekundách na kolo pro každou pozici)
LAP_GAPS = [
    0, 0.13, 0.13, 0.11, 0.19, 0.15, 0.10, 0.13, 0.12, 0.006, 0.006,
    0.036, 0.006, 0.012, 0.006, 0.012, 0.012, 0.012, 0.024, 0
]

# --- Funkce ---
def simulate_race(laps, base_lap_time):
    base_total = base_lap_time * laps
    cumulative_gaps = np.cumsum([g * laps for g in LAP_GAPS])
    scale = 240 / cumulative_gaps[-1]
    gaps_scaled = cumulative_gaps * scale
    base_times = [base_total + g for g in gaps_scaled]

    dnf_count = random.randint(1, 5)
    dnf_indices = random.sample(range(20), dnf_count)
    results = []

    for idx, (name, team) in enumerate(DRIVERS):
        if idx in dnf_indices:
            results.append((None, name, team, "DNF", "Kolize nebo porucha"))
            continue

        time = base_times[idx]
        incident = 0
        notes = []

        if random.random() < 0.2:
            t = random.uniform(5, 10)
            incident += t
            notes.append(f"Technická závada +{t:.1f}s")
        if random.random() < 0.1:
            t = random.uniform(10, 20)
            incident += t
            notes.append(f"Chyba jezdce +{t:.1f}s")
        if random.random() < 0.1:
            t = random.uniform(5, 12)
            incident -= t
            notes.append(f"Výhodná strategie -{t:.1f}s")

        pit_stops = random.randint(1, 5)
        pit_time = sum([random.uniform(20, 26) for _ in range(pit_stops)])
        notes.append(f"{pit_stops}x box +{pit_time:.1f}s")

        total_time = time + incident + pit_time
        results.append((None, name, team, str(timedelta(seconds=int(total_time))), " | ".join(notes)))

    dnf = [r for r in results if r[3] == "DNF"]
    finished = [r for r in results if r[3] != "DNF"]

    # Promíchat 5–8 jezdců mimo DNF až o 2–3 pozice
    indices = random.sample(range(len(finished)), k=min(len(finished), random.randint(5, 8)))
    for i in indices:
        shift = random.choice([-3, -2, -1, 1, 2, 3])
        j = max(0, min(len(finished)-1, i + shift))
        finished[i], finished[j] = finished[j], finished[i]

    final = [(i+1, *r[1:]) for i, r in enumerate(finished)] + [("DNF", *r[1:]) for r in dnf]
    return final

# --- Spuštění ---
if __name__ == "__main__":
    print("F1 SIMULÁTOR 2025")
    
    # Předdefinované hodnoty pro neinteraktivní prostředí
    laps = 55
    base_lap = 82.0  # 1:22 min na kolo

    print(f"Simuluje se závod: {laps} kol, základní čas na kolo: {base_lap} sekund")

    results = simulate_race(laps, base_lap)
    print("\nVýsledky závodu:\n")
    for row in results:
        print(f"{row[0]:>4} | {row[1]:<15} | {row[2]:<20} | {row[3]:>10} | {row[4]}")
