#!/usr/bin/env python3
"""
Jersey Shore Adventure - a text-based game inspired by classic interactive fiction.

Save as jersey_shore_adventure.py and run with Python 3.8+.
"""
import random
import textwrap
import time
import sys

# Utility printing
def slowprint(text, delay=0.0, wrap=True):
    if wrap:
        text = textwrap.fill(text, width=78)
    print(text)
    if delay:
        time.sleep(delay)

def prompt(options, allow_quit=True):
    """
    options: list of strings displayed to user.
    returns index (0-based)
    """
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    if allow_quit:
        print("  0. Quit game")
    while True:
        choice = input("> ").strip()
        if choice == "" and len(options)==1:
            return 0
        if choice == "0" and allow_quit:
            confirm = input("Are you sure you want to quit? (y/n) ").lower()
            if confirm.startswith("y"):
                print("Goodbye!")
                sys.exit(0)
            else:
                continue
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return idx
        print("Please enter a number from the list.")

# Game data
male_names = ["Jacob","Mason","Ethan","Noah","William","Liam","Jayden","Michael","Alexander","Aiden"]
female_names = ["Sophia","Emma","Isabella","Olivia","Ava","Mia","Emily","Abigail","Madison","Elizabeth"]
all_names = list(set(male_names + female_names))
random.seed()

# Cost estimates (you can tweak)
COSTS = {
    "gas_roundtrip": 50.0,
    "food_per_person_day": 15.0,
    "beach_tag": 6.0,
    "rides_budget": 30.0,
    "boardwalk_games": 20.0,
    "souvenir": 15.0
}

# Player state
class Player:
    def __init__(self):
        self.gender = "unspecified"
        self.name = "Player"
        self.friends = []
        self.money = 0.0
        self.day = 0  # days until trip? We'll simulate two months as 60 days timeline
        self.days_available = 60
        self.trips_planned = False
        self.car_loaned = False
        self.parent_trust = 30  # 0-100, higher easier to borrow car
        self.reputation = 50    # influences small events
        self.earned_today = 0.0
        self.history = []

    def log(self, s):
        ts = f"[Day {self.day}]: "
        self.history.append(ts + s)

GAMES_TO_EARN = ["babysit", "mow_lawn", "dog_walk", "bake_sale", "garage_sale", "shift_at_store"]

def choose_friends(player):
    # pick 3 distinct names from early 2010s list, allow mix genders
    choices = random.sample(all_names, 3)
    player.friends = choices
    slowprint(f"You've chosen friends to go with: {', '.join(player.friends)}")

# Mini games to earn money
def earn_money_minigame(job):
    """
    Returns money earned and days spent.
    Some jobs have a small skill-based challenge.
    """
    if job == "babysit":
        slowprint("Babysitting: parents want someone reliable. Keep the kid entertained.")
        slowprint("Quick: Type the word 'story' as fast as you can and press Enter.")
        t0 = time.time()
        ans = input("> ").strip()
        elapsed = time.time() - t0
        if ans.lower() == "story" and elapsed < 6:
            earned = random.uniform(25, 40)
            text = "You told a great story and won the parent's trust."
        else:
            earned = random.uniform(12, 25)
            text = "It went okay — the kid fell asleep eventually."
        days = 1
    elif job == "mow_lawn":
        slowprint("Mowing lawns: physical job. Solve the quick puzzle.")
        a = random.randint(1, 12)
        b = random.randint(1, 12)
        slowprint(f"Quick: what is {a} + {b}?")
        try:
            ans = int(input("> ").strip())
        except:
            ans = None
        if ans == a + b:
            earned = random.uniform(30, 45)
            text = "Fast and accurate — you did a great job."
        else:
            earned = random.uniform(15, 30)
            text = "It was a slog but you finished."
        days = 1
    elif job == "dog_walk":
        slowprint("Dog walking: friendly but unpredictable.")
        choice = prompt(["Walk for an hour (safe, steady pay)", "Walk for two hours (riskier, more pay)"], allow_quit=False)
        if choice == 0:
            earned = random.uniform(10, 20); days = 0.5; text = "Short walk, steady tips."
        else:
            # chance of dog pulling you into puddle -> less pay
            if random.random() < 0.2:
                earned = random.uniform(2, 10); text = "The dog bolted and you had a rough hour."
            else:
                earned = random.uniform(25, 40); text = "Long walk, good tips."
            days = 1
    elif job == "bake_sale":
        slowprint("Bake sale: creative! You set prices and decide product.")
        choice = prompt(["Sell cookies (safe)", "Sell cupcakes (popular)", "Sell giant brownies (expensive)"], allow_quit=False)
        if choice == 0:
            earned = random.uniform(10, 30); text = "Cookies sell okay."
        elif choice == 1:
            earned = random.uniform(30, 60); text = "Cupcakes were a hit!"
        else:
            earned = random.uniform(20, 70) if random.random() < 0.8 else random.uniform(0, 10)
            text = "Brownies mostly sell — if they do, big profit."
        days = 1
    elif job == "garage_sale":
        slowprint("Garage sale: you and friends clear out stuff.")
        earned = random.uniform(40, 120)
        days = 1
        text = "You found a few real gems to sell."
    elif job == "shift_at_store":
        slowprint("Short shift at a local store. You need to balance speed and accuracy.")
        slowprint("Type 'scan' then Enter as fast as you can five times.")
        hits = 0
        t0 = time.time()
        for i in range(5):
            if input("> ").strip().lower() == "scan":
                hits += 1
        elapsed = time.time() - t0
        if hits >= 4 and elapsed < 12:
            earned = random.uniform(60, 90)
            text = "You were fast and friendly — good tips."
        else:
            earned = random.uniform(30, 50)
            text = "You finished the shift; it was okay."
        days = 1
    else:
        earned = 0; days = 0; text = "Nothing happened."
    slowprint(text)
    return earned, days

# Persuasion to borrow car
def persuade_parent(player):
    slowprint("You need to persuade a parent to borrow their car. They are hesitant.")
    slowprint("You can choose your approach: honesty, bargain, or show responsibility.")
    choice = prompt(["Honest plea (appeal to trust)", "Bargain (offer chores/money)", "Demonstrate responsibility (plan and schedule)"], allow_quit=False)
    # Each option uses player's reputation and parent_trust to compute chance
    base = player.parent_trust + (player.reputation - 50)
    if choice == 0:
        chance = base + random.randint(-15, 15)
    elif choice == 1:
        chance = base + 10 + random.randint(-10, 10)
    else:
        chance = base + 20 + random.randint(-8, 8)
    slowprint("You present your case...")
    time.sleep(1)
    if chance > 50:
        slowprint("The parent reluctantly agrees to lend the car — but with conditions.")
        player.car_loaned = True
        player.parent_trust += 10
        player.log("Parent agreed to loan the car (reluctantly).")
        return True
    else:
        slowprint("No luck — the parent says no for now. You can try again later after improving trust.")
        player.parent_trust -= 5
        player.log("Parent refused to loan the car.")
        return False

# Trip planning and budget
def calculate_trip_cost(player, group_size):
    # simple model: gas, food for one day at shore, beach tags per person, rides budget, souvenirs
    gas = COSTS["gas_roundtrip"]
    food = COSTS["food_per_person_day"] * group_size * 1  # assume 1 day
    beach_tags = COSTS["beach_tag"] * group_size
    rides = COSTS["rides_budget"]
    games = COSTS["boardwalk_games"]
    souvenir = COSTS["souvenir"] * group_size
    total = gas + food + beach_tags + rides + games + souvenir
    details = {
        "gas": gas,
        "food": food,
        "beach_tags": beach_tags,
        "rides": rides,
        "games": games,
        "souvenir": souvenir,
        "total": total
    }
    return details

def display_budget(details):
    slowprint("Estimated trip budget breakdown:")
    for k, v in details.items():
        slowprint(f"  {k.replace('_',' ').title():15s} : ${v:.2f}", wrap=False)
    slowprint(f"  {'-'*30}\n  TOTAL             : ${details['total']:.2f}")

# Main gameplay loop
def play_game():
    player = Player()
    slowprint("Welcome to 'Jersey Shore Adventure' — plan a trip from Delaware County, PA to the Jersey Shore!")
    # Gender and name
    slowprint("Do you want to be male or female?")
    g = prompt(["Male", "Female"], allow_quit=False)
    player.gender = "male" if g == 0 else "female"
    player.name = input("Enter your name: ").strip() or ("Alex" if player.gender=="male" else "Taylor")
    slowprint(f"Great — you're {player.name}.")
    choose_friends(player)
    slowprint("You and your friends started planning 2 months ahead. Let's set a budget target.")
    group_size = 1 + len(player.friends)
    details = calculate_trip_cost(player, group_size)
    display_budget(details)
    slowprint(f"You have {player.days_available} days to prepare. Let's earn money, build trust, and plan.")
    player.log("Began planning the Jersey Shore trip.")
    # Main planning loop: allow up to N actions or until trip achieved
    while True:
        slowprint(f"\nDay progress: You have {player.days_available - player.day} days left before the trip.")
        slowprint(f"Current money: ${player.money:.2f}")
        options = [
            "Do an earning job (earn money)",
            "View trip budget details",
            "Try to persuade a parent to lend their car",
            "Plan logistics (what to pack, who drives)",
            "Spend a day social: increase reputation/parental trust",
            "Attempt a quick side challenge for extra cash",
            "Check mission status & attempt final trip (if ready)"
        ]
        choice = prompt(options, allow_quit=False)
        if choice == 0:
            slowprint("Pick a job to do today:")
            job_choice = prompt(["Babysit", "Mow lawn", "Dog walk", "Bake sale", "Garage sale", "Shift at store"], allow_quit=False)
            job = GAMES_TO_EARN[job_choice]
            earned, days_spent = earn_money_minigame(job)
            # Convert half-days to integer day increments for simplicity
            player.money += earned
            player.day += int(max(1, days_spent))
            player.earned_today = earned
            player.log(f"Earned ${earned:.2f} from {job}.")
            slowprint(f"You earned ${earned:.2f}.")
        elif choice == 1:
            display_budget(details)
        elif choice == 2:
            success = persuade_parent(player)
            if success:
                slowprint("You must follow the conditions your parent set — be punctual and responsible.")
            else:
                slowprint("Try building more trust: do chores, show planning, or earn more money to offer.")
        elif choice == 3:
            slowprint("Logistics planning: choose your transportation plan.")
            plan = prompt(["Ask to borrow the parent's car (requires persuasion)", "Take the bus (cheaper but less flexible)", "Rent a car split among friends (expensive)"], allow_quit=False)
            if plan == 0:
                slowprint("You decide to prepare a full plan to show the parent (return time, gas share, emergency contact).")
                player.reputation += 5
                player.log("Prepared a neat driving plan to impress parent.")
            elif plan == 1:
                bus_cost = 20 * group_size
                slowprint(f"Bus option would cost around ${bus_cost:.2f} total. You can choose to reserve it when you have the money.")
            else:
                rent_cost = 120.0
                slowprint(f"Renting a car for the day would cost approx ${rent_cost:.2f} split among the group.")
        elif choice == 4:
            slowprint("Social day: Do a favor, help around the house, and build trust.")
            player.parent_trust += random.randint(1, 6)
            player.reputation += random.randint(0, 4)
            player.day += 1
            player.log("Spent a social day improving trust and reputation.")
            slowprint("You did some chores and talked responsibly with your parents. Trust increased.")
        elif choice == 5:
            # Quick challenge
            slowprint("Quick challenge: a fast reaction test. Type 'ready' then when the word 'GO!' appears type 'go'.")
            if input("Type 'ready' and press Enter: ").strip().lower() == "ready":
                wait = random.uniform(1.0, 3.0)
                slowprint("Get ready... (wait for GO!)", delay=0.7)
                time.sleep(wait)
                print("GO!")
                t0 = time.time()
                ans = input().strip().lower()
                elapsed = time.time() - t0
                if ans == "go" and elapsed < 1.5:
                    bonus = random.uniform(10, 40)
                    player.money += bonus
                    player.log(f"Quick challenge success: +${bonus:.2f}")
                    slowprint(f"Nice reflexes — you got an extra ${bonus:.2f}.")
                else:
                    slowprint("You hesitated — no bonus this time.")
            else:
                slowprint("You weren't ready. No bonus.")
        elif choice == 6:
            # Check if ready to attempt final trip
            slowprint("Final trip attempt: do you want to see if you can go now?")
            proceed = prompt(["Attempt the trip now (spend money and try to arrange car/transport)", "Keep preparing"], allow_quit=False)
            if proceed == 1:
                continue
            # Attempt trip
            details = calculate_trip_cost(player, group_size)
            total_needed = details["total"]
            slowprint(f"Total needed: ${total_needed:.2f}. You currently have ${player.money:.2f}.")
            if player.money < total_needed:
                slowprint("You don't have enough money yet. Keep earning or cut costs.")
                # Offer cost-cutting: skip rides, souvenirs, or camp for cheaper food
                cut = prompt(["Cut rides budget ($20 saved)", "Skip souvenirs ($15/person saved)", "Try bus instead of car (save $30)","Cancel attempt"], allow_quit=False)
                if cut == 0:
                    details["rides"] -= 20; total_needed -= 20
                elif cut == 1:
                    details["souvenir"] -= 15*group_size; total_needed -= 15*group_size
                elif cut == 2:
                    details["gas"] -= 30; total_needed -= 30
                else:
                    slowprint("You decide not to attempt the trip yet.")
                    continue
                slowprint("Adjusted budget:")
                display_budget(details)
                if player.money < total_needed:
                    slowprint("Still not enough. Back to planning.")
                    continue
            # Now check transport: car loaned or not
            if not player.car_loaned:
                slowprint("You don't yet have the car arranged.")
                method = prompt(["Try persuading parent now", "Take the bus"], allow_quit=False)
                if method == 0:
                    ok = persuade_parent(player)
                    if not ok:
                        slowprint("Parent refused. You must take the bus or cancel.")
                        take_bus = True
                    else:
                        take_bus = False
                else:
                    take_bus = True
            else:
                take_bus = False
            # If bus, adjust costs and proceed
            if take_bus:
                slowprint("Taking the bus: more rigid schedule, but doable.")
                player.money -= total_needed
                player.log("Took bus trip to Jersey Shore.")
                conclude_trip(player, details, group_size, took_bus=True)
                return
            else:
                # Car. Check parent's final condition; maybe they set rules.
                slowprint("Using parent's car. You must promise to follow curfew and share gas money.")
                share_gas = total_needed * 0.0  # already included
                player.money -= total_needed
                player.log("Borrowed car and went to Jersey Shore.")
                conclude_trip(player, details, group_size, took_bus=False)
                return

def conclude_trip(player, details, group_size, took_bus=False):
    slowprint("\n--- TRIP DAY ---")
    slowprint("You and your friends arrive at the Jersey Shore. The sun, the smell of saltwater, the boardwalk lights — it's everything you hoped.")
    # Narrative choices on day at shore
    slowprint("How do you spend your first hours?")
    options = ["Beach first (relax, swim)", "Boardwalk rides and games", "Split time: beach then boardwalk"]
    choice = prompt(options, allow_quit=False)
    if choice == 0:
        slowprint("You set up towels, take turns with music, and build a sand fort. Beach tags checked, laughs shared.")
        joy = 10
    elif choice == 1:
        slowprint("You ride the big roller coaster, beat an arcade high score, and win a ridiculous stuffed animal.")
        joy = 12
    else:
        slowprint("You split the day. A few rides and then a calming sunset on the beach.")
        joy = 11
    # Random event: rainy wind
    if random.random() < 0.12:
        slowprint("A sudden summer rain sends everyone under the boardwalk roof. You trade soggy fries for goofy stories.")
        joy -= 2
    slowprint(f"After a day of fun, you head home. You spent ${details['total']:.2f} in total as planned.")
    slowprint("On the way back, your group is quiet, tired, but glowing: the trip succeeded.")
    if took_bus:
        slowprint("Taking the bus was less flexible but everyone enjoyed it and the memories were worth it.")
    else:
        slowprint("The parent's car made the trip smooth — you repaid them and kept your promises, which strengthened trust at home.")
        player.parent_trust += 10
    slowprint("You return home, the friends already talking about the next small adventure.")
    player.log("Trip completed successfully.")
    slowprint("\n--- END ---\nThanks for playing Jersey Shore Adventure!")
    # show a short summary
    slowprint("Trip summary:")
    slowprint(f"  Player name: {player.name}")
    slowprint(f"  Final trust with parent: {player.parent_trust}")
    slowprint(f"  Final reputation: {player.reputation}")
    slowprint("  Events log (recent):")
    for e in player.history[-6:]:
        slowprint(f"    {e}")
    return

if __name__ == "__main__":
    try:
        play_game()
    except KeyboardInterrupt:
        print("\nGame interrupted. Goodbye!")
