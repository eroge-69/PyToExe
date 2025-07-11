import time
import datetime
import threading
import sys
import os

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
filename = os.path.join(log_dir, f"log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")

def format_time(seconds):
    return time.strftime("%H:%M:%S", time.gmtime(seconds))

def live_timer(stop_event):
    start_time = time.time()
    while not stop_event.is_set():
        elapsed = time.time() - start_time
        sys.stdout.write(f"\r⏳ Time elapsed: {format_time(elapsed)}")
        sys.stdout.flush()
        time.sleep(1)
    print()

def save_entry(name, duration):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"{name}: {duration}\n")

print("🎯 Timer started... (Press Enter to stop each session, type `end` to finish)")

try:
    while True:
        activity = input("\n\n📝 Enter activity name: ").strip()
        if activity.lower() == "end":
            break

        print(f"⏱ Timer started for «{activity}»... (Press Enter to stop)")

        stop_event = threading.Event()
        timer_thread = threading.Thread(target=live_timer, args=(stop_event,))
        start = time.time()
        timer_thread.start()

        input()
        stop_event.set()
        timer_thread.join()
        end = time.time()

        duration = end - start
        formatted = format_time(duration)

        print(f"✅ Duration for «{activity}»: {formatted}")
        save_entry(activity, formatted)

except KeyboardInterrupt:
    print("\n\n❗ Interrupted by user (Ctrl+C)")
