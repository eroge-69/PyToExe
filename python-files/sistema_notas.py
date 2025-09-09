
def painel_principal(notas):
    print("\n>>> Painel Principal <<<")
    print(f"Total de notas cadastradas: {len(notas)}")
    print("-----------------------------")

def inserir_nota(notas):
    nota = float(input(f"Digite a nota {len(notas)+1}: "))
    notas.append(nota)
    print("Nota inserida com sucesso!")

def relatorio_completo(notas):
    print("\n>>> Relatório Completo <<<")
    if len(notas) == 0:
        print("Nenhuma nota cadastrada.")
    else:
        soma = sum(notas)
        media = soma / len(notas)
        maior = max(notas)
        menor = min(notas)

        print("Notas cadastradas:")
        for i, n in enumerate(notas, start=1):
            print(f"Nota {i}: {n}")

        print("-----------------------------")
        print(f"Média: {media:.2f}")
        print(f"Maior nota: {maior}")
        print(f"Menor nota: {menor}")

def menu():
    notas = []

    while True:
        print("\n=============================")
        print("     SISTEMA DE NOTAS")
        print("     Assistência Social")
        print("=============================")
        print("1 - Painel Principal")
        print("2 - Inserir Nota")
        print("3 - Relatório Completo")
        print("0 - Sair")
        print("=============================")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            painel_principal(notas)
        elif opcao == "2":
            inserir_nota(notas)
        elif opcao == "3":
            relatorio_completo(notas)
        elif opcao == "0":
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    menu()
