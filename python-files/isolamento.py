print("Esse programa calcula a distância para isolamento.")
while True:
    altura = float(input("Digite a altura: "))
    largura = float(input("Digite a largura: "))


    #severidade
    carga_incendio = float(input("Digite a carga de incêndio(NT04): "))
    if(carga_incendio <= 680):
        severidade = "I"
    elif(680 < carga_incendio <= 1460):
        severidade = "II"
    else:
        severidade = "III"

    #porcentagem de abertura fachada
    area_fachada = altura * largura
    area_abertura = float(input("Digite a área de abertura: "))
    porcentagem_abertura = (area_abertura / area_fachada) * 100

    #encontrar o a
    if(altura > largura):
        x = altura / largura
    elif(largura > altura):
        x = largura / altura
    else:
        print("os valores são iguais.")

    print("=" * 50)
    print(f"X = {x}")
    print(f"Severidade = {severidade}")
    print(f"Porcentagem de abertura = {porcentagem_abertura}%")
    print("Consulte na tabela 3 da NT 08.")
    a = float(input("Digite o valor de a: "))
    print("=" * 50)

    #encontrar o b
    while True:
        bombeiros = input("Há bombeiros na cidade?(S/N): ")
        if(bombeiros == "S") or (bombeiros == "s"):
            b = 1.5
            break
        elif(bombeiros == "N") or (bombeiros == "n"):
            b = 3
            break
        else:
            print("entrada incorreta.")

    #calcula a distância
    if(largura > altura):
        d = (a * altura) + b
    else:
        d = (a * largura) + b

    print("="*50)
    print(f"D = {d}m")
    print("="*50)
    continuar = input("Deseja calcular outra distância?(s/n): ")
    if(continuar == "n") or (continuar == "N"):
        break





