import tkinter as tk
from tkinter import ttk, messagebox

# ------------------ DATA ------------------ #
quiz_questions = [
    {"question": "Which movement promoted Swadeshi goods?",
     "options": ["Chipko", "Non-Cooperation", "Swadeshi", "Quit India"],
     "answer": "Swadeshi"},
    {"question": "Which state is famous for Pattachitra art?",
     "options": ["Odisha", "Gujarat", "Kerala", "Tamil Nadu"],
     "answer": "Odisha"},
    {"question": "Which material is used in Blue Pottery?",
     "options": ["Clay", "Wood", "Quartz", "Glass"],
     "answer": "Quartz"},
]

arts = [
    ("🎨 Madhubani Paintings - Bihar",
     "A traditional art form from Bihar using fingers, twigs, matchsticks, and natural dyes. Known for geometric patterns and religious motifs."),
    ("🎨 Pattachitra - Odisha",
     "Scroll painting with mythological narratives. Painted on cloth using natural colors and fine detailing."),
    ("🍯 Blue Pottery - Rajasthan",
     "Delicate, non-clay pottery made with quartz and glass. Famous for blue dye floral motifs."),
    ("🪀 Channapatna Toys - Karnataka",
     "Handmade wooden toys polished with natural colors, using a unique lacquerware technique."),
    ("🧵 Phulkari Embroidery - Punjab",
     "Bright, floral threadwork traditionally used in shawls and dupattas. Passed down from mothers to daughters."),
    ("🖍️ Warli Art - Maharashtra",
     "Tribal art using white paint on mud walls. Represents rural life and harmony with nature."),
    ("🧱 Terracotta - West Bengal",
     "Sculptures and pottery crafted from baked clay. Often used in temples and household decorations."),
    ("🖊️ Kalamkari - Andhra Pradesh",
     "Hand-painted or block-printed cotton textiles depicting epics and mythology.")
]

# ------------------ APP CLASS ------------------ #
class VocalForLocalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🇮🇳 Vocal for Local - Empowering Indian Heritage")
        self.geometry("850x600")
        self.configure(bg="white")

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TNotebook.Tab", font=("Arial", 12, "bold"))
        self.style.configure("TButton", font=("Arial", 11))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        self.create_home_tab()
        self.create_explore_tab()
        self.create_feedback_tab()
        self.create_quiz_tab()

        credit = tk.Label(self, text="Designed by Ankit Pal, Class 11-D", font=("Arial", 10, "italic"), anchor="e", fg="#888")
        credit.pack(side="bottom", anchor="se", pady=4, padx=8)

    def create_home_tab(self):
        home = ttk.Frame(self.notebook)
        self.notebook.add(home, text="🏠 Home")

        tk.Label(home, text="VOCAL FOR LOCAL", font=("Helvetica", 30, "bold"), fg="#1A237E").pack(pady=(30, 10))

        tk.Label(home, text="Empowering Indian Heritage & Culture", font=("Arial", 16, "italic"), fg="#424242").pack(pady=(0, 20))

        intro_text = (
            "India has a rich tradition of handicrafts, folk art, textiles, pottery, and more. These crafts are not just a livelihood for many, "
            "but also an expression of the soul of our culture. Through the Vocal for Local movement, we aim to create awareness and support "
            "for local artisans, rural industries, and cultural practices that have been passed down through generations."
        )

        mission_text = (
            "Our mission is to:\n"
            "• Promote Indian art and heritage among youth.\n"
            "• Inspire people to choose local over foreign products.\n"
            "• Provide a platform to explore traditional crafts and knowledge.\n"
            "• Encourage pride in our indigenous culture and creativity."
        )

        quote_text = (
            "“Local is not just a need; it is our responsibility. Be vocal about your choices. "
            "Support those who keep India’s culture alive.”"
        )

        tk.Label(home, text=intro_text, font=("Arial", 12), wraplength=750, justify="left", fg="#333").pack(padx=30, pady=10)
        tk.Label(home, text="Our Mission", font=("Arial", 14, "bold"), fg="#1B5E20").pack(pady=(20, 5))
        tk.Label(home, text=mission_text, font=("Arial", 12), wraplength=750, justify="left", fg="#333").pack(padx=30)
        tk.Label(home, text=quote_text, font=("Arial", 12, "italic"), wraplength=750, fg="#616161").pack(pady=25, padx=30)

        closing = (
            "This application allows you to:\n"
            "✔ Explore traditional art forms.\n"
            "✔ Learn fun facts through an interactive quiz.\n"
            "✔ Share your valuable feedback to improve our mission."
        )

    def create_explore_tab(self):
        explore = ttk.Frame(self.notebook)
        self.notebook.add(explore, text="🧭 Explore Arts")

        canvas = tk.Canvas(explore)
        scrollbar = ttk.Scrollbar(explore, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(scrollable_frame, text="Explore Indian Art Forms", font=("Arial", 18, "bold")).pack(pady=15)

        for title, desc in arts:
            tk.Label(scrollable_frame, text=title, font=("Arial", 13, "bold"), anchor="w", justify="left").pack(anchor="w", padx=20, pady=(10, 2))
            tk.Label(scrollable_frame, text="→ " + desc, font=("Arial", 11), wraplength=700, justify="left", fg="#555").pack(anchor="w", padx=40)

    def create_feedback_tab(self):
        feedback = ttk.Frame(self.notebook)
        self.notebook.add(feedback, text="💬 Feedback")

        tk.Label(feedback, text="We’d love your feedback!", font=("Arial", 18, "bold")).pack(pady=15)

        tk.Label(feedback, text="Name:", font=("Arial", 12)).pack(anchor="w", padx=30)
        name_entry = tk.Entry(feedback, width=30, font=("Arial", 12))
        name_entry.pack(pady=5)

        tk.Label(feedback, text="Rate our app:", font=("Arial", 12)).pack(anchor="w", padx=30, pady=(10, 5))
        stars = []
        rating_var = tk.IntVar(value=0)

        def set_rating(value):
            rating_var.set(value)
            for i in range(5):
                stars[i].config(text="★" if i < value else "☆")

        star_frame = tk.Frame(feedback)
        star_frame.pack()
        for i in range(5):
            lbl = tk.Label(star_frame, text="☆", font=("Arial", 24), cursor="hand2")
            lbl.pack(side="left", padx=5)
            lbl.bind("<Button-1>", lambda e, v=i+1: set_rating(v))
            stars.append(lbl)

        tk.Label(feedback, text="Your Comments:", font=("Arial", 12)).pack(anchor="w", padx=30, pady=(10, 5))
        comment_box = tk.Text(feedback, width=60, height=5)
        comment_box.pack()

        def submit_feedback():
            if not name_entry.get() or rating_var.get() == 0:
                messagebox.showwarning("Incomplete", "Please enter your name and give a rating.")
                return
            messagebox.showinfo("Submitted", "Thank you for your feedback!")
            name_entry.delete(0, tk.END)
            comment_box.delete("1.0", tk.END)
            set_rating(0)

        ttk.Button(feedback, text="Submit Feedback", command=submit_feedback).pack(pady=15)

    def create_quiz_tab(self):
        quiz = ttk.Frame(self.notebook)
        self.notebook.add(quiz, text="🧠 Swadeshi Quiz")

        tk.Label(quiz, text="Test Your Swadeshi Knowledge", font=("Arial", 18, "bold")).pack(pady=15)

        self.q_index = 0
        self.score = 0
        self.quiz_frame = tk.Frame(quiz)
        self.quiz_frame.pack()

        self.radio_var = tk.StringVar()
        self.progress = ttk.Progressbar(quiz, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        def load_question():
            for widget in self.quiz_frame.winfo_children():
                widget.destroy()
            if self.q_index < len(quiz_questions):
                q = quiz_questions[self.q_index]
                self.radio_var.set("")
                tk.Label(self.quiz_frame, text=f"Q{self.q_index + 1}. {q['question']}", font=("Arial", 12, "bold"), wraplength=600).pack(anchor="w", pady=5)
                for opt in q["options"]:
                    ttk.Radiobutton(self.quiz_frame, text=opt, variable=self.radio_var, value=opt).pack(anchor="w")
                ttk.Button(self.quiz_frame, text="Submit", command=check_answer).pack(pady=10)
            else:
                self.progress["value"] = 100
                result = f"✅ You scored {self.score} out of {len(quiz_questions)}"
                tk.Label(self.quiz_frame, text=result, font=("Arial", 14, "bold"), fg="#2E7D32").pack(pady=20)

        def check_answer():
            selected = self.radio_var.get()
            if selected == quiz_questions[self.q_index]["answer"]:
                self.score += 1
            self.q_index += 1
            self.progress["value"] = (self.q_index / len(quiz_questions)) * 100
            load_question()

        load_question()


# ------------------ RUN APP ------------------ #
if __name__ == "__main__":
    app = VocalForLocalApp()
    app.mainloop()
