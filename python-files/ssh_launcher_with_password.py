
import subprocess
import pty
import os

ssh_command = [
    "ssh",
    "-o", "StrictHostKeyChecking=no",
    "-N",
    "-R",
    "53700:192.168.100.57:43700",
    "biobridge@192.168.1.50"
]

password = "M15@2dwin0n7y"

def run_ssh_with_password():
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp(ssh_command[0], ssh_command)
    else:
        while True:
            try:
                output = os.read(fd, 1024).decode("utf-8")
                print(output, end="")
                if "password:" in output.lower():
                    os.write(fd, (password + "\n").encode("utf-8"))
                    break
            except OSError:
                break

if __name__ == "__main__":
    run_ssh_with_password()
