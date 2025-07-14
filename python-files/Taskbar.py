# importing tkinter module
from tkinter import *
from tkinter.ttk import *
import messagebox


print('By ivan_super123')





# creating tkinter window
root = Tk()
root.title('Убывающяя шкала')

# Progress bar widget
progress = Progressbar(root, orient = HORIZONTAL,
              length = 500, mode = 'determinate')

# Function responsible for the updation
# of the progress bar value
def bar():
    progress['value'] = 100
    
    for x in range(100):
        import time
        progress['value'] -= 1
        root.update_idletasks()
        time.sleep(1)

    messagebox.showinfo('info', 'Время вышло!!!')
    

    


    

progress.pack(pady = 10)

# This button will initialize
# the progress bar
Button(root, text = 'Start', command = bar).pack(pady = 10)

# infinite loop
mainloop()
