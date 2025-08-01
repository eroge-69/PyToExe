import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import os
import random

class TimetableGenerator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("School Timetable Generator")
        self.root.geometry("1200x800")
        self.root.configure(bg='white')
        
        # Data storage
        self.school_data = {}
        self.classes_data = []
        self.teachers_data = []
        self.subjects_data = {}
        self.timetables = {}
        self.stream_data = {}  # Store stream information for classes 11-12
        
        # Board curricula with stream-based subjects for 11-12
        self.board_subjects = {
            "CBSE": {
                1: ["English", "Hindi", "Mathematics", "EVS", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                2: ["English", "Hindi", "Mathematics", "EVS", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                3: ["English", "Hindi", "Mathematics", "EVS", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                4: ["English", "Hindi", "Mathematics", "EVS", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                5: ["English", "Hindi", "Mathematics", "EVS", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                6: ["English", "Hindi", "Mathematics", "Science", "Social Science", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                7: ["English", "Hindi", "Mathematics", "Science", "Social Science", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                8: ["English", "Hindi", "Mathematics", "Science", "Social Science", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                9: ["English", "Hindi", "Mathematics", "Science", "Social Science", "Physical Education", "Computer Science", "REGIONAL_LANGUAGE"],
                10: ["English", "Hindi", "Mathematics", "Science", "Social Science", "Physical Education", "Computer Science", "REGIONAL_LANGUAGE"],
                # Classes 11-12 will be populated based on stream selection
            },
            "ICSE": {
                1: ["English", "Hindi", "Mathematics", "EVS", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                2: ["English", "Hindi", "Mathematics", "EVS", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                3: ["English", "Hindi", "Mathematics", "EVS", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                4: ["English", "Hindi", "Mathematics", "EVS", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                5: ["English", "Hindi", "Mathematics", "EVS", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                6: ["English", "Hindi", "Mathematics", "Science", "History", "Geography", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                7: ["English", "Hindi", "Mathematics", "Science", "History", "Geography", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                8: ["English", "Hindi", "Mathematics", "Science", "History", "Geography", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                9: ["English", "Hindi", "Mathematics", "Physics", "Chemistry", "Biology", "History", "Geography", "Computer Applications", "REGIONAL_LANGUAGE"],
                10: ["English", "Hindi", "Mathematics", "Physics", "Chemistry", "Biology", "History", "Geography", "Computer Applications", "REGIONAL_LANGUAGE"],
            },
            "State Board": {
                1: ["English", "Regional Language", "Mathematics", "EVS", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                2: ["English", "Regional Language", "Mathematics", "EVS", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                3: ["English", "Regional Language", "Mathematics", "EVS", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                4: ["English", "Regional Language", "Mathematics", "EVS", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                5: ["English", "Regional Language", "Mathematics", "EVS", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                6: ["English", "Regional Language", "Mathematics", "Science", "Social Science", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                7: ["English", "Regional Language", "Mathematics", "Science", "Social Science", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                8: ["English", "Regional Language", "Mathematics", "Science", "Social Science", "Art", "Physical Education", "REGIONAL_LANGUAGE"],
                9: ["English", "Regional Language", "Mathematics", "Science", "Social Science", "Physical Education", "REGIONAL_LANGUAGE"],
                10: ["English", "Regional Language", "Mathematics", "Science", "Social Science", "Physical Education", "REGIONAL_LANGUAGE"],
            }
        }

        # Stream-based subjects for classes 11-12
        self.stream_subjects = {
            "Science": {
                "core": ["English", "Physics", "Chemistry", "Mathematics", "REGIONAL_LANGUAGE"],
                "optional": ["Biology", "Computer Science", "Physical Education"],
                "labs": ["Physics Lab", "Chemistry Lab", "Biology Lab", "Computer Lab"]
            },
            "Commerce": {
                "core": ["English", "Accountancy", "Business Studies", "Economics", "REGIONAL_LANGUAGE"],
                "optional": ["Mathematics", "Computer Science", "Physical Education", "Entrepreneurship"],
                "labs": ["Computer Lab", "Business Lab"]
            },
            "Arts/Humanities": {
                "core": ["English", "History", "Political Science", "Geography", "REGIONAL_LANGUAGE"],
                "optional": ["Psychology", "Sociology", "Economics", "Philosophy", "Physical Education"],
                "labs": ["Computer Lab", "Geography Lab"]
            }
        }

        # Add ECA and lab data storage
        self.eca_data = {}
        self.lab_data = {}
        self.extra_class_data = {}
        
        self.current_frame = None
        self.create_main_menu()
        
    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
            
    def create_main_menu(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg='white')
        self.current_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        title = tk.Label(self.current_frame, text="SCHOOL TIMETABLE GENERATOR", 
                        font=('Arial', 20, 'bold'), bg='white')
        title.pack(pady=20)
        
        buttons_frame = tk.Frame(self.current_frame, bg='white')
        buttons_frame.pack(expand=True)
        
        buttons = [
            ("School Details", self.school_details_screen),
            ("Class Details", self.class_details_screen),
            ("Subject Details", self.subject_details_screen),
            ("Teacher Details", self.teacher_details_screen),
            ("Generate Timetable", self.generate_timetable_screen),
            ("Export Timetable", self.export_timetable_screen)
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(buttons_frame, text=text, command=command,
                          font=('Arial', 12), width=20, height=2,
                          bg='lightblue', relief='raised', bd=2)
            btn.pack(pady=10)
    
    def school_details_screen(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg='white')
        self.current_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(self.current_frame, text="TIME TABLE GENERATOR", 
                        font=('Arial', 16, 'bold'), bg='white')
        title.pack(pady=10)
        
        # Main form frame
        form_frame = tk.Frame(self.current_frame, bg='white', relief='solid', bd=2)
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # School name and board
        top_frame = tk.Frame(form_frame, bg='white')
        top_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(top_frame, text="ENTER SCHOOL NAME:", bg='white', font=('Arial', 10)).grid(row=0, column=0, sticky='w', padx=5)
        tk.Label(top_frame, text="(Enter the full name of your school)", bg='white', font=('Arial', 8), fg='gray').grid(row=0, column=2, sticky='w', padx=5)
        self.school_name_entry = tk.Entry(top_frame, width=30, font=('Arial', 10))
        self.school_name_entry.grid(row=0, column=1, padx=10)
        
        tk.Label(top_frame, text="SELECT BOARD:", bg='white', font=('Arial', 10)).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        tk.Label(top_frame, text="(Choose your school's curriculum board)", bg='white', font=('Arial', 8), fg='gray').grid(row=1, column=2, sticky='w', padx=5)
        self.board_var = tk.StringVar()
        board_combo = ttk.Combobox(top_frame, textvariable=self.board_var, values=list(self.board_subjects.keys()), 
                                  width=27, font=('Arial', 10))
        board_combo.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(top_frame, text="SELECT REGION:", bg='white', font=('Arial', 10)).grid(row=2, column=0, sticky='w', padx=5, pady=5)
        tk.Label(top_frame, text="(Select your state/region for regional language)", bg='white', font=('Arial', 8), fg='gray').grid(row=2, column=2, sticky='w', padx=5)
        self.region_var = tk.StringVar()
        region_combo = ttk.Combobox(top_frame, textvariable=self.region_var, 
                                   values=["Tamil Nadu", "Karnataka", "Kerala", "Andhra Pradesh", "Telangana", "Maharashtra", "Gujarat", "Rajasthan", "Punjab", "Haryana", "Uttar Pradesh", "Bihar", "West Bengal", "Odisha", "Jharkhand", "Chhattisgarh", "Madhya Pradesh", "Assam", "Other"], 
                                   width=27, font=('Arial', 10))
        region_combo.grid(row=2, column=1, padx=10, pady=5)
        
        # Update timings frame to include senior secondary
        timings_frame = tk.Frame(form_frame, bg='white')
        timings_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Primary, Secondary, and Senior Secondary columns
        primary_frame = tk.LabelFrame(timings_frame, text="PRIMARY CLASS TIMINGS:", bg='white', font=('Arial', 10, 'bold'))
        primary_frame.pack(side='left', fill='both', expand=True, padx=5)

        secondary_frame = tk.LabelFrame(timings_frame, text="SECONDARY CLASS TIMINGS:", bg='white', font=('Arial', 10, 'bold'))
        secondary_frame.pack(side='left', fill='both', expand=True, padx=5)

        senior_secondary_frame = tk.LabelFrame(timings_frame, text="SENIOR SECONDARY CLASS TIMINGS:", bg='white', font=('Arial', 10, 'bold'))
        senior_secondary_frame.pack(side='left', fill='both', expand=True, padx=5)

        # Create timing fields for all three sections
        self.create_timing_fields(primary_frame, 'primary')
        self.create_timing_fields(secondary_frame, 'secondary')
        self.create_timing_fields(senior_secondary_frame, 'senior_secondary')
        
        # Working days
        days_frame = tk.LabelFrame(form_frame, text="SELECT WORKING DAYS:", bg='white', font=('Arial', 10, 'bold'))
        days_frame.pack(fill='x', padx=20, pady=10)
        
        days_inner = tk.Frame(days_frame, bg='white')
        days_inner.pack(pady=10)
        
        tk.Label(days_inner, text="(Select the days your school operates)", bg='white', font=('Arial', 8), fg='gray').pack()
        
        self.working_days = {}
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        days_checkboxes = tk.Frame(days_inner, bg='white')
        days_checkboxes.pack(pady=5)
        
        for i, day in enumerate(days):
            var = tk.BooleanVar()
            self.working_days[day] = var
            cb = tk.Checkbutton(days_checkboxes, text=day, variable=var, bg='white', font=('Arial', 10))
            cb.grid(row=0, column=i, padx=10)
        
        # Buttons
        btn_frame = tk.Frame(self.current_frame, bg='white')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Save & Continue", command=self.save_school_details,
                 font=('Arial', 12), bg='lightgreen', width=15).pack(side='left', padx=10)
        tk.Button(btn_frame, text="Back to Menu", command=self.create_main_menu,
                 font=('Arial', 12), bg='lightcoral', width=15).pack(side='left', padx=10)
    
    def create_timing_fields(self, parent, level):
        fields = {}
        
        # School start timing
        tk.Label(parent, text="School start timing:", bg='white', font=('Arial', 9)).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        tk.Label(parent, text="(e.g., 9:00)", bg='white', font=('Arial', 7), fg='gray').grid(row=0, column=2, sticky='w', padx=2)
        fields['start_time'] = tk.Entry(parent, width=15, font=('Arial', 9))
        fields['start_time'].grid(row=0, column=1, padx=5, pady=2)
        
        # Prayer timing
        tk.Label(parent, text="Prayer timing:", bg='white', font=('Arial', 9)).grid(row=1, column=0, sticky='w', padx=5, pady=2)
        tk.Label(parent, text="(e.g., 8:45)", bg='white', font=('Arial', 7), fg='gray').grid(row=1, column=2, sticky='w', padx=2)
        fields['prayer_time'] = tk.Entry(parent, width=15, font=('Arial', 9))
        fields['prayer_time'].grid(row=1, column=1, padx=5, pady=2)
        
        # Duration of period
        tk.Label(parent, text="Duration of period:", bg='white', font=('Arial', 9)).grid(row=2, column=0, sticky='w', padx=5, pady=2)
        fields['period_duration'] = tk.Entry(parent, width=15, font=('Arial', 9))
        fields['period_duration'].grid(row=2, column=1, padx=5, pady=2)
        tk.Label(parent, text="(in min, e.g., 40)", bg='white', font=('Arial', 7), fg='gray').grid(row=2, column=2, sticky='w', padx=2)
        
        # Dispersal time
        tk.Label(parent, text="Dispersal Time:", bg='white', font=('Arial', 9)).grid(row=3, column=0, sticky='w', padx=5, pady=2)
        tk.Label(parent, text="(e.g., 15:30)", bg='white', font=('Arial', 7), fg='gray').grid(row=3, column=2, sticky='w', padx=2)
        fields['dispersal_time'] = tk.Entry(parent, width=15, font=('Arial', 9))
        fields['dispersal_time'].grid(row=3, column=1, padx=5, pady=2)
        
        # Extra class checkbox for senior secondary only
        if level == 'senior_secondary':
            fields['extra_class_var'] = tk.BooleanVar()
            extra_class_cb = tk.Checkbutton(parent, text="Extra Class", variable=fields['extra_class_var'],
                                          bg='white', font=('Arial', 9), 
                                          command=lambda: self.toggle_extra_class_timing(level))
            extra_class_cb.grid(row=4, column=0, columnspan=3, pady=5)
            
            # Extra class timing (initially hidden)
            fields['extra_class_frame'] = tk.Frame(parent, bg='white')
            fields['extra_class_frame'].grid(row=5, column=0, columnspan=3, sticky='ew', padx=5, pady=5)
            fields['extra_class_frame'].grid_remove()  # Hide initially
            
            tk.Label(fields['extra_class_frame'], text="Extra Class Timing:", bg='white', font=('Arial', 8)).grid(row=0, column=0, sticky='w', padx=2)
            tk.Label(fields['extra_class_frame'], text="(e.g., 16:00-17:00)", bg='white', font=('Arial', 7), fg='gray').grid(row=1, column=0, padx=2)
            fields['extra_class_timing'] = tk.Entry(fields['extra_class_frame'], width=15, font=('Arial', 8))
            fields['extra_class_timing'].grid(row=0, column=1, padx=5)
        
        # Break timings section
        break_row = 6 if level == 'senior_secondary' else 4
        break_frame = tk.LabelFrame(parent, text="BREAK TIMINGS", bg='white', font=('Arial', 9, 'bold'))
        break_frame.grid(row=break_row, column=0, columnspan=3, sticky='ew', padx=5, pady=5)
        
        # 1st Break
        tk.Label(break_frame, text="1ST BREAK:", bg='white', font=('Arial', 8, 'bold')).grid(row=0, column=0, columnspan=2, pady=2)
        tk.Label(break_frame, text="AFTER CLASS:", bg='white', font=('Arial', 8)).grid(row=1, column=0, sticky='w', padx=2)
        fields['break1_after'] = tk.Entry(break_frame, width=8, font=('Arial', 8))
        fields['break1_after'].grid(row=1, column=1, padx=2)
        tk.Label(break_frame, text="DURATION:", bg='white', font=('Arial', 8)).grid(row=1, column=2, sticky='w', padx=2)
        fields['break1_duration'] = tk.Entry(break_frame, width=8, font=('Arial', 8))
        fields['break1_duration'].grid(row=1, column=3, padx=2)
        tk.Label(break_frame, text="(period no.)", bg='white', font=('Arial', 6), fg='gray').grid(row=2, column=0, columnspan=2)
        tk.Label(break_frame, text="(minutes)", bg='white', font=('Arial', 6), fg='gray').grid(row=2, column=2, columnspan=2)
        
        # Lunch time
        tk.Label(break_frame, text="LUNCH TIME:", bg='white', font=('Arial', 8, 'bold')).grid(row=3, column=0, columnspan=2, pady=2)
        tk.Label(break_frame, text="AFTER CLASS:", bg='white', font=('Arial', 8)).grid(row=4, column=0, sticky='w', padx=2)
        fields['lunch_after'] = tk.Entry(break_frame, width=8, font=('Arial', 8))
        fields['lunch_after'].grid(row=4, column=1, padx=2)
        tk.Label(break_frame, text="DURATION:", bg='white', font=('Arial', 8)).grid(row=4, column=2, sticky='w', padx=2)
        fields['lunch_duration'] = tk.Entry(break_frame, width=8, font=('Arial', 8))
        fields['lunch_duration'].grid(row=4, column=3, padx=2)
        tk.Label(break_frame, text="(period no.)", bg='white', font=('Arial', 6), fg='gray').grid(row=5, column=0, columnspan=2)
        tk.Label(break_frame, text="(minutes)", bg='white', font=('Arial', 6), fg='gray').grid(row=5, column=2, columnspan=2)
        
        # 2nd Break
        tk.Label(break_frame, text="2ND BREAK:", bg='white', font=('Arial', 8, 'bold')).grid(row=6, column=0, columnspan=2, pady=2)
        tk.Label(break_frame, text="AFTER CLASS:", bg='white', font=('Arial', 8)).grid(row=7, column=0, sticky='w', padx=2)
        fields['break2_after'] = tk.Entry(break_frame, width=8, font=('Arial', 8))
        fields['break2_after'].grid(row=7, column=1, padx=2)
        tk.Label(break_frame, text="DURATION:", bg='white', font=('Arial', 8)).grid(row=7, column=2, sticky='w', padx=2)
        fields['break2_duration'] = tk.Entry(break_frame, width=8, font=('Arial', 8))
        fields['break2_duration'].grid(row=7, column=3, padx=2)
        tk.Label(break_frame, text="(period no.)", bg='white', font=('Arial', 6), fg='gray').grid(row=8, column=0, columnspan=2)
        tk.Label(break_frame, text="(minutes)", bg='white', font=('Arial', 6), fg='gray').grid(row=8, column=2, columnspan=2)
        
        if level == 'primary':
            self.primary_fields = fields
        elif level == 'secondary':
            self.secondary_fields = fields
        else:  # senior_secondary
            self.senior_secondary_fields = fields
    
    def toggle_extra_class_timing(self, level):
        """Show/hide extra class timing based on checkbox"""
        if level == 'senior_secondary':
            extra_class_frame = self.senior_secondary_fields['extra_class_frame']
            if self.senior_secondary_fields['extra_class_var'].get():
                extra_class_frame.grid()
            else:
                extra_class_frame.grid_remove()
    
    def save_school_details(self):
        if not self.school_name_entry.get() or not self.board_var.get() or not self.region_var.get():
            messagebox.showerror("Error", "Please fill in school name, select board, and select region")
            return
            
        # Get regional language based on region
        regional_languages = {
            "Tamil Nadu": "Tamil",
            "Karnataka": "Kannada", 
            "Kerala": "Malayalam",
            "Andhra Pradesh": "Telugu",
            "Telangana": "Telugu",
            "Maharashtra": "Marathi",
            "Gujarat": "Gujarati",
            "Rajasthan": "Rajasthani",
            "Punjab": "Punjabi",
            "Haryana": "Hindi",
            "Uttar Pradesh": "Hindi",
            "Bihar": "Hindi",
            "West Bengal": "Bengali",
            "Odisha": "Odia",
            "Jharkhand": "Hindi",
            "Chhattisgarh": "Hindi",
            "Madhya Pradesh": "Hindi",
            "Assam": "Assamese",
            "Other": "Regional Language"
        }
        
        regional_language = regional_languages.get(self.region_var.get(), "Regional Language")
        
        # Update board subjects with actual regional language
        for board in self.board_subjects:
            for class_num in self.board_subjects[board]:
                subjects = self.board_subjects[board][class_num]
                # Replace REGIONAL_LANGUAGE placeholder with actual regional language
                if "REGIONAL_LANGUAGE" in subjects:
                    idx = subjects.index("REGIONAL_LANGUAGE")
                    subjects[idx] = regional_language
        
        # Update stream subjects with regional language
        for stream in self.stream_subjects:
            if "REGIONAL_LANGUAGE" in self.stream_subjects[stream]["core"]:
                idx = self.stream_subjects[stream]["core"].index("REGIONAL_LANGUAGE")
                self.stream_subjects[stream]["core"][idx] = regional_language
        
        # Save extra class data for senior secondary
        extra_class_enabled = self.senior_secondary_fields.get('extra_class_var', tk.BooleanVar()).get()
        extra_class_timing = ""
        if extra_class_enabled:
            extra_class_timing = self.senior_secondary_fields.get('extra_class_timing', tk.Entry()).get()
            if not extra_class_timing:
                messagebox.showerror("Error", "Please specify extra class timing for senior secondary")
                return
        
        self.school_data = {
            'name': self.school_name_entry.get(),
            'board': self.board_var.get(),
            'region': self.region_var.get(),
            'regional_language': regional_language,
            'primary_timings': {k: v.get() if hasattr(v, 'get') else v for k, v in self.primary_fields.items() if k not in ['extra_class_var', 'extra_class_frame', 'extra_class_timing']},
            'secondary_timings': {k: v.get() if hasattr(v, 'get') else v for k, v in self.secondary_fields.items() if k not in ['extra_class_var', 'extra_class_frame', 'extra_class_timing']},
            'senior_secondary_timings': {k: v.get() if hasattr(v, 'get') else v for k, v in self.senior_secondary_fields.items() if k not in ['extra_class_var', 'extra_class_frame', 'extra_class_timing']},
            'working_days': [day for day, var in self.working_days.items() if var.get()],
            'extra_class_enabled': extra_class_enabled,
            'extra_class_timing': extra_class_timing
        }
        
        messagebox.showinfo("Success", "School details saved successfully!")
        self.class_details_screen()
    
    def class_details_screen(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg='white')
        self.current_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_frame = tk.Frame(self.current_frame, bg='white', relief='solid', bd=2)
        title_frame.pack(fill='x', pady=10)
        tk.Label(title_frame, text="CLASS DETAILS", font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
        
        # Input section
        input_frame = tk.Frame(self.current_frame, bg='white')
        input_frame.pack(fill='x', pady=10)
        
        # Class selection
        tk.Label(input_frame, text="SELECT CLASS:", bg='white', font=('Arial', 10)).grid(row=0, column=0, padx=10, pady=5)
        tk.Label(input_frame, text="(Choose class number 1-12)", bg='white', font=('Arial', 8), fg='gray').grid(row=1, column=0, padx=10)
        self.class_var = tk.StringVar()
        class_combo = ttk.Combobox(input_frame, textvariable=self.class_var, 
                                  values=[str(i) for i in range(1, 13)], width=15)
        class_combo.grid(row=0, column=1, padx=10, pady=5)
        
        # Sections
        tk.Label(input_frame, text="ADD SECTIONS:", bg='white', font=('Arial', 10)).grid(row=0, column=2, padx=10, pady=5)
        tk.Label(input_frame, text="(e.g., A,B,C or leave blank)", bg='white', font=('Arial', 8), fg='gray').grid(row=1, column=2, padx=10)
        self.sections_entry = tk.Entry(input_frame, width=20)
        self.sections_entry.grid(row=0, column=3, padx=10, pady=5)
        
        # No section checkbox
        self.no_section_var = tk.BooleanVar()
        tk.Checkbutton(input_frame, text="NO SECTION:", variable=self.no_section_var, 
                      bg='white', font=('Arial', 10)).grid(row=2, column=2, columnspan=2, pady=5)
        tk.Label(input_frame, text="(Check if class has no sections)", bg='white', font=('Arial', 8), fg='gray').grid(row=3, column=2, columnspan=2)
        
        # Add class button
        tk.Button(input_frame, text="ADD CLASS", command=self.add_class,
                 font=('Arial', 10), bg='lightblue', width=15).grid(row=4, column=1, columnspan=2, pady=10)
        
        # Class list
        list_frame = tk.LabelFrame(self.current_frame, text="CLASS LIST", bg='white', font=('Arial', 12, 'bold'))
        list_frame.pack(fill='both', expand=True, pady=10)
        
        # Headers
        headers_frame = tk.Frame(list_frame, bg='white', relief='solid', bd=1)
        headers_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(headers_frame, text="CLASS", bg='white', font=('Arial', 10, 'bold'), 
                relief='solid', bd=1, width=20).pack(side='left', fill='x', expand=True)
        tk.Label(headers_frame, text="SECTIONS", bg='white', font=('Arial', 10, 'bold'), 
                relief='solid', bd=1, width=20).pack(side='left', fill='x', expand=True)
        
        # Scrollable list
        self.class_list_frame = tk.Frame(list_frame, bg='white')
        self.class_list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.update_class_list()
        
        # Buttons
        btn_frame = tk.Frame(self.current_frame, bg='white')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Continue", command=self.subject_details_screen,
                 font=('Arial', 12), bg='lightgreen', width=15).pack(side='left', padx=10)
        tk.Button(btn_frame, text="Back", command=self.school_details_screen,
                 font=('Arial', 12), bg='lightcoral', width=15).pack(side='left', padx=10)
    
    def add_class(self):
        if not self.class_var.get():
            messagebox.showerror("Error", "Please select a class")
            return
            
        class_num = int(self.class_var.get())
        
        if self.no_section_var.get():
            sections = []
        else:
            sections_text = self.sections_entry.get().strip()
            if sections_text:
                sections = [s.strip().upper() for s in sections_text.split(',')]
            else:
                sections = []
        
        # Check if class already exists
        for existing_class in self.classes_data:
            if existing_class['class'] == class_num:
                messagebox.showerror("Error", f"Class {class_num} already exists")
                return
        
        self.classes_data.append({
            'class': class_num,
            'sections': sections
        })
        
        self.update_class_list()
        self.class_var.set('')
        self.sections_entry.delete(0, tk.END)
        self.no_section_var.set(False)
    
    def update_class_list(self):
        for widget in self.class_list_frame.winfo_children():
            widget.destroy()
            
        for class_data in self.classes_data:
            row_frame = tk.Frame(self.class_list_frame, bg='white', relief='solid', bd=1)
            row_frame.pack(fill='x', pady=1)
            
            tk.Label(row_frame, text=f"Class {class_data['class']}", bg='white', 
                    relief='solid', bd=1, width=20).pack(side='left', fill='x', expand=True)
            
            sections_text = ', '.join(class_data['sections']) if class_data['sections'] else 'No Sections'
            tk.Label(row_frame, text=sections_text, bg='white', 
                    relief='solid', bd=1, width=20).pack(side='left', fill='x', expand=True)
    
    def subject_details_screen(self):
        if not self.classes_data:
            messagebox.showerror("Error", "Please add classes first")
            return
            
        if not self.school_data.get('board'):
            messagebox.showerror("Error", "Please set school board first")
            return
            
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg='white')
        self.current_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_frame = tk.Frame(self.current_frame, bg='white', relief='solid', bd=2)
        title_frame.pack(fill='x', pady=10)
        tk.Label(title_frame, text="SUBJECT DETAILS", font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
        
        # Instructions
        instruction_frame = tk.Frame(self.current_frame, bg='white')
        instruction_frame.pack(fill='x', pady=5)
        tk.Label(instruction_frame, text="Select subjects for each class. For classes 11-12, choose stream first.", 
                bg='white', font=('Arial', 10), fg='gray').pack()
        
        # Scrollable frame
        canvas = tk.Canvas(self.current_frame, bg='white')
        scrollbar = ttk.Scrollbar(self.current_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Subject selection for each class
        self.subject_vars = {}
        self.stream_vars = {}
        board = self.school_data['board']
        
        for class_data in self.classes_data:
            class_num = class_data['class']
            
            class_frame = tk.LabelFrame(scrollable_frame, text=f"CLASS {class_num}", 
                                       bg='white', font=('Arial', 12, 'bold'))
            class_frame.pack(fill='x', padx=10, pady=10)
            
            # For classes 11-12, add stream selection
            if class_num >= 11:
                stream_frame = tk.Frame(class_frame, bg='white', relief='solid', bd=1)
                stream_frame.pack(fill='x', padx=10, pady=5)
                
                tk.Label(stream_frame, text="SELECT STREAM:", bg='white', font=('Arial', 11, 'bold')).pack(anchor='w', padx=10, pady=5)
                
                stream_var = tk.StringVar()
                self.stream_vars[class_num] = stream_var
                stream_var.trace('w', lambda *args, cn=class_num: self.update_stream_subjects(cn))
                
                stream_combo = ttk.Combobox(stream_frame, textvariable=stream_var,
                                          values=list(self.stream_subjects.keys()), width=20)
                stream_combo.pack(anchor='w', padx=10, pady=5)
                
                # Create placeholder for subjects
                subjects_frame = tk.Frame(class_frame, bg='white', relief='solid', bd=1)
                subjects_frame.pack(fill='x', padx=10, pady=10)
                
                # Store reference for later updates
                if not hasattr(self, 'class_subject_frames'):
                    self.class_subject_frames = {}
                self.class_subject_frames[class_num] = subjects_frame
                
                self.subject_vars[class_num] = {}
                
            else:
                # For classes 1-10, use regular board subjects
                subjects_frame = tk.Frame(class_frame, bg='white', relief='solid', bd=1)
                subjects_frame.pack(fill='x', padx=10, pady=10)
                
                if class_num in self.board_subjects[board]:
                    subjects = self.board_subjects[board][class_num]
                    self.subject_vars[class_num] = {}
                    
                    # Create checkboxes in 2 columns
                    for i, subject in enumerate(subjects):
                        var = tk.BooleanVar()
                        self.subject_vars[class_num][subject] = var
                        
                        row = i // 2
                        col = i % 2
                        
                        cb = tk.Checkbutton(subjects_frame, text=subject, variable=var, 
                                           bg='white', font=('Arial', 10))
                        cb.grid(row=row, column=col, sticky='w', padx=20, pady=2)

            # Add ECA checkbox for all classes
            eca_var = tk.BooleanVar()
            eca_var.trace('w', lambda *args, cn=class_num: self.toggle_eca_details(cn))
            self.subject_vars[class_num]['ECA'] = eca_var

            eca_cb = tk.Checkbutton(class_frame, text="ECA (Extra Curricular Activities)", 
                                   variable=eca_var, bg='white', font=('Arial', 10, 'bold'))
            eca_cb.pack(anchor='w', padx=20, pady=5)

            # ECA details frame (initially hidden)
            eca_details_frame = tk.Frame(class_frame, bg='white')
            eca_details_frame.pack(anchor='w', padx=40, pady=5)
            eca_details_frame.pack_forget()  # Hide initially

            tk.Label(eca_details_frame, text="ECA Day:", bg='white', font=('Arial', 9)).grid(row=0, column=0, padx=5)
            tk.Label(eca_details_frame, text="(Select day for ECA)", bg='white', font=('Arial', 7), fg='gray').grid(row=1, column=0, padx=5)
            eca_day_var = tk.StringVar()
            eca_day_combo = ttk.Combobox(eca_details_frame, textvariable=eca_day_var,
                                        values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
                                        width=10, font=('Arial', 9))
            eca_day_combo.grid(row=0, column=1, padx=5)

            tk.Label(eca_details_frame, text="ECA Time:", bg='white', font=('Arial', 9)).grid(row=0, column=2, padx=5)
            tk.Label(eca_details_frame, text="(e.g., 14:00-15:00)", bg='white', font=('Arial', 7), fg='gray').grid(row=1, column=2, padx=5)
            eca_time_entry = tk.Entry(eca_details_frame, width=15, font=('Arial', 9))
            eca_time_entry.grid(row=0, column=3, padx=5)

            # Store ECA details widgets for later access
            if not hasattr(self, 'eca_widgets'):
                self.eca_widgets = {}
            self.eca_widgets[class_num] = {
                'frame': eca_details_frame,
                'day_var': eca_day_var,
                'time_entry': eca_time_entry
            }

            # Add Lab Activities for higher secondary classes (11-12)
            if class_num >= 11:
                lab_var = tk.BooleanVar()
                lab_var.trace('w', lambda *args, cn=class_num: self.toggle_lab_details(cn))
                self.subject_vars[class_num]['LAB'] = lab_var

                lab_cb = tk.Checkbutton(class_frame, text="Lab Activities", 
                                       variable=lab_var, bg='white', font=('Arial', 10, 'bold'))
                lab_cb.pack(anchor='w', padx=20, pady=5)

                # Lab details frame (initially hidden)
                lab_details_frame = tk.Frame(class_frame, bg='white')
                lab_details_frame.pack(anchor='w', padx=40, pady=5)
                lab_details_frame.pack_forget()  # Hide initially

                tk.Label(lab_details_frame, text="Lab Days:", bg='white', font=('Arial', 9)).grid(row=0, column=0, padx=5)
                tk.Label(lab_details_frame, text="(Select days for lab)", bg='white', font=('Arial', 7), fg='gray').grid(row=1, column=0, padx=5)
                
                # Lab days selection
                lab_days_frame = tk.Frame(lab_details_frame, bg='white')
                lab_days_frame.grid(row=0, column=1, columnspan=3, padx=5)
                
                lab_days_vars = {}
                for i, day in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]):
                    var = tk.BooleanVar()
                    lab_days_vars[day] = var
                    cb = tk.Checkbutton(lab_days_frame, text=day[:3], variable=var, bg='white', font=('Arial', 8))
                    cb.grid(row=0, column=i, padx=2)

                tk.Label(lab_details_frame, text="Lab Time:", bg='white', font=('Arial', 9)).grid(row=2, column=0, padx=5)
                tk.Label(lab_details_frame, text="(e.g., 14:00-16:00)", bg='white', font=('Arial', 7), fg='gray').grid(row=3, column=0, padx=5)
                lab_time_entry = tk.Entry(lab_details_frame, width=15, font=('Arial', 9))
                lab_time_entry.grid(row=2, column=1, padx=5)

                # Store Lab details widgets for later access
                if not hasattr(self, 'lab_widgets'):
                    self.lab_widgets = {}
                self.lab_widgets[class_num] = {
                    'frame': lab_details_frame,
                    'days_vars': lab_days_vars,
                    'time_entry': lab_time_entry
                }
        
        # Buttons
        btn_frame = tk.Frame(self.current_frame, bg='white')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Save & Continue", command=self.save_subjects,
                 font=('Arial', 12), bg='lightgreen', width=15).pack(side='left', padx=10)
        tk.Button(btn_frame, text="Back", command=self.class_details_screen,
                 font=('Arial', 12), bg='lightcoral', width=15).pack(side='left', padx=10)
    
    def update_stream_subjects(self, class_num):
        """Update subjects based on selected stream for classes 11-12"""
        if class_num not in self.stream_vars:
            return
            
        stream = self.stream_vars[class_num].get()
        if not stream or class_num not in self.class_subject_frames:
            return
        
        # Clear existing subject checkboxes
        subjects_frame = self.class_subject_frames[class_num]
        for widget in subjects_frame.winfo_children():
            widget.destroy()
        
        # Get subjects for the selected stream
        stream_data = self.stream_subjects[stream]
        all_subjects = stream_data['core'] + stream_data['optional']
        
        # Create new checkboxes
        self.subject_vars[class_num] = {}
        
        # Core subjects (mandatory)
        tk.Label(subjects_frame, text="CORE SUBJECTS (Mandatory):", bg='white', font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        
        for i, subject in enumerate(stream_data['core']):
            var = tk.BooleanVar()
            var.set(True)  # Core subjects are selected by default
            self.subject_vars[class_num][subject] = var
            
            row = (i // 2) + 1
            col = i % 2
            
            cb = tk.Checkbutton(subjects_frame, text=subject, variable=var, 
                               bg='white', font=('Arial', 10), state='disabled')
            cb.grid(row=row, column=col, sticky='w', padx=20, pady=2)
        
        # Optional subjects
        start_row = (len(stream_data['core']) // 2) + 2
        tk.Label(subjects_frame, text="OPTIONAL SUBJECTS:", bg='white', font=('Arial', 10, 'bold')).grid(row=start_row, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        
        for i, subject in enumerate(stream_data['optional']):
            var = tk.BooleanVar()
            self.subject_vars[class_num][subject] = var
            
            row = start_row + (i // 2) + 1
            col = i % 2
            
            cb = tk.Checkbutton(subjects_frame, text=subject, variable=var, 
                               bg='white', font=('Arial', 10))
            cb.grid(row=row, column=col, sticky='w', padx=20, pady=2)
        
        # Store stream selection
        self.stream_data[class_num] = stream
    
    def toggle_eca_details(self, class_num):
        """Show/hide ECA details based on checkbox"""
        if class_num in self.eca_widgets:
            eca_frame = self.eca_widgets[class_num]['frame']
            if self.subject_vars[class_num]['ECA'].get():
                eca_frame.pack(anchor='w', padx=40, pady=5)
            else:
                eca_frame.pack_forget()
    
    def toggle_lab_details(self, class_num):
        """Show/hide Lab details based on checkbox"""
        if class_num in self.lab_widgets:
            lab_frame = self.lab_widgets[class_num]['frame']
            if self.subject_vars[class_num]['LAB'].get():
                lab_frame.pack(anchor='w', padx=40, pady=5)
            else:
                lab_frame.pack_forget()
    
    def save_subjects(self):
        self.subjects_data = {}
        self.eca_data = {}
        self.lab_data = {}
        
        for class_num, subjects in self.subject_vars.items():
            selected_subjects = []
            for subject, var in subjects.items():
                if var.get():
                    if subject == 'ECA':
                        # Handle ECA separately
                        if class_num in self.eca_widgets:
                            day = self.eca_widgets[class_num]['day_var'].get()
                            time = self.eca_widgets[class_num]['time_entry'].get()
                            if day and time:
                                self.eca_data[class_num] = {'day': day, 'time': time}
                                selected_subjects.append('ECA')
                            else:
                                messagebox.showerror("Error", f"Please specify ECA day and time for Class {class_num}")
                                return
                    elif subject == 'LAB':
                        # Handle Lab separately
                        if class_num in self.lab_widgets:
                            lab_days = [day for day, var in self.lab_widgets[class_num]['days_vars'].items() if var.get()]
                            time = self.lab_widgets[class_num]['time_entry'].get()
                            if lab_days and time:
                                self.lab_data[class_num] = {'days': lab_days, 'time': time}
                                selected_subjects.append('LAB')
                            else:
                                messagebox.showerror("Error", f"Please specify lab days and time for Class {class_num}")
                                return
                    else:
                        selected_subjects.append(subject)
            
            if selected_subjects:
                self.subjects_data[class_num] = selected_subjects
        
        if not self.subjects_data:
            messagebox.showerror("Error", "Please select at least one subject for one class")
            return
            
        messagebox.showinfo("Success", "Subjects, ECA, and Lab details saved successfully!")
        self.teacher_details_screen()
    
    def teacher_details_screen(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg='white')
        self.current_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_frame = tk.Frame(self.current_frame, bg='white', relief='solid', bd=2)
        title_frame.pack(fill='x', pady=10)
        tk.Label(title_frame, text="TEACHER DETAILS", font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
        
        # Input section
        input_frame = tk.Frame(self.current_frame, bg='white', relief='solid', bd=2)
        input_frame.pack(fill='x', pady=10, padx=20)
        
        # Teacher info
        info_frame = tk.Frame(input_frame, bg='white')
        info_frame.pack(fill='x', pady=10)
        
        tk.Label(info_frame, text="TEACHER NAME:", bg='white', font=('Arial', 10)).grid(row=0, column=0, padx=10, pady=5)
        tk.Label(info_frame, text="(Enter full name)", bg='white', font=('Arial', 8), fg='gray').grid(row=1, column=0, padx=10)
        self.teacher_name_entry = tk.Entry(info_frame, width=20, font=('Arial', 10))
        self.teacher_name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(info_frame, text="EMPLOYEE ID:", bg='white', font=('Arial', 10)).grid(row=0, column=2, padx=10, pady=5)
        tk.Label(info_frame, text="(Unique ID)", bg='white', font=('Arial', 8), fg='gray').grid(row=1, column=2, padx=10)
        self.employee_id_entry = tk.Entry(info_frame, width=20, font=('Arial', 10))
        self.employee_id_entry.grid(row=0, column=3, padx=10, pady=5)
        
        tk.Label(info_frame, text="EMAIL:", bg='white', font=('Arial', 10)).grid(row=2, column=0, padx=10, pady=5)
        tk.Label(info_frame, text="(Optional)", bg='white', font=('Arial', 8), fg='gray').grid(row=3, column=0, padx=10)
        self.teacher_email_entry = tk.Entry(info_frame, width=20, font=('Arial', 10))
        self.teacher_email_entry.grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(info_frame, text="QUALIFICATION:", bg='white', font=('Arial', 10)).grid(row=2, column=2, padx=10, pady=5)
        tk.Label(info_frame, text="(e.g., M.A., B.Ed.)", bg='white', font=('Arial', 8), fg='gray').grid(row=3, column=2, padx=10)
        self.teacher_qualification_entry = tk.Entry(info_frame, width=20, font=('Arial', 10))
        self.teacher_qualification_entry.grid(row=2, column=3, padx=10, pady=5)
        
        # Class selection
        class_frame = tk.LabelFrame(input_frame, text="SELECT CLASS:", bg='white', font=('Arial', 10, 'bold'))
        class_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(class_frame, text="(Select classes this teacher will teach)", bg='white', font=('Arial', 8), fg='gray').pack()
        
        self.teacher_class_vars = {}
        class_inner = tk.Frame(class_frame, bg='white')
        class_inner.pack(pady=5)
        
        col = 0
        row = 0
        for class_data in self.classes_data:
            class_num = class_data['class']
            sections = class_data['sections']
            
            if not sections:  # No sections
                var = tk.BooleanVar()
                var.trace('w', self.update_subject_selection)
                self.teacher_class_vars[f"Class {class_num}"] = var
                cb = tk.Checkbutton(class_inner, text=f"Class {class_num}", variable=var, 
                                   bg='white', font=('Arial', 9))
                cb.grid(row=row, column=col, sticky='w', padx=10, pady=2)
                col += 1
                if col > 3:
                    col = 0
                    row += 1
            else:
                for section in sections:
                    var = tk.BooleanVar()
                    var.trace('w', self.update_subject_selection)
                    self.teacher_class_vars[f"Class {class_num}-{section}"] = var
                    cb = tk.Checkbutton(class_inner, text=f"Class {class_num}-{section}", variable=var, 
                                       bg='white', font=('Arial', 9))
                    cb.grid(row=row, column=col, sticky='w', padx=10, pady=2)
                    col += 1
                    if col > 3:
                        col = 0
                        row += 1
        
        # Subject selection
        self.subject_frame = tk.LabelFrame(input_frame, text="SELECT SUBJECT:", bg='white', font=('Arial', 10, 'bold'))
        self.subject_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(self.subject_frame, text="(Select subjects this teacher can teach)", bg='white', font=('Arial', 8), fg='gray').pack()
        
        self.teacher_subject_vars = {}
        
        # Add teacher button
        tk.Button(input_frame, text="ADD TEACHER +", command=self.add_teacher,
                 font=('Arial', 12), bg='lightblue', width=20).pack(pady=20)
        
        # Teachers summary (simplified)
        summary_frame = tk.LabelFrame(self.current_frame, text="TEACHERS SUMMARY", bg='white', font=('Arial', 12, 'bold'))
        summary_frame.pack(fill='both', expand=True, pady=10)
        
        self.teachers_summary_label = tk.Label(summary_frame, text="No teachers added yet", 
                                             bg='white', font=('Arial', 10))
        self.teachers_summary_label.pack(pady=20)
        
        self.update_teachers_summary()
        
        # Buttons
        btn_frame = tk.Frame(self.current_frame, bg='white')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Continue", command=self.generate_timetable_screen,
                 font=('Arial', 12), bg='lightgreen', width=15).pack(side='left', padx=10)
        tk.Button(btn_frame, text="Back", command=self.subject_details_screen,
                 font=('Arial', 12), bg='lightcoral', width=15).pack(side='left', padx=10)
        
    
    def update_subject_selection(self, *args):
        # Clear existing subject checkboxes
        for widget in self.subject_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.destroy()
        
        self.teacher_subject_vars = {}
        
        # Get selected classes
        selected_classes = []
        for class_name, var in self.teacher_class_vars.items():
            if var.get():
                if '-' in class_name:
                    class_num = int(class_name.split('-')[0].replace('Class ', ''))
                else:
                    class_num = int(class_name.replace('Class ', ''))
                selected_classes.append(class_num)
        
        # Show subjects for selected classes
        all_subjects = set()
        for class_num in selected_classes:
            if class_num in self.subjects_data:
                all_subjects.update(self.subjects_data[class_num])
        
        if all_subjects:
            subjects_inner = tk.Frame(self.subject_frame, bg='white')
            subjects_inner.pack(pady=5)
            
            col = 0
            row = 0
            for subject in sorted(all_subjects):
                var = tk.BooleanVar()
                self.teacher_subject_vars[subject] = var
                cb = tk.Checkbutton(subjects_inner, text=subject, variable=var, 
                                   bg='white', font=('Arial', 9))
                cb.grid(row=row, column=col, sticky='w', padx=10, pady=2)
                col += 1
                if col > 2:
                    col = 0
                    row += 1
    
    def add_teacher(self):
        name = self.teacher_name_entry.get().strip()
        emp_id = self.employee_id_entry.get().strip()
        email = self.teacher_email_entry.get().strip()
        qualification = self.teacher_qualification_entry.get().strip()
        
        if not name or not emp_id:
            messagebox.showerror("Error", "Please enter teacher name and employee ID")
            return
        
        # Check if employee ID already exists
        for teacher in self.teachers_data:
            if teacher['employee_id'] == emp_id:
                messagebox.showerror("Error", "Employee ID already exists")
                return
        
        selected_classes = [class_name for class_name, var in self.teacher_class_vars.items() if var.get()]
        selected_subjects = [subject for subject, var in self.teacher_subject_vars.items() if var.get()]
        
        if not selected_classes or not selected_subjects:
            messagebox.showerror("Error", "Please select at least one class and one subject")
            return
        
        self.teachers_data.append({
            'name': name,
            'employee_id': emp_id,
            'email': email,
            'qualification': qualification,
            'classes': selected_classes,
            'subjects': selected_subjects
        })
        
        # Clear form
        self.teacher_name_entry.delete(0, tk.END)
        self.employee_id_entry.delete(0, tk.END)
        self.teacher_email_entry.delete(0, tk.END)
        self.teacher_qualification_entry.delete(0, tk.END)
        for var in self.teacher_class_vars.values():
            var.set(False)
        for var in self.teacher_subject_vars.values():
            var.set(False)
        
        self.update_teachers_summary()
        messagebox.showinfo("Success", "Teacher added successfully!")
    
    def update_teachers_summary(self):
        """Update the simplified teachers summary"""
        if not self.teachers_data:
            self.teachers_summary_label.config(text="No teachers added yet")
            return
        
        summary_text = f"Total Teachers Added: {len(self.teachers_data)}\n\n"
        
        # Group by subjects
        subject_teachers = {}
        for teacher in self.teachers_data:
            for subject in teacher['subjects']:
                if subject not in subject_teachers:
                    subject_teachers[subject] = []
                subject_teachers[subject].append(teacher['name'])
        
        summary_text += "Teachers by Subject:\n"
        for subject, teachers in sorted(subject_teachers.items()):
            summary_text += f"• {subject}: {len(teachers)} teacher(s)\n"
        
        self.teachers_summary_label.config(text=summary_text, justify='left')
    
    def generate_timetable_screen(self):
        if not self.teachers_data:
            messagebox.showerror("Error", "Please add teachers first")
            return
        
        # Generate timetables
        self.generate_timetables()
        
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg='white')
        self.current_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_frame = tk.Frame(self.current_frame, bg='white', relief='solid', bd=2)
        title_frame.pack(fill='x', pady=10)
        tk.Label(title_frame, text="GENERATE TIME TABLE", font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
        
        # Instructions
        instruction_frame = tk.Frame(self.current_frame, bg='white')
        instruction_frame.pack(fill='x', pady=5)
        tk.Label(instruction_frame, text="Select a class to view its timetable. Physical Education is limited to 2 periods per week.", 
                bg='white', font=('Arial', 10), fg='gray').pack()
        
        # Manual change checkbox
        manual_frame = tk.Frame(self.current_frame, bg='white')
        manual_frame.pack(fill='x', pady=5)
        
        self.manual_edit_var = tk.BooleanVar()
        self.manual_edit_var.set(True)
        tk.Checkbutton(manual_frame, text="MANUAL CHANGE", variable=self.manual_edit_var,
                      command=self.toggle_manual_edit, bg='white', font=('Arial', 12)).pack(side='right', padx=20)
        tk.Label(manual_frame, text="(Enable to edit timetable manually)", bg='white', font=('Arial', 8), fg='gray').pack(side='right', padx=5)
        
        # Class selection
        class_select_frame = tk.Frame(self.current_frame, bg='white')
        class_select_frame.pack(fill='x', pady=10)
        
        tk.Label(class_select_frame, text="Select Class:", bg='white', font=('Arial', 12)).pack(side='left', padx=10)
        tk.Label(class_select_frame, text="(Choose class to view timetable)", bg='white', font=('Arial', 8), fg='gray').pack(side='left', padx=5)
        
        self.selected_class_var = tk.StringVar()
        class_options = []
        for class_data in self.classes_data:
            class_num = class_data['class']
            if not class_data['sections']:
                class_options.append(f"Class {class_num}")
            else:
                for section in class_data['sections']:
                    class_options.append(f"Class {class_num}-{section}")
        
        class_combo = ttk.Combobox(class_select_frame, textvariable=self.selected_class_var,
                                  values=class_options, width=20)
        class_combo.pack(side='left', padx=10)
        class_combo.bind('<<ComboboxSelected>>', self.display_timetable)
        
        # Timetable display
        self.timetable_frame = tk.Frame(self.current_frame, bg='white', relief='solid', bd=2)
        self.timetable_frame.pack(fill='both', expand=True, pady=10)
        
        # Buttons
        btn_frame = tk.Frame(self.current_frame, bg='white')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Regenerate", command=self.regenerate_timetable,
                 font=('Arial', 12), bg='lightblue', width=15).pack(side='left', padx=10)
        tk.Button(btn_frame, text="Export", command=self.export_timetable_screen,
                 font=('Arial', 12), bg='lightgreen', width=15).pack(side='left', padx=10)
        tk.Button(btn_frame, text="Back", command=self.teacher_details_screen,
                 font=('Arial', 12), bg='lightcoral', width=15).pack(side='left', padx=10)
        
        # Display first class timetable if available
        if class_options:
            self.selected_class_var.set(class_options[0])
            self.display_timetable()
    
    def generate_timetables(self):
        """Generate varied timetables for all classes with limited PE periods"""
        self.timetables = {}
        working_days = self.school_data.get('working_days', ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
        
        for class_data in self.classes_data:
            class_num = class_data['class']
            
            # Determine if primary, secondary, or senior secondary
            if class_num <= 5:
                timings = self.school_data.get('primary_timings', {})
            elif class_num <= 10:
                timings = self.school_data.get('secondary_timings', {})
            else:  # 11-12
                timings = self.school_data.get('senior_secondary_timings', {})
            
            if not class_data['sections']:
                class_key = f"Class {class_num}"
                self.timetables[class_key] = self.create_class_timetable(class_key, class_num, timings, working_days)
            else:
                for section in class_data['sections']:
                    class_key = f"Class {class_num}-{section}"
                    self.timetables[class_key] = self.create_class_timetable(class_key, class_num, timings, working_days)
    
    def create_class_timetable(self, class_key, class_num, timings, working_days):
        """Create varied timetable for a specific class with limited PE periods"""
        # Get subjects for this class
        subjects = self.subjects_data.get(class_num, [])
        
        # Remove special subjects from regular rotation
        regular_subjects = [s for s in subjects if s not in ['ECA', 'LAB']]
        
        # Get teachers for this class
        class_teachers = {}
        for teacher in self.teachers_data:
            if class_key in teacher['classes']:
                for subject in teacher['subjects']:
                    if subject in regular_subjects:
                        class_teachers[subject] = teacher['name']
        
        if not class_teachers:
            return {}
        
        # Create time slots
        try:
            start_time = datetime.strptime(timings.get('start_time', '9:00'), '%H:%M')
            period_duration = int(timings.get('period_duration', '40'))
            
            # Calculate periods and breaks
            periods_per_day = 8  # Default
            time_slots = []
            current_time = start_time
            
            for period in range(1, periods_per_day + 1):
                end_time = current_time + timedelta(minutes=period_duration)
                time_slots.append({
                    'period': period,
                    'start': current_time.strftime('%H:%M'),
                    'end': end_time.strftime('%H:%M'),
                    'type': 'period'
                })
                current_time = end_time
                
                # Add breaks
                if period == int(timings.get('break1_after', '2')):
                    break_duration = int(timings.get('break1_duration', '15'))
                    current_time += timedelta(minutes=break_duration)
                    time_slots.append({
                        'period': f"Break 1",
                        'start': (current_time - timedelta(minutes=break_duration)).strftime('%H:%M'),
                        'end': current_time.strftime('%H:%M'),
                        'type': 'break'
                    })
                elif period == int(timings.get('lunch_after', '4')):
                    lunch_duration = int(timings.get('lunch_duration', '30'))
                    current_time += timedelta(minutes=lunch_duration)
                    time_slots.append({
                        'period': f"Lunch",
                        'start': (current_time - timedelta(minutes=lunch_duration)).strftime('%H:%M'),
                        'end': current_time.strftime('%H:%M'),
                        'type': 'break'
                    })
                elif period == int(timings.get('break2_after', '6')):
                    break_duration = int(timings.get('break2_duration', '15'))
                    current_time += timedelta(minutes=break_duration)
                    time_slots.append({
                        'period': f"Break 2",
                        'start': (current_time - timedelta(minutes=break_duration)).strftime('%H:%M'),
                        'end': current_time.strftime('%H:%M'),
                        'type': 'break'
                    })
        except:
            # Fallback to simple time slots
            time_slots = [
                {'period': 1, 'start': '9:00', 'end': '9:40', 'type': 'period'},
                {'period': 2, 'start': '9:40', 'end': '10:20', 'type': 'period'},
                {'period': 'Break 1', 'start': '10:20', 'end': '10:35', 'type': 'break'},
                {'period': 3, 'start': '10:35', 'end': '11:15', 'type': 'period'},
                {'period': 4, 'start': '11:15', 'end': '11:55', 'type': 'period'},
                {'period': 'Lunch', 'start': '11:55', 'end': '12:25', 'type': 'break'},
                {'period': 5, 'start': '12:25', 'end': '13:05', 'type': 'period'},
                {'period': 6, 'start': '13:05', 'end': '13:45', 'type': 'period'},
            ]
        
        # Create subject distribution for varied daily schedules with PE limitation
        period_slots = [slot for slot in time_slots if slot['type'] == 'period']
        subject_list = list(class_teachers.keys())
        
        # Separate PE from other subjects
        pe_subject = 'Physical Education'
        other_subjects = [s for s in subject_list if s != pe_subject]
        
        # Generate different timetable for each day
        timetable = {}
        pe_periods_assigned = 0  # Track PE periods across the week
        
        for day_idx, day in enumerate(working_days):
            timetable[day] = []
            
            # Create a shuffled subject list for this day to ensure variety
            daily_subjects = other_subjects.copy()
            random.shuffle(daily_subjects)
            
            # Add PE only if we haven't reached the limit of 2 periods per week
            # Assign PE to specific days (e.g., Tuesday and Thursday)
            if pe_subject in class_teachers and pe_periods_assigned < 2:
                if day in ['Tuesday', 'Thursday'] or (pe_periods_assigned == 0 and day_idx >= len(working_days) - 2):
                    # Insert PE at a random position (not first or last period)
                    if len(period_slots) > 2:
                        pe_position = random.randint(1, min(len(period_slots) - 2, 4))
                        daily_subjects.insert(pe_position, pe_subject)
                        pe_periods_assigned += 1
            
            # Extend the list to cover all periods
            while len(daily_subjects) < len(period_slots):
                daily_subjects.extend(other_subjects)
            
            subject_index = 0
            
            for slot in time_slots:
                if slot['type'] == 'break':
                    timetable[day].append({
                        'time': f"{slot['start']}-{slot['end']}",
                        'subject': slot['period'],
                        'type': 'break'
                    })
                else:
                    if subject_index < len(daily_subjects):
                        subject = daily_subjects[subject_index]
                        teacher = class_teachers.get(subject, 'TBD')
                        timetable[day].append({
                            'time': f"{slot['start']}-{slot['end']}",
                            'subject': subject,
                            'teacher': teacher,
                            'type': 'period'
                        })
                        subject_index += 1
                    else:
                        timetable[day].append({
                            'time': f"{slot['start']}-{slot['end']}",
                            'subject': 'Free Period',
                            'type': 'period'
                        })
        
        # Handle ECA if present
        if class_num in self.eca_data:
            eca_info = self.eca_data[class_num]
            eca_day = eca_info['day']
            eca_time = eca_info['time']
            
            if eca_day in timetable:
                timetable[eca_day].append({
                    'time': eca_time,
                    'subject': 'ECA',
                    'type': 'eca'
                })
        
        # Handle Lab Activities for higher secondary classes
        if class_num in self.lab_data:
            lab_info = self.lab_data[class_num]
            lab_days = lab_info['days']
            lab_time = lab_info['time']
            
            # Get stream-specific lab subjects
            stream = self.stream_data.get(class_num, 'Science')
            lab_subjects = self.stream_subjects.get(stream, {}).get('labs', ['Lab'])
            
            for day in lab_days:
                if day in timetable:
                    # Randomly assign a lab subject for this day
                    lab_subject = random.choice(lab_subjects)
                    timetable[day].append({
                        'time': lab_time,
                        'subject': lab_subject,
                        'type': 'lab'
                    })
        
        # Handle extra class for senior secondary (classes 11-12)
        if class_num >= 11 and self.school_data.get('extra_class_enabled', False):
            extra_class_timing = self.school_data.get('extra_class_timing', '')
            if extra_class_timing:
                # Add extra class to all working days
                for day in working_days:
                    timetable[day].append({
                        'time': extra_class_timing,
                        'subject': 'Extra Class',
                        'type': 'extra_class'
                    })
        
        return timetable
    
    def display_timetable(self, event=None):
        """Display timetable for selected class"""
        class_key = self.selected_class_var.get()
        if not class_key or class_key not in self.timetables:
            return
        
        # Clear existing timetable
        for widget in self.timetable_frame.winfo_children():
            widget.destroy()
        
        # Class label with stream info for 11-12
        class_num = int(class_key.split('-')[0].replace('Class ', ''))
        title_text = class_key
        if class_num >= 11 and class_num in self.stream_data:
            title_text += f" ({self.stream_data[class_num]} Stream)"
        
        tk.Label(self.timetable_frame, text=title_text, font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
        
        # PE limitation notice
        pe_notice = tk.Label(self.timetable_frame, text="Note: Physical Education is limited to 2 periods per week", 
                           font=('Arial', 10), bg='white', fg='blue')
        pe_notice.pack(pady=5)
        
        timetable = self.timetables[class_key]
        
        # Create table
        table_frame = tk.Frame(self.timetable_frame, bg='white')
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Headers
        days = list(timetable.keys())
        if not days:
            tk.Label(table_frame, text="No timetable generated", bg='white').pack()
            return
        
        # Time column header
        tk.Label(table_frame, text="Time", font=('Arial', 10, 'bold'), 
                relief='solid', bd=1, bg='lightgray').grid(row=0, column=0, sticky='nsew')
        
        # Day headers
        for col, day in enumerate(days, 1):
            tk.Label(table_frame, text=day, font=('Arial', 10, 'bold'), 
                    relief='solid', bd=1, bg='lightgray').grid(row=0, column=col, sticky='nsew')
        
        # Get maximum number of time slots across all days
        max_slots = max(len(timetable[day]) for day in days)
        
        # Create rows
        for row in range(1, max_slots + 1):
            # Time column - use first day's time slot
            first_day = days[0]
            if row-1 < len(timetable[first_day]):
                time_text = timetable[first_day][row-1]['time']
            else:
                time_text = ""
            
            tk.Label(table_frame, text=time_text, font=('Arial', 9), 
                    relief='solid', bd=1, bg='white').grid(row=row, column=0, sticky='nsew')
            
            # Subject for each day
            for col, day in enumerate(days, 1):
                if row-1 < len(timetable[day]):
                    day_slot = timetable[day][row-1]
                    if day_slot['type'] == 'break':
                        text = day_slot['subject']
                        bg_color = 'lightblue'
                    elif day_slot['type'] == 'eca':
                        text = day_slot['subject']
                        bg_color = 'lightgreen'
                    elif day_slot['type'] == 'lab':
                        text = day_slot['subject']
                        bg_color = 'lightyellow'
                    elif day_slot['type'] == 'extra_class':
                        text = day_slot['subject']
                        bg_color = 'lightcoral'
                    else:
                        text = f"{day_slot['subject']}\n({day_slot.get('teacher', 'TBD')})"
                        # Highlight PE periods
                        bg_color = 'lightpink' if day_slot['subject'] == 'Physical Education' else 'white'
                    
                    if self.manual_edit_var.get() and day_slot['type'] not in ['break', 'eca', 'lab', 'extra_class']:
                        # Create editable entry
                        entry = tk.Text(table_frame, height=3, width=15, font=('Arial', 8),
                                       relief='solid', bd=1, bg=bg_color)
                        entry.insert('1.0', text)
                        entry.grid(row=row, column=col, sticky='nsew')
                    else:
                        # Create label
                        label = tk.Label(table_frame, text=text, font=('Arial', 8), 
                                        relief='solid', bd=1, bg=bg_color, wraplength=100)
                        label.grid(row=row, column=col, sticky='nsew')
                else:
                    # Empty cell
                    tk.Label(table_frame, text="", font=('Arial', 8), 
                            relief='solid', bd=1, bg='white').grid(row=row, column=col, sticky='nsew')
        
        # Configure grid weights
        for i in range(len(days) + 1):
            table_frame.columnconfigure(i, weight=1)
        for i in range(max_slots + 1):
            table_frame.rowconfigure(i, weight=1)
    
    def toggle_manual_edit(self):
        """Toggle manual edit mode"""
        self.display_timetable()
    
    def regenerate_timetable(self):
        """Regenerate all timetables"""
        self.generate_timetables()
        self.display_timetable()
        messagebox.showinfo("Success", "Timetables regenerated successfully!\nPhysical Education limited to 2 periods per week.")
    
    def export_timetable_screen(self):
        if not self.timetables:
            messagebox.showerror("Error", "No timetables to export. Please generate timetables first.")
            return
            
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg='white')
        self.current_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_frame = tk.Frame(self.current_frame, bg='white', relief='solid', bd=2)
        title_frame.pack(fill='x', pady=10)
        tk.Label(title_frame, text="EXPORT TIME TABLE", font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
        
        # Instructions
        tk.Label(self.current_frame, text="SELECT TIMETABLE OF CLASS TO EXPORT", 
                bg='white', font=('Arial', 12)).pack(pady=10)
        tk.Label(self.current_frame, text="(Choose which class timetables to save as files)", 
                bg='white', font=('Arial', 10), fg='gray').pack()
        
        # Selection frame
        selection_frame = tk.Frame(self.current_frame, bg='white', relief='solid', bd=2)
        selection_frame.pack(fill='both', expand=True, padx=50, pady=20)
        
        # Export all checkbox
        self.export_all_var = tk.BooleanVar()
        tk.Checkbutton(selection_frame, text="EXPORT ALL", variable=self.export_all_var,
                      bg='white', font=('Arial', 12), command=self.toggle_export_all).pack(pady=10)
        tk.Label(selection_frame, text="(Select all classes at once)", bg='white', font=('Arial', 8), fg='gray').pack()
        
        # Individual class checkboxes
        self.export_class_vars = {}
        for class_key in sorted(self.timetables.keys()):
            var = tk.BooleanVar()
            self.export_class_vars[class_key] = var
            
            # Add stream info for display
            class_num = int(class_key.split('-')[0].replace('Class ', ''))
            display_text = class_key
            if class_num >= 11 and class_num in self.stream_data:
                display_text += f" ({self.stream_data[class_num]})"
            
            tk.Checkbutton(selection_frame, text=display_text, variable=var,
                          bg='white', font=('Arial', 11)).pack(anchor='w', padx=20, pady=2)
        
        # Buttons
        btn_frame = tk.Frame(self.current_frame, bg='white')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Export Selected", command=self.export_selected_timetables,
                 font=('Arial', 12), bg='lightgreen', width=15).pack(side='left', padx=10)
        tk.Button(btn_frame, text="Preview", command=self.preview_export,
                 font=('Arial', 12), bg='lightblue', width=15).pack(side='left', padx=10)
        tk.Button(btn_frame, text="Back", command=self.generate_timetable_screen,
                 font=('Arial', 12), bg='lightcoral', width=15).pack(side='left', padx=10)
    
    def toggle_export_all(self):
        """Toggle all class selections"""
        export_all = self.export_all_var.get()
        for var in self.export_class_vars.values():
            var.set(export_all)
    
    def export_selected_timetables(self):
        """Export selected timetables to text files"""
        selected_classes = [class_key for class_key, var in self.export_class_vars.items() if var.get()]
        
        if not selected_classes:
            messagebox.showerror("Error", "Please select at least one class to export")
            return
        
        try:
            # Create exports directory
            if not os.path.exists('timetable_exports'):
                os.makedirs('timetable_exports')
            
            for class_key in selected_classes:
                filename = f"timetable_exports/{class_key.replace(' ', '_').replace('-', '_')}_timetable.txt"
                
                class_num = int(class_key.split('-')[0].replace('Class ', ''))
                
                with open(filename, 'w') as f:
                    f.write(f"TIMETABLE FOR {class_key}\n")
                    if class_num >= 11 and class_num in self.stream_data:
                        f.write(f"Stream: {self.stream_data[class_num]}\n")
                    f.write(f"School: {self.school_data.get('name', 'N/A')}\n")
                    f.write(f"Board: {self.school_data.get('board', 'N/A')}\n")
                    f.write("Note: Physical Education limited to 2 periods per week\n")
                    f.write("=" * 80 + "\n\n")
                    
                    timetable = self.timetables[class_key]
                    
                    # Write timetable
                    for day, slots in timetable.items():
                        f.write(f"{day.upper()}\n")
                        f.write("-" * 40 + "\n")
                        
                        for slot in slots:
                            if slot['type'] == 'break':
                                f.write(f"{slot['time']}: {slot['subject']}\n")
                            elif slot['type'] == 'eca':
                                f.write(f"{slot['time']}: {slot['subject']}\n")
                            elif slot['type'] == 'lab':
                                f.write(f"{slot['time']}: {slot['subject']}\n")
                            elif slot['type'] == 'extra_class':
                                f.write(f"{slot['time']}: {slot['subject']}\n")
                            else:
                                teacher_info = f" - {slot.get('teacher', 'TBD')}" if slot.get('teacher') else ""
                                f.write(f"{slot['time']}: {slot['subject']}{teacher_info}\n")
                        
                        f.write("\n")
            
            messagebox.showinfo("Success", f"Timetables exported successfully!\nFiles saved in 'timetable_exports' folder\nPhysical Education limited to 2 periods per week.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export timetables: {str(e)}")
    
    def preview_export(self):
        """Preview selected timetables"""
        selected_classes = [class_key for class_key, var in self.export_class_vars.items() if var.get()]
        
        if not selected_classes:
            messagebox.showerror("Error", "Please select at least one class to preview")
            return
        
        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Timetable Preview")
        preview_window.geometry("800x600")
        preview_window.configure(bg='white')
        
        # Create scrollable text widget
        text_frame = tk.Frame(preview_window, bg='white')
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap='word', font=('Courier', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Generate preview content
        preview_content = ""
        for class_key in selected_classes:
            class_num = int(class_key.split('-')[0].replace('Class ', ''))
            
            preview_content += f"TIMETABLE FOR {class_key}\n"
            if class_num >= 11 and class_num in self.stream_data:
                preview_content += f"Stream: {self.stream_data[class_num]}\n"
            preview_content += f"School: {self.school_data.get('name', 'N/A')}\n"
            preview_content += f"Board: {self.school_data.get('board', 'N/A')}\n"
            preview_content += "Note: Physical Education limited to 2 periods per week\n"
            preview_content += "=" * 60 + "\n\n"
            
            timetable = self.timetables[class_key]
            
            for day, slots in timetable.items():
                preview_content += f"{day.upper()}\n"
                preview_content += "-" * 30 + "\n"
                
                for slot in slots:
                    if slot['type'] == 'break':
                        preview_content += f"{slot['time']}: {slot['subject']}\n"
                    elif slot['type'] == 'eca':
                        preview_content += f"{slot['time']}: {slot['subject']}\n"
                    elif slot['type'] == 'lab':
                        preview_content += f"{slot['time']}: {slot['subject']}\n"
                    elif slot['type'] == 'extra_class':
                        preview_content += f"{slot['time']}: {slot['subject']}\n"
                    else:
                        teacher_info = f" - {slot.get('teacher', 'TBD')}" if slot.get('teacher') else ""
                        preview_content += f"{slot['time']}: {slot['subject']}{teacher_info}\n"
                
                preview_content += "\n"
            
            preview_content += "\n" + "=" * 60 + "\n\n"
        
        text_widget.insert('1.0', preview_content)
        text_widget.config(state='disabled')
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Close button
        tk.Button(preview_window, text="Close", command=preview_window.destroy,
                 font=('Arial', 12), bg='lightcoral').pack(pady=10)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TimetableGenerator()
    app.run()
