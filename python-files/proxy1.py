import socket
import threading
import webbrowser
from tkinter import Tk, Label, Entry, Button, messagebox, Frame

class ProxyServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f"Proxy server running on {self.host}:{self.port}")

    def handle_client(self, client_socket):
        request = client_socket.recv(1024)
        print(f"Received: {request}")
        # Forward the request to the Lifeboat server
        lifeboat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lifeboat_socket.connect(('play.lbsg.net', 19132))
        lifeboat_socket.send(request)
        response = lifeboat_socket.recv(4096)
        client_socket.send(response)
        client_socket.close()
        lifeboat_socket.close()

    def start(self):
        while True:
            client_socket, addr = self.server.accept()
            print(f"Accepted connection from {addr}")
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

class ProxyUI:
    def __init__(self, master):
        self.master = master
        master.title("Lifeboat Proxy")
        master.geometry("300x200")

        self.frame = Frame(master)
        self.frame.pack(pady=10)

        self.label = Label(self.frame, text="Enter IP and Port:")
        self.label.pack()

        self.ip_entry = Entry(self.frame)
        self.ip_entry.pack()
        self.ip_entry.insert(0, "127.0.0.1")

        self.port_entry = Entry(self.frame)
        self.port_entry.pack()
        self.port_entry.insert(0, "8080")

        self.start_button = Button(self.frame, text="Start Proxy", command=self.start_proxy)
        self.start_button.pack(pady=5)

        self.signup_button = Button(self.frame, text="Sign Up", command=self.open_signup)
        self.signup_button.pack(pady=5)

    def start_proxy(self):
        ip = self.ip_entry.get()
        port = int(self.port_entry.get())
        proxy_server = ProxyServer(ip, port)
        threading.Thread(target=proxy_server.start, daemon=True).start()
        messagebox.showinfo("Info", f"Proxy started on {ip}:{port}")

    def open_signup(self):
        webbrowser.open("https://login.live.com/oauth20_authorize.srf?redirect_uri=https%3a%2f%2afsisu.xboxlive.com%2fconnect%2foauth%2fXboxLive&response_type=code&state=LAAAAAEB3BtSGYjpUHOF_qiv_yxZpxItXQLaVouNfbYBfPlHmXRidPpeAW3WOjc2Mzk2MjI0YmJmZDQ0ZjBhYzFjMGRiNDEyNWFiNThhMSBpWk5oRmp1RkZFK3pGU1JVM2FITWJRLjABAQ&client_id=7d5c843b-fe26-45f7-9073-b683b2ac7ec3&scope=XboxLive.Signin%20+XboxLive.offline_access&lw=1&fl=dob,easi2&xsup=1&uaid=de11c9d3a04948c1abdca61d82e0c9de&cobrandid=8058f65d-ce06-4c30-9559-473c9275a65d&nopa=2")

if __name__ == "__main__":
    root = Tk()
    proxy_ui = ProxyUI(root)
    root.mainloop()
