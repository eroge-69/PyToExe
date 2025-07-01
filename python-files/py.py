import tkinter as tk
import random

window = tk.Tk()
window.title('Game')

text = tk.Label(window, text='You are in dark room in a mysterious castle\nIn front of you are five doors. You must choose one.')
text.pack()

entry = tk.Entry(window)
entry.pack(padx=10, pady=10)

response_text = tk.Label(window, text='', wraplength=300)
response_text.pack()

def send():
    playerChoice = entry.get()
    if playerChoice == '1':
        response_text.config(text='You find a room full of treasure. You are rich!\n\nRICH ENDING')
    elif playerChoice == '2':
        response_text.config(text='You go into the room and found a sleeping dragon.\n'
                                   '1) Try to steal some of dragon gold\n'
                                   '2) Try to sneak around the dragon to the exit\n')
        entry.delete(0, tk.END)
        entry.insert(0, '1 or 2')
        entry.bind('<Return>', dragon_choice)
    elif playerChoice == '3':
        response_text.config(text='You are in a bedroom, and you found a crystal of teleport! Where do you want to teleport?\n'
                                   '1) To the room of gold. I try to steal some money\n'
                                   '2) To the sunshine. I try to sneak around this castle\n'
                                   '3) To my bedroom... In MY house... I am tired...\n')
        entry.delete(0, tk.END)
        entry.insert(0, '1, 2 or 3')
        entry.bind('<Return>', teleport_choice)
    elif playerChoice == '4':
        response_text.config(text='You enter a room with a sphinx.\n'
                                   'It asks you to guess what number it is thinking of, between 1 and 10.')
        entry.delete(0, tk.END)
        entry.insert(0, 'guess a number between 1 and 10')
        entry.bind('<Return>', sphinx_choice)
    elif playerChoice == '5':
        response_text.config(text='It is the exit of the castle.\n\nEXIT ENDING')

def dragon_choice(event):
    dragonChoice = entry.get()
    if dragonChoice == '1':
        response_text.config(text='The dragon wakes up and eats you. You are delicious.\n\nDRAGON ENDING')
    elif dragonChoice == '2':
        response_text.config(text='You sneak around the castle, blinking in the sunshine.\n\nSNEAK ENDING')
    entry.delete(0, tk.END)

def teleport_choice(event):
    teleportCrystal = entry.get()
    if teleportCrystal == '1':
        response_text.config(text='You go into the room and found a sleeping dragon.\nIt wakes up and eats you.\n\nDRAGON ENDING')
    elif teleportCrystal == '2':
        response_text.config(text='You sneak around the castle, blinking in the sunshine.\n\nSNEAK ENDING')
    elif teleportCrystal == '3':
        response_text.config(text='OK, you are teleporting...\n-------UNKNOWN ERROR-------\n'
                                  '------Please try again-----\nType 1 to try again, 2 to exit')
        entry.delete(0, tk.END)
        entry.insert(0, '1 or 2')
        entry.bind('<Return>', teleport_retry)
    entry.delete(0, tk.END)

def teleport_retry(event):
    playerType = entry.get()
    if playerType == '1':
        response_text.config(text='OK, you are teleporting...\n-------UNKNOWN ERROR-------\nERROR ENDING')
    elif playerType == '2':
        response_text.config(text='You chose to exit without retrying.')
    entry.delete(0, tk.END)

def sphinx_choice(event):
    try:
        number = int(entry.get())
        if number == random.randint(1, 10):
            response_text.config(text='The sphinx tells you it gives you money, it is the correct answer!\n\nRICH ENDING')
        else:
            response_text.config(text='The sphinx tells you that your guess is incorrect.\n'
                                      'You are now its prisoner forever.\n\nSPHINX ENDING')
    except ValueError:
        response_text.config(text='Please enter a valid number between 1 and 10.')
    entry.delete(0, tk.END)

button = tk.Button(window, text="Send", command=send)
button.pack(padx=10, pady=10)

window.mainloop()