
import base64
import tempfile
import os

# Встроенный .ogg аудиофайл
ogg_base64 = """T2dnUwACAAAAAAAAAAACXgAAAAAAAIvYXT8BHgF2b3JiaXMAAAAAAkSsAAAAAAAAAHECAAAAAAC4AU9nZ1MAAAAAAAAAAAAAAl4AAAEAAACL5lOeEjv/////////////////////kQN2b3JiaXMrAAAAWGlwaC5PcmcgbGliVm9yYmlzIEkgMjAxMjAyMDMgKE9tbmlwcmVzZW50KQAAAAABBXZvcmJpcylCQ1YBAAgAAAAxTCDFgNCQVQAAEAAAYCQpDpNmSSmllKEoeZiUSEkppZTFMImYlInFGGOMMcYYY4wxxhhjjCA0ZBUAAAQAgCgJjqPmSWrOOWcYJ45yoDlpTjinIAeKUeA5CcL1JmNuprSma27OKSUIDVkFAAACAEBIIYUUUkghhRRiiCGGGGKIIYcccsghp5xyCiqooIIKMsggg0wy6aSTTjrpqKOOOuootNBCCy200kpMMdVWY669Bl18c84555xzzjnnnHPOCUJDVgEAIAAABEIGGWQQQgghhRRSiCmmmHIKMsiA0JBVAAAgAIAAAAAAR5EUSbEUy7EczdEkT/IsURM10TNFU1RNVVVVVXVdV3Zl13Z113Z9WZiFW7h9WbiFW9iFXfeFYRiGYRiGYRiGYfh93/d93/d9IDRkFQAgAQCgIzmW4ymiIhqi4jmiA4SGrAIAZAAABAAgCZIiKZKjSaZmaq5pm7Zoq7Zty7Isy7IMhIasAgAAAQAEAAAAAACgaZqmaZqmaZqmaZqmaZqmaZqmaZpmWZZlWZZlWZZlWZZlWZZlWZZlWZZlWZZlWZZlWZZlWZZlWZZlWUBoyCoAQAIAQMdxHMdxJEVSJMdyLAcIDVkFAMgAAAgAQFIsxXI0R3M0x3M8x3M8R3REyZRMzfRMDwgNWQUAAAIACAAAAAAAQDEcxXEcydEkT1It03I1V3M913NN13VdV1VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVWB0JBVAAAEAAAhnWaWaoAIM5BhIDRkFQCAAAAAGKEIQwwIDVkFAAAEAACIoeQgmtCa8805DprloKkUm9PBiVSbJ7mpmJtzzjnnnGzOGeOcc84pypnFoJnQmnPOSQyapaCZ0JpzznkSmwetqdKac84Z55wOxhlhnHPOadKaB6nZWJtzzlnQmuaouRSbc86JlJsntblUm3POOeecc84555xzzqlenM7BOeGcc86J2ptruQldnHPO+WSc7s0J4ZxzzjnnnHPOOeecc84JQkNWAQBAAAAEYdgYxp2CIH2OBmIUIaYhkx50jw6ToDHIKaQejY5GSqmDUFIZJ6V0gtCQVQAAIAAAhBBSSCGFFFJIIYUUUkghhhhiiCGnnHIKKqikkooqyiizzDLLLLPMMsusw84667DDEEMMMbTSSiw11VZjjbXmnnOuOUhrpbXWWiullFJKKaUgNGQVAAACAEAgZJBBBhmFFFJIIYaYcsopp6CCCggNWQUAAAIACAAAAPAkzxEd0REd0REd0REd0REdz/EcURIlURIl0TItUzM9VVRVV3ZtWZd127eFXdh139d939eNXxeGZVmWZVmWZVmWZVmWZVmWZQlCQ1YBACAAAABCCCGEFFJIIYWUYowxx5yDTkIJgdCQVQAAIACAAAAAAEdxFMeRHMmRJEuyJE3SLM3yNE/zNNETRVE0TVMVXdEVddMWZVM2XdM1ZdNVZdV2Zdm2ZVu3fVm2fd/3fd/3fd/3fd/3fd/XdSA0ZBUAIAEAoCM5kiIpkiI5juNIkgSEhqwCAGQAAAQAoCiO4jiOI0mSJFmSJnmWZ4maqZme6amiCoSGrAIAAAEABAAAAAAAoGiKp5iKp4iK54iOKImWaYmaqrmibMqu67qu67qu67qu67qu67qu67qu67qu67qu67qu67qu67qu67pAaMgqAEACAEBHciRHciRFUiRFciQHCA1ZBQDIAAAIAMAxHENSJMeyLE3zNE/zNNETPdEzPVV0RRcIDVkFAAACAAgAAAAAAMCQDEuxHM3RJFFSLdVSNdVSLVVUPVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVdU0TdM0gdCQlQAAGQAA5KSm1HoOEmKQOYlBaAhJxBzFXDrpnKNcjIeQI0ZJ7SFTzBAEtZjQSYUU1OJaah1zVIuNrWRIQS22xlIh5agHQkNWCAChGQAOxwEcTQMcSwMAAAAAAAAASdMATRQBzRMBAAAAAAAAwNE0QBM9QBNFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcTQM0UQQ0UQQAAAAAAAAATRQB0VQB0TQBAAAAAAAAQBNFwDNFQDRVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcTQM0UQQ0UQQAAAAAAAAATRQBUTUBTzQBAAAAAAAAQBNFQDRNQFRNAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAQ4AAAEWQqEhKwKAOAEAh+NAkiBJ8DSAY1nwPHgaTBPgWBY8D5oH0wQAAAAAAAAAAABA8jR4HjwPpgmQNA+eB8+DaQIAAAAAAAAAAAAgeR48D54H0wRIngfPg+fBNAEAAAAAAAAAAADwTBOmCdGEagI804RpwjRhqgAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAACAAQcAgAATykChISsCgDgBAIejSBIAADiSZFkAAKBIkmUBAIBlWZ4HAACSZXkeAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAIABBwCAABPKQKEhKwGAKAAAh6JYFnAcywKOY1lAkiwLYFkATQN4GkAUAYAAAIACBwCAABs0JRYHKDRkJQAQBQDgcBTL0jRR5DiWpWmiyHEsS9NEkWVpmqaJIjRL00QRnud5pgnP8zzThCiKomkCUTRNAQAABQ4AAAE2aEosDlBoyEoAICQAwOE4luV5oiiKpmmaqspxLMvzRFEUTVNVXZfjWJbniaIomqaqui7L0jTPE0VRNE1VdV1omueJoiiapqq6LjRNFE3TNFVVVV0XmuaJpmmaqqqqrgvPE0XTNE1VdV3XBaJomqapqq7rukAUTdM0VdV1XReIomiapqq6rusC0zRNVVVd15VlgGmqqqq6riwDVFVVXdeVZRmgqqrquq4rywDXdV3ZlWVZBuC6rivLsiwAAODAAQAgwAg6yaiyCBtNuPAAFBqyIgCIAgAAjGFKMaUMYxJCCqFhTEJIIWRSUioppQpCKiWVUkFIpaRSMkotpZZSBSGVkkqpIKRSUikFAIAdOACAHVgIhYasBADyAAAIY5RizDnnJEJKMeaccxIhpRhzzjmpFGPOOeeclJIx55xzTkrJmHPOOSelZMw555yTUjrnnHMOSimldM4556SUUkLonHNSSimdc845AQBABQ4AAAE2imxOMBJUaMhKACAVAMDgOJalaZ4niqZpSZKmeZ4nmqZpapKkaZ4niqZpmjzP80RRFE1TVXme54miKJqmqnJdURRN0zRNVSXLoiiKpqmqqgrTNE3TVFVVhWmapmmqquvCtlVVVV3XdWHbqqqqruu6wHVd13VlGbiu67quLAsAAE9wAAAqsGF1hJOiscBCQ1YCABkAAIQxCCmEEFIGIaQQQkgphZAAAIABBwCAABPKQKEhKwGAcAAAgBCMMcYYY4wxNoxhjDHGGGOMMXEKY4wxxhhjjDHGGGOMMcYYY4wxxhhjjDHGGGOMMcYYY4wxxhhjjDHGGGOMMcYYY4wxxhhjjDHGGGOMMcYYY4wxxhhjjDHGGGOMMcYYY4wxxhhjjDHGGGOMMcYYY4wxxhhjjDHGGGOMMcYYY4wxxhhjjDHG2FprrbVWABjOhQNAWYSNM6wknRWOBhcashIACAkAAIxBiDHoJJSSSkoVQow5KCWVllqKrUKIMQilpNRabDEWzzkHoaSUWooptuI556Sk1FqMMcZaXAshpZRaiy22GJtsIaSUUmsxxlpjM0q1lFqLMcYYayxKuZRSa7HFGGuNRSibW2sxxlprrTUp5XNLsdVaY6y1JqOMkjHGWmustdYilFIyxhRTrLXWmoQwxvcYY6wx51qTEsL4HlMtsdVaa1JKKSNkjanGWnNOSglljI0t1ZRzzgUAQD04AEAlGEEnGVUWYaMJFx6AQkNWAgC5AQAIQkoxxphzzjnnnHMOUqQYc8w55yCEEEIIIaQIMcaYc85BCCGEEEJIGWPMOecghBBCCKGEklLKmHPOQQghhFJKKSWl1DnnIIQQQiillFJKSqlzzkEIIYRSSimllJRSCCGEEEIIpZRSSikppZRCCCGEEkoppZRSUkophRBCCKWUUkoppaSUUgohhBBKKaWUUkpJKaUUQgmllFJKKaWUklJKKaUQSimllFJKKSWllFJKpZRSSimllFJKSimllEoppZRSSimllJRSSimVUkoppZRSSikppZRSSqmUUkoppZRSUkoppZRSKaWUUkoppaSUUkoppVJKKaWUUkpJKaWUUkqllFJKKaWUklJKKaWUUiqllFJKKaUAAKADBwCAACMqLcROM648AkcUMkxAhYasBADIAAAQB7G01lqrjHLKSUmtQ0Ya5qCk2EkHIbVYS2UgQcpJSp2CCCkGqYWMKqWYk5ZCy5hSDGIrMXSMMUc55VRCxxgAAACCAAADETITCBRAgYEMADhASJACAAoLDB3DRUBALiGjwKBwTDgnnTYAAEGIzBCJiMUgMaEaKCqmA4DFBYZ8AMjQ2Ei7uIAuA1zQxV0HQghCEIJYHEABCTg44YYn3vCEG5ygU1TqQAAAAAAAHgDgAQAg2QAiIqKZ4+jw+AAJERkhKTE5QREAAAAAADsA+AAASFKAiIho5jg6PD5AQkRGSEpMTlACAAABBAAAAABAAAEICAgAAAAAAAQAAAAICE9nZ1MABD8VAAAAAAAAAl4AAAIAAACooPGbClZU/y3/Hebu8tUcVl85mH3UBcZAqZmH1VcOZh91gTFQauZZJ0shTRBWcAgYa0XUYMUWYtW0LrZAi6IIqiqCtVptLniqVZ1aFHx7nTotqKrhFFvVqqJBRbCg1aIR1SIeACR6r63SZlxPDl2wJXqvrdJmXE8OXbAld/qYdmg2ctgGAPa2BhYx1bC3iMWCdUsxLEQk30xE1ejUqFbEFgUtRZ96iT//2SDYoqpaK2qDLbFAtQoqANp33Uxse5r7DyQfxrAU+66biW1Pc/+B5MMYluInFWVkmYqyqLciyqLeirJSlClCxLaLSyDFgVjMgcWImdiBmQmIidxJAABEVbFWUbWKtWqNUatGrLFGrDWsYmlpaWFVrWPVwrqYqkGxRhWdCKBagGmKgIWNhlqzLoYaWLFuYRqYIKa5JVQi1DAtFAC1ZhXMHbxFVbSKVqMqqqKKCgAGY1EVrUZ1lTe1EyCXXBkE+PxZsi9/9d1xZQfvc2ZVrcnhK3tVIN9++Dy5nz/7u2TWBdn52W3vJOYqDcB1kHd33bPnmKdGrbWyrg5nk7nNtdPduio31eaTzK3gvhds/ZDWCmRzM3Mzm2vnKtlX6XfmbFUVBcA0VC2sW5hqxWZralqYiAoKKGKKYmHdQEUFAJ5H3aziV+q9YOQHSOZRN6v4lXovGPkBkgcybDpbdsMUF6ekInYQ1xRjB2JHYimEmcrBQQwAAJj2htiovVjt7AyLIPYmFhu1RcTAagVLS2tWMUzTFqaBYWlYImBRtRqd1oARK0a0RlUUrGoErRhbQLQIkUWr2gEmAohhXQxBNzid3d/Gf1RjQBUURQSj9S6gAMRWtGIwIryu+CptnrRCvLE7ySvakUKD+2iRq6yUCNQ0MMC6BYppCCo2AGhUBBAr6FS0KNZqVI2mL+X40wBuDRAAmLiLTx1mSDNl8sYGfT0gsigL6FAFY0UVyy3IUHfCsydgRARAA1qFa9sEALCiFQsAAIA1WgUaAuIOSuUJB6xWsgGI29LkbACIEkgAftbcbHKzw7ogpV/GFyboWXOzyc0O64KUfhlfmKC3HtAy2Q6mgyPiVGJiqTiVU+FIjNiBCQgYAAAAqL2YFgyriGBjg9XeasHWYidib2MPVlWj04ro1Cg6RacOEDQGAVExiqpYwV34S+saVnaVX3rEgGojVjWqCtJbb3VLuUcqglHFoNGpIKp0g4kIC02t1T7/GeIdZLrqlsXYIAJoEMtlI8t/Sfsce0AMoCpaG7GSk+ZLGWytRkSrsRXE0FkMIYqxLaqqtQYVLQEvsSX1BvwLuSoOpNpyNI4mDpbEOe1ySgDDpoLAKABeptxM4J8bZ4LgE4GJtky5mcA/N84EwScCE+2NNBjbDlLN3CFlOjgScyCJU6USc5gAAAAAoGKxF1uxqqq9vWGHjcWwtVWLnUVsrfaGiI2CNejU6tCKAP+XkIoNgGKxVlEVxYBYEIsKokUEMCJobAsqamCpBoqNonK5BkgQh8gSGKNVjIDYgvd7XtDaYjGgImIBa0RsBK0gZBDRYggeOYPzCbZVVRCLDdqufrQ6FAbky+FFWITyxvFw80AAMP/WqoqAEevElisoJ4QWEEAAG0xgogTg+aDb7Kb8OO/EPSG0ZDDoEAUQqwjYFsAgqlYAHmbcDPjPZ71LYczfQhtHXphxM+A/n/UuhTF/C20ceYc2k9inIwExR2IOjhxBLJWDmJgAAAAAAJj2NraGWq0WMS1WLLaK2mBh1WYbTKvWLMUG0wLD0sCwbsWwqlbAUCytYVqYKmIKmIYFK1pBMAiCUUVEFUUrAF9qoT9CVYxFK2KjoMpndk6MYMBYYyyranz1+YZGl7Kb11VEFa2C2KIqxrXDFWrysUU5yd9S/joJtyojvpryZa0IAAAAwB0ZUFQBrFGxoGIBq+wkq1YwqCJiLFodBsJX/kSgAl8AsLAQJZCbWQVgp36RqXGuRVXEIKLVgAWeZRx2/D/92q+glQWseMsyDjv+n37tV9DKAla87ZsjBwcHYjEHB2KSUzEzAwAAAAAqCoZVG2y2hY1izUaxZktrWFqz2RY2ixUbrZiGVRusWzFFBbFqg3XDsDQwGp06VLGiClbUdOsak0srotWogsVisTjnnPdVgVq7CgFXJgz1uxNqrZH57jogU8PZzG7e+kt5QtyWAPAluUD464Rx3VqgSqbGre8kA5AFcubKOe+BXL4KNpMVrcaIEVWwcOWc82p8kLWzmQlAFj7L1rvPk/u1hq25XwA="""

# Сохраняем .ogg во временный файл
temp_dir = tempfile.gettempdir()
ogg_path = os.path.join(temp_dir, "peppy.osuhit_Clicks_Useful_1.ogg")
with open(ogg_path, "wb") as f:
    f.write(base64.b64decode(ogg_base64))

# Теперь основной код приложения
# Файл .ogg доступен по пути: ogg_path


import customtkinter as ctk
import os
import subprocess
import tkinter.filedialog as filedialog
import shutil
import sys
import webbrowser
from tkinter import messagebox
import pygame

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class PyToExeConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Py to Exe Converter v1.3")
        self.root.geometry("700x550")
        self.root.resizable(True, True)

        self.selected_files = []
        self.icon_path = None
        self.is_pressed = {}
        self.original_sizes = {}

        pygame.mixer.init()
        self.click_sound = pygame.mixer.Sound(resource_path("peppy.osuhit_Clicks_Useful_1.ogg"))

        self.create_widgets()

    def create_widgets(self):
        header_frame = ctk.CTkFrame(master=self.root)
        header_frame.pack(pady=10, fill="x")

        self.label = ctk.CTkLabel(master=header_frame, text="Py to exe", font=("Arial", 24, "bold"), text_color="#FF1493")
        self.label.pack()

        files_frame = ctk.CTkFrame(master=self.root)
        files_frame.pack(pady=10, padx=10, fill="x")

        self.first_file_button = ctk.CTkButton(
            master=files_frame, text="Первый py файл",
            command=lambda: self.button_action(self.first_file_button, self.select_file, 0),
            fg_color="#FF1493", hover_color="#FF69B4", width=200
        )
        self.first_file_button.pack(side="left", padx=5)
        self.is_pressed[self.first_file_button] = False
        self.original_sizes[self.first_file_button] = (200, self.first_file_button._current_height)

        self.second_file_button = ctk.CTkButton(
            master=files_frame, text="Второй py файл",
            command=lambda: self.button_action(self.second_file_button, self.select_file, 1),
            fg_color="#FF1493", hover_color="#FF69B4", width=200
        )
        self.second_file_button.pack(side="left", padx=5)
        self.is_pressed[self.second_file_button] = False
        self.original_sizes[self.second_file_button] = (200, self.second_file_button._current_height)

        self.add_file_button = ctk.CTkButton(
            master=files_frame, text="Добавить файл",
            command=lambda: self.button_action(self.add_file_button, self.select_file, len(self.selected_files)),
            fg_color="#FF1493", hover_color="#FF69B4", width=200
        )
        self.add_file_button.pack(side="left", padx=5)
        self.is_pressed[self.add_file_button] = False
        self.original_sizes[self.add_file_button] = (200, self.add_file_button._current_height)

        self.files_text = ctk.CTkTextbox(master=self.root, height=150, width=650)
        self.files_text.pack(pady=10, padx=10, fill="both")
        self.files_text.configure(state="disabled")

        options_frame = ctk.CTkFrame(master=self.root)
        options_frame.pack(pady=10, padx=10, fill="x")

        self.console_var = ctk.BooleanVar(value=False)
        self.console_check = ctk.CTkCheckBox(master=options_frame, text="Показать консоль", variable=self.console_var)
        self.console_check.pack(side="left", padx=5)

        self.onefile_var = ctk.BooleanVar(value=True)
        self.onefile_check = ctk.CTkCheckBox(master=options_frame, text="Один .exe файл", variable=self.onefile_var)
        self.onefile_check.pack(side="left", padx=5)

        self.icon_button = ctk.CTkButton(
            master=options_frame, text="Выбрать иконку",
            command=lambda: self.button_action(self.icon_button, self.select_icon),
            fg_color="#FF1493", hover_color="#FF69B4", width=150
        )
        self.icon_button.pack(side="right", padx=5)
        self.is_pressed[self.icon_button] = False
        self.original_sizes[self.icon_button] = (150, self.icon_button._current_height)

        self.convert_button = ctk.CTkButton(
            master=self.root, text="Собрать",
            command=lambda: self.button_action(self.convert_button, self.convert_to_exe),
            fg_color="#FF1493", hover_color="#FF69B4", width=200
        )
        self.convert_button.pack(pady=20)
        self.is_pressed[self.convert_button] = False
        self.original_sizes[self.convert_button] = (200, self.convert_button._current_height)

        self.status_label = ctk.CTkLabel(master=self.root, text="Готов к работе", font=("Arial", 12))
        self.status_label.pack(pady=10)

        self.telegram_button = ctk.CTkButton(
            master=self.root, text="Telegram",
            command=lambda: self.button_action(self.telegram_button, self.open_telegram),
            fg_color="#FF1493", hover_color="#FF69B4", width=150
        )
        self.telegram_button.pack(pady=5)
        self.is_pressed[self.telegram_button] = False
        self.original_sizes[self.telegram_button] = (150, self.telegram_button._current_height)

    def select_file(self, index):
        file = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if file:
            if index < len(self.selected_files):
                self.selected_files[index] = file
            else:
                self.selected_files.append(file)
            self.update_files_text()
            self.status_label.configure(text="Файл выбран успешно!")

    def select_icon(self):
        icon = filedialog.askopenfilename(filetypes=[("Icon files", "*.ico"), ("All files", "*.*")])
        if icon:
            self.icon_path = icon
            self.status_label.configure(text=f"Иконка выбрана: {os.path.basename(icon)}")

    def update_files_text(self):
        self.files_text.configure(state="normal")
        self.files_text.delete("1.0", ctk.END)
        for file in self.selected_files:
            self.files_text.insert(ctk.END, f"{file}\n")
        self.files_text.configure(state="disabled")

    def open_telegram(self):
        webbrowser.open("https://t.me/hhh0n1programs")
        self.status_label.configure(text="Открыт Telegram-канал!")

    def button_action(self, button, command, *args):
        try:
            self.click_sound.play()
        except Exception as e:
            print(f"Ошибка звука: {e}")
        self.is_pressed[button] = True
        original_width, original_height = self.original_sizes[button]
        new_width = int(original_width * 0.9)
        new_height = int(original_height * 0.9)
        button.configure(width=new_width, height=new_height)
        self.root.update()
        self.root.after(100, lambda: self.animate_button(button, original_width, original_height))
        self.root.after(200, lambda: command(*args))

    def animate_button(self, button, original_width, original_height):
        if self.is_pressed[button]:
            button.configure(width=original_width, height=original_height)
            self.is_pressed[button] = False

    def convert_to_exe(self):
        if not self.selected_files:
            messagebox.showerror("Ошибка", "Не выбрано ни одного файла!")
            return
        try:
            command = ["pyinstaller"]
            if self.onefile_var.get():
                command.append("--onefile")
            if not self.console_var.get():
                command.append("--noconsole")
            if self.icon_path and os.path.exists(self.icon_path):
                command.append(f"--icon={self.icon_path}")
            else:
                self.status_label.configure(text="Предупреждение: Иконка не выбрана или не найдена.")
            for file in self.selected_files:
                if os.path.exists(file):
                    command.append(file)
                else:
                    messagebox.showerror("Ошибка", f"Файл {file} не найден!")
                    return
            self.status_label.configure(text="Конвертация... Пожалуйста, подождите")
            self.root.update()
            result = subprocess.run(command, capture_output=True, text=True, cwd=os.path.dirname(self.selected_files[0]))
            if result.returncode == 0:
                dist_folder = "dist"
                if os.path.exists(dist_folder):
                    exe_files = [f for f in os.listdir(dist_folder) if f.endswith(".exe")]
                    if exe_files:
                        exe_file = exe_files[0]
                        source_path = os.path.join(dist_folder, exe_file)
                        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
                        os.makedirs(downloads_path, exist_ok=True)
                        destination_path = os.path.join(downloads_path, exe_file)
                        shutil.move(source_path, destination_path)
                        self.status_label.configure(text=f"Успешно! Перемещено в Загрузки как {exe_file}")
                        shutil.rmtree(dist_folder, ignore_errors=True)
                    else:
                        self.status_label.configure(text="Ошибка: .exe файл не найден в dist!")
                else:
                    self.status_label.configure(text="Ошибка: Папка dist не создана!")
            else:
                self.status_label.configure(text=f"Ошибка компиляции: {result.stderr[:200]}")
                with open("error_log.txt", "w", encoding="utf-8") as f:
                    f.write(result.stderr)
                messagebox.showwarning("Ошибка", "Подробности сохранены в error_log.txt")
        except Exception as e:
            self.status_label.configure(text=f"Ошибка: {str(e)}")
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    try:
        root = ctk.CTk()
        app = PyToExeConverter(root)
        root.mainloop()
    except Exception as e:
        print(f"Ошибка запуска GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

