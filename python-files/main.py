import time
from tkinter import *
from tkinter import ttk
from winsound import *
from random import *

def first_button():
    entry.destroy()
    global second_window
    second_window = Tk()
    second_window.title("Рваное очко")
    second_window.geometry("500x500+0+0")

    global timer_label
    second_label = Label(text="Ты наверное думаешь что знаешь математику и программирование, да?\nСейчас мы это и проверим")
    second_button_start_timer = Button(text="Начать", width=50, command=second_button)

    second_label.pack()
    second_button_start_timer.pack()

temni_prince = lambda: PlaySound("sound.wav", SND_FILENAME)
entry_sound = lambda: PlaySound('entry.wav', SND_FILENAME)



#--------------------------------2 слайд------------------------------
counter = 0
def dop():
    global counter
    counter += 1
    dopbtn['text'] = f"Звучит легко {counter} раз"

def random_windows():
    arr = ["Водопадик", "Лучшая подруга", "Role-play", "25 кадр", "210 часов в ZA POE", "Звучит легко", "Спортивные перчатки", "Обоснованные штаны", "Долбеб", "Даун ты долбоеб", "Петтинг", "Репосты у тебя ваще заебись", "Украинизация"]
    for i in range(100):
        x = randint(10, 1800)
        y = randint(10, 1000)
        i = randint(0, len(arr)-1)
        win = Tk()
        win.geometry(f"300x50+{x}+{y}")
        txt = arr[i]
        win.title(txt)
    final_button = Button(text="ФИНАЛ", command=grand_finale)
    final_button.pack()

def second_button():
    temni_prince()
    second_window.destroy()
    global third_window
    third_window = Tk()
    third_window.geometry("500x500+0+0")
    third_window.title("Тест на знание программирования и математики")

    q1 = Label(text="Как на языке C++ выводить текст в консоль?")
    a1 = Text(height=2)
    q2 =Label(text="Корень квадртаный из 16, умноженный на 7:")
    a2 = Text(height=2)
    q3 = Label(text="Как зовут твоего преподавателя по матану?")
    a3 = Text(height=2)
    q4 = Label(text="По какому принципу шифруется текст в кодировке BaseN?")
    a4 = Text(height=2)
    global dopbtn
    dopbtn = Button(text="Звучит легко", width=40, command=random_windows)
    q1.pack()
    a1.pack()
    q2.pack()
    a2.pack()
    q3.pack()
    a3.pack()
    q4.pack()
    a4.pack()
    dopbtn.pack()

#---------- GRAND FINALE ------------

def grand_finale():
    third_window.destroy()
    final_window = Tk()
    final_window.geometry('1200x800+0+0')
    frame25 = PhotoImage(file='doner.png')
    frame25_label = Label(image=frame25)
    frame25_label.image = frame25
    frame25_label.pack()

#---------- Entry window ------------
def entry_func():

    root.destroy()

    global entry
    entry = Tk()
    entry.title("Приложение")
    entry.geometry(f"800x800+0+0")

    entry_sound()

    entry_label = Label(
        text="Привет мой друг!\nДавно не виделись! Не забыл еще, \nчто пока ты проебывал время на ZAPOE2, \n"
             "твой лучший друг Роман учился настоящему бизнесу?\nЭто мой проект, над которым я работал на протяжении\n "
             "последнего месяца. \nВ него было вложено \nочень много сил и времени, надеюсь он тебе понравится.\n",
        font=('Arial', 20))
    entry_label.pack()
    btn = ttk.Button(text="Сосать", command=first_button)
    btn.config(width=50)
    btn.pack()



    viperr = PhotoImage(file="viperr.png")
    viperr_label = Label(image=viperr, text="нiнмiш и кiй", compound="top")
    viperr_label.image = viperr
    viperr_label.pack()



root = Tk()
root.geometry('300x300+0+0')
entry_button = Button(text="Start", command=entry_func)
entry_button.pack(anchor="s")

root.mainloop()