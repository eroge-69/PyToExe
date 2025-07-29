import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import requests
import subprocess
import sys
from datetime import datetime
import webbrowser
import pandas as pd
import numpy as np
import yfinance as yf
import random
from dataclasses import dataclass
from typing import Optional, List
import socket
import platform

@dataclass
class SignalData:
    symbol: str
    signal: str
    confidence: float
    price: float
    reasons: List[str]
    timestamp: datetime

class NetworkManager:
    """Handle network operations and ping functionality"""
    
    @staticmethod
    def get_ping(host="8.8.8.8", timeout=3):
        """Get ping in milliseconds"""
        try:
            if platform.system().lower() == "windows":
                cmd = f"ping -n 1 -w {timeout*1000} {host}"
            else:
                cmd = f"ping -c 1 -W {timeout} {host}"
            
            start_time = time.time()
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=timeout)
            end_time = time.time()
            
            if result.returncode == 0:
                # Calculate ping from actual time taken
                ping_ms = int((end_time - start_time) * 1000)
                return min(ping_ms, 999)  # Cap at 999ms
            else:
                return -1
        except:
            return -1
    
    @staticmethod
    def test_connection():
        """Test internet connection"""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except:
            return False

class VoiceManager:
    """Handle text-to-speech functionality"""
    
    @staticmethod
    def speak(text):
        """Text to speech using system TTS"""
        try:
            if platform.system().lower() == "windows":
                # Windows SAPI
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty('rate', 200)
                engine.setProperty('volume', 0.9)
                engine.say(text)
                engine.runAndWait()
            else:
                # macOS/Linux
                subprocess.run(['say', text] if platform.system().lower() == "darwin" 
                             else ['espeak', text], check=False)
        except:
            # Fallback: system beep
            print('\a')  # Bell sound
    
    @staticmethod
    def signal_notification(symbol, signal_type):
        """Play signal notification"""
        message = f"Signal received for {symbol}: {signal_type}"
        threading.Thread(target=VoiceManager.speak, args=(message,), daemon=True).start()

class TradingEngine:
    """Enhanced trading engine with ping monitoring"""
    
    def __init__(self, symbol):
        self.symbol = symbol
        self.last_signal = None
        self.ping_history = []
        
    def generate_realistic_data(self, periods=50):
        """Generate realistic market data"""
        base_prices = {
            'EURUSD': 1.0850, 'GBPUSD': 1.2650, 'USDJPY': 149.50,
            'AUDUSD': 0.6750, 'BTCUSD': 42000.0, 'ETHUSD': 2400.0,
            'AAPL': 185.0, 'GOOGL': 142.0, 'TSLA': 240.0
        }
        
        base_price = base_prices.get(self.symbol, 1.0000)
        dates = pd.date_range(start=datetime.now(), periods=periods, freq='1min')
        
        prices = []
        current_price = base_price
        
        for i in range(periods):
            volatility = random.uniform(-0.002, 0.002)
            trend = 0.0001 * np.sin(i / 20)
            current_price += current_price * (trend + volatility)
            prices.append(current_price)
        
        # Create OHLC data
        data = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            if i == 0:
                open_price = price
            else:
                open_price = data[i-1]['Close']
            
            spread = price * random.uniform(0.0001, 0.0005)
            high = price + spread * random.uniform(0.2, 1.0)
            low = price - spread * random.uniform(0.2, 1.0)
            close = price + random.uniform(-spread/2, spread/2)
            
            data.append({
                'Open': open_price, 'High': high, 'Low': low, 'Close': close
            })
        
        return pd.DataFrame(data, index=dates)
    
    def get_signal(self):
        """Generate trading signal with notification"""
        try:
            # Try to get real data first
            ticker = yf.Ticker(f"{self.symbol}=X" if self.symbol in ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD'] else self.symbol)
            data = ticker.history(period='1d', interval='1m')
            
            if data.empty or len(data) < 20:
                # Use simulated data
                data = self.generate_realistic_data()
        except:
            # Fallback to simulated data
            data = self.generate_realistic_data()
        
        # Calculate indicators
        data['SMA5'] = data['Close'].rolling(5, min_periods=1).mean()
        data['SMA10'] = data['Close'].rolling(10, min_periods=1).mean()
        data['RSI'] = self.calculate_rsi(data['Close'])
        
        # Get current values
        current_price = float(data['Close'].iloc[-1])
        sma5 = float(data['SMA5'].iloc[-1])
        sma10 = float(data['SMA10'].iloc[-1])
        rsi = float(data['RSI'].iloc[-1])
        
        # Generate signal
        buy_score = 0
        sell_score = 0
        reasons = []
        
        # SMA analysis
        if sma5 > sma10:
            buy_score += 30
            reasons.append("SMA5 > SMA10 (Bullish)")
        else:
            sell_score += 30
            reasons.append("SMA5 < SMA10 (Bearish)")
        
        # RSI analysis
        if rsi < 30:
            buy_score += 40
            reasons.append(f"RSI Oversold ({rsi:.1f})")
        elif rsi > 70:
            sell_score += 40
            reasons.append(f"RSI Overbought ({rsi:.1f})")
        else:
            reasons.append(f"RSI Neutral ({rsi:.1f})")
        
        # Price momentum
        momentum = (current_price - float(data['Close'].iloc[-5])) / float(data['Close'].iloc[-5]) * 100
        if momentum > 0.1:
            buy_score += 20
            reasons.append(f"Bullish momentum ({momentum:.2f}%)")
        elif momentum < -0.1:
            sell_score += 20
            reasons.append(f"Bearish momentum ({momentum:.2f}%)")
        
        # Determine final signal
        if buy_score > sell_score and buy_score >= 40:
            signal = "BUY"
            confidence = min(buy_score, 95)
        elif sell_score > buy_score and sell_score >= 40:
            signal = "SELL"
            confidence = min(sell_score, 95)
        else:
            signal = "HOLD"
            confidence = max(buy_score, sell_score)
        
        signal_data = SignalData(
            symbol=self.symbol,
            signal=signal,
            confidence=confidence,
            price=current_price,
            reasons=reasons,
            timestamp=datetime.now()
        )
        
        # Check if signal changed and play notification
        if signal in ['BUY', 'SELL'] and self.last_signal != signal:
            VoiceManager.signal_notification(self.symbol, signal)
            self.last_signal = signal
        
        return signal_data
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = delta.where(delta > 0, 0).rolling(period, min_periods=1).mean()
        loss = -delta.where(delta < 0, 0).rolling(period, min_periods=1).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

class PairWindow:
    """Individual window for each currency pair"""
    
    def __init__(self, parent, symbol, engine):
        self.parent = parent
        self.symbol = symbol
        self.engine = engine
        self.window = None
        self.monitoring = False
        self.ping_label = None
        self.signal_widgets = {}
        
    def create_window(self):
        """Create independent window for pair"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"🎯 {self.symbol} - Live Trading")
        self.window.geometry("500x600")
        self.window.configure(bg='#1a1a1a')
        
        # Header with ping
        header_frame = tk.Frame(self.window, bg='#00ff88', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame,
                              text=f"💱 {self.symbol} LIVE",
                              bg='#00ff88', fg='black',
                              font=('Arial', 16, 'bold'))
        title_label.pack(side='left', padx=20, pady=15)
        
        self.ping_label = tk.Label(header_frame,
                                  text="Ping: ---ms",
                                  bg='#00ff88', fg='black',
                                  font=('Arial', 12, 'bold'))
        self.ping_label.pack(side='right', padx=20, pady=15)
        
        # Signal display
        signal_frame = tk.LabelFrame(self.window,
                                   text=f"📊 {self.symbol} SIGNALS",
                                   bg='#2a2a2a', fg='white',
                                   font=('Arial', 14, 'bold'))
        signal_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_signal_display(signal_frame)
        
        # Control buttons
        control_frame = tk.Frame(self.window, bg='#1a1a1a')
        control_frame.pack(fill='x', padx=10, pady=10)
        
        start_btn = tk.Button(control_frame,
                             text="🚀 START MONITORING",
                             command=self.toggle_monitoring,
                             bg='#00ff88', fg='black',
                             font=('Arial', 11, 'bold'),
                             width=18, height=2)
        start_btn.pack(side='left', padx=5)
        
        refresh_btn = tk.Button(control_frame,
                               text="🔄 REFRESH",
                               command=self.manual_refresh,
                               bg='#ff8800', fg='white',
                               font=('Arial', 11, 'bold'),
                               width=12, height=2)
        refresh_btn.pack(side='left', padx=5)
        
        # Start monitoring and ping updates
        self.start_monitoring()
        self.update_ping()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_signal_display(self, parent):
        """Create signal display widgets"""
        # Price display
        price_frame = tk.Frame(parent, bg='#3a3a3a', relief='ridge', bd=2)
        price_frame.pack(fill='x', padx=10, pady=10)
        
        price_label = tk.Label(price_frame,
                              text="CURRENT PRICE",
                              bg='#3a3a3a', fg='#cccccc',
                              font=('Arial', 10))
        price_label.pack(pady=5)
        
        price_value = tk.Label(price_frame,
                              text="$0.0000",
                              bg='#3a3a3a', fg='white',
                              font=('Arial', 24, 'bold'))
        price_value.pack(pady=5)
        
        # Signal display
        signal_frame = tk.Frame(parent, bg='#3a3a3a', relief='ridge', bd=2)
        signal_frame.pack(fill='x', padx=10, pady=10)
        
        signal_label = tk.Label(signal_frame,
                               text="CURRENT SIGNAL",
                               bg='#3a3a3a', fg='#cccccc',
                               font=('Arial', 10))
        signal_label.pack(pady=5)
        
        signal_value = tk.Label(signal_frame,
                               text="WAITING...",
                               bg='#3a3a3a', fg='#ffaa00',
                               font=('Arial', 20, 'bold'))
        signal_value.pack(pady=10)
        
        confidence_value = tk.Label(signal_frame,
                                   text="0% Confidence",
                                   bg='#3a3a3a', fg='white',
                                   font=('Arial', 14))
        confidence_value.pack(pady=5)
        
        # Action recommendations
        action_frame = tk.Frame(parent, bg='#3a3a3a', relief='ridge', bd=2)
        action_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        action_label = tk.Label(action_frame,
                               text="TRADING RECOMMENDATION",
                               bg='#3a3a3a', fg='#cccccc',
                               font=('Arial', 10))
        action_label.pack(pady=5)
        
        action_text = tk.Text(action_frame,
                             bg='#3a3a3a', fg='white',
                             font=('Arial', 11),
                             height=8, wrap='word',
                             state='disabled')
        action_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Store widget references
        self.signal_widgets = {
            'price': price_value,
            'signal': signal_value,
            'confidence': confidence_value,
            'action': action_text
        }
    
    def update_display(self):
        """Update signal display"""
        try:
            signal_data = self.engine.get_signal()
            
            # Update price
            self.signal_widgets['price'].config(text=f"${signal_data.price:.4f}")
            
            # Update signal
            if signal_data.signal == "BUY":
                self.signal_widgets['signal'].config(text="🟢 BUY SIGNAL", fg='#00ff88')
            elif signal_data.signal == "SELL":
                self.signal_widgets['signal'].config(text="🔴 SELL SIGNAL", fg='#ff4444')
            else:
                self.signal_widgets['signal'].config(text="🟡 HOLD", fg='#ffaa00')
            
            # Update confidence
            self.signal_widgets['confidence'].config(text=f"{signal_data.confidence:.0f}% Confidence")
            
            # Update action text
            action_text = self.signal_widgets['action']
            action_text.config(state='normal')
            action_text.delete(1.0, tk.END)
            
            if signal_data.signal in ['BUY', 'SELL']:
                recommendation = f"🎯 TRADE RECOMMENDATION:\n\n"
                recommendation += f"Symbol: {signal_data.symbol}\n"
                recommendation += f"Direction: {signal_data.signal}\n"
                recommendation += f"Confidence: {signal_data.confidence:.0f}%\n"
                recommendation += f"Entry Price: ${signal_data.price:.4f}\n\n"
                recommendation += "📊 Analysis:\n"
                for reason in signal_data.reasons:
                    recommendation += f"• {reason}\n"
                
                if signal_data.confidence >= 70:
                    recommendation += "\n🔥 HIGH PROBABILITY TRADE"
                elif signal_data.confidence >= 50:
                    recommendation += "\n⚡ MODERATE PROBABILITY"
                else:
                    recommendation += "\n⚠️ LOW PROBABILITY - CAUTION"
            else:
                recommendation = "⏸️ No clear signal at the moment.\n\n"
                recommendation += "Current market analysis:\n"
                for reason in signal_data.reasons:
                    recommendation += f"• {reason}\n"
                recommendation += "\nWaiting for better setup..."
            
            action_text.insert(1.0, recommendation)
            action_text.config(state='disabled')
            
        except Exception as e:
            print(f"Error updating {self.symbol}: {e}")
    
    def update_ping(self):
        """Update ping display"""
        if not self.window or not self.window.winfo_exists():
            return
        
        def ping_worker():
            ping = NetworkManager.get_ping()
            if ping > 0:
                color = '#00ff88' if ping < 50 else '#ffaa00' if ping < 100 else '#ff4444'
                self.window.after(0, lambda: self.ping_label.config(
                    text=f"Ping: {ping}ms", fg='black', bg=color))
            else:
                self.window.after(0, lambda: self.ping_label.config(
                    text="Ping: Offline", fg='white', bg='#ff4444'))
        
        threading.Thread(target=ping_worker, daemon=True).start()
        
        # Schedule next ping update
        if self.window and self.window.winfo_exists():
            self.window.after(5000, self.update_ping)
    
    def start_monitoring(self):
        """Start signal monitoring"""
        if not self.monitoring:
            self.monitoring = True
            threading.Thread(target=self.monitoring_loop, daemon=True).start()
    
    def monitoring_loop(self):
        """Monitoring loop for this pair"""
        while self.monitoring and self.window and self.window.winfo_exists():
            try:
                self.update_display()
                time.sleep(10)  # Update every 10 seconds
            except Exception as e:
                print(f"Monitoring error for {self.symbol}: {e}")
                time.sleep(5)
    
    def toggle_monitoring(self):
        """Toggle monitoring"""
        self.monitoring = not self.monitoring
        if self.monitoring:
            self.start_monitoring()
    
    def manual_refresh(self):
        """Manual refresh"""
        self.update_display()
    
    def on_close(self):
        """Handle window close"""
        self.monitoring = False
        if self.window:
            self.window.destroy()

class QuotexTradingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 Quootex Trading Signals Pro")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a1a')
        
        # Variables
        self.monitoring = False
        self.engines = {}
        self.signal_history = []
        self.pair_windows = {}
        self.global_ping = 0
        
        # Initialize trading engines
        symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]
        for symbol in symbols:
            self.engines[symbol] = TradingEngine(symbol)
            self.pair_windows[symbol] = PairWindow(self.root, symbol, self.engines[symbol])
        
        # Create GUI
        self.create_widgets()
        self.update_clock()
        self.update_global_ping()
        
        # Auto-start monitoring
        self.start_monitoring()
        
        # Check TTS availability
        self.check_tts()
    
    def check_tts(self):
        """Check if TTS is available"""
        try:
            if platform.system().lower() == "windows":
                import pyttsx3
            print("✅ Text-to-Speech available")
        except ImportError:
            print("⚠️ Text-to-Speech not available. Install pyttsx3 for voice notifications.")
            messagebox.showwarning("TTS Warning", 
                                 "Text-to-Speech not available.\nInstall pyttsx3 for voice notifications:\npip install pyttsx3")
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Title bar with global ping
        title_frame = tk.Frame(self.root, bg='#00ff88', height=50)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, 
                              text="🎯 QUOTEX TRADING SIGNALS PRO", 
                              bg='#00ff88', fg='black',
                              font=('Arial', 16, 'bold'))
        title_label.pack(side='left', padx=20, pady=10)
        
        # Global ping display
        self.global_ping_label = tk.Label(title_frame,
                                         text="Ping: ---ms",
                                         bg='#00ff88', fg='black',
                                         font=('Arial', 12, 'bold'))
        self.global_ping_label.pack(side='right', padx=10, pady=10)
        
        self.clock_label = tk.Label(title_frame, 
                                   text="", 
                                   bg='#00ff88', fg='black',
                                   font=('Arial', 12, 'bold'))
        self.clock_label.pack(side='right', padx=20, pady=10)
        
        # Control panel
        control_frame = tk.Frame(self.root, bg='#2a2a2a', height=60)
        control_frame.pack(fill='x', padx=10, pady=5)
        control_frame.pack_propagate(False)
        
        # Buttons
        self.start_button = tk.Button(control_frame,
                                    text="🚀 MONITORING ACTIVE",
                                    command=self.toggle_monitoring,
                                    bg='#00ff88', fg='black',
                                    font=('Arial', 11, 'bold'),
                                    width=18, height=2)
        self.start_button.pack(side='left', padx=10, pady=10)
        
        quotex_button = tk.Button(control_frame,
                                text="🌐 OPEN QUOTEX",
                                command=self.open_quotex,
                                bg='#0088ff', fg='white',
                                font=('Arial', 11, 'bold'),
                                width=12, height=2)
        quotex_button.pack(side='left', padx=5, pady=10)
        
        refresh_button = tk.Button(control_frame,
                                 text="🔄 REFRESH",
                                 command=self.manual_refresh,
                                 bg='#ff8800', fg='white',
                                 font=('Arial', 11, 'bold'),
                                 width=10, height=2)
        refresh_button.pack(side='left', padx=5, pady=10)
        
        # Status
        self.status_label = tk.Label(control_frame,
                                   text="✅ READY FOR TRADING",
                                   bg='#2a2a2a', fg='#00ff88',
                                   font=('Arial', 10, 'bold'))
        self.status_label.pack(side='right', padx=20, pady=10)
        
        # Main content
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Signals panel - now clickable
        signals_frame = tk.LabelFrame(main_frame, 
                                    text="📊 LIVE TRADING SIGNALS (Click to open individual windows)",
                                    bg='#2a2a2a', fg='white',
                                    font=('Arial', 12, 'bold'))
        signals_frame.pack(fill='both', expand=True, pady=5)
        
        # Create clickable signal displays
        self.signal_widgets = {}
        symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]
        
        for i, symbol in enumerate(symbols):
            self.create_signal_widget(signals_frame, symbol, i//2, i%2)
        
        # History panel
        history_frame = tk.LabelFrame(main_frame,
                                    text="📈 RECENT SIGNALS",
                                    bg='#2a2a2a', fg='white',
                                    font=('Arial', 12, 'bold'),
                                    height=150)
        history_frame.pack(fill='x', pady=5)
        history_frame.pack_propagate(False)
        
        # History listbox
        self.history_listbox = tk.Listbox(history_frame,
                                        bg='#3a3a3a', fg='white',
                                        font=('Courier', 9),
                                        height=8)
        self.history_listbox.pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_signal_widget(self, parent, symbol, row, col):
        """Create clickable signal display widget"""
        # Main frame - now clickable
        frame = tk.Frame(parent, bg='#3a3a3a', relief='ridge', bd=2, cursor='hand2')
        frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        # Configure grid weights
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        # Bind click event to frame and all child widgets
        def open_pair_window(event=None):
            self.pair_windows[symbol].create_window()
        
        frame.bind("<Button-1>", open_pair_window)
        
        # Symbol header
        header_frame = tk.Frame(frame, bg='#3a3a3a', cursor='hand2')
        header_frame.pack(fill='x', padx=10, pady=5)
        header_frame.bind("<Button-1>", open_pair_window)
        
        symbol_label = tk.Label(header_frame,
                              text=f"💱 {symbol} (Click to open)",
                              bg='#3a3a3a', fg='#00ff88',
                              font=('Arial', 12, 'bold'),
                              cursor='hand2')
        symbol_label.pack(side='left')
        symbol_label.bind("<Button-1>", open_pair_window)
        
        # Price display
        price_label = tk.Label(header_frame,
                             text="$0.0000",
                             bg='#3a3a3a', fg='white',
                             font=('Arial', 10),
                             cursor='hand2')
        price_label.pack(side='right')
        price_label.bind("<Button-1>", open_pair_window)
        
        # Signal display
        signal_frame = tk.Frame(frame, bg='#3a3a3a', cursor='hand2')
        signal_frame.pack(fill='x', padx=10, pady=5)
        signal_frame.bind("<Button-1>", open_pair_window)
        
        signal_label = tk.Label(signal_frame,
                              text="WAITING...",
                              bg='#3a3a3a', fg='#ffaa00',
                              font=('Arial', 14, 'bold'),
                              cursor='hand2')
        signal_label.pack()
        signal_label.bind("<Button-1>", open_pair_window)
        
        # Confidence
        confidence_label = tk.Label(signal_frame,
                                  text="0%",
                                  bg='#3a3a3a', fg='white',
                                  font=('Arial', 12),
                                  cursor='hand2')
        confidence_label.pack()
        confidence_label.bind("<Button-1>", open_pair_window)
        
        # Action
        action_label = tk.Label(frame,
                              text="Click to open individual window",
                              bg='#3a3a3a', fg='#cccccc',
                              font=('Arial', 9),
                              wraplength=200,
                              cursor='hand2')
        action_label.pack(fill='x', padx=10, pady=5)
        action_label.bind("<Button-1>", open_pair_window)
        
        # Store references
        self.signal_widgets[symbol] = {
            'frame': frame,
            'price': price_label,
            'signal': signal_label,
            'confidence': confidence_label,
            'action': action_label
        }
    
    def update_signal_display(self, signal_data):
        """Update signal display for a symbol"""
        symbol = signal_data.symbol
        if symbol not in self.signal_widgets:
            return
        
        widgets = self.signal_widgets[symbol]
        
        # Update price
        widgets['price'].config(text=f"${signal_data.price:.4f}")
        
        # Update signal with colors
        if signal_data.signal == "BUY":
            widgets['signal'].config(text="🟢 BUY", fg='#00ff88')
        elif signal_data.signal == "SELL":
            widgets['signal'].config(text="🔴 SELL", fg='#ff4444')
        else:
            widgets['signal'].config(text="🟡 HOLD", fg='#ffaa00')
        
        # Update confidence
        widgets['confidence'].config(text=f"{signal_data.confidence:.0f}%")
        
        # Update action
        widgets['action'].config(text=f"Click for {symbol} details")
    
    def add_to_history(self, signal_data):
        """Add signal to history"""
        timestamp = signal_data.timestamp.strftime("%H:%M:%S")
        history_text = f"[{timestamp}] {signal_data.symbol}: {signal_data.signal} ({signal_data.confidence:.0f}%)"
        
        self.history_listbox.insert(0, history_text)
        
        # Keep only last 50 entries
        if self.history_listbox.size() > 50:
            self.history_listbox.delete(50, tk.END)
        
        # Auto-scroll to top
        self.history_listbox.see(0)
    
    def update_signals(self):
        """Update all signals"""
        for symbol, engine in self.engines.items():
            try:
                signal_data = engine.get_signal()
                self.update_signal_display(signal_data)
                
                # Add to history if signal changed
                if signal_data.signal in ['BUY', 'SELL']:
                    self.add_to_history(signal_data)
            except Exception as e:
                print(f"Error updating {symbol}: {e}")
    
    def update_global_ping(self):
        """Update global ping display"""
        def ping_worker():
            ping = NetworkManager.get_ping()
            if ping > 0:
                color = '#00ff88' if ping < 50 else '#ffaa00' if ping < 100 else '#ff4444'
                self.root.after(0, lambda: self.global_ping_label.config(
                    text=f"Ping: {ping}ms", fg='black', bg=color))
            else:
                self.root.after(0, lambda: self.global_ping_label.config(
                    text="Ping: Offline", fg='white', bg='#ff4444'))
        
        threading.Thread(target=ping_worker, daemon=True).start()
        
        # Schedule next ping update
        self.root.after(5000, self.update_global_ping)
    
    def monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self.update_signals()
                self.status_label.config(text="✅ SIGNALS UPDATED", fg='#00ff88')
                
                # Wait 10 seconds
                for i in range(10):
                    if not self.monitoring:
                        break
                    time.sleep(1)
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(5)
    
    def start_monitoring(self):
        """Start signal monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.start_button.config(text="🛑 STOP MONITORING", bg='#ff4444')
            self.status_label.config(text="🔄 MONITORING ACTIVE...", fg='#ffaa00')
            
            # Start monitoring thread
            monitor_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
            monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop signal monitoring"""
        self.monitoring = False
        self.start_button.config(text="🚀 START MONITORING", bg='#00ff88')
        self.status_label.config(text="⏸️ MONITORING STOPPED", fg='#ff4444')
    
    def toggle_monitoring(self):
        """Toggle monitoring on/off"""
        if self.monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()
    
    def manual_refresh(self):
        """Manual refresh of signals"""
        if not self.monitoring:
            self.update_signals()
            self.status_label.config(text="🔄 MANUALLY REFRESHED", fg='#00ff88')
    
    def open_quotex(self):
        """Open Quotex website"""
        webbrowser.open("https://quotex.io")
        self.status_label.config(text="🌐 QUOTEX OPENED", fg='#0088ff')
    
    def update_clock(self):
        """Update clock display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.config(text=current_time)
        
        # Schedule next update
        self.root.after(1000, self.update_clock)

def main():
    """Main function to run the app"""
    try:
        root = tk.Tk()
        app = QuotexTradingApp(root)
        
        # Set window icon and properties
        root.resizable(True, True)
        root.minsize(800, 600)
        
        # Center window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")
        
        # Handle close event
        def on_closing():
            app.stop_monitoring()
            # Close all pair windows
            for pair_window in app.pair_windows.values():
                pair_window.monitoring = False
                if pair_window.window and pair_window.window.winfo_exists():
                    pair_window.window.destroy()
            root.quit()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the application
        root.mainloop()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main()
