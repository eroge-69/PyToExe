# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: masaryScript.py
# Bytecode version: 3.9.0beta5 (3425)

import PySimpleGUI as sg
from PySimpleGUI.PySimpleGUI import Output
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from csv import writer
import os
from openpyxl import load_workbook
from datetime import datetime
import re

city_index = {
    'city name\n(drop down list )': ['CAIRO', 'GIZA', 'ALEXANDRIA', 'PORT SAID', 'ISMAILIA', 'BANHA', 'LUXOR', 'ASWAN', 'ARISH', 'SHARM ELSHEKH', 'HURGHADA', 'MARSA MATROH', 'TABA', 'RAAS ELBAR', 'TANTA', 'MANSOURA', 'EL MAHALA', 'EL MENIA', 'BANI SWIEF', 'ASSUIT', 'SUHAG', 'SUEZ', 'EL FAYOUM', 'DOMYAT', 'SHEBEN EL KOUM', 'EL ZAGAZEG', 'KAFR ELSHEIKH', 'EL KHARGA', 'DAMANHOUR', 'TOUKH', 'KAHA', '10TH OF RAMADAN', 'SOHAG', 'MADINAT EL SALAM', 'MADINAT 6TH OCTOBER', 'ELTAL ELKABEER', 'ELKANATER ELKHAYRIA', 'KALIOUB', 'EL GHARBIA', 'EL MENOFIA', 'DAKAHLIA', 'EL SHARKIA', 'EL BEHERA', 'KENA', 'EL QALOUBIA', 'South Sinai', 'North Sinai', 'NEWEBAA', 'ELWADY ELGEDID', 'EL KUWAIT', 'OTHERS']
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
        csv_writer = writer(write_obj, delimi
