import subprocess
import datetime

with open("passwords.txt", "w", encoding="utf-8") as file:
    try:
        points = 0
        succpoints = 0
        profiles = subprocess.run(["netsh", "wlan", "show", "profiles"], stdout=-1)
        strprofiles = profiles.stdout.decode('cp866')
        for stroke in strprofiles.split("\n"):
            if len(stroke.split(":")) > 1 and stroke.split(":")[1] != "\r":
                ssid = stroke.split(":")[1].removeprefix(" ").removesuffix("\r")
                points += 1
                try:
                    password = subprocess.run(["netsh", "wlan", "show", "profiles", f'name={ssid}', "key=clear"], stdout=-1)
                    strpass = password.stdout.decode('cp866')
                    findpass = False
                    for strokepass in strpass.split("\n"):
                        if strokepass.find("Содержимое ключа") != -1:
                            realpass = strokepass.split(":")[1].removeprefix(' ').removesuffix('\r')
                            file.write(f"{ssid} = {realpass}\n")
                            succpoints += 1
                            findpass = True
                            print(f"Getting and writing password for '{ssid}'")
                    if findpass == False:
                        raise Exception(f"Dont found 'Содержимое ключа'")
                except Exception as exp:
                    print(f"Error when getting password for '{ssid}': {exp}")
        file.write(f"\nTime of parsing: {datetime.datetime.now()}")
        print(f"Parsing succesfully completed. Getting {succpoints}/{points} password at all ({round(succpoints/points*100, 2)}%)")
        input()
    except Exception as exp:
        print(f"Fatal Error: {exp}")
        input()
    finally:
        file.close()