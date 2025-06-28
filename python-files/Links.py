from tkinter import *
from tkinter import messagebox
import sqlite3
from displayurls import DisplayU
import re
from tkinter import ttk



con = sqlite3.connect('database_urls.db')
cur = con.cursor()


class AddUrl:
    def __init__(self, root2):
        self.root2 = root2


   
        #Start
        #image
        self.icon_add = PhotoImage(file='icons/add.png')
        self.icon_url_add = PhotoImage(file='icons/urladd.png')
        self.icon_name = PhotoImage(file='icons/name.png')



        self.regex = re.compile(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")
       

        self.enturl = ttk.Label(self.root2, text='Enter The Url:', font='times 15 bold').place(x=40, y=40)
        self.addurl = ttk.Entry(self.root2, width=30, font='arial 15 bold')
        self.addurl.place(x=240, y=40)
        self.urlimage = ttk.Label(self.root2, image=self.icon_url_add).place(x=590, y=40)

        self.entname = ttk.Label(self.root2, text='Enter The Name:', font='times 15 bold').place(x=40, y=100)
        self.addname = ttk.Entry(self.root2, width=30, font='arial 15 bold')
        self.addname.place(x=240, y=100)
        self.name = ttk.Label(self.root2, image=self.icon_name).place(x=590, y=100)


        #Button
        self.btn_add = ttk.Button(self.root2, text='  Add To DataBase', image=self.icon_add, compound=LEFT, command=self.Funcadd).place(relx = 0.5, rely = 0.7, anchor = CENTER, y=15)
        self.btn_display = ttk.Button(self.root2, text='Display Links', command=self.funcdisplay).place(relx = 0.5, rely = 0.9, anchor = CENTER)
        #End



        self.menuico = PhotoImage(file='icons/menu.png')
        self.menuimag = ttk.Label(self.root2, image=self.menuico).place(x=590, y=160)
        self.entchoice = ttk.Label(self.root2, text='What is this link:', font='times 15 bold').place(x=40, y=160)
        self.n = StringVar()
        self.monthchoosen = ttk.Combobox(self.root2, width=15, textvariable=self.n, font='arial 15 bold')
        self.monthchoosen.place(x=240, y=160)

        # Adding combobox drop down list
        self.mychoices = (' Group', ' Account',' App', 'Course', 'Documentation', 'webApp')
        self.monthchoosen['values'] = self.mychoices






    def Funcadd(self):
        links2 = cur.execute('SELECT * FROM links').fetchall()
        list_urls = []
        for item in links2:
            list_urls.append(item[2].lower())


        if re.findall(self.regex, self.addurl.get()):
            if self.n.get() in self.mychoices:
                url = self.addurl.get()
                name = self.addname.get()
                type1 = self.n.get()

                if url.lower() in list_urls:
                    messagebox.showinfo('Warning', 'This link is in the database!', icon='warning')

                else:
                    if name != ' ':
                        query = "INSERT INTO 'links' (id, name, url, type) VALUES(?,?,?,?)"
                        cur.execute(query, (id(url), name, url, type1))
                        con.commit()
                        messagebox.showinfo('Success', 'Successfully added to database', icon='info')
                        self.addurl.delete(0, END)
                        self.addname.delete(0, END)
                        self.monthchoosen.delete('0', 'end')
            else:
                messagebox.showinfo('Warning', 'This choice is Wrong', icon='warning')
 
                
        else:
            messagebox.showinfo('Warning', 'This Link is Wrong', icon='warning')


    def funcdisplay(self):
        windows_display = DisplayU()
        self.root2.wm_state('iconic')




def main():
    root = Tk()
    window = AddUrl(root)
    root.geometry('700x360')
    root.resizable(False, False)
    root.title('Add Url')
    root.config(bg='#434242')
    root.iconbitmap("icons/app-development.ico")
    root.mainloop()

if __name__ == '__main__':
    main()

