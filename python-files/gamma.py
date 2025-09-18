# gamma_simulador.py

import time

def alternar_gamma(estado):
    if estado:
        print("Gamma médio ativado")
    else:
        print("Gamma total ativado")
    return not estado

def main():
    estado = False
    print("Simulador de alternância de gamma")
    print("Pressione Enter para alternar, ou digite 'sair' para encerrar")
    while True:
        entrada = input()
        if entrada.lower() == "sair":
            break
        estado = alternar_gamma(estado)
        time.sleep(0.2)  # pequeno delay para visualização

if __name__ == "__main__":
    main()
