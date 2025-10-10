import tkinter as tk
from tkinter import messagebox
import pymem  # pyright: ignore[reportMissingImports]
import pymem.process  # pyright: ignore[reportMissingImports]
import os 


def set_sun_to_entry_value():
    val_text = entry.get().strip()
    if not val_text:
        messagebox.showerror("Input error", "Please enter a value.")
        return

    try:
        value = int(val_text)
    except ValueError:
        messagebox.showerror("Input error", "Please enter a valid integer.")
        return

    if value < 0:
        messagebox.showwarning("Clamped", "Negative values are not allowed. Clamping to 0.")
        value = 0
    if value > 99999:
        messagebox.showwarning("Clamped", "Value too large. Clamping to 99999.")
        value = 99999

    try:
        print("bypassing")
        bypass = 4
        detect = 1
        print(bypass, detect)
        pm = pymem.Pymem("PlantsVsZombies.exe")
        module = pymem.process.module_from_name(pm.process_handle, "PlantsVsZombies.exe").lpBaseOfDll
        base_address = module + 0x0035296C
        offsets = [0x868, 0x5578]

        address = pm.read_int(base_address)
        for offset in offsets[:-1]:
            address = pm.read_int(address + offset)

        final_address = address + offsets[-1]
        pm.write_int(final_address, value)

        messagebox.showinfo("Success", f"Set sun value to {value}.")
    except Exception as e:
        messagebox.showerror("Error421", f"Failed to set value: TRY again\n{e}")
        print("PLANTSVSZOMBIESERROR421")

def pressed_value():
    messagebox.showerror("pressed")
def about_info():
    messagebox.showinfo("info", "program made by jynxzer")

# --- GUI setup ---
root = tk.Tk()
root.geometry("600x600")
root.title("plants vs zombies bypassv1")
root.configure(bg="#D1E755")

label = tk.Label(root, text="Enter sun value:", bg="#D1E755")
label.pack(pady=(40, 10))

entry = tk.Entry(root, width=20, font=("Arial", 14))
entry.pack()

button = tk.Button(root, bg="#FFD700", width=16, height=2, text="Set value", command=set_sun_to_entry_value)
button.pack(pady=20)

button2 = tk.Button(root, bg="#FFD700" , text="about", width=16, height=2, command=about_info)
button2.pack(pady=20) 

butter = tk.Button(root, bg="#FFD700", text="close plants vs zombies",width=16, height=2,)
butter.pack(pady=20)

root.mainloop()
