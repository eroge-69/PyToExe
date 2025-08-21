def gerar_relatorio():
    # Entradas do usuário
    lote_numero = int(input("Número do lote: "))
    empresa = input("Nome da empresa vencedora: ")
    produto_id = int(input("ID do produto: "))
    produto_nome = input("Nome do produto: ")
    valor_ofertado = float(input("Valor ofertado pelo vencedor (R$): "))
    valor_previa = float(input("Menor valor da prévia (R$): "))
    empresa_previa = input("Empresa da prévia: ")
    classificacao = int(input("Classificação da empresa da prévia na disputa (0 se não participou): "))
    valor_previa_final = float(input("Valor ofertado pela empresa da prévia na disputa (R$, se não participou, digite 0): "))
    desconto = float(input("Valor do desconto concedido (R$): "))
    quantidade = int(input("Quantidade de itens: "))

    # Valor final é calculado automaticamente
    valor_final = valor_ofertado - desconto

    # Se quantidade > 1, calcula abatimento total
    if quantidade > 1:
        abatimento_total = desconto * quantidade
        texto_abatimento = f" O abatimento total foi de R$ {abatimento_total:,.2f}."
    else:
        texto_abatimento = ""

    # Texto da classificação da empresa prévia
    if classificacao == 0:
        texto_classificacao = f"{empresa_previa}, convidada para a disputa, não apresentou proposta."
    else:
        texto_classificacao = (
            f"{empresa_previa}, que participou da disputa e ocupa a {classificacao}ª colocação "
            f"com o valor de R$ {valor_previa_final:,.2f}."
        )

    # Relatório formatado
    relatorio = f"""
LOTE {lote_numero:02d} - {empresa}
ID {produto_id} - {produto_nome} - valor ofertado R$ {valor_final:,.2f}
O menor preço obtido na cotação prévia foi de R$ {valor_previa:,.2f}, da empresa {texto_classificacao}
Em negociação, o fornecedor concedeu R$ {desconto:,.2f} de desconto, passando o valor de R$ {valor_ofertado:,.2f} para R$ {valor_final:,.2f}.{texto_abatimento}
""".strip()

    print("\n=== RELATÓRIO GERADO ===")
    print(relatorio)


# Executa a função
gerar_relatorio()
