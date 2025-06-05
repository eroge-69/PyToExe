import tkinter as tk
from tkinter import messagebox
import requests
import json
import time
import threading
from datetime import datetime
import os
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem, Icon

CONFIG_FILE = "config.json"

class ChatRelay:
    def __init__(self, api_key, webhooks):
        self.api_key = api_key
        self.webhooks = webhooks
        self.active = {'global': False, 'trade': False, 'cartel': False}
        self.last_fetch_time = 0
        self.last_messages = {'global': [], 'trade': [], 'cartel': []}  # To track last sent messages

    def send_to_discord(self, chat_type, message):
        webhook_url = self.webhooks.get(chat_type)
        if webhook_url:
            data = {"content": message}
            try:
                response = requests.post(webhook_url, json=data)
                response.raise_for_status()  # Check for HTTP errors
            except requests.exceptions.RequestException as e:
                print(f"Failed to send message: {message}, Error: {e}")

    def send_recent_messages(self):
        current_time = int(time.time())
        timestamp2 = current_time
        timestamp1 = current_time - 1800  # 30 minutes ago
        url = f"https://cartelempire.online/api/chat?type=global,trade,cartel&limit=100&from={timestamp1}&to={timestamp2}&key={self.api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()  # Check for HTTP errors
            chat_data = response.json()

            for chat_type in ['global', 'trade', 'cartel']:
                if self.active[chat_type]:  # Only process if active
                    messages = chat_data.get(f"{chat_type}Chat", [])
                    new_messages = [msg for msg in messages if msg not in self.last_messages[chat_type]]

                    for message in new_messages:
                        if 'posted' in message and 'name' in message and 'message' in message:
                            local_time = datetime.fromtimestamp(int(message['posted'])).strftime('%Y-%m-%d %H:%M:%S')
                            formatted_message = f"{local_time} {message['name']}: {message['message']}"
                            self.send_to_discord(chat_type, formatted_message)
                            self.last_messages[chat_type].append(message)  # Track sent messages

                    if new_messages:
                        self.last_messages[chat_type] = messages  # Update the last messages list

        except requests.exceptions.RequestException as e:
            print("Error fetching chat:", e)

    def listen_for_messages(self):
        while True:
            if any(self.active.values()):  # Only run if any relay is active
                current_time = int(time.time())
                if current_time - self.last_fetch_time >= 20:  # Fetch every 20 seconds
                    self.send_recent_messages()  # Fetch and send all types
                    self.last_fetch_time = current_time
            time.sleep(1)  # Sleep to avoid busy waiting

class ChatRelayApp:
    def __init__(self, master):
        self.master = master
        master.title("Ducks B. Chatty")
        master.geometry("260x335")
        self.master.iconbitmap("icon.ico")  # Set the application icon

        self.api_key_label = tk.Label(master, text="API Key:")
        self.api_key_label.pack()
        self.api_key_entry = tk.Entry(master)
        self.api_key_entry.pack()

        self.webhook_entries = {}
        chat_types = ['global', 'trade', 'cartel']
        self.check_vars = {chat_type: tk.BooleanVar() for chat_type in chat_types}
        self.status_labels = {chat_type: None for chat_type in chat_types}  # To hold status labels

        for chat_type in chat_types:
            label = tk.Label(master, text=f"{chat_type.capitalize()} Webhook:")
            label.pack()
            entry = tk.Entry(master)
            entry.pack()
            self.webhook_entries[chat_type] = entry
            
            checkbox = tk.Checkbutton(master, text=f"Enable {chat_type.capitalize()} Relay", variable=self.check_vars[chat_type])
            checkbox.pack()

            status_label = tk.Label(master, text="Status: Stopped", fg="red")
            status_label.pack()
            self.status_labels[chat_type] = status_label  # Store the status label

        self.toggle_button = tk.Button(master, text="Start Relay", command=self.toggle_relay)
        self.toggle_button.pack()

        self.chat_relay = None

        self.load_config()

        master.protocol("WM_DELETE_WINDOW", self.on_closing)
        master.bind("<Unmap>", self.on_minimize)

        self.icon = None

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.api_key_entry.insert(0, config.get('api_key', ''))
                for chat_type in ['global', 'trade', 'cartel']:
                    self.webhook_entries[chat_type].insert(0, config.get('webhooks', {}).get(chat_type, ''))
                    self.check_vars[chat_type].set(config.get('active', {}).get(chat_type, False))

    def save_config(self):
        config = {
            'api_key': self.api_key_entry.get(),
            'webhooks': {chat_type: self.webhook_entries[chat_type].get() for chat_type in ['global', 'trade', 'cartel']},
            'active': {chat_type: self.check_vars[chat_type].get() for chat_type in ['global', 'trade', 'cartel']}
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)

    def toggle_relay(self):
        api_key = self.api_key_entry.get()
        if not api_key:
            messagebox.showwarning("Input Error", "API Key must be provided.")
            return

        if self.chat_relay is None:
            webhooks = {ct: self.webhook_entries[ct].get() for ct in ['global', 'trade', 'cartel']}
            self.chat_relay = ChatRelay(api_key, webhooks)
            threading.Thread(target=self.chat_relay.listen_for_messages, daemon=True).start()

        for chat_type in ['global', 'trade', 'cartel']:
            self.chat_relay.active[chat_type] = self.check_vars[chat_type].get()
            # Update status labels
            if self.chat_relay.active[chat_type]:
                self.status_labels[chat_type].config(text="Status: Running", fg="green")
            else:
                self.status_labels[chat_type].config(text="Status: Stopped", fg="red")

        if any(self.chat_relay.active.values()):
            self.toggle_button.config(text="Stop Relay")
        else:
            self.toggle_button.config(text="Start Relay")

    def on_closing(self):
        if self.chat_relay:
            for chat_type in self.chat_relay.active.keys():
                self.chat_relay.active[chat_type] = False
        self.save_config()  # Save configuration before closing
        self.master.destroy()

    def on_minimize(self, event):
        if event.state == 'withdrawn':  # Minimized
            self.master.withdraw()  # Hide the main window
            self.setup_tray_icon()  # Set up the tray icon

    def setup_tray_icon(self):
        icon_image = Image.open("icon.ico")  # Load the icon for the tray
        self.icon = Icon("ChatRelay", icon_image, "Ducks B. Chatty", self.create_menu())
        self.icon.run(setup=self.icon_setup)

    def create_menu(self):
        return (MenuItem("Restore", self.restore), MenuItem("Quit", self.quit_app))

    def icon_setup(self, icon):
        icon.visible = True

    def restore(self, icon, item):
        self.master.deiconify()  # Restore the main window
        self.icon.stop()  # Stop the tray icon

    def quit_app(self, icon, item):
        if self.chat_relay:
            for chat_type in self.chat_relay.active.keys():
                self.chat_relay.active[chat_type] = False
        self.save_config()  # Save configuration before quitting
        icon.stop()  # Stop the tray icon
        self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatRelayApp(root)
    root.mainloop()
