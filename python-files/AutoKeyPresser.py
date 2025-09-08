from pynput.keyboard import Key, Controller
import time
try:
    keyboard = Controller()
    presskey = input("What Key to Spam Press???\n>")
    times = float(input("how many times to press?? If infinity type -1\n>"))
    delaytime = float(input("What delay Between Pressing Keys?(seconds)\n>"))
    input("press enter to continue")


    for count in range(3, 0, -1):
        print(count)
        time.sleep(1)


    if times == -1:
        while True:
            keyboard.press(presskey)
            keyboard.release(presskey)
            #keyboard.send(delaytime)
            time.sleep(delaytime)
    elif times >= 0:
        for number in range(times):
            keyboard.press(presskey)
            keyboard.release(presskey)
            #keyboard.send(presskey)
            time.sleep(delaytime)
except:
	print("A error occured")
