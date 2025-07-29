
def main():
    try:
        agua = float(input("Digite o valor da conta de água (R$): "))
        luz = float(input("Digite o valor da conta de luz (R$): "))

        total = agua + luz
        por_pessoa = total / 2
        restante = 500 - por_pessoa

        print(f"\nTotal das contas: R$ {total:.2f}")
        print(f"Valor para cada pessoa: R$ {por_pessoa:.2f}")
        print(f"R$500,00 menos a metade: R$ {restante:.2f}")

    except ValueError:
        print("⚠️ Erro: Digite apenas números válidos!")

if __name__ == "__main__":
    main()
