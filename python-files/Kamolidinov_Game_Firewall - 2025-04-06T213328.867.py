
import psutil
import time
import requests
from bs4 import BeautifulSoup

# O'yin ro'yxatiga o'yinlar qo'shish
games_keywords = ['game', 'gaming', 'play', 'download', 'cs1.6', 'tlauncher']

# Parolni aniqlash
correct_password = "23-maktab0123"

# O'yin ekanligini aniqlash uchun internetdan qidirish
def is_game(program_name):
    try:
        # Google qidiruviga so'rov yuborish
        search_url = f"https://www.google.com/search?q={program_name}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(search_url, headers=headers)
        
        # Sahifa ma'lumotlarini olish
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Qidiruv natijalarida o'yin haqidagi ma'lumotlarni aniqlash
        for item in soup.find_all('h3'):
            if any(keyword in item.text.lower() for keyword in games_keywords):
                return True
        return False
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        return False

# Parolni so'rash
def ask_password():
    password = input("Parolni kiriting: ")
    if password == correct_password:
        print("Parol to'g'ri, o'yinga kirish mumkin.")
    else:
        print("Parol noto'g'ri. Dastur yopiladi.")
        exit()

# Dastur ishlayotganini tekshirish
def check_running_processes():
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            program_name = proc.info['name'].lower()
            if 'cs1.6' in program_name or 'tlauncher' in program_name:
                print(f"O'yin {proc.info['name']} ishlamoqda.")
                ask_password()
            elif is_game(program_name):
                print(f"O'yin {proc.info['name']} ishlamoqda.")
                ask_password()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

# Dastur ishga tushadi
def main():
    while True:
        check_running_processes()  # O'yinlarni tekshirish
        time.sleep(5)  # 5 soniya kutish va yana tekshirish

if __name__ == "__main__":
    main()
