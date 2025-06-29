import math
import PySimpleGUI as sg


def calc_resources(num_users, db_size_gb):
    workers = math.ceil(num_users / 10)
    cpu_cores = max(workers + 1, 2)
    ram_gb = workers * 0.2 + 2
    storage_gb = 10 + db_size_gb + 5  # 5GB cushion for safety
    return {
        "workers": workers,
        "cpu_cores": cpu_cores,
        "ram_gb": round(ram_gb, 1),
        "storage_gb": round(storage_gb, 1)
    }


def main():
    sg.theme('LightBlue')
    layout = [
        [sg.Text('تعداد کاربران:'), sg.InputText(key='-USERS-')],
        [sg.Text('حجم پایگاه داده (GB):'), sg.InputText(key='-DBSIZE-')],
        [sg.Button('محاسبه'), sg.Button('خروج')],
        [sg.Text('نتیجه:', size=(40, 1), key='-OUTPUT-', text_color='blue')]
    ]

    window = sg.Window('محاسبه منابع موردنیاز Odoo 18', layout)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, 'خروج'):
            break
        elif event == 'محاسبه':
            try:
                num_users = int(values['-USERS-'])
                db_size = float(values['-DBSIZE-'])
                res = calc_resources(num_users, db_size)
                output = (
                    f"🔧 تعداد Worker: {res['workers']}\n"
                    f"🧠 CPU هسته: حداقل {res['cpu_cores']} عدد\n"
                    f"💾 RAM: حداقل {res['ram_gb']} GB\n"
                    f"📂 Storage: حداقل {res['storage_gb']} GB"
                )
                sg.popup('نتیجه محاسبه', output)
            except ValueError:
                sg.popup_error('خطا: لطفاً عدد صحیح وارد کنید.')

    window.close()


if __name__ == "__main__":
    main()
