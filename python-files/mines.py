import tkinter as tk
import random
import time
import json
import os

# -------------------- Game State --------------------
cash = 1000
grid_size = 5
num_mines = 1
current_multiplier = 1.0
current_winnings = 0
current_bet = 0
luck_multiplier = 1
rebirth_multiplier = 1.0
last_click_time = 0
money_clicks = 0
achievements = {
    "Lucky Starter": False,
    "First Payday": False,
    "Cookie Clicker Apprentice": False,
    "Mines Master": False,
    "Rich Miner": False,
    "High Roller": False
}
leaderboard = {
    "highest_cash": 0,
    "achievements_unlocked": 0
}

# -------------------- Functions --------------------
def update_multiplier():
    global current_multiplier
    current_multiplier = round(1 + (num_mines_var.get() / (grid_size**2)) * 2, 2)
    multiplier_label.config(text=f"Current Multiplier: {current_multiplier:.2f}x (Rebirth x{rebirth_multiplier:.2f})")

def start_game():
    global mines, revealed, current_winnings, current_bet
    revealed = []
    current_winnings = 0
    current_bet = 0
    update_cash_label()
    round_winnings_label.config(text=f"Round Winnings: ${current_winnings:,.2f}")
    update_multiplier()

    safe_tiles_needed = grid_size**2 - num_mines_var.get()
    adjusted_safe_tiles = min(grid_size**2, int(safe_tiles_needed * luck_multiplier))
    all_indices = list(range(grid_size**2))
    mines_count = grid_size**2 - adjusted_safe_tiles
    mines = random.sample(all_indices, mines_count)

    for i, btn in enumerate(buttons):
        btn.config(bg="#2c3e50", text="", state="normal")
        btn.original_bg = "#2c3e50"

def pick_tile(index):
    global current_winnings, current_bet, cash
    if current_bet == 0:
        current_bet = bet.get()
        if current_bet <= 0 or current_bet > cash:
            return
        cash -= current_bet
        update_cash_label()

    if index in mines:
        buttons[index].config(bg="#e74c3c", text="💣")
        start_game()
    else:
        buttons[index].config(bg="#27ae60", text="✓", state="disabled")
        buttons[index].original_bg = "#27ae60"
        current_winnings += int(current_bet * (current_multiplier - 1) * rebirth_multiplier)
        round_winnings_label.config(text=f"Round Winnings: ${current_winnings:,.2f}")
    check_achievements()

def cash_out():
    global cash, current_winnings, current_bet, leaderboard
    if current_winnings > 0:
        cash += current_winnings
        show_money_animation(current_winnings)
        current_winnings = 0
        current_bet = 0
        update_cash_label()
        round_winnings_label.config(text=f"Round Winnings: $0.00")
        start_game()
    check_achievements()
    leaderboard["highest_cash"] = max(leaderboard["highest_cash"], cash)

def buy_luck():
    global cash, luck_multiplier
    if cash >= 5000:
        cash -= 5000
        luck_multiplier *= 2
        luck_label.config(text=f"Luck: {luck_multiplier}x")
        update_cash_label()
    check_achievements()

def update_cash_label():
    cash_label.config(text=f"Balance: ${cash:,.2f}")

def on_enter(e):
    e.widget.config(bg="#34495e")

def on_leave(e):
    if hasattr(e.widget, "original_bg"):
        e.widget.config(bg=e.widget.original_bg)

# -------------------- Achievements --------------------
def check_achievements():
    global achievements, cash, money_clicks, leaderboard
    # Short-term achievements
    if not achievements["Lucky Starter"] and len(revealed) >= 5:
        achievements["Lucky Starter"] = True
        cash = int(cash * 1.3)
        update_cash_label()
        show_money_animation(int(cash * 0.3))
        achievement_label.config(text="Achievement unlocked: Lucky Starter 🎉")
        root.after(3000, lambda: achievement_label.config(text=""))

    if not achievements["First Payday"] and current_winnings >= 500:
        achievements["First Payday"] = True
        cash = int(cash * 1.3)
        update_cash_label()
        show_money_animation(int(cash * 0.3))
        achievement_label.config(text="Achievement unlocked: First Payday 💰")
        root.after(3000, lambda: achievement_label.config(text=""))

    if not achievements["Cookie Clicker Apprentice"] and money_clicks >= 50:
        achievements["Cookie Clicker Apprentice"] = True
        cash = int(cash * 1.3)
        update_cash_label()
        show_money_animation(int(cash * 0.3))
        achievement_label.config(text="Achievement unlocked: Cookie Clicker Apprentice 🍪")
        root.after(3000, lambda: achievement_label.config(text=""))

    # Long-term achievements
    if not achievements["Mines Master"] and len(revealed) == grid_size**2 - len(mines):
        achievements["Mines Master"] = True
        cash = int(cash * 2)
        update_cash_label()
        show_money_animation(int(cash / 2))
        achievement_label.config(text="Achievement unlocked: Mines Master 🏆")
        root.after(3000, lambda: achievement_label.config(text=""))

    leaderboard["achievements_unlocked"] = sum(achievements.values())

# -------------------- Money+ Mini-Game --------------------
def open_money_game():
    global money_window, last_click_time, money_clicks
    money_window = tk.Toplevel(root)
    money_window.title("Money+ Mini Game 💰")
    money_window.configure(bg="#d35400")

    money_label = tk.Label(money_window, text=f"Cash: ${cash}", font=("Arial", 16, "bold"), fg="white", bg="#d35400")
    money_label.pack(pady=10)

    def click_cookie():
        global cash, last_click_time, money_clicks
        current_time = time.time()
        if current_time - last_click_time >= 2:
            cash += 10
            money_clicks += 1
            last_click_time = current_time
            money_label.config(text=f"Cash: ${cash}")
            update_cash_label()
            show_money_animation(10)
            check_achievements()

    cookie_btn = tk.Button(money_window, text="🍪 Click Me!", font=("Arial", 24, "bold"), width=10, height=5,
                           bg="#f39c12", fg="white", command=click_cookie)
    cookie_btn.pack(pady=20)

    back_btn = tk.Button(money_window, text="Back to Mines", font=("Arial", 14), bg="#8e44ad", fg="white",
                         command=money_window.destroy)
    back_btn.pack(pady=10)

# -------------------- Floating Money Animation --------------------
def show_money_animation(amount):
    anim_label = tk.Label(root, text=f"+${amount:,}", fg="#f1c40f", bg="#1e272e", font=("Arial", 14, "bold"))
    # Ensure it stays on screen
    x = min(root.winfo_width() - 50, cash_label.winfo_x())
    y = max(5, cash_label.winfo_y() - 20)
    anim_label.place(x=x, y=y)

    def move_up(step=0):
        if step < 20:
            anim_label.place(x=x, y=y - step)
            root.after(30, lambda: move_up(step + 2))
        else:
            anim_label.destroy()
    move_up()

# -------------------- Saving & Offline Earnings --------------------
def load_game():
    global cash, luck_multiplier, achievements, money_clicks
    if os.path.exists("save.json"):
        try:
            with open("save.json", "r") as f:
                data = json.load(f)
            cash = data.get("cash", 1000)
            luck_multiplier = data.get("luck_multiplier", 1)
            achievements.update(data.get("achievements", achievements))
            money_clicks = data.get("money_clicks", 0)
            last_seen = data.get("last_seen", time.time())

            offline_seconds = time.time() - last_seen
            offline_minutes = offline_seconds / 60
            bonus = int(offline_minutes / 10) * 10
            if bonus > 0:
                cash += bonus
                update_cash_label()
                show_money_animation(bonus)
                achievement_label.config(text=f"Welcome back! You earned ${bonus} offline.")
                root.after(5000, lambda: achievement_label.config(text=""))
        except:
            # If file is corrupted, reset
            save_game()

def save_game():
    data = {
        "cash": cash,
        "luck_multiplier": luck_multiplier,
        "achievements": achievements,
        "money_clicks": money_clicks,
        "last_seen": time.time()
    }
    with open("save.json", "w") as f:
        json.dump(data, f, indent=4)

def on_exit():
    save_game()
    root.destroy()

# -------------------- Rebirth System --------------------
def rebirth():
    global cash, luck_multiplier, rebirth_multiplier, current_winnings, current_bet
    if cash >= 100000:
        rebirth_multiplier *= 1.3
        cash = 0
        luck_multiplier = 1
        current_winnings = 0
        current_bet = 0
        update_cash_label()
        luck_label.config(text=f"Luck: {luck_multiplier}x")
        round_winnings_label.config(text=f"Round Winnings: $0.00")
        achievement_label.config(text=f"Rebirth! Multiplier Boost: {rebirth_multiplier:.2f}x 🎉")
        root.after(5000, lambda: achievement_label.config(text=""))
        start_game()

# -------------------- UI Setup --------------------
root = tk.Tk()
root.title("Python Mines 💣")
root.configure(bg="#1e272e")

cash_label = tk.Label(root, text=f"Balance: ${cash:,.2f}", font=("Arial", 20, "bold"),
                      fg="#2ecc71", bg="#1e272e")
cash_label.pack(pady=10)

bet_frame = tk.Frame(root, bg="#1e272e")
bet_frame.pack(pady=5)

tk.Label(bet_frame, text="Bet Amount", fg="white", bg="#1e272e").grid(row=0, column=0, padx=5)
bet = tk.IntVar(value=100)
tk.Entry(bet_frame, textvariable=bet, width=10, bg="#34495e", fg="white", insertbackground="white").grid(row=0, column=1, padx=5)

tk.Label(bet_frame, text="Number of Mines", fg="white", bg="#1e272e").grid(row=0, column=2, padx=5)
num_mines_var = tk.IntVar(value=1)
mines_spinbox = tk.Spinbox(bet_frame, from_=1, to=grid_size**2-1, textvariable=num_mines_var,
                           width=5, command=update_multiplier, bg="#34495e", fg="white", justify="center")
mines_spinbox.grid(row=0, column=3, padx=5)

multiplier_label = tk.Label(bet_frame, text=f"Current Multiplier: {current_multiplier:.2f}x (Rebirth x{rebirth_multiplier:.2f})",
                            fg="#2ecc71", bg="#1e272e")
multiplier_label.grid(row=0, column=4, padx=10)

round_winnings_label = tk.Label(root, text=f"Round Winnings: ${current_winnings:,.2f}", font=("Arial", 14),
                                fg="#f1c40f", bg="#1e272e")
round_winnings_label.pack(pady=5)

cashout_btn = tk.Button(root, text="Cash Out 💰", command=cash_out, bg="#e67e22", fg="white", font=("Arial", 14, "bold"))
cashout_btn.pack(pady=10)

luck_frame = tk.Frame(root, bg="#1e272e")
luck_frame.pack(pady=5)
luck_label = tk.Label(luck_frame, text=f"Luck: {luck_multiplier}x", fg="#f39c12", bg="#1e272e", font=("Arial", 14))
luck_label.pack(side="left", padx=5)
buy_luck_btn = tk.Button(luck_frame, text="Buy Luck ($5,000)", command=buy_luck, bg="#8e44ad", fg="white")
buy_luck_btn.pack(side="left", padx=5)

money_btn = tk.Button(root, text="Money+", font=("Arial", 14, "bold"), bg="#3498db", fg="white", command=open_money_game)
money_btn.pack(pady=10)

rebirth_btn = tk.Button(root, text="Rebirth 🔄 ($100k)", font=("Arial", 14, "bold"), bg="#16a085", fg="white", command=rebirth)
rebirth_btn.pack(pady=5)

achievement_label = tk.Label(root, text="", font=("Arial", 14), fg="#f1c40f", bg="#1e272e")
achievement_label.pack(pady=5)

grid_frame = tk.Frame(root, bg="#1e272e")
grid_frame.pack(pady=10)

buttons = []
for i in range(grid_size**2):
    btn = tk.Button(grid_frame, bg="#2c3e50", width=6, height=3, command=lambda i=i: pick_tile(i))
    btn.grid(row=i//grid_size, column=i%grid_size, padx=3, pady=3)
    btn.original_bg = "#2c3e50"
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    buttons.append(btn)

# -------------------- Start Game --------------------
load_game()
start_game()
root.protocol("WM_DELETE_WINDOW", on_exit)
root.mainloop()
