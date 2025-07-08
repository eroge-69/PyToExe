import subprocess
import tkinter as tk
from tkinter import messagebox

# List of computers to check
comp_list = ['MCL132','MCL129','MCL115','MCL118','MCL120','MCL126','MCL127','MCL128','MCL179','MCL181','MCL182']

# Prepare commands for each machine
cmd_list = [['qwinsta', '/server:' + comp_name] for comp_name in comp_list]


# Run qwinsta for each machine
procs_list = []
for cmd in cmd_list:
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,  # Don't use shell=True with list
            timeout=10  # Shorter timeout for testing; increase as needed
        )
    except subprocess.TimeoutExpired:
        proc = subprocess.CompletedProcess(cmd, returncode=1, stdout=b'', stderr=b'Timeout')
    procs_list.append(proc)

# Build the message output
messageout = '          Open Source \n'
for i, proc in enumerate(procs_list):
    output = proc.stdout.decode('utf-8', errors='ignore')
    error = proc.stderr.decode('utf-8', errors='ignore')

    messageout += f"{comp_list[i]}:           "

    if proc.returncode != 0 or 'Error' in error or 'Timeout' in error:
        messageout += 'Error/Offline'
    elif 'Active' in output:
        messageout += 'Active'
    else:
        messageout += 'Inactive'

    if i == 1:
        messageout += '\n\n          Modelling'
    messageout += '\n'

# Display result in messagebox
root = tk.Tk()
root.withdraw()  # Hide the main window
messagebox.showinfo("PC Usage Status", messageout)
root.mainloop()
