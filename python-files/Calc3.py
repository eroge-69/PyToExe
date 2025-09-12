from tabulate import tabulate

print("Введите исходные данные")
H = float(input("Введите напор с учетом потерь в трубопроводе (в метрах) H= ").replace(",", "."))
Q = float(input("Введите расход (в м3/с) Q= ").replace(",", "."))
N = float(input("Введите частоту вращения турбины и генератора (об/мин) N= ").replace(",", "."))
η = float(input("Введите КПД η= ").replace(",", "."))

Z = 0
while True:
    try:
        Z = int(input("Введите кол-во сопел Z= "))
        if Z >= 1 and Z <= 4:
            break
        elif Z == 6:
            break
        else:
            print("Введите целое число из списка [1,2,3,4,6]")
    except ValueError:
        print("Введите целое число из списка [1,2,3,4,6]")

def check_par_КПД(par):
    if 0 <= par <= 1:
        par = par * 100
    return par

η = check_par_КПД(η)

def cacl(par1, par2, par3, par4, par5):
    while True:
        try:
            Cv = float(input("Введите коэф скорости (0.98-0.99) Cv= "))
            if Cv >= 0.98 and Cv <= 0.99:
                break
            else:
                print("Введите коэф скорости из интервала (0.98 - 0.99)")
        except ValueError:
            print("Введите коэф скорости")

    #1. Расчет скорости струи воды v:
    v = Cv * (2 * 9.81 * H)**0.5
    
    #2. Расчет окружной скорости u:
    u = 0.45 * v
    
    #3. Расчет диаметра колеса D:
    D = (60 * u) / (3.14 * N)
    
    #4. Расчет диаметра сопла d:
    d = ((4 * Q) / (3.14 * v * Z))**0.5
    
    #5. Расчет кол-ва ковшей z:
    z = round((15 + D/(2 * d)), 0)
    
    #6. Расчет мощности Р:
    P = (η/100) * 9.81 * Q * H
    
    #7. Соотношение диаметров Р.К. и Сопла
    dc_D1 = d/D
    
    #8. Диаметр струи d0:
    d0 = 0.545 * (Q/(Z * H**0.5))**0.5
    
    #9. Коэф быстроходности ns:
    ns = (1.16 * N * P**0.5) / (H * H**0.25)
    
    return v, u, D, d, z, P, dc_D1, d0, ns

res = cacl(H, Q, N, η, Z)

# Оформление
data = [
    ['Исходные данные:'],
    ['Наименование', 'Значение', 'Единица измерения'],
    ['Напор Н', H, 'м'],
    ['Расход Q', Q, 'м3/с'],
    ['Cкорость вращения N', N, 'об/мин'],
    ['КПД η', η, '%'],
    ['Кол-во сопел Z', Z, 'шт']
]

data_header1 = data[0]
data_header2 = data[1]
data_value = data[2:]

print("Представление исходных данных в виде таблицы")
print(data_header1[0])

table1 = tabulate(data_value,
                  headers=data_header2,
                  tablefmt='rst',
                  colalign=('center', 'center', 'center'))

print(table1)

data_res = [
    ['Результаты расчета:'],
    ['Наименование', 'Значение', 'Единица измерения'],
    ['Скорость струи воды на выходе из сопла υ', round(res[0], 2), 'м/c'],
    ['Окружная скорость u', round(res[1], 2), 'м/с'],
    ['Диаметр колеса D', round(res[2] * 100, 2), 'см'],  # Перевод в см
    ['Диаметр сопла d', round(res[3] * 1000, 2), 'мм'],  # Исправлена единица измерения
    ['Кол-во ковшей z', int(res[4]), 'шт'],  # int вместо round для целого числа
    ['Мощность P', round(res[5], 2), 'кВт'],
    ['Соотношение диаметров Р.К. и сопла dc/D1', round(res[6], 2), '-'],
    ['Диаметр струи d0', round(res[7] * 1000, 2), 'мм'],  # Перевод в мм
    ['Коэффициент быстроходности ns', round(res[8], 2), '-']
]

data_header_res1 = data_res[0]
data_header_res2 = data_res[1]
data_value_res = data_res[2:]

print("Формирование результатов расчета в таблицу")
print(data_header_res1[0])

table2 = tabulate(data_value_res,
                  headers=data_header_res2,
                  tablefmt='rst',
                  colalign=('left', 'center', 'center'))
print(table2)

