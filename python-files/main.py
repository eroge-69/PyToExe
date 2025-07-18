import customtkinter
import os
import datetime
import sys

def shutdown():
    try:
        hours = int(hour_var.get())
        minutes = int(minute_var.get())
        seconds = int(second_var.get())
        total_seconds = hours * 3600 + minutes * 60 + seconds
        global shutdown_time
        shutdown_time = total_seconds
        os.system(f"shutdown /s /t {total_seconds}")
        countdown(shutdown_time)
        reset_values()
    except ValueError:
        timer_label.configure(text="Angka Tidak Valid", text_color="red", font=("Helvetica", 20))
        app.after(1000, lambda: timer_label.configure(text="00:00:00", text_color="white", font=("Helvetica", 40)))

def reset_values():
    hour_var.set("0")
    minute_var.set("0")
    second_var.set("0")

def cancel_shutdown():
    os.system("shutdown /a")
    timer_label.configure(text="Shutdown Dibatalkan", text_color="red", font=("Helvetica", 20))
    app.after(200, lambda: sys.exit())

def countdown(shutdown_time):
    if shutdown_time > 0:
        timer = datetime.timedelta(seconds=shutdown_time)
        timer_label.configure(text=str(timer))
        shutdown_time -= 1
        app.after(1000, countdown, shutdown_time)
        if shutdown_time < 10:
            timer_label.configure(text="Memulai Shutdown..", text_color="white", font=("Helvetica", 20))

app = customtkinter.CTk()
app.geometry("300x255")
app.resizable(False, False)
app.title("Shutdown Timer")#Hapus ini jika code eror

timer_label = customtkinter.CTkLabel(app, text="00:00:00", font=("Helvetica", 40), text_color="white")
timer_label.pack(pady=20)

hour_var = customtkinter.StringVar(value="0")
minute_var = customtkinter.StringVar(value="0")
second_var = customtkinter.StringVar(value="0")

frame = customtkinter.CTkFrame(app)
frame.pack(pady=10)

framebutton = customtkinter.CTkFrame(app)
framebutton.pack(pady=10)

hour_label = customtkinter.CTkLabel(frame, text="Hour", font=("Helvetica", 12))
hour_label.grid(row=0, column=0, padx=10)

minute_label = customtkinter.CTkLabel(frame, text="Minute", font=("Helvetica", 12))
minute_label.grid(row=0, column=1, padx=10)

second_label = customtkinter.CTkLabel(frame, text="Second", font=("Helvetica", 12))
second_label.grid(row=0, column=2, padx=10)

hour_menu = customtkinter.CTkComboBox(frame, variable=hour_var, values=[str(i) for i in range(0, 25)], width=60)
hour_menu.grid(row=1, column=0, padx=10)

minute_menu = customtkinter.CTkComboBox(frame, variable=minute_var, values=[str(i) for i in range(0, 60)], width=60)
minute_menu.grid(row=1, column=1, padx=10)

second_menu = customtkinter.CTkComboBox(frame, variable=second_var, values=[str(i) for i in range(0, 60)], width=60)
second_menu.grid(row=1, column=2, padx=10)

submit_button = customtkinter.CTkButton(framebutton, text="Submit", command=shutdown, width=80, fg_color="green", hover_color="darkgreen")
submit_button.grid(row=0, column=0, padx=10)

cancel_button = customtkinter.CTkButton(framebutton, text="Cancel", command=cancel_shutdown, width=80, fg_color="red", hover_color="darkred")
cancel_button.grid(row=0, column=1, padx=10)

shutdown_time = 0
app.mainloop()