from tkinter import *
from tkinter import messagebox
import random
import platform

print("Ignore this console window, This game was made in python and was compiled but I forgot to remove this console window...")

# Hangman figure parts (with proper escaping)
HANGMAN_PARTS = [
    """  _______
     |/      |
     |      
     |      
     |       
     |      
     |
    _|___""",
    """  _______
     |/      |
     |      (_)
     |      
     |       
     |      
     |
    _|___""",
    """  _______
     |/      |
     |      (_)
     |       |
     |       |
     |      
     |
    _|___""",
    """  _______
     |/      |
     |      (_)
     |      \\|
     |       |
     |      
     |
    _|___""",
    """  _______
     |/      |
     |      (_)
     |      \\|/
     |       |
     |      
     |
    _|___""",
    """  _______
     |/      |
     |      (_)
     |      \\|/
     |       |
     |      / 
     |
    _|___""",
    """  _______
     |/      |
     |      (_)
     |      \\|/
     |       |
     |      / \\
     |
    _|___"""
]

# FULL ORIGINAL WORD LISTS
car_brands = [
    "Lamborghini", "Ferrari", "Porsche", "Bugatti", "Tesla", "BMW", "Mercedes-Benz", 
    "Audi", "Volkswagen", "Toyota", "Honda", "Nissan", "Ford", "Chevrolet", "Dodge", 
    "Jeep", "Subaru", "Mazda", "Hyundai", "Kia", "Volvo", "Jaguar", "Land Rover", 
    "Maserati", "Aston Martin"
]

food_names = [
    "pizza", "burger", "sushi", "pasta", "tacos", "steak", "salad", "fried chicken", 
    "ice cream", "sandwich", "noodles", "curry", "dumplings", "hot dog", "lasagna", 
    "ramen", "paella", "falafel", "burrito", "shawarma", "pancakes", "waffles", 
    "chow mein", "pulao", "biryani"
]

countries = [
    "united states", "canada", "mexico", "brazil", "argentina", "united kingdom", 
    "france", "germany", "italy", "spain", "portugal", "netherlands", "belgium", 
    "sweden", "norway", "denmark", "finland", "russia", "china", "japan", 
    "south korea", "india", "pakistan", "bangladesh", "indonesia", "australia", 
    "new zealand", "egypt", "nigeria", "kenya", "south africa", "morocco", "turkey", 
    "saudi arabia", "iran", "iraq", "afghanistan", "thailand", "vietnam", 
    "philippines", "malaysia", "singapore", "greece", "switzerland", "austria", 
    "poland", "ukraine", "czech republic", "hungary", "romania"
]

continents = [
    "africa", "antarctica", "asia", "europe", "north america", "south america", 
    "australia"
]

oceans = [
    "pacific ocean", "atlantic ocean", "indian ocean", "southern ocean", "arctic ocean"
]

capital_cities = [
    "washington, d.c.", "ottawa", "mexico city", "london", "paris", "berlin", "rome", 
    "madrid", "lisbon", "amsterdam", "brussels", "riad", "stockholm", "helsinki", 
    "moscow", "beijing", "tokyo", "seoul", "new delhi", "canberra", "wellington", 
    "cairo", "nairobi", "pretoria", "islamabad"
]

animals = [
    "elephant", "giraffe", "kangaroo", "alligator", "penguin", "dolphin", 
    "rhinoceros", "chimpanzee", "ostrich", "crocodile"
]

fruits = [
    "apple", "banana", "mango", "pineapple", "strawberry", "blueberry", "watermelon", 
    "kiwi", "papaya", "pomegranate"
]

movies = [
    "inception", "titanic", "gladiator", "avatar", "casablanca", "interstellar", 
    "joker", "rocky", "frozen", "up"
]

sports = [
    "soccer", "basketball", "cricket", "badminton", "swimming", "tennis", 
    "volleyball", "rugby", "baseball", "cycling"
]

def credit():
    credit1 = Tk()
    credit1.config(bg="#00ff00")
    credit1.title("Credits")
    Label(credit1, bg="#00ff00", font=("Consolas", 40), text="Owner/Creator: Ayan Ashraf").pack()
    credit1.resizable(False, False)
    credit1.mainloop()

class HangmanGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Hangman Game")
        self.root.config(bg="#00ff00")
        
        # Maximize window
        if platform.system() == "Windows":
            self.root.state('zoomed')
        else:
            self.root.attributes('-zoomed', True)
        
        # Game variables
        self.categories = {
            "Car Brand": [w.lower() for w in car_brands],
            "Food": [w.lower() for w in food_names],
            "Country": [w.lower() for w in countries],
            "Continent": [w.lower() for w in continents],
            "Ocean": [w.lower() for w in oceans],
            "Capital City": [w.lower() for w in capital_cities],
            "Animal": [w.lower() for w in animals],
            "Fruit": [w.lower() for w in fruits],
            "Movie": [w.lower() for w in movies],
            "Sport": [w.lower() for w in sports]
        }
        
        self.word_category, self.secret_word = random.choice(list(self.categories.items()))
        self.secret_word = random.choice(self.secret_word).lower()
        self.guessed_letters = set()
        self.mistakes = 0
        self.max_mistakes = len(HANGMAN_PARTS) - 1
        
        # UI setup
        self.setup_ui()
    
    def setup_ui(self):
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Top frame
        top_frame = Frame(self.root, bg="#00ff00")
        top_frame.pack(pady=20)
        
        # Hangman display
        self.hangman_label = Label(top_frame, text=HANGMAN_PARTS[0], font=("Courier", 14), 
                                 bg="#00ff00", fg="black", justify=LEFT)
        self.hangman_label.grid(row=0, column=0, padx=20)
        
        # Hint label
        self.hint_label = Label(top_frame, text=f"Category: {self.word_category}", 
                              font=("Impact", 16), bg="#00ff00", fg="white")
        self.hint_label.grid(row=0, column=1, padx=20)
        
        # Word display
        self.word_display = Label(top_frame, text=self.get_display_word(), 
                                font=("Arial", 24), bg="#00ff00", fg="white")
        self.word_display.grid(row=1, column=0, columnspan=2, pady=20)
        
        # Letter buttons
        letters_frame = Frame(self.root, bg="#00ff00")
        letters_frame.pack(pady=20)
        
        for i, letter in enumerate("abcdefghijklmnopqrstuvwxyz"):
            btn = Button(letters_frame, text=letter.upper(), font=("Impact", 14), 
                        width=2, height=1, bg="black", fg="#00ff00",
                        activebackground="black", activeforeground="#00ff00",
                        command=lambda l=letter: self.guess_letter(l))
            btn.grid(row=i//9, column=i%9, padx=2, pady=2)
        
        # Exit button
        Button(self.root, text="Exit to Menu", font=("Impact", 14),
              bg="black", fg="#00ff00", command=self.show_main_menu).pack(pady=20)
    
    def get_display_word(self):
        return " ".join([letter if letter in self.guessed_letters else "_" for letter in self.secret_word])
    
    def guess_letter(self, letter):
        letter = letter.lower()
        if letter in self.guessed_letters:
            return
        
        self.guessed_letters.add(letter)
        
        if letter in self.secret_word:
            self.word_display.config(text=self.get_display_word())
            if "_" not in self.get_display_word():
                self.game_over(True)
        else:
            self.mistakes += 1
            self.hangman_label.config(text=HANGMAN_PARTS[self.mistakes])
            if self.mistakes >= self.max_mistakes:
                self.game_over(False)
    
    def game_over(self, won):
        for child in self.root.winfo_children():
            if isinstance(child, Frame):
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, Button):
                        grandchild.config(state=DISABLED)
        
        message = f"Congratulations! You guessed: {self.secret_word}" if won else f"Game Over! The word was: {self.secret_word}"
        Label(self.root, text=message, font=("Impact", 24), bg="#00ff00", fg="white").pack(pady=20)
        Button(self.root, text="Play Again", font=("Impact", 18), 
              bg="black", fg="#00ff00", command=self.reset_game).pack(pady=10)
    
    def reset_game(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.__init__(self.root)
    
    def show_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        MainMenu(self.root)

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Hangman Game")
        self.root.config(bg="black")
        
        if platform.system() == "Windows":
            self.root.state('zoomed')
        else:
            self.root.attributes('-zoomed', True)
        
        center_frame = Frame(root, bg="black")
        center_frame.pack(expand=True)
        
        # Play button with original animations
        play_button = Button(center_frame, text="Play", font=("Impact", 38),
                            bg="black", fg="#00ff00", activebackground="black",
                            activeforeground="#00ff00", 
                            command=lambda: HangmanGame(self.root))
        play_button.pack(pady=20)
        
        # Credits button with original animations
        credits_button = Button(center_frame, text="Credits", font=("Impact", 38),
                               bg="black", fg="#00ff00", activebackground="black",
                               activeforeground="#00ff00", command=credit)
        credits_button.pack(pady=20)
        
        # Bind hover effects
        play_button.bind("<Enter>", lambda e: self.on_hover(e, True))
        play_button.bind("<Leave>", lambda e: self.on_hover(e, False))
        credits_button.bind("<Enter>", lambda e: self.on_hover(e, True))
        credits_button.bind("<Leave>", lambda e: self.on_hover(e, False))
    
    def on_hover(self, event, is_hovering):
        widget = event.widget
        if is_hovering:
            widget.config(font=("Impact", 42), bg="darkgreen")
        else:
            widget.config(font=("Impact", 38), bg="black")

if __name__ == "__main__":
    root = Tk()
    MainMenu(root)
    root.mainloop()
