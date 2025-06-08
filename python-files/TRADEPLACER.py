# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: tradeplacer.py
# Bytecode version: 3.10.0rc2 (3439)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

import time
import pandas as pd
from datetime import datetime, timedelta
import os
import time
import pandas as pd
import sys
import datetime as dt
import colorama
from colorama import Fore, Back, Style
import json
import time
import numpy as np
import os
import undetected_chromedriver as uc
from quotexpy import Quotex
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
bot_created_date = dt.date(2024, 11, 10)
current_date = dt.date.today()
time_difference = current_date - bot_created_date
if time_difference.days >= 30000000:
    print('License expired')
    sys.exit()
import colorama
from colorama import Fore, Back, Style
colorama.init()
bot_boundary = f'{Fore.CYAN}{Style.BRIGHT}*******************************************************************\n* {Fore.WHITE}                                                                {Fore.CYAN}*\n* {Fore.WHITE}            Welcome to {Fore.GREEN}Auto Trading Bot{Fore.WHITE}                         {Fore.CYAN}*\n* {Fore.WHITE}                                                                {Fore.CYAN}*\n* {Fore.WHITE}  Contact us on {Fore.MAGENTA}Telegram{Fore.WHITE} to implement any strategy on your bot  {Fore.CYAN}*\n* {Fore.WHITE}                                                                {Fore.CYAN}*\n*******************************************************************{Style.RESET_ALL}'
print(bot_boundary)
option = Options()
option.add_argument('--disable-extensions')
option.add_argument('--disable-notifications')
option.add_argument('--window-size=720,720')
option.binary_location = 'Chrome\\chrome.exe'
d = DesiredCapabilities.CHROME
d['goog:loggingPrefs'] = {'performance': 'ALL'}
driver = uc.Chrome(driver_executable_path='chromedriver\\chromedriver.exe', options=option, desired_capabilities=d)
driver.delete_all_cookies()
driver.get('https://qxbroker.com/en/sign-in')
wait = WebDriverWait(driver, 10)
email_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/bdi/div/div/div[2]/div/div[2]/div[3]/form/div[1]/input')))
entered_email = input('Enter your email: ')
if entered_email not in ['kuruba.arun@gmail.com', 'shimul5522hasan@gmail.com', 'junaidabdultashwin@gmail.com', 'alkaium33421@gmail.com', 'hamzarashid1914@hotmail.com']:
    print('inccorrect email. Exiting.')
    time.sleep(5)
    sys.exit()
email_input.send_keys(entered_email)
pass_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/bdi/div/div/div[2]/div/div[2]/div[3]/form/div[2]/input')))
password = input('Enter your password: ')
pass_input.send_keys(password)
sign_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/bdi/div/div/div[2]/div/div[2]/div[3]/form/button')))
sign_button.click()
ssid = None
while True:
    if ssid is not None:
        break
    for entry in driver.get_log('performance'):
        try:
            shell = entry['message']
            payloadData = json.loads(shell)['message']['params']['response']['payloadData']
            if 'auth' in shell and 'session' in shell:
                ssid = payloadData
        except:
            continue
    time.sleep(1)
_ga_L4T5GBPFHJ = None
_ga = None
lang = None
nas = None
z = None
_vid_t = None
__vid_l3 = None
__cf_bm = None
cookies = driver.get_cookies()
for cookie in cookies:
    if cookie['name'] == '_ga_L4T5GBPFHJ':
        _ga_L4T5GBPFHJ = cookie['value']
    elif cookie['name'] == '_ga':
        _ga = cookie['value']
    elif cookie['name'] == 'lang':
        lang = cookie['value']
    elif cookie['name'] == 'nas':
        nas = cookie['value']
    elif cookie['name'] == 'z':
        z = cookie['value']
    elif cookie['name'] == '_vid_t':
        _vid_t = cookie['value']
    elif cookie['name'] == '__vid_l3':
        __vid_l3 = cookie['value']
    elif cookie['name'] == '__cf_bm':
        __cf_bm = cookie['value']
weboscket_cookie = f'referer=https%3A%2F%2Fwww.google.com%2F; _ga_L4T5GBPFHJ={_ga_L4T5GBPFHJ}; _ga={_ga}; lang={lang}; nas={nas}; z={z}; _vid_t={_vid_t}; __vid_l3={__vid_l3}; __cf_bm={__cf_bm}'
user_agent = driver.execute_script('return navigator.userAgent;')
host = driver.execute_script('return window.location.host;')
if ssid:
    driver.quit()
qx_api = Quotex(set_ssid=ssid, host=host, user_agent=user_agent, weboscket_cookie=weboscket_cookie)
check_connect, message = qx_api.connect()
if check_connect == True:
    print(Fore.GREEN + 'Log In Successful.' + Style.RESET_ALL)
else:
    print(Fore.RED + 'Log In failed.' + Style.RESET_ALL)
print()
trade_duration = 300
amounts = []
print(f'{Fore.BLUE}Trading type\n{Style.RESET_ALL}1. Compounding\n2. Martingale')
trading_type = int(input('Enter your trading type(1/2): '))
print()
if trading_type == 1:
    compounding = int(input('Enter No. of compounding steps: '))
    for i in range(compounding):
        amount = int(input(f'Enter Amount {i + 1}: '))
        amounts.append(amount)
elif trading_type == 2:
    martingale = int(input('Enter No. of Martingale steps: '))
    for i in range(martingale):
        amount = int(input(f'Enter Amount {i + 1}: '))
        amounts.append(amount)
steps = len(amounts)
mart = 0
co = 0
print()
account = input('Which account you want to use(P/R): ')
account = account.lower()
if account == 'r':
    qx_api.change_balance('REAL')
    print(f'You selecr real account, your balance is {Fore.WHITE}{qx_api.get_balance()}{Style.RESET_ALL}')
elif account == 'p':
    qx_api.change_balance('PRACTICE')
    print(f'You selecr practice account, your balance is {Fore.WHITE}{qx_api.get_balance()}{Style.RESET_ALL}')
balance = qx_api.get_balance()
now_balance = balance
new_balance = now_balance
print()
profit = int(input(f'{Fore.GREEN}Enter your profit target: {Style.RESET_ALL}'))
stop_loss = int(input(f'{Fore.RED}Enter your loss target: {Style.RESET_ALL}'))
stop_loss = -abs(stop_loss)
print()
overallprofit = 0
percentage = int(input('Select assets with a minimum return percentage of: '))
print(f'{Fore.YELLOW} Bot start.....{Style.RESET_ALL}')
print()
import sys
if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(sys.executable)
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
file_path = os.path.join(script_dir, 'trades.txt')
trades_df = pd.read_csv(file_path, sep=', ')
print('List of Signals:')
print(trades_df)
print('==================')
if trading_type == 1:
    for index, trade in trades_df.iterrows():
        currency = trade['currency']
        direction = trade['direction']
        time_str = trade['time']
        current_time = datetime.now()
        time_obj = time.strptime(time_str, '%H:%M')
        time_seconds = time_obj.tm_hour * 3600 + time_obj.tm_min * 60
        current_seconds = current_time.hour * 3600 + current_time.minute * 60 + current_time.second
        time_difference = time_seconds - current_seconds
        if time_difference < 0:
            print(f'Signal {index + 1} is in the past. Skipping...')
            print('==================')
            continue
        print(f'Signal {index + 1} is in the future. Waiting for {time_difference} seconds...')
        for seconds_remaining in range(time_difference, 0, -1):
            print(f'Next Signal in {seconds_remaining} seconds', end='\r')
            time.sleep(1)
        print(currency)
        asset_data = qx_api.get_payment().get(currency)
        if asset_data and asset_data['open'] and (asset_data['payment'] >= 85):
            c, buy_info = qx_api.buy(currency, amounts[co], direction, trade_duration)
            if 'id' in buy_info.keys():
                print(f'Trade {index + 1}: {direction} {currency} placed successfully!')
                print('result', qx_api.check_win(buy_info['id']))
                result = qx_api.check_win(buy_info['id'])
                if result > 0:
                    overallprofit = overallprofit + result
                    if overallprofit >= profit:
                        print(f'{Fore.GREEN}Profit target hit!{Style.RESET_ALL}')
                        time.sleep(10)
                        qx_api.close()
                        sys.exit()
                    co += 1
                    if co == steps:
                        co = 0
                elif result < 0:
                    overallprofit = overallprofit + result
                    if overallprofit >= profit:
                        print(f'{Fore.GREEN}Profit target hit!{Style.RESET_ALL}')
                        time.sleep(10)
                        qx_api.close()
                        sys.exit()
                    co = 0
                else:
                    overallprofit = overallprofit
                    co = co
        else:
            print('SKIP.. LOW RETURN')
elif trading_type == 2:
    for index, trade in trades_df.iterrows():
        currency = trade['currency']
        direction = trade['direction']
        time_str = trade['time']
        current_time = datetime.now()
        time_obj = time.strptime(time_str, '%H:%M')
        time_seconds = time_obj.tm_hour * 3600 + time_obj.tm_min * 60
        current_seconds = current_time.hour * 3600 + current_time.minute * 60 + current_time.second
        time_difference = time_seconds - current_seconds
        if time_difference < 0:
            print(f'Signal {index + 1} is in the past. Skipping...')
            print('==================')
            continue
        print(f'Signal {index + 1} is in the future. Waiting for {time_difference} seconds...')
        for seconds_remaining in range(time_difference, 0, -1):
            print(f'Next Signal in {seconds_remaining} seconds', end='\r')
            time.sleep(1)
        asset_data = qx_api.get_payment().get(currency)
        if asset_data and asset_data['open'] and (asset_data['payment'] >= 85):
            for money in amounts:
                c, buy_info = qx_api.buy(currency, money, direction, trade_duration)
                if 'id' in buy_info.keys():
                    print(f'Trade {index + 1}: {direction} {currency} placed successfully!')
                    print('result', qx_api.check_win(buy_info['id']))
                    result = qx_api.check_win(buy_info['id'])
                    if result > 0:
                        overallprofit = overallprofit + result
                        if overallprofit <= stop_loss:
                            print(f'{Fore.RED}Loss target hit!{Style.RESET_ALL}')
                            time.sleep(10)
                            qx_api.close()
                            sys.exit()
                        mart = 0
                        break
                    if result < 0:
                        overallprofit = overallprofit + result
                        if overallprofit <= stop_loss:
                            print(f'{Fore.RED}Loss target hit!{Style.RESET_ALL}')
                            time.sleep(10)
                            qx_api.close()
                            sys.exit()
                        mart += 1
                        if mart == steps:
                            mart = 0
                        break
                    overallprofit = overallprofit
                    mart = mart
                    break
        else:
            print('SKIP.. LOW RETURN')