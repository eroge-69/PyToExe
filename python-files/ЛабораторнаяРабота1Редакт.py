import tkinter as tk
from tkinter import messagebox


def form1() -> None:
    var = int(variant_entry.get())
    if var not in range(1, 21):
        messagebox.showerror('Ошибка', 'Неверный вариант\nВыберите от 1 до 20')
    else:
        try:
            n1 = float(str(entry1.get()).replace(',', '.'))
            n2 = float(str(entry2.get()).replace(',', '.'))
    
            if var == 1: # Вычислить сумму и произведение этих чисел, и вывести эти значения на экран
                res1 = n1 + n2
                res2 = n1 * n2
                res1_text = f'Сумма: {res1:.5f}'
                res2_text = f'Произведение: {res2:.5f}'
    
            elif var == 2: # Вычислить сумму этих чисел и сумму их квадратов, и вывести эти значения на экран
                res1 = n1 + n2
                res2 = n1 ** 2 + n2 ** 2
                res1_text = f'Сумма: {res1:.5f}'
                res2_text = f'Сумма квадратов: {res2:.5f}'
    
            elif var == 3: # Вычислить квадрат и куб суммы этих чисел и вывести эти значения на экран
                sum_val = n1 + n2
                res1 = sum_val ** 2
                res2 = sum_val ** 3
                res1_text = f'Квадрат суммы: {res1:.5f}'
                res2_text = f'Куб суммы: {res2:.5f}'
    
            elif var == 4: # Вычислить сумму квадратных корней этих чисел и квадратный корень из их суммы и вывести эти значения на экран
                res1 = n1 ** 0.5 + n2 ** 0.5
                res2 = (n1 + n2) ** 0.5
                res1_text = f'Сумма корней: {res1:.5f}'
                res2_text = f'Корень суммы: {res2:.5f}'
    
            elif var == 5: # Вычислить сумму двух чисел, разделить каждое из чисел на эту сумму и вывести эти значения на экран
                sum_val = n1 + n2
                res1 = n1 / sum_val
                res2 = n2 / sum_val
                res1_text = f'Первое/Сумму: {res1:.5f}'
                res2_text = f'Второе/Сумму: {res2:.5f}'
    
            elif var == 6: # Вычислить сумму двух чисел, разделить эту сумму последовательно на каждое из чисел и вывести эти значения на экран
                sum_val = n1 + n2
                res1 = sum_val / n1
                res2 = sum_val / n2
                res1_text = f'Сумма/Первое: {res1:.5f}'
                res2_text = f'Сумма/Второе: {res2:.5f}'
    
            elif var == 7: # Квадрат первого числа сложить с кубом второго, куб первого числа сложить с квадратом второго и вывести эти значения на экран
                res1 = n1 ** 2 + n2 ** 3
                res2 = n1 ** 3 + n2 ** 2
                res1_text = f'Квадрат1 + Куб2: {res1:.5f}'
                res2_text = f'Куб1 + Квадрат2: {res2:.5f}'
    
            elif var == 8: # Разделить эти числа, вычислить квадратный корень из полученного частного, а также отдельно квадратный корень из первого числа разделить на квадратный корень из второго числа и вывести эти значения на экран
                частное = n1 / n2
                res1 = частное ** 0.5
                res2 =  n1 ** 0.5 / n2 ** 0.5
                res1_text = f'√(a/b): {res1:.5f}'
                res2_text = f'√a/√b: {res2:.5f}'
    
            elif var == 9: # Разделить сумму этих чисел на сумму их квадратных корней, а также вычислить обратную величину и вывести эти значения на экран
                sum_val = n1 + n2
                sum_sqrt = n1 ** 0.5 + n2 ** 0.5
                res1 = sum_val / sum_sqrt
                res2 = 1 / res1 if res1 != 0 else '∞'
                res1_text = f'Сумма/Сумму корней: {res1:.5f}'
                res2_text = f'Обратная: {res2:.5f}'
    
            elif var == 10: # Вычислить квадрат суммы квадратных корней этих чисел и квадрат суммы их квадратов и вывести эти значения на экран
                sum_sqrt = n1 ** 0.5 + n2 ** 0.5
                sum_squares = n1 ** 2 + n2 ** 2
                res1 = sum_sqrt ** 2
                res2 = sum_squares ** 2
                res1_text = f'Квадрат суммы корней: {res1:.5f}'
                res2_text = f'Квадрат суммы квадратов: {res2:.5f}'
    
            elif var == 11: # Вычислить среднее значение этих чисел, а также разницу между каждым из этих чисел и их средним значением и вывести эти значения на экран
                average = (n1 + n2) / 2
                diff1 = n1 - average
                diff2 = n2 - average
                res1_text = f'Среднее: {average:.5f}'
                res2_text = f'Разницы: {diff1:.5f} и {diff2:.5f}'
    
            elif var == 12: # Вычислить квадратные корни из каждого числа и сложить их с самими числами и их квадратами и вывести эти значения на экран
                res1 = n1 ** 0.5 + n1 + n1 ** 2
                res2 = n2 ** 0.5 + n2 + n2 ** 2
                res1_text = f'Для первого: {res1:.5f}'
                res2_text = f'Для второго: {res2:.5f}'
    
            elif var == 13: # Возвести первое число в степень, равную втором числу, а второе число – в степень, равную первому числу и вывести эти значения на экран
                res1 = n1 ** n2
                res2 = n2 ** n1
                res1_text = f'a^b: {res1:.5f}'
                res2_text = f'b^a: {res2:.5f}'
    
            elif var == 14: # Вычислить корень из первого числа со степенью, равной второму числу и вывести эти значения на экран
                res1 = n1 ** (1 / n2) if n2 != 0 else '∞'
                res2 = n2 ** (1 / n1) if n1 != 0 else '∞'
                res1_text = f'Корень(a) степени b: {res1:.5f}'
                res2_text = f'Корень(b) степени a: {res2:.5f}'
    
            elif var == 15: # Каждое из чисел увеличить на два и вычислить произведение этих величин, а также обратную величину и вывести эти значения на экран
                n1_plus = n1 + 2
                n2_plus = n2 + 2
                res1 = n1_plus * n2_plus
                res2 = 1 / res1 if res1 != 0 else '∞'
                res1_text = f'Произведение (a+2)*(b+2): {res1:.5f}'
                res2_text = f'Обратная: {res2:.5f}'
    
            elif var == 16: # Первое число увеличить в два раза, второе число уменьшить в два раза и вычислить сумму и произведение этих значений и вывести эти значения на экран
                n1_double = n1 * 2
                n2_half = n2 / 2
                res1 = n1_double + n2_half
                res2 = n1_double * n2_half
                res1_text = f'Сумма: {res1:.5f}'
                res2_text = f'Произведение: {res2:.5f}'
    
            elif var == 17: # Вычислить сумму и произведение обратных значений этих чисел и вывести эти значения на экран
                inv1 = 1 / n1 if n1 != 0 else '∞'
                inv2 = 1 / n2 if n2 != 0 else '∞'
                res1 = inv1 + inv2 if isinstance(inv1, float) else '∞'
                res2 = inv1 * inv2 if isinstance(inv1, float) else '∞'
                res1_text = f'Сумма обратных: {res1:.5f}'
                res2_text = f'Произведение обратных: {res2:.5f}'
    
            elif var == 18: # Сложить эти два числа и каждое из них возвести в степень, равную вычисленной сумме и вывести эти значения на экран
                sum_val = n1 + n2
                res1 = n1 ** sum_val
                res2 = n2 ** sum_val
                res1_text = f'a^(a+b): {res1:.5f}'
                res2_text = f'b^(a+b): {res2:.5f}'
    
            elif var == 19: # Сложить каждое из этих чисел с их обратным значением и вывести эти значения на экран
                res1 = n1 + (1 / n1 if n1 != 0 else '∞')
                res2 = n2 + (1 / n2 if n2 != 0 else '∞')
                res1_text = f'a + 1/a: {res1:.5f}'
                res2_text = f'b + 1/b: {res2:.5f}'
    
            elif var == 20: # Вычислить сумму этих чисел и возвести эту сумму в степень, равную вычисленной сумме
                sum_val = n1 + n2
                res1 = sum_val ** sum_val
                res1_text = f'Сумма {sum_val:.5f} в степени {sum_val:.5f}: {res1:.5f}'
                res2_text = f'(a+b)^(a+b)'
    
        except ValueError:
            messagebox.showerror('Ошибка', 'Пожалуйста, вводите только целые/десятичные числа')
        except ZeroDivisionError:
            messagebox.showerror('Ошибка', 'Пожалуйста, не делите на ноль')
        except Exception as e:
            messagebox.showerror('Ошибка', f'Произошла ошибка: {str(e)}')
    
        res1_var.set(res1_text)
        res2_var.set(res2_text)


root = tk.Tk()
root.title('form1')
root.geometry('300x300')

tk.Label(root, text='Вариант (1-20):').pack()
variant_entry = tk.Entry(root, width=10)
variant_entry.pack()
variant_entry.insert(0, '1')

tk.Label(root, text='Первое число:').pack()
entry1 = tk.Entry(root, width=20)
entry1.pack()

tk.Label(root, text='Второе число:').pack()
entry2 = tk.Entry(root, width=20)
entry2.pack()

tk.Button(root, text='Вычислить', command=form1, bg='lightgreen').pack(pady=10)

tk.Label(root, text='Результат:').pack()

res1_var = tk.StringVar()
res2_var = tk.StringVar()

tk.Label(root, textvariable=res1_var, bg='lightyellow', width=40, anchor='w').pack()
tk.Label(root, textvariable=res2_var, bg='lightyellow', width=40, anchor='w').pack()

root.mainloop()










