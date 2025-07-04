# -*- coding: utf-8 -*-
import datetime

def main():
    print("=" * 50)
    print("ПРОГРАММА РАСЧЕТА ПУТЕВОГО ЛИСТА ТАНКА Т-90М")
    print("=" * 50 + "\n")

    # Ввод данных
    маршрут = input("Маршрут следования (откуда-куда): ")
    расстояние = float(input("Планируемое расстояние (км): "))
    скорость = float(input("Средняя скорость (км/ч): "))
    время_движ = расстояние / скорость
    время_простой = float(input("Время простоя с работающим двигателем (ч): "))
    
    # Топливные параметры Т-90М
    РАСХОД_ДВИЖ = 4.8  # л/км
    РАСХОД_ХОЛОСТОЙ = 12.0  # л/ч
    БАК_ОБЩИЙ = 1200  # л

    # Расчеты
    расход_движение = расстояние * РАСХОД_ДВИЖ
    расход_простой = время_простой * РАСХОД_ХОЛОСТОЙ
    общий_расход = расход_движение + расход_простой

    # Ввод данных о топливе
    топливо_нач = float(input(f"\nНачальное топливо (макс. {БАК_ОБЩИЙ} л): "))
    заправка = float(input("Заправлено в пути (л): "))
    топливо_кон = топливо_нач + заправка - общий_расход

    # Проверки
    if топливо_нач > БАК_ОБЩИЙ:
        print("\n! ОШИБКА: Начальное топливо превышает ёмкость баков")
        return
        
    if топливо_кон < 0:
        print("\n! ТРЕВОГА: Недостаточно топлива для выполнения маршрута")
        топливо_кон = 0

    # Генерация отчета
    дата = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    
    отчет = f"""
{'='*50}
ПУТЕВОЙ ЛИСТ ТАНКА Т-90М
{'='*50}
Дата формирования: {дата}
Маршрут: {маршрут}
Дальность: {расстояние:.1f} км
Время в движении: {время_движ:.1f} ч
Простой с работой двигателя: {время_простой:.1f} ч

РАСХОД ТОПЛИВА:
- На движение ({расстояние:.1f} км × {РАСХОД_ДВИЖ} л/км) = {расход_движение:.1f} л
- На холостом ходу ({время_простой:.1f} ч × {РАСХОД_ХОЛОСТОЙ} л/ч) = {расход_простой:.1f} л
ОБЩИЙ РАСХОД: {общий_расход:.1f} л

ТОПЛИВНЫЙ БАЛАНС:
+ Начальный остаток: {топливо_нач:.1f} л
+ Заправлено в пути: {заправка:.1f} л
- Расход по маршруту: {общий_расход:.1f} л
= Конечный остаток: {топливо_кон:.1f} л

Механик-водитель: _______________
Командир машины: _______________
{'='*50}
"""
    print(отчет)
    
    # Сохранение в файл
    с_сохранением = input("Сохранить в файл? (д/н): ").lower()
    if с_сохранением == 'д':
        имя_файла = f"Путевой_лист_Т90М_{дата.replace(' ','_').replace(':','-')}.txt"
        with open(имя_файла, 'w', encoding='utf-8') as f:
            f.write(отчет)
        print(f"Файл сохранен: {имя_файла}")

if __name__ == "__main__":
    main()