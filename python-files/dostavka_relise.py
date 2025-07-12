import os
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox

class DeliveryApp:
    def __init__(self):
        self.delivery_prices = {
             "Торбеево": 500,
              "Дракино": 700,
            "Салазгорь": 800,
             "Жуково": 900,
              "Никольск": 900,
              "Красноармеец": 1300,
            "Краснополье": 900,
             "Тат.Юнки": 1200,
             "Атюрьево": 1800,
              "Мальцево": 1000,
            "Сургодь": 1000,
             "Красаевка": 1200,
              "Светлый путь": 1300,
            "Варжеляй": 1100,
             "Лопатино": 1200,
              "Хилково": 1100,
            "Ивановка": 1400,
              "Дм.Усад": 1400,
              "Морд.Юнки": 1600,
            "Виндрей": 2000,
             "Носакино": 1500,
              "Усть-Рахмановка": 1600,
            "Кажлодка": 1000,
             "Куликово": 1600,
              "Ст.Пичуры": 1400,
             "Савва": 1100,
              "Самбур": 1000,
            "Шуструй": 1400,
             "Малышево": 1400,
              "Курташки": 1800,
             "Ковылкино": 3000,
              "Зубова поляна": 2500,
            "Краснослободск": 3500,
            "Спасск": 2000
        }

        self.tech_list = [
            "Холодильник",
            "Стиральная машина",
            "Морозильный ларь",
            "Газовая плита",
            "Морозильная камера"
        ]

        self.service_prices = {
            "Помощь с заносом": 300,
            "Занос": 600,
            "Занос второй этаж": 550,
            "Занос третий этаж": 900,
            "Занос четвертый этаж": 1150,
            "Занос пятый этаж": 1350
        }

        self.root = tb.Window(themename="minty")
        self.root.title("Доставка техники")
        self.root.geometry("750x900")
        self.root.resizable(False, False)

        self.address_var = tb.StringVar()
        self.phone_var = tb.StringVar(value="+7 ")
        self.additional_phone_var = tb.StringVar(value="+7 ")
        self.service_var = tb.StringVar()
        self.tech_var = tb.StringVar()
        self.time_var = tb.StringVar()
        self.price_var = tb.StringVar()
        self.total_price_var = tb.IntVar(value=0)

        self.create_widgets()
        self.root.mainloop()

    def create_widgets(self):
        main_frame = tb.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        tb.Label(
            main_frame,
            text="🚛 Доставка бытовой техники RomaExpress",
            font=("Segoe UI", 20, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 10))

        form_frame = tb.LabelFrame(
            main_frame,
            text=" Данные для доставки ",
            bootstyle="info",
            padding=15
        )
        form_frame.pack(fill="x", pady=10)

        tb.Label(form_frame, text="Адрес доставки *", font=("Segoe UI", 11)).pack(anchor="w")
        address_box = tb.Combobox(
            form_frame,
            textvariable=self.address_var,
            values=list(self.delivery_prices.keys()),
            font=("Segoe UI", 11),
            bootstyle="primary"
        )
        address_box.pack(fill="x", pady=5)
        address_box.bind("<<ComboboxSelected>>", self.update_price)

        tb.Label(form_frame, text="Телефон *", font=("Segoe UI", 11)).pack(anchor="w")
        phone_entry = tb.Entry(
            form_frame,
            textvariable=self.phone_var,
            font=("Segoe UI", 11)
        )
        phone_entry.pack(fill="x", pady=5)
        phone_entry.bind('<KeyRelease>', lambda e: self.format_phone(phone_entry, self.phone_var))

        tb.Label(form_frame, text="Доп. телефон", font=("Segoe UI", 11)).pack(anchor="w")
        additional_phone_entry = tb.Entry(
            form_frame,
            textvariable=self.additional_phone_var,
            font=("Segoe UI", 11)
        )
        additional_phone_entry.pack(fill="x", pady=5)
        additional_phone_entry.bind('<KeyRelease>', lambda e: self.format_phone(additional_phone_entry, self.additional_phone_var))

        tb.Label(form_frame, text="Доп. услуга", font=("Segoe UI", 11)).pack(anchor="w")
        service_box = tb.Combobox(
            form_frame,
            textvariable=self.service_var,
            values=list(self.service_prices.keys()),
            font=("Segoe UI", 11),
            bootstyle="primary"
        )
        service_box.pack(fill="x", pady=5)
        service_box.bind("<<ComboboxSelected>>", self.update_price)

        tb.Label(form_frame, text="Вид техники", font=("Segoe UI", 11)).pack(anchor="w")
        tech_box = tb.Combobox(
            form_frame,
            textvariable=self.tech_var,
            values=self.tech_list,
            font=("Segoe UI", 11),
            bootstyle="primary"
        )
        tech_box.pack(fill="x", pady=5)

        tb.Label(form_frame, text="Время доставки", font=("Segoe UI", 11)).pack(anchor="w")
        tb.Entry(
            form_frame,
            textvariable=self.time_var,
            font=("Segoe UI", 11)
        ).pack(fill="x", pady=5)

        price_frame = tb.Frame(main_frame)
        price_frame.pack(fill="x", pady=10)

        tb.Label(
            price_frame,
            text="Стоимость доставки:",
            font=("Segoe UI", 11)
        ).pack(side="left", padx=5)

        tb.Entry(
            price_frame,
            textvariable=self.price_var,
            font=("Segoe UI", 12),
            width=10,
            justify="center"
        ).pack(side="left")
        self.price_var.trace_add("write", lambda *args: self.update_total_price())

        tb.Label(
            price_frame,
            text="Итого:",
            font=("Segoe UI", 11, "bold")
        ).pack(side="left", padx=(20, 5))

        tb.Label(
            price_frame,
            textvariable=self.total_price_var,
            font=("Segoe UI", 14, "bold"),
            foreground="green"
        ).pack(side="left")

        tb.Label(
            price_frame,
            text="руб.",
            font=("Segoe UI", 11)
        ).pack(side="left", padx=5)

        btn_frame = tb.Frame(main_frame)
        btn_frame.pack(fill="x", pady=20)

        tb.Button(
            btn_frame,
            text="Очистить",
            command=self.clear_form,
            bootstyle="danger",
            width=12
        ).pack(side="left", padx=5)

        tb.Button(
            btn_frame,
            text="Печать заявки",
            command=self.print_order,
            bootstyle="success",
            width=15
        ).pack(side="right", padx=5)

        tb.Label(
            main_frame,
            text="* - обязательные поля",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        ).pack(side="bottom", pady=10)

    def format_phone(self, entry, var):
        digits = ''.join(filter(str.isdigit, var.get()))

        if digits.startswith("8"):
            digits = "7" + digits[1:]
        elif not digits.startswith("7"):
            digits = "7" + digits

        digits = digits[:11]
        digits = digits[1:]

        formatted = "+7 "
        if len(digits) >= 1:
            formatted += f"({digits[:3]}"
        if len(digits) >= 4:
            formatted += f") {digits[3:6]}"
        if len(digits) >= 6:
            formatted += f"-{digits[6:8]}"
        if len(digits) >= 8:
            formatted += f"-{digits[8:10]}"

        var.set(formatted)
        entry.icursor(len(formatted))

    def update_price(self, event=None):
        address = self.address_var.get()
        service = self.service_var.get()
        base_price = self.delivery_prices.get(address, 0)
        service_price = self.service_prices.get(service, 0)
        total = base_price + service_price
        self.price_var.set(str(total))
        self.total_price_var.set(total)

    def update_total_price(self, *args):
        try:
            price = int(self.price_var.get())
            if price < 0:
                price = 0
            self.total_price_var.set(price)
        except ValueError:
            self.total_price_var.set(0)

    def clear_form(self):
        self.address_var.set("")
        self.phone_var.set("+7 ")
        self.additional_phone_var.set("+7 ")
        self.service_var.set("")
        self.tech_var.set("")
        self.time_var.set("")
        self.price_var.set("")
        self.total_price_var.set(0)

    def print_order(self):
        if not self.address_var.get() or len(self.phone_var.get()) < 18:
            messagebox.showerror("Ошибка", "Заполните обязательные поля: адрес и телефон")
            return

        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Заявка на доставку</title>
            <style>
                body {{
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 18px;
                    padding: 40px;
                    line-height: 1.6;
                }}
                h1 {{
                    color: #0d6efd;
                    border-bottom: 2px solid #0d6efd;
                    padding-bottom: 10px;
                }}
                .label {{
                    font-weight: bold;
                }}
                .total {{
                    color: green;
                    font-size: 22px;
                    font-weight: bold;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <h1>🚛 Заявка на доставку</h1>
            <p><span class="label">Адрес:</span> {self.address_var.get()}</p>
            <p><span class="label">Телефон:</span> {self.phone_var.get()}</p>
            <p><span class="label">Доп. телефон:</span> {self.additional_phone_var.get()}</p>
            <p><span class="label">Техника:</span> {self.tech_var.get()}</p>
            <p><span class="label">Доп. услуга:</span> {self.service_var.get()}</p>
            <p><span class="label">Время доставки:</span> {self.time_var.get()}</p>
            <p class="total">ИТОГО: {self.total_price_var.get()} руб.</p>
        </body>
        </html>
        """

        filename = "заявка.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)

        try:
            os.startfile(filename)
            messagebox.showinfo("Успешно", "Заявка отправлена на печать!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось напечатать: {e}")


if __name__ == "__main__":
    app = DeliveryApp()
