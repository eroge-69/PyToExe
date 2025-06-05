import socket


host = socket.gethostname()
local_ip = socket.gethostbyname(host)

while True:
    try:
#UDP
        UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #create UDP socket
        UDP_socket.bind (('localhost', 16969)) #Lua script in FlyWithLua broadcast NMEA

#TCP
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create TCP socket
        server_socket.bind(('', 10110)) 
        server_socket.listen(1)
        print(f"You IP address: {local_ip}:10110")
        print("wait for connection")
        client_socket, client_address = server_socket.accept() #Accept TCP
        print(f"connection has been established with {client_address}")

        while True:
            conn, addr = UDP_socket.recvfrom(10245)     #recvfrom - reveive message to UDP (message, from whom)
            print(f"NMEA {conn}")
            client_socket.sendall(conn) #sendall - send message to TCP
    except:
        continue