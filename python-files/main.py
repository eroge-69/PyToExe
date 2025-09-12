import sys
import tkinter as tk
from tkinter import messagebox
import random
import os
from PIL import Image, ImageTk  # Pillow library for image handling

# ====== Path Verification ======
EXPECTED_PATH = r"C:\Users\hp\Desktop\Add_Test"

# Get absolute directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

if os.path.normpath(current_dir) != os.path.normpath(EXPECTED_PATH):
    print(f"Error: main.py must be located in {EXPECTED_PATH}")
    print(current_dir)
    sys.exit(1)  # Exit the application immediately
# Paths to image folders
SMILE_FOLDER = "smile_images"
SAD_FOLDER = "sad_images"

class AddTwoNumbersApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Add Two Numbers Game")

        # Generate first question
        self.num1 = 0
        self.num2 = 0

        # Question label
        self.question_label = tk.Label(root, text="", font=("Arial", 16))
        self.question_label.pack(pady=10)

        # Entry for answer
        self.answer_entry = tk.Entry(root, font=("Arial", 14))
        self.answer_entry.pack(pady=5)

        # Button to check answer
        self.check_button = tk.Button(root, text="Check Answer", font=("Arial", 14), command=self.check_answer)
        self.check_button.pack(pady=5)

        # Label to display emoji
        self.image_label = tk.Label(root)
        self.image_label.pack(pady=10)

        # Start first question
        self.new_question()

    def new_question(self):
        """Generate two random numbers and update the question label."""
        self.num1 = random.randint(1, 10)
        self.num2 = random.randint(1, 10)
        self.question_label.config(text=f"What is {self.num1} + {self.num2}?")
        self.answer_entry.delete(0, tk.END)
        self.image_label.config(image="")  # Clear previous image

    def check_answer(self):
        """Check if the user's answer is correct and display the appropriate emoji."""
        try:
            user_answer = int(self.answer_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a number.")
            return

        if user_answer == self.num1 + self.num2:
            self.show_random_image(SMILE_FOLDER)
        else:
            self.show_random_image(SAD_FOLDER)

        # Generate a new question after showing result
        self.root.after(1500, self.new_question)

    def show_random_image(self, folder):
        """Display a random image from the given folder."""
        try:
            images = [f for f in os.listdir(folder) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
            if not images:
                messagebox.showerror("Error", f"No images found in {folder}")
                return
            img_path = os.path.join(folder, random.choice(images))
            img = Image.open(img_path)
            img = img.resize((100, 100), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            self.image_label.config(image=tk_img)
            self.image_label.image = tk_img  # Keep reference
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = AddTwoNumbersApp(root)
    root.mainloop()
