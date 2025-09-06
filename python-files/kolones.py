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
    print("=== Column Rebar Calculator ===")
    floors = int(input("Number of floors: "))
    
    heights = []
    for i in range(floors):
        h = float(input(f"Height of floor {i+1} (m): "))
        heights.append(h)
    
    total_columns = int(input("Total number of columns: "))
    
    columns_per_floor = []
    for i in range(floors):
        c = int(input(f"Columns continuing on floor {i+1}: "))
        columns_per_floor.append(c)
    
    dia = float(input("Rebar diameter (mm): "))
    bar_length = float(input("Bar length (e.g. 12, 14, 16): "))
    with_wait = input("With waiting length (yes/no): ").lower() in ["yes", "y"]
    
    wait = 60 * dia / 1000 if with_wait else 0.0
    
    cuts = []
    for i in range(floors):
        length = heights[i] + wait
        cuts += [length] * columns_per_floor[i]
    
    print("\n--- Cuts ---")
    print([round(c, 2) for c in cuts])
    
    bars, waste = cut_bars(bar_length, cuts)
    
    print("\n--- Cutting Result ---")
    for i, bar in enumerate(bars, 1):
        used = sum(bar)
        print(f"Bar {i}: {bar} (Total {used:.2f}m, Waste {bar_length - used:.2f}m)")
    
    print(f"\nTotal Waste: {waste:.2f} m ({(waste/(len(bars)*bar_length))*100:.2f}%)")
    print(f"Total bars: {len(bars)}")


if name == "main":
    main()