#!/usr/bin/env python
import time
print("The EFS terminal requires an auth key. please enter your auth key... (tester key is 'tester')") #i call it 'mash' (Mock-Bash) yeah im pretty clever <-- gonna kms
key = input("")
burst = ("undef")
cd = (1)
login = 1
while login == 1:
    if key == "FAJIMAD":
        print("Login completed welcome usr UHLPRO")
        login = 2
    elif key == "FREEDOMWAR":
        print("Login completed welcome usr SAMMY")
        login = 2
    elif key == "tester":
        print("Login completed welcome usr TESTER")
        login = 2
    else:
        print("Key invalid try again")
        key = input("")

while burst !="fell":
    print("Please enter a command or type 'help' for a list of commands")
    burst = input("")
    burst = burst.lower()
    if burst == "help":
        print("Current commands are 'ls' 'cat' 'vpncon'(running in restricted mode)")
        continue
    if burst == "vpncon":
        print("You are connected to EFS vpn tunnel at 10.1.10.244")
        continue
    if burst == "ls":
        print("juror.txt README.TXT")
        continue
    if burst == "cat":
        print("cat requires an argument in the form of a file i.e 'cat <filename>' if you entered a file name and it returned this then make sure you spelt it right")
        continue
    if burst == "cat juror.txt":
        print("there was nothing leFt for thEm at this point. alL they couLd do")
        continue
    if burst == "fell":
        print("Burst protocol engaged, authorities have been notified.")
        continue
    if burst == "cat readme.txt":
        print("Welcome to the EFS terminal! this is used to view or modify files that are on the same server as the user. if the terminal is running in restricted mode then you will only be able to read files not write.")
        continue
    else:
        print("no command recongnized")
        continue
print("vpn tunnel change confirmed")
while burst !="yes":
    print("Please enter a command or type 'help' for a list of commands")
    burst = input("")
    burst = burst.lower()
    if burst == "help":
        print("Current commands are 'ls' 'cat' 'vpncon' 'cd'")
        continue
    if burst == "vpncon":
        print("You are connected to EFS vpn tunnel at 10.1.10.252")
        continue
    if burst == "ls":
         if cd == 1:
             print("burst juror.txt README.TXT")
             continue
         elif cd == 2:
             print (".. burst.txt")
             continue
    if burst == "cat":
        print("cat requires an argument in the form of a file i.e 'cat <filename>'")
        continue
    if burst == "cat juror.txt":
        print("there was nothing leFt for thEm at this point. alL they couLd do")
        continue
    if burst == "cat readme.txt":
        print("Welcome to the EFS terminal! this is used to view or modify files that are on the same server as the user. if the terminal is running in restricted mode then you will only be able to read files not write.")
        continue
    if burst == "cd":
        print("cd requires an argument in the form of a directory i.e 'cd <directoryname> directories do not have a file exentension")
        continue
    if burst == "cd burst":
        print("Changed current directory to 'burst'")
        cd = 2
        continue
    if burst == "cd ..":
        cd = 1
        print("changed current directory to 'showdonttell'")
        continue
    if burst == "cat burst.txt":
        if cd == 1:
            print("file not found in current directory but was found in 'burst' directory change directory and run again")
            continue
        if cd == 2:
            print("696620796F75206B656570206D6F76696E6720666F727761726420796F75206D69676874207769736820796F75206469646E742E2061736B20796F757273656C663A2061726520796F7520737572653F")
            continue
    else:
        print("no command recongnized")
print("break the veil. follow my trail - raven")
