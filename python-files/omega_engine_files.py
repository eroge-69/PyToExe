import tkinter
from tkinter import PhotoImage
from tkinter import Scrollbar, Text
import tkinter.filedialog




window = tkinter.Tk()



global file
global file_contents

global window_x
global window_y
window_x = 0
window_y = 0

file = None
file_contents = None

window.title("Omega Engine Debugger")
window.iconphoto(False, PhotoImage(file="icon.png"))
window.geometry(f"600x400+{window_x}+{window_y}")


other_menus_button = tkinter.Button(window, text="Other Menus")
other_menus_button.pack(padx=10, pady=10)

welcome_label = tkinter.Label(window, text="Omega Engine File Debugger", font=("Arial", 16))
welcome_label.pack(pady=20)

desc_label = tkinter.Label(window, text="Debug your custom mod scripts here!\nBut first... submit the file you want the debug engine to revew\nYou could also look at the other features this engine has to offer!", font=("Arial", 12))
desc_label.pack(pady=10)

open_file_button = tkinter.Button(window, text="Open File", command=lambda: open_file(), width=20, height=2, font=("Arial", 12))
open_file_button.pack(pady=10)

file_label = tkinter.Label(window, text=f"File open: {file}", font=("Arial", 10), foreground="green")
right_file_label = tkinter.Label(window, text="File is'nt recognised as an Omega Engine file", font=("Arial", 10), foreground="red")

read_file_button = tkinter.Button(window, text="Read File", command=lambda: _open_read_window())
#read_file_button.pack(pady=10, padx=10, anchor="se", fill=tkinter.X, side=tkinter.RIGHT)

def open_file():
    global file
    file = tkinter.filedialog.askopenfilename(
    title="Select a file",
    filetypes=(("JSON Files", "*.json"), ("XML Files", "*.xml"), ("Configuration Files", "*.cfg"), ("All files", "*.*"))
    )
    print(f"Selected file: {file}")
    global file_contents
    file_contents = open(file).read()
    print(f"The file contents are: {file_contents}")

    file_label.config(text=f"File open: {file}", foreground="green")
    file_label.pack_forget()
    file_label.pack(pady=10, side=tkinter.LEFT, anchor="sw", fill=tkinter.X)

    read_file_button.pack(pady=10, padx=10, anchor="se", fill=tkinter.X, side=tkinter.RIGHT)

    #read_file_button.pack(pady=10, padx=10, anchor="se", fill=tkinter.X, side=tkinter.RIGHT)

    #file_label.pack(pady=10, side=tkinter.LEFT)

    open_file_button.config(text="Close File", command=lambda: close_file())

def close_file():
    
    file = None
    file_contents = None
    
    file_label.pack_forget()

    read_file_button.pack_forget()

    open_file_button.config(text="Open File", command=lambda: open_file())

def _open_read_window():
    read_window = tkinter.Tk()
    read_window.title("Read File")

    #file_contents_text = tkinter.Label(read_window, text=f"File: {file}\nFile contents:\n\n{file_contents}", font=("Arial", 10), justify="left")
    #file_contents_text.pack(pady=10, padx=10, side=tkinter.LEFT, anchor="nw", fill=tkinter.X)
    read_window.geometry(f"400x300+{window_x}+{window_y}")

    #def close_read_file_window():
        #read_window.destroy()
        #window.destroy()

    #window.protocol("WM_DELETE_WINDOW", close_read_file_window)
    

    scrollbar = Scrollbar(read_window)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

    text_widget = Text(read_window, wrap="word", font=("Arial", 10), yscrollcommand=scrollbar.set)
    text_widget.insert("1.0", f"File: {file}\nFile info:{open(file)}\nFile contents:\n\n{file_contents}")
    text_widget.config(state="disabled")
    text_widget.pack(pady=10, padx=10, expand=True, fill="both", side=tkinter.LEFT)

    scrollbar.config(command=text_widget.yview)


    read_window.mainloop()



def on_main_close():
        window.destroy()

window.protocol("WM_DELETE_WINDOW", on_main_close)


window.mainloop()