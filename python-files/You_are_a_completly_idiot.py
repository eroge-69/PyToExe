from tkinter import *
import tkinter as tk

import threading
import time
import random
import sys

def disable_event():
	pass
def move_window():
	root = Tk()
	root.title('YOU ARE A COMPLETLY IDIOT :D')
	root.attributes('-toolwindow', True)

	x = random.randint(0, 999)
	y = random.randint(0, 999)
	root.resizable(0,0)
	root.geometry(f'235x200+{x}+{y}')
	root.configure(background='white')

	Label(root, text='You are an IDIOT', fg='black', font=('Terminal', 13), bg='white').place(x=50, y=20)
	Label(root, text='Imagine clicking a POP-UP', fg='red', font=('Terminal', 13), bg='white').place(x=20, y=100)

	root.protocol("WM_DELETE_WINDOW", disable_event

    
    root.mainloop()
 if __name__ == "__main__":
 	while True: 
 		thread = threading.Thread(target=move_window)	
 		thread.start()
