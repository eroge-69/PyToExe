import tkinter as tk
from tkinter import messagebox, colorchooser
import requests
import json

# -------------------- Theme System --------------------
custom_bg_color = "#2C2F33"
custom_entry_color = "#333333"
custom_text_color = "#FFFFFF"

themes = {
    "Light": {
        "bg": "#F0F0F0",
        "fg": "#000000",
        "entry_bg": "#FFFFFF",
        "button_bg": "#4CAF50",
        "button_fg": "#FFFFFF",
        "highlight": "#CCCCCC"
    },
    "Dark": {
        "bg": "#2C2F33",
        "fg": "#FFFFFF",
        "entry_bg": "#23272A",
        "button_bg": "#7289DA",
        "button_fg": "#FFFFFF",
        "highlight": "#444444"
    },
    "Custom": {
        "bg": custom_bg_color,
        "fg": custom_text_color,
        "entry_bg": custom_entry_color,
        "button_bg": "#00A86B",
        "button_fg": "#FFFFFF",
        "highlight": "#444444"
    }
}

styled_widgets = []

def apply_theme():
    style = themes[theme_var.get()]
    root.config(bg=style["bg"])
    canvas.config(bg=style["bg"])
    scroll_frame.config(bg=style["bg"])
    for widget in styled_widgets:
        if isinstance(widget, (tk.Entry, tk.Text)):
            widget.config(bg=style["entry_bg"], fg=style["fg"], insertbackground=style["fg"],
                          highlightbackground=style["highlight"], highlightthickness=1)
        elif isinstance(widget, tk.Label):
            widget.config(bg=style["bg"], fg=style["fg"])
        elif isinstance(widget, tk.OptionMenu):
            widget.config(bg=style["entry_bg"], fg=style["fg"], highlightbackground=style["highlight"])
        elif isinstance(widget, tk.Button):
            widget.config(bg=style["button_bg"], fg=style["button_fg"], activebackground=style["highlight"])

def on_theme_change(*args):
    if theme_var.get() == "Custom":
        color = colorchooser.askcolor(title="Choose Background Color")[1]
        if color:
            themes["Custom"]["bg"] = color
        entry_color = colorchooser.askcolor(title="Choose Entry/Textbox Color")[1]
        if entry_color:
            themes["Custom"]["entry_bg"] = entry_color
        text_color = colorchooser.askcolor(title="Choose Text Color")[1]
        if text_color:
            themes["Custom"]["fg"] = text_color
    apply_theme()

# -------------------- Discord Send Function --------------------
def send_to_discord():
    webhook_url = webhook_entry.get().strip()
    username = username_entry.get().strip()
    unit_name = unit_name_entry.get().strip()
    unit_desc = unit_desc_entry.get("1.0", tk.END).strip()
    realism = realism_var.get()
    if realism == "Other":
        realism = realism_other_entry.get().strip() or "Other"
    operations = operations_entry.get().strip()
    era = era_var.get()
    if era == "Other":
        era = era_other_entry.get().strip() or "Other"
    timezone = timezone_entry.get().strip()
    language = language_entry.get().strip()
    recruiter = recruiter_entry.get().strip()
    roles = roles_entry.get().strip()
    discord = discord_entry.get().strip()
    image_url = image_url_entry.get().strip()

    if not webhook_url:
        messagebox.showerror("Error", "Webhook URL cannot be empty!")
        return
    if not unit_name or not unit_desc:
        messagebox.showerror("Error", "Unit Name and Description are required!")
        return

    embed = {
        "title": unit_name,
        "description": unit_desc,
        "color": 3447003,
        "fields": [
            {"name": "Type of Realism", "value": realism, "inline": True},
            {"name": "Types of Operations", "value": operations or "N/A", "inline": True},
            {"name": "Era", "value": era or "N/A", "inline": True},
            {"name": "Timezone", "value": timezone or "N/A", "inline": True},
            {"name": "Language", "value": language or "N/A", "inline": True},
            {"name": "Recruiter", "value": recruiter or "N/A", "inline": True},
            {"name": "Roles Available", "value": roles or "N/A", "inline": False},
            {"name": "Discord", "value": discord or "N/A", "inline": False},
        ]
    }

    if image_url:
        embed["image"] = {"url": image_url}

    payload = {"username": username or "Unit Poster Bot", "embeds": [embed]}

    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 204:
            messagebox.showinfo("Success", "Unit info sent to Discord!")
        else:
            messagebox.showerror("Error", f"Failed to send. Status Code: {response.status_code}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# -------------------- GUI --------------------
root = tk.Tk()
root.title("Discord Unit Sender")
root.geometry("700x800")

# Scrollable frame
canvas = tk.Canvas(root, borderwidth=0, highlightthickness=0)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

scroll_frame = tk.Frame(canvas)
scroll_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

scroll_frame.bind("<Configure>", on_frame_configure)

def create_labeled_entry(label_text):
    label = tk.Label(scroll_frame, text=label_text)
    label.pack(anchor="w", pady=(10, 0), padx=10)
    entry = tk.Entry(scroll_frame)
    entry.pack(fill="x", padx=10)
    styled_widgets.extend([label, entry])
    return entry

# -------------------- Theme Section --------------------
theme_var = tk.StringVar(value="Dark")
theme_label = tk.Label(scroll_frame, text="Select Theme:")
theme_label.pack(anchor="w", pady=(10, 0), padx=10)
theme_menu = tk.OptionMenu(scroll_frame, theme_var, "Light", "Dark", "Custom")
theme_menu.pack(fill="x", padx=10)
theme_var.trace("w", on_theme_change)
styled_widgets.extend([theme_label, theme_menu])

# -------------------- Input Fields --------------------
webhook_entry = create_labeled_entry("Webhook URL:")
username_entry = create_labeled_entry("Username (optional):")
unit_name_entry = create_labeled_entry("Unit Name:")

desc_label = tk.Label(scroll_frame, text="Unit Description:")
desc_label.pack(anchor="w", pady=(10, 0), padx=10)
unit_desc_entry = tk.Text(scroll_frame, height=4)
unit_desc_entry.pack(fill="x", padx=10)
styled_widgets.extend([desc_label, unit_desc_entry])

# Realism
realism_label = tk.Label(scroll_frame, text="Type of Realism:")
realism_label.pack(anchor="w", pady=(10, 0), padx=10)
realism_var = tk.StringVar(value="Realism")
realism_menu = tk.OptionMenu(scroll_frame, realism_var, "Realism", "Semi-Realism", "Relaxed", "Other")
realism_menu.pack(fill="x", padx=10)
realism_other_entry = tk.Entry(scroll_frame)
realism_other_entry.pack(fill="x", padx=10, pady=(0, 5))
styled_widgets.extend([realism_label, realism_menu, realism_other_entry])
def toggle_realism_entry(*args):
    realism_other_entry.config(state="normal" if realism_var.get() == "Other" else "disabled")
realism_var.trace("w", toggle_realism_entry)
toggle_realism_entry()

operations_entry = create_labeled_entry("Types of Operations:")

# Era
era_label = tk.Label(scroll_frame, text="Era:")
era_label.pack(anchor="w", pady=(10, 0), padx=10)
era_var = tk.StringVar(value="Modern")
era_menu = tk.OptionMenu(scroll_frame, era_var, "Vietnam", "WW1", "WW2", "Modern", "Futuristic", "Other")
era_menu.pack(fill="x", padx=10)
era_other_entry = tk.Entry(scroll_frame)
era_other_entry.pack(fill="x", padx=10, pady=(0, 5))
styled_widgets.extend([era_label, era_menu, era_other_entry])
def toggle_era_entry(*args):
    era_other_entry.config(state="normal" if era_var.get() == "Other" else "disabled")
era_var.trace("w", toggle_era_entry)
toggle_era_entry()

# Remaining fields
timezone_entry = create_labeled_entry("Timezone:")
language_entry = create_labeled_entry("Language:")
recruiter_entry = create_labeled_entry("Recruiter:")
roles_entry = create_labeled_entry("Roles Available:")
discord_entry = create_labeled_entry("Discord:")
image_url_entry = create_labeled_entry("Image URL (Optional):")

# Submit button
submit_btn = tk.Button(scroll_frame, text="Send to Discord", command=send_to_discord)
submit_btn.pack(fill="x", pady=20, padx=10)
styled_widgets.append(submit_btn)

# Apply theme initially
apply_theme()

# Run
root.mainloop()
