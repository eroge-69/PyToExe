import socket
import os
import PySimpleGUI as sg
from datetime import datetime
 
path = 'C:/Pacs_message/'
 
def start():
    SRV_ADDR = str(values['-ip-']), int(values['-port-'])
    srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_sock.bind(SRV_ADDR)
    srv_sock.listen(10)
    sg.Popup('server is running')
    
    while True:
        connect, addr = srv_sock.accept()
        curdat = datetime.now()
        txt_file = open(path + curdat.strftime("%d%m%Y%H%M%S") + "_newmessage.txt", "a")
        txt_file.write(curdat.strftime("%d-%m-%Y %H:%M:%S") + " new connection from {address}".format(address=addr)+"\n")
        data = connect.recv(1024)
        txt_file.write(str(data)+"\n")
        connect.close()
        txt_file.close()
 
layout = [
    [sg.Text('IP   '), sg.In("192.168.25.110", key='-ip-', size=(14,1))
     ],
    [sg.Text('Port'), sg.In("6005", key='-port-', size=(5,1))
     ],
    [sg.SimpleButton('Старт', button_color=('white', 'green'), key='-run-')]
    ]
window = sg.Window('TCP Server', layout)
 
while True:
    event, values = window.read()
    if event in ('Exit', 'Cancel'):
        break
    if event == '-run-':
        start()
    
window.close()
