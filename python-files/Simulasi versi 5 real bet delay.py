import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm

# === PARAMETER UMUM ===
n_total = 1000000
sample_sizes = [30, 50, 70, 90, 110, 130]
monitor_window = max(sample_sizes)
threshold_z = -4
post_trigger_length = 50
chance = 0.5
real_bet_delay = 0

# === 1. GENERATE DATA ACAK ===
data = np.random.choice([0, 1], size=n_total, p=[1 - chance, chance])

# ===2. GENERATE DATA ACAK ===
data = np.random.choice([0, 1], size=n_total, p=[1 - chance, chance])

# === 3. HITUNG Z-SCORE DAN ENTRY POINT ===
def z_score(sample):
    p_hat = np.mean(sample)
    std = np.sqrt(chance * (1 - chance) / len(sample))
    if std == 0:
        return 0
    return (p_hat - chance) / std

entry_points = []
loss_streaks_after_trigger = []
triggered_sample_sizes = []

i = monitor_window
while i + post_trigger_length < n_total:
    triggered = False
    for size in sample_sizes:
        sample = data[i - size:i]
        z = z_score(sample)
        if z <= threshold_z:
            entry_points.append(i)
            triggered_sample_sizes.append(size)
            # Hitung max loss streak
            post_data = data[i:i + post_trigger_length]
            streak = 0
            max_streak = 0
            for val in post_data:
                if val == 0:
                    streak += 1
                    max_streak = max(max_streak, streak)
                else:
                    streak = 0
            loss_streaks_after_trigger.append(max_streak)
            triggered = True
            break
    i += post_trigger_length if triggered else 1

# === SIMPAN KE CSV (Loss Streak Info) ===
streak_df = pd.DataFrame({
    "Entry_Point": entry_points,
    "Triggered_Sample_Size": triggered_sample_sizes,
    "Max_Loss_Streak": loss_streaks_after_trigger
})
streak_df.to_csv("hasil_loss_streak.csv", index=False)

# === GRAFIK DISTRIBUSI STREAK ===
plt.figure(figsize=(10, 5))
plt.hist(loss_streaks_after_trigger, bins=range(1, max(loss_streaks_after_trigger)+2), align='left', rwidth=0.8, color='skyblue')
plt.title("Distribusi Max Loss Streak setelah Z <= -2.2")
plt.xlabel("Max Loss Streak")
plt.ylabel("Frekuensi")
plt.grid(True)
plt.savefig("grafik_loss_streak.png")
plt.close()

# === 3. STRATEGI TARUHAN + HISTORY ===
starting_balance = 100
balance = starting_balance
multiplier = 2.1
initial_bet = 0.5
max_recovery_steps = 24

full_martingale_results = []
balance_history = [balance]
drawdowns = []
peak = balance
bet_history = []

for idx, entry in enumerate(entry_points):
    bet_amount = initial_bet
    i = entry + real_bet_delay
    total_bet = 0
    win = False
    step = 0

    while i < len(data) and bet_amount <= balance and step < max_recovery_steps:
        outcome = data[i]
        total_bet += bet_amount
        is_win = outcome == 1
        next_balance = balance + (bet_amount * multiplier - total_bet) if is_win else balance - bet_amount

        bet_history.append({
            "Entry_Index": idx,
            "Step": step,
            "Round": i,
            "Bet_Amount": bet_amount,
            "Outcome": outcome,
            "Balance_After": next_balance,
            "Result": "WIN" if is_win else "LOSS"
        })

        if is_win:
            profit = bet_amount * multiplier - total_bet
            balance += profit
            full_martingale_results.append(profit)
            win = True
            break
        else:
            i += 1
            bet_amount *= multiplier
            step += 1

    if not win:
        full_martingale_results.append(-total_bet)
        balance -= total_bet
        if balance < starting_balance:
            break

    balance_history.append(balance)
    if balance > peak:
        peak = balance
    drawdowns.append((peak - balance) / peak)

# === SIMPAN HISTORY TARUHAN KE CSV ===
history_df = pd.DataFrame(bet_history)
history_df.to_csv("history_taruhan.csv", index=False)

# === RANGKUM HASIL ===
total_profit = sum(full_martingale_results)
avg_profit = total_profit / len(full_martingale_results)
roi = (total_profit / starting_balance) * 100
max_dd = max(drawdowns) * 100 if drawdowns else 0

print("\n=== Parameter ===")
print("Z-score:", threshold_z)
print("Sample Sizes:", sample_sizes)
print("Total Roll:", n_total)
print("Initial Balance:", starting_balance)
print("Initial Bet:", initial_bet)
print("Real Delay:", real_bet_delay)
print("Multiplier:", multiplier)
print("Max Recovery Steps:", max_recovery_steps)
print("\n=== Result ===")
print("Jumlah Entry:", len(full_martingale_results))
print(f"Total Profit: ${total_profit:.5f}")
print(f"Average Profit per Entry: ${avg_profit:.5f}")
print(f"ROI: {roi:.2f}%")
print(f"Final Balance: ${balance:.5f}")
print("Max Loss Streak:", max(loss_streaks_after_trigger))
print(f"Max Drawdown: {max_dd:.2f}%")

# === GRAFIK SALDO ===
plt.figure(figsize=(10, 5))
plt.plot(balance_history, color='green')
plt.title("Grafik Perubahan Saldo")
plt.xlabel("Entry ke-n")
plt.ylabel("Saldo (USD)")
plt.grid(True)
plt.savefig("grafik_saldo.png")
plt.close()

# === GRAFIK DRAWDOWN ===
plt.figure(figsize=(10, 4))
plt.plot(np.array(drawdowns) * 100, color='red')
plt.title("Grafik Drawdown (%)")
plt.xlabel("Entry ke-n")
plt.ylabel("Drawdown (%)")
plt.grid(True)
plt.savefig("grafik_drawdown.png")
plt.close()
