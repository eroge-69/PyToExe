import tkinter as tk
from tkinter import messagebox, Frame, Label, Button, Entry, Scale, Checkbutton, StringVar, IntVar, BooleanVar
import random
import time
import threading
import json
import os

class LegendQuizGame:

    def award_point(self):
        self.score += 1
        try:
            if self.current_country in self.difficulty_results:
                if self.current_difficulty in self.difficulty_results[self.current_country]:
                    self.difficulty_results[self.current_country][self.current_difficulty]["score"] = self.score
            self.save_scores()
        except Exception:
            pass


    def load_scores(self):
        if os.path.exists("scores.json"):
            try:
                with open("scores.json", "r", encoding="utf-8") as f:
                    self.difficulty_results = json.load(f)
            except Exception:
                pass

    def save_scores(self):
        try:
            with open("scores.json", "w", encoding="utf-8") as f:
                json.dump(self.difficulty_results, f)
        except Exception:
            pass

    def __init__(self, root):
        self.root = root
        self.root.title("Legend Quiz Game")
        self.root.geometry("1200x800")
        self.root.resizable(False, False)
        self.root.configure(bg="black")
        
        self.load_scores()
        # Game variables
        self.sound_volume = 50
        self.mods_enabled = False
        self.nightmare_unlocked = True # Changed to False initially
        self.meme_unlocked = True
        self.fullscreen_enabled = False
        
        # Track completed difficulties and scores
        self.difficulty_results = {
            "Tunisia": {"Easy": {"completed": False, "score": 0, "total_questions": 0},
                        "Normal": {"completed": False, "score": 0, "total_questions": 0},
                        "Hard": {"completed": False, "score": 0, "total_questions": 0},
                        "Insane": {"completed": False, "score": 0, "total_questions": 0},
                        "Impossible": {"completed": False, "score": 0, "total_questions": 0},
                        "Nightmare": {"completed": False, "score": 0, "total_questions": 0}},
            "Japan": {"Easy": {"completed": False, "score": 0, "total_questions": 0},
                      "Normal": {"completed": False, "score": 0, "total_questions": 0},
                      "Hard": {"completed": False, "score": 0, "total_questions": 0},
                      "Insane": {"completed": False, "score": 0, "total_questions": 0},
                      "Impossible": {"completed": False, "score": 0, "total_questions": 0},
                      "Nightmare": {"completed": False, "score": 0, "total_questions": 0}},
            "Mexico": {"Easy": {"completed": False, "score": 0, "total_questions": 0},
                       "Normal": {"completed": False, "score": 0, "total_questions": 0},
                       "Hard": {"completed": False, "score": 0, "total_questions": 0},
                       "Insane": {"completed": False, "score": 0, "total_questions": 0},
                       "Impossible": {"completed": False, "score": 0, "total_questions": 0},
                       "Nightmare": {"completed": False, "score": 0, "total_questions": 0}},
            "India": {"Easy": {"completed": False, "score": 0, "total_questions": 0},
                      "Normal": {"completed": False, "score": 0, "total_questions": 0},
                      "Hard": {"completed": False, "score": 0, "total_questions": 0},
                      "Insane": {"completed": False, "score": 0, "total_questions": 0},
                      "Impossible": {"completed": False, "score": 0, "total_questions": 0},
                      "Nightmare": {"completed": False, "score": 0, "total_questions": 0}},
            "Italy": {"Easy": {"completed": False, "score": 0, "total_questions": 0},
                      "Normal": {"completed": False, "score": 0, "total_questions": 0},
                      "Hard": {"completed": False, "score": 0, "total_questions": 0},
                      "Insane": {"completed": False, "score": 0, "total_questions": 0},
                      "Impossible": {"completed": False, "score": 0, "total_questions": 0},
                      "Nightmare": {"completed": False, "score": 0, "total_questions": 0}}
        }
        
        # Game state variables
        self.current_country = ""
        self.current_difficulty = ""
        self.current_question_index = 0
        self.score = 0
        self.time_left = 0
        self.timer_id = None
        self.float_timer_id = None
        self.option_buttons = []
        self.questions_for_current_game = [] # Initialize here
        self.player1_score = 0
        self.player2_score = 0
        self.current_player = 1
        self.current_round = 0
        self.fullscreen_enabled = True
        
        # Bind F11 key for fullscreen toggle
        self.root.bind("<F11>", self.toggle_fullscreen)
        
        # Start with animated intro
        self.root.attributes("-fullscreen", self.fullscreen_enabled)
        self.show_animated_intro()

    def toggle_fullscreen(self, event=None):
        self.fullscreen_enabled = not self.fullscreen_enabled
        self.root.attributes("-fullscreen", self.fullscreen_enabled)

    def show_animated_intro(self):
        
        self.intro_frame = tk.Frame(self.root, bg="black")
        self.intro_frame.pack(fill="both", expand=True)
        
        self.intro_label = tk.Label(
            self.intro_frame, 
            text="", 
            font=("Arial", 24, "bold"), 
            fg="white", 
            bg="black"
        )
        self.intro_label.pack(expand=True)
        
        self.animate_text("Welcome to Legend Quiz Game 🧐", self.show_second_text)
    
    def animate_text(self, text, callback=None):
        self.intro_label.config(text="")
        self.animate_text_recursive(text, 0, callback)
    
    def animate_text_recursive(self, text, index, callback):
        if index < len(text):
            current_text = self.intro_label.cget("text") + text[index]
            self.intro_label.config(text=current_text)
            self.root.after(100, lambda: self.animate_text_recursive(text, index + 1, callback))
        else:
            if callback:
                self.root.after(2000, callback)
    
    def show_second_text(self):
        self.animate_text("We Hope You Like This Game", self.show_main_menu)
    
    def show_main_menu(self):
        self.clear_screen()
        self.root.configure(bg="black")
        
        title = tk.Label(
            self.root, 
            text="Legend Quiz Game 🧐", 
            font=("Arial", 36, "bold"), 
            fg="gold", 
            bg="black"
        )
        title.pack(pady=50)
        
        subtitle = tk.Label(
            self.root,
            text="Test your knowledge about the world!",
            font=("Arial", 18),
            fg="white",
            bg="black"
        )
        subtitle.pack(pady=10)
        
        buttons_frame = tk.Frame(self.root, bg="black")
        buttons_frame.pack(pady=50)
        
        single_btn = tk.Button(
            buttons_frame,
            text="Single Player",
            font=("Arial", 18, "bold"),
            width=25,
            height=2,
            bg="blue",
            fg="white",
            command=self.show_country_selection
        )
        single_btn.pack(pady=10)
        
        multi_btn = tk.Button(
            buttons_frame,
            text="Multiplayer",
            font=("Arial", 18, "bold"),
            width=25,
            height=2,
            bg="green",
            fg="white",
            command=self.show_multiplayer_menu
        )
        multi_btn.pack(pady=10)
        
        settings_btn = tk.Button(
            buttons_frame,
            text="Settings",
            font=("Arial", 18, "bold"),
            width=25,
            height=2,
            bg="orange",
            fg="white",
            command=self.show_settings
        )
        settings_btn.pack(pady=10)
        
        quit_btn = tk.Button(
            buttons_frame,
            text="Quit",
            font=("Arial", 18, "bold"),
            width=25,
            height=2,
            bg="red",
            fg="white",
            command=self.quit_game
        )
        quit_btn.pack(pady=10)

    def show_country_selection(self):
        self.clear_screen()
        self.root.configure(bg="navy")
        
        title = tk.Label(
            self.root,
            text="Choose Country",
            font=("Arial", 28, "bold"),
            fg="white",
            bg="navy"
        )
        title.pack(pady=30)
        
        countries_frame = tk.Frame(self.root, bg="navy")
        countries_frame.pack(pady=20)
        
        countries = [
            ("Tunisia 🇹🇳", "Tunisia", "red"),
            ("Japan 🇯🇵", "Japan", "crimson"),
            ("Mexico 🇲🇽", "Mexico", "green"),
            ("India 🇮🇳", "India", "orange"),
            ("Italy 🇮🇹", "Italy", "darkgreen")
        ]
        
        for display_name, country_code, color in countries:
            btn = tk.Button(
                countries_frame,
                text=display_name,
                font=("Arial", 18, "bold"),
                width=20,
                height=2,
                bg=color,
                fg="white" if color not in ["yellow", "lightgreen"] else "black",
                command=lambda c=country_code: self.select_country(c)
            )
            btn.pack(pady=10)
        
        back_btn = tk.Button(
            self.root,
            text="Back",
            font=("Arial", 16),
            bg="gray",
            fg="white",
            command=self.show_main_menu
        )
        back_btn.pack(pady=30)

    def select_country(self, country):
        self.current_country = country
        self.show_difficulty_selection()

    def show_difficulty_selection(self):
        self.clear_screen()
        self.root.configure(bg="black")
        
        title = tk.Label(
            self.root,
            text=f"Choose Difficulty - {self.current_country}",
            font=("Arial", 28, "bold"),
            fg="white",
            bg="black"
        )
        title.pack(pady=30)
        
        difficulty_frame = tk.Frame(self.root, bg="black")
        difficulty_frame.pack(pady=20)
        
        difficulties = [
            ("Easy", "Easy", "lightgreen"),
            ("Normal", "Normal", "yellow"),
            ("Hard", "Hard", "red"),
            ("Insane", "Insane", "darkred"),
            ("Impossible", "Impossible", "purple")
        ]
        
        if self.mods_enabled:
            if self.nightmare_unlocked:
                difficulties.append(("Nightmare", "Nightmare", "black"))
            if self.meme_unlocked:
                difficulties.append(("Meme", "Meme", "pink"))
        
        for display_name, difficulty_code, color in difficulties:
            btn = tk.Button(
                difficulty_frame,
                text=display_name,
                font=("Arial", 16, "bold"),
                width=30,
                height=2,
                bg=color,
                fg="white" if color not in ["yellow", "lightgreen"] else "black",
                command=lambda d=difficulty_code: self.select_difficulty_and_start_quiz(d)
            )
            btn.pack(pady=8)
        
        back_btn = tk.Button(
            self.root,
            text="Back",
            font=("Arial", 16),
            bg="gray",
            fg="white",
            command=self.show_country_selection
        )
        back_btn.pack(pady=30)

    def select_difficulty_and_start_quiz(self, difficulty):
        self.current_difficulty = difficulty
        self.current_question_index = 0
        self.score = 0
        self.load_questions()
        
        settings = self.get_difficulty_settings(self.current_difficulty)
        num_questions = settings["num_questions"]
        
        available_questions = self.all_questions[self.current_country][self.current_difficulty]
        # Ensure we don't try to get more questions than available
        if len(available_questions) < num_questions:
            num_questions = len(available_questions)
            
        self.questions_for_current_game = random.sample(available_questions, num_questions)
        
        if self.current_difficulty == "Impossible":
            self.show_impossible_question()
        elif self.current_difficulty == "Nightmare":
            self.show_nightmare_question()
        elif self.current_difficulty == "Meme":
            self.show_meme_question()
        elif self.current_difficulty == "Insane":
            self.show_crazy_question()
        else:
            self.show_next_question()

    def clear_screen(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        if hasattr(self, 'float_timer_id') and self.float_timer_id:
            self.root.after_cancel(self.float_timer_id)
            self.float_timer_id = None
        if hasattr(self, 'impossible_float_timer_id') and self.impossible_float_timer_id:
            self.root.after_cancel(self.impossible_float_timer_id)
            self.impossible_float_timer_id = None
        if hasattr(self, 'nightmare_visibility_timer_id') and self.nightmare_visibility_timer_id:
            self.root.after_cancel(self.nightmare_visibility_timer_id)
            self.nightmare_visibility_timer_id = None
        if hasattr(self, 'nightmare_question_cycle_id') and self.nightmare_question_cycle_id:
            self.root.after_cancel(self.nightmare_question_cycle_id)
            self.nightmare_question_cycle_id = None

        for widget in self.root.winfo_children():
            widget.destroy()
        self.option_buttons = []

    def quit_game(self):
        self.save_scores()
        self.root.destroy()

    def load_questions(self):
        self.all_questions = {
            "Tunisia": {
                "Easy": [
                    {"question": "What is the capital of Tunisia?", "options": ["Tunis", "Sfax", "Sousse"], "answer_index": 0},
                    {"question": "What is the official currency of Tunisia?", "options": ["Dinar", "Dirham", "Pound"], "answer_index": 0},
                    {"question": "Which sea does Tunisia overlook?", "options": ["Red Sea", "Mediterranean Sea", "Black Sea"], "answer_index": 1},
                    {"question": "What is the most famous Tunisian dish?", "options": ["Couscous", "Pizza", "Pasta"], "answer_index": 0},
                    {"question": "What is the name of the highest mountain in Tunisia?", "options": ["Jebel ech Chambi", "Jebel Boukornine", "Jebel Zaghouan"], "answer_index": 0},
                ],
                "Normal": [
                    {"question": "How many governorates are there in Tunisia?", "options": ["20", "22", "24", "26"], "answer_index": 2},
                    {"question": "Who was the first president of Tunisia?", "options": ["Habib Bourguiba", "Zine El Abidine Ben Ali", "Beji Caid Essebsi", "Mohamed Ghannouchi"], "answer_index": 0},
                    {"question": "What is the name of the famous Roman archaeological city in Tunisia?", "options": ["Carthage", "Dougga", "El Djem", "All of the above"], "answer_index": 3},
                    {"question": "In what year did Tunisia gain independence?", "options": ["1950", "1956", "1960", "1962"], "answer_index": 1},
                    {"question": "What is the name of the desert located in southern Tunisia?", "options": ["Sinai Desert", "Sahara Desert", "Negev Desert", "Rub' al Khali Desert"], "answer_index": 1},
                ],
                "Hard": [
                    {"question": "What is the name of the strait that separates Tunisia from Italy?", "options": ["Strait of Gibraltar", "Strait of Sicily", "Bab-el-Mandeb Strait", "Strait of Hormuz"], "answer_index": 1},
                    {"question": "What is the name of the Tunisian poet who wrote the national anthem?", "options": ["Aboul-Qacem Echebbi", "Mahmoud Darwish", "Nizar Qabbani", "Ahmed Shawqi"], "answer_index": 0},
                    {"question": "What is the name of the Tunisian city famous for pottery?", "options": ["Nabeul", "Kairouan", "Tozeur", "Djerba"], "answer_index": 0},
                    {"question": "What is the name of the first university in Tunisia?", "options": ["Ez-Zitouna University", "Tunis El Manar University", "University of Carthage", "University of Sousse"], "answer_index": 0},
                    {"question": "What is the name of the famous international film festival in Tunisia?", "options": ["Carthage Film Festival", "Cannes Film Festival", "Venice Film Festival", "Berlin Film Festival"], "answer_index": 0},
                    {"question": "What is the name of the first Tunisian woman to win a Nobel Prize?", "options": ["None", "Tawhida Ben Cheikh", "Radhia Haddad", "Fatima al-Fihri"], "answer_index": 0},
                    {"question": "What is the name of the battle in which the Romans finally defeated the Carthaginians?", "options": ["Battle of Zama", "Battle of Cannae", "Battle of Actium", "Battle of Thapsus"], "answer_index": 0},
                    {"question": "What is the name of the first Tunisian newspaper?", "options": ["Ar-Raid at-Tunisi", "As-Sabah", "Ash-Shourouk", "Al-Maghrib"], "answer_index": 0},
                    {"question": "What is the name of the first Tunisian political party?", "options": ["Destour Party", "Neo Destour Party", "National Action Party", "Ummah Party"], "answer_index": 0},
                    {"question": "What is the name of the first Tunisian currency after independence?", "options": ["Tunisian Franc", "Tunisian Dinar", "Tunisian Riyal", "Tunisian Lira"], "answer_index": 0},
                ],
                "Insane": [
                    {"question": "Who was the first foreign minister of Tunisia after independence?", "options": ["Habib Bourguiba", "Sadek Mokaddem", "Mongi Slim", "Bahi Ladgham"], "answer_index": 2},
                    {"question": "Who was the first Tunisian woman to hold a ministerial position?", "options": ["Fatma Zahra", "Fouzia Ben Fraj", "Naziha Zarrouk", "Radhia Haddad"], "answer_index": 2},
                    {"question": "Who was the first Tunisian to win an Olympic medal?", "options": ["Mohammed Gammoudi", "Oussama Mellouli", "Habiba Ghribi", "Mohamed Ali Klai"], "answer_index": 0},
                    {"question": "What is the name of the first Tunisian city to be listed as a UNESCO World Heritage Site?", "options": ["Carthage", "El Djem", "Kairouan", "Tunis Medina"], "answer_index": 0},
                    {"question": "Who was the first president of the Tunisian National Constituent Assembly after the revolution?", "options": ["Mustapha Ben Jaafar", "Moncef Marzouki", "Fouad Mebazaa", "Rached Ghannouchi"], "answer_index": 0},
                ],
                "Impossible": [
                    {"question": "Who was the first foreign minister of Tunisia after independence?", "options": ["Habib Bourguiba", "Sadek Mokaddem", "Mongi Slim", "Bahi Ladgham"], "answer_index": 2},
                    {"question": "Who was the first Tunisian woman to hold a ministerial position?", "options": ["Fatma Zahra", "Fouzia Ben Fraj", "Naziha Zarrouk", "Radhia Haddad"], "answer_index": 2},
                    {"question": "Who was the first Tunisian to win an Olympic medal?", "options": ["Mohammed Gammoudi", "Oussama Mellouli", "Habiba Ghribi", "Mohamed Ali Klai"], "answer_index": 0},
                    {"question": "What is the name of the first Tunisian city to be listed as a UNESCO World Heritage Site?", "options": ["Carthage", "El Djem", "Kairouan", "Tunis Medina"], "answer_index": 0},
                    {"question": "Who was the first president of the Tunisian National Constituent Assembly after the revolution?", "options": ["Mustapha Ben Jaafar", "Moncef Marzouki", "Fouad Mebazaa", "Rached Ghannouchi"], "answer_index": 0},
                ],
                "Nightmare": [
                    {"question": "Who was the first president of the Tunisian National Constituent Assembly after the revolution?", "options": ["Mustapha Ben Jaafar", "Moncef Marzouki", "Fouad Mebazaa", "Rached Ghannouchi"], "answer_indices": [0]},
                    {"question": "Who was the first Tunisian woman to hold a ministerial position?", "options": ["Fatma Zahra", "Fouzia Ben Fraj", "Naziha Zarrouk", "Radhia Haddad"], "answer_indices": [2]},
                    {"question": "Who was the first Tunisian to win an Olympic medal?", "options": ["Mohammed Gammoudi", "Oussama Mellouli", "Habiba Ghribi", "Mohamed Ali Klai"], "answer_indices": [0]},
                    {"question": "What is the name of the first Tunisian city to be listed as a UNESCO World Heritage Site?", "options": ["Carthage", "El Djem", "Kairouan", "Tunis Medina"], "answer_indices": [0]},
                    {"question": "Who was the first foreign minister of Tunisia after independence?", "options": ["Habib Bourguiba", "Sadek Mokaddem", "Mongi Slim", "Bahi Ladgham"], "answer_indices": [2]},
                ],
                "Meme": [
                    {"question": "What has an eye but cannot see?", "options": ["A needle", "A storm", "A potato", "A camera"], "answer_index": 0},
                    {"question": "What has to be broken before you can use it?", "options": ["An egg", "A secret", "A promise", "A heart"], "answer_index": 0},
                    {"question": "What is full of holes but still holds water?", "options": ["A sponge", "A net", "A sieve", "A colander"], "answer_index": 0},
                    {"question": "What question can you never answer yes to?", "options": ["Are you asleep yet?", "Are you hungry?", "Are you happy?", "Are you ready?"], "answer_index": 0},
                    {"question": "What is always in front of you but can't be seen?", "options": ["The future", "The past", "The present", "The truth"], "answer_index": 0},
                ]
            },
            "Japan": {
                "Easy": [
                    {"question": "What is the capital of Japan?", "options": ["Tokyo", "Kyoto", "Osaka"], "answer_index": 0},
                    {"question": "What is the official currency of Japan?", "options": ["Yen", "Won", "Yuan"], "answer_index": 0},
                    {"question": "What is the most famous mountain in Japan?", "options": ["Mount Fuji", "Mount Everest", "Mount Kilimanjaro"], "answer_index": 0},
                    {"question": "What is the famous Japanese dish made of rice and raw fish?", "options": ["Sushi", "Ramen", "Tempura"], "answer_index": 0},
                    {"question": "What is the name of the traditional Japanese garment?", "options": ["Kimono", "Sari", "Abaya"], "answer_index": 0},
                ],
                "Normal": [
                    {"question": "What is the name of the current Emperor of Japan?", "options": ["Naruhito", "Akihito", "Hirohito", "Meiji"], "answer_index": 0},
                    {"question": "What is the name of the Japanese martial art that focuses on throwing?", "options": ["Judo", "Karate", "Taekwondo", "Kung Fu"], "answer_index": 0},
                    {"question": "What is the national flower of Japan?", "options": ["Cherry Blossom", "Tulip", "Rose", "Lotus"], "answer_index": 0},
                    {"question": "What is the name of the Japanese city destroyed by an atomic bomb in 1945?", "options": ["Hiroshima", "Nagasaki", "Tokyo", "Osaka"], "answer_index": 0},
                    {"question": "What is the name of the high-speed train in Japan?", "options": ["Shinkansen", "Maglev", "Eurostar", "TGV"], "answer_index": 0},
                ],
                "Hard": [
                    {"question": "What is the name of the oldest Buddhist temple in Japan?", "options": ["Horyu-ji Temple", "Kinkaku-ji Temple", "Fushimi Inari-taisha", "Senso-ji Temple"], "answer_index": 0},
                    {"question": "What is the name of the Japanese poet famous for Haiku poems?", "options": ["Matsuo Bashō", "Yosa Buson", "Kobayashi Issa", "Masaoka Shiki"], "answer_index": 0},
                    {"question": "What is the Japanese art of flower arrangement called?", "options": ["Ikebana", "Origami", "Bonsai", "Sado"], "answer_index": 0},
                    {"question": "What is the name of the traditional Japanese drama that uses masks?", "options": ["Noh", "Kabuki", "Bunraku", "Kyōgen"], "answer_index": 0},
                    {"question": "What was the first capital of Japan?", "options": ["Nara", "Kyoto", "Tokyo", "Osaka"], "answer_index": 0},
                    {"question": "What is the name of the first Japanese novel?", "options": ["The Tale of Genji", "The Pillow Book", "The Heike Monogatari", "Kojiki"], "answer_index": 0},
                    {"question": "Who was the first empress to rule Japan?", "options": ["Empress Suiko", "Empress Jingū", "Empress Kōken", "Empress Meishō"], "answer_index": 0},
                    {"question": "What is the name of the first Japanese animated film in color?", "options": ["Hakuja Den", "Panda and the Magic Serpent", "Spirited Away", "Princess Mononoke"], "answer_index": 0},
                    {"question": "What is the name of the first Japanese newspaper?", "options": ["Nichi Nichi Shimbun", "Yomiuri Shimbun", "Asahi Shimbun", "Mainichi Shimbun"], "answer_index": 0},
                    {"question": "Who was the first Japanese to win a Nobel Prize?", "options": ["Yasunari Kawabata", "Kenzaburō Ōe", "Shinya Yamanaka", "Kazuo Ishiguro"], "answer_index": 0},
                ],
                "Insane": [
                    {"question": "Who was the first Japanese ambassador to the United States?", "options": ["Muragaki Norimasa", "Takezo Iwakura", "Yoshida Shigeru", "Itō Hirobumi"], "answer_index": 0},
                    {"question": "Who was the first Japanese person to go to space?", "options": ["Toyohiro Akiyama", "Mamoru Mohri", "Chiaki Mukai", "Koichi Wakata"], "answer_index": 0},
                    {"question": "Who was the first Japanese woman to hold a ministerial position?", "options": ["Kikue Yamakawa", "Masae Kasai", "Kikue Yamakawa", "Tomoko Nakamura"], "answer_index": 0},
                    {"question": "Who was the first Japanese to win a gold medal at the Winter Olympics?", "options": ["Takashi Ono", "Yuzuru Hanyu", "Masae Kasai", "Nobuo Tanaka"], "answer_index": 2},
                    {"question": "What is the name of the first Japanese city to be listed as a UNESCO World Heritage Site?", "options": ["Kyoto", "Nara", "Hiroshima", "Shirakawa-go"], "answer_index": 0},
                ],
                "Impossible": [
                    {"question": "Who was the first Japanese ambassador to the United States?", "options": ["Muragaki Norimasa", "Takezo Iwakura", "Yoshida Shigeru", "Itō Hirobumi"], "answer_index": 0},
                    {"question": "Who was the first Japanese person to go to space?", "options": ["Toyohiro Akiyama", "Mamoru Mohri", "Chiaki Mukai", "Koichi Wakata"], "answer_index": 0},
                    {"question": "Who was the first Japanese woman to hold a ministerial position?", "options": ["Kikue Yamakawa", "Masae Kasai", "Kikue Yamakawa", "Tomoko Nakamura"], "answer_index": 0},
                    {"question": "Who was the first Japanese to win a gold medal at the Winter Olympics?", "options": ["Takashi Ono", "Yuzuru Hanyu", "Masae Kasai", "Nobuo Tanaka"], "answer_index": 2},
                    {"question": "What is the name of the first Japanese city to be listed as a UNESCO World Heritage Site?", "options": ["Kyoto", "Nara", "Hiroshima", "Shirakawa-go"], "answer_index": 0},
                ],
                "Nightmare": [
                    {"question": "Which Japanese elements are considered sacred in Shinto?", "options": ["Mount Fuji", "Cherry Blossoms", "Rice Fields", "Ocean Waves", "Bamboo Forests"], "answer_indices": [0, 1, 2, 3, 4]}, # Round 1: 5 correct out of 5 displayed
                    {"question": "Which of these are traditional Japanese martial arts?", "options": ["Judo", "Karate", "Sumo", "Taekwondo", "Kung Fu", "Boxing", "Wrestling", "Fencing"], "answer_indices": [0, 1, 2]}, # Round 2: 3 correct out of 8 displayed
                    {"question": "Which is the correct Japanese writing system?", "options": ["Hiragana", "Katakana", "Kanji", "Romaji", "Hangul", "Chinese Characters", "Arabic Script", "Latin Alphabet", "Cyrillic", "Hebrew", "Thai Script", "Devanagari"], "answer_indices": [0]}, # Round 3: 1 correct out of 12 displayed
                    {"question": "Which Japanese city was the ancient capital?", "options": ["Kyoto", "Tokyo", "Osaka", "Hiroshima", "Nagoya", "Yokohama", "Kobe", "Fukuoka", "Sendai", "Sapporo", "Nara", "Kawasaki", "Saitama", "Chiba", "Shizuoka", "Kumamoto"], "answer_indices": [0]}, # Round 4: 1 correct out of 16 displayed
                    {"question": "Which is the traditional Japanese tea ceremony utensil?", "options": ["Chawan", "Chopsticks", "Fork", "Spoon", "Knife", "Plate", "Bowl", "Cup", "Glass", "Mug", "Saucer", "Tray", "Napkin", "Tablecloth", "Placemat", "Coaster", "Pitcher", "Teapot", "Kettle", "Strainer"], "answer_indices": [0]}, # Round 5: 1 correct out of 20 displayed
                ],
                "Meme": [
                    {"question": "Why can't fish play soccer?", "options": ["Because they don't have legs", "Because they live in water", "Because they don't like sports", "Because they don't have a ball"], "answer_index": 0},
                    {"question": "What has teeth but cannot eat?", "options": ["A comb", "A fork", "A saw", "A brush"], "answer_index": 0},
                    {"question": "What gets wetter the more it dries?", "options": ["A towel", "A sponge", "A cloth", "A mop"], "answer_index": 0},
                    {"question": "What has to be broken before you can use it?", "options": ["An egg", "A secret", "A promise", "A heart"], "answer_index": 0},
                    {"question": "What is always in front of you but can't be seen?", "options": ["The future", "The past", "The present", "The truth"], "answer_index": 0},
                ]
            },
            "Mexico": {
                "Easy": [
                    {"question": "What is the capital of Mexico?", "options": ["Mexico City", "Guadalajara", "Monterrey"], "answer_index": 0},
                    {"question": "What is the official currency of Mexico?", "options": ["Peso", "Dollar", "Euro"], "answer_index": 0},
                    {"question": "What is the most famous Mexican dish?", "options": ["Taco", "Burrito", "Enchilada"], "answer_index": 0},
                    {"question": "What is the official language of Mexico?", "options": ["Spanish", "English", "French"], "answer_index": 0},
                    {"question": "What is the name of the ancient civilization famous for building pyramids in Mexico?", "options": ["Maya", "Inca", "Aztec"], "answer_index": 0},
                ],
                "Normal": [
                    {"question": "What is the name of the most famous Mexican celebration held on November 1st?", "options": ["Day of the Dead", "Independence Day", "Christmas", "Easter"], "answer_index": 0},
                    {"question": "Who is the most famous Mexican artist known for her self-portraits?", "options": ["Frida Kahlo", "Diego Rivera", "José Clemente Orozco", "David Alfaro Siqueiros"], "answer_index": 0},
                    {"question": "What is the national animal of Mexico?", "options": ["Golden Eagle", "Bear", "Wolf", "Lion"], "answer_index": 0},
                    {"question": "What is the name of the most famous archaeological site in Mexico that includes the Pyramid of the Sun?", "options": ["Teotihuacan", "Chichen Itza", "Palenque", "Tulum"], "answer_index": 0},
                    {"question": "What is the national sport of Mexico?", "options": ["Charrería", "Football", "Boxing", "Baseball"], "answer_index": 0},
                ],
                "Hard": [
                    {"question": "What is the name of the longest river in Mexico?", "options": ["Rio Grande", "Colorado River", "Yukon River", "Mississippi River"], "answer_index": 0},
                    {"question": "Who was the first president of Mexico?", "options": ["Guadalupe Victoria", "Benito Juárez", "Porfirio Díaz", "Francisco Madero"], "answer_index": 0},
                    {"question": "What is the name of the Mexican city famous for silver production?", "options": ["Taxco", "Guanajuato", "San Miguel de Allende", "Oaxaca"], "answer_index": 0},
                    {"question": "What is the name of the first university in Mexico?", "options": ["National Autonomous University of Mexico", "University of Guadalajara", "University of Monterrey", "University of Puebla"], "answer_index": 0},
                    {"question": "What is the name of the famous international music festival in Mexico?", "options": ["Cervantino Festival", "Vienna Festival", "Salzburg Festival", "Edinburgh Festival"], "answer_index": 0},
                    {"question": "What is the name of the first Mexican woman to win a Nobel Prize?", "options": ["None", "Frida Kahlo", "María Teresa Torres", "Elena Poniatowska"], "answer_index": 0},
                    {"question": "What is the name of the battle that led to Mexico's independence from Spain?", "options": ["Battle of Dolores", "Battle of Puebla", "Battle of Chapultepec", "Battle of Mexico City"], "answer_index": 0},
                    {"question": "What is the name of the first Mexican newspaper?", "options": ["La Gaceta de México", "El Universal", "Excelsior", "La Jornada"], "answer_index": 0},
                    {"question": "What is the name of the first Mexican political party?", "options": ["Institutional Revolutionary Party", "National Revolutionary Party", "Constitutional Revolutionary Party", "Mexican National Revolutionary Party"], "answer_index": 0},
                    {"question": "What is the name of the first Mexican currency after independence?", "options": ["Mexican Peso", "Mexican Real", "Mexican Pound", "Mexican Dollar"], "answer_index": 0},
                ],
                "Insane": [
                    {"question": "Who was the first Mexican ambassador to the United States?", "options": ["Manuel de la Peña y Peña", "José Manuel de Herrera", "Miguel Hidalgo y Costilla", "Benito Juárez"], "answer_index": 1},
                    {"question": "Who was the first Mexican woman to hold a ministerial position?", "options": ["María Teresa Torres", "María Elena Poniatowska", "María Teresa Torres", "María Teresa Torres"], "answer_index": 0},
                    {"question": "Who was the first Mexican to win an Olympic medal?", "options": ["Humberto Mariles Cortés", "Joaquín Capilla", "Mario Vázquez Raña", "Juan Fernández"], "answer_index": 1},
                    {"question": "What is the name of the first Mexican city to be listed as a UNESCO World Heritage Site?", "options": ["Mexico City", "Puebla", "Oaxaca", "Palenque"], "answer_index": 3},
                    {"question": "Who was the first president of the Mexican National Constituent Assembly after the revolution?", "options": ["Venustiano Carranza", "Francisco Madero", "Álvaro Obregón", "Plutarco Elías Calles"], "answer_index": 0},
                ],
                "Impossible": [
                    {"question": "Who was the first Mexican ambassador to the United States?", "options": ["Manuel de la Peña y Peña", "José Manuel de Herrera", "Miguel Hidalgo y Costilla", "Benito Juárez"], "answer_index": 1},
                    {"question": "Who was the first Mexican woman to hold a ministerial position?", "options": ["María Teresa Torres", "María Elena Poniatowska", "María Teresa Torres", "María Teresa Torres"], "answer_index": 0},
                    {"question": "Who was the first Mexican to win an Olympic medal?", "options": ["Humberto Mariles Cortés", "Joaquín Capilla", "Mario Vázquez Raña", "Juan Fernández"], "answer_index": 1},
                    {"question": "What is the name of the first Mexican city to be listed as a UNESCO World Heritage Site?", "options": ["Mexico City", "Puebla", "Oaxaca", "Palenque"], "answer_index": 3},
                    {"question": "Who was the first president of the Mexican National Constituent Assembly after the revolution?", "options": ["Venustiano Carranza", "Francisco Madero", "Álvaro Obregón", "Plutarco Elías Calles"], "answer_index": 0},
                ],
                "Nightmare": [
                    {"question": "Which Mexican foods are traditional?", "options": ["Tacos", "Enchiladas", "Tamales", "Quesadillas", "Mole"], "answer_indices": [0, 1, 2, 3, 4]}, # Round 1: 5 correct out of 5 displayed
                    {"question": "Which of these are Mexican states?", "options": ["Jalisco", "Oaxaca", "Yucatan", "California", "Texas", "Florida", "Arizona", "Nevada"], "answer_indices": [0, 1, 2]}, # Round 2: 3 correct out of 8 displayed
                    {"question": "Which is the correct Mexican currency?", "options": ["Peso", "Dollar", "Euro", "Yen", "Pound", "Franc", "Real", "Bolivar", "Quetzal", "Colon", "Cordoba", "Lempira"], "answer_indices": [0]}, # Round 3: 1 correct out of 12 displayed
                    {"question": "Which Mexican civilization built Chichen Itza?", "options": ["Maya", "Aztec", "Olmec", "Zapotec", "Inca", "Cherokee", "Sioux", "Apache", "Navajo", "Iroquois", "Pueblo", "Hopi", "Zuni", "Comanche", "Shoshone", "Blackfoot"], "answer_indices": [0]}, # Round 4: 1 correct out of 16 displayed
                    {"question": "Which is the traditional Mexican dance?", "options": ["Jarabe Tapatío", "Tango", "Salsa", "Merengue", "Bachata", "Cumbia", "Reggaeton", "Flamenco", "Waltz", "Foxtrot", "Cha-cha", "Rumba", "Samba", "Bossa Nova", "Mambo", "Bolero", "Fandango", "Jota", "Sevillanas", "Sardana"], "answer_indices": [0]}, # Round 5: 1 correct out of 20 displayed
                ],
                "Meme": [
                    {"question": "What has an eye but cannot see?", "options": ["A needle", "A storm", "A potato", "A camera"], "answer_index": 0},
                    {"question": "What has to be broken before you can use it?", "options": ["An egg", "A secret", "A promise", "A heart"], "answer_index": 0},
                    {"question": "What is full of holes but still holds water?", "options": ["A sponge", "A net", "A sieve", "A colander"], "answer_index": 0},
                    {"question": "What question can you never answer yes to?", "options": ["Are you asleep yet?", "Are you hungry?", "Are you happy?", "Are you ready?"], "answer_index": 0},
                    {"question": "What is always in front of you but can't be seen?", "options": ["The future", "The past", "The present", "The truth"], "answer_index": 0},
                ]
            },
            "India": {
                "Easy": [
                    {"question": "What is the capital of India?", "options": ["New Delhi", "Mumbai", "Bengaluru"], "answer_index": 0},
                    {"question": "What is the official currency of India?", "options": ["Rupee", "Yen", "Yuan"], "answer_index": 0},
                    {"question": "What is the most famous tourist attraction in India?", "options": ["Taj Mahal", "Eiffel Tower", "Great Wall of China"], "answer_index": 0},
                    {"question": "What is the official language of India?", "options": ["Hindi", "English", "French"], "answer_index": 0},
                    {"question": "What is the name of the sacred river in India?", "options": ["Ganges River", "Nile River", "Amazon River"], "answer_index": 0},
                ],
                "Normal": [
                    {"question": "What is the largest city in India by population?", "options": ["Mumbai", "New Delhi", "Bengaluru", "Kolkata"], "answer_index": 0},
                    {"question": "What is the most popular sport in India?", "options": ["Cricket", "Football", "Hockey", "Tennis"], "answer_index": 0},
                    {"question": "What is the Indian festival that celebrates colors?", "options": ["Holi", "Diwali", "Eid al-Fitr", "Eid al-Adha"], "answer_index": 0},
                    {"question": "Who is the most famous Indian actor in Bollywood?", "options": ["Shah Rukh Khan", "Amitabh Bachchan", "Salman Khan", "Aamir Khan"], "answer_index": 0},
                    {"question": "What is the highest mountain in India?", "options": ["Kangchenjunga", "Mount Everest", "Mount Kilimanjaro", "Alps"], "answer_index": 0},
                ],
                "Hard": [
                    {"question": "What is the name of the oldest university in India?", "options": ["Nalanda University", "University of Delhi", "University of Mumbai", "University of Calcutta"], "answer_index": 0},
                    {"question": "What is the name of the Indian philosopher considered the founder of Yoga?", "options": ["Patanjali", "Gautama Buddha", "Mahatma Gandhi", "Rabindranath Tagore"], "answer_index": 0},
                    {"question": "What is the traditional Indian dance characterized by complex movements and facial expressions?", "options": ["Bharatanatyam", "Kathak", "Odissi", "Manipuri"], "answer_index": 0},
                    {"question": "What is the name of the Indian musical instrument similar to a lute?", "options": ["Sitar", "Tabla", "Harmonium", "Flute"], "answer_index": 0},
                    {"question": "Who was the first president of India?", "options": ["Rajendra Prasad", "Jawaharlal Nehru", "Sarvepalli Radhakrishnan", "Zakir Husain"], "answer_index": 0},
                    {"question": "What is the name of the first Indian woman to win a Nobel Prize?", "options": ["Mother Teresa", "Indira Gandhi", "Sarojini Naidu", "Mira Behn"], "answer_index": 0},
                    {"question": "What is the name of the battle that led to the establishment of the Mughal Empire in India?", "options": ["First Battle of Panipat", "Battle of Plassey", "Battle of Buxar", "Battle of Karnal"], "answer_index": 0},
                    {"question": "What is the name of the first Indian newspaper?", "options": ["Bengal Gazette", "The Times of India", "Hindustan Times", "The Indian Express"], "answer_index": 0},
                    {"question": "What is the name of the first Indian political party?", "options": ["Indian National Congress", "Bharatiya Janata Party", "Communist Party of India", "Congress Party"], "answer_index": 0},
                    {"question": "What is the name of the first Indian currency after independence?", "options": ["Indian Rupee", "Indian Peso", "Indian Pound", "Indian Dollar"], "answer_index": 0},
                ],
                "Insane": [
                    {"question": "Who was the first Indian ambassador to the United States?", "options": ["Asaf Ali", "Vijaya Lakshmi Pandit", "Jawaharlal Nehru", "Sarvepalli Radhakrishnan"], "answer_index": 0},
                    {"question": "Who was the first Indian to go to space?", "options": ["Rakesh Sharma", "Kalpana Chawla", "Sunita Williams", "Raja Chari"], "answer_index": 0},
                    {"question": "Who was the first Indian woman to hold a ministerial position?", "options": ["Amrit Kaur", "Indira Gandhi", "Sushma Swaraj", "Pratibha Patil"], "answer_index": 0},
                    {"question": "Who was the first Indian to win an Olympic medal?", "options": ["Norman Pritchard", "Khashaba Dadasaheb Jadhav", "Leander Paes", "Abhinav Bindra"], "answer_index": 0},
                    {"question": "What is the name of the first Indian city to be listed as a UNESCO World Heritage Site?", "options": ["Agra", "Delhi", "Mumbai", "Jaipur"], "answer_index": 0},
                ],
                "Impossible": [
                    {"question": "Who was the first Indian ambassador to the United States?", "options": ["Asaf Ali", "Vijaya Lakshmi Pandit", "Jawaharlal Nehru", "Sarvepalli Radhakrishnan"], "answer_index": 0},
                    {"question": "Who was the first Indian to go to space?", "options": ["Rakesh Sharma", "Kalpana Chawla", "Sunita Williams", "Raja Chari"], "answer_index": 0},
                    {"question": "Who was the first Indian woman to hold a ministerial position?", "options": ["Amrit Kaur", "Indira Gandhi", "Sushma Swaraj", "Pratibha Patil"], "answer_index": 0},
                    {"question": "Who was the first Indian to win an Olympic medal?", "options": ["Norman Pritchard", "Khashaba Dadasaheb Jadhav", "Leander Paes", "Abhinav Bindra"], "answer_index": 0},
                    {"question": "What is the name of the first Indian city to be listed as a UNESCO World Heritage Site?", "options": ["Agra", "Delhi", "Mumbai", "Jaipur"], "answer_index": 0},
                ],
                "Nightmare": [
                    {"question": "Which Indian festivals are celebrated with lights?", "options": ["Diwali", "Holi", "Navratri", "Eid", "Christmas"], "answer_indices": [0, 1, 2]}, # Round 1: 3 correct out of 5 displayed
                    {"question": "Which of these are major rivers in India?", "options": ["Ganges", "Yamuna", "Brahmaputra", "Nile", "Amazon", "Mississippi", "Danube", "Volga"], "answer_indices": [0, 1, 2]}, # Round 2: 3 correct out of 8 displayed
                    {"question": "Which is the correct Indian classical dance form?", "options": ["Bharatanatyam", "Kathak", "Odissi", "Ballet", "Salsa", "Hip-hop", "Tap Dance", "Breakdance", "Flamenco", "Tango", "Waltz", "Foxtrot"], "answer_indices": [0]}, # Round 3: 1 correct out of 12 displayed
                    {"question": "Which Indian city is known as the 'Silicon Valley of India'?", "options": ["Bengaluru", "Mumbai", "New Delhi", "Chennai", "Hyderabad", "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane", "Bhopal", "Visakhapatnam"], "answer_indices": [0]}, # Round 4: 1 correct out of 16 displayed
                    {"question": "Which is a traditional Indian musical instrument?", "options": ["Sitar", "Tabla", "Harmonium", "Guitar", "Piano", "Drums", "Violin", "Flute", "Trumpet", "Saxophone", "Clarinet", "Trombone", "Harp", "Accordion", "Mandolin", "Banjo", "Ukulele", "Bagpipes", "Didgeridoo", "Ocarina"], "answer_indices": [0]}, # Round 5: 1 correct out of 20 displayed
                ],
                "Meme": [
                    {"question": "What has an eye but cannot see?", "options": ["A needle", "A storm", "A potato", "A camera"], "answer_index": 0},
                    {"question": "What has to be broken before you can use it?", "options": ["An egg", "A secret", "A promise", "A heart"], "answer_index": 0},
                    {"question": "What is full of holes but still holds water?", "options": ["A sponge", "A net", "A sieve", "A colander"], "answer_index": 0},
                    {"question": "What question can you never answer yes to?", "options": ["Are you asleep yet?", "Are you hungry?", "Are you happy?", "Are you ready?"], "answer_index": 0},
                    {"question": "What is always in front of you but can't be seen?", "options": ["The future", "The past", "The present", "The truth"], "answer_index": 0},
                ]
            },
            "Italy": {
                "Easy": [
                    {"question": "What is the capital of Italy?", "options": ["Rome", "Milan", "Venice"], "answer_index": 0},
                    {"question": "What is the official currency of Italy?", "options": ["Euro", "Lira", "Dollar"], "answer_index": 0},
                    {"question": "What is the most famous tourist attraction in Italy?", "options": ["Colosseum", "Leaning Tower of Pisa", "Trevi Fountain"], "answer_index": 0},
                    {"question": "What is the official language of Italy?", "options": ["Italian", "English", "French"], "answer_index": 0},
                    {"question": "What is the famous Italian dish made of dough, sauce, and cheese?", "options": ["Pizza", "Pasta", "Lasagna"], "answer_index": 0},
                ],
                "Normal": [
                    {"question": "What is the most famous Italian city known for its canals?", "options": ["Venice", "Rome", "Milan", "Florence"], "answer_index": 0},
                    {"question": "Who is the most famous Italian artist who painted the Mona Lisa?", "options": ["Leonardo da Vinci", "Michelangelo", "Raphael", "Donatello"], "answer_index": 0},
                    {"question": "What is the most famous Italian sports car?", "options": ["Ferrari", "Lamborghini", "Maserati", "Alfa Romeo"], "answer_index": 0},
                    {"question": "What is the most famous volcanic mountain in Italy?", "options": ["Mount Vesuvius", "Mount Etna", "Stromboli", "Monte Bianco"], "answer_index": 0},
                    {"question": "What is the most popular sport in Italy?", "options": ["Football", "Basketball", "Volleyball", "Tennis"], "answer_index": 0},
                ],
                "Hard": [
                    {"question": "What is the name of the oldest university in Italy?", "options": ["University of Bologna", "Sapienza University of Rome", "University of Padua", "University of Naples Federico II"], "answer_index": 0},
                    {"question": "What is the name of the Italian philosopher considered the founder of Yoga?", "options": ["Seneca", "Cicero", "Marcus Aurelius", "Augustine"], "answer_index": 0},
                    {"question": "What is the famous Italian opera written by Verdi?", "options": ["Aida", "La Traviata", "Rigoletto", "All of the above"], "answer_index": 3},
                    {"question": "What is the name of the Italian musical instrument similar to a violin?", "options": ["Viola", "Cello", "Contrabass", "Violin"], "answer_index": 0},
                    {"question": "Who was the first president of Italy?", "options": ["Enrico De Nicola", "Luigi Einaudi", "Giovanni Gronchi", "Giuseppe Saragat"], "answer_index": 0},
                    {"question": "What is the name of the first Italian woman to win a Nobel Prize?", "options": ["Grazia Deledda", "Maria Montessori", "Rita Levi-Montalcini", "Aldo Moro"], "answer_index": 0},
                    {"question": "What is the name of the battle that led to the unification of Italy?", "options": ["Battle of Solferino", "Battle of Magenta", "Battle of Custoza", "Battle of Rome"], "answer_index": 0},
                    {"question": "What is the name of the first Italian newspaper?", "options": ["Gazzetta di Parma", "Corriere della Sera", "La Repubblica", "La Stampa"], "answer_index": 0},
                    {"question": "What is the name of the first Italian political party?", "options": ["Italian Socialist Party", "Christian Democracy", "Italian Communist Party", "National Fascist Party"], "answer_index": 0},
                    {"question": "What is the name of the first Italian currency after unification?", "options": ["Italian Lira", "Italian Franc", "Italian Pound", "Italian Dollar"], "answer_index": 0},
                ],
                "Insane": [
                    {"question": "Who was the first Italian ambassador to the United States?", "options": ["Solon Borland", "Giorgio Washington", "Giuseppe Garibaldi", "Vittorio Emanuele II"], "answer_index": 0},
                    {"question": "Who was the first Italian to go to space?", "options": ["Franco Malerba", "Umberto Guidoni", "Roberto Vittori", "Paolo Nespoli"], "answer_index": 0},
                    {"question": "Who was the first Italian woman to hold a ministerial position?", "options": ["Angelina Merlin", "Tina Anselmi", "Nilde Iotti", "Susanna Agnelli"], "answer_index": 0},
                    {"question": "Who was the first Italian to win an Olympic medal?", "options": ["Pietro Antonio Rufo", "Erminio Spalla", "Nello Pagani", "Aldo Nadal"], "answer_index": 0},
                    {"question": "What is the name of the first Italian city to be listed as a UNESCO World Heritage Site?", "options": ["Rome", "Florence", "Venice", "Naples"], "answer_index": 0},
                ],
                "Impossible": [
                    {"question": "Who was the first Italian ambassador to the United States?", "options": ["Solon Borland", "Giorgio Washington", "Giuseppe Garibaldi", "Vittorio Emanuele II"], "answer_index": 0},
                    {"question": "Who was the first Italian to go to space?", "options": ["Franco Malerba", "Umberto Guidoni", "Roberto Vittori", "Paolo Nespoli"], "answer_index": 0},
                    {"question": "Who was the first Italian woman to hold a ministerial position?", "options": ["Angelina Merlin", "Tina Anselmi", "Nilde Iotti", "Susanna Agnelli"], "answer_index": 0},
                    {"question": "Who was the first Italian to win an Olympic medal?", "options": ["Pietro Antonio Rufo", "Erminio Spalla", "Nello Pagani", "Aldo Nadal"], "answer_index": 0},
                    {"question": "What is the name of the first Italian city to be listed as a UNESCO World Heritage Site?", "options": ["Rome", "Florence", "Venice", "Naples"], "answer_index": 0},
                ],
                "Nightmare": [
                    {"question": "Which Italian cities are known for their art and architecture?", "options": ["Rome", "Florence", "Venice", "Milan", "Naples"], "answer_indices": [0, 1, 2, 3, 4]}, # Round 1: 5 correct out of 5 displayed
                    {"question": "Which of these are famous Italian dishes?", "options": ["Pizza", "Pasta", "Lasagna", "Sushi", "Taco", "Curry", "Hamburger", "Hot Dog"], "answer_indices": [0, 1, 2]}, # Round 2: 3 correct out of 8 displayed
                    {"question": "Which is the correct Italian car brand?", "options": ["Ferrari", "Lamborghini", "Maserati", "Fiat", "Alfa Romeo", "Porsche", "BMW", "Mercedes-Benz", "Audi", "Volkswagen", "Toyota", "Honda"], "answer_indices": [0]}, # Round 3: 1 correct out of 12 displayed
                    {"question": "Which Italian landmark is a leaning tower?", "options": ["Leaning Tower of Pisa", "Colosseum", "Trevi Fountain", "Duomo di Milano", "St. Peter's Basilica", "Pantheon", "Vatican City", "Sistine Chapel", "Pompeii", "Herculaneum", "Mount Vesuvius", "Lake Como", "Amalfi Coast", "Cinque Terre", "Dolomites", "Sardinia"], "answer_indices": [0]}, # Round 4: 1 correct out of 16 displayed
                    {"question": "Which is a traditional Italian opera composer?", "options": ["Giuseppe Verdi", "Giacomo Puccini", "Gioachino Rossini", "Wolfgang Amadeus Mozart", "Ludwig van Beethoven", "Johann Sebastian Bach", "George Frideric Handel", "Franz Schubert", "Robert Schumann", "Johannes Brahms", "Pyotr Ilyich Tchaikovsky", "Richard Wagner", "Claude Debussy", "Maurice Ravel", "Igor Stravinsky", "Sergei Rachmaninoff", "Dmitri Shostakovich", "Béla Bartók", "Arnold Schoenberg", "Alban Berg"], "answer_indices": [0]}, # Round 5: 1 correct out of 20 displayed
                ],
                "Meme": [
                    {"question": "What has an eye but cannot see?", "options": ["A needle", "A storm", "A potato", "A camera"], "answer_index": 0},
                    {"question": "What has to be broken before you can use it?", "options": ["An egg", "A secret", "A promise", "A heart"], "answer_index": 0},
                    {"question": "What is full of holes but still holds water?", "options": ["A sponge", "A net", "A sieve", "A colander"], "answer_index": 0},
                    {"question": "What question can you never answer yes to?", "options": ["Are you asleep yet?", "Are you hungry?", "Are you happy?", "Are you ready?"], "answer_index": 0},
                    {"question": "What is always in front of you but can't be seen?", "options": ["The future", "The past", "The present", "The truth"], "answer_index": 0},
                ]
            },
            "Japan": {
                "Easy": [
                    {"question": "What is the capital of Japan?", "options": ["Tokyo", "Kyoto", "Osaka"], "answer_index": 0},
                    {"question": "What is the official currency of Japan?", "options": ["Yen", "Won", "Yuan"], "answer_index": 0},
                    {"question": "What is the most famous mountain in Japan?", "options": ["Mount Fuji", "Mount Everest", "Mount Kilimanjaro"], "answer_index": 0},
                    {"question": "What is the famous Japanese dish made of rice and raw fish?", "options": ["Sushi", "Ramen", "Tempura"], "answer_index": 0},
                    {"question": "What is the name of the traditional Japanese garment?", "options": ["Kimono", "Sari", "Abaya"], "answer_index": 0},
                ],
                "Normal": [
                    {"question": "What is the name of the current Emperor of Japan?", "options": ["Naruhito", "Akihito", "Hirohito", "Meiji"], "answer_index": 0},
                    {"question": "What is the name of the Japanese martial art that focuses on throwing?", "options": ["Judo", "Karate", "Taekwondo", "Kung Fu"], "answer_index": 0},
                    {"question": "What is the national flower of Japan?", "options": ["Cherry Blossom", "Tulip", "Rose", "Lotus"], "answer_index": 0},
                    {"question": "What is the name of the Japanese city destroyed by an atomic bomb in 1945?", "options": ["Hiroshima", "Nagasaki", "Tokyo", "Osaka"], "answer_index": 0},
                    {"question": "What is the name of the high-speed train in Japan?", "options": ["Shinkansen", "Maglev", "Eurostar", "TGV"], "answer_index": 0},
                ],
                "Hard": [
                    {"question": "What is the name of the oldest Buddhist temple in Japan?", "options": ["Horyu-ji Temple", "Kinkaku-ji Temple", "Fushimi Inari-taisha", "Senso-ji Temple"], "answer_index": 0},
                    {"question": "What is the name of the Japanese poet famous for Haiku poems?", "options": ["Matsuo Bashō", "Yosa Buson", "Kobayashi Issa", "Masaoka Shiki"], "answer_index": 0},
                    {"question": "What is the Japanese art of flower arrangement called?", "options": ["Ikebana", "Origami", "Bonsai", "Sado"], "answer_index": 0},
                    {"question": "What is the name of the traditional Japanese drama that uses masks?", "options": ["Noh", "Kabuki", "Bunraku", "Kyōgen"], "answer_index": 0},
                    {"question": "What was the first capital of Japan?", "options": ["Nara", "Kyoto", "Tokyo", "Osaka"], "answer_index": 0},
                    {"question": "What is the name of the first Japanese novel?", "options": ["The Tale of Genji", "The Pillow Book", "The Heike Monogatari", "Kojiki"], "answer_index": 0},
                    {"question": "Who was the first empress to rule Japan?", "options": ["Empress Suiko", "Empress Jingū", "Empress Kōken", "Empress Meishō"], "answer_index": 0},
                    {"question": "What is the name of the first Japanese animated film in color?", "options": ["Hakuja Den", "Panda and the Magic Serpent", "Spirited Away", "Princess Mononoke"], "answer_index": 0},
                    {"question": "What is the name of the first Japanese newspaper?", "options": ["Nichi Nichi Shimbun", "Yomiuri Shimbun", "Asahi Shimbun", "Mainichi Shimbun"], "answer_index": 0},
                    {"question": "Who was the first Japanese to win a Nobel Prize?", "options": ["Yasunari Kawabata", "Kenzaburō Ōe", "Shinya Yamanaka", "Kazuo Ishiguro"], "answer_index": 0},
                ],
                "Insane": [
                    {"question": "Who was the first Japanese ambassador to the United States?", "options": ["Muragaki Norimasa", "Takezo Iwakura", "Yoshida Shigeru", "Itō Hirobumi"], "answer_index": 0},
                    {"question": "Who was the first Japanese person to go to space?", "options": ["Toyohiro Akiyama", "Mamoru Mohri", "Chiaki Mukai", "Koichi Wakata"], "answer_index": 0},
                    {"question": "Who was the first Japanese woman to hold a ministerial position?", "options": ["Kikue Yamakawa", "Masae Kasai", "Kikue Yamakawa", "Tomoko Nakamura"], "answer_index": 0},
                    {"question": "Who was the first Japanese to win a gold medal at the Winter Olympics?", "options": ["Takashi Ono", "Yuzuru Hanyu", "Masae Kasai", "Nobuo Tanaka"], "answer_index": 2},
                    {"question": "What is the name of the first Japanese city to be listed as a UNESCO World Heritage Site?", "options": ["Kyoto", "Nara", "Hiroshima", "Shirakawa-go"], "answer_index": 0},
                ],
                "Impossible": [
                    {"question": "Who was the first Japanese ambassador to the United States?", "options": ["Muragaki Norimasa", "Takezo Iwakura", "Yoshida Shigeru", "Itō Hirobumi"], "answer_index": 0},
                    {"question": "Who was the first Japanese person to go to space?", "options": ["Toyohiro Akiyama", "Mamoru Mohri", "Chiaki Mukai", "Koichi Wakata"], "answer_index": 0},
                    {"question": "Who was the first Japanese woman to hold a ministerial position?", "options": ["Kikue Yamakawa", "Masae Kasai", "Kikue Yamakawa", "Tomoko Nakamura"], "answer_index": 0},
                    {"question": "Who was the first Japanese to win a gold medal at the Winter Olympics?", "options": ["Takashi Ono", "Yuzuru Hanyu", "Masae Kasai", "Nobuo Tanaka"], "answer_index": 2},
                    {"question": "What is the name of the first Japanese city to be listed as a UNESCO World Heritage Site?", "options": ["Kyoto", "Nara", "Hiroshima", "Shirakawa-go"], "answer_index": 0},
                ],
                "Meme": [
                    {"question": "Why can't fish play soccer?", "options": ["Because they don't have legs", "Because they live in water", "Because they don't like sports", "Because they don't have a ball"], "answer_index": 0},
                    {"question": "What has teeth but cannot eat?", "options": ["A comb", "A fork", "A saw", "A brush"], "answer_index": 0},
                    {"question": "What gets wetter the more it dries?", "options": ["A towel", "A sponge", "A cloth", "A mop"], "answer_index": 0},
                    {"question": "What has to be broken before you can use it?", "options": ["An egg", "A secret", "A promise", "A heart"], "answer_index": 0},
                    {"question": "What is always in front of you but can't be seen?", "options": ["The future", "The past", "The present", "The truth"], "answer_index": 0},
                ]
            },
            "Mexico": {
                "Easy": [
                    {"question": "What is the capital of Mexico?", "options": ["Mexico City", "Guadalajara", "Monterrey"], "answer_index": 0},
                    {"question": "What is the official currency of Mexico?", "options": ["Peso", "Dollar", "Euro"], "answer_index": 0},
                    {"question": "What is the most famous Mexican dish?", "options": ["Taco", "Burrito", "Enchilada"], "answer_index": 0},
                    {"question": "What is the official language of Mexico?", "options": ["Spanish", "English", "French"], "answer_index": 0},
                    {"question": "What is the name of the ancient civilization famous for building pyramids in Mexico?", "options": ["Maya", "Inca", "Aztec"], "answer_index": 0},
                ],
                "Normal": [
                    {"question": "What is the name of the most famous Mexican celebration held on November 1st?", "options": ["Day of the Dead", "Independence Day", "Christmas", "Easter"], "answer_index": 0},
                    {"question": "Who is the most famous Mexican artist known for her self-portraits?", "options": ["Frida Kahlo", "Diego Rivera", "José Clemente Orozco", "David Alfaro Siqueiros"], "answer_index": 0},
                    {"question": "What is the national animal of Mexico?", "options": ["Golden Eagle", "Bear", "Wolf", "Lion"], "answer_index": 0},
                    {"question": "What is the name of the most famous archaeological site in Mexico that includes the Pyramid of the Sun?", "options": ["Teotihuacan", "Chichen Itza", "Palenque", "Tulum"], "answer_index": 0},
                    {"question": "What is the national sport of Mexico?", "options": ["Charrería", "Football", "Boxing", "Baseball"], "answer_index": 0},
                ],
                "Hard": [
                    {"question": "What is the name of the longest river in Mexico?", "options": ["Rio Grande", "Colorado River", "Yukon River", "Mississippi River"], "answer_index": 0},
                    {"question": "Who was the first president of Mexico?", "options": ["Guadalupe Victoria", "Benito Juárez", "Porfirio Díaz", "Francisco Madero"], "answer_index": 0},
                    {"question": "What is the name of the Mexican city famous for silver production?", "options": ["Taxco", "Guanajuato", "San Miguel de Allende", "Oaxaca"], "answer_index": 0},
                    {"question": "What is the name of the first university in Mexico?", "options": ["National Autonomous University of Mexico", "University of Guadalajara", "University of Monterrey", "University of Puebla"], "answer_index": 0},
                    {"question": "What is the name of the famous international music festival in Mexico?", "options": ["Cervantino Festival", "Vienna Festival", "Salzburg Festival", "Edinburgh Festival"], "answer_index": 0},
                    {"question": "What is the name of the first Mexican woman to win a Nobel Prize?", "options": ["None", "Frida Kahlo", "María Teresa Torres", "Elena Poniatowska"], "answer_index": 0},
                    {"question": "What is the name of the battle that led to Mexico's independence from Spain?", "options": ["Battle of Dolores", "Battle of Puebla", "Battle of Chapultepec", "Battle of Mexico City"], "answer_index": 0},
                    {"question": "What is the name of the first Mexican newspaper?", "options": ["La Gaceta de México", "El Universal", "Excelsior", "La Jornada"], "answer_index": 0},
                    {"question": "What is the name of the first Mexican political party?", "options": ["Institutional Revolutionary Party", "National Revolutionary Party", "Constitutional Revolutionary Party", "Mexican National Revolutionary Party"], "answer_index": 0},
                    {"question": "What is the name of the first Mexican currency after independence?", "options": ["Mexican Peso", "Mexican Real", "Mexican Pound", "Mexican Dollar"], "answer_index": 0},
                ],
                "Insane": [
                    {"question": "Who was the first Mexican ambassador to the United States?", "options": ["Manuel de la Peña y Peña", "José Manuel de Herrera", "Miguel Hidalgo y Costilla", "Benito Juárez"], "answer_index": 1},
                    {"question": "Who was the first Mexican woman to hold a ministerial position?", "options": ["María Teresa Torres", "María Elena Poniatowska", "María Teresa Torres", "María Teresa Torres"], "answer_index": 0},
                    {"question": "Who was the first Mexican to win an Olympic medal?", "options": ["Humberto Mariles Cortés", "Joaquín Capilla", "Mario Vázquez Raña", "Juan Fernández"], "answer_index": 1},
                    {"question": "What is the name of the first Mexican city to be listed as a UNESCO World Heritage Site?", "options": ["Mexico City", "Puebla", "Oaxaca", "Palenque"], "answer_index": 3},
                    {"question": "Who was the first president of the Mexican National Constituent Assembly after the revolution?", "options": ["Venustiano Carranza", "Francisco Madero", "Álvaro Obregón", "Plutarco Elías Calles"], "answer_index": 0},
                ],
                "Impossible": [
                    {"question": "Who was the first Mexican ambassador to the United States?", "options": ["Manuel de la Peña y Peña", "José Manuel de Herrera", "Miguel Hidalgo y Costilla", "Benito Juárez"], "answer_index": 1},
                    {"question": "Who was the first Mexican woman to hold a ministerial position?", "options": ["María Teresa Torres", "María Elena Poniatowska", "María Teresa Torres", "María Teresa Torres"], "answer_index": 0},
                    {"question": "Who was the first Mexican to win an Olympic medal?", "options": ["Humberto Mariles Cortés", "Joaquín Capilla", "Mario Vázquez Raña", "Juan Fernández"], "answer_index": 1},
                    {"question": "What is the name of the first Mexican city to be listed as a UNESCO World Heritage Site?", "options": ["Mexico City", "Puebla", "Oaxaca", "Palenque"], "answer_index": 3},
                    {"question": "Who was the first president of the Mexican National Constituent Assembly after the revolution?", "options": ["Venustiano Carranza", "Francisco Madero", "Álvaro Obregón", "Plutarco Elías Calles"], "answer_index": 0},
                ],
                "Meme": [
                    {"question": "What has an eye but cannot see?", "options": ["A needle", "A storm", "A potato", "A camera"], "answer_index": 0},
                    {"question": "What has to be broken before you can use it?", "options": ["An egg", "A secret", "A promise", "A heart"], "answer_index": 0},
                    {"question": "What is full of holes but still holds water?", "options": ["A sponge", "A net", "A sieve", "A colander"], "answer_index": 0},
                    {"question": "What question can you never answer yes to?", "options": ["Are you asleep yet?", "Are you hungry?", "Are you happy?", "Are you ready?"], "answer_index": 0},
                    {"question": "What is always in front of you but can't be seen?", "options": ["The future", "The past", "The present", "The truth"], "answer_index": 0},
                ]
            },
            "India": {
                "Easy": [
                    {"question": "What is the capital of India?", "options": ["New Delhi", "Mumbai", "Bengaluru"], "answer_index": 0},
                    {"question": "What is the official currency of India?", "options": ["Rupee", "Yen", "Yuan"], "answer_index": 0},
                    {"question": "What is the most famous tourist attraction in India?", "options": ["Taj Mahal", "Eiffel Tower", "Great Wall of China"], "answer_index": 0},
                    {"question": "What is the official language of India?", "options": ["Hindi", "English", "French"], "answer_index": 0},
                    {"question": "What is the name of the sacred river in India?", "options": ["Ganges River", "Nile River", "Amazon River"], "answer_index": 0},
                ],
                "Normal": [
                    {"question": "What is the largest city in India by population?", "options": ["Mumbai", "New Delhi", "Bengaluru", "Kolkata"], "answer_index": 0},
                    {"question": "What is the most popular sport in India?", "options": ["Cricket", "Football", "Hockey", "Tennis"], "answer_index": 0},
                    {"question": "What is the Indian festival that celebrates colors?", "options": ["Holi", "Diwali", "Eid al-Fitr", "Eid al-Adha"], "answer_index": 0},
                    {"question": "Who is the most famous Indian actor in Bollywood?", "options": ["Shah Rukh Khan", "Amitabh Bachchan", "Salman Khan", "Aamir Khan"], "answer_index": 0},
                    {"question": "What is the highest mountain in India?", "options": ["Kangchenjunga", "Mount Everest", "Mount Kilimanjaro", "Alps"], "answer_index": 0},
                ],
                "Hard": [
                    {"question": "What is the name of the oldest university in India?", "options": ["Nalanda University", "University of Delhi", "University of Mumbai", "University of Calcutta"], "answer_index": 0},
                    {"question": "What is the name of the Indian philosopher considered the founder of Yoga?", "options": ["Patanjali", "Gautama Buddha", "Mahatma Gandhi", "Rabindranath Tagore"], "answer_index": 0},
                    {"question": "What is the traditional Indian dance characterized by complex movements and facial expressions?", "options": ["Bharatanatyam", "Kathak", "Odissi", "Manipuri"], "answer_index": 0},
                    {"question": "What is the name of the Indian musical instrument similar to a lute?", "options": ["Sitar", "Tabla", "Harmonium", "Flute"], "answer_index": 0},
                    {"question": "Who was the first president of India?", "options": ["Rajendra Prasad", "Jawaharlal Nehru", "Sarvepalli Radhakrishnan", "Zakir Husain"], "answer_index": 0},
                    {"question": "What is the name of the first Indian woman to win a Nobel Prize?", "options": ["Mother Teresa", "Indira Gandhi", "Sarojini Naidu", "Mira Behn"], "answer_index": 0},
                    {"question": "What is the name of the battle that led to the establishment of the Mughal Empire in India?", "options": ["First Battle of Panipat", "Battle of Plassey", "Battle of Buxar", "Battle of Karnal"], "answer_index": 0},
                    {"question": "What is the name of the first Indian newspaper?", "options": ["Bengal Gazette", "The Times of India", "Hindustan Times", "The Indian Express"], "answer_index": 0},
                    {"question": "What is the name of the first Indian political party?", "options": ["Indian National Congress", "Bharatiya Janata Party", "Communist Party of India", "Congress Party"], "answer_index": 0},
                    {"question": "What is the name of the first Indian currency after independence?", "options": ["Indian Rupee", "Indian Peso", "Indian Pound", "Indian Dollar"], "answer_index": 0},
                ],
                "Insane": [
                    {"question": "Who was the first Indian ambassador to the United States?", "options": ["Asaf Ali", "Vijaya Lakshmi Pandit", "Jawaharlal Nehru", "Sarvepalli Radhakrishnan"], "answer_index": 0},
                    {"question": "Who was the first Indian to go to space?", "options": ["Rakesh Sharma", "Kalpana Chawla", "Sunita Williams", "Raja Chari"], "answer_index": 0},
                    {"question": "Who was the first Indian woman to hold a ministerial position?", "options": ["Amrit Kaur", "Indira Gandhi", "Sushma Swaraj", "Pratibha Patil"], "answer_index": 0},
                    {"question": "Who was the first Indian to win an Olympic medal?", "options": ["Norman Pritchard", "Khashaba Dadasaheb Jadhav", "Leander Paes", "Abhinav Bindra"], "answer_index": 0},
                    {"question": "What is the name of the first Indian city to be listed as a UNESCO World Heritage Site?", "options": ["Agra", "Delhi", "Mumbai", "Jaipur"], "answer_index": 0},
                ],
                "Impossible": [
                    {"question": "Who was the first Indian ambassador to the United States?", "options": ["Asaf Ali", "Vijaya Lakshmi Pandit", "Jawaharlal Nehru", "Sarvepalli Radhakrishnan"], "answer_index": 0},
                    {"question": "Who was the first Indian to go to space?", "options": ["Rakesh Sharma", "Kalpana Chawla", "Sunita Williams", "Raja Chari"], "answer_index": 0},
                    {"question": "Who was the first Indian woman to hold a ministerial position?", "options": ["Amrit Kaur", "Indira Gandhi", "Sushma Swaraj", "Pratibha Patil"], "answer_index": 0},
                    {"question": "Who was the first Indian to win an Olympic medal?", "options": ["Norman Pritchard", "Khashaba Dadasaheb Jadhav", "Leander Paes", "Abhinav Bindra"], "answer_index": 0},
                    {"question": "What is the name of the first Indian city to be listed as a UNESCO World Heritage Site?", "options": ["Agra", "Delhi", "Mumbai", "Jaipur"], "answer_index": 0},
                ],
                "Meme": [
                    {"question": "What has an eye but cannot see?", "options": ["A needle", "A storm", "A potato", "A camera"], "answer_index": 0},
                    {"question": "What has to be broken before you can use it?", "options": ["An egg", "A secret", "A promise", "A heart"], "answer_index": 0},
                    {"question": "What is full of holes but still holds water?", "options": ["A sponge", "A net", "A sieve", "A colander"], "answer_index": 0},
                    {"question": "What question can you never answer yes to?", "options": ["Are you asleep yet?", "Are you hungry?", "Are you happy?", "Are you ready?"], "answer_index": 0},
                    {"question": "What is always in front of you but can't be seen?", "options": ["The future", "The past", "The present", "The truth"], "answer_index": 0},
                ]
            },
            "Italy": {
                "Easy": [
                    {"question": "What is the capital of Italy?", "options": ["Rome", "Milan", "Venice"], "answer_index": 0},
                    {"question": "What is the official currency of Italy?", "options": ["Euro", "Lira", "Dollar"], "answer_index": 0},
                    {"question": "What is the most famous tourist attraction in Italy?", "options": ["Colosseum", "Leaning Tower of Pisa", "Trevi Fountain"], "answer_index": 0},
                    {"question": "What is the official language of Italy?", "options": ["Italian", "English", "French"], "answer_index": 0},
                    {"question": "What is the famous Italian dish made of dough, sauce, and cheese?", "options": ["Pizza", "Pasta", "Lasagna"], "answer_index": 0},
                ],
                "Normal": [
                    {"question": "What is the most famous Italian city known for its canals?", "options": ["Venice", "Rome", "Milan", "Florence"], "answer_index": 0},
                    {"question": "Who is the most famous Italian artist who painted the Mona Lisa?", "options": ["Leonardo da Vinci", "Michelangelo", "Raphael", "Donatello"], "answer_index": 0},
                    {"question": "What is the most famous Italian sports car?", "options": ["Ferrari", "Lamborghini", "Maserati", "Alfa Romeo"], "answer_index": 0},
                    {"question": "What is the most famous volcanic mountain in Italy?", "options": ["Mount Vesuvius", "Mount Etna", "Stromboli", "Monte Bianco"], "answer_index": 0},
                    {"question": "What is the most popular sport in Italy?", "options": ["Football", "Basketball", "Volleyball", "Tennis"], "answer_index": 0},
                ],
                "Hard": [
                    {"question": "What is the name of the oldest university in Italy?", "options": ["University of Bologna", "Sapienza University of Rome", "University of Padua", "University of Naples Federico II"], "answer_index": 0},
                    {"question": "What is the name of the Italian philosopher considered the founder of Yoga?", "options": ["Seneca", "Cicero", "Marcus Aurelius", "Augustine"], "answer_index": 0},
                    {"question": "What is the famous Italian opera written by Verdi?", "options": ["Aida", "La Traviata", "Rigoletto", "All of the above"], "answer_index": 3},
                    {"question": "What is the name of the Italian musical instrument similar to a violin?", "options": ["Viola", "Cello", "Contrabass", "Violin"], "answer_index": 0},
                    {"question": "Who was the first president of Italy?", "options": ["Enrico De Nicola", "Luigi Einaudi", "Giovanni Gronchi", "Giuseppe Saragat"], "answer_index": 0},
                    {"question": "What is the name of the first Italian woman to win a Nobel Prize?", "options": ["Grazia Deledda", "Maria Montessori", "Rita Levi-Montalcini", "Aldo Moro"], "answer_index": 0},
                    {"question": "What is the name of the battle that led to the unification of Italy?", "options": ["Battle of Solferino", "Battle of Magenta", "Battle of Custoza", "Battle of Rome"], "answer_index": 0},
                    {"question": "What is the name of the first Italian newspaper?", "options": ["Gazzetta di Parma", "Corriere della Sera", "La Repubblica", "La Stampa"], "answer_index": 0},
                    {"question": "What is the name of the first Italian political party?", "options": ["Italian Socialist Party", "Christian Democracy", "Italian Communist Party", "National Fascist Party"], "answer_index": 0},
                    {"question": "What is the name of the first Italian currency after unification?", "options": ["Italian Lira", "Italian Franc", "Italian Pound", "Italian Dollar"], "answer_index": 0},
                ],
                "Insane": [
                    {"question": "Who was the first Italian ambassador to the United States?", "options": ["Solon Borland", "Giorgio Washington", "Giuseppe Garibaldi", "Vittorio Emanuele II"], "answer_index": 0},
                    {"question": "Who was the first Italian to go to space?", "options": ["Franco Malerba", "Umberto Guidoni", "Roberto Vittori", "Paolo Nespoli"], "answer_index": 0},
                    {"question": "Who was the first Italian woman to hold a ministerial position?", "options": ["Angelina Merlin", "Tina Anselmi", "Nilde Iotti", "Susanna Agnelli"], "answer_index": 0},
                    {"question": "Who was the first Italian to win an Olympic medal?", "options": ["Pietro Antonio Rufo", "Erminio Spalla", "Nello Pagani", "Aldo Nadal"], "answer_index": 0},
                    {"question": "What is the name of the first Italian city to be listed as a UNESCO World Heritage Site?", "options": ["Rome", "Florence", "Venice", "Naples"], "answer_index": 0},
                ],
                "Impossible": [
                    {"question": "Who was the first Italian ambassador to the United States?", "options": ["Solon Borland", "Giorgio Washington", "Giuseppe Garibaldi", "Vittorio Emanuele II"], "answer_index": 0},
                    {"question": "Who was the first Italian to go to space?", "options": ["Franco Malerba", "Umberto Guidoni", "Roberto Vittori", "Paolo Nespoli"], "answer_index": 0},
                    {"question": "Who was the first Italian woman to hold a ministerial position?", "options": ["Angelina Merlin", "Tina Anselmi", "Nilde Iotti", "Susanna Agnelli"], "answer_index": 0},
                    {"question": "Who was the first Italian to win an Olympic medal?", "options": ["Pietro Antonio Rufo", "Erminio Spalla", "Nello Pagani", "Aldo Nadal"], "answer_index": 0},
                    {"question": "What is the name of the first Italian city to be listed as a UNESCO World Heritage Site?", "options": ["Rome", "Florence", "Venice", "Naples"], "answer_index": 0},
                ],
                "Meme": [
                    {"question": "What has an eye but cannot see?", "options": ["A needle", "A storm", "A potato", "A camera"], "answer_index": 0},
                    {"question": "What has to be broken before you can use it?", "options": ["An egg", "A secret", "A promise", "A heart"], "answer_index": 0},
                    {"question": "What is full of holes but still holds water?", "options": ["A sponge", "A net", "A sieve", "A colander"], "answer_index": 0},
                    {"question": "What question can you never answer yes to?", "options": ["Are you asleep yet?", "Are you hungry?", "Are you happy?", "Are you ready?"], "answer_index": 0},
                    {"question": "What is always in front of you but can't be seen?", "options": ["The future", "The past", "The present", "The truth"], "answer_index": 0},
                ]
            },
        }

    def get_difficulty_settings(self, difficulty):
        settings = {
            "Easy": {"num_questions": 5, "num_options": 3, "time": 20},
            "Normal": {"num_questions": 8, "num_options": 4, "time": 15},
            "Hard": {"num_questions": 12, "num_options": 5, "time": 12},
            "Insane": {"num_questions": 16, "num_options": 6, "time": 10},
            "Impossible": {"num_questions": 20, "num_options": 7, "time": 8},
            "Nightmare": {"num_questions": 20, "num_options": 7, "time": 6},
            "Meme": {"num_questions": 10, "num_options": 2, "time": float("inf")}
        }
        return settings.get(difficulty, settings["Normal"])

    def show_next_question(self):
        if self.current_question_index >= len(self.questions_for_current_game):
            self.show_result()
            return
            
        self.clear_screen()
        self.root.configure(bg="black")
        
        question_data = self.questions_for_current_game[self.current_question_index]
        question_text = question_data["question"]
        options = question_data["options"]
        self.correct_answer_index = question_data["answer_index"]
        
        # Shuffle options to prevent fixed correct answer position
        shuffled_options_with_indices = list(enumerate(options))
        random.shuffle(shuffled_options_with_indices)
        
        # Store original options for Hard mode shuffling
        self.original_options = options.copy()
        self.shuffled_options_with_indices = shuffled_options_with_indices.copy()
        
        # Timer
        self.time_left = self.get_difficulty_settings(self.current_difficulty)["time"]
        self.timer_label = tk.Label(
            self.root,
            text=f"Time Left: {self.time_left}",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="black"
        )
        self.timer_label.pack(pady=10)
        
        # Display question
        q_label = tk.Label(
            self.root,
            text=question_text,
            font=("Arial", 22, "bold"),
            fg="white",
            bg="black",
            wraplength=700
        )
        q_label.pack(pady=30)
        
        options_frame = tk.Frame(self.root, bg="black")
        options_frame.pack(pady=20)
        
        self.option_buttons = []
        
        for i, (original_index, option_text) in enumerate(shuffled_options_with_indices):
            display_text = option_text
            
            btn = tk.Button(
                options_frame,
                text=display_text,
                font=("Arial", 16),
                width=40,
                height=2,
                bg="gray",
                fg="white",
                command=lambda idx=original_index: self.check_answer(idx)
            )
            btn.pack(pady=5)
            self.option_buttons.append(btn)
        
        self.start_timer()
        
        # Start text shuffling for Hard mode
        if self.current_difficulty == "Hard":
            self.start_hard_text_shuffle()

    def start_hard_text_shuffle(self):
        """Shuffle button texts every 2 seconds for Hard mode"""
        if hasattr(self, 'hard_shuffle_timer_id') and self.hard_shuffle_timer_id:
            self.root.after_cancel(self.hard_shuffle_timer_id)

        def shuffle_texts():
            if not hasattr(self, 'option_buttons') or not self.option_buttons:
                return
            
            # Get current texts from buttons
            current_texts = [btn.cget("text") for btn in self.option_buttons]
            
            # Shuffle the texts
            random.shuffle(current_texts)
            
            # Apply shuffled texts to buttons
            for i, btn in enumerate(self.option_buttons):
                btn.config(text=current_texts[i])
            
            # Schedule next shuffle
            self.hard_shuffle_timer_id = self.root.after(2000, shuffle_texts)
        
        # Start shuffling after 2 seconds
        self.hard_shuffle_timer_id = self.root.after(2000, shuffle_texts)

    def start_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        
        if self.time_left == float("inf"): # Meme mode
            self.timer_label.config(text="Time Left: Infinite")
            return
            
        if self.time_left > 0:
            self.timer_label.config(text=f"Time Left: {self.time_left}")
            self.time_left -= 1
            self.timer_id = self.root.after(1000, self.start_timer)
        else:
            self.check_answer(timeout=True)

    def check_answer(self, selected_index=None, timeout=False):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
            
        for btn in self.option_buttons:
            btn.config(state="disabled")
            
        is_correct = False
        if not timeout and selected_index == self.correct_answer_index:
            is_correct = True
            self.score += 1
            
        result_text = "Correct! 🎉" if is_correct else "Wrong! ❌"
        if timeout:
            result_text = "Time's Up! ⏰"
            
        result_label = tk.Label(
            self.root,
            text=result_text,
            font=("Arial", 20, "bold"),
            fg="green" if is_correct else "red",
            bg="black"
        )
        result_label.pack(pady=20)
        
        correct_option_text = self.questions_for_current_game[self.current_question_index]["options"][self.correct_answer_index]
        correct_answer_label = tk.Label(
            self.root,
            text=f"Correct Answer: {correct_option_text}",
            font=("Arial", 16),
            fg="gold",
            bg="black"
        )
        correct_answer_label.pack(pady=10)
        
        next_btn = tk.Button(
            self.root,
            text="Next",
            font=("Arial", 16),
            bg="blue",
            fg="white",
            command=self.advance_to_next_question
        )
        next_btn.pack(pady=30)

    def advance_to_next_question(self):
        self.current_question_index += 1
        if self.current_question_index >= len(self.questions_for_current_game):
            self.show_result()
        else:
            if self.current_difficulty == "Impossible":
                self.show_impossible_question()
            elif self.current_difficulty == "Nightmare":
                self.show_nightmare_question()
            elif self.current_difficulty == "Meme":
                self.show_meme_question()
            elif self.current_difficulty == "Insane":
                self.show_crazy_question()
            else:
                self.show_next_question()

    def show_result(self):
        self.clear_screen()
        self.root.configure(bg="black")
        
        total_questions = len(self.questions_for_current_game)
        percentage = (self.score / total_questions) * 100 if total_questions > 0 else 0
        
        comment = ""
        if percentage >= 95:
            stars = 10
            comment = "Great Job! You can become "
        elif percentage >= 90:
            stars = 9
            comment = "أداء أسطوري! لكن هل يمكنك فعلها مرة أخرى؟ 🤔"
        elif percentage >= 80:
            stars = 8
            comment = "ممتاز! لكن لا تظن أنك أسطورة بعد! 😉"
        elif percentage >= 70:
            stars = 7
            comment = "جيد جداً! لكن يبدو أنك بحاجة لبعض الدراسة الإضافية! 🤓"
        elif percentage >= 60:
            stars = 6
            comment = "ma7soub jibt essid min widhnoo 🤷‍♀️"
        elif percentage >= 50:
            stars = 5
            comment = "Atleast you passed,Maybe try again."
        elif percentage >= 40:
            stars = 4
            comment = "Go Back To Daycare.You Smol Gremlin"
        elif percentage >= 30:
            stars = 3
            comment = "Not even close to average. Get better bozo"
        elif percentage >= 20:
            stars = 2
            comment = "My grandma got all 10 Stars. So get better."
        elif percentage >= 10:
            stars = 1
            comment = "A Unborn Chicken did better than you!"
        else:
            stars = 0
            comment = "Unalive yourself you piece of crap"
            
        result_text = f"Your Score: {self.score}/{total_questions}\n\n"
        star_emoji = "\u2B50"
        empty_star_emoji = "\u2606"
        result_text += f"Stars: {star_emoji * stars}{empty_star_emoji * (10 - stars)}\n\n"
        result_text += comment
        
        result_label = tk.Label(
            self.root,
            text=result_text,
            font=("Arial", 20, "bold"),
            fg="white",
            bg="black",
            wraplength=700
        )
        result_label.pack(pady=50)
        
        if self.current_difficulty != "Meme": # Meme mode doesn't affect completion status
            self.difficulty_results[self.current_country][self.current_difficulty]["completed"] = True
            self.difficulty_results[self.current_country][self.current_difficulty]["score"] = self.score
            self.difficulty_results[self.current_country][self.current_difficulty]["total_questions"] = total_questions
            self.check_for_unlocks()
            
        menu_btn = tk.Button(
            self.root,
            text="Main Menu",
            font=("Arial", 16),
            bg="blue",
            fg="white",
            command=self.show_main_menu
        )
        menu_btn.pack(pady=30)

    def check_for_unlocks(self):
        # Check for Nightmare unlock (50% correct rate across all Impossible difficulties)
        total_impossible_questions = 0
        achieved_impossible_score = 0
        for country in self.difficulty_results:
            data = self.difficulty_results[country]["Impossible"]
            total_impossible_questions += data["total_questions"]
            achieved_impossible_score += data["score"]
        
        impossible_percentage = (achieved_impossible_score / total_impossible_questions) * 100 if total_impossible_questions > 0 else 0

        if impossible_percentage >= 50 and not self.nightmare_unlocked:
            self.nightmare_unlocked = True
            messagebox.showinfo("Nightmare Unlocked!", "Congratulations! You've achieved 50% or more in all Impossible difficulties! Nightmare mode is now unlocked in Settings!")
        
        # New logic for Meme mode unlock: all difficulties completed and 50% correct rate across all difficulties
        all_difficulties_completed = True
        total_possible_score = 0
        achieved_score = 0
        
        for country in self.difficulty_results:
            for difficulty_name, data in self.difficulty_results[country].items():
                if difficulty_name != "Meme": # Exclude Meme mode itself from completion check
                    if not data["completed"]:
                        all_difficulties_completed = False
                        break
                    total_possible_score += data["total_questions"]
                    achieved_score += data["score"]
            if not all_difficulties_completed:
                break
        
        overall_percentage = (achieved_score / total_possible_score) * 100 if total_possible_score > 0 else 0
        
        if all_difficulties_completed and overall_percentage >= 50 and not self.meme_unlocked:
            self.meme_unlocked = True
            messagebox.showinfo("Meme Unlocked!", "Congratulations! You've completed all difficulties with an overall 50% correct rate! Meme Mode is now unlocked in Settings!")

    def show_settings(self):
        self.clear_screen()
        self.root.configure(bg="darkgray")
        
        title = tk.Label(
            self.root,
            text="Settings",
            font=("Arial", 28, "bold"),
            fg="white",
            bg="darkgray"
        )
        title.pack(pady=30)
        
        volume_label = tk.Label(
            self.root,
            text=f"Volume: {self.sound_volume}%",
            font=("Arial", 18),
            fg="white",
            bg="darkgray"
        )
        volume_label.pack(pady=15)
        
        volume_slider = tk.Scale(
            self.root,
            from_=0, to=100,
            orient=tk.HORIZONTAL,
            length=300,
            bg="lightgray",
            fg="black",
            command=lambda val: self.update_volume(val, volume_label)
        )
        volume_slider.set(self.sound_volume)
        volume_slider.pack(pady=10)
        
        mods_frame = tk.Frame(self.root, bg="darkgray")
        mods_frame.pack(pady=20)
        
        mods_label = tk.Label(
            mods_frame,
            text="Enable Special Modes (Mods)",
            font=("Arial", 18),
            fg="white",
            bg="darkgray"
        )
        mods_label.pack(side=tk.LEFT, padx=10)
        
        self.mods_enabled_var = tk.BooleanVar(value=self.mods_enabled)
        mods_checkbox = tk.Checkbutton(
            mods_frame,
            text="Enable",
            variable=self.mods_enabled_var,
            command=self.toggle_mods,
            font=("Arial", 16),
            bg="darkgray",
            fg="white",
            selectcolor="green"
        )
        mods_checkbox.pack(side=tk.LEFT)
        
        nightmare_status = "Unlocked" if self.nightmare_unlocked else "Locked"
        meme_status = "Unlocked" if self.meme_unlocked else "Locked"
        status_text = f"Nightmare Mode: {nightmare_status}\n"
        status_text += f"Meme Mode: {meme_status}"
        status_label = tk.Label(
            self.root,
            text=status_text,
            font=("Arial", 14),
            fg="lightblue",
            bg="darkgray"
        )
        status_label.pack(pady=10)
        
        fullscreen_frame = tk.Frame(self.root, bg="darkgray")
        fullscreen_frame.pack(pady=20)
        
        fullscreen_label = tk.Label(
            fullscreen_frame,
            text="Fullscreen Mode",
            font=("Arial", 18),
            fg="white",
            bg="darkgray"
        )
        fullscreen_label.pack(side=tk.LEFT, padx=10)
        
        self.fullscreen_var = tk.BooleanVar(value=self.fullscreen_enabled)
        fullscreen_checkbox = tk.Checkbutton(
            fullscreen_frame,
            text="Enable",
            variable=self.fullscreen_var,
            command=self.toggle_fullscreen_from_settings,
            font=("Arial", 16),
            bg="darkgray",
            fg="white",
            selectcolor="green"
        )
        fullscreen_checkbox.pack(side=tk.LEFT)
        
        back_btn = tk.Button(
            self.root,
            text="Back",
            font=("Arial", 16),
            bg="gray",
            fg="white",
            command=self.show_main_menu
        )
        back_btn.pack(pady=30)

    def toggle_fullscreen_from_settings(self):
        self.fullscreen_enabled = self.fullscreen_var.get()
        self.root.attributes("-fullscreen", self.fullscreen_enabled)

    def update_volume(self, val, label):
        self.sound_volume = int(val)
        label.config(text=f"Volume: {self.sound_volume}%")

    def toggle_mods(self):
        self.mods_enabled = self.mods_enabled_var.get()
        if not self.mods_enabled:
            messagebox.showinfo("Alert", "Special modes disabled. They will not appear in the difficulty list.")
        else:
            messagebox.showinfo("Alert", "Special modes enabled. They will appear in the difficulty list if unlocked.")
        self.show_settings()

    def show_developers_screen(self):
        self.clear_screen()
        self.root.configure(bg="black")
        
        dev_label = tk.Label(
            self.root,
            text="Thank you for playing Legend Quiz Game!\n\nDevelopers:\nAdam Haje\nMoemen Sahraoui\n\nSpecial Thanks to:\nomaima and gomycode",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="black",
            wraplength=700
        )
        dev_label.pack(pady=100)
        
        self.root.after(5000, self.show_main_menu)

    def show_multiplayer_menu(self):
        self.clear_screen()
        self.root.configure(bg="darkblue")
        
        title = tk.Label(
            self.root,
            text="Multiplayer Mode",
            font=("Arial", 28, "bold"),
            fg="white",
            bg="darkblue"
        )
        title.pack(pady=30)
        
        players_frame = tk.Frame(self.root, bg="darkblue")
        players_frame.pack(pady=20)
        
        p1_label = tk.Label(
            players_frame,
            text="Player 1 Name:",
            font=("Arial", 18),
            fg="white",
            bg="darkblue"
        )
        p1_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.player1_name_entry = tk.Entry(
            players_frame,
            font=("Arial", 16),
            width=20
        )
        self.player1_name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        p2_label = tk.Label(
            players_frame,
            text="Player 2 Name:",
            font=("Arial", 18),
            fg="white",
            bg="darkblue"
        )
        p2_label.grid(row=1, column=0, padx=10, pady=10)
        
        self.player2_name_entry = tk.Entry(
            players_frame,
            font=("Arial", 16),
            width=20
        )
        self.player2_name_entry.grid(row=1, column=1, padx=10, pady=10)
        
        rounds_label = tk.Label(
            self.root,
            text="Number of Rounds:",
            font=("Arial", 18),
            fg="white",
            bg="darkblue"
        )
        rounds_label.pack(pady=10)
        
        self.rounds_var = tk.IntVar(value=5)
        rounds_frame = tk.Frame(self.root, bg="darkblue")
        rounds_frame.pack(pady=10)
        
        for rounds in [3, 5, 7, 10]:
            rounds_btn = tk.Button(
                rounds_frame,
                text=str(rounds),
                font=("Arial", 16),
                width=5,
                bg="lightblue",
                fg="black",
                command=lambda r=rounds: self.select_rounds(r)
            )
            rounds_btn.pack(side=tk.LEFT, padx=5)
        
        start_btn = tk.Button(
            self.root,
            text="Start Game",
            font=("Arial", 18, "bold"),
            bg="green",
            fg="white",
            command=self.start_multiplayer_game
        )
        start_btn.pack(pady=30)
        
        back_btn = tk.Button(
            self.root,
            text="Back",
            font=("Arial", 16),
            bg="gray",
            fg="white",
            command=self.show_main_menu
        )
        back_btn.pack(pady=20)

    def select_rounds(self, rounds):
        self.rounds_var.set(rounds)

    def start_multiplayer_game(self):
        player1_name = self.player1_name_entry.get().strip()
        player2_name = self.player2_name_entry.get().strip()
        
        if not player1_name or not player2_name:
            messagebox.showerror("Error", "Please enter both player names!")
            return
            
        if player1_name == player2_name:
            messagebox.showerror("Error", "Player names must be different!")
            return
            
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.total_rounds = self.rounds_var.get()
        self.current_round = 0
        self.player1_score = 0
        self.player2_score = 0
        self.current_player = 1
        
        self.load_questions()
        self.show_multiplayer_round()

    def show_multiplayer_round(self):
        if self.current_round >= self.total_rounds:
            self.show_multiplayer_results()
            return
            
        self.current_round += 1
        
        countries = list(self.all_questions.keys())
        self.current_country = random.choice(countries)
        
        if self.current_round <= 2:
            difficulty = "Easy"
        elif self.current_round <= 4:
            difficulty = "Normal"
        elif self.current_round <= 6:
            difficulty = "Hard"
        elif self.current_round <= 8:
            difficulty = "Insane"
        else:
            difficulty = "Impossible"
            
        self.current_difficulty = difficulty
        
        available_questions = self.all_questions[self.current_country][self.current_difficulty]
        self.current_question = random.choice(available_questions)
        
        self.show_multiplayer_question()

    def show_multiplayer_question(self):
        # Destroy all widgets from the previous round before creating new ones
        for widget in self.root.winfo_children():
            widget.destroy()
        self.option_buttons = [] # Clear the list of option buttons

        self.root.configure(bg="darkblue")
        
        # Create main container with grid layout
        main_frame = tk.Frame(self.root, bg="darkblue")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configure grid weights for responsive layout
        main_frame.grid_columnconfigure(0, weight=3)  # Question area (left side)
        main_frame.grid_columnconfigure(1, weight=1)  # Details area (right side)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Left side: Question and answers
        question_frame = tk.Frame(main_frame, bg="darkblue")
        question_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        # Question text (smaller size)
        question_text = self.current_question["question"]
        q_label = tk.Label(
            question_frame,
            text=question_text,
            font=("Arial", 18, "bold"),  # Reduced from 22
            fg="white",
            bg="darkblue",
            wraplength=600  # Reduced from 700
        )
        q_label.pack(pady=(0, 20))
        
        # Options frame
        options_frame = tk.Frame(question_frame, bg="darkblue")
        options_frame.pack(fill="both", expand=True)
        
        self.option_buttons = []
        options = self.current_question["options"]
        self.correct_answer_index = self.current_question["answer_index"]
        
        # Shuffle options to prevent fixed correct answer position
        shuffled_options_with_indices = list(enumerate(options))
        random.shuffle(shuffled_options_with_indices)

        for i, (original_index, option_text) in enumerate(shuffled_options_with_indices):
            btn = tk.Button(
                options_frame,
                text=option_text,
                font=("Arial", 14),  # Reduced from 16
                width=35,  # Reduced from 40
                height=2,
                bg="lightblue",
                fg="black",
                command=lambda idx=original_index: self.check_multiplayer_answer(idx)
            )
            btn.pack(pady=3)  # Reduced from 5
            self.option_buttons.append(btn)
        
        # Right side: Game details
        details_frame = tk.Frame(main_frame, bg="navy", relief="raised", bd=2)
        details_frame.grid(row=0, column=1, sticky="nsew")
        
        # Details title
        details_title = tk.Label(
            details_frame,
            text="Game Info",
            font=("Arial", 16, "bold"),
            fg="gold",
            bg="navy"
        )
        details_title.pack(pady=(10, 20))
        
        # Round info
        round_info = tk.Label(
            details_frame,
            text=f"Round {self.current_round}/{self.total_rounds}",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="navy"
        )
        round_info.pack(pady=5)
        
        # Country and difficulty
        location_info = tk.Label(
            details_frame,
            text=f"{self.current_country}\n{self.current_difficulty}",
            font=("Arial", 12),
            fg="lightblue",
            bg="navy",
            justify="center"
        )
        location_info.pack(pady=5)
        
        # Separator
        separator = tk.Frame(details_frame, height=2, bg="gold")
        separator.pack(fill="x", padx=10, pady=10)
        
        # Scores
        scores_title = tk.Label(
            details_frame,
            text="Scores",
            font=("Arial", 14, "bold"),
            fg="gold",
            bg="navy"
        )
        scores_title.pack(pady=(0, 10))
        
        player1_score_label = tk.Label(
            details_frame,
            text=f"{self.player1_name}: {self.player1_score}",
            font=("Arial", 12),
            fg="lightgreen" if self.current_player == 1 else "white",
            bg="navy"
        )
        player1_score_label.pack(pady=2)
        
        player2_score_label = tk.Label(
            details_frame,
            text=f"{self.player2_name}: {self.player2_score}",
            font=("Arial", 12),
            fg="lightgreen" if self.current_player == 2 else "white",
            bg="navy"
        )
        player2_score_label.pack(pady=2)
        
        # Current player turn
        current_player_name = self.player1_name if self.current_player == 1 else self.player2_name
        turn_label = tk.Label(
            details_frame,
            text=f"Turn: {current_player_name}",
            font=("Arial", 14, "bold"),
            fg="lightgreen",
            bg="navy"
        )
        turn_label.pack(pady=(20, 10))
        
        # Timer
        settings = self.get_difficulty_settings(self.current_difficulty)
        self.time_left = settings["time"]
        self.timer_label = tk.Label(
            details_frame,
            text=f"Time: {self.time_left}",
            font=("Arial", 16, "bold"),
            fg="yellow",
            bg="navy"
        )
        self.timer_label.pack(pady=10)
            
        self.start_multiplayer_timer()

    def start_multiplayer_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        
        if self.time_left > 0:
            self.timer_label.config(text=f"Time Left: {self.time_left}")
            self.time_left -= 1
            self.timer_id = self.root.after(1000, self.start_multiplayer_timer)
        else:
            self.check_multiplayer_answer(timeout=True)

    def check_multiplayer_answer(self, selected_index=None, timeout=False):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
            
        for btn in self.option_buttons:
            btn.config(state="disabled")
            
        is_correct = False
        if not timeout and selected_index == self.correct_answer_index:
            is_correct = True
            if self.current_player == 1:
                self.player1_score += 1
            else:
                self.player2_score += 1
                
        current_player_name = self.player1_name if self.current_player == 1 else self.player2_name
        
        if timeout:
            result_text = f"انتهى الوقت! {current_player_name} لم يجب في الوقت المناسب ⏰"
            result_color = "orange"
        elif is_correct:
            result_text = f"صحيح! {current_player_name} يسجل نقطة! 🎉"
            result_color = "green"
        else:
            result_text = f"خطأ! {current_player_name} لا يسجل نقطة ❌"
            result_color = "red"
        
        # Create a result popup frame in the center
        result_popup = tk.Frame(self.root, bg="white", relief="raised", bd=3)
        result_popup.place(relx=0.5, rely=0.5, anchor="center")
        
        result_label = tk.Label(
            result_popup,
            text=result_text,
            font=("Arial", 16, "bold"),
            fg=result_color,
            bg="white",
            padx=20,
            pady=10
        )
        result_label.pack()
        
        correct_option_text = self.current_question["options"][self.correct_answer_index]
        correct_answer_label = tk.Label(
            result_popup,
            text=f"Correct Answer: {correct_option_text}",
            font=("Arial", 14),
            fg="darkblue",
            bg="white",
            padx=20,
            pady=5
        )
        correct_answer_label.pack()
        
        # Next button in the popup
        next_round_btn = tk.Button(
            result_popup,
            text="Next Round",
            font=("Arial", 14),
            bg="blue",
            fg="white",
            padx=20,
            pady=5,
            command=lambda: [result_popup.destroy(), self.advance_multiplayer_round()]
        )
        next_round_btn.pack(pady=10)

    def advance_multiplayer_round(self):
        # Toggle player for the next round
        self.current_player = 1 if self.current_player == 2 else 2
        # Simply call show_multiplayer_round which will handle clearing the screen
        self.show_multiplayer_round()

    def show_multiplayer_results(self):
        self.clear_screen()
        self.root.configure(bg="darkblue")
        
        title = tk.Label(
            self.root,
            text="Match Results",
            font=("Arial", 28, "bold"),
            fg="white",
            bg="darkblue"
        )
        title.pack(pady=30)
        
        results_text = f"{self.player1_name}: {self.player1_score} points\n"
        results_text += f"{self.player2_name}: {self.player2_score} points\n\n"
        
        if self.player1_score > self.player2_score:
            winner = self.player1_name
            results_text += f"🏆 الفائز: {winner}! (يبدو أن {self.player2_name} بحاجة إلى دروس خصوصية!)"
        elif self.player2_score > self.player1_score:
            winner = self.player2_name
            results_text += f"🏆 الفائز: {winner}! (لا تقلق يا {self.player1_name}، هناك دائماً ألعاب أخرى لتخسرها!)"
        else:
            results_text += "🤝 تعادل! كلاكما رائع... أو سيء بنفس القدر! 🤷‍♂️ (على الأقل لم يخسر أحد بشكل فظيع!)"
        
        results_label = tk.Label(
            self.root,
            text=results_text,
            font=("Arial", 20, "bold"),
            fg="white",
            bg="darkblue",
            wraplength=700
        )
        results_label.pack(pady=50)
        
        buttons_frame = tk.Frame(self.root, bg="darkblue")
        buttons_frame.pack(pady=30)
        
        play_again_btn = tk.Button(
            buttons_frame,
            text="Play Again",
            font=("Arial", 16),
            bg="green",
            fg="white",
            command=self.show_multiplayer_menu
        )
        play_again_btn.pack(side=tk.LEFT, padx=10)
        
        menu_btn = tk.Button(
            buttons_frame,
            text="Main Menu",
            font=("Arial", 16),
            bg="blue",
            fg="white",
            command=self.show_main_menu
        )
        menu_btn.pack(side=tk.LEFT, padx=10)

    def show_impossible_question(self):
        if self.current_question_index >= len(self.questions_for_current_game):
            self.show_result()
            return
            
        self.clear_screen()
        self.root.configure(bg="purple")
        
        question_data = self.questions_for_current_game[self.current_question_index]
        question_text = question_data["question"]
        options = question_data["options"]
        self.correct_answer_index = question_data["answer_index"]
        
        self.time_left = self.get_difficulty_settings(self.current_difficulty)["time"]
        self.timer_label = tk.Label(
            self.root,
            text=f"Time Left: {self.time_left}",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="purple"
        )
        self.timer_label.pack(pady=10)
        
        self.q_label = tk.Label(
            self.root,
            text=question_text,
            font=("Arial", 22, "bold"),
            fg="white",
            bg="purple",
            wraplength=700
        )
        self.q_label.pack(pady=30)
        
        self.options_frame = tk.Frame(self.root, bg="purple")
        self.options_frame.pack(fill="both", expand=True)
        
        self.option_buttons = []
        self.current_options = options.copy()
        
        # Shuffle options to prevent fixed correct answer position
        shuffled_options_with_indices = list(enumerate(self.current_options))
        random.shuffle(shuffled_options_with_indices)

        for i, (original_index, option_text) in enumerate(shuffled_options_with_indices):
            btn = tk.Button(
                self.options_frame,
                text=option_text, # Display full text
                font=("Arial", 16, "bold"),
                width=40,
                height=2,
                bg="gray",
                fg="white",
                command=lambda idx=original_index: self.check_answer(idx)
            )
            self.option_buttons.append(btn)
            
        self.start_timer()
        self.start_impossible_float_options()

    def start_impossible_float_options(self):
        if hasattr(self, 'impossible_float_timer_id') and self.impossible_float_timer_id:
            self.root.after_cancel(self.impossible_float_timer_id)

        def float_options():
            for btn in self.option_buttons:
                btn_width = btn.winfo_width()
                btn_height = btn.winfo_height()

                # Ensure the window is updated to get correct width/height
                self.root.update_idletasks()
                root_width = self.root.winfo_width()
                root_height = self.root.winfo_height()

                # Calculate new random position within bounds
                # Ensure buttons stay within the visible area and don't overlap with timer/question labels
                center_x = root_width / 2
                center_y = root_height / 2

                # Define a smaller central area for button movement
                # Adjust these values to control how close to the center they stay
                movement_range_x = 200  # pixels around center_x
                movement_range_y = 150  # pixels around center_y

                min_x = int(center_x - movement_range_x / 2)
                max_x = int(center_x + movement_range_x / 2 - btn_width)
                min_y = int(center_y - movement_range_y / 2)
                max_y = int(center_y + movement_range_y / 2 - btn_height)

                # Ensure boundaries are still valid
                if max_x < min_x: max_x = min_x
                if max_y < min_y: max_y = min_y

                new_x = random.randint(min_x, max_x)
                new_y = random.randint(min_y, max_y)

                btn.place(x=new_x, y=new_y)
            self.impossible_float_timer_id = self.root.after(200, float_options)
        float_options() # Start immediately

    def show_nightmare_question(self):
        if self.current_question_index >= len(self.questions_for_current_game):
            self.show_result()
            return
            
        self.clear_screen()
        self.root.configure(bg="darkred")
        
        question_data = self.questions_for_current_game[self.current_question_index]
        question_text = question_data["question"]
        options = question_data["options"]
        self.correct_answer_indices = question_data["answer_indices"] # Changed to indices for multiple correct answers
        
        # Determine current Nightmare round (1-5)
        self.nightmare_round = (self.current_question_index // 1) + 1 # Each question is a new round for now
        if self.nightmare_round > 5: # Cap at 5 rounds
            self.nightmare_round = 5

        num_options_to_display = 4
        num_correct_answers = 1
        options_per_row = 4
        button_width = 20
        button_font_size = 16

        if self.nightmare_round == 1:
            num_options_to_display = 5
            num_correct_answers = 5 # All correct
            options_per_row = 5
            button_width = 15
            button_font_size = 14
        elif self.nightmare_round == 2:
            num_options_to_display = 8
            num_correct_answers = 3
            options_per_row = 4
            button_width = 20
            button_font_size = 14
        elif self.nightmare_round == 3:
            num_options_to_display = 12
            num_correct_answers = 1
            options_per_row = 4
            button_width = 20
            button_font_size = 12
        elif self.nightmare_round == 4:
            num_options_to_display = 16
            num_correct_answers = 1
            options_per_row = 4
            button_width = 20
            button_font_size = 12
        elif self.nightmare_round == 5:
            num_options_to_display = 20
            num_correct_answers = 1
            options_per_row = 5
            button_width = 15
            button_font_size = 10

        # Ensure we have enough options to display
        if len(options) < num_options_to_display:
            # Pad with dummy options if needed (should be handled by load_questions later)
            options.extend(["Dummy Option"] * (num_options_to_display - len(options)))
        
        # Select options to display (including correct ones and random incorrect ones)
        displayed_options = []
        
        # Get actual correct options based on current round's num_correct_answers
        # Ensure num_correct_answers does not exceed the number of available correct answers
        num_correct_answers_for_round = min(num_correct_answers, len(self.correct_answer_indices))
        actual_correct_options_indices = random.sample(self.correct_answer_indices, num_correct_answers_for_round)
        correct_options_texts = [options[idx] for idx in actual_correct_options_indices]
        
        # Add correct options
        displayed_options.extend(correct_options_texts)
        
        # Add incorrect options
        incorrect_options = [opt for i, opt in enumerate(options) if i not in self.correct_answer_indices]
        random.shuffle(incorrect_options)
        
        # Ensure we don't try to add more incorrect options than available
        num_incorrect_to_add = num_options_to_display - len(correct_options_texts)
        displayed_options.extend(incorrect_options[:num_incorrect_to_add])
        random.shuffle(displayed_options)

        # Update correct_answer_indices based on the new shuffled displayed_options
        self.current_correct_answer_indices = []
        for correct_opt_text in correct_options_texts:
            self.current_correct_answer_indices.append(displayed_options.index(correct_opt_text))

        self.time_left = self.get_difficulty_settings(self.current_difficulty)["time"]
        self.timer_label = tk.Label(
            self.root,
            text=f"Time Left: {self.time_left}",
            font=("Arial", 18, "bold"),
            fg="red",
            bg="darkred"
        )
        self.timer_label.pack(pady=10)
        
        self.q_label = tk.Label(
            self.root,
            text=f"💀 {question_text} (Round {self.nightmare_round}) 💀",
            font=("Arial", 22, "bold"),
            fg="white",
            bg="darkred",
            wraplength=700
        )
        self.q_label.pack(pady=30)
        
        self.options_frame = tk.Frame(self.root, bg="darkred")
        self.options_frame.pack(fill="both", expand=True)
        
        self.option_buttons = []
        
        for i, option_text in enumerate(displayed_options):
            btn = tk.Button(
                self.options_frame,
                text=option_text[::-1], # Reverse text for Nightmare mode
                font=("Arial", button_font_size, "bold"),
                width=button_width,
                height=2,
                bg="black",
                fg="red",
                activebackground="darkred",
                activeforeground="white",
                command=lambda idx=i: self.check_nightmare_answer(idx)
            )
            row_num = i // options_per_row
            col_num = i % options_per_row
            btn.grid(row=row_num, column=col_num, padx=5, pady=5) # Use grid for layout
            self.option_buttons.append(btn)
            
        self.options_frame.grid_columnconfigure(list(range(options_per_row)), weight=1)
        self.options_frame.grid_rowconfigure(list(range(num_options_to_display // options_per_row)), weight=1)

        self.start_nightmare_timer()
        self.start_nightmare_option_visibility_cycle()
        self.start_nightmare_question_cycle()

    def start_nightmare_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        
        if self.time_left > 0:
            self.timer_label.config(text=f"Time Left: {self.time_left}")
            self.time_left -= 1
            self.timer_id = self.root.after(1000, self.start_nightmare_timer)
        else:
            self.check_nightmare_answer(timeout=True)

    def start_nightmare_option_visibility_cycle(self):
        if hasattr(self, 'nightmare_visibility_timer_id') and self.nightmare_visibility_timer_id:
            self.root.after_cancel(self.nightmare_visibility_timer_id)

        def toggle_visibility():
            if not hasattr(self, 'option_buttons') or not self.option_buttons:
                return

            for btn in self.option_buttons:
                if btn.cget("fg") == "red": # If currently visible (red text)
                    btn.config(fg="darkred", bg="darkred") # Make invisible
                else:
                    btn.config(fg="red", bg="black") # Make visible
            
            # Schedule next toggle: 1 second visible, 0.5 second hidden
            if self.option_buttons[0].cget("fg") == "red": # If currently visible, next hide after 1 sec
                self.nightmare_visibility_timer_id = self.root.after(1000, toggle_visibility)
            else: # If currently hidden, next show after 0.5 sec
                self.nightmare_visibility_timer_id = self.root.after(500, toggle_visibility)
        toggle_visibility() # Start immediately

    def start_nightmare_question_cycle(self):
        if hasattr(self, 'nightmare_question_cycle_id') and self.nightmare_question_cycle_id:
            self.root.after_cancel(self.nightmare_question_cycle_id)

        def reverse_directions(text):
            # Only reverse 'يمين' and 'يسار'
            text = text.replace('يمين', 'LEFT_TEMP').replace('يسار', 'RIGHT_TEMP')
            text = text.replace('LEFT_TEMP', 'يسار').replace('RIGHT_TEMP', 'يمين')
            return text

        def cycle_question_text():
            if not hasattr(self, 'q_label') or not self.q_label:
                return

            question_data = self.questions_for_current_game[self.current_question_index]
            original_question_text = question_data["question"]
            
            # Check if the original question contains directional words
            directional_words = ["يمين", "يسار", "أعلى", "أسفل"]
            contains_directional_word = any(word in original_question_text for word in directional_words)

            if contains_directional_word:
                # Toggle between original and reversed text
                current_text_on_screen = self.q_label.cget("text").replace("💀 ", "").replace(" 💀", "")
                if current_text_on_screen.strip() == original_question_text.strip():
                    processed_text = reverse_directions(original_question_text)
                    self.q_label.config(text=f"💀 {processed_text} 💀")
                else:
                    self.q_label.config(text=f"💀 {original_question_text} 💀")
            else:
                # If no directional words, just display the original text (no cycling)
                self.q_label.config(text=f"💀 {original_question_text} 💀")

            self.nightmare_question_cycle_id = self.root.after(750, cycle_question_text)
        cycle_question_text() # Start immediately

    def check_nightmare_answer(self, selected_index=None, timeout=False):
        if hasattr(self, "nightmare_visibility_timer_id") and self.nightmare_visibility_timer_id:
            self.root.after_cancel(self.nightmare_visibility_timer_id)
        if hasattr(self, "nightmare_question_cycle_id") and self.nightmare_question_cycle_id:
            self.root.after_cancel(self.nightmare_question_cycle_id)
            
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
            
        for btn in self.option_buttons:
            btn.config(state="disabled")
            
        is_correct = False
        if not timeout and selected_index is not None:
            if selected_index in self.current_correct_answer_indices:
                is_correct = True
                self.score += 1
                
        if timeout:
            result_text = "💀 Time's Up! The nightmare continues! 💀"
            result_color = "red"
        elif is_correct:
            result_text = "🔥 Correct! But the nightmare isn't over yet! 🔥"
            result_color = "green"
        else:
            result_text = "💀 Wrong! The nightmare gets worse! 💀"
            result_color = "red"
            
        result_label = tk.Label(
            self.root,
            text=result_text,
            font=("Arial", 20, "bold"),
            fg=result_color,
            bg="darkred"
        )
        result_label.pack(pady=20)
        
        # Display all correct answers for Nightmare mode
        correct_options_texts = [self.questions_for_current_game[self.current_question_index]["options"][idx] for idx in self.correct_answer_indices]
        correct_answer_label = tk.Label(
            self.root,
            text=f"Correct Answer(s): {', '.join(correct_options_texts)}",
            font=("Arial", 16),
            fg="gold",
            bg="darkred"
        )
        correct_answer_label.pack(pady=10)
        
        next_btn = tk.Button(
            self.root,
            text="Next",
            font=("Arial", 16),
            bg="black",
            fg="red",
            command=self.advance_to_next_question
        )
        next_btn.pack(pady=30)

    def show_meme_question(self):
        if self.current_question_index >= len(self.questions_for_current_game):
            self.show_developers_screen()
            return
            
        self.clear_screen()
        self.root.configure(bg="purple")
        
        question_data = self.questions_for_current_game[self.current_question_index]
        question_text = question_data["question"]
        options = question_data["options"][:2]
        self.correct_answer_index = question_data["answer_index"]
        
        timer_label = tk.Label(
            self.root,
            text="⏰ Time Left: Infinite ∞",
            font=("Arial", 18, "bold"),
            fg="yellow",
            bg="purple"
        )
        timer_label.pack(pady=10)
        
        q_label = tk.Label(
            self.root,
            text=f"😂 {question_text} 😂",
            font=("Arial", 22, "bold"),
            fg="white",
            bg="purple",
            wraplength=700
        )
        q_label.pack(pady=30)
        
        options_frame = tk.Frame(self.root, bg="purple")
        options_frame.pack(pady=20)
        
        self.option_buttons = []
        
        colors = ["orange", "lightgreen"]
        # Shuffle options to prevent fixed correct answer position
        shuffled_options_with_indices = list(enumerate(options))
        random.shuffle(shuffled_options_with_indices)

        for i, (original_index, option_text) in enumerate(shuffled_options_with_indices):
            btn = tk.Button(
                options_frame,
                text=option_text,
                font=("Arial", 16, "bold"),
                width=40,
                height=2,
                bg=colors[i % len(colors)],
                fg="black",
                command=lambda idx=original_index: self.check_meme_answer(idx)
            )
            btn.pack(pady=10)
            self.option_buttons.append(btn)

    def check_meme_answer(self, selected_index):
        for btn in self.option_buttons:
            btn.config(state="disabled")
            
        is_correct = (selected_index == self.correct_answer_index)
        if is_correct:
            self.score += 1
            
        if is_correct:
            result_text = "🎉 Correct! You are the king of memes! 🎉"
            result_color = "green"
        else:
            result_text = "😅 Wrong! But it's okay, memes are for fun! 😅"
            result_color = "red"
            
        result_label = tk.Label(
            self.root,
            text=result_text,
            font=("Arial", 20, "bold"),
            fg=result_color,
            bg="purple"
        )
        result_label.pack(pady=20)
        
        correct_option_text = self.questions_for_current_game[self.current_question_index]["options"][self.correct_answer_index]
        correct_answer_label = tk.Label(
            self.root,
            text=f"Correct Answer: {correct_option_text}",
            font=("Arial", 16),
            fg="gold",
            bg="purple"
        )
        correct_answer_label.pack(pady=10)
        
        next_btn = tk.Button(
            self.root,
            text="Next",
            font=("Arial", 16),
            bg="orange",
            fg="black",
            command=self.advance_to_next_question
        )
        next_btn.pack(pady=30)

    def show_crazy_question(self):
        if self.current_question_index >= len(self.questions_for_current_game):
            self.show_result()
            return
            
        self.clear_screen()
        self.root.configure(bg="darkred") # Using darkred for Insane mode as well, similar to Nightmare
        
        question_data = self.questions_for_current_game[self.current_question_index]
        question_text = question_data["question"]
        options = question_data["options"]
        self.correct_answer_index = question_data["answer_index"]
        
        self.time_left = self.get_difficulty_settings(self.current_difficulty)["time"]
        self.timer_label = tk.Label(
            self.root,
            text=f"Time Left: {self.time_left}",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="darkred"
        )
        self.timer_label.pack(pady=10)
        
        q_label = tk.Label(
            self.root,
            text=question_text,
            font=("Arial", 22, "bold"),
            fg="white",
            bg="darkred",
            wraplength=700
        )
        q_label.pack(pady=30)
        
        options_frame = tk.Frame(self.root, bg="darkred")
        options_frame.pack(pady=20)
        
        self.option_buttons = []
        self.original_options = options.copy()
        
        # Shuffle options to prevent fixed correct answer position
        shuffled_options_with_indices = list(enumerate(options))
        random.shuffle(shuffled_options_with_indices)

        for i, (original_index, option_text) in enumerate(shuffled_options_with_indices):
            encrypted_text = "?" * len(option_text) # Encrypt with question marks
            btn = tk.Button(
                options_frame,
                text=encrypted_text,
                font=("Arial", 16),
                width=40,
                height=2,
                bg="gray",
                fg="white",
                command=lambda idx=original_index: self.check_answer(idx)
            )
            btn.bind("<Enter>", lambda event, btn=btn, text=option_text: btn.config(text=text))
            btn.bind("<Leave>", lambda event, btn=btn, text=encrypted_text: btn.config(text=text))
            btn.pack(pady=5)
            self.option_buttons.append(btn)
        
        self.start_timer()
        self.start_insane_text_shuffle()

    def start_insane_text_shuffle(self):
        """Shuffle button texts every 3 seconds for Insane mode while keeping encryption"""
        if hasattr(self, 'insane_shuffle_timer_id') and self.insane_shuffle_timer_id:
            self.root.after_cancel(self.insane_shuffle_timer_id)

        def shuffle_texts():
            if not hasattr(self, 'option_buttons') or not self.option_buttons:
                return
            
            # Get the actual option texts from the current question's options
            question_data = self.questions_for_current_game[self.current_question_index]
            options_for_shuffling = question_data["options"].copy()
            random.shuffle(options_for_shuffling)
            
            # Apply shuffled texts to buttons with encryption
            for i, btn in enumerate(self.option_buttons):
                if i < len(options_for_shuffling):
                    option_text = options_for_shuffling[i]
                    encrypted_text = "?" * len(option_text)
                    btn.config(text=encrypted_text)
                    
                    # Update the hover events with new text
                    btn.unbind("<Enter>")
                    btn.unbind("<Leave>")
                    btn.bind("<Enter>", lambda event, btn=btn, text=option_text: btn.config(text=text))
                    btn.bind("<Leave>", lambda event, btn=btn, text=encrypted_text: btn.config(text=text))
            
            # Schedule next shuffle
            self.insane_shuffle_timer_id = self.root.after(3000, shuffle_texts)
        
        # Start shuffling after 3 seconds
        self.insane_shuffle_timer_id = self.root.after(3000, shuffle_texts)
if __name__ == "__main__":
    root = tk.Tk()
    game = LegendQuizGame(root)
    root.mainloop()


