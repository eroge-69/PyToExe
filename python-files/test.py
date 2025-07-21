#server.py
import socket

HOST = '192.168.1.100'
PORT = 8800

while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
      #hex_string_data = "48656C6C6F20486578"  #"Hello Hex" in hex
      #hex_string_data = "00f9ff"    #ON All
      #hex_string_data = "0009ff"    #OFF All
      
            byte_data = bytes(input("Enter command code : "),"utf-8")

            hex_string_data = byte_data.decode("utf-8")
      
            print("received data from the client:", hex_string_data)
            byte_data = bytes.fromhex(hex_string_data)
            conn.sendall(byte_data)
        print(f"Sent: {byte_data.hex()}")
 
