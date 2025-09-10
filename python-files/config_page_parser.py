from bs4 import BeautifulSoup
import pandas as pd
import re
import os

def main(html_file):
    set_script_dir_as_working_dir()
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'lxml')
    table_headers = extract_table_headers(page_html=soup)
    table_rows = extract_table_rows(page_html=soup)
    rows_list = create_row_dictionaries(table_headers=table_headers,
                                        table_rows=table_rows)
    result_dataframe = pd.DataFrame.from_records(rows_list)
    separate_comment_from_comment_date(df = result_dataframe)          
    columns_to_drop = ['Mid', 'Open', 'Max', 'Min', 'Avg', 'Market', 'Market_2', 'Admit', 'Объем (BID)', 'Объем (ASK)', 'Объем (LAST)', 'Статус скрипта', 'Ответственный менеджер', 'Отчет', 'Last effective', 'Last 10', 'Flags', 'logs', '', 'Комментарий']
    result_dataframe.drop(columns=columns_to_drop, inplace=True)
    result_dataframe.to_excel('result.xlsx', index=False, freeze_panes=(1,1))
    return result_dataframe

def set_script_dir_as_working_dir():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

def extract_table_headers(page_html):
    table_headers = [header.text for header in page_html.select('table.list>thead>tr>th')]
    return table_headers

def extract_table_rows(page_html):
    table_rows = page_html.select('table.list>tbody>tr')
    return table_rows

def create_row_dictionaries(table_headers, table_rows):
    rows_list = []
    for row in table_rows:
        row_dict = {}
        row_values = [cell for cell in row.find_all('td')]
        fields_low_quotes_number = []
        for header, value in zip(table_headers, row_values):
            if header == 'Flags':
                row_dict['Просрочен'] = get_flag_value(cell_content=value,
                                                       searched_flag='//i.cbonds.ru/icons/clock.png')
                row_dict['Считается в CE'] = get_flag_value(cell_content=value,
                                                            searched_flag='//i.cbonds.ru/icons/line48.png')
            if quotes_number_is_low(cell_content=value):
                if header in ['Обработано бумаг', 'Bid', 'Ask', 'Last', 'Close', 'Оборот', 'Число сделок', 'Объем сделок в бумагах']:
                    fields_low_quotes_number.append(header)  
            row_dict[header] = value.get_text(separator="", strip=True).replace('\\n','').strip()
        if row_dict['Просрочен'] == 'Нет' and len(fields_low_quotes_number) > 0:
            row_dict['Мало котировок'] = ', '.join(fields_low_quotes_number)
        row_dict['Тестовый'] = is_in_test_mode(row)
        rows_list.append(row_dict)
    return rows_list

def get_flag_value(cell_content, searched_flag):
    flag_present = cell_content.find('img', attrs={'src': searched_flag}) != None
    if flag_present:
        flag_value = 'Да'
    else:
        flag_value = 'Нет'
    return flag_value

def quotes_number_is_low(cell_content):
    try:
        if 'red' in cell_content.attrs['class']:
            return True     
    except KeyError:
        pass
    return False

def is_in_test_mode(row):
    if 'test_mode' in row['class']:
        return 'Да'
    return 'Нет'

def separate_comment_from_comment_date(df):
    df['Комментарий менеджера'] = '' 
    df['Дата комментария'] = ''
    for row_number in range(0, df.shape[0]):
        if df.loc[row_number, 'Комментарий'] != '':
            comment_and_date_list = df.loc[row_number, 'Комментарий'].split(' /', maxsplit = 1)
            df.loc[row_number, 'Комментарий менеджера'] = comment_and_date_list[0]
            date_pattern = r'\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$'
            df.loc[row_number, 'Дата комментария'] = re.search(date_pattern, comment_and_date_list[1]).group()

main(html_file='html.txt')

