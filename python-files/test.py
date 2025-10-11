from random import choice, randint
step1 = ['круг с диаметром', 'квадрат со стороной', 'раносторонний треугольник со стороной', 'отрезок длиной']
step2 = randint(1, 90)
print(f'Сделай программу на питоне для turtle, которая будет рисовать {choice(step1)} {step2}')
