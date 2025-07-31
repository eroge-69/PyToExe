import pandas as pd
import chardet
import ipaddress
import re
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from typing import Union, Optional

# ------------------ CONFIG ------------------ #
CONFIG = {
    'encoding': ['utf-8', 'utf-8-sig'],
    'delimiter': ';',
    'required_columns': [
        'PLZ2',
        'Ort2',
        'str.',
        'Nr',
        'Nr. Zusatz',
        'Fortinet Serialnumber',
        'Schulungsnetz Netzwerkadresse',
        'Schulungsnetz Subnetzmaske',
        'Spielstättennetz Netzwerkadresse',
        'Spielstättennetz Subnetzmaske',
        'Standortnetz Netzwerkadresse',
        'Standortnetz Subnetzmaske',
        'Kunden Host Name',
        'DTSec-Loopback',
        'Firewall Host Name',
        'MPLS IP-CE Router',
        'Rollout Termine',
        'FortiAP Serialnumber',
        'FortiAP LizenzKey'
    ],
    'valid_ip_ranges': {
        'standortnetz': ['172.27.0.0/16', '172.29.0.0/16'],
        'spielstaetten': ['172.28.0.0/16', '172.30.0.0/16'],
        'schulungsnetz': ['10.56.0.0/15']
    },
    'device_blueprint': 'Spielstaetten_ZTP',
    'excel_date_base': datetime(1899, 12, 30),
    'ip_networks': {
        'dtsec_mgmt_loopback': '172.21.58.0/23'
    },
    'name_pattern': r'^[A-Z]{2}-\d{6}-\d{3}-\d{3}$',
    'firewall_hostname_pattern': r'^[a-z]{2}-[a-z]{3,7}-[a-z]{6}-[a-z]{2,4}-\d{1,3}$'
}

# ------------------ FUNKTIONEN AUS DEINEM SKRIPT ------------------ #
def check_file_encoding(file_path: str) -> bool:
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        return encoding.lower() in CONFIG['encoding']

def is_semicolon_separated(file_path: str) -> bool:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            first_line = file.readline()
            return CONFIG['delimiter'] in first_line
    except Exception as e:
        raise ValueError(f"Error checking the delimiter: {str(e)}")

def calculate_first_usable_ip(network_address: str, subnet_mask: str) -> str:
    try:
        cidr = f'{network_address}/{subnet_mask}'
        network = ipaddress.ip_network(cidr, strict=False)
        first_usable_ip = network.network_address + 1
        return f'{first_usable_ip}/{network.prefixlen}'
    except ValueError as e:
        return f'Invalid network address/subnet mask: {e}'

def excel_to_date(date_value: Union[int, str]) -> Optional[datetime]:
    if isinstance(date_value, int):
        try:
            return CONFIG['excel_date_base'] + timedelta(days=date_value)
        except ValueError:
            return None
    elif isinstance(date_value, str):
        try:
            day, month, year = map(int, date_value.split('.'))
            return datetime(year, month, day)
        except ValueError:
            return None
    else:
        return None

def is_valid_serial_number(serial_number: str) -> bool:
    if not isinstance(serial_number, str) or len(serial_number) == 0:
        return False
    if len(serial_number) != 16:
        return False
    if not serial_number.startswith("FG"):
        return False
    return True

def is_valid_device_blueprint(blueprint: str) -> bool:
    return isinstance(blueprint, str) and len(blueprint) > 0

def is_valid_name(name: str) -> bool:
    return bool(re.match(CONFIG['name_pattern'], name))

def is_valid_ip(ip: str, network: str = None) -> bool:
    try:
        ip_address = ipaddress.ip_address(ip.split('/')[0])
        if network:
            return ip_address in ipaddress.ip_network(network)
        return True
    except ValueError:
        return False

def is_valid_firewall_hostname(hostname: str) -> bool:
    return bool(re.match(CONFIG['firewall_hostname_pattern'], hostname))

def is_valid_location_address(address: str) -> bool:
    return isinstance(address, str) and len(address) > 0

def is_valid_mpls_gateway_ip(ip: str) -> bool:
    return is_valid_ip(ip)

def is_valid_standortnetz_ip(ip: str) -> bool:
    return any(is_valid_ip(ip, network) for network in CONFIG['valid_ip_ranges']['standortnetz'])

def is_valid_spielstaetten_ip_address(ip: str) -> bool:
    return any(is_valid_ip(ip, network) for network in CONFIG['valid_ip_ranges']['spielstaetten'])

def is_valid_schulungsnetz_ip(ip: str) -> bool:
    return is_valid_ip(ip, CONFIG['valid_ip_ranges']['schulungsnetz'][0])

def is_valid_fortiap_serialnumber(serial_number: str) -> bool:
    return isinstance(serial_number, str) and len(serial_number) > 0

def is_valid_fortiap_license_key(license_key: str) -> bool:
    return isinstance(license_key, str) and len(license_key) > 0

def process_custom_csv(input_file: str, output_file: str) -> None:
    if not check_file_encoding(input_file):
        raise ValueError('The input file is not encoded in UTF-8. Please ensure the file is encoded in utf-8 or utf-8-sig.')

    if not is_semicolon_separated(input_file):
        raise ValueError('The input file is not semicolon-separated. Please ensure ";" is used as the delimiter.')

    df = pd.read_csv(input_file, sep=CONFIG['delimiter'])

    if not all(column in df.columns for column in CONFIG['required_columns']):
        missing_columns = [col for col in CONFIG['required_columns'] if col not in df.columns]
        raise ValueError(f"The following required columns are missing: {', '.join(missing_columns)}")

    df['Rollout Termine'] = df['Rollout Termine'].apply(excel_to_date)
    df = df[df['Rollout Termine'].notna()]
    df = df[(df['Fortinet Serialnumber'].notna()) & (df['Fortinet Serialnumber'] != '-')]

    df.rename(columns={
        'Kunden Host Name': 'Name',
        'DTSec-Loopback': 'var_dtsec_mgmt_loopback',
        'Firewall Host Name': 'var_firewall_hostname',
        'MPLS IP-CE Router': 'var_mpls_gateway_ip',
        'Fortinet Serialnumber': 'Serial Number'
    }, inplace=True)

    df['var_location_address'] = (
        df['PLZ2'].astype(int).astype(str) + ' ' +
        df['Ort2'] + ', ' +
        df['str.'] + ' ' +
        df['Nr'].astype(int).astype(str) +
        df.apply(lambda row: ' ' + str(row['Nr. Zusatz']) if row['Nr. Zusatz'] != "0" else '', axis=1)
    )

    df['Device Blueprint'] = CONFIG['device_blueprint']

    df['var_standortnetz_ip'] = df.apply(
        lambda row: calculate_first_usable_ip(row['Standortnetz Netzwerkadresse'], row['Standortnetz Subnetzmaske']),
        axis=1
    )
    df['var_spielstaetten_ip_address'] = df.apply(
        lambda row: calculate_first_usable_ip(row['Spielstättennetz Netzwerkadresse'], row['Spielstättennetz Subnetzmaske']),
        axis=1
    )
    df['var_schulungsnetz_ip'] = df.apply(
        lambda row: calculate_first_usable_ip(row['Schulungsnetz Netzwerkadresse'], row['Schulungsnetz Subnetzmaske']),
        axis=1
    )

    invalid_rows = []
    error_descriptions = []
    for index, row in df.iterrows():
        errors = []
        if not is_valid_serial_number(row['Serial Number']): errors.append('Invalid Fortinet serial number')
        if not is_valid_device_blueprint(row['Device Blueprint']): errors.append('Invalid device blueprint')
        if not is_valid_name(row['Name']): errors.append('Invalid name')
        if not is_valid_ip(row['var_dtsec_mgmt_loopback'], CONFIG['ip_networks']['dtsec_mgmt_loopback']): errors.append('Invalid mgmt loopback IP')
        if not is_valid_firewall_hostname(row['var_firewall_hostname']): errors.append('Invalid firewall hostname')
        if not is_valid_location_address(row['var_location_address']): errors.append('Invalid address')
        if not is_valid_mpls_gateway_ip(row['var_mpls_gateway_ip']): errors.append('Invalid MPLS gateway IP')
        if not is_valid_standortnetz_ip(row['var_standortnetz_ip']): errors.append('Invalid standortnetz IP')
        if not is_valid_spielstaetten_ip_address(row['var_spielstaetten_ip_address']): errors.append('Invalid spielstaetten IP')
        if not is_valid_schulungsnetz_ip(row['var_schulungsnetz_ip']): errors.append('Invalid schulungsnetz IP')
        if not is_valid_fortiap_serialnumber(row['FortiAP Serialnumber']): errors.append('Invalid FortiAP serial number')
        if not is_valid_fortiap_license_key(row['FortiAP LizenzKey']): errors.append('Invalid FortiAP license key')
        if errors:
            invalid_rows.append(index)
            error_descriptions.append(', '.join(errors))

    # Ergebnis-Ordner anlegen
    result_dir = os.path.dirname(output_file)
    os.makedirs(result_dir, exist_ok=True)

    invalid_df = df.loc[invalid_rows]
    invalid_df.insert(0, 'Exclusion Reason', error_descriptions)
    invalid_df.to_csv(os.path.join(result_dir, "failed.csv"), index=False, sep=CONFIG['delimiter'])

    valid_df = df[~df.index.isin(invalid_rows)][[
        'Serial Number','Device Blueprint','Name','var_dtsec_mgmt_loopback',
        'var_firewall_hostname','var_location_address','var_mpls_gateway_ip',
        'var_standortnetz_ip','var_spielstaetten_ip_address','var_schulungsnetz_ip'
    ]]
    valid_df.to_csv(os.path.join(result_dir, "valid.csv"), index=False, sep=CONFIG['delimiter'])

    additional_df = df[['Rollout Termine','var_firewall_hostname','Serial Number',
                        'FortiAP Serialnumber','FortiAP LizenzKey','Name','var_location_address']].copy()
    additional_df['ap_hostname'] = additional_df['var_firewall_hostname'].apply(lambda x: x.replace('-fw-', '-ap-'))
    additional_df = additional_df[['Rollout Termine','var_firewall_hostname','ap_hostname',
                                   'Serial Number','FortiAP Serialnumber','FortiAP LizenzKey','Name','var_location_address']]
    additional_df.to_csv(os.path.join(result_dir, "additional.csv"), index=False, sep=CONFIG['delimiter'])

# ------------------ GUI ------------------ #
def run_gui():
    def select_input():
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if path: input_entry.delete(0, tk.END); input_entry.insert(0, path)

    def select_output():
        path = filedialog.askdirectory()
        if path: output_entry.delete(0, tk.END); output_entry.insert(0, path)

    def run_process():
        try:
            input_file = input_entry.get()
            output_dir = output_entry.get()
            if not input_file or not output_dir:
                messagebox.showerror("Fehler", "Bitte Eingabedatei und Ausgabeordner auswählen.")
                return
            process_custom_csv(input_file, os.path.join(output_dir, "result.csv"))
            messagebox.showinfo("Erfolg", "Verarbeitung abgeschlossen.\nDie Dateien wurden im Ausgabeordner gespeichert.")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    root = tk.Tk()
    root.title("CSV-Processor")
    tk.Label(root, text="Eingabe CSV:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    input_entry = tk.Entry(root, width=50); input_entry.grid(row=0, column=1, padx=10)
    tk.Button(root, text="Durchsuchen", command=select_input).grid(row=0, column=2, padx=10)

    tk.Label(root, text="Ausgabeordner:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    output_entry = tk.Entry(root, width=50); output_entry.grid(row=1, column=1, padx=10)
    tk.Button(root, text="Durchsuchen", command=select_output).grid(row=1, column=2, padx=10)

    tk.Button(root, text="Verarbeiten", command=run_process, bg="green", fg="white").grid(row=2, column=0, columnspan=3, pady=20)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
