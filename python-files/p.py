from tkinter import *
from tkinter import messagebox
from string import ascii_uppercase

def center_window(window, width=300, height=200):
    # get screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # calculate position x and y coordinates
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    window.geometry('%dx%d+%d+%d' % (width, height, x, y))

def start_game():
    global secret_word
    secret_word = "".join(i for i in word_entry.get() if i.isalpha())
    if secret_word :
        start_menu.destroy()
        root.deiconify()
        guess_label["text"] = generat_guess(secret_word)
    else:
        messagebox.showinfo("No word entered", "Please enter a word",icon="warning")
        word_entry.delete(0,END)

def generat_guess(word):
    return " ".join("_" for _ in range(len(word)))

def check_letter(letter, button):
    global guess_label, wrong_guess, guessed_letters
    if letter in secret_word:
        word = [i for i in guess_label['text'] if i != " "]
        for idx, i in enumerate(secret_word):
            if i == letter:
                word[idx] = letter
                guessed_letters += 1
        guess_label["text"] = " ".join(i.upper() for i in word)
    else:
        wrong_guess += 1
        hang_man["image"] = hang_imgs[wrong_guess]
    button.config(state="disabled")
    check_game_over()
    
def check_game_over():
    if guessed_letters == len(secret_word):
        game_over("won")
    if wrong_guess == len(hang_imgs):
       game_over("lose")
    

def game_over(end):
    match end:
        case "won":
            if messagebox.showinfo("GAME OVER", "Game over you WIN!!") == "ok":
                root.destroy()
        case "lose":
            if messagebox.showinfo("GAME OVER", "Game over you LOSE!!") == "ok":
                root.destroy()

root = Tk()
center_window(root, 500, 600)
root.resizable(width=False, height=False)
root.title("Hang Man")
root.iconbitmap("images/icon.ico")

frame_ttl = Frame(root, width=500 , height=60)
frame_ttl.grid(row=0, column=0, columnspan=2)

frame_img = Frame(root, width=250, height=350)
frame_img.grid(row=1, column=0)

frame_gs = Frame(root, width=250, height=350)
frame_gs.grid(row=1, column=1)

frame_btn = Frame(root, width=500, height=150)
frame_btn.grid(row=2, column=0, columnspan=2)

hang_imgs = [PhotoImage(file=f"images/hangman{i}.png") for i in range(1, 9)]
wrong_guess = 0
lettters = ascii_uppercase
idx = 0
guessed_letters = 0

Label(frame_ttl, text="Hang Man Game", font=('Josefin Sans', 25, "bold")).place(relx=.5, rely=.5, anchor=CENTER)

hang_man = Label(frame_img, image=hang_imgs[wrong_guess])
hang_man.place(relx=.5, rely=.5, anchor=CENTER)

guess_label = Label(frame_gs, text="", font=('Josefin Sans', 20, "bold"))
guess_label.place(relx=.5, rely=.5, anchor=CENTER)

for i in range(3):
    for j in range(10):
        if i == 2 and (j == 0 or j == 1):
            continue
        if idx < len(lettters):
            btn = Button(frame_btn, text=lettters[idx], font=('Josefin Sans', 15, "bold"), width=2)
            btn.config(command=lambda x=lettters[idx].lower(), button=btn: check_letter(x, button))
            btn.grid(row=i, column=j, padx=2, pady=2)
            idx += 1
        else:
            continue






root.withdraw()



start_menu = Tk()
start_menu.title("Start Menu")
start_menu.resizable(width=False, height=False)
center_window(start_menu, 450, 300)
start_menu.iconbitmap("images/icon.ico")

Label(start_menu, text="Welcome to The Hang Man Game".upper(), font=('Josefin Sans', 15, "bold")).pack(pady=10, anchor=CENTER)
Label(start_menu, text="Enter the secret word :", font=('Josefin Sans', 18)).pack(pady=10)
word_entry = Entry(start_menu, font=('Josefin Sans', 15), justify=CENTER)
word_entry.pack(pady=10, ipady=5) 
start_btn =Button(start_menu, text="START", font=('Josefin Sans', 15), justify=CENTER, command=start_game)
start_btn.pack(pady=10) 


start_menu.mainloop()
