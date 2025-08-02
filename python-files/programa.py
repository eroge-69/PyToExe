import time
import os
from win10toast import ToastNotifier


toaster = ToastNotifier()
nome = os.getlogin()


def bemvindo():
    print("Olá, seja bem-vindo ao programa teste")
    time.sleep(0.5)
    print("")
    print("Aqui irei fazer perguntas de 'Sim' e 'Não', tem de escrever corretamente")
    p1()


def p1():
    time.sleep(0.5)
    print("")
    p1r = input("Vamos fazer um teste, responda Sim a esta").upper()
    print("")
    time.sleep(0.5)
    if p1r == "SIM":
        print("Certo, vamos continuar")
        p2()
    elif p1r == "NÃO":
        print("Por que você respondeu Não, certo vamos continuar")
        p2()
    else:
        print("Respota inválida")
        p1()


def p2():
    time.sleep(0.5)
    print("")
    print("Agora vamos para um simples questionário")
    time.sleep(0.5)
    print("")
    p2r = input("Você está solteiro?").upper()
    time.sleep(0.5)
    print("")
    if p2r == "SIM":
        print("Fico feliz por você, vamos continuar")
        p3()
    elif p2r == "NÃO":
        print("Ás vezes a solidão é o melhor caminho, vamos continuar")
        p3()
    else:
        print("Resposta inválida")
        p2()


def p3():
    time.sleep(0.5)
    print("")
    p3r = input("Você gosta de sua casa").upper()
    time.sleep(0.5)
    print("")
    if p3r == "SIM":
        print("Uma boa casa é sempre bom")
        p4()
    elif p3r == "NÃO":
        print("Uma casa pequena ou outro problema pode ser desagradavel")
        p4()
    else:
        print("Resposta inválida")
        p3()


def p4():
    time.sleep(0.5)
    print("")
    p4r = input("Você se sente sozinho?").upper()
    time.sleep(0.5)
    print("")
    if p4r == "SIM":
        print("Todos nós nos sentimos sozinho alguma vez")
        p5()
    elif p4r == "NÃO":
        print("Fico feliz por você")
        p5()
    else:
        print("Resposta inválida")
        p4()


def p5():
    time.sleep(0.5)
    print("")
    p5r = input("Você está sozinho?").upper()
    time.sleep(0.5)
    print("")
    if p5r == "SIM":
        print("Você não está")
        os.system("start microsoft.windows.camera:")
        p6()
    elif p5r == "NÃO":
        print("Ainda bem que sabe")
        os.system("start microsoft.windows.camera:")
        p6()
    else:
        print("Resposta inválida")
        p5()


def p6():
    time.sleep(0.5)
    print("")
    print("Vamos fazer um pausa de 20s, relaxe um pouco")
    time.sleep(7.0)
    toaster.show_toast("Aviso", "Dispositivo conectado com sucesso", duration=5)
    time.sleep(13.0)
    print("")
    print(f"Vamos continuar, {nome}")
    p7()


def p7():
    time.sleep(0.5)
    print("")
    p7r = input("Você tem controle no seu PC?").upper()
    if p7r == "SIM":
        print("Você não tem")
        os.system("shutdown /r /t 5")
        final()
    elif p7r == "NÃO":
        print("Ainda bem que sabe")
        final()
    else:
        print("Resposta inválida")
        p7()


def final():
    time.sleep(0.5)
    print("")
    print("Sua experiência chegou ao fim, espere a nova versão do programa")
    time.sleep(0.5)
    print("")
    print(f"Adeus, {nome}")


bemvindo()
