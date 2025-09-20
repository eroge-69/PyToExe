import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import time
import json
import os
from datetime import datetime, timedelta
import webbrowser

class PolymarketBTCBot:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Polymarket BTC 15min Trading Bot")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a1a')
        
        # API endpoints
        self.gamma_api_base = "https://gamma-api.polymarket.com"
        self.clob_api_base = "https://clob.polymarket.com"
        
        # Trading parameters
        self.initial_capital = 1000
        self.current_capital = self.initial_capital
        self.base_bet = 10
        self.current_bet = self.base_bet
        self.follow_trend = True
        self.consecutive_losses = 0
        self.daily_trades = 0
        self.max_daily_trades = 20
        
        # Kelly Criterion parameters
        self.win_probability = 0.5
        self.total_trades = 0
        self.total_wins = 0
        
        # Market tracking
        self.current_market = None
        self.current_market_id = None
        self.last_btc_price = None
        self.last_direction = None
        self.position_start_price = None
        
        # Trading state
        self.is_running = False
        self.thread = None
        
        # Market data
        self.yes_price = 0.5
        self.no_price = 0.5
        self.market_end_time = None
        self.chainlink_btc_price = None
        
        self.setup_gui()
        self.load_settings()
        
    def setup_gui(self):
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#1a1a1a', foreground='white')
        style.configure('TFrame', background='#1a1a1a')
        style.configure('TLabelFrame', background='#1a1a1a', foreground='white')
        style.configure('TButton', background='#333333', foreground='white')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = tk.Label(main_frame, text="🚀 Polymarket BTC 15min Prediction Bot", 
                              font=("Arial", 16, "bold"), bg='#1a1a1a', fg='#00ff00')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0,10))
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ Bot Settings", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Capital settings
        tk.Label(settings_frame, text="Initial Capital ($):", bg='#1a1a1a', fg='white').grid(row=0, column=0, sticky=tk.W)
        self.capital_var = tk.StringVar(value=str(self.initial_capital))
        capital_entry = tk.Entry(settings_frame, textvariable=self.capital_var, width=12, bg='#333333', fg='white')
        capital_entry.grid(row=0, column=1, padx=(5,20))
        
        tk.Label(settings_frame, text="Base Bet ($):", bg='#1a1a1a', fg='white').grid(row=0, column=2, sticky=tk.W)
        self.base_bet_var = tk.StringVar(value=str(self.base_bet))
        bet_entry = tk.Entry(settings_frame, textvariable=self.base_bet_var, width=12, bg='#333333', fg='white')
        bet_entry.grid(row=0, column=3, padx=5)
        
        # Strategy selection
        tk.Label(settings_frame, text="Strategy:", bg='#1a1a1a', fg='white').grid(row=1, column=0, sticky=tk.W, pady=(10,0))
        self.strategy_var = tk.StringVar(value="Follow Trend")
        strategy_combo = ttk.Combobox(settings_frame, textvariable=self.strategy_var, 
                                    values=["Follow Trend", "Opposite Trend"], width=15)
        strategy_combo.grid(row=1, column=1, pady=(10,0), padx=(5,20))
        strategy_combo.state(['readonly'])
        
        # Market info frame
        market_frame = ttk.LabelFrame(main_frame, text="📈 Current Market Info", padding="10")
        market_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Market status labels
        self.market_status_label = tk.Label(market_frame, text="Market Status: Searching for active market...", 
                                          bg='#1a1a1a', fg='yellow', font=("Arial", 10, "bold"))
        self.market_status_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        self.btc_price_label = tk.Label(market_frame, text="Chainlink BTC Price: --", 
                                       bg='#1a1a1a', fg='#00ff00')
        self.btc_price_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.market_end_label = tk.Label(market_frame, text="Market Ends: --", 
                                        bg='#1a1a1a', fg='white')
        self.market_end_label.grid(row=1, column=1, sticky=tk.W, padx=(20,0), pady=2)
        
        # Price display frame
        price_frame = tk.Frame(market_frame, bg='#1a1a1a')
        price_frame.grid(row=2, column=0, columnspan=2, pady=5)
        
        self.yes_price_label = tk.Label(price_frame, text="YES: $0.50", 
                                       bg='#1a1a1a', fg='#00ff00', font=("Arial", 12, "bold"))
        self.yes_price_label.pack(side=tk.LEFT, padx=10)
        
        self.no_price_label = tk.Label(price_frame, text="NO: $0.50", 
                                      bg='#1a1a1a', fg='#ff4444', font=("Arial", 12, "bold"))
        self.no_price_label.pack(side=tk.LEFT, padx=10)
        
        # Control buttons frame
        control_frame = tk.Frame(main_frame, bg='#1a1a1a')
        control_frame.grid(row=3, column=0, columnspan=3, pady=15)
        
        self.start_button = tk.Button(control_frame, text="🚀 Start Trading", command=self.start_trading,
                                     bg='#00aa00', fg='white', font=("Arial", 12, "bold"), padx=20)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(control_frame, text="🛑 Stop Trading", command=self.stop_trading,
                                    bg='#aa0000', fg='white', font=("Arial", 12, "bold"), padx=20, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.refresh_button = tk.Button(control_frame, text="🔄 Refresh Market", command=self.find_active_market,
                                       bg='#0066aa', fg='white', font=("Arial", 10), padx=15)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        # Trading signals frame
        signals_frame = ttk.LabelFrame(main_frame, text="🎯 Trading Signals", padding="10")
        signals_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.signal_display = tk.Text(signals_frame, height=6, width=80, bg='#222222', fg='#00ff00',
                                     font=("Courier", 10), insertbackground='white')
        signal_scrollbar = tk.Scrollbar(signals_frame, orient="vertical", command=self.signal_display.yview)
        self.signal_display.configure(yscrollcommand=signal_scrollbar.set)
        self.signal_display.grid(row=0, column=0, sticky=(tk.W, tk.E))
        signal_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Trading Statistics", padding="10")
        stats_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Stats labels
        stats_left = tk.Frame(stats_frame, bg='#1a1a1a')
        stats_left.grid(row=0, column=0, sticky=tk.W)
        
        self.capital_label = tk.Label(stats_left, text=f"💰 Capital: ${self.current_capital}", 
                                     bg='#1a1a1a', fg='#00ff00', font=("Arial", 11, "bold"))
        self.capital_label.grid(row=0, column=0, sticky=tk.W)
        
        self.bet_label = tk.Label(stats_left, text=f"💸 Current Bet: ${self.current_bet}", 
                                 bg='#1a1a1a', fg='white')
        self.bet_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        stats_right = tk.Frame(stats_frame, bg='#1a1a1a')
        stats_right.grid(row=0, column=1, sticky=tk.W, padx=(40,0))
        
        self.win_rate_label = tk.Label(stats_right, text="🏆 Win Rate: 0%", 
                                      bg='#1a1a1a', fg='white')
        self.win_rate_label.grid(row=0, column=0, sticky=tk.W)
        
        self.trades_label = tk.Label(stats_right, text=f"📈 Trades: {self.daily_trades}/{self.max_daily_trades}", 
                                    bg='#1a1a1a', fg='white')
        self.trades_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Find active market on startup
        self.find_active_market()
    
    def get_chainlink_btc_price(self):
        """Get BTC price from Chainlink data feed"""
        try:
            # This would connect to Chainlink's BTC/USD price feed
            # For now, using a reliable BTC price API as proxy
            response = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=BTC", timeout=5)
            data = response.json()
            return float(data['data']['rates']['USD'])
        except:
            return None
    
    def find_active_market(self):
        """Find active BTC 15min prediction market"""
        try:
            self.log("🔍 Searching for active BTC 15min markets...")
            
            # Search for BTC markets
            response = requests.get(f"{self.gamma_api_base}/markets?active=true&closed=false", timeout=10)
            markets = response.json()
            
            btc_markets = []
            for market in markets:
                if ("btc" in market.get('question', '').lower() or 
                    "bitcoin" in market.get('question', '').lower()):
                    if "15m" in market.get('question', '').lower() or "15 min" in market.get('question', '').lower():
                        btc_markets.append(market)
            
            if btc_markets:
                # Get the most recent market
                self.current_market = btc_markets[0]
                self.current_market_id = self.current_market['id']
                
                self.market_status_label.config(text=f"✅ Active Market Found: {self.current_market['question'][:60]}...",
                                              fg='#00ff00')
                
                # Get market end time
                end_time = datetime.fromisoformat(self.current_market['endDate'].replace('Z', '+00:00'))
                self.market_end_time = end_time
                
                self.get_market_prices()
                self.log(f"📋 Market: {self.current_market['question']}")
                self.log(f"⏰ Ends: {end_time.strftime('%H:%M:%S')}")
                
            else:
                self.market_status_label.config(text="❌ No active BTC 15min markets found", fg='red')
                self.log("❌ No active BTC 15min prediction markets found")
                
        except Exception as e:
            self.log(f"❌ Error finding markets: {str(e)}")
            self.market_status_label.config(text="❌ Error connecting to Polymarket API", fg='red')
    
    def get_market_prices(self):
        """Get real-time share prices for current market"""
        if not self.current_market_id:
            return
        
        try:
            # Get market details including token prices
            response = requests.get(f"{self.gamma_api_base}/markets/{self.current_market_id}", timeout=5)
            market_data = response.json()
            
            # Extract YES/NO token prices
            if 'tokens' in market_data:
                for token in market_data['tokens']:
                    if token['outcome'] == 'Yes':
                        self.yes_price = float(token.get('price', 0.5))
                    elif token['outcome'] == 'No':
                        self.no_price = float(token.get('price', 0.5))
            
            # Update display
            self.yes_price_label.config(text=f"YES: ${self.yes_price:.3f}")
            self.no_price_label.config(text=f"NO: ${self.no_price:.3f}")
            
            # Get Chainlink BTC price
            btc_price = self.get_chainlink_btc_price()
            if btc_price:
                self.chainlink_btc_price = btc_price
                self.btc_price_label.config(text=f"Chainlink BTC Price: ${btc_price:,.2f}")
            
            # Update market end time display
            if self.market_end_time:
                time_left = self.market_end_time - datetime.now()
                if time_left.total_seconds() > 0:
                    minutes_left = int(time_left.total_seconds() / 60)
                    self.market_end_label.config(text=f"Market Ends in: {minutes_left} min")
                else:
                    self.market_end_label.config(text="Market Ended - Finding new market...")
                    self.find_active_market()
                    
        except Exception as e:
            self.log(f"❌ Error getting market prices: {str(e)}")
    
    def calculate_kelly_bet(self):
        """Calculate optimal bet size using Kelly Criterion"""
        if self.total_trades < 5:
            return self.base_bet
        
        win_prob = self.total_wins / self.total_trades
        
        # For Polymarket: if you buy YES at price p, you win (1-p)/p if correct
        # Kelly = (bp - q) / b where b = (1-p)/p, p = win_prob, q = 1-win_prob
        
        current_price = self.yes_price if self.get_signal() == "BUY_YES" else self.no_price
        b = (1 - current_price) / current_price  # Odds received
        
        kelly_fraction = (b * win_prob - (1 - win_prob)) / b
        kelly_bet = max(0.01, kelly_fraction) * self.current_capital
        
        # Cap at 10% of capital and ensure minimum bet
        return min(max(kelly_bet, 5), self.current_capital * 0.1)
    
    def get_signal(self):
        """Generate trading signal based on strategy"""
        if not self.chainlink_btc_price:
            return None
        
        # Determine trend direction
        if self.last_btc_price:
            if self.chainlink_btc_price > self.last_btc_price:
                current_trend = "UP"
            else:
                current_trend = "DOWN"
        else:
            current_trend = "UP"  # Default
        
        # Apply strategy
        if self.follow_trend:
            signal_direction = current_trend
        else:
            signal_direction = "DOWN" if current_trend == "UP" else "UP"
        
        # Convert to Polymarket signal
        return "BUY_YES" if signal_direction == "UP" else "BUY_NO"
    
    def should_execute_trade(self):
        """Check if we should execute a trade"""
        if not self.current_market or not self.market_end_time:
            return False
        
        # Check if we're in the first 5 minutes of a 15-minute cycle
        now = datetime.now()
        time_left = (self.market_end_time - now).total_seconds()
        
        # Trade in first 5 minutes (when 10-15 minutes remain)
        return 600 <= time_left <= 900  # 10-15 minutes remaining
    
    def execute_trade_signal(self):
        """Generate and display trade signal"""
        signal = self.get_signal()
        if not signal:
            return
        
        bet_size = self.calculate_kelly_bet()
        current_price = self.yes_price if signal == "BUY_YES" else self.no_price
        shares_to_buy = bet_size / current_price
        
        # Calculate expected profit
        expected_profit = shares_to_buy * (1 - current_price) if signal == "BUY_YES" else shares_to_buy * (1 - self.no_price)
        max_loss = bet_size
        
        # Generate trade signal
        signal_text = f"""
🚨 TRADE SIGNAL 🚨
Time: {datetime.now().strftime('%H:%M:%S')}
Action: {signal}
Price: ${current_price:.3f}
Recommended Bet: ${bet_size:.2f}
Shares to Buy: {shares_to_buy:.1f}
Max Profit: ${expected_profit:.2f}
Max Loss: ${max_loss:.2f}
Kelly %: {(bet_size/self.current_capital)*100:.1f}%
BTC Price: ${self.chainlink_btc_price:,.2f}
-------------------------------------------"""
        
        self.log(signal_text)
        
        # Update position tracking
        self.position_start_price = self.chainlink_btc_price
        self.total_trades += 1
        
        # Show notification
        self.signal_display.insert(tk.END, signal_text + "\n")
        self.signal_display.see(tk.END)
        
        # Flash the signal
        self.root.configure(bg='#ffff00')
        self.root.after(200, lambda: self.root.configure(bg='#1a1a1a'))
    
    def trading_loop(self):
        """Main trading loop"""
        while self.is_running:
            try:
                # Update market prices every 10 seconds
                self.get_market_prices()
                
                # Check for trade opportunities
                if self.should_execute_trade():
                    self.execute_trade_signal()
                    time.sleep(60)  # Wait 1 minute before next signal
                
                # Check if current market ended
                if self.market_end_time and datetime.now() > self.market_end_time:
                    self.log("📋 Market ended. Searching for new market...")
                    self.find_active_market()
                
                # Update last BTC price for trend calculation
                if self.chainlink_btc_price:
                    self.last_btc_price = self.chainlink_btc_price
                
                time.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                self.log(f"❌ Error in trading loop: {str(e)}")
                time.sleep(30)
    
    def start_trading(self):
        """Start the trading bot"""
        try:
            self.initial_capital = float(self.capital_var.get())
            self.current_capital = self.initial_capital
            self.base_bet = float(self.base_bet_var.get())
            self.follow_trend = self.strategy_var.get() == "Follow Trend"
            
            if not self.current_market:
                self.find_active_market()
            
            if not self.current_market:
                messagebox.showerror("Error", "No active BTC markets found!")
                return
            
            self.is_running = True
            self.thread = threading.Thread(target=self.trading_loop, daemon=True)
            self.thread.start()
            
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            
            self.log("🚀 Trading bot started!")
            self.log(f"💰 Capital: ${self.current_capital}")
            self.log(f"📈 Strategy: {self.strategy_var.get()}")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")
    
    def stop_trading(self):
        """Stop the trading bot"""
        self.is_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.log("🛑 Trading bot stopped!")
    
    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)  # Also print to console
        
        # Add to signal display if it's a signal
        if "TRADE SIGNAL" in message or "🚨" in message:
            self.signal_display.insert(tk.END, message + "\n")
            self.signal_display.see(tk.END)
    
    def update_stats(self):
        """Update statistics display"""
        self.capital_label.config(text=f"💰 Capital: ${self.current_capital:.2f}")
        self.bet_label.config(text=f"💸 Current Bet: ${self.current_bet:.2f}")
        
        win_rate = (self.total_wins / self.total_trades * 100) if self.total_trades > 0 else 0
        self.win_rate_label.config(text=f"🏆 Win Rate: {win_rate:.1f}%")
        
        self.trades_label.config(text=f"📈 Trades: {self.daily_trades}/{self.max_daily_trades}")
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists("polymarket_settings.json"):
                with open("polymarket_settings.json", "r") as f:
                    settings = json.load(f)
                    self.total_trades = settings.get("total_trades", 0)
                    self.total_wins = settings.get("total_wins", 0)
        except:
            pass
    
    def save_settings(self):
        """Save settings to file"""
        settings = {
            "total_trades": self.total_trades,
            "total_wins": self.total_wins,
            "current_capital": self.current_capital
        }
        try:
            with open("polymarket_settings.json", "w") as f:
                json.dump(settings, f)
        except:
            pass
    
    def run(self):
        """Start the application"""
        def on_closing():
            if self.is_running:
                self.stop_trading()
            self.save_settings()
            self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Auto-refresh market data every 30 seconds
        def auto_refresh():
            if not self.is_running:
                self.get_market_prices()
            self.root.after(30000, auto_refresh)
        
        self.root.after(5000, auto_refresh)  # Start after 5 seconds
        self.root.mainloop()

if __name__ == "__main__":
    app = PolymarketBTCBot()
    app.run()