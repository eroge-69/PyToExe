pref = input("Введи префикс:")
fromto = list(map(int, input("Введи от и до (через пробел):").split()))

num_len = len(str(fromto[1]))

for num in range(fromto[0], fromto[1]):
    print("+7" + pref + str(num).zfill(num_len))

