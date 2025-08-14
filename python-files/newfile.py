#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MND — Анализатор (Mobile portrait-optimized)
Версия: компактная, исправлена нижняя панель, добавлены Preset и Export CSV.
Учебный прототип — не мед. устройство.
"""

import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
import json
import csv
import os

# ---------- Reference ----------
REF = {
    "TSH_low": 0.4, "TSH_high": 4.0,
    "FT4_low": 9.0, "FT4_high": 22.0,
    "FT3_low": 2.6, "FT3_high": 6.8,
    "AT_TPO_pos": 34.0, "AT_TSHR_pos": 1.75
}

LOG_CSV = "mnd_log.csv"
LAST_JSON = "last_report.json"

def safe_float(x):
    try:
        if x is None or str(x).strip() == "":
            return None
        return float(str(x).strip())
    except:
        return None

def clamp_int(v):
    try:
        return max(0, min(100, int(round(v))))
    except:
        return 0

# --- аналитика (как было) ---
def compute_scores(tsh, ft4, ft3, at_tpo, at_tshr, symptoms_list):
    h_score = 0; h_reasons = []
    if tsh is not None:
        if tsh < 0.01:
            h_score += 4; h_reasons.append(f"TSH очень низкий ({tsh})")
        elif tsh < REF["TSH_low"]:
            h_score += 3; h_reasons.append(f"TSH понижен ({tsh})")
    if ft4 is not None:
        if ft4 > REF["FT4_high"] * 1.5:
            h_score += 3; h_reasons.append(f"FT4 значительно повышен ({ft4})")
        elif ft4 > REF["FT4_high"]:
            h_score += 2; h_reasons.append(f"FT4 повышен ({ft4})")
    if ft3 is not None:
        if ft3 > REF["FT3_high"] * 1.5:
            h_score += 3; h_reasons.append(f"FT3 значительно повышен ({ft3})")
        elif ft3 > REF["FT3_high"]:
            h_score += 2; h_reasons.append(f"FT3 повышен ({ft3})")
    if at_tshr is not None and at_tshr >= REF["AT_TSHR_pos"]:
        h_score += 3; h_reasons.append(f"AT-TSHR повышены ({at_tshr})")
    hyper_symptoms = {"тахикардия","тремор","похудание","потливость","непереносимость тепла","нервозность","экзофтальм"}
    hits = [s for s in symptoms_list if s in hyper_symptoms]
    if hits:
        h_score += min(len(hits),3); h_reasons.append("Симптомы: " + ", ".join(hits))
    hyper_pct = clamp_int(100.0 * h_score / max(1,13))

    p_score = 0; p_reasons = []
    if tsh is not None and tsh > REF["TSH_high"]:
        p_score += 4; p_reasons.append(f"TSH повышен ({tsh})")
    if ft4 is not None and ft4 < REF["FT4_low"]:
        p_score += 3; p_reasons.append(f"FT4 снижен ({ft4})")
    if at_tpo is not None and at_tpo > REF["AT_TPO_pos"]:
        p_score += 2; p_reasons.append(f"AT-TPO повышен ({at_tpo})")
    hypo_symptoms = {"утомляемость","зябкость","сухость кожи","запор","прибавка веса","отеки","выпадение волос"}
    hits2 = [s for s in symptoms_list if s in hypo_symptoms]
    if hits2:
        p_score += min(len(hits2),3); p_reasons.append("Симптомы: " + ", ".join(hits2))
    hypo_pct = clamp_int(100.0 * p_score / max(1,12))

    sub_score = 0; sub_reasons = []
    if tsh is not None and tsh < REF["TSH_low"] and (ft4 is None or ft4 <= REF["FT4_high"]) and (ft3 is None or ft3 <= REF["FT3_high"]):
        sub_score = 3; sub_reasons.append("Низкий TSH при нормальном FT4/FT3 — субклинический гипер")
    if tsh is not None and tsh > REF["TSH_high"] and ft4 is not None and ft4 >= REF["FT4_low"]:
        sub_score = 3; sub_reasons.append("Высокий TSH при нормальном FT4 — субклинический гипо")
    sub_pct = clamp_int(100.0 * sub_score / 3)

    tmn_score = 0; tmn_reasons = []
    if tsh is not None and tsh < REF["TSH_low"] and ((ft4 is not None and ft4 > REF["FT4_high"]) or (ft3 is not None and ft3 > REF["FT3_high"])):
        tmn_score += 2; tmn_reasons.append("Лаб. профиль гипертиреоза")
    if at_tshr is not None and at_tshr < REF["AT_TSHR_pos"]:
        tmn_score += 1; tmn_reasons.append("AT-TSHR не повышены")
    tmn_pct = clamp_int(100.0 * tmn_score / 4)

    thy_score = 0; thy_reasons = []
    if "боль" in symptoms_list or "боль в шее" in symptoms_list:
        thy_score += 2; thy_reasons.append("Боль в шее/чувствительность")
    if tsh is not None and tsh < REF["TSH_low"] and ft4 is not None and ft4 > REF["FT4_high"]:
        thy_score += 2; thy_reasons.append("Тиреотоксическая фаза")
    thy_pct = clamp_int(100.0 * thy_score / 4)

    return {
        "hyper": {"pct": hyper_pct, "reasons": h_reasons},
        "hypo": {"pct": hypo_pct, "reasons": p_reasons},
        "subclinical": {"pct": sub_pct, "reasons": sub_reasons},
        "toxic_mn": {"pct": tmn_pct, "reasons": tmn_reasons},
        "thyroiditis": {"pct": thy_pct, "reasons": thy_reasons}
    }

def build_report(patient_id, tsh, ft4, ft3, at_tpo, at_tshr, symptoms_raw):
    primary, details, _ = synthesize_all(tsh, ft4, ft3, at_tpo, at_tshr, symptoms_raw)
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    report = {
        "patient_id": patient_id or "anon",
        "timestamp": now,
        "inputs": {"TSH": tsh, "FT4": ft4, "FT3": ft3, "AT_TPO": at_tpo, "AT_TSHR": at_tshr, "symptoms": symptoms_raw},
        "primary": {"name": primary[0], "prob": int(primary[1]), "reasons": primary[2]},
        "details": details
    }
    return report

def synthesize_all(tsh, ft4, ft3, at_tpo, at_tshr, symptoms_raw):
    symptoms = [s.strip().lower() for s in (symptoms_raw or "").split(",") if s.strip()]
    scores = compute_scores(tsh, ft4, ft3, at_tpo, at_tshr, symptoms)
    items = [
        ("Гипертиреоз", scores["hyper"]["pct"], scores["hyper"]["reasons"]),
        ("Гипотиреоз", scores["hypo"]["pct"], scores["hypo"]["reasons"]),
        ("Субклиническая форма", scores["subclinical"]["pct"], scores["subclinical"]["reasons"]),
        ("Токсический зоб (подозрение)", scores["toxic_mn"]["pct"], scores["toxic_mn"]["reasons"]),
        ("Тиреоидит (подозрение)", scores["thyroiditis"]["pct"], scores["thyroiditis"]["reasons"])
    ]
    primary = sorted(items, key=lambda x: x[1], reverse=True)[0]
    return primary, scores, symptoms

# --- утилиты ---
def log_report_csv(report, path=None):
    headers = ["timestamp","patient_id","primary_name","primary_prob","TSH","FT4","FT3","AT_TPO","AT_TSHR","symptoms"]
    row = [
        report["timestamp"], report["patient_id"], report["primary"]["name"], report["primary"]["prob"],
        report["inputs"].get("TSH"), report["inputs"].get("FT4"), report["inputs"].get("FT3"),
        report["inputs"].get("AT_TPO"), report["inputs"].get("AT_TSHR"), report["inputs"].get("symptoms")
    ]
    try:
        out = path or LOG_CSV
        write_header = not os.path.exists(out)
        with open(out, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if write_header:
                w.writerow(headers)
            w.writerow(row)
    except Exception as e:
        print("Log error:", e)

def save_last_report(report):
    try:
        with open(LAST_JSON, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Save last error:", e)

def pmolL_to_ngdL_ft4(v):
    try: return round(float(v) * 0.0777, 3)
    except: return None
def ngdL_to_pmolL_ft4(v):
    try: return round(float(v) / 0.0777, 3)
    except: return None

# ---------- UI ----------
def create_mobile_ui():
    root = tk.Tk()
    root.title("МНД — Анализатор (Mobile)")
    root.geometry("360x780")
    root.configure(bg="#f7f9fb")

    # compact parameters
    CONTENT_PADX = 12
    ENTRY_FONT = ("Segoe UI", 10)
    BTN_FONT = ("Segoe UI", 10)
    BTN_HEIGHT = 1  # чуть уже кнопки

    # Header
    header = tk.Frame(root, bg="#2b6cdf", padx=CONTENT_PADX, pady=6)
    header.pack(fill="x")
    tk.Label(header, text="МНД — Анализатор", bg="#2b6cdf", fg="white", font=("Segoe UI", 18, "bold")).pack(fill="x")

    # Canvas + scrollable frame
    canvas = tk.Canvas(root, bg="#f7f9fb", highlightthickness=0, borderwidth=0)
    canvas.pack(side="top", fill="both", expand=True)

    scrollable_frame = tk.Frame(canvas, bg="#f7f9fb")
    window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    scrollable_frame.bind("<Configure>", on_frame_configure)

    def on_canvas_configure(event):
        try:
            canvas.itemconfig(window_id, width=event.width)
        except:
            pass
    canvas.bind("<Configure>", on_canvas_configure)

    # drag scrolling
    def _on_touch_start(event):
        try: canvas.scan_mark(event.x, event.y)
        except: pass
    def _on_touch_move(event):
        try: canvas.scan_dragto(event.x, event.y, gain=1)
        except: pass
    canvas.bind("<ButtonPress-1>", _on_touch_start)
    canvas.bind("<B1-Motion>", _on_touch_move)

    # mouse wheel support
    def _on_mousewheel(event):
        try:
            if hasattr(event, "num"):
                if event.num == 4: canvas.yview_scroll(-1, "units")
                elif event.num == 5: canvas.yview_scroll(1, "units")
            else:
                delta = int(-1 * (event.delta / 120))
                canvas.yview_scroll(delta, "units")
        except: pass
    root.bind_all("<MouseWheel>", _on_mousewheel)
    root.bind_all("<Button-4>", _on_mousewheel)
    root.bind_all("<Button-5>", _on_mousewheel)

    frame = scrollable_frame

    def labeled_entry(label_text):
        lbl = tk.Label(frame, text=label_text, bg="#f7f9fb", font=ENTRY_FONT)
        lbl.pack(anchor="w", padx=CONTENT_PADX, pady=(4,2))
        e = tk.Entry(frame, font=ENTRY_FONT)
        e.pack(fill="x", pady=(0,6), padx=CONTENT_PADX)
        return e

    ent_pid = labeled_entry("ID пациента (опц.):")
    ent_tsh = labeled_entry("TSH (мЕд/л):")
    ent_ft4 = labeled_entry("FT4 (пмоль/л):")
    ent_ft3 = labeled_entry("FT3 (пмоль/л):")
    ent_at_tpo = labeled_entry("AT-TPO (U/mL):")
    ent_at_tshr = labeled_entry("AT-TSHR (ед.):")

    lbl_sym = tk.Label(frame, text="Симптомы (через запятую):", bg="#f7f9fb", font=ENTRY_FONT)
    lbl_sym.pack(anchor="w", padx=CONTENT_PADX, pady=(4,2))
    ent_symptoms = tk.Entry(frame, font=ENTRY_FONT)
    ent_symptoms.pack(fill="x", pady=(0,6), padx=CONTENT_PADX)

    # buttons container
    btn_frame = tk.Frame(frame, bg="#f7f9fb")
    btn_frame.pack(fill="x", pady=(6,6), padx=CONTENT_PADX)

    # renderers
    def render_report_preview(report):
        p = report["primary"]
        lines = [f"{p['name']} — ~{p['prob']}%", "Основания:"]
        if p["reasons"]:
            lines += [f" - {r}" for r in p["reasons"][:3]]
        else:
            lines.append(" - нет явных оснований")
        return "\n".join(lines)

    def render_report_text(report):
        lines = []
        p = report["primary"]
        lines.append("КЛИНИЧЕСКОЕ ЗАКЛЮЧЕНИЕ")
        lines.append(f"Пациент: {report['patient_id']}")
        lines.append(f"Время: {report['timestamp']}\n")
        lines.append(f"Основная вероятность: {p['name']} — ~{p['prob']}%\n")
        lines.append("Входные данные:")
        for k,v in report["inputs"].items():
            lines.append(f" • {k}: {v}")
        lines.append("\nОснования:")
        for i,r in enumerate(p["reasons"], start=1):
            lines.append(f" {i}. {r}")
        lines.append("\nДетали:")
        for k,val in report["details"].items():
            reasons = "; ".join(val["reasons"]) if val["reasons"] else "—"
            lines.append(f" • {k}: {val['pct']}% — {reasons}")
        lines.append("\nРекомендации: обсудить с эндокринологом. Это образовательный прототип.")
        return "\n".join(lines)

    def show_full_report(report):
        txt = render_report_text(report)
        win = tk.Toplevel(root)
        win.title("Полный отчёт")
        win.geometry("600x700")
        t = tk.Text(win, wrap="word")
        t.insert("1.0", txt)
        t.config(state="disabled")
        t.pack(fill="both", expand=True)
        tk.Button(win, text="Закрыть", command=win.destroy).pack(pady=6)

    # actions
    def calc_risk_action():
        tsh = safe_float(ent_tsh.get()); ft4 = safe_float(ent_ft4.get()); ft3 = safe_float(ent_ft3.get())
        at_tpo = safe_float(ent_at_tpo.get()); at_tshr = safe_float(ent_at_tshr.get())
        symptoms_raw = ent_symptoms.get()
        if tsh is None:
            messagebox.showerror("Ошибка", "Введите корректный TSH")
            return
        primary, scores, _ = synthesize_all(tsh, ft4, ft3, at_tpo, at_tshr, symptoms_raw)
        lines = [f"Пациент: {ent_pid.get() or 'anon'}", f"Основная вероятность: {primary[0]} (~{primary[1]}%)", ""]
        for k, v in scores.items():
            reasons = "; ".join(v["reasons"]) if v["reasons"] else "—"
            lines.append(f"{k}: {v['pct']}% — {reasons}")
        result_label.config(text="\n".join(lines))
        status_label.config(text="Риски рассчитаны", bg="#4caf50")

    def analyze_action():
        show_processing()
        try:
            tsh = safe_float(ent_tsh.get()); ft4 = safe_float(ent_ft4.get()); ft3 = safe_float(ent_ft3.get())
            at_tpo = safe_float(ent_at_tpo.get()); at_tshr = safe_float(ent_at_tshr.get())
            symptoms_raw = ent_symptoms.get()
            if tsh is None:
                messagebox.showerror("Ошибка", "Введите корректный TSH")
                return
            report = build_report(ent_pid.get(), tsh, ft4, ft3, at_tpo, at_tshr, symptoms_raw)
            preview = render_report_preview(report)
            result_label.config(text=preview)
            status_label.config(text=f"Анализ готов: {report['primary']['name']} ~{report['primary']['prob']}%", bg="#4caf50")
            if not view_full_btn.winfo_ismapped():
                view_full_btn.pack(fill="x", padx=CONTENT_PADX, pady=(6,4))
            try:
                log_report_csv(report)
                save_last_report(report)
            except Exception as e:
                print("Logging/saving last failed:", e)
        finally:
            stop_processing()

    def save_json_action():
        tsh = safe_float(ent_tsh.get())
        if tsh is None:
            messagebox.showerror("Ошибка", "Введите TSH перед сохранением")
            return
        report = build_report(ent_pid.get(), safe_float(ent_tsh.get()), safe_float(ent_ft4.get()), safe_float(ent_ft3.get()), safe_float(ent_at_tpo.get()), safe_float(ent_at_tshr.get()), ent_symptoms.get())
        fname = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON","*.json")])
        if not fname:
            return
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Сохранено", f"Файл сохранён: {fname}")

    def clear_inputs_action():
        for e in (ent_pid, ent_tsh, ent_ft4, ent_ft3, ent_at_tpo, ent_at_tshr, ent_symptoms):
            e.delete(0, "end")
        result_label.config(text="Результат появится здесь")
        status_label.config(text="Очищено", bg="#9e9e9e")

    def copy_preview_action():
        txt = result_label.cget("text")
        if not txt or txt.strip() == "":
            messagebox.showinfo("Копирование", "Нет текста для копирования")
            return
        root.clipboard_clear()
        root.clipboard_append(txt)
        messagebox.showinfo("Копирование", "Текст скопирован в буфер обмена")

    def load_last_report_action():
        try:
            with open(LAST_JSON, "r", encoding="utf-8") as f:
                r = json.load(f)
            ent_pid.delete(0,"end"); ent_pid.insert(0, r.get("patient_id",""))
            inputs = r.get("inputs",{})
            def put(e, k): e.delete(0,"end"); e.insert(0, str(inputs.get(k,"") or ""))
            put(ent_tsh, "TSH"); put(ent_ft4, "FT4"); put(ent_ft3, "FT3"); put(ent_at_tpo, "AT_TPO"); put(ent_at_tshr, "AT_TSHR")
            ent_symptoms.delete(0,"end"); ent_symptoms.insert(0, inputs.get("symptoms",""))
            result_label.config(text=render_report_preview(r))
            status_label.config(text="Загружен последний отчёт", bg="#ffb300")
        except Exception:
            messagebox.showinfo("Загрузка", "Нет сохранённого последнего отчёта")

    def convert_ft4_action():
        val = safe_float(ent_ft4.get())
        if val is None:
            messagebox.showinfo("Конвертация", "Введите FT4 (pmol/L) в поле")
            return
        converted = pmolL_to_ngdL_ft4(val)
        messagebox.showinfo("Конвертация FT4", f"{val} pmol/L ≈ {converted} ng/dL")

    # --- новые маленькие фичи ---
    def fill_sample_data():
        ent_pid.delete(0,"end"); ent_pid.insert(0, "test_001")
        ent_tsh.delete(0,"end"); ent_tsh.insert(0, "0.05")
        ent_ft4.delete(0,"end"); ent_ft4.insert(0, "40")
        ent_ft3.delete(0,"end"); ent_ft3.insert(0, "8")
        ent_at_tpo.delete(0,"end"); ent_at_tpo.insert(0, "10")
        ent_at_tshr.delete(0,"end"); ent_at_tshr.insert(0, "2.0")
        ent_symptoms.delete(0,"end"); ent_symptoms.insert(0, "тахикардия,тремор")
        status_label.config(text="Заполнены примерные данные", bg="#607d8b")

    def export_log_action():
        # ask where to save
        fpath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not fpath:
            return
        # try copy current log to chosen path
        try:
            if os.path.exists(LOG_CSV):
                with open(LOG_CSV, "r", encoding="utf-8") as src:
                    data = src.read()
                with open(fpath, "w", encoding="utf-8", newline="") as dst:
                    dst.write(data)
                messagebox.showinfo("Экспорт", f"Журнал экспортирован: {fpath}")
            else:
                messagebox.showinfo("Экспорт", "Лог пуст: нет данных для экспорта")
        except Exception as e:
            messagebox.showerror("Экспорт", f"Ошибка при экспорте: {e}")

    # processing indicator
    def show_processing(msg="Анализ..."):
        dots = [".","..","..."]
        idx = 0
        def tick():
            nonlocal idx
            status_label.config(text=msg + dots[idx % len(dots)], bg="#0288d1")
            idx += 1
            status_label._after_id = root.after(400, tick)
        tick()

    def stop_processing():
        try:
            root.after_cancel(status_label._after_id)
        except:
            pass
        status_label.config(text="Готово", bg="#4caf50")

    # buttons (compact)
    bopts = {"font": BTN_FONT, "height": BTN_HEIGHT}
    btn_risk = tk.Button(btn_frame, text="Калькулятор рисков", bg="#2196f3", fg="white", command=calc_risk_action, **bopts)
    btn_risk.pack(fill="x", pady=3)
    btn_analyze = tk.Button(btn_frame, text="Анализировать", bg="#00a86b", fg="white", command=analyze_action, **bopts)
    btn_analyze.pack(fill="x", pady=3)
    btn_save = tk.Button(btn_frame, text="Сохранить JSON", bg="#455a64", fg="white", command=save_json_action, **bopts)
    btn_save.pack(fill="x", pady=3)

    btn_clear = tk.Button(btn_frame, text="Очистить", bg="#ef5350", fg="white", command=clear_inputs_action, **bopts)
    btn_clear.pack(fill="x", pady=3)
    btn_copy = tk.Button(btn_frame, text="Копировать превью", bg="#607d8b", fg="white", command=copy_preview_action, **bopts)
    btn_copy.pack(fill="x", pady=3)
    btn_load_last = tk.Button(btn_frame, text="Загрузить последний", command=load_last_report_action, font=BTN_FONT, height=1)
    btn_load_last.pack(fill="x", pady=3)
    btn_conv = tk.Button(btn_frame, text="FT4 → ng/dL", command=convert_ft4_action, font=BTN_FONT, height=1)
    btn_conv.pack(fill="x", pady=3)

    # presets & export
    btn_sample = tk.Button(btn_frame, text="Пример данных", command=fill_sample_data, font=BTN_FONT, height=1)
    btn_sample.pack(fill="x", pady=3)
    btn_export = tk.Button(btn_frame, text="Экспорт журнала", command=export_log_action, font=BTN_FONT, height=1)
    btn_export.pack(fill="x", pady=3)

    # bottom area (fixed): preview and status bar
    bottom_frame = tk.Frame(root, bg="#f7f9fb")
    bottom_frame.pack(side="bottom", fill="x")

    view_full_btn = tk.Button(bottom_frame, text="Показать полный отчёт", bg="#607d8b", fg="white", command=lambda: show_full_report(build_report(ent_pid.get(), safe_float(ent_tsh.get()), safe_float(ent_ft4.get()), safe_float(ent_ft3.get()), safe_float(ent_at_tpo.get()), safe_float(ent_at_tshr.get()), ent_symptoms.get())), font=BTN_FONT)
    view_full_btn.pack_forget()

    # ограниченная высота превью — чтобы статусбар всегда видно и не накладывался
    result_label = tk.Label(bottom_frame, text="Результат появится здесь", bg="white", anchor="nw", justify="left", bd=1, relief="solid", padx=8, pady=6)
    result_label.pack(fill="both", expand=False, padx=CONTENT_PADX, pady=(8,4))
    result_label.config(height=3)  # небольшой фикс по высоте (в строках), видно сразу — можно увеличить при надобности

    status_label = tk.Label(root, text="Готово", bg="#4caf50", fg="white", anchor="w", relief="flat")
    status_label.pack(side="bottom", fill="x")

    # validation & button enable
    def highlight_on_invalid(entry):
        val = entry.get().strip()
        if val == "":
            entry.config(bg="white"); return
        try:
            float(val)
            entry.config(bg="white")
        except:
            entry.config(bg="#ffe6e6")

    def update_buttons_state(*_):
        valid = False
        try:
            valid = ent_tsh.get().strip() != "" and safe_float(ent_tsh.get()) is not None
        except:
            valid = False
        state = "normal" if valid else "disabled"
        btn_risk.config(state=state)
        btn_analyze.config(state=state)
        btn_save.config(state=state)

    for e in (ent_tsh, ent_ft4, ent_ft3, ent_at_tpo, ent_at_tshr, ent_symptoms):
        e.bind("<FocusOut>", lambda ev, en=e: highlight_on_invalid(en))
        e.bind("<KeyRelease>", lambda ev: update_buttons_state())

    update_buttons_state()

    # expose helpers to globals if needed
    globals().update({
        "render_report_text": render_report_text,
        "render_report_preview": render_report_preview,
        "show_full_report": show_full_report,
        "build_report": build_report,
        "synthesize_all": synthesize_all
    })

    root.mainloop()

if __name__ == "__main__":
    create_mobile_ui()