#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().run_cell_magic('time', '', "import pandas as pd\n\nfrom pandas import ExcelWriter\nfrom pandas import ExcelFile\n\nfrom openpyxl import load_workbook\nfrom openpyxl.utils.cell import range_boundaries\n\nimport numpy as np\nimport os as os\nimport re\n\nfrom datetime import datetime\nst_time = datetime.now()\nprint('Начало цикла: ',st_time)\n\nimport time\ntime.sleep(0) # sleep for two seconds\n\npd.set_option('display.max_rows', 200)\npd.set_option('display.max_columns', None)\n\nimport locale\nlocale.setlocale(locale.LC_ALL, '')\n'ru_RU.UTF-8'\ngen_start = datetime.now()")


# In[2]:


names = ["Доходы 2025 3Q", "Доходы 2025 2Q", "Доходы 2025 1Q",
         "Доходы 2024 4Q", "Доходы 2024 3Q", "Доходы 2024 2Q", "Доходы 2024 1Q",
         "Доходы 2023 4Q", "Доходы 2023 3Q", "Доходы 2023 2Q", "Доходы 2023 1Q",
         "Доходы 2022 4Q", "Доходы 2022 3Q", "Доходы 2022 2Q", "Доходы 2022 1Q" ]
#print(len(names))

name = names[3] # Вот здесь менять!


path="P:/ДЭ/!ДОХОДЫ/для СВОДов/" + name + ".xlsx"
print(path)
year = re.findall(r'\b\d+\b', name)[0]
print("Год: ",year)

stats = os.stat(path)
print(name,'\n',locale.format('%d', stats.st_size/1024/1024, grouping=True),' mb')


# In[ ]:


get_ipython().run_cell_magic('time', '', 'print(datetime.now())\ndf1=pd.read_excel(path,skiprows=0, index_col=None, sheet_name="СВОД")\n\nprint(df1.shape)')


# In[ ]:


df1.dtypes


# In[ ]:


print('Выр РУБ: ',locale.format('%d', df1['Выручка РУБ'].sum(), grouping=True))
print('Кол-во:  ',locale.format('%d', df1['Кол-во'].sum(), grouping=True))
print('ДГ.TEU:  ',locale.format('%d', df1['ДГ.TEU'].sum(), grouping=True))
print('ДГ.TEU(прр):',locale.format('%d',df1[df1['Вид работ 1']== 'ПРР']['ДГ.TEU'].sum(), grouping=True))
print('ДГ.Вес:  ',locale.format('%d', df1['ДГ.Вес'].sum(), grouping=True))


# In[ ]:


get_ipython().run_cell_magic('time', '', '#df1 = DB.copy(deep=True)\n#df1=df1.drop(columns=["Дата окончания хранения", "Дата начала хранения", "Регистратор.Дата"])\n\n\n\ndf1["Направление_уделки"] = np.where(df1[\'Направление2\'] == "Импорт" ,    "Импорт",\n    np.where(df1[\'Направление2\'] == "Экспорт",    "Экспорт",\n    np.where(df1[\'ДГ.Фронт прибытия\'] == "Море каботаж", "Каботаж",\n    np.where(df1[\'ДГ.Фронт убытия\'] == "Море каботаж",   "Каботаж", "Внутриросс"))))\n\ndf1["ДГ.ФРОНТЫ"] = df1["ДГ.Фронт прибытия"] + " - " + df1["ДГ.Фронт убытия"]')


# In[ ]:


df1['ДГ.Наполненность'] = np.where(~pd.isnull(df1['ДГ.Наполненность']), df1['ДГ.Наполненность'], df1['Наполненость'])
df1['ДГ.Футовость'] = np.where(~pd.isnull(df1['ДГ.Футовость']), df1['ДГ.Футовость'], df1['Футовость'])


# In[ ]:


df1.drop(columns =['Груз.Номенклатура','Футовость','Наполненость','Характеристика'], inplace = True )

df1.rename(columns = {'ДГ.Груз2':'Груз.Номенклатура',
                      'ДГ.Футовость':'ФУТ',
                      'ДГ.Наполненность':'Наполн',
                      'Характеристика.Наименование для печати':'Характеристика',
                      'Партнёр_ВМТП':'ВГО_ДВМП',
                      'Выручка РУБ' : 'Выручка',
                      'ДГ.TEU' : 'TEU',
                      'Партнер':'Партнёр',
                      'Ед. изм.':'Ед изм'}, inplace = True)


# #### Выгружаем Таблицы "спр_партнер_корректный" и  "Пункты_отпр и назн"
# 

# In[ ]:


name_file = "P:/ДЭ/Базы Данных/Выручка/Спарвочник_для_БД.xlsx"
name_sht = 'спр'

stats = os.stat(name_file)
print(name_file,'\n',locale.format('%d', stats.st_size/1024, grouping=True),' kb')


# In[ ]:


#Функция извлечения таблицы:
def extract_tables(ws):
    dfs_tmp = {}
     
    for t_name, table_range in [ws.tables.items()[index]]:
        # Get position of data table
        min_col, min_row, max_col, max_row = range_boundaries(table_range)
        
        # Convert tablet to DataFrame
        table = ws.iter_rows(min_row, max_row, min_col, max_col, values_only=True)
        header = next(table)
        df = pd.DataFrame(table, columns=header)

        dfs_tmp[t_name] = df

    return dfs_tmp


        #Dictionary to store all the dfs in. 
        #Format: {table_name1: df, table_name2: df, ...}
dfs = {}


# In[ ]:


get_ipython().run_cell_magic('time', '', '#Загружаем книгу:\nwb = load_workbook(name_file)\nws = wb.active')


# In[ ]:


name_tbl = 'спр_партнер_корректный'
index = ws.tables.items().index(list(filter(lambda x: x[0] == name_tbl, ws.tables.items()))[0])    
print(ws.tables.items()[index])

# Вызываем функцию извлечения таблицы
for ws in wb.worksheets:
    dfs.update(extract_tables(ws))

# Назначаем таблицу в отдельную переменную
spr_partner = pd.DataFrame(dfs[name_tbl])

spr_partner = spr_partner[['Партнер','Партнер корректный','Код партнера']].dropna(axis=0).rename(columns = {'Код партнера':'Код партнера'}).drop_duplicates(subset = 'Код партнера', keep = 'last')#.drop(columns = 'Код партнера')

print ("spr_partner (строки, колонки) = ",spr_partner.shape)
spr_partner.drop_duplicates(subset = 'Код партнера',keep = 'last',inplace = True)


# In[ ]:


name_tbl = 'Пункты_отпр_и_назн'

index = ws.tables.items().index(list(filter(lambda x: x[0] == name_tbl, ws.tables.items()))[0])    
print(ws.tables.items()[index])

for ws in wb.worksheets:
    dfs.update(extract_tables(ws))

spr_station = pd.DataFrame(dfs[name_tbl])

spr_station = spr_station[['Станция/Порт','Город/Страна','Сервис','RWS (Оформление документов)']].dropna(axis=0).drop_duplicates()
print ("spr_station (строки, колонки) = ",spr_station.shape)

spr_station.shape
spr_station.drop_duplicates(subset = 'Станция/Порт',inplace = True)



# In[ ]:


print (df1[['Кол-во','Выручка','TEU']].fillna(0).astype('int64').sum())


# In[ ]:


#df1['Код партнера'] = df1.astype({'Код партнера': 'str'})
df1.dtypes
#df1['Код партнера'][~pd.isnull(df1['Код партнера'])]
#spr_partner['Код партнера']


# In[ ]:


df1['ДГ.Пункт назначения (убытие)']


# In[ ]:


get_ipython().run_cell_magic('time', '', "print(datetime.now())\nprint(df1.shape)\nprint('ДГ.TEU(прр):',locale.format('%d',df1[df1['Вид работ 1']== 'ПРР']['TEU'].sum(), grouping=True))\ndf2 = df1.join(spr_station.set_index('Станция/Порт'), how='left',on='ДГ.Пункт назначения (убытие)')\nprint(df2.shape)\nprint('ДГ.TEU(прр):',locale.format('%d',df2[df2['Вид работ 1']== 'ПРР']['TEU'].sum(), grouping=True))\ndf2 = df2.join(spr_partner.set_index('Код партнера'), how='left', on='Код партнера') #Менять на Код Партнёра здесь\nprint(df2.shape)\nprint('ДГ.TEU(прр):',locale.format('%d',df2[df2['Вид работ 1']== 'ПРР']['TEU'].sum(), grouping=True))")


# In[ ]:


df2["ВГО_ДВМП"][df2["ВГО_ДВМП"]!='3-и лица']
print('ДГ.TEU(прр):',locale.format('%d',df2[df2['Вид работ 1']== 'ПРР']['TEU'].sum(), grouping=True))

df2['ДГ.грузооборот погрузки']=df2['ДГ.грузооборот погрузки'].astype('datetime64[ns]')
df2['ДГ.грузооборот выгрузки']=df2['ДГ.грузооборот выгрузки'].astype('datetime64[ns]')


# In[ ]:


print('ДГ.TEU(прр):',locale.format('%d',df1[df1['Вид работ 1']== 'ПРР']['TEU'].sum(), grouping=True))


df2["ВГО_ДВМП"] = np.where(df2['ВГО_ДВМП'] == "3-и лица" ,    "3-и лица",df2['Партнёр'])
print('ДГ.TEU(прр):',locale.format('%d',df2[df2['Вид работ 1']== 'ПРР']['TEU'].sum(), grouping=True))

df2['TEU'] = np.where((df2['ДГ.грузооборот погрузки'].dt.strftime('%Y') == year) | (df2['ДГ.грузооборот выгрузки'].dt.strftime('%Y') == year),
                      df2['TEU'],0)
print('ДГ.TEU(прр):',locale.format('%d',df2[df2['Вид работ 1']== 'ПРР']['TEU'].sum(), grouping=True))


# In[ ]:


df1['ДГ.грузооборот погрузки'].replace(to_replace = 0.0, value = ("2018-01-05"))
df1['ДГ.грузооборот погрузки'] = df1['ДГ.грузооборот погрузки'].astype('datetime64[ns]')
df1.dtypes
df1['ДГ.грузооборот погрузки'].dt.strftime('%Y').unique()


# In[ ]:


df1['ДГ.грузооборот погрузки']


# In[ ]:


df2['ДГ.грузооборот погрузки'].dt.strftime('%Y').unique()


# In[ ]:


print('Выр РУБ: ',locale.format('%d', df1['Выручка'].sum(), grouping=True))
print('Выр РУБ: ',locale.format('%d', df2['Выручка'].sum(), grouping=True))

print('Кол-во:  ',locale.format('%d', df1['Кол-во'].sum(), grouping=True))
print('Кол-во:  ',locale.format('%d', df2['Кол-во'].sum(), grouping=True))

print('ДГ.TEU:  ',locale.format('%d', df1['TEU'].sum(), grouping=True))
print('ДГ.TEU:  ',locale.format('%d', df2['TEU'].sum(), grouping=True))

print('ДГ.Вес:  ',locale.format('%d', df1['ДГ.Вес'].sum(), grouping=True))
print('ДГ.Вес:  ',locale.format('%d', df2['ДГ.Вес'].sum(), grouping=True))


# In[ ]:





# In[ ]:


df2['Характеристика'].fillna("", inplace=True)


# In[ ]:


df2['SOC/COC'] = np.where( np.logical_and (df2['Характеристика'].str.contains(r'SOC') ,  df2["Доп. работы (доходы) для ВМТП"] == "Услуги терминала по погрузке/выгрузке контейнера/груза"), 'SOC',
                    np.where( np.logical_and (df2['Характеристика'].str.contains(r'COC') ,  df2["Доп. работы (доходы) для ВМТП"] == "Услуги терминала по погрузке/выгрузке контейнера/груза"), 'COC',
                    np.where(  df2["Доп. работы (доходы) для ВМТП"] == "Услуги терминала по погрузке/выгрузке контейнера/груза", 'SOC/COC', '' )))
                              
    
print('TEU (ПРР):  ',locale.format('%d', df1[df1['Вид работ 1']== 'ПРР']['TEU'].sum(), grouping=True))
print('TEU (ПРР):  ',locale.format('%d', df2[df2['Вид работ 1']== 'ПРР']['TEU'].sum(), grouping=True))


# In[ ]:


df2.dtypes


# In[ ]:


Save_columns = ["Партнёр", "Группа договоров", "Направление", "Подразделение",'Код партнера',
                "Характеристика", "Груз.Номенклатура", 
                "Доп. работы (доходы) для ВМТП", "Ед изм", "Кол-во", 
                "Выручка", "Стивидор", "РУБ/Кол-во", "ВГО", "ВГО_ДВМП", 
                "Направление2", "Груз", "Груз2", "Вид работ 1", "Вид данных", 
                "Период", "ФУТ", 'Наполн',
                "ДГ.Группа аналитического учета", "ДГ.ВКГГ", "TEU", 
                "ДГ.Фронт прибытия", "ДГ.Фронт убытия", "ДГ.Экспедитор", 
                "Направление_уделки", "ДГ.ФРОНТЫ", "Город/Страна", 
                "Сервис", "RWS (Оформление документов)", 
                "SOC/COC"]
df3 = df2[Save_columns]


#df3 = df3.drop(columns = 'Груз.Номенклатура')
#df3 = df3.rename(columns = {'ДГ.Груз2' : 'Груз.Номенклатура',
#                            'ДГ.Футовость' : 'ФУТ',
#                            'ДГ.Наполненность' : 'Наполн',
#                            'Характеристика.Наименование для печати': 'Характеристика',
#                            'ВГО_ДВМП' : 'Партнёр_ВМТП',
#                            'Выручка РУБ' : 'Выручка',
#                           'TEU' : 'TEU' })
df3["БД"] = "ФАКТ "+year+"_ext"

print('TEU (ПРР):  ',locale.format('%d', df1[df1['Вид работ 1']== 'ПРР']['TEU'].sum(), grouping=True))
print('TEU (ПРР):  ',locale.format('%d', df3[df3['Вид работ 1']== 'ПРР']['TEU'].sum(), grouping=True))


# ## Группировка

# In[ ]:


df3_Columns = [ 'БД',
                'Период',
                'Партнёр',
                'Код партнера',
                'Груз',
                'Груз2',
                'Груз.Номенклатура',
                'ФУТ',
                'Наполн',
                'Направление',
                'Направление2',
                'Подразделение',
                'Вид работ 1',
                'Доп. работы (доходы) для ВМТП',
                'Характеристика',
                'Стивидор',
                'ВГО',
                'ВГО_ДВМП',
                'Ед изм',
                'РУБ/Кол-во',
                'Кол-во',
                'Выручка',
                'TEU',
                'Группа договоров',
                'Вид данных',
                'ДГ.Группа аналитического учета',
                'ДГ.ВКГГ',
                'ДГ.Фронт прибытия',
                'ДГ.Фронт убытия',
                'ДГ.Экспедитор',
                'Направление_уделки',
                'ДГ.ФРОНТЫ',

                "Город/Страна","Сервис",
                "RWS (Оформление документов)", "SOC/COC"]

df3_Columns.remove('Кол-во')
df3_Columns.remove('Выручка')
df3_Columns.remove('TEU')
print('TEU (ПРР):  ',locale.format('%d', df1[df1['Вид работ 1']== 'ПРР']['TEU'].sum(), grouping=True))
print('TEU (ПРР):  ',locale.format('%d', df3[df3['Вид работ 1']== 'ПРР']['TEU'].sum(), grouping=True))


# In[ ]:


get_ipython().run_cell_magic('time', '', "print(datetime.now())\n\n# ['Кол-во','Выручка РУБ','ДГ.TEU']\ndf3[['Кол-во','Выручка','TEU']].fillna(0).astype('float64')\ndf4 = df3[df3_Columns+['Кол-во','Выручка','TEU']]\ndf4 = df4.fillna( value = 0 )\nprint (df4.shape)\nrev_1 = df3['Выручка'].astype('float64').sum().round(4)\ndf4['Период'] = pd.to_datetime(df4['Период'],errors='coerce')\ndf4['Период'] = df4['Период'].dt.strftime('%Y-%m-01')\n\n#df4 = df4.groupby(df3_Columns).aggregate({'Кол-во':'sum','Выручка':'sum','TEU':'sum'}).reset_index()\n#df4 = df4.pivot_table(  values=['Кол-во','Выручка','TEU'], index = df3_Columns,  aggfunc=np.sum)\n#df4=df4.groupby(['Кол-во','Выручка','TEU']  ).sum()\n\ndf4=df4.groupby(df3_Columns, ).agg({'Кол-во':'sum','Выручка':'sum','TEU':'sum'}).reset_index()    \nprint (df4.shape)\n\nrev_2= df4['Выручка'].astype('float64').sum().round(4)\nprint ( rev_1)\nprint ( rev_2)\nprint ('Проверка: ', rev_1==rev_2)")


# In[ ]:





# In[ ]:


print('Выр РУБ: ',locale.format('%d', df1['Выручка'].sum(), grouping=True))
print('Выр РУБ: ',locale.format('%d', df4['Выручка'].sum(), grouping=True))

print('Кол-во:  ',locale.format('%d', df1['Кол-во'].sum(), grouping=True))
print('Кол-во:  ',locale.format('%d', df4['Кол-во'].sum(), grouping=True))

print('ДГ.TEU:  ',locale.format('%d', df1['TEU'].sum(), grouping=True))
print('ДГ.TEU:  ',locale.format('%d', df4['TEU'].sum(), grouping=True))

print('TEU (ПРР):  ',locale.format('%d', df1[df1['Вид работ 1']== 'ПРР']['TEU'].sum(), grouping=True))
print('TEU (ПРР):  ',locale.format('%d', df4[df4['Вид работ 1']== 'ПРР']['TEU'].sum(), grouping=True))

#print('ДГ.Вес:  ',locale.format('%d', df1['ДГ.Вес'].sum(), grouping=True))
#print('ДГ.Вес:  ',locale.format('%d', df4['Тонн'].sum(), grouping=True))


# In[ ]:


get_ipython().run_cell_magic('time', '', 'f_name = "P:/ДЭ/!ДОХОДЫ/для СВОДов/"+name+"_для_БД"+".xlsx"\nsht_name = \'БД\'\nt_name = \'БД\'\n\n# Create a Pandas Excel writer using XlsxWriter as the engine.\nwriter = pd.ExcelWriter(f_name, engine=\'xlsxwriter\')\n# Get the xlsxwriter workbook and worksheet objects.\nworkbook = writer.book  \n    \n# Write the dataframe data to XlsxWriter. Turn off the default header and\n# index and skip one row to allow us to insert a user defined header.\ndf4.to_excel(writer,sheet_name=sht_name, startrow=1, header=False, index=False)\n\n# Order the columns if necessary.\n#df = df[[\'Rank\', \'Country\', \'Population\']]\nworksheet = writer.sheets[sht_name]\n\n\n# Get the dimensions of the dataframe.\n(max_row, max_col) = df4.shape\n\n# Create a list of column headers, to use in add_table().\ncolumn_settings = [{\'header\': column} for column in df4.columns]\n\n# Add the Excel table structure. Pandas will add the data.\nworksheet.add_table(0, 0, max_row, max_col - 1, {\'columns\': column_settings,\'name\' : t_name})\n\n# Make the columns wider for clarity.\nworksheet.set_column(0, max_col - 1, 12) \n    \nwriter.save()\nwriter.close()\nprint (f_name)')


# In[ ]:


gen_end = datetime.now()
print ('Начало цикла: ',gen_start)
print ('Конец  цикла: ',gen_end)
print ('Время  цикла: ',gen_end - gen_start)


# In[ ]:


print(df1['Выручка'].sum())
print(df4['Выручка'].sum())
print(df1[df1['Вид работ 1']== 'ПРР']['TEU'].sum())
print(df4[df4['Вид работ 1']== 'ПРР']['TEU'].sum())
print(df4.shape)
#print(df4[df4['Код партнера'] == '00-00002296']['Выручка'].sum())
#print(df4[df4['Код партнера'] == '00-00000012']['Выручка'].sum())


# 

# In[ ]:




