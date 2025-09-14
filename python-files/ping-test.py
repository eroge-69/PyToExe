import tkinter as tk

# Create the main window
root = tk.Tk()
root.title("My First App")
root.geometry("300x200")  # width x height

entry = tk.Entry(root, width=20)
entry.pack()
# If user typed "Roblox" then say "Logged in"
def check_entry():
    if entry.get() == "Roblox":
        print("Logged in")
    else:
        print("Access Denied")

btn = tk.Button(root, text="Submit", command=check_entry)
btn.pack()

root.mainloop()