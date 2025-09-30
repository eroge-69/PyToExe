
import os

DownCounter = 0

print ("This is a network availability checker script\n")


ip_check = ["192.168.1.1","192.168.1.130","192.168.1.41","192.168.1.140","192.168.1.82","192.168.1.200","192.168.1.35"]  # List with the important ip

for ip in ip_check:
    

    response = os.popen (f"ping {ip}").read()

    if 'unreachable' not in response :   #means that the string received = 4 is found and ping succeeded
        print ("-----------------Checking Process-----------------\n")     
    else : 
        print(f"Host with IP : {ip} is not working\n") 
        DownCounter+=1
    
if DownCounter == len(ip_check):
    print("All Hosts Are Working ")

print("Checking Process is finished")
        
