import numpy as np
import math
import sys
import os
#Метод половинного деления
def half_divide_method(a, b,px ,n):
    x = (a + b) / 2
    while math.fabs(func(px,n,x)) >= e:
        x = (a + b) / 2
        a, b = (a, x) if func(px,n,a) * func(px,n,x) < 0 else (x, b)
    return (a + b) / 2
#Метод ньютона 
def OMEGANEWTON9000(px,a,b,n,n2):
    xn=[]
    for i in range(n2-1):
        xleft=a+(b-a)*(i/n2)
        xright=a+(b-a)*((i+1)/n2)
       
        if func(px,n,xleft)*func(px,n,xright)<0:
            x=(xleft+xright)/2
            xn.append(half_divide_method(xleft, xright,px ,n))
           
    return xn
def func(f,n,x):
    z=0
    for i in range(n+1):
        z=(-f[i])*(x**(n-i))+z
    return z
def funcp(f,n,x):
    z=0
    for i in range(n):
        z=(n-i)*(-f[i])*(x**(n-i-1))+z
      
    return z

e = 0.001
#n = int(input('Введите размерность матрицы\n'))
#n=4
#Проверка размера матрицы
try:
    with open('matrix.txt','r')as f:
       checksize =f.readline().split()
    n=len(checksize)
except BaseException:
    print("Отсутствует файл")
    os.system("pause")
    sys.exit(0)

try:
    a = np.loadtxt("matrix.txt", usecols=range(0,n), dtype=np.double)# считываем матрицу с файла
    y=[1]
    a=a.reshape(-1,n)
except BaseException:
    print('Матрица введена не корректно')
    os.system("pause")
    sys.exit(0)
    #os.system("pause")
print ( "Размер заданной матрицы:",n)
print("Заданная матрица:\n",a)
#Проверка на симметричность
a2=np.array(a)
a2=a2.reshape(-1,n)
a2=a2.transpose()
for i in range(n):
    for j in range(n):
        if a[i][j]!=a2[i][j]:
            print("Матрица не симметрична!")
            f=input()
            sys.exit(0)
#поиск левого и правого конца отрезка
puk=[]
puk2=[]
for i in range(n):
    puk.append(a[i][0])
f=0
for i in range(n):
    for j in range(1,n):
        f+=math.fabs(a[i][j])
    puk2.append(f)
    f=0
min=puk[0]-puk2[0]
max=puk[0]+puk2[0]
for i in range(n):
    if puk[i]-puk2[i] <min:
        min=puk[i]-puk2[i]
    if puk[i]+puk2[i] >max:
         max=puk[i]+puk2[i]
for i in range(n-1):
    y.append(0) 
firstVector=np.array(y)#нулевой вектор
#левая часть системы
x=np.vstack(firstVector).reshape(1,n)
for i in range(1,n):   
    x=np.vstack((x,np.dot(a,firstVector)))
    firstVector=x[i]
#правая часть системы
y=np.dot(a,firstVector)
x=x.transpose()
px = np.linalg.solve(x, y)#решение системы уравнений
px=np.append(px,-1)
px=np.flip(px)
px2=np.delete(px,0)
print("Результат решения системы уравнений \n",px2)
print("Собственные числа:")
print(OMEGANEWTON9000(px,min,max,n,100))#вызов метода ньютона и запись его результата в переменную xx
xx=OMEGANEWTON9000(px,min,max,n,100)
q=[1]
vectors=[]
qtofile=[[1] * n for i in range(n)]
for j in range(n):
    for i in range(1,n):
      q.append(xx[j]*q[i-1]-px[i])
      qtofile[j][i]=xx[j]*q[i-1]-px[i]
    y=q[0]*x[0:n,n-1]
    for i in range(1,n):
      y+=q[i]*x[0:n,n-i-1]
    q=[1]
    for i in range(n):
        vectors.append(y[i])
normi=[]
s=0
vectors2 = np.array(vectors)
vectors2=vectors2.reshape((-1, n))
ownVectors=vectors2
for i in range(n):
    for j in range(n):
       s+=vectors2[i][j]**2
    normi.append(math.sqrt(s))
    s=0
print('Нормированные собственные векторы:')
vectors3 = np.copy(vectors2)
for i in range(n):
    print(vectors2[i,0:n]/normi[i])
    vectors3[i,0:n]=vectors2[i,0:n]/normi[i]
#Запись всего в файл
mintofile = str(round(min,4))
maxtofile = str(round(max,4))
ntofile=str(n)
y=y.reshape(n,1)
x=np.hstack((x,y))
for i in range(len(xx)):#округление собственных числе для красоты до 4 знаков после запятой
    xx[i]=round(xx[i],4)
xxtofile=' '.join([str(item)for item in xx])
mainqtofile=np.array(qtofile)
with open("result.txt", "w") as file:
    file.write('Размер матрицы:'+ntofile+'\n')
    np.savetxt(file, x,fmt='%.4f', delimiter=', ',header='Система p:')
    np.savetxt(file, px2.reshape(1,n),fmt='%.4f', delimiter=', ',header='Решение системы p:')
    file.write('Собственные числа:\n'+xxtofile+'\n')
    np.savetxt(file, vectors3.transpose(),fmt='%.4f', delimiter=', ',header='Нормированные собственные векторы:')
print("Результат работы программы содержится в файле result.txt")
os.system("pause")
