
import discord
import threading
from tkinter import Tk, Label, Entry, Button, messagebox

class MobileClient(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user}")
        await self.change_presence(status=discord.Status.online)
        print("Status set to Mobile.")

def start_bot(token):
    intents = discord.Intents.default()
    client = MobileClient(proxy=None, self_bot=True, intents=intents)
    client.run(token, bot=False)

def run_gui():
    def on_start():
        token = token_entry.get().strip()
        if not token:
            messagebox.showerror("Error", "Please enter your token.")
            return
        start_btn.config(state='disabled')
        threading.Thread(target=start_bot, args=(token,), daemon=True).start()
        messagebox.showinfo("Running", "Status set to Mobile. Leave this window open.")

    def on_quit():
        root.destroy()
        os._exit(0)

    root = Tk()
    root.title("Discord Mobile Status")
    root.geometry("300x150")

    Label(root, text="Enter your token:").pack(pady=5)
    token_entry = Entry(root, width=40, show="*")
    token_entry.pack(pady=5)

    start_btn = Button(root, text="Set Mobile Status", command=on_start)
    start_btn.pack(pady=5)

    quit_btn = Button(root, text="Exit", command=on_quit)
    quit_btn.pack(pady=5)

    root.mainloop()

run_gui()
