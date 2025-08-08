import webbrowser
import tkinter as tk
from tkinter import messagebox

# ---------------- PDF Links ----------------
pdf_links = {
    "0001": "https://drive.google.com/file/d/1KB6lrlBrYZBFhpIkJYH8Kjji5AY4F_G6/view?pli=1",
    "0002": "https://drive.google.com/file/d/1koXtmKXoz3PnGlvuXTx919auRiFF8uRk/view",
    "0003": "https://drive.google.com/file/d/1FtoZyuEMwpLn4x4q4WFnbVq3UDo0g_RA/view"
}

# ---------------- Open PDF Function ----------------
def open_pdf():
    code = entry.get().strip()
    if code in pdf_links:
        webbrowser.open(pdf_links[code])
    else:
        messagebox.showerror("Invalid Code", "❌ The entered code is incorrect!")

# ---------------- Main Window ----------------
root = tk.Tk()
root.title("Home Login")
root.geometry("400x250")
root.configure(bg="#f4f4f4")
root.resizable(False, False)

# Center the window on screen
window_width = 400
window_height = 250
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
pos_x = int((screen_width / 2) - (window_width / 2))
pos_y = int((screen_height / 2) - (window_height / 2))
root.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")

# ---------------- Title Label ----------------
title_label = tk.Label(root, text="📄 Home Login", font=("Arial", 18, "bold"), fg="#333", bg="#f4f4f4")
title_label.pack(pady=(25, 10))

# ---------------- Entry Label ----------------
label = tk.Label(root, text="Enter 4-digit code:", font=("Arial", 12), bg="#f4f4f4")
label.pack(pady=(5, 5))

# ---------------- Entry Box ----------------
entry = tk.Entry(root, font=("Arial", 16), justify="center", relief="solid", bd=1)
entry.pack(pady=5, ipady=5, ipadx=5)
entry.focus()

# ---------------- Button ----------------
btn = tk.Button(
    root,
    text="🔓 Open PDF",
    font=("Arial", 14, "bold"),
    bg="#4CAF50",
    fg="white",
    relief="flat",
    activebackground="#45a049",
    cursor="hand2",
    command=open_pdf
)
btn.pack(pady=20, ipadx=10, ipady=5)

# ---------------- Footer ----------------
footer = tk.Label(root, text="Powered by Home Login", font=("Arial", 9), bg="#f4f4f4", fg="#777")
footer.pack(side="bottom", pady=5)

root.mainloop()
