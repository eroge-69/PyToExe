import os
import subprocess
import shutil

# Mapeamento das lojas: chave -> (nome, terceiro_octeto_da_rede)
LOJAS = {
    1: ("LOJA 01 REPUBLICA", 3),
    2: ("LOJA 02 TIRADENTES", 4),
    3: ("LOJA 03 RIO BRANCO", 6),
    4: ("LOJA 04 CAMPOLIM", 8),
    5: ("LOJA 05 ITAVUVU", 11),
    6: ("LOJA 06 OZANAN", 13),
    7: ("LOJA 07 DUQUE", 17),
    8: ("LOJA 08 GENERAL", 19),
    9: ("LOJA 09 COLINAS", 21),
    10: ("LOJA 10 DOM PEDRO", 23),
    11: ("LOJA 11 TAUBATÉ", 27),
}

DEFAULT_VNC_PATHS = [
    r"C:\Program Files (x86)\UltraVNC\vncviewer.exe",
    r"C:\Program Files\UltraVNC\vncviewer.exe",
]

VNC_PASSWORD = "econect"


def find_vncviewer():
    for p in DEFAULT_VNC_PATHS:
        if os.path.exists(p):
            return p
    exe = shutil.which("vncviewer")
    if exe:
        return exe
    return None


def mostrar_menu():
    print("=== Menu de Lojas ===")
    for k in sorted(LOJAS.keys()):
        nome, rede = LOJAS[k]
        print(f"{k:2d}. {nome} (rede: 192.168.{rede}.x)")
    print(" 0. Sair")
    print("=====================")


def ler_inteiro(prompt, minimo=None, maximo=None):
    while True:
        try:
            s = input(prompt).strip()
            if s == "":
                print("Entrada vazia — tente novamente.")
                continue
            v = int(s)
            if minimo is not None and v < minimo:
                print(f"Valor deve ser >= {minimo}.")
                continue
            if maximo is not None and v > maximo:
                print(f"Valor deve ser <= {maximo}.")
                continue
            return v
        except ValueError:
            print("Digite um número inteiro válido.")


def main():
    vnc_path = find_vncviewer()
    if vnc_path:
        print(f"vncviewer encontrado em: {vnc_path}")
    else:
        print("⚠ vncviewer não encontrado automaticamente.")

    while True:
        mostrar_menu()
        loja = ler_inteiro("Escolha a loja (número): ", minimo=0, maximo=max(LOJAS.keys()))
        if loja == 0:
            print("Saindo.")
            break
        if loja not in LOJAS:
            print("Loja inválida. Tente novamente.")
            continue

        nome_loja, rede = LOJAS[loja]
        pdv = ler_inteiro("Digite o NUMERO do PDV (ex: 1): ", minimo=1, maximo=250)

        # Regras diferentes para cálculo do IP
        if loja == 2:  # LOJA 02 - TIRADENTES
            ip_final = 10 + pdv
        else:
            ip_final = 200 + pdv

        ip = f"192.168.{rede}.{ip_final}"
        print(f"\nConectando ao PDV {pdv} - {nome_loja} -> IP: {ip}")

        args = [vnc_path or "vncviewer", ip, "/viewonly", "/password", VNC_PASSWORD, "/autoscaling"]

        if vnc_path and os.path.exists(vnc_path):
            subprocess.Popen(args, close_fds=True)
            print("✅ VNC aberto.")
        else:
            print("⚠ vncviewer não disponível. Comando que seria executado:")
            print(" ".join(args))

        repetir = input("\nDeseja fazer outro acesso? (S/n): ").strip().lower()
        if repetir == "n":
            print("Finalizando.")
            break


if __name__ == "__main__":
    main()
