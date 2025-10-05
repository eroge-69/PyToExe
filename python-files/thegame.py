import os
from tkinter import *
import webbrowser
import time
import pygame

# Get the directory of this script
script_dir = os.path.dirname(__file__)

# Set the "battles" folder to be in the same directory as this script
battles_dir = os.path.join(script_dir, "battles")

# Create the "battles" folder if it doesn't exist
if not os.path.exists(battles_dir):
    os.makedirs(battles_dir)
    print(f"Folder 'battles' created at: {battles_dir}")
else:
    print(f"Folder 'battles' already exists at: {battles_dir}")

# Function to open a file
def open_file(file_name):
    file_path = os.path.join(battles_dir, file_name)
    if os.path.exists(file_path):
        webbrowser.open(file_path)
    else:
        print(f"File not found: {file_path}")

# Set up the main window (but hide it initially)
root = Tk()
root.title("FoxTale Battle Selector")
root.geometry("400x300")
root.resizable(True, True)  # Allow resizing
root.config(bg="#001f3f")  # Dark blue background
root.withdraw()  # Hide the window initially

# Set GUI scale to 145%
scale_factor = 1.45
root.tk.call("tk", "scaling", scale_factor)

# Initialize pygame for background music
pygame.init()
pygame.mixer.init()
bg_music_path = os.path.join(script_dir, "bg_ost.mp3")

# Function to play background music
def play_music():
    if os.path.exists(bg_music_path):
        pygame.mixer.music.load(bg_music_path)
        pygame.mixer.music.play(-1)  # Loop indefinitely
    else:
        print(f"Background music file not found: {bg_music_path}")

# Loading window
def show_loading_window():
    loading_window = Toplevel(root)
    loading_window.title("Loading...")
    loading_window.geometry("200x100")
    loading_window.resizable(False, False)
    loading_window.config(bg="#001f3f")
    Label(loading_window, text="Loading...", font=("Arial", 12), fg="white", bg="#001f3f").pack(pady=20)

    # Close the loading window after 5000 ms (5 seconds)
    loading_window.after(5000, lambda: [loading_window.destroy(), show_main_window()])

def show_main_window():
    # Center the main window on the screen
    window_width = 400
    window_height = 300
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.deiconify()  # Show the main window

# Page system variables
items_per_page = 9
battle_files = os.listdir(battles_dir) if os.path.isdir(battles_dir) else []
current_page = 0

# Function to display current page
def show_page(page):
    global current_page
    current_page = page
    update_page_label()
    for widget in root.winfo_children():
        if widget.winfo_class() == "Button":
            widget.destroy()
    start = page * items_per_page
    end = start + items_per_page
    for i, file_name in enumerate(battle_files[start:end]):
        # Remove the file extension
        file_name_base = os.path.splitext(file_name)

        row = i // 3
        col = i % 3

        # Create a button with the file name as the text
        button = Button(
            root,
            text=file_name_base,
            command=lambda name=file_name: open_file(name),
            bg="orange",  # Orange background
            fg="white",
            width=15,
            height=2,
            font=("Determination", 12)  # Use "Determination" font
        )
        # Hover effect with size change and color
        button.bind("<Enter>", lambda e, b=button: (
            b.config(bg="black", fg="black", width=17, height=3)
        ))
        button.bind("<Leave>", lambda e, b=button: (
            b.config(bg="orange", fg="white", width=15, height=2)
        ))
        button.grid(row=row, column=col, padx=10, pady=10)

# Function to go to previous page
def prev_page():
    global current_page
    if current_page > 0:
        current_page -= 1
        show_page(current_page)

# Function to go to next page
def next_page():
    global current_page
    if current_page < (len(battle_files) - 1) // items_per_page:
        current_page += 1
        show_page(current_page)

# Function to list files in the "battles" folder
def list_battles():
    show_page(current_page)

# Add navigation buttons and page label
prev_button = Button(root, text="⬅", command=prev_page, bg="orange", fg="white", font=("Arial", 12))
next_button = Button(root, text="➡", command=next_page, bg="orange", fg="white", font=("Arial", 12))
page_label = Label(root, text=f"Page: {current_page + 1}", font=("Arial", 12), bg="#001f3f", fg="white")

# Place buttons and label at the bottom of the window
prev_button.grid(row=3, column=0, padx=10, pady=10)
page_label.grid(row=3, column=1, padx=10, pady=10)
next_button.grid(row=3, column=2, padx=10, pady=10)

# Function to update the page label
def update_page_label():
    page_label.config(text=f"Page: {current_page + 1}")

# Add keyboard support for navigation
def on_key_press(event):
    if event.keysym == "Left":
        prev_page()
    elif event.keysym == "Right":
        next_page()

root.bind("<KeyPress>", on_key_press)

# Focus handler to play music when the window is in focus
def on_focus_in(event):
    play_music()

# Focus handler to stop music when the window loses focus
def on_focus_out(event):
    pygame.mixer.music.stop()

# Function to handle window close event
def on_closing():
    pygame.mixer.music.stop()
    root.destroy()

# Bind the events
root.bind("<FocusIn>", on_focus_in)
root.bind("<FocusOut>", on_focus_out)
root.protocol("WM_DELETE_WINDOW", on_closing)

# Call the function to list the files
list_battles()

# Start the GUI event loop
show_loading_window()
root.mainloop()
