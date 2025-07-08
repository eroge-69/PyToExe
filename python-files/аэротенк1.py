import math
# Константы
CP_AIR = 1005  # Удельная теплоёмкость воздуха (Дж/(кг·К))
RHO_AIR = 1.2  # Плотность воздуха (кг/м³)
PI = math.pi

def input_pipe_params(parent_length):
    """Ввод параметров трубы с возможностью указания координаты ответвления"""
    diam = float(input("  - Диаметр трубы (мм): ")) / 1000
    length = float(input("  - Длина трубы (м): "))
    wall = float(input("  - Толщина стенки (мм): ")) / 1000
    # Запрос координаты только если это ответвление
    if parent_length > 0:
        pos = float(input(f"  - Координата ответвления от начала родительской трубы (0-{parent_length} м): "))
        while pos < 0 or pos > parent_length:
            print(f"Ошибка: координата должна быть в пределах 0-{parent_length} м")
            pos = float(input("  - Введите корректную координату: "))
    else:
        pos = 0  # Для магистральной трубы
    
    return {'diam': diam, 'length': length, 'wall': wall, 'pos': pos, 'branches': []}
def add_branches(pipe):
    """Рекурсивное добавление ответвлений с указанием координат"""
    n_branches = int(input(f"  - Количество ответвлений от текущей трубы (0 если нет): "))
    for i in range(n_branches):
        print(f"\nВвод параметров для ответвления {i+1}:")
        branch = input_pipe_params(pipe['length'])
        pipe['branches'].append(branch)
        add_branches(branch)  # Рекурсия для вложенных ответвлений
def calculate_cooling(pipe, temp_in, mass_flow, temp_env, material_lambda, level=0):
    """Рекурсивный расчёт охлаждения с учётом координат ответвлений"""
    ALPHA_INT = 15  # Коэффициент теплоотдачи внутри
    ALPHA_EXT = 30   # Коэффициент теплоотдачи снаружи
    # Расчёт температуры в начале текущей трубы
    if pipe['pos'] > 0:
        # Для ответвлений - вычисляем температуру в точке подключения
        ratio = pipe['pos'] / pipe['parent_length']
        temp_in = pipe['parent_temp_start'] + (pipe['parent_temp_end'] - pipe['parent_temp_start']) * ratio
    # Расчёт для текущей трубы
    k = 1 / (1/ALPHA_INT + pipe['wall']/material_lambda + 1/ALPHA_EXT)
    perimeter = PI * pipe['diam']
    flow_per_branch = mass_flow / max(1, len(pipe['branches']))
    
    temp_out = temp_env + (temp_in - temp_env) * math.exp(
        -k * perimeter * pipe['length'] / (flow_per_branch * CP_AIR)
    )
    # Отступ для визуализации иерархии
    indent = "  " * level
    print(f"\n{indent}Труба {pipe['diam']*1000:.0f}мм ({pipe['length']}м):")
    print(f"{indent}  Подключена на координате: {pipe['pos']:.1f} м")
    print(f"{indent}  Температура на входе: {temp_in:.1f}°C")
    print(f"{indent}  Температура на выходе: {temp_out:.1f}°C")
    
    # Подготовка данных для дочерних ответвлений
    for branch in pipe['branches']:
        branch['parent_length'] = pipe['length']
        branch['parent_temp_start'] = temp_in
        branch['parent_temp_end'] = temp_out
        calculate_cooling(branch, temp_out, flow_per_branch/len(pipe['branches']), 
                         temp_env, material_lambda, level+1)

def main():
    print("Расчёт температуры воздуха в разветвлённой системе")
    print("------------------------------------------------")
    print("Внимание! Координаты ответвлений указываются от начала родительской трубы.\n")
    # 1. Магистральная труба (не имеет родителя)
    print("Ввод параметров магистральной трубы:")
    main_pipe = input_pipe_params(0)
    main_pipe['parent_length'] = 0
    main_pipe['parent_temp_start'] = 0
    main_pipe['parent_temp_end'] = 0
    # 2. Рекурсивный ввод ответвлений
    add_branches(main_pipe)
    # 3. Параметры воздуха
    print("\nПараметры воздуха:")
    flow_rate = float(input("  - Расход воздуха (м³/ч): "))
    temp_in = float(input("  - Начальная температура воздуха (°C): "))
    temp_env = float(input("  - Температура окружающей среды (°C): "))
    # 4. Материал труб
    print("\nМатериалы труб:")
    materials = {
        '1': {'name': 'Нержавеющая сталь', 'lambda': 17},
        '2': {'name': 'Легированная сталь', 'lambda': 45},
        '3': {'name': 'Обычная сталь', 'lambda': 50}
    }
    for k, v in materials.items():
        print(f"  {k}. {v['name']} (λ={v['lambda']} Вт/(м·К))")
    material = materials[input("  Выберите материал (1-3): ")]
    
    # Расчёт
    mass_flow = flow_rate * RHO_AIR / 3600
    print("\nРезультаты расчёта:")
    calculate_cooling(main_pipe, temp_in, mass_flow, temp_env, material['lambda'])

if __name__ == "__main__":
    main()