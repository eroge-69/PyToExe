import tkinter as tk
from tkinter import ttk, messagebox
import random
import datetime

class ForexTradingBotGUI:
    """
    A mock FOREX trading bot GUI application using Tkinter.
    This application simulates trade tracking and does NOT connect to live FOREX markets.
    """
    def __init__(self, master):
        self.master = master
        master.title("Mock FOREX Trading Bot")
        master.geometry("1000x700") # Set initial window size
        master.resizable(True, True) # Allow window resizing
        master.configure(bg='#2e2e2e') # Dark background for a modern look

        self.balance = 10000.00 # Starting mock balance
        self.open_trades = []
        self.closed_trades = []
        self.trade_id_counter = 0

        # Style for themed widgets
        self.style = ttk.Style()
        self.style.theme_use('clam') # 'clam' or 'alt' often look better than 'default'
        self.style.configure("TFrame", background="#3c3c3c")
        self.style.configure("TLabel", background="#3c3c3c", foreground="#e0e0e0", font=('Arial', 10))
        self.style.configure("TButton", background="#5c5c5c", foreground="#ffffff", font=('Arial', 10, 'bold'), borderwidth=0, focusthickness=3, focuscolor='none')
        self.style.map("TButton",
                       background=[('active', '#7a7a7a')],
                       foreground=[('active', '#ffffff')])
        self.style.configure("Treeview.Heading", background="#555555", foreground="#ffffff", font=('Arial', 10, 'bold'))
        self.style.configure("Treeview", background="#4a4a4a", foreground="#ffffff", fieldbackground="#4a4a4a", borderwidth=0)
        self.style.map("Treeview", background=[('selected', '#007acc')]) # Highlight selected row

        self.create_widgets()
        self.update_dashboard()

    def create_widgets(self):
        """Initializes and places all GUI widgets."""
        # Main frames
        top_frame = ttk.Frame(self.master, padding="10", style="TFrame")
        top_frame.pack(side=tk.TOP, fill=tk.X, expand=False)

        main_content_frame = ttk.Frame(self.master, padding="10", style="TFrame")
        main_content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        log_frame = ttk.Frame(self.master, padding="10", style="TFrame")
        log_frame.pack(side=tk.BOTTOM, fill=tk.X, expand=False)

        # Dashboard elements in top_frame
        self.balance_label = ttk.Label(top_frame, text=f"Balance: ${self.balance:,.2f}", font=('Arial', 14, 'bold'))
        self.balance_label.pack(side=tk.LEFT, padx=10, pady=5)

        # Mock Trade Controls
        trade_controls_frame = ttk.Frame(top_frame, style="TFrame")
        trade_controls_frame.pack(side=tk.RIGHT, padx=10, pady=5)

        ttk.Label(trade_controls_frame, text="Currency Pair:").grid(row=0, column=0, padx=5, pady=2, sticky='w')
        self.pair_entry = ttk.Entry(trade_controls_frame, width=10)
        self.pair_entry.insert(0, "EUR/USD")
        self.pair_entry.grid(row=0, column=1, padx=5, pady=2, sticky='ew')

        ttk.Label(trade_controls_frame, text="Amount ($):").grid(row=0, column=2, padx=5, pady=2, sticky='w')
        self.amount_entry = ttk.Entry(trade_controls_frame, width=10)
        self.amount_entry.insert(0, "1000")
        self.amount_entry.grid(row=0, column=3, padx=5, pady=2, sticky='ew')

        ttk.Button(trade_controls_frame, text="Open Long Trade (Buy)", command=lambda: self.open_mock_trade("BUY")).grid(row=0, column=4, padx=5, pady=2)
        ttk.Button(trade_controls_frame, text="Open Short Trade (Sell)", command=lambda: self.open_mock_trade("SELL")).grid(row=0, column=5, padx=5, pady=2)

        # Notebook for Open and Closed Trades
        self.notebook = ttk.Notebook(main_content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Open Trades Tab
        open_trades_tab = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(open_trades_tab, text="Open Trades 📈")

        self.open_trades_tree = ttk.Treeview(open_trades_tab, columns=("ID", "Pair", "Type", "Entry Price", "Current Price", "P/L", "Open Time"), show="headings")
        self.open_trades_tree.heading("ID", text="ID")
        self.open_trades_tree.heading("Pair", text="Pair")
        self.open_trades_tree.heading("Type", text="Type")
        self.open_trades_tree.heading("Entry Price", text="Entry Price")
        self.open_trades_tree.heading("Current Price", text="Current Price")
        self.open_trades_tree.heading("P/L", text="P/L")
        self.open_trades_tree.heading("Open Time", text="Open Time")

        self.open_trades_tree.column("ID", width=50, anchor=tk.CENTER)
        self.open_trades_tree.column("Pair", width=100, anchor=tk.CENTER)
        self.open_trades_tree.column("Type", width=70, anchor=tk.CENTER)
        self.open_trades_tree.column("Entry Price", width=100, anchor=tk.CENTER)
        self.open_trades_tree.column("Current Price", width=100, anchor=tk.CENTER)
        self.open_trades_tree.column("P/L", width=80, anchor=tk.CENTER)
        self.open_trades_tree.column("Open Time", width=150, anchor=tk.CENTER)

        self.open_trades_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Button(open_trades_tab, text="Close Selected Trade", command=self.close_selected_trade).pack(pady=5)

        # Closed Trades Tab
        closed_trades_tab = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(closed_trades_tab, text="Closed Trades 📊")

        self.closed_trades_tree = ttk.Treeview(closed_trades_tab, columns=("ID", "Pair", "Type", "Entry Price", "Exit Price", "P/L", "Open Time", "Close Time"), show="headings")
        self.closed_trades_tree.heading("ID", text="ID")
        self.closed_trades_tree.heading("Pair", text="Pair")
        self.closed_trades_tree.heading("Type", text="Type")
        self.closed_trades_tree.heading("Entry Price", text="Entry Price")
        self.closed_trades_tree.heading("Exit Price", text="Exit Price")
        self.closed_trades_tree.heading("P/L", text="P/L")
        self.closed_trades_tree.heading("Open Time", text="Open Time")
        self.closed_trades_tree.heading("Close Time", text="Close Time")

        self.closed_trades_tree.column("ID", width=50, anchor=tk.CENTER)
        self.closed_trades_tree.column("Pair", width=100, anchor=tk.CENTER)
        self.closed_trades_tree.column("Type", width=70, anchor=tk.CENTER)
        self.closed_trades_tree.column("Entry Price", width=100, anchor=tk.CENTER)
        self.closed_trades_tree.column("Exit Price", width=100, anchor=tk.CENTER)
        self.closed_trades_tree.column("P/L", width=80, anchor=tk.CENTER)
        self.closed_trades_tree.column("Open Time", width=150, anchor=tk.CENTER)
        self.closed_trades_tree.column("Close Time", width=150, anchor=tk.CENTER)

        self.closed_trades_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Log Text Area
        ttk.Label(log_frame, text="Trade Log:").pack(anchor=tk.W)
        self.log_text = tk.Text(log_frame, height=8, state='disabled', bg="#3c3c3c", fg="#e0e0e0", font=('Arial', 9), borderwidth=0, relief="flat")
        self.log_text.pack(fill=tk.X, expand=True, padx=5, pady=5)
        self.log_text.tag_config('info', foreground='white')
        self.log_text.tag_config('success', foreground='green')
        self.log_text.tag_config('error', foreground='red')

        self.log_message("Welcome to the Mock FOREX Trading Bot GUI!", 'info')

        # Start a periodic update for mock prices and P/L
        self.master.after(2000, self.update_mock_prices) # Update every 2 seconds

    def log_message(self, message, tag='info'):
        """Appends a message to the log text area."""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {message}\n", tag)
        self.log_text.see(tk.END) # Scroll to the end
        self.log_text.config(state='disabled')

    def update_dashboard(self):
        """Updates the balance label and trade tables."""
        self.balance_label.config(text=f"Balance: ${self.balance:,.2f}")

        # Clear existing entries in open trades treeview
        for i in self.open_trades_tree.get_children():
            self.open_trades_tree.delete(i)
        # Populate open trades
        for trade in self.open_trades:
            self.open_trades_tree.insert("", "end", values=(
                trade['id'], trade['pair'], trade['type'],
                f"{trade['entry_price']:.5f}", f"{trade['current_price']:.5f}",
                f"{trade['p_l']:.2f}", trade['open_time'].strftime('%Y-%m-%d %H:%M:%S')
            ), tags=('profit' if trade['p_l'] >= 0 else 'loss'))
        self.open_trades_tree.tag_configure('profit', foreground='green')
        self.open_trades_tree.tag_configure('loss', foreground='red')

        # Clear existing entries in closed trades treeview
        for i in self.closed_trades_tree.get_children():
            self.closed_trades_tree.delete(i)
        # Populate closed trades
        for trade in self.closed_trades:
            self.closed_trades_tree.insert("", "end", values=(
                trade['id'], trade['pair'], trade['type'],
                f"{trade['entry_price']:.5f}", f"{trade['exit_price']:.5f}",
                f"{trade['p_l']:.2f}", trade['open_time'].strftime('%Y-%m-%d %H:%M:%S'),
                trade['close_time'].strftime('%Y-%m-%d %H:%M:%S')
            ), tags=('profit' if trade['p_l'] >= 0 else 'loss'))
        self.closed_trades_tree.tag_configure('profit', foreground='green')
        self.closed_trades_tree.tag_configure('loss', foreground='red')

    def open_mock_trade(self, trade_type):
        """Simulates opening a trade."""
        try:
            pair = self.pair_entry.get().upper()
            amount = float(self.amount_entry.get())

            if not pair or not amount > 0:
                messagebox.showerror("Input Error", "Please enter a valid currency pair and amount.")
                self.log_message("Failed to open trade: Invalid input.", 'error')
                return

            self.trade_id_counter += 1
            entry_price = round(random.uniform(1.00000, 1.20000), 5) # Mock entry price
            current_price = entry_price # Initially current price is entry price

            new_trade = {
                'id': self.trade_id_counter,
                'pair': pair,
                'type': trade_type,
                'amount': amount,
                'entry_price': entry_price,
                'current_price': current_price,
                'p_l': 0.0, # Initial P/L
                'open_time': datetime.datetime.now()
            }
            self.open_trades.append(new_trade)
            self.log_message(f"Opened {trade_type} trade #{new_trade['id']} for {pair} at {entry_price:.5f} with ${amount:,.2f}.", 'success')
            self.update_dashboard()
        except ValueError:
            messagebox.showerror("Input Error", "Amount must be a number.")
            self.log_message("Failed to open trade: Amount must be a number.", 'error')
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.log_message(f"An unexpected error occurred: {e}", 'error')


    def close_selected_trade(self):
        """Simulates closing the selected open trade."""
        selected_item = self.open_trades_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a trade to close.")
            return

        trade_id_to_close = int(self.open_trades_tree.item(selected_item, 'values')[0])
        trade_to_close = None
        for trade in self.open_trades:
            if trade['id'] == trade_id_to_close:
                trade_to_close = trade
                break

        if trade_to_close:
            exit_price = round(random.uniform(trade_to_close['current_price'] * 0.98, trade_to_close['current_price'] * 1.02), 5) # Mock exit price

            # Calculate P/L for closing
            if trade_to_close['type'] == "BUY":
                p_l = (exit_price - trade_to_close['entry_price']) * trade_to_close['amount']
            else: # SELL
                p_l = (trade_to_close['entry_price'] - exit_price) * trade_to_close['amount']

            self.balance += p_l # Update balance

            closed_trade = {
                'id': trade_to_close['id'],
                'pair': trade_to_close['pair'],
                'type': trade_to_close['type'],
                'entry_price': trade_to_close['entry_price'],
                'exit_price': exit_price,
                'p_l': p_l,
                'open_time': trade_to_close['open_time'],
                'close_time': datetime.datetime.now()
            }
            self.closed_trades.append(closed_trade)
            self.open_trades.remove(trade_to_close)
            self.log_message(f"Closed trade #{closed_trade['id']} for {closed_trade['pair']} at {exit_price:.5f}. P/L: ${p_l:,.2f}.", 'success')
            self.update_dashboard()
        else:
            self.log_message(f"Error: Trade #{trade_id_to_close} not found in open trades.", 'error')

    def update_mock_prices(self):
        """Periodically updates mock prices and calculates P/L for open trades."""
        for trade in self.open_trades:
            # Simulate price fluctuation (e.g., +/- 0.0005)
            fluctuation = random.uniform(-0.0005, 0.0005)
            trade['current_price'] = round(trade['current_price'] + fluctuation, 5)

            # Calculate P/L
            if trade['type'] == "BUY":
                trade['p_l'] = (trade['current_price'] - trade['entry_price']) * trade['amount']
            else: # SELL
                trade['p_l'] = (trade['entry_price'] - trade['current_price']) * trade['amount']

        self.update_dashboard()
        self.master.after(2000, self.update_mock_prices) # Schedule next update

if __name__ == "__main__":
    root = tk.Tk()
    app = ForexTradingBotGUI(root)
    root.mainloop()