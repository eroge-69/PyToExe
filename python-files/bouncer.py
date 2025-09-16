import requests,os,sys,time,colorama
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

date = datetime.now()
colorama.init()
check_emails = []

headers = {"User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:86.0) Gecko/20100101 Firefox/86.0"}

fileOpen = "valid_emails"+ str(date) +".txt"
fileOpenIn = "invalid_emails"+ str(date) +".txt"
fileOpenCheck = "to_check_emails"+ str(date) +".txt"



class colors:
    CRED2 = "\033[91m"
    CBLUE2 = "\033[94m"
    ENDC = "\033[0m"
    OKGREEN = '\033[92m'


def intro():
    banner = ("""
                                    d8888b.    d8888b.
                                    88  `8D    88  `8D
                                    88   88    88oooY'
                                    88   88    88~~~b.
                                    88  .8D db 88   8D
                                    Y8888D' VP Y8888P'


                    .o88b.  .d88b.  d8888b. d8888b. d8888b. d8888b.
                    d8P  Y8 .8P  88. 88  `8D 88  `8D VP  `8D 88  `8D
                    8P      88  d'88 88oodD' 88oodD'   oooY' 88oobY'
                    8b      88 d' 88 88~~~   88~~~     ~~~b. 88`8b
                    Y8b  d8 `88  d8' 88      88      db   8D 88 `88.
                    `Y88P'  `Y88P'  88      88      Y8888P' 88    YD                                                                                                                         
                            Zero Bounce v1.0.1 By D.B Decoder
			 telegram  @webspammingss for more toolz
    """)

    for col in banner:
        print(colors.CRED2 + col, end="")
        sys.stdout.flush()
        time.sleep(0.0025)

def work(i):
    payload = {
        "em" : i,
        "ch" : "2m14racqo107o0p0725b",
        "hl" : "checkeremail.com",
        "frm" : "example@gmail.com"
    }

    time.sleep(5)    
    checkeremail = requests.post('https://checkeremail.com/checker-validation.php', headers=headers, data=payload)
    if "Address is valid" in str(checkeremail.content):
        print(colors.OKGREEN + "[+] " + colors.CBLUE2 + i + colors.OKGREEN + " :) Valid.", end="\n")
        with open(fileOpen, "a") as valid:
            valid.write(i+"\n")
    elif "The address can not receive mail" in str(checkeremail.content):
        print( colors.CRED2 + "[~] " + colors.CBLUE2 + i + colors.CRED2 + " :( Can't receive mail.", end="\n")
        with open(fileOpenIn, "a") as valid:
            valid.write(i+"\n")
    else:
        print( colors.CRED2 + "[~] " + colors.CBLUE2 + i + colors.CRED2 + " :( Can't verify.", end="\n")
        with open(fileOpenCheck, "a") as valid:
            valid.write(i+"\n")


intro()



print(colors.ENDC + "Choose between the two (1/2).")
print("")
print(colors.ENDC + "1. Just emails")
print(colors.ENDC + "2. Combo (Emails & password)")
print("")

choice = input(colors.ENDC + "Enter your choice : ")


if choice == "1":
    print("")
    opFile = input(colors.ENDC + "Enter your filename : ")
    print("")
    emails = [line.strip() for line in open(opFile)]

    for email in emails:
        if "@" in email:
            check_emails.append(email)

    pool = ThreadPoolExecutor(max_workers=40)


    for i in check_emails:
        future = pool.submit(work, i)

elif choice == "2":
    print("")
    opFile = input(colors.ENDC + "Enter your filename : ")
    print("")

    emails = [line.strip() for line in open(opFile)]

    for email in emails:
        get_part = email.split(":")
        for i in range(0,2):
            if "@" in get_part[i]:
                check_emails.append(get_part[i])
    
    pool = ThreadPoolExecutor(max_workers=60)

    for i in check_emails:
        future = pool.submit(work, i)
else:
    sys.exit()
    

