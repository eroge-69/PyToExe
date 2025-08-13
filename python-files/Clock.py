import tkinter as tk
from time import strftime
import ctypes

# Show message box using ctypes
ctypes.windll.user32.MessageBoxW(
    0,
    "This collects Date But Dosen't Sell to Cybercriminals/Hackers, "
    "But Tracks your location and Tells the time So don't worry "
    "Your address, age, ID, Credit card, or Location Won't be found.",
    "Privacy Info",
    0
)

# Clock GUI
root = tk.Tk()
root.title("Clock")

def time():
    string = strftime('%H:%M:%S %p\n%A\n%B %d, %Y')
    label.config(text=string)
    label.after(1000, time)

label = tk.Label(root, font=('calibri', 40, 'bold'), background='black', foreground='white')
label.pack(anchor='center')

time()
root.mainloop()
