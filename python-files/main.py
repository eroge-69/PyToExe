import time
import tkinter as tk

root = tk.Tk()
gif = tk.PhotoImage(file="programing_files/remember_me.gif")
label = tk.Label(root, image=gif)
label.pack()
root.mainloop()

import programing_files.dreams

root = tk.Tk()
gif = tk.PhotoImage(file="programing_files/gif/eyes.gif")
label = tk.Label(root, image=gif)
label.pack()
root.mainloop()

print('do you want to use calculator')
calc_choice = input ('1 = yes 2 = no')
if calc_choice =='1':
    import programing_files.calc_py
    time.sleep(2)
else:
    time.sleep(0.6)
    print ('no calculator')
    