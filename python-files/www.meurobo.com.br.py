import time

print('iniciando...')
time.sleep(2)

usuario = input('qual será seu nome de usuario?: ')
print('seja bem vindo(a) ao meurobo,', usuario)
time.sleep(2)

idade = input('antes de continuar, qual é a sua idade?: ')

if int(idade) < 18:
    print('infelizmente você não pode usar o meurobo, pois é menor de idade')
    time.sleep(2)
    print('encerrando...')
    time.sleep(4)
    quit()
else:
    print('você pode usar o meurobo, seja bem vindo(a)!')
    time.sleep(2)
    print('carregando...')
    time.sleep(3)
    print('pronto!')
    time.sleep(2)
    print('Olá,', usuario, 'meu nome é Nicholas, eu sou o desenvolvedor do meurobo')
    time.sleep(2)
    print('eu fiz esse robô para ajudar você a fazer contas simples, como adição, subtração, multiplicação e divisão')
    time.sleep(2)
    print('isso é um prototipo, então pode ser que tenha alguns erros, mas estou sempre tentando melhorar ele')
    time.sleep(2)
    print('você é um dos meus testadores, então se encontrar algum erro, por favor me avise')
    time.sleep(2)
    print('provavelmente, você veio até aqui pelo meu robo que lhe recomendou esse site')
    time.sleep(2)
    print('então, fique a vontade para usar o meurobo,', usuario)
    time.sleep(2)

# Loop principal para fazer várias contas
while True:
    operacao = input('\nqual operação você quer fazer? (adição, subtração, multiplicação, divisão ou sair): ').lower()

    if 'sair' in operacao:
        print('ok, até mais!', usuario)
        break

    # Adição
    elif 'adição' in operacao or '+' in operacao:
        num1 = float(input('primeiro número: '))
        num2 = float(input('segundo número: '))
        resultado = num1 + num2
        print('o resultado de', num1, '+', num2, 'é:', resultado)

    # Subtração
    elif 'subtração' in operacao or '-' in operacao:
        num1 = float(input('primeiro número: '))
        num2 = float(input('segundo número: '))
        resultado = num1 - num2
        print('o resultado de', num1, '-', num2, 'é:', resultado)

    # Multiplicação
    elif 'multiplicação' in operacao or '*' in operacao or 'x' in operacao:
        num1 = float(input('primeiro número: '))
        num2 = float(input('segundo número: '))
        resultado = num1 * num2
        print('o resultado de', num1, '*', num2, 'é:', resultado)

    # Divisão
    elif 'divisão' in operacao or 'dividir' in operacao or '/' in operacao or '÷' in operacao:
        num1 = float(input('primeiro número: '))
        num2 = float(input('segundo número: '))
        if num2 == 0:
            print('erro: divisão por zero não é permitida.')
        else:
            resultado = num1 / num2
            print('o resultado de', num1, '÷', num2, 'é:', resultado)
            if not resultado.is_integer():
                print('Obs: o resultado não é um número inteiro!')

    else:
        print('operação inválida. Por favor, escolha entre adição, subtração, multiplicação, divisão ou sair.')