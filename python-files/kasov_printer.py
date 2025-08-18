Python 3.13.7 (tags/v3.13.7:bcee1c3, Aug 14 2025, 14:15:11) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
pyinstaller
Traceback (most recent call last):
  File "<pyshell#0>", line 1, in <module>
    pyinstaller
NameError: name 'pyinstaller' is not defined
pyinstaller
Traceback (most recent call last):
  File "<pyshell#1>", line 1, in <module>
    pyinstaller
NameError: name 'pyinstaller' is not defined
Перфектно 👍 тогава значи ще вървим на **USB връзка с ESC/POS** 🎯

Това, което трябва да направиш:

---

### 1. Инсталирай нужните библиотеки:

```bash
pip install python-escpos pyusb
```

---

### 2. Намери **Vendor ID** и **Product ID** на твоя принтер:

* Свържи го с USB
* Отвори `Device Manager` → `USB Devices`
* В "Details" → `Hardware Ids` ще видиш нещо като:

```
USB\VID_0416&PID_5011
```

👉 Там **VID = 0416** (VendorID), **PID = 5011** (ProductID).

---

### 3. Код за печат на касова бележка:

```python
from escpos.printer import Usb
import datetime

# Сложи твоите VID и PID тук!
VENDOR_ID = 0x0416
PRODUCT_ID = 0x5011

# Свързване с принтера
printer = Usb(VENDOR_ID, PRODUCT_ID, 0, 0x81, 0x03)

def print_receipt(items):
    subtotal = sum(price for _, price in items)
    vat = subtotal * 0.20
    total = subtotal + vat

...     # Заглавие
...     printer.set(align="center", bold=True, double_height=True)
...     printer.text("КАСОВА БЕЛЕЖКА\n")
...     printer.set(align="center", bold=True)
...     printer.text("Джоб чек - 70 ЕООД\n")
...     printer.text("ЕИК/ДДС: 206318702\n")
...     printer.text("гр. София, р-н Сердика, бл. 41\n")
...     printer.text("--------------------------------\n")
... 
...     # Артикули
...     printer.set(align="left", bold=False)
...     for item, price in items:
...         line = f"{item:<15}{price:>7.2f} лв\n"
...         printer.text(line)
... 
...     printer.text("--------------------------------\n")
...     printer.text(f"Междинна сума: {subtotal:.2f} лв\n")
...     printer.text(f"ДДС (20%):     {vat:.2f} лв\n")
...     printer.text(f"Общо:          {total:.2f} лв\n")
...     printer.text("--------------------------------\n")
... 
...     # Дата
...     printer.text("Дата: " + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S") + "\n")
...     printer.text("Благодарим Ви за покупката!\n\n")
... 
...     # Отрязване на бележката
...     printer.cut()
... 
... # Примерни артикули
... items = [
...     ("Хляб", 1.20),
...     ("Мляко", 2.30),
...     ("Сирене", 5.80)
... ]
... 
... print_receipt(items)
... ```
... 
