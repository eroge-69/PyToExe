import tkinter as tk
from tkinter import messagebox
import random


class QuizGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Game")
        root.state('zoomed')
        self.root.config(bg="lightblue")
        self.root.resizable(True, True)

        # Load questions
        self.load_questions()

        # Game variables
        self.current_question = 0
        self.score = 0
        self.selected_category = ""
        self.questions_for_game = []

        # Timer variables
        self.time_limit = 10  # Will change dynamically
        self.remaining_time = self.time_limit
        self.timer_id = None

        # Create main menu
        
        self.create_main_menu()
        tk.Label(self.root, text= "CODED BY: Prajwol and Aaditya", font=("Arial", 12, "bold"), bg='lightblue', fg='green').pack(pady=20)

    def load_questions(self):
        self.questions_db = {
            "Trigonometry": [
                {"question": "What is sin(30°)?", "options": ["0.5", "√3/2", "1", "0"], "answer": "0.5"},
                {"question": "What is cos(60°)?", "options": ["0", "1", "√3/2", "0.5"], "answer": "0.5"},
                {"question": "What is tan(45°)?", "options": ["0", "1", "√3", "∞"], "answer": "1"},
                {"question": "What is sin(90°)?", "options": ["0", "0.5", "1", "√2/2"], "answer": "1"},
                {"question": "What is cos(0°)?", "options": ["1", "0", "√3/2", "0.5"], "answer": "1"},
                {"question": "What is tan(0°)?", "options": ["1/2", "1", "∞", "0"], "answer": "0"},
                {"question": "What is tan(θ) in terms of sin(θ) and cos(θ)?", "options": ["sin(θ)/cos(θ)", "cos(θ)/sin(θ)", "1/sin(θ)", "1/cos(θ)"], "answer": "sin(θ)/cos(θ)"},
                {"question": "What is sin²(θ) + cos²(θ)?", "options": ["2", "0", "1", "tan(θ)"], "answer": "1"},
                {"question": "What is sec(θ) in terms of cos(θ)?", "options": ["1/cos(θ)", "cos(θ)", "sin(θ)", "1/sin(θ)"], "answer": "1/cos(θ)"},
                {"question": "What is sin(2θ)?", "options": ["2cos(θ)", "sin(θ) + cos(θ)", "sin²(θ) + cos²(θ)", "2sin(θ)cos(θ)"], "answer": "2sin(θ)cos(θ)"},
                {"question": "What is the period of the sine function?", "options": ["3.14", "π", "2π", "4π"], "answer": "2π"},
                {"question": "What is csc(θ) in terms of sin(θ)?", "options": ["1/sin(θ)", "sin(θ)", "cos(θ)/sin(θ)", "tan(θ)"], "answer": "1/sin(θ)"},
                {"question": "What is cos(π/3)?", "options": ["1", "√3/2", "0.5", "0"], "answer": "0.5"},
                {"question": "What is the amplitude of y = 3sin(x)?", "options": ["1", "3", "0", "2π"], "answer": "3"},
                {"question": "What is the range of the cosine function?", "options": ["[-1, 1]", "[0, 1]", "(-∞, ∞)", "[0, ∞)"], "answer": "[-1, 1]"},
                {"question": "What is cot(θ) in terms of sin(θ) and cos(θ)?", "options": ["cos(θ)/sin(θ)", "sin(θ)/cos(θ)", "1/sin(θ)", "1/cos(θ)"], "answer": "cos(θ)/sin(θ)"},
                {"question": "What is sin(π/6)?", "options": ["2", "0.5", "1", "0"], "answer": "0.5"},
                {"question": "What is cos(π/4)?", "options": ["0", "0.5", "1", "√2/2"], "answer": "√2/2"},
                {"question": "What is tan(π/3)?", "options": ["1/√3", "1", "0", "√3"], "answer": "√3"},
                {"question": "What is the phase shift of y = sin(x - π/2)?", "options": ["π/2 right", "π/2 left", "π right", "π left"], "answer": "π/2 right"},
                {"question": "What is the reciprocal identity of tan(θ)?", "options": ["sec(θ)", "cot(θ)", "csc(θ)", "sin(θ)"], "answer": "cot(θ)"},
                {"question": "What is sin(3π/2)?", "options": ["1", "0", "-1", "0.5"], "answer": "-1"},
                {"question": "What is cos(2π)?", "options": ["0.5", "0", "-1", "1"], "answer": "1"},
                {"question": "What is the double angle formula for cos(2θ)?", "options": ["cos²θ - sin²θ", "2sinθcosθ", "sin²θ - cos²θ", "1 - 2sin²θ"], "answer": "cos²θ - sin²θ"},
                {"question": "What is the value of sin(0°)?", "options": ["1", "0", "0.5", "√3/2"], "answer": "0"},
                {"question": "What is the value of cos(90°)?", "options": ["√3/2", "1", "0.5", "0"], "answer": "0"},
                {"question": "What is the value of tan(90°)?", "options": ["1", "0", "Undefined", "∞"], "answer": "Undefined"},
                {"question": "What is the Pythagorean identity involving tan(θ)?", "options": ["1 + tan²θ = sec²θ", "tan²θ + cot²θ = 1", "1 + cot²θ = csc²θ", "tanθ + cotθ = 1"], "answer": "1 + tan²θ = sec²θ"},
                {"question": "What is the period of y = tan(x)?", "options": ["4π", "2π", "π/2", "π"], "answer": "π"},
                {"question": "What is the value of sin(π)?", "options": ["0.5", "1", "-1", "0"], "answer": "0"}
            ],
            "Geometry": [
                {"question": "What is the sum of the interior angles of a triangle?", "options": ["180°", "360°", "90°", "270°"], "answer": "180°"},
                {"question": "What is the formula for the area of a rectangle?", "options": ["length + width", "2 × (length + width)", "length × width", "length ÷ width"], "answer": "length × width"},
                {"question": "What is the Pythagorean theorem?", "options": ["a + b = c²", "a² + b² = c²", "a² - b² = c²", "a × b = c"], "answer": "a² + b² = c²"},
                {"question": "What is the volume formula for a cube?", "options": ["4 × side ", "side²", "side³", "6 × side"], "answer": "side³"},
                {"question": "What is the diagonal length of a square with side s?", "options": ["s√2", "2s", "s/2", "s²"], "answer": "s√2"},
                {"question": "How many sides does a hexagon have?", "options": ["7", "5", "6", "8"], "answer": "6"},
                {"question": "What is the circumference formula for a circle?", "options": ["πr²", "πr²", "2πr", "πr"], "answer": "2πr"},
                {"question": "What is the area formula for a circle?", "options": ["πr²", "2πr", "πd", "πr³/3"], "answer": "πr²"},
                {"question": "What is the sum of the exterior angles of any polygon?", "options": ["160°", "180°", "360°", "720°"], "answer": "360°"},
                {"question": "What is the formula for the volume of a cylinder?", "options": ["πr²h/3", "2πrh", "πr²h", "4πr²"], "answer": "πr²h"},
                {"question": "How many faces does a cube have?", "options": ["6", "4", "8", "12"], "answer": "6"},
                {"question": "What is the formula for the area of a triangle?", "options": ["base × height", "½ × base × height", "side + side + side", "π × base × height"], "answer": "½ × base × height"},
                {"question": "What is the formula for the surface area of a sphere?", "options": ["πr", "πr²", "4/3πr³", "4πr²"], "answer": "4πr²"},
                {"question": "What is the volume formula for a cone?", "options": ["⅓πr²h", "πr²h", "4/3πr³", "2πr²h"], "answer": "⅓πr²h"},
                {"question": "What type of triangle has all sides equal?", "options": ["Isoceles", "Equilateral", "Scalene", "Right"], "answer": "Equilateral"},
                {"question": "What is the formula for the area of a trapezoid?", "options": ["2(l + b)", "b × h", "½(b₁ + b₂)h", "π(b₁ + b₂)"], "answer": "½(b₁ + b₂)h"},
                {"question": "How many degrees are in a right angle?", "options": ["55°", "180°", "45°", "90°"], "answer": "90°"},
                {"question": "What is the formula for the volume of a pyramid?", "options": ["base area × height", "base area × height", "⅓ × base area × height", "π × base area × height"], "answer": "⅓ × base area × height"},
                {"question": "What is the name for a quadrilateral with exactly one pair of parallel sides?", "options": ["Trapezoid", "Parallelogram", "Rhombus", "Rectangle"], "answer": "Trapezoid"},
                {"question": "What is the formula for the diagonal of a rectangular prism with sides a, b, c?", "options": ["a + b + c", "√(a² + b² + c²)", "abc", "2(a + b + c)"], "answer": "√(a² + b² + c²)"},
                {"question": "What is the sum of the interior angles of a pentagon?", "options": ["420°", "540°", "720°", "180°"], "answer": "540°"},
                {"question": "What is the formula for the area of a parallelogram?", "options": ["π × base × height", "½ × base × height", "sum of all sides", "base × height"], "answer": "base × height"},
                {"question": "What is the name for a polygon with 8 sides?", "options": ["Octagon", "Hexagon", "Pentagon", "Decagon"], "answer": "Octagon"},
                {"question": "What is the formula for the surface area of a cylinder?", "options": ["πr²h + 4πr²", "πr²h", "4πr²", "2πr² + 2πrh"], "answer": "2πr² + 2πrh"},
                {"question": "What is the name for two lines that never meet?", "options": ["Parallel", "Perpendicular", "Intersecting", "Concurrent"], "answer": "Parallel"},
                {"question": "What is the formula for the area of a rhombus?", "options": ["½ × base × height", "½ × d₁ × d₂", "side × side", "π × r²"], "answer": "½ × d₁ × d₂"},
                {"question": "What is the formula for the perimeter of a rectangle?", "options": ["4 × side", "length × width", "2(length + width)", "π × diameter"], "answer": "2(length + width)"},
                {"question": "What is the formula for the volume of a sphere?", "options": ["4/3πr³", "πr²h", "4πr²", "⅓πr²h"], "answer": "4/3πr³"},
                {"question": "What is the name for a triangle with all angles less than 90°?", "options": ["Equilateral", "Obtuse", "Right", "Acute"], "answer": "Acute"},
                {"question": "What is the formula for the surface area of a rectangular prism?", "options": ["4(l + w + h)", "Mayank", "2(lw + lh + wh)", "6 × side²"], "answer": "2(lw + lh + wh)"}
            ],
            "Algebra": [
                {"question": "If x + 2 = 5, what is x?", "options": ["1", "2", "3", "5"], "answer": "3"},
                {"question": "Simplify: 2(x + 3)", "options": ["2x + 6", "x + 6", "2x + 3", "x + 3"], "answer": "2x + 6"},
                {"question": "Factor: x² - 9", "options": ["(x-9)(x+1)", "(x+3)(x-3)", "(x-3)²", "x(x-9)"], "answer": "(x+3)(x-3)"},
                {"question": "Solve for x: 3x = 12", "options": ["7", "3", "2", "4"], "answer": "4"},
                {"question": "If x = 2, what is x² + 2x + 1?", "options": ["4", "8", "9", "6"], "answer": "9"},
                {"question": "What is the slope of y = 2x + 3?", "options": ["4", "3", "6", "2"], "answer": "2"},
                {"question": "Solve: 2x - 5 = 11", "options": ["3", "8", "6", "5"], "answer": "8"},
                {"question": "What is the y-intercept of y = -3x + 4?", "options": ["4", "-3", "3", "-4"], "answer": "4"},
                {"question": "Simplify: (x³)(x²)", "options": ["x", "x⁶", "x⁵", "2x⁵"], "answer": "x⁵"},
                {"question": "Solve the system: x + y = 5, x - y = 1", "options": ["x=3, y=-1", "x=2, y=3", "x=3, y=2", "x=1, y=4"], "answer": "x=3, y=2"},
                {"question": "What is the solution to x² - 5x + 6 = 0?", "options": ["x=2 or x=3", "x=1 or x=6", "x=-2 or x=-3", "x=5 or x=6"], "answer": "x=2 or x=3"},
                {"question": "What is the quadratic formula?", "options": ["[-b ± √(b²-4ac)]/2a", "b² - 4ac", "ax² + bx + c = 0", "y = mx + b"], "answer": "[-b ± √(b²-4ac)]/2a"},
                {"question": "Simplify: √(16)", "options": ["2", "8", "4", "16"], "answer": "4"},
                {"question": "What is the value of 5!", "options": ["69", "25", "15", "120"], "answer": "120"},
                {"question": "Solve for x: |x - 3| = 5", "options": ["x=8 or x=-4", "x=8 or x=-2", "x=5 or x=-5", "x=3 or x=-3"], "answer": "x=8 or x=-2"},
                {"question": "What is the solution to 2x + 3 > 7?", "options": ["x > 5", "x < 2", "x > 2", "x < 5"], "answer": "x > 2"},
                {"question": "What is the midpoint formula?", "options": ["((x₁+x₂)/2, (y₁+y₂)/2)", "(x₂-x₁, y₂-y₁)", "√[(x₂-x₁)² + (y₂-y₁)²]", "y = mx + b"], "answer": "((x₁+x₂)/2, (y₁+y₂)/2)"},
                {"question": "What is the distance formula?", "options": ["√[(x₂-x₁)² + (y₂-y₁)²]", "(x₂-x₁, y₂-y₁)", "((x₁+x₂)/2, (y₁+y₂)/2)", "y - y₁ = m(x - x₁)"], "answer": "√[(x₂-x₁)² + (y₂-y₁)²]"},
                {"question": "What is the standard form of a linear equation?", "options": ["y - y₁ = m(x - x₁)", "y = mx + b", "Ax + By = C", "x/a + y/b = 1"], "answer": "Ax + By = C"},
                {"question": "What is the slope-intercept form?", "options": ["y = mx + b", "Ax + By = C", "y - y₁ = m(x - x₁)", "x/a + y/b = 1"], "answer": "y = mx + b"},
                {"question": "What is the point-slope form?", "options": ["x/a + y/b = 1", "y = mx + b", "Ax + By = C", "y - y₁ = m(x - x₁)"], "answer": "y - y₁ = m(x - x₁)"},
                {"question": "Simplify: (2x²y³)³", "options": ["2x⁶y⁹", "6x⁵y⁶", "8x⁶y⁹", "8x⁵y⁶"], "answer": "8x⁶y⁹"},
                {"question": "What is the solution to log₂8 = x?", "options": ["2", "3", "4", "1"], "answer": "3"},
                {"question": "What is the value of i² (imaginary unit)?", "options": ["0", "1", "-1", "i"], "answer": "-1"},
                {"question": "What is the solution to eˡⁿ⁵ = ?", "options": ["6 ", "5", "ln5", "1"], "answer": "5"},
                {"question": "What is the solution to 3ˣ = 81?", "options": ["x=27", "x=3", "x=4", "x=9"], "answer": "x=4"},
                {"question": "What is the solution to √(x + 3) = 5?", "options": ["x=420", "x=22", "x=25", "x=8"], "answer": "x=22"},
                {"question": "What is the solution to (x + 2)(x - 3) = 0?", "options": ["x=-2 or x=3", "x=2 or x=-3", "x=2 or x=3", "x=-2 or x=-3"], "answer": "x=-2 or x=3"},
                {"question": "What is the solution to 4x - 7 = 2x + 5?", "options": ["x=3", "x=2", "x=4", "x=6"], "answer": "x=6"},
                {"question": "What is the solution to x² + 6x + 9 = 0?", "options": ["x=3", "x=-3", "x=0", "x=-6"], "answer": "x=-3"}
            ],
            "Advanced Mathematics": [
                {"question": "If (x + 1)(x - 2) = 0, what is the sum of all possible x?", "options": ["-2", "1", "3", "-1"], "answer": "1"},
                {"question": "If f(x) = x² - 4x + 3, what is the minimum value of f(x)?", "options": ["0", "66", "-2", "-1"], "answer": "-1"},
                {"question": "What is the remainder when 7⁴ is divided by 5?", "options": ["9", "1", "3", "4"], "answer": "1"},
                {"question": "Solve for x: |2x - 1| > 5", "options": ["x > 3 or x < -2", "x > 4 or x < -2", "x > 2 or x < -3", "x > 2 or x < -1"], "answer": "x > 3 or x < -2"},
                {"question": "If log₁₀(2x) = 3, what is x?", "options": ["420", "1000", "1500", "500"], "answer": "500"},
                {"question": "A and B can complete a task in 12 days. B alone does it in 20 days. How long would A alone take?", "options": ["30", "48", "60", "24"], "answer": "30"},
                {"question": "If x ≠ 0 and x² + 1/x² = 10, what is x + 1/x?", "options": ["√10", "3", "4", "5"], "answer": "3 or -3"},
                {"question": "If 4x + 3y = 25 and 3x + 4y = 24, what is x + y?", "options": ["7", "5", "6", "8"], "answer": "6"},
                {"question": "If sin(θ) = 3/5 and θ is in Quadrant II, what is cos(θ)?", "options": ["5/5", "3/6", "4/5", "3/5"], "answer": "-4/5"},
                {"question": "What is the sum of the roots of 3x² - 5x + 2 = 0?", "options": ["5", "3", "5/3", "2/3"], "answer": "5/3"},
                {"question": "How many integers between 100 and 999 are divisible by 7?", "options": ["153", "128", "129", "130"], "answer": "128"},
                {"question": "The area of a circle increases by what percent if its radius is doubled?", "options": ["100%", "200%", "300%", "400%"], "answer": "300%"},
                {"question": "What is the 50th term of the sequence aₙ = 5n - 3?", "options": ["245", "245", "253", "247"], "answer": "247"},
                {"question": "What is the value of x in the equation 2^(x+1) = 64?", "options": ["5", "6", "7", "8"], "answer": "5"},
                {"question": "If 3x + 2y = 18 and 2x - y = 3, what is xy?", "options": ["16", "18", "12", "10"], "answer": "16"},
                {"question": "A rectangle has area 120 and length 5 more than width. What is the width?", "options": ["12", "8", "6", "10"], "answer": "10"},
                {"question": "What is the smallest prime factor of 221?", "options": ["23", "17", "13", "19"], "answer": "13"},
                {"question": "If aₙ = 2aₙ₋₁ + 1, a₁ = 1, what is a₄?", "options": ["9", "15", "17", "11"], "answer": "15"},
                {"question": "What is the greatest common divisor (GCD) of 252 and 105?", "options": ["14", "21", "12", "15"], "answer": "21"},
                {"question": "In a triangle with angles in ratio 2:3:5, what is the smallest angle?", "options": ["18°", "20°", "36°", "40°"], "answer": "36°"},
                {"question": "Solve: x² + 6x + 10 = 0", "options": ["Complex roots", "No solution", "x = 2", "x = -2"], "answer": "Complex roots"},
                {"question": "How many three-digit numbers have digits in strictly increasing order?", "options": ["273", "120", "84", "60"], "answer": "84"},
                {"question": "How many 4-digit numbers can be formed using digits 1–6 without repetition?", "options": ["160", "240", "120", "360"], "answer": "360"},
                {"question": "If the probability of event A is 0.4 and event B is 0.5, and A and B are independent, what is P(A ∩ B)?", "options": ["0.2", "0.9", "0.1", "0.25"], "answer": "0.2"},
                {"question": "If the standard deviation of a data set is zero, what does that imply?", "options": ["Mean is zero", "All values are equal", "There is an outlier", "Skewed data"], "answer": "All values are equal"},
                {"question": "What is the distance between the points (3, -2) and (-1, 1)?", "options": ["√13", "4", "6", "5"], "answer": "5"},
                {"question": "What is the sum of all even numbers from 2 to 100?", "options": ["2555", "2500", "2550", "2750"], "answer": "2550"},
                {"question": "What is the coefficient of x² in (x + 2)(x - 3)?", "options": ["-1", "1", "2", "-2"], "answer": "1"},
                {"question": "If a cube has a surface area of 54, what is its volume?", "options": ["27", "64", "125", "36"], "answer": "27"},
                {"question": "A bag contains 5 red, 6 blue, and 4 green balls. Probability of picking a blue or green?", "options": ["2/3", "3/4", "5/7", "4/5"], "answer": "2/3"}
            ]
        }

    def create_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Quiz Game", font=("Arial", 24, "bold"), bg='lightblue', fg='black').pack(pady=20)
        tk.Label(self.root, text="Select a Category:", font=("Arial", 14), bg='lightblue', fg='black').pack(pady=10)

        for category in self.questions_db:
            tk.Button(
                self.root,
                text=category,
                font=("Arial", 12),
                width=20,
                bg='lightblue',
                fg='black',
                command=lambda c=category: self.start_quiz(c)
            ).pack(pady=5)

        tk.Button(
            self.root,
            text="Exit",
            font=("Arial", 12),
            width=20,
            bg='lightblue',
            fg='red',
            command=self.root.quit
        ).pack(pady=20)

    def start_quiz(self, category):
        self.selected_category = category
        # Set different time limits based on category
        if category == "Geometry":
            self.time_limit = 15
        elif category == "Trigonometry":
            self.time_limit = 20
        elif category == "Algebra":
            self.time_limit = 25
        elif category == "Advanced Mathematics":
            self.time_limit = 30
        else:
            self.time_limit = 15

        self.questions_for_game = random.sample(self.questions_db[category], min(15, len(self.questions_db[category])))
        self.current_question = 0
        self.score = 0
        self.show_question()

    def show_question(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        q = self.questions_for_game[self.current_question]

        tk.Label(self.root, text=f"Question {self.current_question + 1} of {len(self.questions_for_game)}", font=("Arial", 12), bg='lightblue', fg='black').pack(pady=10)
        tk.Label(self.root, text=f"Score: {self.score}", font=("Arial", 12), bg='lightblue', fg='black').pack(pady=5)
        tk.Label(self.root, text=f"Category: {self.selected_category}", font=("Arial", 12, "bold"), bg='lightblue', fg='black').pack(pady=5)
        tk.Label(self.root, text=q["question"], font=("Arial", 14), wraplength=700, justify="center", bg='lightblue', fg='black').pack(pady=20)

        self.selected_option = tk.StringVar(value="")
        for opt in q["options"]:
            tk.Radiobutton(self.root, text=opt, variable=self.selected_option, value=opt, font=("Arial", 12, 'bold'), bg='lightblue', fg='black').pack(anchor="w", padx=100, pady=5)

        tk.Button(self.root, text="Submit Answer", font=("Arial", 12), command=self.check_answer, bg='lightblue', fg='black').pack(pady=20)
        tk.Button(self.root, text="Back to Menu", font=("Arial", 10), command=self.create_main_menu, bg='lightblue', fg='black').pack(pady=10)

        self.remaining_time = self.time_limit
        self.timer_label = tk.Label(self.root, text=f"Time Left: {self.remaining_time} sec", font=("Arial", 12), bg='lightblue', fg='red')
        self.timer_label.pack()
        self.update_timer()

    def update_timer(self):
        self.timer_label.config(text=f"Time Left: {self.remaining_time} sec")
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            messagebox.showinfo("Time's Up", "You ran out of time!")
            self.timer_id = None
            self.current_question += 1
            if self.current_question < len(self.questions_for_game):
                self.show_question()
            else:
                self.show_results()

    def check_answer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        if not self.selected_option.get():
            messagebox.showwarning("Warning", "Please select an answer!")
            return

        correct = self.questions_for_game[self.current_question]["answer"]
        if self.selected_option.get() == correct:
            self.score += 1
            messagebox.showinfo("Correct", "Your answer is correct!")
        else:
            messagebox.showerror("Incorrect", f"Wrong! The correct answer was: {correct}")

        self.current_question += 1

        if self.current_question < len(self.questions_for_game):
            self.show_question()
        else:
            self.show_results()

    def show_results(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        percentage = (self.score / len(self.questions_for_game)) * 100

        tk.Label(self.root, text="Quiz Results", font=("Arial", 24, "bold"), bg='lightblue', fg='grey').pack(pady=20)
        tk.Label(self.root, text=f"Category: {self.selected_category}", font=("Arial", 14), bg='lightblue', fg='black').pack(pady=10)
        tk.Label(self.root, text=f"Score: {self.score}/{len(self.questions_for_game)}", font=("Arial", 16, "bold"), bg='lightblue', fg='black').pack(pady=20)
        tk.Label(self.root, text=f"{percentage:.1f}% Correct", font=("Arial", 14), bg='lightblue', fg='darkgreen').pack(pady=10)

        message = "Excellent! You know this topic very well!" if percentage >= 80 else (
            "Good job! You have a decent knowledge of this topic" if percentage >= 60 else (
                "Not bad, but there's room for improvement." if percentage >= 40 else "You might want to study this topic more."
                "Nice better then Prajwol" if percentage >= 30 else "Prajwol is better then you."
            )
        )

        tk.Label(self.root, text=message, font=("Arial", 12)).pack(pady=20)

        tk.Button(self.root, text="Play Again", font=("Arial", 12), bg='lightblue', fg='red',
                  command=lambda: self.start_quiz(self.selected_category)).pack(pady=10)
        tk.Button(self.root, text="Back to Menu", font=("Arial", 12), command=self.create_main_menu, bg='lightblue', fg='red').pack(pady=10)


# Run the quiz app
if __name__ == "__main__":
    root = tk.Tk()
    app = QuizGame(root)
    root.mainloop()