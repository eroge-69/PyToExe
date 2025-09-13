import subprocess
import ctypes
import sys
import os

def is_admin():
    """Verifica se o script está rodando com privilégios de administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_command(command):
    """Executa um comando no shell e imprime o resultado."""
    try:
        print(f"Executando: {' '.join(command)}")
        result = subprocess.run(command, check=True, capture_output=True, text=True, shell=True)
        print("Sucesso!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Ocorreu um erro:")
        print(e.stderr)

def create_dangerous_rules():
    """Cria as regras de firewall para permitir TODO o tráfego."""
    print("\n--- [AVISO] CRIANDO REGRAS PERIGOSAS QUE ABREM TODO O FIREWALL ---")
    
    rules = {
        "AllowAll_TCP_IN_Script": 'netsh advfirewall firewall add rule name="AllowAll_TCP_IN_Script" dir=in action=allow protocol=TCP localport=any',
        "AllowAll_UDP_IN_Script": 'netsh advfirewall firewall add rule name="AllowAll_UDP_IN_Script" dir=in action=allow protocol=UDP localport=any',
        "AllowAll_TCP_OUT_Script": 'netsh advfirewall firewall add rule name="AllowAll_TCP_OUT_Script" dir=out action=allow protocol=TCP localport=any',
        "AllowAll_UDP_OUT_Script": 'netsh advfirewall firewall add rule name="AllowAll_UDP_OUT_Script" dir=out action=allow protocol=UDP localport=any'
    }
    
    for rule_name, command_str in rules.items():
        run_command(command_str.split())
        
    print("\n--- [CONCLUÍDO] O FIREWALL FOI CONFIGURADO PARA PERMITIR TUDO. SEU PC ESTÁ EXPOSTO. ---")


def remove_dangerous_rules():
    """Remove as regras de firewall criadas por este script."""
    print("\n--- RESTAURANDO SEGURANÇA: REMOVENDO REGRAS PERIGOSAS ---")
    
    rule_names = [
        "AllowAll_TCP_IN_Script",
        "AllowAll_UDP_IN_Script",
        "AllowAll_TCP_OUT_Script",
        "AllowAll_UDP_OUT_Script"
    ]
    
    for name in rule_names:
        command_str = f'netsh advfirewall firewall delete rule name="{name}"'
        run_command(command_str.split())
        
    print("\n--- [CONCLUÍDO] REGRAS DO SCRIPT REMOVIDAS. VERIFIQUE SUAS CONFIGURAÇÕES DE FIREWALL. ---")


def main():
    if not is_admin():
        print("ERRO: Este script precisa ser executado como Administrador.")
        print("Por favor, clique com o botão direito e selecione 'Executar como administrador'.")
        # Pausa para o usuário poder ler a mensagem antes de fechar
        os.system("pause")
        sys.exit(1)

    while True:
        print("\n" + "="*50)
        print("   GERENCIADOR DE REGRAS DE FIREWALL (PERIGOSO)")
        print("="*50)
        print("\nATENÇÃO: As opções abaixo alteram drasticamente a segurança do seu computador.")
        print("1. CRIAR Regras 'Tudo Liberado' (MUITO PERIGOSO)")
        print("2. REMOVER Regras 'Tudo Liberado' criadas por este script")
        print("3. Sair")
        
        choice = input("\nEscolha uma opção: ")
        
        if choice == '1':
            confirm = input("Você tem CERTEZA de que quer abrir seu firewall completamente? Isso é muito arriscado. (s/n): ").lower()
            if confirm == 's':
                create_dangerous_rules()
            else:
                print("Operação cancelada.")
        elif choice == '2':
            remove_dangerous_rules()
        elif choice == '3':
            print("Saindo.")
            break
        else:
            print("Opção inválida. Tente novamente.")
        
        os.system("pause") # Pausa após cada operação

if __name__ == "__main__":
    main()
