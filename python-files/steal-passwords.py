import os
import keyring
import json

def get_edge_passwords():
    # Path to the Edge credentials file
    edge_credentials_path = os.path.expanduser("~") + r"\AppData\Local\Microsoft\Edge\User Data\Default\Login Data"

    # Check if the file exists
    if not os.path.exists(edge_credentials_path):
        print("Edge credentials file not found.")
        return

    # Load the credentials file
    with open(edge_credentials_path, 'r') as file:
        credentials = json.load(file)

    # Extract passwords
    passwords = []
    for credential in credentials:
        url = credential['origin_url']
        username = credential['username_value']
        password = keyring.get_password(url, username)
        if password:
            passwords.append(f"URL: {url}\nUsername: {username}\nPassword: {password}\n")

    return passwords

def save_passwords_to_file(passwords, filename='edge_passwords.txt'):
    with open(filename, 'w') as file:
        file.writelines(passwords)

if __name__ == "__main__":
    passwords = get_edge_passwords()
    if passwords:
        save_passwords_to_file(passwords)
        print("Passwords have been saved to edge_passwords.txt")
    else:
        print("No passwords found or an error occurred.")