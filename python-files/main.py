import telebot
from telebot import types

# Импортируем нужный объект из библиотеки 
from docxtpl import DocxTemplate
from docx2pdf import convert
from time import sleep
from datetime import datetime
# Import PdfReader and PdfWriter modules from the pypdf library
from pypdf import PdfReader, PdfWriter

token ="7810011038:AAGEAOc_9zmJcK1CrmFxuR_T3P6ARschR9k"

bot = telebot.TeleBot(token)

admin = "6744574166"
list_chat = ["6744574166","886675987"]
mes_chat_temp = ''
@bot.message_handler(commands=["start"])
def start_message(message):
    global list_chat,mes_chat_temp
    if str(message.chat.id) not in list_chat:
        bot.send_message(message.chat.id,"Ты добавлен")
        print(message.chat.id, message.from_user.username)
        mes_chat_temp = message.chat.id
        keyboard = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text='Да', callback_data='button1')
        button2 = types.InlineKeyboardButton(text='Нет', callback_data='button2')
        keyboard.add(button1, button2)
        text = f"Хотите добавить @{message.from_user.username} в белый список?"
        bot.send_message(admin, text, reply_markup=keyboard)

data = []

@bot.message_handler(commands=["new"])
def new(message):
    global data
    if str(message.chat.id) in list_chat:
        data = []
        msg = bot.send_message(message.chat.id,"Введите номер телефона получателя")
        bot.register_next_step_handler(msg,nomer_tel)
def nomer_tel(message):
    global data
    nomer = message.text
    nomer = nomer[:-4:] + '-' + nomer[-4::]
    nomer = nomer[:-2:] + '-' + nomer[-2::]
    nomer = nomer[:5:] + ') ' + nomer[5::]
    nomer = nomer[:2:] + ' (' + nomer[2::]
    data.append(nomer)
    msg = bot.send_message(message.chat.id,"Введите ФИО получателя")
    bot.register_next_step_handler(msg,fio_receiver)
def fio_receiver(message):
    global data
    data.append(message.text)
    msg = bot.send_message(message.chat.id,"Введите банк получателя")
    bot.register_next_step_handler(msg,bank_receiver)
def bank_receiver(message):
    global data
    data.append(message.text)
    msg = bot.send_message(message.chat.id,"Введите сумму отправки")
    bot.register_next_step_handler(msg,summa_otprav)

def summa_otprav(message):
    global data
    data.append(message.text)
    msg = bot.send_message(message.chat.id,"Введите ФИО отправителя")
    bot.register_next_step_handler(msg,fio_otprav)
def fio_otprav(message):
    global data
    if message.text == "stop":
        file_name = create_1()
        with open(file_name, 'rb') as doc:
            bot.send_document(message.chat.id, document=doc)
    else:
        data.append(message.text)
        msg = bot.send_message(message.chat.id,"Введите номер счета отправителя")
        bot.register_next_step_handler(msg,chet_otprav)
def chet_otprav(message):
    global data
    data.append(message.text)
    file_name = create_2()
    with open(file_name, 'rb') as doc:
        bot.send_document(message.chat.id, document=doc)
    

def create_1():
    global data
    # Загрузка шаблона
    doc = DocxTemplate("copy_chablon.docx")

    t = datetime.now()
    date = t.strftime("%d.%m.%Y")
    date2 = t.strftime("%d_%m_%Y")
    time = t.strftime("%H:%M")
    time2 = t.strftime("%H_%M")
    print(date,time)
    context = {
            'receiver': data[1],
            'data' : date,
            'time' : time,
            'sh' : '5916',
            'FIO' : 'Виталий Сергеевич Ш.',
            'nomer' : data[0],
            'bank' : data[2],
            'money' : data[3]
        }
    print(data[1])
    print(date)
    print(time)
    print(data[0])
    print(data[2])
    print(data[3])
    # Заполнение шаблона данными
    doc.render(context)

    # Сохранение документа
    doc.save("новый_документ2.docx")
    sleep(1)
    convert("./новый_документ2.docx", f"./document_{date2}_{time2}.pdf")


    # Create a PdfReader object and load the input PDF file
    reader = PdfReader(f"./document_{date2}_{time2}.pdf")
    reader2 = PdfReader(f"./document_{date2}_{time2}.pdf")
    # Creating a new PDF writer object using PdfWriter
    writer = PdfWriter()
    meta = reader2.metadata
    # Adding all pages from the input PDF to the new writer
    for page in reader.pages:
        writer.add_page(page)

    # Format the current date and time for the metadata
    # UTC time offset (optional, adjust as needed)
    utc_time = "+00'00'"

    # Current date and time formatted for metadata
    time = meta.creation_date.strftime(f"D\072%Y%m%d%H%M%S{utc_time}")  
    # Writing new metadata to the PDF
    writer.add_metadata(
        {
            "/Author": "",    # Author information
            "/Producer": "",       # Software used to produce the PDF
            "/Title": "Чек-PDF",                   # Document title
            "/Subject": "",               # Document subject
            "/Keywords": "",             # Keywords associated with the document
            "/CreationDate": time,               # Date and time the document was created
            "/ModDate": "",                    # Date and time the document was last modified
            "/Creator": "",               # Application that created the original document
        }
    )

    # Save the new PDF to a file
    with open(f"./document_{date2}_{time2}.pdf", "wb") as f:
        writer.write(f)
    return f"./document_{date2}_{time2}.pdf"

def create_2():
    global data
    # Загрузка шаблона
    doc = DocxTemplate("copy_chablon.docx")

    t = datetime.now()
    date = t.strftime("%d.%m.%Y")
    date2 = t.strftime("%d_%m_%Y")
    time = t.strftime("%H:%M")
    time2 = t.strftime("%H_%M")
    print(date,time)
    context = {
            'receiver': data[1],
            'data' : date,
            'time' : time,
            'sh' : data[5],
            'FIO' : data[4],
            'nomer' : data[0],
            'bank' : data[2],
            'money' : data[3]
        }
    print(data[1])
    print(date)
    print(time)
    print(data[5])
    print(data[4])
    print(data[0])
    print(data[2])
    print(data[3])
    # Заполнение шаблона данными
    doc.render(context)

    # Сохранение документа
    doc.save("новый_документ2.docx")
    sleep(1)
    convert("./новый_документ2.docx", f"./document_{date2}_{time2}.pdf")


    # Create a PdfReader object and load the input PDF file
    reader = PdfReader(f"./document_{date2}_{time2}.pdf")
    reader2 = PdfReader(f"./document_{date2}_{time2}.pdf")
    # Creating a new PDF writer object using PdfWriter
    writer = PdfWriter()
    meta = reader2.metadata

    # Adding all pages from the input PDF to the new writer
    for page in reader.pages:
        writer.add_page(page)

    # Format the current date and time for the metadata
    # UTC time offset (optional, adjust as needed)
    utc_time = "+00'00'"

    # Current date and time formatted for metadata
    time = meta.creation_date.strftime(f"D\072%Y%m%d%H%M%S{utc_time}")  

    # Writing new metadata to the PDF
    writer.add_metadata(
        {
            "/Author": "",    # Author information
            "/Producer": "",       # Software used to produce the PDF
            "/Title": "Чек-PDF",                   # Document title
            "/Subject": "",               # Document subject
            "/Keywords": "",             # Keywords associated with the document
            "/CreationDate": time,               # Date and time the document was created
            "/ModDate": "",                    # Date and time the document was last modified
            "/Creator": "",               # Application that created the original document
        }
    )

    # Save the new PDF to a file
    with open(f"./document_{date2}_{time2}.pdf", "wb") as f:
        writer.write(f)
    return f"./document_{date2}_{time2}.pdf"

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call: types.CallbackQuery) -> None:
    global list_chat,mes_chat_temp
    """
    Обработка нажатий на инлайн кнопки.
    """
    if call.data == 'button1':
        bot.answer_callback_query(call.id, 'Вы добавили в белый список')
        list_chat.append(str(mes_chat_temp))
        print(list_chat)
    elif call.data == 'button2':
        bot.answer_callback_query(call.id, 'Вы не добавили белый список')

bot.infinity_polling()
