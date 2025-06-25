import tkinter as tk
from tkinter import messagebox
import random

# Define the connection groups
groups = {
    "Live in Ashdod": ["Daniel V", "Daniel K", "Lior D", "Nicole S"],
    "Mitpalelim": ["Arnon O", "Liel R", "Orel B", "Yaakov G"],
    "Family name starts with M": ["Daniel M", "Dotan M", "Hadas M", "Maya N"],
    "Hantarim going in and out": ["Ekaterina Z", "Ethan D", "Maayan B", "Ido G"]
}

# Prepare word list
all_words = sum(groups.values(), [])
random.shuffle(all_words)

# Game state
selected_words = []
matched_groups = []
remaining_words = all_words.copy()
current_grid_order = remaining_words.copy()

# GUI setup
root = tk.Tk()
root.title("Connection Game")

# Frames
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

control_frame = tk.Frame(root)
control_frame.pack(pady=10)

buttons = {}

def reshuffle_and_render():
    """Render the grid, showing matched groups and active buttons."""
    for widget in button_frame.winfo_children():
        widget.destroy()

    row = 0

    # Show matched groups
    for group_name, words in matched_groups:
        lbl = tk.Label(button_frame, text=f"Group: {group_name}", font=("Arial", 14, "bold"))
        lbl.grid(row=row, column=0, columnspan=4, pady=(10, 0))
        row += 1
        for i, word in enumerate(words):
            lbl_word = tk.Label(button_frame, text=word, width=14, height=3,
                                bg="lightgray", relief="groove", font=("Helvetica", 14))
            lbl_word.grid(row=row, column=i, padx=5, pady=5)
        row += 1

    # Show remaining words
    buttons.clear()
    for i, word in enumerate(current_grid_order):
        selected = word in selected_words
        btn = tk.Button(
            button_frame,
            text=word,
            width=14,
            height=2,
            font=("Helvetica", 14, "bold" if selected else "normal"),
            bg="lightblue" if selected else "SystemButtonFace",
            activebackground="lightblue",
            relief="sunken" if selected else "raised",
            command=lambda w=word: on_word_click(w)
        )
        btn.grid(row=row + i // 4, column=i % 4, padx=5, pady=5)
        buttons[word] = btn

def on_word_click(word):
    """Toggle selection of word."""
    if word in selected_words:
        selected_words.remove(word)
    else:
        if len(selected_words) < 4:
            selected_words.append(word)
    reshuffle_and_render()

def check_selection():
    global current_grid_order

    if len(selected_words) != 4:
        messagebox.showinfo("Notice", "Please select exactly 4 words.")
        return

    selected_set = set(selected_words)

    # Full match
    for group_name, words in groups.items():
        if selected_set == set(words):
            matched_groups.append((group_name, words))
            for word in words:
                if word in remaining_words:
                    remaining_words.remove(word)
            messagebox.showinfo("Correct!", f"The connection is: {group_name}")
            selected_words.clear()
            current_grid_order = remaining_words.copy()
            random.shuffle(current_grid_order)
            reshuffle_and_render()
            return

    # 3/4 match
    for words in groups.values():
        if len(selected_set.intersection(set(words))) == 3:
            messagebox.showinfo("Almost!", "3 of your selected words belong to the same group.")
            break
    else:
        messagebox.showwarning("Wrong", "These words are not a known group.")

    selected_words.clear()
    reshuffle_and_render()

# Check button
check_btn = tk.Button(control_frame, text="Check Answer", font=("Arial", 14), command=check_selection)
check_btn.pack()

# Start the game
reshuffle_and_render()
root.mainloop()
