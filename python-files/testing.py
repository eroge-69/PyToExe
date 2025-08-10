import datetime

def send_alert(message):
    print(f"ALERT: {message}")

class OptionCrossoverStrategy:
    def __init__(self):
        self.index = 'Nifty'
        self.option_type = 'weekly'
        self.tf_minutes = 5
        self.strike_type = 'nearest'
        self.max_trades_per_day = 3
        self.lots = 1
        self.sl = 10
        self.target = 15
        self.exit_time = datetime.time(15, 26)
        self.trades_taken = 0
        self.in_trade = False

    def dummy_get_price(self, symbol):
        # Return dummy price that changes over time to simulate crossover
        now_sec = datetime.datetime.now().second
        return 100 + (now_sec % 20)

    def bodies_do_not_overlap(self, price1, price2):
        # Simplified check: difference > 2 means no overlap
        return abs(price1 - price2) > 2

    def check_crossover(self, ce_price, pe_price, prev_ce_price, prev_pe_price):
        if prev_ce_price > prev_pe_price and ce_price < pe_price:
            return 'PE_cross_over_CE'
        elif prev_pe_price > prev_ce_price and ce_price > pe_price:
            return 'CE_cross_over_PE'
        else:
            return None

    def run_strategy(self):
        now = datetime.datetime.now().time()
        if now > self.exit_time:
            if self.in_trade:
                send_alert("Exiting trade at market close.")
                self.in_trade = False
            return

        # Dummy previous prices
        prev_ce = self.dummy_get_price('CE_prev')
        prev_pe = self.dummy_get_price('PE_prev')
        # Dummy current prices
        ce = self.dummy_get_price('CE')
        pe = self.dummy_get_price('PE')

        crossover = self.check_crossover(ce, pe, prev_ce, prev_pe)
        if crossover is None:
            print("No crossover detected.")
            return

        if not self.bodies_do_not_overlap(ce, pe):
            print("Bodies overlap on crossover candle, waiting...")
            return

        if self.trades_taken >= self.max_trades_per_day:
            print("Max trades reached.")
            return

        if self.in_trade:
            print("Already in trade.")
            return

        self.in_trade = True
        self.trades_taken += 1
        direction = 'CE' if crossover == 'CE_cross_over_PE' else 'PE'
        entry_price = ce if direction == 'CE' else pe
        send_alert(f"Trade Entry: {direction} at {entry_price} with SL={self.sl} Target={self.target}")

def main():
    strat = OptionCrossoverStrategy()
    strat.run_strategy()

if __name__ == "__main__":
    main()
