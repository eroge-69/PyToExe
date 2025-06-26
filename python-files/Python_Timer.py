#Created 25/6/2025
#Last updated 25/6/2025
#Made by Ayan Adhikari
#This is a simple timer
#This program tests a new calibration system 
#This is because the one I created in The Lost Journey game was tedious to set up for the user
#This also is practice for using f strings
#----------------------------------------------------------------------#
#Variables, functions and imports
#----------------------------------------------------------------------#
#Imports
import time
import sys
#----------------------------------------------------------------------#
#Variables
amount = 0 #For clear_2()
time_left = 0
x = 100 #This is for printing numbers for calibrating
calibrate = 0
default_calibration = 0
start = False
run = False
name = "Unknown"
#Loading bar variables
load_100 = ("""
  _____________________
 /████████████████████/
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾""")
load_95 = ("""
  _____________________
 /███████████████████ /
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾""")
load_90 = ("""
  _____________________
 /██████████████████  /
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾""")
load_85 = ("""
  _____________________
 /█████████████████   /
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾""")
load_80 = ("""
  _____________________
 /████████████████    /
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾""")
load_75 = ("""
  _____________________
 /███████████████     /
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾""")
load_70 = ("""
  _____________________
 /██████████████      /
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾""")
load_65 = ("""
  _____________________
 /█████████████       /
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾""")
load_60 = ("""
  _____________________
 /████████████        /
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾""")
load_55 = ("""
  _____________________
 /███████████         /
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾""")
load_50 = ("""
  _____________________
 /██████████          /
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾""")
load_45 = ("""
  _____________________
 /█████████           /
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾""")
load_40 = ("""
  _____________________
 /████████            /
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾""")
load_35 = ("""
  _____________________
 /███████             /
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾""")
load_30 = ("""
  _____________________
 /██████              /
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾""")
load_25 = ("""
  _____________________
 /█████               /
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾""")
load_20 = ("""
  _____________________
 /████                /
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾""")
load_15 = ("""
  _____________________
 /███                 /
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾""")
load_10 = ("""
  _____________________
 /██                  /
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾""")
load_5 = ("""
  _____________________
 /█                   /
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾""")
load_0 = ("""
  _____________________
 /                    /
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾""")
#----------------------------------------------------------------------#
#Functions
def clear():
  for i in range (0, 100):
    print(f"")
def clear_2():
  amount = calibrate
  while amount > 0:
    print(f"")
    amount -= 1
def nex():
  input (f"Press enter to continue.")
def enter_number():
  clear()
  print (f"Please enter a number.")
  calibrate = default_calibration - 1
  clear_2()
  nex()
#----------------------------------------------------------------------#
#Basic intro
print(f"Welcome to the timer.")
name = input(f"What is your name? ")
print (f"Hello {name}, first you will need to calibrate the timer to fit your device.")
nex()
clear()
while run == False:
  clear()
  while x > 0:
    print(f"{x}.")
    x -= 1
  try:
    answer = int(input(f"What is the highest number you can see? (Not counting numbers you can partially see) "))
  except:
    enter_number()
    continue
  default_calibration = answer
  clear()
  print (f"Your calibration number is {default_calibration}.")
  print (f"If this is wrong then stuff will show up incorrectly.")
  calibrate = default_calibration - 2
  clear_2()
  nex()
  clear()
  print(f"Is this at the top of your screen? (y/n)")
  calibrate = default_calibration - 1
  clear_2()
  answer = input (f"> ").strip().lower()
  if answer == "y":
    run = True
    break
  elif answer == "n":
    clear()
    print (f"You can recalibrate it to the correct calibration.")
    nex()
    x = 100
    continue
  else:
    clear()
    print(f"Invalid response.")
    nex()
#----------------------------------------------------------------------#
#Main loop
default_calibration //= 2
default_calibration += 2
clear()
print (f"From now on text will show up in the middle of your screen.")
print (f"Now that you have finished calibrating you can start the timer!")
calibrate = default_calibration - 2
clear_2()
nex()
clear()
print (f"Do you want a basic guide on how to use the timer {name}. (y/n)")
calibrate = default_calibration - 1
clear_2()
answer = input(f"> ").strip().lower()
if answer == "y":
  clear()
  print (f"To use the timer simply type the amount of hours, minutes and seconds you want to set the timer for.")
  print (f"If you want to redo one of them simply type n when asked for confirmation.")
  print(f"Make sure to only type numbers.")
else:
  pass
#Loading screen
clear()
print (f"{load_0}")
calibrate = default_calibration - 4
clear_2()
time.sleep(0.5)
clear()
print (f"{load_5}")
clear_2()
time.sleep(0.5)
clear()
print (f"{load_10}")
clear_2()
time.sleep(0.5)
clear()
print (f"{load_15}")
clear_2()
time.sleep(0.5)
clear()
print (f"{load_20}")
clear_2()
time.sleep(0.5)
clear()
print (f"{load_25}")
clear_2()
time.sleep(0.5)
clear()
print (f"{load_30}")
clear_2()
time.sleep(0.5)
clear()
print (f"{load_35}")
clear_2()
time.sleep(0.5)
clear()
print (f"{load_40}")
clear_2()
time.sleep(0.5)
clear()
print (f"{load_45}")
clear_2()
time.sleep(0.5)
clear()
print (f"{load_50}")
clear_2()
time.sleep(0.5)
clear()
print (f"{load_55}")
clear_2()
time.sleep(0.5)
clear()
print (f"{load_60}")
clear_2()
time.sleep(0.5)
clear()
print (f"{load_65}")
clear_2()
time.sleep(0.5)
clear()
print (f"{load_70}")
clear_2()
time.sleep(0.5)
clear()
print (f"{load_75}")
clear_2()
time.sleep(0.5)
clear()
print (f"{load_80}")
clear_2()
time.sleep(0.5)
clear()
print (f"{load_85}")
clear_2()
time.sleep(0.5)
clear()
print (f"{load_85}")
clear_2()
time.sleep(0.5)
clear()
print (f"{load_90}")
clear_2()
time.sleep(0.5)
clear()
print (f"{load_95}")
clear_2()
time.sleep(0.5)
clear()
print (f"{load_95}")
clear_2()
time.sleep(0.5)
clear()
print (f"{load_95}")
clear_2()
time.sleep(0.5)
clear()
print (f"{load_100}")
clear_2()
time.sleep(0.5)
clear()
print(f"Timer initiated successfully!")
calibrate = default_calibration - 1
clear_2()
time.sleep(0.5)
run = True
while run == True:
  while start ==False:
    clear()
    print (f"How long do you want to set the timer for {name}.")
    calibrate = default_calibration - 1
    clear_2()
    try:
      hours = int(input(f"Hours: "))
      minutes = int(input(f"Minutes: "))
      seconds = int(input(f"Seconds:"))
    except:
      enter_number
      continue
    clear()
    print (f"Timer set for {hours} hours, {minutes} minutes and {seconds} seconds.")
    print (f"Do you want to start the timer. (y/n)")
    calibrate = default_calibration - 2
    clear_2()
    answer = input(f"> ").lower().strip()
    if answer == "y":
      time_left = (hours*60*60) + (minutes*60) + (seconds) #Total time left in seconds
      start = True
    else:
      clear()
      print("You can now set the timer again.")
      calibrate = default_calibration - 1
      clear_2()
      nex()
  while time_left > 0:
    clear()
    print (f"{hours}:{minutes}:{seconds}")
    calibrate = default_calibration - 1
    clear_2()
    time.sleep(1)
    if seconds > 0:
      seconds -= 1
    elif minutes > 0:
      minutes -= 1
      seconds = 59
    elif hours > 0:
      hours -= 1
      minutes = 59
      seconds = 59
    time_left -= 1
  if time_left <= 0:
    clear()
    print(f"Time's up!")
    calibrate = default_calibration - 1
    clear_2()
    time.sleep(0.5)
    for i in range (1, 10):
      print("\a")
      time.sleep(0.5)
  clear()
  print(f"Do you want to set another timer? (y/n)")
  calibrate = default_calibration - 1
  clear_2()
  answer = input(f"> ").lower().strip()
  if answer == "y":
    pass
  elif answer == "n":
    sys.exit()
  
  