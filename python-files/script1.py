import pandas as pd
import os
import sys


def parse_wifi_data():
    # Определяем правильный путь к файлу
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)  # для .exe
    else:
        base_dir = os.path.dirname(__file__)  # для .py

    csv_path = os.path.join(base_dir, 'in.csv')

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Файл {csv_path} не найден!")

    with open(csv_path, 'r') as file:
        # ваш код обработки CSV
        pass


if __name__ == '__main__':
    parse_wifi_data()

def parse_wifi_data(input_file, output_file):
    # Чтение данных из файла
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Списки для данных
    ap_data = []
    client_data = []
    non_associated_clients = []
    probed_networks = []
    current_section = None

    # Обработка строк
    for line in lines:
        if line.startswith("BSSID"):
            current_section = "AP"
            continue
        elif line.startswith("Station MAC"):
            current_section = "Client"
            continue

        if current_section == "AP" and line.strip():
            parts = [part.strip() for part in line.split(',')]
            if len(parts) >= 14:
                privacy = parts[5] if len(parts) > 5 else ""
                protection = privacy.split()[0] if privacy else ""

                ap_data.append({
                    'BSSID': parts[0],
                    'ESSID': parts[13] if len(parts) > 13 else "",
                    'Channel': parts[3] if len(parts) > 3 else "",
                    'Protection': protection
                })

        elif current_section == "Client" and line.strip():
            parts = [part.strip() for part in line.split(',')]
            if len(parts) >= 6:
                client_mac = parts[0]
                bssid = parts[5] if len(parts) > 5 else ""

                if bssid == "(not associated)":
                    non_associated_clients.append(client_mac)
                    probed = parts[6].strip() if len(parts) > 6 else ""
                    probed_networks.append(probed)

                client_data.append({
                    'Client MAC': client_mac,
                    'BSSID': "" if bssid == "(not associated)" else bssid
                })

    # Создаем основной DataFrame
    ap_df = pd.DataFrame(ap_data)
    client_df = pd.DataFrame(client_data)

    # Объединяем данные точек доступа с клиентами
    result_df = pd.merge(ap_df, client_df, on='BSSID', how='left')
    result_df['Client MAC'] = result_df['Client MAC'].astype(str).replace('nan', '')

    # Группируем данные для основной таблицы
    grouped = result_df.groupby(['BSSID', 'ESSID', 'Channel', 'Protection'])['Client MAC'].apply(
        lambda x: '\n'.join(filter(None, x))).reset_index()

    # Создаем DataFrame для пустых строк
    empty_rows_before_non_associated = pd.DataFrame([{
        'BSSID': '',
        'ESSID': '',
        'Channel': '',
        'Protection': '',
        'Client MAC': '',
        'Подключенные сети': ''
    } for _ in range(3)])

    # Создаем DataFrame для неподключенных клиентов
    non_associated_data = []
    for mac, network in zip(non_associated_clients, probed_networks):
        non_associated_data.append({
            'BSSID': '',
            'ESSID': 'Неассоциированные клиенты',
            'Channel': '',
            'Protection': '',
            'Client MAC': mac,
            'Подключенные сети': network
        })

    # Создаем DataFrame для пустых строк перед статистикой
    empty_rows_before_stats = pd.DataFrame([{
        'BSSID': '',
        'ESSID': '',
        'Channel': '',
        'Protection': '',
        'Client MAC': '',
        'Подключенные сети': ''
    } for _ in range(3)])

    # Подсчет статистики
    unique_bssid_count = ap_df['BSSID'].nunique()
    connected_clients_count = client_df[client_df['BSSID'] != ""]['BSSID'].count()
    total_clients = connected_clients_count + len(non_associated_clients)

    # Добавляем строку статистики
    stats_row = {
        'BSSID': '',
        'ESSID': 'ИТОГО:',
        'Channel': '',
        'Protection': '',
        'Client MAC': f'Уникальных точек доступа: {unique_bssid_count}\nАссоциированных клиентов: {connected_clients_count}',
        'Подключенные сети': f'Неассоциированных клиентов: {len(non_associated_clients)}\nВсего клиентов: {total_clients}'
    }

    # Объединяем все данные
    final_df = pd.concat([
        grouped,
        empty_rows_before_non_associated,
        pd.DataFrame(non_associated_data),
        empty_rows_before_stats,
        pd.DataFrame([stats_row])
    ], ignore_index=True)

    # Сохраняем в Excel
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')

    final_df.to_excel(writer, index=False,
                     columns=['ESSID', 'BSSID', 'Channel', 'Protection', 'Client MAC', 'Подключенные сети'],
                     header=['Идентификатор сети', 'MAC-адрес', 'Номер канала',
                             'Средство защиты', 'MAC-адрес клиента', 'Подключенные сети'])

    # Настройка форматирования
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    wrap_format = workbook.add_format({'text_wrap': True})
    bold_format = workbook.add_format({'bold': True})

    # Ширина колонок
    worksheet.set_column('A:A', 30)  # ESSID
    worksheet.set_column('B:B', 20)  # BSSID
    worksheet.set_column('C:C', 10)  # Channel
    worksheet.set_column('D:D', 15)  # Protection
    worksheet.set_column('E:E', 25, wrap_format)  # Client MAC
    worksheet.set_column('F:F', 30, wrap_format)  # Подключенные сети

    # Находим индекс строки со статистикой и выделяем ее жирным
    stats_row_index = len(final_df) - 1
    worksheet.set_row(stats_row_index, None, bold_format)

    writer.close()
    print(f"Файл {output_file} успешно создан.")


# Использование функции
input_filename = 'in.csv'
output_filename = 'result.xlsx'
parse_wifi_data(input_filename, output_filename)