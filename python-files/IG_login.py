
try:
    import string , random , re,base64 , os
    from uuid import uuid4
    from requests import Session
    from colorama import Fore , Style
    from time import time
except Exception as e:
    print(e)
    input()
    os._exit(0)
def set_cmd_window_size(width, height):
    os.system(f'mode con: cols={width} lines={height}')
set_cmd_window_size(140, 25)
Purple="\033[1;35m"
def LOGO():
    os.system('cls' if os.name == 'nt' else 'clear')
    return fr"""                                                                                     
{Fore.BLUE}
  .--.--.                                                                                      
 /  /    '.                                    ,--,                         ,--,         ,---, 
|  :  /`. /                                  ,--.'|    ,---.        ,---, ,--.'|       ,---.'| 
;  |  |--`              .--.--.    .--.--.   |  |,    '   ,'\   ,-+-. /  ||  |,        |   | : 
|  :  ;_       ,---.   /  /    '  /  /    '  `--'_   /   /   | ,--.'|'   |`--'_        |   | | 
 \  \    `.   /     \ |  :  /`./ |  :  /`./  ,' ,'| .   ; ,. :|   |  ,"' |,' ,'|     ,--.__| | 
  `----.   \ /    /  ||  :  ;_   |  :  ;_    '  | | '   | |: :|   | /  | |'  | |    /   ,'   | 
  __ \  \  |.    ' / | \  \    `. \  \    `. |  | : '   | .; :|   | |  | ||  | :   .   '  /  | 
 /  /`--'  /'   ;   /|  `----.   \ `----.   \'  : |_|   :    ||   | |  |/ '  : |__ '   ; |:  | 
'--'.     / '   |  / | /  /`--'  //  /`--'  /|  | '.'\   \  / |   | |--'  |  | '.'||   | '/  ' 
  `--'---'  |   :    |'--'.     /'--'.     / ;  :    ;`----'  |   |/      ;  :    ;|   :    :| 
             \   \  /   `--'---'   `--'---'  |  ,   /         '---'       |  ,   /  \   \  /   
              `----'                          ---`-'                       ---`-'    `----'    
                    By Joker @vv1ck | @221298
"""
class IG_LOGIN:
    def __init__(self):
        self.QTR = Session()
        self.tim = time()
        print(LOGO())
        self.info_Device()
        self.login()
    # هنا يجب نسخ جميع الدوال الأخرى كما هي
IG_LOGIN()
