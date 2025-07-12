import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyautogui
import time
import json

# Global action list
actions = []

# Function to pick screen coordinates
def pick_position()
    messagebox.showinfo(Pick Position, Move your mouse to the desired position. Coordinates will be picked in 3 seconds.)
    time.sleep(3)
    x, y = pyautogui.position()
    entry_x.delete(0, tk.END)
    entry_x.insert(0, str(x))
    entry_y.delete(0, tk.END)
    entry_y.insert(0, str(y))

# Add an action to the list
def add_action()
    try
        action = {
            x int(entry_x.get()),
            y int(entry_y.get()),
            type action_type.get(),
            delay int(entry_delay.get()),
            cursor_back cursor_back_var.get(),
            repeat 1,
            comment entry_comment.get()
        }
        actions.append(action)
        update_table()
    except ValueError
        messagebox.showerror(Error, Invalid input. Check your coordinates and delay.)

# Update the action table
def update_table()
    for item in tree.get_children()
        tree.delete(item)
    for idx, act in enumerate(actions)
        tree.insert('', 'end', values=(idx+1, act['type'], act['x'], act['y'], act['delay'], act['repeat'], act['comment']))

# Delete selected action
def delete_selected()
    selected = tree.selection()
    if selected
        index = tree.index(selected[0])
        actions.pop(index)
        update_table()

# Delete all actions
def delete_all()
    actions.clear()
    update_table()

# Save script to file
def save_script()
    file = filedialog.asksaveasfilename(defaultextension=.json, filetypes=[(JSON Files, .json)])
    if file
        with open(file, 'w') as f
            json.dump(actions, f)

# Load script from file
def load_script()
    global actions
    file = filedialog.askopenfilename(filetypes=[(JSON Files, .json)])
    if file
        with open(file, 'r') as f
            actions = json.load(f)
        update_table()

# Execute the action list
def start_execution()
    repeat_count = int(entry_script_repeat.get())
    for _ in range(repeat_count)
        for act in actions
            original_pos = pyautogui.position()
            pyautogui.moveTo(act['x'], act['y'])
            time.sleep(act['delay']  1000)
            pyautogui.click(button='left' if act['type'] == 'Left Click' else 'right')
            if act['cursor_back']
                pyautogui.moveTo(original_pos)

# Main GUI setup
root = tk.Tk()
root.title(Untitled - Auto Mouse Click)

# AddEdit Panel
frame_edit = tk.LabelFrame(root, text=Add  Edit Action)
frame_edit.grid(row=0, column=0, padx=10, pady=5, sticky=w)

entry_x = tk.Entry(frame_edit, width=6)
entry_y = tk.Entry(frame_edit, width=6)
entry_x.grid(row=0, column=1)
entry_y.grid(row=0, column=3)

tk.Label(frame_edit, text=X Co-ordinate).grid(row=0, column=0)
tk.Label(frame_edit, text=Y Co-ordinate).grid(row=0, column=2)
tk.Button(frame_edit, text=Pick, command=pick_position).grid(row=0, column=4, padx=5)

action_type = ttk.Combobox(frame_edit, values=[Left Click, Right Click], state=readonly, width=15)
action_type.set(Left Click)
action_type.grid(row=1, column=1)
tk.Label(frame_edit, text=Action Type).grid(row=1, column=0)

cursor_back_var = tk.BooleanVar()
tk.Checkbutton(frame_edit, text=Cursor Back, variable=cursor_back_var).grid(row=1, column=2)

entry_delay = tk.Entry(frame_edit, width=6)
entry_delay.grid(row=1, column=4)
tk.Label(frame_edit, text=Delay before Action).grid(row=1, column=3)
tk.Label(frame_edit, text=Milli Second(s)).grid(row=1, column=5)

entry_comment = tk.Entry(frame_edit, width=50)
entry_comment.grid(row=2, column=1, columnspan=5, pady=5)
tk.Label(frame_edit, text=Comment).grid(row=2, column=0)

# Buttons
tk.Button(root, text=Add, width=8, command=add_action).grid(row=0, column=1)
tk.Button(root, text=Update, width=8).grid(row=0, column=2)
tk.Button(root, text=Load, width=8, command=load_script).grid(row=0, column=3)
tk.Button(root, text=Save, width=8, command=save_script).grid(row=0, column=4)

# Script Repeat and Execution
tk.Label(root, text=Script Repeat).grid(row=1, column=1)
entry_script_repeat = tk.Entry(root, width=5)
entry_script_repeat.insert(0, 1)
entry_script_repeat.grid(row=1, column=2)
tk.Button(root, text=Start, width=8, command=start_execution).grid(row=1, column=3)

# Action List Table
columns = (Sr, Action, X, Y, Delay, Repeat, Comment)
tree = ttk.Treeview(root, columns=columns, show=headings)
for col in columns
    tree.heading(col, text=col)
    tree.column(col, width=80)
tree.grid(row=2, column=0, columnspan=5, padx=10, pady=5)

# Control buttons
tk.Button(root, text=Move Up).grid(row=2, column=5, sticky=n, pady=2)
tk.Button(root, text=Move Down).grid(row=2, column=5, pady=2)
tk.Button(root, text=Delete, command=delete_selected).grid(row=2, column=5, sticky=s, pady=2)
tk.Button(root, text=Delete All, command=delete_all).grid(row=2, column=5, sticky=se, pady=2)

root.mainloop()
