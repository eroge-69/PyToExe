# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: gui_ps3_syscon_uart_script.py
# Bytecode version: 3.10.0rc2 (3439)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

from binascii import unhexlify as uhx
from Crypto.Cipher import AES
import os
import string
import sys
import signal
import argparse
import time
import serial.tools.list_ports
import subprocess
import webbrowser
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

class PS3UART(object):
    def __init__(self, port, sc_type, serial_speed):
        try:
            import serial
        except ImportError:
            messagebox.showerror('Error', 'The pyserial module is required. You can install it with \'pip install pyserial\'')
            sys.exit(1)
        self.port = port
        self.sc_type = sc_type
        self.serial_speed = serial_speed
        self.ser = serial.Serial()
        self.sc2tb = uhx('71f03f184c01c5ebc3f6a22a42ba9525')
        self.tb2sc = uhx('907e730f4d4e0a0b7b75f030eb1d9d36')
        self.value = uhx('3350BD7820345C29056A223BA220B323')
        self.zero = uhx('00000000000000000000000000000000')
        self.auth1r_header = uhx('10100000FFFFFFFF0000000000000000')
        self.auth2_header = uhx('10010000000000000000000000000000')
        self.ser.port = port
        if serial_speed == '57600':
            self.ser.baudrate = 57600
        else:  # inserted
            if serial_speed == '115200':
                self.ser.baudrate = 115200
            else:  # inserted
                assert False
        self.type = sc_type
        self.ser.timeout = 0.1
        self.ser.open()
        assert self.ser.isOpen()
        self.ser.flush()

    def aes_decrypt_cbc(self, key, iv, data):
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = cipher.decrypt(data)
        return decrypted_data

    def aes_encrypt_cbc(self, key, iv, data):
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_data = cipher.encrypt(data)
        return encrypted_data

    def __del__(self):
        self.ser.close()

    def send(self, data):
        self.ser.write(data.encode('ascii'))

    def receive(self):
        return self.ser.read(self.ser.inWaiting())

    def command(self, com, wait=1, verbose=False):
        if verbose:
            print('Command: ' + com)
        if self.type == 'CXR':
            length = len(com)
            checksum = sum(bytearray(com, 'ascii')) % 256
            if length <= 10:
                self.send('C:{:02X}:{}\r\n'.format(checksum, com))
            else:  # inserted
                j = 10
                self.send('C:{:02X}:{}'.format(checksum, com[0:j]))
                for i in range(length - j, 15, (-15)):
                    self.send(com[j:j + 15])
                    j += 15
                self.send(com[j:] + '\r\n')
        else:  # inserted
            if self.type == 'SW':
                length = len(com)
                if length >= 64:
                    if self.command('SETCMDLONG FF FF')[0]!= 0:
                        return (4294967295, ['Setcmdlong'])
                checksum = sum(bytearray(com, 'ascii')) % 256
                self.send('{}:{:02X}\r\n'.format(com, checksum))
            else:  # inserted
                self.send(com + '\r\n')
        time.sleep(wait)
        answer = self.receive().decode('ascii', 'ignore').strip()
        if verbose:
            print('Answer: ' + answer)
        if self.type == 'CXR':
            answer = answer.split(':')
            if len(answer)!= 3:
                return (4294967295, ['Answer length'])
            checksum = sum(bytearray(answer[2], 'ascii')) % 256
            if answer[0]!= 'R' and answer[0]!= 'E':
                return (4294967295, ['Magic'])
            if answer[1]!= '{:02X}'.format(checksum):
                return (4294967295, ['Checksum'])
            data = answer[2].split(' ')
            if answer[0] == 'R' and len(data) < 2 or (answer[0] == 'E' and len(data)!= 2):
                return (4294967295, ['Data length'])
            if data[0]!= 'OK' or len(data) < 2:
                return (int(data[1], 16), [])
            return (int(data[1], 16), data[2:])
        if self.type == 'SW':
            answer = answer.split('\n')
            for i in range(0, len(answer)):
                answer[i] = answer[i].replace('\n', '').rsplit(':', 1)
                if len(answer[i])!= 2:
                    return (4294967295, ['Answer length'])
                checksum = sum(bytearray(answer[i][0], 'ascii')) % 256
                if answer[i][1]!= '{:02X}'.format(checksum):
                    return (4294967295, ['Checksum'])
                answer[i][0] += '\n'
            else:  # inserted
                ret = answer[(-1)][0].replace('\n', '').split(' ')
                if len(ret) < 2 or (len(ret[1])!= 8 and (not all((c in string.hexdigits for c in ret[1])))):
                    return (0, [x[0] for x in answer])
                if len(answer) == 1:
                    return (int(ret[1], 16), ret[2:])
                return (int(ret[1], 16), [x[0] for x in answer[:(-1)]])
        else:  # inserted
            return (0, [answer])

    def auth(self):
        if self.type == 'CXR' or self.type == 'SW':
            auth1r = self.command('AUTH1 10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
            if auth1r[0] == 0 and auth1r[1]!= []:
                auth1r = uhx(auth1r[1][0])
                if auth1r[0:16] == self.auth1r_header:
                    data = self.aes_decrypt_cbc(self.sc2tb, self.zero, auth1r[16:64])
                    if data[8:16] == self.zero[0:8] and data[16:32] == self.value and (data[32:48] == self.zero):
                        new_data = data[8:16] + data[0:8] + self.zero + self.zero
                        auth2_body = self.aes_encrypt_cbc(self.tb2sc, self.zero, new_data)
                        auth2r = self.command('AUTH2 ' + ''.join(('{:02X}'.format(c) for c in bytearray(self.auth2_header + auth2_body))))
                        return 'Auth successful' if auth2r[0] == 0 else 'Auth failed'
                return 'Auth1 response header invalid'
            return 'Auth1 response invalid'
        scopen = self.command('scopen')
        if 'SC_READY' in scopen[1][0]:
            auth1r = self.command('10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
            auth1r = auth1r[1][0].split('\r')[1][1:]
            if len(auth1r) == 128:
                auth1r = uhx(auth1r)
                if auth1r[0:16] == self.auth1r_header:
                    data = self.aes_decrypt_cbc(self.sc2tb, self.zero, auth1r[16:64])
                    new_data = data[8:16] == self.zero[0:8] and data[16:32] == self.value and (data[32:48] == self.zero) and (data[8:16] + data[0:8] + self.zero + self.zero)
                    auth2_body = self.aes_encrypt_cbc(self.tb2sc, self.zero, new_data)
                    auth2r = self.command(''.join(('{:02X}'.format(c) for c in bytearray(self.auth2_header + auth2_body))))
                    if 'SC_SUCCESS' in auth2r[1][0]:
                        return 'Auth successful'
                    return 'Auth failed'
                else:  # inserted
                    return 'Auth1 response body invalid'
                return 'Auth1 response header invalid'
            return 'Auth1 response invalid'
        return 'scopen response invalid'

def show_button_list(command_entry, handle_command):
    list_window = tk.Toplevel()
    list_window.title("BUTTON LIST")

    button_names = [
        "button1,errlog", "button2,EEP GET", "button3,EEP SET", "button4,clearerrlog",
        "button5,r", "button6,w", "button7,fantbl", "button8,patchvereep",
        "button9,auth", "button10,help", "button11,ERRLOG GET 00", "button12,EEP CSUM",
        "button13,Connect", "button14,Disconnect", "button15,Refresh", "button16,Settings",
        "button17,Play", "button18,Record", "button19,Mute", "button20,Unmute",
        "button21,Up", "button22,Down", "button23,Left", "button24,Right",
        "button25,Zoom In", "button26,Zoom Out", "button27,Full Screen", "button28,Exit",
        "button29,Add", "button30,Remove", "button31,Edit", "button32,Clear",
        "button33,Search", "button34,Filter", "button35,Sort", "button36,Reset",
        "button37,Enable", "button38,Disable", "button39,Lock", "button40,Unlock"
    ]

    def set_command_and_run(cmd_text):
        current_text = command_entry.get()
        if current_text.strip():
            # Ask if user wants to copy
            copy_choice = messagebox.askyesno("Copy to Clipboard?",
                                              f"Do you want to copy the existing command '{current_text}' to clipboard?")
            if copy_choice:
                list_window.clipboard_clear()
                list_window.clipboard_append(current_text)
                list_window.update()

        # Replace with new command
        command_entry.delete(0, tk.END)
        command_entry.insert(0, cmd_text)

        # Run the command
        handle_command()

        # Clear the command box regardless of success or error
        command_entry.delete(0, tk.END)

    # Create 4×10 grid of buttons
    for idx, entry in enumerate(button_names):
        label, cmd = entry.split(",", 1)
        row = idx // 4
        col = idx % 4
        btn = ttk.Button(list_window, text=label, command=lambda c=cmd: set_command_and_run(c))
        btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    for col in range(4):
        list_window.columnconfigure(col, weight=1)
    for row in range(10):
        list_window.rowconfigure(row, weight=1)



def main():
    def handle_command():
        port = port_combobox.get()
        command = command_entry.get()
        sc_type = sc_type_combobox.get()

        if not port or not sc_type:
            messagebox.showerror('Error', 'Please enter both the serial port and SC type.')
            return

        print('Port:', port)
        print('SC Type:', sc_type)
        print('Command:', command)

        if sc_type == 'CXR':
            serial_speed = '57600'
        else:
            serial_speed = '115200'

        ps3 = PS3UART(port, sc_type, serial_speed)
        ret = ps3.command(command)

        if ret[0] == 4294967295:
            messagebox.showerror('Error', 'Command execution failed: {}'.format(ret[1][0]))
            return

        if sc_type == 'CXR':
            output = '{:08X}'.format(ret[0]) + ' ' + ' '.join(ret[1])
        else:
            if not sc_type == 'SW' or (len(ret[1]) > 0 and '\n' not in ret[1][0]):
                output = '{:08X}'.format(ret[0]) + ' ' + ' '.join(ret[1])
            elif len(ret[1]) > 0:
                output = '{:08X}'.format(ret[0]) + '\n' + ''.join(ret[1])
            else:
                output = ret[1][0]

        output_text.insert(tk.END, output + '\n')

    def handle_auth():
        port = port_combobox.get()
        sc_type = sc_type_combobox.get()
        if not port or not sc_type:
            messagebox.showerror('Error', 'Please enter the serial port, SC type.')
            return
        if sc_type == 'CXR':
            serial_speed = '57600'
        else:  # inserted
            serial_speed = '115200'
        ps3 = PS3UART(port, sc_type, serial_speed)
        result = ps3.auth()
        messagebox.showinfo('Authentication Result', result)

    def open_error_logs_lookup():
        url = 'https://www.psdevwiki.com/ps3/Syscon_Error_Codes'
        webbrowser.open(url)

    def show_help():
        commands = ['External mode:', 'EEP GET (get EEPROM address)', 'EEP SET (set EEPROM address value)', 'ERRLOG GET 00 (get errorlog from code 0 - repeat until 1F)', '', 'Internal mode:', 'eepcsum (check EEPROM checksum)', 'errlog (get errlog)', 'clearerrlog (clear errorlog)', 'r (read from eeprom address)', 'w (write to eeprom address)', 'fantbl (get/set/getini/setini/gettable/settable)', 'patchvereep (get patched version)', '', 'Read the PS3-Uart-Guide-V2.pdf for further information']
        helper_window = tk.Toplevel()
        helper_window.title('Available Commands')
        commands_text = tk.Text(helper_window, height=len(commands), width=60)
        commands_text.pack(fill=tk.BOTH, expand=True)
        for command in commands:
            commands_text.insert(tk.END, command + '\n')
        commands_text.configure(state=tk.DISABLED)
        helper_window.mainloop()

    def refresh_ports():
        ports = []
        for port in serial.tools.list_ports.comports():
            if 'Serial' in port.description:
                ports.append(port.device)
        port_combobox['values'] = ports

    def handle_syscon_serial_output():
        serial_port = port_combobox.get()
        sc_type = sc_type_combobox.get()
        if not serial_port or not sc_type:
            messagebox.showerror('Error', 'Please enter the serial port and SC type.')
            return
        if sc_type == 'CXR':
            baud_rate = '57600'
        else:  # inserted
            baud_rate = '115200'
        base_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        script_path = os.path.join(base_dir, 'gui_diag_serial.py')
        if sys.platform.startswith('win'):
            command = ['python', script_path, serial_port, baud_rate]
        else:  # inserted
            command = ['python3', script_path, serial_port, baud_rate]
        subprocess.run(command)

    window = tk.Tk()
    window.title('PS3UART GUI')
    input_frame = tk.Frame(window)
    input_frame.grid(row=0, column=0, padx=10, pady=10)
    port_label = tk.Label(input_frame, text='Serial Port: (Examples: /dev/ttyUSB0 or COM1)')
    port_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
    port_combobox = ttk.Combobox(input_frame, values=serial.tools.list_ports.comports())
    port_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='w')
    refresh_button = tk.Button(input_frame, text='Refresh', command=refresh_ports)
    refresh_button.grid(row=0, column=2, padx=5, pady=5, sticky='w')
    available_ports = [port.device for port in serial.tools.list_ports.comports()]
    port_combobox = ttk.Combobox(input_frame, values=available_ports)
    port_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='w')
    sc_type_label = tk.Label(input_frame, text='SC Type: (Syscon type)')
    sc_type_label.grid(row=1, column=0, padx=5, pady=5, sticky='e')
    sc_type_combobox = ttk.Combobox(input_frame, values=['CXR', 'CXRF', 'SW'])
    sc_type_combobox.set('CXR')
    sc_type_combobox.grid(row=1, column=1, padx=5, pady=5, sticky='w')
    command_label = tk.Label(window, text='Command:')
    command_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')
    command_entry = tk.Entry(window)
    command_entry.grid(row=1, column=1, padx=10, pady=5, sticky='we')
    output_text = tk.Text(window, height=10, width=60)
    output_text.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
    input_button = tk.Button(window, text='Send Command', command=handle_command)
    input_button.grid(row=3, column=0, padx=10, pady=5, sticky='we')
    button_list_btn = ttk.Button(window, text="Button List",
                             command=lambda: show_button_list(command_entry, handle_command))
    button_list_btn.grid(row=0, column=3, padx=10, pady=10, sticky='ne')
    auth_button = tk.Button(window, text='Auth', command=handle_auth)
    auth_button.grid(row=3, column=1, padx=10, pady=5, sticky='we')
    help_button = tk.Button(window, text='Help', command=show_help)
    help_button.grid(row=4, column=0, padx=10, pady=5, sticky='we')
    error_logs_button = tk.Button(window, text='Psdevwiki - Error logs', command=open_error_logs_lookup)
    error_logs_button.grid(row=4, column=1, padx=10, pady=5, sticky='we')
    syscon_serial_output_button = tk.Button(window, text='Diagnose Syscon Serial Output', command=handle_syscon_serial_output)
    syscon_serial_output_button.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky='we')
    window.grid_rowconfigure(2, weight=1)
    window.grid_columnconfigure(1, weight=1)
    window.mainloop()
if __name__ == '__main__':
    main()