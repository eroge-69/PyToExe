import os
import time
import getpass

def log_credentials(username, password):
    with open("credentials.txt", "a") as file:
        file.write("Username: username\nPassword: password\n")


def main():
    username = getpass.getuser()
    password = getpass.getpass()  # Replace with the method to retrieve the password
    log_credentials(username, password)

if __name__ == "__main__":
    main()
