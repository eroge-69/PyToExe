#!/usr/bin/env python
# coding: utf-8

# <h1>Table of Contents<span class="tocSkip"></span></h1>
# <div class="toc"><ul class="toc-item"></ul></div>

# In[1]:


#pip
get_ipython().system('pip install python-docx')
get_ipython().system('pip install pywin32')
get_ipython().system('pip install openpyxl')


# In[2]:


#импорты
import os
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import win32com.client as win32
import tkinter as tk
from openpyxl import load_workbook
from tkinter import filedialog as fd
#win32.gencache.EnsureDispatch("Excel.Application")
#win32.gencache.EnsureDispatch("Word.Application")


# In[3]:


#открытие excel-файла
# Создать корневое окно:  
root = tk.Tk()
root.title('Tkinter Open File Dialog')
root.resizable(False, False)
root.geometry('300x150')  
  
# Определить функцию для выбора файла:  
def select_file():  
    global file
    filetypes = (("Excel files", "*.xlsx;*.xls;*.xlsm"), ('Все файлы', '*.*'))
    file = fd.askopenfilename(title='Открыть Excel-файл', initialdir='/', filetypes=filetypes)
    os.startfile(file)
    root.destroy()
  
# Создать кнопку открытия файла:  
open_button = tk.Button(root, text='Открыть Excel-файл с расчетами', command=select_file)  
open_button.pack(expand=True)  
  
# Запустить приложение:  
root.mainloop()

workbook = load_workbook(file, data_only = True)


# In[4]:


# Создать корневое окно:  
root = tk.Tk()
root.title('Выбор Word-файла')
root.resizable(False, False)
root.geometry('300x150')  
  
# Определить функцию для выбора файла:  
def select_file():  
    global selected_file_path
    filetypes = (("Word files", "*.docx;*.doc;*.docm"), ("Все файлы", "*.*"))
    selected_file_path = fd.askopenfilename(title='Открыть Word-файл', initialdir='/', filetypes=filetypes)
    
    if selected_file_path:  # Проверяем, что файл был выбран
        print(f"Выбран файл: {selected_file_path}")
        # os.startfile(selected_file_path)  # Раскомментируйте, если нужно открыть файл
    else:
        print("Файл не выбран")
    
    root.destroy()
  
# Создать кнопку открытия файла:  
open_button = tk.Button(root, text='Выбрать Word-файл template-2.docx', command=select_file)  
open_button.pack(expand=True)  
  
# Запустить приложение:  
root.mainloop()


# In[5]:


#шритф для заголовка 1
def heading_1(item):
    sel.Style = "Заголовок 1"
    sel.TypeText(item)
    sel.TypeParagraph()
    
#шрифт обычный
def osnova(item):
    sel.Style = "Обычный"
    sel.TypeText(item)
    sel.TypeParagraph()
    
#шрифт обычный жирный
def osnova_gir(item):
    sel.Style = "Обычный жирный"
    sel.TypeText(item)
    sel.TypeParagraph()

#шрифт для заголовка 2
def heading_2(item):
    sel.Style = "Заголовок 2"
    sel.TypeText(item)
    sel.TypeParagraph()
    
#шрифт для заголовка 3
def heading_3(item):
    sel.Style = "Заголовок 3"
    sel.TypeText(item)
    sel.TypeParagraph()
    
#шрифт для заголовка 4
def heading_4(item):
    sel.Style = "Заголовок 4"
    sel.TypeText(item)
    sel.TypeParagraph()
    
#шрифт списка с точкой
def spisok_toch(item):
    sel.Style = "список с точкой"
    sel.TypeText(item)
    sel.TypeParagraph()
    
#шрифт для ссылок
def ssylki(item):
    sel.Style = "ссылки"
    sel.TypeText(item)
    sel.TypeParagraph()
    
#добавление номера таблицы    
def insert_table_caption(word_app, word_text=" Название таблицы"):
    sel = word_app.Selection
    sel.Style = "Обычный жирный"
    sel.ParagraphFormat.Alignment = 0  # Центрирование

    # Вставка текста "Таблица "
    sel.Font.Bold = True
    sel.TypeText("Таблица ")
    #sel.Font.Bold = True

    # Вставка поля STYLEREF "Заголовок 1"
    sel.Fields.Add(sel.Range, Type= -1, Text='STYLEREF "Заголовок 1" \\n \\* MERGEFORMAT')

    # Вставка точки
    sel.TypeText(".")

    # Вставка поля SEQ Таблица
    sel.Fields.Add(sel.Range, Type= -1, Text='SEQ Таблица \\* ARABIC \\s 1')

    # Вставка пробела и текста подписи
    sel.TypeText(word_text)
    sel.TypeParagraph()
    
#добавление номера рисунка    
def insert_graf_caption(word_app, word_text=" Название рисунка"):
    sel = word_app.Selection
    sel.Style = "Обычный жирный"
    sel.ParagraphFormat.Alignment = 0  # Центрирование

    # Вставка текста "Рисунок "
    sel.Font.Bold = True
    sel.TypeText("Рисунок ")
    #sel.Font.Bold = True

    # Вставка поля STYLEREF "Заголовок 1"
    sel.Fields.Add(sel.Range, Type= -1, Text='STYLEREF "Заголовок 1" \\n \\* MERGEFORMAT')

    # Вставка точки
    sel.TypeText(".")

    # Вставка поля SEQ Таблица
    sel.Fields.Add(sel.Range, Type= -1, Text='SEQ Рисунок \\* ARABIC \\s 1')

    # Вставка пробела и текста подписи
    sel.TypeText(word_text)
    sel.TypeParagraph()


# In[6]:


#вставка таблицы
def table(excel, word, doc, file, sheet_name, range_address):
    #workbook = excel.Workbooks.Open(excel_path)
    sheet = workbook.Sheets(sheet_name)
    sheet.Range(range_address).Copy()

    sel = word.Selection
    sel.EndKey(Unit=6)  # Перемещение в конец документа
    sel.Paste()

    if sel.Tables.Count == 0:
        workbook.Close(SaveChanges=False)
        raise RuntimeError("Не удалось вставить таблицу из Excel.")

    table = sel.Tables(sel.Tables.Count)
    
    # Автоматическая ширина по содержимому
    #table.AutoFitBehavior(2)  # wdAutoFitContent

    page_width = doc.PageSetup.PageWidth
    left_margin = doc.PageSetup.LeftMargin
    right_margin = doc.PageSetup.RightMargin
    usable_width = page_width - left_margin - right_margin

    table.PreferredWidthType = 1  # wdPreferredWidthPoints
    table.PreferredWidth = usable_width
    table.AutoFitBehavior(2)  # wdAutoFitWindow

    if table.Rows.Count > 0:
        table.Rows(1).HeadingFormat = True

    for row in table.Rows:
        row.HeightRule = 1  # wdRowHeightExactly
        row.Height = 1

        for cell in row.Cells:
            cell.LeftPadding = 5
            cell.RightPadding = 5
            
            para_format = cell.Range.ParagraphFormat
            para_format.SpaceBefore = 0
            para_format.SpaceAfter = 0

    # Удаление пробелов по краям текста в ячейках таблицы
    for row in table.Rows:
        for cell in row.Cells:
            text = cell.Range.Text.strip()  # .Text включает управляющие символы
            # Удаляем управляющий символ конца ячейки (обычно это '\r\a' или chr(7))
            cleaned_text = text.rstrip('\r\x07').strip()
            cell.Range.Text = cleaned_text
            
#вставка графика
def grafic(sheet_name, number):
    # Открываем Excel-книгу и лист
    wb = excel.Workbooks.Open(file)
    ws = wb.Sheets(sheet_name)

    # Получаем объект графика
    chart_objects = ws.ChartObjects()
    if number < 1 or number > chart_objects.Count:
        wb.Close(False)
        raise IndexError(f"График с номером {number} не найден на листе '{sheet_name}'")

    chart_object = chart_objects(number)
    chart_object.Copy()

    # Вставляем график в конец документа
    content_range = doc.Content
    content_range.Collapse(0)  # wdCollapseEnd = 0
    content_range.Paste()

    # Вставляем перенос строки после графика
    content_range.InsertAfter("\r")

    # Перемещаем курсор в конец документа (на новую строку)
    selection = word.Selection
    selection.EndKey(Unit=6)  # 6 = wdStory (конец документа)


# In[7]:


# Пути к файлам
#excel_path = r"C:\Users\Татьяна\Projects\Оценка\шаблон расчетов АФК3.xlsx"
#word_path = r"C:\Users\Татьяна\Projects\Оценка\template-2.docx"
word_path = selected_file_path

# Запуск Excel и открытие файла
excel = win32.gencache.EnsureDispatch('Excel.Application')
excel.Visible = False

# Запуск Word
word = win32.gencache.EnsureDispatch('Word.Application')
word.Visible = False
doc = word.Documents.Open(word_path)


# In[8]:


#раздел 5.1
sel = word.Selection

heading_1('Анализ финансово-хозяйственной деятельности Общества')
osnova('Целью проведения анализа является определение текущего положения, \
тенденций развития и степени финансовых рисков, характерных для деятельности анализируемого Общества.')

workbook = excel.Workbooks.Open(file)
sheet = workbook.Sheets("техтаблицы")
nach = str(int(sheet.Range("B27").Value))
kon = str(sheet.Range("B28").Value)
osnova('В ходе проведения финансового анализа Общества исследовалась динамика финансового положения предприятия \
в течение '+nach+'–'+kon+' гг. Основными источниками информации служила официальная бухгалтерская отчетность предприятия: \
"Бухгалтерский баланс" (форма 1) с приложениями, "Отчет о финансовых результатах" (форма 2).')
osnova('Анализ финансового состояния компании включает в себя следующие основные части:')
spisok_toch('анализ структуры показателей предприятия (анализ активов, анализ пассивов);')
spisok_toch('анализ показателей ликвидности и финансовой устойчивости;')
spisok_toch('анализ доходов и расходов;')
spisok_toch('анализ показателей деловой активности и рентабельности.')
osnova('Необходимо отметить, что для целей анализа было проведено преобразование отчетности Общества.')

heading_2('Методика финансового анализа. Трансформация финансовых отчетов')
osnova('Исходные финансовые отчеты в настоящем Отчете об оценке преобразованы в такую форму, \
которая является общепринятой в западной практике бухгалтерского учета.')
osnova('Трансформация финансовых отчетов позволяет объединить их отдельные статьи по принципу \
общего экономического содержания и полученный таким образом, анализ агрегированных финансовых \
показателей дает четкое и понятное всем потенциальным инвесторам представление о финансовом положении предприятия.')
heading_3('Активы')
heading_4('Оборотные активы')
osnova('В первой части активов показана наиболее ликвидная их часть – оборотные активы.')
osnova('Оборотные активы включают в себя денежные средства, финансовые вложения (строка 1240), \
дебиторскую задолженность, материально-производственные запасы и прочие оборотные активы. \
Перечисленные выше группы расположены по принципу убывания их ликвидности.')
spisok_toch('Денежные средства равны сумме денежных средств, которыми располагает \
предприятие на дату составления баланса (строка 1250 исходного баланса).')
spisok_toch('Финансовые вложения равны сумме краткосрочных финансовых вложений исходного баланса (строка 1240).')
spisok_toch('Дебиторская задолженность равняется сумме счетов по строке 1230.')
spisok_toch('Налог на добавленную стоимость равняется сумме счетов по строке 1220.')
spisok_toch('Запасы включают в себя сумму счетов по строке 1210.')
spisok_toch('Прочие оборотные активы равняются строке 1260 исходного баланса.')

heading_4('Внеоборотные активы')
osnova('Второй раздел активов трансформированного баланса составляют внеоборотные активы – наименее ликвидная часть активов.')
spisok_toch('Основные средства включают в себя основные средства и незавершенное строительство по строке 1150.')
spisok_toch('Нематериальные активы равны остаточной стоимости нематериальных активов исходного баланса (строка 1110).')
spisok_toch('Прочие внеоборотные активы равны сумме строк 1190 и 1180 исходного баланса.')
spisok_toch('Финансовые вложения равны сумме долгосрочных финансовых вложений исходного баланса (строка 1170).')

heading_3('Капитал и обязательства')
osnova('В пассивах трансформированного баланса все средства, используемые предприятием для финансирования \
своей деятельности, делятся на собственные и заемные.')
heading_4('Обязательства')
osnova('Обязательства представляют собой величину заемных средств, которыми пользуется предприятие, \
они подразделяются по срокам погашения долгов: краткосрочные обязательства перед банком, государством, \
коллективом, покупателями, поставщиками, другими кредиторами; и долгосрочная задолженность.')
osnova_gir('Краткосрочные обязательства')
osnova('Краткосрочные обязательства включают в себя сумму краткосрочных заемных средств (строка 1510 исходного баланса), величину кредиторской задолженности по расчетам за товары \
и услуги, по оплате труда, по социальному страхованию и обеспечению, по внебюджетным платежам \
(строка 1520 суммарно исходного баланса), а также сумму прочих обязательств \
(сумма строк 1530, 1540 и 1550 исходного баланса).')
osnova_gir('Долгосрочные обязательства')
osnova('Долгосрочные обязательства включают в себя сумму долгосрочных заемных средств \
(строка 1410 исходного баланса), резервы под условные обязательства и прочие долгосрочные \
обязательства аналогичны строкам 1420, 1430 и 1450 исходного баланса соответственно.')

heading_4('Собственный капитал')
osnova('Собственный капитал представляет собой те средства, которые были вложены в предприятие \
его учредителями и накопленную за годы его функционирования прибыль. Величина собственного \
капитала равняется сумме уставного и добавочного капитала (строки 1310, 1350 исходного баланса), \
а также тех статей баланса, сформированных за счет прибыли, сумма которых и дает накопленную прибыль \
(сумма строк 1360 и 1370 исходного баланса).')

heading_3('Определения аналитических коэффициентов финансового состояния и эффективности')
osnova('Аналитические коэффициенты финансового состояния и эффективности рассчитывались \
на основе трансформированных баланса и отчета о прибылях и убытках.')

insert_table_caption(word, " Расчет аналитических коэффициентов")

#workbook = excel.Workbooks.Open(excel_path)


sheet_name = "техтаблицы"
range_address = "A1:B21"
table(excel, word, doc, file, sheet_name, range_address)


# In[9]:


#раздел 5.2
heading_2('Анализ финансово-хозяйственной деятельности оцениваемого Общества')
insert_table_caption(word, " Бухгалтерский баланс Форма 1, тыс. руб.")
sheet_name = "Баланс"
range_address = "B5:H48"
table(excel, word, doc, file, sheet_name, range_address)
ssylki('Источник: Бухгалтерский баланс Общества')

heading_3('Активы')

insert_graf_caption(word, " Структура активов Общества, тыс. руб.")
grafic("Баланс",1)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

insert_table_caption(word, " Преобразованный баланс (активы) Общества, тыс. руб.")
sheet_name = "Ан-з бал."
range_address = "B5:G20"
table(excel, word, doc, file, sheet_name, range_address)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

insert_table_caption(word, " Темп прироста активов (по сравнению с предыдущим периодом), %")
sheet_name = "Ан-з бал."
range_address = "B37:F52"
table(excel, word, doc, file, sheet_name, range_address)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

insert_table_caption(word, " Структура внеоборотных активов, %")
sheet_name = "А и П"
range_address = "B15:G23"
table(excel, word, doc, file, sheet_name, range_address)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

insert_table_caption(word, " Структура оборотных активов, %")
sheet_name = "А и П"
range_address = "B26:G33"
table(excel, word, doc, file, sheet_name, range_address)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

heading_3('Пассивы')

insert_graf_caption(word, " Структура пассивов Общества, %")
grafic("А и П",1)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

insert_table_caption(word, " Преобразованный баланс (пассивы) Общества, тыс. руб.")
sheet_name = "Ан-з бал."
range_address = "B21:G33"
table(excel, word, doc, file, sheet_name, range_address)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

insert_table_caption(word, " Темп прироста пассивов (по сравнению с предыдущим периодом), %")
sheet_name = "Ан-з бал."
range_address = "B53:F65"
table(excel, word, doc, file, sheet_name, range_address)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

insert_table_caption(word, " Структура собственного капитала, %")
sheet_name = "А и П"
range_address = "B58:G62"
table(excel, word, doc, file, sheet_name, range_address)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

insert_table_caption(word, " Структура долгосрочных обязательств, %")
sheet_name = "А и П"
range_address = "B65:G69"
table(excel, word, doc, file, sheet_name, range_address)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

insert_table_caption(word, " Структура краткосрочных обязательств, %")
sheet_name = "А и П"
range_address = "B72:G78"
table(excel, word, doc, file, sheet_name, range_address)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

heading_3('Доходы и расходы')

insert_table_caption(word, " Формирование чистой прибыли Общества, тыс. руб.")
sheet_name = "Баланс"
range_address = "B57:H76"
table(excel, word, doc, file, sheet_name, range_address)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

heading_3('Аналитические коэффициенты')

insert_table_caption(word, " Показатели деловой активности")
sheet_name = "Показатели"
range_address = "B5:H30"
table(excel, word, doc, file, sheet_name, range_address)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

insert_graf_caption(word, " Динамика показателей деловой активности, %")
grafic("Показатели",2)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

insert_table_caption(word, " Коэффициенты рентабельности")
sheet_name = "Показатели"
range_address = "B33:H41"
table(excel, word, doc, file, sheet_name, range_address)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

insert_graf_caption(word, " Динамика показателей рентабельности, %")
grafic("Показатели",3)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

insert_table_caption(word, " Анализ ликвидности баланса")
sheet_name = "Показатели"
range_address = "B49:H64"
table(excel, word, doc, file, sheet_name, range_address)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

insert_table_caption(word, " Коэффициенты платежеспособности")
sheet_name = "Показатели"
range_address = "B67:H75"
table(excel, word, doc, file, sheet_name, range_address)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

insert_graf_caption(word, " Динамика показателей платежеспособности")
grafic("Показатели",4)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

insert_table_caption(word, " Коэффициенты финансовой устойчивости")
sheet_name = "Показатели"
range_address = "B81:H88"
table(excel, word, doc, file, sheet_name, range_address)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

insert_graf_caption(word, " Динамика показателей финансовой устойчивости")
grafic("Показатели",5)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

osnova('Параметр восстановления платежеспособности (КВП) считают, когда показатель текущей ликвидности опускается ниже нормативного значения 2.')
osnova('Параметр утраты платежеспособности КУП считают, когда показатель текущей ликвидности больше или равен 2, а коэффициент обеспеченности собственными средствами больше или равен 0,1.')

#workbook = excel.Workbooks.Open(excel_path)
sheet = workbook.Sheets("техтаблицы")
tab_name = str(sheet.Range("B37").Value)
insert_table_caption(word, tab_name)
sheet_name = "техтаблицы"
range_address = "A24:B25"
table(excel, word, doc, file, sheet_name, range_address)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

insert_table_caption(word, " Итоги расчета коэффициента кредитоспособности")
sheet_name = "Показатели"
range_address = "B92:G98"
table(excel, word, doc, file, sheet_name, range_address)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

insert_table_caption(word, " Значения Z-счета")
sheet_name = "Показатели"
range_address = "B100:F103"
table(excel, word, doc, file, sheet_name, range_address)
ssylki('Источник: Бухгалтерский баланс Общества, анализ АФК-Аудит')

heading_3('Резюме о финансовом состоянии Общества')

osnova('После проведения анализа финансово-хозяйственной деятельности Общества было установлено следующее:')


# In[10]:


def get_save_path(default_name="document.docx"):
    """
    Открывает диалоговое окно для выбора пути и имени файла
    Возвращает полный путь для сохранения или None если отменено
    """
    root = tk.Tk()
    root.withdraw()  # Скрываем основное окно
    root.attributes('-topmost', True)  # Поверх других окон
    
    file_types = [("Word documents", "*.docx"), ("All files", "*.*")]
    
    save_path = fd.asksaveasfilename(
        title="Укажите путь и имя для сохранения файла",
        defaultextension=".docx",
        filetypes=file_types,
        initialfile=default_name
    )
    
    root.destroy()
    return save_path

# Пример использования:
if __name__ == "__main__":
    # Получаем путь от пользователя
    save_path = get_save_path("финанализ4.docx")


# In[11]:


doc.SaveAs(save_path)

