import telebot
import os
import pyscreenshot
from datetime import date
from ctypes import cast, POINTER
import comtypes
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import windll
from ctypes import c_int
from ctypes import c_uint
from ctypes import c_ulong
from ctypes import POINTER
from ctypes import byref
bot = telebot.TeleBot('8177916846:AAEJthypcagQOEiGw6w0R68ttnJax3r-DXc')
UserID = 6208760999

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "Привет! Я бот, который может управлять компьютером! 💻\n"
        "Доступные команды:\n"
        "./restart — выключить ПК\n"
        "./shutdown — перезагрузить ПК\n"
        "./msg <текст> — высветить сообщение\n"
        "./cmd <команда> — выполнить команду\n"
        "./screenshot — сделать скриншот\n"
        "./sound <число> — изменить уровень звука и\n./sound — узнать уровень звука\n"
        "./bsod — вызывает синий экран 🟦💀!\n\n"
        "⚠️ Только для администратора!"
    )

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.from_user.id == UserID:
        if message.text == "./restart":
            bot.send_message(message.from_user.id, "Перезагружаю компьютер!")
            os.system("shutdown /r /t 0")

        elif message.text == "./shutdown":
            bot.send_message(message.from_user.id, "Выключаю компьютер!")
            os.system("shutdown /s /t 0")

        elif "./msg" in message.text:
            msgToUser = message.text.split('./msg ', maxsplit=2)
            bot.send_message(message.from_user.id, "Отправляю сообщение на компьютер!")
            os.system(f'msg * "{msgToUser[1]}"')

        elif message.text == "./bsod":
            bot.send_message(message.from_user.id, "Вызываю синий экран!🟦💀")
            nullptr = POINTER(c_int)()
            windll.ntdll.RtlAdjustPrivilege(19, 1, 0, byref(c_int()))
            windll.ntdll.NtRaiseHardError(0xC000007B, 0, nullptr, nullptr, 6, byref(c_uint()))
            
        elif "./cmd" in message.text:
            CommandAct = message.text.split('./cmd ', maxsplit=2)
            bot.send_message(message.from_user.id, "Выполняю команду!")
            os.system(f'{CommandAct[1]}')

        elif message.text == "./screenshot":
            current_date = date.today()
            ImagePath = f'C:\\Users\\АВЕЛЬ\\Pictures\\Screenshots\\Screenshot{current_date}.png'
            bot.send_message(message.from_user.id, "Делаю скриншот!")
            imagetotake = pyscreenshot.grab()
            imagetotake.save(ImagePath)
            bot.send_photo(message.chat.id, open(ImagePath, 'rb'), caption="Скриншот экрана! 📸")
            os.remove(ImagePath)

        elif message.text == "./sound":
            comtypes.CoInitialize()
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                currentvolume = volume.GetMasterVolumeLevelScalar()
                bot.send_message(message.from_user.id, f"Уровень звука равен {round(currentvolume * 100)}%.")
            finally:
                comtypes.CoUninitialize()

        elif "./sound" in message.text:
            try:
                comtypes.CoInitialize()
                SetVolTo = round(float((message.text.split()[1])))
                SetVolTo = max(0, min(100, SetVolTo))
                Vol2 = cast(AudioUtilities.GetSpeakers().Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None),
                    POINTER(IAudioEndpointVolume))
                Vol2.SetMasterVolumeLevelScalar(SetVolTo/100, None)
                bot.send_message(message.from_user.id, f"🔊 Громкость установлена: {SetVolTo}%")
            except (ValueError, IndexError):
                pass     
            finally:
                comtypes.CoUninitialize()
        else:
            bot.send_message(message.from_user.id, f"Нет такой команды, пиши /start")
    else:
        bot.send_message(message.from_user.id, "Вам недоступно!🤔🫡\n")

bot.polling(none_stop=True, interval=0)



