def cut_bars(bar_length, cuts):
    cuts = sorted(cuts, reverse=True)
    bars = []
    
    for cut in cuts:
        placed = False
        for bar in bars:
            if sum(bar) + cut <= bar_length:
                bar.append(cut)
                placed = True
                break
        if not placed:
            bars.append([cut])
    
    waste = sum(bar_length - sum(bar) for bar in bars)
    return bars, waste


def main():
    print("=== Υπολογισμός Σιδήρου για Κολώνες ===")
    floors = int(input("Δώσε αριθμό ορόφων: "))
    
    heights = []
    for i in range(floors):
        h = float(input(f"Ύψος ορόφου {i+1} (m): "))
        heights.append(h)
    
    total_columns = int(input("Πόσες κολώνες έχουμε συνολικά; "))
    
    columns_per_floor = []
    for i in range(floors):
        c = int(input(f"Πόσες κολώνες συνεχίζουν στον όροφο {i+1}; "))
        columns_per_floor.append(c)
    
    dia = float(input("Διάμετρος σιδήρου (mm): "))
    bar_length = float(input("Μήκος ράβδου (π.χ. 12, 14, 16): "))
    with_wait = input("Με αναμονή (ναι/όχι): ").lower() in ["ναι", "nai", "yes", "y"]
    
    wait = 60 * dia / 1000 if with_wait else 0.0
    
    cuts = []
    for i in range(floors):
        length = heights[i] + wait
        cuts += [length] * columns_per_floor[i]
    
    print("\n--- Υπολογισμένα Κοψίματα ---")
    print([round(c, 2) for c in cuts])
    
    bars, waste = cut_bars(bar_length, cuts)
    
    print("\n--- Αποτέλεσμα Κοπών ---")
    for i, bar in enumerate(bars, 1):
        used = sum(bar)
        print(f"Ράβδος {i}: {bar} (Σύνολο {used:.2f}m, Φύρα {bar_length - used:.2f}m)")
    
    print(f"\nΣυνολική Φύρα: {waste:.2f} m ({(waste/(len(bars)*bar_length))*100:.2f}%)")
    print(f"Συνολικές ράβδοι: {len(bars)}")


if name == "main":
    main()