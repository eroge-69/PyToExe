import math
import random
import sys
import pandas as pd
import pickle
import pprint
import tkinter as Tk

class calenar_window:
    def __init__(self):
        root=Tk.Tk()
        root.geometry("600x600")
        root.title("Календарь для любимой планеты")
        root.config(bg='#a39ea0')
        Tk.Label(root,text="Период прецессии, земные сут.", font=('Arial,15,bold'),bg='#a39ea0').place(x=10,y=10)
        Tk.Label(root, text="Сидерический период, земные сут. ", font=('Arial,15,bold'),bg='#a39ea0').place(x=10,y=50)
        Tk.Label(root, text="Период обращения, земные сут.", font=('Arial,15,bold'),bg='#a39ea0').place(x=10,y=90)
        Tk.Label(root, text="Количество месяцев", font=('Arial,15,bold'),bg='#a39ea0').place(x=10,y=150)
        Tk.Label(root, text="Количество дней в неделе", font=('Arial,15,bold'),bg='#a39ea0').place(x=10,y=190)
        Tk.Label(root, text="Год в местном календаре", font=('Arial,15,bold'),bg='#a39ea0').place(x=10,y=230)
        Tk.Label(root, text="Название планеты", font=('Arial,15,bold'),bg='#a39ea0').place(x=10,y=270)
        Tk.Label(root, text="Результат", font=('Arial,15,bold'),bg='#a39ea0').place(x=10,y=310)
        Tk.Label(root, text="Тропический период", font=('Arial,15,bold'),bg='#a39ea0').place(x=10,y=350)
        Tk.Label(root, text="Номер високосного года", font=('Arial,15,bold'),bg='#a39ea0').place(x=10,y=390)
        Tk.Label(root, text="Номер усечённого високосного года", font=('Arial,15,bold'),bg='#a39ea0').place(x=10,y=430)
        self.precession_periodVar=Tk.StringVar()
        Tk.Entry(root, textvariable=self.precession_periodVar,font=('Arial,15,bold')).place(x=350,y=10)
        self.sidereal_periodVar=Tk.StringVar()
        Tk.Entry(root, textvariable=self.sidereal_periodVar,font=('Arial,15,bold')).place(x=350,y=50)
        self.rotation_periodVar=Tk.StringVar()
        Tk.Entry(root, textvariable=self.rotation_periodVar,font=('Arial,15,bold')).place(x=350,y=90)
        self.quantity_of_monthsVar=Tk.StringVar()
        Tk.Entry(root, textvariable=self.quantity_of_monthsVar,font=('Arial,15,bold')).place(x=350,y=150)
        self.days_in_weekVar=Tk.StringVar()
        Tk.Entry(root, textvariable=self.days_in_weekVar,font=('Arial,15,bold')).place(x=350,y=190)
        self.yearVar=Tk.StringVar()
        Tk.Entry(root, textvariable=self.yearVar,font=('Arial,15,bold')).place(x=350,y=230)
        self.planet_nameVar=Tk.StringVar()
        Tk.Entry(root, textvariable=self.planet_nameVar,font=('Arial,15,bold')).place(x=350,y=270)
        self.result=Tk.StringVar()
        Tk.Label(root, textvariable=self.result,font=('Arial,15,bold'),bg='#a39ea0').place(x=350,y=310)
        self.tropical_period=Tk.StringVar()
        Tk.Label(root, textvariable=self.tropical_period,font=('Arial,15,bold'),bg='#a39ea0').place(x=350,y=350)
        self.number_of_lead_year=Tk.StringVar()
        Tk.Label(root, textvariable=self.number_of_lead_year,font=('Arial,15,bold'),bg='#a39ea0').place(x=350,y=390)
        self.number_of_truncated_lead_year=Tk.StringVar()
        Tk.Label(root, textvariable=self.number_of_truncated_lead_year,font=('Arial,15,bold'),bg='#a39ea0').place(x=350,y=430)
        Tk.Button(root, text="Создать календарь",font=('Arial,15,bold'),command=self.calendar).place(x=180,y=470)
        root.mainloop()
    def calendar(self):
        #все числовые параметры вводятся в земных среднесолнечных сутках с точностью до 4 знаков
        precession_period = int(self.precession_periodVar.get())
        sidereal_period = float(self.sidereal_periodVar.get())
        rotation_period = float(self.rotation_periodVar.get())
        quantity_of_months = int(self.quantity_of_monthsVar.get())
        days_in_week = int(self.days_in_weekVar.get())
        year = int(self.yearVar.get())
        planet_name = self.precession_periodVar
        #считаем параметры года
        tropical_period = round((precession_period*sidereal_period/(precession_period+sidereal_period))/rotation_period, 4)
        usual_year = math.floor(tropical_period) #уже в местных сутках  
        if usual_year == tropical_period:
            number_of_lead_year = 0
            number_of_truncated_lead_year = 0
        else:
            number_of_lead_year = int(10000//(10000*(tropical_period-usual_year)))
            quantity_of_truncated_lead_years = int((10000%(10000*(tropical_period-usual_year)))//number_of_lead_year)
            number_of_truncated_lead_year = int((10000//number_of_lead_year)//quantity_of_truncated_lead_years)
            
        days_in_month = usual_year//quantity_of_months
        tail = usual_year-days_in_month*quantity_of_months
        if days_in_month == 0:
            self.result.set("АААААААААААААААААА ошибка, стоп 000000 — слишком большое количество месяцев")
            sys.exit()
        if year%number_of_lead_year==0 and year%(number_of_lead_year*number_of_truncated_lead_year)!=0:
            ++tail
            
        delta_usual = usual_year % days_in_week
        delta_lead = (usual_year+1) % days_in_week

        start_day = (delta_lead * (year//number_of_lead_year) - (year//number_of_truncated_lead_year) + delta_usual * (year - year//number_of_lead_year)) % 7 - 1
        #генерируем случайные названия месяцев и дней недели
        names_of_months = []
        for i in range (quantity_of_months):
            name_of_month  = ""
            lenght = random.randint(3, 10)
            name_of_month += ''.join(chr(random.randint(1041, 1071)) for i in range(lenght))
            names_of_months += [name_of_month]
            
        names_of_days = []
        for i in range (days_in_week):
            name_of_day  = ""
            lenght = random.randint(3, 10)
            name_of_day += ''.join(chr(random.randint(1041, 1071)) for i in range(lenght))
            names_of_days += [name_of_day]
            
        #формируем календарь
        months = []
        for i in range (quantity_of_months):
            temp = []
            for j in range (start_day):
                temp += [0]
            temp1 = list(map(int, ((i) for i in range(1, days_in_month+1))))
            temp += temp1
            c = ((days_in_month+start_day)//days_in_week+1) * days_in_week - (days_in_month+start_day)
            for k in range (c):
                    temp += [0]
            temp = [temp[i:i + days_in_week] for i in range(0, len(temp), days_in_week)]
            start_day = days_in_week - c
            months += [temp]
           
        df_list = []
        for j in range(quantity_of_months):
            df = pd.DataFrame(months[j], columns = names_of_days)
            df_list += []
            df_list += [names_of_months[j]]
            df_list += [df]
            
        calendar = [[year]]
        calendar += df_list

        #костыль для последнего месяца
        calendar += ["ПРИХВОСТЕНЬ"]
        temp = []
        for j in range (start_day):
            temp += [0]
        temp1 = list(map(int, ((i) for i in range(1, tail+1))))
        temp += temp1
        c = (days_in_month//days_in_week+1) * days_in_week - len(temp)
        for k in range (c):
                temp += [0]
        temp = [temp[i:i + days_in_week] for i in range(0, len(temp), days_in_week)]
        df = pd.DataFrame(temp, columns = names_of_days)
        calendar += [df]

        #сохраняем календарь в txt-файл
        pickle.dumps(calendar)

        with open("Календарь для планеты {0} на {1} год.txt".format(planet_name, year), "a") as f:
            pprint.pprint(calendar, stream=f)

        self.result.set("Готово!")
        self.tropical_period.set(format(tropical_period, '10.4f'))
        self.number_of_lead_year.set(format(number_of_lead_year, 'd'))
        self.number_of_truncated_lead_year.set(format(number_of_truncated_lead_year, 'd'))
    
    
if __name__=="__main__":
    calenar_window()
'''
sum_delta_lead = (delta_lead + delta_usual * (delta_usual - 1))%7
sum_delta_truncated = (delta_lead * (number_of_truncated_lead_year//number_of_lead_year-1) + delta_usual * (number_of_truncated_lead_year - number_of_truncated_lead_year//number_of_lead_year + 1))%7

calendar = []
for j in range(quantity_of_months):
    temp=[]
    calendar += [names_of_months[j]]
    temp = list(map(int, ((i) for i in range(1, days_in_month+1))))
    for k in range ((days_in_month//days_in_week+1) * days_in_week - len(temp)):
        temp += [0]
    temp = np.reshape(np.array(temp), (days_in_month//days_in_week+1, days_in_week))
    calendar += [temp]
calendar += ["ПРИХВОСТЕНЬ"]
temp = list(map(int, ((i) for i in range(1, tail+1))))
for k in range ((tail//days_in_week+1) * days_in_week - len(temp) + 1):
    temp += [0]
if tail>days_in_week:
    temp = np.reshape(np.array(temp), (tail//days_in_week+1, days_in_week))
calendar += [temp]
df_list = []
print(1)
for i in range (0, width):
    
    data = [[calendar[i+1]]
            [calendar[i+3]]
            [calendar[i+5]]]
    df = pd.DataFrame(data, columns=[calendar[i], calendar[i+2], calendar[i+4]])
    print(3)
    df_list += df
    ++i
data = [[df_list[0]]
        [df_list[1]]
        [df_list[2]]]
print(2)
df = pd.DataFrame(data)
print(df)
'''
