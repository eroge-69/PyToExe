import tkinter as tk
from tkinter import ttk, messagebox

def fcfs(processes):
    processes.sort(key=lambda x: x['arrival_time']); time = 0; gantt_chart = []
    for process in processes:
        if time < process['arrival_time']: time = process['arrival_time']
        start = time; finish = time + process['burst_time']; time = finish
        process['start_time'] = start; process['finish_time'] = finish; process['turnaround_time'] = finish - process['arrival_time']; process['waiting_time'] = process['turnaround_time'] - process['burst_time']
        gantt_chart.append((process['pid'], start, finish))
    return processes, gantt_chart

def sjf(processes):
    n = len(processes); completed = 0; time = 0; gantt_chart = []; processes = sorted(processes, key=lambda x: x['arrival_time']); is_completed = [False] * n
    while completed < n:
        ready_queue = [p for i, p in enumerate(processes) if p['arrival_time'] <= time and not is_completed[i]]
        if ready_queue:
            current = min(ready_queue, key=lambda x: x['burst_time']); idx = processes.index(current); start = time; finish = time + current['burst_time']; time = finish
            processes[idx]['start_time'] = start; processes[idx]['finish_time'] = finish; processes[idx]['turnaround_time'] = finish - current['arrival_time']; processes[idx]['waiting_time'] = processes[idx]['turnaround_time'] - current['burst_time']
            is_completed[idx] = True; completed += 1; gantt_chart.append((current['pid'], start, finish))
        else: time += 1
    return processes, gantt_chart

def rr(processes, quantum):
    n = len(processes); queue = []; time = 0; completed = 0; remaining_bt = [p['burst_time'] for p in processes]; is_started = [False] * n; is_completed = [False] * n; gantt_chart = []; processes = sorted(processes, key=lambda x: x['arrival_time']); arrived = [False] * n
    while completed < n:
        for i, p in enumerate(processes):
            if p['arrival_time'] <= time and not arrived[i]: queue.append(i); arrived[i] = True
        if not queue: time += 1; continue
        idx = queue.pop(0); p = processes[idx]
        if not is_started[idx]: p['start_time'] = time; is_started[idx] = True
        exec_time = min(quantum, remaining_bt[idx]); gantt_chart.append((p['pid'], time, time + exec_time)); time += exec_time; remaining_bt[idx] -= exec_time
        for i, proc in enumerate(processes):
            if proc['arrival_time'] <= time and not arrived[i]: queue.append(i); arrived[i] = True
        if remaining_bt[idx] == 0: is_completed[idx] = True; completed += 1; p['finish_time'] = time; p['turnaround_time'] = time - p['arrival_time']; p['waiting_time'] = p['turnaround_time'] - p['burst_time']
        else: queue.append(idx)
    return processes, gantt_chart

def generate_table():
    try: count = int(entry_count.get()); assert 7 <= count <= 10
    except: messagebox.showerror("Error", "7 to 10 only."); return
    for widget in frame_table_inputs.winfo_children(): widget.destroy()
    headers = ["Process ID", "Arrival Time", "Burst Time"]
    for j, header in enumerate(headers): tk.Label(frame_table_inputs, text=header, width=15, borderwidth=1, relief="solid", bg=bg_color, font=default_font).grid(row=0, column=j)
    input_entries.clear()
    for i in range(count):
        row = []; tk.Label(frame_table_inputs, text=f"P{i+1}", width=15, borderwidth=1, relief="solid", bg=bg_color, font=default_font).grid(row=i+1, column=0)
        at_entry = tk.Entry(frame_table_inputs, width=15, borderwidth=1, relief="solid", font=default_font); at_entry.grid(row=i+1, column=1); row.append(at_entry)
        bt_entry = tk.Entry(frame_table_inputs, width=15, borderwidth=1, relief="solid", font=default_font); bt_entry.grid(row=i+1, column=2); row.append(bt_entry)
        input_entries.append(row)

def run_scheduler():
    algo = algo_var.get(); processes = []
    for i, row in enumerate(input_entries):
        try: at = int(row[0].get()); bt = int(row[1].get()); processes.append({'pid': f"P{i+1}", 'arrival_time': at, 'burst_time': bt, 'priority': 0})
        except ValueError: messagebox.showerror("Input Error", f"Invalid input in row {i+1}"); return
    if algo == "First Come First Serve": result, gantt = fcfs(processes)
    elif algo == "Shortest Job First": result, gantt = sjf(processes)
    elif algo == "Round Robin":
        try: quantum = int(entry_quantum.get()); assert quantum > 0
        except: messagebox.showerror("Error", "Please enter a valid positive integer."); return
        result, gantt = rr(processes, quantum)
    else: messagebox.showerror("Error", f"{algo} not yet implemented."); return
    update_table(result); draw_gantt(gantt)

def clear_inputs():
    entry_count.delete(0, tk.END); entry_quantum.delete(0, tk.END)
    for row in input_entries:
        for entry in row: entry.delete(0, tk.END)
    for i in table.get_children(): table.delete(i)
    canvas.delete("all")
    label_avg.config(text="AVERAGE WAITING TIME: 0.00                                                           AVERAGE TURNAROUND TIME: 0.00")

def update_table(results):
    for i in table.get_children(): table.delete(i)
    total_wt = 0; total_tat = 0
    for p in results: total_wt += p['waiting_time']; total_tat += p['turnaround_time']; table.insert("", tk.END, values=(p['pid'], p['arrival_time'], p['burst_time'], p['start_time'], p['finish_time'], p['waiting_time'], p['turnaround_time']))
    n = len(results); avg_wt = total_wt / n if n > 0 else 0; avg_tat = total_tat / n if n > 0 else 0
    label_avg.config(text=f"AVERAGE WAITING TIME: {avg_wt:.2f}                                                           AVERAGE TURNAROUND TIME: {avg_tat:.2f}")

def draw_gantt(gantt):
    canvas.delete("all"); canvas_width = canvas.winfo_width(); total_time = gantt[-1][2]; scale = 30; chart_width = total_time * scale; x_start = max((canvas_width - chart_width) // 2, 10); x = x_start
    for pid, start, end in gantt:
        canvas.create_rectangle(x, 20, x + (end - start) * scale, 70, fill="#E6B3FF"); canvas.create_text(x + (end - start) * scale // 2, 45, text=pid, font=default_font); canvas.create_text(x, 75, text=str(start), anchor=tk.NW, font=default_font); x += (end - start) * scale
    canvas.create_text(x, 75, text=str(gantt[-1][2]), anchor=tk.NW, font=default_font)

def on_algo_change(event=None):
    if algo_var.get() == "Round Robin": quantum_frame.pack(after=frame_top, pady=5)
    else: quantum_frame.pack_forget()
    try:
        if int(entry_count.get()) > 0: generate_table()
    except ValueError: pass

bg_color = "#F8E8FF"; default_font = ("Georgia", 13)
root = tk.Tk(); root.title("CPU Process Scheduling Calculator"); root.geometry("1920x1080"); root.configure(bg=bg_color)
main_canvas = tk.Canvas(root, bg=bg_color, highlightthickness=0); main_canvas.create_window((960, 0), anchor="n")
tk.Label(text="CPU PROCESS SCHEDULING CALCULATOR", font=("Georgia", 20, "bold"), bg=bg_color).pack(pady=20)
frame_top = tk.Frame(bg=bg_color); frame_top.pack(pady=10)
tk.Label(frame_top, text="Number of Processes:", bg=bg_color, font=default_font).pack(side=tk.LEFT)
entry_count = tk.Entry(frame_top, width=5, font=default_font); entry_count.pack(side=tk.LEFT, padx=5)
tk.Button(frame_top, text="Generate Table", command=generate_table, font=default_font).pack(side=tk.LEFT)
quantum_frame = tk.Frame(bg=bg_color)
label_quantum = tk.Label(quantum_frame, text="Time Quantum: ", bg=bg_color, font=default_font)
entry_quantum = tk.Entry(quantum_frame, width=5, font=default_font); label_quantum.pack(side=tk.LEFT); entry_quantum.pack(side=tk.LEFT)
algo_var = tk.StringVar(value="First Come First Serve")
frame_algo = tk.Frame(bg=bg_color); frame_algo.pack(pady=5)
tk.Label(frame_algo, text="Select Algorithm:", bg=bg_color, font=default_font).pack(side=tk.LEFT)
algo_dropdown = ttk.Combobox(frame_algo, textvariable=algo_var, values=["First Come First Serve", "Shortest Job First", "Round Robin"], state="readonly", font=default_font, width=30); algo_dropdown.pack(side=tk.LEFT, padx=5); algo_dropdown.bind("<<ComboboxSelected>>", on_algo_change)
frame_table_inputs = tk.Frame(bg=bg_color); frame_table_inputs.pack(pady=10)
tk.Button(text="Run Scheduler", command=run_scheduler, font=default_font).pack(pady=10)
tk.Button(text="Clear All", command=clear_inputs, font=default_font).pack(pady=5)
columns = ("Process ID", "Arrival Time", "Burst Time", "Start Time", "Finish Time", "Waiting Time", "Turnaround Time")
table = ttk.Treeview(columns=columns, show="headings", height=8)
for col in columns: table.heading(col, text=col)
table.pack(pady=10)
label_avg = tk.Label(text="AVERAGE WAITING TIME: 0.00                                                           AVERAGE TURNAROUND TIME: 0.00", font=("Times New Roman", 15, "bold"), bg=bg_color); label_avg.pack(pady=10)
canvas = tk.Canvas(height=100, bg="white"); canvas.pack(pady=20, fill="x")
input_entries = []; on_algo_change(); root.mainloop()