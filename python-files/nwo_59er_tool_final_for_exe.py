
import tkinter as tk
import threading
import random
import string
import time

def generate_random_line(length=80):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))

def start_generation(text_widget):
    start_time = time.time()
    found_trigger = random.randint(30, 150)
    line_count = 0

    while time.time() - start_time < 10:
        line = generate_random_line()
        text_widget.insert(tk.END, line + '\n')
        text_widget.see(tk.END)
        time.sleep(0.05)
        line_count += 1
        if line_count == found_trigger:
            text_widget.insert(tk.END, "[✓] MATCH FOUND at 192.168.{}.{}\n".format(random.randint(0, 255), random.randint(0, 255)))
            text_widget.see(tk.END)

    text_widget.insert(tk.END, '\n' * 15)

    nwo_text = """
███╗   ██╗██╗    ██╗ ██████╗ 
████╗  ██║██║    ██║██╔═══██╗
██╔██╗ ██║██║ █╗ ██║██║   ██║
██║╚██╗██║██║███╗██║██║   ██║
██║ ╚████║╚███╔███╔╝╚██████╔╝
╚═╝  ╚═══╝ ╚══╝╚══╝  ╚═════╝ 
          𝟱𝟵𝙴𝚁 𝚃𝙾𝙾𝙻 𝙰𝙲𝚃𝙸𝚅𝙰𝚃𝙴𝙳
"""
    text_widget.insert(tk.END, nwo_text)
    text_widget.see(tk.END)

def on_enter(event=None):
    input_frame.pack_forget()
    thread = threading.Thread(target=start_generation, args=(text,), daemon=True)
    thread.start()

def start_gui():
    global input_frame, text

    window = tk.Tk()
    window.title("🆂🅲🆁🅸🅿🆃🆂")
    window.configure(bg="black")
    window.geometry("900x600")

    text = tk.Text(window, bg="black", fg="lime", font=("Courier", 10), wrap=tk.NONE)
    text.pack(fill=tk.BOTH, expand=True)

    input_frame = tk.Frame(window, bg="black")
    input_label = tk.Label(input_frame, text="ENTER CODE:", fg="lime", bg="black", font=("Courier", 12))
    input_label.pack(side=tk.LEFT, padx=10)
    input_entry = tk.Entry(input_frame, bg="black", fg="lime", insertbackground="lime", font=("Courier", 12))
    input_entry.pack(side=tk.LEFT)
    input_entry.bind("<Return>", on_enter)
    input_frame.pack(pady=20)

    input_entry.focus()
    window.mainloop()

start_gui()
