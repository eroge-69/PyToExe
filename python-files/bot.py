import re
import time
import telebot,os
from telebot import types 
import subprocess
import requests
import psutil
import random  # تمت إضافة هذا السطر

version = "Vysi Swapper .."
global dir
dir = {}
class Initialization:
    def __init__(self) -> None:
        global dir 
        dir = {
            "bypass": {
                "Rs": "bypass/RsForBypass.txt",
                "bypass_session": "bypass/bypass_session.txt",
                "threads": "bypass/bypass_threads.txt",
                "switch": "bypass/Switch.txt",
            },
            "swapper": {
                "backup_session": "swapper/Backup_Session.txt",
                "main_session": "swapper/Main_Session.txt",
                "swapper_threads": "swapper/Swapper_threads.txt",
                "target_session": "swapper/Target_Session.txt",
                "backup_mode": "swapper/Backup_Mode.txt",
                "check_block": "swapper/Check_Block.txt",
            },
            "setting": {
                "proxy": "setting/proxy.txt",
                "webhook": "setting/webhook.txt",
                "bio": "setting/bio.txt",
                "sessions": "setting/sessions.txt",
                "auto_sessions": "setting/auto_sessions.txt",
                "swaps": "setting/swaps_tele_channel.txt",
                "Dis-Bypass Gif": "setting/Dis-Bypass Gif.txt",
                "Dis-Swap Gif": "setting/Dis-Swap Gif.txt",
            }
        }
        self.initialize_directories_and_files()
    def initialize_directories_and_files(self):
        for _, files in dir.items():
            os.makedirs(os.path.dirname(next(iter(files.values()))), exist_ok=True)
            
            self.create_files(files)
    def create_files(self, files):
        for key, file in files.items():
            if not os.path.exists(file): 
                with open(file, 'w') as f:
                    pass 
id = open("files\\id.txt").read().strip()
token = open("files\\token.txt").read().strip()
bot = telebot.TeleBot(token)
settings= False
bypass = False
swapper = False
AccountInfo = []
class Runner:
    def __init__(self):
        self.tool_processes = {}
    def start_tool(self, bot, message, tool_name):
        tasks = os.popen("tasklist").read()
        if tool_name not in tasks:
            try:
                tool_process = subprocess.Popen([tool_name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                time.sleep(1)

                self.tool_processes[tool_name] = tool_process
                
                if not self.is_process_running(tool_process):
                    bot.send_message(message.chat.id, f"そ {tool_name} has stopped")
                    del self.tool_processes[tool_name]
            except Exception as e:
                bot.send_message(message.chat.id, f"Error starting {tool_name}: {e}")
        else:
            bot.send_message(message.chat.id, f"そ {tool_name} is already running")

    def is_process_running(self, process):
        return process.poll() is None
    def stop_or_terminate(self, bot, message, tool_name):
        k=None
        procname_without_extension = tool_name.replace('.exe', '')
        for process in psutil.process_iter():
            if process.name() == tool_name:
                process.terminate()
                k = True
                if tool_name in self.tool_processes:
                    del self.tool_processes[tool_name]
                bot.send_message(message.chat.id, f"そ{procname_without_extension} stopped")
                break
        if k==None:
            bot.send_message(message.chat.id, f"そ {procname_without_extension} not running")
def format_message():
    message = f"""
    {version} 
"""
    return message
def generate_buttons(btn_names, markup):
    for buttons in btn_names:
        if isinstance(buttons, list):
            markup.row(*buttons)
        else:
            markup.row(buttons)
    return markup
def isMsg(message):
    return True
@bot.message_handler(func=isMsg)
def start(message):
    global settings,bypass,swapper
    try:
        text = message.text
        if message.chat.id == int(id):
            if "/start" == text:
                print(  
                    text
                )
                x = format_message()
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn_names = [["Swapper", "Bypass"],"Settings"]
                markup = generate_buttons(btn_names, markup)
                bot.send_animation(message.chat.id, "https://i.giphy.com/media/xULW8xIYmhTWW3Rv0Y/giphy.gif?cid=9b38fe91qzi1bz1te6bk9c076e4dmggre6n0hrp2nnj6ylm8&ep=v1_gifs_search&rid=giphy.gif&ct=g", caption=x, parse_mode='Markdown', reply_markup=markup)
            elif "Bypass" == text:
                bypass = True
                swapper = False
                settings = False
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn_names = [["Start Bypasser", "Close Bypasser"],["Bypass Session"], ["R/s Released", "Threads"],["Auto Sessions","Check Bypass"],["Back"]]  # تم تعديل هذا السطر
                markup = generate_buttons(btn_names, markup)
                bot.send_message(message.chat.id,"そ Select Mode .. ",reply_markup=markup)
            elif "Swapper" == text:
                swapper = True
                bypass = False
                settings = False
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn_names = [["Start Swapper", "Close Swapper"],["Main Session", "Target Session"], ["Threads","Backup Mode"], ["Check Block","Back"]]
                markup = generate_buttons(btn_names, markup)
                bot.send_message(message.chat.id,"そ Select Mode .. ",reply_markup=markup)
            elif "Settings" == text:
                settings = True
                bypass = False
                swapper = False
                markup = types.ReplyKeyboardMarkup(True)
                btn_names = [["Proxy", "Webhook"], ["Bio"],["SwapsChannel"],["Bypass Gif ","Swapper Gif"],"Back"]
                markup = generate_buttons(btn_names, markup)
                bot.send_message(message.chat.id,"そ Select Mode .. ",reply_markup=markup)
            else:
                if bypass:
                    bypass_handler(message)
                elif swapper:
                    swapper_handler(message)
                elif settings:
                    Settings_handler(message)
                else:
                    bot.reply_to(message,"そ Something went wrong... /start")
        else:
            bot.send_message(message.chat.id,"そ You are not allowed to use this bot Please Contact @vysiii ")
    except Exception as e:
        print(f"Error in start: {e}")

def bypass_handler(message):
    global bypass,swapper,settings
    text = message.text
    if "Start Bypasser" == text:
        if open(f"{dir['bypass']["threads"]}").read().strip() <= "1":
            runner.start_tool(bot, message, "b1.exe")
        elif open(f"{dir['bypass']["threads"]}").read().strip() <= "2":
            runner.start_tool(bot, message, "b2.exe")
        else:
            runner.start_tool(bot, message, "b3.exe")
    elif "Close Bypasser" == text:
        if open(f"{dir['bypass']["threads"]}").read().strip() <= "1":
            runner.stop_or_terminate(bot, message, "b1.exe")
        elif open(f"{dir['bypass']["threads"]}").read().strip() <= "2":
            runner.stop_or_terminate(bot, message, "b2.exe")
        else:
            runner.stop_or_terminate(bot, message, "b3.exe")
        if open(f"{dir['bypass']["switch"]}").read().strip() == "on":
            swapper = True
            bypass = False
            settings = False
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_names = [["Start Swapper", "Close Swapper"],["Main Session", "Target Session"], ["Threads","Backup Mode"], ["Check Block","Back"]]
            markup = generate_buttons(btn_names, markup)
            time.sleep(0.5)
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id + 1)
            bot.send_message(message.chat.id, "Bypass Closed Switch to Swapper..", reply_markup=markup)
    elif "Bypass Session" in text:
        bot.send_message(message.chat.id, "そ Set Bypass session.")
        bot.register_next_step_handler(message,grabberforall,dir["bypass"]["bypass_session"],"Bypass Session",True)
    elif "Threads" in text:
        bot.send_message(message.chat.id, "そ Set Bypass Threads \n Thread = 1 Normal Bypass \n Thread = 2 Secert Bypass \n Thread = +300 AutoBypass Need Sessions ")
        bot.register_next_step_handler(message,grabberforall,dir["bypass"]["threads"],"Threads",False,True)
    elif "R/s Released" in text:
        bot.send_message(message.chat.id, "そ Set R/s Released")
        bot.register_next_step_handler(message,grabberforall,dir["bypass"]["Rs"],"Rs",False,True)
    elif "Auto Sessions" in text:
        bot.send_message(message.chat.id, "そ Send Sessions file.")
        bot.register_next_step_handler(message, set_input, dir["setting"]["sessions"], "Sessions")
        time.sleep(10)
        sessionextracter()
    elif "Check Bypass" == text:  # تمت إضافة هذا الشرط
        bot.send_message(message.chat.id, "そ Send Session id You Want Check it Trusted :")
        bot.register_next_step_handler(message, handle_check_bypass)
    elif "Back" == text:
        bypass = False
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_names = [["Swapper", "Bypass"], "Settings"]
        markup = generate_buttons(btn_names, markup)
        bot.send_message(message.chat.id,"そ Select Mode .. ",reply_markup=markup)

# ======= الكود المضاف للتحقق من البايباس =======
def gen_user_agent():
    app_versions = ["285.0.0.25.109", "284.0.0.22.85", "283.0.0.16.103"]
    android_versions = ["11", "12", "13"]
    device_models = ["SM-G998B", "SM-G991B", "Pixel 5", "Pixel 4a"]
    device_makers = ["samsung", "Google"]
    return (
        f"Instagram {random.choice(app_versions)} Android ("
        f"{random.choice(android_versions)}/"
        f"{random.randint(1, 10)}; "
        f"{random.choice(device_models)}; "
        f"{random.choice(device_makers)}; en_US)"
    )

def get_usernames(sessionid):
    url = 'https://i.instagram.com/api/v1/accounts/current_user/?edit=true'
    headers = {
        'User-Agent': gen_user_agent(),
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'x-ig-app-id': '936619743392459'
    }
    cookies = {'sessionid': sessionid}
    try:
        resp = requests.get(url, headers=headers, cookies=cookies, timeout=8)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return None
    if data.get('message'):
        return None
    user = data.get('user', {})
    return user.get('username'), user.get('trusted_username')

def handle_check_bypass(message):
    sessionid = message.text.strip()
    result = get_usernames(sessionid)
    if not result:
        bot.send_message(message.chat.id, "そ Invalid session or error occurred.")
        return

    username, trusted_username = result
    username = username or ""
    trusted_username = trusted_username or ""

    response_msg = f"Username: @{username}\nTrusted Username: @{trusted_username}\n\n"
    
    if username.strip() == trusted_username.strip():
        response_msg += "そ This Username 14day Bypass it first."
    else:
        response_msg += "そ This Username not 14day You Can Swapped it Successfully."
    
    bot.send_message(message.chat.id, response_msg)
# ======= نهاية الكود المضاف =======

def swapper_handler(message):
    global swapper
    text = message.text
    if "Start Swapper" == text:
        if open(f"{dir['swapper']["backup_mode"]}").read().strip() == "on":
            runner.start_tool(bot, message, "swbackup.exe")
        else:
            runner.start_tool(bot, message, "swapper.exe")
    elif "Close Swapper" == text:
        if open(f"{dir['swapper']["backup_mode"]}").read().strip() == "on":
            runner.stop_or_terminate(bot, message, "swbackup.exe")
        else:
            runner.stop_or_terminate(bot, message, "swapper.exe")
    elif "Main Session" in text:
        bot.send_message(message.chat.id, "そ Set Main session.")
        bot.register_next_step_handler(message,grabberforall,dir["swapper"]["main_session"],"Main Session",True)
    elif "Target Session" in text:
        bot.send_message(message.chat.id, "そ Set Target session.")
        bot.register_next_step_handler(message,grabberforall,dir["swapper"]["target_session"],"Target Session",True)
    elif "Threads" in text:
        bot.send_message(message.chat.id, "そ Set Swapper Threads")
        bot.register_next_step_handler(message,grabberforall,dir["swapper"]["swapper_threads"],"Threads",False,True)
    elif "Backup Mode" == text:
        bot.send_message(message.chat.id, "そ Backup Mode on/off?")
        bot.register_next_step_handler(message,BackupMode)
    elif "Check Block" == text:
        bot.send_message(message.chat.id, "そ Check Block on/off?")
        bot.register_next_step_handler(message,grabberforall,dir["swapper"]["check_block"],"Check Block")
    elif "Back" == text:
        swapper = False
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_names = [["Swapper", "Bypass"],"Settings"]
        markup = generate_buttons(btn_names, markup)
        bot.send_message(message.chat.id,"そ Select Mode .. ",reply_markup=markup)
                
def Settings_handler(message):
    global settings
    text = message.text
    if "Proxy" in text:
        bot.send_message(message.chat.id, "そ Set Proxy .. ")
        bot.register_next_step_handler(message,grabberforall,dir["setting"]["proxy"],"Proxy")
    elif "Webhook" in text:
        bot.send_message(message.chat.id, "そ Set Webhook")
        bot.register_next_step_handler(message,grabberforall,dir["setting"]["webhook"],"Webhook")
    elif "Bio" in text: 
        bot.send_message(message.chat.id , "そ Set bio")
        bot.register_next_step_handler(message,grabberforall,dir["setting"]["bio"],"Bio")
    elif "SwapsChannel" in text:
        bot.send_message(message.chat.id, "そ Make This Bot @vysiiswappBot Admin and Send Your Channel ")
        bot.register_next_step_handler(message,grabberforall,dir["setting"]["swaps"],"SwapsChannel")
    elif "Bypass Gif" in text:
        bot.send_message(message.chat.id, "そ Send Gif Link .. ")
        bot.register_next_step_handler(message,grabberforall,dir["setting"]["Dis-Bypass Gif"],"Dis-Bypass Gif")
    elif "Swapper Gif" in text:
        bot.send_message(message.chat.id, "そ Send Gif Link .. ")
        bot.register_next_step_handler(message,grabberforall,dir["setting"]["Dis-Swap Gif"],"Dis-Swap Gif")
    elif "Back" in text:
        settings = False
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_names = [["Swapper", "Bypass"], "Settings"]
        markup = generate_buttons(btn_names, markup)
        bot.send_message(message.chat.id,"そ Select Mode .. ",reply_markup=markup)
                    
def grabber(session):
    global AccountInfo
    if check_session(session):
        x = get_fb_dtsg(session)
        AccountInfo.append(str(x))
        info_string = "|".join(str(i) for i in AccountInfo)
        return info_string
    else:
        return ""

def grabberforall(message,dir,what,isInfo = False,isDigit = False):
    if isInfo:
        session = message.text
        info = grabber(session)
        if info != "":
            set_oneline_input(info,dir,"@" + info.split("|")[4])
        else:
            bot.send_message(message.chat.id,"*そ Invalid session*",parse_mode='Markdown')
    elif isDigit:
        if message.text.isdigit():
            set_oneline_input(message.text,dir,what)
        else:
            bot.send_message(message.chat.id,"*そ Invalid number*",parse_mode='Markdown')
    else:
        set_oneline_input(message.text,dir,what)


def BackupMode(message):
    if "on" == message.text.lower():
        set_oneline_input("on",dir["swapper"]["backup_mode"],"Backup Mode")
        bot.send_message(message.chat.id,"*そ Backup Mode on.\nSend Session*",parse_mode='Markdown')
        bot.register_next_step_handler(message,grabberforall,dir["swapper"]["backup_session"],"Backup Sessions",True)
    elif "off" == message.text.lower():
        set_oneline_input("off",dir["swapper"]["backup_mode"],"Backup Mode")
        bot.send_message(message.chat.id,"*そ Backup Mode off.*",parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id,"*そ Invalid input*",parse_mode='Markdown')

def set_oneline_input(value, filename = str,key = str):
    with open(filename,'w') as file:
        file.write(f"{value}")
    bot.send_message(id,f"*そ {key} Done.*",parse_mode='Markdown')  
    
def set_input(message, filename, key):
    with open(filename, 'w') as f:
        f.write('')
    
    content = ''
    if message.text:
        content = message.text
    elif message.document:
        content = document(message)
    
    # تقسيم المحتوى إلى أسطر
    lines = content.split('\n')
    
    # كتابة كل سطر في الملف
    with open(filename, 'a') as f:
        for line in lines:
            line = line.strip()
            if line:
                f.write(line + '\n')
    
    bot.send_message(message.chat.id, f"そ {key} set.")  
def document(message: types.Message) -> str:
    if message.document.mime_type == 'text/plain':
        File = requests.get('https://api.telegram.org/bot{0}/getFile?file_id={1}'.format(token, message.document.file_id)).json()['result']['file_path']
        inside_file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, File))
        return inside_file.text
    return 'bruh'
def check_session(session : str):
    global AccountInfo
    url = "https://i.instagram.com/api/v1/accounts/current_user/?edit=true"
    headers = {
        "User-Agent": "Instagram 275.0.0.27.98 Android",
        "Cookie":"sessionid=" + session,
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    response = requests.get(url,headers=headers)
    if response.status_code == 200 and "fbid_v2" in response.text:
        user_data = response.json().get("user", {})
        username = user_data.get("username", "")
        trusted = user_data.get("trusted_username", "")
        fbid = str(user_data.get("fbid_v2", ""))
        email = user_data.get("email", "")
        phone = user_data.get("phone_number", "")
        AccountInfo = [session,fbid,email,phone,username,trusted]
        return True
    else:
        return False
def sessionextracter():
    tasks = os.popen("tasklist").read()
    if "sessionextracter.exe" not in tasks:
        subprocess.Popen(["sessionextracter.exe"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        bot.send_message(id,"Starting sessionextracter process.")
def get_fb_dtsg(session):
    r2 = requests.Session()
    url = "https://accountscenter.instagram.com/?entry_point=app_settings"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)frel Safari/537.36",
        "Cookie": "sessionid=" + session,
    }
    try :
        r = r2.get(url, headers=headers)
    except Exception as e:
        bot.send_message(id,f"[X] can't Get fb_dtsg value")
        return
    if "DTSGInitData" in r.text:
        match = re.search(r'\["DTSGInitData",\[\],.*?"token":"([^"]+)"', r.text)
        if match:
            fb_dtsg = match.group(1)
            return fb_dtsg
    else:
        bot.send_message(id,f"[X] can't Get fb_dtsg value")
        return
def check_tools_status(message):
    excluded_files = [
        "setting/auto_sessions.txt", "setting/sessions.txt"
    ]
    settings_message = "\nSettings Files:\n"
    for file_name, file_path in dir["setting"].items():
        if file_path in excluded_files:
            continue
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    settings_message += f"{file_name}: {f.read().strip()}\n"
            except Exception as e:
                settings_message += f"{file_name}: Error reading file: {e}\n"
        else:
            settings_message += f"{file_name}: File not found.\n"
    if settings_message:
        bot.send_message(message.chat.id, settings_message)
if __name__ == "__main__":
    Initialization()
    runner = Runner()
    while True:
        try:
            bot.polling(True)
        except Exception as e:
            print(f"Error in polling: {e}")
