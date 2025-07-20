import random
import tkinter as tk
from tkinter import messagebox

words = ['python', 'kod', 'skrypt', 'praca', 'aplikacja', 'projekt']

def choose_word():
    return random.choice(words)

def draw():
    if mistake == 1:
        art.create_line(75, 300, 150, 300, width = 3)

    if mistake == 2:
        art.create_line(150, 300, 225, 300, width = 3)

    if mistake == 3:
        art.create_line(150, 300, 150, 50, width = 3)

    if mistake == 4:
            art.create_line(150, 50, 250, 50, width = 3)

    if mistake == 5:
        art.create_line(250, 50, 250, 100, width = 3)

    if mistake == 6:
        art.create_oval(234, 98, 263, 127, width = 3)

    if mistake == 7:
        art.create_line(248, 127, 248, 202, width = 3)

    if mistake == 8:
        art.create_line(248, 127, 220, 167, width = 3)

    if mistake == 9:
        art.create_line(248, 126, 278, 167, width = 3)

    if mistake == 10:
        art.create_line(218, 248, 248, 200, width = 3)

    if mistake == 11:
        art.create_line(278, 248, 248, 200, width = 3)
        string.delete(0, tk.END)
        string.config(state='disabled')
        messagebox.showerror('Przegrałeś!', 'Spróbuj ponownie!')

def write():
    w = ''.join([s if s in letters else '_' for s in word])
    result.config(text=' '.join(w))

    if w == word:
        messagebox.showerror('Wygrana', 'Gratuluję, wygrałeś!')

def guees():
    global mistake
    if not string.get():
        messagebox.showerror('Błąd', 'Wartośc pola jest pusta.\nSpróbuj ponownie!')

    s = str(string.get())

    if s in letters:
        string.delete(0, tk.END)
        messagebox.showerror('Pomyłka', 'Litera została pobrana!')
        return

    letters.append(s)

    if s in word:
        string.delete(0, tk.END)
        write()
    else:
        mistake += 1
        draw()
        string.delete(0, tk.END)

def tryagain():
    global word, mistake, letters
    word = choose_word()
    art.delete('all')
    string.delete(0, tk.END)
    mistake = 0
    letters = []
    print(word)
    result.config(text=' '.join(['_' for _ in word]))

hangman = tk.Tk()
hangman.title('Wisielec')

art = tk.Canvas(hangman, bg = 'white', width = 300, height = 300)
art.pack(padx = 10, pady = 10, fill = tk.BOTH, expand = True)

frame = tk.Frame(hangman)
frame.pack()

result = tk.Label(frame, text = '', font = ('Arial', 11, 'normal'))
result.pack(side = tk.TOP)

string = tk.Entry(frame, font = ('Arial', 11, 'normal'), width = 16)
string.pack(side = tk.TOP)

add = tk.Button(frame, text='Sprawdź', command = guees, bg = '#50C878', fg = 'white', font = ('Arial', 10, 'bold'), width = 7)
add.pack(side = tk.LEFT)

tryagain = tk.Button(frame, text='Od nowa', command = tryagain, bg = '#EE4B2B', fg = 'white', font = ('Arial', 10, 'bold'), width = 7)
tryagain.pack(side = tk.LEFT)

word = choose_word()
result.config(text=' '.join(['_' for _ in word]))
mistake = 0
letters = []
print(word)
hangman.mainloop()