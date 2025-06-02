# import modules
import data
import random as ran
import customtkinter as ctk

# establish variables
score = 1000
answered = {
    "very easy": [],
    "easy": [],
    "normal": [],
    "hard": [],
    "very hard": []
}
difficulty = "normal"
question = ""
Question = ""
Option1 = ""
Option2 = ""
Option3 = ""
Correct = ""
Questions_Answered = 0
Questions_Answered_Correctly = 0


# establish functions
# Function to allow fullscreen to be toggled with <F11>
def toggle_fullscreen(event):
    window.attributes("-fullscreen", not window.attributes("-fullscreen"))
    window.geometry(f"{window.winfo_screenwidth()}x{window.winfo_screenheight()}+0+0")


# function to automatically set customisation for all widgets of a category
def option_button_customisation(window, **configs):
    for widget in window.winfo_children():
        if isinstance(widget, ctk.CTkButton):
            widget.configure(**configs)


def toggle_option_buttons():
    if option1_button.cget("state") == "normal":
        option1_button.configure(state="disabled")
        option2_button.configure(state="disabled")
        option3_button.configure(state="disabled")
        option4_button.configure(state="disabled")
    elif option1_button.cget("state") == "disabled":
        option1_button.configure(state="normal")
        option2_button.configure(state="normal")
        option3_button.configure(state="normal")
        option4_button.configure(state="normal")


# function to create a new question
def new_question():
    global Question, Correct, Option1, Option2, Option3, question, difficulty, answered, score
    score_label.configure(text=score)

    # set current question difficulty based on score
    if score <= 300:
        difficulty = "very easy"
    elif 400 <= score <= 700:
        difficulty = "easy"
    elif 800 <= score <= 1200:
        difficulty = "normal"
    elif 1300 <= score <= 1600:
        difficulty = "hard"
    elif score >= 1700:
        difficulty = "very hard"

# give user a new question; if all questions of a difficulty have been answered reset answered questions for current difficultly
    while True:
        if len(answered[difficulty]) == 15:
            answered[difficulty] = []
        question = ran.randint(0, 14)
        if question in answered[difficulty]:
            continue
        else:
            answered[difficulty].append(question)
            Question = data.chem_set[difficulty][question][0]
            Correct = data.chem_set[difficulty][question][1]
            Option1 = data.chem_set[difficulty][question][2]
            Option2 = data.chem_set[difficulty][question][3]
            Option3 = data.chem_set[difficulty][question][4]
            break
    options = [Correct, Option1, Option2, Option3]
    ran.shuffle(options)
    option1_button.configure(text=options[0])
    option2_button.configure(text=options[1])
    option3_button.configure(text=options[2])
    option4_button.configure(text=options[3])
    question_label.configure(text=Question)
    option1_button.configure(fg_color="#263d75")
    option2_button.configure(fg_color="#263d75")
    option3_button.configure(fg_color="#263d75")
    option4_button.configure(fg_color="#263d75")
    option1_button.configure(hover_color="#3f5996")
    option2_button.configure(hover_color="#3f5996")
    option3_button.configure(hover_color="#3f5996")
    option4_button.configure(hover_color="#3f5996")
    if option1_button.cget("state") == "disabled":
        toggle_option_buttons()


def start_button_event():
    start_button.pack_forget()
    chem_button.pack()


def chem_start():
    chem_button.pack_forget()
    option1_button.pack()
    option2_button.pack()
    option3_button.pack()
    option4_button.pack()
    new_question()


# functions for option buttons
# function for option 1 button when pressed
def option1_button_event():
    global score, Questions_Answered, Questions_Answered_Correctly
    Questions_Answered += 1
    if option1_button.cget("text") == Correct:
        Questions_Answered_Correctly += 1
        option1_button.configure(fg_color="green")
        option1_button.configure(hover_color="green")
        # Adjust score (*if* prevents negative score or too high score)
        if score <= 1900:
            score += 100
    else:
        option1_button.configure(fg_color="red")
        option1_button.configure(hover_color="red")
        for widget in window.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") == Correct:
                widget.configure(fg_color="green")
                widget.configure(hover_color="green")
        if score >= 100:
            score -= 100
    toggle_option_buttons()
    option1_button.after(1, option1_button.update)
    option1_button.after(600, new_question)


# function for option 2 button when pressed
def option2_button_event():
    global score, Questions_Answered, Questions_Answered_Correctly
    Questions_Answered += 1
    if option2_button.cget("text") == Correct:
        Questions_Answered_Correctly += 1
        option2_button.configure(fg_color="green")
        option2_button.configure(hover_color="green")
        # Adjust score (*if* prevents negative score or too high score)
        if score <= 1900:
            score += 100
    else:
        option2_button.configure(fg_color="red")
        option2_button.configure(hover_color="red")
        for widget in window.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") == Correct:
                widget.configure(fg_color="green")
                widget.configure(hover_color="green")
        if score >= 100:
            score -= 100
    toggle_option_buttons()
    option2_button.after(1, option2_button.update)
    option2_button.after(600, new_question)


# function for option 3 button when pressed
def option3_button_event():
    global score, Questions_Answered, Questions_Answered_Correctly
    Questions_Answered += 1
    if option3_button.cget("text") == Correct:
        Questions_Answered_Correctly += 1
        option3_button.configure(fg_color="green")
        option3_button.configure(hover_color="green")
        # Adjust score (*if* prevents negative score or too high score)
        if score <= 1900:
            score += 100
    else:
        option3_button.configure(fg_color="red")
        option3_button.configure(hover_color="red")
        for widget in window.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") == Correct:
                widget.configure(fg_color="green")
                widget.configure(hover_color="green")
        if score >= 100:
            score -= 100
    toggle_option_buttons()
    option3_button.after(1, option3_button.update)
    option3_button.after(600, new_question)


# function for option 4 button when pressed
def option4_button_event():
    global score, Questions_Answered, Questions_Answered_Correctly
    Questions_Answered += 1
    if option4_button.cget("text") == Correct:
        Questions_Answered_Correctly += 1
        option4_button.configure(fg_color="green")
        option4_button.configure(hover_color="green")
        # Adjust score (*if* prevents negative score or too high score)
        if score <= 1900:
            score += 100
    else:
        option4_button.configure(fg_color="red")
        option4_button.configure(hover_color="red")
        for widget in window.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") == Correct:
                widget.configure(fg_color="green")
                widget.configure(hover_color="green")
        if score >= 100:
            score -= 100
    toggle_option_buttons()
    option4_button.after(1, option4_button.update)
    option4_button.after(600, new_question)


# create window
window = ctk.CTk()
window.title("AS 91896v1 Quiz")
window.attributes("-fullscreen", True)
window.geometry(f"{window.winfo_screenwidth()}x{window.winfo_screenheight()}+0+0")
window.bind("<F11>", toggle_fullscreen)

# create labels
# Question Label
question_label = ctk.CTkLabel(
    window,
    text=Question,
    font=("Sans-serif", 24)
)
question_label.pack()

# score label
score_label = ctk.CTkLabel(
    window,
    text=str(score),
)
score_label.pack()

# create buttons
# start button
start_button = ctk.CTkButton(
    window,
    text="Start",
    font=("Sans-serif", 24),
    command=start_button_event,
    fg_color="#263d75",
    hover_color="#3f5996"
)
start_button.pack()

# quiz selection buttons
chem_button = ctk.CTkButton(
    window,
    text="Chemistry Quiz",
    command=chem_start,
    fg_color="#263d75",
    hover_color="#3f5996",
    font=("Sans-serif", 20),
)

# option buttons
option1_button = ctk.CTkButton(
    window,
    text=Option1,
    command=option1_button_event
)
option1_button.pack_forget()

option2_button = ctk.CTkButton(
    window,
    text=Option2,
    command=option2_button_event
)
option2_button.pack_forget()

option3_button = ctk.CTkButton(
    window,
    text=Option3,
    command=option3_button_event
)
option3_button.pack_forget()

option4_button = ctk.CTkButton(
    window,
    text=Correct,
    command=option4_button_event
)
option4_button.pack_forget()


# set default customisations for widgets
option_button_customisation(
    window,
    fg_color="#263d75",
    hover_color="#3f5996",
    font=("Sans-serif", 20),
    state="normal"
    )

# run window
window.mainloop()
