
import paramiko
import pandas as pd
import openpyxl
import tkinter as tk
from tkinter import filedialog, messagebox

def ssh_login(ip, credentials):
    for username, password, enable_password in credentials:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=username, password=password)
            if enable_password:
                shell = ssh.invoke_shell()
                shell.send('enable\n')
                shell.send(f'{enable_password}\n')
            return ssh
        except Exception:
            continue
    return None

def run_commands(ssh, commands):
    output = {}
    for command in commands:
        stdin, stdout, stderr = ssh.exec_command(command)
        output[command] = stdout.read().decode()
    return output

def generate_report(data, output_file):
    df = pd.DataFrame(data)
    df.to_excel(output_file, index=False)

def process_racks(file_path, credentials, commands):
    df = pd.read_excel(file_path, engine='openpyxl')
    report_data = []

    for index, row in df.iterrows():
        ip = row['Rack IP']
        rack_info = {'Rack IP': ip}
        ssh = ssh_login(ip, credentials)
        if ssh:
            rack_info['Login Status'] = 'Success'
            command_output = run_commands(ssh, commands)
            rack_info.update(command_output)
            ssh.close()
        else:
            rack_info['Login Status'] = 'Failed'
        report_data.append(rack_info)

    output_file = 'rack_report.xlsx'
    generate_report(report_data, output_file)
    messagebox.showinfo("Success", f"Report generated: {output_file}")

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        credentials = [
            ('Itpo', 'ItpoNetwork@2023', 'ItpoEnable@246'),
            ('jeetu', 'Jeetu@4321', None),
            ('akash', 'Misra@9000', None)
        ]
        commands = [
            'sh sw',
            'sh int status',
            'sh cdp neighbors',
            'sh device-tracking database',
            'sh ip device tracking all'
        ]
        process_racks(file_path, credentials, commands)

root = tk.Tk()
root.title("Rack Checker Application")
root.geometry("300x150")

btn_select_file = tk.Button(root, text="Select Excel File", command=select_file)
btn_select_file.pack(pady=20)

root.mainloop()
