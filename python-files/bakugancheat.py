import customtkinter as ctk
import tkinter.messagebox as msg
import webbrowser

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

SUBSCRIBE_URL = "https://www.youtube.com/@nedogavsik"  # сюда перекидывает при нажатии кнопок

def need_subscribe():
    webbrowser.open(SUBSCRIBE_URL)

class RobokoppDemo(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ROBOKOPP Cheat")
        self.geometry("1200x750")


        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=20)
        self.sidebar.pack(side="left", fill="y", padx=15, pady=15)

        ctk.CTkLabel(self.sidebar, text="ROBOKOPP", font=("Segoe UI Black", 24)).pack(pady=(20,5))
        ctk.CTkLabel(self.sidebar, text="создатель: сережаробокоп", font=("Segoe UI", 13)).pack(pady=(0,20))

        self.menu_btns = {}
        for name, panel in [
            ("Aim", "aim"),
            ("Настройка аима", "aimcfg"),
            ("Visuals", "visuals"),
            ("Stats", "stats"),
            ("Misc", "misc"),
            ("Спонсоры", "sponsors")
        ]:
            b = ctk.CTkButton(self.sidebar, text=name, command=lambda p=panel: self.switch_panel(p), corner_radius=15)
            b.pack(fill="x", pady=7)
            self.menu_btns[panel] = b


        self.main = ctk.CTkFrame(self, corner_radius=20)
        self.main.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        self.panels = {}
        self.create_panels()
        self.switch_panel("aim")

    def switch_panel(self, name):
        for p in self.panels.values():
            p.pack_forget()
        self.panels[name].pack(fill="both", expand=True, padx=10, pady=10)

    def create_panels(self):

        frame = ctk.CTkFrame(self.main, corner_radius=15)
        self.panels["aim"] = frame
        ctk.CTkLabel(frame, text="AIM", font=("Segoe UI", 22, "bold")).pack(pady=10)

        ctk.CTkSwitch(frame, text="Включить AIM").pack(pady=10)

        self.fov_slider = ctk.CTkSlider(frame, from_=0, to=180, number_of_steps=180, command=lambda v: None)
        self.fov_slider.set(90)
        ctk.CTkLabel(frame, text="FOV (угол обзора)").pack()
        self.fov_slider.pack(pady=5)

        self.smooth_slider = ctk.CTkSlider(frame, from_=0, to=100, command=lambda v: None)
        self.smooth_slider.set(15)
        ctk.CTkLabel(frame, text="Smoothing").pack()
        self.smooth_slider.pack(pady=5)

        frame = ctk.CTkFrame(self.main, corner_radius=15)
        self.panels["aimcfg"] = frame
        ctk.CTkLabel(frame, text="Настройка AIM", font=("Segoe UI", 22, "bold")).pack(pady=10)

        self.prio_var = ctk.StringVar(value="Голова")
        for part in ["Голова", "Грудь", "Ноги"]:
            ctk.CTkRadioButton(frame, text=part, variable=self.prio_var, value=part).pack(anchor="w", padx=20, pady=5)

        ctk.CTkEntry(frame, placeholder_text="Кнопка активации (например MOUSE2)").pack(pady=15)

        frame = ctk.CTkFrame(self.main, corner_radius=15)
        self.panels["visuals"] = frame
        ctk.CTkLabel(frame, text="VISUALS", font=("Segoe UI", 22, "bold")).pack(pady=10)

        tabview = ctk.CTkTabview(frame, width=600, height=400, corner_radius=15)
        tabview.pack(expand=True, fill="both", padx=10, pady=10)

        tab_players = tabview.add("Игроки")
        tab_weapons = tabview.add("Оружие")
        tab_other = tabview.add("Прочее")

        for opt in ["Хитбоксы", "Скелет", "Боксы", "HP бар", "Glow"]:
            ctk.CTkSwitch(tab_players, text=opt).pack(anchor="w", padx=20, pady=5)

        for opt in ["ESP оружия", "ESP гранат", "ESP бомбы"]:
            ctk.CTkSwitch(tab_weapons, text=opt).pack(anchor="w", padx=20, pady=5)

        for opt in ["Радар", "LineESP", "3D Box"]:
            ctk.CTkSwitch(tab_other, text=opt).pack(anchor="w", padx=20, pady=5)

        ctk.CTkLabel(frame, text="Настройки ESP", font=("Segoe UI", 18, "bold")).pack(pady=10)

        self.style_menu = ctk.CTkOptionMenu(frame, values=["Box", "Outline", "Glow"])
        self.style_menu.set("Box")
        self.style_menu.pack(pady=5)

        self.color_menu = ctk.CTkOptionMenu(frame, values=["Красный", "Синий", "Зеленый", "Фиолетовый"])
        self.color_menu.set("Красный")
        self.color_menu.pack(pady=5)

        self.alpha_slider = ctk.CTkSlider(frame, from_=0, to=100, command=lambda v: None)
        self.alpha_slider.set(70)
        ctk.CTkLabel(frame, text="Прозрачность объектов").pack()
        self.alpha_slider.pack(pady=5)

        self.dist_slider = ctk.CTkSlider(frame, from_=10, to=500, command=lambda v: None)
        self.dist_slider.set(250)
        ctk.CTkLabel(frame, text="Дистанция ESP (м)").pack()
        self.dist_slider.pack(pady=5)

        frame = ctk.CTkFrame(self.main, corner_radius=15)
        self.panels["stats"] = frame
        ctk.CTkLabel(frame, text="Статистика", font=("Segoe UI", 22, "bold")).pack(pady=10)

        stats_text = "Ключ: 15ytn-35gfz-ih3\nОставшееся время подписки: 0h"
        box = ctk.CTkTextbox(frame, width=400, height=280)
        box.pack(pady=10)
        box.insert("1.0", stats_text)
        box.configure(state="disabled")

        frame = ctk.CTkFrame(self.main, corner_radius=15)
        self.panels["misc"] = frame
        ctk.CTkLabel(frame, text="Misc", font=("Segoe UI", 22, "bold")).pack(pady=10)
        ctk.CTkButton(frame, text="Открыть лог (пусто)").pack(pady=5)
        ctk.CTkButton(frame, text="Экспорт (демо)").pack(pady=5)
        ctk.CTkButton(frame, text="О программе").pack(pady=5)
    
    
        frame = ctk.CTkFrame(self.main, corner_radius=15)
        self.panels["sponsors"] = frame
        ctk.CTkLabel(frame, text="Спонсоры", font=("Segoe UI", 22, "bold")).pack(pady=10)
        ctk.CTkButton(frame, text="santy5rp", command=need_subscribe).pack(pady=5)


if __name__ == "__main__":
    app = RobokoppDemo()
    app.mainloop()
