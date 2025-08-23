import win32print
from datetime import date, timedelta

PRINTER_NAME = "ZDesigner ZD420-203dpi ZPL2"

def main():
    try:
        copies = int(input("������� �������� ��������? "))
    except ValueError:
        print("����� ������ �����!")
        return

    # ���������� ����
    tomorrow = date.today() + timedelta(days=1)
    label_date = tomorrow.strftime("%d.%m")

    pw = 320   # ������ (40 �� ��� 203 dpi)
    ll = 240   # ������ (30 �� ��� 203 dpi)

    zpl = f"""^XA
^PW{pw}
^LL{ll}
^LH0,0
^CF0,60
^FO0,70^FB{pw},1,0,C,0
^FD{label_date}^FS
^PQ{copies}
^XZ
"""

    hPrinter = win32print.OpenPrinter(PRINTER_NAME)
    try:
        hJob = win32print.StartDocPrinter(hPrinter, 1, ("ZPL Label", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)
        win32print.WritePrinter(hPrinter, zpl.encode("utf-8"))
        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)
        print(f"�������� ({copies} ��.) ���������� �� ������ � {PRINTER_NAME}")
    finally:
        win32print.ClosePrinter(hPrinter)

if name == "__main__":
    main()