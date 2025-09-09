import pandas as pd
import random

def lucky_draw(input_file, output_file, num_winners):
    # Read Excel file
    df = pd.read_excel(input_file)
    
    # Expand list based on number of chances
    pool = []
    for _, row in df.iterrows():
        pool.extend([row['Name']] * int(row['Number of Chances']))
    
    # Ensure we don't ask for more winners than unique participants
    unique_names = list(set(pool))
    if num_winners > len(unique_names):
        raise ValueError("Number of winners exceeds number of unique entrants.")
    
    winners = []
    
    # Draw winners without replacement by removing them from the pool
    for _ in range(num_winners):
        winner = random.choice(pool)
        winners.append(winner)
        # Remove ALL instances of this winner from the pool
        pool = [name for name in pool if name != winner]
    
    # Save to Excel
    winners_df = pd.DataFrame(winners, columns=["Winner"])
    winners_df.to_excel(output_file, index=False)
    
    print("\n🎉 Lucky draw results 🎉")
    for i, w in enumerate(winners, 1):
        print(f"{i}. {w}")
    print(f"\n✅ {num_winners} winners saved to {output_file}\n")


if __name__ == "__main__":
    # Ask user for inputs
    input_file = input("Enter the path to the entrants Excel file (e.g., entrants.xlsx): ").strip()
    output_file = input("Enter the output file name (e.g., winners.xlsx): ").strip()
    num_winners = int(input("Enter the number of winners: ").strip())
    
    lucky_draw(input_file, output_file, num_winners)
