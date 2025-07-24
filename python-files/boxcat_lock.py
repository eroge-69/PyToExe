import tkinter as tk

PASSWORD = "boxcat"
fail_count = 0

def on_enter(event=None):
    global fail_count
    if entry.get().lower() == PASSWORD:
        root.destroy()
    else:
        fail_count += 1
        if fail_count >= 100:
            msg_label.config(text=f"The password is: {PASSWORD}", fg='red')

root = tk.Tk()
root.attributes('-fullscreen', True)
root.configure(bg='black')
root.bind("<Escape>", lambda e: None)
root.bind("<Alt-F4>", lambda e: None)

entry = tk.Entry(root, show='*', fg='black', bg='black', bd=0, insertbackground='black')
entry.place(x=-100, y=-100)
entry.focus()
entry.bind("<Return>", on_enter)

msg_label = tk.Label(root, text="", font=('Consolas', 24), bg='black', fg='black')
msg_label.pack(pady=50)

root.mainloop()
