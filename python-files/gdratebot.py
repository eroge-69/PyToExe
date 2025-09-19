from requests import post
from threading import Thread
from random import randint, choices
from hashlib import sha1
from base64 import urlsafe_b64encode
from itertools import cycle
from time import sleep

from GDgetUserInfos import getUserIDs

possibleletters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

starRates = 0
threadslist = []

def randomdelay() :

    sleep(randint(1500, 2000) / 1000)

def getproxies() :

    try :
            
        with open("proxies.txt", "r") as proxies :

            return [line.strip() for line in proxies]
        
    except FileNotFoundError :

        print("Proxy file 'proxies.txt' not found!")

        return False

def getaccounts() :

        try :
                
            with open("accounts.txt", "r") as accountsfile :

                return [line.strip() for line in accountsfile]
            
        except FileNotFoundError :

            print("Account file 'accounts.txt' not found!")

            return False

def distributeproxies(proxies, threads, max) :

    proxygroups = list([] for _ in range(threads))

    for index, proxy in enumerate(proxies[:max]):
            
        proxygroups[index % threads].append(proxy)

    return proxygroups

def distributeaccounts(accounts, threads, max) :

    accountgroups = list([] for _ in range(threads))

    for index, account in enumerate(accounts[:max]):

        accountgroups[index % threads].append(account)

    return accountgroups

def generate_rs(n) :

    return ("").join(choices(possibleletters, k=n))

def generate_chk(values) :

    def xorcipher(string, key) :

        return "".join(chr(ord(x) ^ ord(y)) for (x, y) in zip(string, cycle(key)))
    
    values.append("ysg6pUrtjn0J")

    string = ("").join(map(str, values))

    hashed = sha1(string.encode()).hexdigest()
    xored = xorcipher(hashed, "58281")
    final = urlsafe_b64encode(xored.encode()).decode()

    return final

def likeThreadFunc(stars, levelID, threadgroups, accountgroups, thread, rates) :

    global starRates

    try :

        proxygroup = threadgroups[thread]
        accountgroup = accountgroups[thread]

        if proxies != False :

            for index, account in enumerate(accountgroup) :

                downloadurl = "https://www.boomlings.com/database/rateGJStars211.php"

                udid = "S15" + str(randint(100000, 100000000)) + str(randint(100000, 100000000)) + str(randint(100000, 100000000)) + str(randint(100000, 100000000))
                randomproxy = proxygroup[index]

                userdata = account.split(",")

                if len(userdata) == 4 :

                    username, password, accountID, playerID = account.split(",")

                elif len(userdata) == 2 :

                    username, password = account.split(",")
                    accountID, playerID = getUserIDs(username=username)

                else :

                    username = userdata[0]
                    password = userdata[1]
                    accountID, playerID = getUserIDs(username=username)

                gjp = sha1((password + "mI29fmAnxgTs").encode()).hexdigest()
                rs = generate_rs(n=10)

                chkvalues = [levelID, stars, rs, accountID, udid, playerID]

                proxy = {

                    "http" : randomproxy,
                    "https" : randomproxy,

                }

                headers = {

                    "User-Agent": "",

                }

                data = {
                    
                    "levelID": levelID,
                    "accountID": accountID,
                    "gjp2": gjp,
                    "rs": rs,
                    "stars": stars,
                    "udid": udid,
                    "uuid": playerID,
                    "chk": generate_chk(values=chkvalues),
                    "secret": "Wmfd2893gb7",

                    }

                try :

                    if starRates >= rates :

                        return

                    raterequest = post(
                        
                        url=downloadurl,
                        data=data,
                        headers=headers,
                        proxies=proxy,
                    
                    )

                    if raterequest.text == "1" :
                        
                        starRates += 1

                        print(f"Sent star rate, Current star rates : {starRates}")
                            
                    if starRates >= rates :

                        return

                except Exception as Error :

                    print(f"There was an Error : {Error}")

    except Exception as Error :

        print(f"There was an Error : {Error}")

if __name__ == "__main__" :

    try :

        while True :

            command = input("Press '0' to exit or '1' to start : ")

            if command == "0" :

                break

            elif command == "1" :

                while True :

                    levelID = input("what is the LevelID : ")

                    try :

                        int(levelID)
                        break

                    except ValueError :
                        
                        print("Invalid levelID")

                proxies = getproxies()
                accounts = getaccounts()

                maxlen = min(len(proxies),len(accounts))

                if proxies != False and accounts != False :

                    while True :

                        stars = input(f"How many stars (1-10 stars!) : ")

                        try :

                            int(stars)

                            if int(stars) > 10 or int(stars) < 1 :

                                print("invalid stars!")

                            else :

                                break

                        except ValueError :

                            print("Invalid value")

                    while True :

                        rates = input(f"How many rates (max {maxlen} for this item!) : ")

                        try :

                            int(rates)

                            if int(rates) > maxlen :

                                print("desired rates are greater than the max amount!")

                            elif int(rates) < 1 :

                                print("too little desired rates!")

                            else :

                                break

                        except ValueError :

                            print("Invalid value")

                    while True :

                        threads = input(f"How many Threads (max : {maxlen}) : ")

                        try :

                            int(threads)

                            if int(threads) < 1 or int(threads) > maxlen :

                                print("Invalid thread amount")

                            else :

                                break

                        except Exception :

                            print("Invalid input")
                    
                    stars = int(stars)
                    rates = int(rates)
                    proxiegroups = distributeproxies(proxies=proxies, threads=int(threads), max=rates)
                    accountgroups = distributeaccounts(accounts=accounts, threads=int(threads), max=rates)

                    for index in range(int(threads)) :
                        
                        thread = Thread(target=likeThreadFunc, args=(stars,levelID,proxiegroups,accountgroups,index,rates))
                        threadslist.append(thread)

                    for thread in threadslist :

                        thread.start()

                    for thread in threadslist :

                        thread.join()

                    threadslist.clear()
                    starRates = 0 
                
                else :

                    print("Proxies unavailable!")

            else :

                print("Invalid input")
    
    except Exception as Error :

        print(f"there was an Error : {Error}")