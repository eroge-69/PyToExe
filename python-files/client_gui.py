
import socket, pickle, zlib
from PyQt5 import QtWidgets, QtGui, QtCore
import sys
from pynput import mouse, keyboard

class ClientGUI(QtWidgets.QWidget):
    def __init__(self, session_id):
        super().__init__()
        self.setWindowTitle(f"Remote Desktop Client - Connect: {session_id}")
        self.setGeometry(100,100,1280,720)
        self.layout=QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.label=QtWidgets.QLabel(self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.label)
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        host,port=session_id.split(":")
        self.sock.connect((host,int(port)))
        self.mouse_listener=mouse.Listener(on_click=self.on_click,on_move=self.on_move)
        self.keyboard_listener=keyboard.Listener(on_press=self.on_press)
        self.mouse_listener.start()
        self.keyboard_listener.start()
        self.last_mouse=(0,0)
        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)

    def send_input(self,event):
        try:
            data=pickle.dumps(event)
            self.sock.sendall(len(data).to_bytes(8,'big'))
            self.sock.sendall(data)
        except: pass

    def on_move(self,x,y): self.last_mouse=(x,y)
    def on_click(self,x,y,button,pressed):
        if pressed:
            self.send_input({'type':'mouse','position':(x,y),'button':'left'})
    def on_press(self,key):
        try:event={'type':'keyboard','key':key.char}
        except AttributeError:event={'type':'keyboard','key':str(key)}
        self.send_input(event)

    def update_frame(self):
        try:
            length_data=self.sock.recv(8)
            if not length_data:return
            length=int.from_bytes(length_data,'big')
            data=b''
            while len(data)<length:
                data+=self.sock.recv(length-len(data))
            img=pickle.loads(zlib.decompress(data))
            image=QtGui.QImage(img,1920,1080,QtGui.QImage.Format_RGB888)
            pix=QtGui.QPixmap.fromImage(image).scaled(self.label.width(),self.label.height())
            self.label.setPixmap(pix)
        except: pass

if __name__=="__main__":
    session_id, ok=QtWidgets.QInputDialog.getText(None,"Session ID","Masukkan Session ID:")
    if ok and session_id:
        app=QtWidgets.QApplication(sys.argv)
        window=ClientGUI(session_id)
        window.show()
        sys.exit(app.exec_())
