import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import sys
import platform

# Funzione beep cross-platform
def beep_alert():
    if platform.system() == "Windows":
        import winsound
        winsound.Beep(1000, 300)  # frequenza 1000Hz, durata 300ms
    elif platform.system() == "Darwin":  # MacOS
        import os
        os.system("afplay /System/Library/Sounds/Glass.aiff")
    else:
        print("\a")  # Linux/altro, terminal beep

class AviatorBot:
    def __init__(self, balance=1000, base_bet=10, max_rounds=100, history_window=20, risk_threshold=0.3):
        self.initial_balance = balance
        self.base_bet = base_bet
        self.max_rounds = max_rounds
        self.history_window = history_window
        self.risk_threshold = balance * risk_threshold
        self.strategies = ["fixed", "martingale", "hybrid"]
        self.reset_all()
        self.current_strategy = "fixed"

    def reset_all(self):
        self.balances = {s: [self.initial_balance] for s in self.strategies}
        self.current_bets = {s: self.base_bet for s in self.strategies}
        self.results = {s: [] for s in self.strategies}
        self.risk_points = {s: [] for s in self.strategies}

    def simulate_multiplier(self):
        multiplier = round(random.expovariate(1/2), 2)
        return max(multiplier, 1.0)

    def play_round(self, cashout=2.0, max_martingale=3):
        for strat in self.strategies:
            mult = self.simulate_multiplier()
            win = False
            bet = self.current_bets[strat]
            bal = self.balances[strat][-1]

            if mult >= cashout:
                bal += bet * (cashout - 1)
                self.current_bets[strat] = self.base_bet
                win = True
            else:
                bal -= bet
                if strat == "martingale" and bet < self.base_bet * (2 ** max_martingale):
                    self.current_bets[strat] *= 2
                elif strat == "hybrid" and bet < self.base_bet * 4:
                    self.current_bets[strat] *= 2
                else:
                    self.current_bets[strat] = self.base_bet

            self.balances[strat].append(bal)
            self.results[strat].append(win)
            # segnala rischio
            if bal < self.risk_threshold:
                self.risk_points[strat].append(len(self.balances[strat])-1)
                beep_alert()  # alert sonoro
            else:
                self.risk_points[strat].append(None)

    def predict_next_strategy(self, cashout=2.0, max_martingale=3, predict_rounds=5, simulations=500):
        predictions = {}
        for strat in self.strategies:
            wins_weighted = 0
            recent_history = self.results[strat][-self.history_window:] if len(self.results[strat]) >= self.history_window else self.results[strat]
            for _ in range(simulations):
                temp_balance = self.balances[strat][-1]
                temp_bet = self.base_bet
                for _ in range(predict_rounds):
                    mult = round(random.expovariate(1/2), 2)
                    mult = max(mult, 1.0)
                    if mult >= cashout:
                        temp_balance += temp_bet * (cashout - 1)
                        temp_bet = self.base_bet
                    else:
                        temp_balance -= temp_bet
                        if strat == "martingale" and temp_bet < self.base_bet * (2 ** max_martingale):
                            temp_bet *= 2
                        elif strat == "hybrid" and temp_bet < self.base_bet * 4:
                            temp_bet *= 2
                        else:
                            temp_bet = self.base_bet
                weight = (sum(recent_history)/len(recent_history) if recent_history else 0.5) + 0.5
                if temp_balance > self.balances[strat][-1]:
                    wins_weighted += weight
            predictions[strat] = wins_weighted / simulations
        best_strat = max(predictions, key=predictions.get)
        return best_strat, predictions

# --- SIMULAZIONE DINAMICA CON ALERT ---
if __name__ == "__main__":
    balance = float(input("Saldo iniziale: "))
    base_bet = float(input("Puntata base: "))
    max_rounds = int(input("Quanti round simulare?: "))
    cashout = float(input("Cashout target: "))
    risk_percent = float(input("Soglia rischio (%) del saldo iniziale: "))/100

    bot = AviatorBot(balance=balance, base_bet=base_bet, max_rounds=max_rounds, risk_threshold=risk_percent)

    fig, ax = plt.subplots(figsize=(12,6))
    lines = {s: ax.plot([], [], label=s.upper())[0] for s in bot.strategies}
    risk_markers = {s: ax.plot([], [], 'ro')[0] for s in bot.strategies}
    prediction_text = ax.text(0.5, 1.02, '', transform=ax.transAxes, ha='center', fontsize=12, weight='bold')
    alert_text = ax.text(0.5, 0.95, '', transform=ax.transAxes, ha='center', fontsize=12, color='red', weight='bold')

    ax.axhline(balance, color='gray', linestyle='--', label='Saldo iniziale')
    ax.axhline(0, color='red', linestyle='--', label='Perdita totale')
    ax.set_xlim(0, max_rounds)
    ax.set_ylim(0, balance*2)
    ax.set_xlabel('Round')
    ax.set_ylabel('Saldo')
    ax.set_title("Simulazione Dinamica AVIATOR con Cambio Automatico Strategia e Alert")
    ax.legend()

    def update(frame):
        bot.play_round(cashout=cashout)

        # Cambio strategia automatica se rischio
        if bot.balances[bot.current_strategy][-1] < bot.risk_threshold:
            best_strat, _ = bot.predict_next_strategy(cashout=cashout)
            bot.current_strategy = best_strat

        # Aggiorna linee e marker rischio
        for strat in bot.strategies:
            lines[strat].set_data(range(len(bot.balances[strat])), bot.balances[strat])
            risk_points_y = [bot.balances[strat][i] if bot.risk_points[strat][i] is not None else None for i in range(len(bot.balances[strat]))]
            risk_markers[strat].set_data(range(len(bot.balances[strat])), risk_points_y)

        prediction_text.set_text(f"Round {frame}: Strategia consigliata → {bot.current_strategy.upper()}")
        # Alert visivo se rischio attuale
        if bot.balances[bot.current_strategy][-1] < bot.risk_threshold:
            alert_text.set_text("⚠️ RISCHIO ALTO! ⚠️")
        else:
            alert_text.set_text("")

        return list(lines.values()) + list(risk_markers.values()) + [prediction_text, alert_text]

    ani = FuncAnimation(fig, update, frames=range(1, max_rounds+1), blit=True, interval=500, repeat=False)
    plt.show()
