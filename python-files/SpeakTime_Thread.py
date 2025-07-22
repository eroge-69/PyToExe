import time
import winsound
import pyttsx3
import threading

# ==== Settings ====
INTERVAL = 15  # Interval in seconds
BEEP_FREQ = 1000  # Frequency of beep in Hz
BEEP_DURATION_MS = 500  # Duration of beep in milliseconds

# ==== Shared event for communication between threads ====
sound_event = threading.Event()
sound_data = {"text": ""}

def format_time(seconds):
    """Formats time in hhh:mm:ss.s format with tenths of a second"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:03d}:{minutes:02d}:{secs:.1f}"

def pluralize_seconds(seconds):
    """Returns correct form of 'секунда', 'минута', 'час' depending on number"""
    n = abs(int(seconds))
    if 11 <= n % 100 <= 14:
        return "секунд"
    elif n % 10 == 1:
        return "секунда"
    elif 2 <= n % 10 <= 4:
        return "секунды"
    else:
        return "секунд"

def pluralize_minutes(minutes):
    n = abs(int(minutes))
    if 11 <= n % 100 <= 14:
        return "минут"
    elif n % 10 == 1:
        return "минута"
    elif 2 <= n % 10 <= 4:
        return "минуты"
    else:
        return "минут"

def pluralize_hours(hours):
    n = abs(int(hours))
    if 11 <= n % 100 <= 14:
        return "часов"
    elif n % 10 == 1:
        return "час"
    elif 2 <= n % 10 <= 4:
        return "часа"
    else:
        return "часов"
        
def format_time_text(seconds):
    total_seconds = int(round(seconds))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    parts = []
    if hours > 0:
        parts.append(f"{hours} {pluralize_hours(hours)}")
    if minutes > 0:
        parts.append(f"{minutes} {pluralize_minutes(minutes)}")
    if seconds > 0 or not parts:
        parts.append(f"{seconds} {pluralize_seconds(seconds)}")

    speech_text = "Прошло: " + " ".join(parts)

    return speech_text


# ==== Background sound thread function ====
def sound_player():
    engine = pyttsx3.init()

    # Set Russian voice if available
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'russian' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

    while True:
        sound_event.wait()  # Wait for signal
        if sound_event.is_set():
            winsound.Beep(BEEP_FREQ, BEEP_DURATION_MS)
            engine.say(sound_data["text"])
            engine.runAndWait()
            engine.stop()
            sound_event.clear()  # Reset event

# ==== Main function ====
def main():
    # print("Press any key to start...")
    # keyboard.read_event()  # Wait for any key press

    print("Timer started! Press CTRL+C to stop.")
    start_time = time.monotonic()

    # Start background sound thread
    player_thread = threading.Thread(target=sound_player, daemon=True)
    player_thread.start()

    next_beep_time = start_time + INTERVAL
    last_printed = ""

    try:
        # First beep and speech immediately
        initial_time_str = format_time(0.0)
        print(f"\rElapsed: {initial_time_str} | Time until next beep: {round(INTERVAL, 1)} sec | Updates every 0.1 sec...", end="", flush=True)
        sound_data["text"] = "0 секунд"
        sound_event.set()
        last_printed = initial_time_str

        while True:
            now = time.monotonic()
            elapsed = now - start_time

            # --- Update display every 0.1 sec ---
            formatted_time = format_time(elapsed)
            time_until_next = max(0.0, round(next_beep_time - now, 1))

            if formatted_time != last_printed:
                print(f"\rElapsed: {formatted_time} | Time until next beep: {time_until_next} sec | Updates every 0.1 sec...", end="", flush=True)
                last_printed = formatted_time

            # --- Check if it's time to trigger event ---
            if now >= next_beep_time - 0.001:
                seconds_elapsed = int(round(elapsed))
                # sound_data["text"] = f"{seconds_elapsed} секунд"
                sound_data["text"] = format_time_text(elapsed)
                sound_event.set()
                next_beep_time += INTERVAL

            # Sleep briefly to update screen faster than once per second
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nTimer stopped.")

if __name__ == "__main__":
    main()