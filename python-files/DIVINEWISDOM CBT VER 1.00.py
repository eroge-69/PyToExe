# divine_wisdom_cbt_fixed_for_start_and_add.py
# Pydroid-friendly CBT app — fixes for Start Exam and Add Question problems
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
import sqlite3
import random
import datetime

DB_FILE = "divine_wisdom_cbt.db"
ADMIN_PASSWORD = "013456aa"

# -------------------------
# Database setup
# -------------------------
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    opt_a TEXT NOT NULL,
    opt_b TEXT NOT NULL,
    opt_c TEXT NOT NULL,
    opt_d TEXT NOT NULL,
    answer TEXT NOT NULL,
    UNIQUE(subject_id, question)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student TEXT,
    subject_id INTEGER,
    score INTEGER,
    total INTEGER,
    date TEXT
)
""")

conn.commit()

# -------------------------
# Helpers
# -------------------------
def get_subjects():
    cursor.execute("SELECT id, name FROM subjects ORDER BY name")
    return cursor.fetchall()

def add_subject(name):
    name = name.strip()
    if not name:
        return False, "Empty name"
    try:
        cursor.execute("INSERT INTO subjects(name) VALUES(?)", (name,))
        conn.commit()
        return True, None
    except sqlite3.IntegrityError:
        return False, "Subject already exists"
    except Exception as e:
        return False, str(e)

def delete_subject_by_id(sid):
    try:
        cursor.execute("DELETE FROM questions WHERE subject_id=?", (sid,))
        cursor.execute("DELETE FROM subjects WHERE id=?", (sid,))
        conn.commit()
        return True
    except Exception:
        return False

def save_question(subject_id, question_text, opts, answer_letter):
    # opts is dict with "A","B","C","D"
    question_text = question_text.strip()
    if not question_text:
        return False, "Empty question"
    for k in ("A","B","C","D"):
        if not opts.get(k) or not opts[k].strip():
            return False, "Option {} empty".format(k)
    answer_letter = answer_letter.strip().upper()
    if answer_letter in ("1","2","3","4"):
        map_i = {"1":"A","2":"B","3":"C","4":"D"}
        answer_letter = map_i[answer_letter]
    if answer_letter not in ("A","B","C","D"):
        return False, "Invalid answer (use A/B/C/D or 1-4)"

    try:
        cursor.execute("""
            INSERT INTO questions(subject_id, question, opt_a, opt_b, opt_c, opt_d, answer)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (subject_id, question_text, opts["A"].strip(), opts["B"].strip(), opts["C"].strip(), opts["D"].strip(), answer_letter))
        conn.commit()
        return True, None
    except sqlite3.IntegrityError:
        return False, "Duplicate question for this subject"
    except Exception as e:
        return False, str(e)

def get_questions_by_subject_id(sid):
    cursor.execute("SELECT id, question, opt_a, opt_b, opt_c, opt_d, answer FROM questions WHERE subject_id=?", (sid,))
    return cursor.fetchall()

def save_result(student, subject_id, score, total):
    try:
        cursor.execute("INSERT INTO results(student, subject_id, score, total, date) VALUES (?, ?, ?, ?, ?)",
                       (student, subject_id, score, total, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        return True
    except Exception:
        return False

def import_questions_to_subject(subject_id, filename):
    # tolerant importer: blocks separated by blank line, lines trimmed
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read().replace("\r\n", "\n").strip()
    except Exception as e:
        return 0, "Could not open file: {}".format(e)

    blocks = [b for b in content.split("\n\n") if b.strip()]
    count = 0
    for block in blocks:
        lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
        if len(lines) < 6:
            continue
        # parse first line as question (allow optional "Question:" prefix)
        qline = lines[0]
        if qline.lower().startswith("question:"):
            question_text = qline.split(":",1)[1].strip()
        else:
            question_text = qline
        # parse options tolerant
        def parse_opt(line):
            # Accept forms: "A) text", "A. text", "A text", or "text"
            if len(line) >= 2 and line[1] == ")" :
                return line.split(")",1)[1].strip()
            if "." in line and line.split(".",1)[0].strip().upper() in ("A","B","C","D"):
                return line.split(".",1)[1].strip()
            if len(line) >= 2 and line[1] == " " and line[0].upper() in ("A","B","C","D"):
                return line[2:].strip()
            return line.strip()

        A = parse_opt(lines[1]) if len(lines) > 1 else ""
        B = parse_opt(lines[2]) if len(lines) > 2 else ""
        C = parse_opt(lines[3]) if len(lines) > 3 else ""
        D = parse_opt(lines[4]) if len(lines) > 4 else ""
        ans_line = lines[5]
        if ans_line.lower().startswith("answer:"):
            ans = ans_line.split(":",1)[1].strip().upper()
        else:
            ans = ans_line.strip().upper()
        if ans in ("1","2","3","4"):
            map_i = {"1":"A","2":"B","3":"C","4":"D"}
            ans = map_i[ans]
        if ans not in ("A","B","C","D"):
            continue
        ok, reason = save_question(subject_id, question_text, {"A":A,"B":B,"C":C,"D":D}, ans)
        if ok:
            count += 1
        # stop at 50
        if count >= 50:
            break
    return count, None

# -------------------------
# GUI
# -------------------------
class CBTApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DIVINE WISDOM CBT")
        # Pydroid safe geometry
        try:
            self.geometry("420x720")
        except Exception:
            pass
        self.configure(bg="#f2f7ff")
        self.main_menu()

    def clear(self):
        for w in self.winfo_children():
            w.destroy()

    def main_menu(self):
        self.clear()
        header = tk.Label(self, text="DIVINE WISDOM CBT", bg="#1e90ff", fg="white", font=("Arial", 18, "bold"))
        header.pack(fill="x", pady=6)
        frame = tk.Frame(self, bg="#f2f7ff")
        frame.pack(expand=True)
        tk.Button(frame, text="Student", width=20, height=2, bg="#6ee7b7", command=self.student_screen).pack(pady=12)
        tk.Button(frame, text="Admin", width=20, height=2, bg="#fbbf24", command=self.admin_login_screen).pack(pady=6)

    # ---------------- Admin ----------------
    def admin_login_screen(self):
        self.clear()
        tk.Label(self, text="Admin Password:", bg="#f2f7ff").pack(pady=12)
        pw = tk.Entry(self, show="*")
        pw.pack(pady=6)
        def check():
            if pw.get() == ADMIN_PASSWORD:
                self.admin_panel()
            else:
                messagebox.showerror("Access Denied", "Wrong password")
        tk.Button(self, text="Login", command=check, bg="#60a5fa").pack(pady=10)
        tk.Button(self, text="Back", command=self.main_menu).pack(pady=6)

    def admin_panel(self):
        self.clear()
        tk.Label(self, text="Admin Panel", bg="#f2f7ff", font=("Arial", 16, "bold")).pack(pady=8)
        tk.Button(self, text="Manage Subjects", width=24, command=self.manage_subjects_screen).pack(pady=6)
        tk.Button(self, text="Manage Questions (Add/Import/Delete)", width=24, command=self.select_subject_for_questions).pack(pady=6)
        tk.Button(self, text="View Results / Export", width=24, command=self.view_results).pack(pady=6)
        tk.Button(self, text="Back", command=self.main_menu).pack(pady=8)

    def manage_subjects_screen(self):
        self.clear()
        tk.Label(self, text="Manage Subjects", bg="#f2f7ff", font=("Arial", 14, "bold")).pack(pady=6)
        listbox = tk.Listbox(self, height=8)
        listbox.pack(padx=12, pady=6, fill="x")
        subs = get_subjects()
        for sid, name in subs:
            listbox.insert(tk.END, name)
        entry = tk.Entry(self)
        entry.pack(padx=12, fill="x", pady=6)
        def do_add():
            ok, reason = add_subject(entry.get())
            if ok:
                messagebox.showinfo("Added", "Subject added")
                self.manage_subjects_screen()
            else:
                messagebox.showerror("Error", reason or "Failed")
        def do_delete():
            try:
                sel = listbox.get(listbox.curselection())
            except Exception:
                messagebox.showwarning("Select", "Select a subject")
                return
            # find subject id
            sid = None
            for s in subs:
                if s[1] == sel:
                    sid = s[0]; break
            if sid is None:
                messagebox.showerror("Error", "Could not find subject id")
                return
            if delete_subject_by_id(sid):
                messagebox.showinfo("Deleted", "Subject deleted")
                self.manage_subjects_screen()
            else:
                messagebox.showerror("Error", "Delete failed")
        tk.Button(self, text="Add Subject", bg="#86efac", command=do_add).pack(pady=6)
        tk.Button(self, text="Delete Selected", bg="#fb7185", command=do_delete).pack(pady=6)
        tk.Button(self, text="Back", command=self.admin_panel).pack(pady=8)

    def select_subject_for_questions(self):
        self.clear()
        tk.Label(self, text="Pick subject to manage questions", bg="#f2f7ff", font=("Arial", 14)).pack(pady=8)
        listbox = tk.Listbox(self, height=10)
        listbox.pack(padx=12, pady=6, fill="x")
        subs = get_subjects()
        for sid, name in subs:
            listbox.insert(tk.END, name)
        def go():
            try:
                idx = listbox.curselection()[0]
            except Exception:
                messagebox.showwarning("Select", "Select a subject")
                return
            sid, name = subs[idx]
            self.manage_questions_screen(sid, name)
        tk.Button(self, text="Manage Questions", bg="#60a5fa", command=go).pack(pady=6)
        tk.Button(self, text="Back", command=self.admin_panel).pack(pady=6)

    def manage_questions_screen(self, subject_id, subject_name):
        self.clear()
        tk.Label(self, text="Manage Questions for: {}".format(subject_name), bg="#f2f7ff", font=("Arial", 14, "bold")).pack(pady=6)
        tk.Label(self, text="Add one question using the text area below (6 lines):", bg="#f2f7ff").pack(pady=4)
        text_area = scrolledtext.ScrolledText(self, width=50, height=10, wrap="word")
        text_area.pack(padx=12, pady=6)

        def parse_text_block(text_block):
            lines = [ln.strip() for ln in text_block.splitlines() if ln.strip()]
            if len(lines) < 6:
                return None, "Need at least 6 non-empty lines"
            qline = lines[0]
            if qline.lower().startswith("question:"):
                qtext = qline.split(":",1)[1].strip()
            else:
                qtext = qline
            def parse_opt(line):
                if len(line) >= 2 and line[1] == ")":
                    return line.split(")",1)[1].strip()
                if "." in line and line.split(".",1)[0].strip().upper() in ("A","B","C","D"):
                    return line.split(".",1)[1].strip()
                if len(line) >= 2 and line[0].upper() in ("A","B","C","D") and line[1] == " ":
                    return line[2:].strip()
                return line.strip()
            A = parse_opt(lines[1]); B = parse_opt(lines[2]); C = parse_opt(lines[3]); D = parse_opt(lines[4])
            ans_line = lines[5]
            if ans_line.lower().startswith("answer:"):
                ans = ans_line.split(":",1)[1].strip().upper()
            else:
                ans = ans_line.strip().upper()
            if ans in ("1","2","3","4"):
                map_i = {"1":"A","2":"B","3":"C","4":"D"}
                ans = map_i[ans]
            if ans not in ("A","B","C","D"):
                return None, "Answer must be A/B/C/D or 1-4"
            return (qtext, {"A":A,"B":B,"C":C,"D":D}, ans), None

        def do_add_from_textarea():
            txt = text_area.get("1.0", "end").strip()
            parsed, err = parse_text_block(txt)
            if not parsed:
                messagebox.showerror("Invalid", err)
                return
            qtext, opts, ans = parsed
            ok, reason = save_question(subject_id, qtext, opts, ans)
            if ok:
                messagebox.showinfo("Saved", "Question added")
                text_area.delete("1.0", "end")
            else:
                messagebox.showerror("Error", reason or "Failed to save question")

        def do_import_file():
            path = filedialog.askopenfilename(filetypes=[("Text Files","*.txt")])
            if not path:
                return
            count, err = import_questions_to_subject(subject_id, path)
            if err:
                messagebox.showerror("Error", err)
            else:
                messagebox.showinfo("Imported", "{} questions imported".format(count))

        def do_delete_question():
            # open small selector of questions for this subject
            win = tk.Toplevel(self)
            win.title("Delete question")
            lb = tk.Listbox(win, width=80)
            lb.pack(fill="both", expand=True, padx=6, pady=6)
            cursor.execute("SELECT id, question FROM questions WHERE subject_id=? ORDER BY id DESC", (subject_id,))
            rows = cursor.fetchall()
            for r in rows:
                tid = r[0]; txt = r[1]
                if len(txt) > 80:
                    txt = txt[:76] + "..."
                lb.insert(tk.END, "{}: {}".format(tid, txt))
            def do_del():
                try:
                    sel = lb.get(lb.curselection())
                except Exception:
                    messagebox.showwarning("Select", "Select a question to delete")
                    return
                qid = int(sel.split(":",1)[0])
                if messagebox.askyesno("Confirm", "Delete this question?"):
                    cursor.execute("DELETE FROM questions WHERE id=?", (qid,))
                    conn.commit()
                    messagebox.showinfo("Deleted", "Question deleted")
                    win.destroy()
            tk.Button(win, text="Delete Selected", bg="#fb7185", command=do_del).pack(pady=6)

        tk.Button(self, text="Add Question (from text area)", bg="#86efac", command=do_add_from_textarea).pack(pady=6)
        tk.Button(self, text="Import Questions from .txt", bg="#60a5fa", command=do_import_file).pack(pady=6)
        tk.Button(self, text="Delete Question", bg="#fb7185", command=do_delete_question).pack(pady=6)
        tk.Button(self, text="Back", command=self.admin_panel).pack(pady=8)

    def view_results(self):
        self.clear()
        tk.Label(self, text="Results (most recent first)", bg="#f2f7ff", font=("Arial", 14, "bold")).pack(pady=6)
        frame = tk.Frame(self, bg="#f2f7ff")
        frame.pack(fill="both", expand=True)
        cursor.execute("""
            SELECT r.student, s.name, r.score, r.total, r.date
            FROM results r LEFT JOIN subjects s ON r.subject_id = s.id
            ORDER BY r.id DESC
        """)
        rows = cursor.fetchall()
        for r in rows:
            student, subj, score, total, date = r
            tk.Label(frame, text="{} | {} | {}/{} | {}".format(student, subj or "(deleted)", score, total, date), anchor="w").pack(fill="x", padx=6)
        def export_csv():
            path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
            if not path:
                return
            try:
                import csv
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Student","Subject","Score","Total","Date"])
                    for r in rows:
                        writer.writerow(r)
                messagebox.showinfo("Exported", "Saved to {}".format(path))
            except Exception as e:
                messagebox.showerror("Error", "Export failed: {}".format(e))
        tk.Button(self, text="Export CSV", bg="#86efac", command=export_csv).pack(pady=6)
        tk.Button(self, text="Back", command=self.admin_panel).pack(pady=6)

    # ---------------- Student flow ----------------
    def student_screen(self):
        self.clear()
        tk.Label(self, text="Student - Enter name and pick subject", bg="#f2f7ff").pack(pady=6)
        name_entry = tk.Entry(self)
        name_entry.pack(padx=12, fill="x", pady=6)
        tk.Label(self, text="Choose Subject:", bg="#f2f7ff").pack(pady=6)
        listbox = tk.Listbox(self, height=8)
        listbox.pack(padx=12, pady=6, fill="x")
        subs = get_subjects()
        for sid, nm in subs:
            listbox.insert(tk.END, nm)
        tk.Label(self, text="Duration (minutes):", bg="#f2f7ff").pack(pady=6)
        dur_entry = tk.Entry(self)
        dur_entry.insert(0, "10")
        dur_entry.pack(pady=4)
        def do_start():
            student = name_entry.get().strip()
            if not student:
                messagebox.showwarning("Missing", "Enter your name")
                return
            try:
                idx = listbox.curselection()[0]
            except Exception:
                messagebox.showwarning("Missing", "Select a subject")
                return
            sid, sname = subs[idx]
            try:
                minutes = int(dur_entry.get())
                if minutes <= 0:
                    raise ValueError
            except Exception:
                messagebox.showwarning("Invalid", "Enter positive integer minutes")
                return
            questions = get_questions_by_subject_id(sid)
            if not questions:
                messagebox.showinfo("No Questions", "This subject has no questions")
                return
            # start exam
            self.start_exam(student, sid, sname, questions, minutes)
        tk.Button(self, text="Start Exam", bg="#86efac", command=do_start).pack(pady=10)
        tk.Button(self, text="Back", command=self.main_menu).pack(pady=6)

    def start_exam(self, student, subject_id, subject_name, questions, minutes):
        self.clear()
        tk.Label(self, text="Exam: {}  |  Student: {}".format(subject_name, student), bg="#f2f7ff", font=("Arial", 14)).pack(pady=6)
        timer_lbl = tk.Label(self, text="", fg="red", bg="#f2f7ff", font=("Arial", 12, "bold"))
        timer_lbl.pack(pady=4)
        random.shuffle(questions)
        # scrollable area
        canvas = tk.Canvas(self, bg="#f2f7ff", highlightthickness=0)
        vsb = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg="#f2f7ff")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        answer_vars = {}
        for idx, q in enumerate(questions, start=1):
            qid = q[0]; qtxt = q[1]
            tk.Label(inner, text="Q{}. {}".format(idx, qtxt), wraplength=380, justify="left", bg="#f2f7ff").pack(anchor="w", padx=6, pady=4)
            var = tk.StringVar(value="")
            for opt_label, opt_text in zip(("A","B","C","D"), q[2:6]):
                tk.Radiobutton(inner, text="{}. {}".format(opt_label, opt_text), variable=var, value=opt_label, bg="#f2f7ff").pack(anchor="w", padx=12)
            answer_vars[qid] = var
        def submit_answers():
            score = 0; total = len(questions)
            for q in questions:
                qid = q[0]; correct = q[6]
                sel = answer_vars[qid].get()
                if sel and sel == correct:
                    score += 1
            save_result(student, subject_id, score, total)
            messagebox.showinfo("Done", "You did great, your scores would be communicated.")
            self.main_menu()
        def countdown(t):
            mins, secs = divmod(t, 60)
            timer_lbl.config(text="Time Left: {:02d}:{:02d}".format(mins, secs))
            if t > 0:
                self.after(1000, countdown, t-1)
            else:
                messagebox.showinfo("Time's Up", "Time is up! Your answers have been submitted.")
                submit_answers()
        # controls
        ctrl = tk.Frame(self, bg="#f2f7ff")
        ctrl.pack(fill="x", pady=6)
        tk.Button(ctrl, text="Submit", bg="#86efac", command=submit_answers).pack(side="left", padx=8)
        tk.Button(ctrl, text="Cancel", command=self.main_menu).pack(side="right", padx=8)
        countdown(minutes * 60)

# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    app = CBTApp()
    app.mainloop()
