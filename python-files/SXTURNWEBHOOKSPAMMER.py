import string, json, requests, random
from pystyle import Colorate, Colors, Center
from os import system
from time import sleep

system('cls')
boucle1 = True
boucle2 = True
failed_previous = False

sent_count = 0

def random_number(digits):
    range_start = 10**(digits-1)
    range_end = (10**digits)-1
    return random.randint(range_start, range_end)

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def send_message(webhook_url):
    username = id_generator(80)
    message = "@everyone qq by insomnia ;3 made with love and vulgarity"
    data = json.dumps({
        "content": message,
        "username": username,
        "tts": False
    })

    header = {
        "content-type": "application/json"
    }

    response = requests.post(webhook_url, data, headers=header)

    if not response.ok:
        if response.status_code == 429:
            system('cls')
            print(Colorate.Horizontal(Colors.black_to_red, Center.XCenter(header_final)))
            print(Colorate.Horizontal(Colors.black_to_red, "[/] ..."))
            sleep(2)
        else:
            system('cls')
            print(Colorate.Horizontal(Colors.black_to_red, Center.XCenter(header_final)))
            print(Colorate.Horizontal(Colors.black_to_red, "[!] Failed to send message !"))
            sleep(15)
    try:
        system('cls')
        print(Colorate.Horizontal(Colors.blue_to_green, Center.XCenter(header_final)))
        print(Colorate.Horizontal(Colors.blue_to_green, f"[+] Message sended ! [ {sent_count} ]"))
    except:
        system('cls')
        print(Colorate.Horizontal(Colors.black_to_red, Center.XCenter(header_final)))
        print(Colorate.Horizontal(Colors.black_to_red, "[!] Failed to send message !"))
        sleep(15)
    return True

header_final = """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠴⠒⠋⠉⠉⠉⠉⠉⠙⠒⠦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠊⠁⠀⠀⠀⣀⣀⣠⠤⠤⠤⠤⠤⣄⠙⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡥⠴⠒⠊⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧⠀⢳⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡟⠀⡀⠀⠀⠀⠀⠀⠀⢀⣠⣶⣿⣷⣤⣀⠈⡆⠘⡆⠀⠀⠀⠀⠀⠀⠀𝑴𝑨𝑫𝑬 𝑩𝒀 𝑺𝑿𝑻𝑼𝑹𝑵⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢷⣸⣿⣿⣶⣤⡀⠀⣴⣿⡟⢉⠀⠀⠀⠉⠀⢸⡀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠁⠀⢀⣩⡛⢿⠉⡍⠛⣷⣾⣿⣷⢤⠴⠷⢄⣇⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡧⢰⣿⣿⣿⠇⠀⣷⠀⠉⠉⠉⠉⠀⠀⠀⠸⢿⠥⢿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⢀⠀⢹⣦⡼⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢧⠀⠀⢀⡀⢠⡀⢛⣁⣬⠆⠉⠉⣱⡿⡍⠀⢸⠛⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣇⢺⣧⣀⣈⣿⣿⣿⣷⣤⣴⣶⡿⣻⠁⠀⣼⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⡎⢿⠛⠛⠛⣿⣾⣏⣩⠍⠀⡸⠃⠀⣰⡧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢮⡳⡌⠉⠻⣿⡿⠀⠀⠼⠁⢠⠞⡟⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⢄⠀⠀⣿⣿⠀⠀⢀⡜⠁⠚⠀⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡞⠈⠻⣗⠦⠽⠿⠤⠞⠁⠀⠀⠀⠀⣿⢷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⠞⠁⣇⠀⠀⠈⠳⢄⡀⠀⠀⠀⠀⠀⠀⢀⡟⢸⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢀⣀⡠⠤⠖⠒⠋⠉⡇⠀⠀⢹⡀⠀⠀⠀⠀⠙⠲⢤⡀⠀⢀⡴⠋⠀⢀⡇⠉⠲⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⣠⠤⠒⠋⠉⠀⠀⠀⠀⠀⠀⢰⣧⠀⠀⠈⣧⠀⠀⠀⠀⠀⠀⠀⡹⠓⠋⠲⡄⠀⠈⣧⠀⠀⠸⡍⠙⠲⠤⣄⣀⠀⠀⠀⠀⠀
⡞⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡿⠀⠀⠀⢻⡳⣄⠀⠀⠀⣠⠞⠀⠀⠀⠀⠘⣆⠀⣾⡄⠀⠀⠹⡄⠀⠀⠀⠈⠉⠒⢤⡀⠀
⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⡇⠀⠀⠀⠈⣇⠈⢣⡀⣰⢳⡀⠀⠀⠀⢀⡞⠉⠶⠁⢧⠀⠀⠀⢱⡀⠀⠀⠀⠀⠀⠀⢧⠀
⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣇⠀⠀⠀⠀⢸⡀⠀⠙⠇⠀⢹⠒⠒⠒⢯⠀⠀⠀⠀⢸⡀⠀⠀⢀⡇⠀⠀⠀⠀⠀⠀⠘⣆
⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠂⠀⠀⠸⠇⠀⠀⠀⠀⠟⠀⠀⠀⠈⠧⠀⠀⠀⠘⠇⠀⠀⠉⠀⠀⠀⠀⠀⠀⠀⠀⠻
⠀⠀⠀⠁⠁⠀⠁⠀⠀⠀⠀⠈⠀⠀⠀⠈⠉⠉⠋⠉⠉⠉⠉⠁⠉⠉⠀⠉⠈⠁⠉⠉⠛⠛⠋⠉⠉⠉⠉⠉⠉⠉⠉⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

\n\n\n\n"""

while boucle1:
    print(Colorate.Horizontal(Colors.yellow_to_red, Center.XCenter(header_final)))
    print(Colorate.Horizontal(Colors.yellow_to_red, "[-] Webhook URL ↓"))
    webhook_url = input("")
    if webhook_url.startswith("https://discord.com/api/webhooks/"):
        boucle1 = False
        system('cls')
    else:
        system('cls')
        print(Colorate.Horizontal(Colors.black_to_red, Center.XCenter(header_final)))
        print(Colorate.Horizontal(Colors.black_to_red, "[!] Error valid link !"))
        sleep(2)
        system('cls')

while boucle2:
    if (send_message(webhook_url)):
        sent_count += 1