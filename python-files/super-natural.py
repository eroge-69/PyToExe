import os,time
from datetime import datetime

desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')


while True:
    nowdate1=datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')
    os.mkdir(desktop_path+"//"+nowdate1)
    print (nowdate1)
    time.sleep(2)
    