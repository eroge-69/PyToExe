import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import ctypes
import cv2
import tempfile
import random
import string
import smtplib
import time
import threading
from datetime import datetime, timedelta
from email.message import EmailMessage
from email.mime.text import MIMEText
import mimetypes
import sys
import webbrowser
import winreg

# Create hidden persistent folder inside AppData\Roaming
appdata_path = os.path.join(os.getenv("APPDATA"), "USBControl")
os.makedirs(appdata_path, exist_ok=True)

lock_file = os.path.join(appdata_path, "lockout_time.txt")

# Make the folder hidden (Windows only)
try:
    ctypes.windll.kernel32.SetFileAttributesW(appdata_path, 0x02)  # 0x02 = FILE_ATTRIBUTE_HIDDEN
except:
    pass  # silently fail if not Windows

# Final secure file paths
password_file = os.path.join(appdata_path, "session_pass.txt")
registration_file = os.path.join(appdata_path, "user_info.txt")
sender_password = "gihj qpnc jgnk dqxb"

# ------------------- Helper Functions -------------------
def generate_passcode():
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    with open(password_file, "w") as f:
        f.write(code)
    return code

def send_passcode_email(to_email, employee_name, passcode):
    sender_email = "suprajaintern@gmail.com"
    sender_password = "gihj qpnc jgnk dqxb"  # Replace with your secure app password

    subject = "Your USB Access Passcode"
    body = f"""Hello {employee_name},

Your registration was successful.
Your USB access passcode is: {passcode}

Regards,
IT Security Team"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        print("Passcode email sent.")
    except Exception as e:
        print("Email error:", e)
    
def send_intruder_alert_email(sender_email, sender_password, to_email, employee_name, image_path):
    try:
        msg = EmailMessage()
        msg['Subject'] = '🚨 Intruder Alert Attempt'
        msg['From'] = sender_email
        msg['To'] = to_email

        msg.set_content(f"""
Hi {employee_name},

❌ Someone tried to access your USB control panel with an incorrect passcode.

📸 An image of the person is attached below.

If this wasn't you, please take immediate action.

Stay safe,
IT Security Team
""")

        if os.path.exists(image_path):
            mime_type, _ = mimetypes.guess_type(image_path)
            mime_main, mime_sub = mime_type.split('/')
            with open(image_path, 'rb') as img:
                msg.add_attachment(img.read(), maintype=mime_main, subtype=mime_sub, filename=os.path.basename(image_path))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print("✅ Intruder alert email sent with image.")

    except Exception as e:
        print("❌ Error sending intruder email:", e)


def get_stored_passcode():
    if os.path.exists(password_file):
        with open(password_file, "r") as f:
            return f.read().strip()
    return None

def is_locked():
    if not os.path.exists(lock_file):
        return False
    try:
        with open(lock_file, "r") as f:
            locked_until = datetime.fromisoformat(f.read().strip())
            return datetime.now() < locked_until
    except:
        return False

def start_lock_timer():
    locked_until = datetime.now() + timedelta(minutes=30)
    with open(lock_file, "w") as f:
        f.write(locked_until.isoformat())
    change_usb_state(enable=False)

def take_intruder_snapshot():
    try:
        cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # or cv2.VideoCapture(0) for Linux
        time.sleep(2)  # Give camera time to initialize

        # Read a few frames to "warm up" the camera
        for i in range(10):
            ret, frame = cam.read()
            if not ret or frame is None or frame.sum() == 0:
                time.sleep(0.1)
                continue
            else:
                image_path = os.path.join(tempfile.gettempdir(), "intruder.jpg")
                cv2.imwrite(image_path, frame)
                print("✅ Intruder image captured.")
                break
        else:
            print("❌ Failed to capture valid frame after retries.")

        cam.release()
        cv2.destroyAllWindows()

    except Exception as e:
        print("Snapshot error:", e)


def is_registered():
    return os.path.exists(registration_file)

def store_registration(name, emp_id, dept, email):
    with open(registration_file, "w") as f:
        f.write(f"{name},{emp_id},{dept},{email}")



def load_registration():
    with open(registration_file, "r") as f:
        return f.read().split(",")
def check_camera_permission():
    try:
        cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        time.sleep(2)
        ret, frame = cam.read()
        cam.release()
        if not ret or frame is None or frame.sum() == 0:
            return False
        return True
    except Exception as e:
        print("Camera check error:", e)
        return False
def resource_path(relative_path):
    """ Get absolute path to resource (works for .py and .exe) """
    try:
        base_path = sys._MEIPASS  # Used by PyInstaller
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def change_usb_state(enable=True):
    try:
        key_path = r"SYSTEM\CurrentControlSet\Services\USBSTOR"
        access = winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY

        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, access) as key:
            value = 3 if enable else 4
            winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, value)
            print(f"✅ Registry updated. USB {'Enabled' if enable else 'Disabled'}")
    except PermissionError:
        print("❌ Permission Denied: Please run the app as Administrator.")
        messagebox.showerror("Admin Access Required", "Please run this program as Administrator to modify USB settings.")
    except Exception as e:
        print("❌ Registry update error:", e)
        messagebox.showerror("Error", f"Failed to update registry: {e}")


def get_usb_status():
    try:
        result = subprocess.check_output(
            'reg query "HKLM\\SYSTEM\\CurrentControlSet\\Services\\USBSTOR" /v Start',
            shell=True, text=True
        )
        if "0x4" in result:
            return "Disabled"
        elif "0x3" in result:
            return "Enabled"
        else:
            return "Unknown"
    except Exception as e:
        print("USB status check error:", e)
        return "Unknown"
def show_terms_and_conditions(self):
    terms_win = tk.Toplevel(self.root)
    terms_win.title("Terms and Conditions")
    terms_win.geometry("600x400")
    terms_win.configure(bg="#f5f5f5")

    tk.Label(
        terms_win, text="Terms and Conditions", 
        font=("Segoe UI", 14, "bold"), 
        bg="#f5f5f5", fg="#003366"
    ).pack(pady=10)

    # Scrollable frame
    frame = tk.Frame(terms_win)
    frame.pack(expand=True, fill="both", padx=10)

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side="right", fill="y")

    text_box = tk.Text(frame, wrap="word", yscrollcommand=scrollbar.set, font=("Segoe UI", 10))
    text_box.pack(expand=True, fill="both")
    scrollbar.config(command=text_box.yview)

    # Terms text
    terms_text = """
USB Access Control Application - Terms

1. Admin Rights Required
This app needs admin privileges to change USB port settings.

2. Camera Access
Used for intruder snapshots when incorrect passcodes are entered.

3. Personal Data
Your details are collected only for sending OTP securely.

4. Internet Requirement
Internet is required for OTP and intruder alert emails.

5. Security
After 3 wrong passcode attempts, USB is locked for 30 minutes.

6. Consent
By clicking 'I Agree', you accept these terms.
"""
    text_box.insert("1.0", terms_text.strip())
    text_box.config(state="disabled")

    # Button frame
    btn_frame = tk.Frame(terms_win, bg="#f5f5f5")
    btn_frame.pack(pady=10)

    tk.Button(
        btn_frame, text="I Agree", 
        bg="#4da6ff", fg="white", 
        font=("Segoe UI", 11, "bold"), width=15,
        command=lambda: [terms_win.destroy(), self.register_form(first_time=True)]
    ).pack(side="left", padx=10)

    tk.Button(
        btn_frame, text="Decline", 
        bg="gray", fg="white", 
        font=("Segoe UI", 11), width=15,
        command=lambda: [terms_win.destroy(), self.root.quit()]
    ).pack(side="right", padx=10)

# ------------------- GUI Class -------------------
class USBControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("USB Access Panel")
        self.root.geometry("500x300")

        self.root.configure(bg="#e6f2ff")

        # Top-right corner buttons
        self.details_btn = tk.Button(root, text="Details", font=("Segoe UI", 10), bg="#4da6ff", fg="white", command=self.show_details)
        self.details_btn.place(x=410, y=10)

        self.re_register_btn = tk.Button(root, text="Re-Register", font=("Segoe UI", 10), bg="#4da6ff", fg="white", command=self.register_form)
        self.re_register_btn.place(x=400, y=40)

        # Welcome message
        self.success_label = tk.Label(root, text="USB Control Panel", bg="#e6f2ff", font=("Segoe UI", 16, "bold"), fg="#003366")
        self.success_label.pack(pady=20)
        self.status_label = tk.Label(self.root, text="", font=("Segoe UI", 11, "bold"), fg="black", bg="#e6f2ff")
        self.status_label.pack(pady=5)
        self.update_usb_status()



        # Buttons
        btn_disable = tk.Button(root, text="Disable USB", font=("Segoe UI", 12), bg="#ff6666", fg="white", width=20, command=self.button_disable_clicked)
        btn_disable.pack(pady=10)

        btn_enable = tk.Button(root, text="Enable USB", font=("Segoe UI", 12), bg="#66cc66", fg="white", width=20, command=self.button_enable_clicked)
        btn_enable.pack(pady=10)

        # Generate first session passcode
        self.session_code = generate_passcode()


    def button_disable_clicked(self):
        user = load_registration()
        new_pass = generate_passcode()
        send_passcode_email(user[3], user[0], new_pass)
        self.ask_password(disable=True)

    def button_enable_clicked(self):
        user = load_registration()
        new_pass = generate_passcode()
        send_passcode_email(user[3], user[0], new_pass)
        self.ask_password(disable=False)
    def update_usb_status(self):
        try:
           status = get_usb_status()
           if status == "Enabled":
              self.status_label.config(text="USB Status: ENABLED", fg="green")
           elif status == "Disabled":
               self.status_label.config(text="USB Status: DISABLED", fg="red")
           else:
               self.status_label.config(text="USB Status: UNKNOWN", fg="orange")
        
           self.root.after(1000, self.update_usb_status)  # 🔄 refresh every 1 second
        except tk.TclError:
            pass


    def ask_password(self, disable):
        win = tk.Toplevel(self.root)
        win.geometry("300x150")
        win.title("Enter Passcode")

        tk.Label(win, text="Enter Passcode:", font=("Segoe UI", 11)).pack(pady=10)
        entry = tk.Entry(win, show="*")
        entry.pack()

        error_lbl = tk.Label(win, text="", fg="red")
        error_lbl.pack()
        def check():
            entered = entry.get()
            stored = get_stored_passcode()
            user = load_registration()  # 🔧 Move this to the top

            self.intruder_attempts = getattr(self, 'intruder_attempts', 0)

            if entered == stored:
                change_usb_state(enable=not disable)
                self.update_usb_status()
                new_pass = generate_passcode()
                send_passcode_email(user[3], user[0], new_pass)
                win.destroy()
                msg = "USB Disabled Successfully" if disable else "USB Enabled Successfully"
                messagebox.showinfo("Success", msg)
            else:
                error_lbl.config(text="Incorrect Passcode")
                self.intruder_attempts += 1

                if self.intruder_attempts >= 3:
                    start_lock_timer()
                    messagebox.showwarning(
                        "Access Blocked",
                        "Too many incorrect attempts!\nUSB access is blocked for 30 minutes."
                    )
                    win.destroy()
                    self.root.quit()
                    return

                def handle_intruder():
                    take_intruder_snapshot()
                    image_path = os.path.join(tempfile.gettempdir(), "intruder.jpg")
                    send_intruder_alert_email(
                        "suprajaintern@gmail.com",
                        sender_password,
                        user[3],
                        user[0],
                        image_path
                    )

                threading.Thread(target=handle_intruder).start()
                messagebox.showerror("Access Denied", "Wrong password!")

        tk.Button(win, text="Submit", command=check).pack(pady=10)

    def show_details(self):
        if not is_registered():
            messagebox.showinfo("Info", "User not registered")
        else:
            html_content = """<!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Project Information</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          margin: 40px;
        }
        h1 {
          font-size: 24px;
        }
        .bold {
          font-weight: bold;
        }
        table {
          border-collapse: collapse;
          width: 100%;
          margin-top: 10px;
          margin-bottom: 20px;
        }
        th, td {
          border: 1px solid #ccc;
          padding: 10px;
          text-align: left;
        }
        .highlight {
          background-color: #e6f0ff;
          font-weight: bold;
          padding: 5px 10px;
          display: inline-block;
          margin-top: 20px;
         }
         .section-title {
           font-weight: bold;
           font-size: 20px;
           margin-top: 40px;
         }
         .logo {
           float: right;
           width: 120px;
         }
       </style>
     </head>
     <body>

       <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT4P6iGaMswghbuKAEXEm-jxpH0TKRwKJycSg&s" alt="Supraja Logo" class="logo">

       <h1>Project Information</h1>
       <p>This project was developed by <span class="bold">Dhilleswar rao, Manikanta, Rochanakumar</span> as part of a 
         <span class="bold">Cyber Security Internship</span>. This project is designed for  
         <span class="bold">A desktop security application that controls USB access and captures intruder snapshots using a webcam when incorrect passcodes are entered.</span>
       </p>

       <table>
         <tr>
           <th>Project Details</th>
           <th>Value</th>
         </tr>
         <tr>
           <td>Project Name</td>
           <td>USB Physical Security</td>
         </tr>
         <tr>
           <td>Project Description</td>
           <td>A desktop security application that controls usb access.</td>
         </tr>
         <tr>
           <td>Project Start Date</td>
           <td>06-JULY-2025</td>
         </tr>
         <tr>
           <td>Project End Date</td>
           <td>09-AUGUST-2025</td>
         </tr>
         <tr>
           <td>Project Status</td>
           <td><b>Completed</b></td>
         </tr>
       </table>

       <div class="bold">Developer Details</div>

       <table>
         <tr>
           <th>Name</th>
           <th>Employee ID</th>
           <th>Email</th>
         </tr>
         <tr>
           <td>Dilleswar rao</td>
           <td>ST#IS#7804</td>
           <td>dhilliallua1@gmail.com</td>
         </tr>
         <tr>
           <td>Manikanta</td>
           <td>ST#IS#7805</td>
           <td>yelamanchilimanikanta123@gmail.com</td>
         </tr>
         <tr>
           <td>Rochanakumar</td>
           <td>ST#IS#7806</td>
           <td>rochanakumar0001@gmail.com</td>
         </tr>
       </table>

       <div class="bold">Company Details</div>

       <table>
         <tr>
           <th>Company</th>
           <th>Value</th>
         </tr>
         <tr>
           <td>Name</td>
           <td>Supraja Technologies</td>
         </tr>
         <tr>
           <td>Email</td>
           <td>contact@suprajatechnologies.com</td>
         </tr>
       </table>

     </body>
     </html>
     """
        file_path = os.path.join(tempfile.gettempdir(), "project_info.html")
        with open(file_path, "w", encoding="utf-8") as f:
             f.write(html_content)

        webbrowser.open(f"file://{file_path}")
         


    def register_form(self, first_time=False):
        win = tk.Toplevel(self.root)
        win.geometry("420x420")
        win.title("Employee Registration")
        win.configure(bg="#f0f8ff")

        tk.Label(win, text="Register Employee", font=("Segoe UI", 15, "bold"),
                 bg="#f0f8ff", fg="#003366").pack(pady=15)

        entries = {}
        fields = ["Name", "Employee ID", "Department", "Email"]

        for field in fields:
            frame = tk.Frame(win, bg="#f0f8ff")
            frame.pack(pady=8, padx=40, fill="x")

            tk.Label(frame, text=field + ":", font=("Segoe UI", 10, "bold"),
                     bg="#f0f8ff").pack(side="left")
            entry = tk.Entry(frame, font=("Segoe UI", 10), width=30)
            entry.pack(side="right")
            entries[field] = entry
        def submit():
            values = [entries[field].get().strip() for field in fields]
            if all(values):
               if not check_camera_permission():
                  messagebox.showwarning(
                      "Camera Permission Required",
                      "Camera access is required to capture intruders.\n\n"
                      "Please allow access to the webcam in your antivirus or system settings,\n"
                      "then restart the application."
                  )
                  win.destroy()
                  self.root.quit()
                  return

               store_registration(*values)
               passcode = generate_passcode()
               send_passcode_email(values[3], values[0], passcode)

               messagebox.showinfo("Success", "Successfully Registered!")
               win.destroy()
               self.success_label.config(text="Registration Completed. Welcome!")
               if first_time:
                  self.root.deiconify()
               else:
                  messagebox.showerror("Error", "Please fill all fields.")

        tk.Button(win, text="Finish Setup", bg="#4da6ff", fg="white",
                  font=("Segoe UI", 11, "bold"), width=20, height=2,
                  command=submit).pack(pady=30)

# ------------------- App Launch -------------------

if __name__ == "__main__":
    if is_locked():
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning(
            "Service Temporarily Blocked",
            "Due to multiple incorrect attempts, USB Control is locked for 30 minutes."
        )
        sys.exit()

    root = tk.Tk()
    if not is_registered():
        root.withdraw()
        app = USBControlApp(root)
        app.show_terms_and_conditions()
        app.register_form(first_time=True)
    else:
        app = USBControlApp(root)
    root.mainloop()
