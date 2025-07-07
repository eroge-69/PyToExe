import tkinter as tk
from tkinter import messagebox

def calculate():
    try:
        total_room = float(entry_total_room.get())
        nights = float(entry_nights.get())
        if nights == 0:
            messagebox.showerror("Error", "Nights cannot be zero.")
            return
        rate = (total_room - 2 * nights) / nights / 1.087
        rate = round(rate, 2)
        total_room_rounded = round(total_room, 2)

        # Format to always show 2 decimal places
        rate_str = f"{rate:.2f}"
        total_room_str = f"{total_room_rounded:.2f}"

        result_text = (
            f"Change the room rate to {rate_str}\n"
            f"Change the Market Code to W2M\n"
            f"Add to Notes:\nCharge Virtual Card: ${total_room_str}"
        )
        result_label.config(text=result_text)
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers.")

root = tk.Tk()
root.title("Room Rate Calculator")
root.configure(bg="black")

window_width = 400
window_height = 350
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

label_total_room = tk.Label(root, text="Total Room:", fg="lime", bg="black", font=("Arial", 12))
label_total_room.pack(pady=(15, 0))

entry_total_room = tk.Entry(root, font=("Arial", 12), justify="center", bg="black", fg="lime", insertbackground="lime")
entry_total_room.pack(pady=5)

label_nights = tk.Label(root, text="Nights:", fg="lime", bg="black", font=("Arial", 12))
label_nights.pack(pady=(10, 0))

entry_nights = tk.Entry(root, font=("Arial", 12), justify="center", bg="black", fg="lime", insertbackground="lime")
entry_nights.pack(pady=5)

calc_button = tk.Button(root, text="Calculate Rate", command=calculate, bg="lime", fg="black", font=("Arial", 12, "bold"))
calc_button.pack(pady=15)

result_label = tk.Label(root, text="", fg="lime", bg="black", font=("Consolas", 12), justify="left", anchor="nw")
result_label.pack(padx=10, pady=(5,15), fill="both", expand=True)

result_label.config(height=8)

root.mainloop()
