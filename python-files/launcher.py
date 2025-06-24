import os
import subprocess

# ⚡️ KONFIGURACJA
CITRIN_PATH = r"C:\ścieżka\do\citrin.exe"           # <-- tu ustaw ścieżkę do Citrin
GAMES_FOLDER = r"C:\ścieżka\do\gier_switch"           # <-- tu ustaw ścieżkę do folderu z grami (.nsp)

def list_games(folder):
    """Zwrot listy plików .nsp w wybranym katalogu."""
    files = [f for f in os.listdir(folder) if f.endswith('.nsp') or f.endswith('.xci')]
    return files

def launch_game(game_name):
    """Uruchamia grę poprzez Citrin."""
    game_path = os.path.join(GAMES_FOLDER, game_name)
    subprocess.Popen([CITRIN_PATH, game_path])

def main():
    games = list_games(GAMES_FOLDER)

    if not games:
        print("❌ Brak gier w katalogu:", GAMES_FOLDER)
        return

    # Wyświetlenie listy gier
    print("\n🎮 Wybierz grę do uruchomienia:\n")
    for idx, game in enumerate(games, 1):
        print(f"[{idx}] {game}")

    choice = input("\n👉 Wybierz numer gry: ")

    try:
        choice = int(choice) - 1
        if 0 <= choice < len(games):
            selected_game = games[choice]
            print(f"▶️ Uruchamiam: {selected_game}")
            launch_game(selected_game)
        else:
            print("❌ Błędny numer gry.")
    except ValueError:
        print("❌ Podaj poprawny numer.")

if __name__ == "__main__":
    main()