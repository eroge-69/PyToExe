import keyboard
import bluetooth
import socket
import time



def scan():
    print("Сканирование bluetooth устройств")
    nearby_devices = bluetooth.discover_devices(lookup_names=True)
    print("Найденные устройства:")
    for addr, name in nearby_devices:
        print(f" {addr} - {name}")



def connect(MAC):
    try:
        print("Подклюяение к", MAC)
        serverMACAddress = MAC  # Put your HC-05 address here
        port = 1  # Match the setting on the HC-05 module
        s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        s.connect((serverMACAddress,port))
        print("Подключен к", MAC)
        while 1:
            text = input()
            if text == "close":
                print("Отключен")
                break
            if text =="control":
                print("Управление")
                
                ms_1 = "" # 000XMMMM XXXX-адрес сообщения MMMM-управление моторами
                ms_2 = "" # 001SSSSS
                ms_3 = "" # 010SSSSS
                while 1:
                    ms_1 = ""
                    if keyboard.is_pressed('w'):
                        ms_1+="1"
                    else:
                        ms_1+="0"
                    if keyboard.is_pressed('s'):
                        ms_1+="1"
                    else:
                        ms_1+="0"
                    if keyboard.is_pressed('a'):
                        ms_1+="1"
                    else:
                        ms_1+="0"
                    if keyboard.is_pressed('d'):
                        ms_1+="1"
                    else:
                        ms_1+="0"
                    ms_1="0000"+ms_1

                    if keyboard.is_pressed('r'):
                        ms_2+="1"
                    else:
                        ms_2+="0"
                    if keyboard.is_pressed('f'):
                        ms_2+="1"
                    else:
                        ms_2+="0"
                    if keyboard.is_pressed('t'):
                        ms_2+="1"
                    else:
                        ms_2+="0"
                    if keyboard.is_pressed('g'):
                        ms_2+="1"
                    else:
                        ms_2+="0"
                    if keyboard.is_pressed('y'):
                        ms_2+="1"
                    else:
                        ms_2+="0"
                    ms_2="001"+ms_2
                    
                    if keyboard.is_pressed('h'):
                        ms_3+="1"
                    else:
                        ms_3+="0"
                    if keyboard.is_pressed('u'):
                        ms_3+="1"
                    else:
                        ms_3+="0"
                    if keyboard.is_pressed('j'):
                        ms_3+="1"
                    else:
                        ms_3+="0"
                    if keyboard.is_pressed('i'):
                        ms_3+="1"
                    else:
                        ms_3+="0"
                    if keyboard.is_pressed('k'):
                        ms_3+="1"
                    else:
                        ms_3+="0"
                    ms_3="010"+ms_3

                    if keyboard.is_pressed('q'):
                        print("Выход из управления")
                        break    
                    
                    time.sleep(0.01)
                    #print(chr(int(up_c,2)))
                    s.send(bytes(chr(int(ms_1,2)), 'UTF-8'))
                    time.sleep(0.01)
                    s.send(bytes(chr(int(ms_2,2)), 'UTF-8'))
                    time.sleep(0.01)
                    s.send(bytes(chr(int(ms_3,2)), 'UTF-8'))
            #s.send(bytes(text, 'UTF-8'))
        s.close()
    except TimeoutError:
        print("Ошибка подключения к", MAC)
    except OSError:
        print("Ошибка подключения к", MAC)
    

while True:
    cmd = input()
    if cmd == "scan":
        scan()
    if cmd.split(" ")[0]=="connect":
        if cmd.split(" ")[0]!=cmd:
            connect(cmd.split(" ")[1])

