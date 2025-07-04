import math
import time

def get_nth_decimal_digit(x, n):
    x = abs(x)
    shift = int(x * 10**n)
    return shift % 10

with open(r"godtongue2assets\godtongue.txt", "r", encoding="utf-8") as f:
    godtongueprime = f.read().splitlines()
with open(r"godtongue2assets\CustomWords.txt", "r", encoding="utf-8") as g:
    customprime = g.read().splitlines()
keeprandomseed = 0
godtongue = godtongueprime
custom = customprime
glossary = godtongue + custom
Responselength = 1
running = 1
print("Type /commands for a list of commands.")
while (running == 1):
    starttime = time.time()
    userinput = input("--: ")
    endtime = time.time()
    timedifference = (endtime - starttime)
    randomdecimal = timedifference - int(timedifference)
    messagefromgod = []

    if (userinput == "/commands"):
        print("-------------Commands-------------")
        print("/commands prints list of commands")
        print("/randomseed to see current randomseed")
        print("/toggleRandomSeed to toggle using current randomseed. By default, a new randomseed is generated with every input")
        print("/setResponseLength to set the current response length, by default 1. Max 500.")
        print("type nothing (i.e just enter) to generate response from god")
        print("/glossaries to change glossarries in use")
        print("/quit to quit")
        print("----------------------------------")
    if (userinput == "/randomseed"):
        print(randomdecimal)
    if ((userinput == "/toggleRandomSeed") or (userinput == "/togglerandomseed")):
        keeprandomseed += 1
    if ((userinput == "/setResponseLength") or (userinput == "/setresponselength")):
        print("Give new response length, must be either integer or R for random")
        ResponselengthInput = input("--: ")
        if ResponselengthInput == "R":
            Responselength = int(get_nth_decimal_digit(randomdecimal,1))
        else:
            Responselength = int(ResponselengthInput) % 500

    if (userinput == ""):
        wordcount = 0
        while wordcount != Responselength:
            fourdigits = randomdecimal * 1000
            currentword = glossary[int(fourdigits) % len(glossary)]
            messagefromgod.append(currentword)
            wordcount +=1
            randomdecimal = randomdecimal * math.sqrt(2)
            if randomdecimal > 1000:
                randomdecimal = randomdecimal - math.pi * 300
        a=0
        b=0
        wordofmessagecount = 0
        while b<= len(messagefromgod):
            b = a + (int(get_nth_decimal_digit(randomdecimal, wordofmessagecount)) % 7)
            wordofmessagecount += 1
            line1 = messagefromgod[a:b]
            a = b
            message = (" ".join(line1))
            print(message)

    if (userinput == "/glossaries"):
        print("Type /custom to toggle the custom wordlist, type /godtongue to toggle the godtongue wordlist")
        userinput2 = input("--: ")
        if (userinput2 == "/godtongue" and godtongueprime == godtongue):
            godtongue = []
        if (userinput2 == "/custom" and customprime == custom):
            custom = []
        if (userinput2 == "/godtongue" and godtongueprime != godtongue):
            godtongue = godtongueprime
        if (userinput2 == "/custom" and customprime != custom):
            custom = customprime

    if (userinput == "/quit"):
        quit()


