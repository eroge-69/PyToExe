a='АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
p=[a[i:i+2] for i in range(0,32,2)]
def n(l):return next(i for i,g in enumerate(p)if l in g)
def e():
 t=input('Текст: ').upper().replace('Ё','Е')
 k=[n(x)for x in'КОФЕ']*(len(t)//4+1)
 r=''.join(p[(n(c)+k[i])%16][::(-1)**(c in p[n(c)][1])]for i,c in enumerate(t))
 print('Шифр:',r)
def d():
 t=input('Шифр: ').upper().replace('Ё','Е')
 k=[n(x)for x in'КОФЕ']*(len(t)//4+1)
 r=''.join(p[(n(c)-k[i])%16][::(-1)**(c in p[n(c)][1])]for i,c in enumerate(t))
 print('Текст:',r)
while True:o=input('1-Шифровать 2-Расшифровать: ');[None,e,d][int(o)]()