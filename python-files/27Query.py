import requests
from bs4 import BeautifulSoup
import lxml.html as lh
import pandas as pd
import xml.etree.ElementTree as ET
import json
import csv
import time
from datetime import datetime,date,timedelta
import os
import urllib.request
import sys
import configparser
from multiprocessing.pool import ThreadPool
import threading
import random

#from prompt_toolkit import prompt
#from prompt_toolkit.completion import WordCompleter
import zipfile
import io
import shutil
import tqdm
from playsound import playsound
#import mplfinance as mpf # This is the old mpl-finance library - note the '_' in the library name

cookie_dic = {}
Common_token="1115989024:AAEo_18W252qLaz5EuQDBwpzNBTD13RAmOg"
Index_token="1383758758:AAHtblT0KxV3E8Gmj-gQ6xEiSIJkzLumRgw"
Stocks_token="1259780160:AAHuH0hpM-Rp8_k38IPnyNNxrE2282dSY5M"
Stocks_chatid="-1001458959153"
Index_chatid="-1001478118747"
Common_chatid="-1001403983472"
TimeForExcel = ""
#current_time = time.strftime("%H:%M:%S")
 
##headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
##            'Accept-Encoding':'gzip, deflate, br',
##            'Accept-Language':'en-US,en;q=0.5',
##                   'Connection':'keep-alive',
##                   'Host':'www.nseindia.com',
##                  'TE':'Trailers',
##                   'Upgrade-Insecure-Requests':'1',
##                   'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:78.0) Gecko/20100101 Firefox/78.0',
##                   #'Cookie':'_ga=GA1.2.1977695528.1513155440; pointer=4; sym1=RELIANCE; pointerfo=1; underlying1=SBIN; instrument1=FUTSTK; optiontype1=-; expiry1=26DEC2019; strikeprice1=-; underlying2=APOLLOTYRE; instrument2=FUTSTK; optiontype2=-; expiry2=26DEC2019; strikeprice2=-; sym2=JINDALSAW; sym3=JINDALSTEL; sym4=SBIN; sym5=MARUTI; underlying3=TATAGLOBAL; instrument3=FUTSTK; optiontype3=-; expiry3=26DEC2019; strikeprice3=-; underlying4=MINDTREE; instrument4=FUTSTK; optiontype4=-; expiry4=26DEC2019; strikeprice4=-; RT="z=1&dm=nseindia.com&si=8d0118cd-c0fc-422f-a783-6bc0cd6c6966&ss=kfi0ib7z&sl=1&tt=161&bcn=%2F%2F684fc53f.akstat.io%2F&ld=22sw&nu=ed8553192c8d124be55949cc1b2e99dc&cl=24ca&ul=24cn&hd=24i0"; _gid=GA1.2.846531547.1600662017; nseQuoteSymbols=[{"symbol":"ASIANPAINT","identifier":null,"type":"equity"},{"symbol":"INDUSINDBK","identifier":null,"type":"equity"},{"symbol":"VEDL","identifier":null,"type":"equity"},{"symbol":"NIFTY","identifier":null,"type":"equity"},{"symbol":"SBIN","identifier":null,"type":"equity"}]; nsit=-xoaBrs03m5psx---3b_aD0T; ak_bmsc=7BB478A45FE644DE50E4C6701294686F174C9C9D2719000054AA6D5F071EC11D~plQ3bP7AMwIEwtsy294rFA7B5e8/4PKYR5v3QPVSq9gjhcBR9Ovr+Cx49K4Ii7jJwKN9AtgIvOiXDh0Amgx9c0VI8BFd7Gk+rxJBn7/GNGDuDqumZoQ0CmuShI+OJg18prcSnVcCIAjX0RScP8T4jlfX3rgBj0ozPz56/EJy6Am6g9ySODN/EgD6d1QY3MlLb3nokFB1/krXJvzKTmgY2zZHZY3PcRCK2QIZXYwpA5ZNoJlmTBliKWy4/N3eJ3c6Rs; bm_sv=DFE155E43A3E128F841F7AD6AF3B2676~rKCE5t4eV22F0XfKU8e/swNboYsziItPs5kICt4GdNjCmJjSy+AhPXjo04+HUwD4XiFZdLI2CNuhKR5DBxctL5IkjCe01XqPg/EoiBeBNagmNuowVMnw0i4yjLjhH/V3xRGpLsPj1DduJjbLm/QRYZuoos/p3xyRuKmcdpTKhLA=; _gat_UA-143761337-1=1; nseappid=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhcGkubnNlIiwiYXVkIjoiYXBpLm5zZSIsImlhdCI6MTYwMTAyNDM2MiwiZXhwIjoxNjAxMDI3OTYyfQ.RacS1Oxi4QzWlWjj9F2yMyQ85trDBNFeoBMTVoTYSvc'
##           }
#Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36
           
headers = {'Accept':'*/*',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'en-US,en;q=0.9',
                   'Connection':'keep-alive',
                   'Host':'www.nseindia.com',
                   'TE':'Trailers',
                   'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"   ',
                   'sec-ch-ua-mobile': '?0',
                   'sec-ch-ua-platform': "Windows",
                   'sec-fetch-dest': 'document',
                   'sec-fetch-mode': 'cors',
                   'sec-fetch-site':'same-origin',
                   'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
                   #'Cookie':'_ga=GA1.2.1977695528.1513155440; pointer=4; sym1=RELIANCE; pointerfo=1; underlying1=SBIN; instrument1=FUTSTK; optiontype1=-; expiry1=26DEC2019; strikeprice1=-; underlying2=APOLLOTYRE; instrument2=FUTSTK; optiontype2=-; expiry2=26DEC2019; strikeprice2=-; sym2=JINDALSAW; sym3=JINDALSTEL; sym4=SBIN; sym5=MARUTI; underlying3=TATAGLOBAL; instrument3=FUTSTK; optiontype3=-; expiry3=26DEC2019; strikeprice3=-; underlying4=MINDTREE; instrument4=FUTSTK; optiontype4=-; expiry4=26DEC2019; strikeprice4=-; RT="z=1&dm=nseindia.com&si=8d0118cd-c0fc-422f-a783-6bc0cd6c6966&ss=kfi0ib7z&sl=1&tt=161&bcn=%2F%2F684fc53f.akstat.io%2F&ld=22sw&nu=ed8553192c8d124be55949cc1b2e99dc&cl=24ca&ul=24cn&hd=24i0"; _gid=GA1.2.846531547.1600662017; nseQuoteSymbols=[{"symbol":"ASIANPAINT","identifier":null,"type":"equity"},{"symbol":"INDUSINDBK","identifier":null,"type":"equity"},{"symbol":"VEDL","identifier":null,"type":"equity"},{"symbol":"NIFTY","identifier":null,"type":"equity"},{"symbol":"SBIN","identifier":null,"type":"equity"}]; nsit=-xoaBrs03m5psx---3b_aD0T; ak_bmsc=7BB478A45FE644DE50E4C6701294686F174C9C9D2719000054AA6D5F071EC11D~plQ3bP7AMwIEwtsy294rFA7B5e8/4PKYR5v3QPVSq9gjhcBR9Ovr+Cx49K4Ii7jJwKN9AtgIvOiXDh0Amgx9c0VI8BFd7Gk+rxJBn7/GNGDuDqumZoQ0CmuShI+OJg18prcSnVcCIAjX0RScP8T4jlfX3rgBj0ozPz56/EJy6Am6g9ySODN/EgD6d1QY3MlLb3nokFB1/krXJvzKTmgY2zZHZY3PcRCK2QIZXYwpA5ZNoJlmTBliKWy4/N3eJ3c6Rs; bm_sv=DFE155E43A3E128F841F7AD6AF3B2676~rKCE5t4eV22F0XfKU8e/swNboYsziItPs5kICt4GdNjCmJjSy+AhPXjo04+HUwD4XiFZdLI2CNuhKR5DBxctL5IkjCe01XqPg/EoiBeBNagmNuowVMnw0i4yjLjhH/V3xRGpLsPj1DduJjbLm/QRYZuoos/p3xyRuKmcdpTKhLA=; _gat_UA-143761337-1=1; nseappid=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhcGkubnNlIiwiYXVkIjoiYXBpLm5zZSIsImlhdCI6MTYwMTAyNDM2MiwiZXhwIjoxNjAxMDI3OTYyfQ.RacS1Oxi4QzWlWjj9F2yMyQ85trDBNFeoBMTVoTYSvc'
           }
           
# Urls for fetching Data
url_oc      = "https://www.nseindia.com/option-chain"
url_bnf     = 'https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY'
url_nf      = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
url_indices = "https://www.nseindia.com/api/allIndices"

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'accept-language': 'en,gu;q=0.9,hi;q=0.8',
            'accept-encoding': 'gzip, deflate, br'}

sess = requests.Session()
cookies = dict()

# Local methods
def set_cookie():
    #sess = requests.Session()
    request = sess.get(url_oc, headers=headers, timeout=10)
    #cookies = dict(request.cookies)
    return dict(request.cookies)

def get_data(url):
    #set_cookie()
    global cookies
    response = sess.get(url, headers=headers, timeout=20, cookies=cookies)
    if(response.status_code==401):
        cookies = set_cookie()
        response = sess.get(url_nf, headers=headers, timeout=20, cookies=cookies)
    if(response.status_code==200):
        return response.text
    print(response.status_code)
    return ""

Candle_timer =  15
STOCK_THREAD_COUNT = 1
INDEX_THREAD_COUNT = 1
SEND_MESSAGE_TELE = 0
SEND_MESSAGE_TELE_TESTING_AFTER1530 = 0

lock = threading.Lock()


def monthToNum(shortMonth):
    return{
        '01' : 'JAN',
        '02' : 'FEB',
        '03' : 'MAR',
        '04' : 'APR',
        '05' : 'MAY',
        '06' : 'JUN',
        '07' : 'JUL',
        '08' : 'AUG',
        '09' : 'SEP', 
        '10' : 'OCT',
        '11' : 'NOV',
        '12' : 'DEC'
}[shortMonth]

def download_FnO_Bhav(date1):
    Currentpath= os.getcwd() +"\\finaloutput\\"
    if not os.path.exists(Currentpath):
      os.mkdir(Currentpath)
    else:
      pass

    date2 = date1
    
    url = 'https://archives.nseindia.com/content/historical/DERIVATIVES/' + str(date1.year) + '/' + monthToNum(str('%02d'%date1.month))
    file_name ='/fo'+ str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year) + 'bhav.csv.zip'
    final_url1 = url + file_name
    csv_file ='/fo'+ str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year) +'bhav.csv'
    #print("URL to doenalod:" + final_url1)
    delta = timedelta(days=1)

    while date1 <= date2:
        if ((int(date1.weekday()) <=4 and not os.path.exists(Currentpath + csv_file) and not is_public_holiday(date1))):
            #print ("Downloading OI File: "+date1.strftime("%d/%m/%Y"))
            #print("URL to download:" + final_url1)
            #download(final_url1,csv_file)
            try: 
                r = requests.get(final_url1, timeout=25)
                if(r.status_code == 200):
                    z = zipfile.ZipFile(io.BytesIO(r.content))
                    z.extractall(Currentpath)

                elif(r.status_code == 404):
                    print("File not found")
                    
                 

                else:
                    pass
            except requests.exceptions.TimeoutError as e: 
                print (e)
                return 0
            except requests.exceptions.ConnectionError as e:
                 print (e)
#            r = requests.get(final_url1)
            except Exception:
               return 0
            
            date1 = date1 + delta
            file_name ='/fo'+ str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year) + 'bhav.csv.zip'
            url = 'https://archives.nseindia.com/content/historical/DERIVATIVES/' + str(date1.year) + '/' + monthToNum(str('%02d'%date1.month))
            final_url1 = url + file_name
            csv_file ='/fo'+ str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year) +'bhav.csv'
            #print("URL to doenalod: 1 " + final_url1)
            
                                          
        else:
            date1 = date1 + delta
            file_name ='/fo'+ str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year) + 'bhav.csv.zip'
            csv_file ='/fo'+ str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year) +'bhav.csv'
            url = 'https://archives.nseindia.com/content/historical/DERIVATIVES/' + str(date1.year) + '/' + monthToNum(str('%02d'%date1.month))
            final_url1 = url + file_name
            #print("URL to doenalod: 2 " + final_url1)

def generate_cookie():
    global cookie_dic
    global lock
    proxies = {'https':'36.255.86.170:4145',
                'https':'36.255.86.170:4145'}
    if(lock.locked() ==  False):
        lock.acquire() 
        print("Baking Cookie")
        ranNum =  random.randint(1, 49)
        #driver = webdriver.Firefox()
        #driver = webdriver.Firefox()
        driver = webdriver.Chrome()
        
        driver.get("https://www.nseindia.com/get-quotes/derivatives?symbol="+stc_Nifty_50[ranNum])
        cookies = driver.get_cookies()
        cookie_dic = {}
        for cookie in cookies:
            cookie_dic[cookie['name']] = cookie['value']
            #print("Name: "+ cookie['name'] + " Value: " + cookie['value'] )

        driver.quit()
        lock.release()
    else:
        print("Already Locked")
        time.sleep(60)
        print("Returning Cookie Might have generated")

def is_public_holiday(date1):
    if(date1 == date(2020, 5, 1) or
       date1 == date(2018, 12, 25) or
       date1 == date(2019, 3, 4) or
       date1 == date(2019, 3, 21) or
       date1 == date(2019, 4, 14) or
       date1 == date(2019, 4, 17) or
       date1 == date(2019, 4, 19) or
       date1 == date(2019, 4, 29) or
       date1 == date(2019, 8, 12) or
       date1 == date(2019, 5, 1) or
       date1 == date(2019, 6, 5) or
       date1 == date(2019, 8, 15) or
       date1 == date(2019, 9, 2) or
       date1 == date(2019, 9, 10) or
       date1 == date(2019, 10, 2) or
       date1 == date(2019, 10, 8) or
       date1 == date(2019, 10, 21) or
       date1 == date(2019, 10, 28) or
       date1 == date(2019, 11, 12) or
       date1 == date(2019, 12, 25) or
       date1 == date(2020, 2, 21) or
       date1 == date(2020, 3, 10) or
       date1 == date(2020, 4, 2) or
       date1 == date(2020, 4, 6) or
       date1 == date(2020, 4, 10) or
       date1 == date(2020, 4, 14) or
       date1 == date(2020, 5, 25) or
       date1 == date(2020, 10, 2) or
       date1 == date(2020, 11, 16) or
       date1 == date(2020, 11, 30) or
       date1 == date(2020, 12, 25) or
       date1 == date(2021, 1, 26) or
       date1 == date(2021, 3, 29) or
       date1 == date(2021, 4, 2) or
       date1 == date(2021, 4, 14) or
       date1 == date(2021, 7, 21) or
       date1 == date(2021, 8, 19) or
       date1 == date(2021, 9, 10) or
       date1 == date(2021, 11, 5) or
       date1 == date(2022, 1, 26) or
       date1 == date(2022, 3, 1) or
       date1 == date(2022, 4, 14) or
       date1 == date(2022, 4, 15) or
       date1 == date(2022, 3, 18) or
       date1 == date(2022, 3, 18) or
       date1 == date(2022, 5, 3) or
       date1 == date(2022, 8, 9) or
       date1 == date(2022, 8, 15) or
       date1 == date(2022, 8, 31) or
       date1 == date(2022, 10, 5) or
       date1 == date(2022, 10, 26) or
       date1 == date(2022, 11, 8) or
       date1 == date(2023, 1, 26) or
       date1 == date(2023, 3, 7) or
       date1 == date(2023, 3, 30) or
       date1 == date(2023, 4, 4) or
       date1 == date(2023, 4, 7) or
       date1 == date(2023, 4, 14) or
       date1 == date(2023, 6, 29) or
       date1 == date(2023, 8, 15) or
       date1 == date(2023, 10, 2) or
       date1 == date(2023, 10, 24) or
       date1 == date(2023, 11, 6) or
       date1 == date(2023, 11, 14) or
       date1 == date(2023, 11, 27) or
       date1 == date(2023, 12, 25) or
       date1 == date(2024, 1, 22) or
       date1 == date(2024, 3, 25) or
       date1 == date(2024, 3, 29) or
       date1 == date(2024, 1, 26) or
       date1 == date(2024, 4, 11) or
       date1 == date(2024, 5, 1) or
       date1 == date(2024, 5, 20) or
       date1 == date(2024, 6, 17) or
       date1 == date(2024, 7, 8) or
       date1 == date(2024, 7, 17) or
       date1 == date(2024, 8, 15) or
       date1 == date(2024, 10, 2) or 
       date1 == date(2024, 11, 20) or
       date1 == date(2025, 3, 31) or
       date1 == date(2025, 4, 10) or
       date1 == date(2025, 4, 14) or
       date1 == date(2025, 4, 18) or
       date1 == date(2025, 5, 1) or
       date1 == date(2021, 3, 11) 
       ):
        return True
    else:
        return False

def getPreviousValidDay():
    date1 = date.today() - timedelta(days=1)
    while int(date1.weekday()) >=5  or is_public_holiday(date1):
         date1=date1-timedelta(days=1)

    download_FnO_Bhav(date1)
    return date1

def sendChart(stc_code, chat_id, token,Tele_not_send):

    try:
    
        if(SEND_MESSAGE_TELE_TESTING_AFTER1530 or (SEND_MESSAGE_TELE and not (Tele_not_send))):
            filename = ".\\" + stc_code + ".png"
            if(os.path.exists(filename)):
                bot = telegram.Bot(token=token)
                bot.send_photo(chat_id=chat_id, photo=open(filename, 'rb'))
        else:
            print("Sending Telegram Message Ignored")
          
    except Exception as e:
        print("Telegram Send failed  Skipping this")
        #time.sleep(30)
               
    
    

def send(msg, chat_id, token,Tele_not_send):
    """
    Send a message to a telegram user or group specified on chatId
    chat_id must be a number!
    """
    msg_sent = 0
    while(msg_sent < 2):
        try:
    
            if(SEND_MESSAGE_TELE_TESTING_AFTER1530 or (SEND_MESSAGE_TELE and not (Tele_not_send))):
                bot = telegram.Bot(token=token)
                bot.sendMessage(chat_id=chat_id, text=msg,parse_mode=telegram.ParseMode.MARKDOWN)
                msg_sent = msg_sent + 2
            else:
                print("Sending Telegram Message Ignored")
                msg_sent = msg_sent + 2
      
           
        except Exception as e:
                print("Telegram Send failed  Skipping this")
                time.sleep(30)
                msg_sent = msg_sent+ 1


"""html_completer = WordCompleter(["ACC","WOCKPHARMA","LUPIN",
                      "LICHSGFIN",
                      "LT",
                      "AUROPHARMA",
                      "MANAPPURAM",
                      "ASHOKLEY",
                      "ONGC",
                      "DIVISLAB",
                      "NCC",
                      "GLENMARK",
                      "TATACOMM",
                      "ADANIPOWER",
                      "BRITANNIA",
                      "UNIONBANK",
                      "GODFRYPHLP",
                      "IBULHSGFIN",
                      "TITAN",
                      "BALKRISIND",
                      "JINDALSTEL",
                      "CADILAHC",
                      "TATAGLOBAL",
                      "MOTHERSUMI",
                      "TV18BRDCST",
                      "SRF",
                      "BANKINDIA",
                      "DLF",
                      "IOC",
                      "GMRINFRA",
                      "BAJFINANCE",
                      "EICHERMOT",
                      "SIEMENS",
                      "BALRAMCHIN",
                      "ARVIND",
                      "RECLTD",
                      "HEXAWARE",
                      "GAIL",
                      "HINDPETRO",
                      "RAYMOND",
                      "HINDUNILVR",
                      "TATACHEM",
                      "PEL",
                      "JSWENERGY",
                      "FEDERALBNK",
                      "NATIONALUM",
                      "SRTRANSFIN",
                      "HDIL",
                      "UBL",
                      "SOUTHBANK",
                      "VEDL",
                      "BAJAJ-AUTO",
                      "AXISBANK",
                      "JUSTDIAL",
                      "ITC",
                      "HDFC",
                      "AMBUJACEM",
                      "ANDHRABANK",
                      "ICICIPRULI",
                      "DHFL",
                      "BHEL",
                      "PFC",
                      "BIOCON",
                      "AJANTPHARM",
                      "SREINFRA",
                      "INDIACEM",
                      "IGL",
                      "HCC",
                      "ADANIENT",
                      "JISLJALEQS",
                      "OIL",
                      "ORIENTBANK",
                      "KOTAKBANK",
                      "CHOLAFIN",
                      "GODREJIND",
                      "AMARAJABAT",
                      "BHARATFORG",
                      "PETRONET",
                      "TATAMOTORS",
                      "SBIN",
                      "MARUTI",
                      "BPCL",
                      "PCJEWELLER",
                      "BHARTIARTL",
                      "EQUITAS",
                      "IFCI",
                      "CANBK",
                      "CIPLA",
                      "IDFCBANK",
                      "APOLLOHOSP",
                      "BANKBARODA",
                      "ULTRACEMCO",
                      "L&TFH",
                      "MCX",
                      "TATAELXSI",
                      "JETAIRWAYS",
                      "BERGEPAINT",
                      "VOLTAS",
                      "M&MFIN",
                      "NHPC",
                      "HAVELLS",
                      "JSWSTEEL",
                      "MINDTREE",
                      "DRREDDY",
                      "RAMCOCEM",
                      "UJJIVAN",
                      "STAR",
                      "PAGEIND",
                      "MRPL",
                      "MFSL",
                      "CONCOR",
                      "KSCL",
                      "JUBLFOOD",
                      "SUNPHARMA",
                      "MGL",
                      "CENTURYTEX",
                      "TCS",
                      "SAIL",
                      "KTKBANK",
                      "ICICIBANK",
                      "RELIANCE",
                      "HINDALCO",
                      "NBCC",
                      "HCLTECH",
                      "MUTHOOTFIN",
                      "M&M",
                      "INFRATEL",
                      "UPL",
                      "BEL",
                      "BEML",
                      "CEATLTD",
                      "KPIT",
                      "TORNTPHARM",
                      "SHREECEM",
                      "JPASSOCIAT",
                      "CANFINHOME",
                      "PNB",
                      "ESCORTS",
                      "TECHM",
                      "KTKBANK",
                      "TVSMOTOR",
                      "ALBK",
                      "SYNDIBANK",
                      "MARICO",
                      "GRASIM",
                      "ZEEL",
                      "RBLBANK",
                      "TORNTPOWER",
                      "IRB",
                      "DALMIABHA",
                      "NESTLEIND",
                      "TATAPOWER",
                      "VGUARD",
                      "COALINDIA",
                      "RELCAPITAL",
                      "RCOM",
                      "TATASTEEL",
                      "INFY",
                      "APOLLOTYRE",
                      "RPOWER",
                      "MCDOWELL-N",
                      "YESBANK",
                      "INDUSINDBK",
                      "BATAINDIA",
                      "CASTROLIND",
                      "ASIANPAINT",
                      "WIPRO",
                      "COLPAL",
                      "NMDC",
                      "INDIGO",
                      "BHARATFIN",
                      "IDFC",
                      "GRANULES",
                      "INDIANB",
                      "OFSS",
                      "INFIBEAM",
                      "SUNTV",
                      "TATAMTRDVR",
                      "HDFCBANK",
                      "ADANIPORTS",
                      "HEROMOTOCO",
                      "IDBI",
                      "IDEA",
                      "CESC",
                      "PTC",
                      "HINDZINC",
                      "BOSCHLTD",
                      "GODREJCP",
                      "FORTIS",
                      "PVR",
                      "POWERGRID",
                      "DISHTV",
                      "BAJAJFINSV",
                      "ENGINERSIN",
                      "DABUR",
                      "CAPF",
                      "CHENNPETRO",
                      "EXIDEIND",
                      "CUMMINSIND",
                      "REPCOHOME",
                      "CGPOWER",
                      "NIITTECH",
                      "MRF",    
                    "BANKNIFTY","NIFTY"])"""

stc_IT = (["INFY","TCS","TECHM","WIPRO","HCLTECH"])
stc_AUTO = (["APOLLOTYRE","ASHOKLEY","BAJAJ-AUTO","BALKRISIND","EICHERMOT","ESCORTS","HEROMOTOCO","MARUTI","TVSMOTOR"])
stc_BANK = (["AXISBANK","BAJFINANCE","BANDHANBNK","BAJAJFINSV","BANKBARODA","CANBK","FEDERALBNK","HDFCBANK","ICICIBANK","IDFCFIRSTB","INDUSINDBK","KOTAKBANK","PNB","RBLBANK","SBIN","YESBANK"])
stc_METAL = (["HINDALCO","SAIL","JINDALSTEL","NATIONALUM","TATASTEEL","VEDL"])
stc_PHARMA = (["APOLLOHOSP","AUROPHARMA","BIOCON","CADILAHC","CIPLA","DIVISLAB","DRREDDY","GLENMARK","LUPIN","PEL","SUNPHARMA","TORNTPHARM"])
stc_FMCG = (["ITC","DABUR","HINDUNILVR","MARICO"])
stc_Index = (["BANKNIFTY","NIFTY"])

stc_Nifty_50 = (["ACC","ADANIENT","ADANIPORTS","ASIANPAINT","AXISBANK","AMBUJACEM","APOLLOHOSP","ASHOKLEY","AUROPHARMA","BAJAJ-AUTO","BAJAJFINSV","BAJFINANCE","BHARTIARTL","BPCL","BRITANNIA","BALKRISIND","BANDHANBNK","BATAINDIA","BIOCON",
                "CANBK","CANFINHOME","CIPLA","COALINDIA","COFORGE","DRREDDY","DEEPAKNTR","DLF","EICHERMOT","GAIL","GRASIM","HCLTECH","HDFCBANK","HEROMOTOCO","HINDALCO","HINDUNILVR","HDFCLIFE","ICICIBANK","INDUSINDBK","IGL",
                "INFY","IOC","ITC","JSWSTEEL","JUBLFOOD","VOLTAS","KOTAKBANK","LT","MARUTI","HINDPETRO","M%26M","TATACHEM","NESTLEIND","NTPC","ONGC","POWERGRID","RELIANCE","SBIN","SHREECEM","SUNPHARMA","TATAMOTORS","TATASTEEL","TATAPOWER","TCS","TECHM","TITAN","ULTRACEMCO","UPL","VEDL","WIPRO","ZEEL","BHARATFORG","LUPIN"
                ])#NIFTYIT","NIFTY","BANKNIFTY"])
                


all_stc_list1 = (["AARTIIND","ABB","ABBOTINDIA","ACC","ADANIENT","ADANIPORTS","ABCAPITAL","ABFRL","ALKEM","AMBUJACEM","APOLLOHOSP","APOLLOTYRE","ASHOKLEY","ASIANPAINT","ASTRAL","ATUL","AUBANK","AUROPHARMA","AXISBANK","BAJAJ-AUTO","BAJFINANCE","BAJAJFINSV","BALKRISIND","BALRAMCHIN","BANDHANBNK","BANKBARODA","BATAINDIA","BERGEPAINT","BEL","BHARATFORG","BHEL","BPCL","BHARTIARTL","BIOCON","BSOFT","BOSCHLTD","BRITANNIA","CANFINHOME","CANBK","CHAMBLFERT","CHOLAFIN","CIPLA","CUB","COALINDIA","COFORGE","COLPAL","CONCOR","COROMANDEL","CROMPTON","CUMMINSIND","DABUR","DALBHARAT","DEEPAKNTR","DELTACORP","DIVISLAB","DIXON","DLF","LALPATHLAB","DRREDDY","EICHERMOT","ESCORTS","EXIDEIND","GAIL","GLENMARK","GMRINFRA","GODREJCP","GODREJPROP","GRANULES","GRASIM","GUJGASLTD","GNFC","HAVELLS","HCLTECH","HDFCAMC","HDFCBANK","HDFCLIFE","HEROMOTOCO","HINDALCO","HAL","HINDCOPPER","HINDPETRO","HINDUNILVR","ICICIBANK","ICICIGI","ICICIPRULI","IDFCFIRSTB","IDFC","IBULHSGFIN","INDIAMART","IEX","IOC","IRCTC","IGL","INDUSTOWER","INDUSINDBK","NAUKRI","INFY","INDIGO","IPCALAB","ITC","JINDALSTEL","JKCEMENT","JSWSTEEL","JUBLFOOD","KOTAKBANK","L%26TFH","LTTS","LT","LAURUSLABS","LICHSGFIN","LTIM","LUPIN","MGL","M%26MFIN","M%26M","MANAPPURAM","MARICO","MARUTI","MFSL","METROPOLIS","MPHASIS","MRF","MCX","MUTHOOTFIN","NATIONALUM","NAVINFLUOR","NESTLEIND","NMDC","NTPC","OBEROIRLTY","ONGC","OFSS","PAGEIND","PERSISTENT","PETRONET","PIIND","PIDILITIND","PEL","POLYCAB","PFC","POWERGRID","PNB","PVRINOX","RBLBANK","RECLTD","RELIANCE","MOTHERSON","SBICARD","SBILIFE","SHREECEM","SHRIRAMFIN","SIEMENS","SRF","SBIN","SAIL","SUNPHARMA","SUNTV","SYNGENE","TATACHEM","TATACOMM","TCS","TATACONSUM","TATAMOTORS","TATAPOWER","TATASTEEL","TECHM","FEDERALBNK","INDIACEM","INDHOTEL","RAMCOCEM","TITAN","TORNTPHARM","TRENT","TVSMOTOR","ULTRACEMCO","UBL","MCDOWELL-N","UPL","VEDL","IDEA","VOLTAS","WIPRO","ZEEL",
                "ZYDUSLIFE","MAZDOCK"])
                


all_stc_list= (["ACC","APLAPOLLO","AUBANK","AARTIIND","ADANIENSOL","ADANIENT","ADANIGREEN","ADANIPORTS","ATGL","ABCAPITAL","ABFRL","ALKEM","AMBUJACEM","ANGELONE","APOLLOHOSP","APOLLOTYRE","ASHOKLEY","ASIANPAINT","ASTRAL","ATUL","AUROPHARMA","DMART","AXISBANK","BSOFT","BSE","BAJAJ-AUTO","BAJFINANCE","BAJAJFINSV","BALKRISIND","BANDHANBNK","BANKBARODA","BANKINDIA","BERGEPAINT","BEL","BHARATFORG","BHEL","BPCL","BHARTIARTL","BIOCON","BOSCHLTD","BRITANNIA","CESC","CGPOWER","CANFINHOME","CANBK","CDSL","CHAMBLFERT","CHOLAFIN","CIPLA","CUB","COALINDIA","COFORGE","COLPAL","CAMS","CONCOR","COROMANDEL","CROMPTON","CUMMINSIND","CYIENT","DLF","DABUR","DALBHARAT","DEEPAKNTR","DELHIVERY","DIVISLAB","DIXON","LALPATHLAB","DRREDDY","EICHERMOT","ESCORTS","EXIDEIND","NYKAA","GAIL","GMRAIRPORT","GLENMARK","GODREJCP","GODREJPROP","GRANULES","GRASIM","GUJGASLTD","GNFC","HCLTECH","HDFCAMC","HDFCBANK","HDFCLIFE","HFCL","HAVELLS","HEROMOTOCO","HINDALCO","HAL","HINDCOPPER","HINDPETRO","HINDUNILVR","HUDCO","ICICIBANK","ICICIGI","ICICIPRULI","IDFCFIRSTB","IRB","ITC","INDIANB","IEX","IOC","IRCTC","IRFC","IGL","INDUSTOWER","INDUSINDBK","NAUKRI","INFY","INDIGO","JKCEMENT","JSWENERGY","JSWSTEEL","JSL","JINDALSTEL","JIOFIN","JUBLFOOD","KEI","KPITTECH","KALYANKJIL","KOTAKBANK","LTF","LTTS","LICHSGFIN","LTIM","LT","LAURUSLABS","LICI","LUPIN","MRF","LODHA","MGL","M%26MFIN","M%26M","MANAPPURAM","MARICO","MARUTI","MFSL","MAXHEALTH","METROPOLIS","MPHASIS","MCX","MUTHOOTFIN","NCC","NHPC","NMDC","NTPC","NATIONALUM","NAVINFLUOR","NESTLEIND","OBEROIRLTY","ONGC","OIL","PAYTM","OFSS","POLICYBZR","PIIND","PVRINOX","PAGEIND","PERSISTENT","PETRONET","PIDILITIND","PEL","POLYCAB","POONAWALLA","PFC","POWERGRID","PRESTIGE","PNB","RBLBANK","RECLTD","RELIANCE","SBICARD","SBILIFE","SHREECEM","SJVN","SRF","MOTHERSON","SHRIRAMFIN","SIEMENS","SONACOMS","SBIN","SAIL","SUNPHARMA","SUNTV","SUPREMEIND","SYNGENE","TATACONSUM","TVSMOTOR","TATACHEM","TATACOMM","TCS","TATAELXSI","TATAMOTORS","TATAPOWER","TATASTEEL","TECHM","FEDERALBNK","INDHOTEL","RAMCOCEM","TITAN","TORENTPHARM","TRENT","TIINDIA","UPL","ULTRACEMCO","UNIONBANK","UBL","UNITDSPR","VBL","VEDL","IDEA","VOLTAS","WIPRO","YESBANK","ETERNAL","ZYDUSLIFE"])





selected_stc =(["ACC","ADANIENT","ADANIPORTS","ADANIPOWER","AMARAJABAT","AMBUJACEM","APOLLOHOSP","APOLLOTYRE","ASHOKLEY","ASIANPAINT","AUROPHARMA","AXISBANK","BAJAJ-AUTO","BANDHANBNK","BAJAJFINSV","BAJFINANCE","BALKRISIND","BANKBARODA","BATAINDIA","BEL","BERGEPAINT","BHARATFORG","BHARTIARTL","BHEL","BIOCON","BOSCHLTD","BPCL","BRITANNIA","CADILAHC","CANBK","CENTURYTEX","CESC","CHOLAFIN","CIPLA","COALINDIA","COLPAL","CONCOR","CUMMINSIND","DABUR","DISHTV","DIVISLAB","DLF","DRREDDY","EICHERMOT","EQUITAS","ESCORTS","EXIDEIND","FEDERALBNK","GAIL","GLENMARK","GMRINFRA","GODREJCP","GRASIM","HAVELLS","HCLTECH","HDFC","HDFCBANK","HEROMOTOCO","HEXAWARE","HINDALCO","HINDPETRO","HINDUNILVR","IBULHSGFIN","ICICIBANK","ICICIPRULI","IDEA","IDFCFIRSTB","IGL","INDIGO","INDUSINDBK","INFRATEL","INFY","IOC","ITC","JINDALSTEL","JSWSTEEL","JUBLFOOD","JUSTDIAL","KOTAKBANK","L&TFH","LICHSGFIN","LT","LUPIN","M&M","M&MFIN","MANAPPURAM","MARICO","MARUTI","MCDOWELL-N","MFSL","MGL","MINDTREE","MOTHERSUMI","MRF","MUTHOOTFIN","NATIONALUM","NBCC","NCC","NESTLEIND","NIITTECH","NMDC","NTPC","OIL","ONGC","PAGEIND","PEL","PETRONET","PFC","PIDILITIND","PNB","POWERGRID","PVR","RAMCOCEM","RBLBANK","RECLTD","RELIANCE","SAIL","SBIN","SHREECEM","SIEMENS","SRF","SRTRANSFIN","SUNPHARMA","SUNTV","TATACHEM","TATAELXSI","TATAGLOBAL","TATAMOTORS","TATAMTRDVR","TATAPOWER","TATASTEEL","TCS","TECHM","TITAN","TORNTPHARM","TORNTPOWER","TVSMOTOR","UBL","UJJIVAN","ULTRACEMCO","UNIONBANK","UPL","VEDL","VOLTAS","WIPRO","YESBANK","ZEEL"
                ])#NIFTYIT","NIFTY","BANKNIFTY"])

selected_stc1 = (["ACC","ADANIENT","ADANIPORTS","AMARAJABAT","AMBUJACEM","APOLLOHOSP","APOLLOTYRE","ASHOKLEY","ASIANPAINT","AUROPHARMA","AXISBANK","BAJAJ-AUTO","BANDHANBNK","BAJAJFINSV","BAJFINANCE","BALKRISIND","BANKBARODA","BATAINDIA","BEL","BERGEPAINT","BHARATFORG","BHARTIARTL","BHEL","BIOCON","BOSCHLTD","BPCL","BRITANNIA","CADILAHC","CANBK","CENTURYTEX","CHOLAFIN","CIPLA","COALINDIA","COLPAL","CONCOR","CUMMINSIND","DABUR","DIVISLAB","DLF","DRREDDY","EICHERMOT","EQUITAS","ESCORTS","EXIDEIND","FEDERALBNK"
                  ])
selected_stc2 = (["GAIL","GLENMARK","GMRINFRA","GODREJCP","GODREJPROP","GRASIM","HAVELLS","HCLTECH","HDFC","HDFCBANK","HDFCLIFE","HEROMOTOCO","HINDALCO","HINDPETRO","HINDUNILVR","IBULHSGFIN","ICICIBANK","ICICIPRULI","IDEA","IDFCFIRSTB","IGL","INDIGO","INDUSINDBK","INFRATEL","INFY","IOC","ITC","JINDALSTEL","JSWSTEEL","JUBLFOOD","JUSTDIAL","KOTAKBANK","LICHSGFIN","LT","LUPIN","MANAPPURAM","MARICO","MARUTI","MCDOWELL-N","MFSL","MGL","MINDTREE","MOTHERSUMI","MRF","MUTHOOTFIN","M%26M","NATIONALUM","NAUKRI","NCC","NESTLEIND","NIITTECH","NMDC","NTPC","ONGC"
                  ])

selected_stc3= (["PAGEIND","PEL","PETRONET","PFC","PIDILITIND","PNB","POWERGRID","PVR","RAMCOCEM","RBLBANK","RECLTD","RELIANCE","SAIL","SBIN","SHREECEM","SIEMENS","SRF","SRTRANSFIN","SUNPHARMA","SUNTV","TATACHEM","TATACONSUM","TATAMOTORS","TATAPOWER","TATASTEEL","TCS","TECHM","TITAN","TORNTPHARM","TORNTPOWER","TVSMOTOR","UBL","UJJIVAN","ULTRACEMCO","UPL","VEDL","VOLTAS","WIPRO","ZEEL"])

test_list = (["ADANIPORTS","ASHOKLEY","ASIANPAINT","AXISBANK","BAJAJ-AUTO","BAJAJFINSV","BAJFINANCE","BHARTIARTL","TCS","NCC","SBIN","MARUTI","ACC","ICICIBANK",])
# Get all get possible expiry date details for the given script
#Nifty50OiChangedf = pd.DataFrame(columns=['Name','CMP','Strike','CE_Change','PE_Change','LotSize','Time','ChngInLots','LTP','Expiry'])


def IndexAnalysis(StockList):
    #print("Entry IndexAnalysis")
    Tele_not_send = False
    current_time_min = time.strftime("%M")
    current_time_sec = time.strftime("%S")
    Effective_min = int(current_time_min)%Candle_timer
    timenow = datetime.now()
    current_time = (timenow - timedelta(minutes=Effective_min)).strftime("%H:%M")

    date1 = date.today()
    #while int(date1.weekday()) >=5  or is_public_holiday(date1):
    while ((int(date1.weekday()) >=5  or is_public_holiday(date1)) 
            and (str('%02d'%date1.day)!="20" and monthToNum(str('%02d'%date1.month)) == "01" and str(date1.year) == "2024" )) :
        date1=date1-timedelta(days=1)
    folder_Name = ".//" + str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year)

    current_time_hour = time.strftime("%H") 
    if( (int(current_time_hour) <= 8) or
        ((int(current_time_hour) <= 9) and (int(current_time_min) <=25)) or
       ((int(current_time_hour) >= 19) and (int(current_time_min) >=40)) or
        (int(current_time_hour) >= 20)):
        #print("To_temp_folder")
        folder_Name = ".//" + str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year) + "_temp"
        Tele_not_send = True
   
    #CE_MaxOIChanged = pd.DataFrame(columns=['Name','CMP','Fut_p','Fut%','oldStrike','newStrike','oldExpiry','newExpiry','Option_Type','PCR','Time'])
    CE_MaxOIChanged = pd.DataFrame(columns=['Name','CMP','Fut_p','Fut%','strike1','strike2','strike1Lots','strike2Lots','strike1Expiry','strike2Expiry','Option_Type','PCR','Time'])
    CE_MaxDeltaOI = pd.DataFrame(columns=['Name','strike1','strike2','strike1Lots','strike2Lots','strike1Expiry','strike2Expiry','Option_Type','PCR','chs1','chs2','Time'])

    #PE_MaxOIChanged = pd.DataFrame(columns=['Name','CMP','Fut_p','Fut%','oldStrike','newStrike','oldExpiry','newExpiry','Option_Type','PCR','Time'])
    PE_MaxOIChanged = pd.DataFrame(columns=['Name','CMP','Fut_p','Fut%','strike1','strike2','strike1Lots','strike2Lots','strike1Expiry','strike2Expiry','Option_Type','PCR','Time'])
    PE_MaxDeltaOI = pd.DataFrame(columns=['Name','strike1','strike2','strike1Lots','strike2Lots','strike1Expiry','strike2Expiry','Option_Type','PCR','chs1','chs2','Time'])

    for i in range (len(StockList)):
       
        
        file_name = folder_Name + "//" + StockList[i] + ".csv"

       # print ("Open file")
        if(os.path.exists(file_name)):
            df3 = pd.read_csv(file_name)

           
            df_stock = df3.loc[df3['Time'] == current_time]

            if(len(df_stock) == 0):
                print("Data Not found for current time: "+current_time + "  " +StockList[i] )
                continue

            #print(df_stock)
            df_fut = df_stock.loc[df_stock['Type'] == "Fut"]
            
            if(len(df_fut) == 0):
                print("Some NSE Issue: "+current_time + "  " +StockList[i] )
                continue
            Fut_Change_OI = df_fut['OI_Change'].sum()
            Fut_total = df_fut['OI'].sum()
            futPer = Fut_Change_OI/(Fut_total-Fut_Change_OI)*100
            
            fut_row = df_fut.iloc[ 0 , : ]
            Fut_price = fut_row['LTP']
            ltp = fut_row['Cash_ltp']
            market_lot = fut_row['Lotsize']
            
            df_ce = df_stock.loc[df_stock['Type'] == "CE"]
            CE_change = df_ce['OI_Change'].sum()
            CE_OI = df_ce['OI'].sum()

            df_pe = df_stock.loc[df_stock['Type'] == "PE"]
            PE_change = df_pe['OI_Change'].sum()
            PE_OI = df_pe['OI'].sum()
            PCR = PE_OI/CE_OI
            #CE_pert = CE_change*100_OI_change
            #PE_pert = PE_change*100/Total_OI_change
            
            #Commnedted diff Change
            """SortedDataMaxCE = df_ce.sort_values(by=['OI'],ascending=False)
            SortedDataMaxPE = df_pe.sort_values(by=['OI'],ascending=False)
            ce_row = SortedDataMaxCE.iloc[ 0 , : ]
            date1 = getPreviousValidDay()
            Currentpath= os.getcwd() +"\\finaloutput\\"
            csv1 = Currentpath + 'fo'+ str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year) +'bhav.csv'
            #futPer = Future_delta/Fut_total*100
            temptime = time.strftime("%H:%M:%S")
            #print ("OpenCSV now"+csv1)
            if(os.path.exists(csv1)):
                
                df1 = pd.read_csv(csv1)
                row1 = df1.loc[df1['SYMBOL'] == StockList[i]]
                optionData = row1[row1['INSTRUMENT'] == 'OPTIDX']
                optionDataCE = optionData[optionData['OPTION_TYP'] == 'CE']
                PreviousDaySortedDataMaxCE = optionDataCE.sort_values(by=['OPEN_INT'],ascending=False)
                if(len(PreviousDaySortedDataMaxCE)):
                    selected_ce_row = PreviousDaySortedDataMaxCE.iloc[ 0 , : ]
                    if((ce_row['Strike'] != selected_ce_row['STRIKE_PR']) or (ce_row['Expiry'] != selected_ce_row['EXPIRY_DT'])):
                    
                        moddf = CE_MaxOIChanged.append({'Name':StockList[i],'CMP':ltp,'Fut_p':Fut_price,'Fut%':float(("%.2f" %futPer)),'oldStrike':int(selected_ce_row['STRIKE_PR']),'newStrike': int(ce_row['Strike']),
                                                'oldExpiry':selected_ce_row['EXPIRY_DT'],'newExpiry':ce_row['Expiry'],'Option_Type': "CE",'PCR':float(("%.2f" %PCR)),'Time':temptime},ignore_index=True)
        
                        CE_MaxOIChanged=moddf
                else:
                    print("From here TATA")
                    
                pe_row = SortedDataMaxPE.iloc[ 0 , : ]
                optionDataPE = optionData[optionData['OPTION_TYP'] == 'PE']
                PreviousDaySortedDataMaxPE = optionDataPE.sort_values(by=['OPEN_INT'],ascending=False)
                if(len(PreviousDaySortedDataMaxPE)):
                    selected_pe_row = PreviousDaySortedDataMaxPE.iloc[ 0 , : ]
                    if((pe_row['Strike'] != selected_pe_row['STRIKE_PR']) or (pe_row['Expiry'] != selected_pe_row['EXPIRY_DT'])):
                
                        moddf = PE_MaxOIChanged.append({'Name':StockList[i],'CMP':ltp,'Fut_p':Fut_price,'Fut%':float(("%.2f" %futPer)),'oldStrike':int(selected_pe_row['STRIKE_PR']),'newStrike': int(pe_row['Strike']),
                                                'oldExpiry':selected_pe_row['EXPIRY_DT'],'newExpiry':pe_row['Expiry'],'Option_Type': "PE",'PCR':float(("%.2f" %PCR)),'Time':temptime},ignore_index=True)
        
                        PE_MaxOIChanged=moddf
            else:
                print("FileNotFound")"""

            SortedDataMaxCE = df_ce.sort_values(by=['OI'],ascending=False)
            SortedDataMaxPE = df_pe.sort_values(by=['OI'],ascending=False)

            if(len(SortedDataMaxCE) >=2):
                temptime = time.strftime("%H:%M:%S")
                ce_row1 = SortedDataMaxCE.iloc[ 0 , : ]
                ce_row2 = SortedDataMaxCE.iloc[ 1 , : ]
                moddf = CE_MaxOIChanged.append({'Name':StockList[i],'CMP':ltp,'Fut_p':Fut_price,'Fut%':float(("%.2f" %futPer)),'strike1':int(ce_row1['Strike']),'strike2': int(ce_row2['Strike']),
                                                'strike1Lots':int(ce_row1['OI']),'strike2Lots':int(ce_row2['OI']),'strike1Expiry':ce_row1['Expiry'],'strike2Expiry':ce_row2['Expiry'],'Option_Type': "CE",'PCR':float(("%.2f" %PCR)),'Time':temptime},ignore_index=True)
        
                CE_MaxOIChanged=moddf

            if(len(SortedDataMaxPE) >=2):
                temptime = time.strftime("%H:%M:%S")
                pe_row1 = SortedDataMaxPE.iloc[ 0 , : ]
                pe_row2 = SortedDataMaxPE.iloc[ 1 , : ]
                moddf = PE_MaxOIChanged.append({'Name':StockList[i],'CMP':ltp,'Fut_p':Fut_price,'Fut%':float(("%.2f" %futPer)),'strike1':int(pe_row1['Strike']),'strike2': int(pe_row2['Strike']),
                                                'strike1Lots':int(pe_row1['OI']),'strike2Lots':int(pe_row2['OI']),'strike1Expiry':pe_row1['Expiry'],'strike2Expiry':pe_row2['Expiry'],'Option_Type': "PE",'PCR':float(("%.2f" %PCR)),'Time':temptime},ignore_index=True)
        
                PE_MaxOIChanged=moddf

            SortedDataMaxChangeCE = df_ce.sort_values(by=['OI_Change'],ascending=False)
            SortedDataMaxChangePE = df_pe.sort_values(by=['OI_Change'],ascending=False)

            if(len(SortedDataMaxChangeCE) >=2):
                temptime = time.strftime("%H:%M:%S")
                ce_row1 = SortedDataMaxChangeCE.iloc[ 0 , : ]
                ce_row2 = SortedDataMaxChangeCE.iloc[ 1 , : ]
                moddf = CE_MaxDeltaOI.append({'Name':StockList[i],'strike1':int(ce_row1['Strike']),'strike2': int(ce_row2['Strike']),
                                                'strike1Lots':int(ce_row1['OI']),'strike2Lots':int(ce_row2['OI']),'strike1Expiry':ce_row1['Expiry'],'strike2Expiry':ce_row2['Expiry'],'Option_Type': "CE",'PCR':float(("%.2f" %PCR)),
                                              'chs1':int(ce_row1['OI_Change']),'chs2':int(ce_row2['OI_Change']),'Time':temptime},ignore_index=True)
        
                CE_MaxDeltaOI=moddf

            if(len(SortedDataMaxChangePE) >=2):
                temptime = time.strftime("%H:%M:%S")
                pe_row1 = SortedDataMaxChangePE.iloc[ 0 , : ]
                pe_row2 = SortedDataMaxChangePE.iloc[ 1 , : ]
                moddf = PE_MaxDeltaOI.append({'Name':StockList[i],'strike1':int(pe_row1['Strike']),'strike2': int(pe_row2['Strike']),
                                                'strike1Lots':int(pe_row1['OI']),'strike2Lots':int(pe_row2['OI']),'strike1Expiry':pe_row1['Expiry'],'strike2Expiry':pe_row2['Expiry'],'Option_Type': "PE",'PCR':float(("%.2f" %PCR)),
                                              'chs1':int(pe_row1['OI_Change']),'chs2':int(pe_row2['OI_Change']),'Time':temptime},ignore_index=True)
        
                PE_MaxDeltaOI=moddf
            

    if(len(CE_MaxOIChanged)):
        print("#######################################################################################")
        print("CE - Max OI Change Index ")
        print("#######################################################################################")
        print(CE_MaxOIChanged)
        print("\n")

    if(len(PE_MaxOIChanged)):
        print("#######################################################################################")
        print("PE - Max OI Change Index ")
        print("#######################################################################################")
        print(PE_MaxOIChanged)
        print("\n")
    """
    for j in range (len(CE_MaxOIChanged)):
        pe_row = CE_MaxOIChanged.iloc[ j , : ]
        if(len(CE_MaxDeltaOI) >= j and len(PE_MaxOIChanged) >= j and len(PE_MaxDeltaOI) >= j):
            ch_row = CE_MaxDeltaOI.iloc[ j , : ]
            pe_row1 = PE_MaxOIChanged.iloc[ j , : ]
            ch_row1 = PE_MaxDeltaOI.iloc[ j , : ]
            #print("Reached here")
            #Str_to_send = "Name : *" + pe_row['Name'] + "*\nCash Price : " + str(pe_row['CMP']) + "\nFuture Price : " + str(pe_row['Fut_p'])  + "\nOld Strike : " + str(pe_row['oldStrike']) + " *:* " + str(pe_row['oldExpiry']) + "\nNew Strike : "+ str(pe_row['newStrike']) + " *:* "+ str(pe_row['newExpiry']) + "\nOption Type : *CE*\nFuture % : " + str(pe_row['Fut%']) +  "\nPCR : " + str(pe_row['PCR'])
            #Str_to_send = "Name : *" + pe_row['Name'] + "*\nCash Price : " + str(pe_row['CMP']) + "\nFuture Price : " + str(pe_row['Fut_p']) + "\nOption Type : *CE*\nFuture % : " + str(pe_row['Fut%']) +  "\nPCR : " + str(pe_row['PCR']) + "\n*Top 2 Strikes with Max OI*\n" + str(pe_row['strike1']) + "*:*" + str(pe_row['strike1Expiry'][:-5]) + " *Lots*: " +str(pe_row['strike1Lots']) + "\n"+ str(pe_row['strike2']) + "*:*"+ str(pe_row['strike2Expiry'][:-5]) +" *Lots*: " +str(pe_row['strike2Lots']) + "\n\n*Top 2 Strikes with Max Change in OI*\n" + str(ch_row['strike1']) + "*:*" + str(ch_row['strike1Expiry'][:-5]) + " *Lots*: " +str(ch_row['strike1Lots']) +" *Change*: " +str(ch_row['chs1']) +"\n"+ str(ch_row['strike2']) + "*:*"+ str(ch_row['strike2Expiry'][:-5]) +" *Lots*: " +str(ch_row['strike2Lots']) +" *Change*: " +str(ch_row['chs2'])
            Str_to_send = "Name : *" + pe_row['Name'] + "*\nCash Price : " + str(pe_row['CMP']) + "\nFuture Price : " + str(pe_row['Fut_p']) + "\nFuture OI % : " + str(pe_row['Fut%']) +  "\nPCR : " + str(pe_row['PCR']) + "\n*Top 2 CE with Max OI*\n" + str(pe_row['strike1']) + "*:*" + str(pe_row['strike1Expiry'][:-5]) + " *Lots*: " +str(pe_row['strike1Lots']) + "\n"+ str(pe_row['strike2']) + "*:*"+ str(pe_row['strike2Expiry'][:-5]) +" *Lots*: " +str(pe_row['strike2Lots']) + "\n\n*Top 2 CE with Max Change in OI*\n" + str(ch_row['strike1']) + "*:*" + str(ch_row['strike1Expiry'][:-5]) + " *Lots*: " +str(ch_row['strike1Lots']) +" *Change*: " +str(ch_row['chs1']) +"\n"+ str(ch_row['strike2']) + "*:*"+ str(ch_row['strike2Expiry'][:-5]) +" *Lots*: " +str(ch_row['strike2Lots']) +" *Change*: " +str(ch_row['chs2']) +"\n\n*Top 2 PE with Max OI*\n" + str(pe_row1['strike1']) + "*:*" + str(pe_row1['strike1Expiry'][:-5]) + " *Lots*: " +str(pe_row1['strike1Lots']) + "\n"+ str(pe_row1['strike2']) + "*:*"+ str(pe_row1['strike2Expiry'][:-5]) +" *Lots*: " +str(pe_row1['strike2Lots']) + "\n\n*Top 2 PE with Max Change in OI*\n" + str(ch_row1['strike1']) + "*:*" + str(ch_row1['strike1Expiry'][:-5]) + " *Lots*: " +str(ch_row1['strike1Lots']) +" *Change*: " +str(ch_row1['chs1']) +"\n"+ str(ch_row1['strike2']) + "*:*"+ str(ch_row1['strike2Expiry'][:-5]) +" *Lots*: " +str(ch_row1['strike2Lots']) +" *Change*: " +str(ch_row1['chs2'])
            send(Str_to_send,Common_chatid,Common_token,Tele_not_send)
            send(Str_to_send,Index_chatid,Index_token,Tele_not_send)

    for j in range (len(PE_MaxOIChanged)):
        pe_row = PE_MaxOIChanged.iloc[ j , : ]
        if(len(PE_MaxDeltaOI) >= j):
            ch_row = PE_MaxDeltaOI.iloc[ j , : ]
            #Str_to_send = "Name : *" + pe_row['Name'] + "*\nCash Price : " + str(pe_row['CMP']) + "\nFuture Price : " + str(pe_row['Fut_p'])  + "\nOld Strike : " + str(pe_row['oldStrike']) + " *:* " + str(pe_row['oldExpiry']) + "\nNew Strike : "+ str(pe_row['newStrike']) + " *:* "+ str(pe_row['newExpiry']) + "\nOption Type : *PE*\nFuture % : " + str(pe_row['Fut%'])  + "\nPCR : " + str(pe_row['PCR'])
            #Str_to_send = "Name : *" + pe_row['Name'] + "*\nCash Price : " + str(pe_row['CMP']) + "\nFuture Price : " + str(pe_row['Fut_p']) + "\nOption Type : *PE*\nFuture % : " + str(pe_row['Fut%']) +  "\nPCR : " + str(pe_row['PCR']) + "\n*Top 2 Strikes with Max OI*\n" + str(pe_row['strike1']) + "*:*" + str(pe_row['strike1Expiry'][:-5]) + " *Lots*: " +str(pe_row['strike1Lots']) + "\n"+ str(pe_row['strike2']) + "*:*"+ str(pe_row['strike2Expiry'][:-5]) +" *Lots*: " +str(pe_row['strike2Lots']) + "\n\n*Top 2 Strikes with Max Change in OI*\n" + str(ch_row['strike1']) + "*:*" + str(ch_row['strike1Expiry'][:-5]) + " *Lots*: " +str(ch_row['strike1Lots']) +" *Change*: " +str(ch_row['chs1']) +"\n"+ str(ch_row['strike2']) + "*:*"+ str(ch_row['strike2Expiry'][:-5]) +" *Lots*: " +str(ch_row['strike2Lots']) +" *Change*: " +str(ch_row['chs2'])
            #send(Str_to_send,Common_chatid,Common_token)
            #send(Str_to_send,Index_chatid,Index_token)
    """
    
    #print("Exit IndexAnalysis")

def FinddataAfter2(date1):
    print(date1)
    CEOiChangedf = pd.DataFrame(columns=['Name','CashPrice','Strike','TotalLots','ChngInLots','Delta','OptPrice','Expiry','Date','Time'])
    PEOiChangedf = pd.DataFrame(columns=['Name','CashPrice','Strike','TotalLots','ChngInLots','Delta','OptPrice','Expiry','Date','Time'])
    
    while int(date1.weekday()) >=5  or is_public_holiday(date1):
                date1=date1+timedelta(days=1)    
    folder_Name = ".//" + str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year)
        
    file_name =  ".//StockList.csv"
    if(os.path.exists(file_name)):
            df = pd.read_csv(file_name)
            StockList = df["0"]
            
    for i in range (len(StockList)):
            
            file_name = folder_Name + "//" + StockList[i] + ".csv"
            
            Difference_1 = 1000
            Differece_2 = 1000
            if((StockList[i] == "NIFTY") | (StockList[i] == "BANKNIFTY") | (StockList[i] == "FINNIFTY")):
                Difference_1 = 500
                Differece_2 = 500
                print("Index Found")
                
            if(os.path.exists(file_name) ):
                df_stock = pd.read_csv(file_name)
                #Temp_df_ce = temp_df_ce.loc[(temp_df_ce['Strike'] == ce_row['Strike']) & (temp_df_ce['Expiry'] == ce_row['Expiry'])]
                df_ce = df_stock.loc[ (df_stock['Type'] == "CE") & ((df_stock['Time'] == "14:00") | (df_stock['Time'] == "14:30") | (df_stock['Time'] == "14:15") | (df_stock['Time'] == "14:45") | (df_stock['Time'] == "15:00") | (df_stock['Time'] == "15:05") | (df_stock['Time'] == "15:10") |(df_stock['Time'] == "15:15")  | (df_stock['Time'] == "15:25") | (df_stock['Time'] == "15:20") |(df_stock['Time'] == "15:30") ) ]
                df_pe = df_stock.loc[ (df_stock['Type'] == "PE") & ((df_stock['Time'] == "14:00") | (df_stock['Time'] == "14:30") | (df_stock['Time'] == "14:15") | (df_stock['Time'] == "14:45") | (df_stock['Time'] == "15:00") | (df_stock['Time'] == "15:05") | (df_stock['Time'] == "15:10") | (df_stock['Time'] == "15:15") | (df_stock['Time'] == "15:20") | (df_stock['Time'] == "15:25") | (df_stock['Time'] == "15:30")  ) ]
               
                #print(df_ce)
                
                OIChange_df_ce = df_ce.loc[df_ce['OI_Change'] >= Difference_1]
                OIChange_df_pe = df_pe.loc[df_pe['OI_Change'] >= Difference_1]
                #SortedDataCE = df_ce.sort_values(by=['OI_Change'],ascending=False)
                #SortedDataPE = df_pe.sort_values(by=['OI_Change'],ascending=False)
                #df[0] = pd.to_datetime(df_ce['TotalLots'])
                #df['difference'] = df[0].sub(df[0].shift(fill_value=df.at[0,0])).dt.total_seconds()
                #OIChange_df_ce_2 = df_ce.loc[df_stock['Time'] == "14:00"]
                #OIChange_df_pe_2 = df_pe.loc[df_stock['Time'] == "14:00"]
                #if(len(OIChange_df_ce_2) == 0):
                
                for index, ce_row in OIChange_df_ce.iterrows():
                    ce_row_base = df_ce.loc[((df_ce['Expiry'] == ce_row['Expiry']) & (df_ce['Strike'] == ce_row['Strike']) & (df_ce['Time'] == "14:00"))]
                    if(len(ce_row_base) == 0):
                        ce_row_base = df_ce.loc[((df_ce['Expiry'] == ce_row['Expiry']) & (df_ce['Strike'] == ce_row['Strike']) & (df_ce['Time'] == "13:45"))]
                    if(len(ce_row_base) == 0):
                        ce_row_base = df_ce.loc[((df_ce['Expiry'] == ce_row['Expiry']) & (df_ce['Strike'] == ce_row['Strike']) & (df_ce['Time'] == "14:15"))]
                    if(len(ce_row_base) != 0): 
                        effectRow = ce_row_base.iloc[ 0 , : ]
                    Delta = (ce_row['OI_Change'] - effectRow['OI_Change'])
                    DeltaAbs = abs(Delta)
                    #print(DeltaAbs)
                    ce_row_Print = df_ce.loc[((df_ce['Expiry'] == ce_row['Expiry']) & (df_ce['Strike'] == ce_row['Strike']))]
                    if((DeltaAbs) >= Differece_2):
                        ce_row_Fut = df_stock.loc[((df_stock['Expiry'] == ce_row['Expiry']) & (df_stock['Type'] == "Fut") & (df_stock['Time'] == ce_row['Time']) )]
                        rowFut = ce_row_Fut.iloc[ 0 , : ]
                        moddf = CEOiChangedf.append({'Name':StockList[i],'CashPrice':rowFut['LTP'],'Strike':ce_row['Strike'],'TotalLots':ce_row['OI'],'ChngInLots':ce_row['OI_Change'],'Delta':Delta,'OptPrice':ce_row['LTP'],
                                'Expiry':ce_row['Expiry'],'Date':date1,'Time':ce_row['Time']},ignore_index=True)
                        CEOiChangedf=moddf
                        #print(ce_row_Print)
        
                for index, pe_row in OIChange_df_pe.iterrows():
                    pe_row_base = df_pe.loc[((df_pe['Expiry'] == pe_row['Expiry']) & (df_pe['Strike'] == pe_row['Strike']) & (df_pe['Time'] == "14:00"))]
                    if(len(pe_row_base) == 0):
                         pe_row_base = df_pe.loc[((df_pe['Expiry'] == pe_row['Expiry']) & (df_pe['Strike'] == pe_row['Strike']) & (df_pe['Time'] == "13:45"))]
                    if(len(pe_row_base) == 0):
                         pe_row_base = df_pe.loc[((df_pe['Expiry'] == pe_row['Expiry']) & (df_pe['Strike'] == pe_row['Strike']) & (df_pe['Time'] == "14:15"))]
                    if(len(pe_row_base) != 0):
                        effectRow = pe_row_base.iloc[ 0 , : ]
                    Delta = (pe_row['OI_Change'] - effectRow['OI_Change'])
                    DeltaAbs = abs(Delta)
                    pe_row_print = df_pe.loc[((df_pe['Expiry'] == pe_row['Expiry']) & (df_pe['Strike'] == pe_row['Strike']))]
                    if(DeltaAbs >= Differece_2):
                        pe_row_Fut = df_stock.loc[((df_stock['Expiry'] == pe_row['Expiry']) & (df_stock['Type'] == "Fut") & (df_stock['Time'] == pe_row['Time']) )]
                        rowFut = pe_row_Fut.iloc[ 0 , : ]
                        moddf = PEOiChangedf.append({'Name':StockList[i],'CashPrice':rowFut['LTP'],'Strike':pe_row['Strike'],'TotalLots':pe_row['OI'],'ChngInLots':pe_row['OI_Change'],'Delta':Delta,'OptPrice':pe_row['LTP'],
                                'Expiry':pe_row['Expiry'],'Date':date1,'Time':pe_row['Time']},ignore_index=True)

                        
                        PEOiChangedf=moddf
                        #print(pe_row_print)
                    
    if(len(CEOiChangedf) > 0):
        print("#######################################################################################")
        print("CE - Max OI Change Stocks ")
        print("#######################################################################################")
        print(CEOiChangedf)
        
     
    if(len(PEOiChangedf) > 0):
        print("#######################################################################################")
        print("PE - Max OI Change Stocks ")
        print("#######################################################################################")
        print(PEOiChangedf)
      
    if((len(CEOiChangedf) > 0) | (len(PEOiChangedf) > 0) ):  
        try:
             AudioFile = ".//Play.mp3"
             playsound(AudioFile,block=False)
    
        except Exception as e:
            print("Anncement Failed "+str(e))
       
        
    

def Analysis(StockList,GlobalPercentage,logging,watchList,WhiteList):
    #Analyzing part now
    Tele_not_send=False
    Total_OI = 0
    current_time_min = time.strftime("%M")
    current_time_sec = time.strftime("%S")
    Effective_min = int(current_time_min)%Candle_timer
    timenow = datetime.now()
    current_time = (timenow - timedelta(minutes=Effective_min)).strftime("%H:%M")

    date1 = date.today()
    #while int(date1.weekday()) >=5  or is_public_holiday(date1):
    while ((int(date1.weekday()) >=5  or is_public_holiday(date1)) 
            and (str('%02d'%date1.day)!="20" and monthToNum(str('%02d'%date1.month)) == "01" and str(date1.year) == "2024" )) :
        date1=date1-timedelta(days=1)
    folder_Name = ".//" + str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year)
    
   
    current_time_hour = time.strftime("%H") 
    if( (int(current_time_hour) <= 8) or
        ((int(current_time_hour) <= 9) and (int(current_time_min) <=25)) or
       ((int(current_time_hour) >= 15) and (int(current_time_min) >=40)) or
        (int(current_time_hour) >= 16)):
        folder_Name = ".//" + str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year) + "_temp"
        Tele_not_send=True
    
    OiChangedf = pd.DataFrame(columns=['Name','CMP','Strike','CE_Change','PE_Change','Fut%','LotSize','Time','TotalLots','ChngInLots','OptPrice','Vwap','BullPoint','BearPoint','Expiry'])
    DoorValedf = pd.DataFrame(columns=['Name','Distance','Change','CMP','Strike','CE_Change','PE_Change','Fut%','LotSize','Time','TotalLots','ChngInLots','OptPrice','Vwap','BullPoint','BearPoint','Expiry'])
    DoorValeOptionsdf = pd.DataFrame(columns=['Name','Distance','Change','CMP','Strike','CE_Change','PE_Change','Fut%','LotSize','Time','TotalLots','ChngInLots','OptPrice','Vwap','BullPoint','BearPoint','Expiry'])

    PriceAbovevwapdf = pd.DataFrame(columns=['Name','CMP','Strike','CE_Change','PE_Change','Fut%','LotSize','Time','TotalLots','ChngInLots','OptPrice','Vwap','BullPoint','BearPoint','Expiry'])


    Nifty50OiChangedf = pd.DataFrame(columns=['Name','CMP','Strike','CE_Change','PE_Change','Fut%','LotSize','Time','TotalLots','ChngInLots','LTP','Vwap','BullPoint','BearPoint','Expiry'])

    Watchlistdf = pd.DataFrame(columns=['Name','CMP','Strike','CE_Change','PE_Change','Fut%','LotSize','Time','TotalLots','ChngInLots','LTP','BullPoint','BearPoint','Expiry'])


    CE_MaxOIChanged = pd.DataFrame(columns=['Name','CMP','FutP','oldStrike','oldLots','oldChange','oldPrice','newPrice','newChange','newLots','newStrike','Option_Type','Fut%','LotSize','PCR','Time'])

    PE_MaxOIChanged = pd.DataFrame(columns=['Name','CMP','FutP','oldStrike','oldLots','oldChange','oldPrice','newPrice','newChange','newLots','newStrike','Option_Type','Fut%','LotSize','PCR','Time'])
    StockCEUnderEye_df = pd.DataFrame(columns=['Name','OldClose','CMP','FutP','OldRedLevel','NewRedLevel','Fut%','Time'])
    StockPEUnderEye_df = pd.DataFrame(columns=['Name','OldClose','CMP','FutP','OldGreenLevel','NewGreenLevel','Fut%','Time'])

    BullCross = pd.DataFrame(columns=['Name','Old-G/R','New-G/R','Fut%','Time'])
    BearCross = pd.DataFrame(columns=['Name','Old-G/R','New-G/R','Fut%','Time'])
    
    CEOiChangedf = pd.DataFrame(columns=['Name','CMP','Strike','TotalLots','ChngInLots','OptPrice','Expiry'])
    PEOiChangedf = pd.DataFrame(columns=['Name','CMP','Strike','TotalLots','ChngInLots','OptPrice','Expiry'])
    OptionChangedf = pd.DataFrame(columns=['Name','CMP','PercentageCh','Fut%','TotalLots','ChngInLots'])
    for i in range (len(StockList)):
        
        if("M&amp;M" == StockList[i]):
            StockList[i] = "M%26M"
        elif("M&amp;MFIN" == StockList[i]):
            StockList[i] = "M%26MFIN"
        elif("L&amp;TFH" == StockList[i]):
            StockList[i] = "L%26TFH"
        file_name = folder_Name + "//" + StockList[i] + ".csv"
        #print(str(len(WhiteList)))
        if(os.path.exists(file_name) and ((StockList[i] in WhiteList) or (len(WhiteList) ==0))):
            df3 = pd.read_csv(file_name)
            
            FirstRow = SortedDataCE.iloc[ 0 , : ]
            df_stock = df3.loc[df3['Time'] == current_time]

            if(len(df_stock) == 0):
                print("Data Not found for current time: "+current_time + "  " +StockList[i] )
                continue

            Total_OI = df_stock['OI'].sum()
            
            df_fut = df_stock.loc[df_stock['Type'] == "Fut"]
            Fut_Change_OI = df_fut['OI_Change'].sum()
            Fut_total = df_fut['OI'].sum()
            futPer = Fut_Change_OI/(Fut_total-Fut_Change_OI)*100

            if(len(df_fut)):
                fut_row = df_fut.iloc[ 0 , : ]
                Fut_price = fut_row['LTP']
                ltp = fut_row['Cash_ltp']
                market_lot = fut_row['Lotsize']
                pChange = fut_row['PChange']
            else:
                print("Fut data issue "+StockList[i])

            df_ce = df_stock.loc[df_stock['Type'] == "CE"]
            itm_ce = df_ce.loc[df_ce['Strike'] <= ltp]
            itm_ce_OI = itm_ce['OI'].sum()
            CE_change = df_ce['OI_Change'].sum()
            CE_OI = df_ce['OI'].sum()
            BullishPoint = itm_ce_OI/CE_OI*100

            df_pe = df_stock.loc[df_stock['Type'] == "PE"]
            itm_pe = df_pe.loc[df_pe['Strike'] >= ltp]
            itm_pe_OI = itm_pe['OI'].sum()
            PE_change = df_pe['OI_Change'].sum()
            PE_OI = df_pe['OI'].sum()
            BearishPoint = itm_pe_OI/PE_OI*100
            PCR = PE_OI/CE_OI
            #CE_pert = CE_change*100/Total_OI_change
            #PE_pert = PE_change*100/Total_OI_change
            SortedDataCE = df_ce.sort_values(by=['OI_Change'],ascending=False)
            SortedDataPE = df_pe.sort_values(by=['OI_Change'],ascending=False)
            
            #Total OI in Option
            TotalLotst = CE_OI+PE_OI
            TotalChanget = CE_change + PE_change
            Option_Oi_Change = (TotalChanget)/(TotalLotst)*100

            if(Option_Oi_Change >= 20 and TotalLotst >=10000):
                moddf = OptionChangedf.append({'Name':StockList[i],'CMP':ltp,'PercentageCh':float(("%.2f" %Option_Oi_Change)),'Fut%':float(("%.2f" %futPer)),
                                                   'TotalLots':TotalLotst,'ChngInLots':TotalChanget
                                                   },ignore_index=True)
                OptionChangedf = moddf
                
            
    
            for j in range(len(SortedDataCE)):
                ce_row = SortedDataCE.iloc[ j , : ]
               
                ce_change_oi = float(ce_row['OI_Change'])
                totalLots = float(ce_row['OI'])
                ce_change_per = ce_change_oi*100/Total_OI
                temptime = time.strftime("%H:%M:%S")
                
                if((float(ce_row['LTP']) > float(ce_row['Vwap'])) and ce_change_oi >= 300):
                    moddf = PriceAbovevwapdf.append({'Name':StockList[i],'CMP':ltp,'Strike':ce_row['Strike'],'CE_Change': float(("%.2f" %ce_change_per)),'PE_Change': "NA"
                                                     ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':ce_change_oi,'OptPrice':ce_row['LTP'],
                                                     'Vwap':ce_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':ce_row['Expiry']},ignore_index=True)
                    PriceAbovevwapdf = moddf
                    
                ##Door-Door Options Only CE
                if(StockList[i] in stc_Nifty_50):
                    OptionsPernct = ce_change_oi/TotalLotst*100
                    difference  = ce_row['Strike'] - ltp
                    percentage = difference/ltp*100
                    Value = ce_row['Vwap']*ce_row['LTP']*ce_change_oi*market_lot/100000
                    #if(StockList[i] == "BHARTIARTL"):
                        #print(OptionsPernct)
                       # print(Value)
                    if(OptionsPernct > 1.5 and percentage >= 7 and Value >= 50):
                    #if(percentage >= 7 and Value >= 50):
                         moddf = DoorValeOptionsdf.append({'Name':StockList[i],'Distance':float(("%.2f" %percentage)),'Change':pChange,'CMP':ltp,'Strike':ce_row['Strike'],'CE_Change': float(("%.2f" %ce_change_per)),'PE_Change': "NA"
                            ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':ce_change_oi,'OptPrice':ce_row['LTP'],
                            'Vwap':ce_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':ce_row['Expiry']},ignore_index=True)
                         DoorValeOptionsdf=moddf
                
                

                if(ce_change_per >=GlobalPercentage):
                    if(logging ==0):
                        print("Found Entry CE: "+ str(ce_change_per))
                   
                    moddf = OiChangedf.append({'Name':StockList[i],'CMP':ltp,'Strike':ce_row['Strike'],'CE_Change': float(("%.2f" %ce_change_per)),'PE_Change': "NA"
                    ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':ce_change_oi,'OptPrice':ce_row['LTP'],
                    'Vwap':ce_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':ce_row['Expiry']},ignore_index=True)

                    if(logging == 0):
                        print(moddf)
                    OiChangedf=moddf
                    
                   


                    difference  = ce_row['Strike'] - ltp
                    percentage = difference/ltp*100
                   
                    if(percentage >= 8):
                        moddf = DoorValedf.append({'Name':StockList[i],'Distance':float(("%.2f" %percentage)),'Change':pChange,'CMP':ltp,'Strike':ce_row['Strike'],'CE_Change': float(("%.2f" %ce_change_per)),'PE_Change': "NA"
                        ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':ce_change_oi,'OptPrice':ce_row['LTP'],
                        'Vwap':ce_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':ce_row['Expiry']},ignore_index=True)
                        DoorValedf=moddf
                    
                else:
                    if(totalLots != 0):
                        ce_change_p = ce_change_oi*100/totalLots
                    else:
                        ce_change_p = 0
                    #if(StockList[i] == "INFY"):
                        #print("Found " + str(ce_row['Strike']) + " ltp " + str(ltp) + " and " + str(ce_change_p) )
                    if((ce_row['Strike']*.97 < ltp) and ce_change_p <= (-5) and ce_row['Strike'] > ltp 
                        and ce_change_oi < -250):
                        print("Found " + StockList[i] + " "+str(ce_row['Strike']) + " ltp " + str(ltp) + " and " + str(ce_change_p) )
                    #j = len(SortedDataCE)
           
            for j in range(len(SortedDataPE)):
           
                
                pe_row = SortedDataPE.iloc[ j , : ]
                
               
                        
                pe_change_oi = float(pe_row['OI_Change'])
                totalLots = float(pe_row['OI'])
               
                pe_change_per = pe_change_oi*100/Total_OI
                temptime = time.strftime("%H:%M:%S")
                
                if((float(pe_row['LTP']) > float(pe_row['Vwap'])) and pe_change_oi >= 300):
                        #print(pe_row['LTP'])
                        #print()
                        moddf = PriceAbovevwapdf.append({'Name':StockList[i],'CMP':ltp,'Strike':pe_row['Strike'],'CE_Change': "NA",'PE_Change': float(("%.2f" %pe_change_per))
                                                   ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':pe_change_oi,'OptPrice':pe_row['LTP'],
                                                   'Vwap':pe_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':pe_row['Expiry']},ignore_index=True)
                        PriceAbovevwapdf = moddf
                        
                ##Door-Door Options Only PE
                if(StockList[i] in stc_Nifty_50):
                    OptionsPernct = pe_change_oi/TotalLotst*100
                    difference  = pe_row['Strike'] - ltp
                    percentage = difference/ltp*100
                    Value = pe_row['Vwap']*pe_row['LTP']*pe_change_oi*market_lot/100000
                   
                    if(OptionsPernct > 1.5 and percentage >= 7 and Value >= 50):
                        moddf = DoorValeOptionsdf.append({'Name':StockList[i],'Distance':float(("%.2f" %percentage)),'Change':pChange,'CMP':ltp,'Strike':pe_row['Strike'],'CE_Change': "NA",'PE_Change': float(("%.2f" %pe_change_per))
                            ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':pe_change_oi,'OptPrice':pe_row['LTP'],
                            'Vwap':pe_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':pe_row['Expiry']},ignore_index=True)
                            
                        DoorValeOptionsdf=moddf
                        
                if (pe_change_per >= GlobalPercentage):
                    if(logging ==0):
                        print("Found Entry PE:"+ str(pe_change_per))
                   
                    moddf = OiChangedf.append({'Name':StockList[i],'CMP':ltp,'Strike':pe_row['Strike'],'CE_Change': "NA",'PE_Change': float(("%.2f" %pe_change_per))
                    ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':pe_change_oi,'OptPrice':pe_row['LTP'],
                    'Vwap':pe_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':pe_row['Expiry']},ignore_index=True)
        
                    if(logging == 0):
                        print(moddf)
                    OiChangedf=moddf
                    
                    


                    difference  = ltp - pe_row['Strike']
                    percentage = difference/ltp*100
                    if(percentage >= 8):
                        moddf = DoorValedf.append({'Name':StockList[i],'Distance':float(("%.2f" %percentage)),'Change':pChange,'CMP':ltp,'Strike':pe_row['Strike'],'CE_Change': "NA",'PE_Change': float(("%.2f" %pe_change_per))
                        ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':pe_change_oi,'OptPrice':pe_row['LTP'],
                        'Vwap':pe_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':pe_row['Expiry']},ignore_index=True)
                        DoorValedf=moddf
                else:
                    if(totalLots != 0):
                        pe_change_p = pe_change_oi*100/totalLots
                    else:
                        pe_change_p = 0
                    #if(StockList[i] == "INFY"):
                        #print("Found " + StockList[i] + " "+str(pe_row['Strike']) + " ltp " + str(ltp) + " and " + str(pe_change_p) )
                    if((pe_row['Strike']*.97 > ltp) and pe_change_p <= (-2) and pe_row['Strike'] < ltp 
                        and pe_change_oi < -50):
                        print("Found " + StockList[i] + " "+str(pe_row['Strike']) + " ltp " + str(ltp) + " and " + str(pe_change_p) )
                    #j = len(SortedDataCE)
           

            #Bull Bear Cross Over
            #Cross over ignoring focusing on actual values
            #date1 = getPreviousValidDay()
            #Currentpath= os.getcwd() +"\\finaloutput\\"
            #csv1 = Currentpath + StockList[i] +'t_OI.csv'
            #date_txt = str(date1.year)  + "-" +str('%02d'%date1.month) +"-"+ str('%02d'%date1.day)

            #vif(os.path.exists(csv1) and 0 ):  
            if(0 ): 
                data = pd.read_csv(csv1)
                Effective_row = data.loc[data['Date'] == date_txt]
                if(len(Effective_row) == 1):
                    row =  Effective_row.iloc[ 0 , : ]
                    #if(row['Trap'] < row['Trap2'] and BearishPoint < BullishPoint):
                    if(BullishPoint >= 34):
                        temptime = time.strftime("%H:%M:%S")
                        #','
                        moddf = BullCross.append({'Name':StockList[i],'Old-G/R':str(row['Trap'])+"/"+str(row['Trap2']),'New-G/R':str(float(("%.2f" %BullishPoint))) +"/"+str(float(("%.2f" %BearishPoint)))
                                ,'Fut%':float(("%.2f" %futPer)),'Time':temptime},ignore_index=True)
                        BullCross=moddf
                    #if(row['Trap'] > row['Trap2'] and BearishPoint > BullishPoint):
                    if(BearishPoint >= 20):
                        temptime = time.strftime("%H:%M:%S")
                        moddf = BearCross.append({'Name':StockList[i],'Old-G/R':str(row['Trap'])+"/"+str(row['Trap2']),'New-G/R':str(float(("%.2f" %BullishPoint))) +"/"+str(float(("%.2f" %BearishPoint)))
                                ,'Fut%':float(("%.2f" %futPer)),'Time':temptime},ignore_index=True)
                        BearCross=moddf

            #Lets check Max OI as per previous day
            #SortedDataMaxCE = df_ce.sort_values(by=['OI'],ascending=False)
            #SortedDataMaxPE = df_pe.sort_values(by=['OI'],ascending=False)
            #if(len(SortedDataMaxCE)==0):
                #continue
            #ce_row = SortedDataMaxCE.iloc[ 0 , : ]
            #date1 = getPreviousValidDay()
            #Currentpath= os.getcwd() +"\\finaloutput\\"
            #csv1 = Currentpath + 'fo'+ str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year) +'bhav.csv'
            #futPer = Future_delta/Fut_total*100
            #if(os.path.exists(csv1) and 0):
            if(0):
                
                df1 = pd.read_csv(csv1)
                row1 = df1.loc[df1['SYMBOL'] == StockList[i]]
                optionData = row1[row1['INSTRUMENT'] == 'OPTSTK']
                optionDataCE = optionData[optionData['OPTION_TYP'] == 'CE']
                PreviousDaySortedDataMaxCE = optionDataCE.sort_values(by=['OPEN_INT'],ascending=False)
                if(len(PreviousDaySortedDataMaxCE)):
                    selected_ce_row = PreviousDaySortedDataMaxCE.iloc[ 0 , : ]
                    
                    if( (ce_row['Strike'] != selected_ce_row['STRIKE_PR']) and (ce_row['Expiry'] == selected_ce_row['EXPIRY_DT'])):
                        #if( (ce_row['Strike'] <= ltp) and (ce_row['Expiry'] == selected_ce_row['EXPIRY_DT'])):
                            if("M%26M" == StockList[i]):
                                StockList[i] = "M&M"
                            elif("M%26MFIN" == StockList[i]):
                                StockList[i] = "M&MFIN"
                            elif("L%26TFH" == StockList[i]):
                                StockList[i] = "L&TFH"
                            ce_row_oldStrike_list = SortedDataMaxCE.loc[SortedDataMaxCE['Strike'] == selected_ce_row['STRIKE_PR'] ]
                            
                            for k in range (len(ce_row_oldStrike_list)):
                                temp_row = ce_row_oldStrike_list.iloc[ k , : ]
                                if(temp_row['Expiry'] == ce_row['Expiry'] ):
                                    ce_row_oldStrike = temp_row
                                    k = len(ce_row_oldStrike_list)

                           

                            if( (futPer >=5 and (int(ce_row_oldStrike['OI_Change']) > 100 or int(ce_row['OI_Change']) > 100)) or
                                (int(ce_row_oldStrike['OI_Change']) > 150 or int(ce_row['OI_Change']) > 150)):
                               
                                moddf = CE_MaxOIChanged.append({'Name':StockList[i],'CMP':ltp,'FutP':Fut_price,'oldStrike':selected_ce_row['STRIKE_PR'],'oldLots':ce_row_oldStrike['OI'],'oldChange':ce_row_oldStrike['OI_Change'],
                                                                'oldPrice':ce_row_oldStrike['LTP'],'newPrice':ce_row['LTP'],'newChange':ce_row['OI_Change'],'newLots':ce_row['OI'],'newStrike': ce_row['Strike'],
                                                             'Option_Type': "CE",'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'PCR':float(("%.2f" %PCR)),'Time':temptime},ignore_index=True)
        
                                if(logging == 0):
                                    print(moddf)
                                CE_MaxOIChanged=moddf
                            

                if(len(SortedDataMaxPE)==0):
                    continue
                pe_row = SortedDataMaxPE.iloc[ 0 , : ]
                optionDataPE = optionData[optionData['OPTION_TYP'] == 'PE']
                PreviousDaySortedDataMaxPE = optionDataPE.sort_values(by=['OPEN_INT'],ascending=False)
                if(len(PreviousDaySortedDataMaxPE)):
                    selected_pe_row = PreviousDaySortedDataMaxPE.iloc[ 0 , : ]
                
                    if( (pe_row['Strike'] != selected_pe_row['STRIKE_PR']) and (pe_row['Expiry'] == selected_pe_row['EXPIRY_DT'])):
                        #if( (pe_row['Strike'] >= ltp) and (pe_row['Expiry'] == selected_pe_row['EXPIRY_DT'])):
                            
                            if("M%26M" == StockList[i]):
                                StockList[i] = "M&M"
                            elif("M%26MFIN" == StockList[i]):
                                StockList[i] = "M&MFIN"
                            elif("L%26TFH" == StockList[i]):
                                StockList[i] = "L&TFH"

                            pe_row_oldStrike_list = SortedDataMaxPE.loc[SortedDataMaxPE['Strike'] == selected_pe_row['STRIKE_PR'] ]
                            for k in range (len(pe_row_oldStrike_list)):
                                temp_row = pe_row_oldStrike_list.iloc[ k , : ]
                                if(temp_row['Expiry'] == pe_row['Expiry'] ):
                                    pe_row_oldStrike = temp_row
                                    k = len(pe_row_oldStrike_list)

                            if((futPer >=5 and (int(pe_row_oldStrike['OI_Change']) > 100 or int(pe_row['OI_Change']) > 100)) or
                                (int(pe_row_oldStrike['OI_Change']) > 150 or int(pe_row['OI_Change']) > 150)):
                                
                                moddf = PE_MaxOIChanged.append({'Name':StockList[i],'CMP':ltp,'FutP':Fut_price,'oldStrike':selected_pe_row['STRIKE_PR'],'oldLots':pe_row_oldStrike['OI'],'oldChange':pe_row_oldStrike['OI_Change'],
                                                                'oldPrice':pe_row_oldStrike['LTP'],'newPrice':pe_row['LTP'],'newChange':pe_row['OI_Change'],'newLots':pe_row['OI'],'newStrike': pe_row['Strike'],
                                                             'Option_Type': "PE",'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'PCR':float(("%.2f" %PCR)),'Time':temptime},ignore_index=True)
        
                                if(logging == 0):
                                    print(moddf)
                                PE_MaxOIChanged=moddf

                    

            #if(os.path.exists(csv1) and 0):
            if(0):
               #Lets Check stock below green or above blue line for 2 days
                df1 = pd.read_csv(csv1)
                row1 = df1.loc[df1['SYMBOL'] == StockList[i]]
                optionData = row1[row1['INSTRUMENT'] == 'OPTSTK']
                optionDataCE = optionData[optionData['OPTION_TYP'] == 'CE']
                optionDataPE = optionData[optionData['OPTION_TYP'] == 'PE']
                PreviousDaySortedDataMaxCE = optionDataCE.sort_values(by=['OPEN_INT'],ascending=False)
                if(len(PreviousDaySortedDataMaxCE)):
                    selected_ce_row = PreviousDaySortedDataMaxCE.iloc[ 0 , : ]
                    if(float(selected_ce_row['CLOSE']) >= float(selected_ce_row['STRIKE_PR']) and
                       float(ltp) >= float(ce_row['Strike'])):
                        
                        moddf = StockCEUnderEye_df.append({'Name':StockList[i],'OldClose':selected_ce_row['CLOSE'],'CMP':ltp,'FutP':Fut_price,'OldRedLevel':selected_ce_row['STRIKE_PR'],
                                                            'NewRedLevel':ce_row['Strike'],
                                                         'Fut%':float(("%.2f" %futPer)),'Time':temptime},ignore_index=True)
        
                            
                        StockCEUnderEye_df=moddf

                PreviousDaySortedDataMaxPE = optionDataPE.sort_values(by=['OPEN_INT'],ascending=False)
                if(len(PreviousDaySortedDataMaxPE)):
                    selected_pe_row = PreviousDaySortedDataMaxPE.iloc[ 0 , : ]
                    if(len(SortedDataMaxPE)==0):
                        continue
                    pe_row = SortedDataMaxPE.iloc[ 0 , : ]
                    if(float(selected_pe_row['CLOSE']) <= float(selected_pe_row['STRIKE_PR']) and
                       float(ltp) <= float(pe_row['Strike'])):
                        
                        moddf = StockPEUnderEye_df.append({'Name':StockList[i],'OldClose':selected_pe_row['CLOSE'],'CMP':ltp,'FutP':Fut_price,'OldGreenLevel':selected_pe_row['STRIKE_PR'],
                                                            'NewGreenLevel':pe_row['Strike'],
                                                         'Fut%':float(("%.2f" %futPer)),'Time':temptime},ignore_index=True)
        
                            
                        StockPEUnderEye_df=moddf
        else:
            #print(StockList[i] + " not in Whitelist")
            OI_Percentage=0

        if(Total_OI !=0 and ((StockList[i] in stc_Nifty_50) or (StockList[i] in watchList))):
            #print("Nifty50 or watch:: "+StockList[i])
            #CE_change = sum(CE_OI_price_list)
            #PE_change = sum(PE_OI_price_list)
            #CE_pert = CE_change*100/Total_OI_change
            #PE_pert = PE_change*100/Total_OI_change

            SortedDataCE = df_ce.sort_values(by=['OI_Change'],ascending=False)
            SortedDataPE = df_pe.sort_values(by=['OI_Change'],ascending=False)

            for j in range(len(SortedDataCE)):
                ce_row = SortedDataCE.iloc[ j , : ]
                ce_change_oi = float(ce_row['OI_Change'])
                totalLots = float(ce_row['OI'])
            
                total_option = Total_OI - Fut_total
                ce_change_per = ce_change_oi*100/total_option
            
                temptime = time.strftime("%H:%M:%S")
                Value = market_lot*ce_change_oi*ce_row['LTP']/100000
        
                if((Value >=50 and ce_change_per >=1.5) or ce_change_per>= 10 ):
                    if(logging == 0):
                        print("Found Entry CE: "+ str(ce_change_per))
                        #print(ce_max_change)
                    
                    if(StockList[i] in stc_Nifty_50):
                        moddf = Nifty50OiChangedf.append({'Name':StockList[i],'CMP':ltp,'Strike':ce_row['Strike'],'CE_Change': float(("%.2f" %ce_change_per)),'PE_Change': "NA"
                        ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':ce_change_oi,'LTP':ce_row['LTP'],
                        'Vwap':ce_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':ce_row['Expiry']},ignore_index=True)
        
                        if(logging == 0):
                            print(moddf)
                        Nifty50OiChangedf=moddf
                    else:
                        moddf = Watchlistdf.append({'Name':StockList[i],'CMP':ltp,'Strike':ce_row['Strike'],'CE_Change': float(("%.2f" %ce_change_per)),'PE_Change': "NA"
                        ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':ce_change_oi,'LTP':ce_row['LTP'],
                        'Vwap':ce_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':ce_row['Expiry']},ignore_index=True)
        
                        if(logging == 0):
                            print(moddf)
                        Watchlistdf=moddf

                    difference  = ce_row['Strike'] - ltp
                    percentage = difference/ltp*100
                    #if(StockList[i] == "BHARTIARTL"):
                        #print(ce_change_per)
                        #print(Value)
                    if(percentage >= 8):
                        moddf = DoorValedf.append({'Name':StockList[i],'Distance':float(("%.2f" %percentage)),'Change':pChange,'CMP':ltp,'Strike':ce_row['Strike'],'CE_Change': float(("%.2f" %ce_change_per)),'PE_Change': "NA"
                        ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':ce_change_oi,'OptPrice':ce_row['LTP'],
                        'Vwap':ce_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':ce_row['Expiry']},ignore_index=True)
                        DoorValedf=moddf
                else:
                    j = len(SortedDataCE)

            for j in range(len(SortedDataPE)):
                pe_row = SortedDataPE.iloc[ j , : ]
                pe_change_oi = float(pe_row['OI_Change'])
                totalLots = float(pe_row['OI'])
                total_option = Total_OI - Fut_total
                pe_change_per = pe_change_oi*100/total_option
                Value = market_lot*pe_change_oi*pe_row['LTP']/100000
                if ((Value >=50 and pe_change_per >=1.5) or pe_change_per >= 10):
                    if(logging == 0):
                        print("Found Entry PE:"+ str(pe_change_per))
                    
                    if(StockList[i] in stc_Nifty_50):
                        moddf = Nifty50OiChangedf.append({'Name':StockList[i],'CMP':ltp,'Strike':pe_row['Strike'],'CE_Change': "NA",'PE_Change': float(("%.2f" %pe_change_per))
                        ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':pe_change_oi,'LTP':pe_row['LTP'],
                        'Vwap':pe_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':pe_row['Expiry']},ignore_index=True)

                        if(logging == 0):
                            print(moddf)
                        Nifty50OiChangedf=moddf
                    else:
                        moddf = Watchlistdf.append({'Name':StockList[i],'CMP':ltp,'Strike':pe_row['Strike'],'CE_Change': "NA",'PE_Change': float(("%.2f" %pe_change_per))
                        ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':pe_change_oi,'OptPrice':pe_row['LTP'],
                        'Vwap':pe_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':pe_row['Expiry']},ignore_index=True)

                        if(logging == 0):
                            print(moddf)
                        Watchlistdf=moddf

                    difference  = ltp - pe_row['Strike']
                    percentage = difference/ltp*100
                    if(percentage >= 8):
                        moddf = DoorValedf.append({'Name':StockList[i],'Distance':float(("%.2f" %percentage)),'Change':pChange,'CMP':ltp,'Strike':pe_row['Strike'],'CE_Change': "NA",'PE_Change': float(("%.2f" %pe_change_per))
                        ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':pe_change_oi,'LTP':pe_row['LTP'],
                        'Vwap':pe_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':pe_row['Expiry']},ignore_index=True)
                        DoorValedf=moddf
                else:
                    j = len(SortedDataPE)

    
        #Logic for Max OI change in counts   
        if(os.path.exists(file_name) and len(df_ce)  ):
            SortedDataCE = df_ce.sort_values(by=['OI_Change'],ascending=False)
            SortedDataPE = df_pe.sort_values(by=['OI_Change'],ascending=False)             
       
        
            ce_row = SortedDataCE.iloc[ 0 , : ]
            
            moddf = CEOiChangedf.append({'Name':StockList[i],'CMP':ltp,'Strike':ce_row['Strike'],'TotalLots':ce_row['OI'],'ChngInLots':ce_row['OI_Change'],'OptPrice':ce_row['LTP'],
                                         'Expiry':ce_row['Expiry']},ignore_index=True)

                    
            CEOiChangedf=moddf

            pe_row = SortedDataPE.iloc[ 0 , : ]
            
            moddf = PEOiChangedf.append({'Name':StockList[i],'CMP':ltp,'Strike':pe_row['Strike'],'TotalLots':pe_row['OI'],'ChngInLots':pe_row['OI_Change'],'OptPrice':pe_row['LTP'],
                                         'Expiry':pe_row['Expiry']},ignore_index=True)

                    
            PEOiChangedf=moddf
    

    if(len(Watchlistdf)):
        print("#######################################################################################")
        print("Watchlist only")
        print("#######################################################################################")
        #print(Watchlistdf)
        print("\n")

    

    if(len(CE_MaxOIChanged)):
        print("#######################################################################################")
        print("CE - Max OI Change Stocks ")
        print("#######################################################################################")
        print(CE_MaxOIChanged)
        print("\n")

    if(len(PE_MaxOIChanged)):
        print("#######################################################################################")
        print("PE - Max OI Change Stocks ")
        print("#######################################################################################")
        print(PE_MaxOIChanged)
        print("\n")

    if(len(StockCEUnderEye_df)):
        print("#######################################################################################")
        print("CE - Stock Above RED line ")
        print("#######################################################################################")
        print(StockCEUnderEye_df)
        print("\n")

    if(len(StockPEUnderEye_df)):
        print("#######################################################################################")
        print("CE - Stock below GREEN line ")
        print("#######################################################################################")
        print(StockPEUnderEye_df)
        print("\n")

    
    if(len(OiChangedf)):
        print("#######################################################################################")
        print("Actual 31...... ")
        print("#######################################################################################")
        print("\n")
        print(OiChangedf)
        OiChangedf.to_csv("31.csv",index=False)
        print("\n")

    if(len(Nifty50OiChangedf)):
        print("#######################################################################################")
        print("Nifty Fifty Option only")
        print("#######################################################################################")
        print(Nifty50OiChangedf)
        Nifty50OiChangedf.to_csv("nifty50.csv",index=False)
        print("\n")


    if(len(DoorValedf)):
        print("#######################################################################################")
        print("Dooorrr Vale ........")
        print("#######################################################################################")
        print(DoorValedf)
        DoorValedf.to_csv("Door.csv",index=False)
        
        
    #if(len(DoorValeOptionsdf)):
        #print("#######################################################################################")
        #print("Dooorrr OPTIONS Vale ........")
        #print("#######################################################################################")
        #print(DoorValeOptionsdf)
        #DoorValedf.to_csv("Door.csv",index=False)
        
        
        
    #if(len(PriceAbovevwapdf)):
    #    print("#######################################################################################")
    #    print("VWAP Vale ........")
    #    print("#######################################################################################")
    #    print(PriceAbovevwapdf)
    #    tempname=datetime.now().strftime("%Y_%m_%d")
    #    PriceAbovevwapdf.to_csv("PriceAbovevwap"+ tempname + ".csv",index=False)
        
       
    if(len(OptionChangedf)):
        print("#######################################################################################")
        print("Options Activity ........")
        print("#######################################################################################")
        print(OptionChangedf)
        tempname=datetime.now().strftime("%Y_%m_%d")
        OptionChangedf.to_csv("OptionsActivity"+ tempname + ".csv",index=False)      
        
    """if(len(BullCross)):
        #NewMerged = pd.merge(BullCross, Nifty50OiChangedf, on="Name")
        #Selected_Name =  Nifty50OiChangedf['Name'].unique()
        #NewMerged = BullCross[Nifty50OiChangedf['Name'].isin(BullCross['Name'])]

        print("#######################################################################################")
        print("Green Line CrossOver")
        print("#######################################################################################")
        print(NewMerged)
        print("\n")

    if(len(BearCross)):
        NewMergedBear = pd.merge(BearCross, Nifty50OiChangedf, on="Name")
        print("#######################################################################################")
        print("Red Line CrossOver")
        print("#######################################################################################")
        print(NewMergedBear)
        print("\n")
        """

        #print("\n")
  
    #print("Going to Calculate Max Change top 10")    
    try:
        AudioFile = Currentpath + "\\Play.mp3"
        playsound(AudioFile)
    
    except Exception as e:
        print("Anncement Failed "+str(e))
        #time.sleep(30)
    """if(len(CEOiChangedf)):    
        SortedDataStocksCE = CEOiChangedf.sort_values(by=['ChngInLots'],ascending=False)
        SortedDataStocksPE = PEOiChangedf.sort_values(by=['ChngInLots'],ascending=False)
     
        print("#######################################################################################")
        print("CE - Max OI Change Stocks -- Top 10 ")
        print("#######################################################################################")
        print(SortedDataStocksCE.head(10))
     
        print("#######################################################################################")
        print("PE - Max OI Change Stocks -- Top 10")
        print("#######################################################################################")
        print(SortedDataStocksPE.head(10))

    result = CE_MaxOIChanged.append(PE_MaxOIChanged)
    Sorted_result = result.sort_values(by=['Name'],ascending=True)

    #print(Sorted_result)
    skip = False
    for j in range (len(Sorted_result)):
        if skip:
            skip = False
            continue
        pe_row = Sorted_result.iloc[ j , : ]
        if(j+1 < len(Sorted_result)):
            pe_row2 = Sorted_result.iloc[ j+1 , : ]
            if(pe_row['Name'] == pe_row2['Name']):
                print("Same Stock:")
                Str_to_send = "Name : *" + pe_row['Name'] + "*\nCash Price : " + str(pe_row['CMP']) + "\nFuture Price : " + str(pe_row['FutP']) + "\nFuture OI % : " + str(pe_row['Fut%']) + "\nOption Type : *" + str(pe_row['Option_Type']) + "*\n*O Strk* " + str(pe_row['oldStrike']) +  " *OI* " +str(pe_row['oldLots'])  +" *Chg* " + str(pe_row['oldChange']) + " *CMP* " + str(pe_row['oldPrice']) + "\n*N Strk* "+ str(pe_row['newStrike']) +  " *OI* " +str(pe_row['newLots'])  +" *Chg* " + str(pe_row['newChange']) + " *CMP* " + str(pe_row['newPrice'])  + "\nOption Type : *" + str(pe_row2['Option_Type']) + "*\n*O Strk* " + str(pe_row2['oldStrike']) +  " *OI* " +str(pe_row2['oldLots'])  +" *Chg* " + str(pe_row2['oldChange']) + " *CMP* " + str(pe_row2['oldPrice']) + "\n*N Strk* " + str(pe_row2['newStrike']) +  " *OI* " + str(pe_row2['newLots'])  +" *Chg* " + str(pe_row2['newChange']) + " *CMP* " + str(pe_row2['newPrice']) + "\nPCR : " + str(pe_row['PCR']) + "\nLot Size : " + str(pe_row['LotSize'])
                skip = True
            else:
                Str_to_send = "Name : *" + pe_row['Name'] + "*\nCash Price : " + str(pe_row['CMP']) + "\nFuture Price : " + str(pe_row['FutP']) +"\nFuture OI % : " + str(pe_row['Fut%']) + "\nOption Type : *"+ str(pe_row['Option_Type'])+"*\n*O Strk* " + str(pe_row['oldStrike']) +  " *OI* " +str(pe_row['oldLots'])  +" *Chg* " + str(pe_row['oldChange']) + " *CMP* " + str(pe_row['oldPrice']) + "\n*N Strk* "+ str(pe_row['newStrike']) +  " *OI* " +str(pe_row['newLots'])  +" *Chg* " + str(pe_row['newChange']) + " *CMP* " + str(pe_row['newPrice'])  + "\nPCR : " + str(pe_row['PCR']) + "\nLot Size : " + str(pe_row['LotSize'])
                
        else:
            Str_to_send = "Name : *" + pe_row['Name'] + "*\nCash Price : " + str(pe_row['CMP']) + "\nFuture Price : " + str(pe_row['FutP']) +"\nFuture OI % : " + str(pe_row['Fut%']) + "\nOption Type : *"+ str(pe_row['Option_Type'])+"*\n*O Strk* " + str(pe_row['oldStrike']) +  " *OI* " +str(pe_row['oldLots'])  +" *Chg* " + str(pe_row['oldChange']) + " *CMP* " + str(pe_row['oldPrice']) + "\n*N Strk* "+ str(pe_row['newStrike']) +  " *OI* " +str(pe_row['newLots'])  +" *Chg* " + str(pe_row['newChange']) + " *CMP* " + str(pe_row['newPrice']) + "\nPCR : " + str(pe_row['PCR']) + "\nLot Size : " + str(pe_row['LotSize'])
        #print(Str_to_send)
        #print(str(j))
        #send(Str_to_send,Common_chatid,Common_token,Tele_not_send)
        #send(Str_to_send,Stocks_chatid,Stocks_token,Tele_not_send)"""

    """for j in range (len(CE_MaxOIChanged)):
        pe_row = CE_MaxOIChanged.iloc[ j , : ]
        Str_to_send = "Name : *" + pe_row['Name'] + "*\nCash Price : " + str(pe_row['CMP']) + "\nFuture Price : " + str(pe_row['FutP']) +"\n*O Strk* " + str(pe_row['oldStrike']) +  " *OI* " +str(pe_row['oldLots'])  +" *Chg* " + str(pe_row['oldChange']) + "*CMP* " + str(pe_row['oldPrice']) + "\n*N Strk* "+ str(pe_row['newStrike']) +  " *OI* " +str(pe_row['newLots'])  +" *Chg* " + str(pe_row['newChange']) + "\n*CMP* " + str(pe_row['newPrice']) + "\nOption Type : *CE*\nFuture OI % : " + str(pe_row['Fut%']) + "\nPCR : " + str(pe_row['PCR']) + "\nLot Size : " + str(pe_row['LotSize'])
        send(Str_to_send,Common_chatid,Common_token,Tele_not_send)
        send(Str_to_send,Stocks_chatid,Stocks_token,Tele_not_send)

    for j in range (len(PE_MaxOIChanged)):
        pe_row = PE_MaxOIChanged.iloc[ j , : ]
        Str_to_send = "Name : *" + pe_row['Name'] + "*\nCash Price : " + str(pe_row['CMP']) + "\nFuture Price : " + str(pe_row['FutP']) +"\nOld Strike : " + str(pe_row['oldStrike']) +  " *Lots*: " +str(pe_row['oldLots'])  +" *Change*: " + str(pe_row['oldChange']) + "\nNew Strike : "+ str(pe_row['newStrike']) +  " *Lots*: " +str(pe_row['newLots'])  +" *Change*: " + str(pe_row['newChange']) + "\nOption Type : *PE*\nFuture OI % : " + str(pe_row['Fut%']) + "\nPCR : " + str(pe_row['PCR'])+ "\nLot Size : " + str(pe_row['LotSize'])
        send(Str_to_send,Common_chatid,Common_token,Tele_not_send)
        send(Str_to_send,Stocks_chatid,Stocks_token,Tele_not_send)"""

    
def Analysis9(StockList,GlobalPercentage,logging,watchList,WhiteList):
    #Analyzing part now
    Tele_not_send=False
    Total_OI = 0
    current_time_min = time.strftime("%M")
    current_time_sec = time.strftime("%S")
    Effective_min = int(current_time_min)%Candle_timer
    timenow = datetime.now()
    current_time = (timenow - timedelta(minutes=Effective_min)).strftime("%H:%M")

    date1 = date.today()
    while int(date1.weekday()) >=5  or is_public_holiday(date1):
        date1=date1-timedelta(days=1)
    folder_Name = ".//" + str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year)
    
   
    current_time_hour = time.strftime("%H") 
    if( (int(current_time_hour) <= 8) or
        ((int(current_time_hour) <= 9) and (int(current_time_min) <=25)) or
       ((int(current_time_hour) >= 15) and (int(current_time_min) >=40)) or
        (int(current_time_hour) >= 16)):
        folder_Name = ".//" + str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year) + "_temp"
        Tele_not_send=True
    
    OiChangedf = pd.DataFrame(columns=['Name','CMP','Strike','CE_Change','PE_Change','Fut%','LotSize','Time','TotalLots','ChngInLots','OptPrice','Vwap','BullPoint','BearPoint','Expiry'])
    DoorValedf = pd.DataFrame(columns=['Name','Distance','Change','CMP','Strike','CE_Change','PE_Change','Fut%','LotSize','Time','TotalLots','ChngInLots','OptPrice','Vwap','BullPoint','BearPoint','Expiry'])
    PriceAbovevwapdf = pd.DataFrame(columns=['Name','CMP','Strike','CE_Change','PE_Change','Fut%','LotSize','Time','TotalLots','ChngInLots','OptPrice','Vwap','BullPoint','BearPoint','Expiry'])


    Nifty50OiChangedf = pd.DataFrame(columns=['Name','CMP','Strike','CE_Change','PE_Change','Fut%','LotSize','Time','TotalLots','ChngInLots','LTP','Vwap','BullPoint','BearPoint','Expiry'])

    Watchlistdf = pd.DataFrame(columns=['Name','CMP','Strike','CE_Change','PE_Change','Fut%','LotSize','Time','TotalLots','ChngInLots','LTP','BullPoint','BearPoint','Expiry'])


    CE_MaxOIChanged = pd.DataFrame(columns=['Name','CMP','FutP','oldStrike','oldLots','oldChange','oldPrice','newPrice','newChange','newLots','newStrike','Option_Type','Fut%','LotSize','PCR','Time'])

    PE_MaxOIChanged = pd.DataFrame(columns=['Name','CMP','FutP','oldStrike','oldLots','oldChange','oldPrice','newPrice','newChange','newLots','newStrike','Option_Type','Fut%','LotSize','PCR','Time'])
    StockCEUnderEye_df = pd.DataFrame(columns=['Name','OldClose','CMP','FutP','OldRedLevel','NewRedLevel','Fut%','Time'])
    StockPEUnderEye_df = pd.DataFrame(columns=['Name','OldClose','CMP','FutP','OldGreenLevel','NewGreenLevel','Fut%','Time'])

    BullCross = pd.DataFrame(columns=['Name','Old-G/R','New-G/R','Fut%','Time'])
    BearCross = pd.DataFrame(columns=['Name','Old-G/R','New-G/R','Fut%','Time'])
    
    CEOiChangedf = pd.DataFrame(columns=['Name','CMP','Strike','TotalLots','ChngInLots','OptPrice','Expiry'])
    PEOiChangedf = pd.DataFrame(columns=['Name','CMP','Strike','TotalLots','ChngInLots','OptPrice','Expiry'])
    OptionChangedf = pd.DataFrame(columns=['Name','CMP','PercentageCh','Fut%','TotalLots','ChngInLots'])
    for i in range (len(StockList)):
        
        
        file_name = folder_Name + "//" + StockList[i] + ".csv"
        #print(str(len(WhiteList)))
        if(os.path.exists(file_name) and ((StockList[i] in WhiteList) or (len(WhiteList) ==0))):
            df3 = pd.read_csv(file_name)

            
            df_stock = df3.loc[df3['Time'] == current_time]

            if(len(df_stock) == 0):
                print("Data Not found for current time: "+current_time + "  " +StockList[i] )
                continue

            Total_OI = df_stock['OI'].sum()
            
            df_fut = df_stock.loc[df_stock['Type'] == "Fut"]
            Fut_Change_OI = df_fut['OI_Change'].sum()
            Fut_total = df_fut['OI'].sum()
            futPer = Fut_Change_OI/(Fut_total-Fut_Change_OI)*100

            if(len(df_fut)):
                fut_row = df_fut.iloc[ 0 , : ]
                Fut_price = fut_row['LTP']
                ltp = fut_row['Cash_ltp']
                market_lot = fut_row['Lotsize']
                pChange = fut_row['PChange']
            else:
                print("Fut data issue "+StockList[i])

            df_ce = df_stock.loc[df_stock['Type'] == "CE"]
            itm_ce = df_ce.loc[df_ce['Strike'] <= ltp]
            itm_ce_OI = itm_ce['OI'].sum()
            CE_change = df_ce['OI_Change'].sum()
            date1 = getPreviousValidDay()
            Currentpath= os.getcwd() +"\\finaloutput\\"
            csv1 = Currentpath + 'fo'+ str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year) +'bhav.csv'
            #futPer = Future_delta/Fut_total*100
            if(os.path.exists(csv1)):
                
                df1 = pd.read_csv(csv1)
                row1 = df1.loc[df1['SYMBOL'] == StockList[i]]
                optionData = row1[row1['INSTRUMENT'] == 'OPTSTK']
                optionDataCE = optionData[optionData['OPTION_TYP'] == 'CE']
                #Traverse CE to correct data
                #SelectedStrike = optionDataCE.[optionData['STRIKE_PR'] == df_ce['Strike']]
                
            CE_OI = df_ce['OI'].sum()
            BullishPoint = itm_ce_OI/CE_OI*100

            df_pe = df_stock.loc[df_stock['Type'] == "PE"]
            itm_pe = df_pe.loc[df_pe['Strike'] >= ltp]
            itm_pe_OI = itm_pe['OI'].sum()
            PE_change = df_pe['OI_Change'].sum()
            PE_OI = df_pe['OI'].sum()
            BearishPoint = itm_pe_OI/PE_OI*100
            PCR = PE_OI/CE_OI
            #CE_pert = CE_change*100/Total_OI_change
            #PE_pert = PE_change*100/Total_OI_change
            SortedDataCE = df_ce.sort_values(by=['OI_Change'],ascending=False)
            SortedDataPE = df_pe.sort_values(by=['OI_Change'],ascending=False)
            
            #Total OI in Option
            TotalLotst = CE_OI+PE_OI
            TotalChanget = CE_change + PE_change
            Option_Oi_Change = (TotalChanget)/(TotalLotst)*100

            if(Option_Oi_Change >= 20 and TotalLotst >=10000):
                moddf = OptionChangedf.append({'Name':StockList[i],'CMP':ltp,'PercentageCh':float(("%.2f" %Option_Oi_Change)),'Fut%':float(("%.2f" %futPer)),
                                                   'TotalLots':TotalLotst,'ChngInLots':TotalChanget
                                                   },ignore_index=True)
                OptionChangedf = moddf
            
    
            for j in range(len(SortedDataCE)):
                ce_row = SortedDataCE.iloc[ j , : ]
               
                ce_change_oi = float(ce_row['OI_Change'])
                totalLots = float(ce_row['OI'])
                ce_change_per = ce_change_oi*100/Total_OI
                temptime = time.strftime("%H:%M:%S")
                
                if((float(ce_row['LTP']) > float(ce_row['Vwap'])) and ce_change_oi >= 300):
                    moddf = PriceAbovevwapdf.append({'Name':StockList[i],'CMP':ltp,'Strike':ce_row['Strike'],'CE_Change': float(("%.2f" %ce_change_per)),'PE_Change': "NA"
                                                     ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':ce_change_oi,'OptPrice':ce_row['LTP'],
                                                     'Vwap':ce_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':ce_row['Expiry']},ignore_index=True)
                    PriceAbovevwapdf = moddf

                if(ce_change_per >=GlobalPercentage):
                    if(logging ==0):
                        print("Found Entry CE: "+ str(ce_change_per))
                   
                    moddf = OiChangedf.append({'Name':StockList[i],'CMP':ltp,'Strike':ce_row['Strike'],'CE_Change': float(("%.2f" %ce_change_per)),'PE_Change': "NA"
                    ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':ce_change_oi,'OptPrice':ce_row['LTP'],
                    'Vwap':ce_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':ce_row['Expiry']},ignore_index=True)

                    if(logging == 0):
                        print(moddf)
                    OiChangedf=moddf
                    
                   


                    difference  = ce_row['Strike'] - ltp
                    percentage = difference/ltp*100
                    if(percentage >= 8):
                        moddf = DoorValedf.append({'Name':StockList[i],'Distance':float(("%.2f" %percentage)),'Change':pChange,'CMP':ltp,'Strike':ce_row['Strike'],'CE_Change': float(("%.2f" %ce_change_per)),'PE_Change': "NA"
                        ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':ce_change_oi,'OptPrice':ce_row['LTP'],
                        'Vwap':ce_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':ce_row['Expiry']},ignore_index=True)
                        DoorValedf=moddf
                    
                else:
                    j = len(SortedDataCE)
           
            for j in range(len(SortedDataPE)):
           
                
                pe_row = SortedDataPE.iloc[ j , : ]
                
               
                        
                pe_change_oi = float(pe_row['OI_Change'])
                totalLots = float(pe_row['OI'])
               
                pe_change_per = pe_change_oi*100/Total_OI
                temptime = time.strftime("%H:%M:%S")
                
                if((float(pe_row['LTP']) > float(pe_row['Vwap'])) and pe_change_oi >= 300):
                        #print(pe_row['LTP'])
                        #print()
                        moddf = PriceAbovevwapdf.append({'Name':StockList[i],'CMP':ltp,'Strike':pe_row['Strike'],'CE_Change': "NA",'PE_Change': float(("%.2f" %pe_change_per))
                                                   ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':pe_change_oi,'OptPrice':pe_row['LTP'],
                                                   'Vwap':pe_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':pe_row['Expiry']},ignore_index=True)
                        PriceAbovevwapdf = moddf
                        
                if (pe_change_per >= GlobalPercentage):
                    if(logging ==0):
                        print("Found Entry PE:"+ str(pe_change_per))
                   
                    moddf = OiChangedf.append({'Name':StockList[i],'CMP':ltp,'Strike':pe_row['Strike'],'CE_Change': "NA",'PE_Change': float(("%.2f" %pe_change_per))
                    ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':pe_change_oi,'OptPrice':pe_row['LTP'],
                    'Vwap':pe_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':pe_row['Expiry']},ignore_index=True)
        
                    if(logging == 0):
                        print(moddf)
                    OiChangedf=moddf
                    
                    


                    difference  = ltp - pe_row['Strike']
                    percentage = difference/ltp*100
                    if(percentage >= 8):
                        moddf = DoorValedf.append({'Name':StockList[i],'Distance':float(("%.2f" %percentage)),'Change':pChange,'CMP':ltp,'Strike':pe_row['Strike'],'CE_Change': "NA",'PE_Change': float(("%.2f" %pe_change_per))
                        ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':pe_change_oi,'OptPrice':pe_row['LTP'],
                        'Vwap':pe_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':pe_row['Expiry']},ignore_index=True)
                        DoorValedf=moddf
                else:
                    j = len(SortedDataPE)

            #Bull Bear Cross Over
            #Cross over ignoring focusing on actual values
            date1 = getPreviousValidDay()
            Currentpath= os.getcwd() +"\\finaloutput\\"
            csv1 = Currentpath + StockList[i] +'t_OI.csv'
            date_txt = str(date1.year)  + "-" +str('%02d'%date1.month) +"-"+ str('%02d'%date1.day)

            if(os.path.exists(csv1)):    
                data = pd.read_csv(csv1)
                Effective_row = data.loc[data['Date'] == date_txt]
                if(len(Effective_row) == 1):
                    row =  Effective_row.iloc[ 0 , : ]
                    #if(row['Trap'] < row['Trap2'] and BearishPoint < BullishPoint):
                    if(BullishPoint >= 34):
                        temptime = time.strftime("%H:%M:%S")
                        #','
                        moddf = BullCross.append({'Name':StockList[i],'Old-G/R':str(row['Trap'])+"/"+str(row['Trap2']),'New-G/R':str(float(("%.2f" %BullishPoint))) +"/"+str(float(("%.2f" %BearishPoint)))
                                ,'Fut%':float(("%.2f" %futPer)),'Time':temptime},ignore_index=True)
                        BullCross=moddf
                    #if(row['Trap'] > row['Trap2'] and BearishPoint > BullishPoint):
                    if(BearishPoint >= 20):
                        temptime = time.strftime("%H:%M:%S")
                        moddf = BearCross.append({'Name':StockList[i],'Old-G/R':str(row['Trap'])+"/"+str(row['Trap2']),'New-G/R':str(float(("%.2f" %BullishPoint))) +"/"+str(float(("%.2f" %BearishPoint)))
                                ,'Fut%':float(("%.2f" %futPer)),'Time':temptime},ignore_index=True)
                        BearCross=moddf

            #Lets check Max OI as per previous day
            SortedDataMaxCE = df_ce.sort_values(by=['OI'],ascending=False)
            SortedDataMaxPE = df_pe.sort_values(by=['OI'],ascending=False)
            if(len(SortedDataMaxCE)==0):
                continue
            ce_row = SortedDataMaxCE.iloc[ 0 , : ]
            date1 = getPreviousValidDay()
            Currentpath= os.getcwd() +"\\finaloutput\\"
            csv1 = Currentpath + 'fo'+ str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year) +'bhav.csv'
            #futPer = Future_delta/Fut_total*100
            if(os.path.exists(csv1) and 0):
                
                df1 = pd.read_csv(csv1)
                row1 = df1.loc[df1['SYMBOL'] == StockList[i]]
                optionData = row1[row1['INSTRUMENT'] == 'OPTSTK']
                optionDataCE = optionData[optionData['OPTION_TYP'] == 'CE']
                PreviousDaySortedDataMaxCE = optionDataCE.sort_values(by=['OPEN_INT'],ascending=False)
                if(len(PreviousDaySortedDataMaxCE)):
                    selected_ce_row = PreviousDaySortedDataMaxCE.iloc[ 0 , : ]
                    
                    if( (ce_row['Strike'] != selected_ce_row['STRIKE_PR']) and (ce_row['Expiry'] == selected_ce_row['EXPIRY_DT'])):
                        #if( (ce_row['Strike'] <= ltp) and (ce_row['Expiry'] == selected_ce_row['EXPIRY_DT'])):
                            if("M%26M" == StockList[i]):
                                StockList[i] = "M&M"
                            elif("M%26MFIN" == StockList[i]):
                                StockList[i] = "M&MFIN"
                            elif("L%26TFH" == StockList[i]):
                                StockList[i] = "L&TFH"
                            ce_row_oldStrike_list = SortedDataMaxCE.loc[SortedDataMaxCE['Strike'] == selected_ce_row['STRIKE_PR'] ]
                            
                            for k in range (len(ce_row_oldStrike_list)):
                                temp_row = ce_row_oldStrike_list.iloc[ k , : ]
                                if(temp_row['Expiry'] == ce_row['Expiry'] ):
                                    ce_row_oldStrike = temp_row
                                    k = len(ce_row_oldStrike_list)

                           

                            if( (futPer >=5 and (int(ce_row_oldStrike['OI_Change']) > 100 or int(ce_row['OI_Change']) > 100)) or
                                (int(ce_row_oldStrike['OI_Change']) > 150 or int(ce_row['OI_Change']) > 150)):
                               
                                moddf = CE_MaxOIChanged.append({'Name':StockList[i],'CMP':ltp,'FutP':Fut_price,'oldStrike':selected_ce_row['STRIKE_PR'],'oldLots':ce_row_oldStrike['OI'],'oldChange':ce_row_oldStrike['OI_Change'],
                                                                'oldPrice':ce_row_oldStrike['LTP'],'newPrice':ce_row['LTP'],'newChange':ce_row['OI_Change'],'newLots':ce_row['OI'],'newStrike': ce_row['Strike'],
                                                             'Option_Type': "CE",'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'PCR':float(("%.2f" %PCR)),'Time':temptime},ignore_index=True)
        
                                if(logging == 0):
                                    print(moddf)
                                CE_MaxOIChanged=moddf
                            

                if(len(SortedDataMaxPE)==0):
                    continue
                pe_row = SortedDataMaxPE.iloc[ 0 , : ]
                optionDataPE = optionData[optionData['OPTION_TYP'] == 'PE']
                PreviousDaySortedDataMaxPE = optionDataPE.sort_values(by=['OPEN_INT'],ascending=False)
                if(len(PreviousDaySortedDataMaxPE)):
                    selected_pe_row = PreviousDaySortedDataMaxPE.iloc[ 0 , : ]
                
                    if( (pe_row['Strike'] != selected_pe_row['STRIKE_PR']) and (pe_row['Expiry'] == selected_pe_row['EXPIRY_DT'])):
                        #if( (pe_row['Strike'] >= ltp) and (pe_row['Expiry'] == selected_pe_row['EXPIRY_DT'])):
                            
                            if("M%26M" == StockList[i]):
                                StockList[i] = "M&M"
                            elif("M%26MFIN" == StockList[i]):
                                StockList[i] = "M&MFIN"
                            elif("L%26TFH" == StockList[i]):
                                StockList[i] = "L&TFH"

                            pe_row_oldStrike_list = SortedDataMaxPE.loc[SortedDataMaxPE['Strike'] == selected_pe_row['STRIKE_PR'] ]
                            for k in range (len(pe_row_oldStrike_list)):
                                temp_row = pe_row_oldStrike_list.iloc[ k , : ]
                                if(temp_row['Expiry'] == pe_row['Expiry'] ):
                                    pe_row_oldStrike = temp_row
                                    k = len(pe_row_oldStrike_list)

                            if((futPer >=5 and (int(pe_row_oldStrike['OI_Change']) > 100 or int(pe_row['OI_Change']) > 100)) or
                                (int(pe_row_oldStrike['OI_Change']) > 150 or int(pe_row['OI_Change']) > 150)):
                                
                                moddf = PE_MaxOIChanged.append({'Name':StockList[i],'CMP':ltp,'FutP':Fut_price,'oldStrike':selected_pe_row['STRIKE_PR'],'oldLots':pe_row_oldStrike['OI'],'oldChange':pe_row_oldStrike['OI_Change'],
                                                                'oldPrice':pe_row_oldStrike['LTP'],'newPrice':pe_row['LTP'],'newChange':pe_row['OI_Change'],'newLots':pe_row['OI'],'newStrike': pe_row['Strike'],
                                                             'Option_Type': "PE",'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'PCR':float(("%.2f" %PCR)),'Time':temptime},ignore_index=True)
        
                                if(logging == 0):
                                    print(moddf)
                                PE_MaxOIChanged=moddf

                    

            if(os.path.exists(csv1) and 0):
               #Lets Check stock below green or above blue line for 2 days
                df1 = pd.read_csv(csv1)
                row1 = df1.loc[df1['SYMBOL'] == StockList[i]]
                optionData = row1[row1['INSTRUMENT'] == 'OPTSTK']
                optionDataCE = optionData[optionData['OPTION_TYP'] == 'CE']
                optionDataPE = optionData[optionData['OPTION_TYP'] == 'PE']
                PreviousDaySortedDataMaxCE = optionDataCE.sort_values(by=['OPEN_INT'],ascending=False)
                if(len(PreviousDaySortedDataMaxCE)):
                    selected_ce_row = PreviousDaySortedDataMaxCE.iloc[ 0 , : ]
                    if(float(selected_ce_row['CLOSE']) >= float(selected_ce_row['STRIKE_PR']) and
                       float(ltp) >= float(ce_row['Strike'])):
                        
                        moddf = StockCEUnderEye_df.append({'Name':StockList[i],'OldClose':selected_ce_row['CLOSE'],'CMP':ltp,'FutP':Fut_price,'OldRedLevel':selected_ce_row['STRIKE_PR'],
                                                            'NewRedLevel':ce_row['Strike'],
                                                         'Fut%':float(("%.2f" %futPer)),'Time':temptime},ignore_index=True)
        
                            
                        StockCEUnderEye_df=moddf

                PreviousDaySortedDataMaxPE = optionDataPE.sort_values(by=['OPEN_INT'],ascending=False)
                if(len(PreviousDaySortedDataMaxPE)):
                    selected_pe_row = PreviousDaySortedDataMaxPE.iloc[ 0 , : ]
                    if(len(SortedDataMaxPE)==0):
                        continue
                    pe_row = SortedDataMaxPE.iloc[ 0 , : ]
                    if(float(selected_pe_row['CLOSE']) <= float(selected_pe_row['STRIKE_PR']) and
                       float(ltp) <= float(pe_row['Strike'])):
                        
                        moddf = StockPEUnderEye_df.append({'Name':StockList[i],'OldClose':selected_pe_row['CLOSE'],'CMP':ltp,'FutP':Fut_price,'OldGreenLevel':selected_pe_row['STRIKE_PR'],
                                                            'NewGreenLevel':pe_row['Strike'],
                                                         'Fut%':float(("%.2f" %futPer)),'Time':temptime},ignore_index=True)
        
                            
                        StockPEUnderEye_df=moddf
        else:
            #print(StockList[i] + " not in Whitelist")
            OI_Percentage=0

        if(Total_OI !=0 and ((StockList[i] in stc_Nifty_50) or (StockList[i] in watchList))):
            #print("Nifty50 or watch:: "+StockList[i])
            #CE_change = sum(CE_OI_price_list)
            #PE_change = sum(PE_OI_price_list)
            #CE_pert = CE_change*100/Total_OI_change
            #PE_pert = PE_change*100/Total_OI_change

            SortedDataCE = df_ce.sort_values(by=['OI_Change'],ascending=False)
            SortedDataPE = df_pe.sort_values(by=['OI_Change'],ascending=False)

            for j in range(len(SortedDataCE)):
                ce_row = SortedDataCE.iloc[ j , : ]
                ce_change_oi = float(ce_row['OI_Change'])
                totalLots = float(ce_row['OI'])
            
                total_option = Total_OI - Fut_total
                ce_change_per = ce_change_oi*100/total_option
            
                temptime = time.strftime("%H:%M:%S")
                Value = market_lot*ce_change_oi*ce_row['LTP']/100000
        
                if((Value >=50 and ce_change_per >=1.5) or ce_change_per>= 10 ):
                    if(logging == 0):
                        print("Found Entry CE: "+ str(ce_change_per))
                        #print(ce_max_change)
                    
                    if(StockList[i] in stc_Nifty_50):
                        moddf = Nifty50OiChangedf.append({'Name':StockList[i],'CMP':ltp,'Strike':ce_row['Strike'],'CE_Change': float(("%.2f" %ce_change_per)),'PE_Change': "NA"
                        ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':ce_change_oi,'LTP':ce_row['LTP'],
                        'Vwap':ce_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':ce_row['Expiry']},ignore_index=True)
        
                        if(logging == 0):
                            print(moddf)
                        Nifty50OiChangedf=moddf
                    else:
                        moddf = Watchlistdf.append({'Name':StockList[i],'CMP':ltp,'Strike':ce_row['Strike'],'CE_Change': float(("%.2f" %ce_change_per)),'PE_Change': "NA"
                        ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':ce_change_oi,'LTP':ce_row['LTP'],
                        'Vwap':ce_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':ce_row['Expiry']},ignore_index=True)
        
                        if(logging == 0):
                            print(moddf)
                        Watchlistdf=moddf

                    difference  = ce_row['Strike'] - ltp
                    percentage = difference/ltp*100
                    if(percentage >= 8):
                        moddf = DoorValedf.append({'Name':StockList[i],'Distance':float(("%.2f" %percentage)),'Change':pChange,'CMP':ltp,'Strike':ce_row['Strike'],'CE_Change': float(("%.2f" %ce_change_per)),'PE_Change': "NA"
                        ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':ce_change_oi,'OptPrice':ce_row['LTP'],
                        'Vwap':ce_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':ce_row['Expiry']},ignore_index=True)
                        DoorValedf=moddf
                else:
                    j = len(SortedDataCE)

            for j in range(len(SortedDataPE)):
                pe_row = SortedDataPE.iloc[ j , : ]
                pe_change_oi = float(pe_row['OI_Change'])
                totalLots = float(pe_row['OI'])
                total_option = Total_OI - Fut_total
                pe_change_per = pe_change_oi*100/total_option
                Value = market_lot*pe_change_oi*pe_row['LTP']/100000
                if ((Value >=50 and pe_change_per >=1.5) or pe_change_per >= 10):
                    if(logging == 0):
                        print("Found Entry PE:"+ str(pe_change_per))
                    
                    if(StockList[i] in stc_Nifty_50):
                        moddf = Nifty50OiChangedf.append({'Name':StockList[i],'CMP':ltp,'Strike':pe_row['Strike'],'CE_Change': "NA",'PE_Change': float(("%.2f" %pe_change_per))
                        ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':pe_change_oi,'LTP':pe_row['LTP'],
                        'Vwap':pe_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':pe_row['Expiry']},ignore_index=True)

                        if(logging == 0):
                            print(moddf)
                        Nifty50OiChangedf=moddf
                    else:
                        moddf = Watchlistdf.append({'Name':StockList[i],'CMP':ltp,'Strike':pe_row['Strike'],'CE_Change': "NA",'PE_Change': float(("%.2f" %pe_change_per))
                        ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':pe_change_oi,'OptPrice':pe_row['LTP'],
                        'Vwap':pe_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':pe_row['Expiry']},ignore_index=True)

                        if(logging == 0):
                            print(moddf)
                        Watchlistdf=moddf

                    difference  = ltp - pe_row['Strike']
                    percentage = difference/ltp*100
                    if(percentage >= 8):
                        moddf = DoorValedf.append({'Name':StockList[i],'Distance':float(("%.2f" %percentage)),'Change':pChange,'CMP':ltp,'Strike':pe_row['Strike'],'CE_Change': "NA",'PE_Change': float(("%.2f" %pe_change_per))
                        ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'TotalLots':totalLots,'ChngInLots':pe_change_oi,'LTP':pe_row['LTP'],
                        'Vwap':pe_row['Vwap'],'BullPoint':float(("%.2f" %BullishPoint)),'BearPoint':float(("%.2f" %BearishPoint)),'Expiry':pe_row['Expiry']},ignore_index=True)
                        DoorValedf=moddf
                else:
                    j = len(SortedDataPE)

    
        #Logic for Max OI change in counts   
        if(len(df_ce)):
            SortedDataCE = df_ce.sort_values(by=['OI_Change'],ascending=False)
            SortedDataPE = df_pe.sort_values(by=['OI_Change'],ascending=False)             
       
        
            ce_row = SortedDataCE.iloc[ 0 , : ]
            
            moddf = CEOiChangedf.append({'Name':StockList[i],'CMP':ltp,'Strike':ce_row['Strike'],'TotalLots':ce_row['OI'],'ChngInLots':ce_row['OI_Change'],'OptPrice':ce_row['LTP'],
                                         'Expiry':ce_row['Expiry']},ignore_index=True)

                    
            CEOiChangedf=moddf

            pe_row = SortedDataPE.iloc[ 0 , : ]
            
            moddf = PEOiChangedf.append({'Name':StockList[i],'CMP':ltp,'Strike':pe_row['Strike'],'TotalLots':pe_row['OI'],'ChngInLots':pe_row['OI_Change'],'OptPrice':pe_row['LTP'],
                                         'Expiry':pe_row['Expiry']},ignore_index=True)

                    
            PEOiChangedf=moddf
    

    if(len(Watchlistdf)):
        print("#######################################################################################")
        print("Watchlist only")
        print("#######################################################################################")
        #print(Watchlistdf)
        print("\n")

    

    if(len(CE_MaxOIChanged)):
        print("#######################################################################################")
        print("CE - Max OI Change Stocks ")
        print("#######################################################################################")
        print(CE_MaxOIChanged)
        print("\n")

    if(len(PE_MaxOIChanged)):
        print("#######################################################################################")
        print("PE - Max OI Change Stocks ")
        print("#######################################################################################")
        print(PE_MaxOIChanged)
        print("\n")

    if(len(StockCEUnderEye_df)):
        print("#######################################################################################")
        print("CE - Stock Above RED line ")
        print("#######################################################################################")
        print(StockCEUnderEye_df)
        print("\n")

    if(len(StockPEUnderEye_df)):
        print("#######################################################################################")
        print("CE - Stock below GREEN line ")
        print("#######################################################################################")
        print(StockPEUnderEye_df)
        print("\n")

    
    if(len(OiChangedf)):
        print("#######################################################################################")
        print("Actual 31...... ")
        print("#######################################################################################")
        print("\n")
        print(OiChangedf)
        OiChangedf.to_csv("31.csv",index=False)
        print("\n")

    if(len(Nifty50OiChangedf)):
        print("#######################################################################################")
        print("Nifty Fifty Option only")
        print("#######################################################################################")
        print(Nifty50OiChangedf)
        Nifty50OiChangedf.to_csv("nifty50.csv",index=False)
        print("\n")


    if(len(DoorValedf)):
        print("#######################################################################################")
        print("Dooorrr Vale ........")
        print("#######################################################################################")
        print(DoorValedf)
        DoorValedf.to_csv("Door.csv",index=False)
        
        
    if(len(PriceAbovevwapdf)):
        print("#######################################################################################")
        print("VWAP Vale ........")
        print("#######################################################################################")
        print(PriceAbovevwapdf)
        tempname=datetime.now().strftime("%Y_%m_%d")
        PriceAbovevwapdf.to_csv("PriceAbovevwap"+ tempname + ".csv",index=False)
        
       
    if(len(OptionChangedf)):
        print("#######################################################################################")
        print("Options Activity ........")
        print("#######################################################################################")
        print(OptionChangedf)
        tempname=datetime.now().strftime("%Y_%m_%d")
        OptionChangedf.to_csv("OptionsActivity"+ tempname + ".csv",index=False)      
        
    """if(len(BullCross)):
        #NewMerged = pd.merge(BullCross, Nifty50OiChangedf, on="Name")
        #Selected_Name =  Nifty50OiChangedf['Name'].unique()
        #NewMerged = BullCross[Nifty50OiChangedf['Name'].isin(BullCross['Name'])]

        print("#######################################################################################")
        print("Green Line CrossOver")
        print("#######################################################################################")
        print(NewMerged)
        print("\n")

    if(len(BearCross)):
        NewMergedBear = pd.merge(BearCross, Nifty50OiChangedf, on="Name")
        print("#######################################################################################")
        print("Red Line CrossOver")
        print("#######################################################################################")
        print(NewMergedBear)
        print("\n")
        """

        #print("\n")
  
    #print("Going to Calculate Max Change top 10")    
    try:
        AudioFile = Currentpath + "\\Play.mp3"
        playsound(AudioFile)
    
    except Exception as e:
        print("Anncement Failed "+str(e))
        #time.sleep(30)
    """if(len(CEOiChangedf)):    
        SortedDataStocksCE = CEOiChangedf.sort_values(by=['ChngInLots'],ascending=False)
        SortedDataStocksPE = PEOiChangedf.sort_values(by=['ChngInLots'],ascending=False)
     
        print("#######################################################################################")
        print("CE - Max OI Change Stocks -- Top 10 ")
        print("#######################################################################################")
        print(SortedDataStocksCE.head(10))
     
        print("#######################################################################################")
        print("PE - Max OI Change Stocks -- Top 10")
        print("#######################################################################################")
        print(SortedDataStocksPE.head(10))

    result = CE_MaxOIChanged.append(PE_MaxOIChanged)
    Sorted_result = result.sort_values(by=['Name'],ascending=True)

    #print(Sorted_result)
    skip = False
    for j in range (len(Sorted_result)):
        if skip:
            skip = False
            continue
        pe_row = Sorted_result.iloc[ j , : ]
        if(j+1 < len(Sorted_result)):
            pe_row2 = Sorted_result.iloc[ j+1 , : ]
            if(pe_row['Name'] == pe_row2['Name']):
                print("Same Stock:")
                Str_to_send = "Name : *" + pe_row['Name'] + "*\nCash Price : " + str(pe_row['CMP']) + "\nFuture Price : " + str(pe_row['FutP']) + "\nFuture OI % : " + str(pe_row['Fut%']) + "\nOption Type : *" + str(pe_row['Option_Type']) + "*\n*O Strk* " + str(pe_row['oldStrike']) +  " *OI* " +str(pe_row['oldLots'])  +" *Chg* " + str(pe_row['oldChange']) + " *CMP* " + str(pe_row['oldPrice']) + "\n*N Strk* "+ str(pe_row['newStrike']) +  " *OI* " +str(pe_row['newLots'])  +" *Chg* " + str(pe_row['newChange']) + " *CMP* " + str(pe_row['newPrice'])  + "\nOption Type : *" + str(pe_row2['Option_Type']) + "*\n*O Strk* " + str(pe_row2['oldStrike']) +  " *OI* " +str(pe_row2['oldLots'])  +" *Chg* " + str(pe_row2['oldChange']) + " *CMP* " + str(pe_row2['oldPrice']) + "\n*N Strk* " + str(pe_row2['newStrike']) +  " *OI* " + str(pe_row2['newLots'])  +" *Chg* " + str(pe_row2['newChange']) + " *CMP* " + str(pe_row2['newPrice']) + "\nPCR : " + str(pe_row['PCR']) + "\nLot Size : " + str(pe_row['LotSize'])
                skip = True
            else:
                Str_to_send = "Name : *" + pe_row['Name'] + "*\nCash Price : " + str(pe_row['CMP']) + "\nFuture Price : " + str(pe_row['FutP']) +"\nFuture OI % : " + str(pe_row['Fut%']) + "\nOption Type : *"+ str(pe_row['Option_Type'])+"*\n*O Strk* " + str(pe_row['oldStrike']) +  " *OI* " +str(pe_row['oldLots'])  +" *Chg* " + str(pe_row['oldChange']) + " *CMP* " + str(pe_row['oldPrice']) + "\n*N Strk* "+ str(pe_row['newStrike']) +  " *OI* " +str(pe_row['newLots'])  +" *Chg* " + str(pe_row['newChange']) + " *CMP* " + str(pe_row['newPrice'])  + "\nPCR : " + str(pe_row['PCR']) + "\nLot Size : " + str(pe_row['LotSize'])
                
        else:
            Str_to_send = "Name : *" + pe_row['Name'] + "*\nCash Price : " + str(pe_row['CMP']) + "\nFuture Price : " + str(pe_row['FutP']) +"\nFuture OI % : " + str(pe_row['Fut%']) + "\nOption Type : *"+ str(pe_row['Option_Type'])+"*\n*O Strk* " + str(pe_row['oldStrike']) +  " *OI* " +str(pe_row['oldLots'])  +" *Chg* " + str(pe_row['oldChange']) + " *CMP* " + str(pe_row['oldPrice']) + "\n*N Strk* "+ str(pe_row['newStrike']) +  " *OI* " +str(pe_row['newLots'])  +" *Chg* " + str(pe_row['newChange']) + " *CMP* " + str(pe_row['newPrice']) + "\nPCR : " + str(pe_row['PCR']) + "\nLot Size : " + str(pe_row['LotSize'])
        #print(Str_to_send)
        #print(str(j))
        #send(Str_to_send,Common_chatid,Common_token,Tele_not_send)
        #send(Str_to_send,Stocks_chatid,Stocks_token,Tele_not_send)"""

    """for j in range (len(CE_MaxOIChanged)):
        pe_row = CE_MaxOIChanged.iloc[ j , : ]
        Str_to_send = "Name : *" + pe_row['Name'] + "*\nCash Price : " + str(pe_row['CMP']) + "\nFuture Price : " + str(pe_row['FutP']) +"\n*O Strk* " + str(pe_row['oldStrike']) +  " *OI* " +str(pe_row['oldLots'])  +" *Chg* " + str(pe_row['oldChange']) + "*CMP* " + str(pe_row['oldPrice']) + "\n*N Strk* "+ str(pe_row['newStrike']) +  " *OI* " +str(pe_row['newLots'])  +" *Chg* " + str(pe_row['newChange']) + "\n*CMP* " + str(pe_row['newPrice']) + "\nOption Type : *CE*\nFuture OI % : " + str(pe_row['Fut%']) + "\nPCR : " + str(pe_row['PCR']) + "\nLot Size : " + str(pe_row['LotSize'])
        send(Str_to_send,Common_chatid,Common_token,Tele_not_send)
        send(Str_to_send,Stocks_chatid,Stocks_token,Tele_not_send)

    for j in range (len(PE_MaxOIChanged)):
        pe_row = PE_MaxOIChanged.iloc[ j , : ]
        Str_to_send = "Name : *" + pe_row['Name'] + "*\nCash Price : " + str(pe_row['CMP']) + "\nFuture Price : " + str(pe_row['FutP']) +"\nOld Strike : " + str(pe_row['oldStrike']) +  " *Lots*: " +str(pe_row['oldLots'])  +" *Change*: " + str(pe_row['oldChange']) + "\nNew Strike : "+ str(pe_row['newStrike']) +  " *Lots*: " +str(pe_row['newLots'])  +" *Change*: " + str(pe_row['newChange']) + "\nOption Type : *PE*\nFuture OI % : " + str(pe_row['Fut%']) + "\nPCR : " + str(pe_row['PCR'])+ "\nLot Size : " + str(pe_row['LotSize'])
        send(Str_to_send,Common_chatid,Common_token,Tele_not_send)
        send(Str_to_send,Stocks_chatid,Stocks_token,Tele_not_send)"""


    
def download_single_stock_data(stc_code):
    global TimeForExcel
    if("M&amp;M" == stc_code):
        stc_code = "M%26M"
    elif("M&amp;MFIN" == stc_code):
        stc_code = "M%26MFIN"
    elif("L&amp;TFH" == stc_code):
        stc_code = "L%26TFH"

    #print ("Enter + "+ stc_code + " Time:" + TimeForExcel)
    current_time_min = time.strftime("%M")
    current_time_sec = time.strftime("%S")
    Effective_min = int(current_time_min)%Candle_timer
    timenow = datetime.now()
    current_time = (timenow - timedelta(minutes=Effective_min)).strftime("%H:%M")
    tempTimer = Effective_min*60 - int(current_time_sec)
    
    tempdf_data = pd.DataFrame(columns=['Name','Cash_ltp','Lotsize','PChange','Type','Strike','OI','OI_Change','LTP','Expiry','Time','Vwap'])
    
    CE_OI_price_list = []
    PE_OI_price_list = []
    CE_Total = []
    PE_Total = []
    Total_OI = 0
    Total_OI_change = 0
    Option_CE_Total = 0
    Option_PE_Total = 0
    Future_delta = 0
    Fut_total = 0
    #headers = {'User-Agent': 'Chrome/56.0.2924.76'}
    proxies = {'https':'https://36.255.86.170:4145',
                'http':'http://36.255.86.170:4145'}
    
    Base_url=" https://www.nseindia.com/api/quote-derivative?symbol=" + stc_code
    #print(Base_url)

    #if(stc_code == "NIFTY"):
     #   print ("\nNifty Reached here 1")
    try:
        #if(not cookie_dic):
            #generate_cookie()
        page = get_data(Base_url)
        #page = requests.get(Base_url,stream=True,headers=headers,cookies=cookie_dic,timeout=50)#,proxies=proxies)
           
        #print(page)
        #for c in page.cookies:
         #   print(c.name, c.value)
       # print(page)
        soup = page
        #soup = BeautifulSoup(page.content, 'html.parser')
        if(stc_code=='0'):
            print(soup)
        if(soup):
            d = json.loads(str(soup))
            #print(d)
        else:
            print("Soup Returned null for Stock: "+stc_code)
            Total_OI = 0
            return 1
            #json_formatted_str = json.dumps(d, indent=2)
            #print(d["stocks"][0]["metadata"]["instrumentType"])

        if(len(d["stocks"]) == 0):
           print("Invalid Data from Server for Stock :" + stc_code)
           return 1
        for j in range (len(d["stocks"])):
            if("Stock Futures" == d["stocks"][j]["metadata"]["instrumentType"]):
                # Futures Data
                #print(d["stocks"][j])
                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["changeinOpenInterest"]
                if(text != '-'):
                    fut_change_oi = int(text)
                else:
                    fut_change_oi= 0
                Total_OI_change = Total_OI_change + fut_change_oi
                Future_delta = Future_delta  + fut_change_oi

                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["openInterest"]
                if(text != '-'):
                    fut_total_oi = int(text)
                else:
                    fut_total_oi= 0

                Total_OI = Total_OI + fut_total_oi
                Fut_total = Fut_total + fut_total_oi
        
                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["marketLot"]
                if(text != '-'):
                    market_lot = int(text)
                else:
                    market_lot = 0

                cash_ltp = d["stocks"][j]["underlyingValue"]
                lastprice = d["stocks"][j]["metadata"]["lastPrice"]
                pChange = d["stocks"][j]["metadata"]["pChange"]
                expDate = d["stocks"][j]["metadata"]["expiryDate"]
                vmap = float(d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["vmap"])
                
                
                tempmoddf = tempdf_data.append({'Name':stc_code,'Cash_ltp':cash_ltp,'PChange':float(("%.2f" %pChange)),'Lotsize':market_lot,'Type':"Fut",'Strike': "",'OI':fut_total_oi,
                                                'OI_Change':fut_change_oi,'LTP':lastprice, 'Expiry':expDate,'Time':TimeForExcel,'Vwap':vmap},ignore_index=True)
                    #print(tempmoddf)
                tempdf_data = tempmoddf
                
            elif("Call" == d["stocks"][j]["metadata"]["optionType"]):
                #Options Call Data
                
                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["openInterest"]
                if(text != '-'):
                    CE_total_OI = int(text)
                else:
                    CE_total_OI= 0

                Total_OI =  Total_OI + CE_total_OI
                Option_CE_Total = Option_CE_Total + CE_total_OI
                
                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["changeinOpenInterest"]
                if(text != '-'):
                    CE_change_OI = int(text)
                    #if(CE_change_OI != 0):
                        #print(d["stocks"][j])
                else:
                    CE_change_OI= 0
                Total_OI_change = Total_OI_change + CE_change_OI

                text= d["stocks"][j]["metadata"]["lastPrice"]
                
                CE_LTP = float(text)
                vmap = float(d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["vmap"])

                text= d["stocks"][j]["metadata"]["strikePrice"]
                if(text != '-'):
                    strike_price = int(float(text))
                else:
                    strike_price= 0

                expDate = d["stocks"][j]["metadata"]["expiryDate"]
                CE_OI_price_list.append(CE_change_OI)
               
                tempmoddf = tempdf_data.append({'Name':stc_code,'Cash_ltp':"",'PChange':"",'Lotsize':"",'Type':"CE",'Strike':strike_price,'OI':CE_total_OI,'OI_Change':CE_change_OI,'LTP':CE_LTP,
                                                  'Expiry':expDate,'Time':TimeForExcel,'Vwap':vmap},ignore_index=True)
                #print(tempmoddf)
                tempdf_data = tempmoddf
                
                
                    
            elif("Put" == d["stocks"][j]["metadata"]["optionType"]):

                text= d["stocks"][j]["metadata"]["lastPrice"]
               
                PE_LTP = float(text)
                vmap = float(d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["vmap"])
                    
                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["changeinOpenInterest"]
                if(text != '-'):
                    PE_change_OI = int(text)
                else:
                    PE_change_OI= 0
                Total_OI_change = Total_OI_change + PE_change_OI

                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["openInterest"]
                if(text != '-'):
                    PE_total_OI = int(text)
                else:
                    PE_total_OI= 0
                Total_OI = Total_OI + PE_total_OI
                Option_PE_Total = Option_PE_Total + PE_total_OI

                text= d["stocks"][j]["metadata"]["strikePrice"]
                if(text != '-'):
                    strike_price = int(float(text))
                else:
                    strike_price= 0

                PE_OI_price_list.append(PE_change_OI)

                expDate = d["stocks"][j]["metadata"]["expiryDate"]
                temptime = time.strftime("%H:%M:%S")
                tempmoddf = tempdf_data.append({'Name':stc_code,'Cash_ltp':"",'PChange':"",'Lotsize':"",'Type':"PE",'Strike':strike_price,'OI':PE_total_OI,'OI_Change':PE_change_OI,'LTP':PE_LTP,
                                              'Expiry':expDate,'Time':TimeForExcel,'Vwap':vmap},ignore_index=True)
                    #print(tempmoddf)
               
                tempdf_data = tempmoddf

            else:
                return 0

        date1 = date.today()
        #while int(date1.weekday()) >=5  or is_public_holiday(date1):
        while ((int(date1.weekday()) >=5  or is_public_holiday(date1)) 
            and (str('%02d'%date1.day)!="20" and monthToNum(str('%02d'%date1.month)) == "01" and str(date1.year) == "2024" )) :
            date1=date1-timedelta(days=1)

        folder_Name = ".//" + str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year)
        
        
        current_time_hour = time.strftime("%H") 
        if( (int(current_time_hour) <= 8) or
            ((int(current_time_hour) <= 9) and (int(current_time_min) <=25)) or
           ((int(current_time_hour) >= 15) and (int(current_time_min) >=40)) or
            (int(current_time_hour) >= 16)):
            #print("To_temp_folder")
            folder_Name = ".//" + str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year) + "_temp"
       
        
        
        if(not os.path.exists(folder_Name)):
            os.mkdir(folder_Name)

        file_name = folder_Name + "//" + stc_code + ".csv"
        #:10print("Chec File name: "+file_name)

        if(stc_code == "NIFTY"):
            print ("Nifty Reached here 2")
        if(os.path.exists(file_name)):
            df3 = pd.read_csv(file_name)
            result = df3.append(tempdf_data)
            result.to_csv(file_name,index=False)
        else:
            #print("Write in file_name: "+file_name)
            tempdf_data.to_csv(file_name)
        
       
      
        return 1

    except Exception as e:
        print("Exception "+str(e) +" occured for: "+stc_code + " Skipping this 3")
        #generate_cookie()
        #download_single_stock_data(stc_code)
        Total_OI = 0
        
        
        

def download_single_index_data(stc_code):
    #print("Entry download_single_index_data")
    current_time_min = time.strftime("%M")
    current_time_sec = time.strftime("%S")
    Effective_min = int(current_time_min)%Candle_timer
    timenow = datetime.now()
    current_time = (timenow - timedelta(minutes=Effective_min)).strftime("%H:%M")
    #tempTimer = Effective_min*60 - int(current_time_sec)

    tempdf_data = pd.DataFrame(columns=['Name','Cash_ltp','Lotsize','Type','Strike','OI','OI_Change','LTP','Expiry','Time','Vwap'])
    
    CE_OI_price_list = []
    PE_OI_price_list = []
    CE_Total = []
    PE_Total = []
    Total_OI = 0
    Total_OI_change = 0
    Option_CE_Total = 0
    Option_PE_Total = 0
    Future_delta = 0
    Fut_total = 0
    #headers = {'User-Agent': 'Safari/537.36'}
    Base_url="https://www.nseindia.com/api/quote-derivative?symbol=" + stc_code
    #print(Base_url)
    try:
    #if(1):
        #if(not cookie_dic):
         #   generate_cookie()
        page = get_data(Base_url)
        #page = requests.get(Base_url,headers=headers,cookies=cookie_dic,timeout=50)
        #print(page)
   
      
        #soup = BeautifulSoup(page.content, 'html.parser')
        soup = page
        #print(soup)
        if(soup):
            d = json.loads(str(soup))
            print(d)
        else:
            print("Soup Returned null for Stock: "+stc_code)
            Total_OI = 0
            #json_formatted_str = json.dumps(d, indent=2)
            #print(d["stocks"][0]["metadata"]["instrumentType"])
        #print("Reached here download_single_index_data")
        if(len(d["stocks"]) == 0):
           print("Invalid Data from Server")
           return 1
        for j in range (len(d["stocks"])):
            if("Index Futures" == d["stocks"][j]["metadata"]["instrumentType"]):
                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["changeinOpenInterest"]
                if(text != '-'):
                    fut_change_oi = int(text)
                else:
                    fut_change_oi= 0
                Total_OI_change = Total_OI_change + fut_change_oi
                Future_delta = Future_delta  + fut_change_oi

                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["openInterest"]
                if(text != '-'):
                    fut_total_oi = int(text)
                else:
                    fut_total_oi= 0

                Total_OI = Total_OI + fut_total_oi
                Fut_total = Fut_total + fut_total_oi
        
                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["marketLot"]
                if(text != '-'):
                    market_lot = int(text)
                else:
                    market_lot = 0

                cash_ltp = d["stocks"][j]["underlyingValue"]
                lastprice = d["stocks"][j]["metadata"]["lastPrice"]
                expDate = d["stocks"][j]["metadata"]["expiryDate"]
                vmap = float(d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["vmap"])

                tempmoddf = tempdf_data.append({'Name':stc_code,'Cash_ltp':cash_ltp,'Lotsize':market_lot,'Type':"Fut",'Strike': "",'OI':fut_total_oi,
                                                'OI_Change':fut_change_oi,'LTP':lastprice, 'Expiry':expDate,'Time':current_time,'Vwap':vmap},ignore_index=True)
                    #print(tempmoddf)
                tempdf_data = tempmoddf
                 
            elif("Call" == d["stocks"][j]["metadata"]["optionType"]):
                text  = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["openInterest"]
                if(text != '-'):
                    CE_total_OI = int(text)
                else:
                    CE_total_OI= 0
                Total_OI =  Total_OI + CE_total_OI
                Option_CE_Total = Option_CE_Total + CE_total_OI
              
                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]['changeinOpenInterest']
                if(text != '-'):
                    CE_change_OI = int(text)
                else:
                    CE_change_OI= 0
                Total_OI_change = Total_OI_change + CE_change_OI
                
                text = d["stocks"][j]["metadata"]["lastPrice"]
                CE_LTP = float(text)

                text = d["stocks"][j]["metadata"]['strikePrice']
                if(text != '-'):
                    strike_price = int(float(text))
                else:
                    strike_price= 0

                expDate = d["stocks"][j]["metadata"]['expiryDate']
                ltp = d["stocks"][j]['underlyingValue']
                vmap = float(d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["vmap"])
                
                tempmoddf = tempdf_data.append({'Name':stc_code,'Cash_ltp':ltp,'Lotsize':"",'Type':"CE",'Strike':strike_price,'OI':CE_total_OI,'OI_Change':CE_change_OI,'LTP':CE_LTP,
                                                  'Expiry':expDate,'Time':current_time,'Vwap':vmap},ignore_index=True)
                #print(tempmoddf)
                tempdf_data = tempmoddf
                
            elif("Put" == d["stocks"][j]["metadata"]["optionType"]):
                text = d["stocks"][j]["metadata"]["lastPrice"]
                PE_LTP = float(text)

                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]['changeinOpenInterest']
                if(text != '-'):
                    PE_change_OI = int(text)
                else:
                    PE_change_OI= 0
                Total_OI_change = Total_OI_change + PE_change_OI

                text  =d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["openInterest"]
                if(text != '-'):
                    PE_total_OI = int(text)
                else:
                    PE_total_OI= 0
                Total_OI = Total_OI + PE_total_OI
                Option_PE_Total = Option_PE_Total + PE_total_OI

                text = d["stocks"][j]["metadata"]['strikePrice']
                if(text != '-'):
                    strike_price = int(float(text))
                else:
                    strike_price= 0
                
                
                expDate = d["stocks"][j]["metadata"]['expiryDate']
                ltp = d["stocks"][j]['underlyingValue']
                vmap = float(d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["vmap"])

                tempmoddf = tempdf_data.append({'Name':stc_code,'Cash_ltp':ltp,'Lotsize':"",'Type':"PE",'Strike':strike_price,'OI':PE_total_OI,'OI_Change':PE_change_OI,'LTP':PE_LTP,
                                              'Expiry':expDate,'Time':current_time,'Vwap':vmap},ignore_index=True)
                    #print(tempmoddf)
               
                tempdf_data = tempmoddf
            else:
                pass

        
        date1 = date.today()
        while ((int(date1.weekday()) >=5  or is_public_holiday(date1)) 
                and (str('%02d'%date1.day)!="20" and monthToNum(str('%02d'%date1.month)) == "01" and str(date1.year) == "2024" )) :
            date1=date1-timedelta(days=1)

        folder_Name = ".//" + str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year)
      
        current_time_hour = time.strftime("%H") 
        if( (int(current_time_hour) <= 8) or
            ((int(current_time_hour) <= 9) and (int(current_time_min) <=25)) or
           ((int(current_time_hour) >= 15) and (int(current_time_min) >=40)) or
            (int(current_time_hour) >= 16)):
            #print("To_temp_folder")
            folder_Name = ".//" + str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year) + "_temp"
        if(not os.path.exists(folder_Name)):
            os.mkdir(folder_Name)

        file_name = folder_Name + "//" + stc_code + ".csv"
        #print("Chec File name: "+file_name)

        if(os.path.exists(file_name)):
            df3 = pd.read_csv(file_name)
            result = df3.append(tempdf_data)
            result.to_csv(file_name,index=False)
        else:
            #print("Write in file_name: "+file_name)
            tempdf_data.to_csv(file_name)
        

        return 1

    except Exception as e:
        print("Exception "+str(e) +" occured for: "+stc_code + " Skipping this 5")
        Total_OI = 0
        
"""def download_single_stock_data(stc_code):
    if("M&amp;M" == stc_code):
        stc_code = "M%26M"
    elif("M&amp;MFIN" == stc_code):
        stc_code = "M%26MFIN"
    elif("L&amp;TFH" == stc_code):
        stc_code = "L%26TFH"

    current_time_min = time.strftime("%M")
    current_time_sec = time.strftime("%S")
    Effective_min = int(current_time_min)%Candle_timer
    timenow = datetime.now()
    current_time = (timenow - timedelta(minutes=Effective_min)).strftime("%H:%M")
    #tempTimer = Effective_min*60 - int(current_time_sec)

    tempdf_data = pd.DataFrame(columns=['Name','Cash_ltp','Lotsize','Type','Strike','OI','OI_Change','LTP','Expiry','Time'])
    
    CE_OI_price_list = []
    PE_OI_price_list = []
    CE_Total = []
    PE_Total = []
    Total_OI = 0
    Total_OI_change = 0
    Option_CE_Total = 0
    Option_PE_Total = 0
    Future_delta = 0
    Fut_total = 0
    headers = {'User-Agent': 'Safari/537.36'}
    Base_url=" https://www.nseindia.com/api/quote-derivative?symbol=" + stc_code


    try:
        page = requests.get(Base_url,headers=headers,timeout=30)
           
   
      
        soup = BeautifulSoup(page.content, 'html.parser')
        if(soup):
            d = json.loads(str(soup))
        else:
            print("Soup Returned null for Stock: "+stc_code)
            Total_OI = 0
            #json_formatted_str = json.dumps(d, indent=2)
            #print(d["stocks"][0]["metadata"]["instrumentType"])
        for j in range (len(d["stocks"])):
            if("Stock Futures" == d["stocks"][j]["metadata"]["instrumentType"]):
                # Futures Data
                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["changeinOpenInterest"]
                if(text != '-'):
                    fut_change_oi = int(text)
                else:
                    fut_change_oi= 0
                Total_OI_change = Total_OI_change + fut_change_oi
                Future_delta = Future_delta  + fut_change_oi

                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["openInterest"]
                if(text != '-'):
                    fut_total_oi = int(text)
                else:
                    fut_total_oi= 0

                Total_OI = Total_OI + fut_total_oi
                Fut_total = Fut_total + fut_total_oi
        
                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["marketLot"]
                if(text != '-'):
                    market_lot = int(text)
                else:
                    market_lot = 0

                cash_ltp = d["stocks"][j]["underlyingValue"]
                lastprice = d["stocks"][j]["metadata"]["lastPrice"]
                expDate = d["stocks"][j]["metadata"]["expiryDate"]
                
                tempmoddf = tempdf_data.append({'Name':stc_code,'Cash_ltp':cash_ltp,'Lotsize':market_lot,'Type':"Fut",'Strike': "",'OI':fut_total_oi,
                                                'OI_Change':fut_change_oi,'LTP':lastprice, 'Expiry':expDate,'Time':current_time},ignore_index=True)
                    #print(tempmoddf)
                tempdf_data = tempmoddf
                
            elif("Call" == d["stocks"][j]["metadata"]["optionType"]):
                #Options Call Data
                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["openInterest"]
                if(text != '-'):
                    CE_total_OI = int(text)
                else:
                    CE_total_OI= 0

                Total_OI =  Total_OI + CE_total_OI
                Option_CE_Total = Option_CE_Total + CE_total_OI
                
                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["changeinOpenInterest"]
                if(text != '-'):
                    CE_change_OI = int(text)
                else:
                    CE_change_OI= 0
                Total_OI_change = Total_OI_change + CE_change_OI

                text= d["stocks"][j]["metadata"]["lastPrice"]
                
                CE_LTP = float(text)
                   

                text= d["stocks"][j]["metadata"]["strikePrice"]
                if(text != '-'):
                    strike_price = int(float(text))
                else:
                    strike_price= 0

                expDate = d["stocks"][j]["metadata"]["expiryDate"]
                CE_OI_price_list.append(CE_change_OI)
               
                tempmoddf = tempdf_data.append({'Name':stc_code,'Cash_ltp':"",'Lotsize':"",'Type':"CE",'Strike':strike_price,'OI':CE_total_OI,'OI_Change':CE_change_OI,'LTP':CE_LTP,
                                                  'Expiry':expDate,'Time':current_time},ignore_index=True)
                #print(tempmoddf)
                tempdf_data = tempmoddf
                
                
                    
            elif("Put" == d["stocks"][j]["metadata"]["optionType"]):

                text= d["stocks"][j]["metadata"]["lastPrice"]
               
                PE_LTP = float(text)
                    
                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["changeinOpenInterest"]
                if(text != '-'):
                    PE_change_OI = int(text)
                else:
                    PE_change_OI= 0
                Total_OI_change = Total_OI_change + PE_change_OI

                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["openInterest"]
                if(text != '-'):
                    PE_total_OI = int(text)
                else:
                    PE_total_OI= 0
                Total_OI = Total_OI + PE_total_OI
                Option_PE_Total = Option_PE_Total + PE_total_OI

                text= d["stocks"][j]["metadata"]["strikePrice"]
                if(text != '-'):
                    strike_price = int(float(text))
                else:
                    strike_price= 0

                PE_OI_price_list.append(PE_change_OI)

                expDate = d["stocks"][j]["metadata"]["expiryDate"]
                temptime = time.strftime("%H:%M:%S")
                tempmoddf = tempdf_data.append({'Name':stc_code,'Cash_ltp':"",'Lotsize':"",'Type':"PE",'Strike':strike_price,'OI':PE_total_OI,'OI_Change':PE_change_OI,'LTP':PE_LTP,
                                              'Expiry':expDate,'Time':current_time},ignore_index=True)
                    #print(tempmoddf)
               
                tempdf_data = tempmoddf

            else:
                pass

        date1 = date.today()
        while int(date1.weekday()) >=5  or is_public_holiday(date1):
            date1=date1-timedelta(days=1)

        folder_Name = ".//" + str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year)
        if(not os.path.exists(folder_Name)):
            os.mkdir(folder_Name)

        file_name = folder_Name + "//" + stc_code + ".csv"
        #print("Chec File name: "+file_name)

        if(os.path.exists(file_name)):
            df3 = pd.read_csv(file_name)
            result = df3.append(tempdf_data)
            result.to_csv(file_name,index=False)
        else:
            print("Write in file_name: "+file_name)
            tempdf_data.to_csv(file_name)
        

        return 1

    except Exception as e:
        print("Exception "+str(e) +" occured for: "+stc_code + " Skipping this")
        Total_OI = 0"""
def plot_index(dates,stc_code):
    Index_MaxOI = pd.DataFrame(columns=['Date','Open','High','Low','Close','Fut_p','Fut%','ce_strike1','ce_strike2','ce_strike3','pe_strike1','pe_strike2','pe_strike3','LevelCEOI1','LevelPEOI1','PCR'])
    Index_MaxChangeOI = pd.DataFrame(columns=['Date','Open','High','Low','Close','Fut_p','Fut%','ce_strike1','ce_strike2','ce_strike3','pe_strike1','pe_strike2','pe_strike3','LevelCEOI1','LevelPEOI1','LevelCEOI2','LevelPEOI2','LevelCEOI3','LevelPEOI3','PCR'])
    #Fetch Level
    tempdate = dates[-1]
    csv1 = ".//" + str('%02d'%tempdate.day) + monthToNum(str('%02d'%tempdate.month)) + str(tempdate.year)
    file_name = csv1 + "//" + stc_code + ".csv"
    if(os.path.exists(file_name)):
        df2 = pd.read_csv(file_name)
        df_fut = df2.loc[df2['Type'] == "Fut"]
        fut_row = df_fut.iloc[ 0 , : ]
        ltp_level = int(fut_row['Cash_ltp'])
        print(str(ltp_level))
        if(stc_code == "NIFTY"):
            diff_level = ltp_level%100
            #print(str(diff_level))
            if(diff_level > 50):
                Level1 = (int(ltp_level/100))*100 + 100
            else:
                Level1 = (int(ltp_level/100))*100
        elif(stc_code == "BANKNIFTY"):
            diff_level = ltp_level%500
            if(diff_level > 250):
                Level1 = (int(ltp_level/500))*500 + 500
            else:
                Level1 = (int(ltp_level/500))*500
   
    for i in range (len(dates)):
        csv1 = ".//" + str('%02d'%dates[i].day) + monthToNum(str('%02d'%dates[i].month)) + str(dates[i].year)
        file_name = csv1 + "//" + stc_code + ".csv"
        if(os.path.exists(file_name)):
            #print("File found : "+file_name)
            df2 = pd.read_csv(file_name)

            Selected_time =  df2['Time'].unique()
            #print("Time of Candles: "+ str(len(Selected_time)))
            #print (Selected_time)

            for z in range(len(Selected_time)):
       
                temp_candle_df = df2.loc[df2['Time'] == Selected_time[z]]
           
                df_fut = temp_candle_df.loc[temp_candle_df['Type'] == "Fut"]

                Fut_Change_OI = df_fut['OI_Change'].sum()
                Fut_total = df_fut['OI'].sum()
                futPer = Fut_Change_OI/(Fut_total-Fut_Change_OI)*100
            
                fut_row = df_fut.iloc[ 0 , : ]
                Fut_price = fut_row['LTP']
                ltp = fut_row['Cash_ltp']
                market_lot = fut_row['Lotsize']
            
                df_ce = temp_candle_df.loc[temp_candle_df['Type'] == "CE"]
                CE_change = df_ce['OI_Change'].sum()
                CE_OI = df_ce['OI'].sum()

                df_ce_level1 = df_ce.loc[df_ce['Strike'] == Level1]
                level_total_ce_OI1 = df_ce_level1['OI'].sum()

                #df_ce_level2 = df_ce.loc[df_ce['Strike'] == Level2]
                #level_total_ce_OI2 = df_ce_level2['OI'].sum()

                #df_ce_level3 = df_ce.loc[df_ce['Strike'] == Level3]
                #level_total_ce_OI3 = df_ce_level3['OI'].sum()

                df_pe = temp_candle_df.loc[temp_candle_df['Type'] == "PE"]
                PE_change = df_pe['OI_Change'].sum()
                PE_OI = df_pe['OI'].sum()
                PCR = PE_OI/CE_OI

                df_pe_level1 = df_pe.loc[df_pe['Strike'] == Level1]
                level_total_pe_OI1 = df_pe_level1['OI'].sum()

                #df_pe_level2 = df_pe.loc[df_pe['Strike'] == Level2]
                #level_total_pe_OI2 = df_pe_level2['OI'].sum()

                #df_pe_level3 = df_pe.loc[df_pe['Strike'] == Level3]
                #level_total_pe_OI3 = df_pe_level3['OI'].sum()


                SortedDataMaxCE = df_ce.sort_values(by=['OI'],ascending=False)
                SortedDataMaxPE = df_pe.sort_values(by=['OI'],ascending=False)

                if(len(SortedDataMaxCE) >=3 and len(SortedDataMaxPE) >=3):
                    #temptime = datetime.now()
                    ce_row1 = SortedDataMaxCE.iloc[ 0 , : ]
                    ce_row2 = SortedDataMaxCE.iloc[ 1 , : ]
                    ce_row3 = SortedDataMaxCE.iloc[ 2 , : ]

                    pe_row1 = SortedDataMaxPE.iloc[ 0 , : ]
                    pe_row2 = SortedDataMaxPE.iloc[ 1 , : ]
                    pe_row3 = SortedDataMaxPE.iloc[ 2 , : ]

                    #print(Selected_time[z])
                    str1 = str(dates[i].year) + "-" + str('%02d'%dates[i].month) + "-" +str('%02d'%dates[i].day) + " " + Selected_time[z] + ":00"
                    #print(str1)
                    datetime_object = datetime.strptime(str1, '%Y-%m-%d %H:%M:%S')
                    moddf = Index_MaxOI.append({'Date':datetime_object,'Open':ltp,'High':ltp,'Low':ltp,'Close':ltp,'Fut_p':Fut_price,'Fut%':float(("%.2f" %futPer)),'ce_strike1':int(ce_row1['Strike']),'ce_strike2': int(ce_row2['Strike']),
                                                    'ce_strike3': int(ce_row3['Strike']),'pe_strike1': int(pe_row1['Strike']),'pe_strike2': int(pe_row2['Strike']),'pe_strike3': int(pe_row3['Strike']),
                                                'LevelCEOI1':level_total_ce_OI1,'LevelPEOI1':level_total_pe_OI1,'PCR':float(("%.2f" %PCR))},ignore_index=True)
        
                    Index_MaxOI=moddf

                SortedDataMaxChangeCE = df_ce.sort_values(by=['OI_Change'],ascending=False)
                SortedDataMaxChangePE = df_pe.sort_values(by=['OI_Change'],ascending=False)

                if(len(SortedDataMaxChangeCE) >=3 and len(SortedDataMaxChangePE) >=3):
                    #temptime = datetime.now()
                    ce_row1 = SortedDataMaxChangeCE.iloc[ 0 , : ]
                    ce_row2 = SortedDataMaxChangeCE.iloc[ 1 , : ]
                    ce_row3 = SortedDataMaxChangeCE.iloc[ 2 , : ]

                    pe_row1 = SortedDataMaxChangePE.iloc[ 0 , : ]
                    pe_row2 = SortedDataMaxChangePE.iloc[ 1 , : ]
                    pe_row3 = SortedDataMaxChangePE.iloc[ 2 , : ]

                    #print(Selected_time[z])
                    str1 = str(dates[i].year) + "-" + str('%02d'%dates[i].month) + "-" +str('%02d'%dates[i].day) + " " + Selected_time[z] + ":00"
                    #print(str1)
                    datetime_object = datetime.strptime(str1, '%Y-%m-%d %H:%M:%S')
                    moddf = Index_MaxChangeOI.append({'Date':datetime_object,'Open':ltp,'High':ltp,'Low':ltp,'Close':ltp,'Fut_p':Fut_price,'Fut%':float(("%.2f" %futPer)),'ce_strike1':int(ce_row1['Strike']),'ce_strike2': int(ce_row2['Strike']),
                                                    'ce_strike3': int(ce_row3['Strike']),'pe_strike1': int(pe_row1['Strike']),'pe_strike2': int(pe_row2['Strike']),'pe_strike3': int(pe_row3['Strike']),
                                                'LevelCEOI1':level_total_ce_OI1,'LevelPEOI1':level_total_pe_OI1,'PCR':float(("%.2f" %PCR))},ignore_index=True)
        
                    Index_MaxChangeOI=moddf



    NumCandles = len(Index_MaxChangeOI)
    data2 = Index_MaxOI.set_index('Date')
    data = Index_MaxChangeOI.set_index('Date')
    #CashPrice = data['CMP']
    FutPrice = data['Fut_p']
    #FutPercent = date['Fut%']
    CEStrike1 = data2['ce_strike1']
    CEStrike2 = data['ce_strike1']
    CEStrike3 = data['ce_strike3']
    PEStrike1 = data2['pe_strike1']
    PEStrike2 = data['pe_strike1']
    PEStrike3 = data['pe_strike3']
    PCR = data['PCR']
    LevelCEOI1 = data2['LevelCEOI1']
    LevelPEOI1 = data['LevelPEOI1']
    #LevelCEOI2 = data['LevelCEOI2']
    #LevelPEOI2 = data['LevelPEOI2']
    #LevelCEOI3 = data['LevelCEOI3']
    #LevelPEOI3 = data['LevelPEOI3']
        
    ap0 = [mpf.make_addplot((CEStrike2[-NumCandles:]),type='line',width=1,panel=0,secondary_y=False,color='tomato'),
        #mpf.make_addplot((CEStrike2[-NumCandles:]),type='line',width=0.5,panel=0,secondary_y=False,color='green'),
        #mpf.make_addplot((CEStrike3[-NumCandles:]),type='line',width=0.4,panel=0,secondary_y=False,color='green'),
        #mpf.make_addplot((PEStrike1[-NumCandles:]),type='line',width=1,panel=0,secondary_y=False,color='tomato'),
        mpf.make_addplot((PEStrike2[-NumCandles:]),type='line',width=1,panel=0,secondary_y=False,color='green'),
        #mpf.make_addplot((PEStrike3[-NumCandles:]),type='line',width=0.4,panel=0,secondary_y=False,color='tomato')]
        mpf.make_addplot((PCR[-NumCandles:]),type='line',width=1,panel=1,secondary_y=False,color='black'),
        mpf.make_addplot((LevelCEOI1[-NumCandles:]),type='line',width=1,panel=2,secondary_y=False,color='red',ylabel=str(Level1)),
        mpf.make_addplot((LevelPEOI1[-NumCandles:]),type='line',width=1,panel=2,secondary_y=False,color='green')]
        #mpf.make_addplot((LevelCEOI2[-NumCandles:]),type='line',width=1,panel=3,secondary_y=False,color='red',ylabel=str(Level2)),
        #mpf.make_addplot((LevelPEOI2[-NumCandles:]),type='line',width=1,panel=3,secondary_y=False,color='green'),
        #mpf.make_addplot((LevelCEOI3[-NumCandles:]),type='line',width=1,panel=4,secondary_y=False,color='red',ylabel=str(Level3)),
        #mpf.make_addplot((LevelPEOI3[-NumCandles:]),type='line',width=1,panel=4,secondary_y=False,color='green')]

        #mpf.make_addplot((Delvol[:]),type='bar',panel=1,secondary_y=False,color='black'),
        #mpf.make_addplot((COI[:]),type='bar',panel=2,color='y'),
        #mpf.make_addplot((multiplied_list[:]),type='bar',secondary_y=False,panel=2,color='black')]     # uses panel 0 by default
        #ap0 = mpf.make_addplot(data['Deliverable Volume'],type='bar',width=0.7,panel=1,
                                # color='dimgray',alpha=1,secondary_y=False),
    
        #mc = mpf.make_marketcolors(volume='silver')
        #s  = mpf.make_mpf_style(marketcolors=mc,y_on_right=True,gridstyle='dashed',gridcolor='white',base_mpl_style='ggplot')

    mpf.plot(data[-NumCandles:],type='line',title=stc_code,addplot=ap0,figsize=(15,8.5),savefig='.\\'+stc_code+'.png')

def fromNewSiteTele(GlobalPercentage,logging,ExludeList,watchList,WhiteList):
    #Get list of all Stocks

    date1 = date.today()
    while int(date1.weekday()) >=5  or is_public_holiday(date1):
        date1=date1-timedelta(days=1)

    folder_Name = ".//" + str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year)
    if(not os.path.exists(folder_Name)):
        os.mkdir(folder_Name)

    file_name = folder_Name + "//StockList.csv"
    #print("Chec File name: "+file_name)
    

    if(os.path.exists(file_name)):
        df = pd.read_csv(file_name)
        StockList = df["0"]
    else:
        Base_url="https://www.nseindia.com/api/master-quote"
       

        

        try:
            page = requests.get(Base_url,headers=headers,cookies=cookie_dic,timeout=30)
            #print(page.content)
            soup = BeautifulSoup(page.content, 'html.parser')
            if(soup):
                StockList = json.loads(str(soup))
                df = pd.DataFrame(StockList)
                df.to_csv(file_name, index=False)
                #StockList.append("NIFTY")
                #StockList.append("BANKNIFTY")
                #moddf = StockList.append("NIFTY")
                #StockList = moddf
                #moddf = StockList.append("BANKNIFTY")
                #StockList = moddf
            else:
                print("Soup Returned null for Stock: ")
               
           
            #print(StockList)

        except Exception as e:
            print("Exception "+str(e) +" occured while fetching Stock-List: " " Seems server down")
            tempdate = getPreviousValidDay()
            folder_Name = ".//" + str('%02d'%tempdate.day) + monthToNum(str('%02d'%tempdate.month)) + str(tempdate.year)
            file_name = folder_Name + "//StockList.csv"
            if(os.path.exists(file_name)):
                df = pd.read_csv(file_name)
                StockList = df["0"]
                #moddf = StockList.append("NIFTY")
                #StockList = moddf
                #moddf = StockList.append("BANKNIFTY")
                #StockList = moddf
                #print(StockList)
                
            else:
                StockList = []
            Total_OI = 0

    
    tempdf = pd.DataFrame(columns=['Name','Total_OI_Change','CE_Change','PE_Change','LotSize','Time','CE','PE'])


    current_time_min = time.strftime("%M")
    current_time_sec = time.strftime("%S")
    Effective_min = int(current_time_min)%Candle_timer
    timenow = datetime.now()
    current_min = (timenow - timedelta(minutes=Effective_min)).strftime("%M")

    

   

    
    

    poolIndex = ThreadPool(processes=INDEX_THREAD_COUNT)
    index_list = ["NIFTY","BANKNIFTY"]
    index_list = []
    for _ in tqdm.tqdm(poolIndex.imap_unordered(download_single_index_data, index_list), total=len(index_list)):
        pass

    IndexAnalysis(index_list)

    if(current_min == "15" or current_min == "45" or 1):
        #generate_cookie()
        print(current_min + "is for stocks")
        #print(StockList)
        pool = ThreadPool(processes=STOCK_THREAD_COUNT)
        #index_list = ["SBIN","VEDL"]
        for _ in tqdm.tqdm(pool.imap_unordered(download_single_stock_data, StockList), total=len(StockList)):
            pass
    if(current_min == "15" or current_min == "45" or 1):
        Analysis(StockList,GlobalPercentage,logging,watchList,WhiteList)

    date1 = date.today()
    while int(date1.weekday()) >=5  or is_public_holiday(date1):
        date1=date1-timedelta(days=1)
    folder_Name = ".//" + str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year) + "_temp"
    Tele_not_send = False
    if(os.path.exists(folder_Name)):
        shutil.rmtree(folder_Name)
        Tele_not_send = True
    
    #Making Plot and sending
    #date2 = date1 - timedelta(days=2)
    #dates = pd.date_range(date2,date1,freq='B')
    #plot_index(dates,"NIFTY")
    #sendChart("NIFTY", Index_chatid,Index_token,Tele_not_send)
    #plot_index(dates,"BANKNIFTY")
    #sendChart("BANKNIFTY",Index_chatid,Index_token,Tele_not_send)
    #os.system('..\python.exe .\Plot_Index.py')
    
    
def fromNewSiteTeleNifty50(GlobalPercentage,logging,ExludeList,watchList,WhiteList):
    #Get list of all Stocks

    date1 = date.today()
    while int(date1.weekday()) >=5  or is_public_holiday(date1):
        date1=date1-timedelta(days=1)

    folder_Name = ".//" + str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year)
    if(not os.path.exists(folder_Name)):
        os.mkdir(folder_Name)

    file_name = folder_Name + "//StockList.csv"
    #print("Chec File name: "+file_name)
    
    StockList = stc_Nifty_50
    if(os.path.exists(file_name) or 1):
        #df = pd.read_csv(file_name)
        StockList = stc_Nifty_50
    else:
        Base_url="https://www.nseindia.com/api/master-quote"
       

        

        try:
            page = requests.get(Base_url,headers=headers,cookies=cookie_dic,timeout=30)
            #print(page.content)
            soup = BeautifulSoup(page.content, 'html.parser')
            if(soup):
                StockList = json.loads(str(soup))
                df = pd.DataFrame(StockList)
                df.to_csv(file_name, index=False)
                #StockList.append("NIFTY")
                #StockList.append("BANKNIFTY")
                #moddf = StockList.append("NIFTY")
                #StockList = moddf
                #moddf = StockList.append("BANKNIFTY")
                #StockList = moddf
            else:
                print("Soup Returned null for Stock: ")
               
           
            #print(StockList)

        except Exception as e:
            print("Exception "+str(e) +" occured while fetching Stock-List: " " Seems server down")
            tempdate = getPreviousValidDay()
            folder_Name = ".//" + str('%02d'%tempdate.day) + monthToNum(str('%02d'%tempdate.month)) + str(tempdate.year)
            file_name = folder_Name + "//StockList.csv"
            if(os.path.exists(file_name)):
                df = pd.read_csv(file_name)
                StockList = df["0"]
                #moddf = StockList.append("NIFTY")
                #StockList = moddf
                #moddf = StockList.append("BANKNIFTY")
                #StockList = moddf
                #print(StockList)
                
            else:
                StockList = []
            Total_OI = 0

    
    tempdf = pd.DataFrame(columns=['Name','Total_OI_Change','CE_Change','PE_Change','LotSize','Time','CE','PE'])


    current_time_min = time.strftime("%M")
    current_time_sec = time.strftime("%S")
    Effective_min = int(current_time_min)%Candle_timer
    timenow = datetime.now()
    current_min = (timenow - timedelta(minutes=Effective_min)).strftime("%M")

    

   

    
    

    poolIndex = ThreadPool(processes=INDEX_THREAD_COUNT)
    index_list = ["NIFTY","BANKNIFTY"]
    #index_list = []
    for _ in tqdm.tqdm(poolIndex.imap_unordered(download_single_index_data, index_list), total=len(index_list)):
        pass

    IndexAnalysis(index_list)

    if(current_min == "15" or current_min == "45" or 1):
        #generate_cookie()
        print(current_min + "is for stocks")
        #print(StockList)
        pool = ThreadPool(processes=STOCK_THREAD_COUNT)
        #index_list = ["SBIN","VEDL"]
        for _ in tqdm.tqdm(pool.imap_unordered(download_single_stock_data, StockList), total=len(StockList)):
            pass
    if(current_min == "15" or current_min == "45" or 1):
        Analysis(StockList,GlobalPercentage,logging,watchList,WhiteList)

    date1 = date.today()
    while int(date1.weekday()) >=5  or is_public_holiday(date1):
        date1=date1-timedelta(days=1)
    folder_Name = ".//" + str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year) + "_temp"
    Tele_not_send = False
    if(os.path.exists(folder_Name)):
        shutil.rmtree(folder_Name)
        Tele_not_send = True
    
    #Making Plot and sending
    #date2 = date1 - timedelta(days=2)
    #dates = pd.date_range(date2,date1,freq='B')
    #plot_index(dates,"NIFTY")
    #sendChart("NIFTY", Index_chatid,Index_token,Tele_not_send)
    #plot_index(dates,"BANKNIFTY")
    #sendChart("BANKNIFTY",Index_chatid,Index_token,Tele_not_send)
    #os.system('..\python.exe .\Plot_Index.py')

    
def fromNewSiteTele9(GlobalPercentage,logging,ExludeList,watchList,WhiteList):
    #Get list of all Stocks

    date1 = date.today()
    while int(date1.weekday()) >=5  or is_public_holiday(date1):
        date1=date1-timedelta(days=1)

    folder_Name = ".//" + str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year)
    if(not os.path.exists(folder_Name)):
        os.mkdir(folder_Name)

    file_name = folder_Name + "//StockList.csv"
    #print("Chec File name: "+file_name)
    

    if(os.path.exists(file_name)):
        df = pd.read_csv(file_name)
        StockList = df["0"]
    else:
        Base_url="https://www.nseindia.com/api/master-quote"
       

        

        try:
            page = requests.get(Base_url,headers=headers,cookies=cookie_dic,timeout=30)
            #print(page.content)
            soup = BeautifulSoup(page.content, 'html.parser')
            if(soup):
                StockList = json.loads(str(soup))
                df = pd.DataFrame(StockList)
                df.to_csv(file_name, index=False)
                #StockList.append("NIFTY")
                #StockList.append("BANKNIFTY")
                #moddf = StockList.append("NIFTY")
                #StockList = moddf
                #moddf = StockList.append("BANKNIFTY")
                #StockList = moddf
            else:
                print("Soup Returned null for Stock: ")
               
           
            #print(StockList)

        except Exception as e:
            print("Exception "+str(e) +" occured while fetching Stock-List: " " Seems server down")
            tempdate = getPreviousValidDay()
            folder_Name = ".//" + str('%02d'%tempdate.day) + monthToNum(str('%02d'%tempdate.month)) + str(tempdate.year)
            file_name = folder_Name + "//StockList.csv"
            if(os.path.exists(file_name)):
                df = pd.read_csv(file_name)
                StockList = df["0"]
                #moddf = StockList.append("NIFTY")
                #StockList = moddf
                #moddf = StockList.append("BANKNIFTY")
                #StockList = moddf
                #print(StockList)
                
            else:
                StockList = []
            Total_OI = 0

    
    tempdf = pd.DataFrame(columns=['Name','Total_OI_Change','CE_Change','PE_Change','LotSize','Time','CE','PE'])


    current_time_min = time.strftime("%M")
    current_time_sec = time.strftime("%S")
    Effective_min = int(current_time_min)%Candle_timer
    timenow = datetime.now()
    current_min = (timenow - timedelta(minutes=Effective_min)).strftime("%M")

    

   

    
    

    poolIndex = ThreadPool(processes=INDEX_THREAD_COUNT)
    index_list = ["NIFTY","BANKNIFTY"]
    #index_list = []
    for _ in tqdm.tqdm(poolIndex.imap_unordered(download_single_index_data, index_list), total=len(index_list)):
        pass

    IndexAnalysis(index_list)

    if(current_min == "15" or current_min == "45" or 1):
        #generate_cookie()
        print(current_min + "is for stocks")
        #print(StockList)
        pool = ThreadPool(processes=STOCK_THREAD_COUNT)
        #index_list = ["SBIN","VEDL"]
        for _ in tqdm.tqdm(pool.imap_unordered(download_single_stock_data9, StockList), total=len(StockList)):
            pass
    if(current_min == "15" or current_min == "45" or 1):
        Analysis(StockList,GlobalPercentage,logging,watchList,WhiteList)

    date1 = date.today()
    while int(date1.weekday()) >=5  or is_public_holiday(date1):
        date1=date1-timedelta(days=1)
    folder_Name = ".//" + str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year) + "_temp"
    Tele_not_send = False
    if(os.path.exists(folder_Name)):
        shutil.rmtree(folder_Name)
        Tele_not_send = True
    
    #Making Plot and sending
    #date2 = date1 - timedelta(days=2)
    #dates = pd.date_range(date2,date1,freq='B')
    #plot_index(dates,"NIFTY")
    #sendChart("NIFTY", Index_chatid,Index_token,Tele_not_send)
    #plot_index(dates,"BANKNIFTY")
    #sendChart("BANKNIFTY",Index_chatid,Index_token,Tele_not_send)
    #os.system('..\python.exe .\Plot_Index.py')
    
        
def fromNewSite(GlobalPercentage,logging,ExludeList,watchList):
    #Get list of all Stocks
    Base_url="https://www.nseindia.com/api/master-quote"
    headers = {'User-Agent': 'Safari/537.36'}

    try:
        page = requests.get(Base_url,headers=headers,timeout=30)
           
        
    except Exception as e:
        print("Exception "+str(e) +" occured for: "+symbol + " Skipping this 6")
        Total_OI = 0
    
    soup = BeautifulSoup(page.content, 'html.parser')
    StockList = json.loads(str(soup))
    print(StockList)

    
    OiChangedf = pd.DataFrame(columns=['Name','CMP','Strike','CE_Change','PE_Change','Fut%','LotSize','Time','ChngInLots','OptPrice','Expiry'])

    Nifty50OiChangedf = pd.DataFrame(columns=['Name','CMP','Strike','CE_Change','PE_Change','Fut%','LotSize','Time','ChngInLots','LTP','Expiry'])

    Watchlistdf = pd.DataFrame(columns=['Name','CMP','Strike','CE_Change','PE_Change','Fut%','LotSize','Time','ChngInLots','LTP','Expiry'])


    CE_MaxOIChanged = pd.DataFrame(columns=['Name','CMP','oldStrike','newStrike','Option_Type','Fut%','LotSize','Time'])

    PE_MaxOIChanged = pd.DataFrame(columns=['Name','CMP','oldStrike','newStrike','Option_Type','Fut%','LotSize','Time'])

    
    tempdf = pd.DataFrame(columns=['Name','Total_OI_Change','CE_Change','PE_Change','LotSize','Time','CE','PE'])

    #results = ThreadPool(5).map(download_FnO_Bhav, valid_list)
    #results = ThreadPool(5).map(download_cash_local_copy, valid_list)

    for i in range(len(StockList)):
        if(logging == 0):
            print(StockList[i])
        if("M&amp;M" == StockList[i]):
            StockList[i] = "M%26M"
            #print("Code changed to:"+StockList[i])
        elif("M&amp;MFIN" == StockList[i]):
            StockList[i] = "M%26MFIN"
            #print("Code changed to:"+StockList[i])
        elif("L&amp;TFH" == StockList[i]):
            StockList[i] = "L%26TFH"
            #print("Code changed to:"+StockList[i])
        elif(StockList[i] in ExludeList):
            if(logging == 0):
                print("Skipping due to Exclude list: "+StockList[i])
            continue

        if(logging != 0):
           done = int(50*i/len(StockList))
           sys.stdout.write('\r[{}{}]{}%'.format('#' * done, '.' * (50-done),done*2))
           sys.stdout.flush()
        
        tempdf_ce = pd.DataFrame(columns=['Strike','CE_OI','CE_Change','CE_LTP','Expiry'])
        tempdf_pe = pd.DataFrame(columns=['Strike','PE_OI','PE_Change','PE_LTP','Expiry'])
        CE_OI_price_list = []
        PE_OI_price_list = []
        CE_Total = []
        PE_Total = []
        Total_OI = 0
        Total_OI_change = 0
        Option_CE_Total = 0
        Option_PE_Total = 0
        Future_delta = 0
        Fut_total = 0
        Base_url=" https://www.nseindia.com/api/quote-derivative?symbol=" + StockList[i]


        try:
            page = requests.get(Base_url,headers=headers,timeout=30)
           
        except Exception as e:
            print("Exception "+str(e) +" occured for: "+StockList[i] + " Skipping this 1")
            Total_OI = 0
            
      
        soup = BeautifulSoup(page.content, 'html.parser')
        if(soup):
            d = json.loads(str(soup))
        else:
            print("Soup Returned null for Stock: "+StockList[i])
            Total_OI = 0
        #json_formatted_str = json.dumps(d, indent=2)
        #print(d["stocks"][0]["metadata"]["instrumentType"])
        for j in range (len(d["stocks"])):
            if("Stock Futures" == d["stocks"][j]["metadata"]["instrumentType"]):
                # Futures Data
                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["changeinOpenInterest"]
                if(text != '-'):
                    fut_change_oi = int(text)
                else:
                    fut_change_oi= 0
                Total_OI_change = Total_OI_change + fut_change_oi
                Future_delta = Future_delta  + fut_change_oi

                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["openInterest"]
                if(text != '-'):
                    fut_total_oi = int(text)
                else:
                    fut_total_oi= 0

                Total_OI = Total_OI + fut_total_oi
                Fut_total = Fut_total + fut_total_oi
        
                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["marketLot"]
                if(text != '-'):
                    market_lot = int(text)
                else:
                    market_lot = 0

                ltp = d["stocks"][j]["underlyingValue"]
                
            elif("Call" == d["stocks"][j]["metadata"]["optionType"]):
                #Options Call Data
                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["openInterest"]
                if(text != '-'):
                    CE_total_OI = int(text)
                else:
                    CE_total_OI= 0

                Total_OI =  Total_OI + CE_total_OI
                Option_CE_Total = Option_CE_Total + CE_total_OI
                
                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["changeinOpenInterest"]
                if(text != '-'):
                    CE_change_OI = int(text)
                else:
                    CE_change_OI= 0
                Total_OI_change = Total_OI_change + CE_change_OI

                text= d["stocks"][j]["metadata"]["lastPrice"]
                
                    
                CE_LTP = float(text)
                   

                text= d["stocks"][j]["metadata"]["strikePrice"]
                if(text != '-'):
                    strike_price = int(float(text))
                else:
                    strike_price= 0

                expDate = d["stocks"][j]["metadata"]["expiryDate"]
                CE_OI_price_list.append(CE_change_OI)

                tempmoddf = tempdf_ce.append({'Strike':strike_price,'CE_OI':CE_total_OI,'CE_Change':CE_change_OI,'CE_LTP':CE_LTP,
                                              'Expiry':expDate},ignore_index=True)
                #print(tempmoddf)
                tempdf_ce = tempmoddf
                
                
                    
            elif("Put" == d["stocks"][j]["metadata"]["optionType"]):

                text= d["stocks"][j]["metadata"]["lastPrice"]
               
                PE_LTP = float(text)
                    
                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["changeinOpenInterest"]
                if(text != '-'):
                    PE_change_OI = int(text)
                else:
                    PE_change_OI= 0
                Total_OI_change = Total_OI_change + PE_change_OI

                text = d["stocks"][j]["marketDeptOrderBook"]["tradeInfo"]["openInterest"]
                if(text != '-'):
                    PE_total_OI = int(text)
                else:
                    PE_total_OI= 0
                Total_OI = Total_OI + PE_total_OI
                Option_PE_Total = Option_PE_Total + PE_total_OI

                text= d["stocks"][j]["metadata"]["strikePrice"]
                if(text != '-'):
                    strike_price = int(float(text))
                else:
                    strike_price= 0

                PE_OI_price_list.append(PE_change_OI)

                expDate = d["stocks"][j]["metadata"]["expiryDate"]

                tempmoddf = tempdf_pe.append({'Strike':strike_price,'PE_OI':PE_total_OI,'PE_Change':PE_change_OI,'PE_LTP':PE_LTP,
                                              'Expiry':expDate},ignore_index=True)
                #print(tempmoddf)
               
                tempdf_pe = tempmoddf

            else:
                pass

        if(Total_OI !=0):
            OI_Percentage = Total_OI_change*100/Total_OI
            CE_change = sum(CE_OI_price_list)
            PE_change = sum(PE_OI_price_list)
            #CE_pert = CE_change*100/Total_OI_change
            #PE_pert = PE_change*100/Total_OI_change
            SortedDataCE = tempdf_ce.sort_values(by=['CE_Change'],ascending=False)
            SortedDataPE = tempdf_pe.sort_values(by=['PE_Change'],ascending=False)
            
    
            for j in range(len(SortedDataCE)):
                ce_row = SortedDataCE.iloc[ j , : ]
                ce_change_oi = float(ce_row['CE_Change'])
                ce_change_per = ce_change_oi*100/Total_OI
                temptime = time.strftime("%H:%M:%S")

                if(ce_change_per >=GlobalPercentage):
                    if(logging ==0):
                        print("Found Entry CE: "+ str(ce_change_per))
                    futPer = Future_delta/Fut_total*100
                    moddf = OiChangedf.append({'Name':StockList[i],'CMP':ltp,'Strike':ce_row['Strike'],'CE_Change': float(("%.2f" %ce_change_per)),'PE_Change': "NA"
                    ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'ChngInLots':ce_change_oi,'OptPrice':ce_row['CE_LTP'],'Expiry':ce_row['Expiry']},ignore_index=True)
        
                    if(logging == 0):
                        print(moddf)
                    OiChangedf=moddf
                else:
                    j = len(SortedDataCE)
           
            for j in range(len(SortedDataPE)):
           
                
                pe_row = SortedDataPE.iloc[ j , : ]
                pe_change_oi = float(pe_row['PE_Change'])
               
                pe_change_per = pe_change_oi*100/Total_OI
                temptime = time.strftime("%H:%M:%S")
                if (pe_change_per >= GlobalPercentage):
                    if(logging ==0):
                        print("Found Entry PE:"+ str(pe_change_per))
                    futPer = Future_delta/Fut_total*100  
                    moddf = OiChangedf.append({'Name':StockList[i],'CMP':ltp,'Strike':pe_row['Strike'],'CE_Change': "NA",'PE_Change': float(("%.2f" %pe_change_per))
                    ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'ChngInLots':pe_change_oi,'OptPrice':pe_row['PE_LTP'],'Expiry':pe_row['Expiry']},ignore_index=True)
        
                    if(logging == 0):
                        print(moddf)
                    OiChangedf=moddf
                else:
                    j = len(SortedDataPE)

            #Lets check Max OI as per previous day
            SortedDataMaxCE = tempdf_ce.sort_values(by=['CE_OI'],ascending=False)
            SortedDataMaxPE = tempdf_pe.sort_values(by=['PE_OI'],ascending=False)
            ce_row = SortedDataMaxCE.iloc[ 0 , : ]
            date1 = getPreviousValidDay()
            Currentpath= os.getcwd() +"\\finaloutput\\"
            csv1 = Currentpath + 'fo'+ str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year) +'bhav.csv'
            futPer = Future_delta/Fut_total*100
            if(os.path.exists(csv1) and futPer >=5 ):
                
                df1 = pd.read_csv(csv1)
                row1 = df1.loc[df1['SYMBOL'] == StockList[i]]
                optionData = row1[row1['INSTRUMENT'] == 'OPTSTK']
                optionDataCE = optionData[optionData['OPTION_TYP'] == 'CE']
                PreviousDaySortedDataMaxCE = optionDataCE.sort_values(by=['OPEN_INT'],ascending=False)
                if(len(PreviousDaySortedDataMaxCE)):
                    selected_ce_row = PreviousDaySortedDataMaxCE.iloc[ 0 , : ]
                    if( (ce_row['Strike'] != selected_ce_row['STRIKE_PR']) and (ce_row['Expiry'] == selected_ce_row['EXPIRY_DT'])):
                        #if( (ce_row['Strike'] <= ltp) and (ce_row['Expiry'] == selected_ce_row['EXPIRY_DT'])):
                            futPer = Future_delta/Fut_total*100
                            if("M%26M" == StockList[i]):
                                StockList[i] = "M&M"
                            elif("M%26MFIN" == StockList[i]):
                                StockList[i] = "M&MFIN"
                            elif("L%26TFH" == StockList[i]):
                                StockList[i] = "L&TFH"
                            moddf = CE_MaxOIChanged.append({'Name':StockList[i],'CMP':ltp,'oldStrike':selected_ce_row['STRIKE_PR'],'newStrike': ce_row['Strike'],
                                                         'Option_Type': "CE",'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime},ignore_index=True)
        
                            if(logging == 0):
                                print(moddf)
                            CE_MaxOIChanged=moddf
                    
                pe_row = SortedDataMaxPE.iloc[ 0 , : ]
                optionDataPE = optionData[optionData['OPTION_TYP'] == 'PE']
                PreviousDaySortedDataMaxPE = optionDataPE.sort_values(by=['OPEN_INT'],ascending=False)
                if(len(PreviousDaySortedDataMaxPE)):
                    selected_pe_row = PreviousDaySortedDataMaxPE.iloc[ 0 , : ]
                
                    if( (pe_row['Strike'] != selected_pe_row['STRIKE_PR']) and (pe_row['Expiry'] == selected_pe_row['EXPIRY_DT'])):
                        #if( (pe_row['Strike'] >= ltp) and (pe_row['Expiry'] == selected_pe_row['EXPIRY_DT'])):
                            futPer = Future_delta/Fut_total*100
                            if("M%26M" == StockList[i]):
                                StockList[i] = "M&M"
                            elif("M%26MFIN" == StockList[i]):
                                StockList[i] = "M&MFIN"
                            elif("L%26TFH" == StockList[i]):
                                StockList[i] = "L&TFH"
                            moddf = PE_MaxOIChanged.append({'Name':StockList[i],'CMP':ltp,'oldStrike':selected_pe_row['STRIKE_PR'],'newStrike': pe_row['Strike'],
                                                         'Option_Type': "PE",'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime},ignore_index=True)
        
                            if(logging == 0):
                                print(moddf)
                            PE_MaxOIChanged=moddf


               
                """result_index = row1['STRIKE_PR'].sub(ltp).abs().idxmin()
                strikelist = []
                result_row = df1.iloc[result_index , : ]
                strikelist.append(result_row['STRIKE_PR'])
                result_row = df1.iloc[result_index-1 , : ]
                strikelist.append(result_row['STRIKE_PR'])
                result_row = df1.iloc[result_index+1 , : ]
                strikelist.append(result_row['STRIKE_PR'])
                for k in range(len(strikelist)):
                    ce_strikes = tempdf_ce[tempdf_ce['Strike'] == strikelist[k]]
                    pe_strikes = tempdf_pe[tempdf_pe['Strike'] == strikelist[k]]
                    ce_strike_row = ce_strikes.iloc[0 , : ]
                    pe_strike_row = pe_strikes.iloc[0 , : ]
                    #print (ce_strike_row)
                    #print (pe_strike_row)

                    old_CE_OI = row1[(row1['STRIKE_PR']==strikelist[k]) & (row1['OPTION_TYP'] == "CE") & row1['EXPIRY_DT'] == ce_strike_row['Expiry']][['OPEN_INT']]
                    old_PE_OI = row1[(row1['STRIKE_PR']==strikelist[k]) & (row1['OPTION_TYP'] == "PE") & row1['EXPIRY_DT'] == ce_strike_row['Expiry']][['OPEN_INT']]
                    if((old_CE_OI > old_PE_OI) and (pe_strike_row['PE_OI'] > ce_strike_row['CE_OI'])):
                        print("For Stock "+StockList[i] + " OI Cross Over for strike "+ strikelist[k])
                    elif( (old_CE_OI < old_PE_OI) and (pe_strike_row['PE_OI'] < ce_strike_row['CE_OI'])):
                        print("For Stock "+StockList[i] + " OI Cross Over for strike "+ strikelist[k])"""
        else:
            OI_Percentage=0

        if(Total_OI !=0 and ((StockList[i] in stc_Nifty_50) or (StockList[i] in watchList))):
            #print("Nifty50 or watch:: "+StockList[i])
            CE_change = sum(CE_OI_price_list)
            PE_change = sum(PE_OI_price_list)
            #CE_pert = CE_change*100/Total_OI_change
            #PE_pert = PE_change*100/Total_OI_change

            SortedDataCE = tempdf_ce.sort_values(by=['CE_Change'],ascending=False)
            SortedDataPE = tempdf_pe.sort_values(by=['PE_Change'],ascending=False)

            for j in range(len(SortedDataCE)):
                ce_row = SortedDataCE.iloc[ j , : ]
                ce_change_oi = float(ce_row['CE_Change'])
            
                total_option = Option_CE_Total+Option_PE_Total
                ce_change_per = ce_change_oi*100/total_option
            
                temptime = time.strftime("%H:%M:%S")
                Value = market_lot*ce_change_oi*ce_row['CE_LTP']/100000
        
                if((Value >=50 and ce_change_per >=1.5) or ce_change_per>= 10 ):
                    if(logging == 0):
                        print("Found Entry CE: "+ str(ce_change_per))
                        #print(ce_max_change)
                    futPer = Future_delta/Fut_total*100
                    if(StockList[i] in stc_Nifty_50):
                        moddf = Nifty50OiChangedf.append({'Name':StockList[i],'CMP':ltp,'Strike':ce_row['Strike'],'CE_Change': float(("%.2f" %ce_change_per)),'PE_Change': "NA"
                        ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'ChngInLots':ce_change_oi,'LTP':ce_row['CE_LTP'],'Expiry':ce_row['Expiry']},ignore_index=True)
        
                        if(logging == 0):
                            print(moddf)
                        Nifty50OiChangedf=moddf
                    else:
                        moddf = Watchlistdf.append({'Name':StockList[i],'CMP':ltp,'Strike':ce_row['Strike'],'CE_Change': float(("%.2f" %ce_change_per)),'PE_Change': "NA"
                        ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'ChngInLots':ce_change_oi,'LTP':ce_row['CE_LTP'],'Expiry':ce_row['Expiry']},ignore_index=True)
        
                        if(logging == 0):
                            print(moddf)
                        Watchlistdf=moddf
                else:
                    j = len(SortedDataCE)

            for j in range(len(SortedDataPE)):
                pe_row = SortedDataPE.iloc[ j , : ]
                pe_change_oi = float(pe_row['PE_Change'])
                total_option = Option_CE_Total+Option_PE_Total
                pe_change_per = pe_change_oi*100/total_option
                Value = market_lot*pe_change_oi*pe_row['PE_LTP']/100000
                if ((Value >=50 and pe_change_per >=1.5) or pe_change_per >= 10):
                    if(logging == 0):
                        print("Found Entry PE:"+ str(pe_change_per))
                    futPer = Future_delta/Fut_total*100
                    if(StockList[i] in stc_Nifty_50):
                        moddf = Nifty50OiChangedf.append({'Name':StockList[i],'CMP':ltp,'Strike':pe_row['Strike'],'CE_Change': "NA",'PE_Change': float(("%.2f" %pe_change_per))
                        ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'ChngInLots':pe_change_oi,'LTP':pe_row['PE_LTP'],'Expiry':pe_row['Expiry']},ignore_index=True)

                        if(logging == 0):
                            print(moddf)
                        Nifty50OiChangedf=moddf
                    else:
                        moddf = Watchlistdf.append({'Name':StockList[i],'CMP':ltp,'Strike':pe_row['Strike'],'CE_Change': "NA",'PE_Change': float(("%.2f" %pe_change_per))
                        ,'Fut%':float(("%.2f" %futPer)),'LotSize':market_lot,'Time':temptime,'ChngInLots':pe_change_oi,'LTP':pe_row['PE_LTP'],'Expiry':pe_row['Expiry']},ignore_index=True)

                        if(logging == 0):
                            print(moddf)
                        Watchlistdf=moddf
                else:
                    j = len(SortedDataPE)

    if(len(OiChangedf)):
        print("\n")
        print(OiChangedf)
        print("\n")

    if(len(Nifty50OiChangedf)):
        print("#######################################################################################")
        print("Nifty Fifty Option only")
        print("#######################################################################################")
        print(Nifty50OiChangedf)
        print("\n")

    if(len(Watchlistdf)):
        print("#######################################################################################")
        print("Watchlist only")
        print("#######################################################################################")
        #print(Watchlistdf)
        print("\n")

    

    if(len(CE_MaxOIChanged)):
        print("#######################################################################################")
        print("CE - Max OI Change Stocks ")
        print("#######################################################################################")
        print(CE_MaxOIChanged)
        print("\n")

    if(len(PE_MaxOIChanged)):
        print("#######################################################################################")
        print("PE - Max OI Change Stocks ")
        print("#######################################################################################")
        print(PE_MaxOIChanged)
        print("\n")

        for j in range (len(CE_MaxOIChanged)):
            pe_row = CE_MaxOIChanged.iloc[ j , : ]
            print("Reached here")
            Str_to_send = "Name - " + pe_row['Name'] + "\nCMP - " + str(pe_row['CMP']) + "\noldStrike - " + str(pe_row['oldStrike']) + "\nnewStrike - "+ str(pe_row['newStrike']) + "\nOption-Type - CE\nFut% - " + str(pe_row['Fut%']) + "\nLotSize - " + str(pe_row['LotSize'])
            send(Str_to_send,"-1001403983472")

        for j in range (len(PE_MaxOIChanged)):
            pe_row = PE_MaxOIChanged.iloc[ j , : ]
            Str_to_send = "Name - " + pe_row['Name'] + "\nCMP - " + str(pe_row['CMP']) + "\noldStrike - " + str(pe_row['oldStrike']) + "\nnewStrike - "+ str(pe_row['newStrike']) + "\nOption-Type - PE\nFut% - " + str(pe_row['Fut%']) + "\nLotSize - " + str(pe_row['LotSize'])
            send(Str_to_send,"-1001403983472")
        
                
def newUtility(symbol):


    Base_url = "https://www.nseindia.com/get-quotes/derivatives?symbol=" + symbol
    headers = {'User-Agent': 'Safari/537.36'}

    page = requests.get(Base_url,headers=headers)
    print(page)
    print("=======================")
    print(page.headers)
    print("=======================")
    for c in page.cookies:
        print(c.name, c.value)
        #print(page.cookies)
    soup = BeautifulSoup(page.content, 'html.parser')
    #print(soup)

    """Base_url="https://www.nseindia.com/api/option-chain-equities?symbol=" + symbol
    
    options_temp_df = pd.DataFrame(columns=['Strike','CE_OI','CE_Change','CE_Vol','CE_LTP','PE_LTP','PE_Vol','PE_OI','PE_Change','Expiry'])
    

    page = requests.get(Base_url,headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    d = json.loads(str(soup))
    json_formatted_str = json.dumps(d, indent=2)
    print(json_formatted_str)
    for i in range((len(d["records"]["data"]))):
        strike = d["records"]["data"][i]["strikePrice"]
        print(str(strike))
        Expiry = d["records"]["data"][i]["expiryDate"]
        if "CE" in d["records"]["data"][i]:
            CE_OI  = d["records"]["data"][i]["CE"]['openInterest']
            CE_Change = d["records"]["data"][i]["CE"]['changeinOpenInterest']
            CE_LTP = d["records"]["data"][i]["CE"]['lastPrice']
            CE_VOL = d["records"]["data"][i]["CE"]['totalTradedVolume']
        if "PE" in d["records"]["data"][i]:
            PE_OI  = d["records"]["data"][i]["PE"]['openInterest']
            PE_Change = d["records"]["data"][i]["PE"]['changeinOpenInterest']
            PE_LTP = d["records"]["data"][i]["PE"]['lastPrice']
            PE_VOL = d["records"]["data"][i]["PE"]['totalTradedVolume']

        tempmoddf = options_temp_df.append({'Strike':strike,'CE_OI':CE_OI,'CE_Change':CE_Change,'CE_VOL':CE_VOL,'CE_LTP':CE_LTP,'PE_LTP':PE_LTP,
                                            'PE_VOL':PE_VOL,'PE_OI':PE_OI,'PE_Change':PE_Change,'Expiry':Expiry},ignore_index=True)
        options_temp_df = tempmoddf

    SortedDataCE = options_temp_df.sort_values(by=['CE_Change'],ascending=False)
    SortedDataPE = options_temp_df.sort_values(by=['PE_Change'],ascending=False)
            
    print(SortedDataCE.head(5))
    print(SortedDataPE.head(5))

    Base_url=" https://www.nseindia.com/api/quote-derivative?symbol=" + symbol
    page = requests.get(Base_url,headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    d = json.loads(str(soup))
    json_formatted_str = json.dumps(d, indent=2)
    print(json_formatted_str)
    """
            
    #for i in d["records"]["data"]:
     #   text = d["records"]["data"][i]
      #  print(text)
    #print(soup.prettify)
    #print(soup.derivativeAllContracts)
    # Locate where expiry date details are available
    #locate_expiry_point = soup.find(id="derivativeAllContracts")
    #str_data = str(locate_expiry_point)
    #print(locate_expiry_point)
    
    #expiry_rows = locate_expiry_point.find_all('option')

    #index = 0
    #expiry_list = []
    #for each_row in expiry_rows:
        # skip first row as it does not have value
     #   if index <= 0:
      #      index = index + 1
       #     continue
       # index = index + 1
        # Remove HTML tag and save to list
        #expiry_list.append(BeautifulSoup(str(each_row), 'html.parser').get_text())

    #print(expiry_list)

    #tds = soup.find_all('td')
    #csv_data = []

    #for td in tds:
     #   inner_text = td.text
      #  strings = inner_text.split("\n")

       # csv_data.extend([string for string in strings if string])

    #print(",".join(csv_data))
    #for child in soup.recursiveChildGenerator():
     #   if child.name:
      #      print(child.name)

    #print(soup.dumps())
    

def test(symbol):
    #Base_url = "https://www.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?symbol=" + symbol + "&date=" + exp_list[i]

    Base_url = "https://www1.nseindia.com/live_market/dynaContent/live_watch/get_quote/GetQuoteFO.jsp?underlying=" +symbol +"&instrument=FUTSTK&expiry=26MAR2020"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    #res = requests.get(url, headers=headers)
    
    page = requests.get(Base_url,headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    table_cls_2 = soup.find(id="responseDiv")
    #req_row = table_cls_2.find_all('li')

    #for i in range(len(table_cls_2)):
        #text = BeautifulSoup(str(table_cls_2[i]), 'html.parser').get_text()
        #print(table_cls_2[i])


    
    print(table_cls_2)
    
    str_data = str(table_cls_2)
    dataSplited = str_data.split('{',1)
    
    actualData = "{" + dataSplited[1]
    print(actualData)
    #print(table_cls_2.value())
    #obj = JSON.parse("{"+table_cls_2+"}");JSON
    dataSplited = actualData.split('}')
    actualData = ''
    for i in range(len(dataSplited)-1):
        actualData = actualData + dataSplited[i] + "}"
    #actualData = actualData+ "}"
    print(actualData)
    d = json.loads(actualData)
    #dataSplited = table_cls_2.split('{')
    print(d["data"][0]["pchangeinOpenInterest"])
    print(d["data"][0]["changeinOpenInterest"])
    print(d["data"][0]["pchangeinOpenInterest"])
    #tree = ET.parse(table_cls_2)
    #print(tree)

def test2():
    proxy_support = urllib.request.ProxyHandler({"http":"http://61.233.25.166:80"})
    opener = urllib.request.build_opener(proxy_support)
    urllib.request.install_opener(opener)
    print ("qwqwq")
    html = urllib.request.urlopen("https://www.nseindia.com/companies-listing/corporate-filings-shareholding-pattern").read()
    print (html)


def IndexView():
    #Index Option Chain Analysis
    StockList = ["NIFTY","BANKNIFTY"]
    headers = {'User-Agent': 'Safari/537.36'}
    options_temp_df = pd.DataFrame(columns=['Strike','CE_OI','CE_Change','CE_VOL','CE_LTP','PE_LTP','PE_VOL','PE_OI','PE_Change','Expiry'])
    OiChangedf = pd.DataFrame(columns=['Name','CMP','Strike','CE_Change','PE_Change','LotSize','Time','ChngInLots','Expiry'])
    for i in range(len(StockList)):
        tempdf_ce = pd.DataFrame(columns=['Strike','CE_OI','CE_Change','CE_LTP','Expiry'])
        tempdf_pe = pd.DataFrame(columns=['Strike','PE_OI','PE_Change','PE_LTP','Expiry'])
        CE_OI_price_list = []
        PE_OI_price_list = []
        CE_Total = []
        PE_Total = []
        Total_OI = 0
        Total_OI_change = 0
        Option_CE_Total = 0
        Option_PE_Total = 0
        Future_delta = 0
        Fut_total = 0
        CE_OI = 0
        CE_Change = 0
        CE_LTP = 0
        CE_VOL = 0
        PE_OI = 0
        PE_Change = 0
        PE_VOL = 0
        PE_LTP = 0
        
        Base_url=" https://www.nseindia.com/api/option-chain-indices?symbol=" + StockList[i]

        try:
            page = requests.get(Base_url,headers=headers,timeout=30)
           
        except Exception as e:
            print("Exception "+str(e) +" occured for: "+StockList[i] + " Skipping this 2")
            Total_OI = 0

        soup = BeautifulSoup(page.content, 'html.parser')
        d = json.loads(str(soup))

        if "index" in d["records"]:
            ltp = d["records"]["index"]["last"]
            advance = d["records"]["index"]["advances"]
            decline = d["records"]["index"]["declines"]
        else:
            ltp = 0
        
        for j in range (len(d["records"]["data"])):
            strike = d["records"]["data"][j]["strikePrice"]
            #print(str(strike))
            Expiry = d["records"]["data"][j]["expiryDate"]
            if "CE" in d["records"]["data"][j]:
                CE_OI  = d["records"]["data"][j]["CE"]['openInterest']
                Total_OI = Total_OI + CE_OI
                CE_Change = d["records"]["data"][j]["CE"]['changeinOpenInterest']
                CE_LTP = d["records"]["data"][j]["CE"]['lastPrice']
                CE_VOL = d["records"]["data"][j]["CE"]['totalTradedVolume']
            if "PE" in d["records"]["data"][j]:
                PE_OI  = d["records"]["data"][j]["PE"]['openInterest']
                Total_OI = Total_OI + PE_OI
                PE_Change = d["records"]["data"][j]["PE"]['changeinOpenInterest']
                PE_LTP = d["records"]["data"][j]["PE"]['lastPrice']
                PE_VOL = d["records"]["data"][j]["PE"]['totalTradedVolume']

            tempmoddf = options_temp_df.append({'Strike':strike,'CE_OI':CE_OI,'CE_Change':CE_Change,'CE_VOL':CE_VOL,'CE_LTP':CE_LTP,'PE_LTP':PE_LTP,
                                            'PE_VOL':PE_VOL,'PE_OI':PE_OI,'PE_Change':PE_Change,'Expiry':Expiry},ignore_index=True)
            options_temp_df = tempmoddf

        SortedDataCE = options_temp_df.sort_values(by=['CE_Change'],ascending=False)
        SortedDataPE = options_temp_df.sort_values(by=['PE_Change'],ascending=False)
            
        #print(SortedDataCE.head(5))
        #print(SortedDataPE.head(5))
        OiChangedf = pd.DataFrame(columns=['Name','CMP','Strike','CE_Change','PE_Change','Fut%','LotSize','Time','ChngInLots','OptPrice','Expiry'])

        for j in range(5):
            ce_row = SortedDataCE.iloc[ j , : ]
            #ce_sum = ce_row['CE_OI'].sum()
            ce_percent = ce_row['CE_Change']*100/Total_OI
            temptime = time.strftime("%H:%M:%S")


            moddf = OiChangedf.append({'Name':StockList[i],'CMP':ltp,'Strike':ce_row['Strike'],'CE_Change': float(("%.2f" %ce_percent)),'PE_Change': "NA"
                    ,'Fut%':"NA",'LotSize':"25",'Time':temptime,'ChngInLots':ce_row['CE_Change'],'OptPrice':ce_row['CE_LTP'],'Expiry':ce_row['Expiry']},ignore_index=True)
        
            #print(moddf)
            OiChangedf=moddf
           

        for j in range(5):
            pe_row = SortedDataPE.iloc[ j , : ]
            #ce_sum = ce_row['CE_OI'].sum()
            pe_percent = pe_row['PE_Change']*100/Total_OI
            temptime = time.strftime("%H:%M:%S")


            moddf = OiChangedf.append({'Name':StockList[i],'CMP':ltp,'Strike':pe_row['Strike'],'CE_Change': "NA",'PE_Change': float(("%.2f" %pe_percent))
                    ,'Fut%':"NA",'LotSize':"25",'Time':temptime,'ChngInLots':ce_row['CE_Change'],'OptPrice':pe_row['CE_LTP'],'Expiry':pe_row['Expiry']},ignore_index=True)
        
            #print(moddf)
            OiChangedf=moddf

            

        print(OiChangedf)


def start_timer_until(target_hour, target_minute):
    """
    Starts a timer that runs until the specified hour and minute of the current day.
    """
    while True:
        now = datetime.now()
        target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

        if now >= target_time:
            print(f"It's {target_hour:02d}:{target_minute:02d} PM! Timer finished.")
            break
        else:
            time_left = target_time - now
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            print(f"Time remaining: {hours:02d}h {minutes:02d}m {seconds:02d}s", end='\r')
            time.sleep(1)

# Set the target time to 2 PM

def AnalyseUnwinding(date1,time1):

    CEOiChangedf = pd.DataFrame(columns=['Name','Price','Strike','MorningOI','ChngInLots','LotsLeft','Percent','OptPrice','Sauda','Expiry'])
    PEOiChangedf = pd.DataFrame(columns=['Name','Price','Strike','MorningOI','ChngInLots','LotsLeft','Percent','OptPrice','Sauda','Expiry'])
    timenow = datetime.now()
    Candle_timer = 15
    current_time_min = time.strftime("%M")
    current_time_sec = time.strftime("%S")
    current_time_hour = time.strftime("%H") 
    Effective_min = int(current_time_min)%Candle_timer
    if(time1 == "1"):
        current_time = (timenow - timedelta(minutes=Effective_min)).strftime("%H:%M")
    else:
        current_time = "15:30"
    #current_time = "21:45"
    folder_Name = ".//" + str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year)
    if(not os.path.exists(folder_Name)):
        os.mkdir(folder_Name)

    file_name =  ".//StockList.csv"
    if(os.path.exists(file_name)):
        df = pd.read_csv(file_name)
        StockList = df["0"]
    
    if(((int(current_time_hour) <= 8) or
        ((int(current_time_hour) <= 9) and (int(current_time_min) <=25)) or
        ((int(current_time_hour) >= 15) and (int(current_time_min) >=40)) or
         (int(current_time_hour) >= 16)) and time1 =="1"): 
        #print("To_temp_folder")
        folder_Name = ".//" + str('%02d'%date1.day) + monthToNum(str('%02d'%date1.month)) + str(date1.year) + "_temp"
        
    print(current_time)
    for i in range (len(StockList)):
        
        file_name = folder_Name + "//" + StockList[i] + ".csv"
        if(os.path.exists(file_name) ):
            df_stock = pd.read_csv(file_name)
            df_ce = df_stock.loc[((df_stock['Type'] == "CE") & (df_stock['Time'] == current_time) & (df_stock['OI_Change'] < 0)) ]
            df_pe = df_stock.loc[((df_stock['Type'] == "PE") & (df_stock['Time'] == current_time)& (df_stock['OI_Change'] < 0)) ]
            SortedDataCE = df_ce.sort_values(by=['OI_Change'],ascending=True)
            SortedDataPE = df_pe.sort_values(by=['OI_Change'],ascending=True)
            #print(df_ce)
            for index, row in SortedDataCE.iterrows():
                #print(row)
                #print(df_ce.iloc[i, 0], df_ce.iloc[i, 11])
                ce_row_Fut = df_stock.loc[((df_stock['Expiry'] == row['Expiry']) & (df_stock['Type'] == "Fut") & (df_stock['Time'] == current_time) )]
                if(len(ce_row_Fut) != 0):
                    rowFut = ce_row_Fut.iloc[ 0 , : ]
                    KitnePaise = rowFut['Lotsize']*row['LTP']
                    Current_Strike = row['Strike']
                    StrikeTill10percent = rowFut['LTP']*1.1
                    #print(StrikeTill10percent)
                    if((StrikeTill10percent > Current_Strike) & (Current_Strike > rowFut['LTP']) ):
                        OICHange= row['OI_Change']
                        absolOI = abs(OICHange)
                        TotalOI = row['OI'] - OICHange
                        #print(OICHange)
                        Percentage = absolOI/TotalOI*100
                        Percent_number = round(Percentage, 2)
                        if(((TotalOI>=500) & (OICHange < 0))):
                            if( Percent_number > 15):
                
                                moddf = CEOiChangedf.append({'Name':StockList[i],'Price':rowFut['LTP'],'Strike':row['Strike'],'MorningOI':TotalOI,'ChngInLots':row['OI_Change'],'LotsLeft':row['OI'],'Percent':Percent_number,'OptPrice':row['LTP'],'Sauda':KitnePaise,
                                'Expiry':row['Expiry']},ignore_index=True)

                        
                                CEOiChangedf=moddf
                else:
                    print("Data not found")
                            
                            
            for index, row in SortedDataPE.iterrows():
                #print(row)
                #print(df_ce.iloc[i, 0], df_ce.iloc[i, 11])
                pe_row_Fut = df_stock.loc[((df_stock['Expiry'] == row['Expiry']) & (df_stock['Type'] == "Fut") & (df_stock['Time'] == current_time) )]
                if(len(pe_row_Fut) != 0):
                    rowFut = pe_row_Fut.iloc[ 0 , : ]
                    KitnePaise = rowFut['Lotsize']*row['LTP']
                    Current_Strike = row['Strike']
                    StrikeTill10percent = rowFut['LTP']*.90
                    if((StrikeTill10percent < Current_Strike) & (Current_Strike < rowFut['LTP']) ):
                        OICHange = row['OI_Change']
                        absolOI = abs(OICHange)
                        TotalOI = row['OI'] - OICHange
                        Percentage = absolOI/TotalOI*100
                        Percent_number = round(Percentage, 2)
                        if(((TotalOI>=500) & (OICHange < 0))):
                            if(Percent_number > 15):
                
                                moddf = PEOiChangedf.append({'Name':StockList[i],'Price':rowFut['LTP'],'Strike':row['Strike'],'MorningOI':TotalOI,'ChngInLots':row['OI_Change'],'LotsLeft':row['OI'],'Percent':Percent_number,'OptPrice':row['LTP'],'Sauda':KitnePaise,
                                'Expiry':row['Expiry']},ignore_index=True)

                        
                                PEOiChangedf=moddf
                else:
                      print("Data not found")
            
            #pe_row = SortedDataPE.iloc[ 0 , : ]
            
            #moddf = PEOiChangedf.append({'Name':StockList[i],'Strike':pe_row['Strike'],'TotalLots':pe_row['OI'],'ChngInLots':pe_row['OI_Change'],'OptPrice':pe_row['LTP'],'Vwap':pe_row['Vwap'],
                  #  'Expiry':pe_row['Expiry']},ignore_index=True)

                    
            #PEOiChangedf=moddf
            
    #SortedDataStocksCE = CEOiChangedf.sort_values(by=['ChngInLots'],ascending=True)
    #SortedDataStocksPE = PEOiChangedf.sort_values(by=['ChngInLots'],ascending=True)
     
    print("#######################################################################################")
    print("CE - Max OI Unwinding ")
    print("#######################################################################################")
    print(CEOiChangedf)
     
    print("#######################################################################################")
    print("PE - Max OI Unwinding ")
    print("#######################################################################################")
    print(PEOiChangedf)
    
def main(t,i,n,exp):
    global TimeForExcel
    timestart = time.strftime("%Y-%m-%d-%H-%M-%S")
    input_option = "1"
    #config = configparser.ConfigParser()
    #config.read('Config.ini')
    if(i==0):
        print ("****************************************************************************")
        print ("********************                                    ********************")
        print ("******************** Climax Action Version 1.0 *****************************")
        print ("********************                                    ********************")
        print ("****************************************************************************")
        print ("******************** Started at "+str(timestart)+"*************************")
        print ("****************************************************************************")
        print ("*********************Creater : Sonshu/heartwon******************************")
        print ("****************************************************************************")
        print ("\n")
    
    
        #input_option = input("Please enter the choice:")
        option_selected = "1"

    if(input_option == "2"):
        date_entry = input('Enter a date in DD-MM-YYYY format:')
        day, month, year = map(int, date_entry.split('-'))
        date1 = date(year, month, day)
        AnalyseUnwinding(date1,"2")
         
    else:
        

    
   
        current_time_min = time.strftime("%M")
        current_time_sec = time.strftime("%S")
        Effective_min = Candle_timer - int(current_time_min)%Candle_timer
        tempTimer = Effective_min*60 - int(current_time_sec)
       # print(stc_Nifty_50)

        #print("Wait for {0} seconds from {1}".format(tempTimer,
         #                                               datetime.now().strftime("%H:%M:%S.%f")))

        #while(tempTimer >0):
         #   if(input_option=='9'):
          #      tempTimer=5
           # if(tempTimer >100):
            #    time.sleep(60)
             #   tempTimer = tempTimer-59
            #elif(tempTimer >5 and tempTimer < 100):
             #   time.sleep(5)
              #  tempTimer=tempTimer-5
            #elif(tempTimer <= 5):
             #   time.sleep(tempTimer)
              #  tempTimer=0
                
            
                   
            #sys.stdout.write('\r[Waiting for {} seconds more]'.format(tempTimer))
            #sys.stdout.flush()
            
        #Check Time
        
        #14:00
        now = datetime.now()
        target_time930 = now.replace(hour=9, minute=30, second=0, microsecond=0)
        target_time945 = now.replace(hour=9, minute=45, second=0, microsecond=0)
        target_time10 = now.replace(hour=10, minute=00, second=0, microsecond=0)
        target_time1015 = now.replace(hour=10, minute=15, second=0, microsecond=0)
        target_time1030 = now.replace(hour=10, minute=30, second=0, microsecond=0)
        target_time1045 = now.replace(hour=10, minute=45, second=0, microsecond=0)
        target_time1100 = now.replace(hour=11, minute=00, second=0, microsecond=0)
        target_time1115 = now.replace(hour=11, minute=15, second=0, microsecond=0)
        target_time1130 = now.replace(hour=11, minute=30, second=0, microsecond=0)
        target_time1145 = now.replace(hour=11, minute=45, second=0, microsecond=0)
        target_time1200 = now.replace(hour=12, minute=00, second=0, microsecond=0)
        target_time1215 = now.replace(hour=12, minute=15, second=0, microsecond=0)
        target_time1230 = now.replace(hour=12, minute=30, second=0, microsecond=0)
        target_time1245 = now.replace(hour=12, minute=45, second=0, microsecond=0)
        target_time1300 = now.replace(hour=13, minute=00, second=0, microsecond=0)
        target_time1315 = now.replace(hour=13, minute=15, second=0, microsecond=0)
        target_time1330 = now.replace(hour=13, minute=30, second=0, microsecond=0)
        target_time1345 = now.replace(hour=13, minute=45, second=0, microsecond=0)
        
        target_time14 = now.replace(hour=14, minute=00, second=0, microsecond=0)
        target_time1415 = now.replace(hour=14, minute=15, second=0, microsecond=0)
        target_time1430 = now.replace(hour=14, minute=30, second=0, microsecond=0)
        target_time1445 = now.replace(hour=14, minute=45, second=0, microsecond=0)
        target_time1500 = now.replace(hour=15, minute=00, second=0, microsecond=0)
        target_time1505 = now.replace(hour=15, minute=5, second=0, microsecond=0)
        target_time1510 = now.replace(hour=15, minute=10, second=0, microsecond=0)
        target_time1515 = now.replace(hour=15, minute=15, second=0, microsecond=0)
        target_time1520 = now.replace(hour=15, minute=20, second=0, microsecond=0)
        target_time1525 = now.replace(hour=15, minute=25, second=0, microsecond=0)
        target_time1530 = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        if now < target_time930:
            start_timer_until(9, 30)  
        elif (now > target_time930 and now < target_time945) :
            start_timer_until(9, 45)
        elif (now > target_time945 and now < target_time10) :
            start_timer_until(10, 00)
        elif (now > target_time10 and now < target_time1015) :
            start_timer_until(10, 15)
        elif (now > target_time1015 and now < target_time1030) :
            start_timer_until(10, 30)
        elif (now > target_time1030 and now < target_time1045) :
            start_timer_until(10, 45)
        elif (now > target_time1045 and now < target_time1100) :
            start_timer_until(11, 00)
        elif (now > target_time1100 and now < target_time1115) :
            start_timer_until(11, 15)
        elif (now > target_time1115 and now < target_time1130) :
            start_timer_until(11, 30)
        elif (now > target_time1130 and now < target_time1145) :
            start_timer_until(11, 45)
        elif (now > target_time1145 and now < target_time1200) :
            start_timer_until(12, 00)
        elif (now > target_time1200 and now < target_time1215) :
            start_timer_until(12, 15)
        elif (now > target_time1215 and now < target_time1230) :
            start_timer_until(12, 30)
        elif (now > target_time1230 and now < target_time1245) :
            start_timer_until(12, 45)
        elif (now > target_time1245 and now < target_time1300) :
            start_timer_until(13, 00)
        elif (now > target_time1300 and now < target_time1315) :
            start_timer_until(13, 15)
        elif (now > target_time1315 and now < target_time1330) :
            start_timer_until(13, 30)
        elif (now > target_time1330 and now < target_time1345) :
            start_timer_until(13, 45)
        elif (now > target_time1345 and now < target_time14) :
            start_timer_until(14, 00)  
        elif (now > target_time14 and now < target_time1415) :
            start_timer_until(14, 15)  
        elif (now > target_time1415 and now < target_time1430) :
            start_timer_until(14, 30)  
        elif (now > target_time1430 and now < target_time1445) :
            start_timer_until(14, 45)
        elif (now > target_time1445 and now < target_time1500) :
            start_timer_until(15, 00)  
        elif (now > target_time1500 and now < target_time1505) :
            start_timer_until(15, 5)  
        elif (now > target_time1505 and now < target_time1510) :
            start_timer_until(15, 10)  
        elif (now > target_time1510 and now < target_time1515) :
            start_timer_until(15, 15)  
        elif (now > target_time1515 and now < target_time1520) :
            start_timer_until(15, 20)  
        elif (now > target_time1520 and now < target_time1525) :
            start_timer_until(15, 25)  
        elif (now > target_time1525 and now < target_time1530) :
            start_timer_until(15, 30)
        else:
            print("Market Closed")
            #t = 1
            current_time_min = time.strftime("%M")
            current_time_sec = time.strftime("%S")
            Effective_min = Candle_timer - int(current_time_min)%Candle_timer
            tempTimer = Effective_min*60 - int(current_time_sec)
            print("Wait for {0} seconds from {1}".format(tempTimer,
                                                        datetime.now().strftime("%H:%M:%S.%f")))

            while(tempTimer >0):
                if(tempTimer >100):
                    time.sleep(60)
                    tempTimer = tempTimer-59
                elif(tempTimer >5 and tempTimer < 100):
                    time.sleep(5)
                    tempTimer=tempTimer-5
                elif(tempTimer <= 5):
                    time.sleep(tempTimer)
                    tempTimer=0
                
            
                   
                sys.stdout.write('\r[Waiting for {} seconds more]'.format(tempTimer))
                sys.stdout.flush()
            
        current_time = time.strftime("%H:%M")
        print ("\n")
        
        
        pool = ThreadPool(processes=STOCK_THREAD_COUNT)
        #index_list = ["NIFTY","BANKNIFTY"]
        #print(stc_Nifty_50)
        #print(all_stc_list)
        #stc_Nifty_50 = all_stc_list
        file_name = ".//StockList.csv"
        #print("Chec File name: "+file_name)

        TimeForExcel = current_time
        print(TimeForExcel)
        if(os.path.exists(file_name)):
            df = pd.read_csv(file_name)
            all_stc_list = df["0"]
        
        
            
            for _ in tqdm.tqdm(pool.imap_unordered(download_single_stock_data, all_stc_list), total=len(all_stc_list)):
                pass
                
            
            FinddataAfter2(date.today())
            #Analysis(all_stc_list,GlobalPercentage,1,watchList,WhiteList)

            #print("Test with driver:"+timestart)
            #driver = webdriver.Chrome()
            
            #driver.get("https://www.nseindia.com/api/quote-derivative?symbol=SBIN")
            #cookies = driver.get_cookies()
            #doup = driver.page_source
            #soup = BeautifulSoup(driver.page_source)
            #dict_from_json = json.loads(soup.find("body").text)
            #d = json.loads(driver.find_element_by_tag_name('body').text)
            
            #cookie_dic = {}
            #for cookie in cookies:
                #cookie_dic[cookie['name']] = cookie['value']
                #print("Name: "+ cookie['name'] + " Value: " + cookie['value'] )

            #driver.quit()
            #print(doup)
            #df = pd.read_xml( f'https://www.nseindia.com/api/quote-derivative?symbol=SBIN')
            #print(df)

            #fromNewSiteTeleNifty50(GlobalPercentage,Timer,ExludeList,watchList,WhiteList)
            #if(Timer != 0):
                #timestart = time.strftime("%H-%M-%S")
                #print("The Selected Data at:"+timestart)    
            #file_name = ".//StockList.csv"
          
            #AnalyseUnwinding(date.today(),"1")
            main(1,1,"No","hehe")
            #print("Timer value is:"+str(Timer))
           
   
        FinddataAfter2(date.today())
        #AnalyseUnwinding(date.today(),"1")
    
    timeend = time.strftime("%Y-%m-%d-%H-%M-%S")   
    print ("\n")
    print ("****************************************************************************")
    print ("******************** Climax Action Version 1.0 ******************************")
    print ("****************************************************************************")
    print ("******************** Finished at "+str(timeend)+"************************")
   
    print ("\n")

main(0,0,"No","hehe")