# gamma_test.py
estado = False

def alternar_gamma():
    global estado
    if estado:
        print("Gamma médio ativado")
    else:
        print("Gamma total ativado")
    estado = not estado

# loop simples de teste
while True:
    entrada = input("Digite Enter para alternar gamma (ou 'sair' para fechar): ")
    if entrada.lower() == "sair":
        break
    alternar_gamma()

