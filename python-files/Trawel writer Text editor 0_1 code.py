import tkinter as tk
import re
from tkinter.ttk import *
from tkinter.filedialog import askopenfilename, asksaveasfilename

# Stack to store text history
undo_stack = [""]
redo_stack = []

# Function to update undo stack on text change
def on_text_change( textb, undo_stack, redo_stack):
    current_text = textb.get(1.0, tk.END)
    if undo_stack[-1] != current_text:
        undo_stack.append(current_text)
    # Clear redo stack on new input
    redo_stack.clear()

# Function to handle undo
def undo_action( textb, undo_stack, redo_stack):
    if len(undo_stack) > 1:
        redo_stack.append(undo_stack.pop())
        textb.delete(1.0, tk.END)
        textb.insert(1.0, undo_stack[-1])

# Function to handle redo
def redo_action( textb, undo_stack, redo_stack):
    if redo_stack:
        text = redo_stack.pop()
        undo_stack.append(text)
        textb.delete(1.0, tk.END)
        textb.insert(1.0, text)


def test(event):
    print("run")

def save_file(root, textb):
    file_path = asksaveasfilename(filetypes = [("Text Files, .txt")])

    if not file_path:
        return

    with open(file_path, "w") as f:
        content = textb.get(1.0, tk.END)
        f.write(content)



 #setting up the batshit abomination that is the options
def options_enabled(buts,textb):
    but1 = buts[0]
    but2 = buts[1]
    but3 = buts[2]
    but4 = buts[3]
    but5 = buts[4]  

    print("\a")

    but1.focus()

    #setting up the arrow keys
    arrow_keyR = root.bind("<Right>", lambda event: right_option(buts))
    arrow_keyL = root.bind("<Left>", lambda event: left_option(buts))

#setting up the F1 key to go back also apperently you cant bind stuff to array and frame does not work
    op_key = but1.bind("<F1>", lambda event: focus_back(textb))
    op_key = but2.bind("<F1>", lambda event: focus_back(textb))
    op_key = but3.bind("<F1>", lambda event: focus_back(textb))
    op_key = but4.bind("<F1>", lambda event: focus_back(textb))
    op_key = but5.bind("<F1>", lambda event: focus_back(textb))   

def focus_back(textb):
    print("\a")
    textb.focus_set()
   
# setting up what the right arrow does
def right_option(buts):
    work = root.focus_get()

    if work == buts[0]:
        buts[1].focus_set()
    if work == buts[1]:
        buts[2].focus_set()
    if work == buts[2]:
        buts[3].focus_set()
    if work == buts[3]:
        buts[4].focus_set()
    if work == buts[4]:
        buts[0].focus_set()
  
# setting up what the left arrow does
def left_option(buts):
    work = root.focus_get()

    if work == buts[4]:
        buts[3].focus_set()
    if work == buts[3]:
        buts[2].focus_set()
    if work == buts[2]:
        buts[1].focus_set()
    if work == buts[1]:
        buts[0].focus_set()
    if work == buts[0]:
        buts[4].focus_set()

  #setting up the word counting
def word_count(textb,but):
    words = textb.get(1.0, tk.END)
    word_number = len( re.findall( r'\w+', words ) )
    
    if word_number == 1:
        but_con = f"{word_number}" " SLOV0"
    elif word_number > 1 and word_number < 5:
        but_con = f"{word_number}" " SLOVA"
    else:
        but_con = f"{word_number}" " SLOV"

    but.bind("<Return>",lambda event: page_count(textb, but))

    but.configure(text=but_con)

 #setting up the page counting
def page_count(textb, but):
    symbols = textb.get(1.0, tk.END)
    
    # Remove line breaks
    symbol_no_line = symbols.replace('\n', '')

    # Count the number of characters excluding line breaks
    symbol_number = len(symbol_no_line)  
    page_number = symbol_number / 1500
    Number_fin = int(page_number)
    
    if Number_fin == 1:
        but_con = f"{Number_fin}" " STRANA"
    elif Number_fin > 1 and Number_fin < 5:
        but_con = f"{Number_fin}" " STRANY"
    else:
        but_con = f"{Number_fin}" " STRAN"
    
    print(symbol_number) 
    but.configure(text=but_con)
    but.bind("<Return>", lambda event: word_count(textb, but))


 #Setting up the window
root = tk.Tk()
root.geometry("490x362")
root.resizable(0,0)
root.title("Trawel writer: Text editor 0.2")
root['background']='#bfbfbf'
#root.attributes('-fullscreen', True)
    
#Setting up the textbox
Textbox = tk.Text(root, height=15, undo=True, font=('Sitka Banner', 12))
Textbox.pack(padx=6, pady=6)
Textbox['background']='#ffffff'
    
#Setting up the area for buttons
buttonframe = tk.Frame(root)

buttonframe['background']='#bfbfbf'
    
buttonframe.columnconfigure(0, weight=1)
buttonframe.columnconfigure(1, weight=1)  
buttonframe.columnconfigure(2, weight=1)
buttonframe.columnconfigure(3, weight=1)
buttonframe.columnconfigure(4, weight=1)
buttonframe.columnconfigure(5, weight=1)
buttonframe.columnconfigure(6, weight=1)
buttonframe.rowconfigure(0, weight=1)

buttonframe.pack(padx=33)

#getting icons from memory
save_ic = tk.PhotoImage(file=r'/home/ive/terka/coding/travel writer/icons/save_icon.png')
back_ic = tk.PhotoImage(file=r'/home/ive/terka/coding/travel writer/icons/back_icon.png')
forward_ic = tk.PhotoImage(file=r'/home/ive/terka/coding/travel writer/icons/forward_icon.png')
menu_ic = tk.PhotoImage(file=r'/home/ive/terka/coding/travel writer/icons/menu_icon.png')
word_ic = tk.PhotoImage(file=r'/home/ive/terka/coding/travel writer/icons/word_count_icon.png')

#Setting up the buttons
save_button = tk.Button(buttonframe, height=800, width=510, text= "ULOŽIT", font= ('Consolas', 9))
back_button = tk.Button(buttonframe, height=800, width=510, text= "ZPĚT", font= ('Consolas', 9))
forward_button = tk.Button(buttonframe, height=800, width=510, text= "ZNOVU", font= ('Consolas', 9))
back_button.configure(image = back_ic, compound = 'top')
menu_button = tk.Button(buttonframe, height=800, width=510, text= "MENŮ", font= ('Consolas', 9))
pageword_button = tk.Button(buttonframe, height=800, width=510, font= ('Consolas', 9)) 
word_count(Textbox, pageword_button)

Textbox.bind("<KeyRelease>", lambda event: word_count(Textbox, pageword_button))
# Capture every key press to track changes
Textbox.bind("<KeyRelease>", lambda event:on_text_change(Textbox, undo_stack, redo_stack))
root.bind("<Escape>", lambda event: quit())

menu_button['background']='#bfbfbf'
save_button['background']='#bfbfbf'
back_button['background']='#bfbfbf'
forward_button['background']='#bfbfbf'
pageword_button['background']='#bfbfbf'

save_button.grid(row=0, column= 1, pady=6, sticky = "s")
back_button.grid(row=0, column= 2, pady=6, sticky = "s")
forward_button.grid(row=0, column= 3, pady=6, sticky = "s")
menu_button.grid(row=0, column= 4, pady=6, sticky = "s")
pageword_button.grid(row=0, column= 5, pady=6, sticky = "s")

save_button.configure(image = save_ic, compound = 'top')
back_button.configure(image = back_ic, compound = 'top')
forward_button.configure(image = forward_ic, compound = 'top')
menu_button.configure(image = menu_ic, compound = 'top')
pageword_button.configure(image = word_ic, compound = 'top')

save_button.bind("<Return>", lambda event: save_file(root, Textbox))
menu_button.bind("<Return>",test)
back_button.bind("<Return>", lambda event: undo_action(Textbox, undo_stack, redo_stack))
forward_button.bind("<Return>", lambda event: redo_action(Textbox, undo_stack, redo_stack))
pageword_button.bind("<Return>",lambda event: counting(Textbox, pageword_button))

buttons = [save_button, back_button, forward_button, menu_button, pageword_button]

# seting the focus to the text box
Textbox.focus()
    
#setting the options bar to to f1
options_key = Textbox.bind("<F1>", lambda event: options_enabled(buttons, Textbox))

root.mainloop()