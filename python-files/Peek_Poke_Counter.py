import tkinter as tk
from tkinter import messagebox

# Terms to count
terms = [
    "MEC1/COMMAND_LANE",
    "MEC1/MONITOR_LANE",
    "MEC2/COMMAND_LANE",
    "MEC2/MONITOR_LANE"
]

# Function to count terms
def count_terms():
    text = text_box.get("1.0", tk.END)
    results = []
    for term in terms:
        count = text.count(term)
        results.append(f"{term}: {count}")
    messagebox.showinfo("Term Count Results", "\n".join(results))

# Function to reset the text box
def reset_text():
    text_box.delete("1.0", tk.END)

# Create main window
window = tk.Tk()
window.title("Term Counter")
window.geometry("800x600")

# Large text box
text_box = tk.Text(window, wrap=tk.WORD, font=("Arial", 12))
text_box.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

# Buttons frame
button_frame = tk.Frame(window)
button_frame.pack(pady=10)

# Count button
count_button = tk.Button(button_frame, text="Count", command=count_terms, width=15)
count_button.pack(side=tk.LEFT, padx=10)

# Reset button
reset_button = tk.Button(button_frame, text="Reset", command=reset_text, width=15)
reset_button.pack(side=tk.LEFT, padx=10)

# Run the application
window.mainloop()
