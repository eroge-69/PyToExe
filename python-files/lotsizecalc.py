def calculate_lot_size(risk_dollars, stop_loss_pips, pair_type="USD"): 
    """
    Calculate lot size for Forex trading.

    risk_dollars : float -> Risk in account currency (USD)
    stop_loss_pips : float -> Stop loss in pips
    pair_type : str -> "USD" for USD-quoted pairs (EURUSD, GBPUSD etc.)
                   -> "JPY" for JPY-quoted pairs (USDJPY, EURJPY etc.)

    Returns: lot size (float)
    """

    # Pip value per 1 standard lot
    if pair_type.upper() == "USD":
        pip_value_per_lot = 10   # $10 per pip per 1 lot
    elif pair_type.upper() == "JPY":
        pip_value_per_lot = 9.1  # approx $9.1 depending on rate, adjustable
    else:
        print("Unknown pair type, defaulting to USD-based pip value.")
        pip_value_per_lot = 10

    # Risk per pip in $ = Total Risk ÷ Stop loss
    risk_per_pip = risk_dollars / stop_loss_pips

    # Lot size = Required pip value ÷ Pip value per lot
    lot_size = risk_per_pip / pip_value_per_lot

    return round(lot_size, 2)


if __name__ == "__main__":
    print("=== Forex Lot Size Calculator ===")
    risk = float(input("Enter your risk in USD: "))
    sl = float(input("Enter stop loss in pips: "))
    pair = input("Enter pair type (USD/JPY): ")

    lot = calculate_lot_size(risk, sl, pair)
    print(f"\nRecommended Lot Size: {lot} lots")
