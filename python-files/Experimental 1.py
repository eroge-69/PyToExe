# detect changes in a website
# Importing libraries
import time
import hashlib
from urllib.request import urlopen, Request
import telebot

#telegram bot
bot = telebot.TeleBot("8099739290:AAHymLN0YleOfDEBhF_GC2BqeONRgXKoOfQ", parse_mode=None)

# setting the URL you want to monitor
url = Request('https://w9.villainsaredestinedtodie.com/',
              headers={'User-Agent': 'Mozilla/5.0'})

# to perform a GET request and load the
# content of the website and store it in a var
response = urlopen(url).read()

# to create the initial hash
currentHash = hashlib.sha224(response).hexdigest()
print("running")
time.sleep(2)
while True:
    try:
        # perform the get request and store it in a var
        response = urlopen(url).read()

        # create a hash
        currentHash = hashlib.sha224(response).hexdigest()

        # wait for 30 seconds
        time.sleep(3)

        # perform the get request
        response = urlopen(url).read()

        # create a new hash
        newHash = hashlib.sha224(response).hexdigest()

        # check if new hash is same as the previous hash
        if newHash == currentHash:
            continue

        # if something changed in the hashes
        else:
            # notify
            print("something changed")

            bot.send_message(6001384446, "🌐 Website updated! Hash changed!")

            # again read the website
            response = urlopen(url).read()

            # create a hash
            currentHash = hashlib.sha224(response).hexdigest()
            
            # wait for 30 seconds
            time.sleep(30)
            continue

    # To handle exceptions
    except Exception as e:
        print("error")

#send a ping to my phone 

