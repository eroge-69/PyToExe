import tkinter as tk
from tkinter import messagebox
import serial
import threading
import subprocess

# --- SERIAL CONFIG ---
try:
    ser = serial.Serial("COM4", 9600, timeout=1)
except Exception as e:
    ser = None
    print("Serial connection failed:", e)

def send_command(cmd: str):
    if ser and ser.is_open:
        ser.write((cmd + "\n").encode("utf-8"))
        log_output(f"> {cmd}")
    else:
        log_output("[ERROR] Serial not connected")

def log_output(msg: str):
    output_box.insert(tk.END, msg + "\n")
    output_box.see(tk.END)

# --- Reader thread ---
def serial_reader():
    if not ser:
        return
    while True:
        try:
            line = ser.readline().decode(errors="ignore").strip()
            if line:
                log_output(line)
        except Exception:
            break

# --- GUI ---
root = tk.Tk()
root.title("Remote CAN Flasher Utility (RCFU)")

canvas = tk.Canvas(root, width=600, height=400, bg="lightblue")
canvas.pack(fill="both", expand=True)

# --- Draw boxes ---
# EB box
eb_box = canvas.create_rectangle(460, 150, 560, 220, fill="darkgreen", outline="black", width=2)
eb_label = canvas.create_text(510, 185, text="EB", fill="lightgreen", font=("Arial", 14, "bold"))
eb_highlight = canvas.create_rectangle(455, 145, 565, 225, outline="lightgreen", width=4, state="hidden")

# Vector boxes
vec_top = canvas.create_rectangle(250, 60, 330, 110, fill="red", outline="black", width=2)
vec_top_inner = canvas.create_rectangle(260, 80, 320, 100, fill="white", outline="")
vec_top_label = canvas.create_text(290, 90, text="Vector", fill="black", font=("Arial", 10, "bold"))

vec_bottom = canvas.create_rectangle(250, 280, 330, 330, fill="red", outline="black", width=2)
vec_bottom_inner = canvas.create_rectangle(260, 300, 320, 320, fill="white", outline="")
vec_bottom_label = canvas.create_text(290, 310, text="Vector", fill="black", font=("Arial", 10, "bold"))

# ECU boxes
fba_box = canvas.create_rectangle(80, 60, 150, 110, fill="grey", outline="black", width=2)
fba_label = canvas.create_text(115, 85, text="FBA", fill="black", font=("Arial", 10, "bold"))

rwa_box = canvas.create_rectangle(80, 280, 150, 330, fill="grey", outline="black", width=2)
rwa_label = canvas.create_text(115, 305, text="RWA", fill="black", font=("Arial", 10, "bold"))

# RCFU box
rcfu_box = canvas.create_rectangle(250, 150, 330, 220, fill="orange", outline="black", width=2)
rcfu_label = canvas.create_text(290, 185, text="RCFU", fill="black", font=("Arial", 14, "bold"))

# --- State variables ---
fba_to_eb = False
rwa_to_eb = False
eb_power = False

# --- Connection lines (static) ---
canvas.create_line(150, 85, 250, 195, width=3, fill="red")  # FBA to RCFU 
canvas.create_line(150, 305, 250, 195, width=3, fill="blue")  # RWA to RCFU  

# --- Connection lines (dynamic) ---
fba_line = canvas.create_line(290, 110, 290, 150, width=3, fill="red")  # Vector top to EB
rwa_line = canvas.create_line(290, 220, 290, 280, width=3, fill="blue")  # Vector bottom to EB
eb_line = canvas.create_line(330, 185, 460, 185, width=3, state="hidden")  # RCFU to EB

# --- Functions ---
def update_ecu_states():
    """Update which ECU is clickable and draw red border if blocked."""
    if fba_to_eb and not rwa_to_eb:
        canvas.itemconfig(rwa_box, outline="red", width=4)
        canvas.tag_unbind(rwa_box, "<Button-1>")
        canvas.tag_unbind(rwa_label, "<Button-1>")
    elif rwa_to_eb and not fba_to_eb:
        canvas.itemconfig(fba_box, outline="red", width=4)
        canvas.tag_unbind(fba_box, "<Button-1>")
        canvas.tag_unbind(fba_label, "<Button-1>")
    else:
        canvas.itemconfig(fba_box, outline="black", width=2)
        canvas.itemconfig(rwa_box, outline="black", width=2)
        canvas.tag_bind(fba_box, "<Button-1>", toggle_fba)
        canvas.tag_bind(fba_label, "<Button-1>", toggle_fba)
        canvas.tag_bind(rwa_box, "<Button-1>", toggle_rwa)
        canvas.tag_bind(rwa_label, "<Button-1>", toggle_rwa)

def update_eb_highlight():
    """Show or hide the green border around EB box depending on power state."""
    if eb_power:
        canvas.itemconfigure(eb_highlight, state="normal")
    else:
        canvas.itemconfigure(eb_highlight, state="hidden")

def toggle_fba(event=None):
    global fba_to_eb
    if fba_to_eb:
        canvas.itemconfigure(fba_line, state="normal")
        canvas.itemconfigure(eb_line, state="hidden", fill="black")
        send_command("endfba")
        log_output("Sent command: endfba")
    else:
        if rwa_to_eb:
            return
        canvas.itemconfigure(fba_line, state="hidden")
        canvas.itemconfigure(eb_line, state="normal", fill="red")
        send_command("startfba")
        log_output("Sent command: startfba")
    fba_to_eb = not fba_to_eb
    update_ecu_states()

def toggle_rwa(event=None):
    global rwa_to_eb
    if rwa_to_eb:
        canvas.itemconfigure(rwa_line, state="normal")
        canvas.itemconfigure(eb_line, state="hidden", fill="black")
        send_command("endrwa")
        log_output("Sent command: endrwa")
    else:
        if fba_to_eb:
            return
        canvas.itemconfigure(rwa_line, state="hidden")
        canvas.itemconfigure(eb_line, state="normal", fill="blue")
        send_command("startrwa")
        log_output("Sent command: startrwa")
    rwa_to_eb = not rwa_to_eb
    update_ecu_states()

def toggle_power(event=None):
    global eb_power
    if eb_power:
        send_command("endeb")
        log_output("Sent command: endeb")
    else:
        send_command("starteb")
        log_output("Sent command: starteb")
    eb_power = not eb_power
    update_eb_highlight()

def reset_eb():
    send_command("reseteb")
    log_output("Sent command: reseteb")

def reset_self():
    send_command("resetself")
    log_output("Sent command: resetself")
    global eb_power
    eb_power = False
    update_eb_highlight()
    global fba_to_eb
    global rwa_to_eb
    fba_to_eb = False
    rwa_to_eb = False
    canvas.itemconfigure(fba_line, state="normal")
    canvas.itemconfigure(rwa_line, state="normal")
    canvas.itemconfigure(eb_line, state="hidden", fill="black")
    update_ecu_states()

def check_eb():
    """Open Windows Change adapter settings"""
    try:
        subprocess.Popen(["control", "ncpa.cpl"])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open settings:\n{e}")

# --- Bind clicks on ECU boxes (switches) ---
canvas.tag_bind(fba_box, "<Button-1>", toggle_fba)
canvas.tag_bind(fba_label, "<Button-1>", toggle_fba)
canvas.tag_bind(rwa_box, "<Button-1>", toggle_rwa)
canvas.tag_bind(rwa_label, "<Button-1>", toggle_rwa)
canvas.tag_bind(eb_box, "<Button-1>", toggle_power) 

# --- Buttons ---
btn_frame = tk.Frame(root)
btn_frame.pack(fill="x")
btn_frame.configure(bg="beige")

power_btn = tk.Button(btn_frame, background="lightgrey", text="Toggle EB Power", command=toggle_power)
power_btn.pack(side="left", padx=10, pady=5)


checkeb_btn = tk.Button(btn_frame, background="lightgrey", text="Check EB Connection", command=check_eb)
checkeb_btn.pack(side="left", padx=10, pady=5)

resetself_btn = tk.Button(btn_frame, background="red", text="Reset RCFU", command=reset_self)
resetself_btn.pack(side="right", padx=10, pady=5)

reseteb_btn = tk.Button(btn_frame, background="yellow", text="Reset EB", command=reset_eb)
reseteb_btn.pack(side="right", padx=10, pady=5)

# --- Output box at bottom ---
output_box = tk.Text(root, height=8, bg="lightgreen", fg="black", insertbackground="white", font=("Callibri", 10, "bold"))
output_box.pack(fill="x")

# --- Start serial reader thread ---
if ser:
    threading.Thread(target=serial_reader, daemon=True).start()

#reset RCFU on start
send_command("resetself")

root.mainloop()
