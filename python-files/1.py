from decimal import Decimal, getcontext

def calcular_pi(precisao):
    # Configura a precisão com alguns dígitos extras pra evitar erro de arredondamento
    getcontext().prec = precisao + 5  
    
    # Fórmula de Gauss-Legendre
    a = Decimal(1)
    b = Decimal(1) / Decimal(2).sqrt()
    t = Decimal(1) / Decimal(4)
    p = Decimal(1)

    for _ in range(precisao):
        an = (a + b) / 2
        b = (a * b).sqrt()
        t -= p * (a - an) ** 2
        a = an
        p *= 2

    pi = (a + b) ** 2 / (4 * t)
    return str(pi)[:precisao+2]  # +2 pra incluir "3."

if __name__ == "__main__":
    n = int(input("Digite a quantidade de casas decimais de π que deseja calcular: "))
    resultado = calcular_pi(n)
    print(f"\nπ com {n} casas decimais:\n{resultado}")
