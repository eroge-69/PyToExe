import time
import winsound
print("Welcome to the python stopwatch!")
time.sleep(0.25)
print("Please enter a timer (in seconds) that you want to start from (zero is very popular).")
time.sleep(0.25)
TimerAmount = input()
if TimerAmount.isdigit():
    TimerAmount = int(TimerAmount)
    print("Would you like to set a stopwatch starting from" , TimerAmount , "seconds?")
    ans = input().upper()
    if ans == "YES" or "Y" or "Ye":
        print("Brilliant! I'll start the stopwatch.")
        while TimerAmount > -11111111111111111111111111111111111111:
            TimerAmount += 1
            print (TimerAmount)
            time.sleep(1)
    else:
        print("Okay then. See you soon.")
    
else:
    print("I don't know what you've put in, but that's not a number. Try again.")
