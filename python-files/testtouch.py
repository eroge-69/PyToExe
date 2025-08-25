from pynput import mouse, keyboard
import time
import threading
import pickle  # To save and load recordings

# File to store the recorded data
SAVE_FILE = "mouse_recording.pkl"

# List to store mouse events
mouse_events = []

# Flags and recording start timer
recording = False
replaying = False
start_time_recording = 0  # Tracks when recording started

# Function to record mouse movements, clicks, and scrolls
def on_move(x, y):
    if recording:
        elapsed = time.time() - start_time_recording
        mouse_events.append(('move', x, y, elapsed))

def on_click(x, y, button, pressed):
    if recording:
        elapsed = time.time() - start_time_recording
        mouse_events.append(('click', x, y, button, pressed, elapsed))

def on_scroll(x, y, dx, dy):
    if recording:
        elapsed = time.time() - start_time_recording
        mouse_events.append(('scroll', x, y, dx, dy, elapsed))

# Function to save recording to a file
def save_recording():
    with open(SAVE_FILE, "wb") as f:
        pickle.dump(mouse_events, f)
    print("Recording saved.")

# Function to load recording from file
def load_recording():
    global mouse_events
    try:
        with open(SAVE_FILE, "rb") as f:
            mouse_events = pickle.load(f)
        print("Recording loaded.")
        return True
    except (FileNotFoundError, EOFError):
        print("No previous recording found.")
        return False

# Function to replay mouse events
def replay_mouse_events():
    global replaying
    replaying = True
    print("Replaying recorded events...")

    while replaying:  # Infinite loop to replay events
        start_time_replay = time.time()  # Reset start time for each cycle
        for event in mouse_events:
            if not replaying:
                break  # Stop replaying if 's' is pressed
            
            event_time = event[-1]  # Get the relative timestamp
            # Wait until the correct time to replay the event
            while (time.time() - start_time_replay) < event_time:
                if not replaying:
                    return  # Stop replaying
                time.sleep(0.001)
            
            if event[0] == 'move':
                mouse_controller.position = (event[1], event[2])
            elif event[0] == 'click':
                mouse_controller.position = (event[1], event[2])
                if event[4]:  # pressed
                    mouse_controller.press(event[3])
                else:
                    mouse_controller.release(event[3])
            elif event[0] == 'scroll':
                mouse_controller.position = (event[1], event[2])
                mouse_controller.scroll(event[3], event[4])
        
        print("Replay cycle finished. Restarting...")
        time.sleep(0.1)  # Small delay before restarting

    print("Replay stopped.")

# Handle key presses
def on_press(key):
    global recording, start_time_recording, replaying
    try:
        if key.char == 'r':
            if not recording and not replaying:
                print("Recording started...")
                recording = True
                mouse_events.clear()
                start_time_recording = time.time()
            elif recording:
                print("Recording stopped.")
                recording = False
                save_recording()
        
        elif key.char == 'a':
            if not recording and not replaying and mouse_events:
                print("Replaying...")
                threading.Thread(target=replay_mouse_events).start()
        
        elif key.char == 'p':  # Load saved recording and replay
            if not recording and not replaying:
                if load_recording():
                    print("Replaying saved recording...")
                    threading.Thread(target=replay_mouse_events).start()
        
        elif key.char == 's':  # Stop replaying and exit
            if replaying:
                print("Stopping replay.")
                replaying = False
            else:
                print("Exiting program.")
                exit()

    except AttributeError:
        pass

# Set up listeners
mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
keyboard_listener = keyboard.Listener(on_press=on_press)
mouse_controller = mouse.Controller()

# Start listeners
mouse_listener.start()
keyboard_listener.start()

# Keep the script running
print("Script is running. Press 'r' to start/stop recording, 'a' to replay, 'p' to replay saved recording, 's' to stop.")
keyboard_listener.join()
