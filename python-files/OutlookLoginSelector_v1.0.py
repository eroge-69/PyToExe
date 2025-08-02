import PySimpleGUI as sg import json import os from cryptography.fernet import Fernet from subprocess import Popen

=== CONFIG ===

DATA_FILE = 'emails.dat' KEY_FILE = 'secret.key'

=== ENCRYPTION SETUP ===

def load_key(): if not os.path.exists(KEY_FILE): key = Fernet.generate_key() with open(KEY_FILE, 'wb') as f: f.write(key) else: with open(KEY_FILE, 'rb') as f: key = f.read() return Fernet(key)

def save_emails(email_list): fernet = load_key() data = json.dumps(email_list).encode() encrypted = fernet.encrypt(data) with open(DATA_FILE, 'wb') as f: f.write(encrypted)

def load_emails(): if not os.path.exists(DATA_FILE): return [] fernet = load_key() with open(DATA_FILE, 'rb') as f: encrypted = f.read() try: decrypted = fernet.decrypt(encrypted) return json.loads(decrypted.decode()) except: return []

=== GUI WINDOWS ===

def main_window(emails): layout = [ [sg.Text('Select Email Accounts to Login:')], [sg.Checkbox(email, key=email)] for email in emails ] layout.append([sg.Button('Open Outlook'), sg.Button('Exit')]) return sg.Window('Outlook Login Selector', layout, finalize=True)

def editor_window(emails): layout = [ [sg.Text('Manage Email List')], [sg.Listbox(values=emails, size=(40, 6), key='EMAILS', enable_events=True)], [sg.Input(key='NEW_EMAIL'), sg.Button('Add')], [sg.Button('Remove Selected'), sg.Button('Save'), sg.Button('Cancel')] ] return sg.Window('Email Editor', layout, modal=True)

=== MAIN LOOP ===

def run(): emails = load_emails() win = main_window(emails)

while True:
    event, values = win.read(timeout=100)

    # Secret hotkey: Ctrl + Shift + E
    if event == '__TIMEOUT__':
        if sg.running_windows():
            try:
                if sg.get_windows()[0].TKroot.focus_get() and sg.tkinter.TkVersion >= 8:
                    if win.TKroot.focus_get().state() == ('Control', 'Shift', 'E'):
                        event = 'SecretEditor'
            except:
                pass

    if event in (sg.WINDOW_CLOSED, 'Exit'):
        break
    elif event == 'Open Outlook':
        selected = [email for email in emails if values.get(email)]
        if selected:
            sg.popup("Outlook will open. Please select the right account inside Outlook.")
            Popen(['start', 'outlook.exe'], shell=True)
        else:
            sg.popup("Please select at least one email account.")
    elif event == 'SecretEditor':
        win_editor = editor_window(emails)
        while True:
            e_event, e_vals = win_editor.read()
            if e_event in (sg.WINDOW_CLOSED, 'Cancel'):
                break
            elif e_event == 'Add':
                new_email = e_vals['NEW_EMAIL'].strip()
                if new_email and new_email not in emails:
                    emails.append(new_email)
                    win_editor['EMAILS'].update(values=emails)
                    win['__TIMEOUT__'] = True
            elif e_event == 'Remove Selected':
                selected_emails = e_vals['EMAILS']
                for email in selected_emails:
                    emails.remove(email)
                win_editor['EMAILS'].update(values=emails)
                win['__TIMEOUT__'] = True
            elif e_event == 'Save':
                save_emails(emails)
                break
        win_editor.close()
        win.close()
        win = main_window(emails)

win.close()

if name == 'main': run()

