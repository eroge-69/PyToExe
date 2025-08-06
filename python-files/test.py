import csv
import random
import time
import tkinter as tk
from tkinter import messagebox, ttk
import requests
from io import StringIO
import os
from datetime import datetime

# --- Configuration Constants ---
TOTAL_TIME = 1200  # Total test duration in seconds (30 minutes)
# Google Sheet CSV export URL for the question bank.
# Ensure this URL is publicly accessible for the application to fetch data.
CSV_URL = "https://docs.google.com/spreadsheets/d/1T-2cSbGIVp0Zs9MgDtaCG5YIN-UBfMxCmEeNjYwwea0/export?format=csv&gid=0"

QUESTIONS_LIMIT = 10  # Maximum number of questions to display per test
MARKS_PER_QUESTION = 1  # Marks awarded for each correct answer
RESULTS_BASE_DIR = "Robotics Unit Test Results"  # Base folder to save test results

# --- Global Variables ---
questions = []  # Stores the list of questions for the current test
answer_vars = []  # List of Tkinter StringVar/IntVar objects to hold user answers
start_time = None  # Timestamp when the quiz starts, used for timer
timer_label = None  # Tkinter Label widget to display the countdown timer
canvas = None  # Tkinter Canvas widget for scrollable question display

# --- Tkinter Root Window Setup ---
root = tk.Tk()
root.title("Robotics Unit Test")
root.geometry("850x650")  # Set initial window size

# --- Tkinter StringVars for User Information ---
name_var = tk.StringVar()
roll_var = tk.StringVar()
div_var = tk.StringVar()
grade_var = tk.StringVar()

# --- Functions ---

def load_questions_from_csv_url():
    """
    Fetches questions from a Google Sheets CSV URL.
    Returns a list of dictionaries, where each dictionary represents a question.
    Handles network errors gracefully.
    """
    all_questions = []
    try:
        resp = requests.get(CSV_URL)
        resp.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        f = StringIO(resp.text)  # Use StringIO to treat the string as a file
        reader = csv.DictReader(f)  # Read CSV data into dictionaries
        all_questions = list(reader)
        return all_questions
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Network Error", f"Failed to load questions from URL: {e}\nPlease check your internet connection or the CSV URL.")
        return []
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred while loading questions: {e}")
        return []

def filter_questions_by_grade(all_questions, grade):
    """
    Filters the loaded questions by the selected grade, shuffles them,
    and returns a limited number of questions as defined by QUESTIONS_LIMIT.
    """
    filtered = [q for q in all_questions if q.get("Grade", "").strip() == grade]
    random.shuffle(filtered)
    return filtered[:QUESTIONS_LIMIT]

def get_answer_value(question_data, answer_key):
    """
    Gets the full text of an answer option (e.g., "A machine") based on its key (e.g., "A").
    """
    if question_data.get("Type", "").strip().upper() == "MCQ":
        return question_data.get(f"Option {answer_key}", answer_key)
    return answer_key

def save_answers_locally(name, roll, div, grade, answers, score, questions_list):
    """
    Saves the student's answers, score, and the questions themselves to a CSV file.
    The files are organized into subdirectories by grade and division, and the filename
    includes a date and time stamp.
    """
    # Create the directory structure: Results/Grade_X/Division_Y
    grade_dir = os.path.join(RESULTS_BASE_DIR, f"Grade_{grade}")
    div_dir = os.path.join(grade_dir, f"Division_{div}")
    os.makedirs(div_dir, exist_ok=True)

    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_')).rstrip()
    
    # Add a timestamp to the filename to avoid overwriting
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{roll}_{safe_name}_{timestamp}.csv"
    filepath = os.path.join(div_dir, filename)

    try:
        with open(filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", name])
            writer.writerow(["Roll No", roll])
            writer.writerow(["Division", div])
            writer.writerow(["Grade", grade])
            writer.writerow(["Final Score", f"{score}"])
            writer.writerow([])
            writer.writerow(["Question", "User Answer", "Correct Answer", "Result"])
            
            for i in range(len(questions_list)):
                q_data = questions_list[i]
                user_answer_key = answers[i]
                correct_answer_key = q_data.get("Answer", "").strip()
                
                # Get the full text for both answers for better readability
                user_answer_text = get_answer_value(q_data, user_answer_key)
                correct_answer_text = get_answer_value(q_data, correct_answer_key)

                result = "Correct" if user_answer_key.lower() == correct_answer_key.lower() else "Incorrect"
                
                writer.writerow([
                    q_data.get("Question", "N/A"),
                    user_answer_text,
                    correct_answer_text,
                    result
                ])

        messagebox.showinfo("Success", f"Your results have been saved to:\n{filepath}")
    except Exception as e:
        messagebox.showerror("Save Error", f"Failed to save results: {e}")

def calculate_score(questions_list, user_answers):
    """
    Calculates the student's score based on their answers and the correct answers.
    Handles MCQ, True/False, and Fill-in-the-Blanks question types.
    """
    score = 0
    for q, user_ans_key in zip(questions_list, user_answers):
        correct_answer_key = q.get("Answer", "").strip()
        # Compare user's answer key (e.g., 'A', 'True', 'LED') with the correct one
        if user_ans_key.lower() == correct_answer_key.lower():
            score += MARKS_PER_QUESTION
    return score

def submit_quiz():
    """
    Handles the quiz submission process:
    1. Validates user input fields.
    2. Calculates the score.
    3. Saves the results locally.
    4. Displays a final message and closes the application.
    """
    if not (name_var.get().strip() and roll_var.get().strip() and div_var.get() and grade_var.get()):
        messagebox.showerror("Error", "Please fill in all personal information fields (Name, Roll No, Division, Grade) before submitting.")
        return

    answers = [v.get().strip() for v in answer_vars]

    score = calculate_score(questions, answers)

    # Save the results, passing all required information
    save_answers_locally(
        name_var.get().strip(),
        roll_var.get().strip(),
        div_var.get(),
        grade_var.get(),
        answers,
        score,
        questions
    )

    messagebox.showinfo(
        "Test Completed",
        f"Test submitted successfully!\nYour score: {score} out of {QUESTIONS_LIMIT * MARKS_PER_QUESTION}"
    )
    root.destroy()

def on_mouse_wheel(event):
    """
    Handles mouse wheel scrolling for the canvas.
    Works across different OS (event.num for Linux, event.delta for Windows/macOS).
    """
    if event.num == 5 or event.delta == -120:  # Scroll down
        canvas.yview_scroll(1, "units")
    elif event.num == 4 or event.delta == 120:  # Scroll up
        canvas.yview_scroll(-1, "units")

def show_questions():
    """
    Clears the initial screen and displays the quiz questions.
    Sets up a scrollable canvas for questions and starts the timer.
    """
    global canvas, timer_label
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="🤖 Robotics Term Test", font=("Arial", 18, "bold"), fg="#333").pack(pady=10)

    canvas = tk.Canvas(root, borderwidth=0, background="#f0f0f0")
    scroll = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    frame = tk.Frame(canvas, background="#f0f0f0")

    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scroll.set)

    canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scroll.pack(side="right", fill="y")

    root.bind_all("<MouseWheel>", on_mouse_wheel)
    root.bind_all("<Button-4>", on_mouse_wheel)
    root.bind_all("<Button-5>", on_mouse_wheel)

    global answer_vars, start_time
    answer_vars = []

    for idx, q_data in enumerate(questions):
        tk.Label(
            frame,
            text=f"{idx+1}. {q_data.get('Question', 'N/A')}",
            wraplength=750,
            justify="left",
            font=("Arial", 10, "bold"),
            background="#f0f0f0",
            fg="#222"
        ).pack(anchor="w", padx=10, pady=5)

        var = tk.StringVar()
        var.set('')
        answer_vars.append(var)

        question_type = q_data.get("Type", "MCQ").strip().upper()

        if question_type == "MCQ":
            for opt_key in ["A", "B", "C", "D"]:
                option_value = q_data.get(f"Option {opt_key}", "")
                if option_value:
                    tk.Radiobutton(
                        frame,
                        text=f"{opt_key}. {option_value}",
                        variable=var,
                        value=opt_key,
                        font=("Arial", 10),
                        background="#f0f0f0",
                        fg="#444",
                        activebackground="#e0e0e0"
                    ).pack(anchor="w", padx=30)
        elif question_type in ["TF", "TRUE/FALSE", "TRUE OR FALSE", "TRUEFALSE"]:
            for opt_value in ["TRUE", "FALSE"]:
                tk.Radiobutton(
                    frame,
                    text=opt_value,
                    variable=var,
                    value=opt_value,
                    font=("Arial", 10),
                    background="#f0f0f0",
                    fg="#444",
                    activebackground="#e0e0e0"
                ).pack(anchor="w", padx=30)
        elif question_type in ["FIB", "FILL IN THE BLANKS", "FILLUPS"]:
            tk.Entry(
                frame,
                textvariable=var,
                width=50,
                font=("Arial", 10),
                bd=2,
                relief="groove"
            ).pack(anchor="w", padx=30, pady=5)
        else:
            tk.Label(frame, text=f"Error: Unknown question type '{question_type}'. Displaying as MCQ.", font=("Arial", 9, "italic"), fg="red", background="#f0f0f0").pack(anchor="w", padx=10)
            for opt_key in ["A", "B", "C", "D"]:
                option_value = q_data.get(f"Option {opt_key}", "")
                if option_value:
                    tk.Radiobutton(
                        frame,
                        text=f"{opt_key}. {option_value}",
                        variable=var,
                        value=opt_key,
                        font=("Arial", 10),
                        background="#f0f0f0",
                        fg="#444",
                        activebackground="#e0e0e0"
                    ).pack(anchor="w", padx=30)

    tk.Button(
        root,
        text="Submit Test",
        command=submit_quiz,
        bg="#28a745",
        fg="white",
        font=("Arial", 12, "bold"),
        relief="raised",
        bd=3,
        padx=15,
        pady=5
    ).pack(pady=15)

    timer_label = tk.Label(root, text="", font=("Arial", 12, "bold"), fg="#d9534f")
    timer_label.pack(pady=5)
    start_time = time.time()
    update_timer()

def update_timer():
    """
    Updates the countdown timer displayed on the screen every second.
    Automatically submits the quiz when time runs out.
    """
    global timer_label
    if not timer_label or not timer_label.winfo_exists():
        return

    elapsed_time = time.time() - start_time
    remaining_time = TOTAL_TIME - int(elapsed_time)

    mins, secs = divmod(max(0, remaining_time), 60)

    timer_label.config(text=f"🕒 Time left: {mins:02}:{secs:02}")

    if remaining_time <= 0:
        messagebox.showinfo("Time's Up!", "Your time for the test has expired. Submitting your answers automatically.")
        submit_quiz()
    else:
        root.after(1000, update_timer)

def validate_and_start():
    """
    Performs mandatory validation on the first screen's input fields.
    If validation passes, it proceeds to load questions and start the quiz.
    If validation fails, it shows an error message.
    """
    name = name_var.get().strip()
    roll_no = roll_var.get().strip()
    division = div_var.get()
    grade = grade_var.get()

    if not name:
        messagebox.showerror("Validation Error", "Name is a mandatory field. Please enter your full name.")
        return
    
    if not roll_no:
        messagebox.showerror("Validation Error", "Roll Number is a mandatory field. Please enter your roll number.")
        return

    if not division:
        messagebox.showerror("Validation Error", "Division is a mandatory field. Please select your division.")
        return

    if not grade:
        messagebox.showerror("Validation Error", "Grade is a mandatory field. Please select your grade.")
        return
    
    if not roll_no.isdigit():
        messagebox.showerror("Validation Error", "Roll Number must be a number.")
        return

    load_and_start(grade)

def start_screen():
    """
    Displays the initial screen for student information input.
    """
    tk.Label(root, text="📘 Robotics Unit Test", font=("Arial", 20, "bold"), fg="#0056b3").pack(pady=20)

    tk.Label(root, text="Full Name:", font=("Arial", 12)).pack()
    tk.Entry(root, textvariable=name_var, font=("Arial", 12), width=40, bd=2, relief="groove").pack(pady=5)

    tk.Label(root, text="Roll Number:", font=("Arial", 12)).pack()
    tk.Entry(root, textvariable=roll_var, font=("Arial", 12), width=40, bd=2, relief="groove").pack(pady=5)

    tk.Label(root, text="Select Division:", font=("Arial", 12)).pack()
    ttk.Combobox(root, textvariable=div_var, values=("A", "B", "C", "D"), state="readonly", font=("Arial", 12), width=37).pack(pady=5)
    div_var.set("")  

    tk.Label(root, text="Select Grade (5–9):", font=("Arial", 12)).pack()
    ttk.Combobox(root, textvariable=grade_var, values=("5", "6", "7", "8", "9"), state="readonly", font=("Arial", 12), width=37).pack(pady=5)
    grade_var.set("")

    tk.Button(
        root,
        text="Start Quiz",
        bg="#007bff",
        fg="white",
        font=("Arial", 14, "bold"),
        command=validate_and_start,
        relief="raised",
        bd=3,
        padx=20,
        pady=10
    ).pack(pady=30)

def load_and_start(selected_grade):
    """
    Loads questions based on the grade and then proceeds to display the quiz questions.
    """
    global questions
    all_questions = load_questions_from_csv_url()

    if not all_questions:
        messagebox.showerror("No Questions", "Could not load any questions. Please ensure the Google Sheet URL is correct and publicly accessible.")
        return

    questions = filter_questions_by_grade(all_questions, selected_grade)

    if not questions:
        messagebox.showerror("No Questions Found", f"No questions found for Grade {selected_grade}. Please ensure the Google Sheet contains questions for this grade.")
        return

    show_questions()

# --- Application Start ---
if __name__ == "__main__":
    start_screen()
    root.mainloop()