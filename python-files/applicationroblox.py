import tkinter as tk
import time
import threading  # Required for running the macro without freezing the GUI
import pyautogui
# import keyboard # Not used in the provided macro logic, but kept if needed later
import autoit

# Global control flag to stop the macro thread
is_running = False
macro_thread = None


# --- Worker Function (Runs in a separate thread) ---
def _run_macro_loop():
    """
    The main macro logic, executed in its own thread.
    It checks the global 'is_running' flag in every loop iteration.
    """
    global is_running
    x = 930

    status_label.config(text="click icitte pour stoper le cave", fg="orange")

    try:
        # The loop now checks the global flag
        while is_running:

            # --- Macro Steps ---
            time.sleep(3)
            if not is_running: break  # Check flag before lengthy operation
            autoit.mouse_wheel("down", 100)

            time.sleep(1)
            if not is_running: break
            autoit.mouse_click("left", x, 740)

            time.sleep(0.5)
            if not is_running: break
            autoit.mouse_click("left", x, 530)

            time.sleep(0.5)
            if not is_running: break
            autoit.mouse_click("left", x, 320)

            time.sleep(0.5)
            if not is_running: break
            autoit.mouse_wheel("up", 5)

            time.sleep(1)
            if not is_running: break
            autoit.mouse_click("left", x, 815)

            time.sleep(0.5)
            if not is_running: break
            autoit.mouse_click("left", x, 610)

            time.sleep(0.5)
            if not is_running: break
            autoit.mouse_click("left", x, 400)

            time.sleep(10)  # Longest wait period
            # --- End of Macro Steps ---

        # When the loop exits (because is_running became False)
        status_label.config(text="t'as arreter le script le grand", fg="blue")

    except Exception as e:
        # Handle exceptions gracefully
        status_label.config(text=f"Macro Error: {e}", fg="red")
        print(f"Macro Error: {e}")
    finally:
        is_running = False
        # Re-enable the Start button and disable the Stop button
        start_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)


# --- Button Command Functions (Called by the GUI) ---

def start_macro():
    """Starts the macro in a new thread."""
    global is_running, macro_thread

    if is_running:
        status_label.config(text="attend le cave", fg="orange")
        return

    is_running = True
    # Start the worker function in a dedicated thread
    macro_thread = threading.Thread(target=_run_macro_loop)
    macro_thread.daemon = True  # Allows the thread to exit when the main program closes
    macro_thread.start()

    # Update button states
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)


def stop_macro():
    """Sets the control flag to False, stopping the macro on the next loop check."""
    global is_running
    is_running = False
    status_label.config(text="attend que ca finisse", fg="purple")


# --- App Setup ---

window = tk.Tk()
window.title("app croter")
window.geometry("350x180")  # Increased width slightly for two buttons
window.resizable(False, False)

# --- Button Frame for layout ---
button_frame = tk.Frame(window)
button_frame.pack(pady=20)

# --- Start Button Configuration ---
start_button = tk.Button(
    button_frame,
    text="Brainroter (START)",
    width=15,
    height=2,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 10, "bold"),
    relief=tk.RAISED,
    command=start_macro
)
start_button.pack(side=tk.LEFT, padx=10)

# --- Stop Button Configuration ---
stop_button = tk.Button(
    button_frame,
    text="arrete",
    width=15,
    height=2,
    bg="#F44336",  # Red background
    fg="white",
    font=("Arial", 10, "bold"),
    relief=tk.RAISED,
    command=stop_macro,
    state=tk.DISABLED  # Starts disabled until the macro is running
)
stop_button.pack(side=tk.LEFT, padx=10)

# --- Status Label ---
status_label = tk.Label(
    window,
    text="fait par seturrox, (ton daddy qui touche ton ti pipi)",
    fg="#333333",
    pady=10
)
status_label.pack()

# Start the application loop
window.mainloop()

