import pandas as pd
from datetime import datetime
import win32com.client as win32

# === НАСТРОЙКИ ===
excel_file = r"\\axruse1srv1\Fileserver\Кафета\Кафета-Срок на годност.xlsx"   # път до файла
mail_to = ["aytach.berov@technomarket.bg"]              # получатели на имейлите
today = datetime.today().date()

# === ЧЕТЕНЕ НА EXCEL ===
df = pd.read_excel(excel_file)

# Очакваме колони: 'Артикулен номер', 'Име на артикула', 'Баркод', 'Срок на годност'
for i, row in df.iterrows():
    artikul = str(row['Артикулен номер'])
    ime = str(row['Име на артикула'])
    barkod = str(row['Баркод'])
    expiry_date = pd.to_datetime(row['Срок на годност']).date()
    days_left = (expiry_date - today).days

    subject = None
    body = None

    if days_left == 30:
        subject = f"Напомняне: {ime} ({artikul}) изтича след 1 месец"
        body = f"Продукт: {ime}\nАртикулен номер: {artikul}\nБаркод: {barkod}\nСрок на годност: {expiry_date}\n\nОстава 1 месец."
    elif days_left == 7:
        subject = f"Напомняне: {ime} ({artikul}) изтича след 1 седмица"
        body = f"Продукт: {ime}\nАртикулен номер: {artikul}\nБаркод: {barkod}\nСрок на годност: {expiry_date}\n\nОстава 1 седмица."
    elif days_left < 0:
        subject = f"ВНИМАНИЕ: {ime} ({artikul}) е с изтекъл срок"
        body = f"Продукт: {ime}\nАртикулен номер: {artikul}\nБаркод: {barkod}\nСрок на годност: {expiry_date}\n\n!!! СРОКЪТ Е ИЗТЕКЪЛ !!!"

    if subject and body:
        # Изпращане на имейл през Outlook
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.Subject = subject
        mail.Body = body
        for recipient in mail_to:
            mail.Recipients.Add(recipient)
        mail.Send()
        print(f"Изпратен имейл за {ime}")
