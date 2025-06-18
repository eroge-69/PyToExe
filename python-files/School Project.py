import tkinter as tk

root = tk.Tk()
root.title("Compact Calculator")

history = []  # Store previous calculations

def calc(key):
    if key == "=":
        try:
            result = str(eval(entry.get()))
            history.append(f"{entry.get()} = {result}")  # Add to history
            entry.set(result)
        except:
            entry.set("Error")
    elif key == "C":
        entry.set("")
    elif key == "Hist":
        entry.set("\n".join(history[-5:]))  # Show last 5 calculations
    else:
        entry.set(entry.get() + key)

entry = tk.StringVar()
frame = tk.Frame(root)
frame.pack(fill="both", expand=True)

display = tk.Entry(frame, textvariable=entry, font=("Arial", 20), justify="right")
display.pack(fill="both", expand=True)

buttons = [
    "7", "8", "9", "/", "C",
    "4", "5", "6", "*", "(",
    "1", "2", "3", "-", ")",
    "0", ".", "=", "+", "Hist"
]

for b in buttons:
    tk.Button(frame, text=b, font=("Arial", 20),
              command=lambda x=b: calc(x)).pack(fill="both", expand=True, side="left")

root.mainloop()
