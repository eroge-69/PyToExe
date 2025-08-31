import socket

sa = "10.0.0.171"
p = "5431" 

conn = socket.socket(socket.AP_INET, socket.SOCK_STREAM)

conn.connect((sa, p))
