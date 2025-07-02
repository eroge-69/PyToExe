
import json
import os

DATA_FILE = "marvel_watchlist.json"

marvel_list = [
    "Captain America: The First Avenger (1943–1945)",
    "Captain Marvel (1995)",
    "Iron Man (2010)",
    "Iron Man 2 (2011)",
    "The Incredible Hulk (2011)",
    "Thor (2011)",
    "The Avengers (2012)",
    "Iron Man 3 (2012)",
    "Thor: The Dark World (2013)",
    "Captain America: The Winter Soldier (2014)",
    "Guardians of the Galaxy (2014)",
    "Guardians of the Galaxy Vol. 2 (2014)",
    "Avengers: Age of Ultron (2015)",
    "Ant-Man (2015)",
    "Captain America: Civil War (2016)",
    "Black Widow (2016)",
    "Black Panther (2016)",
    "Spider-Man: Homecoming (2016)",
    "Doctor Strange (2016–2017)",
    "Thor: Ragnarok (2017)",
    "Ant-Man and the Wasp (2017)",
    "Avengers: Infinity War (2017)",
    "Avengers: Endgame (2018–2023)",
    "Loki – Season 1 (2012 Branch)",
    "WandaVision (2023)",
    "The Falcon and the Winter Soldier (2023)",
    "Shang-Chi and the Legend of the Ten Rings (2023)",
    "Eternals (2023)",
    "Spider-Man: Far From Home (2023)",
    "Spider-Man: No Way Home (2023)",
    "Doctor Strange in the Multiverse of Madness (2023)",
    "Ms. Marvel (2023)",
    "Thor: Love and Thunder (2023)",
    "She-Hulk (2024)",
    "Moon Knight (2024)",
    "Secret Invasion (2025)",
    "The Marvels (2025)",
    "Loki – Season 2 (Beyond Time)",
    "What If…? (Multiverse)"
]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {movie: False for movie in marvel_list}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def display_checklist(data):
    print("\n=== Marvel Timeline Checklist ===")
    for i, movie in enumerate(marvel_list):
        status = "✅" if data[movie] else "❌"
        print(f"{i + 1}. {status} {movie}")
    print("=================================\n")

def mark_watched(data):
    display_checklist(data)
    try:
        num = int(input("Enter movie/series number you watched: "))
        if 1 <= num <= len(marvel_list):
            data[marvel_list[num - 1]] = True
            print(f"Marked '{marvel_list[num - 1]}' as watched ✅")
        else:
            print("Invalid number!")
    except ValueError:
        print("Please enter a valid number.")

def main():
    data = load_data()
    while True:
        display_checklist(data)
        print("Options:\n1. Mark as Watched\n2. Exit")
        choice = input("Choose: ")
        if choice == "1":
            mark_watched(data)
            save_data(data)
        elif choice == "2":
            save_data(data)
            print("Goodbye! Your progress is saved.")
            break
        else:
            print("Invalid option!")

if __name__ == "__main__":
    main()
