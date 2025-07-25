
from faker import Faker
import random

def gerar_cpf():
    def calcular_digito(digs):
        s = sum([int(digs[i]) * (len(digs)+1-i) for i in range(len(digs))])
        d = 11 - s % 11
        return '0' if d >= 10 else str(d)

    nove_digitos = ''.join([str(random.randint(0, 9)) for _ in range(9)])
    d1 = calcular_digito(nove_digitos)
    d2 = calcular_digito(nove_digitos + d1)
    cpf = f"{nove_digitos[:3]}.{nove_digitos[3:6]}.{nove_digitos[6:9]}-{d1}{d2}"
    return cpf

def gerar_nome():
    faker = Faker('pt_BR')
    return faker.name()

def main():
    print("\n🔷🔷 LXZ METAS 🔷🔷\n")
    while True:
        nome = gerar_nome()
        cpf = gerar_cpf()
        print(f"Nome: {nome}")
        print(f"CPF:  {cpf}")
        print("-" * 30)
        cont = input("Gerar outro? (s/n): ").lower()
        if cont != 's':
            break
        print()

if __name__ == "__main__":
    main()
