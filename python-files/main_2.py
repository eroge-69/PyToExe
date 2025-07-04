from tkinter import *
import random as r
from tkinter import messagebox
import sys
import os

def resource_path(relative_path):

    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
wi = Tk()
wi.geometry("640x640")  
wi.title("TIC-TAC-TOE")


o_image = PhotoImage(file=resource_path("image cropped.png"))
x_image = PhotoImage(file=resource_path("circle.png"))

# Function 
def computer_move():
    empty_buttons = [btn for btn in buttons if not hasattr(btn, "played")]
    if empty_buttons:
        btn = r.choice(empty_buttons)
        btn.config(image=x_image)
        btn.image = x_image
        btn.symbol = 'X'
        btn.config(state="disabled")
        btn.played = True
        check_winner()

def display_x(btn):
    btn.config(image=o_image)
    btn.image = o_image
    btn.symbol = 'O'
    btn.config(state="disabled")
    btn.played = True

    if not check_winner():  # If player didn't win
        wi.after(500, computer_move)
   
    
def check_winner():
    grid = [['' for _ in range(3)] for _ in range(3)]
    for btn, (row, col) in positions.items():
        if hasattr(btn, "played"):
            grid[row][col] = getattr(btn, "symbol", '')

    def winner(symbol):
        for i in range(3):
            if all(grid[i][j] == symbol for j in range(3)): return True
            if all(grid[j][i] == symbol for j in range(3)): return True
        if all(grid[i][i] == symbol for i in range(3)): return True
        if all(grid[i][2 - i] == symbol for i in range(3)): return True
        return False

    if winner('O'):
        messagebox.showinfo("Game Over", "You Win!")
        disable_all()
        return True
    elif winner('X'):
        messagebox.showinfo("Game Over", "Computer Wins!")
        disable_all()
        return True
    elif all(hasattr(btn, "played") for btn in buttons):
        messagebox.showinfo("Game Over", "It's a Draw!")
        disable_all()
        return True
    return False
empty_image = PhotoImage(width=200, height=200)

# Frame 
frame = Frame(wi, padx=10, pady=10)
frame.pack()
positions = {}
def disable_all():
    for btn in buttons:
        btn.config(state="disabled")

#grid
buttons = []
for row in range(3):
    for col in range(3):
        btn = Button(frame,
                     image=empty_image,
                     width=200,
                     height=200,
                     compound='center')
        btn.grid(row=row, column=col)
        btn.config(command=lambda b=btn: display_x(b))
        buttons.append(btn)
        positions[btn] = (row, col)

wi.mainloop()
  