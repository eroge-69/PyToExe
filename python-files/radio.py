#!/usr/bin/python3import tkinter as tk
import tkinter as tk
from tkinter import messagebox

def calculate():
    try:
        LiverCts_350s = float(entry_LiverCts_350s.get())
        LiverCts_150s = float(entry_LiverCts_150s.get())
        Activity_150s = float(entry_Activity_150s.get())
        BPInt = float(entry_BPInt.get())
        BloodPoolCts_150s = float(entry_BloodPoolCts_150s.get())
        FrameDuration = float(entry_FrameDuration.get())
        RemnantLiverArea = float(entry_RemnantLiverArea.get())
        WholeLiverArea = float(entry_WholeLiverArea.get())
        BSA = float(entry_BSA.get())
        FRL_Function = float(entry_FRL_Function.get())

        # Liver Uptake
        LiverUptake = (LiverCts_350s - LiverCts_150s) / (Activity_150s * BPInt / BloodPoolCts_150s)

        # Liver Uptake Rate % per minute
        LiverUptakeRate = 100 * LiverUptake * 60 / FrameDuration

        # Future Remnant Liver (FRL) Function % of Total Liver Uptake
        FRL_Function_pct = 100 * (RemnantLiverArea / WholeLiverArea)

        # FRL Function Normalised for BSA
        FRL_Function_Normalised = FRL_Function / BSA

        result_text = (
            f"Liver Uptake: {LiverUptake:.4f}\n"
            f"Liver Uptake Rate % per minute: {LiverUptakeRate:.4f}\n"
            f"Future Remnant Liver (FRL) Function %: {FRL_Function_pct:.4f}\n"
            f"FRL Function Normalised for BSA: {FRL_Function_Normalised:.4f}"
        )
        messagebox.showinfo("Результаты расчёта", result_text)

    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числовые значения.")

root = tk.Tk()
root.title("Расчёт по формуле Экмана")

labels = [
    "LiverCts(350s)", "LiverCts(150s)", "Activity(150s)", "BPInt",
    "BloodPoolCts(150s)", "Frame Duration (s)", "Remnant Liver Area", "Whole Liver Area",
    "BSA", "FRL Function"
]

entries = []
for label in labels:
    tk.Label(root, text=label).pack()
    entry = tk.Entry(root)
    entry.pack()
    entries.append(entry)

(entry_LiverCts_350s, entry_LiverCts_150s, entry_Activity_150s, entry_BPInt,
 entry_BloodPoolCts_150s, entry_FrameDuration, entry_RemnantLiverArea,
 entry_WholeLiverArea, entry_BSA, entry_FRL_Function) = entries

tk.Button(root, text="Вычислить", command=calculate).pack()

root.mainloop()
