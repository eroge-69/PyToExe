import os, csv, smtplib
from datetime import datetime, date, time, timedelta
from email.message import EmailMessage

counterFiles = os.listdir('.')
yesterday = datetime.strftime(datetime.now() - timedelta(1), '%d-%m-%Y')
for f in counterFiles:
    if yesterday in f:
        counterFile = f
with open(counterFile, 'rb') as f:
    file_data = f.read()
    file_name = f.name
# Работа с почтой
sender = 'admin@5planet.com'
mailPassword = 'hfodgmqnsetgctvl'
# Адреса  отправки почты (receivers.txt)
with open('receivers.txt', 'r') as f:
    receiverList = [i for i in f.read().split()]
#Заголовок письма
for m in receiverList:
    msg = EmailMessage()
    msg['Subject'] = '📑 Данные счетчиков за ' + yesterday
    msg['From'] = sender
    msg['To'] = m
    msg.set_content(
      #Подпись письма
        ' 📑 Данные счетчиков за (' + yesterday + ')\n\n--- \nС уважением,\nДмитрий Нестеренко.\nСистемный администратор МФТК "Пять Планет"')
    msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
    with smtplib.SMTP_SSL('smtp.yandex.ru', 465) as smtp:
        smtp.login(sender, mailPassword)
        smtp.send_message(msg)
print('Done!')
print('Готово!')
time.sleep(2)
print('The Email was sent successfully!')
print('Электронное письмо было успешно отправлено!')
time.sleep(2)
print('OK!')