from flet import *
import sqlite3
import openpyxl
from openpyxl.styles import Font, Alignment

# --- Database Setup ---
conn = sqlite3.connect("fine_arts1.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    code TEXT,
    depatmen TEXT,
    the_year_of_rat TEXT,
    ministeral_order TEXT,
    graduation_order TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    stage INTEGER,
    subject_name TEXT,
    unit INTEGER,
    mark REAL,
    FOREIGN KEY (student_id) REFERENCES students(id)
)
''')
conn.commit()




# --- Build Stage Frame ---
def build_stage_frame(stage_num, color):
    subject_fields = []
    unit_fields = []
    mark_fields = []
    mark_sums = []
    rows = []
    
    for i in range(16):
        subject = TextField(label=f"بابەت {i+1}", width=190, height=30, text_align='center')
        unit = TextField(label="یەکە", width=60, height=30, text_align='center')
        mark = TextField(label="نمرە", width=100, height=30, text_align='center')
        mark_sum = TextField(label="نمرە×یەکە", width=100, height=30, read_only=True, text_align='center')

        subject_fields.append(subject)
        unit_fields.append(unit)
        mark_fields.append(mark)
        mark_sums.append(mark_sum)

        rows.append(Row([subject, unit, mark, mark_sum], spacing=10))

    unit_total = TextField(label="⚖️ کۆی یەکەکان", read_only=True, width=150, height=30, text_align='center')
    mark_total = TextField(label="📊 کۆی نمرە×یەکە", read_only=True, width=150, height=30, text_align='center')
    frame_total = TextField(label="📌  کۆ نمرە", read_only=True, width=200, height=30, text_align='center')

    container = Container(
        content=Column([
            Text(f"قۆناغی {stage_num}", size=16, weight='bold', text_align='center'),
            *rows,
            Row([unit_total, mark_total], spacing=20),
            frame_total
        ], spacing=8),
        border_radius=10,
        padding=15,
        bgcolor=color,
        width=500,
        height=725,
        alignment=alignment.top_left
    )

    return {
        "frame": container,
        "subjects": subject_fields,
        "units": unit_fields,
        "marks": mark_fields,
        "mark_sums": mark_sums,
        "unit_total": unit_total,
        "mark_total": mark_total,
        "frame_total": frame_total
    }


# --- Main App ---
def main(page: Page):
    page.title = "Fine Arts - Students"
    page.scroll = "auto"
    page.window_width = 1200
    page.window_height = 950
    page.bgcolor = 'silver'
    page.theme_mode = ThemeMode.LIGHT

    name = TextField(label="ناوی قوتابی", width=250, rtl=True)
    code = TextField(label="کۆدی قوتابی", width=250, rtl=True)
    depatmen = TextField(label="بەش", width=250, rtl=True)
    the_year_of_rat = TextField(label="ساڵی دەرچوون", width=250, rtl=True)
    ministeral_order = TextField(label="فەرمانی وەرگرتن", width=250, rtl=True)
    graduation_order = TextField(label="فەرمانی دەرچوون", width=250, rtl=True)

    colors = ["#dcedc8", "#ffccbc", "#bbdefb", "#ffcdd2"]
    stage_frames = [build_stage_frame(i, colors[i-1]) for i in range(1, 5)]

    status = Text("", color="blue")

    total_grade = TextField(
        label="📌 کۆی چوار ساڵە  ",
        read_only=True,
        width=350,
        height=40,
        text_align='center',
        bgcolor="#eeeeee"
    )

    def update_totals(e=None):
        total_units = 0
        total_weighted_marks = 0

        stage_averages = []

        for frame in stage_frames:
            unit_sum = 0
            weighted_sum = 0

            for u, m, ms in zip(frame["units"], frame["marks"], frame["mark_sums"]):
                try:
                    if u.value and m.value:
                        u_val = int(u.value)
                        m_val = float(m.value)
                        product = u_val * m_val
                        ms.value = str(round(product, 2))
                        unit_sum += u_val
                        weighted_sum += product
                    else:
                        ms.value = ""
                except:
                    ms.value = ""

            frame["unit_total"].value = str(unit_sum)
            frame["mark_total"].value = str(round(weighted_sum, 2))
            avg = round(weighted_sum / unit_sum, 2) if unit_sum else 0
            frame["frame_total"].value = str(avg)

            total_units += unit_sum
            total_weighted_marks += weighted_sum

            stage_averages.append(avg)

        # کۆ نمرەی کۆتایی:
        weights = [0.10, 0.20, 0.30, 0.40]
        weighted_total = 0
        for avg, w in zip(stage_averages, weights):
            weighted_total += avg * w

        total_grade.value = str(round(weighted_total, 2))

        total_grade.bgcolor = "#ccffcc" if weighted_total >= 50 else "#ffcccc"
        page.update()

    def clear_fields():
        for field in [name, code, depatmen, the_year_of_rat, ministeral_order, graduation_order]:
            field.value = ""

        for frame in stage_frames:
            for f in frame["subjects"] + frame["units"] + frame["marks"] + frame["mark_sums"]:
                f.value = ""
            frame["unit_total"].value = ""
            frame["mark_total"].value = ""
            frame["frame_total"].value = ""

        total_grade.value = ""
        total_grade.bgcolor = "#eeeeee"
        status.value = ""
        page.update()

    def save_data(e):
        if not name.value.strip():
            status.value = "⚠️ تکایە ناو داخڵ بکە"
            page.update()
            return

        cursor.execute(
            "INSERT INTO students (name, code, depatmen, the_year_of_rat, ministeral_order, graduation_order) VALUES (?, ?, ?, ?, ?, ?)",
            (name.value, code.value, depatmen.value, the_year_of_rat.value, ministeral_order.value, graduation_order.value)
        )
        student_id = cursor.lastrowid

        for idx, frame in enumerate(stage_frames):
            for sub, unit, mark in zip(frame["subjects"], frame["units"], frame["marks"]):
                if sub.value.strip() and unit.value.strip() and mark.value.strip():
                    try:
                        u = int(unit.value)
                        m = float(mark.value)
                        cursor.execute(
                            "INSERT INTO subjects (student_id, stage, subject_name, unit, mark) VALUES (?, ?, ?, ?, ?)",
                            (student_id, idx + 1, sub.value, u, m)
                        )
                    except ValueError:
                        pass

        conn.commit()
        status.value = f"✅ {name.value} تۆمارکرا بەسەرکەوتوویی"
        clear_fields()
        page.update()

    def export_to_excel(e):
        if not name.value.strip():
            status.value = "⚠️ ناوی قوتابی داخڵ بکە بۆ ناردن"
            page.update()
            return

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Student Data"

        ws.append(["👤 ناوی قوتابی", name.value])
        ws.append(["🔢 کۆدی قوتابی", code.value])
        ws.append(["📚 بەش", depatmen.value])
        ws.append(["📅 ساڵی دەرچوون", the_year_of_rat.value])
        ws.append(["📜 فەرمانی وەرگرتن", ministeral_order.value])
        ws.append(["📜 فەرمانی دەرچوون", graduation_order.value])
        ws.append([])

        for idx, frame in enumerate(stage_frames):
            ws.append([f"📘 قۆناغی {idx+1}"])
            ws.append(["ناوی بابەت", "یەکە", "نمرە", "نمرە×یەکە"])

            for sub, unit, mark, product in zip(frame["subjects"], frame["units"], frame["marks"], frame["mark_sums"]):
                if sub.value.strip():
                    ws.append([sub.value, unit.value, mark.value, product.value])

            ws.append(["کۆی یەکەکان", frame["unit_total"].value])
            ws.append(["کۆی نمرە×یەکە", frame["mark_total"].value])
            ws.append(["📌کۆی چوار ساڵە " , frame["frame_total"].value])
            ws.append([])

        ws.append(["📊  کۆی چوار ساڵ", total_grade.value])

        for row in ws.iter_rows():
            for cell in row:
                cell.alignment = Alignment(horizontal="center")
                if cell.row == 1:
                    cell.font = Font(bold=True)

        safe_name = name.value.replace(" ", "_")
        filename = f"student_{safe_name}.xlsx"
        wb.save(filename)

        status.value = f"📤 هەڵگیرا: {filename}"
        page.update()

    for frame in stage_frames:
        for f in frame["units"] + frame["marks"]:
            f.on_change = update_totals

    update_totals()

    page.add(
        Column([
            Row([Image(src="sue.png", width=150)], alignment=MainAxisAlignment.CENTER),
            Row([code, name], alignment=MainAxisAlignment.CENTER),
            Row([depatmen, the_year_of_rat], alignment=MainAxisAlignment.CENTER),
            Row([ministeral_order, graduation_order], alignment=MainAxisAlignment.CENTER),
            Row([stage_frames[0]["frame"], stage_frames[1]["frame"]], alignment=MainAxisAlignment.CENTER, spacing=20, rtl=True),
            Row([stage_frames[2]["frame"], stage_frames[3]["frame"]], alignment=MainAxisAlignment.CENTER, spacing=20, rtl=True),
            Row([total_grade], alignment=MainAxisAlignment.CENTER),
            Row([
                ElevatedButton("💾 تۆمارکردن", on_click=save_data, bgcolor="green", color="white"),
                ElevatedButton("📤 ناردن بۆ Excel", on_click=export_to_excel, bgcolor="blue", color="white")
            ], alignment=MainAxisAlignment.CENTER),
            status
        ], scroll=ScrollMode.AUTO)
    )

app(target=main)
