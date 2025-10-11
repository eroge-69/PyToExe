
import customtkinter
import CTkFileDialog
import tkinter
import CTkTable
import pandas
import pathlib
import toplevel


window = customtkinter.CTk()
window.geometry('500x500')
window.title('مدیریت دادرسی مالیاتی فارس')

table_font = customtkinter.CTkFont(family='B Titr', size=20)



file_entry = customtkinter.CTkEntry(window, width=300)
file_entry.pack(pady='30')

def file_name():
    name = tkinter.filedialog.askopenfilename()
    file_entry.insert(0, f'{name}')
    # path = pathlib.Path(name)
    # file = pandas.read_excel(path)
    # daily_value = list(file.values)
    # table.configure(values=daily_value)




file_pick = customtkinter.CTkButton(window, command=file_name, text='انتخاب فایل', text_color='black', font=customtkinter.CTkFont(family='B Homa', size=20))
file_pick.pack()


speed_choose = customtkinter.CTkComboBox(window, values=['1000', '1100', '1200', '1300', '1400', '1500', '900', '800', '700', '600', '500', '500', '400', '300', '200', '100'])
speed_choose.pack(pady='30')

list_frame = None


def list_view():
    a = file_entry.get()
    b = speed_choose.get()
    list_frame = toplevel.AutoScrollApp(daily_list=a, speed=b)
    list_frame.auto_scroll()







eghdam = customtkinter.CTkButton(window, command=list_view, text='شروع', text_color='black', font=customtkinter.CTkFont(family='B Homa', size=20))
eghdam.pack()



window.mainloop()


















