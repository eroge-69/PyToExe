from datetime import datetime

def xirr(cash_flows, guess=0.1, max_iterations=1000, tol=1e-6):
    def npv(rate):
        return sum(
            cf / (1 + rate) ** ((date - t0).days / 365.0)
            for date, cf in cash_flows
        )

    def d_npv(rate):
        return sum(
            -((date - t0).days / 365.0) * cf / (1 + rate) ** (((date - t0).days / 365.0) + 1)
            for date, cf in cash_flows
        )

    t0 = cash_flows[0][0]
    rate = guess

    for _ in range(max_iterations):
        npv_val = npv(rate)
        d_npv_val = d_npv(rate)
        if d_npv_val == 0:
            raise ZeroDivisionError("Zero derivative. Try a different guess.")
        new_rate = rate - npv_val / d_npv_val
        if abs(new_rate - rate) < tol:
            return new_rate
        rate = new_rate

    raise ValueError("XIRR did not converge.")

def get_cash_flows_from_user():
    print("Enter your cash flows one by one.")
    print("Format: YYYY-MM-DD amount (e.g., 2020-01-01 -1000)")
    print("Type 'done' when finished.\n")

    cash_flows = []
    while True:
        entry = input("Cash flow: ").strip()
        if entry.lower() == "done":
            break
        try:
            date_str, amount_str = entry.split()
            date = datetime.strptime(date_str, "%Y-%m-%d")
            amount = float(amount_str)
            cash_flows.append((date, amount))
        except ValueError:
            print("Invalid format. Please enter in format: YYYY-MM-DD amount")

    if not cash_flows:
        raise ValueError("No cash flows entered.")
    return cash_flows

def print_cash_flows_table(cash_flows):
    print("\nEntered Cash Flows:")
    print("-" * 30)
    print(f"{'Date':<15} {'Amount':>10}")
    print("-" * 30)
    for date, amount in cash_flows:
        print(f"{date.strftime('%Y-%m-%d'):<15} {amount:>10,.2f}")
    print("-" * 30)

# --- Main Program ---
if __name__ == "__main__":
    try:
        flows = get_cash_flows_from_user()
        print_cash_flows_table(flows)
        result = xirr(flows)
        print(f"\nXIRR: {result:.6f} or {result * 100:.2f}%")
    except Exception as e:
        print(f"Error: {e}")