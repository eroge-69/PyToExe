import tkinter as tk
from tkinter import messagebox, simpledialog
import socket
import json
import os
CONFIG_FILE = "config.json"
def generate_dpl(text):
    return "^XA\n^FO115,40\n^A0N,100,140\n^FD{}^FS\n^XZ\n".format(text)
def generate_dpl_numbered(text):
    return "^XA\n^FO80,45\n^A0N,75,50\n^FD{}^FS\n^XZ\n".format(text)
def send_to_network_printer(ip, port, texts, numbered=False):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(10)
            sock.connect((ip, port))
            for text in texts:
                dpl = generate_dpl_numbered(text) if numbered else generate_dpl(text)
                sock.sendall(dpl.encode('utf-8'))
        return True
    except Exception as e:
        messagebox.showerror("Tisková chyba", f"Chyba při tisku na {ip}:{port}\n{e}")
        return False
def save_printer_ip(ip):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"ip": ip, "port": 9100}, f)
def load_printer_ip():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return data.get("ip", ""), data.get("port", 9100)
    return "", 9100
def change_printer_ip():
    current_ip, _ = load_printer_ip()
    new_ip = simpledialog.askstring("Zadej IP tiskárny", "IP adresa tiskárny:", initialvalue=current_ip or "")
    if new_ip:
        save_printer_ip(new_ip)
BG_COLOR = "#FF9F09"
FG_COLOR = "#B30000"
BUTTON_BG = FG_COLOR
BUTTON_FG = "white"
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_LABEL = ("Segoe UI", 14, "bold")
FONT_BUTTON = ("Segoe UI", 13, "bold")
FONT_RADIO = ("Segoe UI", 12)
root = tk.Tk()
root.title("Tisk štítků – síťová tiskárna")
root.geometry("700x700")
root.minsize(600, 600)
canvas = tk.Canvas(root, bg=BG_COLOR, highlightthickness=0)
canvas.pack(fill="both", expand=True)
FRAME_WIDTH = 500
FRAME_HEIGHT = 500
frame_main = tk.Frame(canvas, bg=BG_COLOR, width=FRAME_WIDTH, height=FRAME_HEIGHT)
frame_fixed = tk.Frame(canvas, bg=BG_COLOR, width=FRAME_WIDTH, height=FRAME_HEIGHT)
frame_numbered = tk.Frame(canvas, bg=BG_COLOR, width=FRAME_WIDTH, height=FRAME_HEIGHT)
frame_window_main = canvas.create_window(0, 0, window=frame_main, anchor="center", width=FRAME_WIDTH, height=FRAME_HEIGHT)
frame_window_fixed = canvas.create_window(0, 0, window=frame_fixed, anchor="center", width=FRAME_WIDTH, height=FRAME_HEIGHT)
frame_window_numbered = canvas.create_window(0, 0, window=frame_numbered, anchor="center", width=FRAME_WIDTH, height=FRAME_HEIGHT)
btn_back = tk.Button(root, text="← Zpět", bg=BUTTON_BG, fg=BUTTON_FG, font=FONT_BUTTON, command=lambda: show_frame(frame_main))
def update_canvas_position(event):
    center_x = event.width // 2
    center_y = event.height // 2
    canvas.coords(frame_window_main, center_x, center_y)
    canvas.coords(frame_window_fixed, center_x, center_y)
    canvas.coords(frame_window_numbered, center_x, center_y)
canvas.bind("<Configure>", update_canvas_position)
def show_frame(frame):
    for f, window_id in [(frame_main, frame_window_main), (frame_fixed, frame_window_fixed), (frame_numbered, frame_window_numbered)]:
        canvas.itemconfigure(window_id, state="hidden")
    if frame == frame_main:
        canvas.itemconfigure(frame_window_main, state="normal")
        btn_back.place_forget()
    elif frame == frame_fixed:
        canvas.itemconfigure(frame_window_fixed, state="normal")
        btn_back.place(x=10, y=10)
    elif frame == frame_numbered:
        canvas.itemconfigure(frame_window_numbered, state="normal")
        btn_back.place(x=10, y=10)
tk.Label(frame_main, text="Tisk štítků – hlavní menu", font=FONT_TITLE, bg=BG_COLOR, fg=FG_COLOR).pack(pady=20)
tk.Button(frame_main, text="Nastavit IP tiskárny", command=change_printer_ip, bg=BUTTON_BG, fg=BUTTON_FG, font=FONT_BUTTON, width=30).pack(pady=10)
tk.Button(frame_main, text="Tisk z přednastavených možností", command=lambda: show_frame(frame_fixed), bg=BUTTON_BG, fg=BUTTON_FG, font=FONT_BUTTON, width=30).pack(pady=10)
tk.Button(frame_main, text="Tisk s číslováním (např. 2025.1)", command=lambda: show_frame(frame_numbered), bg=BUTTON_BG, fg=BUTTON_FG, font=FONT_BUTTON, width=30).pack(pady=10)
tk.Label(frame_fixed, text="Vyber typ štítku:", bg=BG_COLOR, fg=FG_COLOR, font=FONT_LABEL).pack(pady=20)
choice = tk.StringVar(value="FRI")
radio_frame = tk.Frame(frame_fixed, bg=BG_COLOR)
radio_frame.pack(pady=5)
def update_radio_style():
    for rb, val in zip(radio_buttons, ["FRI", "IMP", "KAT"]):
        if choice.get() == val:
            rb.config(bg=FG_COLOR, fg=BUTTON_FG, selectcolor=FG_COLOR)
        else:
            rb.config(bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR)
radio_buttons = []
for val in ["FRI", "IMP", "KAT"]:
    rb = tk.Radiobutton(radio_frame, text=val, variable=choice, value=val, bg=BG_COLOR, fg=FG_COLOR,
                        selectcolor=BG_COLOR, font=FONT_RADIO, indicatoron=0, width=8, command=update_radio_style)
    rb.pack(side="left", padx=5)
    radio_buttons.append(rb)
update_radio_style()
tk.Label(frame_fixed, text="Počet kusů (1–100):", bg=BG_COLOR, fg=FG_COLOR, font=FONT_LABEL).pack(pady=15)
entry_count_fixed = tk.Entry(frame_fixed, font=FONT_RADIO, justify="center")
entry_count_fixed.pack()
def print_labels():
    try:
        count = int(entry_count_fixed.get())
        if not (1 <= count <= 100):
            raise ValueError
    except ValueError:
        messagebox.showerror("Chyba", "Počet musí být číslo od 1 do 100.")
        return
    ip, port = load_printer_ip()
    if not ip:
        messagebox.showwarning("Tiskárna", "Nejdřív nastav IP tiskárny.")
        return
    text_to_print = choice.get()
    if text_to_print.strip() == "":
        messagebox.showerror("Chyba", "Text pro tisk nemůže být prázdný!")
        return
    send_to_network_printer(ip, port, [text_to_print] * count)
    messagebox.showinfo("Hotovo", f"Vytištěno {count}x: {text_to_print}")
tk.Button(frame_fixed, text="Tisknout", command=print_labels, bg=BUTTON_BG, fg=BUTTON_FG, font=FONT_BUTTON).pack(pady=20)
tk.Label(frame_numbered, text="Zadej základní číslo (max 8 znaků):", bg=BG_COLOR, fg=FG_COLOR, font=FONT_LABEL).pack(pady=20)
entry_base_numbered = tk.Entry(frame_numbered, font=FONT_RADIO, justify="center")
entry_base_numbered.pack()
tk.Label(frame_numbered, text="Počet štítků (1–100):", bg=BG_COLOR, fg=FG_COLOR, font=FONT_LABEL).pack(pady=20)
entry_count_numbered = tk.Entry(frame_numbered, font=FONT_RADIO, justify="center")
entry_count_numbered.pack()
def print_numbered():
    try:
        base = entry_base_numbered.get().strip()
        if len(base) > 8:
            raise ValueError("Základ může mít maximálně 8 znaků.")
        if not base.isdigit():
            raise ValueError("Základ musí být číslo.")
        count = int(entry_count_numbered.get())
        if not (1 <= count <= 100):
            raise ValueError("Počet mimo rozsah.")
    except ValueError as ve:
        messagebox.showerror("Chyba", str(ve))
        return
    ip, port = load_printer_ip()
    if not ip:
        messagebox.showwarning("Tiskárna", "Nejdřív nastav IP tiskárny.")
        return
    texts = [f"{base}.{i+1}" for i in range(count)]
    send_to_network_printer(ip, port, texts, numbered=True)
    messagebox.showinfo("Hotovo", f"Vytištěno {count} štítků ve formátu {base}.x")
tk.Button(frame_numbered, text="Tisknout", command=print_numbered, bg=BUTTON_BG, fg=BUTTON_FG, font=FONT_BUTTON).pack(pady=20)
show_frame(frame_main)
root.mainloop()
