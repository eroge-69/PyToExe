import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import random

def convert_xls_to_txt():
    # Select input file
    input_file = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel files", "*.xls *.xlsx")]
    )
    if not input_file:
        return

    # Select output file
    output_file = filedialog.asksaveasfilename(
        title="Save Output Text File",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")]
    )
    if not output_file:
        return

    try:
        df = pd.read_excel(input_file)

        # Prepare output lines
        output_lines = []

        # --- Row 1: Answer key ---
        answer_key = "00000"
        key_answers = []  # store keys for later checking
        for col in df.columns:
            if "Q" in col and "Key" in col:   # find answer key columns
                value = df[col].iloc[0] if not pd.isna(df[col].iloc[0]) else "Z"
                key_val = str(value).strip() if str(value).strip() else "Z"
                answer_key += key_val
                key_answers.append(key_val)
        output_lines.append(answer_key)

        # --- Row 2: 00000 + 1s until same length as Row 1 ---
        row2 = "00000" + "1" * (len(answer_key) - 5)
        output_lines.append(row2)

        # --- Row 3+: Roll No (padded to 5 digits) + Answers ---
        for i in range(len(df)):
            roll_no = str(df["Roll No"].iloc[i]).split('.')[0] if not pd.isna(df["Roll No"].iloc[i]) else "0"
            roll_no = roll_no.zfill(5)  # pad to 5 digits

            row_str = roll_no
            q_index = 0  # track which question we are on

            for col in df.columns:
                if "Q" in col and "Options" in col:
                    value = df[col].iloc[i] if not pd.isna(df[col].iloc[i]) else ""
                    ans = str(value).strip()

                    if ans == "":  
                        # pick a wrong answer different from key
                        all_choices = ["A", "B", "C", "D", "E"]
                        correct = key_answers[q_index] if q_index < len(key_answers) else "Z"
                        wrong_choices = [x for x in all_choices if x != correct]
                        ans = random.choice(wrong_choices) if wrong_choices else "Z"

                    row_str += ans
                    q_index += 1

            output_lines.append(row_str)

        # Save to text file
        with open(output_file, "w") as f:
            for line in output_lines:
                f.write(line + "\n")

        messagebox.showinfo("Success", f"Conversion completed!\nSaved as:\n{output_file}")

    except Exception as e:
        messagebox.showerror("Error", str(e))

def show_about():
    messagebox.showinfo("About", "EvalBee Report to Buksu Item Analyzer\n\nProgram by:\nMark Daniel G. Dacer, MSIT")

# --- GUI Setup ---
root = tk.Tk()
root.title("EvalBee Report to Buksu Item Analyzer")

# --- Center the window on screen ---
window_width = 400
window_height = 200

# Get the screen dimension
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Find the center point
center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)

# Set the position of the window to the center of the screen
root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

# Convert button
btn_convert = tk.Button(root, text="Convert XLS to TXT", command=convert_xls_to_txt, height=2, width=25)
btn_convert.pack(expand=True, pady=10)

# About button
btn_about = tk.Button(root, text="About", command=show_about, width=10)
btn_about.pack(pady=5)

root.mainloop()
