#!/usr/bin/env python3
"""
stock_treasure.py
A console stock‑trading game with real market data, a bank, and random world events.
Improvements:
- More stock options to buy.
- More fluctuations in the stocks prices.
- Randomly create stock jumps (surges/drops).
- Always show what shares you buy and sell costed you.
- Shows for each stock you own: shares owned, total paid, average price paid, current price, and unrealized gain/loss.
"""

import time
import random
from collections import defaultdict

import yfinance as yf

# ───────────────────────────────────────────────────────────────────────
STARTING_CASH = 25_000.0
TARGET_NET_WORTH = 5_000_000.0

SIMULATION_SPEED = 0.1  # change to 0.5 or 0.1 for a faster test

ANNUAL_BANK_RATE = 0.05

# Expanded Stock List
STOCKS = {
    "AAPL":  "Apple Inc. – Designer of iPhone, iPad, Mac, and services.",
    "MSFT":  "Microsoft Corp. – Developer of Windows, Office, Azure, and cloud services.",
    "GOOG":  "Alphabet Inc. – Parent of Google, leader in search and advertising.",
    "AMZN":  "Amazon.com Inc. – E‑commerce, AWS, and digital streaming.",
    "TSLA":  "Tesla Inc. – Electric cars, solar, and battery technology.",
    "JPM":   "JP Morgan Chase & Co. – Global banking and financial services.",
    "XOM":   "Exxon Mobil Corp. – Oil & gas exploration and production.",
    "NVDA":  "NVIDIA Corp. – GPU and AI hardware for GPUs, data centers, and GPUs.",
    "V":     "Visa Inc. – Payment solutions and global network.",
    "NFLX":  "Netflix Inc. – Streaming video and original content.",
    "DIS":   "The Walt Disney Company – Entertainment and media.",
    "BAC":   "Bank of America Corp. – Financial services.",
    "INTC":  "Intel Corp. – Semiconductor and technology.",
    "KO":    "Coca-Cola Co. – Beverages.",
    "PEP":   "PepsiCo Inc. – Beverages and snacks.",
    "SBUX":  "Starbucks Corp. – Coffeehouse chain.",
    "MCD":   "McDonald's Corp. – Fast food giant.",
    "BA":    "Boeing Co. – Aerospace and defense.",
    "CSCO":  "Cisco Systems Inc. – Networking and IT.",
    "ADBE":  "Adobe Inc. – Software and media.",
    "PYPL":  "PayPal Holdings Inc. – Digital payments.",
    "CRM":   "Salesforce Inc. – Cloud software.",
    "ORCL":  "Oracle Corp. – Database and cloud services.",
    "T":     "AT&T Inc. – Telecommunications.",
    "GE":    "General Electric Co. – Diversified conglomerate.",
    "HON":   "Honeywell International – Industrial and tech.",
    "WMT":   "Walmart Inc. – Retail giant.",
    "CVX":   "Chevron Corp. – Energy.",
    "F":     "Ford Motor Co. – Automotive.",
    "GM":    "General Motors Co. – Automotive.",
}

WORLD_EVENTS = [
    {
        "name": "Tech Boom",
        "desc": "Rapid innovation in AI accelerates growth for tech giants.",
        "targets": ["AAPL", "MSFT", "GOOG", "AMZN", "NVDA", "INTC", "ADBE", "CRM", "ORCL", "CSCO"],
        "factor_range": (1.05, 1.15),   # +5% to +15%
    },
    {
        "name": "Oil Shock",
        "desc": "Geopolitical tensions spike oil prices, hurting energy stocks.",
        "targets": ["XOM", "CVX"],
        "factor_range": (0.82, 0.95),   # -18% to -5%
    },
    {
        "name": "Banking Restructuring",
        "desc": "New regulations tighten credit availability for banks.",
        "targets": ["JPM", "BAC"],
        "factor_range": (0.90, 0.99),   # -10% to -1%
    },
    {
        "name": "Consumer Surge",
        "desc": "Consumer confidence returns; retail stocks rally.",
        "targets": ["TSLA", "AMZN", "V", "MCD", "WMT", "SBUX"],
        "factor_range": (1.02, 1.10),   # +2% to +10%
    },
    {
        "name": "Pandemic Re‑emergence",
        "desc": "Unpredictable health crisis hits supply chains worldwide.",
        "targets": list(STOCKS.keys()),
        "factor_range": (0.78, 0.95),   # -22% to -5%
    },
]

def get_input(prompt):
    return input(prompt)

def clear_screen():
    import os
    result = os.system('cls' if os.name == 'nt' else 'clear')
    if result != 0:
        print("(Screen clear not supported in this terminal.)")

class Portfolio:
    def __init__(self, cash=STARTING_CASH):
        self.cash = cash
        self.holdings = defaultdict(int)   # {sym: shares}
        # Track what you paid: {sym: total_paid}
        self.total_paid = defaultdict(float)  # {sym: total $ spent buying}
        self.total_bought = defaultdict(int)  # {sym: total shares bought}

    def net_worth(self, prices):
        value = self.cash
        for sym, shares in self.holdings.items():
            value += shares * prices.get(sym, 0.0)
        value += 0  # optional for clarity
        return value

    def can_afford(self, cost):
        return self.cash >= cost

    def buy(self, sym, shares, price):
        if shares <= 0:
            return False, "Number of shares must be positive."
        cost = shares * price
        if cost > self.cash:
            return False, f"Insufficient funds: need ${cost:.2f}, have ${self.cash:.2f}"
        self.cash -= cost
        self.holdings[sym] += shares
        self.total_paid[sym] += cost
        self.total_bought[sym] += shares
        return True, cost

    def sell(self, sym, shares, price):
        if shares <= 0:
            return False, "Number of shares must be positive.", 0.0
        if shares > self.holdings.get(sym, 0):
            return False, f"You don't own enough shares of {sym}", 0.0
        proceeds = shares * price
        self.cash += proceeds
        self.holdings[sym] -= shares

        # Remove proportional paid info
        if self.total_bought[sym] > 0:
            fraction = shares / self.total_bought[sym]
            self.total_paid[sym] -= self.total_paid[sym] * fraction
            self.total_bought[sym] -= shares
            # Clamp to 0 if all sold
            if self.holdings[sym] == 0 or self.total_bought[sym] == 0:
                self.total_paid[sym] = 0
                self.total_bought[sym] = 0
        return True, proceeds

class Bank:
    def __init__(self, annual_rate=ANNUAL_BANK_RATE):
        self.balance = 0.0
        self.annual_rate = annual_rate

    def deposit(self, amount):
        if amount <= 0:
            return False, "Amount must be positive."
        self.balance += amount
        return True, ""

    def withdraw(self, amount):
        if amount <= 0:
            return False, "Amount must be positive."
        if amount > self.balance:
            return False, f"Bank only holds ${self.balance:.2f}"
        self.balance -= amount
        return True, ""

    def apply_monthly_interest(self):
        monthly = self.annual_rate / 12.0
        self.balance *= (1.0 + monthly)

class GameEngine:
    def __init__(self):
        self.day = 0
        self.portfolio = Portfolio()
        self.bank = Bank()
        self.prices = {sym: 1.0 for sym in STOCKS}

    def fetch_current_prices(self):
        for sym in STOCKS:
            try:
                ticker = yf.Ticker(sym)
                for period in ['1d', '2d', '3d', '4d', '5d']:
                    hist = ticker.history(period=period, interval="1d")
                    if not hist.empty:
                        self.prices[sym] = float(hist["Close"][-1])
                        break
                else:
                    print(f"⚠️  No recent price found for {sym}. Using previous value: ${self.prices[sym]:.2f}")
            except Exception as e:
                print(f"⚠️  Error grabbing price for {sym}: {e}")

    def apply_random_event(self):
        # World event (50% chance)
        if random.random() < 0.5:
            pass
        else:
            event = random.choice(WORLD_EVENTS)
            factor_min, factor_max = event["factor_range"]
            print("\n" + "="*50)
            print(f"⚡️  WORLD EVENT: {event['name'].upper()} — {event['desc']}")
            print("="*50)
            for sym in event["targets"]:
                factor = random.uniform(factor_min, factor_max)
                old_price = self.prices.get(sym, 1.0)
                self.prices[sym] *= factor
                print(f"    {sym} price changed from ${old_price:.2f} to ${self.prices[sym]:.2f} ({factor*100:.1f}% change)")
            print("="*50 + "\n")

        # RANDOM INDIVIDUAL STOCK FLUCTUATIONS (every day)
        for sym, price in self.prices.items():
            # Normal daily move: ±1% to ±3%
            daily_vol = random.uniform(-0.03, 0.03)
            self.prices[sym] *= (1 + daily_vol)
            # Random jump/dip: 1 in 15 chance, ±10% to ±30%
            if random.randint(1, 15) == 1:
                jump = random.uniform(0.10, 0.30)
                direction = random.choice([-1, 1])
                self.prices[sym] *= (1 + direction * jump)
                if direction == 1:
                    print(f"🚀 {sym} SURGE! Jumps +{jump*100:.1f}% to ${self.prices[sym]:.2f}")
                else:
                    print(f"💥 {sym} CRASH! Drops -{jump*100:.1f}% to ${self.prices[sym]:.2f}")

    def apply_monthly_interest(self):
        if self.day > 0 and self.day % 30 == 0:
            self.bank.apply_monthly_interest()
            print(f"💰 Bank balance after interest: ${self.bank.balance:.2f}")

    def net_worth(self):
        return self.portfolio.net_worth(self.prices) + self.bank.balance

    def show_status(self):
        clear_screen()
        print(f"--- Day {self.day} ---")
        print(f"Bank balance:            ${self.bank.balance:,.2f}")
        print("\nMarket Prices:")
        for sym, price in self.prices.items():
            print(f"  {sym:5} : ${price:,.2f} — {STOCKS[sym][:70]}")
        print("\nYour Holdings:")
        holdings_exist = any(shares > 0 for shares in self.portfolio.holdings.values())
        if not holdings_exist:
            print("  (no holdings)")
        else:
            print(
                "  Symbol    Shares    Avg Paid    Total Paid    Current    Value    Gain/Loss"
            )
            print(
                "  ---------------------------------------------------------------------------"
            )
            for sym, shares in self.portfolio.holdings.items():
                if shares > 0:
                    total_paid = self.portfolio.total_paid[sym]
                    total_bought = self.portfolio.total_bought[sym]
                    avg_paid = total_paid / total_bought if total_bought > 0 else 0
                    current = self.prices[sym]
                    value = shares * current
                    gainloss = value - (avg_paid * shares)
                    print(
                        f"  {sym:5}   {shares:6}   ${avg_paid:8.2f}   ${total_paid:10.2f}   ${current:7.2f}   ${value:7.2f}   ${gainloss:9.2f}"
                    )
        print(f"\nCash:                    ${self.portfolio.cash:,.2f}")
        net = self.net_worth()
        print(f"\nNet Worth:                ${net:,.2f} / ${TARGET_NET_WORTH:,.2f}")

    def player_action(self):
        while True:
            print("\nChoose an action:")
            print("  1) Buy shares")
            print("  2) Sell shares")
            print("  3) Deposit to bank")
            print("  4) Withdraw from bank")
            print("  5) Skip (no action)")
            choice = get_input("Enter number: ").strip()
            try:
                opt = int(choice)
            except ValueError:
                print("Invalid input, please enter a number between 1–5.")
                continue

            if opt == 1:
                self.action_buy()
                break
            elif opt == 2:
                self.action_sell()
                break
            elif opt == 3:
                self.action_deposit()
                break
            elif opt == 4:
                self.action_withdraw()
                break
            elif opt == 5:
                print("No action taken this day.")
                break
            else:
                print("Unknown option. Try again.")

    def action_buy(self):
        print("\nAvailable stocks:")
        for sym in STOCKS:
            print(f"  {sym:5} : ${self.prices[sym]:,.2f} — {STOCKS[sym]}")
        sym = get_input("\n  Symbol to buy: ").strip().upper()
        if sym not in STOCKS:
            print(f"Invalid symbol: {sym}")
            return
        try:
            shares = int(get_input("  Shares: ").strip())
        except ValueError:
            print("  Must be an integer.")
            return
        price = self.prices.get(sym)
        if not price:
            print("  Price unavailable for that symbol.")
            return
        ok, cost = self.portfolio.buy(sym, shares, price)
        if ok:
            print(f"  Bought {shares} shares of {sym} at ${price:.2f} each → Total cost: ${cost:.2f} (${price:.2f} x {shares})")
        else:
            print(f"  {cost}")

    def action_sell(self):
        sym = get_input("  Symbol to sell: ").strip().upper()
        if sym not in STOCKS:
            print(f"Invalid symbol: {sym}")
            return
        try:
            shares = int(get_input("  Shares: ").strip())
        except ValueError:
            print("  Must be an integer.")
            return
        price = self.prices.get(sym)
        if not price:
            print("  Price unavailable for that symbol.")
            return
        ok, proceeds = self.portfolio.sell(sym, shares, price)
        if ok:
            print(f"  Sold {shares} shares of {sym} at ${price:.2f} each → Total proceeds: ${proceeds:.2f} (${price:.2f} x {shares})")
        else:
            print(f"  {proceeds}")

    def action_deposit(self):
        try:
            amt = float(get_input("  Deposit amount: $").strip())
        except ValueError:
            print("  Must be a number.")
            return
        if amt > self.portfolio.cash:
            print("  You don't have that much cash.")
            return
        ok, msg = self.bank.deposit(amt)
        if ok:
            self.portfolio.cash -= amt
            print(f"  Deposited ${amt:.2f} into bank.")
        else:
            print(f"  {msg}")

    def action_withdraw(self):
        try:
            amt = float(get_input("  Withdraw amount: $").strip())
        except ValueError:
            print("  Must be a number.")
            return
        ok, msg = self.bank.withdraw(amt)
        if ok:
            self.portfolio.cash += amt
            print(f"  Withdrew ${amt:.2f} from bank.")
        else:
            print(f"  {msg}")

    def run(self):
        print(f"🎉 Welcome to the Stock Treasure Game!")
        print(f"Start with ${STARTING_CASH:,} and aim for ${TARGET_NET_WORTH:,}.")
        print(f"One day = {SIMULATION_SPEED} real seconds.\n")
        print("Tip: Press Ctrl+C to quit at any time.")

        while True:
            self.day += 1
            self.fetch_current_prices()
            self.apply_random_event()
            self.apply_monthly_interest()
            self.show_status()

            if self.net_worth() >= TARGET_NET_WORTH:
                print("\n🏆  You won! Congratulations, you reached the target net worth!")
                print("Suggestion: Add save/load feature for future improvements.")
                break

            holdings_exist = any(shares > 0 for shares in self.portfolio.holdings.values())
            if self.portfolio.cash <= 0 and not holdings_exist and self.bank.balance <= 0:
                print("\n💀  Game over – you’ve run out of funds and holdings.")
                print("Suggestion: Implement a restart or 'easy mode' option.")
                break

            self.player_action()

            print(f"\n--- Day {self.day} ends. Waiting {SIMULATION_SPEED} seconds ...")
            try:
                time.sleep(SIMULATION_SPEED)
            except KeyboardInterrupt:
                print("\n🛑  Game interrupted. Bye!")
                break

if __name__ == "__main__":
    try:
        GameEngine().run()
    except KeyboardInterrupt:
        print("\n🛑  Game interrupted. Bye!")
