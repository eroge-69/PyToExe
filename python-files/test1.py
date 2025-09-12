from tkinter import * 
from tkinter import filedialog
from tkinter import messagebox as mb
from tkinter import ttk
import webbrowser
import os
def googlesearch():
    start = text1.index("sel.first")
    end = text1.index("sel.last")
    selected_text = text1.get(start, end) 
    search_query= selected_text
    #search_query = "привет мир"
    google_url = f"https://www.google.com/search?q={search_query}"
    webbrowser.open(google_url)
def textcheck(event):
    txt = text1.get("1.0", "end-1c")
    if not txt:
        mainmenu1.entryconfig("Вырезать               Ctrl+q", state="disabled")
        mainmenu1.entryconfig("Копировать          Ctrl+w", state="disabled")
        
        mainmenu1.entryconfig("Удалить                 Ctrl+r", state="disabled")
    else:
        mainmenu1.entryconfig("Вырезать               Ctrl+q", state="normal")
        mainmenu1.entryconfig("Копировать          Ctrl+w", state="normal")

        mainmenu1.entryconfig("Удалить                 Ctrl+r", state="normal")
def bufercheck(event):
    if T == "":
        mainmenu1.entryconfig("Вставить                Ctrl+e", state="disabled")
    else:
        mainmenu1.entryconfig("Вставить                Ctrl+e", state="normal")
def save_file():
    # Открываем диалоговое окно "Сохранить как..."
    filepath = filedialog.asksaveasfilename(
        defaultextension=".txt", # Расширение по умолчанию
        filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")] # Типы файлов
    )
    if filepath: # Если пользователь выбрал файл (не нажал "Отменить")
        # Здесь вы можете сохранить содержимое вашего приложения по этому пути
        print(f"Файл будет сохранен по пути: {filepath}")
        # Пример сохранения текста из виджета Text
        with open(filepath, "w") as file:
            file.write(text1.get("1.0", END))

def newokno():
    global tab_frame,text1
    tab_frame = ttk.Frame(notebook)
    notebook.add(tab_frame, text="Новая вкладка") # Здесь будет создаваться текст вкладки
    # Добавьте сюда виджеты для новой вкладки (например, Text для многострочного текста)
    text1 = Text(tab_frame,width=500,height=350,wrap=NONE) 
    text1.config(yscrollcommand=scrollV.set,xscrollcommand=scrollH.set) 
    text1.pack(fill=BOTH,expand=0) 
    scrollV.config(command=text1.yview) 
    scrollH.config(command=text1.xview) 
def perenosstrok():
    print(int(perenos.get()))
    if perenos.get():
        text1.config(wrap=WORD)
    else:
        text1.config(wrap=NONE)
def read_selected_file():
    text1.delete(1.0, 'end')
    file_path = filedialog.askopenfilename()
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Пример 3: построчная обработка с помощью цикла for
            file.seek(0)
            for line in file:
                text1.insert(END,line.strip() + '\n')


def cutevent(event):
    global T
    # Получаем начальный и конечный индексы выделения
    start = text1.index("sel.first")
    end = text1.index("sel.last")
    selected_text = text1.get(start, end) 
    # Получаем сам выделенный текст (для возможного копирования)
    # Удаляем выделенный текст из виджета
    text1.delete(start, end)
    # Очищаем буфер обмена и добавляем вырезанный текст
    # Это опционально, если вы хотите, чтобы текст был и вырезан, и скопирован
    #root.clipboard_clear()
    T = selected_text
    #root.clipboard_append(selected_text)
    #root.update()
def copyevent(event): 
    global T 
    start = text1.index("sel.first")
    end = text1.index("sel.last")
    selected_text = text1.get(start, end) 
    T = selected_text

def pasteevent(event): 
    text1.insert(END,T)
def deleteall(event):
    start = text1.index("sel.first")
    end = text1.index("sel.last")
    text1.delete(start, end)
def cut():
    global T
    start = text1.index("sel.first")
    end = text1.index("sel.last")
    selected_text = text1.get(start, end) 
    text1.delete(start, end)
    T = selected_text
def copy():
    global T 
    start = text1.index("sel.first")
    end = text1.index("sel.last")
    selected_text = text1.get(start, end) 
    T = selected_text
def paste():
    text1.insert(END,T)
def delete():
    start = text1.index("sel.first")
    end = text1.index("sel.last")
    text1.delete(start, end)
def exit_win(): 
    root.destroy() 
def openwindow():
    global root,scrollV,scrollH,mainmenu,textmenu,mainmenu1,mainmenu2,submenu,stroka,perenos,notebook,text1
    root = Tk() 
    root.title('Блокнот') 
    root.geometry("500x350") 
    #Добавляем полосы прокрутки 
    scrollV = Scrollbar(root,orient=VERTICAL) 
    scrollV.pack(side=RIGHT,fill=Y) 
    scrollH = Scrollbar(root,orient=HORIZONTAL) 
    scrollH.pack(side=BOTTOM,fill=X) 
    #Добавляем текстовый виджет 
    #text1 = Text(tab_frame,width=500,height=350,wrap=NONE) 
    #text1.config(yscrollcommand=scrollV.set,xscrollcommand=scrollH.set) 
    #text1.pack#(fill=BOTH,expand=0) 
    #Привязываем полосы прокрутки к виджету 
    #scrollV.config(command=text1.yview) 
    #scrollH.config(command=text1.xview) 
    #Создаем оконное меню 
    mainmenu = Menu(root) 
    root.config(menu=mainmenu) 
    textmenu = Menu(mainmenu, tearoff=0) 
    textmenu.add_command(label='Новая вкладка',command=newokno ) 
    textmenu.add_command(label='Новое окно',command=openwindow) 
    textmenu.add_command(label='Откpыть',command=read_selected_file ) 
    textmenu.add_command(label='Что нового' ) 
    textmenu.add_command(label='Сохранить' ) 
    textmenu.add_command(label='Сохранить как',command=save_file) 
    textmenu.add_command(label='Сохранить все' ) 
    textmenu.add_separator()
    textmenu.add_command(label='Параметры страницы' ) 
    textmenu.add_command(label='Печать' ) 
    textmenu.add_separator()
    textmenu.add_command(label='Закрыть вкладку' ) 
    textmenu.add_command(label='Закрыть окно' ) 
    textmenu.add_command(label='Выйти', command=exit_win) 
    mainmenu.add_cascade(label='Файл',menu=textmenu) 

    mainmenu1 = Menu(mainmenu, tearoff=0)
    mainmenu1.add_command(label="Отменить")
    mainmenu1.add_separator()
    mainmenu1.add_command(label="Вырезать               Ctrl+q",command=cut,state="disabled")
    mainmenu1.add_command(label="Копировать          Ctrl+w",command=copy,state="disabled")
    mainmenu1.add_command(label="Вставить                Ctrl+e",command=paste,state="disabled")
    mainmenu1.add_command(label="Удалить                 Ctrl+r",command=delete,state="disabled")
    mainmenu1.add_separator()
    mainmenu1.add_command(label="Поиск с помощью Google",command=googlesearch)
    mainmenu1.add_separator()
    mainmenu1.add_command(label="Найти")
    mainmenu1.add_command(label="Найти далее")
    mainmenu1.add_command(label="Найти ранее")
    mainmenu1.add_command(label="Заменить")
    mainmenu1.add_command(label="Перейти")
    mainmenu1.add_separator()
    mainmenu1.add_command(label="Bы6paть все")
    mainmenu1.add_command(label="Время и дата")
    mainmenu1.add_separator()
    mainmenu1.add_command(label="Шрифт")
    mainmenu.add_cascade(label="Изменить", menu=mainmenu1)

    mainmenu2 = Menu(mainmenu, tearoff=0)
    submenu = Menu(mainmenu2, tearoff=0) # tearoff=0 убирает отрывающуюся линию
    mainmenu2.add_cascade(label="Масштаб", menu=submenu)
    submenu.add_command(label="Увеличить")
    submenu.add_command(label="Уменьшить")
    submenu.add_separator() # Добавляет разделитель между пунктами
    submenu.add_command(label="Восстановить масштаб по умолчанию")
    stroka = IntVar()
    perenos = IntVar()
    mainmenu2.add_checkbutton(label="Строка состояния", variable=stroka)
    mainmenu2.add_checkbutton(label="Перенос по словам", variable=perenos,command=perenosstrok)
    mainmenu.add_cascade(label="Просмотр", menu=mainmenu2)
    notebook = ttk.Notebook(root)
    notebook.pack(expand=1, fill="both", padx=5, pady=5)
    tab_frame = ttk.Frame(notebook)
    notebook.add(tab_frame, text="Новая вкладка")
    text1 = Text(tab_frame,width=500,height=350,wrap=NONE) 
    text1.config(yscrollcommand=scrollV.set,xscrollcommand=scrollH.set) 
    text1.pack(fill=BOTH,expand=0) 
    scrollV.config(command=text1.yview) 
    scrollH.config(command=text1.xview) 
    text1.bind('<Control-q>', cutevent)
    text1.bind('<Control-w>', copyevent)
    text1.bind('<Control-e>', pasteevent) 
    text1.bind('<Control-r>', deleteall) 
    text1.bind("<KeyRelease>", bufercheck)
    text1.bind("<<Selection>>", textcheck)
    root.mainloop()
openwindow()
newokno()
