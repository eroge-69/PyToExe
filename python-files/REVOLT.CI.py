import requests
import threading
import os
import sys

stop_flag = [False]

def spam(webhook_url, message):
    while not stop_flag[0]:
        try:
            requests.post(webhook_url, json={"content": message})
        except Exception as e:
            print(f"Error: {e}")

# Preset spam messages
def get_preset_message():
    print("\nChoose a preset message or type your own:")
    print("1. Invisible message (blank spam)")
    print("2. 200x @everyone")
    print("3. BIG 300x @everyone @here")
    print("4. REVOLT.CI IS THE BEST")
    print("5. Custom message")

    while True:
        choice = input("Enter choice (1-5): ").strip()
        if choice == "1":
            return "\u200b" * 200  # Zero-width space
        elif choice == "2":
            return "@everyone " * 200
        elif choice == "3":
            return "# " + ("@everyone @here " * 100).strip()
        elif choice == "4":
            return "@here **REVOLT.CI IS THE MOST SIGMA WEBHOOK SPAMMER OF ALL TIME** @here" * 20
        elif choice == "5":
            return input("Enter your custom message: ").strip()
        else:
            print("Invalid choice. Try again.")


# Get user input
webhook_url = input("Enter Discord Webhook URL: ").strip()
message = get_preset_message()

# Start multiple threads to spam fast
threads = []
for _ in range(45):  # Increase number for more speed (careful!)
    t = threading.Thread(target=spam, args=(webhook_url, message))
    t.start()
    threads.append(t)

# Listen for stop or restart
while True:
    user_input = input("Type 'stop' to stop or 'restart' to restart: ").strip().lower()
    if user_input == "stop":
        stop_flag[0] = True
        for t in threads:
            t.join()
        print("Spamming stopped.")
        break
    elif user_input == "restart":
        stop_flag[0] = True
        for t in threads:
            t.join()
        print("Restarting the application...\n")
        os.execl(sys.executable, sys.executable, *sys.argv)

input("Press Enter to exit...")
