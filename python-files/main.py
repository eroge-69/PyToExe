#!/usr/bin/env python3
import math

"""
Калькулятор требуемых мощностей для Шлюза доступа.

- Рассчитывает одновременные сессии RDP, SSH и других протоколов.
- Определяет необходимое количество узлов и их мощности по таблице NODES_TABLE.
- Считает примерное дисковое пространство для хранения сессий.
"""

# ===== Таблица мощностей =====
NODES_TABLE = [
    {"RDP_MAX": 50,  "CPU": 3,   "Cores": 4,  "RAM": "8-16"},
    {"RDP_MAX": 100, "CPU": 2.1, "Cores": 8, "RAM": "16-24"},
    {"RDP_MAX": 200, "CPU": 2.4, "Cores": 10, "RAM": "24-32"},
    {"RDP_MAX": 300, "CPU": 2.4, "Cores": 10,  "RAM": "48-64"},
    {"RDP_MAX": 450, "CPU": 3.2, "Cores": 8,  "RAM": "64-96"},
]

# ===== Функции =====
def input_with_default(prompt, default, cast_type=int):
    """Ввод с подсказкой значения по умолчанию"""
    value = input(f"{prompt} ({default}): ").strip()
    return cast_type(value) if value else default

def select_node_config(rdp_equiv, ssh_equiv=0):
    """Выбор мощности узла из таблицы по RDP-эквиваленту"""
    for row in NODES_TABLE:
        if rdp_equiv <= row["RDP_MAX"]:
            return row
    return NODES_TABLE[-1]

def calc_required_nodes(rdp_equiv):
    """Расчет количества узлов, чтобы не превышать RDP_MAX"""
    nodes = 1
    while True:
        per_node = math.ceil(rdp_equiv / nodes)
        cfg = select_node_config(per_node)
        if per_node <= cfg["RDP_MAX"]:
            return nodes
        nodes += 1

def calc_disk_rdp(rdp_sessions, hours, shifts, mb_per_min=10):
    """Диск для RDP сессий в MB"""
    return rdp_sessions * mb_per_min * 60 * hours * shifts

def calc_disk_ssh(ssh_sessions, hours, shifts, mb_per_hour=2):
    """Диск для SSH сессий в MB"""
    return ssh_sessions * mb_per_hour * hours * shifts

# ===== Ввод данных =====
print("\n=== Ввод параметров расчёта для Шлюза доступа ===")
users = input_with_default("Количество пользователей в смену", 50)
shifts = input_with_default("Количество смен", 1)
hours_per_shift = input_with_default("Длительность смены в часах", 8)
sessions_per_user = input_with_default("Количество сессий на пользователя", 1)

simult_sessions = users * sessions_per_user

# ===== Ввод процентов протоколов =====
print("\nВведите процент одновременных сессий для каждого протокола.")
print("Сумма всех процентов не должна превышать 100%.\n")
while True:
    default_rdp = 50
    rdp_percent = input_with_default(f"Процент RDP ({default_rdp}%)", default_rdp)
    remaining = 100 - rdp_percent
    default_ssh = remaining // 2
    ssh_percent = input_with_default(f"Процент SSH (осталось {remaining}%)", default_ssh)
    remaining -= ssh_percent
    default_other = remaining
    other_percent = input_with_default(f"Процент других протоколов (осталось {remaining}%)", default_other)
    total_percent = rdp_percent + ssh_percent + other_percent
    if total_percent > 100:
        print(f"Сумма процентов ({total_percent}%) превышает 100%. Попробуйте снова.\n")
    else:
        break

# ===== Расчет одновременных сессий =====
rdp_sessions = math.ceil(simult_sessions * rdp_percent / 100)
ssh_sessions = math.ceil(simult_sessions * ssh_percent / 100)
other_sessions = math.ceil(simult_sessions * other_percent / 100)

# ===== Перевод SSH и других в RDP-эквивалент для мощности =====
rdp_equiv = rdp_sessions + math.ceil(ssh_sessions / 4) + other_sessions

# ===== Определяем количество узлов =====
num_nodes = calc_required_nodes(rdp_equiv)
rdp_per_node = math.ceil(rdp_sessions / num_nodes)
ssh_per_node = math.ceil(ssh_sessions / num_nodes)
other_per_node = math.ceil(other_sessions / num_nodes)

node_cfg = select_node_config(rdp_per_node + math.ceil(ssh_per_node/4) + other_per_node)

# ===== Расчет диска =====
disk_rdp_total = calc_disk_rdp(rdp_sessions, hours_per_shift, shifts)
disk_ssh_total = calc_disk_ssh(ssh_sessions, hours_per_shift, shifts)
disk_other_total = calc_disk_rdp(other_sessions, hours_per_shift, shifts)  # как RDP
disk_total = disk_rdp_total + disk_ssh_total + disk_other_total
disk_node_mb = math.ceil(disk_total / num_nodes)
disk_node_gb = disk_node_mb / 1024

# ===== Вывод результатов =====
RESET = "\033[0m"
BOLD = "\033[1m"
COLORS = ["\033[92m", "\033[93m", "\033[94m"]
PARAM_COLOR = "\033[96m"

print("\n" + "="*80)
print(f"{BOLD}Одновременные сессии:{RESET} RDP: {rdp_sessions}, SSH: {ssh_sessions}, Другие: {other_sessions}")
print(f"{BOLD}Общее количество сессий для хранения:{RESET} {rdp_sessions + ssh_sessions + other_sessions}")
print(f"{BOLD}Необходимое количество нод:{RESET} {num_nodes}\n")

for i in range(1, num_nodes + 1):
    color = COLORS[(i-1) % len(COLORS)]
    print(f"\n{color}{'='*80}{RESET}")
    print(f"{color}{BOLD}Узел {i}:{RESET}")
    print(f"{color}{'-'*60}{RESET}")
    print(f"RDP на узел: {rdp_per_node}")
    print(f"SSH на узел: {ssh_per_node}")
    print(f"Другие протоколы на узел: {other_per_node}")
    print(f"{PARAM_COLOR}CPU: {node_cfg['CPU']} GHz{RESET}")
    print(f"{PARAM_COLOR}Cores: {node_cfg['Cores']}{RESET}")
    print(f"{PARAM_COLOR}RAM: {node_cfg['RAM']} GB{RESET}")
    print(f"{PARAM_COLOR}Диск на узел: {disk_node_mb:.2f} MB (~{disk_node_gb:.2f} GB){RESET}")
    print(f"{color}{'='*80}{RESET}")

print("\n⚠ Результаты укрупнённые. Для точного расчета рекомендуется учитывать реальные одновременные сессии, активность пользователей и разрешение экранов")
print("="*80)
