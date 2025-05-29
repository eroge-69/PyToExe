import tkinter as tk
from pynput import mouse, keyboard
from pynput.mouse import Controller
import subprocess
import time

TEXT_FILE_PATH = "kte.txt"  # ⬅️ Set your file path here


def get_clipboard_text():
    try:
        return subprocess.check_output("pbpaste", universal_newlines=True)
    except Exception:
        return ""


def search_in_file(keyword, context=8):  # Shows 8 lines after the match
    matches = []
    try:
        with open(TEXT_FILE_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if keyword.lower() in line.lower():
                # Start from the matching line
                start = i
                # Show the next 'context' number of lines
                end = min(len(lines), i + context + 1)
                snippet = "".join(lines[start:end]).strip()
                matches.append(snippet)
    except Exception as e:
        matches.append(f"Error reading file: {e}")
    if not matches:
        matches.append(f"No results for: '{keyword}'")
    return matches


def show_popup(text_snippets):
    global current_popup, current_index, current_snippets

    if not text_snippets:
        return

    current_snippets = text_snippets
    current_index = {"current": 0}

    popup = tk.Toplevel()
    popup.attributes("-topmost", True)
    popup.overrideredirect(True)
    popup.attributes("-alpha", 0.9)
    popup.attributes("-transparent", True)
    popup.configure(bg="systemTransparent")

    # Create a temporary label to calculate required height
    temp_label = tk.Label(
        popup,
        text=f"Match 1 of {len(text_snippets)}\n{text_snippets[0]}",
        font=("Courier", 10),
        wraplength=400,
        justify="left",
        bg="systemTransparent",
    )
    temp_label.pack()
    temp_label.update()

    # Calculate required height (add small padding)
    required_height = temp_label.winfo_height() + 5  # Reduced padding
    temp_label.destroy()

    width = 300  # Smaller width
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    x = (screen_width - width) // 2
    y = screen_height - required_height - 20  # Moved closer to bottom
    popup.geometry(f"{width}x{required_height}+{x}+{y}")

    label = tk.Label(
        popup,
        text=f"Match 1 of {len(text_snippets)}\n{text_snippets[0]}",
        font=("Courier", 8),  # Smaller font size
        fg="#686565",
        bg="#FFFFFF",
        wraplength=300,  # Adjust wrap length to match smaller width
        justify="left",
    )
    label.pack(padx=3, pady=3)  # Reduced padding

    popup.label = label  # Attach label to popup for global access
    current_popup = popup  # Update global popup reference

    popup.focus_force()
    popup.grab_set()


# Define global variables for popup and handlers
current_popup = None
current_index = {"current": 0}
current_snippets = []


def on_key_press(key):
    try:
        key_char = key.char if hasattr(key, "char") else str(key)
        if key_char in ["x", "X"]:
            if current_index["current"] < len(current_snippets) - 1:
                current_index["current"] += 1
                # Ensure the popup remains active and visible when switching matches
                if current_popup:
                    current_popup.focus_force()
                    current_popup.grab_set()
                    current_popup.label.config(
                        text=f"Match {current_index['current'] + 1} of {len(current_snippets)}\n\n{current_snippets[current_index['current']]}"
                    )
        elif key_char in ["z", "Z"]:
            if current_index["current"] > 0:
                current_index["current"] -= 1
                current_popup.label.config(
                    text=f"Match {current_index['current'] + 1} of {len(current_snippets)}\n\n{current_snippets[current_index['current']]}"
                )
        elif key_char == "Escape":
            current_popup.destroy()
    except Exception:
        pass


# Start keyboard listener globally
keyboard.Listener(on_press=on_key_press).start()


def on_mouse_release(x, y, button, pressed):
    if not pressed:
        subprocess.run("pbcopy < /dev/null", shell=True)
        subprocess.run(
            'osascript -e \'tell application "System Events" to keystroke "c" using command down\'',
            shell=True,
        )

        time.sleep(0.2)
        selected_text = get_clipboard_text().strip()

        if selected_text:
            snippets = search_in_file(selected_text)
            root.after(0, lambda: show_popup(snippets))
            mouse_controller = Controller()
            mouse_controller.position = (x, y)
            mouse_controller.click(button)


# Create a root Tk instance (used only for scheduling)
root = tk.Tk()
root.withdraw()

# Start mouse listener
mouse.Listener(on_click=on_mouse_release).start()

# Run the main loop to process GUI events
root.mainloop()
