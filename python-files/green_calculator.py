import tkinter as tk

def on_click(event):
    text = event.widget.cget("text")
    if text == "=":
        try:
            result = str(eval(str(entry_var.get())))
            entry_var.set(result)
        except Exception:
            entry_var.set("Error")
    elif text == "C":
        entry_var.set("")
    else:
        entry_var.set(entry_var.get() + text)

root = tk.Tk()
root.title("Green Calculator")
root.configure(bg="#1d2f1d")
root.geometry("320x420")
root.resizable(False, False)

entry_var = tk.StringVar()
entry = tk.Entry(root, textvariable=entry_var, font="Arial 20", bd=10, relief=tk.RIDGE, bg="#ccffcc", fg="black")
entry.pack(fill=tk.BOTH, ipadx=8, ipady=15, pady=10, padx=10)

btns_frame = tk.Frame(root, bg="#1d2f1d")
btns_frame.pack()

buttons = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["C", "0", "=", "+"],
]

for row in buttons:
    row_frame = tk.Frame(btns_frame, bg="#1d2f1d")
    row_frame.pack(fill=tk.BOTH, expand=True)
    for char in row:
        btn = tk.Button(row_frame, text=char, font="Arial 18", relief=tk.RAISED, bd=4, width=5, height=2,
                        bg="#66cc66", fg="black")
        btn.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5)
        btn.bind("<Button-1>", on_click)

root.mainloop()
