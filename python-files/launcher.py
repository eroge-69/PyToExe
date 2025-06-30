import subprocess
import sys
def safe_import(package):
    try:
        return __import__(package)
    except ImportError:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return __import__(package)
        except subprocess.CalledProcessError as e:
            print(f"Ошибка установки {package}: {e.stderr.decode()}")
            raise

try:
    psutil = safe_import("psutil")
    minecraft = safe_import("minecraft_launcher_lib")
except Exception as e:
    print(f"Фатальная ошибка: {e}")
    sys.exit(1)

import psutil
import tkinter as tk
from tkinter import Tk, Label, Entry, Button, mainloop,Frame,Toplevel,Scale,HORIZONTAL,Checkbutton,BooleanVar
from tkinter import ttk
from tkinter.ttk import Combobox
import minecraft_launcher_lib


import json
import os

mem = psutil.virtual_memory()

mem_min = 1
mem_max = str(mem[0])[:2]
mem_max = int(mem_max)-1
deflt_mem = "2"

class App:

    def __init__(self, master):
        self.master = master


        self.check_var1 = tk.BooleanVar()
        self.checkbutton1 = tk.Checkbutton(master, variable=self.check_var1,text='Отображать Снапшоты, Альфа, Бета версии',
            onvalue=1, offvalue=0,command=self.check_snap_shots)
        self.checkbutton1.place(x =0, y = 100)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Загрузка состояний
        self.load_states()

    def on_closing(self):
        self.save_states()
        self.master.destroy()

    def save_states(self):
        states = {
            "check_var1": self.check_var1.get()
        }
        with open("check_states.json", "w") as f:
            json.dump(states, f)

    def load_states(self):
        if os.path.isfile("check_states.json"):
            with open("check_states.json", "r") as f:
                states = json.load(f)
                self.check_var1.set(states.get("check_var1", 0))
   
    def check_snap_shots(self):
        if self.check_var1.get() == True:
            version_list = []
            for i in versions:
                version_list.append(i["id"])
            version_select.config(values=version_list)
                
        if self.check_var1.get() == False:
            version_list = []           
            for i in versions:
                if i["type"] == "release":
                    version_list.append(i["id"])
            version_select.config(values=version_list)




def main():
    global versions
    global version_select

    def open_options_window():
        
        
        
        
        
        global memory_set
        global inf_for_mem
        
        
        
        #создание дочернего окна
        new_window = Toplevel(window)
        app = App(new_window)    
        new_window.title("Настройки") 
        new_window.geometry("500x300")
        new_window.grab_set()
        new_window.resizable(width=False, height=False)
        
        

        
        #опция включения и выключения снапшотов
               
        #ползунок для выбора памяти
        memory_set = Scale(new_window, from_=mem_min, to=mem_max,
                              orient= HORIZONTAL)
        memory_set.place(x=150,y=10)
        str_memory = Label(new_window,text = "Выделение памяти: ", font= "Centry 11")
        str_memory.place(x= 0, y = 20)
        
        #кнопка подтверждения памяти
        mem_conf_btn = ttk.Button(new_window,text = "подтвердить",command=set_mem)
        mem_conf_btn.place(x= 300,y = 20)
        inf_for_mem = Label(new_window,text = f"Используемая память: {deflt_mem} ГБ",font = "Arial 9")
        inf_for_mem.place(x = 330,y = 50)
        
        
    def set_mem():
        global deflt_mem

        deflt_mem = str(memory_set.get())
        inf_for_mem.config(text = f"Используемая память: {deflt_mem} ГБ",font = "Arial 9")
        
        
    def launch():
        window.withdraw()

        minecraft_launcher_lib.install.install_minecraft_version(version_select.get(), minecraft_directory)

        login_data_s = username_input.get()

        options = {
            'username': login_data_s,
            "jvmArguments": [f"-Xmx{deflt_mem}"+"G"]
                }
        
        minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(version_select.get(), minecraft_directory, options)
    
        subprocess.run(minecraft_command)

        sys.exit(0)

    window = Tk()
    window.title("WLauncher")
    window.geometry("1050x660")
    window.resizable(width=False, height=False)

    frame1 = Frame(window, bg="AntiqueWhite2",width=1500,height=200)
    frame1.place(x=0,y =580)
    
    username_input = Entry(window,width=38)
    username_input.place(x=20, y = 590)

    minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
    versions = minecraft_launcher_lib.utils.get_available_versions(minecraft_directory)
    
    version_list = []           
    for i in versions:
        if i["type"] == "release":
            version_list.append(i["id"])

    ttk.Button(window,text = "Настройки",command= open_options_window).place(x=950,y = 590)
    

    version_select = Combobox(window, values=version_list,width=38)
    version_select.place(x=285, y = 590)
    

    
    version_select.current(0)

    ttk.Button(window, text="Запуск", command=launch,width=25).place(x= 575, y = 590)

    mainloop()


if __name__ == "__main__":
    main()

