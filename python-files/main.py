def calcular_valor_total():
    while True:
        try:
            num_parcelas = int(input("Quantas parcelas serão? "))
            if num_parcelas > 0:
                break
            else:
                print("Por favor, insira um número maior que zero.")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número inteiro.")

    dados_calculo = []

    print("\n--- Inserção de Dados ---")
    for i in range(num_parcelas):
        print(f"\nColetando dados para a Parcela {i + 1} de {num_parcelas}:")
        
        while True:
            try:
                saldo_devedor_str = input("Insira o saldo devedor (use vírgula para centavos): ")
                saldo_devedor = float(saldo_devedor_str.replace(',', '.'))
                break
            except ValueError:
                print("Erro. Por favor, insira um número (ex: 1500,50).")

        while True:
            try:
                valor_parcela_str = input("Insira o valor da parcela (use vírgula para centavos): ")
                valor_parcela = float(valor_parcela_str.replace(',', '.'))
                dados_calculo.append({'saldo': saldo_devedor, 'parcela': valor_parcela})
                break
            except ValueError:
                print("Valor inválido. Por favor, insira um número (ex: 350,25).")

    print("\n--- Seleção do Coeficiente ---")
    opcoes_coeficiente = {"1": 0.0274, "2": 0.0254, "3": 0.0231}
    
    while True:
        print("Qual o coeficiente?")
        print("Opções disponíveis:")
        print("  1) 0,0274")
        print("  2) 0,0254")
        print("  3) 0,0231")
        
        escolha = input("Digite o número da opção desejada (1, 2 ou 3): ")
        
        if escolha in opcoes_coeficiente:
            coeficiente = opcoes_coeficiente[escolha]
            print(f"Coeficiente {coeficiente} selecionado.")
            break
        else:
            print("\nOpção inválida. Por favor, escolha uma das opções listadas.\n")

    valor_total = 0
    for dados in dados_calculo:
        resultado_parcela = (dados['parcela'] / coeficiente) - dados['saldo']
        valor_total += resultado_parcela

    resultado_formatado = f"{valor_total:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
    print("\n---------------------------------")
    print(f"O VALOR TOTAL LIBERADO É: R$ {resultado_formatado}")
    print("---------------------------------")


if __name__ == "__main__":
    calcular_valor_total()