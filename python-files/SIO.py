import random
from tkinter import ttk
import tkinter as tk
import time

names_list=("Егор","Даниил","Илья","Игорь","Анна","София","Тимур","Лаура","Даниэлла")
color_list=("red","blue","green","yellow","magenta","cyan","purple","orange")
aspects_tuple=("ЧЛ","БЛ","ЧС","БС","ЧЭ","БЭ","ЧИ","БИ")

#Модели А социотипов
TIM_functions={"Дон Кихот":{"ЧИ":"Базовая",
                            "БЛ":"Творческая",
                            "ЧС":"Ролевая",
                            "БЭ":"Болевая",
                            "БС":"Суггестивная",
                            "ЧЭ":"Оценочная",
                            "БИ":"Наблюдательная",
                            "ЧЛ":"Фоновая",},
               "Дюма":{"БС":"Базовая",
                            "ЧЭ":"Творческая",
                            "БИ":"Ролевая",
                            "ЧЛ":"Болевая",
                            "ЧИ":"Суггестивная",
                            "БЛ":"Оценочная",
                            "ЧС":"Наблюдательная",
                            "БЭ":"Фоновая",},
                "Гюго":{"ЧЭ":"Базовая",
                        "БС":"Творческая",
                        "ЧЛ":"Ролевая",
                        "БИ":"Болевая",
                        "БЛ":"Суггестивная",
                        "ЧИ":"Оценочная",
                        "БЭ":"Наблюдательная",
                        "ЧС":"Фоновая",},
               "Робеспьер":{"БЛ":"Базовая",
                            "ЧИ":"Творческая",
                            "БЭ":"Ролевая",
                            "ЧС":"Болевая",
                            "ЧЭ":"Суггестивная",
                            "БС":"Оценочная",
                            "ЧЛ":"Наблюдательная",
                            "БИ":"Фоновая",},
               "Жуков":{"ЧС":"Базовая",
                            "БЛ":"Творческая",
                            "ЧИ":"Ролевая",
                            "БЭ":"Болевая",
                            "БИ":"Суггестивная",
                            "ЧЭ":"Оценочная",
                            "БС":"Наблюдательная",
                            "ЧЛ":"Фоновая",},
               "Есенин":{"БИ":"Базовая",
                            "ЧЭ":"Творческая",
                            "БС":"Ролевая",
                            "ЧЛ":"Болевая",
                            "ЧС":"Суггестивная",
                            "БЛ":"Оценочная",
                            "ЧИ":"Наблюдательная",
                            "БЭ":"Фоновая",},
               "Гамлет":{"ЧЭ":"Базовая",
                            "БИ":"Творческая",
                            "ЧЛ":"Ролевая",
                            "БС":"Болевая",
                            "БЛ":"Суггестивная",
                            "ЧС":"Оценочная",
                            "БЭ":"Наблюдательная",
                            "ЧИ":"Фоновая",},
               "Максим Горький":{"БЛ":"Базовая",
                            "ЧС":"Творческая",
                            "БЭ":"Ролевая",
                            "ЧИ":"Болевая",
                            "ЧЭ":"Суггестивная",
                            "БИ":"Оценочная",
                            "ЧЛ":"Наблюдательная",
                            "БС":"Фоновая",},
               "Наполеон":{"ЧС":"Базовая",
                            "БЭ":"Творческая",
                            "ЧИ":"Ролевая",
                            "БЛ":"Болевая",
                            "БИ":"Суггестивная",
                            "ЧЛ":"Оценочная",
                            "БС":"Наблюдательная",
                            "ЧЭ":"Фоновая",},
               "Бальзак":{"БИ":"Базовая",
                            "ЧЛ":"Творческая",
                            "БС":"Ролевая",
                            "ЧЭ":"Болевая",
                            "ЧС":"Суггестивная",
                            "БЭ":"Оценочная",
                            "ЧИ":"Наблюдательная",
                            "БЛ":"Фоновая",},
               "Джек Лондон":{"ЧЛ":"Базовая",
                            "БИ":"Творческая",
                            "ЧЭ":"Ролевая",
                            "БС":"Болевая",
                            "БЭ":"Суггестивная",
                            "ЧС":"Оценочная",
                            "БЛ":"Наблюдательная",
                            "ЧИ":"Фоновая",},
               "Драйзер":{"БЭ":"Базовая",
                            "ЧС":"Творческая",
                            "БЛ":"Ролевая",
                            "ЧИ":"Болевая",
                            "ЧЛ":"Суггестивная",
                            "БИ":"Оценочная",
                            "ЧЭ":"Наблюдательная",
                            "БС":"Фоновая",},
               "Гексли":{"ЧИ":"Базовая",
                            "БЭ":"Творческая",
                            "ЧС":"Ролевая",
                            "БЛ":"Болевая",
                            "БС":"Суггестивная",
                            "ЧЛ":"Оценочная",
                            "БИ":"Наблюдательная",
                            "ЧЭ":"Фоновая",},
               "Габен":{"БС":"Базовая",
                            "ЧЛ":"Творческая",
                            "БИ":"Ролевая",
                            "ЧЭ":"Болевая",
                            "ЧИ":"Суггестивная",
                            "БЭ":"Оценочная",
                            "ЧС":"Наблюдательная",
                            "БЛ":"Фоновая",},
               "Штирлиц":{"ЧЛ":"Базовая",
                            "БС":"Творческая",
                            "ЧЭ":"Ролевая",
                            "БИ":"Болевая",
                            "БЭ":"Суггестивная",
                            "ЧИ":"Оценочная",
                            "БЛ":"Наблюдательная",
                            "ЧС":"Фоновая",},
               "Достоевский":{"БЭ":"Базовая",
                            "ЧИ":"Творческая",
                            "БЛ":"Ролевая",
                            "ЧС":"Болевая",
                            "ЧЛ":"Суггестивная",
                            "БС":"Оценочная",
                            "ЧЭ":"Наблюдательная",
                            "БИ":"Фоновая",}}



#коэффициенты отношения
function_line=                    ("Базовая","Творческая","Ролевая","Болевая","Суггестивная","Оценочная","Наблюдательная","Фоновая")
values_function={"Базовая":       (    0,         1,         -3,       -4,          3,            2,          -2,            -1    ),
                 "Творческая":    (    1,         0,         -4,       -3,          2,            3,          -1,            -2    ),
                 "Ролевая":       (   -3,        -4,          0,        1,         -2,           -1,           3,             2    ),
                 "Болевая":       (   -4,        -3,          1,        0,         -1,           -2,           2,             3    ),
                 "Суггестивная":  (    3,         2,         -2,       -1,          0,            1,          -3,            -4    ),
                 "Оценочная":     (    2,         3,         -1,       -2,          1,            0,          -4,            -3    ),
                 "Наблюдательная":(   -2,        -1,          3,        2,         -3,           -4,           0,             1    ),
                 "Фоновая":       (   -1,        -2,          2,        3,         -4,           -3,           1,             0    )}





#"полы и потолки" аспектов
floor_and_roof={"Базовая":("Базовая","Творческая","Ролевая","Суггестивная","Оценочная","Наблюдательная","Фоновая"),
                "Творческая":("Творческая","Ролевая","Суггестивная","Оценочная","Наблюдательная"),
                "Ролевая":("Ролевая","Суггестивная","Оценочная"),
                "Суггестивная":("Суггестивная","Суггестивная"),
                "Оценочная":("Ролевая","Суггестивная","Оценочная"),
                "Наблюдательная":("Творческая","Ролевая","Суггестивная","Оценочная","Наблюдательная"),
                "Фоновая":("Базовая","Творческая","Ролевая","Суггестивная","Оценочная","Наблюдательная","Фоновая")}











#отношения
relationship={"T1":[0,0,0,0,0,0],"T2":[0,0,0,0,0,0],"T3":[0,0,0,0,0,0],"T4":[0,0,0,0,0,0],"T5":[0,0,0,0,0,0],"T6":[0,0,0,0,0,0]}



#параметры окна
main=tk.Tk()
main.geometry("1500x950")
main.minsize(1500,950)
main.maxsize(1500,950)


#экран обмена
exchange_screen=tk.Canvas(bg="white", width=800, height=800)
exchange_screen.place(x=350,y=90)
hex_aspect=exchange_screen.create_polygon(300,250,  500,250,   600,390,   500,550,   300,550,     200,390, outline="black")

#имена разговаривающих
first_partner=tk.StringVar()
second_partner=tk.StringVar()
first_partner.set("Первый")
second_partner.set("Второй")
first_partner_name=tk.Label(textvariable=first_partner, font=16)
first_partner_name.place(x=450,y=10)
and_sign=tk.Label(text="и", font=16)
and_sign.place(x=750,y=10)
second_partner_name=tk.Label(textvariable=second_partner, font=16)
second_partner_name.place(x=970,y=10)

#значение отношений
relationship_bar=tk.Canvas(bg="lightgray", width=1480, height=23)
relationship_bar.place(x=10, y=55)
relation_val=relationship_bar.create_rectangle(745,2,   745,23,  fill="white")




#номер цикла
cycle=tk.IntVar()
value=cycle.get()
cycle_name=tk.Label(text="Цикл", font=18)
cycle_name.place(x=650,y=900)
cycle_number=tk.Label(textvariable=cycle, font=18)
cycle_number.place(x=800,y=900)



#сборник параметров 
all_TIM=["T1","T2","T3","T4","T5","T6"]
names_TIM=[]
types_TIM=[]
colors_TIM=[]





#создание ТИМов
for i in range(6):
    names_TIM.append(random.choice(names_list))
    types_TIM.append(random.choice(list(TIM_functions.keys())))
    colors_TIM.append(random.choice(color_list))
print(names_TIM)
print(types_TIM)
print(colors_TIM)



#Первый
first_oval=exchange_screen.create_oval(10,10,150,150, fill=colors_TIM[all_TIM.index("T1")])
first_name=tk.Label(text=names_TIM[all_TIM.index("T1")], font=16)
first_name.place(x=120,y=120)
first_tim=tk.Label(text=types_TIM[all_TIM.index("T1")], font=16)
first_tim.place(x=120,y=180)
#Второй
second_oval=exchange_screen.create_oval(10,320,150,460, fill=colors_TIM[all_TIM.index("T2")])
second_name=tk.Label(text=names_TIM[all_TIM.index("T2")], font=16)
second_name.place(x=120,y=430)
second_tim=tk.Label(text=types_TIM[all_TIM.index("T2")], font=16)
second_tim.place(x=120,y=490)
#Третий
third_oval=exchange_screen.create_oval(10,650,150,790, fill=colors_TIM[all_TIM.index("T3")])
third_name=tk.Label(text=names_TIM[all_TIM.index("T3")], font=16)
third_name.place(x=120,y=760)
third_tim=tk.Label(text=types_TIM[all_TIM.index("T3")], font=16)
third_tim.place(x=120,y=820)
#Четвёртый
fourth_oval=exchange_screen.create_oval(650,10,790,150, fill=colors_TIM[all_TIM.index("T4")])
fourth_name=tk.Label(text=names_TIM[all_TIM.index("T4")], font=16)
fourth_name.place(x=1270,y=120)
fourth_tim=tk.Label(text=types_TIM[all_TIM.index("T4")], font=16)
fourth_tim.place(x=1270,y=180)
#Пятый
fifth_oval=exchange_screen.create_oval(650,320,790,460, fill=colors_TIM[all_TIM.index("T5")])
fifth_name=tk.Label(text=names_TIM[all_TIM.index("T5")], font=16)
fifth_name.place(x=1270,y=430)
fifth_tim=tk.Label(text=types_TIM[all_TIM.index("T5")], font=16)
fifth_tim.place(x=1270,y=490)
#Шестой
sixth_oval=exchange_screen.create_oval(650,650,790,790, fill=colors_TIM[all_TIM.index("T6")])
sixth_name=tk.Label(text=names_TIM[all_TIM.index("T6")], font=16)
sixth_name.place(x=1270,y=760)
sixth_tim=tk.Label(text=types_TIM[all_TIM.index("T6")], font=16)
sixth_tim.place(x=1270,y=820)


def change_bar(number_one,number_two):
    if relationship[number_one][all_TIM.index(number_two)]>0:
        relationship_bar.coords(relation_val, 745,2,    745+(relationship[number_one][all_TIM.index(number_two)]*7.35),23)
        relationship_bar.itemconfig(relation_val, fill="darkgreen")
    elif relationship[number_one][all_TIM.index(number_two)]<0:
        relationship_bar.coords(relation_val, 745+(relationship[number_one][all_TIM.index(number_two)]*7.35),2,    745,23)
        relationship_bar.itemconfig(relation_val, fill="darkred")
    elif relationship[number_one][all_TIM.index(number_two)]==0:
        relationship_bar.coords(relation_val, 745,2,    745,23)
        relationship_bar.itemconfig(relation_val, fill="white")



while True:
    all_contacts={"T1":[],"T2":[],"T3":[],"T4":[],"T5":[],"T6":[]}
    for i in all_TIM:
        all_contacts[i]=all_TIM.copy()
        del all_contacts[i][all_TIM.index(i)]
        print(all_contacts)
    value+=1
    cycle.set(value)
    #выбор говорящих
    for partner_number_one in all_contacts:
        for partner_number_two in all_TIM:
            if partner_number_two not in all_contacts[partner_number_one]:
                continue
            else:
                first_partner.set(names_TIM[all_TIM.index(partner_number_one)])
                second_partner.set(names_TIM[all_TIM.index(partner_number_two)])
                val_ship=relationship[partner_number_one][all_TIM.index(partner_number_two)]
                print("начало:",val_ship)
                change_bar(partner_number_one,partner_number_two)
                possible_one=list(aspects_tuple).copy()
                for i in possible_one:
                    if TIM_functions[types_TIM[all_TIM.index(partner_number_one)]][i]=="Болевая":
                        del possible_one[aspects_tuple.index(i)]
                        break
                possible_two=list(aspects_tuple).copy()
                for i in possible_two:
                    if TIM_functions[types_TIM[all_TIM.index(partner_number_two)]][i]=="Болевая":
                        del possible_two[aspects_tuple.index(i)]
                        break
                print(partner_number_one)
                print(partner_number_two)
                #начало диалога
                while True:
                    #шестиугольник для определения говорящего
                    cur_aspect=random.choice(possible_one)
                    print(cur_aspect)
                    print(floor_and_roof[TIM_functions[types_TIM[all_TIM.index(partner_number_one)]][cur_aspect]])
                    cur_function=random.choice(floor_and_roof[TIM_functions[types_TIM[all_TIM.index(partner_number_one)]][cur_aspect]])
                    print(cur_function)
                    exchange_screen.itemconfig(hex_aspect, fill=colors_TIM[all_TIM.index(partner_number_one)])
                    if cur_aspect=="ЧИ":
                        form=exchange_screen.create_polygon(400,290,  500,500,  300,500,   outline="white",   fill="black")
                        function_label=exchange_screen.create_text(400,425,   text=cur_function[0],   fill="white", font=("Arial",55))
                    elif cur_aspect=="БИ":
                        form=exchange_screen.create_polygon(400,290,  500,500,  300,500,   outline="black",   fill="white")
                        function_label=exchange_screen.create_text(400,425,   text=cur_function[0],   fill="black", font=("Arial",55))
                    elif cur_aspect=="БС":
                        form=exchange_screen.create_oval(300,290,  500,500,  outline="black",   fill="white")
                        function_label=exchange_screen.create_text(400,395,   text=cur_function[0],   fill="black", font=("Arial",55))
                    elif cur_aspect=="ЧС":
                        form=exchange_screen.create_oval(300,290,  500,500,  outline="white",   fill="black")
                        function_label=exchange_screen.create_text(400,395,   text=cur_function[0],   fill="white", font=("Arial",55))
                    elif cur_aspect=="ЧЛ":
                        form=exchange_screen.create_rectangle(300,290,  500,500,  outline="white",   fill="black")
                        function_label=exchange_screen.create_text(400,400,   text=cur_function[0],   fill="white", font=("Arial",55))
                    elif cur_aspect=="БЛ":
                        form=exchange_screen.create_rectangle(300,290,  500,500,  outline="black",   fill="white")
                        function_label=exchange_screen.create_text(400,400,   text=cur_function[0],   fill="black", font=("Arial",55))
                    elif cur_aspect=="ЧЭ":
                        form=exchange_screen.create_polygon(300,290,  390,290,  390,430,  500,430,  500,500,  300,500,    outline="white",   fill="black")
                        function_label=exchange_screen.create_text(350,450,   text=cur_function[0],   fill="white", font=("Arial",55))
                    elif cur_aspect=="БЭ":
                        form=exchange_screen.create_polygon(300,290,  390,290,  390,430,  500,430,  500,500,  300,500,    outline="black",   fill="white")
                        function_label=exchange_screen.create_text(350,450,   text=cur_function[0],   fill="black", font=("Arial",55))
                    main.update()
                    time.sleep(2)
                    exchange_screen.delete(form)
                    exchange_screen.delete(function_label)
                    val_ship+=values_function[cur_function][function_line.index(TIM_functions[types_TIM[all_TIM.index(partner_number_two)]][cur_aspect])]
                    relationship[partner_number_one][all_TIM.index(partner_number_two)]=val_ship
                    print("середина:",val_ship)
                    change_bar(partner_number_one,partner_number_two)
                    if values_function[cur_function][function_line.index(TIM_functions[types_TIM[all_TIM.index(partner_number_two)]][cur_aspect])]<0:
                        if partner_number_two in all_contacts[partner_number_one]:
                            del all_contacts[partner_number_one][all_contacts[partner_number_one].index(partner_number_two)]
                            print(all_contacts)
                        if partner_number_one in all_contacts[partner_number_two]:
                            del all_contacts[partner_number_two][all_contacts[partner_number_two].index(partner_number_one)]
                            print(all_contacts)
                        main.update()
                        time.sleep(2)
                        break
                    main.update()
                    time.sleep(2)
                    cur_aspect=random.choice(possible_two)
                    cur_function=random.choice(floor_and_roof[TIM_functions[types_TIM[all_TIM.index(partner_number_two)]][cur_aspect]])
                    exchange_screen.itemconfig(hex_aspect, fill=colors_TIM[all_TIM.index(partner_number_two)])
                    if cur_aspect=="ЧИ":
                        form=exchange_screen.create_polygon(400,290,  500,500,  300,500,   outline="white",   fill="black")
                        function_label=exchange_screen.create_text(400,425,   text=cur_function[0],   fill="white", font=("Arial",55))
                    elif cur_aspect=="БИ":
                        form=exchange_screen.create_polygon(400,290,  500,500,  300,500,   outline="black",   fill="white")
                        function_label=exchange_screen.create_text(400,425,   text=cur_function[0],   fill="black", font=("Arial",55))
                    elif cur_aspect=="БС":
                        form=exchange_screen.create_oval(300,290,  500,500,  outline="black",   fill="white")
                        function_label=exchange_screen.create_text(400,395,   text=cur_function[0],   fill="black", font=("Arial",55))
                    elif cur_aspect=="ЧС":
                        form=exchange_screen.create_oval(300,290,  500,500,  outline="white",   fill="black")
                        function_label=exchange_screen.create_text(400,395,   text=cur_function[0],   fill="white", font=("Arial",55))
                    elif cur_aspect=="ЧЛ":
                        form=exchange_screen.create_rectangle(300,290,  500,500,  outline="white",   fill="black")
                        function_label=exchange_screen.create_text(400,400,   text=cur_function[0],   fill="white", font=("Arial",55))
                    elif cur_aspect=="БЛ":
                        form=exchange_screen.create_rectangle(300,290,  500,500,  outline="black",   fill="white")
                        function_label=exchange_screen.create_text(400,400,   text=cur_function[0],   fill="black", font=("Arial",55))
                    elif cur_aspect=="ЧЭ":
                        form=exchange_screen.create_polygon(300,290,  390,290,  390,430,  500,430,  500,500,  300,500,    outline="white",   fill="black")
                        function_label=exchange_screen.create_text(350,450,   text=cur_function[0],   fill="white", font=("Arial",55))
                    elif cur_aspect=="БЭ":
                        form=exchange_screen.create_polygon(300,290,  390,290,  390,430,  500,430,  500,500,  300,500,    outline="black",   fill="white")
                        function_label=exchange_screen.create_text(350,450,   text=cur_function[0],   fill="black", font=("Arial",55))
                    main.update()
                    time.sleep(2)
                    exchange_screen.delete(form)
                    exchange_screen.delete(function_label)
                    val_ship+=values_function[cur_function][function_line.index(TIM_functions[types_TIM[all_TIM.index(partner_number_one)]][cur_aspect])]
                    print("конец:",val_ship)
                    relationship[partner_number_two][all_TIM.index(partner_number_one)]=val_ship
                    change_bar(partner_number_two,partner_number_one)
                    if values_function[cur_function][function_line.index(TIM_functions[types_TIM[all_TIM.index(partner_number_one)]][cur_aspect])]<0:
                        if partner_number_two in all_contacts[partner_number_one]:
                            del all_contacts[partner_number_one][all_contacts[partner_number_one].index(partner_number_two)]
                            print(all_contacts)
                        if partner_number_one in all_contacts[partner_number_two]:
                            del all_contacts[partner_number_two][all_contacts[partner_number_two].index(partner_number_one)]
                            print(all_contacts)
                        main.update()
                        time.sleep(2)
                        break
                    main.update()
                    time.sleep(2)
        

main.mainloop()
