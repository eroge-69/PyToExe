from flask import Flask, render_template_string, request, jsonify, send_file
import pandas as pd
from datetime import datetime, date
import os
import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

app = Flask(__name__)

# File paths
USERS_FILE = "users.xlsx"
ATTENDANCE_FILE = "attendance.xlsx"

def initialize_files():
    """Initialize Excel files if they don\\'t exist"""
    # Initialize users file
    if not os.path.exists(USERS_FILE):
        df_users = pd.DataFrame(columns=["Barcode", "Name", "Department", "User_Type"])
        df_users.to_excel(USERS_FILE, index=False)
    
    # Initialize attendance file
    if not os.path.exists(ATTENDANCE_FILE):
        df_attendance = pd.DataFrame(columns=["Barcode", "Name", "Department", "User_Type", "Entry_Time", "Exit_Time", "Date"])
        df_attendance.to_excel(ATTENDANCE_FILE, index=False)

def load_users():
    """Load users from Excel file"""
    try:
        return pd.read_excel(USERS_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Barcode", "Name", "Department", "User_Type"])

def save_users(df):
    """Save users to Excel file"""
    df.to_excel(USERS_FILE, index=False)

def load_attendance():
    """Load attendance from Excel file"""
    try:
        df = pd.read_excel(ATTENDANCE_FILE)
        # Ensure datetime columns are correctly parsed, handling 'Still Inside' string
        for col in ["Entry_Time", "Date"]:
            if col in df.columns and not df.empty:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        if "Exit_Time" in df.columns and not df.empty:
            df["Exit_Time"] = df["Exit_Time"].apply(lambda x: None if x == "Still Inside" else pd.to_datetime(x, errors="coerce"))
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Barcode", "Name", "Department", "User_Type", "Entry_Time", "Exit_Time", "Date"])

def save_attendance(df):
    """Save attendance to Excel file"""
    # Convert NaT/None in Exit_Time to 'Still Inside' string before saving
    df_to_save = df.copy()
    if "Exit_Time" in df_to_save.columns:
        df_to_save["Exit_Time"] = df_to_save["Exit_Time"].apply(lambda x: "Still Inside" if pd.isna(x) else x)
    df_to_save.to_excel(ATTENDANCE_FILE, index=False)
@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/scan", methods=["POST"])
def scan_barcode():
    data = request.get_json()
    barcode = data.get("barcode")

    if not barcode:
        return jsonify({"message": "Invalid barcode"}), 400

    df_users = load_users()
    user = df_users[df_users["Barcode"] == barcode]

    if user.empty:
        return jsonify({"message": "User not found!"}), 404

    user_data = user.iloc[0]
    now = datetime.now()
    today = now.date()
    
    df_attendance = load_attendance()
    
    # Filter for records for the current user and today's date
    user_today_attendance = df_attendance[
        (df_attendance['Barcode'] == barcode) &
        (df_attendance['Date'].dt.date == today)
    ]

    # Check for an active entry (Exit_Time is 'Still Inside' or None/NaT after loading)
    active_entry = user_today_attendance[
        user_today_attendance["Exit_Time"] == "Still Inside"
    ]

    if not active_entry.empty:
        # User is currently 'Still Inside', record exit time
        idx = active_entry.index[0]
        df_attendance.loc[idx, 'Exit_Time'] = now
        message = f"Exit recorded for {user_data['Name']}"
        action = "Exit"
    else:
        # Record new entry (user was not 'Still Inside')
        new_entry = pd.DataFrame([{
            "Barcode": barcode,
            "Name": user_data["Name"],
            "Department": user_data["Department"] if pd.notna(user_data["Department"]) else "-",
            "User_Type": user_data["User_Type"],
            "Entry_Time": now,
            "Exit_Time": "Still Inside", # Store as string
            "Date": today
        }])
        df_attendance = pd.concat([df_attendance, new_entry], ignore_index=True)
        message = f"Entry recorded for {user_data['Name']}"
        action = "Entry"

    save_attendance(df_attendance)

    return jsonify({
        "message": f"{action} recorded for {user_data['Name']}",
        "name": user_data["Name"],
        "barcode": barcode,
        "action": action,
        "time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "user_type": user_data["User_Type"]
    })

@app.route("/get_attendance", methods=["GET"])
def get_attendance():
    limit = request.args.get("limit", "all")
    user_type = request.args.get("user_type", "all")
    department = request.args.get("department", "all")
    year = request.args.get("year", "all")
    day = request.args.get("day", "all")
    month = request.args.get("month", "all")
    
    df_attendance = load_attendance()
    
    if df_attendance.empty:
        return jsonify([])
    
    # Filter by user type
    if user_type != "all":
        df_attendance = df_attendance[df_attendance["User_Type"] == user_type]
    
    # Filter by department
    if department != "all":
        df_attendance = df_attendance[df_attendance["Department"] == department]
    
    # Filter by year
    if year != "all":
        df_attendance = df_attendance[df_attendance["Date"].dt.year == int(year)]
    
    # Filter by month
    if month != "all":
        df_attendance = df_attendance[df_attendance["Date"].dt.month == int(month)]
    
    # Filter by day
    if day != "all":
        df_attendance = df_attendance[df_attendance["Date"].dt.day == int(day)]
    
    # Sort by most recent first
    if not df_attendance.empty:
        df_attendance = df_attendance.sort_values("Entry_Time", ascending=False)
        
        # Convert datetime objects to string for JSON serialization
        df_attendance = df_attendance.copy()
        df_attendance["Entry_Time"] = df_attendance["Entry_Time"].apply(
            lambda x: x.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(x) else ""
        )
        # Display 'Still Inside' for null Exit_Time values
        df_attendance["Exit_Time"] = df_attendance["Exit_Time"].apply(
            lambda x: x.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(x) else "Still Inside"
        )
        df_attendance["Date"] = df_attendance["Date"].apply(
            lambda x: x.strftime("%Y-%m-%d") if pd.notna(x) else ""
        )
        df_attendance["Department"] = df_attendance["Department"].fillna("")

        # Apply limit
        if limit != "all":
            try:
                limit_num = int(limit)
                df_attendance = df_attendance.head(limit_num)
            except ValueError:
                pass
    
    return jsonify(df_attendance.to_dict(orient="records"))

@app.route("/get_users", methods=["GET"])
def get_users():
    user_type = request.args.get("user_type", "all")
    df_users = load_users()
    
    if user_type != "all":
        df_users = df_users[df_users["User_Type"] == user_type]
    
    return jsonify(df_users.to_dict(orient="records"))

@app.route("/get_departments", methods=["GET"])
def get_departments():
    df_users = load_users()
    departments = df_users["Department"].dropna().unique().tolist()
    return jsonify(departments)

@app.route("/add_user", methods=["POST"])
def add_user():
    data = request.get_json()
    df_users = load_users()
    
    # Check if barcode already exists
    if not df_users[df_users["Barcode"] == data["barcode"]].empty:
        return jsonify({"message": "Barcode already exists!"}), 400
    
    new_user = pd.DataFrame([{
        "Barcode": data["barcode"],
        "Name": data["name"],
        "Department": data.get("department", ""),
        "User_Type": data["user_type"]
    }])
    
    df_users = pd.concat([df_users, new_user], ignore_index=True)
    save_users(df_users)
    
    return jsonify({"message": "User added successfully!"})

@app.route("/update_user", methods=["POST"])
def update_user():
    data = request.get_json()
    df_users = load_users()
    
    user_idx = df_users[df_users["Barcode"] == data["barcode"]].index
    if user_idx.empty:
        return jsonify({"message": "User not found!"}), 404
    
    idx = user_idx[0]
    df_users.loc[idx, "Name"] = data["name"]
    df_users.loc[idx, "Department"] = data.get("department", "")
    df_users.loc[idx, "User_Type"] = data["user_type"]
    
    save_users(df_users)
    return jsonify({"message": "User updated successfully!"})

@app.route("/delete_user", methods=["POST"])
def delete_user():
    data = request.get_json()
    df_users = load_users()
    
    df_users = df_users[df_users["Barcode"] != data["barcode"]]
    save_users(df_users)
    
    return jsonify({"message": "User deleted successfully!"})

@app.route("/add_attendance", methods=["POST"])
def add_attendance():
    data = request.get_json()
    df_attendance = load_attendance()
    df_users = load_users()
    
    # Get user info
    user = df_users[df_users["Barcode"] == data["barcode"]]
    if user.empty:
        return jsonify({"message": "User not found!"}), 404
    
    user_data = user.iloc[0]
    
    new_record = pd.DataFrame([{
        "Barcode": data["barcode"],
        "Name": user_data["Name"],
        "Department": user_data["Department"] if pd.notna(user_data["Department"]) else "",
        "User_Type": user_data["User_Type"],
        "Entry_Time": datetime.strptime(data["entry_time"], "%Y-%m-%dT%H:%M"),
        "Exit_Time": datetime.strptime(data["exit_time"], "%Y-%m-%dT%H:%M") if data.get("exit_time") else "Still Inside",
        "Date": datetime.strptime(data["date"], "%Y-%m-%d").date()
    }])
    
    df_attendance = pd.concat([df_attendance, new_record], ignore_index=True)
    save_attendance(df_attendance)
    
    return jsonify({"message": "Attendance record added successfully!"})

@app.route("/export_attendance", methods=["POST"])
def export_attendance():
    data = request.get_json()
    format_type = data.get("format", "excel")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    
    df_attendance = load_attendance()
    
    # Filter by date range if provided
    if start_date and end_date and not df_attendance.empty:
        df_attendance["Date"] = pd.to_datetime(df_attendance["Date"])
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        df_attendance = df_attendance[
            (df_attendance["Date"] >= start_date) & 
            (df_attendance["Date"] <= end_date)
        ]
    
    # Create file
    output = io.BytesIO()
    
    if format_type == "excel":
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_attendance.to_excel(writer, index=False, sheet_name='Attendance')
        
        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name=f'attendance_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    elif format_type == "csv":
        df_attendance.to_csv(output, index=False)
        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name=f'attendance_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mimetype='text/csv'
        )

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>📚 Library Attendance System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: \'Segoe UI\', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #81c784 0%, #4caf50 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            background: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            max-width: 1200px;
            margin: auto;
            position: relative;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .header h1 {
            color: #2e7d32;
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .settings-container {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 10;
        }

        .scan-section {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: #f1f8e9;
            border-radius: 15px;
        }

        #barcodeInput {
            width: 100%;
            max-width: 400px;
            padding: 15px;
            font-size: 18px;
            border: 2px solid #4caf50;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
        }

        .settings-btn {
            background: #4caf50;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
            position: relative;
        }

        .settings-btn:hover {
            background: #388e3c;
            transform: translateY(-2px);
        }

        .controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 15px;
        }

        .filter-group {
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }

        select, input {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }

        .table-container {
            overflow-x: auto;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }

        th {
            background: #4caf50;
            color: white;
            padding: 15px 10px;
            text-align: left;
            font-weight: 600;
        }

        td {
            padding: 12px 10px;
            border-bottom: 1px solid #eee;
        }

        tr:hover {
            background: #f1f8e9;
        }

        /* Popup Styles */
        .popup {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(135deg, #4caf50, #388e3c);
            color: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            z-index: 1000;
            text-align: center;
            min-width: 350px;
            animation: popupSlide 0.3s ease-out;
        }

        @keyframes popupSlide {
            from {
                opacity: 0;
                transform: translate(-50%, -60%);
            }
            to {
                opacity: 1;
                transform: translate(-50%, -50%);
            }
        }

        .popup h3 {
            font-size: 24px;
            margin-bottom: 15px;
        }

        .popup-info {
            font-size: 16px;
            margin: 10px 0;
        }

        .popup-barcode {
            font-family: \'Courier New\', monospace;
            font-size: 18px;
            font-weight: bold;
            background: rgba(255, 255, 255, 0.2);
            padding: 8px;
            border-radius: 5px;
            margin: 10px 0;
        }

        /* Modal Styles */
        .modal {
            display: none;
            position: fixed;
            z-index: 1001;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
        }

        .modal-content {
            background-color: white;
            margin: 5% auto;
            padding: 30px;
            border-radius: 15px;
            width: 90%;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
        }

        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }

        .close:hover {
            color: #000;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #2e7d32;
        }

        .form-group input, .form-group select {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
        }

        .btn {
            background: #4caf50;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
        }

        .btn:hover {
            background: #388e3c;
        }

        .btn-danger {
            background: #f44336;
        }

        .btn-danger:hover {
            background: #d32f2f;
        }

        .status-message {
            padding: 15px;
            margin: 15px 0;
            border-radius: 8px;
            text-align: center;
            font-weight: 600;
        }

        .status-success {
            background: #e8f5e8;
            color: #2e7d32;
            border: 1px solid #c8e6c9;
        }

        .status-error {
            background: #ffebee;
            color: #c62828;
            border: 1px solid #ffcdd2;
        }

        .settings-menu {
            display: none;
            position: absolute;
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            z-index: 100;
            min-width: 200px;
            top: 100%;
            left: 0;
        }

        .settings-menu-item {
            padding: 12px 16px;
            cursor: pointer;
            border-bottom: 1px solid #eee;
            transition: background 0.2s;
        }

        .settings-menu-item:hover {
            background: #f1f8e9;
        }

        .settings-menu-item:last-child {
            border-bottom: none;
        }

        @media (max-width: 768px) {
            .container {
                padding: 20px;
            }
            
            .settings-container {
                position: static;
                text-align: center;
                margin-bottom: 20px;
            }
            
            .controls {
                flex-direction: column;
                align-items: stretch;
            }
            
            .filter-group {
                justify-content: center;
            }
            
            .settings-btn {
                width: auto;
            }
        }
    </style>
</head>
<body>

    <div class=\"container\">
    <div style="width: 100%; overflow: hidden;">
        <img src="https://coes.dypgroup.edu.in/wp-content/uploads/2017/06/STRIP-1-1-scaled.jpg"
             style="width: 100%; height: 150px; display: block;" alt="Banner">
    </div>
    </div>
    <div class=\"container\">
            <div class=\"header\">
            <h1>📚 Library Attendance System</h1>
            <p>Scan your ID card to record entry/exit</p>
        </div>
        
        <div class=\"scan-section\">
            <input type=\"text\" id=\"barcodeInput\" placeholder=\"Scan or enter barcode here...\" autofocus>
            <div id=\"statusMessage\" class=\"status-message\" style=\"display: none;\"></div>
        </div>

        <div class=\"settings-container\">
            <div style=\"position: relative;\">
                <button class=\"settings-btn\" onclick=\"toggleSettingsMenu()\">⚙️ Settings</button>
                <div id=\"settingsMenu\" class=\"settings-menu\">
                    <div class=\"settings-menu-item\" onclick=\"openUserManagement()\">👥 User Management</div>
                    <div class=\"settings-menu-item\" onclick=\"openManualEntry()\">✏️ Manual Entry</div>
                    <div class=\"settings-menu-item\" onclick=\"openExportRecords()\">📊 Export Records</div>
                    <div class=\"settings-menu-item\" onclick=\"refreshAttendance()\">🔄 Refresh</div>
                </div>
            </div>
        </div>

        <div class=\"controls\">
            <div class=\"filter-group\">
                <label>Filter:</label>
                <select id=\"userTypeFilter\" onchange=\"filterAttendance()\">
                    <option value=\"all\">All User Types</option>
                    <option value=\"student\">Students</option>
                    <option value=\"faculty\">Faculty</option>
                    <option value=\"non_teaching_staff\">Non-Teaching Staff</option>
                    <option value=\"admin\">Admin</option>
                </select>
                
                <select id=\"departmentFilter\" onchange=\"filterAttendance()\">
                    <option value=\"all\">All Departments</option>
                </select>
                
                <select id=\"yearFilter\" onchange=\"filterAttendance()\">
                    <option value=\"all\">All Years</option>
                </select>
                
                <select id=\"monthFilter\" onchange=\"filterAttendance()\">
                    <option value=\"all\">All Months</option>
                    <option value=\"1\">January</option>
                    <option value=\"2\">February</option>
                    <option value=\"3\">March</option>
                    <option value=\"4\">April</option>
                    <option value=\"5\">May</option>
                    <option value=\"6\">June</option>
                    <option value=\"7\">July</option>
                    <option value=\"8\">August</option>
                    <option value=\"9\">September</option>
                    <option value=\"10\">October</option>
                    <option value=\"11\">November</option>
                    <option value=\"12\">December</option>
                </select>
                
                <select id=\"dayFilter\" onchange=\"filterAttendance()\">
                    <option value=\"all\">All Days</option>
                </select>
            </div>
            
            <div class=\"filter-group\">
                <label>Display Limit:</label>
                <select id=\"displayLimit\" onchange=\"filterAttendance()\">
                    <option value=\"20\">20</option>
                    <option value=\"50\">50</option>
                    <option value=\"100\">100</option>
                    <option value=\"all\">All</option>
                </select>
            </div>
        </div>

        <div class=\"table-container\">
            <table id=\"attendanceTable\">
                <thead>
                    <tr>
                        <th>Barcode</th>
                        <th>Name</th>
                        <th>Department</th>
                        <th>Type</th>
                        <th>Entry Time</th>
                        <th>Exit Time</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
    </div>

    <!-- User Management Modal -->
    <div id=\"userModal\" class=\"modal\">
        <div class=\"modal-content\">
            <span class=\"close\" onclick=\"closeModal(\'userModal\')\">&times;</span>
            <h2>👥 User Management</h2>
            
            <div class=\"controls\">
                <div class=\"filter-group\">
                    <label>Filter Users:</label>
                    <select id=\"userFilterType\" onchange=\"loadUsers()\">
                        <option value=\"all\">All Users</option>
                        <option value=\"student\">Students</option>
                        <option value=\"faculty\">Faculty</option>
                        <option value=\"non_teaching_staff\">Non-Teaching Staff</option>
                        <option value=\"admin\">Admin</option>
                    </select>
                </div>
                <button class=\"btn\" onclick=\"openAddUser()\">➕ Add User</button>
            </div>

            <div class=\"table-container\" style=\"max-height: 400px; overflow-y: auto;\">
                <table id=\"usersTable\">
                    <thead>
                        <tr>
                            <th>Barcode</th>
                            <th>Name</th>
                            <th>Department</th>
                            <th>Type</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Add/Edit User Modal -->
    <div id=\"addUserModal\" class=\"modal\">
        <div class=\"modal-content\">
            <span class=\"close\" onclick=\"closeModal(\'addUserModal\')\">&times;</span>
            <h2 id=\"userFormTitle\">➕ Add User</h2>
            
            <form id=\"userForm\">
                <div class=\"form-group\">
                    <label>Barcode:</label>
                    <input type=\"text\" id=\"userBarcode\" required>
                </div>
                
                <div class=\"form-group\">
                    <label>Name:</label>
                    <input type=\"text\" id=\"userName\" required>
                </div>
                
                <div class=\"form-group\">
                    <label>Department:</label>
                    <input type=\"text\" id=\"userDepartment\">
                </div>
                
                <div class=\"form-group\">
                    <label>User Type:</label>
                    <select id=\"userType\" required>
                        <option value=\"student\">Student</option>
                        <option value=\"faculty\">Faculty</option>
                        <option value=\"non_teaching_staff\">Non-Teaching Staff</option>
                        <option value=\"admin\">Admin</option>
                    </select>
                </div>
                
                <button type=\"submit\" class=\"btn\">💾 Save</button>
                <button type=\"button\" class=\"btn\" onclick=\"closeModal(\'addUserModal\')\">❌ Cancel</button>
            </form>
        </div>
    </div>

    <!-- Manual Entry Modal -->
    <div id=\"manualEntryModal\" class=\"modal\">
        <div class=\"modal-content\">
            <span class=\"close\" onclick=\"closeModal(\'manualEntryModal\')\">&times;</span>
            <h2>✏️ Manual Attendance Entry</h2>
            
            <form id=\"manualEntryForm\">
                <div class=\"form-group\">
                    <label>Barcode:</label>
                    <input type=\"text\" id=\"manualBarcode\" required>
                </div>
                
                <div class=\"form-group\">
                    <label>Date:</label>
                    <input type=\"date\" id=\"manualDate\" required>
                </div>
                
                <div class=\"form-group\">
                    <label>Entry Time:</label>
                    <input type=\"datetime-local\" id=\"manualEntryTime\" required>
                </div>
                
                <div class=\"form-group\">
                    <label>Exit Time:</label>
                    <input type=\"datetime-local\" id=\"manualExitTime\">
                </div>
                
                <button type=\"submit\" class=\"btn\">💾 Add Record</button>
                <button type=\"button\" class=\"btn\" onclick=\"closeModal(\'manualEntryModal\')\">❌ Cancel</button>
            </form>
        </div>
    </div>

    <!-- Export Modal -->
    <div id=\"exportModal\" class=\"modal\">
        <div class=\"modal-content\">
            <span class=\"close\" onclick=\"closeModal(\'exportModal\')\">&times;</span>
            <h2>📊 Export Attendance Records</h2>
            
            <form id=\"exportForm\">
                <div class=\"form-group\">
                    <label>Export Format:</label>
                    <select id=\"exportFormat\" required>
                        <option value=\"excel\">Excel (.xlsx)</option>
                        <option value=\"csv\">CSV (.csv)</option>
                    </select>
                </div>
                
                <div class=\"form-group\">
                    <label>Start Date:</label>
                    <input type=\"date\" id=\"exportStartDate\">
                </div>
                
                <div class=\"form-group\">
                    <label>End Date:</label>
                    <input type=\"date\" id=\"exportEndDate\">
                </div>
                
                <button type=\"submit\" class=\"btn\">📥 Export</button>
                <button type=\"button\" class=\"btn\" onclick=\"closeModal(\'exportModal\')\">❌ Cancel</button>
            </form>
        </div>
    </div>

    <script>
        let currentEditBarcode = null;

        document.addEventListener(\"DOMContentLoaded\", function () {
            loadAttendance();
            loadDepartments();
            populateYearFilter();
            populateDayFilter();
            document.getElementById(\"barcodeInput\").focus();
            
            // Set today\'s date as default for manual entry
            document.getElementById(\"manualDate\").value = new Date().toISOString().split(\'T\')[0];
            
            // Close settings menu when clicking outside
            document.addEventListener(\'click\', function(event) {
                const settingsMenu = document.getElementById(\'settingsMenu\');
                const settingsBtn = event.target.closest(\'\\.settings-btn\');
                
                if (!settingsBtn && !settingsMenu.contains(event.target)) {
                    settingsMenu.style.display = \'none\';
                }
            });
        });

        document.getElementById(\"barcodeInput\").addEventListener(\"keypress\", function (event) {
            if (event.key === \"Enter\") {
                scanBarcode();
            }
        });

        // Auto-clear input after 2 seconds of inactivity (simulates barcode scanner behavior)
        let inputTimeout;
        document.getElementById(\"barcodeInput\").addEventListener(\"input\", function() {
            clearTimeout(inputTimeout);
            inputTimeout = setTimeout(() => {
                if (this.value.length > 0) {
                    scanBarcode();
                }
            }, 100);
        });

        function toggleSettingsMenu() {
            const menu = document.getElementById(\'settingsMenu\');
            menu.style.display = menu.style.display === \'block\' ? \'none\' : \'block\';
        }

        function scanBarcode() {
            let barcode = document.getElementById(\"barcodeInput\").value.trim();
            if (barcode === \"\") return;

            fetch(\"/scan\", {
                method: \"POST\",
                body: JSON.stringify({ barcode: barcode }),
                headers: { \"Content-Type\": \"application/json\" }
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    showPopup(data);
                    document.getElementById(\"barcodeInput\").value = \"\";
                    document.getElementById(\"barcodeInput\").focus();
                    setTimeout(() => loadAttendance(), 500);
                }
            })
            .catch(error => {
                showStatus(\"Error: \" + error.message, \"error\");
            });
        }

        function showPopup(data) {
            const popup = document.createElement(\'div\');
            popup.className = \'popup\';
            popup.innerHTML = `
                <h3>${data.action} Recorded ✅</h3>
                <div class=\"popup-info\"><strong>Name:</strong> ${data.name}</div>
                <div class=\"popup-barcode\"><strong>ID:</strong> ${data.barcode}</div>
                <div class=\"popup-info\"><strong>Type:</strong> ${data.user_type}</div>
                <div class=\"popup-info\"><strong>Time:</strong> ${new Date(data.time).toLocaleString()}</div>
            `;
            
            document.body.appendChild(popup);
            
            setTimeout(() => {
                popup.style.opacity = \'0\';
                setTimeout(() => {
                    document.body.removeChild(popup);
                }, 300);
            }, 5000);
        }

        function loadAttendance() {
            const limit = document.getElementById(\"displayLimit\").value;
            const userType = document.getElementById(\"userTypeFilter\").value;
            const department = document.getElementById(\"departmentFilter\").value;
            const year = document.getElementById(\"yearFilter\").value;
            const month = document.getElementById(\"monthFilter\").value;
            const day = document.getElementById(\"dayFilter\").value;
            
            const params = new URLSearchParams({
                limit: limit,
                user_type: userType,
                department: department,
                year: year,
                month: month,
                day: day
            });
            
            fetch(`/get_attendance?${params}`)
            .then(response => response.json())
            .then(data => {
                const tableBody = document.querySelector(\"#attendanceTable tbody\");
                tableBody.innerHTML = \"\";
                
                if (data.length === 0) {
                    const tr = document.createElement(\"tr\");
                    tr.innerHTML = `<td colspan=\"7\" style=\"text-align: center; color: #666;\">No attendance records found</td>`;
                    tableBody.appendChild(tr);
                    return;
                }
                
                data.forEach(row => {
                    const tr = document.createElement(\"tr\");
                    tr.innerHTML = `
                        <td>${row.Barcode || \'-\'}
                        <td>${row.Name || \'-\'}
                        <td>${row.Department || \'-\'}
                        <td>${row.User_Type || \'-\'}
                        <td>${row.Entry_Time || \'-\'}
                        <td>${row.Exit_Time || \'Still Inside\'}</td>
                        <td>${row.Date || \'-\'}
                    `;
                    tableBody.appendChild(tr);
                });
            })
            .catch(error => {
                console.error(\'Error loading attendance:\', error);
                const tableBody = document.querySelector(\"#attendanceTable tbody\");
                tableBody.innerHTML = `<tr><td colspan=\"7\" style=\"text-align: center; color: #f44336;\">Error loading attendance records</td></tr>`;
            });
        }

        function loadDepartments() {
            fetch(\'/get_departments\')
            .then(response => response.json())
            .then(departments => {
                const departmentFilter = document.getElementById(\'departmentFilter\');
                // Clear existing options except \"All Departments\"
                departmentFilter.innerHTML = \'<option value=\"all\">All Departments</option>\';
                
                departments.forEach(dept => {
                    if (dept && dept.trim() !== \'\') {
                        const option = document.createElement(\'option\');
                        option.value = dept;
                        option.textContent = dept;
                        departmentFilter.appendChild(option);
                    }
                });
            });
        }

        function populateYearFilter() {
            const yearFilter = document.getElementById(\'yearFilter\');
            const currentYear = new Date().getFullYear();
            
            for (let year = currentYear - 5; year <= currentYear + 1; year++) {
                const option = document.createElement(\'option\');
                option.value = year;
                option.textContent = year;
                yearFilter.appendChild(option);
            }
        }

        function populateDayFilter() {
            const dayFilter = document.getElementById(\'dayFilter\');
            
            for (let day = 1; day <= 31; day++) {
                const option = document.createElement(\'option\');
                option.value = day;
                option.textContent = day;
                dayFilter.appendChild(option);
            }
        }

        function filterAttendance() {
            loadAttendance();
        }

        function refreshAttendance() {
            loadAttendance();
            loadDepartments();
            showStatus(\"Attendance records refreshed!\", \"success\");
            document.getElementById(\'settingsMenu\').style.display = \'none\';
        }

        function openUserManagement() {
            document.getElementById(\"userModal\").style.display = \"block\";
            document.getElementById(\'settingsMenu\').style.display = \'none\';
            loadUsers();
        }

        function loadUsers() {
            const userType = document.getElementById(\"userFilterType\").value;
            
            fetch(`/get_users?user_type=${userType}`)
            .then(response => response.json())
            .then(data => {
                const tableBody = document.querySelector(\"#usersTable tbody\");
                tableBody.innerHTML = \"\";
                
                data.forEach(user => {
                    const tr = document.createElement(\'tr\');
                    tr.innerHTML = `
                        <td>${user.Barcode}</td>
                        <td>${user.Name}</td>
                        <td>${user.Department || \'-\'}
                        <td>${user.User_Type}</td>
                        <td>
                            <button class=\"btn\" onclick=\"editUser(\'${user.Barcode}\')\">✏️ Edit</button>
                            <button class=\"btn btn-danger\" onclick=\"deleteUser(\'${user.Barcode}\')\">🗑️ Delete</button>
                        </td>
                    `;
                    tableBody.appendChild(tr);
                });
            });
        }

        function openAddUser() {
            currentEditBarcode = null;
            document.getElementById(\"userFormTitle\").textContent = \"➕ Add User\";
            document.getElementById(\"userForm\").reset();
            document.getElementById(\"userBarcode\").disabled = false;
            document.getElementById(\"addUserModal\").style.display = \"block\";
        }

        function editUser(barcode) {
            currentEditBarcode = barcode;
            document.getElementById(\"userFormTitle\").textContent = \"✏️ Edit User\";
            
            // Load user data
            fetch(`/get_users`)
            .then(response => response.json())
            .then(users => {
                const user = users.find(u => u.Barcode === barcode);
                if (user) {
                    document.getElementById(\"userBarcode\").value = user.Barcode;
                    document.getElementById(\"userName\").value = user.Name;
                    document.getElementById(\"userDepartment\").value = user.Department || \'\';
                    document.getElementById(\"userType\").value = user.User_Type;
                    document.getElementById(\"userBarcode\").disabled = true;
                    document.getElementById(\"addUserModal\").style.display = \"block\";
                }
            });
        }

        function deleteUser(barcode) {
            if (confirm(`Are you sure you want to delete user with barcode: ${barcode}?`)) {
                fetch(\"/delete_user\", {
                    method: \"POST\",
                    body: JSON.stringify({ barcode: barcode }),
                    headers: { \"Content-Type\": \"application/json\" }
                })
                .then(response => response.json())
                .then(data => {
                    showStatus(data.message, \"success\");
                    loadUsers();
                });
            }
        }

        document.getElementById(\"userForm\").addEventListener(\"submit\", function(e) {
            e.preventDefault();
            
            const userData = {
                barcode: document.getElementById(\"userBarcode\").value,
                name: document.getElementById(\"userName\").value,
                department: document.getElementById(\"userDepartment\").value,
                user_type: document.getElementById(\"userType\").value
            };
            
            const url = currentEditBarcode ? \"/update_user\" : \"/add_user\";
            
            fetch(url, {
                method: \"POST\",
                body: JSON.stringify(userData),
                headers: { \"Content-Type\": \"application/json\" }
            })
            .then(response => response.json())
            .then(data => {
                showStatus(data.message, response.ok ? \"success\" : \"error\");
                if (response.ok) {
                    closeModal(\'addUserModal\');
                    loadUsers();
                    loadDepartments(); // Refresh departments list
                }
            });
        });

        function openManualEntry() {
            document.getElementById(\"manualEntryModal\").style.display = \"block\";
            document.getElementById(\'settingsMenu\').style.display = \'none\';
        }

        document.getElementById(\"manualEntryForm\").addEventListener(\"submit\", function(e) {
            e.preventDefault();
            
            const entryData = {
                barcode: document.getElementById(\"manualBarcode\").value,
                date: document.getElementById(\"manualDate\").value,
                entry_time: document.getElementById(\"manualEntryTime\").value,
                exit_time: document.getElementById(\"manualExitTime\").value || null
            };
            
            fetch(\"/add_attendance\", {
                method: \"POST\",
                body: JSON.stringify(entryData),
                headers: { \"Content-Type\": \"application/json\" }
            })
            .then(response => response.json())
            .then(data => {
                showStatus(data.message, response.ok ? \"success\" : \"error\");
                if (response.ok) {
                    closeModal(\'manualEntryModal\');
                    loadAttendance();
                    document.getElementById(\"manualEntryForm\").reset();
                    document.getElementById(\"manualDate\").value = new Date().toISOString().split(\'T\')[0];
                }
            });
        });

        function openExportRecords() {
            document.getElementById(\"exportModal\").style.display = \"block\";
            document.getElementById(\'settingsMenu\').style.display = \'none\';
        }

        document.getElementById(\"exportForm\").addEventListener(\"submit\", function(e) {
            e.preventDefault();
            
            const exportData = {
                format: document.getElementById(\"exportFormat\").value,
                start_date: document.getElementById(\"exportStartDate\").value,
                end_date: document.getElementById(\"exportEndDate\").value
            };
            
            fetch(\"/export_attendance\", {
                method: \"POST\",
                body: JSON.stringify(exportData),
                headers: { \"Content-Type\": \"application/json\" }
            })
            .then(response => {
                if (response.ok) {
                    return response.blob();
                }
                throw new Error(\'Export failed\');
            })
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement(\'a\');
                a.style.display = \'none\';
                a.href = url;
                a.download = `attendance_export_${new Date().toISOString().split(\'T\')[0]}.${exportData.format === \'excel\' ? \'xlsx\' : \'csv\'}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                showStatus(\"Export completed successfully!\", \"success\");
                closeModal(\'exportModal\');
            })
            .catch(error => {
                showStatus(\"Export failed: \" + error.message, \"error\");
            });
        });

        function closeModal(modalId) {
            document.getElementById(modalId).style.display = \"none\";
        }

        function showStatus(message, type) {
            const statusDiv = document.getElementById(\"statusMessage\");
            statusDiv.textContent = message;
            statusDiv.className = `status-message status-${type}`;
            statusDiv.style.display = \"block\";
            
            setTimeout(() => {
                statusDiv.style.display = \"none\";
            }, 3000);
        }

        // Close modals when clicking outside
        window.onclick = function(event) {
            const modals = document.querySelectorAll(\'\\.modal\');
            modals.forEach(modal => {
                if (event.target === modal) {
                    modal.style.display = \"none\";
                }
            });
        }
    </script>
</body>
</html>
"""

import webbrowser

if __name__ == "__main__":
    initialize_files()

    import threading, webbrowser
    def _open_browser():
        webbrowser.open_new("http://127.0.0.1:5000/")

    threading.Timer(1.0, _open_browser).start()

    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

