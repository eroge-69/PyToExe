import sounddevice as sd
import psutil

def list_mics():
    devices = sd.query_devices()
    input_devs = [(idx, d['name']) for idx, d in enumerate(devices) if d['max_input_channels'] > 0]
    if not input_devs:
        print("No microphone/input devices found.")
        return
    print("Available Microphones:")
    for idx, name in input_devs:
        print(f"{idx}: {name}")

def list_apps():
    procs = [(p.pid, p.name()) for p in psutil.process_iter(['name']) if p.info['name']]
    if not procs:
        print("No running applications found.")
        return
    print("Running Applications:")
    for pid, name in procs:
        print(f"{pid}: {name}")

def main():
    while True:
        print("\n--- Sound Capture Menu ---")
        print("1. Capture from Mic")
        print("2. Capture from App")
        print("0. Exit")
        choice = input("Select an option: ").strip()
        if choice == "1":
            list_mics()
        elif choice == "2":
            list_apps()
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()