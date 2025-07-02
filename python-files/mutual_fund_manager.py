import datetime
import sqlite3
from contextlib import contextmanager

class MutualFundManager:
    def __init__(self, db_name="mutual_funds.db"):
        self.db_name = db_name
        self._initialize_database()

    def _initialize_database(self):
        """Initialize SQLite database and create tables if they don't exist."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            # Ledger table for transaction history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    fund_name TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    rate REAL NOT NULL,
                    date TEXT NOT NULL,
                    profit_loss REAL
                )
            """)
            # Holdings table for active lots
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS holdings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fund_name TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    rate REAL NOT NULL,
                    date TEXT NOT NULL
                )
            """)
            conn.commit()

    @contextmanager
    def _get_db_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_name)
        try:
            yield conn
        finally:
            conn.close()

    def add_lot(self):
        """Adds a new mutual fund purchase lot to the holdings and ledger."""
        fund_name = input("Enter Mutual Fund Name: ").strip().upper()
        try:
            quantity = float(input("Enter Quantity: "))
            rate = float(input("Enter Rate per unit: "))
            date_str = input("Enter Purchase Date (YYYY-MM-DD): ")
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

        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            # Add to holdings
            cursor.execute("""
                INSERT INTO holdings (fund_name, quantity, rate, date)
                VALUES (?, ?, ?, ?)
            """, (fund_name, quantity, rate, date_str))
            # Add to ledger
            cursor.execute("""
                INSERT INTO ledger (type, fund_name, quantity, rate, date, profit_loss)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ('add', fund_name, quantity, rate, date_str, None))
            conn.commit()

        print(f"Added {quantity} units of {fund_name} at {rate} per unit on {date_str}.")

    def redeem_lot(self):
        """Handles mutual fund redemption, calculates profit/loss using FIFO."""
        fund_name = input("Enter Mutual Fund Name for redemption: ").strip().upper()
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, quantity, rate, date FROM holdings WHERE fund_name = ? ORDER BY date", (fund_name,))
            holdings = [{'id': row[0], 'quantity': row[1], 'rate': row[2], 'date': datetime.datetime.strptime(row[3], "%Y-%m-%d")} for row in cursor.fetchall()]
        
        if not holdings:
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

        available_quantity = sum(lot['quantity'] for lot in holdings)
        if redeem_quantity > available_quantity:
            print(f"Insufficient units for {fund_name}. Available: {available_quantity}, Requested: {redeem_quantity}")
            return

        profit_loss = 0
        remaining_redeem_quantity = redeem_quantity
        redeemed_from_lots = []

        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            for lot in holdings:
                if remaining_redeem_quantity <= 0:
                    break

                if lot['quantity'] >= remaining_redeem_quantity:
                    profit_loss += (redeem_rate - lot['rate']) * remaining_redeem_quantity
                    cursor.execute("UPDATE holdings SET quantity = ? WHERE id = ?", (lot['quantity'] - remaining_redeem_quantity, lot['id']))
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
                    cursor.execute("DELETE FROM holdings WHERE id = ?", (lot['id'],))

            # Add redemption to ledger
            cursor.execute("""
                INSERT INTO ledger (type, fund_name, quantity, rate, date, profit_loss)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ('redeem', fund_name, redeem_quantity, redeem_rate, date_str, profit_loss))
            conn.commit()

        print(f"Redeemed {redeem_quantity} units of {fund_name} at {redeem_rate} per unit.")
        print(f"Profit/Loss on redemption: {profit_loss:.2f}")

    def show_ledger(self):
        """Displays all transactions in the ledger, script-wise."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT type, fund_name, quantity, rate, date, profit_loss FROM ledger")
            ledger = [{'type': row[0], 'fund_name': row[1], 'quantity': row[2], 'rate': row[3], 'date': datetime.datetime.strptime(row[4], "%Y-%m-%d"), 'profit_loss': row[5]} for row in cursor.fetchall()]

        if not ledger:
            print("No transactions to display in the ledger yet.")
            return

        print("\n--- Mutual Fund Ledger ---")
        ledger_by_fund = {}
        for transaction in ledger:
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
                    # Note: redeemed_from details are not stored in SQLite for simplicity
        print("\n--- End of Ledger ---")

    def show_balance(self):
        """Displays the closing balance of units in hand for each mutual fund."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT fund_name, quantity, rate, date FROM holdings")
            holdings = {}
            for row in cursor.fetchall():
                fund_name, quantity, rate, date = row
                if fund_name not in holdings:
                    holdings[fund_name] = []
                holdings[fund_name].append({
                    'quantity': quantity,
                    'rate': rate,
                    'date': datetime.datetime.strptime(date, "%Y-%m-%d")
                })

        if not holdings:
            print("No holdings available.")
            return

        print("\n--- Closing Balance ---")
        total_value = 0
        for fund_name, lots in holdings.items():
            total_units = sum(lot['quantity'] for lot in lots)
            total_investment = sum(lot['quantity'] * lot['rate'] for lot in lots)
            print(f"\nFund: {fund_name}")
            print(f"Total Units: {total_units:.2f}")
            print(f"Total Investment Value: {total_investment:.2f}")
            print("Lots:")
            for lot in sorted(lots, key=lambda x: x['date']):
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