from deep_translator import GoogleTranslator
from tkinter import *
from tkinter import ttk
import keyboard
import pyperclip as pc

root = Tk()
root.geometry("800x500+0+0")

target = "en"
def to_change(event):
    global source

    source = to_lang.get()

source="auto"
def from_change(event):
    global target

    target = from_lang.get()

def translate():
    to_translate = text_to.get("1.0",'end')
    translated = GoogleTranslator(source=source, target=target).translate(to_translate)
    text_from.delete("1.0",'end')
    text_from.insert(INSERT, translated)

def clear():
    text_to.delete("1.0", 'end')

def insert():
    if len(text_to.get("1.0", "end"))<=0:
        text_to.insert(INSERT, pc.paste())

keyboard.add_hotkey("Ctrl+V", insert)

available_languages = tuple(GoogleTranslator().get_supported_languages(as_dict=False))
font = ("Arial", 10)

to_lang = ttk.Combobox(root, values=("auto",)+available_languages, state="readonly", font=font)
to_lang.current(0)
to_lang.place(relwidth=0.3, relheight=0.05, rely=0.05, relx=0.1)
to_lang.bind("<<ComboboxSelected>>", to_change)

from_lang = ttk.Combobox(root, values=available_languages, state="readonly", font=font)
from_lang.current(21)
from_lang.place(relwidth=0.3, relheight=0.05, rely=0.05, relx=0.6)
from_lang.bind("<<ComboboxSelected>>", from_change)

perevodchik = Label(text = "Переводчик", font = ('Arial', 16, 'bold'))
perevodchik.pack()

Label(root, text="c", font=font).place(relwidth=0.1, relheight=0.05, rely=0.05, relx=0)
Label(root, text="на", font=font).place(relwidth=0.1, relheight=0.05, rely=0.05, relx=0.5)

text_to = Text(root, font=font)
text_to.place(relheight=0.7, relwidth=0.35, relx=0.1, rely=0.15)

text_from = Text(root, font=font)
text_from.place(relheight=0.7, relwidth=0.35, relx=0.55, rely=0.15)

button_translate = Button(root, text="Перевести", command=translate)
button_translate.place(relwidth=0.3, relheight=0.05, rely=0.9, relx=0.6)
button_clear = Button(root, text="Очистить", command=clear)
button_clear.place(relwidth=0.3, relheight=0.05, rely=0.9, relx=0.1)

root.mainloop()
