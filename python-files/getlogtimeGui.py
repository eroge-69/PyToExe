import requests
import datetime
import csv
import tkinter as tk
from tkinter import ttk, messagebox
from collections import defaultdict

BASE_URL = "https://api.clickup.com/api/v2"
CLICKUP_BASE_TASK_URL = "https://app.clickup.com/t"

def export_csv(api_token, team_id, user_id, start_date_str, end_date_str):
    headers = {"Authorization": api_token}

    start_date = int(datetime.datetime.strptime(start_date_str, "%Y-%m-%d").timestamp() * 1000)
    end_date = int((datetime.datetime.strptime(end_date_str, "%Y-%m-%d") + datetime.timedelta(days=1)).timestamp() * 1000)

    # Call time_entries API
    url = f"{BASE_URL}/team/{team_id}/time_entries"
    params = {"start_date": start_date, "end_date": end_date, "assignee": user_id}
    res = requests.get(url, headers=headers, params=params)
    entries = res.json().get("data", [])

    # Gộp logtime
    task_day_hours = defaultdict(float)
    task_name_map = {}
    task_names = set()

    for entry in entries:
        task = entry.get("task")
        if not task:
            continue
        task_id = task.get("id")
        task_name = task.get("name", "No title")
        start = datetime.datetime.fromtimestamp(int(entry["start"]) / 1000)
        date_str = start.date().isoformat()
        duration_ms = int(entry.get("duration", 0))
        hours_logged = duration_ms / 1000 / 60 / 60

        task_day_hours[(task_id, date_str)] += hours_logged
        task_name_map[task_id] = task_name
        task_names.add(task_id)

    # Lấy Estimated Time
    task_estimates = {}
    for task_id in task_names:
        task_url_api = f"{BASE_URL}/task/{task_id}"
        res_task = requests.get(task_url_api, headers=headers)
        if res_task.status_code == 200:
            est_ms = res_task.json().get("time_estimate") or 0
            task_estimates[task_id] = round(est_ms / 1000 / 60 / 60, 2)
        else:
            task_estimates[task_id] = 0

    # Chuẩn bị CSV
    rows = []
    total_hours = 0
    for (task_id, date_str), hours in sorted(task_day_hours.items()):
        task_url = f"{CLICKUP_BASE_TASK_URL}/{task_id}"
        est_hours = task_estimates.get(task_id, 0)
        rows.append([task_id, task_url, task_name_map[task_id], date_str, round(hours,2), est_hours])
        total_hours += hours
    rows.append(["", "", "Total", "", round(total_hours,2), ""])

    csv_file = f"clickup_logtime_{user_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Task ID","Task URL","Task Name","Date","Time Logged (h)","Estimated Time (h)"])
        writer.writerows(rows)

    return csv_file, total_hours

def run_export():
    api_token = entry_token.get().strip()
    team_id = combo_team.get().split(" ")[0]  # team_id trước dấu space
    user_id = entry_user_id.get().strip()
    start_date = entry_start.get().strip()
    end_date = entry_end.get().strip()
    if not api_token or not team_id or not user_id or not start_date or not end_date:
        messagebox.showerror("Error", "Vui lòng điền đầy đủ thông tin")
        return
    try:
        csv_file, total_hours = export_csv(api_token, team_id, user_id, start_date, end_date)
        messagebox.showinfo("Success", f"✅ Export xong: {csv_file}\nTổng giờ: {round(total_hours,2)}h")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# ===== GUI =====
root = tk.Tk()
root.title("ClickUp Logtime Exporter")

tk.Label(root, text="API_TOKEN").grid(row=0, column=0, sticky="w")
entry_token = tk.Entry(root, width=50)
entry_token.grid(row=0, column=1)

tk.Label(root, text="User ID").grid(row=1, column=0, sticky="w")
entry_user_id = tk.Entry(root, width=20)
entry_user_id.grid(row=1, column=1, sticky="w")

tk.Label(root, text="Team (ID Name)").grid(row=2, column=0, sticky="w")
combo_team = ttk.Combobox(root, width=40, values=[])  # bạn có thể điền tĩnh hoặc call API để lấy team list
combo_team.grid(row=2, column=1, sticky="w")

tk.Label(root, text="Start Date (YYYY-MM-DD)").grid(row=3, column=0, sticky="w")
entry_start = tk.Entry(root)
entry_start.grid(row=3, column=1, sticky="w")

tk.Label(root, text="End Date (YYYY-MM-DD)").grid(row=4, column=0, sticky="w")
entry_end = tk.Entry(root)
entry_end.grid(row=4, column=1, sticky="w")

btn_export = tk.Button(root, text="Export CSV", command=run_export)
btn_export.grid(row=5, column=0, columnspan=2, pady=10)

root.mainloop()

