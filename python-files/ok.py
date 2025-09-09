from tkinter import *
from tkinter import filedialog, messagebox, Menu
from PIL import Image, ImageTk, ImageSequence
import os

file = None
chunk = 1024
frames = []

def size_format(s):
    for u in ["bytes", "KB", "MB", "GB"]:
        if s < 1024:
            return f"{s:.2f} {u}"
        s /= 1024
    return f"{s:.2f} TB"

def name_short(n, l=15):
    if len(n) <= l:
        return n
    base, ext = os.path.splitext(n)
    return base[:12] + "..." + ext

def status_update(destruction_status=""):
    if file:
        s = os.path.getsize(file)
        n = os.path.basename(file)
        name_label.config(text=f"File Name: {name_short(n)}")
        size_label.config(text=f"File Size: {size_format(s)}")
    else:
        name_label.config(text="File Name: No file selected")
        size_label.config(text="File Size: 0")
    
    # Fixed file status label below file info
    if destruction_status:
        status_label.config(text=f"File Status: {destruction_status}")
    else:
        status_label.config(text="File Status: Not Wiped")

def show_hex(data):
    text.delete("1.0", END)
    text.insert(END, " ".join(f"{b:02X}" for b in data))

def open_file():
    global file
    path = filedialog.askopenfilename(title="Select File")
    if not path:
        return
    file = path
    # Show first chunk in hex when opening
    with open(path, "rb") as f:
        data = f.read(chunk)
    show_hex(data)
    status_update()

def save_edit():
    if not file:
        return
    confirm = messagebox.askyesno("Confirm User Wiping",
                                  "Are you sure you want to perform User Wiping?\nThis will modify part of the file.")
    if not confirm:
        return
    try:
        hex_data = text.get("1.0", END).strip().split()
        new_bytes = bytes(int(x, 16) for x in hex_data)
        with open(file, "r+b") as f:
            f.seek(0)
            f.write(new_bytes)

        # Flash top panel yellow to indicate User Wiping
        top_panel.config(bg="yellow")
        root.update()
        root.after(500, lambda: top_panel.config(bg="black"))

        # Hex view clear பண்ணாமல் வைக்கவும்
        # text.delete("1.0", END)

        status_update(destruction_status="User Wiping Done")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def collapse_all():
    if not file:
        return
    confirm = messagebox.askyesno("Confirm Total Wiping",
                                  "WARNING: Total Wiping will destroy all file data!\nThis cannot be undone.\nDo you want to continue?")
    if not confirm:
        return
    try:
        s = os.path.getsize(file)
        with open(file, "r+b") as f:
            f.seek(0)
            f.write(b'\x00' * s)
            f.truncate(s)
        
        # **Red flash removed**

        # Clear hex view after total wipe
        text.delete("1.0", END)

        # Status update
        status_update(destruction_status="Completely Destroyed")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def load_gif(path, size=(180, 180)):
    try:
        g = Image.open(path)
        return [ImageTk.PhotoImage(f.copy().resize(size)) for f in ImageSequence.Iterator(g)]
    except:
        return []

def animate(ind=0):
    if frames:
        gif_label.config(image=frames[ind])
        gif_label.image = frames[ind]
        ind = (ind + 1) % len(frames)
        root.after(100, animate, ind)

root = Tk()
root.title("Binary Collapse Tool")
root.geometry("1200x700")

menu = Menu(root, font=("Helvetica", 10, "bold"))
root.config(menu=menu)
fmenu = Menu(menu, tearoff=0, font=("Helvetica", 10))
menu.add_cascade(label="File", menu=fmenu)
fmenu.add_command(label="Open", command=open_file)
fmenu.add_command(label="User Wiping", command=save_edit)
fmenu.add_command(label="Total Wiping", command=collapse_all)
fmenu.add_separator()
fmenu.add_command(label="Exit", command=root.quit)

# Top Panel
top_height = 150
top_width = 1200
top_panel = Frame(root, bg="black", width=top_width, height=top_height)
top_panel.pack_propagate(False)
top_panel.pack(side=TOP, fill=X)

gif_label = Label(top_panel, bg="black")
gif_label.place(x=-20, y=-30)

frames = load_gif("Hackathon/Event.gif")
animate()

name_label = Label(top_panel, text="File Name: No file selected", font=("Courier", 5, "bold"), bg="black", fg="white")
name_label.place(x=150, y=10)

size_label = Label(top_panel, text="File Size: 0", font=("Courier", 5, "bold"), bg="black", fg="white")
size_label.place(x=150, y=35)

# Status label below file info (fixed)
status_label = Label(top_panel, text="File Status: Not Wiped", font=("Courier", 5, "bold"), bg="black", fg="white")
status_label.place(x=150, y=85)

# Main frame for hex view
main = Frame(root)
main.pack(expand=True, fill="both")

tframe = Frame(main)
tframe.pack(expand=True, fill="both", padx=5, pady=5)

scroll = Scrollbar(tframe)
scroll.pack(side=RIGHT, fill=Y)

text = Text(tframe, wrap=WORD, font=("Courier", 11), bg="lightgreen", fg="black", yscrollcommand=scroll.set)
text.pack(expand=True, fill="both")
scroll.config(command=text.yview)

status_update()
root.mainloop()