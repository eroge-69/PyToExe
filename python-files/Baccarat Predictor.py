import tkinter as tk
from tkinter import ttk, messagebox, font
import json
import os
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Literal
import webbrowser
from dataclasses import dataclass, asdict
import math

# Type definitions
CardValue = Literal['A', '2', '3', '4', '5', '6', '7', '8', '9', '0']
GameOutcome = Literal['Player', 'Banker', 'Tie']
Advantage = Literal['Player', 'Banker', 'Neutral']
PredictionType = Literal['BANKER', 'PLAYER', 'NEUTRAL']
PredictionState = Literal['collecting', 'prediction-shown']

@dataclass
class CardCount:
    zeros: int = 0
    numbers: int = 0
    total: int = 0
    advantage: Advantage = 'Neutral'
    intensity: float = 0.0

@dataclass
class RoundData:
    player_cards: List[CardValue]
    banker_cards: List[CardValue]
    outcome: GameOutcome
    round_number: int

@dataclass
class SimplePrediction:
    prediction: PredictionType
    numbers_count: int
    zeros_count: int
    rounds_analyzed: int

@dataclass
class PredictionResult:
    outcome: GameOutcome
    confidence: int
    reasoning: str
    patterns: List[str]

@dataclass
class PatternAnalysis:
    streak_length: int
    streak_type: Optional[GameOutcome]
    alternating_pattern: bool
    recent_outcomes: List[GameOutcome]
    pattern_confidence: int

@dataclass
class TrialStatus:
    is_active: bool = False
    remaining_time_ms: int = 0
    is_expired: bool = False
    start_time: int = 0
    end_time: int = 0

@dataclass
class SessionData:
    hands_played: int = 0
    wins: int = 0
    losses: int = 0
    ties: int = 0
    win_rate: float = 0.0
    profit_loss: float = 0.0
    is_active: bool = False

@dataclass
class LastPredictionTracker:
    prediction: PredictionType
    was_correct: Optional[bool] = None

class LightningBaccaratApp:
    def __init__(self):
        # Constants
        self.TRIAL_DURATION_MS = 50 * 60 * 1000  # 50 minutes
        self.STORAGE_FILE = 'lightning_baccarat_trial.json'
        self.WINDOW_WIDTH = 390
        self.WINDOW_HEIGHT = 844
        
        # Initialize data
        self.trial_status = TrialStatus()
        self.card_count = CardCount()
        self.recent_rounds: List[RoundData] = []
        self.current_player_cards: List[CardValue] = []
        self.current_banker_cards: List[CardValue] = []
        self.is_recording_player_cards = True
        self.session_data = SessionData()
        self.current_prediction: Optional[PredictionResult] = None
        self.prediction_state: PredictionState = 'collecting'
        self.active_prediction: Optional[SimplePrediction] = None
        self.last_prediction_tracker: Optional[LastPredictionTracker] = None
        self.is_session_active = False
        self.is_processing = False
        self.is_analyzing = False
        
        # Initialize GUI
        self.setup_window()
        self.setup_styles()
        self.create_widgets()
        
        # Load trial data and start timer
        self.load_trial_data()
        self.start_trial_timer()
        
        # Auto-start trial if needed
        if not self.trial_status.is_active and not self.trial_status.is_expired and self.trial_status.start_time == 0:
            self.start_trial()

    def setup_window(self):
        self.root = tk.Tk()
        self.root.title("⚡ Lightning Baccarat - Mobile Edition")
        self.root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg='#064e3b')  # Dark green background
        
        # Center window on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.WINDOW_WIDTH) // 2
        y = (screen_height - self.WINDOW_HEIGHT) // 2
        self.root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{x}+{y}")

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.style.configure('Title.TLabel', 
                           background='#064e3b', 
                           foreground='#fbbf24',
                           font=('Arial', 16, 'bold'))
        
        self.style.configure('Subtitle.TLabel',
                           background='#064e3b',
                           foreground='#d1d5db',
                           font=('Arial', 10))
        
        self.style.configure('Card.TButton',
                           font=('Arial', 12, 'bold'),
                           padding=(5, 5))
        
        self.style.configure('Action.TButton',
                           font=('Arial', 10, 'bold'),
                           padding=(8, 4))
        
        self.style.configure('Small.TButton',
                           font=('Arial', 8, 'bold'),
                           padding=(4, 2))

    def create_widgets(self):
        # Main container with scrollable frame
        self.main_canvas = tk.Canvas(self.root, bg='#064e3b', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = tk.Frame(self.main_canvas, bg='#064e3b')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack canvas and scrollbar
        self.main_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        self.main_canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        # Create main content
        self.create_header()
        self.create_trial_status()
        self.create_session_controls()
        self.create_card_display()
        self.create_card_input()
        self.create_prediction_display()
        self.create_prediction_engine()
        self.create_statistics()
        
        # Update display
        self.update_display()

    def _on_mousewheel(self, event):
        self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def create_header(self):
        header_frame = tk.Frame(self.scrollable_frame, bg='#1f2937', relief='raised', bd=2)
        header_frame.pack(fill='x', padx=5, pady=5)
        
        title_label = tk.Label(header_frame, 
                              text="⚡ Lightning Baccarat ⚡",
                              bg='#1f2937',
                              fg='#fbbf24',
                              font=('Arial', 16, 'bold'))
        title_label.pack(pady=5)
        
        subtitle_label = tk.Label(header_frame,
                                 text="Lightning Card Input System",
                                 bg='#1f2937',
                                 fg='#d1d5db',
                                 font=('Arial', 10))
        subtitle_label.pack()

    def create_trial_status(self):
        self.trial_frame = tk.Frame(self.scrollable_frame, bg='#064e3b')
        self.trial_frame.pack(fill='x', padx=5, pady=2)
        
        self.trial_label = tk.Label(self.trial_frame,
                                   text="",
                                   bg='#16a34a',
                                   fg='white',
                                   font=('Arial', 10, 'bold'),
                                   relief='raised',
                                   bd=2,
                                   padx=10,
                                   pady=5)

    def create_session_controls(self):
        controls_frame = tk.Frame(self.scrollable_frame, bg='#1f2937', relief='raised', bd=2)
        controls_frame.pack(fill='x', padx=5, pady=5)
        
        # Session status and controls
        status_frame = tk.Frame(controls_frame, bg='#1f2937')
        status_frame.pack(fill='x', padx=5, pady=5)
        
        self.session_status_label = tk.Label(status_frame,
                                            text="Session: Inactive",
                                            bg='#1f2937',
                                            fg='#d1d5db',
                                            font=('Arial', 10, 'bold'))
        self.session_status_label.pack()
        
        button_frame = tk.Frame(status_frame, bg='#1f2937')
        button_frame.pack(pady=5)
        
        self.start_button = tk.Button(button_frame,
                                     text="🚀 Start Session",
                                     bg='#16a34a',
                                     fg='white',
                                     font=('Arial', 10, 'bold'),
                                     command=self.start_session,
                                     relief='raised',
                                     bd=2,
                                     padx=10,
                                     pady=5)
        self.start_button.pack(side='left', padx=2)
        
        self.reset_button = tk.Button(button_frame,
                                     text="Reset",
                                     bg='#dc2626',
                                     fg='white',
                                     font=('Arial', 10, 'bold'),
                                     command=self.reset_session,
                                     relief='raised',
                                     bd=2,
                                     padx=10,
                                     pady=5)
        self.reset_button.pack(side='left', padx=2)

    def create_card_display(self):
        display_frame = tk.Frame(self.scrollable_frame, bg='#1f2937', relief='raised', bd=2)
        display_frame.pack(fill='x', padx=5, pady=5)
        
        # Player and Banker card displays
        cards_frame = tk.Frame(display_frame, bg='#1f2937')
        cards_frame.pack(fill='x', padx=5, pady=5)
        
        # Player cards
        self.player_frame = tk.Frame(cards_frame, bg='#1e40af', relief='raised', bd=2)
        self.player_frame.pack(side='left', fill='both', expand=True, padx=2)
        
        tk.Label(self.player_frame,
                text="Player Cards",
                bg='#1e40af',
                fg='white',
                font=('Arial', 10, 'bold')).pack(pady=2)
        
        self.player_cards_label = tk.Label(self.player_frame,
                                          text="None",
                                          bg='#1e40af',
                                          fg='white',
                                          font=('Arial', 12))
        self.player_cards_label.pack()
        
        self.player_total_label = tk.Label(self.player_frame,
                                          text="Total: 0",
                                          bg='#1e40af',
                                          fg='#93c5fd',
                                          font=('Arial', 10))
        self.player_total_label.pack()
        
        # Banker cards
        self.banker_frame = tk.Frame(cards_frame, bg='#dc2626', relief='raised', bd=2)
        self.banker_frame.pack(side='right', fill='both', expand=True, padx=2)
        
        tk.Label(self.banker_frame,
                text="Banker Cards",
                bg='#dc2626',
                fg='white',
                font=('Arial', 10, 'bold')).pack(pady=2)
        
        self.banker_cards_label = tk.Label(self.banker_frame,
                                          text="None",
                                          bg='#dc2626',
                                          fg='white',
                                          font=('Arial', 12))
        self.banker_cards_label.pack()
        
        self.banker_total_label = tk.Label(self.banker_frame,
                                          text="Total: 0",
                                          bg='#dc2626',
                                          fg='#fca5a5',
                                          font=('Arial', 10))
        self.banker_total_label.pack()
        
        # Card input mode selector
        mode_frame = tk.Frame(display_frame, bg='#1f2937')
        mode_frame.pack(fill='x', padx=5, pady=5)
        
        self.player_mode_button = tk.Button(mode_frame,
                                           text="🔵 Player Cards Ready",
                                           bg='#1e40af',
                                           fg='white',
                                           font=('Arial', 9, 'bold'),
                                           command=self.switch_to_player,
                                           relief='raised',
                                           bd=2)
        self.player_mode_button.pack(side='left', fill='x', expand=True, padx=1)
        
        self.banker_mode_button = tk.Button(mode_frame,
                                           text="Banker Cards Ready",
                                           bg='#374151',
                                           fg='#9ca3af',
                                           font=('Arial', 9, 'bold'),
                                           command=self.switch_to_banker,
                                           relief='raised',
                                           bd=2)
        self.banker_mode_button.pack(side='right', fill='x', expand=True, padx=1)
        
        # Outcome recording
        outcome_frame = tk.Frame(display_frame, bg='#1f2937')
        outcome_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(outcome_frame,
                text="Record Outcome",
                bg='#1f2937',
                fg='#d1d5db',
                font=('Arial', 10, 'bold')).pack()
        
        outcome_buttons_frame = tk.Frame(outcome_frame, bg='#1f2937')
        outcome_buttons_frame.pack(pady=2)
        
        tk.Button(outcome_buttons_frame,
                 text="Player",
                 bg='#1e40af',
                 fg='white',
                 font=('Arial', 9, 'bold'),
                 command=lambda: self.record_outcome('Player'),
                 relief='raised',
                 bd=2,
                 width=8).pack(side='left', padx=1)
        
        tk.Button(outcome_buttons_frame,
                 text="Banker",
                 bg='#dc2626',
                 fg='white',
                 font=('Arial', 9, 'bold'),
                 command=lambda: self.record_outcome('Banker'),
                 relief='raised',
                 bd=2,
                 width=8).pack(side='left', padx=1)
        
        tk.Button(outcome_buttons_frame,
                 text="Tie",
                 bg='#d97706',
                 fg='white',
                 font=('Arial', 9, 'bold'),
                 command=lambda: self.record_outcome('Tie'),
                 relief='raised',
                 bd=2,
                 width=8).pack(side='left', padx=1)

    def create_card_input(self):
        input_frame = tk.Frame(self.scrollable_frame, bg='#1f2937', relief='raised', bd=2)
        input_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(input_frame,
                text="🎮 Lightning Card Input",
                bg='#1f2937',
                fg='#fbbf24',
                font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Card buttons grid
        cards_grid_frame = tk.Frame(input_frame, bg='#1f2937')
        cards_grid_frame.pack(padx=10, pady=5)
        
        self.card_buttons = {}
        card_values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        
        for i, card in enumerate(card_values):
            row = i // 5
            col = i % 5
            
            btn = tk.Button(cards_grid_frame,
                           text=card,
                           bg='#7c3aed',
                           fg='white',
                           font=('Arial', 14, 'bold'),
                           width=4,
                           height=2,
                           command=lambda c=card: self.handle_card_input(c),
                           relief='raised',
                           bd=3)
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.card_buttons[card] = btn
        
        # Undo button
        self.undo_button = tk.Button(input_frame,
                                    text="🔄 UNDO LAST CARD",
                                    bg='#dc2626',
                                    fg='white',
                                    font=('Arial', 10, 'bold'),
                                    command=self.handle_remove_last_card,
                                    relief='raised',
                                    bd=2,
                                    pady=5)
        self.undo_button.pack(fill='x', padx=10, pady=5)
        
        # Info labels
        tk.Label(input_frame,
                text="Tap cards • A,2,3,4,5,6,7,8,9,0",
                bg='#1f2937',
                fg='#9ca3af',
                font=('Arial', 8)).pack()
        
        tk.Label(input_frame,
                text="Optimized for live play",
                bg='#1f2937',
                fg='#6b7280',
                font=('Arial', 8)).pack()

    def create_prediction_display(self):
        self.prediction_display_frame = tk.Frame(self.scrollable_frame, bg='#1f2937', relief='raised', bd=2)
        
        # This frame will be packed/unpacked based on prediction state
        self.prediction_content_frame = tk.Frame(self.prediction_display_frame, bg='#1f2937')
        self.prediction_content_frame.pack(fill='x', padx=5, pady=5)
        
        self.prediction_title_label = tk.Label(self.prediction_content_frame,
                                              text="🔮 5 Round Prediction",
                                              bg='#1f2937',
                                              fg='#fbbf24',
                                              font=('Arial', 10, 'bold'))
        self.prediction_title_label.pack()
        
        self.prediction_result_label = tk.Label(self.prediction_content_frame,
                                               text="",
                                               bg='#1f2937',
                                               fg='white',
                                               font=('Arial', 12, 'bold'))
        self.prediction_result_label.pack()
        
        self.prediction_details_label = tk.Label(self.prediction_content_frame,
                                                text="",
                                                bg='#1f2937',
                                                fg='#9ca3af',
                                                font=('Arial', 9))
        self.prediction_details_label.pack()
        
        self.prediction_instruction_label = tk.Label(self.prediction_content_frame,
                                                    text="📝 Record next outcome to reset",
                                                    bg='#1f2937',
                                                    fg='#fbbf24',
                                                    font=('Arial', 9))
        self.prediction_instruction_label.pack()

    def create_prediction_engine(self):
        self.engine_frame = tk.Frame(self.scrollable_frame, bg='#581c87', relief='raised', bd=2)
        
        # Header
        header_frame = tk.Frame(self.engine_frame, bg='#581c87')
        header_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(header_frame,
                text="🔮 Lightning Prediction Engine",
                bg='#581c87',
                fg='white',
                font=('Arial', 12, 'bold')).pack()
        
        # Card advantage display
        advantage_frame = tk.Frame(self.engine_frame, bg='#1f2937', relief='sunken', bd=2)
        advantage_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(advantage_frame,
                text="Card Advantage",
                bg='#1f2937',
                fg='white',
                font=('Arial', 10, 'bold')).pack()
        
        self.advantage_label = tk.Label(advantage_frame,
                                       text="Neutral 0.0x",
                                       bg='#1f2937',
                                       fg='#9ca3af',
                                       font=('Arial', 10, 'bold'))
        self.advantage_label.pack()
        
        # Card counts
        counts_frame = tk.Frame(advantage_frame, bg='#1f2937')
        counts_frame.pack(fill='x', pady=2)
        
        self.zeros_label = tk.Label(counts_frame,
                                   text="Zeros: 0",
                                   bg='#1f2937',
                                   fg='#60a5fa',
                                   font=('Arial', 9))
        self.zeros_label.pack(side='left', expand=True)
        
        self.numbers_label = tk.Label(counts_frame,
                                     text="Numbers: 0",
                                     bg='#1f2937',
                                     fg='#34d399',
                                     font=('Arial', 9))
        self.numbers_label.pack(side='left', expand=True)
        
        self.total_label = tk.Label(counts_frame,
                                   text="Total: 0",
                                   bg='#1f2937',
                                   fg='#a78bfa',
                                   font=('Arial', 9))
        self.total_label.pack(side='left', expand=True)
        
        # Prediction result display
        self.prediction_result_frame = tk.Frame(self.engine_frame, bg='#581c87')
        
        self.prediction_outcome_label = tk.Label(self.prediction_result_frame,
                                                text="",
                                                bg='#581c87',
                                                fg='white',
                                                font=('Arial', 16, 'bold'))
        
        self.prediction_confidence_label = tk.Label(self.prediction_result_frame,
                                                   text="",
                                                   bg='#581c87',
                                                   fg='white',
                                                   font=('Arial', 12))
        
        self.prediction_reasoning_label = tk.Label(self.prediction_result_frame,
                                                  text="",
                                                  bg='#1f2937',
                                                  fg='#d1d5db',
                                                  font=('Arial', 9),
                                                  wraplength=350,
                                                  justify='center')
        
        self.prediction_patterns_label = tk.Label(self.prediction_result_frame,
                                                 text="",
                                                 bg='#581c87',
                                                 fg='#c084fc',
                                                 font=('Arial', 8),
                                                 wraplength=350,
                                                 justify='center')
        
        # Default display
        self.prediction_default_frame = tk.Frame(self.engine_frame, bg='#581c87')
        self.prediction_default_frame.pack(fill='x', padx=5, pady=10)
        
        tk.Label(self.prediction_default_frame,
                text="🎯",
                bg='#581c87',
                fg='white',
                font=('Arial', 24)).pack()
        
        self.prediction_status_label = tk.Label(self.prediction_default_frame,
                                               text="Ready to analyze 5-round patterns",
                                               bg='#581c87',
                                               fg='#d1d5db',
                                               font=('Arial', 10))
        self.prediction_status_label.pack()
        
        # Buttons
        button_frame = tk.Frame(self.engine_frame, bg='#581c87')
        button_frame.pack(fill='x', padx=5, pady=5)
        
        self.generate_button = tk.Button(button_frame,
                                        text="🔮 Generate Prediction",
                                        bg='#7c3aed',
                                        fg='white',
                                        font=('Arial', 10, 'bold'),
                                        command=self.make_prediction,
                                        relief='raised',
                                        bd=2,
                                        pady=5)
        self.generate_button.pack(side='left', fill='x', expand=True, padx=1)
        
        self.reset_prediction_button = tk.Button(button_frame,
                                                text="🔄 Reset",
                                                bg='#374151',
                                                fg='white',
                                                font=('Arial', 10, 'bold'),
                                                command=self.reset_prediction,
                                                relief='raised',
                                                bd=2,
                                                pady=5)
        self.reset_prediction_button.pack(side='right', fill='x', expand=True, padx=1)

    def create_statistics(self):
        self.stats_frame = tk.Frame(self.scrollable_frame, bg='#374151', relief='raised', bd=2)
        
        # Header
        header_frame = tk.Frame(self.stats_frame, bg='#374151')
        header_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(header_frame,
                text="📊 Statistics",
                bg='#374151',
                fg='white',
                font=('Arial', 12, 'bold')).pack()
        
        # Stats grid
        stats_grid_frame = tk.Frame(self.stats_frame, bg='#374151')
        stats_grid_frame.pack(fill='x', padx=5, pady=5)
        
        # Hands played
        hands_frame = tk.Frame(stats_grid_frame, bg='#1f2937', relief='raised', bd=1)
        hands_frame.pack(side='left', fill='both', expand=True, padx=1, pady=1)
        
        self.hands_value_label = tk.Label(hands_frame,
                                         text="0",
                                         bg='#1f2937',
                                         fg='white',
                                         font=('Arial', 14, 'bold'))
        self.hands_value_label.pack()
        
        tk.Label(hands_frame,
                text="Hands",
                bg='#1f2937',
                fg='#9ca3af',
                font=('Arial', 8)).pack()
        
        # Win rate
        winrate_frame = tk.Frame(stats_grid_frame, bg='#1f2937', relief='raised', bd=1)
        winrate_frame.pack(side='right', fill='both', expand=True, padx=1, pady=1)
        
        self.winrate_value_label = tk.Label(winrate_frame,
                                           text="0.0%",
                                           bg='#1f2937',
                                           fg='#34d399',
                                           font=('Arial', 14, 'bold'))
        self.winrate_value_label.pack()
        
        tk.Label(winrate_frame,
                text="Win Rate",
                bg='#1f2937',
                fg='#9ca3af',
                font=('Arial', 8)).pack()
        
        # Second row
        stats_grid_frame2 = tk.Frame(self.stats_frame, bg='#374151')
        stats_grid_frame2.pack(fill='x', padx=5, pady=5)
        
        # P/L
        pl_frame = tk.Frame(stats_grid_frame2, bg='#1f2937', relief='raised', bd=1)
        pl_frame.pack(side='left', fill='both', expand=True, padx=1, pady=1)
        
        self.pl_value_label = tk.Label(pl_frame,
                                      text="0.00",
                                      bg='#1f2937',
                                      fg='#9ca3af',
                                      font=('Arial', 14, 'bold'))
        self.pl_value_label.pack()
        
        tk.Label(pl_frame,
                text="P/L",
                bg='#1f2937',
                fg='#9ca3af',
                font=('Arial', 8)).pack()
        
        # Wins
        wins_frame = tk.Frame(stats_grid_frame2, bg='#1f2937', relief='raised', bd=1)
        wins_frame.pack(side='right', fill='both', expand=True, padx=1, pady=1)
        
        self.wins_value_label = tk.Label(wins_frame,
                                        text="0",
                                        bg='#1f2937',
                                        fg='#34d399',
                                        font=('Arial', 14, 'bold'))
        self.wins_value_label.pack()
        
        tk.Label(wins_frame,
                text="Wins",
                bg='#1f2937',
                fg='#9ca3af',
                font=('Arial', 8)).pack()
        
        # Footer
        footer_frame = tk.Frame(self.scrollable_frame, bg='#064e3b')
        footer_frame.pack(fill='x', padx=5, pady=10)
        
        tk.Label(footer_frame,
                text="🚀 Mobile optimized • Live casino ready",
                bg='#064e3b',
                fg='#9ca3af',
                font=('Arial', 8)).pack()

    # Trial System Methods
    def load_trial_data(self):
        try:
            if os.path.exists(self.STORAGE_FILE):
                with open(self.STORAGE_FILE, 'r') as f:
                    data = json.load(f)
                    self.trial_status = TrialStatus(**data)
                    self.calculate_trial_status()
        except Exception as e:
            print(f"Error loading trial data: {e}")
            self.trial_status = TrialStatus()

    def save_trial_data(self):
        try:
            with open(self.STORAGE_FILE, 'w') as f:
                json.dump(asdict(self.trial_status), f)
        except Exception as e:
            print(f"Error saving trial data: {e}")

    def calculate_trial_status(self):
        if self.trial_status.start_time == 0:
            return
        
        now = int(time.time() * 1000)
        remaining_time_ms = max(0, self.trial_status.end_time - now)
        is_expired = remaining_time_ms <= 0 and self.trial_status.is_active
        
        self.trial_status.remaining_time_ms = remaining_time_ms
        self.trial_status.is_expired = is_expired
        self.trial_status.is_active = self.trial_status.is_active and not is_expired

    def start_trial(self):
        now = int(time.time() * 1000)
        end_time = now + self.TRIAL_DURATION_MS
        
        self.trial_status = TrialStatus(
            is_active=True,
            remaining_time_ms=self.TRIAL_DURATION_MS,
            is_expired=False,
            start_time=now,
            end_time=end_time
        )
        
        self.save_trial_data()

    def start_trial_timer(self):
        def update_timer():
            while True:
                if self.trial_status.is_active:
                    self.calculate_trial_status()
                    self.save_trial_data()
                    
                    if self.trial_status.is_expired:
                        self.root.after(0, self.show_trial_expired)
                        break
                    
                    self.root.after(0, self.update_trial_display)
                
                time.sleep(1)
        
        timer_thread = threading.Thread(target=update_timer, daemon=True)
        timer_thread.start()

    def format_remaining_time(self, time_ms: int) -> str:
        if time_ms <= 0:
            return "00:00"
        total_seconds = time_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def update_trial_display(self):
        if not self.trial_status.is_active or self.trial_status.is_expired:
            self.trial_label.pack_forget()
            return
        
        remaining_time = self.format_remaining_time(self.trial_status.remaining_time_ms)
        remaining_minutes = self.trial_status.remaining_time_ms / (1000 * 60)
        
        if remaining_minutes <= 5:
            bg_color = '#dc2626'  # Red
            icon = '🚨'
            message = 'Trial ending soon!'
        elif remaining_minutes <= 10:
            bg_color = '#d97706'  # Yellow
            icon = '⚠️'
            message = 'Trial time low!'
        else:
            bg_color = '#16a34a'  # Green
            icon = '⚡'
            message = ''
        
        self.trial_label.config(
            text=f"{icon} Trial: {remaining_time} {message}",
            bg=bg_color
        )
        self.trial_label.pack(pady=5)

    def show_trial_expired(self):
        # Hide main content and show expired screen
        for widget in self.scrollable_frame.winfo_children():
            widget.pack_forget()
        
        # Create trial expired screen
        expired_frame = tk.Frame(self.scrollable_frame, bg='#064e3b')
        expired_frame.pack(fill='both', expand=True, padx=10, pady=20)
        
        # Header
        header_frame = tk.Frame(expired_frame, bg='#1f2937', relief='raised', bd=3)
        header_frame.pack(fill='x', pady=10)
        
        tk.Label(header_frame,
                text="⚡",
                bg='#1f2937',
                fg='#fbbf24',
                font=('Arial', 32)).pack(pady=5)
        
        tk.Label(header_frame,
                text="Lightning Baccarat",
                bg='#1f2937',
                fg='#fbbf24',
                font=('Arial', 16, 'bold')).pack()
        
        tk.Label(header_frame,
                text="Trial Period Expired",
                bg='#1f2937',
                fg='#d1d5db',
                font=('Arial', 12)).pack(pady=5)
        
        # Expired badge
        tk.Label(header_frame,
                text="🚫 TRIAL EXPIRED",
                bg='#dc2626',
                fg='white',
                font=('Arial', 12, 'bold'),
                relief='raised',
                bd=2,
                padx=10,
                pady=5).pack(pady=10)
        
        # Trial summary
        summary_frame = tk.Frame(expired_frame, bg='#1f2937', relief='raised', bd=2)
        summary_frame.pack(fill='x', pady=10)
        
        tk.Label(summary_frame,
                text="📊 Trial Summary",
                bg='#1f2937',
                fg='white',
                font=('Arial', 12, 'bold')).pack(pady=5)
        
        trial_duration_ms = self.trial_status.end_time - self.trial_status.start_time
        duration_minutes = trial_duration_ms // (1000 * 60)
        
        start_date = datetime.fromtimestamp(self.trial_status.start_time / 1000).strftime("%Y-%m-%d %H:%M:%S")
        end_date = datetime.fromtimestamp(self.trial_status.end_time / 1000).strftime("%Y-%m-%d %H:%M:%S")
        
        tk.Label(summary_frame,
                text=f"Duration: {duration_minutes} minutes",
                bg='#1f2937',
                fg='#60a5fa',
                font=('Arial', 10)).pack()
        
        tk.Label(summary_frame,
                text=f"Started: {start_date}",
                bg='#1f2937',
                fg='#9ca3af',
                font=('Arial', 9)).pack()
        
        tk.Label(summary_frame,
                text=f"Expired: {end_date}",
                bg='#1f2937',
                fg='#9ca3af',
                font=('Arial', 9)).pack(pady=(0, 5))
        
        # Upgrade section
        upgrade_frame = tk.Frame(expired_frame, bg='#581c87', relief='raised', bd=2)
        upgrade_frame.pack(fill='x', pady=10)
        
        tk.Label(upgrade_frame,
                text="🚀",
                bg='#581c87',
                fg='white',
                font=('Arial', 24)).pack(pady=5)
        
        tk.Label(upgrade_frame,
                text="Upgrade to Full Version",
                bg='#581c87',
                fg='white',
                font=('Arial', 14, 'bold')).pack()
        
        tk.Label(upgrade_frame,
                text="Continue using Lightning Baccarat with unlimited access:",
                bg='#581c87',
                fg='#d1d5db',
                font=('Arial', 10),
                wraplength=350).pack(pady=5)
        
        features = [
            "✓ Unlimited session time",
            "✓ Advanced prediction algorithms",
            "✓ Real-time card counting",
            "✓ Pattern analysis & statistics"
        ]
        
        for feature in features:
            tk.Label(upgrade_frame,
                    text=feature,
                    bg='#581c87',
                    fg='#34d399',
                    font=('Arial', 9)).pack()
        
        # Buttons
        button_frame = tk.Frame(expired_frame, bg='#064e3b')
        button_frame.pack(fill='x', pady=10)
        
        tk.Button(button_frame,
                 text="💎 Upgrade Now",
                 bg='#16a34a',
                 fg='white',
                 font=('Arial', 12, 'bold'),
                 command=self.open_upgrade_link,
                 relief='raised',
                 bd=3,
                 padx=20,
                 pady=10).pack(pady=5)
        
        tk.Button(button_frame,
                 text="📧 Contact Support",
                 bg='#374151',
                 fg='white',
                 font=('Arial', 10, 'bold'),
                 command=self.open_support_link,
                 relief='raised',
                 bd=2,
                 padx=20,
                 pady=5).pack(pady=5)
        
        # Footer
        tk.Label(expired_frame,
                text="Thank you for trying Lightning Baccarat!",
                bg='#064e3b',
                fg='#9ca3af',
                font=('Arial', 9)).pack(pady=10)

    def open_upgrade_link(self):
        webbrowser.open('https://lightningbaccarat.com/upgrade')

    def open_support_link(self):
        webbrowser.open('mailto:support@lightningbaccarat.com')

    # Card Counting Methods
    def calculate_advantage(self, zeros: int, numbers: int) -> Tuple[Advantage, float]:
        diff = zeros - numbers
        total = zeros + numbers
        
        if total == 0:
            return 'Neutral', 0.0
        
        intensity = min((abs(diff) / total) * 100, 100)
        
        if diff > 2:
            return 'Player', intensity
        elif diff < -2:
            return 'Banker', intensity
        else:
            return 'Neutral', intensity

    def add_card(self, card: CardValue):
        is_zero = card == '0'
        is_number = card in ['2', '3', '4', '5', '6', '7', '8', '9']
        
        if is_zero:
            self.card_count.zeros += 1
        if is_number:
            self.card_count.numbers += 1
        if is_zero or is_number:
            self.card_count.total += 1
        
        self.card_count.advantage, self.card_count.intensity = self.calculate_advantage(
            self.card_count.zeros, self.card_count.numbers
        )

    def remove_last_card(self):
        if self.card_count.total == 0:
            return
        
        self.card_count.zeros = max(0, self.card_count.zeros - 1)
        self.card_count.numbers = max(0, self.card_count.numbers - 1)
        self.card_count.total = max(0, self.card_count.total - 1)
        
        self.card_count.advantage, self.card_count.intensity = self.calculate_advantage(
            self.card_count.zeros, self.card_count.numbers
        )

    def reset_card_count(self):
        self.card_count = CardCount()

    # Baccarat Logic Methods
    def calculate_baccarat_total(self, cards: List[CardValue]) -> int:
        total = 0
        for card in cards:
            if card == 'A':
                total += 1
            elif card == '0':
                total += 0
            else:
                total += int(card)
        return total % 10

    # Pattern Analysis Methods
    def analyze_patterns(self, rounds: List[RoundData]) -> PatternAnalysis:
        if len(rounds) == 0:
            return PatternAnalysis(
                streak_length=0,
                streak_type=None,
                alternating_pattern=False,
                recent_outcomes=[],
                pattern_confidence=0
            )
        
        outcomes = [round_data.outcome for round_data in rounds]
        recent_outcomes = outcomes[-5:]
        
        # Calculate streak
        streak_length = 1
        streak_type = outcomes[-1]
        
        for i in range(len(outcomes) - 2, -1, -1):
            if outcomes[i] == streak_type and outcomes[i] != 'Tie':
                streak_length += 1
            else:
                break
        
        # Check for alternating pattern
        alternating_pattern = False
        if len(outcomes) >= 4:
            non_tie_outcomes = [outcome for outcome in outcomes if outcome != 'Tie']
            if len(non_tie_outcomes) >= 4:
                alternating_pattern = True
                for i in range(1, min(4, len(non_tie_outcomes))):
                    if non_tie_outcomes[i] == non_tie_outcomes[i - 1]:
                        alternating_pattern = False
                        break
        
        # Calculate pattern confidence
        pattern_confidence = 0
        if streak_length >= 3:
            pattern_confidence = min(85, 40 + (streak_length * 10))
        elif alternating_pattern:
            pattern_confidence = 65
        else:
            pattern_confidence = 30
        
        return PatternAnalysis(
            streak_length=streak_length if streak_type != 'Tie' else 0,
            streak_type=streak_type if streak_type != 'Tie' else None,
            alternating_pattern=alternating_pattern,
            recent_outcomes=recent_outcomes,
            pattern_confidence=pattern_confidence
        )

    def calculate_card_advantage(self) -> Tuple[float, float]:
        zeros = self.card_count.zeros
        numbers = self.card_count.numbers
        total = self.card_count.total
        
        if total == 0:
            return 50.0, 50.0
        
        zero_ratio = zeros / total
        number_ratio = numbers / total
        
        player_boost = zero_ratio * 15
        banker_boost = number_ratio * 12
        
        base_player_chance = 45.8
        base_banker_chance = 50.7
        
        player_advantage = min(85, max(15, base_player_chance + player_boost - (banker_boost * 0.5)))
        banker_advantage = min(85, max(15, base_banker_chance + banker_boost - (player_boost * 0.5)))
        
        return player_advantage, banker_advantage

    def generate_prediction(self) -> PredictionResult:
        patterns = self.analyze_patterns(self.recent_rounds)
        player_advantage, banker_advantage = self.calculate_card_advantage()
        
        predicted_outcome: GameOutcome = 'Player'
        confidence = 50
        reasoning = ''
        detected_patterns = []
        
        if patterns.streak_type and patterns.streak_length >= 3:
            predicted_outcome = 'Banker' if patterns.streak_type == 'Player' else 'Player'
            confidence = min(80, 45 + (patterns.streak_length * 8))
            reasoning = f"{patterns.streak_length}-hand {patterns.streak_type} streak suggests break"
            detected_patterns.append(f"{patterns.streak_length} {patterns.streak_type} streak")
        elif patterns.alternating_pattern:
            last_non_tie = [outcome for outcome in patterns.recent_outcomes if outcome != 'Tie'][0]
            predicted_outcome = 'Banker' if last_non_tie == 'Player' else 'Player'
            confidence = 70
            reasoning = 'Alternating pattern detected'
            detected_patterns.append('Alternating pattern')
        else:
            if player_advantage > banker_advantage:
                predicted_outcome = 'Player'
                confidence = min(75, 50 + ((player_advantage - banker_advantage) * 0.8))
                reasoning = 'Card composition favors Player'
            else:
                predicted_outcome = 'Banker'
                confidence = min(75, 50 + ((banker_advantage - player_advantage) * 0.8))
                reasoning = 'Card composition favors Banker'
        
        if self.card_count.advantage != 'Neutral':
            detected_patterns.append(f"{self.card_count.advantage} advantage ({self.card_count.intensity:.1f}x)")
        
        if self.card_count.intensity > 1.2:
            confidence = min(85, confidence + (self.card_count.intensity * 5))
            reasoning += f" + strong card count ({self.card_count.intensity:.1f}x)"
        
        return PredictionResult(
            outcome=predicted_outcome,
            confidence=round(confidence),
            reasoning=reasoning,
            patterns=detected_patterns
        )

    def calculate_simple_prediction(self, rounds_data: List[RoundData]) -> SimplePrediction:
        if len(rounds_data) < 5:
            return SimplePrediction(
                prediction='NEUTRAL',
                numbers_count=0,
                zeros_count=0,
                rounds_analyzed=0
            )
        
        relevant_rounds = rounds_data[-5:]
        numbers_count = 0
        zeros_count = 0
        
        for round_data in relevant_rounds:
            all_cards = round_data.player_cards + round_data.banker_cards
            for card in all_cards:
                if card == '0':
                    zeros_count += 1
                else:
                    numbers_count += 1
        
        prediction: PredictionType = 'NEUTRAL'
        if numbers_count > zeros_count:
            prediction = 'BANKER'
        elif zeros_count > numbers_count:
            prediction = 'PLAYER'
        
        return SimplePrediction(
            prediction=prediction,
            numbers_count=numbers_count,
            zeros_count=zeros_count,
            rounds_analyzed=5
        )

    # Session Management Methods
    def start_session(self):
        if self.trial_status.is_expired:
            return
        
        self.is_session_active = True
        self.session_data.is_active = True
        self.reset_card_count()
        self.update_display()

    def reset_session(self):
        self.is_session_active = False
        self.recent_rounds = []
        self.current_player_cards = []
        self.current_banker_cards = []
        self.is_recording_player_cards = True
        self.prediction_state = 'collecting'
        self.active_prediction = None
        self.last_prediction_tracker = None
        self.current_prediction = None
        self.session_data = SessionData()
        self.is_processing = False
        self.reset_card_count()
        self.update_display()

    def switch_to_player(self):
        if self.trial_status.is_expired or not self.is_session_active:
            return
        self.is_recording_player_cards = True
        self.update_display()

    def switch_to_banker(self):
        if self.trial_status.is_expired or not self.is_session_active:
            return
        self.is_recording_player_cards = False
        self.update_display()

    def handle_card_input(self, card: CardValue):
        if self.trial_status.is_expired or self.is_processing or not self.is_session_active:
            return
        
        if self.is_recording_player_cards and len(self.current_player_cards) >= 3:
            return
        if not self.is_recording_player_cards and len(self.current_banker_cards) >= 3:
            return
        
        self.is_processing = True
        
        try:
            self.add_card(card)
            
            if self.is_recording_player_cards:
                if len(self.current_player_cards) < 3:
                    self.current_player_cards.append(card)
            else:
                if len(self.current_banker_cards) < 3:
                    self.current_banker_cards.append(card)
            
            self.update_display()
        finally:
            self.root.after(100, lambda: setattr(self, 'is_processing', False))

    def handle_remove_last_card(self):
        if self.trial_status.is_expired or self.is_processing:
            return
        
        self.is_processing = True
        
        try:
            self.remove_last_card()
            
            if self.is_recording_player_cards and len(self.current_player_cards) > 0:
                self.current_player_cards.pop()
            elif not self.is_recording_player_cards and len(self.current_banker_cards) > 0:
                self.current_banker_cards.pop()
            
            self.update_display()
        finally:
            self.root.after(100, lambda: setattr(self, 'is_processing', False))

    def record_outcome(self, outcome: GameOutcome):
        if self.trial_status.is_expired or not self.is_session_active or self.is_processing:
            return
        
        self.is_processing = True
        
        try:
            new_round = RoundData(
                player_cards=self.current_player_cards.copy(),
                banker_cards=self.current_banker_cards.copy(),
                outcome=outcome,
                round_number=len(self.recent_rounds) + 1
            )
            
            # Update session data
            self.session_data.hands_played += 1
            if outcome == 'Player':
                self.session_data.wins += 1
            elif outcome == 'Banker':
                self.session_data.losses += 1
            else:
                self.session_data.ties += 1
            
            if self.session_data.hands_played > 0:
                self.session_data.win_rate = (self.session_data.wins / self.session_data.hands_played) * 100
            
            profit_change = 1 if outcome == 'Player' else -1 if outcome == 'Banker' else 0
            self.session_data.profit_loss += profit_change
            
            # Handle predictions
            if self.prediction_state == 'prediction-shown' and self.active_prediction:
                prediction_was_correct = False
                if (self.active_prediction.prediction == 'BANKER' and outcome == 'Banker') or \
                   (self.active_prediction.prediction == 'PLAYER' and outcome == 'Player') or \
                   (self.active_prediction.prediction == 'NEUTRAL' and outcome == 'Tie'):
                    prediction_was_correct = True
                
                self.last_prediction_tracker = LastPredictionTracker(
                    prediction=self.active_prediction.prediction,
                    was_correct=prediction_was_correct
                )
                
                self.prediction_state = 'collecting'
                self.active_prediction = None
                
                if not prediction_was_correct:
                    self.recent_rounds = [new_round]
                else:
                    self.recent_rounds.append(new_round)
            else:
                self.recent_rounds.append(new_round)
                
                if self.prediction_state == 'collecting' and len(self.recent_rounds) >= 5:
                    new_prediction = self.calculate_simple_prediction(self.recent_rounds)
                    if new_prediction.rounds_analyzed >= 5:
                        self.active_prediction = new_prediction
                        self.prediction_state = 'prediction-shown'
            
            # Keep only last 10 rounds
            self.recent_rounds = self.recent_rounds[-10:]
            
            # Reset cards for next round
            self.current_player_cards = []
            self.current_banker_cards = []
            self.is_recording_player_cards = True
            
            self.update_display()
        finally:
            self.root.after(100, lambda: setattr(self, 'is_processing', False))

    def make_prediction(self):
        if self.trial_status.is_expired or len(self.recent_rounds) < 5:
            return
        
        self.is_analyzing = True
        self.update_display()
        
        def analyze():
            time.sleep(0.8)  # Simulate analysis time
            prediction = self.generate_prediction()
            self.current_prediction = prediction
            self.is_analyzing = False
            self.root.after(0, self.update_display)
        
        threading.Thread(target=analyze, daemon=True).start()

    def reset_prediction(self):
        if self.trial_status.is_expired:
            return
        self.current_prediction = None
        self.update_display()

    # Display Update Methods
    def update_display(self):
        self.update_session_display()
        self.update_card_display()
        self.update_card_input_display()
        self.update_prediction_display()
        self.update_prediction_engine_display()
        self.update_statistics_display()

    def update_session_display(self):
        if self.is_session_active:
            self.session_status_label.config(text="Session: 🟢 Active", fg='#34d399')
            self.start_button.pack_forget()
            self.reset_button.pack(side='left', padx=2)
        else:
            self.session_status_label.config(text="Session: Inactive", fg='#9ca3af')
            self.reset_button.pack_forget()
            self.start_button.pack(side='left', padx=2)

    def update_card_display(self):
        # Update player cards
        player_text = ', '.join(self.current_player_cards) if self.current_player_cards else "None"
        self.player_cards_label.config(text=player_text)
        self.player_total_label.config(text=f"Total: {self.calculate_baccarat_total(self.current_player_cards)}")
        
        # Update banker cards
        banker_text = ', '.join(self.current_banker_cards) if self.current_banker_cards else "None"
        self.banker_cards_label.config(text=banker_text)
        self.banker_total_label.config(text=f"Total: {self.calculate_baccarat_total(self.current_banker_cards)}")
        
        # Update mode buttons
        if self.is_recording_player_cards:
            self.player_mode_button.config(
                text="🔵 Player Cards Ready",
                bg='#1e40af',
                fg='white'
            )
            self.banker_mode_button.config(
                text="Banker Cards Ready",
                bg='#374151',
                fg='#9ca3af'
            )
        else:
            self.player_mode_button.config(
                text="Player Cards Ready",
                bg='#374151',
                fg='#9ca3af'
            )
            self.banker_mode_button.config(
                text="🔴 Banker Cards Ready",
                bg='#dc2626',
                fg='white'
            )

    def update_card_input_display(self):
        # Update card button states
        input_disabled = (not self.is_session_active or 
                         self.trial_status.is_expired or 
                         self.is_processing or
                         (self.is_recording_player_cards and len(self.current_player_cards) >= 3) or
                         (not self.is_recording_player_cards and len(self.current_banker_cards) >= 3))
        
        for card, button in self.card_buttons.items():
            if input_disabled:
                button.config(state='disabled', bg='#374151')
            else:
                button.config(state='normal', bg='#7c3aed')
        
        # Update undo button
        undo_disabled = (not self.is_session_active or 
                        self.trial_status.is_expired or 
                        self.is_processing)
        
        if undo_disabled:
            self.undo_button.config(state='disabled', bg='#374151')
        else:
            self.undo_button.config(state='normal', bg='#dc2626')

    def update_prediction_display(self):
        if self.prediction_state == 'prediction-shown' and self.active_prediction and not self.trial_status.is_expired:
            self.prediction_display_frame.pack(fill='x', padx=5, pady=5)
            
            # Update prediction result
            prediction_text = self.active_prediction.prediction
            if prediction_text == 'BANKER':
                icon = '🔴'
                color = '#dc2626'
            elif prediction_text == 'PLAYER':
                icon = '🔵'
                color = '#1e40af'
            else:
                icon = '⚫'
                color = '#6b7280'
            
            self.prediction_result_label.config(
                text=f"{icon} {prediction_text}",
                fg=color
            )
            
            details_text = f"Numbers: {self.active_prediction.numbers_count} | Zeros: {self.active_prediction.zeros_count}\n({self.active_prediction.rounds_analyzed} rounds analyzed)"
            self.prediction_details_label.config(text=details_text)
            
        elif (self.prediction_state == 'collecting' and 
              len(self.recent_rounds) > 0 and 
              len(self.recent_rounds) < 5 and 
              not self.trial_status.is_expired):
            
            self.prediction_display_frame.pack(fill='x', padx=5, pady=5)
            self.prediction_title_label.config(text="📊 Collecting Data")
            self.prediction_result_label.config(
                text=f"Rounds: {len(self.recent_rounds)}/5 (need {5 - len(self.recent_rounds)} more)",
                fg='#9ca3af'
            )
            
            if self.last_prediction_tracker:
                status = "✅ CORRECT" if self.last_prediction_tracker.was_correct else "❌ WRONG"
                color = '#34d399' if self.last_prediction_tracker.was_correct else '#ef4444'
                details_text = f"Last: {self.last_prediction_tracker.prediction} was {status}"
                self.prediction_details_label.config(text=details_text, fg=color)
            else:
                self.prediction_details_label.config(text="")
            
            self.prediction_instruction_label.pack_forget()
        else:
            self.prediction_display_frame.pack_forget()

    def update_prediction_engine_display(self):
        if len(self.recent_rounds) >= 5 and not self.trial_status.is_expired:
            self.engine_frame.pack(fill='x', padx=5, pady=5)
            
            # Update card advantage
            advantage_text = f"{self.card_count.advantage} {self.card_count.intensity:.1f}x"
            if self.card_count.advantage == 'Player':
                color = '#60a5fa'
            elif self.card_count.advantage == 'Banker':
                color = '#ef4444'
            else:
                color = '#9ca3af'
            
            self.advantage_label.config(text=advantage_text, fg=color)
            
            # Update counts
            self.zeros_label.config(text=f"Zeros: {self.card_count.zeros}")
            self.numbers_label.config(text=f"Numbers: {self.card_count.numbers}")
            self.total_label.config(text=f"Total: {self.card_count.total}")
            
            # Update prediction result or default display
            if self.current_prediction:
                self.prediction_default_frame.pack_forget()
                self.prediction_result_frame.pack(fill='x', padx=5, pady=10)
                
                # Update outcome
                outcome_text = self.current_prediction.outcome
                if outcome_text == 'Player':
                    icon = '🔵'
                elif outcome_text == 'Banker':
                    icon = '🔴'
                else:
                    icon = '⚫'
                
                self.prediction_outcome_label.config(text=f"{icon} {outcome_text}")
                self.prediction_outcome_label.pack(pady=2)
                
                # Update confidence
                confidence = self.current_prediction.confidence
                if confidence >= 75:
                    conf_color = '#34d399'
                elif confidence >= 60:
                    conf_color = '#fbbf24'
                else:
                    conf_color = '#ef4444'
                
                self.prediction_confidence_label.config(
                    text=f"Confidence: {confidence}%",
                    fg=conf_color
                )
                self.prediction_confidence_label.pack()
                
                # Update reasoning
                self.prediction_reasoning_label.config(text=self.current_prediction.reasoning)
                self.prediction_reasoning_label.pack(pady=5)
                
                # Update patterns
                if self.current_prediction.patterns:
                    patterns_text = " • ".join(self.current_prediction.patterns)
                    self.prediction_patterns_label.config(text=patterns_text)
                    self.prediction_patterns_label.pack()
                else:
                    self.prediction_patterns_label.pack_forget()
                
            else:
                self.prediction_result_frame.pack_forget()
                self.prediction_default_frame.pack(fill='x', padx=5, pady=10)
                
                if self.is_analyzing:
                    self.prediction_status_label.config(text="Analyzing patterns...")
                else:
                    self.prediction_status_label.config(text="Ready to analyze 5-round patterns")
            
            # Update buttons
            generate_disabled = (len(self.recent_rounds) < 5 or 
                               self.trial_status.is_expired or 
                               self.is_analyzing)
            
            if generate_disabled:
                self.generate_button.config(state='disabled', bg='#374151')
            else:
                self.generate_button.config(state='normal', bg='#7c3aed')
            
            if self.is_analyzing:
                self.generate_button.config(text="🔮 Analyzing...")
            else:
                self.generate_button.config(text="🔮 Generate Prediction")
            
            reset_disabled = self.trial_status.is_expired
            if reset_disabled:
                self.reset_prediction_button.config(state='disabled', bg='#1f2937')
            else:
                self.reset_prediction_button.config(state='normal', bg='#374151')
        else:
            self.engine_frame.pack_forget()

    def update_statistics_display(self):
        if self.session_data.hands_played > 0:
            self.stats_frame.pack(fill='x', padx=5, pady=5)
            
            # Update values
            self.hands_value_label.config(text=str(self.session_data.hands_played))
            
            # Update win rate with color
            win_rate = self.session_data.win_rate
            if win_rate >= 60:
                color = '#34d399'
            elif win_rate >= 50:
                color = '#fbbf24'
            else:
                color = '#ef4444'
            
            self.winrate_value_label.config(
                text=f"{win_rate:.1f}%",
                fg=color
            )
            
            # Update P/L with color
            pl = self.session_data.profit_loss
            if pl > 0:
                color = '#34d399'
                text = f"+{pl:.2f}"
            elif pl < 0:
                color = '#ef4444'
                text = f"{pl:.2f}"
            else:
                color = '#9ca3af'
                text = "0.00"
            
            self.pl_value_label.config(text=text, fg=color)
            
            # Update wins
            self.wins_value_label.config(text=str(self.session_data.wins))
        else:
            self.stats_frame.pack_forget()

    def run(self):
        # Check if trial is expired on startup
        if self.trial_status.is_expired:
            self.show_trial_expired()
        
        self.root.mainloop()

if __name__ == "__main__":
    app = LightningBaccaratApp()
    app.run()
