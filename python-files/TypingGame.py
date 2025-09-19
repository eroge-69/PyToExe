import random
import time
from datetime import datetime

# --- ANSI Color Codes ---
RESET = '\033[0m'
BOLD = '\033[1m'

# Text Colors
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
WHITE = '\033[97m'
BLUE = '\033[94m'

# Background Colors (for banners)
BG_BLUE = '\033[44m'
BG_GREEN = '\033[42m'
BG_RED = '\033[41m'

# --- Word Lists ---
level1_words = [
    "apple", "banana", "cat", "dog", "elephant", "fish", "grape", "house", "ice", "juice",
    "kite", "lion", "moon", "nose", "orange", "pig", "queen", "rose", "sun", "tree",
    "umbrella", "van", "water", "xray", "yarn", "zebra", "ball", "car", "desk", "egg"
]

level2_words = [
    "academy", "balance", "capture", "deliver", "energy", "fashion", "gallery", "harmony",
    "identity", "justice", "kingdom", "library", "mystery", "natural", "observe", "passion",
    "quality", "respect", "science", "theory", "update", "victory", "window", "youth",
    "zephyr", "ancient", "benefit", "courage", "dynamic", "element", "fortune", "gravity",
    "honest", "imagine", "journey", "knowledge", "lounge", "mission", "network", "option",
    "pattern", "quiet", "random", "symbol", "texture", "unique", "variety", "wisdom",
    "xenon", "yield", "zodiac", "alliance", "biology", "charity", "dialogue", "ecology",
    "freedom", "growth", "horizon", "insight"
]

level3_words = [
    "abundance", "benevolent", "capricious", "diligence", "eloquence", "fortitude", "gregarious",
    "hypothesis", "impeccable", "juxtapose", "kinesthetic", "labyrinth", "magnanimous", "nebulous",
    "obfuscate", "paradigm", "quintessential", "resilient", "sagacious", "transcend", "ubiquitous",
    "venerable", "wanderlust", "xenophobia", "yearning", "zealous", "acrimonious", "belligerent",
    "cognizant", "disparate", "enervate", "facetious", "garrulous", "harangue", "idiosyncrasy",
    "juxtaposition", "kaleidoscope", "languid", "meticulous", "nonchalant", "ostracize", "precocious",
    "quixotic", "recalcitrant", "serendipity", "tantamount", "umbrage", "vicissitude", "winsome",
    "xerophilous", "yokel", "zephyr", "ameliorate", "bombastic", "catalyst", "deleterious", "ephemeral",
    "fastidious", "grandiloquent", "hedonist", "inscrutable", "jocular", "knell", "lethargic",
    "mellifluous", "nadir", "obsequious", "pusillanimous", "quandary", "recalcitrant", "sanctimonious",
    "temerity", "usurp", "vicissitude", "wizened", "xenial", "yoke", "zealot", "anachronistic",
    "bucolic", "circumspect", "defenestrate", "elucidate", "flagrant", "grandiose", "hubris",
    "impetuous", "jettison", "kismet"
]

# --- Score Logging ---
def log_score(name, score):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("scores.txt", "a") as file:
        file.write(f"Name: {name}, Score: {score}, Date: {timestamp}\n")

def display_scores():
    try:
        with open("scores.txt", "r") as file:
            print(f"\n{BOLD}{CYAN}========== SCOREBOARD =========={RESET}")
            print(file.read())
            print(f"{BOLD}{CYAN}===============================\n{RESET}")
    except FileNotFoundError:
        print(f"{RED}No scores logged yet.{RESET}")

# --- Game Logic ---
def play_level(words, level_num, current_score):
    print(f"\n{BG_BLUE}{WHITE}{BOLD}   LEVEL {level_num} - Type all words within 200s!   {RESET}\n")
    words_to_type = words.copy()
    random.shuffle(words_to_type)
    start_time = time.time()
    time_limit = 200  # seconds

    for word in words_to_type:
        elapsed = time.time() - start_time
        remaining = time_limit - elapsed
        if remaining <= 0:
            print(f"\n{BG_RED}{WHITE}{BOLD}   Time's up!   {RESET}\n")
            return False, current_score

        print(f"{YELLOW}Word: {BOLD}{word}{RESET}")
        print(f"{CYAN}Time remaining: {int(remaining)} seconds{RESET}")
        typed = input(f"{GREEN}Your input: {RESET}").strip()

        if typed != word:
            print(f"\n{BG_RED}{WHITE}{BOLD}   Wrong! The correct word was '{word}'.   {RESET}\n")
            return False, current_score

        current_score += 10
        print(f"{GREEN}✓ Correct! +10 points{RESET}\n")

    print(f"{BG_GREEN}{WHITE}{BOLD}   Congrats! You completed Level {level_num}!   {RESET}\n")
    return True, current_score

# --- Main ---
def main():
    print(f"{BOLD}{CYAN}\n===============================")
    print("  WELCOME TO THE TYPING GAME  ")
    print("===============================\n" + RESET)

    name = input(f"{WHITE}What is your name? {RESET}")
    print(f"\n{GREEN}Good luck, {BOLD}{name}{RESET}{GREEN}! Type all words correctly to advance.{RESET}\n")

    total_score = 0

    passed, total_score = play_level(level1_words, 1, total_score)
    if not passed:
        print(f"{RED}Game Over. Try again! Your score: {total_score}{RESET}")
        log_score(name, total_score)
        display_scores()
        return

    passed, total_score = play_level(level2_words, 2, total_score)
    if not passed:
        print(f"{RED}Game Over. Try again! Your score: {total_score}{RESET}")
        log_score(name, total_score)
        display_scores()
        return

    passed, total_score = play_level(level3_words, 3, total_score)
    if not passed:
        print(f"{RED}Game Over. Try again! Your score: {total_score}{RESET}")
        log_score(name, total_score)
        display_scores()
        return

    print(f"\n{BG_GREEN}{WHITE}{BOLD}   Amazing {name}! You completed all levels!   {RESET}\n")
    print(f"{CYAN}Your final score: {BOLD}{total_score}{RESET}\n")
    log_score(name, total_score)
    display_scores()

if __name__ == "__main__":
    main()
