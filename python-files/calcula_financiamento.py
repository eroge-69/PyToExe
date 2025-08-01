def calcular_parcelas_com_juros(valor_total, parcelas, taxa_juros):
    saldo_devedor = valor_total
    lista_parcelas = []

    for i in range(parcelas):
        juros = saldo_devedor * (taxa_juros / 100)
        parcela = (saldo_devedor / (parcelas - i)) + juros
        lista_parcelas.append(parcela)
        saldo_devedor -= saldo_devedor / (parcelas - i)

    return lista_parcelas


def calcular_nova_qtd_parcelas(valor_total, taxa_juros, limite_parcela):
    saldo_devedor = valor_total
    parcelas = 1
    while True:
        parcelas += 1
        lista = calcular_parcelas_com_juros(valor_total, parcelas, taxa_juros)
        media = sum(lista) / len(lista)
        if media <= limite_parcela:
            return parcelas, lista


def calcular_novo_credito_rotativo(media_parcela, limite_percentual):
    return media_parcela / limite_percentual


def relatorio(valor_bem, parcelas, taxa_juros, credito_rotativo):
    print("\n--- RELATÓRIO DO FINANCIAMENTO ---")
    limite_parcela = credito_rotativo * 0.35
    lista_parcelas = calcular_parcelas_com_juros(valor_bem, parcelas, taxa_juros)
    media = sum(lista_parcelas) / len(lista_parcelas)

    print(f"\nValor do bem: R$ {valor_bem:,.2f}")
    print(f"Número de parcelas: {parcelas}")
    print(f"Taxa de juros: {taxa_juros:.2f}% ao mês")
    print(f"Crédito rotativo disponível: R$ {credito_rotativo:,.2f}")
    print(f"Limite de parcela (35% do crédito): R$ {limite_parcela:,.2f}")
    print(f"Média das parcelas com juros: R$ {media:,.2f}\n")

    for i, p in enumerate(lista_parcelas, start=1):
        print(f"Parcela {i}: R$ {p:,.2f}")

    if media <= limite_parcela:
        print("\n✅ As parcelas estão dentro do limite permitido.")
    else:
        print("\n❌ As parcelas estão ACIMA do limite permitido.")
        novas_parcelas, nova_lista = calcular_nova_qtd_parcelas(valor_bem, taxa_juros, limite_parcela)
        novo_credito = calcular_novo_credito_rotativo(media, 0.35)

        print(f"\nPara que as parcelas fiquem dentro do limite:")
        print(f"- Número de parcelas deveria ser: {novas_parcelas}")
        print(f"- OU o crédito rotativo deveria ser: R$ {novo_credito:,.2f}")


def main():
    print("=== Simulador de Parcelamento com Juros e Verificação de Crédito ===")
    valor_bem = float(input("Digite o valor do bem financiável (R$): "))
    parcelas = int(input("Digite a quantidade de parcelas: "))
    taxa_juros = float(input("Digite a taxa de juros mensal (%): "))
    credito_rotativo = float(input("Digite o valor do crédito rotativo disponível (R$): "))

    relatorio(valor_bem, parcelas, taxa_juros, credito_rotativo)


if __name__ == "__main__":
    main()

