import tkinter as tk
from tkinter import font
import random
import time

class VerbGame:
    def __init__(self, root):
        self.root = root
        self.root.title("English Verb Challenge")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Verb dictionaries
        self.irregular_verbs = {
            "be": "was/were", "become": "became", "begin": "began", "break": "broke",
            "bring": "brought", "build": "built", "buy": "bought", "choose": "chose",
            "come": "came", "do": "did", "drink": "drank", "drive": "drove", "eat": "ate",
            "fall": "fell", "feel": "felt", "fight": "fought", "find": "found", "fly": "flew",
            "forget": "forgot", "get": "got", "give": "gave", "go": "went", "have": "had",
            "know": "knew", "leave": "left", "make": "made", "meet": "met", "pay": "paid",
            "read": "read", "run": "ran", "say": "said", "see": "saw", "sell": "sold",
            "send": "sent", "sing": "sang", "sit": "sat", "sleep": "slept", "speak": "spoke",
            "stand": "stood", "swim": "swam", "take": "took", "teach": "taught", "tell": "told",
            "think": "thought", "understand": "understood", "wear": "wore", "win": "won", "write": "wrote"
        }
        
        self.regular_verbs = {
            "ask": "asked", "call": "called", "clean": "cleaned", "close": "closed",
            "cook": "cooked", "dance": "danced", "help": "helped", "jump": "jumped",
            "laugh": "laughed", "like": "liked", "live": "lived", "look": "looked",
            "love": "loved", "move": "moved", "open": "opened", "play": "played",
            "rain": "rained", "shop": "shopped", "smile": "smiled", "start": "started",
            "stay": "stayed", "stop": "stopped", "study": "studied", "talk": "talked",
            "travel": "traveled", "try": "tried", "visit": "visited", "wait": "waited",
            "walk": "walked", "want": "wanted", "work": "worked"
        }
        
        # Common mistakes for regular verbs
        self.common_mistakes = {
            "stop": ["stoped", "stop"],
            "study": ["studyed", "studed"],
            "try": ["tryed", "trid"],
            "plan": ["planed", "plann"],
            "prefer": ["prefered", "preferrd"],
            "open": ["opend", "open"],
            "shop": ["shoped", "shop"]
        }
        
        # Game state
        self.game_mode = None
        self.blue_score = 0
        self.red_score = 0
        self.current_team = None
        self.used_verbs = set()
        self.current_verb = None
        self.correct_answer = None
        self.time_left = 0
        self.timer_running = False
        self.paused = False
        self.correct_in_row = 0
        self.team_questions = {"blue": [], "red": []}
        
        # Fonts that work across systems
        self.title_font = font.Font(family="Helvetica", size=24, weight="bold")
        self.verb_font = font.Font(family="Helvetica", size=32, weight="bold")
        self.button_font = font.Font(family="Helvetica", size=14)
        self.timer_font = font.Font(family="Helvetica", size=18, weight="bold")
        self.score_font = font.Font(family="Helvetica", size=16)
        
        # Start screen
        self.show_welcome_screen()
    
    def show_welcome_screen(self):
        """Display welcome screen with game options"""
        self.clear_screen()
        self.root.configure(bg="#f0f0f0")
        
        welcome_label = tk.Label(
            self.root,
            text="Welcome to English Verb Master!",
            font=self.title_font,
            bg="#f0f0f0"
        )
        welcome_label.pack(pady=50)
        
        desc_label = tk.Label(
            self.root,
            text="Practice regular and irregular past tense verbs\nChoose your game mode:",
            font=self.button_font,
            bg="#f0f0f0"
        )
        desc_label.pack(pady=20)
        
        single_btn = tk.Button(
            self.root,
            text="Single Player Practice",
            font=self.button_font,
            command=lambda: self.start_game("single"),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10
        )
        single_btn.pack(pady=20)
        
        multi_btn = tk.Button(
            self.root,
            text="Team Challenge (Blue vs Red)",
            font=self.button_font,
            command=lambda: self.start_game("multi"),
            bg="#2196F3",
            fg="white",
            padx=20,
            pady=10
        )
        multi_btn.pack(pady=20)
    
    def start_game(self, mode):
        """Initialize game based on selected mode"""
        self.game_mode = mode
        self.blue_score = 0
        self.red_score = 0
        self.used_verbs = set()
        self.correct_in_row = 0
        
        if mode == "multi":
            self.current_team = random.choice(["blue", "red"])  # Randomize starting team
            self.prepare_team_questions()
            if not self.team_questions["blue"] and not self.team_questions["red"]:
                self.show_no_questions_error()
                return
            self.show_team_question()
        else:
            self.show_single_question()
    
    def prepare_team_questions(self):
        """Prepare questions for both teams (4 irregular, 1 regular each)"""
        self.team_questions = {"blue": [], "red": []}
        
        # Get all available irregular verbs not used yet
        available_irregular = list(set(self.irregular_verbs.keys()) - self.used_verbs)
        
        # Make sure we have enough irregular verbs
        if len(available_irregular) < 8:  # Need 8 total (4 per team)
            available_irregular = list(self.irregular_verbs.keys())
            self.used_verbs = set()
        
        # Select 4 unique irregular verbs for each team
        blue_irregular = random.sample(available_irregular, 4)
        remaining_irregular = [v for v in available_irregular if v not in blue_irregular]
        red_irregular = random.sample(remaining_irregular, 4)
        
        # Select 1 regular verb with common mistakes for each team
        available_regular = list(set(self.common_mistakes.keys()) - self.used_verbs)
        if len(available_regular) < 2:
            available_regular = list(self.common_mistakes.keys())
        
        blue_regular = random.choice(available_regular)
        available_regular.remove(blue_regular)
        red_regular = random.choice(available_regular) if available_regular else blue_regular
        
        # Combine and shuffle questions for each team
        self.team_questions["blue"] = blue_irregular + [blue_regular]
        random.shuffle(self.team_questions["blue"])
        
        self.team_questions["red"] = red_irregular + [red_regular]
        random.shuffle(self.team_questions["red"])
        
        # Mark these verbs as used
        self.used_verbs.update(blue_irregular + red_irregular + [blue_regular, red_regular])
    
    def show_no_questions_error(self):
        """Show error when no questions are available"""
        self.clear_screen()
        self.root.configure(bg="#f0f0f0")
        
        error_label = tk.Label(
            self.root,
            text="Not enough verbs available for a new game.\nPlease try again later.",
            font=self.title_font,
            bg="#f0f0f0",
            fg="red"
        )
        error_label.pack(pady=50)
        
        back_btn = tk.Button(
            self.root,
            text="Back to Main Menu",
            font=self.button_font,
            command=self.show_welcome_screen,
            bg="#2196F3",
            fg="white",
            padx=20,
            pady=10
        )
        back_btn.pack(pady=20)
    
    def show_team_question(self):
        """Display question for current team"""
        self.clear_screen()
        self.update_team_background()
        self.show_score_header()
        
        # Check if current team has questions left
        if not self.team_questions[self.current_team]:
            self.next_team_question()
            return
        
        # Get current question
        verb = self.team_questions[self.current_team][0]
        self.current_verb = verb
        
        # Determine verb type and correct answer
        if verb in self.irregular_verbs:
            correct = self.irregular_verbs[verb]
            options = self.generate_options(verb, irregular=True)
        elif verb in self.regular_verbs:
            correct = self.regular_verbs[verb]
            options = self.generate_options(verb, irregular=False)
        else:
            # Skip this verb if not found (shouldn't happen)
            self.team_questions[self.current_team].pop(0)
            self.show_team_question()
            return
        
        self.correct_answer = correct
        
        # Display team info
        team_label = tk.Label(
            self.root,
            text=f"{self.current_team.capitalize()} Team's Turn",
            font=self.title_font,
            bg=self.get_team_color()
        )
        team_label.pack(pady=20)
        
        # Display verb question
        verb_label = tk.Label(
            self.root,
            text=f"What is the past tense of: {verb}",
            font=self.verb_font,
            bg=self.get_team_color()
        )
        verb_label.pack(pady=30)
        
        # Display answer options
        for option in options:
            btn = tk.Button(
                self.root,
                text=option,
                font=self.button_font,
                command=lambda o=option: self.check_team_answer(o),
                bg="white",
                fg="black",
                padx=20,
                pady=10,
                width=15
            )
            btn.pack(pady=5)
        
        # Setup timer
        self.time_left = 10
        self.timer_running = True
        self.timer_label = tk.Label(
            self.root,
            text=f"⏱️ Time: {self.time_left}s",
            font=self.timer_font,
            bg=self.get_team_color()
        )
        self.timer_label.pack(pady=20)
        
        # Progress bar
        self.progress = tk.Canvas(self.root, width=600, height=20, bg="#ddd")
        self.progress.pack()
        self.progress_bar = self.progress.create_rectangle(0, 0, 600, 20, fill="#4CAF50")
        
        self.update_timer()
    
    def show_single_question(self):
        """Display question for single player mode"""
        self.clear_screen()
        self.root.configure(bg="#f0f0f0")
        self.show_single_header()
        
        # Get a unique verb
        verb = self.get_unique_verb()
        if verb is None:
            self.show_no_questions_error()
            return
            
        self.current_verb = verb
        
        # Determine verb type (80% irregular)
        if random.random() < 0.8 and verb in self.irregular_verbs:
            correct = self.irregular_verbs[verb]
            options = self.generate_options(verb, irregular=True)
        elif verb in self.regular_verbs:
            correct = self.regular_verbs[verb]
            options = self.generate_options(verb, irregular=False)
        else:
            # Skip this verb if not found (shouldn't happen)
            self.show_single_question()
            return
        
        self.correct_answer = correct
        
        # Display verb question
        verb_label = tk.Label(
            self.root,
            text=f"What is the past tense of: {verb}",
            font=self.verb_font,
            bg="#f0f0f0"
        )
        verb_label.pack(pady=50)
        
        # Display answer options
        for option in options:
            btn = tk.Button(
                self.root,
                text=option,
                font=self.button_font,
                command=lambda o=option: self.check_single_answer(o),
                bg="white",
                fg="black",
                padx=20,
                pady=10,
                width=15
            )
            btn.pack(pady=5)
    
    def get_unique_verb(self):
        """Get a verb that hasn't been used yet"""
        available_verbs = (
            list(set(self.irregular_verbs.keys()) - self.used_verbs) +
            list(set(self.common_mistakes.keys()) - self.used_verbs)
        )
        
        if not available_verbs:
            return None
            
        verb = random.choice(available_verbs)
        self.used_verbs.add(verb)
        return verb
    
    def generate_options(self, verb, irregular):
        """Generate answer options with common mistakes"""
        options = []
        
        if irregular:
            correct = self.irregular_verbs[verb]
            options.append(correct)
            
            # Add common mistake (just adding -ed)
            options.append(f"{verb}ed")
        else:
            correct = self.regular_verbs[verb]
            options.append(correct)
            
            # Add common mistake from our dictionary
            if verb in self.common_mistakes:
                options.append(random.choice(self.common_mistakes[verb]))
            else:
                # Generic mistake
                options.append(f"{verb}ed")
        
        # Make sure we have exactly 2 options
        options = list(set(options))
        if len(options) > 2:
            options = options[:2]
        
        return options
    
    def update_timer(self):
        """Update the timer display"""
        if self.timer_running and not self.paused:
            self.time_left -= 1
            self.timer_label.config(text=f"⏱️ Time: {self.time_left}s")
            
            # Update progress bar
            progress_width = 600 * (self.time_left / 10)
            self.progress.coords(self.progress_bar, 0, 0, progress_width, 20)
            
            # Change color when time is running out
            if self.time_left <= 3:
                self.progress.itemconfig(self.progress_bar, fill="#F44336")
            
            if self.time_left > 0:
                self.root.after(1000, self.update_timer)
            else:
                self.timer_running = False
                self.check_team_answer("")  # Time's up counts as incorrect
    
    def check_team_answer(self, answer):
        """Check answer in team mode"""
        self.timer_running = False
        
        # Remove the current question
        if self.team_questions[self.current_team]:
            self.team_questions[self.current_team].pop(0)
        
        if answer == self.correct_answer:
            self.correct_in_row += 1
            
            # Improved motivational messages
            if self.correct_in_row >= 5:
                result = "You're amazing! 5 in a row! 🌟"
            elif self.correct_in_row >= 4:
                result = "Outstanding! 4 in a row! ✨"
            elif self.correct_in_row >= 3:
                result = "Excellent! 3 in a row! 👍"
            else:
                result = "Correct!"
            
            # Fixed: Now correctly adds score to current team
            if self.current_team == "blue":
                self.blue_score += 1
            else:
                self.red_score += 1
        else:
            result = "Incorrect"
            self.correct_in_row = 0
        
        self.show_team_feedback(result)
    
    def check_single_answer(self, answer):
        """Check answer in single player mode"""
        if answer == self.correct_answer:
            result = "Correct!"
            self.blue_score += 1  # Using blue_score to track single player score
        else:
            result = "Incorrect"
        
        self.show_single_feedback(result)
    
    def show_team_feedback(self, result):
        """Show feedback after team answer"""
        self.clear_screen()
        self.update_team_background()
        self.show_score_header()
        
        # Result label
        result_label = tk.Label(
            self.root,
            text=result,
            font=self.title_font,
            bg=self.get_team_color()
        )
        result_label.pack(pady=40)
        
        # Explanation label
        explain_label = tk.Label(
            self.root,
            text=f"'{self.current_verb}' → '{self.correct_answer}'",
            font=self.verb_font,
            bg=self.get_team_color()
        )
        explain_label.pack(pady=20)
        
        # Pause button
        self.paused = False
        pause_btn = tk.Button(
            self.root,
            text="Pause (read explanation)",
            font=self.button_font,
            command=self.toggle_pause,
            bg="#FFC107",
            fg="black",
            padx=20,
            pady=10
        )
        pause_btn.pack(pady=30)
        
        # Timer for auto-continue
        self.time_left = 5
        self.timer_label = tk.Label(
            self.root,
            text=f"Continuing in: {self.time_left}s",
            font=self.timer_font,
            bg=self.get_team_color()
        )
        self.timer_label.pack(pady=20)
        
        self.update_feedback_timer()
    
    def show_single_feedback(self, result):
        """Show feedback after single player answer"""
        self.clear_screen()
        self.root.configure(bg="#f0f0f0")
        self.show_single_header()
        
        # Result label
        result_label = tk.Label(
            self.root,
            text=result,
            font=self.title_font,
            bg="#f0f0f0"
        )
        result_label.pack(pady=50)
        
        # Explanation label
        explain_label = tk.Label(
            self.root,
            text=f"The correct answer is: {self.correct_answer}",
            font=self.button_font,
            bg="#f0f0f0"
        )
        explain_label.pack(pady=20)
        
        # Next question button
        next_btn = tk.Button(
            self.root,
            text="Next Question →",
            font=self.button_font,
            command=self.next_single_question,
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10
        )
        next_btn.pack(pady=30)
        
        # End game button
        end_btn = tk.Button(
            self.root,
            text="End Game",
            font=self.button_font,
            command=self.show_final_results,
            bg="#F44336",
            fg="white",
            padx=20,
            pady=10
        )
        end_btn.pack(pady=10)
    
    def toggle_pause(self):
        """Toggle pause state on feedback screen"""
        self.paused = not self.paused
        if not self.paused:
            self.next_team_question()
    
    def update_feedback_timer(self):
        """Update timer on feedback screen"""
        if not self.paused:
            self.time_left -= 1
            self.timer_label.config(text=f"Continuing in: {self.time_left}s")
            
            if self.time_left > 0:
                self.root.after(1000, self.update_feedback_timer)
            else:
                self.next_team_question()
    
    def next_team_question(self):
        """Move to next question in team mode"""
        # Always switch teams after each question
        self.current_team = "red" if self.current_team == "blue" else "blue"
        
        # Check if current team has questions left
        if len(self.team_questions[self.current_team]) > 0:
            self.show_team_question()
        else:
            # Check if other team has questions left
            opposite_team = "red" if self.current_team == "blue" else "blue"
            if len(self.team_questions[opposite_team]) > 0:
                self.current_team = opposite_team
                self.show_team_question()
            else:
                self.show_final_results()
   
    def next_single_question(self):
        """Move to next question in single player mode"""
        self.show_single_question()
    
    def show_final_results(self):
        """Display final results"""
        self.clear_screen()
        self.root.configure(bg="#f0f0f0")
        
        # Title
        title_label = tk.Label(
            self.root,
            text="Game Results",
            font=self.title_font,
            bg="#f0f0f0"
        )
        title_label.pack(pady=40)
        
        if self.game_mode == "multi":
            # Blue team score
            blue_label = tk.Label(
                self.root,
                text=f"🔵 Blue Team: {self.blue_score}",
                font=self.timer_font,
                fg="blue",
                bg="#f0f0f0"
            )
            blue_label.pack(pady=10)
            
            # Red team score
            red_label = tk.Label(
                self.root,
                text=f"🔴 Red Team: {self.red_score}",
                font=self.timer_font,
                fg="red",
                bg="#f0f0f0"
            )
            red_label.pack(pady=10)
            
            # Winner announcement
            if self.blue_score > self.red_score:
                winner_text = "Blue Team Wins! 🎉"
                color = "blue"
            elif self.red_score > self.blue_score:
                winner_text = "Red Team Wins! 🎉"
                color = "red"
            else:
                winner_text = "It's a Tie! 🤝"
                color = "black"
            
            winner_label = tk.Label(
                self.root,
                text=winner_text,
                font=self.title_font,
                fg=color,
                bg="#f0f0f0"
            )
            winner_label.pack(pady=30)
        else:
            # Single player results
            score_label = tk.Label(
                self.root,
                text=f"Your Score: {self.blue_score}",
                font=self.title_font,
                fg="#4CAF50",
                bg="#f0f0f0"
            )
            score_label.pack(pady=30)
        
        # Play again button
        again_btn = tk.Button(
            self.root,
            text="Play Again",
            font=self.button_font,
            command=self.show_welcome_screen,
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10
        )
        again_btn.pack(pady=20)
        
        # Exit button
        exit_btn = tk.Button(
            self.root,
            text="Exit",
            font=self.button_font,
            command=self.root.quit,
            bg="#F44336",
            fg="white",
            padx=20,
            pady=10
        )
        exit_btn.pack(pady=10)
    
    def show_score_header(self):
        """Display score header in team mode"""
        header = tk.Frame(self.root, bg=self.get_team_color())
        header.pack(fill="x", pady=10)
        
        blue_score = tk.Label(
            header,
            text=f"🔵 Blue: {self.blue_score}",
            font=self.score_font,
            fg="white",
            bg="blue",
            padx=20
        )
        blue_score.pack(side="left", padx=20)
        
        timer_space = tk.Label(
            header,
            text="",
            font=self.score_font,
            bg=self.get_team_color()
        )
        timer_space.pack(side="left", expand=True)
        
        red_score = tk.Label(
            header,
            text=f"🔴 Red: {self.red_score}",
            font=self.score_font,
            fg="white",
            bg="red",
            padx=20
        )
        red_score.pack(side="right", padx=20)
    
    def show_single_header(self):
        """Display header in single player mode"""
        header = tk.Frame(self.root, bg="#f0f0f0")
        header.pack(fill="x", pady=10)
        
        score_label = tk.Label(
            header,
            text=f"Your Score: {self.blue_score}",
            font=self.score_font,
            bg="#f0f0f0"
        )
        score_label.pack(side="left", padx=20)
        
        end_btn = tk.Button(
            header,
            text="End Game",
            font=self.button_font,
            command=self.show_final_results,
            bg="#F44336",
            fg="white",
            padx=10
        )
        end_btn.pack(side="right", padx=20)
    
    def get_team_color(self):
        """Get background color for current team"""
        return "#2196F3" if self.current_team == "blue" else "#F44336"
    
    def update_team_background(self):
        """Update background to team color"""
        self.root.configure(bg=self.get_team_color())
    
    def clear_screen(self):
        """Remove all widgets from screen"""
        for widget in self.root.winfo_children():
            widget.destroy()

# Run the game
if __name__ == "__main__":
    root = tk.Tk()
    game = VerbGame(root)
    root.mainloop()