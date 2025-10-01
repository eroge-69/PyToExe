"""Демо-2021. Логическая функция F задаётся выражением (x V y) * ¬(y <=> z) * ¬w.
Дан частично заполненный фрагмент таблицы истинности функции F, содержащий неповторяющиеся строки.
Определите, какому столбцу таблицы истинности функции F соответствует каждая из переменных x, y, z, w.
?	?	?	?	F
1		1		1
0	1		0	1
	1	1	0	1
В ответе напишите буквы x, y, z, w в том порядке, в котором идут соответствующие им столбцы.
Ответ: zyxw     """

# способ 1
print('x y z w')
for x in range(2):
    for y in range(2):
        for z in range(2):
            for w in range(2):
                f = (x or y) and not (y == z) and not w
                if f:
                    print(x, y, z, w)


# способ 2
from itertools import *
print('x y z w')
for x, y, z, w in product((0, 1), repeat=4):
    f = (x or y) and not (y == z) and not w
    if f:
        print(x, y, z, w)


# способ 3
from itertools import *
def f(x, y, w, z):
    return (x or y) and not (y == z) and not w


for a1, a2, a3, a4 in product([0, 1], repeat=4):
    table = [(1, a1, 1, a2), (0, 1, a3, 0), (a4, 1, 1, 0)]
    if len(table) == len(set(table)):
        for p in permutations('xywz'):
            if [f(**dict(zip(p, row))) for row in table] == [1, 1, 1]:
                print(p)
