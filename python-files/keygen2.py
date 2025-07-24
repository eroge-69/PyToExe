import tkinter as tk
from tkinter import messagebox
import random
import string

def generate_key(section_len, section_count, char_type):
    charset = ''
    if char_type == 'Digits':
        charset = string.digits
    elif char_type == 'Letters':
        charset = string.ascii_uppercase
    else:
        charset = string.ascii_uppercase + string.digits

    sections = []
    for _ in range(section_count):
        section = ''.join(random.choice(charset) for _ in range(section_len))
        sections.append(section)
    return '-'.join(sections)

def on_generate():
    try:
        sec_len = int(entry_section_len.get())
        sec_count = int(entry_section_count.get())
        char_type = char_var.get()
        key = generate_key(sec_len, sec_count, char_type)
        text_output.delete("1.0", tk.END)
        text_output.insert(tk.END, key)
    except ValueError:
        messagebox.showerror("Error", "Section length and count must be numbers.")

def on_modify():
    old = entry_old.get().strip()
    new = entry_new.get().strip()
    text = text_output.get("1.0", tk.END)
    modified = text.replace(old, new)
    text_output.delete("1.0", tk.END)
    text_output.insert(tk.END, modified)

# === Główne okno ===
root = tk.Tk()
root.title("KeyGen - Ceezz Freak Edition")
root.geometry("600x500")

# === Kanwa z poruszającym się tłem ===
canvas = tk.Canvas(root, width=600, height=500, bg="black", highlightthickness=0)
canvas.place(x=0, y=0)

moving_texts = []
for _ in range(30):
    x = random.randint(0, 600)
    y = random.randint(0, 500)
    t = canvas.create_text(x, y, text="H4HA H4ck5", fill="#08ff00", font=("Consolas", 12, "bold"))
    moving_texts.append(t)

def animate():
    for text in moving_texts:
        canvas.move(text, random.randint(-2, 2), random.randint(-1, 1))
        pos = canvas.coords(text)
        # Reset jeśli wyjdzie poza ekran
        if pos[0] < 0 or pos[0] > 600 or pos[1] < 0 or pos[1] > 500:
            canvas.coords(text, random.randint(0, 600), random.randint(0, 500))
    root.after(50, animate)

animate()

# === UI — wszystko nad Canvas ===
frame = tk.Frame(root, bg="#000000", highlightbackground="lime", highlightthickness=2)
frame.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(frame, text="Characters per section:", fg="lime", bg="black").pack()
entry_section_len = tk.Entry(frame, bg="black", fg="lime", insertbackground="lime")
entry_section_len.pack()

tk.Label(frame, text="Number of sections:", fg="lime", bg="black").pack()
entry_section_count = tk.Entry(frame, bg="black", fg="lime", insertbackground="lime")
entry_section_count.pack()

tk.Label(frame, text="Character type:", fg="lime", bg="black").pack()
char_var = tk.StringVar(value="Both")
tk.OptionMenu(frame, char_var, "Digits", "Letters", "Both").pack()

tk.Button(frame, text="Generate Key", command=on_generate, bg="black", fg="lime").pack(pady=5)

text_output = tk.Text(frame, height=3, width=30, bg="black", fg="lime", insertbackground="lime")
text_output.pack()

tk.Label(frame, text="Find:", fg="lime", bg="black").pack()
entry_old = tk.Entry(frame, bg="black", fg="lime", insertbackground="lime")
entry_old.pack()

tk.Label(frame, text="Replace with:", fg="lime", bg="black").pack()
entry_new = tk.Entry(frame, bg="black", fg="lime", insertbackground="lime")
entry_new.pack()

tk.Button(frame, text="Modify Key", command=on_modify, bg="black", fg="lime").pack(pady=5)

root.mainloop()
