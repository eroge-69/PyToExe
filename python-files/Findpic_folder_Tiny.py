import os
import threading
from tkinter import Tk, Entry, Label, Listbox, END, Frame, Canvas
from PIL import Image, ImageTk

# Global variables
IMAGE_FOLDER = ""
all_files = []

# Extract top edge color
def get_top_edge_color(img):
    img = img.convert("RGB")
    width = img.width
    top_pixels = [img.getpixel((x, 0)) for x in range(width)]
    r = sum(p[0] for p in top_pixels) // width
    g = sum(p[1] for p in top_pixels) // width
    b = sum(p[2] for p in top_pixels) // width
    return "#%02x%02x%02x" % (r, g, b)

# Main window
root = Tk()
root.title("Image Search")
root.geometry("250x480+50+20")
root.resizable(False, False)
root.configure(bg="black")

# Folder path entry
folder_frame = Frame(root, bg="black")
folder_frame.pack(pady=(6, 5), padx=13, fill="x")

folder_label = Label(folder_frame, text="Image Folder:", font=("Arial", 12), fg="white", bg="black")
folder_label.pack(side="left")

folder_entry = Entry(folder_frame, font=("Arial", 12), fg="white", bg="black", insertbackground="white", width=25)
folder_entry.pack(side="left", padx=(5, 0), fill="x", expand=True)
folder_entry.focus_set()

# Listbox
listbox = Listbox(root, font=("Arial", 10), height=5, bg="black", fg="white", bd=0, highlightthickness=0, relief="flat")
listbox.pack(padx=15, ipadx=5, fill="x")

# Search box
search_entry = Entry(root, font=("Arial", 28, "bold"), width=11, bd=8, fg="white", bg="black", insertbackground="white", state="disabled")
search_entry.pack(padx=5, ipadx=5, pady=0, ipady=0)

# Main image frame
image_frame = Frame(root, bg="black", width=230, height=180)
image_frame.pack(pady=5)
image_frame.pack_propagate(False)

image_label = Label(image_frame, bg="black")
image_label.place(relx=0.5, rely=0.5, anchor="center")

# Thumbnail canvas
thumb_canvas = Canvas(root, bg="black", height=93, highlightthickness=0)
thumb_canvas.pack(fill="x", pady=5)

thumb_scroll_frame = Frame(thumb_canvas, bg="black")
thumb_window = thumb_canvas.create_window((0, 0), window=thumb_scroll_frame, anchor="nw")

def start_drag(event):
    thumb_canvas.scan_mark(event.x, event.y)

def drag(event):
    thumb_canvas.scan_dragto(event.x, event.y, gain=1)

thumb_canvas.bind("<ButtonPress-1>", start_drag)
thumb_canvas.bind("<B1-Motion>", drag)

def update_scroll_region(event=None):
    thumb_canvas.configure(scrollregion=thumb_canvas.bbox("all"))

thumb_scroll_frame.bind("<Configure>", update_scroll_region)

# Show image
def show_image(filename):
    if not IMAGE_FOLDER:
        return

    path = os.path.join(IMAGE_FOLDER, filename + ".jpg")
    if not os.path.exists(path):
        image_label.config(image='', text="Image not found", bg="black")
        image_frame.config(bg="black")
        return

    try:
        img = Image.open(path)
        edge_color = get_top_edge_color(img)
        image_label.config(bg=edge_color)
        image_frame.config(bg=edge_color)

        box_w, box_h = 230, 180
        min_w, min_h = int(box_w * 0.80), int(box_h * 0.80)

        img.thumbnail((box_w, box_h), Image.LANCZOS)

        if img.width < min_w and img.height < min_h:
            scale = min(min_w / img.width, min_h / img.height)
            new_w = min(int(img.width * scale), box_w)
            new_h = min(int(img.height * scale), box_h)
            img = img.resize((new_w, new_h), Image.LANCZOS)

        photo = ImageTk.PhotoImage(img)
        image_label.config(image=photo, text="")
        image_label.image = photo
    except:
        image_label.config(text="Error loading image", image='', bg="black")
        image_frame.config(bg="black")

# Promote thumbnail
def promote_image(name, matches):
    show_image(name)
    update_thumbnails(name, matches)

# Update thumbnails
def update_thumbnails(current_main, matches):
    for widget in thumb_scroll_frame.winfo_children():
        widget.destroy()

    thumb_scroll_frame.update_idletasks()
    thumb_scroll_frame.config(width=thumb_canvas.winfo_width())
    thumb_scroll_frame.pack_configure(padx=(5, 0))

    if current_main in matches:
        start = matches.index(current_main) + 1
    else:
        start = 0

    thumbs = matches[start:start + 30]
    canvas_w = thumb_canvas.winfo_width() or 320
    row = Frame(thumb_scroll_frame, bg="black", height=30)
    row.pack(anchor="w")
    row_w = 0

    def create_thumb(i):
        nonlocal row, row_w
        if i >= len(thumbs): return

        name = thumbs[i]
        path = os.path.join(IMAGE_FOLDER, name + ".jpg")
        if not os.path.exists(path):
            root.after(10, lambda: create_thumb(i + 1))
            return

        try:
            img = Image.open(path)
            img.thumbnail((100, 25), Image.LANCZOS)
            edge = get_top_edge_color(img)
            photo = ImageTk.PhotoImage(img)
            w = photo.width()

            if row_w + w + 4 > canvas_w:
                row = Frame(thumb_scroll_frame, bg="black", height=30)
                row.pack(anchor="w")
                row_w = 0

            container = Frame(row, bg=edge, width=w, height=30)
            container.pack_propagate(False)
            container.pack(side="left", padx=2, pady=1)

            label = Label(container, image=photo, bg=edge)
            label.image = photo
            label.place(relx=0.5, rely=0.5, anchor="center")
            label.bind("<Button-1>", lambda e, n=name: promote_image(n, matches))

            row_w += w + 4
        except:
            pass

        root.after(10, lambda: create_thumb(i + 1))

    create_thumb(0)

# Update results
def update_results():
    typed = search_entry.get().strip()
    listbox.delete(0, END)

    if not typed:
        show_image("AAA")
        update_thumbnails("AAA", [])
        return

    matches = [f for f in all_files if typed.lower() in f.lower()]
    for m in matches:
        listbox.insert(END, m)

    if matches:
        show_image(matches[0])
        update_thumbnails(matches[0], matches)
    else:
        show_image("AAA")
        update_thumbnails("AAA", [])

# Delayed search
search_timer = None
def on_key_release(event):
    global search_timer
    typed = search_entry.get().strip()

    if event.keysym in ["Up", "Down", "Left", "Right", "Shift_L", "Shift_R", "Control_L", "Control_R"]:
        return

    if search_timer:
        search_timer.cancel()

    if len(typed) >= 3:
        update_results()
    else:
        search_timer = threading.Timer(0.7, update_results)
        search_timer.start()

search_entry.bind("<KeyRelease>", on_key_release)

# Listbox select
def on_listbox_select(event):
    sel = listbox.curselection()
    if sel:
        name = listbox.get(sel[0])
        show_image(name)
        update_thumbnails(name, listbox.get(0, END))

listbox.bind("<<ListboxSelect>>", on_listbox_select)

# Load folder path
def load_image_folder(event=None):
    global IMAGE_FOLDER, all_files
    path = folder_entry.get().strip()

    if not os.path.isdir(path):
        listbox.delete(0, END)
        listbox.insert(END, "Invalid folder path")
        show_image("AAA")
        update_thumbnails("AAA", [])
        return

    IMAGE_FOLDER = path
    all_files = [f[:-4] for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(".jpg")]

    search_entry.config(state="normal")
    update_results()
    search_entry.focus_set()  # Moves the cursor to the search box

folder_entry.bind("<Return>", load_image_folder)

# Start app
root.mainloop()
