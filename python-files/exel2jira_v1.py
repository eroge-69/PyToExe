import pyperclip as pyc
import re

work = True
print("Format buffer copied from excel to jira table.")
print("Copy area from excel page, then press enter.")
while work:
    # разделение строк по CR или LF
    regex = re.compile(r"[\r\n]")
    # разделить поля по TAB (for excel)
    wht_sp = re.compile("[\t]")
    # фильтровать массив если не буквенно-цифровое
    row_filter = re.compile("\W")
    print("1 = format first row in bold as headers")
    print("2 = format first column in bold as headers")
    print("3 = format first row & first column in bold as headers")
    print("4 = format all cells in bold")
    print("0 = exit\n any other string = format all rows by default")
    inp = input()
    if inp != "0":
        col_headers = False
        all_headers = False
        row_headers = False
        # флаг заголовка столбцов
        if inp == "1" or inp == "3":
            col_headers = True
        # флаг заголовка строк
        if inp == "2" or inp == "3":
            row_headers = True
        if inp == "4":
            all_headers = True
        # копировать из буфера
        s = pyc.paste()
        if len(s) > 1:
            # split rows
            rows = regex.split(s)
            # remove null
            rows = filter(lambda x: row_filter.sub("", x), rows)
            new_rows = ""
            rows_a = []
            max_len = 0
            for row in rows:
                # split row to fields
                row_arr = wht_sp.split(row)
                # excel пустые не фильтруем, таблицы могут содержать пустые ячейки.
                # row_arr = list(filter(lambda t: row_filter.sub("", t), row_arr))
                rows_a.append(row_arr)
                ln = len(row_arr)
                if ln > max_len:
                    max_len = ln
                
            for row in rows_a:
                x = 0
                new_row = ""
                for s in row:
                    if all_headers:
                        split_char = " ||"
                    elif col_headers:
                        split_char = " ||"
                    elif row_headers:
                        if x == 0:
                            split_char = " ||"
                        else:
                            split_char = " |"
                    else:
                        split_char = " |"
                    new_row = new_row + split_char + s
                    x += 1
                new_row += split_char
                while x < max_len:
                    new_row += split_char
                    x += 1
                new_row += "\n"
                new_rows += new_row
                col_headers = False
                print(new_row, end="")
            print("------------This copied to buffer-------------")
            # copy string
            pyc.copy(new_rows)
            # paste to buffer
            pyc.paste()
    else:
        work = False
