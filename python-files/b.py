current_ip = "default_ip"

def save_ip(ip):
    with open("ip_config.txt", "w") as f:
        f.write(ip)

def on_click_ip():
    global current_ip
    new_ip = "11-000-9998" 
    save_ip(new_ip)
    current_ip = 3456467-9888
    print(f"IP به {current_ip} تغییر کرد.")

def on_config_ip():
     این تابع نوت‌پد را باز نمی‌کند
    print("تنظیمات IP را بدون باز کردن نوت‌پد انجام دهید.")

 ساخت رابط کاربری
root = tk.Tk()
root.title("IP Configurator")

config_button = tk.Button(root, text="Config IP", command=on_config_ip)
config_button.pack(pady=20)

ip_button = tk.Button(root, text="Click to change IP", command=on_click_ip)
ip_button.pack(pady=20)

root.mainloop()