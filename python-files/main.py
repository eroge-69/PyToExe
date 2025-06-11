import math

def creare_complex(a, b):
    return (a, b)

def modul(z):
    return math.sqrt(z[0] ** 2 + z[1] ** 2)

def este_prim(n):
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def adauga(lista, z):
    lista.append(z)

def insereaza(lista, z, poz):
    lista.insert(poz, z)

def sterge(lista, poz):
    if 0 <= poz < len(lista):
        lista.pop(poz)

def sterge_interval(lista, start, stop):
    if 0 <= start <= stop < len(lista):
        del lista[start:stop+1]

def inlocuieste(lista, vechi, nou):
    for i in range(len(lista)):
        if lista[i] == vechi:
            lista[i] = nou

def parte_imaginara(lista, start, stop):
    if 0 <= start <= stop < len(lista):
        for i in range(start, stop+1):
            print(f"{lista[i]} => imaginar: {lista[i][1]}")

def numere_cu_modul(lista, relatie, valoare):
    for z in lista:
        m = modul(z)
        if (relatie == '<' and m < valoare) or \
           (relatie == '=' and abs(m - valoare) < 1e-5) or \
           (relatie == '>' and m > valoare):
            print(f"{z} (modul: {m:.2f})")

def suma(lista, start, stop):
    if 0 <= start <= stop < len(lista):
        real = sum(lista[i][0] for i in range(start, stop+1))
        imaginar = sum(lista[i][1] for i in range(start, stop+1))
        return (real, imaginar)
    return (0, 0)

def produs(lista, start, stop):
    if start > stop or start < 0 or stop >= len(lista):
        return (0, 0)
    rez = (1, 0)
    for i in range(start, stop+1):
        a, b = rez
        c, d = lista[i]
        rez = (a*c - b*d, a*d + b*c)
    return rez

def sortare_desc_imag(lista):
    lista.sort(key=lambda z: z[1], reverse=True)

def filtrare_prim(lista):
    return [z for z in lista if not este_prim(z[0])]

def filtrare_modul(lista, relatie, val):
    return [z for z in lista if not ((relatie == '<' and modul(z) < val) or
                                     (relatie == '=' and abs(modul(z) - val) < 1e-5) or
                                     (relatie == '>' and modul(z) > val))]

def afisare(lista):
    print("Lista actuală:", [f"{z[0]}+{z[1]}i" for z in lista])

def main():
    lst = []
    istoric = []

    while True:
        print("\n1.Adaugă 2.Inserează 3.Șterge 4.Inlocuiește 5.Imaginar")
        print("6.Modul <,=,> 7.Sumă 8.Produs 9.Sortare imag. 10.Filtrare prim")
        print("11.Filtrare modul 12.Undo 0.Ieșire")

        comanda = input("Comandă: ")
        if comanda == '0':
            break
        elif comanda in {'1', '2'}:
            a, b = int(input("Real: ")), int(input("Imaginar: "))
            if comanda == '1':
                istoric.append(lst[:])
                adauga(lst, creare_complex(a, b))
            else:
                poz = int(input("Poz: "))
                istoric.append(lst[:])
                insereaza(lst, creare_complex(a, b), poz)
        elif comanda == '3':
            tip = input("1:poz, 2:interval: ")
            istoric.append(lst[:])
            if tip == '1':
                sterge(lst, int(input("Poz: ")))
            else:
                sterge_interval(lst, int(input("Start: ")), int(input("Stop: ")))
        elif comanda == '4':
            a1, b1 = int(input("Vechi real: ")), int(input("Vechi imag: "))
            a2, b2 = int(input("Nou real: ")), int(input("Nou imag: "))
            istoric.append(lst[:])
            inlocuieste(lst, (a1, b1), (a2, b2))
        elif comanda == '12' and istoric:
            lst = istoric.pop()
        afisare(lst)

if __name__ == "__main__":
    main()
