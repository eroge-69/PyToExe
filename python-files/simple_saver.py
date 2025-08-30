import tkinter as tk

def save_data():
    text = entry.get()
    with open("saved_data.txt", "a") as file:
        file.write(text + "\n")
    entry.delete(0, tk.END)

root = tk.Tk()
root.title("Simple Data Saver")
root.geometry("300x150")

tk.Label(root, text="Enter some data:").pack(pady=5)
entry = tk.Entry(root, width=30)
entry.pack(pady=5)

tk.Button(root, text="Save", command=save_data).pack(pady=5)

root.mainloop()
