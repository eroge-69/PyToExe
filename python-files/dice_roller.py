import random
import re
import tkinter as tk
from tkinter import messagebox

def roll_dice(sides=6):
	if savage_attacker.get() == 1 and sides >= 3: 
		return random.randint(3, sides)
	return random.randint(1, sides)

def roll_dice_formula(formula):
	match = re.match(r'(\d+)d(\d+)(?:\s+(\w+))?', formula)
	if match:
		num_dice = int(match.group(1))
		sides = int(match.group(2))
		damage_type = match.group(3) if match.group(3) else "generic" 
		rolls = [roll_dice(sides) for _ in range(num_dice)]
		label_text = roll_label.cget("text")
		label_text += f"Rolling {num_dice}d{sides} ({damage_type}): " + ", ".join(map(str, rolls)) + " = " + str(sum(rolls)) + "\n"
		roll_label.config(text=label_text)
		return rolls, damage_type
	else:
		raise ValueError(f"Invalid dice formula: {formula}")

def evaluate_expression(expression):
	def dice_roll(match):
		rolls, _ = roll_dice_formula(match.group(0)) 
		return str(sum(rolls)) 
	expression = re.sub(r'\d+d\d+(?:\s+\w+)?', dice_roll, expression)
	try:
		return eval(expression)  
	except Exception as e:
		raise ValueError(f"Invalid expression: {expression}")

def roll_dice_gui():
	formula = formula_entry.get().strip().lower()
	try:
		roll_label.config(text=" ")
		result = evaluate_expression(formula)
		result_label.config(text=f"Result: {result}")
	except ValueError as e:
		messagebox.showerror("Error", str(e))


# Create the main window for the GUI
root = tk.Tk()
root.title("Dice Roller")



# Input field for dice formula
formula_label = tk.Label(root, text="Enter Expression (e.g., '2d6 fire + 3d4 cold - 5'):")
formula_label.pack(pady=5)
formula_entry = tk.Entry(root, width=30)
formula_entry.pack(pady=5)

# Use tk.IntVar for the Checkbutton variable
savage_attacker = tk.IntVar()

# Button for savage attacker feat (rerolls)
savage_button = tk.Checkbutton(root, text="Savage Attacker", variable=savage_attacker, onvalue=1, offvalue=0)
savage_button.pack(pady=10)

# Button to roll the dice
roll_button = tk.Button(root, text="Roll Dice", command=roll_dice_gui)
roll_button.pack(pady=10)

# Label to display results
result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.pack(pady=10)

roll_label = tk.Label(root, text="Enter your dice formula and roll!", font=("Arial", 14))
roll_label.pack(pady=10)

# Run the GUI
root.mainloop()



