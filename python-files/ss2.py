import csv
import ipaddress
from pysnmp.hlapi import (
    getCmd, SnmpEngine, CommunityData, UdpTransportTarget,
    ContextData, ObjectType, ObjectIdentity
)

ip_file = 'iprange.txt'
csv_file = 'relatorio_impressoras.csv'

def load_printers_from_file(file_path):
    ip_list = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.replace('\ufeff', '')  # remove BOM se existir
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if ',' in line:
                    parts = line.split(',')
                    if len(parts) == 2:
                        try:
                            start_ip = ipaddress.IPv4Address(parts[0].strip())
                            end_ip = ipaddress.IPv4Address(parts[1].strip())
                            if start_ip > end_ip:
                                print(f"⚠️ Intervalo inválido: {line}")
                                continue
                            current = start_ip
                            while current <= end_ip:
                                ip_list.append(str(current))
                                current += 1
                        except ValueError:
                            print(f"⚠️ IP inválido: {line}")
                    else:
                        print(f"⚠️ Mais de uma vírgula: {line}")
                else:
                    try:
                        ip = ipaddress.IPv4Address(line)
                        ip_list.append(str(ip))
                    except ValueError:
                        print(f"⚠️ IP inválido: {line}")
    except FileNotFoundError:
        print(f"❌ Ficheiro '{file_path}' não encontrado.")
    return ip_list

def get_snmp_value(ip, oid):
    iterator = getCmd(
        SnmpEngine(),
        CommunityData('public', mpModel=0),
        UdpTransportTarget((ip, 161), timeout=2.0, retries=1),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    )
    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
    if errorIndication or errorStatus:
        return None




    for varBind in varBinds:
        return int(varBind[1])

# Apenas o toner preto
toner_index = 1
toner_label = 'Preto'

page_count_oid = '1.3.6.1.2.1.43.10.2.1.4.1.1'
level_oid_template = f'1.3.6.1.2.1.43.11.1.1.9.1.{toner_index}'
max_oid_template = f'1.3.6.1.2.1.43.11.1.1.8.1.{toner_index}'

printers = load_printers_from_file(ip_file)
header = ['IP', 'Total de Páginas', 'Toner Preto (%)']
linhas_csv = []

for printer in printers:
    print(f'\n📠 Impressora {printer}')
    linha = [printer]

    page_count = get_snmp_value(printer, page_count_oid)
    if page_count is not None:
        print(f'  - Total de páginas: {page_count}')
        linha.append(str(page_count))
    else:
        print(f'  - Total de páginas: Erro ao obter dados')
        linha.append('')

    level = get_snmp_value(printer, level_oid_template)
    max_level = get_snmp_value(printer, max_oid_template)

    if level is not None and max_level:
        percent = int((level / max_level) * 100)
        print(f'  - Toner Preto: {percent}% ({level}/{max_level})')
        linha.append(str(percent))
    else:
        print(f'  - Toner Preto: Não disponível')
        linha.append('')

    linhas_csv.append(linha)

with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(linhas_csv)

print(f'\n✅ Resultados exportados para: {csv_file}')
