import tkinter as tk
from tkinter import ttk, messagebox
from xrpl.wallet import Wallet
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import Payment
from xrpl.models.requests import AccountInfo
from xrpl.transaction import submit_and_wait
from xrpl.utils import xrp_to_drops, drops_to_xrp
from xrpl.core.addresscodec import is_valid_classic_address
import qrcode
from PIL import Image, ImageTk
import io, requests, threading
from datetime import datetime
from pathlib import Path

# === Constants === #
MAINNET_URL = "https://s1.ripple.com:51234"
TESTNET_URL = "https://s.altnet.rippletest.net:51234"
THEME_BG = "#1e1e1e"
THEME_FG = "white"
FONT_TITLE = ("Arial", 14, "bold")
FONT_BODY = ("Arial", 12)

# === App Setup === #
app = tk.Tk()
app.title("xAneyL_3.2 Desktop Wallet")
app.geometry("1000x750")
app.configure(bg=THEME_BG)



# === Clients (Mainnet Selectable) === #
mainnet_rpc_choice = tk.StringVar(value=MAINNET_URL)
client_mainnet = JsonRpcClient(mainnet_rpc_choice.get())
client_testnet = JsonRpcClient(TESTNET_URL)

style = ttk.Style()
style.theme_use("default")
style.configure("TNotebook", background=THEME_BG)
style.configure("TNotebook.Tab", background="#2a2a2a", foreground="white", padding=10)
style.map("TNotebook.Tab", background=[("selected", "#444")])

notebook = ttk.Notebook(app)
mainnet_tab = tk.Frame(notebook, bg=THEME_BG)
testnet_tab = tk.Frame(notebook, bg=THEME_BG)
notebook.add(mainnet_tab, text="🌐 Mainnet")
notebook.add(testnet_tab, text="🧪 Testnet")
explorer_tab = tk.Frame(notebook, bg=THEME_BG)
notebook.add(explorer_tab, text="🔎 Explorer")
meme_tab = tk.Frame(notebook, bg=THEME_BG)
notebook.add(meme_tab, text="🪙 Meme Coin")
notebook.pack(expand=1, fill="both")
vanity_tab = tk.Frame(notebook, bg=THEME_BG)
notebook.add(vanity_tab, text="🎯 Vanity")

# === Utility Functions === #
def log(widget, msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    widget.insert(tk.END, f"[{timestamp}] {msg}\n")
    widget.see(tk.END)

def save_wallet(seed, address):
    Path("wallets").mkdir(exist_ok=True)
    filename = f"wallets/wallet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w") as f:
        f.write(f"Seed: {seed}\nAddress: {address}\n")
    return filename

def show_qr(address):
    qr_img = qrcode.make(address)
    buf = io.BytesIO()
    qr_img.save(buf, format="PNG")
    top = tk.Toplevel(app)
    top.title("📷 QR Code")
    img = ImageTk.PhotoImage(Image.open(buf))
    label = tk.Label(top, image=img)
    label.image = img
    label.pack()

# === Core Wallet Logic === #
def threaded(func):
    def wrapper(*args, **kwargs):
        threading.Thread(target=lambda: func(*args, **kwargs)).start()
    return wrapper

@threaded
def generate_wallet(vars, logbox, is_mainnet=False):
    wallet = Wallet.create()
    vars['seed'].set(wallet.seed)
    vars['address'].set(wallet.classic_address)
    vars['valid'].set("✅")
    if is_mainnet:
        path = save_wallet(wallet.seed, wallet.classic_address)
        log(logbox, f"📁 Saved wallet to {path}")
    log(logbox, f"🎲 Generated wallet {wallet.classic_address}")

@threaded
def import_wallet(vars, logbox):
    try:
        wallet = Wallet.from_seed(vars['seed'].get().strip())
        vars['address'].set(wallet.classic_address)
        vars['valid'].set("✅")
        log(logbox, f"🔑 Imported wallet {wallet.classic_address}")
    except Exception as e:
        vars['valid'].set("❌")
        log(logbox, f"❌ Import error: {e}")

@threaded
def check_balance(client, address, logbox, balance_var):
    try:
        req = AccountInfo(account=address, ledger_index="validated")
        res = client.request(req).result
        balance = drops_to_xrp(res["account_data"]["Balance"])
        balance_var.set(f"{balance} XRP")
        log(logbox, f"💰 Balance: {balance} XRP")
    except Exception:
        balance_var.set("0 XRP")
        log(logbox, "⚠️ Could not fetch balance. Wallet may be unfunded.")

@threaded
def send_xrp(client, vars, logbox):
    try:
        seed = vars['seed'].get().strip()
        dest = vars['dest'].get().strip()
        tag = vars['tag'].get().strip()
        amount = float(vars['amount'].get().strip())
        wallet = Wallet.from_seed(seed)
        tx = Payment(
            account=wallet.classic_address,
            amount=xrp_to_drops(amount),
            destination=dest,
            destination_tag=int(tag) if tag else None
        )
        result = submit_and_wait(tx, client, wallet)
        res = result.result
        fee = drops_to_xrp(res['tx_json'].get('Fee', '0'))
        log(logbox, f"✅ Sent {format(amount, '.6f')} XRP to {dest}\n🔁 TX: {res.get('hash', 'N/A')} | Fee: {fee} XRP")
    except Exception as e:
        log(logbox, f"❌ Send error: {e}")

@threaded
def fund_with_faucet(address, logbox, client, balance_var):
    try:
        res = requests.post("https://faucet.altnet.rippletest.net/accounts", json={"destination": address})
        if res.status_code == 200:
            log(logbox, "🚰 Faucet funded successfully!")
            threading.Timer(5, lambda: check_balance(client, address, logbox, balance_var)).start()
        else:
            log(logbox, "❌ Faucet funding failed.")
    except Exception as e:
        log(logbox, f"❌ Faucet error: {e}")

# === GUI Component === #
def build_wallet_ui(frame, client, is_mainnet):
    auto_refresh = tk.BooleanVar(value=False)

    def refresh_loop():
        if auto_refresh.get():
            check_balance(client, vars['address'].get(), logbox, balance_var)
            frame.after(15000, refresh_loop)  # refresh every 15s

        frame.after(15000, refresh_loop)  # start loop
    vars = {k: tk.StringVar() for k in ["seed", "address", "amount", "dest", "tag", "valid"]}
    balance_var = tk.StringVar()

    def slider_action(val):
        if int(val) == 100:
            slider.set(0)
            confirm = messagebox.askyesno("Confirm Transaction", "Are you sure you want to send this XRP?")
            if confirm:
                send_xrp(client, vars, logbox)

    # Layout
    for label, var in [("🔐 Seed:", "seed"), ("🏦 Address:", "address")]:
        tk.Label(frame, text=label, fg=THEME_FG, bg=THEME_BG, font=FONT_BODY).pack()
        show = '' if var != 'seed' else '*'
        entry = tk.Entry(frame, textvariable=vars[var], width=60, show=show)
        entry.pack()
        if var == 'seed':
            def reveal(event, e=entry): e.config(show='')
            def hide(event, e=entry): e.config(show='*')
            entry.bind('<Enter>', reveal)
            entry.bind('<Leave>', hide)

    box = tk.Frame(frame, bg="#222")
    box.pack(pady=5, fill=tk.X, padx=10)

    button_frame = tk.Frame(box, bg=THEME_BG)
    button_frame.pack(pady=5)
    tk.Button(button_frame, text="📤 Import", command=lambda: import_wallet(vars, logbox)).pack(side=tk.LEFT, padx=4)
    tk.Button(button_frame, text="🎲 Generate", command=lambda: generate_wallet(vars, logbox, is_mainnet)).pack(side=tk.LEFT, padx=4)
    tk.Button(button_frame, text="🔍 QR", command=lambda: show_qr(vars['address'].get())).pack(side=tk.LEFT, padx=4)
    tk.Button(button_frame, text="📡 Check Balance", command=lambda: check_balance(client, vars['address'].get(), logbox, balance_var)).pack(side=tk.LEFT, padx=4)

    if not is_mainnet:
        tk.Button(frame, text="🚰 Fund Faucet", command=lambda: fund_with_faucet(vars['address'].get(), logbox, client, balance_var)).pack(pady=2)

    tk.Label(frame, textvariable=vars['valid'], fg="green", bg=THEME_BG, font=FONT_BODY).pack()

    balance_box = tk.LabelFrame(frame, text="💰 Wallet Balance", bg=THEME_BG, fg="cyan", font=FONT_TITLE)
    balance_box.pack(fill=tk.X, padx=10, pady=5)

    tk.Checkbutton(frame, text="🔄 Auto Refresh Balance", variable=auto_refresh, bg=THEME_BG, fg=THEME_FG, font=FONT_BODY, selectcolor=THEME_BG, activebackground=THEME_BG).pack()
    tk.Label(balance_box, textvariable=balance_var, fg="cyan", bg=THEME_BG, font=FONT_TITLE).pack(pady=4)

    for label, var in [("📨 Send To:", "dest"), ("💸 Amount XRP:", "amount"), ("🏷️ Destination Tag:", "tag")]:
        tk.Label(frame, text=label, fg=THEME_FG, bg=THEME_BG, font=FONT_BODY).pack()
        tk.Entry(frame, textvariable=vars[var]).pack()

        slider = tk.Scale(frame, from_=0, to=100, orient=tk.HORIZONTAL, length=300, label="Slide to Sign & Send", command=slider_action)
    slider.pack(pady=5)
    logbox = tk.Text(frame, bg="#121212", fg="white", height=15)
    logbox.pack(fill=tk.BOTH, expand=True, pady=6)
    vars['balance'] = balance_var
    return vars

# === WebSocket Listener === #
import asyncio
import websockets
import json

def start_websocket_listener(address, logbox, balance_var):
    async def listen():
        uri = "wss://xrplcluster.com"
        try:
            async with websockets.connect(uri) as ws:
                subscribe_msg = json.dumps({
                    "command": "subscribe",
                    "accounts": [address]
                })
                await ws.send(subscribe_msg)
                while True:
                    response = await ws.recv()
                    msg = json.loads(response)
                    if "transaction" in msg:
                        tx = msg["transaction"]
                        if tx.get("Destination") == address:
                            log(logbox, f"📥 Incoming payment detected!")
                            check_balance(client_mainnet, address, logbox, balance_var)
        except Exception as e:
            log(logbox, f"❌ WebSocket error: {e}")

    def run():
        asyncio.run(listen())

    threading.Thread(target=run, daemon=True).start()


logo = Image.open("ripple_logo.png")
logo = logo.resize((100, 30))
logo_img = ImageTk.PhotoImage(logo)
label_frame = tk.Frame(mainnet_tab, bg=THEME_BG)
tk.Label(label_frame, image=logo_img, bg=THEME_BG).pack(side="left")
tk.Label(label_frame, text="xAneyL_3.2", font=("Arial", 10), fg="#008cff", bg=THEME_BG).pack(side="left", padx=5)
label_frame.pack(pady=(10, 2))
label_frame.image = logo_img
tk.Label(mainnet_tab, text="🌐 Select Mainnet RPC Endpoint:", bg=THEME_BG, fg=THEME_FG, font=FONT_BODY).pack(pady=4)
ttk.Combobox(mainnet_tab, textvariable=mainnet_rpc_choice, values=[
    "https://s1.ripple.com:51234",
    "https://s2.ripple.com:51234",
    "https://xrplcluster.com",
    "https://rpc.xrplf.org"
], state="readonly", width=40).pack(pady=2)

# Update client after RPC selection
mainnet_rpc_choice.trace_add("write", lambda *_, var=mainnet_rpc_choice: update_mainnet_client(var.get()))

def update_mainnet_client(url):
    global client_mainnet
    client_mainnet = JsonRpcClient(url)

w_mainnet_vars = build_wallet_ui(mainnet_tab, client_mainnet, is_mainnet=True)
def delayed_websocket_start():
    start_websocket_listener(w_mainnet_vars['address'].get(), mainnet_tab.children['!text'], w_mainnet_vars['balance'])

app.after(1000, delayed_websocket_start)
left = tk.Frame(testnet_tab, bg=THEME_BG); left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
right = tk.Frame(testnet_tab, bg=THEME_BG); right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
build_wallet_ui(left, client_testnet, is_mainnet=False)
build_wallet_ui(right, client_testnet, is_mainnet=False)

import webbrowser

def open_explorer():
    explorer = explorer_choice.get()
    tab = explorer_tab_choice.get()
    addr = w_mainnet_vars['address'].get().strip() if tab == "Mainnet" else ""
    if tab == "Testnet":
        test_addr = left.children.get('!entry') or list(left.children.values())[1]
        addr = test_addr.get().strip() if hasattr(test_addr, 'get') else ""

    if not addr:
        messagebox.showwarning("No Address", "Please import or generate a wallet first.")
        return

    base_url = {
        "Bithomp": "https://bithomp.com/explorer/" if tab == "Mainnet" else "https://test.bithomp.com/explorer/",
        "XRPSCAN": "https://xrpscan.com/account/"
    }.get(explorer, "https://bithomp.com/explorer/")

    if messagebox.askyesno("Open Explorer", f"Open {tab} wallet on {explorer}?"):
        webbrowser.open(base_url + addr)

tk.Label(explorer_tab, text="🔎 XRPL Explorer Viewer", bg=THEME_BG, fg=THEME_FG, font=FONT_TITLE).pack(pady=20)
explorer_choice = tk.StringVar(value="Bithomp")
explorer_tab_choice = tk.StringVar(value="Mainnet")

tk.Label(explorer_tab, text="Choose Explorer:", bg=THEME_BG, fg=THEME_FG, font=FONT_BODY).pack(pady=5)
ttk.Combobox(explorer_tab, textvariable=explorer_choice, values=["Bithomp", "XRPSCAN"], state="readonly").pack()

tk.Label(explorer_tab, text="Select Network:", bg=THEME_BG, fg=THEME_FG, font=FONT_BODY).pack(pady=5)
ttk.Combobox(explorer_tab, textvariable=explorer_tab_choice, values=["Mainnet", "Testnet"], state="readonly").pack()

tk.Button(explorer_tab, text="🌐 Open Explorer", font=FONT_BODY, command=open_explorer).pack(pady=10)

# === Vanity Tab === #
import random

try:
    with open("google20kwords", "r") as f:
        DEFAULT_WORDS = [w.strip().lower() for w in f if 3 <= len(w.strip()) <= 8]
except Exception:
    DEFAULT_WORDS = [
        "bear", "moon", "wow", "cool", "cash", "king", "bull", "rich", "xrp", "pump", "gold", "moonshot"
    ]

vanity_running = threading.Event()
vanity_prefix = tk.StringVar()
vanity_status = tk.StringVar(value="Waiting to start...")
vanity_threads = tk.StringVar(value="4")
vanity_match = tk.StringVar()
vanity_mode = tk.StringVar(value="manual")
vanity_length = tk.StringVar(value="4")

vanity_log = tk.Text(vanity_tab, bg="#121212", fg="white", height=15)

vanity_running = threading.Event()

vanity_prefix = tk.StringVar()
vanity_status = tk.StringVar(value="Waiting to start...")
vanity_match = tk.StringVar()

vanity_log = tk.Text(vanity_tab, bg="#121212", fg="white", height=15)


def start_vanity_search():
    mode = vanity_mode.get()
    length = int(vanity_length.get())
    prefix = vanity_prefix.get().strip() if mode == "manual" else "r"

    if not prefix.startswith("r"):
        messagebox.showwarning("Invalid Prefix", "Prefix must start with 'r'")
        return

    vanity_running.set()
    vanity_status.set(f"Searching with {vanity_threads.get()} threads...")
    vanity_log.delete("1.0", tk.END)

    wordlist = DEFAULT_WORDS if mode == "wordlist" else []
    found = threading.Event()

    def loop(worker_id):
        tries = 0
        while vanity_running.is_set() and not found.is_set():
            tries += 1
            wallet = Wallet.create()
            addr = wallet.classic_address

            if mode == "wordlist":
                word = random.choice(wordlist)
                if len(word) == length - 1:
                    test = "r" + word
                    if addr.startswith(test):
                        found.set()
                        vanity_status.set(f"✅ Found '{test}' after {tries} tries [Worker {worker_id}]")
                        vanity_match.set(addr)
                        path = save_wallet(wallet.seed, addr)
                        log(vanity_log, f"📁 Saved to {path}")
                        return
            else:
                if addr.startswith(prefix):
                    found.set()
                    vanity_status.set(f"✅ Found after {tries} tries: {addr} [Worker {worker_id}]")
                    vanity_match.set(addr)
                    path = save_wallet(wallet.seed, addr)
                    log(vanity_log, f"📁 Saved to {path}")
                    return

            if tries % 500 == 0:
                log(vanity_log, f"[Worker {worker_id}] Tried {tries}... still searching")

    for i in range(int(vanity_threads.get())):
        threading.Thread(target=loop, args=(i+1,), daemon=True).start()

def stop_vanity_search():
    vanity_running.clear()
    vanity_status.set("Stopping...")


frame_top = tk.Frame(vanity_tab, bg=THEME_BG)
frame_top.pack(pady=10)
tk.Label(frame_top, text="🎯 Vanity Search Mode:", bg=THEME_BG, fg=THEME_FG, font=FONT_BODY).pack()
ttk.Combobox(frame_top, textvariable=vanity_mode, values=["manual", "wordlist"], state="readonly", width=20).pack(pady=2)

manual_frame = tk.Frame(frame_top, bg=THEME_BG)
tk.Label(manual_frame, text="Manual Prefix (starts with 'r'):", bg=THEME_BG, fg=THEME_FG, font=("Arial", 11)).pack()
tk.Entry(manual_frame, textvariable=vanity_prefix, width=30).pack()
manual_frame.pack()

auto_frame = tk.Frame(frame_top, bg=THEME_BG)
tk.Label(auto_frame, text="Auto Word Length (4–8):", bg=THEME_BG, fg=THEME_FG, font=("Arial", 11)).pack()
ttk.Combobox(auto_frame, textvariable=vanity_length, values=["4", "5", "6", "7", "8"], state="readonly").pack()

# Threads selector
tk.Label(auto_frame, text="Worker Threads:", bg=THEME_BG, fg=THEME_FG, font=("Arial", 11)).pack(pady=(10, 0))
ttk.Combobox(auto_frame, textvariable=vanity_threads, values=[str(i) for i in range(1, 17)], state="readonly").pack()
ttk.Combobox(auto_frame, textvariable=vanity_length, values=["4", "5", "6", "7", "8"], state="readonly").pack()
auto_frame.pack()

def toggle_vanity_mode(*_):
    if vanity_mode.get() == "manual":
        manual_frame.pack()
        auto_frame.forget()
    else:
        auto_frame.pack()
        manual_frame.forget()

vanity_mode.trace_add("write", toggle_vanity_mode)
toggle_vanity_mode()
tk.Entry(frame_top, textvariable=vanity_prefix, width=30).pack()

btns = tk.Frame(vanity_tab, bg=THEME_BG)
btns.pack(pady=5)
tk.Button(btns, text="🚀 Start", command=start_vanity_search).pack(side="left", padx=5)
tk.Button(btns, text="🛑 Stop", command=stop_vanity_search).pack(side="left", padx=5)

vanity_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
tk.Label(vanity_tab, textvariable=vanity_status, fg="cyan", bg=THEME_BG, font=("Arial", 11, "italic")).pack()
tk.Label(vanity_tab, textvariable=vanity_match, fg="#00ffcc", bg=THEME_BG, font=("Courier", 11, "bold")).pack(pady=(0, 10))

# === Meme Coin Tab Content === #
tk.Label(meme_tab, text="🪙 Meme Coin Tools Coming Soon", bg=THEME_BG, fg=THEME_FG, font=FONT_TITLE).pack(pady=30)
tk.Label(meme_tab, text="Here you’ll be able to view, send, and receive meme tokens on the XRPL.", bg=THEME_BG, fg=THEME_FG, font=FONT_BODY).pack(pady=10)
tk.Label(meme_tab, text="🚧 Feature in development", bg=THEME_BG, fg="#ffaa00", font=("Arial", 12, "italic")).pack(pady=10)


app.mainloop()
