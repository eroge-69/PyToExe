from tkinter import *
from tkinter import messagebox
import random
import os

from translate import Translator


FOS = Tk()
FOS.title("FobuimOS")
FOS.attributes('-fullscreen', True)
FOS.resizable(width=False, height=False)
FOS["bg"] = "blue"



open_windows = {}
taskbar_buttons = {}

def show_desktop():
    
    start_button.pack_forget()
    
    
    desktop_frame = Frame(FOS, bg="navy")
    desktop_frame.pack(fill=BOTH, expand=True)
    
    
    taskbar_frame = Frame(FOS, bg="gray20", height=40)
    taskbar_frame.pack(fill=X, side=BOTTOM)
    taskbar_frame.pack_propagate(False)
    
    
    clock_label = Label(taskbar_frame, text="00:00:00", bg="gray20", fg="white")
    clock_label.pack(side=RIGHT, padx=10)
    
    def update_clock():
        from time import strftime
        clock_label.config(text=strftime('%H:%M:%S'))
        clock_label.after(1000, update_clock)
    
    update_clock()
    
    
    global taskbar_apps_frame
    taskbar_apps_frame = Frame(taskbar_frame, bg="gray20")
    taskbar_apps_frame.pack(side=LEFT, fill=X, expand=True, padx=10)
    
    
    create_desktop_icons(desktop_frame)

def add_to_taskbar(app_name, window):
    
    if app_name not in taskbar_buttons:
        btn = Button(taskbar_apps_frame, text=app_name, 
                    command=lambda: bring_to_front(app_name), bg="gray30", fg="white")
        btn.pack(side=LEFT, padx=2)
        taskbar_buttons[app_name] = (btn, window)

def bring_to_front(app_name):
    
    if app_name in taskbar_buttons:
        window = taskbar_buttons[app_name][1]
        window.deiconify()  
        window.lift()     
        window.focus_force()

def remove_from_taskbar(app_name):
    
    if app_name in taskbar_buttons:
        taskbar_buttons[app_name][0].destroy()
        del taskbar_buttons[app_name]

def create_desktop_icons(desktop):
    
    
    def open_calculator():
        if "calculator" in open_windows:
            bring_to_front("Калькулятор")
            return
            
        calc_window = Toplevel(FOS)
        calc_window.title("Калькулятор")
        calc_window.geometry("300x400")
        
        
        entry = Entry(calc_window, font=('Arial', 20), justify=RIGHT)
        entry.pack(fill=X, padx=10, pady=10)
        
        
        buttons_frame = Frame(calc_window)
        buttons_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+',
            'C', '(', ')', '←'
        ]
        
        
        row, col = 0, 0
        for btn_text in buttons:
            if btn_text == '=':
                btn = Button(buttons_frame, text=btn_text, font=('Arial', 16),
                           command=lambda: calculate_result(entry))
            elif btn_text == 'C':
                btn = Button(buttons_frame, text=btn_text, font=('Arial', 16),
                           command=lambda: entry.delete(0, END))
            elif btn_text == '←':
                btn = Button(buttons_frame, text=btn_text, font=('Arial', 16),
                           command=lambda: entry.delete(len(entry.get())-1))
            else:
                btn = Button(buttons_frame, text=btn_text, font=('Arial', 16),
                           command=lambda t=btn_text: entry.insert(END, t))
            
            btn.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
            col += 1
            if col > 3:
                col = 0
                row += 1
        
        
        for i in range(5):
            buttons_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            buttons_frame.grid_columnconfigure(i, weight=1)
        
        open_windows["calculator"] = calc_window
        add_to_taskbar("Калькулятор", calc_window)
        
        def on_close():
            calc_window.destroy()
            remove_from_taskbar("Калькулятор")
            open_windows.pop("calculator")
        
        calc_window.protocol("WM_DELETE_WINDOW", on_close)
    
    def calculate_result(entry):
        try:
            result = eval(entry.get())
            entry.delete(0, END)
            entry.insert(0, str(result))
        except:
            entry.delete(0, END)
            entry.insert(0, "Ошибка")
    
    def open_translator():
        if "translator" in open_windows:
            bring_to_front("Переводчик")
            return
            
        trans_window = Toplevel(FOS)
        trans_window.title("Переводчик")
        trans_window.geometry("500x400")
        
        Label(trans_window, text="Русский текст:", font=('Arial', 12)).pack(pady=5)
        russian_text = Text(trans_window, height=6, width=50, font=('Arial', 11))
        russian_text.pack(pady=5, padx=10)
        
        Label(trans_window, text="Английский перевод:", font=('Arial', 12)).pack(pady=5)
        english_text = Text(trans_window, height=6, width=50, font=('Arial', 11))
        english_text.pack(pady=5, padx=10)
        
        def translate_text():
            try:
                text = russian_text.get("1.0", END).strip()
                if text:
                    translator = Translator(from_lang="ru", to_lang="en")
                    translation = translator.translate(text)
                    english_text.delete("1.0", END)
                    english_text.insert("1.0", translation)
                else:
                    messagebox.showwarning("Внимание", "Введите текст для перевода")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось перевести: {str(e)}")
        
        Button(trans_window, text="Перевести", command=translate_text, 
               font=('Arial', 12), bg="lightblue").pack(pady=10)
        
        open_windows["translator"] = trans_window
        add_to_taskbar("Переводчик", trans_window)
        
        def on_close():
            trans_window.destroy()
            remove_from_taskbar("Переводчик")
            open_windows.pop("translator")
        
        trans_window.protocol("WM_DELETE_WINDOW", on_close)
    
    def open_notes():
        if "notes" in open_windows:
            bring_to_front("Заметки")
            return
            
        notes_window = Toplevel(FOS)
        notes_window.title("Заметки")
        notes_window.geometry("400x600")
        
        
        text_area = Text(notes_window, font=('Arial', 12), wrap=WORD)
        text_area.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        
        buttons_frame = Frame(notes_window)
        buttons_frame.pack(fill=X, padx=10, pady=5)
        
        def save_note():
            note = text_area.get("1.0", END)
            try:
                with open("note.txt", "w", encoding="utf-8") as f:
                    f.write(note)
                messagebox.showinfo("Сохранено", "Заметка сохранена!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")
        
        def load_note():
            try:
                if os.path.exists("note.txt"):
                    with open("note.txt", "r", encoding="utf-8") as f:
                        content = f.read()
                    text_area.delete("1.0", END)
                    text_area.insert("1.0", content)
                else:
                    messagebox.showinfo("Инфо", "Нет сохраненных заметок")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить: {str(e)}")
        
        Button(buttons_frame, text="Сохранить", command=save_note, 
               font=('Arial', 11), bg="lightgreen").pack(side=LEFT, padx=5)
        Button(buttons_frame, text="Загрузить", command=load_note,
               font=('Arial', 11), bg="lightblue").pack(side=LEFT, padx=5)
        Button(buttons_frame, text="Очистить", command=lambda: text_area.delete("1.0", END),
               font=('Arial', 11), bg="lightcoral").pack(side=LEFT, padx=5)
        
        open_windows["notes"] = notes_window
        add_to_taskbar("Заметки", notes_window)
        
        def on_close():
            notes_window.destroy()
            remove_from_taskbar("Заметки")
            open_windows.pop("notes")
        
        notes_window.protocol("WM_DELETE_WINDOW", on_close)
    
    def open_game():
        if "game" in open_windows:
            bring_to_front("КНБ")
            return
            
        game_window = Toplevel(FOS)
        game_window.title("Камень-Ножницы-Бумага")
        game_window.geometry("400x600")
        
        result_text = StringVar()
        result_text.set("Выберите ваш ход")
        
        Label(game_window, text="Камень-Ножницы-Бумага", font=('Arial', 16, 'bold')).pack(pady=15)
        
        choice_frame = Frame(game_window)
        choice_frame.pack(pady=15)
        
        Button(choice_frame, text="Камень", width=10, height=2,
               command=lambda: play_game("камень"), font=('Arial', 12)).pack(side=LEFT, padx=8)
        Button(choice_frame, text="Ножницы", width=10, height=2,
               command=lambda: play_game("ножницы"), font=('Arial', 12)).pack(side=LEFT, padx=8)
        Button(choice_frame, text="Бумага", width=10, height=2,
               command=lambda: play_game("бумага"), font=('Arial', 12)).pack(side=LEFT, padx=8)
        
        result_label = Label(game_window, textvariable=result_text, font=('Arial', 14))
        result_label.pack(pady=20)
        
        score_frame = Frame(game_window)
        score_frame.pack(pady=15)
        
        Label(score_frame, text="Счет:", font=('Arial', 12)).pack(side=LEFT)
        score_label = Label(score_frame, text="Победы: 0 | Поражения: 0 | Ничьи: 0", font=('Arial', 12))
        score_label.pack(side=LEFT, padx=10)
        
        wins, losses, draws = 0, 0, 0
        
        def play_game(user_choice):
            nonlocal wins, losses, draws
            choices = ["камень", "ножницы", "бумага"]
            computer_choice = random.choice(choices)
            
            if user_choice == computer_choice:
                result = f"Ничья! Оба выбрали {user_choice}"
                draws += 1
            elif (user_choice == "камень" and computer_choice == "ножницы") or \
                 (user_choice == "ножницы" and computer_choice == "бумага") or \
                 (user_choice == "бумага" and computer_choice == "камень"):
                result = f"Вы выиграли! {user_choice} побеждает {computer_choice}"
                wins += 1
            else:
                result = f"Вы проиграли! {computer_choice} побеждает {user_choice}"
                losses += 1
            
            result_text.set(f"Компьютер выбрал: {computer_choice}\n{result}")
            score_label.config(text=f"Победы: {wins} | Поражения: {losses} | Ничьи: {draws}")
        
        open_windows["game"] = game_window
        add_to_taskbar("Игра", game_window)
        
        def on_close():
            game_window.destroy()
            remove_from_taskbar("Игра")
            open_windows.pop("game")
        
        game_window.protocol("WM_DELETE_WINDOW", on_close)
    

    apps = [
        ("Калькулятор", open_calculator),
        ("Переводчик", open_translator), 
        ("Заметки", open_notes),
        ("КНБ", open_game)
    ]
    
    for i, (name, func) in enumerate(apps):
        btn = Button(desktop, text=name, width=15, height=3, 
                    command=func, bg="lightblue", font=('Arial', 12))
        btn.place(x=50 + (i * 200), y=50)


start_button = Button(FOS, text="Войти", command=show_desktop, 
                     font=('Arial', 20), width=10, height=2, bg="lightgreen")
start_button.pack(expand=True)


FOS.bind('<Escape>', lambda e: FOS.attributes('-fullscreen', False))

FOS.mainloop()