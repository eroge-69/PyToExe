import html

import requests
import random
import time
import re
from bs4 import BeautifulSoup

def randomRangeNum():
    return random.randint(1,3)
import numpy as np
def vote():
    response = session.get(
        'https://www.ceskatelevize.cz/porady/1181680258-tyden-v-regionech-brno/13650-soutez-ireporteru/?pollVote=20077',
        headers=headers, allow_redirects=False)
    randomTime = random.randint(5, 45)
    print("davam hlas, cekam " + str(randomTime) + "sekund")
    time.sleep(randomTime)

def getSecondBiggest(arr):
    arr = np.array(arr, dtype=int)
    if len(arr) < 2:
        return None
    sorted_arr = np.sort(arr)  # seřadí vzestupně, duplicity zůstanou
    return sorted_arr[-2]      # druhé největší


i = 1
while i < 10:
    session = requests.Session()


    randomNum = random.randint(500, 600)
    randomNum2 = random.randint(4, 5)
    randomNum3 = random.randint(14, 17)
    randomNum4 = random.randint(140, 147)
    randomNum5 = random.randint(3200, 4300)
    randomNum6 = random.randint(60, 92)

    user_agent_list = [
        'Mozilla/'+str(randomNum2)+'.0 (iPad; CPU OS 12_1 like Mac OS X) AppleWebKit/'+str(randomNum)+'.1.'+str(randomNum3)+' (KHTML, like Gecko) Mobile/15E'+str(randomNum4+4),
        'Mozilla/'+str(randomNum2)+'.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'+str(randomNum)+'.36 (KHTML, like Gecko) Chrome/93.0.'+str(randomNum5+2)+'.82 Safari/'+str(randomNum+2)+'.36',
        'Mozilla/'+str(randomNum2)+'.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/'+str(randomNum)+'.1.'+str(randomNum3)+' (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
        'Mozilla/'+str(randomNum2)+'.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'+str(randomNum)+'.36 (KHTML, like Gecko) Chrome/'+str(randomNum6)+'.0.'+str(randomNum5)+'.141 Safari/'+str(randomNum)+'.36 Edg/87.0.'+str(randomNum+1)+'.75',
        'Mozilla/'+str(randomNum2)+'.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'+str(randomNum)+'.36 (KHTML, like Gecko) Chrome/'+str(randomNum6)+'.0.'+str(randomNum5)+'.102 Safari/'+str(randomNum)+'.36 Edge/18.18363',
    ]

    useragent = user_agent_list[random.randint(0, len(user_agent_list) - 1)]
    headers = {"User-Agent": useragent}

    response2 = session.get(
        'https://www.ceskatelevize.cz/porady/1181680258-tyden-v-regionech-brno/13650-soutez-ireporteru/',
        headers=headers, allow_redirects=False)

    content = response2.content.decode("utf-8")
    soup = BeautifulSoup(content,"html.parser")
    text = html.unescape(soup.get_text())

    linesVotes = [
    line.strip()
    for line in text.splitlines()
    if " hl." in line
]
    listVotes = []
    for line in linesVotes:
        match = re.search(r'\d+', line)

        if match:
            number = int(match.group())
            listVotes.append(number)
        else:
            print("Žádné číslo nenalezeno")

    #JAKY JE NASE
    ourID = 1

    highestNum = 0
    for num in listVotes:
        if(highestNum<num):
            highestNum = num
    randomn = randomRangeNum()
    secondBiggest = getSecondBiggest(listVotes)
    if(highestNum != listVotes[ourID]):
        vote()
    elif(listVotes[ourID]<secondBiggest+randomn):
        print(f"davam vote, secondbiggest ={secondBiggest} a randomn = {randomn}")
        vote()



    print("mame "+str(listVotes[ourID])+"hlasu.")
    listVotes.remove(listVotes[ourID])
    stringList = str(listVotes)
    print("ostatni maji"+stringList)
    time.sleep(10)