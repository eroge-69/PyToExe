import keyring
import webview
import subprocess
import os
import ctypes

SERVICE_NAME = "OutlookApp"
ACCOUNT_KEY = "OutlookAccount"   # fixed key

def get_credentials():
    """Retrieve saved credentials, otherwise prompt user."""
    creds = keyring.get_password(SERVICE_NAME, ACCOUNT_KEY)
    if creds:
        # Stored as "email|password"
        try:
            email, password = creds.split("|", 1)
            return email, password
        except Exception:
            pass

    # If no saved credentials → ask user
    email = input("Enter your Outlook Email: ")
    password = input("Enter your Outlook Password: ")

    if email and password:
        # Save as single string "email|password"
        keyring.set_password(SERVICE_NAME, ACCOUNT_KEY, f"{email}|{password}")
        return email, password
    else:
        print("Email & password required!")
        return None, None


def notify_outlook_loaded():
    """Send a Windows Toast notification via PowerShell."""
    try:
        ps_script = '''
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
        $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
        $textNodes = $template.GetElementsByTagName("text")
        $textNodes.Item(0).AppendChild($template.CreateTextNode("Outlook")) > $null
        $textNodes.Item(1).AppendChild($template.CreateTextNode("Outlook has loaded successfully!")) > $null
        $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
        $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("OutlookApp")
        $notifier.Show($toast)
        '''
        subprocess.run(["powershell", "-Command", ps_script], check=True)
    except Exception as e:
        print(f"Notification failed: {e}")


# ---- Force custom icon using Win32 API ----
def set_window_icon(window_title, icon_path):
    hwnd = ctypes.windll.user32.FindWindowW(None, window_title)
    if hwnd and os.path.exists(icon_path):
        hicon = ctypes.windll.user32.LoadImageW(
            0, icon_path, 1, 0, 0, 0x00000010  # IMAGE_ICON
        )
        # set small icon
        ctypes.windll.user32.SendMessageW(hwnd, 0x80, 0, hicon)
        # set big icon
        ctypes.windll.user32.SendMessageW(hwnd, 0x80, 1, hicon)


def open_outlook_web_in_app():
    try:
        # show notification before window loads
        notify_outlook_loaded()

        window = webview.create_window(
            "Outlook",
            "https://outlook.office.com/mail/",
            width=1200,
            height=800
        )

        def on_loaded():
            if os.path.exists("icon.ico"):
                set_window_icon("Outlook", os.path.abspath("icon.ico"))

        webview.start(on_loaded)

    except Exception as e:
        print(f"Failed to open Outlook: {e}")


# Directly open Outlook Web
user, pwd = get_credentials()

# If credentials were retrieved or entered, launch Outlook Web
if user and pwd:
    open_outlook_web_in_app()
