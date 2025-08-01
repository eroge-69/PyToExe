import tkinter as tk
from tkinter import ttk, messagebox

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
    parcelas = 1
    while True:
        parcelas += 1
        lista = calcular_parcelas_com_juros(valor_total, parcelas, taxa_juros)
        media = sum(lista) / len(lista)
        if media <= limite_parcela:
            return parcelas, lista


def calcular_novo_credito_rotativo(media_parcela, limite_percentual):
    return media_parcela / limite_percentual


def gerar_relatorio():
    try:
        valor_bem = float(entry_valor_bem.get())
        parcelas = int(entry_parcelas.get())
        taxa_juros = float(entry_juros.get())
        credito_rotativo = float(entry_credito.get())

        limite_parcela = credito_rotativo * 0.35
        lista_parcelas = calcular_parcelas_com_juros(valor_bem, parcelas, taxa_juros)
        media = sum(lista_parcelas) / len(lista_parcelas)

        relatorio = "\n--- RELATÓRIO DO FINANCIAMENTO ---\n"
        relatorio += f"\nValor do bem: R$ {valor_bem:,.2f}"
        relatorio += f"\nNúmero de parcelas: {parcelas}"
        relatorio += f"\nTaxa de juros: {taxa_juros:.2f}% ao mês"
        relatorio += f"\nCrédito rotativo disponível: R$ {credito_rotativo:,.2f}"
        relatorio += f"\nLimite de parcela (35% do crédito): R$ {limite_parcela:,.2f}"
        relatorio += f"\nMédia das parcelas com juros: R$ {media:,.2f}\n"

        for i, p in enumerate(lista_parcelas, start=1):
            relatorio += f"Parcela {i}: R$ {p:,.2f}\n"

        if media <= limite_parcela:
            relatorio += "\n✅ As parcelas estão dentro do limite permitido."
        else:
            relatorio += "\n❌ As parcelas estão ACIMA do limite permitido.\n"
            novas_parcelas, _ = calcular_nova_qtd_parcelas(valor_bem, taxa_juros, limite_parcela)
            novo_credito = calcular_novo_credito_rotativo(media, 0.35)
            relatorio += f"\nPara que as parcelas fiquem dentro do limite:"
            relatorio += f"\n- Número de parcelas ideal: {novas_parcelas}"
            relatorio += f"\n- OU o crédito rotativo deveria ser: R$ {novo_credito:,.2f}"

        text_output.delete(1.0, tk.END)
        text_output.insert(tk.END, relatorio)

    except ValueError:
        messagebox.showerror("Erro", "Por favor, preencha todos os campos corretamente.")


# Criar janela principal
root = tk.Tk()
root.title("Simulador de Financiamento")
root.geometry("650x600")

# Frame de entrada
frame_inputs = tk.Frame(root)
frame_inputs.pack(pady=10)

tk.Label(frame_inputs, text="Valor do bem (R$):").grid(row=0, column=0, sticky="e")
entry_valor_bem = tk.Entry(frame_inputs)
entry_valor_bem.grid(row=0, column=1, padx=10)

tk.Label(frame_inputs, text="Quantidade de parcelas:").grid(row=1, column=0, sticky="e")
entry_parcelas = tk.Entry(frame_inputs)
entry_parcelas.grid(row=1, column=1, padx=10)

tk.Label(frame_inputs, text="Taxa de juros mensal (%):").grid(row=2, column=0, sticky="e")
entry_juros = tk.Entry(frame_inputs)
entry_juros.grid(row=2, column=1, padx=10)

tk.Label(frame_inputs, text="Crédito rotativo (R$):").grid(row=3, column=0, sticky="e")
entry_credito = tk.Entry(frame_inputs)
entry_credito.grid(row=3, column=1, padx=10)

# Botão
btn_calcular = tk.Button(root, text="Simular Financiamento", command=gerar_relatorio)
btn_calcular.pack(pady=10)

# Área de texto para saída
frame_output = tk.Frame(root)
frame_output.pack(fill="both", expand=True, padx=10, pady=10)

text_output = tk.Text(frame_output, wrap="word", height=20)
text_output.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(frame_output, command=text_output.yview)
scrollbar.pack(side="right", fill="y")
text_output.config(yscrollcommand=scrollbar.set)

# Iniciar GUI
root.mainloop()
