import datetime

class MutualFundManager:
    def __init__(self):
        self.ledger = []
        self.holdings = {}

    def add_lot(self):
        """Adds a new mutual fund purchase lot to the holdings and ledger."""
        fund_name = input("Enter Mutual Fund Name: ").strip().upper()
        try:
            quantity = float(input("Enter Quantity: "))
            rate = float(input("Enter Rate per unit: "))
            date_str = input("Enter Purchase Date (YYYY-MM-DD): ")
            # Validate and parse date
            try:
                purchase_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
                return
            
            if quantity <= 0 or rate <= 0:
                print("Quantity and Rate must be positive numbers.")
                return
        except ValueError:
            print("Invalid input for quantity or rate. Please enter numeric values.")
            return

        # Add to holdings for FIFO tracking
        if fund_name not in self.holdings:
            self.holdings[fund_name] = []
        self.holdings[fund_name].append({
            'quantity': quantity,
            'rate': rate,
            'date': purchase_date
        })
        # Sort holdings for FIFO - oldest first
        self.holdings[fund_name].sort(key=lambda x: x['date'])

        # Add to ledger
        self.ledger.append({
            'type': 'add',
            'fund_name': fund_name,
            'quantity': quantity,
            'rate': rate,
            'date': purchase_date,
            'profit_loss': None
        })
        print(f"Added {quantity} units of {fund_name} at {rate} per unit on {date_str}.")

    def redeem_lot(self):
        """Handles mutual fund redemption, calculates profit/loss using FIFO."""
        fund_name = input("Enter Mutual Fund Name for redemption: ").strip().upper()
        if fund_name not in self.holdings or not self.holdings[fund_name]:
            print(f"No holdings found for {fund_name}. Cannot redeem.")
            return

        try:
            redeem_quantity = float(input("Enter Quantity to redeem: "))
            redeem_rate = float(input("Enter Redemption Rate per unit: "))
            date_str = input("Enter Redemption Date (YYYY-MM-DD): ")
            try:
                redeem_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
                return
                
            if redeem_quantity <= 0 or redeem_rate <= 0:
                print("Quantity and Rate must be positive numbers.")
                return
        except ValueError:
            print("Invalid input for quantity or rate. Please enter numeric values.")
            return

        available_quantity = sum(lot['quantity'] for lot in self.holdings[fund_name])
        if redeem_quantity > available_quantity:
            print(f"Insufficient units for {fund_name}. Available: {available_quantity}, Requested: {redeem_quantity}")
            return

        profit_loss = 0
        remaining_redeem_quantity = redeem_quantity
        redeemed_from_lots = []

        # FIFO logic
        for lot in sorted(self.holdings[fund_name], key=lambda x: x['date']):
            if remaining_redeem_quantity <= 0:
                break

            if lot['quantity'] >= remaining_redeem_quantity:
                profit_loss += (redeem_rate - lot['rate']) * remaining_redeem_quantity
                lot['quantity'] -= remaining_redeem_quantity
                redeemed_from_lots.append({
                    'purchase_date': lot['date'],
                    'purchase_rate': lot['rate'],
                    'redeemed_quantity': remaining_redeem_quantity
                })
                remaining_redeem_quantity = 0
            else:
                profit_loss += (redeem_rate - lot['rate']) * lot['quantity']
                remaining_redeem_quantity -= lot['quantity']
                redeemed_from_lots.append({
                    'purchase_date': lot['date'],
                    'purchase_rate': lot['rate'],
                    'redeemed_quantity': lot['quantity']
                })
                lot['quantity'] = 0

        # Remove fully redeemed lots
        self.holdings[fund_name] = [lot for lot in self.holdings[fund_name] if lot['quantity'] > 0]
        if not self.holdings[fund_name]:
            del self.holdings[fund_name]

        # Add to ledger
        self.ledger.append({
            'type': 'redeem',
            'fund_name': fund_name,
            'quantity': redeem_quantity,
            'rate': redeem_rate,
            'date': redeem_date,
            'profit_loss': profit_loss,
            'redeemed_from': redeemed_from_lots
        })

        print(f"Redeemed {redeem_quantity} units of {fund_name} at {redeem_rate} per unit.")
        print(f"Profit/Loss on redemption: {profit_loss:.2f}")

    def show_ledger(self):
        """Displays all transactions in the ledger, script-wise."""
        if not self.ledger:
            print("No transactions to display in the ledger yet.")
            return

        print("\n--- Mutual Fund Ledger ---")
        ledger_by_fund = {}
        for transaction in self.ledger:
            fund_name = transaction['fund_name']
            if fund_name not in ledger_by_fund:
                ledger_by_fund[fund_name] = []
            ledger_by_fund[fund_name].append(transaction)

        for fund_name, transactions in ledger_by_fund.items():
            print(f"\nFund: {fund_name}")
            print("-" * (len(fund_name) + 6))
            for t in transactions:
                date_str = t['date'].strftime("%Y-%m-%d")
                if t['type'] == 'add':
                    print(f"  [{date_str}] Type: ADD, Qty: {t['quantity']:.2f}, Rate: {t['rate']:.2f}")
                elif t['type'] == 'redeem':
                    profit_loss_str = f", P/L: {t['profit_loss']:.2f}" if t['profit_loss'] is not None else ""
                    print(f"  [{date_str}] Type: REDEEM, Qty: {t['quantity']:.2f}, Rate: {t['rate']:.2f}{profit_loss_str}")
                    if 'redeemed_from' in t and t['redeemed_from']:
                        print("    Redeemed from lots:")
                        for lot_info in t['redeemed_from']:
                            print(f"      - Purchased on {lot_info['purchase_date'].strftime('%Y-%m-%d')} at {lot_info['purchase_rate']:.2f}, Redeemed: {lot_info['redeemed_quantity']:.2f}")
        print("\n--- End of Ledger ---")

    def show_balance(self):
        """Displays the closing balance of units in hand for each mutual fund."""
        if not self.holdings:
            print("No holdings available.")
            return

        print("\n--- Closing Balance ---")
        total_value = 0
        for fund_name, lots in self.holdings.items():
            total_units = sum(lot['quantity'] for lot in lots)
            total_investment = sum(lot['quantity'] * lot['rate'] for lot in lots)
            print(f"\nFund: {fund_name}")
            print(f"Total Units: {total_units:.2f}")
            print(f"Total Investment Value: {total_investment:.2f}")
            print("Lots:")
            for lot in lots:
                lot_value = lot['quantity'] * lot['rate']
                print(f"  - Date: {lot['date'].strftime('%Y-%m-%d')}, Units: {lot['quantity']:.2f}, Rate: {lot['rate']:.2f}, Value: {lot_value:.2f}")
            total_value += total_investment
        print(f"\nTotal Portfolio Value: {total_value:.2f}")
        print("\n--- End of Balance ---")

def main():
    manager = MutualFundManager()

    while True:
        print("\n--- Mutual Fund Manager ---")
        print("1. Add Lot (Purchase)")
        print("2. Redemption")
        print("3. Show Ledger")
        print("4. Show Balance")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            manager.add_lot()
        elif choice == '2':
            manager.redeem_lot()
        elif choice == '3':
            manager.show_ledger()
        elif choice == '4':
            manager.show_balance()
        elif choice == '5':
            print("Exiting Mutual Fund Manager. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()