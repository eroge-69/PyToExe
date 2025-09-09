#Крякнул  Asoru мой ккнал: @perehodasoru Anubis идёт нахуй теперь проект мой
while True:
    try:
        import platform
        import os
        os.system("pip install pystyle phonenumbers requests whois python-whois colorama")
        import sys
        import socket
        import pystyle
        import phonenumbers, phonenumbers.timezone, phonenumbers.carrier, phonenumbers.geocoder
        import requests
        import whois
        import random
        import colorama
        import threading
        import string
        import faker
        import bs4
        import urllib.parse
        import colorama
        import concurrent.futures
        import csv
        from pystyle import Colorate, Colors
        import hashlib
        import uuid

        if platform.system() == "Windows":
            import ctypes
            GWL_STYLE = -16
            WS_SIZEBOX = 262144
            WS_MAXIMIZEBOX = 65536
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
            style = style & ~WS_SIZEBOX
            style = style & ~WS_MAXIMIZEBOX
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 3)
            enter = pystyle.Colorate.Horizontal(pystyle.Colors.white_to_red, ('Welcome to Osint Legion, Press "enter" to continue!'))
            pystyle.Anime.Fade(
            pystyle.Center.Center('''░█████╗░░██████╗██╗███╗░░██╗████████╗  ██╗░░░░░███████╗░██████╗░██╗░█████╗░███╗░░██╗   
██╔══██╗██╔════╝██║████╗░██║╚══██╔══╝  ██║░░░░░██╔════╝██╔════╝░██║██╔══██╗████╗░██║
██║░░██║╚█████╗░██║██╔██╗██║░░░██║░░░  ██║░░░░░█████╗░░██║░░██╗░██║██║░░██║██╔██╗██║
██║░░██║░╚═══██╗██║██║╚████║░░░██║░░░  ██║░░░░░██╔══╝░░██║░░╚██╗██║██║░░██║██║╚████║
╚█████╔╝██████╔╝██║██║░╚███║░░░██║░░░  ███████╗███████╗╚██████╔╝██║╚█████╔╝██║░╚███║
░╚════╝░╚═════╝░╚═╝╚═╝░░╚══╝░░░╚═╝░░░  ╚══════╝╚══════╝░╚═════╝░╚═╝░╚════╝░╚═╝░░╚══╝
                                                                                 
                Welcome on Osint Legion Tool'''), pystyle.Colors.white_to_red, pystyle.Colorate.Vertical, enter=True)
        def Main():
            if platform.system() == "Windows":
                os.system("cls")
                pystyle.Write.Print(pystyle.Center.XCenter('''
                                                              
                               

░█████╗░░██████╗██╗███╗░░██╗████████╗  ██╗░░░░░███████╗░██████╗░██╗░█████╗░███╗░░██╗
██╔══██╗██╔════╝██║████╗░██║╚══██╔══╝  ██║░░░░░██╔════╝██╔════╝░██║██╔══██╗████╗░██║
██║░░██║╚█████╗░██║██╔██╗██║░░░██║░░░  ██║░░░░░█████╗░░██║░░██╗░██║██║░░██║██╔██╗██║
██║░░██║░╚═══██╗██║██║╚████║░░░██║░░░  ██║░░░░░██╔══╝░░██║░░╚██╗██║██║░░██║██║╚████║
╚█████╔╝██████╔╝██║██║░╚███║░░░██║░░░  ███████╗███████╗╚██████╔╝██║╚█████╔╝██║░╚███║
░╚════╝░╚═════╝░╚═╝╚═╝░░╚══╝░░░╚═╝░░░  ╚══════╝╚══════╝░╚═════╝░╚═╝░╚════╝░╚═╝░░╚══╝   
                                                                      
                                                                      
                                                                      \n'''), pystyle.Colors.white_to_red, interval = 0.0005)
            else:
                os.system("clear")
                pystyle.Write.Print(pystyle.Center.XCenter('''                                                                   
                                    _     _     

░█████╗░░██████╗██╗███╗░░██╗████████╗  ██╗░░░░░███████╗░██████╗░██╗░█████╗░███╗░░██╗
██╔══██╗██╔════╝██║████╗░██║╚══██╔══╝  ██║░░░░░██╔════╝██╔════╝░██║██╔══██╗████╗░██║
██║░░██║╚█████╗░██║██╔██╗██║░░░██║░░░  ██║░░░░░█████╗░░██║░░██╗░██║██║░░██║██╔██╗██║
██║░░██║░╚═══██╗██║██║╚████║░░░██║░░░  ██║░░░░░██╔══╝░░██║░░╚██╗██║██║░░██║██║╚████║
╚█████╔╝██████╔╝██║██║░╚███║░░░██║░░░  ███████╗███████╗╚██████╔╝██║╚█████╔╝██║░╚███║
░╚════╝░╚═════╝░╚═╝╚═╝░░╚══╝░░░╚═╝░░░  ╚══════╝╚══════╝░╚═════╝░╚═╝░╚════╝░╚═╝░░╚══╝
                                                                        
                                                             \n'''), pystyle.Colors.white_to_red, interval = 0.0005)
            pystyle.Write.Print(pystyle.Center.XCenter('''\n
                                                            
 [1] Phone Lookup           [20] User-agent Generator         
 [2] Website Lookup         [18] Mac-Address Lookup   
 [3] Nick Lookup            [14] Identity Generator 
 [4] IP lookup              [9] Password Generator                
                   
                                                             
'''), pystyle.Colors.white_to_red, interval = 0.0005)
        Main()
        while True:
            choice = pystyle.Write.Input("\n\n[?] Select the option -> ", pystyle.Colors.white_to_red, interval = 0.001)
            if choice == "1":
                phone = pystyle.Write.Input("\n[?] Enter the phone number -> ", pystyle.Colors.white_to_red, interval = 0.005)
                def phoneinfo(phone):
                    try:
                        parsed_phone = phonenumbers.parse(phone, None)
                        if not phonenumbers.is_valid_number(parsed_phone):
                            return pystyle.Write.Print(f"\n[!] An error occurred -> Invalid phone number\n", pystyle.Colors.white_to_red, interval=0.005)
                        carrier_info = phonenumbers.carrier.name_for_number(parsed_phone, "en")
                        country = phonenumbers.geocoder.description_for_number(parsed_phone, "en")
                        region = phonenumbers.geocoder.description_for_number(parsed_phone, "ru")
                        formatted_number = phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                        is_valid = phonenumbers.is_valid_number(parsed_phone)
                        is_possible = phonenumbers.is_possible_number(parsed_phone)
                        timezona = phonenumbers.timezone.time_zones_for_number(parsed_phone)
                        print_phone_info = f"""\n[+] Phone Number -> {formatted_number}
[+] Country -> {country}
[+] Region -> {region}
[+] Operator -> {carrier_info}
[+] Таймзона -> {timezona}
[+] Telegram -> https://t.me/{phone}
[+] Whatsapp -> https://wa.me/{phone}
[+] Viber -> https://viber.click/{phone}\n"""
                        pystyle.Write.Print(print_phone_info, pystyle.Colors.white_to_red, interval=0.005)
                    except Exception as e:
                        pystyle.Write.Print(f"\n[!] An error occurred -> {str(e)}\n", pystyle.Colors.white_to_red, interval=0.005)
                phoneinfo(phone)
            if choice == "2":
                domain = pystyle.Write.Input("\n[?] Enter the site -> ", pystyle.Colors.white_to_red, interval = 0.005)
                def get_website_info(domain):
                    domain_info = whois.whois(domain)
                    print_string = f"""
[+] Domain: {domain_info.domain_name}
[+] Creation Date: {domain_info.creation_date} 
[+] Address: {domain_info.registrant_address}
[+] City: {domain_info.registrant_city}
[+] State: {domain_info.registrant_state}
[+] Postal Code: {domain_info.registrant_postal_code}
[+] Country: {domain_info.registrant_country}
[+] IP: {domain_info.name_servers}
        """
                    pystyle.Write.Print(print_string, pystyle.Colors.white_to_red, interval=0.005)
                get_website_info(domain)
            if choice == "3":
                nick = pystyle.Write.Input(f"\n[?] Enter the Nickname -> ", pystyle.Colors.white_to_red, interval=0.005)
                urls = [
                    f"https://www.instagram.com/{nick}",
                    f"https://www.tiktok.com/@{nick}",
                    f"https://twitter.com/{nick}",
                    f"https://www.facebook.com/{nick}",
                    f"https://www.youtube.com/@{nick}",
                    f"https://t.me/{nick}",
                    f"https://www.roblox.com/user.aspx?username={nick}",
                    f"https://www.twitch.tv/{nick}",
                ]
                for url in urls:
                    try:
                        response = requests.get(url)
                        if response.status_code == 200:
                            pystyle.Write.Print(f"\n{url} - Not Found", pystyle.Colors.white_to_red, interval=0.005)
                        elif response.status_code == 404:
                            pystyle.Write.Print(f"\n{url} - Not Found", pystyle.Colors.white_to_red, interval=0.005)
                        else:
                            pystyle.Write.Print(f"\n{url} - Error {response.status_code}", pystyle.Colors.white_to_red, interval=0.005)
                    except:
                        pystyle.Write.Print(f"\n{url} - Error", pystyle.Colors.white_to_red, interval=0.005)
                print()
            if choice == "4":
                ip = pystyle.Write.Input("\n[?] Insert IP -> ", pystyle.Colors.white_to_red, interval = 0.005)
                def ip_lookup(ip):
                    url = f"http://ip-api.com/json/{ip}"
                    try:
                        response = requests.get(url)
                        data = response.json()
                        if data.get("status") == "fail":
                            pystyle.Write.Print(f"[!] Error Found: {data['message']}\n", pystyle.Colors.white_to_red, interval=0.005)
                        info = ""
                        for key, value in data.items():
                            info += f"[+] {key}: {value}\n"
                        return info
                    except Exception as e:
                        pystyle.Write.Print(f"[!] Error Found: {str(e)}\n", pystyle.Colors.white_to_red, interval=0.005)
                
                
                user_agents = [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
                    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)",
                    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)",
                ]
                def send_request(i):
                    user_agent = random.choice(user_agents)
                    headers = {"User-Agent": user_agent}
                    try:
                        response = requests.get(url, headers=headers)
                        print(f"{colorama.Fore.white_to_red}[+] Request {i} sent successfully\n")
                    except:
                        print(f"{colorama.Fore.white_to_red}[+] Request {i} sent successfully\n")
                threads = []
                for i in range(1, num_requests + 1):
                    t = threading.Thread(target=send_request, args=[i])
                    t.start()
                    threads.append(t)
                for t in threads:
                    t.join()
            
            if choice == "9":
                def get_characters(complexity):
                    characters = string.ascii_letters + string.digits
                    if complexity == "medium":
                        characters += "!@#$%^&*()"
                    elif complexity == "high":
                        characters += string.punctuation
                    return characters
                def generate_password(length, complexity):
                    characters = get_characters(complexity)
                    password = "".join(random.choice(characters) for i in range(length))
                    return password
                password_length = int(
                    pystyle.Write.Input("[?] Insert The Password -> ", pystyle.Colors.white_to_red, interval=0.005)
                )
                complexity = pystyle.Write.Input(
                    "[?] Select The  Difficulty (low, medium, high): ", pystyle.Colors.white_to_red, interval=0.005)
                print()
                complex_password = generate_password(password_length, complexity)
                pystyle.Write.Print("[+] Password -> "+ complex_password + "\n", pystyle.Colors.white_to_red, interval=0.005)
            
            if choice == "14":
                fake = faker.Faker(locale="ru_RU")
                gender = pystyle.Write.Input("\n[?] Select (М - Male, F - Female): ", pystyle.Colors.white_to_red, interval=0.005)
                print()
                if gender not in ["М", "F"]:
                    gender = random.choice(["М", "F"])
                    pystyle.Write.Print(f"[!] See the story, see the story: {gender}\n\n", pystyle.Colors.white_to_red, interval=0.005)
                if gender == "М":
                    first_name = fake.first_name_male()
                    middle_name = fake.middle_name_male()
                else:
                    first_name = fake.first_name_female()
                    middle_name = fake.middle_name_female()
                last_name = fake.last_name()
                full_name = f"{last_name} {first_name} {middle_name}"
                birthdate = fake.date_of_birth()
                age = fake.random_int(min=18, max=80)
                street_address = fake.street_address()
                city = fake.city()
                region = fake.region()
                postcode = fake.postcode()
                address = f"{street_address}, {city}, {region} {postcode}"
                email = fake.email()
                phone_number = fake.phone_number()
                inn = str(fake.random_number(digits=12, fix_len=True))
                snils = str(fake.random_number(digits=11, fix_len=True))
                passport_num = str(fake.random_number(digits=10, fix_len=True))
                passport_series = fake.random_int(min=1000, max=9999)
                pystyle.Write.Print(f"[+] Name, Surname: {full_name}\n", pystyle.Colors.white_to_red, interval=0.005)
                pystyle.Write.Print(f"[+] Gender: {gender}\n", pystyle.Colors.white_to_red, interval=0.005)
                pystyle.Write.Print(f"[+] Date of birth: {birthdate.strftime('%d %B %Y')}\n", pystyle.Colors.white_to_red, interval=0.005)
                pystyle.Write.Print(f"[+] age: {age} лет\n", pystyle.Colors.white_to_red, interval=0.005)
                pystyle.Write.Print(f"[+] Address: {address}\n", pystyle.Colors.white_to_red, interval=0.005)
                pystyle.Write.Print(f"[+] Email: {email}\n", pystyle.Colors.white_to_red, interval=0.005)
                pystyle.Write.Print(f"[+] Phone Number: {phone_number}\n", pystyle.Colors.white_to_red, interval=0.005)
                pystyle.Write.Print(f"[+] passport series: {passport_series} Number: {passport_num}\n", pystyle.Colors.white_to_red, interval=0.005)
            
            if choice == "18":
                def mac_lookup(mac_address):
                    api_url = f"https://api.macvendors.com/{mac_address}"
                    try:
                        response = requests.get(api_url)
                        if response.status_code == 200:
                            return response.text.strip()
                        else:
                            return f"Error: {response.status_code} - {response.text}"
                    except Exception as e:
                        return f"Error: {str(e)}"
                mac_address = pystyle.Write.Input("[?] Insert Mac-Address -> ", pystyle.Colors.white_to_red, interval = 0.005)  # Replace this with the MAC address you want to lookup
                vendor = mac_lookup(mac_address)
                pystyle.Write.Print(f"Vendor: {vendor}", pystyle.Colors.white_to_red, interval=0.005)
            if choice == "20":
                num_agents = pystyle.Write.Input("\n[?] Enter the number in User-agent -> ", pystyle.Colors.white_to_red, interval = 0.005)
                def generate_user_agents(num_agents):
                    versions = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{0}.0) Gecko/{0}{1:02d} Firefox/{0}.0",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:{0}.0) Gecko/{0}{1:02d} Firefox/{0}.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.{0}; rv:{1}.0) Gecko/20{2:02d}{3:02d} Firefox/{1}.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:{0}.0) Gecko/{0}{1:02d} Firefox/{0}.0",
                    ]
                    for _ in range(num_agents):
                        version = random.randint(60, 90)
                        year = random.randint(10, 21)
                        month = random.randint(1, 12)
                        
                        user_agent = random.choice(versions).format(version, year, year, month)
                        pystyle.Write.Print("\n" + user_agent, pystyle.Colors.white_to_red, interval = 0.005)
                generate_user_agents(int(num_agents))
                print()
            
            Main()
    except Exception as e:
        print("[!] Error ->", e)