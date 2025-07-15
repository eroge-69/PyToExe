import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageSequence

def fcfs(processes):
    processes.sort(key=lambda x: x['arrival_time'])
    time = 0
    gantt_chart = []
    for process in processes:
        if time < process['arrival_time']: time = process['arrival_time']
        start = time
        finish = time + process['burst_time']
        time = finish
        process['start_time'] = start
        process['finish_time'] = finish
        process['turnaround_time'] = finish - process['arrival_time']
        process['waiting_time'] = process['turnaround_time'] - process['burst_time']
        gantt_chart.append((process['pid'], start, finish))
    return processes, gantt_chart

def sjf(processes):
    n = len(processes)
    completed = 0
    time = 0
    gantt_chart = []
    processes = sorted(processes, key=lambda x: x['arrival_time'])
    is_completed = [False] * n
    while completed < n:
        ready_queue = []
        for i, p in enumerate(processes):
            if p['arrival_time'] <= time and not is_completed[i]: ready_queue.append(p)
        if ready_queue:
            current = min(ready_queue, key=lambda x: x['burst_time'])
            idx = processes.index(current)
            start = time
            finish = time + current['burst_time']
            time = finish
            processes[idx]['start_time'] = start
            processes[idx]['finish_time'] = finish
            processes[idx]['turnaround_time'] = finish - current['arrival_time']
            processes[idx]['waiting_time'] = processes[idx]['turnaround_time'] - processes[idx]['burst_time']
            is_completed[idx] = True
            completed += 1
            gantt_chart.append((current['pid'], start, finish))
        else:
            time += 1
    return processes, gantt_chart

def rr(processes, quantum):
    n = len(processes)
    queue = []
    time = 0
    completed = 0
    remaining_bt = [p['burst_time'] for p in processes]
    is_started = [False] * n
    is_completed = [False] * n
    gantt_chart = []
    processes = sorted(processes, key=lambda x: x['arrival_time'])
    arrived = [False] * n
    while completed < n:
        for i, p in enumerate(processes):
            if p['arrival_time'] <= time and not arrived[i]:
                queue.append(i)
                arrived[i] = True
        if not queue:
            time += 1
            continue
        idx = queue.pop(0)
        p = processes[idx]
        if not is_started[idx]:
            p['start_time'] = time
            is_started[idx] = True
        exec_time = min(quantum, remaining_bt[idx])
        gantt_chart.append((p['pid'], time, time + exec_time))
        time += exec_time
        remaining_bt[idx] -= exec_time
        for i, proc in enumerate(processes):
            if proc['arrival_time'] <= time and not arrived[i]:
                queue.append(i)
                arrived[i] = True
        if remaining_bt[idx] == 0:
            is_completed[idx] = True
            completed += 1
            p['finish_time'] = time
            p['turnaround_time'] = time - p['arrival_time']
            p['waiting_time'] = p['turnaround_time'] - p['burst_time']
        else:
            queue.append(idx)
    return processes, gantt_chart

def generate_table():
    try:
        count = int(entry_count.get())
        if not (7 <= count <= 10): messagebox.showerror("Error", "Number of processes must be between 7 and 10."); return
    except ValueError: messagebox.showerror("Error", "Please enter a valid integer for the number of processes."); return
    for widget in frame_table_inputs.winfo_children(): widget.destroy()
    headers = ["Process ID", "Arrival Time", "Burst Time"]
    for j, header in enumerate(headers): tk.Label(frame_table_inputs, text=header, width=15, borderwidth=1, relief="solid", bg=bg_color, font=default_font).grid(row=0, column=j)
    input_entries.clear()
    for i in range(count):
        row = []
        tk.Label(frame_table_inputs, text=f"P{i+1}", width=15, borderwidth=1, relief="solid", bg=bg_color, font=default_font).grid(row=i+1, column=0)
        at_entry = tk.Entry(frame_table_inputs, width=17, borderwidth=1, relief="solid", font=default_font, justify='center'); at_entry.grid(row=i+1, column=1); row.append(at_entry)
        bt_entry = tk.Entry(frame_table_inputs, width=17, borderwidth=1, relief="solid", font=default_font, justify='center'); bt_entry.grid(row=i+1, column=2); row.append(bt_entry)
        input_entries.append(row)

def run_scheduler():
    algo = algo_var.get()
    processes = []
    for i, row in enumerate(input_entries):
        try:
            at = int(row[0].get()); bt = int(row[1].get())
            if at < 0 or bt <= 0: messagebox.showerror("Error", f"The input must be a positive integer for P{i+1}."); return
            processes.append({'pid': f"P{i+1}", 'arrival_time': at, 'burst_time': bt, 'priority': 0})
        except ValueError: messagebox.showerror("Error", f"Invalid input in row {i+1}. Please enter positive intergers only."); return
    if not processes: messagebox.showwarning("No Processes", "Enter inputs first."); return
    result = []; gantt = []
    if algo == "First Come First Serve": result, gantt = fcfs(processes)
    elif algo == "Shortest Job First": result, gantt = sjf(processes)
    elif algo == "Round Robin":
        try:
            quantum = int(entry_quantum.get())
            if quantum <= 0: messagebox.showerror("Error", "The value must be positive."); return
        except ValueError: messagebox.showerror("Error", "Please enter a valid positive integer for Time Quantum."); return
        result, gantt = rr(processes, quantum)
    else: messagebox.showerror("Error", f"{algo} not yet implemented."); return
    update_table(result)
    draw_gantt(gantt)

def clear_inputs():
    entry_count.delete(0, tk.END); entry_quantum.delete(0, tk.END)
    for row in input_entries:
        for entry in row: entry.delete(0, tk.END)
    for i in table.get_children(): table.delete(i)
    canvas.delete("all")
    label_avg.config(text="AVERAGE WAITING TIME: 0.00 ms         AVERAGE TURNAROUND TIME: 0.00 ms")

def update_table(results):
    for i in table.get_children(): table.delete(i)
    total_wt = 0; total_tat = 0
    for p in results:
        table.insert("", tk.END, values=(p['pid'], p['arrival_time'], p['burst_time'], p['start_time'], p['finish_time'], p['waiting_time'], p['turnaround_time']))
        total_wt += p['waiting_time']; total_tat += p['turnaround_time']
    n = len(results)
    avg_wt = total_wt / n if n > 0 else 0; avg_tat = total_tat / n if n > 0 else 0
    label_avg.config(text=f"AVERAGE WAITING TIME: {avg_wt:.2f} ms         AVERAGE TURNAROUND TIME: {avg_tat:.2f} ms")

def draw_gantt(gantt):
    canvas.delete("all")
    canvas_width = canvas.winfo_width()
    if not gantt: return
    total_time = gantt[-1][2]
    scale = 30
    chart_width = total_time * scale
    x_start = max((canvas_width - chart_width) // 2, 10)
    x = x_start
    for pid, start, end in gantt:
        block_width = (end - start) * scale
        canvas.create_rectangle(x, 20, x + block_width, 70, fill="#FFCCCC", outline="black")
        canvas.create_text(x + block_width // 2, 45, text=pid, font=default_font)
        canvas.create_text(x, 75, text=str(start), anchor=tk.NW, font=default_font)
        x += block_width
    canvas.create_text(x, 75, text=str(gantt[-1][2]), anchor=tk.NW, font=default_font)

def on_algo_change(event=None):
    if algo_var.get() == "Round Robin": quantum_frame.pack(after=frame_top, pady=5)
    else: quantum_frame.pack_forget()
    try:
        if int(entry_count.get()) > 0: generate_table()
    except ValueError: pass

def launch_main_app():
    frame_front.pack_forget()
    frame_front_text_only.pack_forget()
    scrollable_frame_container.pack(expand=True, fill="both")
    main_canvas.bind("<Configure>", lambda e: main_canvas.itemconfig(main_canvas_window_id, width=e.width))
    main_frame.update_idletasks()
    main_canvas.config(scrollregion=main_canvas.bbox("all"))

def back_to_front():
    scrollable_frame_container.pack_forget()
    if front_tk_frames:
        frame_front.pack(expand=True, fill="both")
        front_page_image_label.place(x=0, y=0, relwidth=1, relheight=1)
        start_button.place(relx=0.5, rely=0.85, anchor=tk.CENTER)
        if len(front_tk_frames) > 1:
            animate_front_gif()
    else:
        frame_front_text_only.pack(expand=True, fill="both")

front_tk_frames = []
front_current_frame_index = 0
front_gif_delay = 100

main_tk_frames = []
main_bg_image_id = None

def animate_front_gif():
    global front_current_frame_index
    if front_tk_frames:
        frame = front_tk_frames[front_current_frame_index]
        front_page_image_label.config(image=frame)
        front_page_image_label.image = frame
        front_current_frame_index = (front_current_frame_index + 1) % len(front_tk_frames)
        root._front_anim_id = root.after(front_gif_delay, animate_front_gif)

def display_main_background_image(image_tk_frame):
    global main_bg_image_id
    if main_bg_image_id:
        main_canvas.delete(main_bg_image_id)
    if image_tk_frame:
        main_bg_image_id = main_canvas.create_image(0, 0, image=image_tk_frame, anchor="nw")
        main_canvas.tag_lower(main_bg_image_id, main_canvas_window_id)
        main_canvas.image = image_tk_frame
    else:
        pass

def load_image_frames(image_path, tk_frames_list, new_width, new_height):
    tk_frames_list.clear()
    try:
        pil_image_obj = Image.open(image_path)
        if pil_image_obj.is_animated:
            for frame in ImageSequence.Iterator(pil_image_obj):
                resized_frame = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
                tk_frames_list.append(ImageTk.PhotoImage(resized_frame))
            return pil_image_obj.info.get('duration', 100)
        else:
            resized_image = pil_image_obj.resize((new_width, new_height), Image.Resampling.LANCZOS)
            tk_frames_list.append(ImageTk.PhotoImage(resized_image))
            return 100
    except Exception as e:
        return 100

def resize_front_image(event):
    global front_gif_delay
    global front_current_frame_index
    if front_gif_path and 'front_page_image_label' in globals():
        new_width = event.width
        new_height = event.height
        if new_width > 0 and new_height > 0:
            if hasattr(root, '_front_anim_id') and root._front_anim_id is not None:
                root.after_cancel(root._front_anim_id)
                root._front_anim_id = None
            
            front_gif_delay = load_image_frames(front_gif_path, front_tk_frames, new_width, new_height)
            front_current_frame_index = 0
            
            if front_tk_frames:
                front_page_image_label.config(image=front_tk_frames[0])
                front_page_image_label.image = front_tk_frames[0]
                if len(front_tk_frames) > 1:
                    animate_front_gif()
            else:
                frame_front.pack_forget()
                frame_front_text_only.pack(expand=True, fill="both")
                start_button_text_only.place(relx=0.5, rely=0.85, anchor=tk.CENTER) # Reposition button on text-only page

def resize_main_background(event):
    if main_image_path and 'main_canvas' in globals():
        new_width = event.width
        new_height = event.height
        if new_width > 0 and new_height > 0:
            load_image_frames(main_image_path, main_tk_frames, new_width, new_height)
            if main_tk_frames:
                display_main_background_image(main_tk_frames[0])
            else:
                main_canvas.config(bg=bg_color)

bg_color = "#FB84A6"
title_fg_color = "#820000"
button_fg_color = "#511414"
secondary_font_family = "Segoe UI"
default_font = (secondary_font_family, 13)

root = tk.Tk()
root.title("CPU Process Scheduling Calculator (Group 5 – CpE-3301)")
root.state('zoomed')

frame_front = tk.Frame(root)
frame_front.pack(expand=True, fill="both")

front_gif_path = "C:\\Users\\addim\\Downloads\\bg.gif" # Keep this path for image loading attempt
front_page_image_label = tk.Label(frame_front)
front_page_image_label.place(x=0, y=0, relwidth=1, relheight=1)
frame_front.bind("<Configure>", resize_front_image)
root._front_anim_id = None

start_button = tk.Button(frame_front, text="START", font=(secondary_font_family, 25, "bold"), command=launch_main_app, bg="#FFB6C1", fg=button_fg_color, relief="raised", bd=5, padx=20, pady=10)
start_button.place(relx=0.5, rely=0.85, anchor=tk.CENTER)

# Alternate text-only front page
frame_front_text_only = tk.Frame(root, bg=bg_color)

tk.Label(frame_front_text_only, text="CPU PROCESS\nSCHEDULING CALCULATOR", font=("Bahnschrift", 45, "bold"), bg=bg_color, fg=title_fg_color).pack(pady=30)
tk.Label(frame_front_text_only, text="CpE 424: OPERATING SYSTEMS", font=(secondary_font_family, 25, "bold"), bg=bg_color, fg=title_fg_color).pack(pady=10)
tk.Label(frame_front_text_only, text="\nGroup 5\nCpE-3301", font=(secondary_font_family, 18, "bold"), bg=bg_color, fg=title_fg_color).pack(pady=5)
names = ["Arancel, Ivy Zenia", "Hebrado, Jazther", "Magbojos, Von Homersly", "Manansala, Addi", "Ramos, Ana Marie", "Revilla, Lynzy Anne"]
for name in names:
    tk.Label(frame_front_text_only, text=name, font=(secondary_font_family, 14), bg=bg_color, fg=title_fg_color).pack()

start_button_text_only = tk.Button(frame_front_text_only, text="START", font=("Bahnschrift", 25, "bold"), command=launch_main_app, bg="#FFB6C1", fg=button_fg_color, relief="raised", bd=5, padx=20, pady=10)
start_button_text_only.place(relx=0.5, rely=0.85, anchor=tk.CENTER)


scrollable_frame_container = tk.Frame(root)
main_image_path = ""
scrollable_frame_container.bind("<Configure>", resize_main_background)
main_canvas = tk.Canvas(scrollable_frame_container, bg=bg_color, highlightthickness=0)
main_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
main_scrollbar = ttk.Scrollbar(scrollable_frame_container, orient="vertical", command=main_canvas.yview)
main_canvas.configure(yscrollcommand=main_scrollbar.set)
main_scrollbar.pack(side="right", fill="y")
main_canvas.pack(side="left", fill="both", expand=True)
main_frame = tk.Frame(main_canvas, bg=bg_color)
main_canvas_window_id = main_canvas.create_window((0, 0), window=main_frame, anchor="nw")
main_frame.bind("<Configure>", lambda event: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
back_btn_frame = tk.Frame(main_frame, bg=bg_color); back_btn_frame.pack(anchor="ne", pady=10, padx=10)
tk.Button(back_btn_frame, text="BACK", font=(secondary_font_family, 18, "bold"), command=back_to_front, bg="#FFB6C1", fg=button_fg_color, relief="raised", bd=3).pack()
tk.Label(main_frame, text="CPU PROCESS\nSCHEDULING CALCULATOR", font=("Bahnschrift", 45, "bold"), bg=bg_color, fg=title_fg_color).pack(pady=20)
frame_top = tk.Frame(main_frame, bg=bg_color); frame_top.pack(pady=10)
tk.Label(frame_top, text="Number of Processes (7-10):", bg=bg_color, font=default_font).pack(side=tk.LEFT)
entry_count = tk.Entry(frame_top, width=5, font=default_font, justify='center'); entry_count.pack(side=tk.LEFT, padx=15)
tk.Button(frame_top, text="CREATE TABLE", command=generate_table, font=(secondary_font_family, 8, "bold"), bg="#FFB6C1", fg=button_fg_color, relief="raised", bd=3).pack(side=tk.LEFT)
quantum_frame = tk.Frame(main_frame, bg=bg_color)
label_quantum = tk.Label(quantum_frame, text="Time Quantum: ", bg=bg_color, font=default_font); label_quantum.pack(side=tk.LEFT)
entry_quantum = tk.Entry(quantum_frame, width=5, font=default_font, justify='center'); entry_quantum.pack(side=tk.LEFT)
algo_var = tk.StringVar(value="First Come First Serve")
frame_algo = tk.Frame(main_frame, bg=bg_color); frame_algo.pack(pady=5)
tk.Label(frame_algo, text="Choose Algorithm: ", bg=bg_color, font=default_font).pack(side=tk.LEFT)
algo_dropdown = ttk.Combobox(frame_algo, textvariable=algo_var, values=["First Come First Serve", "Shortest Job First", "Round Robin"], state="readonly", font=default_font, width=30); algo_dropdown.pack(side=tk.LEFT, padx=5)
algo_dropdown.bind("<<ComboboxSelected>>", on_algo_change)
frame_table_inputs = tk.Frame(main_frame, bg=bg_color); frame_table_inputs.pack(pady=10)
tk.Button(main_frame, text="RUN", command=run_scheduler, font=(secondary_font_family, 11, "bold"), bg="#FFB6C1", fg=button_fg_color, relief="raised", bd=3).pack(pady=10)
tk.Button(main_frame, text="CLEAR ALL", command=clear_inputs, font=(secondary_font_family, 11, "bold"), bg="#FFB6C1", fg=button_fg_color, relief="raised", bd=3).pack(pady=5)
columns = ("Process ID", "Arrival Time", "Burst Time", "Start Time", "Finish Time", "Waiting Time", "Turnaround Time")
table = ttk.Treeview(main_frame, columns=columns, show="headings", height=8)
for col in columns: table.heading(col, text=col); table.column(col, width=100, anchor='center')
table.pack(pady=10, fill="x", expand=True)
label_avg = tk.Label(main_frame, text="AVERAGE WAITING TIME: 0.00 ms         AVERAGE TURNAROUND TIME: 0.00 ms", font=(secondary_font_family, 15, "bold"), bg=bg_color, fg="#4F2B2B"); label_avg.pack(pady=10)
canvas = tk.Canvas(main_frame, height=100, bg="white", highlightbackground="black", highlightthickness=1); canvas.pack(pady=20, fill="x", expand=True)
input_entries = []
on_algo_change()

root.update_idletasks()
event = tk.Event()
event.width = root.winfo_width()
event.height = root.winfo_height()
resize_front_image(event)

root.mainloop()
