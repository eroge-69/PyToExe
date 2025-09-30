import requests
import datetime
import csv
import sys
from collections import defaultdict

# ===== Config =====
API_TOKEN = input("Nhập API_TOKEN ClickUp của bạn: ").strip()

headers = {"Authorization": API_TOKEN}
BASE_URL = "https://api.clickup.com/api/v2"
CLICKUP_BASE_TASK_URL = "https://app.clickup.com/t"

def choose_team_id():
    url = f"{BASE_URL}/team"
    res = requests.get(url, headers=headers)
    data = res.json()
    teams = data.get("teams", [])
    if not teams:
        raise Exception("Không tìm thấy team nào trong workspace của bạn")

    print("Danh sách Teams:")
    for i, team in enumerate(teams, start=1):
        print(f"{i}. {team['name']} (ID: {team['id']})")

    while True:
        choice = input(f"Chọn team (1-{len(teams)}): ")
        if choice.isdigit() and 1 <= int(choice) <= len(teams):
            selected_team = teams[int(choice) - 1]
            print(f"Đã chọn: {selected_team['name']}")
            return selected_team["id"]
        else:
            print("Lựa chọn không hợp lệ, thử lại.")

def get_user_id():
    url = f"{BASE_URL}/user"
    res = requests.get(url, headers=headers)
    data = res.json()
    user_id = data.get("user", {}).get("id")
    username = data.get("user", {}).get("username")
    if not user_id:
        raise Exception("Không lấy được User ID")
    print(f"User ID: {user_id} ({username})")
    return user_id
    
USER_ID = get_user_id()
TEAM_ID = choose_team_id()

# ===== Nhận ngày từ command line =====
if len(sys.argv) != 3:
    print("Cách dùng: python getLogtime.py YYYY-MM-DD YYYY-MM-DD")
    sys.exit(1)

start_date_str = sys.argv[1]
end_date_str = sys.argv[2]

# Convert sang epoch ms
start_date = int(datetime.datetime.strptime(start_date_str, "%Y-%m-%d").timestamp() * 1000)
end_date = int((datetime.datetime.strptime(end_date_str, "%Y-%m-%d") + datetime.timedelta(days=1)).timestamp() * 1000)

print(f"Lấy logtime từ {start_date_str} -> {end_date_str}")

# ===== Call API time_entries =====
url = f"{BASE_URL}/team/{TEAM_ID}/time_entries"
params = {
    "start_date": start_date,
    "end_date": end_date,
    "assignee": USER_ID
}

res = requests.get(url, headers=headers, params=params)
data = res.json()
entries = data.get("data", [])
print(f"Tìm thấy {len(entries)} logtime entries")

# ===== Gộp logtime theo (task_id, date) =====
task_day_hours = defaultdict(float)  # (task_id, date) -> tổng giờ
task_names = set()  # lưu task_id
task_name_map = {}  # task_id -> task_name

for entry in entries:
    task = entry.get("task")
    if not task:
        continue
    task_id = task.get("id")
    task_name = task.get("name", "No title")
    start = datetime.datetime.fromtimestamp(int(entry["start"]) / 1000)
    date_str = start.date().isoformat()
    
    duration_ms = int(entry["duration"]) if entry.get("duration") else 0
    hours_logged = duration_ms / 1000 / 60 / 60

    task_day_hours[(task_id, date_str)] += hours_logged
    task_name_map[task_id] = task_name
    task_names.add(task_id)

# ===== Lấy Estimated Time cho mỗi task =====
task_estimates = {}
for task_id in task_names:
    task_url_api = f"{BASE_URL}/task/{task_id}"
    res_task = requests.get(task_url_api, headers=headers)
    if res_task.status_code == 200:
        task_data = res_task.json()
        est_ms = task_data.get("time_estimate") or 0
        task_estimates[task_id] = round(est_ms / 1000 / 60 / 60, 2)  # giờ
    else:
        task_estimates[task_id] = 0

# ===== Chuẩn bị CSV =====
rows = []
total_hours = 0

for (task_id, date_str), hours in sorted(task_day_hours.items()):
    task_url = f"{CLICKUP_BASE_TASK_URL}/{task_id}"
    est_hours = task_estimates.get(task_id, 0)
    rows.append([task_id, task_url, task_name_map[task_id], date_str, round(hours, 2), est_hours])
    total_hours += hours

# Thêm dòng tổng cộng
rows.append(["", "", "Total", "", round(total_hours, 2), ""])

# ===== Export CSV =====
csv_file = f"clickup_logtime_{USER_ID}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Task ID", "Task URL", "Task Name", "Date", "Time Logged (h)", "Estimated Time (h)"])
    writer.writerows(rows)

print(f"✅ Đã export ra {csv_file}, Tổng giờ log: {round(total_hours, 2)}h")


