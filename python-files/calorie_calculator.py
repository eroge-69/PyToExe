import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json

texts = {
    "en": {
        "title": "Calorie & Macronutrient Calculator",
        "weight": "Weight (kg)",
        "height": "Height (cm)",
        "age": "Age (years)",
        "gender": "Gender",
        "male": "Male",
        "female": "Female",
        "activity": "Activity Level",
        "activities": [
            "Sedentary (little or no exercise)",
            "Lightly active (light exercise 1-3 days/week)",
            "Moderately active (moderate exercise 3-5 days/week)",
            "Very active (hard exercise 6-7 days/week)",
            "Extra active (very hard exercise & physical job)"
        ],
        "calculate": "Calculate",
        "save": "Save Data",
        "load": "Load Data",
        "results_title": "Results",
        "close": "Close",
        "error_input": "Please enter valid numeric values for weight, height, and age.",
        "saved": "User data saved successfully!",
        "save_title": "Save File",
        "load_title": "Open File",
        "bmr": "BMR",
        "total_calories": "Total Calories (with activity)",
        "macros": "Macronutrients",
        "carbs": "Carbs",
        "protein": "Protein",
        "fat": "Fat",
    },
    "ru": {
        "title": "Калькулятор калорий и макронутриентов",
        "weight": "Вес (кг)",
        "height": "Рост (см)",
        "age": "Возраст (лет)",
        "gender": "Пол",
        "male": "Мужской",
        "female": "Женский",
        "activity": "Уровень активности",
        "activities": [
            "Малоподвижный (мало или нет упражнений)",
            "Слегка активный (легкие упражнения 1-3 дня/нед)",
            "Умеренно активный (умеренные упражнения 3-5 дней/нед)",
            "Очень активный (тяжелые упражнения 6-7 дней/нед)",
            "Экстра активный (очень тяжелая физическая работа или тренировки)"
        ],
        "calculate": "Рассчитать",
        "save": "Сохранить данные",
        "load": "Загрузить данные",
        "results_title": "Результаты",
        "close": "Закрыть",
        "error_input": "Пожалуйста, введите корректные числовые значения для веса, роста и возраста.",
        "saved": "Данные пользователя успешно сохранены!",
        "save_title": "Сохранить файл",
        "load_title": "Открыть файл",
        "bmr": "Основной обмен (BMR)",
        "total_calories": "Итоговые калории (с учётом активности)",
        "macros": "Макронутриенты",
        "carbs": "Углеводы",
        "protein": "Белки",
        "fat": "Жиры",
    }
}

current_lang = "en"

def calculate_bmr(weight, height, age, gender):
    if gender == texts[current_lang]["male"]:
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

def calculate_calories(bmr, activity_factor):
    return bmr * activity_factor

def calculate_macros(calories):
    carbs_cal = calories * 0.40
    protein_cal = calories * 0.30
    fat_cal = calories * 0.30

    carbs_g = carbs_cal / 4
    protein_g = protein_cal / 4
    fat_g = fat_cal / 9

    return round(carbs_g,1), round(protein_g,1), round(fat_g,1)

def save_user_data():
    data = {
        'weight': weight_entry.get(),
        'height': height_entry.get(),
        'age': age_entry.get(),
        'gender': gender_var.get(),
        'activity': activity_var.get()
    }
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files","*.json")], title=texts[current_lang]["save_title"])
    if file_path:
        with open(file_path, 'w') as f:
            json.dump(data, f)
        messagebox.showinfo(texts[current_lang]["saved"], texts[current_lang]["saved"])

def load_user_data():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files","*.json")], title=texts[current_lang]["load_title"])
    if file_path:
        with open(file_path, 'r') as f:
            data = json.load(f)
        weight_entry.delete(0, tk.END)
        weight_entry.insert(0, data.get('weight',''))
        height_entry.delete(0, tk.END)
        height_entry.insert(0, data.get('height',''))
        age_entry.delete(0, tk.END)
        age_entry.insert(0, data.get('age',''))
        gender_var.set(data.get('gender', texts[current_lang]["male"]))
        activity_var.set(data.get('activity', texts[current_lang]["activities"][0]))

def show_results_popup(text):
    popup = tk.Toplevel(root)
    popup.title(texts[current_lang]["results_title"])
    popup.geometry("500x400")
    popup.configure(bg="white")
    popup.resizable(False, False)

    result_textbox = tk.Text(popup, font=("Segoe UI", 14), bg="white", relief="flat", wrap="word")
    result_textbox.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    scrollbar = ttk.Scrollbar(popup, command=result_textbox.yview)
    scrollbar.pack(side="right", fill="y")
    result_textbox.config(yscrollcommand=scrollbar.set)

    result_textbox.insert(tk.END, text)
    result_textbox.config(state='disabled')

    close_btn = tk.Button(popup, text=texts[current_lang]["close"], font=("Segoe UI", 14), command=popup.destroy, bg="#e74c3c", fg="white", padx=12, pady=8)
    close_btn.pack(pady=(0,10))

def calculate():
    try:
        weight = float(weight_entry.get())
        height = float(height_entry.get())
        age = int(age_entry.get())
        gender = gender_var.get()
        activity_level = activity_var.get()

        activity_factors = {
            texts["en"]["activities"][0]: 1.2,
            texts["en"]["activities"][1]: 1.375,
            texts["en"]["activities"][2]: 1.55,
            texts["en"]["activities"][3]: 1.725,
            texts["en"]["activities"][4]: 1.9,

            texts["ru"]["activities"][0]: 1.2,
            texts["ru"]["activities"][1]: 1.375,
            texts["ru"]["activities"][2]: 1.55,
            texts["ru"]["activities"][3]: 1.725,
            texts["ru"]["activities"][4]: 1.9,
        }

        bmr = calculate_bmr(weight, height, age, gender)
        calories = calculate_calories(bmr, activity_factors[activity_level])
        carbs, protein, fat = calculate_macros(calories)

        result_text = (
            f"{texts[current_lang]['bmr']}: {bmr:.1f} kcal/day\n"
            f"{texts[current_lang]['total_calories']}: {calories:.1f} kcal/day\n\n"
            f"{texts[current_lang]['macros']}:\n"
            f" • {texts[current_lang]['carbs']}: {carbs} g\n"
            f" • {texts[current_lang]['protein']}: {protein} g\n"
            f" • {texts[current_lang]['fat']}: {fat} g"
        )

        show_results_popup(result_text)

    except ValueError:
        messagebox.showerror(texts[current_lang]["error_input"], texts[current_lang]["error_input"])

def switch_language():
    global current_lang
    current_lang = "ru" if current_lang == "en" else "en"
    update_ui_texts()

def update_ui_texts():
    root.title(texts[current_lang]["title"])
    title_label.config(text=texts[current_lang]["title"])

    weight_label.config(text=texts[current_lang]["weight"])
    height_label.config(text=texts[current_lang]["height"])
    age_label.config(text=texts[current_lang]["age"])
    gender_label.config(text=texts[current_lang]["gender"])
    activity_label.config(text=texts[current_lang]["activity"])

    gender_menu['values'] = [texts[current_lang]["male"], texts[current_lang]["female"]]
    if gender_var.get() not in gender_menu['values']:
        gender_var.set(gender_menu['values'][0])

    activity_menu['values'] = texts[current_lang]["activities"]
    if activity_var.get() not in activity_menu['values']:
        activity_var.set(activity_menu['values'][0])

    calc_button.config(text=texts[current_lang]["calculate"])
    save_button.config(text=texts[current_lang]["save"])
    load_button.config(text=texts[current_lang]["load"])
    lang_toggle_btn.config(text="RU / EN")

root = tk.Tk()
root.geometry("700x650")
root.configure(bg="#f0f4f8")
root.resizable(False, False)

title_frame = tk.Frame(root, bg="#2c3e50", pady=20)
title_frame.pack(fill="x")

title_label = tk.Label(title_frame, font=("Segoe UI", 24, "bold"), fg="white", bg="#2c3e50")
title_label.pack()

input_frame = tk.Frame(root, bg="white", bd=2, relief="groove", padx=30, pady=25)
input_frame.pack(pady=20, padx=40, fill="x")

weight_label = tk.Label(input_frame, font=("Segoe UI", 16), bg="white")
weight_label.grid(row=0, column=0, sticky="w", pady=10)
weight_entry = tk.Entry(input_frame, font=("Segoe UI", 16), bd=2, relief="ridge")
weight_entry.grid(row=0, column=1, pady=10, padx=12, sticky="ew")

height_label = tk.Label(input_frame, font=("Segoe UI", 16), bg="white")
height_label.grid(row=1, column=0, sticky="w", pady=10)
height_entry = tk.Entry(input_frame, font=("Segoe UI", 16), bd=2, relief="ridge")
height_entry.grid(row=1, column=1, pady=10, padx=12, sticky="ew")

age_label = tk.Label(input_frame, font=("Segoe UI", 16), bg="white")
age_label.grid(row=2, column=0, sticky="w", pady=10)
age_entry = tk.Entry(input_frame, font=("Segoe UI", 16), bd=2, relief="ridge")
age_entry.grid(row=2, column=1, pady=10, padx=12, sticky="ew")

gender_label = tk.Label(input_frame, font=("Segoe UI", 16), bg="white")
gender_label.grid(row=3, column=0, sticky="w", pady=10)
gender_var = tk.StringVar()
gender_menu = ttk.Combobox(input_frame, textvariable=gender_var, state="readonly", font=("Segoe UI", 15))
gender_menu.grid(row=3, column=1, pady=10, padx=12, sticky="ew")

activity_label = tk.Label(input_frame, font=("Segoe UI", 16), bg="white")
activity_label.grid(row=4, column=0, sticky="w", pady=10)
activity_var = tk.StringVar()
activity_menu = ttk.Combobox(input_frame, textvariable=activity_var, state="readonly", font=("Segoe UI", 15))
activity_menu.grid(row=4, column=1, pady=10, padx=12, sticky="ew")

input_frame.columnconfigure(1, weight=1)

button_frame = tk.Frame(root, bg="#f0f4f8")
button_frame.pack(pady=20)

calc_button = tk.Button(button_frame, bg="#27ae60", fg="white", font=("Segoe UI", 16, "bold"), bd=0, padx=24, pady=14, cursor="hand2", command=calculate)
calc_button.grid(row=0, column=0, padx=15)

save_button = tk.Button(button_frame, bg="#2980b9", fg="white", font=("Segoe UI", 16, "bold"), bd=0, padx=24, pady=14, cursor="hand2", command=save_user_data)
save_button.grid(row=0, column=1, padx=15)

load_button = tk.Button(button_frame, bg="#8e44ad", fg="white", font=("Segoe UI", 16, "bold"), bd=0, padx=24, pady=14, cursor="hand2", command=load_user_data)
load_button.grid(row=0, column=2, padx=15)

lang_toggle_btn = tk.Button(root, text="RU / EN", bg="#34495e", fg="white", font=("Segoe UI", 14, "bold"), bd=0, padx=12, pady=8, cursor="hand2", command=switch_language)
lang_toggle_btn.pack(pady=10)

update_ui_texts()

root.mainloop()
