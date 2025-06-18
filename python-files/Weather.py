from tkinter import *
from tkinter import ttk

import requests



def data_get():
    city = city_name.get()
    url = f"https://api.openweathermap.org/data/2.5/weather?q=" + city + "&appid=40af1d690cf5aca12b4ea4db5b2cfdbc"
    data = requests.get(url).json()
    w_label1.config(text=data["weather"][0]["main"])
    wb_label1.config(text=data["weather"][0]["description"])
    temp_label1.config(text=str(int(data["main"]["temp"] - 273.15)))
    press_label1.config(text=data["main"]["pressure"])





win = Tk()
win.title("Weather Forecast Tool")
win.config(bg="blue")
win.geometry("500x500")

name_label = Label(win, text="Weather App", font=("Time New Roman", 30, "bold"))
name_label.place(x=25, y=50, height=50, width=450)

city_name = StringVar()

list_name = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
]
com = ttk.Combobox(win, text="Weather Tracker By Mohit Sinha", values=list_name, font=("Time New Roman", 20, "bold"), textvariable=city_name)

com.place(x=25, y=150, height=50, width=450)


w_label = Label(win, text="Weather Climate", font=("Time New Roman", 15))
w_label.place(x=25, y=280, height=50, width=210)
w_label1 = Label(win, text="", font=("Time New Roman", 15))
w_label1.place(x=250, y=280, height=50, width=210)

wb_label = Label(win, text="Weather Description", font=("Time New Roman", 15))
wb_label.place(x=25, y=330, height=50, width=210)
wb_label1 = Label(win, text="", font=("Time New Roman", 15))
wb_label1.place(x=250, y=330, height=50, width=210)

temp_label = Label(win, text="Temperature", font=("Time New Roman", 15))
temp_label.place(x=25, y=380, height=50, width=210)
temp_label1 = Label(win, text="", font=("Time New Roman", 15))
temp_label1.place(x=250, y=380, height=50, width=210)

press_label = Label(win, text="Pressure", font=("Time New Roman", 15))
press_label.place(x=25, y=430, height=50, width=210)
press_label1 = Label(win, text="", font=("Time New Roman", 15))
press_label1.place(x=250, y=430, height=50, width=210)

done_button = Button(win, text="Done", font=("Time New Roman", 20, "bold"),command=data_get)
done_button.place(x=200, y=220, height=50, width=100)

win.mainloop()