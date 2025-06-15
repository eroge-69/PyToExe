import tkinter as tk
from tkinter import ttk
import random
import pyperclip

# Generate valid card numbers using Luhn algorithm
def generate_valid_card(card_number_template):
    # Find all positions of 'x'
    x_positions = [i for i, char in enumerate(card_number_template) if char == 'x']
    
    if not x_positions:
        return card_number_template
    
    # Generate random digits for all x's except last
    temp_card = list(card_number_template)
    for pos in x_positions[:-1]:
        temp_card[pos] = random.choice('0123456789')
    
    # Set last x to 0 temporarily
    last_x_pos = x_positions[-1]
    temp_card[last_x_pos] = '0'
    temp_card_str = ''.join(temp_card)
    
    # Remove non-digit characters for Luhn calculation
    digits = ''.join(filter(str.isdigit, temp_card_str))
    
    # Calculate Luhn check digit
    total = 0
    for i, digit in enumerate(reversed(digits)):
        num = int(digit)
        if i % 2 == 1:
            num *= 2
            if num > 9:
                num -= 9
        total += num
    
    check_digit = (10 - (total % 10)) % 10
    temp_card[last_x_pos] = str(check_digit)
    
    return ''.join(temp_card)

# Generate card details
def generate_card(card_number_template, expiry_month, expiry_year, cvv, num_cards, include_script):
    generated_cards = []
    unique_cards = set()
    
    for _ in range(num_cards * 2):  # Generate extra to account for duplicates
        if len(generated_cards) >= num_cards:
            break
            
        # Generate valid card number
        card_number = generate_valid_card(card_number_template)
        
        # Remove non-digits for uniqueness check
        card_digits = ''.join(filter(str.isdigit, card_number))
        
        # Skip duplicates
        if card_digits in unique_cards:
            continue
            
        unique_cards.add(card_digits)
        
        # Format card info based on selection
        if include_script.get():
            # Format expiry date
            expiry_date = f"{expiry_month:02d}|{str(expiry_year)[2:]}"
            card_info = f"{card_number}|{expiry_date}"
            
            # Add CVV if provided
            if cvv:
                card_info += f"|{cvv}"
        else:
            card_info = card_number
            
        generated_cards.append(card_info)
        
    return generated_cards

def on_generate():
    try:
        card_number_template = entry_card_number.get()
        expiry_month = int(combo_month.get())
        expiry_year = int(combo_year.get())
        cvv = entry_cvv.get() if entry_cvv.get() else None
        num_cards = int(combo_num_cards.get())
        
        if not card_number_template or not num_cards:
            return

        result = generate_card(card_number_template, expiry_month, expiry_year, cvv, num_cards, include_script)
        
        result_text.delete(1.0, tk.END)
        for card in result:
            result_text.insert(tk.END, card + '\n')
    except Exception:
        pass

def on_copy():
    try:
        card_text = result_text.get(1.0, tk.END).strip()
        if card_text:
            pyperclip.copy(card_text)
    except Exception:
        pass

def create_context_menu(event):
    context_menu = tk.Menu(window, tearoff=0)
    focused_widget = window.focus_get()
    
    if isinstance(focused_widget, (tk.Entry, tk.Text)):
        context_menu.add_command(label="Cut", command=lambda: focused_widget.event_generate("<<Cut>>"))
        context_menu.add_command(label="Copy", command=lambda: focused_widget.event_generate("<<Copy>>"))
        context_menu.add_command(label="Paste", command=lambda: focused_widget.event_generate("<<Paste>>"))
    
    try:
        context_menu.tk_popup(event.x_root, event.y_root)
    finally:
        context_menu.grab_release()

# Create main window
window = tk.Tk()
window.title("⚡ Valid Credit Card Generator ⚡")
window.geometry("480x700")
window.resizable(True, True)

# Bind right-click event
window.bind("<Button-3>", create_context_menu)

# Apply modern style
style = ttk.Style()
style.configure("TFrame", background="#f0f0f0")
style.configure("TLabel", background="#f0f0f0", font=("Arial", 11))
style.configure("TButton", font=("Arial", 11))
style.configure("Header.TLabel", font=("Arial", 14, "bold"))
style.configure("TLabelFrame", font=("Arial", 11, "bold"))

# Main container
main_frame = ttk.Frame(window, padding=(12, 10))
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Header
header = ttk.Label(main_frame, text="☠BY JACKSON & KARAM☠", style="Header.TLabel")
header.grid(row=0, column=0, pady=(0, 12))

# Card Number Section
card_number_frame = ttk.LabelFrame(main_frame, text="Card Template (BIN)", padding=(8, 6))
card_number_frame.grid(row=1, column=0, sticky="we", pady=4, padx=4)

label_card_number = ttk.Label(card_number_frame, text="Enter card template (xxxx-xxxx-xxxx-xxxx):")
label_card_number.pack(anchor="w", padx=5, pady=(0, 4))

entry_card_number = ttk.Entry(card_number_frame, width=35, font=("Arial", 11))
entry_card_number.pack(fill=tk.X, padx=5, pady=(0, 4))
entry_card_number.insert(0, "xxxx-xxxx-xxxx-xxxx")

# Number of Cards and Options Section
cards_options_frame = ttk.Frame(main_frame)
cards_options_frame.grid(row=2, column=0, sticky="we", pady=8, padx=4)

# Number of Cards Section
num_cards_frame = ttk.LabelFrame(cards_options_frame, text="Number of Cards", padding=(8, 6))
num_cards_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

label_num_cards = ttk.Label(num_cards_frame, text="Cards to generate (10-500):")
label_num_cards.pack(anchor="w", padx=5, pady=(0, 4))

combo_num_cards = ttk.Combobox(num_cards_frame, values=[str(i) for i in range(10, 501, 10)], width=10, font=("Arial", 11))
combo_num_cards.set("10")
combo_num_cards.pack(anchor="w", padx=5, pady=(0, 4))

# Script Options Section
include_script = tk.BooleanVar(value=True)
chk_include_script = ttk.Checkbutton(num_cards_frame, 
                                    text="Include expiry and CVV",
                                    variable=include_script)
chk_include_script.pack(anchor="w", padx=5, pady=(5, 0))

# Buttons Section
button_frame = ttk.Frame(cards_options_frame)
button_frame.pack(side=tk.LEFT, fill=tk.Y, pady=4)

btn_generate = ttk.Button(button_frame, text="Generate", command=on_generate, width=12)
btn_generate.pack(pady=4)

btn_copy = ttk.Button(button_frame, text="Copy Results", command=on_copy, width=12)
btn_copy.pack(pady=4)

# Expiry Date and CVV Section
expiry_cvv_frame = ttk.Frame(main_frame)
expiry_cvv_frame.grid(row=3, column=0, sticky="we", pady=4, padx=4)

# Expiry Date Section
expiry_frame = ttk.LabelFrame(expiry_cvv_frame, text="Expiry Date", padding=(8, 6))
expiry_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

label_expiry = ttk.Label(expiry_frame, text="Select month and year:")
label_expiry.pack(anchor="w", padx=5, pady=(0, 4))

date_container = ttk.Frame(expiry_frame)
date_container.pack(fill=tk.X, padx=5)

# Month selection
month_label = ttk.Label(date_container, text="Month:")
month_label.pack(side=tk.LEFT, padx=(0, 8))

combo_month = ttk.Combobox(date_container, values=[f"{i:02d}" for i in range(1, 13)], width=4, font=("Arial", 11))
combo_month.set("01")
combo_month.pack(side=tk.LEFT, padx=(0, 16))

# Year selection
year_label = ttk.Label(date_container, text="Year:")
year_label.pack(side=tk.LEFT, padx=(0, 8))

combo_year = ttk.Combobox(date_container, values=[str(year) for year in range(2025, 2036)], width=6, font=("Arial", 11))
combo_year.set("2025")
combo_year.pack(side=tk.LEFT)

# CVV Section
cvv_frame = ttk.LabelFrame(expiry_cvv_frame, text="CVV (optional)", padding=(8, 6))
cvv_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

label_cvv = ttk.Label(cvv_frame, text="Enter CVV")
label_cvv.pack(anchor="w", padx=5, pady=(0, 4))

entry_cvv = ttk.Entry(cvv_frame, width=15, font=("Arial", 11))
entry_cvv.pack(anchor="w", padx=5, pady=(0, 4))

# Results Section
results_frame = ttk.LabelFrame(main_frame, text="Results (Valid Cards)", padding=(8, 6))
results_frame.grid(row=4, column=0, sticky="nsew", pady=8, padx=4)
results_frame.grid_rowconfigure(0, weight=1)
results_frame.grid_columnconfigure(0, weight=1)

text_frame = ttk.Frame(results_frame)
text_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

# Large results text box
result_text = tk.Text(text_frame, wrap=tk.WORD, font=("Courier New", 11))
result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Bind keyboard shortcuts for results text box
result_text.bind("<Control-v>", lambda e: result_text.event_generate("<<Paste>>"))
result_text.bind("<Control-x>", lambda e: result_text.event_generate("<<Cut>>"))
result_text.bind("<Control-c>", lambda e: result_text.event_generate("<<Copy>>"))

scrollbar = ttk.Scrollbar(text_frame, command=result_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
result_text.config(yscrollcommand=scrollbar.set)

# Set weights for expansion
main_frame.grid_rowconfigure(0, weight=0)
main_frame.grid_rowconfigure(1, weight=0)
main_frame.grid_rowconfigure(2, weight=0)
main_frame.grid_rowconfigure(3, weight=0)
main_frame.grid_rowconfigure(4, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

# Start the application
window.mainloop()