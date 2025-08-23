import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tkinter import *
from tkinter import ttk, messagebox, filedialog # Added filedialog for save-as dialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import os
# ------------------------------ NEW IMPORT FOR PDF ------------------------------
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io # For handling image data in memory
# -------------------------------------------------------------------------------

# -------------------- DATABASE SETUP --------------------
def init_db():
    conn = sqlite3.connect("student_performance.db")
    cursor = conn.cursor()
    # Check if table exists and has old schema
    cursor.execute("PRAGMA table_info(question_stats)")
    columns = cursor.fetchall()
    # If table exists but doesn't have student_name column, we need to recreate it
    if columns and not any(col[1] == 'student_name' for col in columns):
        # Backup old data if it exists
        cursor.execute("SELECT * FROM question_stats")
        old_data = cursor.fetchall()
        # Drop old table
        cursor.execute("DROP TABLE IF EXISTS question_stats")
        # Create new table with student_name
        cursor.execute("""
            CREATE TABLE question_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                grade_level INTEGER NOT NULL,
                subject TEXT NOT NULL,
                total_questions INTEGER NOT NULL,
                correct_answers INTEGER NOT NULL,
                wrong_answers INTEGER NOT NULL,
                percentage REAL,
                UNIQUE(student_name, grade_level, subject)
            )
        """)
        # If there was old data, migrate it (with default student name)
        if old_data:
            for row in old_data:
                # row format: (id, grade_level, subject, total_questions, correct_answers, wrong_answers, percentage)
                cursor.execute("""
                    INSERT INTO question_stats 
                    (student_name, grade_level, subject, total_questions, correct_answers, wrong_answers, percentage)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (f"Student_{row[0]}", row[1], row[2], row[3], row[4], row[5], row[6]))
    # If table doesn't exist, create it
    elif not columns:
        cursor.execute("""
            CREATE TABLE question_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                grade_level INTEGER NOT NULL,
                subject TEXT NOT NULL,
                total_questions INTEGER NOT NULL,
                correct_answers INTEGER NOT NULL,
                wrong_answers INTEGER NOT NULL,
                percentage REAL,
                UNIQUE(student_name, grade_level, subject)
            )
        """)
    conn.commit()
    conn.close()

# -------------------- DATA STRUCTURE --------------------
GRADE_SUBJECTS = {
    10: ["Biology", "Physics", "Chemistry", "Mathematics"],
    11: ["Biology", "Physics", "Chemistry", "Mathematics"],
    12: ["Physics", "Mathematics"]
}

# -------------------- DATA OPERATIONS --------------------
def update_question_stats(student_name: str, grade_level: int, subject: str, total_questions: int, 
                         correct_answers: int, wrong_answers: int) -> bool:
    if correct_answers + wrong_answers > total_questions:
        return False
    if grade_level not in GRADE_SUBJECTS or subject not in GRADE_SUBJECTS[grade_level]:
        return False
    percentage = 0.0
    if total_questions > 0:
        percentage = (correct_answers / total_questions) * 100
    conn = sqlite3.connect("student_performance.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO question_stats 
        (student_name, grade_level, subject, total_questions, correct_answers, wrong_answers, percentage)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (student_name, grade_level, subject, total_questions, correct_answers, wrong_answers, percentage))
    conn.commit()
    conn.close()
    return True

def update_multiple_question_stats(student_name: str, grade_level: int, subject_data: list) -> bool:
    """Update stats for multiple subjects at once."""
    try:
        conn = sqlite3.connect("student_performance.db")
        cursor = conn.cursor()
        for subject, total, correct, wrong in subject_data:
            if correct + wrong > total:
                conn.close()
                return False
            if grade_level not in GRADE_SUBJECTS or subject not in GRADE_SUBJECTS[grade_level]:
                conn.close()
                return False
            percentage = 0.0
            if total > 0:
                percentage = (correct / total) * 100
            cursor.execute("""
                INSERT OR REPLACE INTO question_stats 
                (student_name, grade_level, subject, total_questions, correct_answers, wrong_answers, percentage)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (student_name, grade_level, subject, total, correct, wrong, percentage))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating multiple stats: {e}")
        if conn:
            conn.close()
        return False

def remove_student_data(student_name: str) -> bool:
    """Remove all data for a specific student."""
    try:
        conn = sqlite3.connect("student_performance.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM question_stats WHERE student_name=?", (student_name,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error removing student data: {e}")
        return False

def remove_student_subject_data(student_name: str, grade_level: int, subject: str) -> bool:
    """Remove data for a specific student, grade, and subject combination."""
    try:
        conn = sqlite3.connect("student_performance.db")
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM question_stats 
            WHERE student_name=? AND grade_level=? AND subject=?
        """, (student_name, grade_level, subject))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error removing student subject data: {e}")
        return False

def get_all_stats_df() -> pd.DataFrame:
    """Get all statistics as a pandas DataFrame."""
    conn = sqlite3.connect("student_performance.db")
    df = pd.read_sql_query("""
        SELECT student_name, grade_level, subject, total_questions, correct_answers, wrong_answers, percentage 
        FROM question_stats 
        ORDER BY student_name, grade_level, subject
    """, conn)
    conn.close()
    return df

def get_grade_stats_df(grade_level: int) -> pd.DataFrame:
    """Get statistics for a specific grade as a pandas DataFrame."""
    conn = sqlite3.connect("student_performance.db")
    df = pd.read_sql_query("""
        SELECT student_name, grade_level, subject, total_questions, correct_answers, wrong_answers, percentage 
        FROM question_stats 
        WHERE grade_level=?
        ORDER BY student_name, subject
    """, conn, params=(grade_level,))
    conn.close()
    return df

def get_student_stats_df(student_name: str) -> pd.DataFrame:
    """Get statistics for a specific student as a pandas DataFrame."""
    conn = sqlite3.connect("student_performance.db")
    df = pd.read_sql_query("""
        SELECT grade_level, subject, total_questions, correct_answers, wrong_answers, percentage 
        FROM question_stats 
        WHERE student_name=?
        ORDER BY grade_level, subject
    """, conn, params=(student_name,))
    conn.close()
    return df

def get_all_students() -> list:
    """Get list of all student names."""
    conn = sqlite3.connect("student_performance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT student_name FROM question_stats ORDER BY student_name")
    students = [row[0] for row in cursor.fetchall()]
    conn.close()
    return students

def get_student_subjects(student_name: str) -> list:
    """Get list of subjects for a specific student."""
    conn = sqlite3.connect("student_performance.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT grade_level, subject 
        FROM question_stats 
        WHERE student_name=?
        ORDER BY grade_level, subject
    """, (student_name,))
    subjects = [(row[0], row[1]) for row in cursor.fetchall()]
    conn.close()
    return subjects

# -------------------- VISUALIZATION --------------------
# (Visualization functions remain mostly the same, but student name is now used in titles)
def create_bar_chart(df: pd.DataFrame, title: str = "Performance by Subject"):
    """Create a bar chart showing percentages by subject."""
    if df.empty:
        return None
    fig, ax = plt.subplots(figsize=(10, 6))
    # Create labels
    if 'student_name' in df.columns and 'grade_level' in df.columns:
        labels = [f"{row.student_name} ({row.grade_level}-{row.subject})" for row in df.itertuples()]
    elif 'student_name' in df.columns:
        labels = [f"{row.student_name} ({row.subject})" for row in df.itertuples()]
    elif 'grade_level' in df.columns:
        labels = [f"{row.grade_level}-{row.subject}" for row in df.itertuples()]
    else:
        labels = df['subject'].tolist()
    percentages = df['percentage'].tolist()
    bars = ax.bar(range(len(labels)), percentages, color=plt.cm.viridis(np.linspace(0, 1, len(labels))))
    ax.set_xlabel('Students/Subjects')
    ax.set_ylabel('Percentage (%)')
    ax.set_title(title)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_ylim(0, 100)
    # Add percentage labels on bars
    for i, (bar, pct) in enumerate(zip(bars, percentages)):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{pct:.1f}%', ha='center', va='bottom', fontsize=9)
    plt.tight_layout()
    return fig

def create_heatmap(df: pd.DataFrame):
    """Create a heatmap showing performance across grades and subjects."""
    # Pivot the data for heatmap
    if not df.empty and 'grade_level' in df.columns:
        pivot_df = df.pivot(index='subject', columns='grade_level', values='percentage')
        pivot_df = pivot_df.fillna(0)
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(pivot_df, annot=True, cmap='RdYlGn', fmt='.1f', 
                   cbar_kws={'label': 'Percentage (%)'}, ax=ax)
        ax.set_title('Performance Heatmap by Grade and Subject')
        plt.tight_layout()
        return fig
    return None

def create_comparison_chart():
    """Create a comparison chart showing performance across all grades."""
    df = get_all_stats_df()
    if df.empty:
        return None
    fig, ax = plt.subplots(figsize=(12, 7))
    # Group by grade and calculate average performance
    grade_avg = df.groupby('grade_level')['percentage'].mean()
    bars = ax.bar([f'Grade {grade}' for grade in grade_avg.index], 
                  grade_avg.values, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    ax.set_xlabel('Grades')
    ax.set_ylabel('Average Percentage (%)')
    ax.set_title('Average Performance by Grade')
    ax.set_ylim(0, 100)
    # Add value labels on bars
    for bar, value in zip(bars, grade_avg.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{value:.1f}%', ha='center', va='bottom')
    plt.tight_layout()
    return fig

def create_student_performance_chart(student_name: str):
    """Create a performance chart for a specific student."""
    df = get_student_stats_df(student_name)
    if df.empty:
        return None
    fig, ax = plt.subplots(figsize=(10, 6))
    # Create labels with grade and subject
    labels = [f"{row.grade_level}-{row.subject}" for row in df.itertuples()]
    percentages = df['percentage'].tolist()
    bars = ax.bar(range(len(labels)), percentages, color=plt.cm.plasma(np.linspace(0, 1, len(labels))))
    ax.set_xlabel('Grade-Subject')
    ax.set_ylabel('Percentage (%)')
    ax.set_title(f'{student_name} - Performance by Subject') # <-- Student name in title
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_ylim(0, 100)
    # Add percentage labels on bars
    for i, (bar, pct) in enumerate(zip(bars, percentages)):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{pct:.1f}%', ha='center', va='bottom', fontsize=9)
    plt.tight_layout()
    return fig

def create_student_subject_breakdown(student_name: str):
    """Create a breakdown of performance by subject for a specific student."""
    df = get_student_stats_df(student_name)
    if df.empty:
        return None
    fig, ax = plt.subplots(figsize=(10, 6))
    subjects = df['subject'].tolist()
    correct = df['correct_answers'].tolist()
    wrong = df['wrong_answers'].tolist()
    x = np.arange(len(subjects))
    width = 0.35
    rects1 = ax.bar(x - width/2, correct, width, label='Correct', color='#4CAF50')
    rects2 = ax.bar(x + width/2, wrong, width, label='Wrong', color='#F44336')
    ax.set_xlabel('Subjects')
    ax.set_ylabel('Number of Questions')
    ax.set_title(f'{student_name} - Correct vs Wrong Answers by Subject') # <-- Student name in title
    ax.set_xticks(x)
    ax.set_xticklabels(subjects, rotation=45, ha='right')
    ax.legend()
    # Add value labels on bars
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)
    autolabel(rects1)
    autolabel(rects2)
    plt.tight_layout()
    return fig

# ------------------------------ UPDATED FUNCTION FOR PDF EXPORT ------------------------------
def export_student_to_pdf(student_name: str, output_path: str):
    """Export a student's data and plots to a PDF file."""
    try:
        df = get_student_stats_df(student_name)
        if df.empty:
            raise ValueError("No data found for the selected student.")

        # Create the PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Title
        title = Paragraph(f"Performance Report for {student_name}", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))

        # --- Add Student Data Table ---
        # Convert DataFrame to a list of lists for the table
        # Ensure column names match what's fetched (no student_name in df from get_student_stats_df)
        data = [df.columns.tolist()] + df.values.tolist()

        # Create the table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(Paragraph("Student Data:", styles['Heading2']))
        elements.append(Spacer(1, 6))
        elements.append(table)
        elements.append(Spacer(1, 24)) # Add space before charts

        # --- Add Charts ---
        # Generate charts
        fig1 = create_student_performance_chart(student_name)
        fig2 = create_student_subject_breakdown(student_name)

        # List of charts and their titles
        charts = [fig1, fig2]
        chart_titles = [f"{student_name} - Performance by Subject",
                        f"{student_name} - Correct vs Wrong Answers by Subject"]

        for i, fig in enumerate(charts):
            if fig:
                # Save the figure to a BytesIO object in memory
                img_buffer = io.BytesIO()
                # Save with high DPI for better quality in PDF
                fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
                img_buffer.seek(0) # Reset buffer pointer to the beginning

                # Create a ReportLab Image object from the buffer
                # You might need to adjust width/height based on your layout preference
                img = Image(img_buffer, width=450, height=250) # Adjust size as needed

                # Add chart title and image to the PDF elements
                elements.append(Paragraph(chart_titles[i], styles['Heading2']))
                elements.append(Spacer(1, 6))
                elements.append(img)
                elements.append(Spacer(1, 24)) # Add space after the chart

                # Important: Close the matplotlib figure to free up memory
                plt.close(fig)

        # Build the final PDF document
        doc.build(elements)
        return True
    except Exception as e:
        print(f"Error exporting to PDF: {e}")
        # Optionally, show an error message in the GUI here as well
        return False
# ---------------------------------------------------------------------------------------

# -------------------- GUI APPLICATION --------------------
class StudentPerformanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Performance Tracker")
        self.root.geometry("1200x800")
        init_db()
        self.setup_gui()

    def setup_gui(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        self.input_tab = ttk.Frame(self.notebook)
        self.view_tab = ttk.Frame(self.notebook)
        self.visual_tab = ttk.Frame(self.notebook)
        self.student_visual_tab = ttk.Frame(self.notebook)
        self.remove_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.input_tab, text="Data Input")
        self.notebook.add(self.view_tab, text="Data View")
        self.notebook.add(self.visual_tab, text="Visualizations")
        self.notebook.add(self.student_visual_tab, text="Student View")
        self.notebook.add(self.remove_tab, text="Remove Data")

        self.setup_input_tab()
        self.setup_view_tab()
        self.setup_visual_tab()
        self.setup_student_visual_tab()
        self.setup_remove_tab()

    # --- Modified Input Tab with Percentage Option ---
    def setup_input_tab(self):
        main_frame = ttk.Frame(self.input_tab)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        title_label = ttk.Label(main_frame, text="Add Student Performance Data (Table Input)", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))

        # Student selection frame
        student_frame = ttk.Frame(main_frame)
        student_frame.pack(fill=X, pady=(0, 10))
        ttk.Label(student_frame, text="Student Name:").pack(side=LEFT)
        # Create a frame for the combobox and entry
        name_input_frame = ttk.Frame(student_frame)
        name_input_frame.pack(side=LEFT, padx=(10, 0), fill=X, expand=True)
        # Get existing students for the combobox
        existing_students = get_all_students()
        self.student_name_var = StringVar()
        self.student_name_combo = ttk.Combobox(name_input_frame, textvariable=self.student_name_var,
                                             values=existing_students, width=30)
        self.student_name_combo.pack(side=LEFT, fill=X, expand=True)
        # Allow typing new names
        self.student_name_combo['state'] = 'normal' 

        # Grade selection
        grade_frame = ttk.Frame(main_frame)
        grade_frame.pack(fill=X, pady=(0, 20))
        ttk.Label(grade_frame, text="Grade Level:").pack(side=LEFT)
        self.grade_var = StringVar()
        grade_combo = ttk.Combobox(grade_frame, textvariable=self.grade_var, 
                                  values=[10, 11, 12], state="readonly", width=10)
        grade_combo.pack(side=LEFT, padx=(10, 0))
        grade_combo.bind('<<ComboboxSelected>>', self.load_subject_table)

        # Input Method Selection Frame
        method_frame = ttk.Frame(main_frame)
        method_frame.pack(fill=X, pady=(0, 10))
        ttk.Label(method_frame, text="Input Method:").pack(side=LEFT)
        self.input_method_var = StringVar(value="counts") # Default to counts
        ttk.Radiobutton(method_frame, text="Correct/Wrong Counts", variable=self.input_method_var, value="counts", command=self.load_subject_table).pack(side=LEFT, padx=(10, 0))
        ttk.Radiobutton(method_frame, text="Percentage", variable=self.input_method_var, value="percentage", command=self.load_subject_table).pack(side=LEFT, padx=(10, 0))

        # Table frame for subjects
        self.table_frame = ttk.Frame(main_frame)
        self.table_frame.pack(fill=BOTH, expand=True, pady=(0, 20))

        # Placeholder for table
        self.subject_entries = {}
        self.subject_vars = {} # Store variables for entries

        # Submit button
        submit_btn = ttk.Button(main_frame, text="Submit All Data for Grade", command=self.submit_table_data)
        submit_btn.pack(pady=10)

        # Status label
        self.status_label = ttk.Label(main_frame, text="", foreground="green")
        self.status_label.pack()

    def load_subject_table(self, event=None):
        """Load the table for entering subject data based on selected grade and input method."""
        # Clear existing table
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.subject_entries = {}
        self.subject_vars = {}
        grade = self.grade_var.get()
        input_method = self.input_method_var.get() # Get selected input method

        if not grade or int(grade) not in GRADE_SUBJECTS:
            return

        subjects = GRADE_SUBJECTS[int(grade)]

        # Create table header based on input method
        header_frame = ttk.Frame(self.table_frame)
        header_frame.pack(fill=X, pady=2)
        ttk.Label(header_frame, text="Subject", width=20).pack(side=LEFT, padx=5)
        
        if input_method == "counts":
            ttk.Label(header_frame, text="Total Questions", width=15).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Correct Answers", width=15).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Wrong Answers", width=15).pack(side=LEFT, padx=5)
        elif input_method == "percentage":
            ttk.Label(header_frame, text="Total Questions", width=15).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Percentage (%)", width=15).pack(side=LEFT, padx=5)
            # Add a placeholder label to keep column alignment consistent
            ttk.Label(header_frame, text="", width=15).pack(side=LEFT, padx=5) 

        # Create rows for each subject
        for subject in subjects:
            row_frame = ttk.Frame(self.table_frame)
            row_frame.pack(fill=X, pady=2)
            ttk.Label(row_frame, text=subject, width=20).pack(side=LEFT, padx=5)

            # Store variables for each entry
            total_var = StringVar()
            entry1_var = StringVar() # Will be correct or percentage
            entry2_var = StringVar() # Will be wrong or empty
            
            self.subject_vars[subject] = {
                'total': total_var,
                'entry1': entry1_var, # Correct or Percentage
                'entry2': entry2_var  # Wrong or Empty
            }

            total_entry = ttk.Entry(row_frame, textvariable=total_var, width=15)
            
            if input_method == "counts":
                entry1_entry = ttk.Entry(row_frame, textvariable=entry1_var, width=15) # Correct
                entry2_entry = ttk.Entry(row_frame, textvariable=entry2_var, width=15) # Wrong
            elif input_method == "percentage":
                entry1_entry = ttk.Entry(row_frame, textvariable=entry1_var, width=15) # Percentage
                entry2_entry = ttk.Label(row_frame, text="-", width=15) # Placeholder for wrong answers

            total_entry.pack(side=LEFT, padx=5)
            entry1_entry.pack(side=LEFT, padx=5)
            entry2_entry.pack(side=LEFT, padx=5)

            self.subject_entries[subject] = {
                'total': total_entry,
                'entry1': entry1_entry, # Correct or Percentage
                'entry2': entry2_entry  # Wrong or Label
            }

    def submit_table_data(self):
        """Submit all data from the table."""
        try:
            student_name = self.student_name_var.get().strip()
            if not student_name:
                messagebox.showerror("Error", "Please enter or select a student name")
                return
            grade = self.grade_var.get()
            input_method = self.input_method_var.get() # Get selected input method
            if not grade or int(grade) not in GRADE_SUBJECTS:
                messagebox.showerror("Error", "Please select a valid grade level")
                return
            grade_level = int(grade)
            subjects = GRADE_SUBJECTS[grade_level]
            subject_data_list = []
            
            for subject in subjects:
                total_str = self.subject_vars[subject]['total'].get()
                entry1_str = self.subject_vars[subject]['entry1'].get() # Correct or Percentage
                entry2_str = self.subject_vars[subject]['entry2'].get() # Wrong or Empty
                
                # Handle empty fields as 0
                total = int(total_str) if total_str.isdigit() else 0
                
                if input_method == "counts":
                    correct = int(entry1_str) if entry1_str.isdigit() else 0
                    wrong = int(entry2_str) if entry2_str.isdigit() else 0
                    # Basic validation
                    if correct + wrong > total:
                        messagebox.showerror("Error", f"For {subject}, Correct + Wrong cannot exceed Total.")
                        return
                elif input_method == "percentage":
                    try:
                        percentage = float(entry1_str) if entry1_str else 0.0
                        if not (0 <= percentage <= 100):
                            messagebox.showerror("Error", f"For {subject}, Percentage must be between 0 and 100.")
                            return
                        # Calculate correct/wrong from percentage and total
                        correct = round(total * percentage / 100)
                        wrong = total - correct
                        # Ensure rounding doesn't cause sum to exceed total
                        if correct + wrong > total:
                            correct = total
                            wrong = 0
                    except ValueError:
                        messagebox.showerror("Error", f"For {subject}, Please enter a valid number for Percentage.")
                        return
                
                subject_data_list.append((subject, total, correct, wrong))

            if update_multiple_question_stats(student_name, grade_level, subject_data_list):
                self.status_label.config(text=f"Data for Grade {grade_level} submitted successfully for {student_name}!", foreground="green")
                # Refresh student lists in other tabs
                self.update_student_lists()
                self.refresh_data_view() # Refresh data view
            else:
                messagebox.showerror("Error", "Failed to submit data. Check for errors (e.g., correct+wrong > total).")
        except ValueError:
             messagebox.showerror("Error", "Please enter valid numbers in all fields")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    # --- Other tab setups remain mostly the same ---
    def setup_view_tab(self):
        main_frame = ttk.Frame(self.view_tab)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        title_label = ttk.Label(main_frame, text="View Performance Data", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))

        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=X, pady=(0, 20))
        ttk.Button(controls_frame, text="Refresh Data", command=self.refresh_data_view).pack(side=LEFT)
        ttk.Button(controls_frame, text="Export to CSV", command=self.export_to_csv).pack(side=LEFT, padx=(10, 0))
        # ------------------------------ NEW BUTTON FOR PDF EXPORT ------------------------------
        ttk.Button(controls_frame, text="Export to PDF", command=self.export_to_pdf).pack(side=LEFT, padx=(10, 0))
        # ---------------------------------------------------------------------------------------

        grade_filter_frame = ttk.Frame(controls_frame)
        grade_filter_frame.pack(side=RIGHT)
        ttk.Label(grade_filter_frame, text="Filter by Grade:").pack(side=LEFT)
        self.grade_filter_var = StringVar()
        grade_filter_combo = ttk.Combobox(grade_filter_frame, textvariable=self.grade_filter_var,
                                         values=['All', 10, 11, 12], state="readonly", width=10)
        grade_filter_combo.pack(side=LEFT, padx=(10, 0))
        grade_filter_combo.set('All')
        grade_filter_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_data_view())

        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=BOTH, expand=True)

        v_scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=HORIZONTAL)

        self.data_tree = ttk.Treeview(tree_frame, columns=('Student', 'Grade', 'Subject', 'Total', 'Correct', 'Wrong', 'Percentage'),
                                     show='headings', yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        v_scrollbar.config(command=self.data_tree.yview)
        h_scrollbar.config(command=self.data_tree.xview)
        v_scrollbar.pack(side=RIGHT, fill=Y)
        h_scrollbar.pack(side=BOTTOM, fill=X)
        self.data_tree.pack(fill=BOTH, expand=True)

        self.data_tree.heading('Student', text='Student Name')
        self.data_tree.heading('Grade', text='Grade Level')
        self.data_tree.heading('Subject', text='Subject')
        self.data_tree.heading('Total', text='Total Questions')
        self.data_tree.heading('Correct', text='Correct Answers')
        self.data_tree.heading('Wrong', text='Wrong Answers')
        self.data_tree.heading('Percentage', text='Percentage (%)')

        self.data_tree.column('Student', width=120)
        self.data_tree.column('Grade', width=80)
        self.data_tree.column('Subject', width=120)
        self.data_tree.column('Total', width=100)
        self.data_tree.column('Correct', width=100)
        self.data_tree.column('Wrong', width=100)
        self.data_tree.column('Percentage', width=100)

        self.refresh_data_view()

    def refresh_data_view(self):
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        filter_grade = self.grade_filter_var.get()
        if filter_grade == 'All':
            df = get_all_stats_df()
        else:
            df = get_grade_stats_df(int(filter_grade))
        if not df.empty:
            for _, row in df.iterrows():
                self.data_tree.insert('', 'end', values=(
                    row['student_name'],
                    row['grade_level'],
                    row['subject'],
                    row['total_questions'],
                    row['correct_answers'],
                    row['wrong_answers'],
                    f"{row['percentage']:.2f}"
                ))

    def export_to_csv(self):
        try:
            df = get_all_stats_df()
            if df.empty:
                messagebox.showinfo("Info", "No data to export")
                return
            filename = "student_performance_data.csv"
            df.to_csv(filename, index=False)
            messagebox.showinfo("Success", f"Data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")

    # ------------------------------ NEW FUNCTION FOR PDF EXPORT ------------------------------
    def export_to_pdf(self):
        try:
            df = get_all_stats_df()
            if df.empty:
                messagebox.showinfo("Info", "No data to export")
                return
            filename = "student_performance_data.pdf"
            # Note: This exports all data. If you want to filter by grade like CSV,
            # you would need to modify this logic similarly.
            
            # Create the PDF document
            doc = SimpleDocTemplate(filename, pagesize=letter) # Changed to portrait for better table fit
            elements = []
            styles = getSampleStyleSheet()

            # Title
            title = Paragraph("Student Performance Data Report", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 12))

            # Convert DataFrame to a list of lists for the table
            data = [df.columns.tolist()] + df.values.tolist()

            # Create the table
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 8) # Smaller font for better fit
            ]))

            elements.append(table)
            doc.build(elements)
            messagebox.showinfo("Success", f"Data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data to PDF: {str(e)}")
    # ---------------------------------------------------------------------------------------

    def setup_visual_tab(self):
        main_frame = ttk.Frame(self.visual_tab)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        title_label = ttk.Label(main_frame, text="Performance Visualizations", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))

        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=X, pady=(0, 20))
        ttk.Button(controls_frame, text="Generate All Charts", command=self.generate_all_charts).pack(side=LEFT)
        ttk.Button(controls_frame, text="Clear Charts", command=self.clear_charts).pack(side=LEFT, padx=(10, 0))

        chart_type_frame = ttk.Frame(controls_frame)
        chart_type_frame.pack(side=RIGHT)
        ttk.Label(chart_type_frame, text="Chart Type:").pack(side=LEFT)
        self.chart_type_var = StringVar(value="all")
        chart_type_combo = ttk.Combobox(chart_type_frame, textvariable=self.chart_type_var,
                                       values=['All Charts', 'Bar Chart', 'Heatmap', 'Comparison'], 
                                       state="readonly", width=15)
        chart_type_combo.pack(side=LEFT, padx=(10, 0))

        self.chart_canvas_frame = ttk.Frame(main_frame)
        self.chart_canvas_frame.pack(fill=BOTH, expand=True)

        self.chart_canvas = Canvas(self.chart_canvas_frame)
        scrollbar = ttk.Scrollbar(self.chart_canvas_frame, orient=VERTICAL, command=self.chart_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.chart_canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.chart_canvas.configure(scrollregion=self.chart_canvas.bbox("all"))
        )

        self.chart_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.chart_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=RIGHT, fill=Y)
        self.chart_canvas.pack(side=LEFT, fill=BOTH, expand=True)

    def generate_all_charts(self):
        self.clear_charts()
        df = get_all_stats_df()
        if df.empty:
            ttk.Label(self.scrollable_frame, text="No data available for visualization").pack(pady=20)
            return

        selected_chart = self.chart_type_var.get()
        charts_to_generate = []
        if selected_chart == 'All Charts' or selected_chart == 'Bar Chart':
            charts_to_generate.append(('bar', "Performance by Subject"))
        if selected_chart == 'All Charts' or selected_chart == 'Heatmap':
            charts_to_generate.append(('heatmap', "Performance Heatmap"))
        if selected_chart == 'All Charts' or selected_chart == 'Comparison':
            charts_to_generate.append(('comparison', "Grade Comparison"))

        for chart_type, title in charts_to_generate:
            try:
                if chart_type == 'bar':
                    fig = create_bar_chart(df, title)
                elif chart_type == 'heatmap':
                    fig = create_heatmap(df)
                    if fig is None:
                        continue
                elif chart_type == 'comparison':
                    fig = create_comparison_chart()
                    if fig is None:
                        continue
                if fig:
                    chart_frame = ttk.Frame(self.scrollable_frame)
                    chart_frame.pack(fill=BOTH, expand=True, pady=10)
                    canvas = FigureCanvasTkAgg(fig, chart_frame)
                    canvas.draw()
                    canvas.get_tk_widget().pack(fill=BOTH, expand=True)
            except Exception as e:
                error_label = ttk.Label(self.scrollable_frame, 
                                      text=f"Error generating {title}: {str(e)}", 
                                      foreground="red")
                error_label.pack(pady=10)

    def clear_charts(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    # --- Modified Student View Tab ---
    def setup_student_visual_tab(self):
        main_frame = ttk.Frame(self.student_visual_tab)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        title_label = ttk.Label(main_frame, text="Student Performance Visualizations", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))

        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=X, pady=(0, 20))
        ttk.Button(controls_frame, text="Generate Student Charts", command=self.generate_student_charts).pack(side=LEFT)
        ttk.Button(controls_frame, text="Clear Charts", command=self.clear_student_charts).pack(side=LEFT, padx=(10, 0))
        # ------------------------------ NEW BUTTON FOR PDF EXPORT ------------------------------
        ttk.Button(controls_frame, text="Export Student PDF", command=self.export_student_pdf).pack(side=LEFT, padx=(10, 0))
        # ---------------------------------------------------------------------------------------

        # Student selection with scrollable list
        student_frame = ttk.Frame(controls_frame)
        student_frame.pack(side=RIGHT)
        ttk.Label(student_frame, text="Select Student:").pack(side=LEFT)
        self.student_var = StringVar()
        # Create a frame for the combobox
        combo_frame = ttk.Frame(student_frame)
        combo_frame.pack(side=LEFT, padx=(10, 0))
        self.student_combo = ttk.Combobox(combo_frame, textvariable=self.student_var,
                                         state="readonly", width=25) # Increased width
        # Add scrollbar to combobox using a hack (ttk.Combobox doesn't directly support it)
        # The dropdown list itself will be scrollable if there are many items
        self.student_combo.pack()
        self.update_student_list()

        self.student_chart_canvas_frame = ttk.Frame(main_frame)
        self.student_chart_canvas_frame.pack(fill=BOTH, expand=True)

        self.student_chart_canvas = Canvas(self.student_chart_canvas_frame)
        student_scrollbar = ttk.Scrollbar(self.student_chart_canvas_frame, orient=VERTICAL, command=self.student_chart_canvas.yview)
        self.student_scrollable_frame = ttk.Frame(self.student_chart_canvas)

        self.student_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.student_chart_canvas.configure(scrollregion=self.student_chart_canvas.bbox("all"))
        )

        self.student_chart_canvas.create_window((0, 0), window=self.student_scrollable_frame, anchor="nw")
        self.student_chart_canvas.configure(yscrollcommand=student_scrollbar.set)

        student_scrollbar.pack(side=RIGHT, fill=Y)
        self.student_chart_canvas.pack(side=LEFT, fill=BOTH, expand=True)

    def update_student_list(self):
        students = get_all_students()
        self.student_combo['values'] = students
        if students:
            self.student_combo.set(students[0])

    def update_student_lists(self):
        """Update student lists in all relevant tabs."""
        students = get_all_students()
        self.student_combo['values'] = students
        self.student_name_combo['values'] = students # Update input tab combobox
        self.update_remove_student_list() # Update remove tab comboboxes

    def generate_student_charts(self):
        self.clear_student_charts()
        student_name = self.student_var.get()
        if not student_name:
            ttk.Label(self.student_scrollable_frame, text="Please select a student").pack(pady=20)
            return

        df = get_student_stats_df(student_name)
        if df.empty:
            ttk.Label(self.student_scrollable_frame, text=f"No data available for {student_name}").pack(pady=20)
            return

        try:
            # Performance by subject chart - Title now includes student name
            fig1 = create_student_performance_chart(student_name)
            if fig1:
                chart_frame1 = ttk.Frame(self.student_scrollable_frame)
                chart_frame1.pack(fill=BOTH, expand=True, pady=10)
                canvas1 = FigureCanvasTkAgg(fig1, chart_frame1)
                canvas1.draw()
                canvas1.get_tk_widget().pack(fill=BOTH, expand=True)

            # Subject breakdown chart - Title now includes student name
            fig2 = create_student_subject_breakdown(student_name)
            if fig2:
                chart_frame2 = ttk.Frame(self.student_scrollable_frame)
                chart_frame2.pack(fill=BOTH, expand=True, pady=10)
                canvas2 = FigureCanvasTkAgg(fig2, chart_frame2)
                canvas2.draw()
                canvas2.get_tk_widget().pack(fill=BOTH, expand=True)
        except Exception as e:
            error_label = ttk.Label(self.student_scrollable_frame, 
                                  text=f"Error generating charts: {str(e)}", 
                                  foreground="red")
            error_label.pack(pady=10)

    def clear_student_charts(self):
        for widget in self.student_scrollable_frame.winfo_children():
            widget.destroy()

    # ------------------------------ NEW FUNCTION FOR STUDENT PDF EXPORT ------------------------------
    def export_student_pdf(self):
        student_name = self.student_var.get()
        if not student_name:
            messagebox.showerror("Error", "Please select a student first.")
            return

        # Ask user for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title="Save PDF Report As",
            initialfile=f"{student_name}_performance_report.pdf"
        )

        if filename: # If user didn't cancel the dialog
            if export_student_to_pdf(student_name, filename):
                 messagebox.showinfo("Success", f"PDF report for {student_name} exported to:\n{filename}")
            else:
                 messagebox.showerror("Error", f"Failed to export PDF for {student_name}")
    # ---------------------------------------------------------------------------------------

    def setup_remove_tab(self):
        main_frame = ttk.Frame(self.remove_tab)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        title_label = ttk.Label(main_frame, text="Remove Student Data", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))

        remove_student_frame = ttk.LabelFrame(main_frame, text="Remove All Data for Student", padding=10)
        remove_student_frame.pack(fill=X, pady=(0, 20))

        student_remove_frame = ttk.Frame(remove_student_frame)
        student_remove_frame.pack(fill=X, pady=5)
        ttk.Label(student_remove_frame, text="Select Student:").pack(side=LEFT)
        self.remove_student_var = StringVar()
        self.remove_student_combo = ttk.Combobox(student_remove_frame, textvariable=self.remove_student_var,
                                               state="readonly", width=25) # Increased width
        self.remove_student_combo.pack(side=LEFT, padx=(10, 0))
        ttk.Button(remove_student_frame, text="Remove Student Data", 
                  command=self.remove_student).pack(pady=10)

        remove_subject_frame = ttk.LabelFrame(main_frame, text="Remove Specific Subject Data", padding=10)
        remove_subject_frame.pack(fill=X, pady=(0, 20))

        subject_student_frame = ttk.Frame(remove_subject_frame)
        subject_student_frame.pack(fill=X, pady=5)
        ttk.Label(subject_student_frame, text="Select Student:").pack(side=LEFT)
        self.remove_subject_student_var = StringVar()
        self.remove_subject_student_combo = ttk.Combobox(subject_student_frame, 
                                                       textvariable=self.remove_subject_student_var,
                                                       state="readonly", width=25)
        self.remove_subject_student_combo.pack(side=LEFT, padx=(10, 0))
        self.remove_subject_student_combo.bind('<<ComboboxSelected>>', self.update_remove_subjects)

        subject_select_frame = ttk.Frame(remove_subject_frame)
        subject_select_frame.pack(fill=X, pady=5)
        ttk.Label(subject_select_frame, text="Select Subject:").pack(side=LEFT)
        self.remove_subject_var = StringVar()
        self.remove_subject_combo = ttk.Combobox(subject_select_frame, 
                                               textvariable=self.remove_subject_var,
                                               state="readonly", width=25)
        self.remove_subject_combo.pack(side=LEFT, padx=(10, 0))

        ttk.Button(remove_subject_frame, text="Remove Subject Data", 
                  command=self.remove_student_subject).pack(pady=10)

        self.remove_status_label = ttk.Label(main_frame, text="", foreground="green")
        self.remove_status_label.pack()

        self.update_remove_student_list()

    def update_remove_student_list(self):
        students = get_all_students()
        if students:
            self.remove_student_combo['values'] = students
            self.remove_subject_student_combo['values'] = students
            self.remove_student_combo.set(students[0])
            self.remove_subject_student_combo.set(students[0])
            self.update_remove_subjects()
        else:
            self.remove_student_combo['values'] = []
            self.remove_subject_student_combo['values'] = []
            self.remove_subject_combo['values'] = []
            self.remove_student_var.set('')
            self.remove_subject_student_var.set('')
            self.remove_subject_var.set('')

    def update_remove_subjects(self, event=None):
        student_name = self.remove_subject_student_var.get()
        if student_name:
            subjects = get_student_subjects(student_name)
            subject_list = [f"Grade {grade} - {subject}" for grade, subject in subjects]
            self.remove_subject_combo['values'] = subject_list
            if subject_list:
                self.remove_subject_combo.set(subject_list[0])

    def remove_student(self):
        student_name = self.remove_student_var.get()
        if not student_name:
            messagebox.showerror("Error", "Please select a student")
            return
        if messagebox.askyesno("Confirm Removal", 
                              f"Are you sure you want to remove all data for {student_name}? This cannot be undone."):
            if remove_student_data(student_name):
                self.remove_status_label.config(text=f"Successfully removed all data for {student_name}", 
                                              foreground="green")
                self.update_student_lists() # Refresh all student lists
                self.refresh_data_view()
            else:
                messagebox.showerror("Error", "Failed to remove student data")

    def remove_student_subject(self):
        student_name = self.remove_subject_student_var.get()
        subject_info = self.remove_subject_var.get()
        if not student_name or not subject_info:
            messagebox.showerror("Error", "Please select both student and subject")
            return
        try:
            parts = subject_info.split(" - ")
            grade_level = int(parts[0].replace("Grade ", ""))
            subject = parts[1]
        except:
            messagebox.showerror("Error", "Invalid subject selection")
            return
        if messagebox.askyesno("Confirm Removal", 
                              f"Are you sure you want to remove {subject} data for {student_name} in Grade {grade_level}?"):
            if remove_student_subject_data(student_name, grade_level, subject):
                self.remove_status_label.config(text=f"Successfully removed {subject} data for {student_name}", 
                                              foreground="green")
                self.update_student_lists() # Refresh all student lists
                self.refresh_data_view()
            else:
                messagebox.showerror("Error", "Failed to remove student subject data")

# -------------------- MAIN EXECUTION --------------------
if __name__ == "__main__":
    root = Tk()
    app = StudentPerformanceApp(root)
    root.mainloop()