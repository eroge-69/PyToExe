#!/usr/bin/env python3
"""
Simple Elo Rating Manager (CLI)
- Option 1: Add Result
- Option 2: Current Rankings
- Option 3: Quit

Data is stored in ./elo_data.json
"""

import json
import math
import os
from typing import Dict, Tuple

DATA_FILE = "elo_data.json"
DEFAULT_RATING = 1500
DEFAULT_K = 32  # You can tweak this if you like

# ------------------ Storage ------------------

def load_data() -> Dict[str, float]:
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Ensure keys are strings and values are floats
        return {str(k): float(v) for k, v in data.items()}
    except Exception:
        # If file is corrupted, start fresh (and keep a backup)
        if os.path.exists(DATA_FILE):
            os.rename(DATA_FILE, DATA_FILE + ".bak")
        return {}

def save_data(ratings: Dict[str, float]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(ratings, f, indent=2, ensure_ascii=False)

# ------------------ Elo Core ------------------

def expected_score(r_a: float, r_b: float) -> float:
    """Expected score for A vs B (0..1)."""
    return 1.0 / (1.0 + 10 ** ((r_b - r_a) / 400.0))

def update_elo(r_a: float, r_b: float, score_a: float, k: float = DEFAULT_K) -> Tuple[float, float]:
    """
    Update ratings for a single game.
    score_a: 1 for A win, 0 for A loss, 0.5 for draw.
    Returns: (new_r_a, new_r_b)
    """
    e_a = expected_score(r_a, r_b)
    e_b = 1.0 - e_a
    score_b = 1.0 - score_a
    new_a = r_a + k * (score_a - e_a)
    new_b = r_b + k * (score_b - e_b)
    return new_a, new_b

# ------------------ Actions ------------------

def add_result(ratings: Dict[str, float]) -> None:
    print("\n=== Add Result ===")
    a = input("Player A name: ").strip()
    b = input("Player B name: ").strip()
    if not a or not b:
        print("Both player names are required.")
        return
    if a.lower() == b.lower():
        print("Players must be different.")
        return

    # Create players if new
    if a not in ratings:
        ratings[a] = DEFAULT_RATING
        print(f"Created {a} at {DEFAULT_RATING}.")
    if b not in ratings:
        ratings[b] = DEFAULT_RATING
        print(f"Created {b} at {DEFAULT_RATING}.")

    print("\nResult options:")
    print("  1 = A wins")
    print("  2 = B wins")
    print("  3 = Draw")
    res = input("Enter result (1/2/3): ").strip()

    if res == "1":
        score_a = 1.0
    elif res == "2":
        score_a = 0.0
    elif res == "3":
        score_a = 0.5
    else:
        print("Invalid selection.")
        return

    # Optional: custom K-factor per match
    k_in = input(f"K-factor (press Enter for default {DEFAULT_K}): ").strip()
    k_val = DEFAULT_K
    if k_in:
        try:
            k_val = float(k_in)
            if k_val <= 0:
                raise ValueError
        except ValueError:
            print("Invalid K; using default.")
            k_val = DEFAULT_K

    old_a, old_b = ratings[a], ratings[b]
    new_a, new_b = update_elo(old_a, old_b, score_a, k=k_val)

    ratings[a], ratings[b] = new_a, new_b
    save_data(ratings)

    # Show a quick summary
    def delta(n, o): 
        d = n - o
        sign = "+" if d >= 0 else ""
        return f"{n:.1f} ({sign}{d:.1f})"

    print("\nUpdated ratings:")
    print(f"  {a}: {delta(new_a, old_a)}")
    print(f"  {b}: {delta(new_b, old_b)}")

def current_rankings(ratings: Dict[str, float]) -> None:
    print("\n=== Current Rankings ===")
    if not ratings:
        print("No players yet. Add a result first.")
        return
    ordered = sorted(ratings.items(), key=lambda kv: kv[1], reverse=True)

    name_w = max(5, max(len(name) for name, _ in ordered))
    print(f"{'#':>3}  {'Player'.ljust(name_w)}  {'Rating':>8}")
    print("-" * (7 + name_w + 10))
    for i, (name, rating) in enumerate(ordered, start=1):
        print(f"{i:>3}  {name.ljust(name_w)}  {rating:>8.1f}")

# ------------------ CLI Loop ------------------

def main():
    ratings = load_data()
    while True:
        print("\n--- Elo Rating Manager ---")
        print("1) Add Result")
        print("2) Current Rankings")
        print("3) Quit")
        choice = input("Choose an option (1-3): ").strip()

        if choice == "1":
            add_result(ratings)
        elif choice == "2":
            current_rankings(ratings)
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()