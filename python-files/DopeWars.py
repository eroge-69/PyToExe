# dope_wars_text.py
# A fully featured, text-based Python version of Dope Wars (single-file).
# Runs in a terminal. Save as dope_wars_text.py and run with:  python dope_wars_text.py

import os
import json
import math
import random
import textwrap
from collections import defaultdict

GAME_DAYS = 30
START_CASH = 2000
DAILY_INTEREST = 0.10  # 10%
VET_COST = 200
VET_HEAL = 30          # restore per visit
MAX_HEALTH = 100

ARMOR_COST = 1000
ARMOR_HEALTH = 25
HELMET_COST = 2000
HELMET_HEALTH = 50

SALESMAN_TRAVEL_CHANCE = 0.20
ATTACK_BASE_CHANCE = 0.05  # when days_overdue >= 5
ATTACK_DAMAGE_MIN = 5
ATTACK_DAMAGE_MAX = 20

POLICE_RAID_DAILY = 0.01
BAG_FIND_DAILY = 0.05

HIGHSCORE_FILE = "dope_wars_highscore.json"

DIV = "=" * 72
SUBDIV = "-" * 72

DRUGS = [
    # name, (min, max), bulk
    ("Weed", (20, 200), 2),
    ("Shrooms", (50, 400), 2),
    ("Ketamin", (75, 450), 2),
    ("Meph", (100, 500), 2),
    ("MDMA", (150, 550), 2),
    ("Acid", (200, 600), 2),
    ("Cocaine", (1000, 3000), 2),
    ("Heroin", (1500, 4000), 2),
]

LOCATIONS = [
    "Northampton",  # starting
    "Essex",
    "London",       # +10% all prices
    "Scotland",
    "Newcastle",
    "Sittingbourne",
    "Southampton",
]

TAUNTS = {
    "small": [
        "Shark: \"I know where you live, kid. Don't keep me waiting.\"",
        "Shark: \"Pennies today... problems tomorrow.\"",
    ],
    "medium": [
        "Shark: \"Debt's getting spicy. I like spicy. You won't.\"",
        "Shark: \"Tick-tock. Interest don't sleep.\"",
    ],
    "high": [
        "Shark: \"Your tab could buy me a boat. Pay up or swim!\"",
        "Shark: \"You're on my calendar... every day.\"",
    ],
    "extreme": [
        "Shark: \"Congratulations. You're my retirement plan.\"",
        "Shark: \"Run if you want. I own the map.\"",
    ],
}

def clear():
    # light clear for most terminals
    os.system('cls' if os.name == 'nt' else 'clear')

def press_enter():
    input("\n(Press ENTER to continue) ")

def load_highscore():
    if not os.path.exists(HIGHSCORE_FILE):
        return 0
    try:
        with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return int(data.get("highscore", 0))
    except Exception:
        return 0

def save_highscore(score):
    existing = load_highscore()
    if score > existing:
        try:
            with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
                json.dump({"highscore": int(score)}, f)
        except Exception:
            pass

def format_money(x):
    return f"${int(x):,}"

def wrap(s):
    return textwrap.fill(s, width=68)

def weighted_average(old_avg, old_qty, added_qty, price):
    if old_qty <= 0:
        return float(price)
    return (old_avg * old_qty + price * added_qty) / (old_qty + added_qty)

class Player:
    def __init__(self):
        self.cash = START_CASH
        self.bank = 0
        self.debt = 0
        self.health = MAX_HEALTH

        # overdue tracker
        self.days_overdue = 0
        self.paid_debt_today = False

        # inventory: name -> {"qty": int, "avg": float}
        self.inv = {name: {"qty": 0, "avg": 0.0} for name, _, _ in DRUGS}

        # gear
        self.armor = False
        self.helmet = False

    def net_worth(self, market_prices):
        # score as requested: cash + value of drugs - debt
        value = 0
        for name in self.inv:
            qty = self.inv[name]["qty"]
            price = market_prices.get(name, 0)
            value += qty * price
        return int(self.cash + value - self.debt)

    def has_gear(self):
        g = []
        if self.armor: g.append("Armor")
        if self.helmet: g.append("Helmet")
        return ", ".join(g) if g else "None"

    def damage_reduction_multiplier(self):
        # Damage reduction from shark attacks
        mult = 1.0
        if self.armor:
            mult *= 0.75  # 25% reduction
        if self.helmet:
            mult *= 0.50  # additional 50% reduction
        return mult

    def attack_chance_modifier(self, base):
        # reduce chance if geared
        if self.armor and self.helmet:
            return max(0.02, base - 0.03)  # 2%
        elif self.helmet:
            return max(0.03, base - 0.02)  # 3%
        elif self.armor:
            return max(0.04, base - 0.01)  # 4%
        return base

class Market:
    def __init__(self):
        # prices[location][drug] = price for current day
        self.prices = {}

    def roll_daily_prices(self):
        self.prices = {}
        for loc in LOCATIONS:
            self.prices[loc] = {}
            for name, (lo, hi), _ in DRUGS:
                price = random.randint(lo, hi)
                if loc == "London":
                    price = math.ceil(price * 1.10)  # +10%
                self.prices[loc][name] = price

    def get_prices(self, location):
        return self.prices.get(location, {})

def print_header(day, location, player, market, highscore, show_score=True):
    clear()
    print(DIV)
    print(f" DOPE WARS — Day {day}/{GAME_DAYS} — Location: {location}")
    print(DIV)
    prices = market.get_prices(location)
    score = player.net_worth(prices)
    print(f" Cash: {format_money(player.cash)}   Bank: {format_money(player.bank)}   Debt: {format_money(player.debt)}")
    print(f" Health: {player.health}/{MAX_HEALTH}   Gear: {player.has_gear()}")
    if show_score:
        print(f" Score (cash + stash value - debt): {format_money(score)}   Highscore: {format_money(highscore)}")
    print(SUBDIV)

def print_market(location, market, player):
    prices = market.get_prices(location)
    print(" MARKET (All bulk = 2)")
    print(f" {'Drug':<12} {'Price':>10} | {'Owned':>6} {'Avg Cost':>10}")
    print(SUBDIV)
    for name, _, _ in DRUGS:
        price = prices[name]
        owned = player.inv[name]["qty"]
        avg = player.inv[name]["avg"]
        avg_s = format_money(avg) if owned > 0 else "-"
        print(f" {name:<12} {format_money(price):>10} | {owned:>6} {avg_s:>10}")
    print(SUBDIV)

def taunt_for_debt(debt):
    if debt <= 0:
        return None
    if debt < 5000:
        pool = TAUNTS["small"]
    elif debt < 20000:
        pool = TAUNTS["medium"]
    elif debt < 50000:
        pool = TAUNTS["high"]
    else:
        pool = TAUNTS["extreme"]
    return random.choice(pool)

def police_raid(player):
    seized = sum(player.inv[name]["qty"] for name, _, _ in DRUGS)
    for name, _, _ in DRUGS:
        player.inv[name]["qty"] = 0
        player.inv[name]["avg"] = 0.0
    return seized

def bag_on_ground(player):
    name, _, _ = random.choice(DRUGS)
    found = random.randint(1, 50)
    current = player.inv[name]
    # free stash: adjust average price toward 0 properly
    new_qty = current["qty"] + found
    if new_qty > 0:
        current["avg"] = (current["avg"] * current["qty"]) / new_qty
    current["qty"] = new_qty
    return name, found

def apply_interest_and_overdue(player):
    # Apply daily interest
    if player.debt > 0:
        interest = math.ceil(player.debt * DAILY_INTEREST)
        player.debt += interest
        if not player.paid_debt_today:
            player.days_overdue += 1
    else:
        player.days_overdue = 0

    # Reset today's payment flag for the next day
    player.paid_debt_today = False

def loan_shark_attack_check(player):
    if player.debt <= 0:
        return None
    if player.days_overdue < 5:
        return None
    chance = player.attack_chance_modifier(ATTACK_BASE_CHANCE)
    if random.random() < chance:
        dmg = random.randint(ATTACK_DAMAGE_MIN, ATTACK_DAMAGE_MAX)
        dmg = max(1, int(dmg * player.damage_reduction_multiplier()))
        player.health -= dmg
        return dmg
    return None

def daily_random_events(player):
    events = []
    # Police raid
    if random.random() < POLICE_RAID_DAILY:
        seized = police_raid(player)
        events.append(f"POLICE RAID! They seized your stash ({seized} total units). Cash was safe.")
    # Bag find
    if random.random() < BAG_FIND_DAILY:
        name, qty = bag_on_ground(player)
        events.append(f"You found a bag on the ground: +{qty} {name}. (Free!)")
    return events

def try_int(prompt, allow_zero=True, min_val=None, max_val=None):
    while True:
        s = input(prompt).strip().replace(",", "")
        if s == "":
            print("Please enter a number.")
            continue
        if not (s.lstrip("-").isdigit()):
            print("Please enter digits only.")
            continue
        val = int(s)
        if not allow_zero and val == 0:
            print("Zero not allowed.")
            continue
        if min_val is not None and val < min_val:
            print(f"Minimum is {min_val}.")
            continue
        if max_val is not None and val > max_val:
            print(f"Maximum is {max_val}.")
            continue
        return val

def display_market(player, drug_prices):
    """
    Displays the market table with:
    Drug | Current Price | Owned | Avg Cost | Min–Max Price
    """
    # Define the min-max ranges for each drug
    DRUG_RANGES = {
        "Weed": (20, 200),
        "Shrooms": (50, 400),
        "Ketamin": (75, 450),
        "Meph": (100, 500),
        "MDMA": (150, 550),
        "Acid": (200, 600),
        "Cocaine": (1000, 3000),
        "Heroin": (1500, 4000)
    }

    print("\n" + "="*60)
    print(f"{'Drug':<12} {'Price':>10} | {'Owned':>6} {'Avg Cost':>10} {'Range':>15}")
    print("-"*60)

    for name, price in drug_prices.items():
        owned = player.inventory.get(name, 0)
        avg = player.avg_cost.get(name, 0)
        lo, hi = DRUG_RANGES[name]
        rng_s = f"{format_money(lo)}–{format_money(hi)}"
        avg_s = format_money(avg) if owned > 0 else "-"
        print(f"{name:<12} {format_money(price):>10} | {owned:>6} {avg_s:>10} {rng_s:>15}")

    print("="*60 + "\n")

def choose_drug():
    print("Choose a drug by number:")
    for idx, (name, (lo, hi), bulk) in enumerate(DRUGS, 1):
        print(f"  {idx:>2}. {name} (range {format_money(lo)}–{format_money(hi)}, bulk={bulk})")
    while True:
        n = try_int("Drug #: ", min_val=1, max_val=len(DRUGS))
        return DRUGS[n-1][0]

def buy_flow(player, market, location):
    prices = market.get_prices(location)
    print_market(location, market, player)
    drug = choose_drug()
    price = prices[drug]
    print(f"\nBuying {drug} at {format_money(price)} each.")
    max_afford = player.cash // price
    if max_afford <= 0:
        print("You can't afford any.")
        return
    qty = try_int(f"Qty to buy (max {max_afford}): ", min_val=0, max_val=max_afford)
    if qty <= 0:
        return
    cost = qty * price
    player.cash -= cost
    inv = player.inv[drug]
    inv["avg"] = weighted_average(inv["avg"], inv["qty"], qty, price)
    inv["qty"] += qty
    print(f"Bought {qty} {drug} for {format_money(cost)}. New avg cost: {format_money(inv['avg'])}")

def sell_flow(player, market, location):
    prices = market.get_prices(location)
    print_market(location, market, player)
    drug = choose_drug()
    owned = player.inv[drug]["qty"]
    if owned <= 0:
        print(f"You don't own any {drug}.")
        return
    price = prices[drug]
    print(f"\nSelling {drug} at {format_money(price)} each. You own {owned}.")
    qty = try_int(f"Qty to sell (max {owned}): ", min_val=0, max_val=owned)
    if qty <= 0:
        return
    revenue = qty * price
    player.inv[drug]["qty"] -= qty
    # average cost of remaining stays the same automatically; if qty becomes 0, avg becomes 0
    if player.inv[drug]["qty"] == 0:
        player.inv[drug]["avg"] = 0.0
    player.cash += revenue
    print(f"Sold {qty} {drug} for {format_money(revenue)}.")

def bank_flow(player):
    while True:
        print(SUBDIV)
        print(" BANK")
        print(f" Cash: {format_money(player.cash)}   Bank: {format_money(player.bank)}   Debt: {format_money(player.debt)}")
        print("  1) Deposit")
        print("  2) Withdraw")
        print("  3) Borrow (loan shark, unlimited, 10% daily interest)")
        print("  4) Repay loan")
        print("  5) Back")
        choice = input("Choose: ").strip()
        if choice == "1":
            if player.cash <= 0:
                print("No cash to deposit.")
                continue
            amt = try_int(f"Amount to deposit (max {player.cash}): ", min_val=0, max_val=player.cash)
            if amt > 0:
                player.cash -= amt
                player.bank += amt
                print(f"Deposited {format_money(amt)}.")
        elif choice == "2":
            if player.bank <= 0:
                print("No bank balance to withdraw.")
                continue
            amt = try_int(f"Amount to withdraw (max {player.bank}): ", min_val=0, max_val=player.bank)
            if amt > 0:
                player.bank -= amt
                player.cash += amt
                print(f"Withdrew {format_money(amt)}.")
        elif choice == "3":
            amt = try_int("Borrow how much: ", min_val=1)
            player.debt += amt
            player.cash += amt
            print(f"Borrowed {format_money(amt)} from the shark. Daily interest is 10%.")
        elif choice == "4":
            if player.debt <= 0:
                print("You have no debt.")
                continue
            max_pay = min(player.cash, player.debt)
            if max_pay <= 0:
                print("You have no cash to repay.")
                continue
            amt = try_int(f"Repay how much (max {max_pay}): ", min_val=0, max_val=max_pay)
            if amt > 0:
                player.debt -= amt
                player.cash -= amt
                player.paid_debt_today = True
                player.days_overdue = 0
                print(f"Repaid {format_money(amt)}. Remaining debt: {format_money(player.debt)}.")
        elif choice == "5":
            break
        else:
            print("Invalid choice.")

def vet_flow(player):
    print(SUBDIV)
    print(" SHADY VET")
    print(f" Health: {player.health}/{MAX_HEALTH}. {format_money(VET_COST)} per visit; restores about", VET_HEAL, "health.")
    if player.health >= MAX_HEALTH:
        print("You're already at max health.")
        return
    if player.cash < VET_COST:
        print("Not enough cash.")
        return
    confirm = input(f"Pay {format_money(VET_COST)} to get patched up? (y/n): ").strip().lower()
    if confirm.startswith("y"):
        player.cash -= VET_COST
        player.health = min(MAX_HEALTH, player.health + VET_HEAL)
        print(f"Vet patched you up. Health is now {player.health}/{MAX_HEALTH}.")

def travel_flow(current_location):
    print(SUBDIV)
    print(" TRAVEL")
    for i, loc in enumerate(LOCATIONS, 1):
        tag = " (current)" if loc == current_location else ""
        print(f"  {i}. {loc}{tag}")
    while True:
        n = try_int("Go to #: ", min_val=1, max_val=len(LOCATIONS))
        dest = LOCATIONS[n-1]
        if dest == current_location:
            print("You're already there.")
            continue
        return dest

def salesman_event(player):
    print(SUBDIV)
    print(" A shady salesman appears offering protection!")
    print(f"  1) Armor  - {format_money(ARMOR_COST)}  (+{ARMOR_HEALTH} health, reduces attack damage)")
    print(f"  2) Helmet - {format_money(HELMET_COST)} (+{HELMET_HEALTH} health, reduces attack damage)")
    print("  3) Nothing")
    choice = input("Buy something? (1/2/3): ").strip()
    if choice == "1":
        if player.cash >= ARMOR_COST:
            player.cash -= ARMOR_COST
            player.armor = True
            player.health = min(MAX_HEALTH, player.health + ARMOR_HEALTH)
            print(f"You bought Armor. Health now {player.health}/{MAX_HEALTH}.")
        else:
            print("You can't afford Armor.")
    elif choice == "2":
        if player.cash >= HELMET_COST:
            player.cash -= HELMET_COST
            player.helmet = True
            player.health = min(MAX_HEALTH, player.health + HELMET_HEALTH)
            print(f"You bought Helmet. Health now {player.health}/{MAX_HEALTH}.")
        else:
            print("You can't afford Helmet.")
    else:
        print("You pass on the offer.")

def day_start_sequence(day, player, market, location):
    # Interest and overdue handling
    apply_interest_and_overdue(player)

    # Taunt
    t = taunt_for_debt(player.debt)
    if t:
        print(wrap(t))

    # Loan shark attack check
    dmg = loan_shark_attack_check(player)
    if dmg:
        print(f"LOAN SHARK ATTACK! You took {dmg} damage.")
        if player.health <= 0:
            return ["You succumbed to your injuries..."]

    # Daily random events
    events = daily_random_events(player)
    for e in events:
        print(wrap(e))
    return events

def end_of_game_summary(player, market, location):
    prices = market.get_prices(location)
    score = player.net_worth(prices)
    print(DIV)
    print(" GAME OVER")
    print(DIV)
    print(f"Final location: {location}")
    print(f"Cash: {format_money(player.cash)}")
    print(f"Bank: {format_money(player.bank)} (not counted in score)")
    print(f"Debt: {format_money(player.debt)}")
    # List inventory value
    total_val = 0
    print("\nStash value at current market:")
    for name, _, _ in DRUGS:
        qty = player.inv[name]["qty"]
        if qty > 0:
            price = prices[name]
            val = qty * price
            total_val += val
            print(f"  {name:<12} x{qty:<4} @ {format_money(price)} = {format_money(val)}")
    print(SUBDIV)
    print(f"Score = Cash + Stash Value - Debt = {format_money(player.cash)} + {format_money(total_val)} - {format_money(player.debt)}")
    print(f"FINAL SCORE: {format_money(score)}")
    return score

def main_game():
    highscore = load_highscore()

    while True:
        # Initialize game state
        day = 1
        location = "Northampton"
        player = Player()
        market = Market()
        market.roll_daily_prices()

        # Day 1 start sequence (taunts start from day 1)
        print_header(day, location, player, market, highscore)
        day_start_sequence(day, player, market, location)
        press_enter()

        # Main loop
        while day <= GAME_DAYS:
            if player.health <= 0:
                print("\nYou died! The streets claim another soul.")
                break

            print_header(day, location, player, market, highscore)
            print_market(location, market, player)

            print(" Actions:")
            print("  1) Buy")
            print("  2) Sell")
            print("  3) Bank / Loans")
            print("  4) Shady Vet")
            print("  5) Travel (advances a day)")
            print("  6) End Day (wait) (advances a day)")
            print("  7) View Inventory")
            print("  8) Quit Game")
            choice = input("Choose: ").strip()

            if choice == "1":
                buy_flow(player, market, location)
                press_enter()
            elif choice == "2":
                sell_flow(player, market, location)
                press_enter()
            elif choice == "3":
                bank_flow(player)
                press_enter()
            elif choice == "4":
                vet_flow(player)
                press_enter()
            elif choice == "7":
                # inventory view
                print(SUBDIV)
                print(" INVENTORY")
                for name, _, _ in DRUGS:
                    it = player.inv[name]
                    if it["qty"] > 0:
                        print(f"  {name:<12} x{it['qty']:<4} avg {format_money(it['avg'])}")
                if all(player.inv[name]["qty"] == 0 for name,_,_ in DRUGS):
                    print("  (empty)")
                press_enter()
            elif choice == "5":
                # Travel -> advance day, possible salesman event, reroll prices, start-of-day events
                dest = travel_flow(location)
                location = dest

                # 20% salesman random event when traveling
                if random.random() < SALESMAN_TRAVEL_CHANCE:
                    salesman_event(player)

                # Advance day
                day += 1
                if day > GAME_DAYS:
                    break
                market.roll_daily_prices()
                print_header(day, location, player, market, highscore)
                day_start_sequence(day, player, market, location)
                press_enter()
            elif choice == "6":
                # Wait -> advance day without travel
                day += 1
                if day > GAME_DAYS:
                    break
                market.roll_daily_prices()
                print_header(day, location, player, market, highscore)
                day_start_sequence(day, player, market, location)
                press_enter()
            elif choice == "8":
                # quit early
                confirm = input("Are you sure you want to quit this run? (y/n): ").strip().lower()
                if confirm.startswith("y"):
                    break
            else:
                print("Invalid choice.")
                press_enter()

        # End of game
        score = end_of_game_summary(player, market, location)
        if score > highscore:
            print("\nNEW HIGHSCORE!")
            save_highscore(score)
            highscore = score
        else:
            hs = load_highscore()
            print(f"Highscore: {format_money(hs)}")

        print("\nPlay again? (y/n)")
        again = input("> ").strip().lower()
        if not again.startswith("y"):
            print("\nThanks for playing. Stay safe out there.")
            break

if __name__ == "__main__":
    random.seed()  # system time
    main_game()
