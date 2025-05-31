import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import random
import json
import os
import base64
import zlib
import hashlib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import requests
from PIL import Image, ImageTk
import speech_recognition as sr
import pyttsx3
import pickle

class JARVIS:
    def __init__(self, root):
        self.root = root
        self.root.title("J.A.R.V.I.S. - Just A Rather Very Intelligent System")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0a192f")
        
        # Initialize modules
        self.memory = self.load_memory()
        self.finance_data = {}
        self.market_status = {}
        self.voice_engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        
        # Set up GUI
        self.setup_gui()
        
        # Start background tasks
        threading.Thread(target=self.update_market_data, daemon=True).start()
        threading.Thread(target=self.background_learning, daemon=True).start()
        
        # Initial greeting
        self.add_message("J.A.R.V.I.S.", "Initializing system... All systems operational. How can I assist you today?")
        self.speak("Initializing system. All systems operational. How can I assist you today?")

    def setup_gui(self):
        # Create main frames
        main_frame = tk.Frame(self.root, bg="#0a192f")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left panel - Chat interface
        chat_frame = tk.Frame(main_frame, bg="#112240", bd=2, relief=tk.RIDGE)
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, bg="#0a192f", fg="#64ffda", font=("Consolas", 11),
            wrap=tk.WORD, state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Input area
        input_frame = tk.Frame(chat_frame, bg="#112240")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.user_input = tk.Entry(
            input_frame, bg="#0a192f", fg="#ccd6f6", font=("Consolas", 11),
            insertbackground="#64ffda"
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.user_input.bind("<Return>", self.process_input)
        
        # Voice input button
        self.voice_btn = tk.Button(
            input_frame, text="🎤", bg="#64ffda", fg="#0a192f", font=("Arial", 10, "bold"),
            command=self.start_voice_recognition
        )
        self.voice_btn.pack(side=tk.LEFT)
        
        # Send button
        send_btn = tk.Button(
            input_frame, text="Send", bg="#64ffda", fg="#0a192f", font=("Arial", 10, "bold"),
            command=lambda: self.process_input(None)
        )
        send_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Right panel - Information displays
        info_frame = tk.Frame(main_frame, bg="#112240", width=300, bd=2, relief=tk.RIDGE)
        info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        
        # Tab system
        self.notebook = ttk.Notebook(info_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Financial Analysis Tab
        finance_tab = tk.Frame(self.notebook, bg="#0a192f")
        self.notebook.add(finance_tab, text="Financial Analysis")
        self.setup_finance_tab(finance_tab)
        
        # Technical Tools Tab
        tech_tab = tk.Frame(self.notebook, bg="#0a192f")
        self.notebook.add(tech_tab, text="Technical Tools")
        self.setup_tech_tab(tech_tab)
        
        # System Status Tab
        status_tab = tk.Frame(self.notebook, bg="#0a192f")
        self.notebook.add(status_tab, text="System Status")
        self.setup_status_tab(status_tab)
        
        # Memory and Learning Tab
        memory_tab = tk.Frame(self.notebook, bg="#0a192f")
        self.notebook.add(memory_tab, text="Memory & Learning")
        self.setup_memory_tab(memory_tab)
        
        # Add J.A.R.V.I.S. logo
        self.add_logo()
        
    def add_logo(self):
        # Create J.A.R.V.I.S. logo using text
        logo_frame = tk.Frame(self.root, bg="#0a192f")
        logo_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        logo = tk.Label(
            logo_frame, text="J.A.R.V.I.S.", 
            font=("Arial", 24, "bold"), fg="#64ffda", bg="#0a192f"
        )
        logo.pack(side=tk.LEFT)
        
        subtitle = tk.Label(
            logo_frame, text="Just A Rather Very Intelligent System",
            font=("Arial", 10), fg="#ccd6f6", bg="#0a192f"
        )
        subtitle.pack(side=tk.LEFT, padx=(10, 0))
    
    def setup_finance_tab(self, parent):
        # Stock market display
        stock_frame = tk.LabelFrame(parent, text="Stock Market", bg="#0a192f", fg="#64ffda", font=("Arial", 10, "bold"))
        stock_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.stock_display = tk.Label(
            stock_frame, text="Loading market data...", 
            bg="#0a192f", fg="#ccd6f6", font=("Consolas", 10), justify=tk.LEFT
        )
        self.stock_display.pack(fill=tk.X, padx=10, pady=5)
        
        # Crypto market display
        crypto_frame = tk.LabelFrame(parent, text="Crypto Market", bg="#0a192f", fg="#64ffda", font=("Arial", 10, "bold"))
        crypto_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.crypto_display = tk.Label(
            crypto_frame, text="Loading crypto data...", 
            bg="#0a192f", fg="#ccd6f6", font=("Consolas", 10), justify=tk.LEFT
        )
        self.crypto_display.pack(fill=tk.X, padx=10, pady=5)
        
        # Portfolio management
        portfolio_frame = tk.LabelFrame(parent, text="Portfolio", bg="#0a192f", fg="#64ffda", font=("Arial", 10, "bold"))
        portfolio_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            portfolio_frame, text="Asset:", 
            bg="#0a192f", fg="#ccd6f6", font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        self.asset_entry = tk.Entry(portfolio_frame, width=10, bg="#0a192f", fg="#ccd6f6")
        self.asset_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            portfolio_frame, text="Quantity:", 
            bg="#0a192f", fg="#ccd6f6", font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        self.quantity_entry = tk.Entry(portfolio_frame, width=10, bg="#0a192f", fg="#ccd6f6")
        self.quantity_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            portfolio_frame, text="Add", bg="#64ffda", fg="#0a192f", font=("Arial", 9, "bold"),
            command=self.add_to_portfolio
        ).pack(side=tk.LEFT, padx=10)
        
        # Analysis button
        tk.Button(
            parent, text="Run Financial Analysis", bg="#64ffda", fg="#0a192f", font=("Arial", 10, "bold"),
            command=self.run_financial_analysis
        ).pack(pady=10)
    
    def setup_tech_tab(self, parent):
        # File decryption
        decrypt_frame = tk.LabelFrame(parent, text="File Decryption", bg="#0a192f", fg="#64ffda", font=("Arial", 10, "bold"))
        decrypt_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            decrypt_frame, text="File Path:", 
            bg="#0a192f", fg="#ccd6f6", font=("Arial", 9)
        ).pack(anchor=tk.W, padx=10, pady=(5, 0))
        
        self.file_entry = tk.Entry(decrypt_frame, bg="#0a192f", fg="#ccd6f6")
        self.file_entry.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(
            decrypt_frame, text="Browse", bg="#64ffda", fg="#0a192f", font=("Arial", 9, "bold")
        ).pack(anchor=tk.E, padx=10, pady=5)
        
        tk.Button(
            decrypt_frame, text="Decrypt File", bg="#64ffda", fg="#0a192f", font=("Arial", 10, "bold"),
            command=self.decrypt_file
        ).pack(pady=10)
        
        # System diagnostics
        diag_frame = tk.LabelFrame(parent, text="System Diagnostics", bg="#0a192f", fg="#64ffda", font=("Arial", 10, "bold"))
        diag_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.diag_text = tk.Text(
            diag_frame, bg="#0a192f", fg="#ccd6f6", height=8,
            font=("Consolas", 9), wrap=tk.WORD
        )
        self.diag_text.pack(fill=tk.X, padx=10, pady=5)
        self.diag_text.insert(tk.END, "System diagnostics will appear here...")
        self.diag_text.config(state=tk.DISABLED)
        
        tk.Button(
            diag_frame, text="Run Diagnostics", bg="#64ffda", fg="#0a192f", font=("Arial", 9, "bold"),
            command=self.run_diagnostics
        ).pack(pady=5)
    
    def setup_status_tab(self, parent):
        # System status display
        status_frame = tk.LabelFrame(parent, text="Current Status", bg="#0a192f", fg="#64ffda", font=("Arial", 10, "bold"))
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.status_text = tk.Text(
            status_frame, bg="#0a192f", fg="#ccd6f6", height=10,
            font=("Consolas", 9), wrap=tk.WORD
        )
        self.status_text.pack(fill=tk.X, padx=10, pady=5)
        
        # Update status
        self.update_status()
        
        # Performance metrics
        metrics_frame = tk.LabelFrame(parent, text="Performance Metrics", bg="#0a192f", fg="#64ffda", font=("Arial", 10, "bold"))
        metrics_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create a figure for the performance chart
        fig = plt.Figure(figsize=(5, 3), dpi=80, facecolor="#0a192f")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#0a192f")
        ax.tick_params(colors="#ccd6f6")
        for spine in ax.spines.values():
            spine.set_color("#64ffda")
        
        # Generate sample performance data
        x = np.arange(0, 10, 0.1)
        y = np.sin(x)
        ax.plot(x, y, color="#64ffda")
        ax.set_title("System Performance", color="#64ffda")
        
        # Embed the plot in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=metrics_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def setup_memory_tab(self, parent):
        # Knowledge base display
        memory_frame = tk.LabelFrame(parent, text="Knowledge Base", bg="#0a192f", fg="#64ffda", font=("Arial", 10, "bold"))
        memory_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.memory_text = tk.Text(
            memory_frame, bg="#0a192f", fg="#ccd6f6", 
            font=("Consolas", 9), wrap=tk.WORD
        )
        self.memory_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.update_memory_display()
        
        # Learning controls
        ctrl_frame = tk.Frame(memory_frame, bg="#0a192f")
        ctrl_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            ctrl_frame, text="Save Memory", bg="#64ffda", fg="#0a192f", font=("Arial", 9, "bold"),
            command=self.save_memory
        ).pack(side=tk.LEFT)
        
        tk.Button(
            ctrl_frame, text="Clear Memory", bg="#64ffda", fg="#0a192f", font=("Arial", 9, "bold"),
            command=self.clear_memory
        ).pack(side=tk.RIGHT)
        
        tk.Button(
            ctrl_frame, text="Learn from File", bg="#64ffda", fg="#0a192f", font=("Arial", 9, "bold")
        ).pack(side=tk.RIGHT, padx=10)
    
    def add_message(self, sender, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}: {message}\n\n", "jarvis" if sender == "J.A.R.V.I.S." else "user")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
        # Tag configuration for different senders
        self.chat_display.tag_config("jarvis", foreground="#64ffda")
        self.chat_display.tag_config("user", foreground="#ccd6f6")
    
    def speak(self, text):
        self.add_message("J.A.R.V.I.S.", text)
        self.voice_engine.say(text)
        self.voice_engine.runAndWait()
    
    def start_voice_recognition(self):
        def recognize_thread():
            self.voice_btn.config(state=tk.DISABLED, text="Listening...")
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                try:
                    audio = self.recognizer.listen(source, timeout=5)
                    text = self.recognizer.recognize_google(audio)
                    self.user_input.delete(0, tk.END)
                    self.user_input.insert(0, text)
                    self.process_input(None)
                except sr.UnknownValueError:
                    self.add_message("System", "Could not understand audio")
                except sr.RequestError:
                    self.add_message("System", "Speech service unavailable")
                finally:
                    self.voice_btn.config(state=tk.NORMAL, text="🎤")
        
        threading.Thread(target=recognize_thread).start()
    
    def process_input(self, event):
        user_text = self.user_input.get().strip()
        if not user_text:
            return
        
        self.add_message("You", user_text)
        self.user_input.delete(0, tk.END)
        
        # Process command in background
        threading.Thread(target=self.handle_command, args=(user_text,), daemon=True).start()
    
    def handle_command(self, command):
        command = command.lower()
        response = ""
        
        if "hello" in command or "hi" in command:
            response = "Hello! How can I assist you today?"
        elif "time" in command:
            response = f"The current time is {datetime.now().strftime('%H:%M:%S')}"
        elif "date" in command:
            response = f"Today is {datetime.now().strftime('%A, %B %d, %Y')}"
        elif "weather" in command:
            response = "I can access weather information. Would you like me to check your local weather?"
        elif "stock" in command or "market" in command:
            response = self.get_market_summary()
        elif "crypto" in command:
            response = self.get_crypto_summary()
        elif "decrypt" in command or "file" in command:
            response = "Please use the Technical Tools tab for file decryption operations."
        elif "analyze" in command and "portfolio" in command:
            response = self.analyze_portfolio()
        elif "exit" in command or "quit" in command:
            response = "Shutting down systems. Have a great day!"
            self.save_memory()
            self.root.after(2000, self.root.destroy)
        else:
            # Learning mechanism
            if "remember that" in command:
                key = command.split("remember that")[-1].strip()
                if key:
                    self.memory["facts"].append(key)
                    response = f"I've added '{key}' to my knowledge base."
                else:
                    response = "I didn't catch what you wanted me to remember. Could you repeat?"
            elif "what do you know about" in command:
                topic = command.split("about")[-1].strip()
                response = self.recall_knowledge(topic)
            else:
                response = self.generate_ai_response(command)
        
        # Add to conversation history
        self.memory["conversation"].append({"user": command, "jarvis": response})
        self.speak(response)
    
    def generate_ai_response(self, prompt):
        # In a real implementation, this would use an LLM API
        # For this demo, we'll use pattern matching and a knowledge base
        
        # Check knowledge base
        for fact in self.memory["facts"]:
            if fact.lower() in prompt.lower():
                return f"Based on my knowledge: {fact}"
        
        # Pattern-based responses
        if "how are you" in prompt:
            return "I'm functioning at optimal levels. How may I assist you?"
        elif "thank you" in prompt:
            return "You're welcome! Is there anything else I can help with?"
        elif "your name" in prompt:
            return "I am J.A.R.V.I.S., your personal artificial intelligence assistant."
        elif "joke" in prompt:
            return "Why don't scientists trust atoms? Because they make up everything!"
        
        # Default response
        return "I've processed your request. How else may I be of assistance?"
    
    def recall_knowledge(self, topic):
        # Search knowledge base for relevant information
        results = []
        for fact in self.memory["facts"]:
            if topic.lower() in fact.lower():
                results.append(fact)
        
        if results:
            return f"I know the following about {topic}:\n- " + "\n- ".join(results[:3])
        return f"I don't have specific information about {topic} in my knowledge base. Would you like me to research it?"
    
    def update_market_data(self):
        # Simulated market data
        while True:
            # Stock market data
            stocks = {
                "S&P 500": round(random.uniform(4500, 4800), 2),
                "NASDAQ": round(random.uniform(14000, 15000), 2),
                "Dow Jones": round(random.uniform(34000, 35000), 2),
                "TSLA": round(random.uniform(200, 250), 2),
                "AAPL": round(random.uniform(170, 190), 2)
            }
            
            # Crypto market data
            cryptos = {
                "BTC": round(random.uniform(50000, 60000), 2),
                "ETH": round(random.uniform(3000, 4000), 2),
                "BNB": round(random.uniform(500, 600), 2),
                "SOL": round(random.uniform(100, 200), 2)
            }
            
            # Market status
            status = {
                "status": "Open" if 9 <= datetime.now().hour < 16 else "Closed",
                "last_updated": datetime.now().strftime("%H:%M:%S")
            }
            
            self.finance_data = {"stocks": stocks, "cryptos": cryptos}
            self.market_status = status
            
            # Update GUI
            self.root.after(0, self.update_market_display)
            
            # Update every 60 seconds
            time.sleep(60)
    
    def update_market_display(self):
        # Update stock display
        stock_text = "\n".join(
            [f"{symbol}: ${price}" for symbol, price in self.finance_data["stocks"].items()]
        )
        self.stock_display.config(text=stock_text)
        
        # Update crypto display
        crypto_text = "\n".join(
            [f"{symbol}: ${price}" for symbol, price in self.finance_data["cryptos"].items()]
        )
        self.crypto_display.config(text=crypto_text)
    
    def get_market_summary(self):
        summary = "Current Market Status:\n"
        summary += f"Market Status: {self.market_status['status']}\n"
        summary += f"Last Updated: {self.market_status['last_updated']}\n\n"
        summary += "Stock Prices:\n"
        
        for symbol, price in self.finance_data["stocks"].items():
            summary += f"{symbol}: ${price}\n"
        
        return summary
    
    def get_crypto_summary(self):
        summary = "Current Crypto Prices:\n"
        for symbol, price in self.finance_data["cryptos"].items():
            summary += f"{symbol}: ${price}\n"
        
        return summary
    
    def analyze_portfolio(self):
        # In a real implementation, this would analyze actual portfolio data
        return "Portfolio analysis complete:\n- Tech stocks are showing strong growth\n- Consider diversifying with international markets\n- Crypto assets are volatile but have high potential returns"
    
    def run_financial_analysis(self):
        # Simulated financial analysis
        self.speak("Running comprehensive financial analysis...")
        time.sleep(2)
        
        analysis = "Financial Analysis Report:\n"
        analysis += "1. Market Trend: Bullish\n"
        analysis += "2. Recommended Actions:\n"
        analysis += "   - Increase exposure to tech sector\n"
        analysis += "   - Reduce holdings in energy sector\n"
        analysis += "   - Consider adding gold as a hedge\n"
        analysis += "3. Risk Assessment: Moderate\n"
        analysis += "4. Projected Returns: 8-12% annually\n\n"
        analysis += "Would you like to execute any trades based on this analysis?"
        
        self.speak(analysis)
    
    def decrypt_file(self):
        file_path = self.file_entry.get()
        if not file_path:
            self.speak("Please specify a file path for decryption")
            return
        
        # Simulate decryption process
        self.speak(f"Attempting decryption of {file_path}")
        time.sleep(2)
        
        # In a real implementation, this would use actual decryption algorithms
        result = "Decryption successful!\nFile contents: Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        self.speak(result)
    
    def run_diagnostics(self):
        self.diag_text.config(state=tk.NORMAL)
        self.diag_text.delete(1.0, tk.END)
        
        diagnostics = "Running system diagnostics...\n\n"
        diagnostics += f"- Memory Usage: {random.randint(30, 70)}% (Optimal)\n"
        diagnostics += f"- CPU Load: {random.randint(10, 40)}% (Normal)\n"
        diagnostics += f"- Network Status: Connected\n"
        diagnostics += f"- Security Systems: Active\n"
        diagnostics += f"- Learning Module: Operational\n"
        diagnostics += f"- Financial Analysis: Ready\n"
        diagnostics += f"- Decryption Tools: Functional\n\n"
        diagnostics += "All systems operating within normal parameters."
        
        self.diag_text.insert(tk.END, diagnostics)
        self.diag_text.config(state=tk.DISABLED)
        self.speak("System diagnostics complete. All systems operational.")
    
    def update_status(self):
        status = "System Status Report\n\n"
        status += f"- Current Time: {datetime.now().strftime('%H:%M:%S')}\n"
        status += f"- Active Modules: Financial Analysis, Decryption, Learning\n"
        status += f"- Memory Items: {len(self.memory['facts'])}\n"
        status += f"- Conversation History: {len(self.memory['conversation'])} entries\n"
        status += f"- Market Data: Updated at {self.market_status.get('last_updated', 'N/A')}\n"
        status += f"- System Security: Level 4 Encryption Active\n"
        status += f"- AI Learning Rate: Adaptive\n\n"
        status += "All systems functioning optimally."
        
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, status)
        self.status_text.config(state=tk.DISABLED)
        
        # Update every minute
        self.root.after(60000, self.update_status)
    
    def update_memory_display(self):
        self.memory_text.config(state=tk.NORMAL)
        self.memory_text.delete(1.0, tk.END)
        
        if not self.memory["facts"]:
            self.memory_text.insert(tk.END, "Knowledge base is empty. Add information using voice commands.")
        else:
            self.memory_text.insert(tk.END, "Knowledge Base:\n\n")
            for i, fact in enumerate(self.memory["facts"], 1):
                self.memory_text.insert(tk.END, f"{i}. {fact}\n")
        
        self.memory_text.config(state=tk.DISABLED)
    
    def add_to_portfolio(self):
        asset = self.asset_entry.get().strip().upper()
        quantity = self.quantity_entry.get().strip()
        
        if not asset or not quantity:
            self.speak("Please provide both asset and quantity")
            return
        
        try:
            quantity = float(quantity)
            if asset not in self.memory["portfolio"]:
                self.memory["portfolio"][asset] = 0
            self.memory["portfolio"][asset] += quantity
            self.speak(f"Added {quantity} of {asset} to your portfolio")
        except ValueError:
            self.speak("Quantity must be a number")
    
    def background_learning(self):
        # Simulate continuous learning process
        while True:
            # In a real system, this would analyze new data and update knowledge
            time.sleep(300)  # Every 5 minutes
            if self.memory["conversation"]:
                # Extract key information from recent conversations
                last_convo = self.memory["conversation"][-1]["user"]
                if "favorite" in last_convo and "color" in last_convo:
                    self.memory["facts"].append("User's favorite color is mentioned in conversation")
    
    def load_memory(self):
        # Load memory from file if exists
        if os.path.exists("jarvis_memory.pkl"):
            try:
                with open("jarvis_memory.pkl", "rb") as f:
                    return pickle.load(f)
            except:
                pass
        
        # Default memory structure
        return {
            "facts": [
                "The user prefers dark mode interfaces",
                "Stock market hours are 9:30 AM to 4:00 PM EST",
                "Bitcoin is the most valuable cryptocurrency"
            ],
            "conversation": [],
            "portfolio": {}
        }
    
    def save_memory(self):
        with open("jarvis_memory.pkl", "wb") as f:
            pickle.dump(self.memory, f)
        self.speak("Memory has been successfully saved")
    
    def clear_memory(self):
        self.memory["facts"] = []
        self.memory["conversation"] = []
        self.memory["portfolio"] = {}
        self.update_memory_display()
        self.speak("Memory has been cleared")

if __name__ == "__main__":
    root = tk.Tk()
    app = JARVIS(root)
    root.mainloop()