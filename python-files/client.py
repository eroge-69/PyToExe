import socket, cv2, pickle, struct

HOST = "127.0.0.1"   # change to server PC IP in LAN
PORT = 5000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

data = b""
payload_size = struct.calcsize("Q")

while True:
    while len(data) < payload_size:
        packet = client_socket.recv(4*1024)
        if not packet: break
        data += packet

    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("Q", packed_msg_size)[0]

    while len(data) < msg_size:
        data += client_socket.recv(4*1024)

    frame_data = data[:msg_size]
    data = data[msg_size:]

    frame = pickle.loads(frame_data)
    img = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    cv2.imshow("Remote Screen", img)

    if cv2.waitKey(1) == ord('q'):
        break

client_socket.close()
cv2.destroyAllWindows()
