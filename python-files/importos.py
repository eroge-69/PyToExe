import pyautogui
import webbrowser
import random
import string

pyautogui.PAUSE = 0.2
pyautogui.FAILSAFE = True

webbrowser.open_new('https://vak-sms.com/getNumbers/')

pyautogui.moveTo(535, 481, 5)
pyautogui.click(button='left')

#  копировать номер телефона
pyautogui.moveTo(1033, 529, 2)
pyautogui.click(button='left')
pyautogui.moveTo(1033, 529, 2)

# открыть пакет
webbrowser.open_new('https://id.x5.ru/auth/realms/ssox5id/protocol/openid-connect/auth?client_id=pkce_web_subscription&redirect_uri=https%3A%2F%2Fx5paket.ru%2Ffastbuy_promo&state=7d0c09d0-a278-456d-9b13-7052d97d6dcc&response_mode=fragment&response_type=code&scope=openid&nonce=5c6e1133-3f49-401e-8bef-9a1dbb421be6&ui_locales=ru&code_challenge=ABrOp_icemiJUcJISxOksbD8o_F5iNybRgPIfYNGVeQ&code_challenge_method=S256')

# вести номер телефона
pyautogui.moveTo(934, 564, 1)
pyautogui.click(button='left')
pyautogui.hotkey('ctrl', 'v') 
pyautogui.press('enter') 

pyautogui.hotkey('ctrl', '2') 

pyautogui.moveTo(1417, 532, 2)
pyautogui.hotkey('F5')
pyautogui.hotkey('F5') 
pyautogui.hotkey('F5') 
pyautogui.hotkey('F5') 
pyautogui.hotkey('F5') 
pyautogui.hotkey('F5') 
pyautogui.hotkey('F5') 
pyautogui.hotkey('F5') 
pyautogui.hotkey('F5') 
pyautogui.hotkey('F5')  
pyautogui.click(button='left')
pyautogui.moveTo(1417, 532, 2)
pyautogui.hotkey('ctrl', '3') 

pyautogui.moveTo(950, 631, 1)
pyautogui.hotkey('ctrl', 'v') 

# регистрация 
pyautogui.moveTo(804, 333, 2)
pyautogui.click(button='left')
pyautogui.write('Александр')
pyautogui.moveTo(804, 333, 2)

pyautogui.moveTo(804, 448, 2)
pyautogui.click(button='left')
pyautogui.write('Иванов')
pyautogui.moveTo(804, 448, 2)

pyautogui.moveTo(804, 539, 2)
pyautogui.click(button='left')
pyautogui.write("06062004")
pyautogui.moveTo(804, 539, 2)

pyautogui.moveTo(804, 654, 2)
pyautogui.click(button='left')
def random_char(char_num):
       return ''.join(random.choice(string.ascii_letters) for _ in range(char_num))
pyautogui.write(random_char(10)+"@gmail.com")
pyautogui.moveTo(804, 654, 2)

pyautogui.moveTo(804, 734, 2)
pyautogui.click(button='left')
pyautogui.moveTo(804, 734, 2)

pyautogui.moveTo(804, 739, 2)
pyautogui.click(button='left')
pyautogui.moveTo(804, 739, 2)

pyautogui.moveTo(804, 923, 2)
pyautogui.click(button='left')
pyautogui.moveTo(804, 923, 2)

pyautogui.scroll(-10)  # scroll down 10 "clicks"

pyautogui.moveTo(933, 892, 5)


print('end')
