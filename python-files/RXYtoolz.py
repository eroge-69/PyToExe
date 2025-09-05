import requests
import os
import json

logo = """
\033[38;2;255;0;0m   ██████╗ ██╗  ██╗██╗   ██╗    ████████╗ ██████╗  ██████╗ ██╗     ███████╗
\033[38;2;255;128;0m ██╔══██╗╚██╗██╔╝╚██╗ ██╔╝    ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ╚══███╔╝
\033[38;2;255;255;0m ██████╔╝ ╚███╔╝  ╚████╔╝        ██║   ██║   ██║██║   ██║██║       ███╔╝ 
\033[38;2;128;255;0m ██╔══██╗ ██╔██╗   ╚██╔╝         ██║   ██║   ██║██║   ██║██║      ███╔╝  
\033[38;2;0;255;0m   ██║  ██║██╔╝ ██╗   ██║          ██║   ╚██████╔╝╚██████╔╝███████╗███████╗
\033[38;2;0;255;128m ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝          ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝ // by roxy
 

"""



while True:
    os.system("RXY Toolz")
    print("RXY Toolz")
    print(logo)
    print("[1] - IP Lookup")
    print("[2] - webhook sender")
    print("[3] - Playfab DLC Puller (soon)")
    print("[4] - Nitro Generator (soon)")
    print("[5] - Quit")
    print("")
    x = input("Option:")
    

    if x == "1":
        os.system('cls' if os.name == 'nt' else 'clear')
        ip = input("Enter IP:")
        url = f"http://ip-api.com/json/{ip}"
        response = requests.get(url)
        data = response.json()
        print(json.dumps(data, indent=4))
        input("Press Enter to continue...")
        os.system('cls' if os.name == 'nt' else 'clear')


    if x == "2":
        os.system('cls' if os.name == 'nt' else 'clear')
        webhook_url = input("Enter Webhook URL:")
        message = input("Enter Message:")
        data = {
            "content": message
        }
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            print("Message sent successfully.")
        else:
            print(f"Failed to send message. Status code: {response.status_code}")
        input("Press Enter to continue...")
        os.system('cls' if os.name == 'nt' else 'clear')

        if x == "3":
            print("Coming Soon!")
            input("Press Enter to continue...")

            if x == "4":
                os.system('cls' if os.name == 'nt' else 'clear')
                import random
                import string

                def generate_nitro_code():
                    part1 = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
                    part2 = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
                    part3 = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
                    return f"https://discord.gift/{part1}-{part2}-{part3}"

                try:
                    num_codes = int(input("How many Nitro codes to generate? "))
                    with open("nitro_codes.txt", "w") as file:
                        for _ in range(num_codes):
                            code = generate_nitro_code()
                            file.write(code + "\n")
                            print(code)
                    print(f"\n{num_codes} Nitro codes have been generated and saved to nitro_codes.txt")
                except ValueError:
                    print("Please enter a valid number.")
                input("Press Enter to continue...")
                os.system('cls' if os.name == 'nt' else 'clear')
  
    if x == "5":
        print("Goodbye!")
        break

       