import time
import sys

def simulate_process():
    """
    A simple function to simulate a process that runs indefinitely.
    """
    # Get the name of the executable to display a more realistic message
    process_name = sys.argv[0]
    
    print(f"'{process_name}' simulation started...")
    print("This window will keep the process alive.")
    print("Check your Task Manager to see it running.")
    print("Close this window or press Ctrl+C to stop.")
    
    try:
        # This loop runs forever, keeping the script alive
        while True:
            # sleep() prevents the script from using 100% of a CPU core
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n'{process_name}' simulation stopped.")

if __name__ == "__main__":
    simulate_process()