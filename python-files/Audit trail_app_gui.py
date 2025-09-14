import hashlib
import json
import os
import uuid
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog


# ----------------- Configuration -----------------
DB_FILE = "audit_db.json"
UPLOAD_DIR = "uploaded_files"
REPORT_DIR = "reports"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

ADMIN_ROLE = "Admin"
AUDITOR_ROLE = "Auditor"
ANALYST_ROLE = "Analyst"

# ----------------- Backend Classes -----------------
class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password_hash = self._hash_password(password)
        self.role = role
        self.user_id = str(uuid.uuid4())
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    def check_password(self, password):
        return self._hash_password(password) == self.password_hash
    def to_dict(self):
        return {"user_id": self.user_id,"username": self.username,"password_hash": self.password_hash,"role": self.role}

class Logger:
    def __init__(self):
        self.logs = []
    def log_action(self, user_id, username, action_type, description):
        timestamp = datetime.now().isoformat()
        log_entry = {
            "log_id": str(uuid.uuid4()),
            "timestamp": timestamp,
            "user_id": user_id,
            "username": username,
            "action_type": action_type,
            "description": description,
            "status": "Pending Review",
            "reviewer_id": None,
            "review_comment": None,
            "conclusion": None
        }
        self.logs.append(log_entry)
        return log_entry
    def get_logs(self):
        return self.logs
    def review_log(self, log_id, reviewer_id, comment, conclusion):
        for log in self.logs:
            if log["log_id"] == log_id and log["status"]=="Pending Review":
                log["status"]="Approved"
                log["reviewer_id"]=reviewer_id
                log["review_comment"]=comment
                log["conclusion"]=conclusion
                log["review_timestamp"]=datetime.now().isoformat()
                return True
        return False

class AuditApp:
    def __init__(self):
        self.users={}
        self.current_user=None
        self.logger=Logger()
        self.checklists={}
        self._load_data()
    def _load_data(self):
        if os.path.exists(DB_FILE):
            with open(DB_FILE,"r") as f:
                data=json.load(f)
                for udata in data.get("users",[]):
                    u=User(udata["username"],"placeholder",udata["role"])
                    u.user_id=udata["user_id"]
                    u.password_hash=udata["password_hash"]
                    self.users[u.username]=u
                self.logger.logs=data.get("logs",[])
                self.checklists=data.get("checklists",{})
        else:
            self.register_user("admin","admin123",ADMIN_ROLE)
    def _save_data(self):
        data={
            "users":[u.to_dict() for u in self.users.values()],
            "logs":self.logger.get_logs(),
            "checklists":self.checklists
        }
        with open(DB_FILE,"w") as f:
            json.dump(data,f,indent=4)
    def register_user(self,username,password,role):
        if username in self.users: return False
        u=User(username,password,role)
        self.users[username]=u
        self.logger.log_action("SYSTEM","System","User_Creation",f"New user '{username}' with role '{role}'")
        self._save_data()
        return True
    def login(self,username,password):
        if username in self.users and self.users[username].check_password(password):
            self.current_user=self.users[username]
            self.logger.log_action(self.current_user.user_id,self.current_user.username,"User_Login","User logged in")
            self._save_data()
            return True
        else:
            self.logger.log_action("N/A",username,"Failed_Login","Invalid credentials")
            self._save_data()
            return False
    def logout(self):
        if self.current_user:
            self.logger.log_action(self.current_user.user_id,self.current_user.username,"User_Logout","User logged out")
            self.current_user=None
            self._save_data()

# ----------------- GUI -----------------
app=AuditApp()
root=tk.Tk()
root.title("Advanced Audit App")
root.geometry("900x600")

# ----------------- Screens -----------------
def login_screen():
    for w in root.winfo_children(): w.destroy()
    frame=tk.Frame(root); frame.pack(pady=50)
    tk.Label(frame,text="Username").grid(row=0,column=0)
    uentry=tk.Entry(frame); uentry.grid(row=0,column=1)
    tk.Label(frame,text="Password").grid(row=1,column=0)
    pentry=tk.Entry(frame,show="*"); pentry.grid(row=1,column=1)
    def attempt():
        u=uentry.get(); p=pentry.get()
        if app.login(u,p): dashboard_screen()
        else: messagebox.showerror("Error","Invalid credentials")
    tk.Button(frame,text="Login",command=attempt).grid(row=2,column=0,columnspan=2,pady=10)

def dashboard_screen():
    for w in root.winfo_children(): w.destroy()
    frame=tk.Frame(root); frame.pack(pady=20)
    tk.Label(frame,text=f"Welcome {app.current_user.username} ({app.current_user.role})").pack(pady=10)
    tk.Button(frame,text="Upload & Save File",width=30,command=upload_file_action).pack(pady=5)
    tk.Button(frame,text="Analyze File",width=30,command=select_file_for_analysis).pack(pady=5)
    tk.Button(frame,text="Manage Checklists",width=30,command=checklist_screen).pack(pady=5)
    tk.Button(frame,text="View Audit Logs",width=30,command=view_logs_screen).pack(pady=5)
    if app.current_user.role==ADMIN_ROLE: tk.Button(frame,text="Register User",width=30,command=register_user_screen).pack(pady=5)
    if app.current_user.role==AUDITOR_ROLE: tk.Button(frame,text="Review Logs",width=30,command=review_logs_screen).pack(pady=5)
    tk.Button(frame,text="Logout",width=30,command=logout_screen).pack(pady=5)

def logout_screen(): app.logout(); login_screen()

# ----------------- File Upload & Analysis -----------------
def upload_file_action():
    file_path=filedialog.askopenfilename(title="Select File",filetypes=[("All Files","*.*"),("PDF","*.pdf"),("CSV","*.csv"),("Excel","*.xls *.xlsx")])
    if file_path:
        dest=os.path.join(UPLOAD_DIR,os.path.basename(file_path))
        shutil.copy(file_path,dest)
        app.logger.log_action(app.current_user.user_id,app.current_user.username,"File_Upload",f"Uploaded: {os.path.basename(file_path)}")
        app._save_data()
        messagebox.showinfo("Success","File uploaded and saved!")

def select_file_for_analysis():
    file_path=filedialog.askopenfilename(initialdir=UPLOAD_DIR,title="Select File")
    if file_path: analyze_file(file_path)

def analyze_file(file_path):
    ext=os.path.splitext(file_path)[1].lower()
    if ext in [".csv",".xls",".xlsx"]:
        df=pd.read_csv(file_path) if ext==".csv" else pd.read_excel(file_path)
        info=f"Rows: {df.shape[0]}, Columns: {df.shape[1]}\nColumns: {', '.join(df.columns)}"
        messagebox.showinfo("Analysis",info)
    elif ext==".pdf":
        reader=PdfReader(file_path)
        messagebox.showinfo("Analysis",f"PDF Pages: {len(reader.pages)}")
    else:
        messagebox.showinfo("Analysis","No analysis available for this file type")

# ----------------- Checklists -----------------
def checklist_screen():
    win=tk.Toplevel(root); win.title("Checklists"); win.geometry("500x400")
    tk.Label(win,text="Audit Checklists").pack()
    lb=tk.Listbox(win); lb.pack(fill="both",expand=True)
    for name in app.checklists: lb.insert(tk.END,name)
    def add_checklist():
        name=simpledialog.askstring("New Checklist","Checklist Name:")
        if name:
            app.checklists[name]=[]
            app._save_data(); lb.insert(tk.END,name)
    def run_checklist():
        sel=lb.curselection()
        if not sel: return
        name=lb.get(sel[0])
        points=app.checklists[name]
        messagebox.showinfo("Run Checklist",f"Checklist '{name}' has {len(points)} points")
    tk.Button(win,text="Add Checklist",command=add_checklist).pack(pady=5)
    tk.Button(win,text="Run Checklist",command=run_checklist).pack(pady=5)

# ----------------- Audit Logs -----------------
def view_logs_screen():
    logs=app.logger.get_logs()
    win=tk.Toplevel(root); win.title("Audit Logs"); win.geometry("900x400")
    tree=ttk.Treeview(win,columns=("ID","User","Action","Desc","Status","Time"),show="headings")
    for c in ("ID","User","Action","Desc","Status","Time"): tree.heading(c,text=c); tree.column(c,width=140)
    tree.pack(fill="both",expand=True)
    for log in logs:
        tree.insert("", "end", values=(log["log_id"][:8],log["username"],log["action_type"],log["description"],log["status"],log["timestamp"][:19]))

# ----------------- Review Logs -----------------
def review_logs_screen():
    logs=[l for l in app.logger.get_logs() if l["status"]=="Pending Review"]
    if not logs: messagebox.showinfo("Review","No pending logs"); return
    win=tk.Toplevel(root); win.title("Review Logs"); win.geometry("900x400")
    tree=ttk.Treeview(win,columns=("ID","User","Action","Desc","Status","Time"),show="headings")
    for c in ("ID","User","Action","Desc","Status","Time"): tree.heading(c,text=c); tree.column(c,width=140)
    tree.pack(fill="both",expand=True)
    for log in logs: tree.insert("", "end", values=(log["log_id"][:8],log["username"],log["action_type"],log["description"],log["status"],log["timestamp"][:19]))
    def approve():
        sel=tree.selection()
        if not sel: return
        item=tree.item(sel[0]); log_id_prefix=item["values"][0]
        full_id=next((l["log_id"] for l in logs if l["log_id"].startswith(log_id_prefix)),None)
        if full_id:
            comment=simpledialog.askstring("Review","Enter Comment:")
            conclusion=simpledialog.askstring("Conclusion","Enter Conclusion:")
            app.logger.review_log(full_id,app.current_user.user_id,comment,conclusion)
            app._save_data(); messagebox.showinfo("Success","Log Approved")
            review_logs_screen(); win.destroy()
    tk.Button(win,text="Approve Selected",command=approve).pack(pady=5)

# ----------------- User Registration -----------------
def register_user_screen():
    u=simpledialog.askstring("Register","Username:"); 
    if not u: return
    p=simpledialog.askstring("Register","Password:",show="*"); 
    if not p: return
    r=simpledialog.askstring("Register","Role (Admin,Auditor,Analyst):")
    if app.register_user(u,p,r): messagebox.showinfo("Success","User registered")
    else: messagebox.showerror("Error","Username exists")

# ----------------- Run -----------------
login_screen()
root.mainloop()
