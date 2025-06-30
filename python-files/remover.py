import pymem
import os
import customtkinter
import tkinter

customtkinter.set_appearance_mode('dark')
app = customtkinter.CTk()
app.configure(bg='black')
app.geometry('700x300')
app.title('HORRIBLE SOURCE + NO PROTECTION .gg/AHK')

label = customtkinter.CTkLabel(app, text='.gg/AHK', text_color='#FF0000')
label.place(relx=0.5, rely=0.1, anchor=tkinter.CENTER)

entry = customtkinter.CTkEntry(app, placeholder_text='process name', width=120, height=25, border_width=2, corner_radius=10)
entry.place(relx=0.5, rely=0.2, anchor=tkinter.CENTER)

entry1 = customtkinter.CTkEntry(app, placeholder_text='memory address', width=120, height=25, border_width=2, corner_radius=10)
entry1.place(relx=0.5, rely=0.4, anchor=tkinter.CENTER)

entry2 = customtkinter.CTkEntry(app, placeholder_text='length', width=120, height=25, border_width=2, corner_radius=10)
entry2.place(relx=0.5, rely=0.6, anchor=tkinter.CENTER)

def button_event():
    procname = entry.get()
    print(procname)
    address = int(entry1.get(), 0)
    print(address)
    length = int(entry2.get(), 0)
    print(length)
    value = '.' * length
    pm = pymem.Pymem(procname)
    rs = pm.read_string(address, length)
    print(rs)
    pm.write_string(address, value)

button = customtkinter.CTkButton(app, width=120, height=32, border_width=0, corner_radius=8, fg_color='#FF0000', hover_color='#6A6767', text='remove string', command=button_event)
button.place(relx=0.5, rely=0.8, anchor=tkinter.CENTER)

app.mainloop()
