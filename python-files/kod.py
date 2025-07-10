import random

wyjscie = {0: 'a', 1: 'b',2: 'c',3: 'd',4: 'e',5: 'f',6: 'g',7: 'h',8: 'i',9: 'j',10: 'k',11: 'l',12: 'm',13: 'n',14: 'o',15: 'p',16: 'r',17: 's',18: 't',19: 'u',20: 'w',21: 'x',22: 'y',23: 'z'}
wejscie = {'a': 0, 'b': 1,'c': 2,'d': 3,'e': 4,'f': 5,'g': 6,'h': 7,'i': 8,'j': 9,'k': 10,'l': 11,'m': 12,'n': 13,'o': 14,'p': 15,'r': 16,'s': 17,'t': 18,'u': 19,'w': 20,'x': 21,'y': 22,'z': 23}


def dodaj_znak(slowo, pozycja, znak):
    return slowo[:pozycja] + znak + slowo[pozycja:]


def dobry_szyfr(haslo):
    k = len(haslo) // 2 - 1
    p_1 = ''
    p_2 = ''
    przes = random.randint(0, 23)
    while 6 > (wejscie[haslo[0]] + przes) % 24 >= 0:
        przes = random.randint(0, 23)
    for i in range(k, -1, -1):
        w = (wejscie[haslo[i]] + przes) % 24
        l = wyjscie[w]
        p_1 += l
    for i in range(len(haslo) - 1, k, -1):
        w = (wejscie[haslo[i]] + przes) % 24
        l = wyjscie[w]
        p_2 += l
    klucz = wyjscie[przes]
    sabot = ''
    wiad = p_1 + klucz + p_2
    fake = random.randint(0, 5)
    if fake:
        sabot += wyjscie[fake]
    for i in range(fake):
        trol = random.randint(0, 23)
        znak = wyjscie[random.randint(0, 23)]
        sabot = dodaj_znak(sabot, 1, wyjscie[trol])
        wiad = dodaj_znak(wiad, trol % len(wiad), znak)
    print(sabot, wiad, fake)
    zaszyfrowane = sabot + wiad
    return zaszyfrowane


if __name__ == '__main__':
    kod = input('Wprowadz hasło do zakodowania:').split(' ')
    wynik = ''
    for i in kod:
        s = dobry_szyfr(i)
        wynik = wynik + s + ' '
    print(f"to twój komunkiat po zakodowaniu: {wynik}")

