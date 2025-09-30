import requests
import datetime
import csv
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from collections import defaultdict
import threading

BASE_URL = "https://api.clickup.com/api/v2"
CLICKUP_BASE_TASK_URL = "https://app.clickup.com/t"

def get_user_id(api_token, status_var):
    status_var.set("🔹 Lấy User ID...")
    headers = {"Authorization": api_token}
    url = f"{BASE_URL}/user"
    res = requests.get(url, headers=headers)
    data = res.json()
    user_id = data.get("user", {}).get("id")
    username = data.get("user", {}).get("username")
    if not user_id:
        raise Exception("Không lấy được User ID")
    status_var.set(f"✅ User ID: {user_id} ({username})")
    return user_id

def load_teams(api_token, combo_team, btn_load_team, btn_export, status_var):
    def _load():
        try:
            status_var.set("🔹 Lấy danh sách Teams...")
            headers = {"Authorization": api_token}
            url = f"{BASE_URL}/team"
            res = requests.get(url, headers=headers)
            data = res.json()
            teams = data.get("teams", [])
            if not teams:
                raise Exception("Không tìm thấy team nào")
            combo_team['values'] = [f"{team['id']} {team['name']}" for team in teams]
            combo_team.current(0)
            status_var.set(f"✅ Đã tải {len(teams)} team")
            # Ẩn nút Load Team, hiện nút Export
            btn_load_team.grid_remove()
            btn_export.grid()
        except Exception as e:
            status_var.set(f"❌ Lỗi: {str(e)}")
            messagebox.showerror("Error", str(e))

    threading.Thread(target=_load).start()

def export_csv(api_token, team_id, user_id, start_date_str, end_date_str, status_var):
    headers = {"Authorization": api_token}
    status_var.set("🔹 Lấy logtime từ ClickUp...")

    start_date = int(datetime.datetime.strptime(start_date_str, "%Y-%m-%d").timestamp() * 1000)
    end_date = int((datetime.datetime.strptime(end_date_str, "%Y-%m-%d") + datetime.timedelta(days=1)).timestamp() * 1000)

    url = f"{BASE_URL}/team/{team_id}/time_entries"
    params = {"start_date": start_date, "end_date": end_date, "assignee": user_id}
    res = requests.get(url, headers=headers, params=params)
    entries = res.json().get("data", [])
    status_var.set(f"🔹 Tìm thấy {len(entries)} logtime entries")

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

    task_estimates = {}
    for task_id in task_names:
        status_var.set(f"🔹 Lấy Estimated Time cho task {task_name_map[task_id]}...")
        task_url_api = f"{BASE_URL}/task/{task_id}"
        res_task = requests.get(task_url_api, headers=headers)
        if res_task.status_code == 200:
            est_ms = res_task.json().get("time_estimate") or 0
            task_estimates[task_id] = round(est_ms / 1000 / 60 / 60, 2)
        else:
            task_estimates[task_id] = 0

    rows = []
    total_hours = 0
    for (task_id, date_str), hours in sorted(task_day_hours.items()):
        task_url = f"{CLICKUP_BASE_TASK_URL}/{task_id}"
        est_hours = task_estimates.get(task_id, 0)
        rows.append([task_id, task_url, task_name_map[task_id], date_str, round(hours, 2), est_hours])
        total_hours += hours
    rows.append(["", "", "Total", "", round(total_hours, 2), ""])

    csv_file = f"clickup_logtime_{user_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Task ID","Task URL","Task Name","Date","Time Logged (h)","Estimated Time (h)"])
        writer.writerows(rows)

    status_var.set(f"✅ Export xong: {csv_file}, Tổng giờ: {round(total_hours,2)}h")
    messagebox.showinfo("Success", f"✅ Export xong: {csv_file}\nTổng giờ: {round(total_hours,2)}h")

def run_export_thread(api_token, combo_team, start_entry, end_entry, status_var):
    try:
        user_id = get_user_id(api_token, status_var)
        team_str = combo_team.get()
        if not team_str:
            messagebox.showerror("Error", "Vui lòng chọn team")
            return
        team_id = team_str.split(" ")[0]
        start_date_str = start_entry.get_date().strftime("%Y-%m-%d")
        end_date_str = end_entry.get_date().strftime("%Y-%m-%d")
        export_csv(api_token, team_id, user_id, start_date_str, end_date_str, status_var)
    except Exception as e:
        status_var.set(f"❌ Lỗi: {str(e)}")
        messagebox.showerror("Error", str(e))

# ===== GUI =====
root = tk.Tk()
root.title("ClickUp Logtime Exporter")

status_var = tk.StringVar()
status_var.set("Nhập API_TOKEN để bắt đầu")

tk.Label(root, text="API_TOKEN").grid(row=0, column=0, sticky="w")
entry_token = tk.Entry(root, width=50, show="*")
entry_token.grid(row=0, column=1, sticky="w")

tk.Label(root, text="Team").grid(row=1, column=0, sticky="w")
combo_team = ttk.Combobox(root, width=40, values=[])
combo_team.grid(row=1, column=1, sticky="w")

tk.Label(root, text="Start Date").grid(row=2, column=0, sticky="w")
start_entry = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
start_entry.grid(row=2, column=1, sticky="w")

tk.Label(root, text="End Date").grid(row=3, column=0, sticky="w")
end_entry = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
end_entry.grid(row=3, column=1, sticky="w")

btn_load_team = tk.Button(root, text="Load Team", width=20, command=lambda: load_teams(entry_token.get().strip(), combo_team, btn_load_team, btn_export, status_var))
btn_load_team.grid(row=4, column=0, columnspan=2, pady=5)

btn_export = tk.Button(root, text="Export CSV", width=20, command=lambda: threading.Thread(target=run_export_thread, args=(entry_token.get().strip(), combo_team, start_entry, end_entry, status_var)).start())
btn_export.grid(row=5, column=0, columnspan=2, pady=5)
btn_export.grid_remove()  # Ẩn ban đầu

status_label = tk.Label(root, textvariable=status_var, fg="blue")
status_label.grid(row=6, column=0, columnspan=2, sticky="w")

root.mainloop()

