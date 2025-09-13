# Lista para armazenar os clientes
clientes = []

def menu():
    """Exibe o menu de opções e retorna a escolha do usuário."""
    print("\n--- Sistema de Cadastro de Clientes ---")
    print("[1] - Cadastrar novo cliente")
    print("[2] - Listar todos os clientes")
    print("[3] - Sair do programa")
    
    while True:
        try:
            opcao = int(input("Escolha uma opção: "))
            if 1 <= opcao <= 3:
                return opcao
            else:
                print("Opção inválida. Digite um número entre 1 e 3.")
        except ValueError:
            print("Entrada inválida. Digite um número.")

def cadastrar_cliente():
    """Pede as informações e cadastra um novo cliente."""
    print("\n--- Cadastro de Cliente ---")
    nome = input("Digite o nome do cliente: ")
    email = input("Digite o e-mail: ")
    telefone = input("Digite o telefone: ")
    
    novo_cliente = {
        'nome': nome,
        'email': email,
        'telefone': telefone
    }
    
    clientes.append(novo_cliente)
    print("Cliente cadastrado com sucesso!")

def listar_clientes():
    """Exibe todos os clientes cadastrados."""
    if not clientes:
        print("\nNenhum cliente cadastrado ainda.")
        return
    
    print("\n--- Clientes Cadastrados ---")
    for i, cliente in enumerate(clientes, 1):
        print(f"[{i}]")
        print(f"  Nome: {cliente['nome']}")
        print(f"  E-mail: {cliente['email']}")
        print(f"  Telefone: {cliente['telefone']}")
        print("-" * 20)

def main():
    """Função principal que gerencia o fluxo do programa."""
    while True:
        opcao = menu()
        
        if opcao == 1:
            cadastrar_cliente()
        elif opcao == 2:
            listar_clientes()
        elif opcao == 3:
            print("Saindo do programa. Até mais!")
            break

if __name__ == "__main__":
    main()