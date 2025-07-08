import tkinter as tk
from tkinter import filedialog, font, colorchooser, messagebox
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence
import tempfile
import os

# Optional PDF export
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.pagesizes import letter

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt")
    if file_path:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(text_area.get(1.0, tk.END))

def print_file():
    content = text_area.get("1.0", "end-1c")
    if not content.strip():
        return
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        if os.name == "nt":
            os.startfile(tmp_path, "print")
        elif os.name == "posix":
            os.system(f"lpr '{tmp_path}'")
    except Exception as e:
        print(f"Print failed: {e}")

def export_to_pdf():
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if file_path:
        try:
            text = text_area.get("1.0", tk.END).strip().split("\n")
            c = pdf_canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            y = height - 40
            for line in text:
                if y < 40:
                    c.showPage()
                    y = height - 40
                c.drawString(40, y, line)
                y -= 14
            c.save()
            messagebox.showinfo("PDF Export", "PDF saved successfully.")
        except Exception as e:
            messagebox.showerror("PDF Export Failed", str(e))

def change_font_family(event=None):
    selected_font = font_family_var.get()
    current_font = font.Font(family=selected_font, size=font_size_var.get())
    text_area.configure(font=current_font)

def change_font_size(event=None):
    selected_size = int(font_size_var.get())
    current_font = font.Font(family=font_family_var.get(), size=selected_size)
    text_area.configure(font=current_font)

def insert_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
    if file_path:
        size_window = tk.Toplevel(root)
        size_window.title("Resize Image")

        tk.Label(size_window, text="Width:").grid(row=0, column=0)
        tk.Label(size_window, text="Height:").grid(row=1, column=0)

        width_entry = tk.Entry(size_window)
        height_entry = tk.Entry(size_window)
        width_entry.grid(row=0, column=1)
        height_entry.grid(row=1, column=1)

        width_entry.insert(0, "200")
        height_entry.insert(0, "200")

        def apply_size():
            try:
                width = int(width_entry.get())
                height = int(height_entry.get())
                size_window.destroy()

                img = Image.open(file_path).resize((width, height))
                tk_img = ImageTk.PhotoImage(img)
                text_area.image_create(tk.INSERT, image=tk_img)

                if not hasattr(text_area, 'image_refs'):
                    text_area.image_refs = []
                text_area.image_refs.append(tk_img)
            except ValueError:
                size_window.destroy()
                print("Invalid width or height.")

        tk.Button(size_window, text="Insert", command=apply_size).grid(row=2, column=0, columnspan=2)

def insert_moving_gif():
    file_path = filedialog.askopenfilename(filetypes=[("GIF files", "*.gif")])
    if file_path:
        gif_window = tk.Toplevel(root)
        gif_window.title("Animated GIF")

        lbl = tk.Label(gif_window)
        lbl.pack()

        gif = Image.open(file_path)
        frames = [ImageTk.PhotoImage(frame.copy().resize((200, 200))) for frame in ImageSequence.Iterator(gif)]

        def animate(counter=0):
            lbl.configure(image=frames[counter])
            gif_window.after(100, animate, (counter + 1) % len(frames))

        animate()

def change_text_color():
    color = colorchooser.askcolor(title="Choose Text Color")[1]
    if color:
        text_area.configure(fg=color)

def change_bg_color():
    color = colorchooser.askcolor(title="Choose Background Color")[1]
    if color:
        text_area.configure(bg=color)

def update_counters(event=None):
    text = text_area.get("1.0", "end-1c")
    word_count = len(text.strip().split())
    char_count = len(text)
    char_count_no_space = len(text.replace(" ", "").replace("\n", ""))
    counter_var.set(f"Words: {word_count} | Characters: {char_count} ({char_count_no_space} w/o spaces)")
    text_area.edit_modified(False)

# ==== GUI ====
root = tk.Tk()
root.title("Mini Word")
root.geometry("800x500")

font_family_var = tk.StringVar(value="Arial")
font_size_var = tk.IntVar(value=14)

top_frame = tk.Frame(root)
top_frame.pack(side="top", fill="x")

ttk.Label(top_frame, text="Font:").pack(side="left")
font_family_combo = ttk.Combobox(top_frame, textvariable=font_family_var, values=[
    "Arial", "Courier New", "Comic Sans MS", "Times New Roman", "Consolas", "Lucida Console", "Verdana"
], state="readonly")
font_family_combo.pack(side="left", padx=5)
font_family_combo.bind("<<ComboboxSelected>>", change_font_family)

ttk.Label(top_frame, text="Size:").pack(side="left")
font_size_combo = ttk.Combobox(top_frame, textvariable=font_size_var, values=list(range(8, 41)), state="readonly")
font_size_combo.pack(side="left", padx=5)
font_size_combo.bind("<<ComboboxSelected>>", change_font_size)

text_area = tk.Text(root, wrap="word", font=("Arial", 14), undo=True)
text_area.pack(expand=True, fill="both")
text_area.image_refs = []

text_area.bind("<Control-z>", lambda event: text_area.edit_undo())
text_area.bind("<Control-y>", lambda event: text_area.edit_redo())

counter_var = tk.StringVar(value="Words: 0 | Characters: 0 (0 w/o spaces)")
counter_label = ttk.Label(root, textvariable=counter_var, anchor="e", padding=5)
counter_label.pack(side="bottom", fill="x")

text_area.bind("<<Modified>>", update_counters)

# ==== Menus ====
menu = tk.Menu(root)
root.config(menu=menu)

file_menu = tk.Menu(menu, tearoff=False)
menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_command(label="Print", command=print_file)
file_menu.add_command(label="Export to PDF", command=export_to_pdf)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

insert_menu = tk.Menu(menu, tearoff=False)
menu.add_cascade(label="Insert", menu=insert_menu)
insert_menu.add_command(label="Insert Image", command=insert_image)
insert_menu.add_command(label="Insert Moving GIF", command=insert_moving_gif)

color_menu = tk.Menu(menu, tearoff=False)
menu.add_cascade(label="Colors", menu=color_menu)
color_menu.add_command(label="Change Text Color", command=change_text_color)
color_menu.add_command(label="Change Background Color", command=change_bg_color)

update_counters()
root.mainloop()
