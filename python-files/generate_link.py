import tkinter as tk
from tkinter import messagebox

def generate_download_link():
    file_id = entry.get().strip()
    if file_id:
        link = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key=AIzaSyDRMNsj2aQ6Xn8I48jB38ZVlIF8ptxDwK4"
        output.delete(0, tk.END)
        output.insert(0, link)
    else:
        messagebox.showerror("Error", "Please enter a file ID.")

# GUI
root = tk.Tk()
root.title("Google Drive Link Generator")
root.geometry("500x150")

tk.Label(root, text="Enter Google Drive File ID:").pack(pady=5)
entry = tk.Entry(root, width=60)
entry.pack()

tk.Button(root, text="Generate Link", command=generate_download_link).pack(pady=5)
output = tk.Entry(root, width=60)
output.pack()

root.mainloop()
