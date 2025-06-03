import random
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Inches
import sys
import os

def generate_problems(max_number, operation_mode):
    cols = 4
    problems = []
    answers = []
    for _ in range(25):
        row = []
        answer_row = []
        for _ in range(cols):
            is_missing = random.random() < 0.3  # 30% 概率生成包含括号的题目

            if operation_mode == '加法':
                op = '+'
            elif operation_mode == '减法':
                op = '-'
            else:
                op = random.choice(['+', '-'])

            def valid_random_pair(op, max_number):
                while True:
                    if op == '+':
                        a = random.randint(1, max_number)
                        b = random.randint(1, max_number - a)
                        if a > 0 and b > 0:
                            return a, b, a + b
                    else:
                        a = random.randint(1, max_number)
                        b = random.randint(1, a)
                        if a > 0 and b > 0:
                            return a, b, a - b

            a, b, result = valid_random_pair(op, max_number)

            if is_missing:
                formats = [(f"(    ) {op} {b} = {result}", str(a)),
                           (f"{a} {op} (    ) = {result}", str(b)),
                           (f"{a} {op} {b} = (    )", str(result))]
                item, ans = random.choice(formats)
                row.append(item)
                answer_row.append(ans)
            else:
                row.append(f"{a} {op} {b} =    ")
                answer_row.append(str(result))
        problems.append(row)
        answers.append(answer_row)
    return problems, answers

def create_word(problems, answers, filepath):
    doc = Document()

    section = doc.sections[0]
    section.page_height = Inches(11.69)
    section.page_width = Inches(8.27)
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)

    heading = doc.add_heading("", level=1)
    run = heading.add_run("100题计算")
    run.font.size = Pt(20)
    run.font.name = '宋体'
    heading.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    heading.paragraph_format.space_before = Pt(0)

    table = doc.add_table(rows=len(problems), cols=4)
    table.autofit = True

    for row in table.rows:
        for cell in row.cells:
            tc = cell._tc
            tcPr = tc.get_or_add_tcPr()
            borders = OxmlElement('w:tcBorders')
            for border_name in ['top', 'left', 'bottom', 'right']:
                border = OxmlElement(f'w:{border_name}')
                border.set(qn('w:val'), 'nil')
                borders.append(border)
            tcPr.append(borders)

    for i, row in enumerate(problems):
        for j in range(4):
            paragraph = table.cell(i, j).paragraphs[0]
            run = paragraph.add_run(row[j])
            run.font.size = Pt(16)
            run.font.name = '宋体'
            paragraph.paragraph_format.line_spacing = 1.3
            paragraph.paragraph_format.space_before = Pt(0)
            paragraph.paragraph_format.space_after = Pt(0)

    p = doc.add_paragraph("日期：____年____月___日   用时：_____  得分:____")
    p.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
    run = p.runs[0]
    run.font.name = '宋体'
    run.font.size = Pt(16)

    doc.add_page_break()

    ans_heading = doc.add_heading("", level=1)
    run = ans_heading.add_run("答案")
    run.font.size = Pt(20)
    run.font.name = '宋体'
    ans_heading.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    ans_table = doc.add_table(rows=len(answers), cols=4)
    ans_table.autofit = True

    for i, row in enumerate(answers):
        for j in range(4):
            paragraph = ans_table.cell(i, j).paragraphs[0]
            run = paragraph.add_run(row[j])
            run.font.size = Pt(16)
            run.font.name = '宋体'
            paragraph.paragraph_format.line_spacing = 1.3
            paragraph.paragraph_format.space_before = Pt(0)
            paragraph.paragraph_format.space_after = Pt(0)

    doc.save(filepath)
    messagebox.showinfo("成功", f"练习题已生成并保存为:\n{filepath}")

def on_generate():
    max_range = difficulty_var.get()
    mode = operation_var.get()
    max_number = 20 if max_range == '20以内' else 100
    problems, answers = generate_problems(max_number, mode)

    filepath = filedialog.asksaveasfilename(defaultextension=".docx",
                                            filetypes=[("Word 文档", "*.docx")],
                                            title="保存为")
    if filepath:
        create_word(problems, answers, filepath)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == '__main__':
    root = tk.Tk()
    root.title("加减法练习题生成器")
    root.geometry("300x200")

    tk.Label(root, text="选择题目范围:").pack(pady=5)
    difficulty_var = tk.StringVar(value="20以内")
    ttks1 = ttk.Combobox(root, textvariable=difficulty_var, values=["20以内", "100以内"])
    ttks1.pack()

    tk.Label(root, text="选择运算类型:").pack(pady=5)
    operation_var = tk.StringVar(value="加减均可")
    ttks2 = ttk.Combobox(root, textvariable=operation_var, values=["加法", "减法", "加减均可"])
    ttks2.pack()

    tk.Button(root, text="生成Word文档", command=on_generate).pack(pady=20)

    root.mainloop()
