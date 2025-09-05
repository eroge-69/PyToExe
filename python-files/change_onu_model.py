#!/usr/bin/python
# -*- coding: utf-8 -*-

import telnetlib
from time import sleep
from argparse import ArgumentParser

# Argument
parser = ArgumentParser()

parser.add_argument("-i", dest="device", required=True, help="IP addresss", default="192.168.0.1")
parser.add_argument("-u", dest="user", help="user/login name", default="admin")
parser.add_argument("-p", dest="password", help="password", default="!vkf4Kr#Hjc32idf")
options = parser.parse_args()

host = options.device
user = options.user
password = options.password

# Login
tn = telnetlib.Telnet(host)
tn.read_until(b"login:")
tn.write(user.encode("utf-8") + b"\n")
tn.read_until(b"Password:")
tn.write(password.encode("utf-8") + b"\n")

# Commands
tn.read_until(b"#")
tn.write(b"mib set GPON_ONU_MODEL DM986-416-AX30\n")
tn.read_until(b"#")

sleep(2)
tn.write(b"mib commit\n")
tn.read_until(b"#")

sleep(2)
tn.write(b"reboot\n")
output = tn.read_until(b"#").decode("utf-8")
print(output)
print("Done!")

tn.write(b"exit\n")
tn.close()
