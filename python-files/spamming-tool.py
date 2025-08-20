#-----------------------
# SPAM message tool     
# Made by: Omar Ashraf 
#-----------------------
import time
# The message that will be repeated
message = input("What message would you like to be repeated? :)  ")
if len(message) == 0:
    print("Please enter a vaild message.")
# How many times should the computer spam the message
count = int(input("how many times would you like this message to be repeat? "))
if count == 1:
    print("I'm sorry, using this tool for this is useless.")
else:
    print("okay :)\n loading...\n this tool made by: Omar Ashraf")
    time.sleep(1)
    message = "{:s} ".format(message)
    print(message * count)
    time.sleep(1000)