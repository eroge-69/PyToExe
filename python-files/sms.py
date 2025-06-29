
import pandas as pd
import pywhatkit
from datetime import datetime
import os
import time

file_name = "sms.xlsx"
file_path = os.path.join(os.path.dirname(__file__), file_name)

try:
    df = pd.read_excel(file_path)
except Exception as e:
    print(f"Ошибка при открытии файла: {e}")
    input("Нажмите Enter для выхода...")
    exit()

today = datetime.now().date()

for index, row in df.iterrows():
    try:
        date_str = row["Unnamed: 7"]
        if pd.isnull(date_str):
            continue

        deadline = pd.to_datetime(date_str).date()
        days_diff = (today - deadline).days

        if 0 <= days_diff <= 2:
            raw_phone = str(row["Unnamed: 2"]).strip()
            phone = ""
            if raw_phone.startswith("+7") and len(raw_phone) == 12:
                phone = raw_phone
            elif raw_phone.startswith("8") and len(raw_phone) == 11:
                phone = "+7" + raw_phone[1:]
            else:
                print(f"Неверный формат номера: {raw_phone}")
                continue

            message = (
                f"Здравствуйте! Это 'Актив Маркет'.\n"
                f"Напоминаем, что срок хранения Вашего залога подходит к концу.\n"
                f"Пожалуйста, посетите нас до {deadline.strftime('%d.%m.%Y')}, 23:00, чтобы продлить договор или выкупить имущество.\n"
                f"📍Адрес: Абулкаир хана, 84\n📞 +7 771 050 11 21"
            )

            now = datetime.now()
            send_hour = now.hour
            send_minute = now.minute + 2 if now.minute < 58 else now.minute

            print(f"Отправка сообщения на {phone}...")
            pywhatkit.sendwhatmsg(phone, message, send_hour, send_minute)
            time.sleep(10)

    except Exception as e:
        print(f"Ошибка в строке {index}: {e}")

input("Готово! Нажмите Enter для выхода.")
