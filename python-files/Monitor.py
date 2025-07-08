import pandas as pd
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from PIL import ImageGrab
from PIL import Image

# === CONFIG ===
px_per_minute = 2
bar_height = 20
row_gap = 30
top_margin = 120
left_offset = 220

# === Load Excel ===
df = pd.read_excel("X:\SESE\Testegantt.xlsx")  # Replace with your Excel file path

# Convert time columns to full datetime
time_cols = [
    'Tempo Teorico inicio', 'Tempo Teorico inicio Fim',
    'Início descarga', 'Fim de Descarga',
    'Inicio Checagem', 'Fim checagem',
    'Inicio putway', 'Fim Putway'
]
for col in time_cols:
    df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True) # Coerce invalid values to NaT

# === GUI ===
root = tk.Tk()
root.withdraw()

def open_gantt_chart():
    gantt_root = tk.Toplevel()
    gantt_root.title("Gantt Chart")
    gantt_root.state("zoomed")
    gantt_root.configure(bg="#f0f8ff")

    control_frame = tk.Frame(gantt_root, bg="#f0f8ff")
    control_frame.pack(fill="x", pady=5)

    start_var = tk.StringVar()
    end_var = tk.StringVar()
    all_start = df["Tempo Teorico inicio Fim"].min()
    all_end = df["Tempo Teorico inicio Fim"].max()
    start_var.set(all_start.strftime("%Y-%m-%d %H:%M:%S"))
    end_var.set(all_end.strftime("%Y-%m-%d %H:%M:%S"))

    tk.Label(control_frame, text="Start (YYYY-MM-DD HH:MM):", bg="#f0f8ff").pack(side="left", padx=5)
    tk.Entry(control_frame, textvariable=start_var, width=20).pack(side="left")

    tk.Label(control_frame, text="End (YYYY-MM-DD HH:MM):", bg="#f0f8ff").pack(side="left", padx=5)
    tk.Entry(control_frame, textvariable=end_var, width=20).pack(side="left")

    main_area = tk.Frame(gantt_root)
    main_area.pack(fill="both", expand=True)

    header_canvas = tk.Canvas(main_area, height=50, bg="white")
    header_canvas.pack(side="top", fill="x")

    chart_frame = tk.Frame(main_area)
    chart_frame.pack(fill="both", expand=True)

    label_canvas = tk.Canvas(chart_frame, width=200, bg="white")
    label_canvas.pack(side="left", fill="y")

    canvas = tk.Canvas(chart_frame, bg="white")
    canvas.pack(side="left", fill="both", expand=True)

    h_scroll = tk.Scrollbar(chart_frame, orient="horizontal", command=lambda *a: [canvas.xview(*a), header_canvas.xview(*a)])
    h_scroll.pack(side="bottom", fill="x")

    v_scroll = tk.Scrollbar(chart_frame, orient="vertical", command=lambda *a: [canvas.yview(*a), label_canvas.yview(*a)])
    v_scroll.pack(side="right", fill="y")

    canvas.config(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
    header_canvas.config(xscrollcommand=h_scroll.set)
    label_canvas.config(yscrollcommand=v_scroll.set)

    tooltip = None

    def show_tooltip(text, x, y):
        nonlocal tooltip
        if tooltip:
            tooltip.destroy()
        tooltip = tk.Toplevel(canvas)
        tooltip.wm_overrideredirect(True)
        tooltip.geometry(f"+{x+10}+{y+10}")
        label = tk.Label(tooltip, text=text, background="lightyellow", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip():
        nonlocal tooltip
        if tooltip:
            tooltip.destroy()
            tooltip = None

    def draw_legend():
        items = [("Descarga", "forestgreen"), ("Checagem", "gold"), ("Putway", "royalblue"), ("Tempo Teórico", "black")]
        x, y = 1200, 10
        for label, color in items:
            canvas.create_rectangle(x, y, x + 20, y + 20, fill=color if label != "Tempo Teórico" else "", outline=color)
            canvas.create_text(x + 30, y + 10, anchor="w", text=label, font=("Arial", 10))
            y += 25

    def draw_time_axis(start_time, total_minutes):
        for minute in range(0, total_minutes + 1, 60):
            current_time = start_time + pd.Timedelta(minutes=minute)
            x = minute * px_per_minute + left_offset
            label = current_time.strftime("%d-%m %H:%M")
            header_canvas.create_text(x + 5, 10, anchor="nw", text=label, font=("Arial", 9, "bold"))
            header_canvas.create_line(x, 30, x, 50, fill="#ccc", dash=(2, 4))
            canvas.create_line(x, top_margin - 10, x, 3000, fill="#ccc", dash=(2, 4))

    def draw_gantt():
        canvas.delete("all")
        header_canvas.delete("all")
        label_canvas.delete("all")
        draw_legend()

        try:
            start_filter = pd.to_datetime(start_var.get())
            end_filter = pd.to_datetime(end_var.get())
        except Exception as e:
            print("Invalid date format:", e)
            return

        filtered_df = df[
            (df["Tempo Teorico inicio Fim"] >= start_filter) &
            (df["Tempo Teorico inicio Fim"] <= end_filter)
        ]

        filtered_grouped = {}
        for _, row in filtered_df.iterrows():
            task_id = str(row['ID'])
            filtered_grouped[task_id] = []

            if pd.notna(row['Início descarga']) and pd.notna(row['Fim de Descarga']):
                filtered_grouped[task_id].append({
                    "label": "Descarga", "id": task_id,
                    "start": row['Início descarga'], "end": row['Fim de Descarga']
                })

            if pd.notna(row['Inicio Checagem']) and pd.notna(row['Fim checagem']):
                filtered_grouped[task_id].append({
                    "label": "Checagem", "id": task_id,
                    "start": row['Inicio Checagem'], "end": row['Fim checagem']
                })

            if pd.notna(row['Inicio putway']) and pd.notna(row['Fim Putway']):
                filtered_grouped[task_id].append({
                    "label": "Putway", "id": task_id,
                    "start": row['Inicio putway'], "end": row['Fim Putway']
                })

            if pd.notna(row['Tempo Teorico inicio']) and pd.notna(row['Tempo Teorico inicio Fim']):
                filtered_grouped[task_id].append({
                    "label": "Tempo Teórico", "id": task_id,
                    "start": row['Tempo Teorico inicio'], "end": row['Tempo Teorico inicio Fim'],
                    "outline": True
                })

        if not filtered_grouped:
            return

        min_time = min(task["start"] for tasks in filtered_grouped.values() for task in tasks)
        max_time = max(task["end"] for tasks in filtered_grouped.values() for task in tasks)
        total_minutes = int((max_time - min_time).total_seconds() / 60)
        draw_time_axis(min_time, total_minutes)

        canvas.config(scrollregion=(0, 0, total_minutes * px_per_minute + left_offset, len(filtered_grouped) * row_gap + top_margin))
        label_canvas.config(scrollregion=(0, 0, left_offset, len(filtered_grouped) * row_gap + top_margin))
        header_canvas.config(scrollregion=(0, 0, total_minutes * px_per_minute + left_offset, 50))

        task_rects = []

        for row_index, (task_id, task_list) in enumerate(filtered_grouped.items()):
            y = row_index * row_gap + top_margin
            try:
                janela_val = df.loc[df["ID"].astype(str) == str(task_id), "Janela"].values[0]
            except IndexError:
                janela_val = "—"

            label_canvas.create_text(10, y + bar_height / 2, anchor="w",
                                     text=f"ID: {task_id} | {janela_val}",
                                     font=("Arial", 8, "bold"))

            for task in task_list:
                start_offset = int((task["start"] - min_time).total_seconds() / 60)
                duration = int((task["end"] - task["start"]).total_seconds() / 60)
                x_start = start_offset * px_per_minute + left_offset
                x_end = x_start + duration * px_per_minute

                if task.get("outline"):
                    rect = canvas.create_rectangle(x_start, y,                    x_end, y + bar_height, outline="green2", width=2)
                else:
                    color = {
                        "Descarga": "forestgreen",
                        "Checagem": "gold",
                        "Putway": "royalblue"
                    }.get(task["label"], "gray")
                    rect = canvas.create_rectangle(x_start, y, x_end, y + bar_height, fill=color, outline="")
                    canvas.create_text(x_start + 5, y + bar_height / 2, anchor="w", text=task["label"], fill="white")

                task_rects.append((rect, f"{task['label']} ({duration} min)", task["id"], task["label"]))

        def on_click(event):
            x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
            for rect_id, _, tid, label in task_rects:
                coords = canvas.coords(rect_id)
                if coords and coords[0] <= x <= coords[2] and coords[1] <= y <= coords[3]:
                    for rid, _, other_tid, other_label in task_rects:
                        color = "gray" if other_tid == tid else {
                            "Descarga": "forestgreen",
                            "Checagem": "gold",
                            "Putway": "royalblue"
                        }.get(other_label, "gray")
                        canvas.itemconfig(rid, fill=color)
                    break

        def on_motion(event):
            x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
            for rect_id, text, _, _ in task_rects:
                coords = canvas.coords(rect_id)
                if coords and coords[0] <= x <= coords[2] and coords[1] <= y <= coords[3]:
                    if not tooltip:
                        show_tooltip(text, event.x_root, event.y_root)
                    return
            hide_tooltip()

        canvas.bind("<Button-1>", on_click)
        canvas.bind("<Motion>", on_motion)

    draw_gantt()

    def zoom(event):
        global px_per_minute
        if event.delta > 0:
            px_per_minute = min(px_per_minute * 1.2, 10)
        else:
            px_per_minute = max(px_per_minute / 1.2, 0.5)
        draw_gantt()

    canvas.bind("<MouseWheel>", zoom)
    canvas.bind_all("<Shift-MouseWheel>", lambda e: canvas.xview_scroll(-1 * int(e.delta / 120), "units"))

    def export_image():
        x = gantt_root.winfo_rootx() + canvas.winfo_x()
        y = gantt_root.winfo_rooty() + canvas.winfo_y()
        x1 = x + canvas.winfo_width()
        y1 = y + canvas.winfo_height()

        # Save as PNG first
        image_path = "gantt_export.png"
        pdf_path = "gantt_export.pdf"
        ImageGrab.grab().crop((x, y, x1, y1)).save(image_path)

        # Convert to PDF
        image = Image.open(image_path)
        if image.mode == "RGBA":
            image = image.convert("RGB")
        image.save(pdf_path, "PDF", resolution=100.0)

        print(f"Exported as {pdf_path}")


    ttk.Button(control_frame, text="Filtrar data", command=draw_gantt).pack(side="left", padx=10)
    ttk.Button(control_frame, text="Export", command=export_image).pack(side="left", padx=10)
    ttk.Button(gantt_root, text="⬅ Back to Menu", command=lambda: [gantt_root.destroy(), root.deiconify()]).pack(pady=10)

# Launch the Gantt chart window
open_gantt_chart()



root = tk.Tk()
root.title("")
root.state('zoomed')
root.configure(bg="#e9f0fa")

# Background gradient (using Canvas)
bg_canvas = tk.Canvas(root, width=1920, height=1080, highlightthickness=0)
bg_canvas.place(x=0, y=0)

for i in range(0, 1080, 2):
    shade = 240 - i // 10  # gradually darken from 240
    shade = max(200, shade)  # keep it from getting too dark
    hex_color = f"#{shade:02x}{shade:02x}{shade:02x}"
    bg_canvas.create_line(0, i, 1920, i, fill=hex_color)


# Animated fade-in (simple workaround using opacity over time)
root.attributes("-alpha", 0.0)
def fade_in(step=0):
    alpha = root.attributes("-alpha")
    if alpha < 1.0:
        alpha = min(1.0, alpha + 0.05)
        root.attributes("-alpha", alpha)
        root.after(50, fade_in)

fade_in()

# Header text
header = tk.Label(root, text="Monitor Loz",
                  font=("Segoe UI", 28, "bold"), bg="#e9f0fa", fg="#003366")
header.pack(pady=60)

# Fancy button style
def animate_click(widget):
    orig = widget.cget("bg")
    widget.configure(bg="#cce6ff")
    root.after(150, lambda: widget.configure(bg=orig))

def create_shiny_button(text, command):
    btn = tk.Label(root, text=text, font=("Segoe UI", 14, "bold"),
                   bg="white", fg="#003366", bd=4, relief="ridge", padx=20, pady=10,
                   cursor="hand2")
    btn.pack(pady=15)
    btn.bind("<Enter>", lambda e: btn.configure(bg="#f0f8ff"))
    btn.bind("<Leave>", lambda e: btn.configure(bg="white"))
    btn.bind("<Button-1>", lambda e: [animate_click(btn), command()])



    return btn

# Example button actions
def monitor_live():
    import tkinter as tk
    from tkinter import ttk
    import pandas as pd

    df = pd.read_excel("X:\SESE\Monitoslive.xlsx")
    latest = df.iloc[-1]

    # Create styled window
    win = tk.Toplevel()
    win.title("Monitor")
    win.state("zoomed")
    win.configure(bg="#e7f0fa")  # light blue-gray

    # Custom colors
    primary_color = "#007acc"     # deep blue
    accent_color = "#d6eaff"      # soft blue
    font_color = "#2c3e50"
    card_bg = "white"

    # Title section
    tk.Label(
        win, text="📊 Monitor", font=("Segoe UI", 24, "bold"),
        bg="#e7f0fa", fg=primary_color
    ).pack(pady=(30, 10))

    # Metrics panel frame
    content = tk.Frame(win, bg=card_bg, bd=2, relief="groove")
    content.pack(fill="both", expand=True, padx=60, pady=30)

    # Define and display metrics
    metrics = [
        ("Data", latest["Data"]),
        ("Total de Camiões", latest["Total de Camiões"]),
        ("Descarregados", latest["Descarregados"]),
        ("Checados", latest["Checados"]),
        ("LOZ 5 - Descarregados", latest["Descarregados Loz 5"]),
        ("LOZ 5 - Checados", latest["Checados LOZ 5"]),
        ("LOZ 7 CX - Descarregados", latest["Descarregados Loz 7 CX"]),
        ("LOZ 7 CX - Checados", latest["Checados LOZ 7 CX"]),
        ("LOZ 7 Mot - Descarregados", latest["Loz 7 Mot"]),
        ("LOZ 7 Mot - Checados", latest["Checados Loz 7 Mot"]),
        ("LOZ 10 - Descarregados", latest["Loz 10"]),
        ("LOZ 10 - Checados", latest["Checados LOZ 10"]),
    ]

    for i, (label, value) in enumerate(metrics):
        row = tk.Frame(content, bg=card_bg)
        row.grid(row=i, column=0, padx=20, pady=8, sticky="w")
        tk.Label(row, text=f"{label}:", font=("Segoe UI", 12), bg=card_bg, fg=font_color, width=28, anchor="w").pack(side="left")
        tk.Label(row, text=str(value), font=("Segoe UI", 12, "bold"), bg=card_bg, fg=primary_color).pack(side="left")

    # Animated detail effect (simple after() fade pulse)
    def pulse():
        current = title_label.cget("fg")
        new = "#005f99" if current == primary_color else primary_color
        title_label.config(fg=new)
        win.after(1000, pulse)

    title_label = tk.Label(win, text="⏱ Dados mais recentes atualizados", font=("Segoe UI", 10, "italic"), bg="#e7f0fa", fg=primary_color)
    title_label.pack(pady=(5, 0))
    pulse()  # start animation loop

    # Return button with style
    style = ttk.Style()
    style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"), foreground="white", background=primary_color)
    style.map("Accent.TButton",
              background=[("active", "#005f99"), ("pressed", "#004d80")])

    def close_window():
        win.destroy()

    ttk.Button(win, text="← Voltar ao Menu", style="Accent.TButton", command=close_window).pack(pady=25)





def report_diario():
    root.withdraw()
    report_win = tk.Toplevel()
    report_win.title("Relatório Diário")
    report_win.state("zoomed")
    report_win.configure(bg="#f0f8ff")

    title = tk.Label(report_win, text="📄 Relatório Diário",
                     font=("Segoe UI", 22, "bold"), bg="#f0f8ff", fg="#003366")
    title.pack(pady=20)

    frame = tk.Frame(report_win)
    frame.pack(fill="both", expand=True, padx=20, pady=10)

    cols = list(df.columns)
    tree = ttk.Treeview(frame, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))

    tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscroll=scrollbar.set)

    def back_to_menu():
        report_win.destroy()
        root.deiconify()

    ttk.Button(report_win, text="⬅ Voltar ao Menu", command=back_to_menu).pack(pady=10)


# Create the buttons
create_shiny_button("Monitor LOZ", monitor_live)
create_shiny_button("Gráfico Gantt", open_gantt_chart)
create_shiny_button("Report Diário", report_diario)

root.mainloop()
