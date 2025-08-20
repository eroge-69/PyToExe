import pyperclip

def wrap_line_preserving_words(line, width=93):
    line = line.rstrip()
    if not line:
        return [""]
    words = line.split()
    result = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + (1 if current_line else 0) <= width:
            if current_line:
                current_line += " "
            current_line += word
        else:
            result.append(current_line.ljust(width))
            current_line = word
    if current_line:
        result.append(current_line.ljust(width))
    return result

print("📂 Programa iniciado!")
print("💬 Cole o texto que deseja formatar (pode ser multilinha).")
print("📌 Quando terminar, digite uma linha vazia e pressione Enter.")
print("✅ O texto formatado será copiado para a área de transferência.")
print("✖ Para sair, digite 'sair'.\n")

while True:
    print("Cole seu texto (ou digite 'sair' para encerrar):")
    linhas_input = []
    while True:
        linha = input()
        if linha.lower() == "sair":
            print("👋 Programa encerrado.")
            exit()
        if linha == "":
            break
        linhas_input.append(linha)

    resultado = []
    for linha in linhas_input:
        resultado.extend(wrap_line_preserving_words(linha, 93))

    texto_formatado = "\n".join(resultado)
    pyperclip.copy(texto_formatado)

    print("\n✅ Texto formatado gerado e copiado para a área de transferência!\n")
    print("Preview (primeiras 5 linhas):")
    preview = "\n".join(resultado[:5])
    print(preview)
    print("\nCole onde quiser usando CTRL+V ou COLAR.\n")
