import tkinter as tk
from tkinter import messagebox

def encode_msg(msg):
    n = 1
    encoded_msg = ""
    for l in msg:
        if l != " ":
            if n == 1:
                encoded_msg += chr(ord(l) + 5)
                n = 0
            else:
                encoded_msg += l
                n = 1
        else:
            encoded_msg += l
    return encoded_msg

def decode_msg(msg):
    n = 1
    decoded_msg = ""
    for l in msg:
        if l != " ":
            if n == 1:
                decoded_msg += chr(ord(l) - 5)
                n = 0
            else:
                decoded_msg += l
                n = 1
        else:
            decoded_msg += l
    return decoded_msg

def handle_encode():
    msg = input_text.get("1.0", tk.END).strip()
    if not msg:
        messagebox.showwarning("שגיאה", "הכנס הודעה")
        return
    result = encode_msg(msg)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, result)

def handle_decode():
    msg = input_text.get("1.0", tk.END).strip()
    if not msg:
        messagebox.showwarning("שגיאה", "הכנס הודעה")
        return
    result = decode_msg(msg)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, result)

# יצירת חלון
root = tk.Tk()
root.title("מוצפן-קל")

# ממשק
tk.Label(root, text="הודעה:", font=("Arial", 14)).pack()
input_text = tk.Text(root, height=5, width=50)
input_text.pack(pady=5)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

tk.Button(btn_frame, text="🔐 הצפן", command=handle_encode, width=15).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="🔓 פענח", command=handle_decode, width=15).pack(side=tk.RIGHT, padx=5)

tk.Label(root, text="תוצאה:", font=("Arial", 14)).pack()
output_text = tk.Text(root, height=5, width=50)
output_text.pack(pady=5)

# הפעלת חלון
root.mainloop()
