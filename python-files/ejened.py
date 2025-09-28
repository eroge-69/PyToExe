import datetime
import win32com.client as win32

def Ejenedelniy():
    try:
        i = 0
        Uglub = ""

        myWord = win32.gencache.EnsureDispatch('Word.Application')
        # Create new document from template
        myDocument = myWord.Documents.Add(r"C:\Шаблоны_отчетов\Еженедельный.docx")
        myWord.Visible = True

        excel = win32.gencache.EnsureDispatch('Excel.Application')
        wb = excel.ActiveWorkbook
        ws = excel.ActiveSheet

        # Sort data by column A5 ascending with header
        last_row = ws.Range("A3").Value + 4
        sort_range = ws.Range(ws.Cells(4, 1), ws.Cells(last_row, 13))
        sort_range.Sort(Key1=ws.Range("A5"), Order1=1, Header=1)  # 1 = xlAscending, Header=1 means xlYes

        # Collect data for analysis from columns 19 to 22 (S to V)
        for i in range(5, last_row + 1):
            Uglub += f"{ws.Cells(i, 19).Value} {ws.Cells(i, 20).Value} {ws.Cells(i, 21).Value} {ws.Cells(i, 22).Value}\r\r"

        # Fill bookmarks in Word document
        with myDocument:
            # Date range 6 days ago to today
            myDocument.Bookmarks("Дата_отчета").Range.Text = (datetime.datetime.now() - datetime.timedelta(days=6)).strftime("%d.%m") + "-" + datetime.datetime.now().strftime("%d.%m.%Y")
            myDocument.Bookmarks("Колво_отключений").Range.Text = str(ws.Range("A3").Value)
            myDocument.Bookmarks("Углуб_анализ").Range.Text = Uglub
            myDocument.Bookmarks("Период_AirFASE").Range.Text = (datetime.datetime.now() - datetime.timedelta(days=9)).strftime("%d.%m") + "-" + (datetime.datetime.now() - datetime.timedelta(days=3)).strftime("%d.%m.%Y")
            myDocument.Bookmarks("Период_СС").Range.Text = (datetime.datetime.now() - datetime.timedelta(days=9)).strftime("%d.%m") + "-" + (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%d.%m.%Y")

            # Copy table with disconnections from Excel and paste into Word bookmark
            ws.Range(ws.Cells(4, 18), ws.Cells(last_row, 23)).Copy()
            myDocument.Bookmarks("Таблица_отключений").Range.PasteExcelTable(False, False, False)
            myDocument.Range.Font.Size = 12

            # Copy table with outages from Excel and paste into Word bookmark
            ws.Range(ws.Cells(4, 43), ws.Cells(ws.Range("AD3").Value + 4, 49)).Copy()
            myDocument.Bookmarks("Таблица_уходы").Range.PasteExcelTable(False, False, False)
            myDocument.Range.Font.Size = 12

            # Set paragraph spacing after to 0
            myDocument.Range.ParagraphFormat.SpaceAfter = 0

            # Set first row of tables as header rows
            myDocument.Tables(1).Rows(1).HeadingFormat = True
            myDocument.Tables(2).Rows(1).HeadingFormat = True

        # Cleanup
        myDocument = None
        myWord = None

    except Exception as e:
        import pythoncom
        pythoncom.CoInitialize()
        print(f"Произошла ошибка: {e}")
        if 'myWord' in locals() and myWord is not None:
            myWord.Quit()
            myDocument = None
            myWord = None