import tkinter as tk
from tkinter import messagebox
from ldap3 import Server, Connection, ALL
from datetime import datetime
import csv

# Lista de OUs e arquivos de saída
BASES = {
    "DesktopMan.csv": "OU=Desktops,OU=Computers,OU=MAN-LA,OU=Domain Resources,DC=sa,DC=vwg",
    "LaptopMan.csv": "OU=Laptops,OU=Computers,OU=MAN-LA,OU=Domain Resources,DC=sa,DC=vwg",
    "WorkstationMan.csv": "OU=Workstation,OU=Computers,OU=MAN-LA,OU=Domain Resources,DC=sa,DC=vwg",
    "DesktopVwAnchieta.csv": "OU=Office,OU=Desktops,OU=Computers,OU=ANC,OU=VWBR,OU=Domain Resources,DC=sa,DC=vwg",
    "DesktopVwCuritiba.csv": "OU=Office,OU=Desktops,OU=Computers,OU=CUR,OU=VWBR,OU=Domain Resources,DC=sa,DC=vwg",
    "DesktopVwSaoCarlos.csv": "OU=Office,OU=Desktops,OU=Computers,OU=SCA,OU=VWBR,OU=Domain Resources,DC=sa,DC=vwg",
    "DesktopVwTaubate.csv": "OU=Office,OU=Desktops,OU=Computers,OU=TBT,OU=VWBR,OU=Domain Resources,DC=sa,DC=vwg",
    "DesktopVwVinhedo.csv": "OU=Office,OU=Desktops,OU=Computers,OU=VNH,OU=VWBR,OU=Domain Resources,DC=sa,DC=vwg",
    "LaptopVwAnchieta.csv": "OU=Office,OU=Laptops,OU=Computers,OU=ANC,OU=VWBR,OU=Domain Resources,DC=sa,DC=vwg",
    "LaptopVwCuritiba.csv": "OU=Office,OU=Laptops,OU=Computers,OU=CUR,OU=VWBR,OU=Domain Resources,DC=sa,DC=vwg",
    "LaptopVwSaoCarlos.csv": "OU=Office,OU=Laptops,OU=Computers,OU=SCA,OU=VWBR,OU=Domain Resources,DC=sa,DC=vwg",
    "LaptopVwTaubate.csv": "OU=Office,OU=Laptops,OU=Computers,OU=TBT,OU=VWBR,OU=Domain Resources,DC=sa,DC=vwg",
    "LaptopVwVinhedo.csv": "OU=Office,OU=Laptops,OU=Computers,OU=VNH,OU=VWBR,OU=Domain Resources,DC=sa,DC=vwg",
    "WorkstationVwAnchieta.csv": "OU=Workstation,OU=Computers,OU=ANC,OU=VWBR,OU=Domain Resources,DC=sa,DC=vwg",
    "WorkstationVwCuritiba.csv": "OU=Workstations,OU=Computers,OU=CUR,OU=VWBR,OU=Domain Resources,DC=sa,DC=vwg",
    "WorkstationVwTaubate.csv": "OU=Workstation,OU=Computers,OU=TBT,OU=VWBR,OU=Domain Resources,DC=sa,DC=vwg",
    "DesktopAudi.csv": "OU=Computers,OU=AUDI,OU=Domain Resources,DC=sa,DC=vwg"
}

# Função para converter timestamp do AD
def convert_timestamp(ts):
    if ts:
        return datetime.fromtimestamp(int(ts) / 10**7 - 11644473600).strftime('%Y-%m-%d %H:%M:%S')
    return ''

# Função principal de exportação
def exportar_dados():
    servidor = entry_servidor.get()
    usuario = entry_usuario.get()
    senha = entry_senha.get()

    try:
        server = Server(servidor, get_info=ALL)
        conn = Connection(server, user=usuario, password=senha, auto_bind=True)

        for filename, search_base in BASES.items():
            conn.search(search_base, '(objectClass=computer)', attributes=[
                'name', 'operatingSystem', 'operatingSystemVersion', 'lastLogonTimestamp'
            ])
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Name', 'OperatingSystem', 'OperatingSystemVersion', 'LastLogonDate'])
                for entry in conn.entries:
                    writer.writerow([
                        entry.name.value,
                        entry.operatingSystem.value if entry.operatingSystem else '',
                        entry.operatingSystemVersion.value if entry.operatingSystemVersion else '',
                        convert_timestamp(entry.lastLogonTimestamp.value) if entry.lastLogonTimestamp else ''
                    ])

        conn.unbind()
        messagebox.showinfo("Sucesso", "Exportação concluída com sucesso!")

    except Exception as e:
        messagebox.showerror("Erro", str(e))

# Interface gráfica
root = tk.Tk()
root.title("Exportar Computadores do AD para CSV")

tk.Label(root, text="Servidor LDAP:").grid(row=0, column=0, sticky='e')
entry_servidor = tk.Entry(root, width=50)
entry_servidor.insert(0, "ldap://sa.vwg")
entry_servidor.grid(row=0, column=1)

tk.Label(root, text="Usuário:").grid(row=1, column=0, sticky='e')
entry_usuario = tk.Entry(root, width=50)
entry_usuario.insert(0, "SA\\admin_user")
entry_usuario.grid(row=1, column=1)

tk.Label(root, text="Senha:").grid(row=2, column=0, sticky='e')
entry_senha = tk.Entry(root, show="*", width=50)
entry_senha.grid(row=2, column=1)

tk.Button(root, text="Exportar para CSV", command=exportar_dados).grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()
