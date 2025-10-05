import asyncio
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import discord
import sys
import os

# ---------- CLIENT THREAD & QUEUE SETUP ----------
class ClientRunner:
    def __init__(self, is_bot=True):
        self.loop = None
        self.queue = None
        self.client = None
        self.thread = None
        self.is_bot = is_bot

    def start_loop(self, token, log_callback):
        if self.thread and self.thread.is_alive():
            log_callback("[CLIENT] Client already running.", 'error')
            return

        def _target():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.queue = asyncio.Queue()
            intents = discord.Intents.default()
            intents.members = True
            intents.message_content = True
            client = discord.Client(intents=intents)
            self.client = client
            stop_event = asyncio.Event()

            @client.event
            async def on_ready():
                self._log(log_callback, f"[CLIENT] Logged in as {client.user} (id={client.user.id})", 'success')
                self.loop.create_task(self._queue_consumer(client, self.queue, stop_event, log_callback))

            async def start_client():
                try:
                    await client.start(token)
                except Exception as e:
                    self._log(log_callback, f"[CLIENT ERROR] {e}", 'error')

            try:
                self.loop.create_task(start_client())
                self.loop.run_forever()
            finally:
                try:
                    self.loop.run_until_complete(client.close())
                except:
                    pass

        self.thread = threading.Thread(target=_target, daemon=True)
        self.thread.start()
        self._log(log_callback, "[CLIENT] Starting client thread...", 'info')

    def stop_loop(self, log_callback):
        if not (self.loop and self.loop.is_running()):
            self._log(log_callback, "[CLIENT] Client not running.", 'error')
            return
        def _stop():
            self.loop.stop()
        self.loop.call_soon_threadsafe(_stop)
        self._log(log_callback, "[CLIENT] Stop signal sent; client thread will exit.", 'info')

    async def _queue_consumer(self, client, queue, stop_event, log_callback):
        current_task = None
        while True:
            cmd = await queue.get()
            if cmd.get("action") == "start":
                guilds_or_channels = cmd.get("channels", [])
                delay = cmd.get("delay", 5)
                message = cmd.get("message", "")
                self._log(log_callback, f"[CLIENT] Received start: {len(guilds_or_channels)} targets, delay={delay}s", 'info')
                if current_task and not current_task.done():
                    self._log(log_callback, "[CLIENT] Another job is running; ignore new start until finished or press Stop.", 'warning')
                else:
                    stop_event.clear()
                    current_task = asyncio.create_task(self._send_to_targets(client, guilds_or_channels, delay, message, stop_event, log_callback, self.is_bot))
            elif cmd.get("action") == "stop":
                stop_event.set()
                self._log(log_callback, "[CLIENT] Stop requested: current sending will stop after current message.", 'info')
            elif cmd.get("action") == "shutdown":
                self._log(log_callback, "[CLIENT] Shutdown requested.", 'info')
                try:
                    await client.close()
                finally:
                    self.loop.stop()
                break

    async def _send_to_targets(self, client, targets, delay, message, stop_event, log_callback, is_bot):
        for target in targets:
            if stop_event.is_set():
                self._log(log_callback, "[CLIENT] Stopped by user.", 'warning')
                break
            try:
                if is_bot:
                    # For bot, send to all members in guild
                    guild = client.get_guild(target)
                    if guild is None:
                        try:
                            guild = await client.fetch_guild(target)
                        except Exception as e:
                            self._log(log_callback, f"[FAIL] Guild {target}: cannot fetch ({e})", 'error')
                            continue
                    members = guild.members
                    self._log(log_callback, f"[INFO] Found {len(members)} members in guild {target}", 'info')
                    for member in members:
                        if stop_event.is_set():
                            break
                        try:
                            await member.send(message)
                            self._log(log_callback, f"[OK] Sent to {member.name}#{member.discriminator} (id={member.id})", 'success')
                        except Exception as e:
                            self._log(log_callback, f"[ERROR] Sending to {member.name}#{member.discriminator}: {e}", 'error')
                        await asyncio.sleep(delay)
                else:
                    # For user, send to channel
                    ch = client.get_channel(target)
                    if ch is None:
                        try:
                            ch = await client.fetch_channel(target)
                        except Exception as e:
                            self._log(log_callback, f"[FAIL] Channel {target}: cannot fetch ({e})", 'error')
                            continue
                    if hasattr(ch, "send"):
                        await ch.send(message)
                        self._log(log_callback, f"[OK] Sent to channel {target}", 'success')
                    else:
                        self._log(log_callback, f"[SKIP] Channel {target} is not sendable.", 'warning')
            except Exception as e:
                self._log(log_callback, f"[ERROR] Processing target {target}: {e}", 'error')

    def enqueue(self, item):
        if not (self.loop and self.loop.is_running()):
            raise RuntimeError("Client loop not running")
        return asyncio.run_coroutine_threadsafe(self.queue.put(item), self.loop)

    def _log(self, log_callback, text, tag='info'):
        if callable(log_callback):
            log_callback(text, tag)

# ---------- GUI ----------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Discord Announce Controller")
        if os.path.exists("icon.ico"):
            self.root.iconbitmap("icon.ico")
        
        self.theme = 'light'
        self.themes = {
            'light': {'bg': '#F5F6F5', 'fg': '#333333', 'btn_bg': '#4CAF50', 'btn_hover': '#45a049', 'btn_disabled': '#A9A9A9',
                      'entry_bg': '#FFFFFF', 'entry_fg': '#000000', 'log_bg': '#E8ECEF', 'log_fg': '#333333'},
            'dark': {'bg': '#2C2F33', 'fg': '#FFFFFF', 'btn_bg': '#1E90FF', 'btn_hover': '#1E90FF', 'btn_disabled': '#666666',
                     'entry_bg': '#40444B', 'entry_fg': '#FFFFFF', 'log_bg': '#2C2F33', 'log_fg': '#FFFFFF'}
        }
        self.apply_theme()

        self.notebook = ttk.Notebook(root, style='Custom.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.bot_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.bot_frame, text='Bot Announce')
        self.bot_runner = ClientRunner(is_bot=True)
        self.setup_bot_tab()

        self.user_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.user_frame, text='User Ads')
        self.user_runner = ClientRunner(is_bot=False)
        self.setup_user_tab()

        self.theme_btn = tk.Button(root, text="Toggle Theme", command=self.toggle_theme,
                                  bg=self.themes[self.theme]['btn_bg'], fg=self.themes[self.theme]['fg'],
                                  activebackground=self.themes[self.theme]['btn_hover'])
        self.theme_btn.pack(pady=5)

        # Style for notebook tabs
        style = ttk.Style()
        style.configure('Custom.TNotebook.Tab', background=self.themes[self.theme]['bg'],
                        foreground=self.themes[self.theme]['fg'], padding=[10, 5])
        style.map('Custom.TNotebook.Tab', background=[('selected', self.themes[self.theme]['entry_bg'])],
                  foreground=[('selected', self.themes[self.theme]['fg'])])

    def apply_theme(self):
        theme = self.themes[self.theme]
        self.root.configure(bg=theme['bg'])
        self.update_widget_themes(self.root)

    def toggle_theme(self):
        self.theme = 'dark' if self.theme == 'light' else 'light'
        self.apply_theme()
        self.notebook.configure(style='Custom.TNotebook')
        self.update_notebook_style()

    def update_widget_themes(self, widget):
        theme = self.themes[self.theme]
        try:
            widget.configure(bg=theme['bg'], fg=theme['fg'])
            if isinstance(widget, tk.Entry):
                widget.configure(bg=theme['entry_bg'], fg=theme['entry_fg'], insertbackground=theme['fg'])
            elif isinstance(widget, tk.Text):
                widget.configure(bg=theme['entry_bg'], fg=theme['entry_fg'])
            elif isinstance(widget, tk.Button):
                widget.configure(bg=theme['btn_bg'], fg=theme['fg'], activebackground=theme['btn_hover'],
                                disabledforeground=theme['btn_disabled'])
            elif isinstance(widget, scrolledtext.ScrolledText):
                widget.configure(bg=theme['log_bg'], fg=theme['log_fg'])
        except:
            pass
        for child in widget.winfo_children():
            self.update_widget_themes(child)

    def update_notebook_style(self):
        theme = self.themes[self.theme]
        style = ttk.Style()
        style.configure('Custom.TNotebook.Tab', background=theme['bg'], foreground=theme['fg'], padding=[10, 5])
        style.map('Custom.TNotebook.Tab', background=[('selected', theme['entry_bg'])],
                  foreground=[('selected', theme['fg'])])

    def setup_bot_tab(self):
        theme = self.themes[self.theme]
        tk.Label(self.bot_frame, text="Bot Token:", bg=theme['bg'], fg=theme['fg']).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.bot_token_entry = tk.Entry(self.bot_frame, width=50, show="*", bg=theme['entry_bg'], fg=theme['entry_fg'])
        self.bot_token_entry.grid(row=0, column=1, padx=10, pady=5, sticky="we")
        tk.Button(self.bot_frame, text="Load Token", command=self.load_bot_token_file, bg='#FF9800', fg='white',
                  activebackground='#F57C00').grid(row=0, column=2, padx=5, pady=5)

        tk.Label(self.bot_frame, text="Server IDs (one per line):", bg=theme['bg'], fg=theme['fg']).grid(row=1, column=0, sticky="nw", padx=10, pady=5)
        self.bot_ch_text = tk.Text(self.bot_frame, height=5, width=50, bg=theme['entry_bg'], fg=theme['entry_fg'])
        self.bot_ch_text.grid(row=1, column=1, padx=10, pady=5, sticky="we")

        tk.Label(self.bot_frame, text="Delay (seconds):", bg=theme['bg'], fg=theme['fg']).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.bot_delay_entry = tk.Entry(self.bot_frame, width=10, bg=theme['entry_bg'], fg=theme['entry_fg'])
        self.bot_delay_entry.insert(0, "5")
        self.bot_delay_entry.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        tk.Label(self.bot_frame, text="Message to send:", bg=theme['bg'], fg=theme['fg']).grid(row=3, column=0, sticky="nw", padx=10, pady=5)
        self.bot_msg_text = tk.Text(self.bot_frame, height=6, width=50, bg=theme['entry_bg'], fg=theme['entry_fg'])
        self.bot_msg_text.grid(row=3, column=1, padx=10, pady=5, sticky="we")

        btn_frame = tk.Frame(self.bot_frame, bg=theme['bg'])
        btn_frame.grid(row=4, column=1, sticky="w", pady=10)
        self.bot_start_btn = tk.Button(btn_frame, text="Start Bot", command=self.start_bot, bg='#4CAF50', fg='white',
                                      activebackground='#45a049')
        self.bot_start_btn.grid(row=0, column=0, padx=5)
        self.bot_stop_btn = tk.Button(btn_frame, text="Stop Bot", command=self.stop_bot, bg='#F44336', fg='white',
                                     activebackground='#D32F2F')
        self.bot_stop_btn.grid(row=0, column=1, padx=5)
        self.bot_run_btn = tk.Button(btn_frame, text="Start Sending", command=self.bot_start_sending, state="disabled",
                                    bg='#2196F3', fg='white', activebackground='#1976D2')
        self.bot_run_btn.grid(row=0, column=2, padx=5)
        self.bot_pause_btn = tk.Button(btn_frame, text="Stop Sending", command=self.bot_stop_sending, state="disabled",
                                      bg='#FF9800', fg='white', activebackground='#F57C00')
        self.bot_pause_btn.grid(row=0, column=3, padx=5)

        tk.Label(self.bot_frame, text="Log:", bg=theme['bg'], fg=theme['fg']).grid(row=5, column=0, sticky="nw", padx=10, pady=5)
        self.bot_log_box = scrolledtext.ScrolledText(self.bot_frame, width=60, height=10, state="disabled",
                                                    bg=theme['log_bg'], fg=theme['log_fg'])
        self.bot_log_box.grid(row=5, column=1, columnspan=2, padx=10, pady=5, sticky="we")
        self.configure_log_tags(self.bot_log_box)

        self.bot_frame.grid_columnconfigure(1, weight=1)

    def setup_user_tab(self):
        theme = self.themes[self.theme]
        tk.Label(self.user_frame, text="User Token:", bg=theme['bg'], fg=theme['fg']).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.user_token_entry = tk.Entry(self.user_frame, width=50, show="*", bg=theme['entry_bg'], fg=theme['entry_fg'])
        self.user_token_entry.grid(row=0, column=1, padx=10, pady=5, sticky="we")
        tk.Button(self.user_frame, text="Load Token", command=self.load_user_token_file, bg='#FF9800', fg='white',
                  activebackground='#F57C00').grid(row=0, column=2, padx=5, pady=5)

        tk.Label(self.user_frame, text="Channel IDs (one per line):", bg=theme['bg'], fg=theme['fg']).grid(row=1, column=0, sticky="nw", padx=10, pady=5)
        self.user_ch_text = tk.Text(self.user_frame, height=5, width=50, bg=theme['entry_bg'], fg=theme['entry_fg'])
        self.user_ch_text.grid(row=1, column=1, padx=10, pady=5, sticky="we")

        tk.Label(self.user_frame, text="Delay (minutes):", bg=theme['bg'], fg=theme['fg']).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.user_delay_entry = tk.Entry(self.user_frame, width=10, bg=theme['entry_bg'], fg=theme['entry_fg'])
        self.user_delay_entry.insert(0, "1")
        self.user_delay_entry.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        tk.Label(self.user_frame, text="Message to send:", bg=theme['bg'], fg=theme['fg']).grid(row=3, column=0, sticky="nw", padx=10, pady=5)
        self.user_msg_text = tk.Text(self.user_frame, height=6, width=50, bg=theme['entry_bg'], fg=theme['entry_fg'])
        self.user_msg_text.grid(row=3, column=1, padx=10, pady=5, sticky="we")

        btn_frame = tk.Frame(self.user_frame, bg=theme['bg'])
        btn_frame.grid(row=4, column=1, sticky="w", pady=10)
        self.user_start_btn = tk.Button(btn_frame, text="Start User", command=self.start_user, bg='#4CAF50', fg='white',
                                       activebackground='#45a049')
        self.user_start_btn.grid(row=0, column=0, padx=5)
        self.user_stop_btn = tk.Button(btn_frame, text="Stop User", command=self.stop_user, bg='#F44336', fg='white',
                                      activebackground='#D32F2F')
        self.user_stop_btn.grid(row=0, column=1, padx=5)
        self.user_run_btn = tk.Button(btn_frame, text="Start Sending", command=self.user_start_sending, state="disabled",
                                     bg='#2196F3', fg='white', activebackground='#1976D2')
        self.user_run_btn.grid(row=0, column=2, padx=5)
        self.user_pause_btn = tk.Button(btn_frame, text="Stop Sending", command=self.user_stop_sending, state="disabled",
                                       bg='#FF9800', fg='white', activebackground='#F57C00')
        self.user_pause_btn.grid(row=0, column=3, padx=5)

        tk.Label(self.user_frame, text="Log:", bg=theme['bg'], fg=theme['fg']).grid(row=5, column=0, sticky="nw", padx=10, pady=5)
        self.user_log_box = scrolledtext.ScrolledText(self.user_frame, width=60, height=10, state="disabled",
                                                     bg=theme['log_bg'], fg=theme['log_fg'])
        self.user_log_box.grid(row=5, column=1, columnspan=2, padx=10, pady=5, sticky="we")
        self.configure_log_tags(self.user_log_box)

        self.user_frame.grid_columnconfigure(1, weight=1)

    def configure_log_tags(self, log_box):
        log_box.tag_config('success', foreground='#4CAF50')
        log_box.tag_config('error', foreground='#F44336')
        log_box.tag_config('warning', foreground='#FF9800')
        log_box.tag_config('info', foreground='#2196F3')

    def load_bot_token_file(self):
        try:
            with open("bot_token.txt", "r", encoding="utf-8") as f:
                token = f.read().strip()
            self.bot_token_entry.delete(0, tk.END)
            self.bot_token_entry.insert(0, token)
            self.bot_log("Loaded token from bot_token.txt", 'success')
        except Exception as e:
            messagebox.showerror("Error", f"Cannot load token file: {e}")

    def load_user_token_file(self):
        try:
            with open("user_token.txt", "r", encoding="utf-8") as f:
                token = f.read().strip()
            self.user_token_entry.delete(0, tk.END)
            self.user_token_entry.insert(0, token)
            self.user_log("Loaded token from user_token.txt", 'success')
        except Exception as e:
            messagebox.showerror("Error", f"Cannot load token file: {e}")

    def bot_log(self, text, tag='info'):
        self.log(self.bot_log_box, text, tag)

    def user_log(self, text, tag='info'):
        self.log(self.user_log_box, text, tag)

    def log(self, log_box, text, tag='info'):
        log_box.configure(state="normal")
        log_box.insert(tk.END, text + "\n", tag)
        log_box.see(tk.END)
        log_box.configure(state="disabled")

    def start_bot(self):
        token = self.bot_token_entry.get().strip()
        if not token:
            messagebox.showwarning("Missing token", "Please enter bot token.")
            return
        try:
            self.bot_runner.start_loop(token, lambda t, tag: self.root.after(0, self.bot_log, t, tag))
            self.bot_run_btn.config(state="normal")
            self.bot_pause_btn.config(state="normal")
            self.bot_start_btn.config(state="disabled")
            self.bot_stop_btn.config(state="normal")
            self.bot_log("[UI] Bot start requested.", 'info')
        except Exception as e:
            messagebox.showerror("Start failed", str(e))

    def stop_bot(self):
        try:
            if self.bot_runner.loop and self.bot_runner.loop.is_running():
                try:
                    self.bot_runner.enqueue({"action": "shutdown"})
                except Exception:
                    pass
                self.bot_runner.stop_loop(lambda t, tag: self.root.after(0, self.bot_log, t, tag))
            self.bot_start_btn.config(state="normal")
            self.bot_run_btn.config(state="disabled")
            self.bot_pause_btn.config(state="disabled")
            self.bot_stop_btn.config(state="disabled")
            self.bot_log("[UI] Bot stop requested.", 'info')
        except Exception as e:
            messagebox.showerror("Stop failed", str(e))

    def start_user(self):
        token = self.user_token_entry.get().strip()
        if not token:
            messagebox.showwarning("Missing token", "Please enter user token.")
            return
        try:
            self.user_runner.start_loop(token, lambda t, tag: self.root.after(0, self.user_log, t, tag))
            self.user_run_btn.config(state="normal")
            self.user_pause_btn.config(state="normal")
            self.user_start_btn.config(state="disabled")
            self.user_stop_btn.config(state="normal")
            self.user_log("[UI] User start requested.", 'info')
        except Exception as e:
            messagebox.showerror("Start failed", str(e))

    def stop_user(self):
        try:
            if self.user_runner.loop and self.user_runner.loop.is_running():
                try:
                    self.user_runner.enqueue({"action": "shutdown"})
                except Exception:
                    pass
                self.user_runner.stop_loop(lambda t, tag: self.root.after(0, self.user_log, t, tag))
            self.user_start_btn.config(state="normal")
            self.user_run_btn.config(state="disabled")
            self.user_pause_btn.config(state="disabled")
            self.user_stop_btn.config(state="disabled")
            self.user_log("[UI] User stop requested.", 'info')
        except Exception as e:
            messagebox.showerror("Stop failed", str(e))

    def _parse_channel_ids(self, ch_text):
        txt = ch_text.get("1.0", tk.END).strip().splitlines()
        ids = []
        for line in txt:
            s = line.strip()
            if s:
                try:
                    ids.append(int(s))
                except:
                    continue
        return ids

    def bot_start_sending(self):
        self.start_sending(self.bot_runner, self.bot_ch_text, self.bot_delay_entry, self.bot_msg_text, self.bot_log, delay_multiplier=1, is_guild=True)

    def user_start_sending(self):
        self.start_sending(self.user_runner, self.user_ch_text, self.user_delay_entry, self.user_msg_text, self.user_log, delay_multiplier=60, is_guild=False)

    def start_sending(self, runner, ch_text, delay_entry, msg_text, log_func, delay_multiplier=1, is_guild=False):
        try:
            targets = self._parse_channel_ids(ch_text)
            if not targets:
                messagebox.showwarning("No targets", "Please enter at least one server/channel ID.")
                return
            try:
                delay = float(delay_entry.get().strip()) * delay_multiplier
            except:
                messagebox.showwarning("Delay error", "Delay must be a number.")
                return
            message = msg_text.get("1.0", tk.END).strip()
            if not message:
                messagebox.showwarning("Empty message", "Please enter a message to send.")
                return
            item = {"action": "start", "channels": targets, "delay": delay, "message": message}
            runner.enqueue(item)
            log_func("[UI] Enqueued start sending.", 'info')
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def bot_stop_sending(self):
        self.stop_sending(self.bot_runner, self.bot_log)

    def user_stop_sending(self):
        self.stop_sending(self.user_runner, self.user_log)

    def stop_sending(self, runner, log_func):
        try:
            runner.enqueue({"action": "stop"})
            log_func("[UI] Enqueued stop sending.", 'info')
        except Exception as e:
            messagebox.showerror("Error", str(e))

def main():
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop_bot(), app.stop_user(), root.destroy()))
    root.geometry("600x700")
    root.mainloop()

if __name__ == "__main__":
    main()