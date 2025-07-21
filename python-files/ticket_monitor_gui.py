
import requests
import time
import threading
from tkinter import Tk, Label, Entry, Button, messagebox
from win10toast import ToastNotifier
from datetime import datetime

toaster = ToastNotifier()

def show_notification(message):
    toaster.show_toast("🚆 Билеты РЖД найдены!", message, duration=15, threaded=True)

def check_tickets(departure, arrival, date, interval):
    url = "https://www.rzd.ru/v3/api/public/en/timetable/trains"
    headers = {"User-Agent": "Mozilla/5.0"}

    while True:
        print(f"[{datetime.now()}] Проверка билетов {departure} → {arrival} на {date}")
        payload = {
            "direction": "0",
            "st0": departure,
            "st1": arrival,
            "dt0": date,
            "checkSeats": "1"
        }

        try:
            r = requests.get(url, params=payload, headers=headers)
            r.raise_for_status()
            data = r.json()

            trains = data.get("tp", [])
            if not trains:
                print("Поезда не найдены.")
            else:
                found = False
                msg_text = ""

                for train in trains[0].get("list", []):
                    num = train["number"]
                    name = train.get("brand", "")
                    cars = train.get("cars", [])

                    for car in cars:
                        free = int(car["freeSeats"])
                        if free > 0:
                            found = True
                            msg_text += f"{num} ({name}) - {car['type']} - Свободно: {free} мест\n"

                if found:
                    print("🚨 Билеты найдены!")
                    print(msg_text)
                    show_notification(msg_text)
                else:
                    print("Свободных мест нет.")

        except Exception as e:
            print("Ошибка при проверке:", e)

        time.sleep(interval)

def start_check():
    dep = entry_dep.get().strip()
    arr = entry_arr.get().strip()
    date = entry_date.get().strip()
    if not (dep and arr and date):
        messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
        return

    try:
        datetime.strptime(date, "%d.%m.%Y")
    except ValueError:
        messagebox.showerror("Ошибка", "Дата должна быть в формате ДД.ММ.ГГГГ")
        return

    interval = 600
    threading.Thread(target=check_tickets, args=(dep, arr, date, interval), daemon=True).start()
    messagebox.showinfo("Мониторинг запущен", f"Отслеживаем {dep} → {arr} на {date}")

root = Tk()
root.title("Мониторинг билетов РЖД")

Label(root, text="Станция отправления:").grid(row=0, column=0, sticky="e")
Label(root, text="Станция прибытия:").grid(row=1, column=0, sticky="e")
Label(root, text="Дата (ДД.ММ.ГГГГ):").grid(row=2, column=0, sticky="e")

entry_dep = Entry(root, width=30)
entry_arr = Entry(root, width=30)
entry_date = Entry(root, width=15)

entry_dep.grid(row=0, column=1, padx=10, pady=5)
entry_arr.grid(row=1, column=1, padx=10, pady=5)
entry_date.grid(row=2, column=1, padx=10, pady=5)

Button(root, text="Запустить мониторинг", command=start_check).grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()
