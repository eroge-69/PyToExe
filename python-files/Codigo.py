import socket
import os

def get_ip():
    """Obtém o IP atual da máquina"""
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return ip

def main():
    ip_atual = get_ip()
    print(f"IP atual: {ip_atual}")

    novo_ip = input("Digite o novo IP (exemplo 192.168.1.100): ")
    mascara = input("Digite a máscara (exemplo 255.255.255.0): ")
    gateway = input("Digite o gateway (exemplo 192.168.1.1): ")

    confirma = input(f"\nConfirma alterar para {novo_ip} (s/n)? ").lower()

    if confirma == "s":
        # Nome da interface - deve ser ajustado conforme o computador
        interface = "Ethernet"

        comando = f'netsh interface ip set address name="{interface}" static {novo_ip} {mascara} {gateway}'
        print(f"\nExecutando comando:\n{comando}\n")

        os.system(comando)
        print("✅ IP alterado com sucesso (se tiver permissões de administrador).")
    else:
        print("Operação cancelada.")

if __name__ == "__main__":
    main()