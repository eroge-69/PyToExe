import datetime
import logging
from typing import Optional

# Dummy placeholders for Dhan API / broker data fetching
# Replace with actual API calls in your environment
def get_spot_price(index_name: str, at_time: datetime.time) -> float:
    # Fetch spot price for Nifty, Sensex, BankNifty at 9:14am IST
    # Placeholder: return fixed dummy price
    return 18000.0

def get_option_candle(symbol: str, timeframe_minutes: int, at_time: datetime.datetime) -> Optional[dict]:
    # Fetch 5 or 15 min candle for given option symbol at specific time
    # Return dict with open, close, high, low
    # Placeholder: return dummy candle data
    return {'open': 100.0, 'close': 110.0, 'high': 115.0, 'low': 95.0}

def send_alert(message: str):
    # Dummy alert sender (print to console or send email/webhook)
    print(f"ALERT: {message}")

class OptionCrossoverStrategy:
    def __init__(self):
        self.index = 'Nifty'  # 'Nifty', 'Sensex', 'BankNifty' - default
        self.option_type = 'weekly'  # 'weekly' or 'monthly'
        self.tf_minutes = 5  # 5 or 15 min timeframe for crossover check
        self.strike_type = 'nearest'  # 'ATM', 'ITM', 'OTM', or 'nearest'
        self.max_trades_per_day = 3
        self.lots = 1
        self.sl = 10
        self.target = 15
        self.exit_time = datetime.time(15, 26)  # 3:26 PM IST exit time
        self.trades_taken = 0
        self.in_trade = False
        self.trade_entry_price = 0.0
        self.trade_direction = None  # 'CE' or 'PE'
        self.log_file = "strategy_log.txt"
        logging.basicConfig(filename=self.log_file, level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def select_strikes(self, spot_price: float):
        # Select strike prices based on spot and strike_type
        # Placeholder logic: nearest strike rounded to 50 points
        nearest_strike = round(spot_price / 50) * 50
        if self.strike_type == 'ATM' or self.strike_type == 'nearest':
            ce_strike = nearest_strike
            pe_strike = nearest_strike
        elif self.strike_type == 'ITM':
            ce_strike = nearest_strike - 50
            pe_strike = nearest_strike + 50
        elif self.strike_type == 'OTM':
            ce_strike = nearest_strike + 50
            pe_strike = nearest_strike - 50
        else:
            ce_strike = nearest_strike
            pe_strike = nearest_strike
        return ce_strike, pe_strike

    def check_crossover(self, ce_price, pe_price, prev_ce_price, prev_pe_price):
        # Return crossover type or None
        # CE > PE to PE > CE or vice versa
        if prev_ce_price > prev_pe_price and ce_price < pe_price:
            return 'PE_cross_over_CE'
        elif prev_pe_price > prev_ce_price and ce_price > pe_price:
            return 'CE_cross_over_PE'
        else:
            return None

    def bodies_do_not_overlap(self, candle1, candle2):
        # Check if candle bodies (open-close) do NOT overlap
        c1_low = min(candle1['open'], candle1['close'])
        c1_high = max(candle1['open'], candle1['close'])
        c2_low = min(candle2['open'], candle2['close'])
        c2_high = max(candle2['open'], candle2['close'])
        return c1_high < c2_low or c2_high < c1_low

    def run_strategy(self):
        # Main loop - placeholder example for intraday monitoring
        # You would run this every 5 or 15 minutes depending on TF
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))  # IST timezone

        if now.time() > self.exit_time:
            if self.in_trade:
                logging.info("Exiting trade at market close.")
                send_alert("Exiting all trades at 3:26 PM IST")
                self.in_trade = False
            return

        # Get spot price at 9:14am IST
        nine_fourteen = now.replace(hour=9, minute=14, second=0, microsecond=0)
        spot_price = get_spot_price(self.index, nine_fourteen.time())
        ce_strike, pe_strike = self.select_strikes(spot_price)

        # Build option symbols (example format)
        ce_symbol = f"{self.index}_{self.option_type}_CE_{ce_strike}"
        pe_symbol = f"{self.index}_{self.option_type}_PE_{pe_strike}"

        # Get current and previous candle prices for CE and PE
        tf = self.tf_minutes
        current_candle_time = now.replace(second=0, microsecond=0)
        prev_candle_time = current_candle_time - datetime.timedelta(minutes=tf)

        ce_candle = get_option_candle(ce_symbol, tf, current_candle_time)
        pe_candle = get_option_candle(pe_symbol, tf, current_candle_time)
        prev_ce_candle = get_option_candle(ce_symbol, tf, prev_candle_time)
        prev_pe_candle = get_option_candle(pe_symbol, tf, prev_candle_time)

        if None in [ce_candle, pe_candle, prev_ce_candle, prev_pe_candle]:
            logging.warning("Missing candle data, skipping this cycle")
            return

        # Check crossover
        crossover = self.check_crossover(
            ce_candle['close'], pe_candle['close'],
            prev_ce_candle['close'], prev_pe_candle['close']
        )

        if crossover is None:
            logging.info("No crossover detected at this time.")
            return

        # Check if bodies do not overlap on crossover candle
        if not self.bodies_do_not_overlap(ce_candle, pe_candle):
            logging.info("Bodies overlap on crossover candle, waiting for next candle.")
            # Wait until next candle satisfies condition (to be implemented in live loop)
            return

        # Enter trade on next candle open (simulated here as immediate for example)
        if self.trades_taken >= self.max_trades_per_day:
            logging.info("Max trades reached for today.")
            return

        if self.in_trade:
            logging.info("Already in trade, no new entry.")
            return

        self.in_trade = True
        self.trades_taken += 1
        self.trade_direction = 'CE' if crossover == 'CE_cross_over_PE' else 'PE'
        self.trade_entry_price = ce_candle['close'] if self.trade_direction == 'CE' else pe_candle['close']

        sl, target = self.sl, self.target
        if self.index in ['Sensex', 'BankNifty']:
            sl, target = 30, 40
        logging.info(f"Entering trade {self.trade_direction} at {self.trade_entry_price} with SL {sl} and target {target}")
        send_alert(f"Trade Entry: {self.trade_direction} @ {self.trade_entry_price} SL={sl} Target={target}")

    # Add more methods as needed for SL/Target monitoring and trailing SL

def main():
    strategy = OptionCrossoverStrategy()
    # For testing, just run one cycle
    strategy.run_strategy()

if __name__ == "__main__":
    main()
