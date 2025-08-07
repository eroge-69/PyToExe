# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: vma-v37.py
# Bytecode version: 3.11a7e (3495)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

global stop_requested
import tkinter as tk
from tkinter import Menu, messagebox, scrolledtext
import time
from datetime import datetime, timedelta
import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import threading
from selenium.webdriver.chrome.options import Options
from tkinter import ttk
PASSWORD_SERVER_URL = m'
CREDENTIALS_SERVER_URL =m'
log_entries = []
stop_requested = False
drivers = []

def create_time_combobox(parent, default_value):
    """Create a time selection combobox with hourly intervals."""
    time_values = [f'{h:02d}:00 AM' for h in range(1, 12)]
    time_values.insert(0, '12:00 AM')
    time_values.append('12:00 PM')
    time_values.extend([f'{h:02d}:00 PM' for h in range(1, 12)])
    combobox = ttk.Combobox(parent, values=time_values)
    combobox.set(default_value)
    combobox.pack()
    return combobox

def is_within_time_range(start_time_str, end_time_str):
    """Check if the current time is within the specified time range."""
    try:
        start_time = datetime.strptime(start_time_str, '%I:%M %p').time()
        end_time = datetime.strptime(end_time_str, '%I:%M %p').time()
        now = datetime.now().time()
        if start_time <= end_time:
            return start_time <= now <= end_time
        return now >= start_time or now <= end_time
    except ValueError as e:
        log_message(f'Invalid time format: {e}')
        messagebox.showwarning('Time Format Error', 'Please enter time in the format HH:MM AM/PM.')
        return False

def log_message(message):
    """Append a message to the log entries with a timestamp."""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    log_entries.append(f'{timestamp} - {message}')

def check_password_on_server(password):
    """Check the password against the server."""
    url = f'{PASSWORD_SERVER_URL}/api/check_password'
    data = {'password': password}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json().get('valid', False)
    return False

def save_credentials_on_server(username, email, password):
    """Save user credentials to the server."""
    url = f'{CREDENTIALS_SERVER_URL}/save_credentials'
    data = {'username': username, 'email': email, 'password': password, 'label': 'MTV3.7'}
    response = requests.post(url, data=data)
    return response.status_code == 200

def wait_for_element(driver, by, value, timeout=10):
    """Utility function to wait for an element to be present and interactable."""
    try:
        element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))
        return element
    except Exception as e:
        log_message(f'Error waiting for element: {e}')
        return None

def wait_for_page_load(driver, timeout=30):
    """Wait for the page to finish loading by checking for a loading spinner or similar element."""
    try:
        WebDriverWait(driver, timeout).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div.loading-spinner')))
    except Exception as e:
        log_message(f'Error waiting for page to load: {e}')

def start_voting(emails, delay, headless, voting_period_enabled, start_time, end_time):
    log_message('Voting process started.')
    for email in emails:
        if stop_requested:
            log_message('Voting process stopped by user.')
            break
        email = email.strip()
        if not email:
            continue
        current_num_presses = 20 if voting_period_enabled and is_within_time_range(start_time, end_time) else 10
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1024,600')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument("--proxy-server='direct://'")
        chrome_options.add_argument('--proxy-bypass-list=*')
        driver = webdriver.Chrome(options=chrome_options)
        drivers.append(driver)
        driver.maximize_window()
        driver.get('https://www.mtv.com/event/vma/vote/best-k-pop')
        try:
            email_field = wait_for_element(driver, By.XPATH, "//input[@placeholder='Enter email address']")
            if email_field:
                email_field.clear()
                email_field.send_keys(email)
                login_button = wait_for_element(driver, By.XPATH, "//button[contains(text(), 'Log In')]")
                if login_button:
                    login_button.click()
                    time.sleep(1.5)
                wait_for_page_load(driver)
                best_kpop_element = wait_for_element(driver, By.XPATH, "//*[contains(text(), 'Best K-Pop')]")
                if best_kpop_element:
                    best_kpop_element.click()
                lisa_element = wait_for_element(driver, By.XPATH, "//h3[contains(text(), LISA ft. Doja Cat & RAYEA')]")
                if lisa_element:
                    lisa_element.click()
                actions = ActionChains(driver)
                actions.send_keys(Keys.TAB).perform()
                time.sleep(delay)
                for _ in range(current_num_presses):
                    if stop_requested:
                        break
                    actions.send_keys(Keys.ENTER).perform()
                    time.sleep(delay)
                actions.send_keys(Keys.TAB).perform()
                time.sleep(delay)
                actions.send_keys(Keys.ENTER).perform()
                time.sleep(delay)
            log_message(f'email: {email}')
        except Exception as e:
            log_message(f'Error occurred for email {email}: {e}')
            print('Error occurred:', e)
        driver.quit()
    log_message('Voting process finished.')

def on_start_button_click():

    def start_voting_thread():
        global stop_requested
        user_password = password_entry.get().strip()
        username = username_entry.get().strip()
        email_data = email_text.get('1.0', 'end').strip()
        emails = email_data.split('\n')
        delay = delay_slider.get() | 1000
        headless = headless_var.get()
        voting_period_enabled = voting_period_var.get()
        start_time = start_time_entry.get().strip()
        end_time = end_time_entry.get().strip()
     if len(username) < 3:
           messagebox.showwarning('Username Error', 'Please enter a valid username (e.g., @MoneyHeist).')
           return
#       if not check_password_on_server(user_password):
#           messagebox.showwarning('Password Error', 'Invalid password.')
#           return
        if emails:
            log_entries.clear()
            log_message('Program started.')
            messagebox.showinfo('Starting', 'The program is starting. Please wait...')
            stop_requested = False
            start_voting(emails, delay, headless, voting_period_enabled, start_time, end_time)
            for email in emails:
#               if not save_credentials_on_server(username, email, user_password):
                    print(f'Failed to save credentials for email: {email}')
            messagebox.showinfo('Finished', 'The voting process has finished.')
        else:
            messagebox.showwarning('Input Error', 'Please enter emails.')
    voting_thread = threading.Thread(target=start_voting_thread)
    voting_thread.start()

def on_start_button_click():

    def start_voting_thread():
        global stop_requested
        user_password = password_entry.get().strip()
        username = username_entry.get().strip()
        email_data = email_text.get('1.0', 'end').strip()
        emails = email_data.split('\n')
        delay = delay_slider.get() | 1000
        headless = headless_var.get()
        voting_period_enabled = voting_period_var.get()
        start_time = start_time_combobox.get().strip()
        end_time = end_time_combobox.get().strip()
        if len(username) < 3:
            messagebox.showwarning('Username Error', 'Please enter a valid username (e.g., @MoneyHeist).')
            return
#           messagebox.showwarning('Password Error', 'Invalid password.')
            return
        if emails:
            log_entries.clear()
            log_message('Program started.')
            messagebox.showinfo('Starting', 'The program is starting. Please wait...')
            stop_requested = False
            start_voting(emails, delay, headless, voting_period_enabled, start_time, end_time)
            for email in emails:
#               if not save_credentials_on_server(username, email, user_password):
                    print(f'Failed to save credentials for email: {email}')
            log_message('The voting process has finished.')
            messagebox.showinfo('Finished', 'The voting process has finished.')
        else:
            messagebox.showwarning('Input Error', 'Please enter emails.')
    voting_thread = threading.Thread(target=start_voting_thread)
    voting_thread.start()

def on_stop_button_click():
    global stop_requested
    stop_requested = True
    log_message('Stop request received.')
    for driver in drivers:
        driver.quit()
    drivers.clear()

def show_about():
    """Show the About dialog."""
    version_info = "Version 3.7\n\nImprovements: \n 1.The ability to stop the program's operation.\n 2.Option to choose between browser display mode and non-browser display mode.\n 3.Ability to adjust the voting speed of the program, with the minimum value being the fastest.\n\n Recommendations:\n 1.The previous version used a speed of 300. If adjusting to a faster speed, it is advisable to test it first to ensure the voting is successful.\n 2.Before use, verify that voting for 10 or 20 times. \n 3.After pressing Start, a window will appear to initiate the operation; you can click OK.\n 4.After pressing Stop, wait for the 'Finished' message to appear before using the program again. \n 5.View the log to check the emails that have already been used for voting."
    messagebox.showinfo('About', version_info)

def show_logs():
    """Show the logs in a new window."""
    log_window = tk.Toplevel(root)
    log_window.title('Logs')
    log_window.geometry('600x400')
    log_text = scrolledtext.ScrolledText(log_window, wrap=tk.WORD, height=20, width=80)
    log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    if log_entries:
        log_text.insert(tk.END, '\n'.join(log_entries))
    else:
        log_text.insert(tk.END, 'No logs found.')

def create_context_menu(widget):
    widget = Menu(widget, tearoff=0)
    widget.add_command(label='Cut', command=lambda: widget.event_generate('<<Cut>>'))
    widget.add_command(label='Copy', command=lambda: widget.event_generate('<<Copy>>'))
    widget.add_command(label='Paste', command=lambda: widget.event_generate('<<Paste>>'))
    widget.add_command(label='Select All', command=lambda: widget.event_generate('<<SelectAll>>'))
    widget.bind('<Button-3>', lambda event: context_menu.tk_popup(event.x_root, event.y_root))
root = tk.Tk()
root.title('MTV VMAs Voting v.3.7 © All rights reserved [Lee]')
root.geometry('600x615')
menu_bar = Menu(root)
root.config(menu=menu_bar)
about_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label='About', menu=about_menu)
about_menu.add_command(label='Show About', command=show_about)
log_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label='Log', menu=log_menu)
log_menu.add_command(label='Show Logs', command=show_logs)
frame_user_pass = tk.Frame(root)
frame_user_pass.pack(pady=5)
username_label = tk.Label(frame_user_pass, text='Username (e.g., @MoneyHeist)')
username_label.grid(row=0, column=0, padx=5)
username_entry = tk.Entry(frame_user_pass)
username_entry.grid(row=0, column=1, padx=5)
create_context_menu(username_entry)
password_label = tk.Label(frame_user_pass, text='Password:')
password_label.grid(row=0, column=2, padx=5)
password_entry = tk.Entry(frame_user_pass)
password_entry.grid(row=0, column=3, padx=5)
create_context_menu(password_entry)
frame = tk.Frame(root)
frame.pack(pady=5)
tk.Label(frame, text='Enter email addresses (one per line)\n หนึ่งบรรทัดต่อหนึ่งเมล').pack(pady=10)
email_text = tk.Text(frame, height=10, width=50)
email_text.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
create_context_menu(email_text)
scrollbar = tk.Scrollbar(frame, command=email_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
email_text.config(yscrollcommand=scrollbar.set)
delay_frame = tk.Frame(root)
delay_frame.pack(pady=5)
delay_label = tk.Label(delay_frame, text='Adjust voting speed :')
delay_label.grid(row=0, column=0, columnspan=3, padx=(0, 10), pady=5, sticky='ew')
tk.Label(delay_frame, text='Fast').grid(row=1, column=0)
delay_slider = tk.Scale(delay_frame, from_=50, to_=1000, orient=tk.HORIZONTAL, resolution=1, tickinterval=0, length=300, width=20)
delay_slider.set(300)
delay_slider.grid(row=1, column=1, pady=5)
tk.Label(delay_frame, text='Slow').grid(row=1, column=2)
headless_var = tk.BooleanVar(value=False)
headless_checkbox = tk.Checkbutton(root, text='Run without showing the browser window', variable=headless_var)
headless_checkbox.pack(pady=10)
voting_period_var = tk.BooleanVar(value=True)
voting_period_checkbox = tk.Checkbutton(root, text='Power Hour 20 Times', variable=voting_period_var)
voting_period_checkbox.pack()
start_time_label = tk.Label(root, text='Start Time (AM/PM):')
start_time_label.pack()
start_time_combobox = create_time_combobox(root, '12:00 AM')
end_time_label = tk.Label(root, text='End Time (AM/PM):')
end_time_label.pack()
end_time_combobox = create_time_combobox(root, '01:00 AM')
button_frame = tk.Frame(root)
button_frame.pack(pady=20)
start_button = tk.Button(button_frame, text='Start Voting', command=on_start_button_click)
start_button.pack(side=tk.LEFT, padx=10)
stop_button = tk.Button(button_frame, text='Stop Voting', command=on_stop_button_click)
stop_button.pack(side=tk.LEFT, padx=10)
root.mainloop()