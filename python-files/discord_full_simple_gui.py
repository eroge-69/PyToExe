import json, os, threading, tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import discord
from discord.ext import commands

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        default = {
            "token": "",
            "channels": [],
            "interval_cycle": 300,
            "interval_channel": 10,
            "reply_delays": [15, 3, 30],
            "replies": ["", "", ""]
        }
        save_config(default)
        return default
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

config = load_config()

intents = discord.Intents.default()
intents.messages = True
intents.dm_messages = True
client = commands.Bot(command_prefix="!", self_bot=True, intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    log_box.insert(tk.END, f"Berhasil login sebagai {client.user}\n")
    log_box.see(tk.END)

@client.event
async def on_message(message: discord.Message):
    try:
        if message.author.id == client.user.id or message.author.bot:
            return
        if isinstance(message.channel, discord.DMChannel):
            cfg = load_config()
            delays = cfg.get("reply_delays", [15, 3, 30])
            replies = cfg.get("replies", ["", "", ""])
            for delay, reply in zip(delays, replies):
                if not reply.strip():
                    continue
                await asyncio.sleep(delay)
                await message.channel.send(reply)
                log_box.insert(tk.END, f"Auto reply ke {message.author}: {reply}\n")
                log_box.see(tk.END)
    except Exception as e:
        log_box.insert(tk.END, f"Error auto-reply: {e}\n")
        log_box.see(tk.END)

root = tk.Tk()
root.title("Discord Selfbot GUI + Klik Kanan Paste")

# ========= MENU KLIK KANAN =========
def add_context_menu(widget):
    menu = tk.Menu(widget, tearoff=0)
    menu.add_command(label="Cut", command=lambda: widget.event_generate("<<Cut>>"))
    menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
    menu.add_command(label="Paste", command=lambda: widget.event_generate("<<Paste>>"))

    def popup(event):
        menu.tk_popup(event.x_root, event.y_root)
    widget.bind("<Button-3>", popup)

# ========== GUI ==============
tk.Label(root, text="Token:").grid(row=0, column=0, sticky="w")
token_entry = tk.Entry(root, width=70)
token_entry.grid(row=0, column=1, columnspan=3, sticky="w")
token_entry.insert(0, config["token"])
add_context_menu(token_entry)

tk.Label(root, text="Daftar Channel dan Pesan (format: ChannelID : Pesan):").grid(row=1, column=0, sticky="w", pady=(5,0))
channels_text = tk.Text(root, width=80, height=6)
channels_text.grid(row=2, column=0, columnspan=4, sticky="nsew")
if config["channels"]:
    txt = "\n".join(f"{c['id']} : {c['msg']}" for c in config["channels"])
    channels_text.insert(tk.END, txt)
add_context_menu(channels_text)

tk.Label(root, text="Interval antar cycle (detik):").grid(row=3, column=0, sticky="w")
cycle_entry = tk.Entry(root, width=6)
cycle_entry.insert(0, str(config["interval_cycle"]))
cycle_entry.grid(row=3, column=1, sticky="w")
add_context_menu(cycle_entry)

tk.Label(root, text="Interval antar channel (detik):").grid(row=3, column=2, sticky="w")
chan_entry = tk.Entry(root, width=6)
chan_entry.insert(0, str(config["interval_channel"]))
chan_entry.grid(row=3, column=3, sticky="w")
add_context_menu(chan_entry)

reply_delay = config["reply_delays"]
reply_text = config["replies"]
labels = ["1", "2", "3"]
delay_entry, text_entry = [], []
for i, n in enumerate(labels):
    tk.Label(root, text=f"Reply {n} delay (detik):").grid(row=4+i, column=0, sticky="w")
    e1 = tk.Entry(root, width=6)
    e1.insert(0, str(reply_delay[i]))
    e1.grid(row=4+i, column=1, sticky="w")
    delay_entry.append(e1)
    add_context_menu(e1)

    tk.Label(root, text=f"Reply {n} isi:").grid(row=4+i, column=2, sticky="w")
    e2 = tk.Entry(root, width=30)
    e2.insert(0, reply_text[i])
    e2.grid(row=4+i, column=3, sticky="w")
    text_entry.append(e2)
    add_context_menu(e2)

log_box = tk.Text(root, width=80, height=10)
log_box.grid(row=8, column=0, columnspan=4)
add_context_menu(log_box)

bot_thread = None
running = False

def parse_channels_from_text():
    lines = channels_text.get("1.0", tk.END).strip().splitlines()
    result = []
    for line in lines:
        if ":" in line:
            parts = line.split(":", 1)
            cid = parts[0].strip()
            msg = parts[1].strip()
            if cid:
                result.append({"id": cid, "msg": msg})
    return result

def start_bot():
    global bot_thread, running
    running = True
    log_box.insert(tk.END, "Memulai bot...\n")
    log_box.see(tk.END)
    cfg = {
        "token": token_entry.get().strip(),
        "channels": parse_channels_from_text(),
        "interval_cycle": int(cycle_entry.get() or 300),
        "interval_channel": int(chan_entry.get() or 10),
        "reply_delays": [int(d.get() or 0) for d in delay_entry],
        "replies": [t.get() for t in text_entry]
    }
    save_config(cfg)

    def run():
        try:
            client.run(cfg["token"])
        except Exception as e:
            log_box.insert(tk.END, f"Error: {e}\n")
            log_box.see(tk.END)
            running = False
    bot_thread = threading.Thread(target=run, daemon=True)
    bot_thread.start()

def stop_bot():
    global running
    running = False
    try:
        asyncio.run_coroutine_threadsafe(client.close(), client.loop)
        log_box.insert(tk.END, "Bot dihentikan.\n")
        log_box.see(tk.END)
    except Exception as e:
        log_box.insert(tk.END, f"Error stop: {e}\n")
        log_box.see(tk.END)

def save_current_config():
    cfg = {
        "token": token_entry.get().strip(),
        "channels": parse_channels_from_text(),
        "interval_cycle": int(cycle_entry.get() or 300),
        "interval_channel": int(chan_entry.get() or 10),
        "reply_delays": [int(d.get() or 0) for d in delay_entry],
        "replies": [t.get() for t in text_entry]
    }
    save_config(cfg)
    log_box.insert(tk.END, "Config berhasil disimpan.\n")
    log_box.see(tk.END)

def load_current_config():
    cfg = load_config()
    token_entry.delete(0, tk.END)
    token_entry.insert(0, cfg["token"])
    cycle_entry.delete(0, tk.END)
    cycle_entry.insert(0, str(cfg["interval_cycle"]))
    chan_entry.delete(0, tk.END)
    chan_entry.insert(0, str(cfg["interval_channel"]))
    for i in range(3):
        delay_entry[i].delete(0, tk.END)
        delay_entry[i].insert(0, str(cfg["reply_delays"][i]))
        text_entry[i].delete(0, tk.END)
        text_entry[i].insert(0, cfg["replies"][i])
    channels_text.delete("1.0", tk.END)
    if cfg["channels"]:
        txt = "\n".join(f"{c['id']} : {c['msg']}" for c in cfg["channels"])
        channels_text.insert(tk.END, txt)
    log_box.insert(tk.END, "Config berhasil di-load.\n")
    log_box.see(tk.END)

tk.Button(root, text="Start Bot", command=start_bot).grid(row=7, column=0)
tk.Button(root, text="Stop Bot", command=stop_bot).grid(row=7, column=1)
tk.Button(root, text="Save Config", command=save_current_config).grid(row=7, column=2)
tk.Button(root, text="Load Config", command=load_current_config).grid(row=7, column=3)

root.mainloop()