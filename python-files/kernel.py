print("""
 0000       000000000      0000         0       0       0    000000000      000000000       0       000000000
0    0      0              0   0000     0       0      0 0       0         0               0 0          0
0     0     0              0      0     0       0     0   0      0        0               0   0         0
0000000     000000000      0      0     000000000    0000000     0       0               0000000        0
0     0     0              0      00    0       0    0     0     0        0              0     0        0
0     0     0              0      0     0       0    0     0     0         0             0     0        0
0     00    000000000      000000000    0       0    0     0     0          000000000    0     0        0
""")
print("os is starting")
print("redhatcat bootloader commands the 1st command is (bootdev) the bootdev is a command this starts the redhatcat for developers and the 2nd command i the (boot) its boot the redhatcat original normal edition")
import os

def run_command(command):
    if command == "bootdev":
        os.system("redhatcatdev")
    elif command == "boot":
        os.system("redhatcat")
    else:
        print("Invalid command.")

while True:
    command = input("Enter command: ")
    run_command(command)