# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: masaryScript.py
# Bytecode version: 3.9.0beta5 (3425)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

import PySimpleGUI as sg
from PySimpleGUI.PySimpleGUI import Output
pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from csv import writer
import os
from openpyxl import load_workbook
from datetime import datetime
import re

city_index = {
    'city name\n(drop down list )': [
        'CAIRO', 'GIZA', 'ALEXANDRIA', 'PORT SAID', 'ISMAILIA', 'BANHA', 'LUXOR', 'ASWAN', 'ARISH',
        'SHARM ELSHEKH', 'HURGHADA', 'MARSA MATROH', 'TABA', 'RAAS ELBAR', 'TANTA', 'MANSOURA',
        'EL MAHALA', 'EL MENIA', 'BANI SWIEF', 'ASSUIT', 'SUHAG', 'SUEZ', 'EL FAYOUM', 'DOMYAT',
        'SHEBEN EL KOUM', 'EL ZAGAZEG', 'KAFR ELSHEIKH', 'EL KHARGA', 'DAMANHOUR', 'TOUKH', 'KAHA',
        '10TH OF RAMADAN', 'SOHAG', 'MADINAT EL SALAM', 'MADINAT 6TH OCTOBER', 'ELTAL ELKABEER',
        'ELKANATER ELKHAYRIA', 'KALIOUB', 'EL GHARBIA', 'EL MENOFIA', 'DAKAHLIA', 'EL SHARKIA',
        'EL BEHERA', 'KENA', 'EL QALOUBIA', 'South Sinai', 'North Sinai', 'NEWEBAA',
        'ELWADY ELGEDID', 'EL KUWAIT', 'OTHERS'
    ]
}

city_index_df = pd.DataFrame(city_index)


def prepend_line(file_name, line):
    dummy_file = file_name + '.bak'
    with open(file_name, 'r', encoding='utf-8') as read_obj:
        with open(dummy_file, 'w', encoding='utf-8') as write_obj:
            write_obj.write(line + '\n')
            for line in read_obj:
                write_obj.write(line)
    os.remove(file_name)
    os.rename(dummy_file, file_name)

def append_list_as_row(file_name, list_of_elem):
    with open(file_name, 'a+', newline='') as write_obj:
        csv_writer = writer(write_obj, delimiter=';')
        csv_writer.writerow(list_of_elem)

def Gentare_file(fileName):
    now = datetime.now()
    outFileName = fileName[:(-5)] + '_Output_REF' + now.strftime('%H%M%y%m%d') + '.csv'
    df1 = pd.read_excel(fileName, sheet_name=0, dtype=str)
    df_Left_join = pd.merge(df1, city_index_df, on='city name\n(drop down list )', how='left')
    df_am = pd.DataFrame()
    df_am['Mrn'] = df1['merchants \nreference no']
    df_am['Opration'] = 'AM'
    df_am['BankCode'] = '011200'
    df_am['BRANCH_CODE'] = '000155'
    df_am['PROFILE_CODE'] = '204'
    df_am['ACRONYM'] = df1['ACRONYM\nmax 30 charactar']
    df_am['ABREV_LOCATION'] = df1['city name\n(drop down list )']
    df_am['IDENTIFICATION_INFO'] = df1['MERCHANT\n first NAME ENG'] + ' ' + df1['MERCHANT rest of  NAME ENG\nmax 38 charactar']
    df_am['STATUS'] = 'N'
    df_am['DISCOUNT_CODE'] = df1['discount code'].astype(str)
    df_am['SPECIAL_DISCOUNT_CODE'] = ''
    df_am['ACTIVITY_CODE'] = '0099'
    df_am['ADDRESS1'] = df1['ADDRESS1\nmax 30 charactar'].astype(str).apply(lambda x: x.ljust(30))
    df_am['ADDRESS2\nmax 30 charactar'] = df1['ADDRESS2\nmax 30 charactar'].astype(str).apply(lambda x: x.ljust(100))
    df_am['city_code'] = df_Left_join['city_code'].astype(str)
    df_am['region_code'] = '001'
    df_am['mobileno'] = df1['MOBILE'].astype(str)
    df_am['mobileno'] = df_am['mobileno'].apply(lambda x: x.ljust(180))
    df_am['Add'] = df_am['ADDRESS1'] + df_am['ADDRESS2\nmax 30 charactar'] + df_am['city_code'] + df_am['region_code'] + df_am['mobileno']
    df_am['LANGUAGE'] = 'ENG'
    df_am['MERCHANTRest'] = df1['MERCHANT rest of  NAME ENG\nmax 38 charactar'].astype(str).apply(lambda x: x.ljust(40))
    df_am['MerchantName'] = df1['MERCHANT\n first NAME ENG'].astype(str).apply(lambda x: x.ljust(40))
    df_am['nIDCode'] = '02'
    df_am['nID'] = df1['NATIONAL ID'].astype(str)
    df_am['nID'] = df_am['nID'].apply(lambda x: x.ljust(248))
    df_am['zero1'] = '0'
    df_am['zero1'] = df_am['zero1'].apply(lambda x: x.ljust(30))
    df_am['zero2'] = '0'
    df_am['zero2'] = df_am['zero2'].apply(lambda x: x.ljust(70))
    df_am['owner_info'] = df_am['MERCHANTRest'] + df_am['MerchantName'] + df_am['nIDCode'] + df_am['nID'] + df_am['zero1'] + df_am['zero2']
    df_am['empty1'] = ''
    df_am['empty2'] = ''
    df_am['CONTACT_LANGUAGE'] = 'ENG'
    df_am['empty3'] = ''
    df_am['LEGAL_IDENTIFICATION'] = df1['NATIONAL ID'].astype(str)
    df_am['STATEMENT_CODE'] = '01'
    df_am['SETTLEMENT_MODE'] = 'T'
    df_am['MARKUP_CODE'] = ''
    df_am['AGREEMENT_DATE'] = ''
    df_am['NBR_ACCOUNTS'] = '001'
    df_am['ACCOUNT_BUFFER'] = '1550001000103704        EGPN'
    df_am['RESERVED1'] = 'N0'
    df_am['RESERVED2'] = ''
    df_am['RESERVED3'] = ''
    df_am = df_am[['Opration', 'Mrn', 'BankCode', 'BRANCH_CODE', 'PROFILE_CODE', 'ACRONYM', 'ABREV_LOCATION', 'IDENTIFICATION_INFO', 'STATUS', 'DISCOUNT_CODE', 'SPECIAL_DISCOUNT_CODE', 'ACTIVITY_CODE', 'Add', 'LANGUAGE', 'owner_info', 'empty1', 'empty2', 'CONTACT_LANGUAGE', 'empty3', 'LEGAL_IDENTIFICATION', 'STATEMENT_CODE', 'SETTLEMENT_MODE', 'MARKUP_CODE', 'AGREEMENT_DATE', 'NBR_ACCOUNTS', 'ACCOUNT_BUFFER', 'RESERVED1', 'RESERVED2', 'RESERVED3']]
    df_am.to_csv(outFileName, index=False, header=False, mode='a', sep=';')
    df_ao = pd.DataFrame()
    df_ao['Mrn'] = df1['merchants \nreference no']
    df_ao['Mrn2'] = df_ao['Mrn']
    df_ao['Opration'] = 'AO'
    df_ao['BankCode'] = '011200'
    df_ao['BRANCH_CODE'] = '000155'
    df_ao['ACRONYM'] = df1['ACRONYM\nmax 30 charactar']
    df_ao['ACRONYM2'] = df_ao['ACRONYM']
    df_ao['ABREV_LOCATION'] = df1['city name\n(drop down list )']
    df_ao['mcc'] = df1['mcc']
    df_ao['currency_code'] = 'EGP'
    df_ao['add'] = df_am['Add']
    df_ao['contact_name'] = ''
    df_ao['contact_lang'] = ''
    df_ao['contact_postion'] = ''
    df_ao['LEGAL_IDENTIFICATION'] = df_am['LEGAL_IDENTIFICATION']
    df_ao['EQUIPMENT_CODE_1'] = '100'
    df_ao['EQUIPMENT_NUMBER_1'] = '001'
    df_ao['EQUIPMENT_FEES_CODE_1'] = '002'
    df_ao['EQUIPMENT_CODE_2'] = '200'
    df_ao['EQUIPMENT_NUMBER_2'] = ''
    df_ao['EQUIPMENT_FEES_CODE_2'] = ''
    df_ao['EQUIPMENT_CODE_3'] = ''
    df_ao['EQUIPMENT_NUMBER_3'] = ''
    df_ao['EQUIPMENT_FEES_CODE_3'] = ''
    df_ao['CAPTURE_MODE'] = 'B'
    df_ao['STOP_LIST_CODE'] = ''
    df_ao['STATEMENT_CODE'] = '01'
    df_ao['LANGUAGE'] = 'ENG'
    df_ao['EXTERNAL_OUTLET_NUMBER'] = ''
    df_ao['FRAUD_INDICATOR'] = '0'
    df_ao['OUTLET_ACTIVITY_CODE'] = '0099'
    df_ao['DISCOUNT_CODE'] = df_am['DISCOUNT_CODE']
    df_ao['SPECIAL_DISCOUNT_CODE'] = ''
    df_ao['FLOOR_LIMIT_INDEX'] = '0001'
    df_ao['MARKUP_CODE'] = ''
    df_ao['NB_ACCOUNTS_LINK'] = '01'
    df_ao['ACCOUNTS_NUMBER'] = '1550001000103704'
    df_ao['RESERVED1'] = ''
    df_ao['RESERVED2'] = ''
    df_ao['RESERVED3'] = ''
    df_ao = df_ao[['Opration', 'Mrn', 'Mrn2', 'BankCode', 'BRANCH_CODE', 'ACRONYM', 'ACRONYM2', 'ABREV_LOCATION', 'mcc', 'currency_code', 'add', 'contact_name', 'contact_lang', 'contact_postion', 'LEGAL_IDENTIFICATION', 'EQUIPMENT_CODE_1', 'EQUIPMENT_NUMBER_1', 'EQUIPMENT_FEES_CODE_1', 'EQUIPMENT_CODE_2', 'EQUIPMENT_NUMBER_2', 'EQUIPMENT_FEES_CODE_2', 'EQUIPMENT_CODE_3', 'EQUIPMENT_NUMBER_3', 'EQUIPMENT_FEES_CODE_3', 'CAPTURE_MODE', 'STOP_LIST_CODE', 'STATEMENT_CODE', 'LANGUAGE', 'EXTERNAL_OUTLET_NUMBER', 'FRAUD_INDICATOR', 'OUTLET_ACTIVITY_CODE', 'DISCOUNT_CODE', 'SPECIAL_DISCOUNT_CODE', 'FLOOR_LIMIT_INDEX', 'MARKUP_CODE', 'NB_ACCOUNTS_LINK', 'ACCOUNTS_NUMBER', 'RESERVED1', 'RESERVED2', 'RESERVED3']]
    df_ao.to_csv(outFileName, index=False, header=False, mode='a', sep=';')
    df_ap = pd.DataFrame()
    df_ap['serial'] = df1['serial']
    df_ap['oparation'] = 'AP'
    df_ap['Mrn'] = df_ao['Mrn']
    df_ap['BankCode'] = '011200'
    df_ap['BRANCH_CODE'] = '000155'
    df_ap['masterIndcator'] = 'A'
    df_ap['posNumer'] = ''
    df_ap['POSGrouping'] = '001'
    df_ap['ACRONYM'] = df_ao['ACRONYM']
    df_ap['ABREV_LOCATION'] = df_ao['ABREV_LOCATION']
    df_ap['city_code'] = df_Left_join['city_code'].astype(str)
    df_ap['region_code'] = '001'
    df_ap['pos_brand_code'] = '003'
    df_ap['PROTOCOL_INDEX'] = '01'
    df_ap['POS_PROFILE_CODE'] = '0003'
    df_ap['Trx_prosseing_mod'] = 'DM'
    df_ap['pin_padding'] = '                         '
    df_ap['Termainal_mod_status'] = 'L'
    df_ap['currency_code'] = 'EGP'
    df_ap['MINIMUM_AMOUNT_C1'] = ''
    df_ap['FLOOR_LIMIT_C1'] = ''
    df_ap['CEILING_LIMIT_C1'] = ''
    df_ap['CURRENCY_CODE_2'] = ''
    df_ap['MINIMUM_AMOUNT_C2'] = ''
    df_ap['FLOOR_LIMIT_C2'] = ''
    df_ap['CEILING_LIMIT_C2'] = ''
    df_ap['CURRENCY_CODE_3'] = ''
    df_ap['MINIMUM_AMOUNT_C3'] = ''
    df_ap['FLOOR_LIMIT_C3'] = ''
    df_ap['CEILING_LIMIT_C3'] = ''
    df_ap['CURRENCY_CODE_4'] = ''
    df_ap['MINIMUM_AMOUNT_C4'] = ''
    df_ap['FLOOR_LIMIT_C4'] = ''
    df_ap['CEILING_LIMIT_C4'] = ''
    df_ap['CURRENCY_CODE_5'] = ''
    df_ap['MINIMUM_AMOUNT_C5'] = ''
    df_ap['FLOOR_LIMIT_C5'] = ''
    df_ap['CEILING_LIMIT_C5'] = ''
    df_ap['CURRENCY_CODE_6'] = ''
    df_ap['MINIMUM_AMOUNT_C6'] = ''
    df_ap['FLOOR_LIMIT_C6'] = ''
    df_ap['CEILING_LIMIT_C6'] = ''
    df_ap['CREDIT_NOTE_FLAG'] = ''
    df_ap['dail_hour'] = '20040111'
    df_ap['DIAL_PREFIXE'] = ''
    df_ap['TONE_PULSE_FLAG'] = 'T'
    df_ap['PIN_KEY_NUMBER'] = ''
    df_ap['TRANSPORT_PIN_KEY_NUMBER'] = '005'
    df_ap['MAC_KEY_NUMBER'] = ''
    df_ap['MASTER_KEY_NUMBER'] = ''
    df_ap['U_PASSWORD'] = ''
    df_ap['LANGUAGE_CODE_1'] = 'ENG'
    df_ap['LANGUAGE_CODE_2'] = ''
    df_ap['LANGUAGE_CODE_3'] = ''
    df_ap['IDLE_LOOP_DISPLAY'] = ''
    df_ap['TERMINAL_APPLICATION_CODE'] = ''
    df_ap['CURRENT_SOFTWARE_VERSION'] = ''
    df_ap['EQUIPMENT_FEE_CODE'] = ''
    df_ap['STOP_LIST_CODE'] = '000'
    df_ap['RESERVED1'] = ''
    df_ap['RESERVED2'] = ''
    df_ap['RESERVED2'] = ''
    df_ap = df_ap[
    ['oparation', 'serial', 'Mrn', 'BankCode', 'BRANCH_CODE', 'masterIndcator', 'posNumer', 'POSGrouping', 'ACRONYM',
     'ABREV_LOCATION', 'city_code', 'region_code', 'pos_brand_code', 'PROTOCOL_INDEX', 'POS_PROFILE_CODE',
     'Trx_prosseing_mod', 'pin_padding', 'Termainal_mod_status', 'currency_code', 'MINIMUM_AMOUNT_C1',
     'FLOOR_LIMIT_C1', 'CEILING_LIMIT_C1', 'CURRENCY_CODE_2', 'MINIMUM_AMOUNT_C2', 'FLOOR_LIMIT_C2',
     'CEILING_LIMIT_C2', 'CURRENCY_CODE_3', 'MINIMUM_AMOUNT_C3', 'FLOOR_LIMIT_C3', 'CEILING_LIMIT_C3',
     'CURRENCY_CODE_4', 'MINIMUM_AMOUNT_C4', 'FLOOR_LIMIT_C4', 'CEILING_LIMIT_C4', 'CURRENCY_CODE_5',
     'MINIMUM_AMOUNT_C5', 'FLOOR_LIMIT_C5', 'CEILING_LIMIT_C5', 'CURRENCY_CODE_6', 'MINIMUM_AMOUNT_C6',
     'FLOOR_LIMIT_C6', 'CEILING_LIMIT_C6', 'CREDIT_NOTE_FLAG', 'dail_hour', 'DIAL_PREFIXE', 'TONE_PULSE_FLAG',
     'PIN_KEY_NUMBER', 'TRANSPORT_PIN_KEY_NUMBER', 'MAC_KEY_NUMBER', 'MASTER_KEY_NUMBER', 'U_PASSWORD']
]

    df_ap.to_csv(outFileName, index=False, header=False, mode='a', sep=';')
    total = len(df_am.index) + len(df_ao.index) + len(df_ap.index)
    number_str_total = str(total)
    zero_filled_number_total = number_str_total.zfill(8)
    number_str_am = str(len(df_am.index))
    number_str_ao = str(len(df_ao.index))
    number_str_ap = str(len(df_ap.index))
    zero_filled_number_am = number_str_am.zfill(8)
    zero_filled_number_ao = number_str_ao.zfill(8)
    zero_filled_number_ap = number_str_ap.zfill(8)
    zerosz = '00000000'
    row_contents = ['TR', zero_filled_number_am, zero_filled_number_ao, zero_filled_number_ap, zerosz, zerosz, zerosz, zerosz, zerosz, zerosz, zero_filled_number_total, '', '']
    today = datetime.today()
    unqID = now.strftime('%H%M%y%m%d')
    prepend_line(outFileName, 'HR;RF' + unqID + ';' + today.strftime('%Y%m%d') + ';;')
    append_list_as_row(outFileName, row_contents)
    return outFileName
sg.theme('DarkTeal2')
layout = [[sg.T('')], [sg.Text('Choose a file: '), sg.Input(), sg.FileBrowse(key='-IN-')], [sg.Button('Genrate BM File')]]
window = sg.Window('BM HPS Sheet Transformer', layout, size=(600, 150))
while True:  # inserted
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == 'Genrate BM File':
        sg.Popup('File \"' + Gentare_file(values['-IN-']) + '\" Genrated Successfully in the same dirctory')