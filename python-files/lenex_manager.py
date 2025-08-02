import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import xml.etree.ElementTree as ET
from datetime import datetime, date
import csv
import os
from typing import Dict, List, Optional
import json

class LenexManager:
    def __init__(self, root):
        self.root = root
        self.root.title("LENEX Swimming Meet Manager")
        self.root.geometry("1200x800")
        
        # Data storage
        self.meets = {}
        self.current_meet_id = None
        self.athletes = {}
        self.events = {}
        self.entries = {}
        self.results = {}
        self.sessions = {}
        self.clubs = {}
        
        # ID counters
        self.next_meet_id = 1
        self.next_athlete_id = 1
        self.next_event_id = 1
        self.next_entry_id = 1
        self.next_result_id = 1
        self.next_session_id = 1
        self.next_club_id = 1
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.setup_meet_tab()
        self.setup_athletes_tab()
        self.setup_events_tab()
        self.setup_entries_tab()
        self.setup_results_tab()
        
        # Menu bar
        self.setup_menu()
        
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Meet", command=self.new_meet)
        file_menu.add_command(label="Open Meet", command=self.open_meet)
        file_menu.add_command(label="Save Meet", command=self.save_meet)
        file_menu.add_separator()
        file_menu.add_command(label="Export LENEX", command=self.export_lenex)
        file_menu.add_command(label="Import LENEX", command=self.import_lenex)
        
    def setup_meet_tab(self):
        # Meet Info Tab
        self.meet_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.meet_frame, text="Meet Info")
        
        # Meet details form
        details_frame = ttk.LabelFrame(self.meet_frame, text="Meet Details")
        details_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Meet form fields
        ttk.Label(details_frame, text="Meet Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.meet_name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.meet_name_var, width=50).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(details_frame, text="City:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.meet_city_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.meet_city_var, width=30).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(details_frame, text="Nation:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.meet_nation_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.meet_nation_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(details_frame, text="Course:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.meet_course_var = tk.StringVar(value="LCM")
        course_combo = ttk.Combobox(details_frame, textvariable=self.meet_course_var, 
                                   values=["LCM", "SCM", "SCY"], width=10)
        course_combo.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(details_frame, text="Deadline:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.meet_deadline_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.meet_deadline_var, width=15).grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(details_frame, text="(YYYY-MM-DD)").grid(row=4, column=2, sticky=tk.W, padx=5, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(details_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Create Meet", command=self.create_meet).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Meet", command=self.update_meet).pack(side=tk.LEFT, padx=5)
        
        # Sessions section
        sessions_frame = ttk.LabelFrame(self.meet_frame, text="Sessions")
        sessions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Sessions list
        self.sessions_tree = ttk.Treeview(sessions_frame, columns=("Date", "Time", "Name"), show="tree headings")
        self.sessions_tree.heading("#0", text="ID")
        self.sessions_tree.heading("Date", text="Date")
        self.sessions_tree.heading("Time", text="Time")
        self.sessions_tree.heading("Name", text="Name")
        self.sessions_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        session_button_frame = ttk.Frame(sessions_frame)
        session_button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(session_button_frame, text="Add Session", command=self.add_session).pack(side=tk.LEFT, padx=2)
        ttk.Button(session_button_frame, text="Edit Session", command=self.edit_session).pack(side=tk.LEFT, padx=2)
        ttk.Button(session_button_frame, text="Delete Session", command=self.delete_session).pack(side=tk.LEFT, padx=2)
        
    def setup_athletes_tab(self):
        # Athletes Tab
        self.athletes_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.athletes_frame, text="Athletes")
        
        # Athletes list
        list_frame = ttk.LabelFrame(self.athletes_frame, text="Athletes")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.athletes_tree = ttk.Treeview(list_frame, columns=("LastName", "FirstName", "Birth", "Gender", "Club"), show="tree headings")
        self.athletes_tree.heading("#0", text="ID")
        self.athletes_tree.heading("LastName", text="Last Name")
        self.athletes_tree.heading("FirstName", text="First Name")
        self.athletes_tree.heading("Birth", text="Birth Date")
        self.athletes_tree.heading("Gender", text="Gender")
        self.athletes_tree.heading("Club", text="Club")
        self.athletes_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Athletes form
        form_frame = ttk.LabelFrame(self.athletes_frame, text="Athlete Details")
        form_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Form fields
        ttk.Label(form_frame, text="Last Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.athlete_lastname_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.athlete_lastname_var, width=30).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="First Name:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.athlete_firstname_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.athlete_firstname_var, width=30).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Birth Date:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.athlete_birth_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.athlete_birth_var, width=15).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Gender:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.athlete_gender_var = tk.StringVar()
        ttk.Combobox(form_frame, textvariable=self.athlete_gender_var, values=["M", "F"], width=5).grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Club:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.athlete_club_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.athlete_club_var, width=40).grid(row=2, column=1, columnspan=2, padx=5, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Add Athlete", command=self.add_athlete).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Athlete", command=self.update_athlete).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Athlete", command=self.delete_athlete).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Import CSV", command=self.import_athletes_csv).pack(side=tk.LEFT, padx=5)
        
        # Bind selection event
        self.athletes_tree.bind("<<TreeviewSelect>>", self.on_athlete_select)
        
    def setup_events_tab(self):
        # Events Tab
        self.events_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.events_frame, text="Events")
        
        # Events list
        list_frame = ttk.LabelFrame(self.events_frame, text="Events")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.events_tree = ttk.Treeview(list_frame, columns=("Number", "Gender", "Distance", "Stroke", "Round"), show="tree headings")
        self.events_tree.heading("#0", text="ID")
        self.events_tree.heading("Number", text="Number")
        self.events_tree.heading("Gender", text="Gender")
        self.events_tree.heading("Distance", text="Distance")
        self.events_tree.heading("Stroke", text="Stroke")
        self.events_tree.heading("Round", text="Round")
        self.events_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Events form
        form_frame = ttk.LabelFrame(self.events_frame, text="Event Details")
        form_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(form_frame, text="Event Number:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.event_number_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.event_number_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Gender:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.event_gender_var = tk.StringVar()
        ttk.Combobox(form_frame, textvariable=self.event_gender_var, values=["M", "F", "X"], width=5).grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Distance:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.event_distance_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.event_distance_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Stroke:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.event_stroke_var = tk.StringVar()
        stroke_values = ["FREE", "BACK", "BREAST", "FLY", "MEDLEY", "SURFACE", "APNEA", "UNKNOWN"]
        ttk.Combobox(form_frame, textvariable=self.event_stroke_var, values=stroke_values, width=15).grid(row=1, column=3, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Round:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.event_round_var = tk.StringVar(value="TIM")
        round_values = ["TIM", "FIN", "SEM", "PRE", "QUA"]
        ttk.Combobox(form_frame, textvariable=self.event_round_var, values=round_values, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Add Event", command=self.add_event).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Event", command=self.update_event).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Event", command=self.delete_event).pack(side=tk.LEFT, padx=5)
        
        self.events_tree.bind("<<TreeviewSelect>>", self.on_event_select)
        
    def setup_entries_tab(self):
        # Entries Tab
        self.entries_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.entries_frame, text="Entries")
        
        # Entries list
        list_frame = ttk.LabelFrame(self.entries_frame, text="Entries")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.entries_tree = ttk.Treeview(list_frame, columns=("Athlete", "Event", "EntryTime"), show="tree headings")
        self.entries_tree.heading("#0", text="ID")
        self.entries_tree.heading("Athlete", text="Athlete")
        self.entries_tree.heading("Event", text="Event")
        self.entries_tree.heading("EntryTime", text="Entry Time")
        self.entries_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Entries form
        form_frame = ttk.LabelFrame(self.entries_frame, text="Entry Details")
        form_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(form_frame, text="Athlete:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.entry_athlete_var = tk.StringVar()
        self.entry_athlete_combo = ttk.Combobox(form_frame, textvariable=self.entry_athlete_var, width=30)
        self.entry_athlete_combo.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Event:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.entry_event_var = tk.StringVar()
        self.entry_event_combo = ttk.Combobox(form_frame, textvariable=self.entry_event_var, width=30)
        self.entry_event_combo.grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Entry Time:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.entry_time_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.entry_time_var, width=15).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(form_frame, text="(HH:MM:SS.ss)").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Add Entry", command=self.add_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Entry", command=self.update_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Entry", command=self.delete_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Import CSV", command=self.import_entries_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export CSV", command=self.export_entries_csv).pack(side=tk.LEFT, padx=5)
        
        self.entries_tree.bind("<<TreeviewSelect>>", self.on_entry_select)
        
    def setup_results_tab(self):
        # Results Tab
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Results")
        
        # Results list
        list_frame = ttk.LabelFrame(self.results_frame, text="Results")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.results_tree = ttk.Treeview(list_frame, columns=("Athlete", "Event", "ResultTime", "Place"), show="tree headings")
        self.results_tree.heading("#0", text="ID")
        self.results_tree.heading("Athlete", text="Athlete")
        self.results_tree.heading("Event", text="Event")
        self.results_tree.heading("ResultTime", text="Result Time")
        self.results_tree.heading("Place", text="Place")
        self.results_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Results form
        form_frame = ttk.LabelFrame(self.results_frame, text="Result Details")
        form_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(form_frame, text="Athlete:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.result_athlete_var = tk.StringVar()
        self.result_athlete_combo = ttk.Combobox(form_frame, textvariable=self.result_athlete_var, width=30)
        self.result_athlete_combo.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Event:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.result_event_var = tk.StringVar()
        self.result_event_combo = ttk.Combobox(form_frame, textvariable=self.result_event_var, width=30)
        self.result_event_combo.grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Result Time:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.result_time_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.result_time_var, width=15).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Place:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.result_place_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.result_place_var, width=10).grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Add Result", command=self.add_result).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Result", command=self.update_result).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Result", command=self.delete_result).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Import CSV", command=self.import_results_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export CSV", command=self.export_results_csv).pack(side=tk.LEFT, padx=5)
        
        self.results_tree.bind("<<TreeviewSelect>>", self.on_result_select)
        
    # Meet management methods
    def new_meet(self):
        # Clear all data
        self.meets = {}
        self.athletes = {}
        self.events = {}
        self.entries = {}
        self.results = {}
        self.sessions = {}
        self.current_meet_id = None
        self.refresh_all_displays()
        
    def create_meet(self):
        if not self.meet_name_var.get() or not self.meet_city_var.get():
            messagebox.showerror("Error", "Please fill in required fields (Name, City)")
            return
            
        meet_id = self.next_meet_id
        self.meets[meet_id] = {
            'id': meet_id,
            'name': self.meet_name_var.get(),
            'city': self.meet_city_var.get(),
            'nation': self.meet_nation_var.get(),
            'course': self.meet_course_var.get(),
            'deadline': self.meet_deadline_var.get(),
            'timing': 'MANUAL1'
        }
        self.current_meet_id = meet_id
        self.next_meet_id += 1
        messagebox.showinfo("Success", f"Meet '{self.meet_name_var.get()}' created successfully!")
        
    def update_meet(self):
        if not self.current_meet_id:
            messagebox.showerror("Error", "No meet selected to update")
            return
            
        self.meets[self.current_meet_id].update({
            'name': self.meet_name_var.get(),
            'city': self.meet_city_var.get(),
            'nation': self.meet_nation_var.get(),
            'course': self.meet_course_var.get(),
            'deadline': self.meet_deadline_var.get()
        })
        messagebox.showinfo("Success", "Meet updated successfully!")
        
    # Session management
    def add_session(self):
        if not self.current_meet_id:
            messagebox.showerror("Error", "Please create a meet first")
            return
            
        dialog = SessionDialog(self.root, "Add Session")
        if dialog.result:
            session_id = self.next_session_id
            self.sessions[session_id] = {
                'id': session_id,
                'meet_id': self.current_meet_id,
                'number': dialog.result['number'],
                'date': dialog.result['date'],
                'daytime': dialog.result['daytime'],
                'name': dialog.result['name']
            }
            self.next_session_id += 1
            self.refresh_sessions_display()
            
    def edit_session(self):
        selection = self.sessions_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a session to edit")
            return
            
        session_id = int(self.sessions_tree.item(selection[0])['text'])
        session = self.sessions[session_id]
        
        dialog = SessionDialog(self.root, "Edit Session", session)
        if dialog.result:
            self.sessions[session_id].update(dialog.result)
            self.refresh_sessions_display()
            
    def delete_session(self):
        selection = self.sessions_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a session to delete")
            return
            
        session_id = int(self.sessions_tree.item(selection[0])['text'])
        if messagebox.askyesno("Confirm", "Delete selected session?"):
            del self.sessions[session_id]
            self.refresh_sessions_display()
            
    # Athlete management methods
    def add_athlete(self):
        if not self.athlete_lastname_var.get() or not self.athlete_firstname_var.get():
            messagebox.showerror("Error", "Please fill in required fields")
            return
            
        athlete_id = self.next_athlete_id
        self.athletes[athlete_id] = {
            'id': athlete_id,
            'lastname': self.athlete_lastname_var.get(),
            'firstname': self.athlete_firstname_var.get(),
            'birthdate': self.athlete_birth_var.get(),
            'gender': self.athlete_gender_var.get(),
            'club': self.athlete_club_var.get()
        }
        self.next_athlete_id += 1
        self.refresh_athletes_display()
        self.refresh_entry_combos()
        self.clear_athlete_form()
        
    def update_athlete(self):
        selection = self.athletes_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select an athlete to update")
            return
            
        athlete_id = int(self.athletes_tree.item(selection[0])['text'])
        self.athletes[athlete_id].update({
            'lastname': self.athlete_lastname_var.get(),
            'firstname': self.athlete_firstname_var.get(),
            'birthdate': self.athlete_birth_var.get(),
            'gender': self.athlete_gender_var.get(),
            'club': self.athlete_club_var.get()
        })
        self.refresh_athletes_display()
        self.refresh_entry_combos()
        
    def delete_athlete(self):
        selection = self.athletes_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select an athlete to delete")
            return
            
        athlete_id = int(self.athletes_tree.item(selection[0])['text'])
        if messagebox.askyesno("Confirm", "Delete selected athlete?"):
            del self.athletes[athlete_id]
            self.refresh_athletes_display()
            self.refresh_entry_combos()
            
    def on_athlete_select(self, event):
        selection = self.athletes_tree.selection()
        if selection:
            athlete_id = int(self.athletes_tree.item(selection[0])['text'])
            athlete = self.athletes[athlete_id]
            
            self.athlete_lastname_var.set(athlete['lastname'])
            self.athlete_firstname_var.set(athlete['firstname'])
            self.athlete_birth_var.set(athlete['birthdate'])
            self.athlete_gender_var.set(athlete['gender'])
            self.athlete_club_var.set(athlete['club'])
            
    def clear_athlete_form(self):
        self.athlete_lastname_var.set("")
        self.athlete_firstname_var.set("")
        self.athlete_birth_var.set("")
        self.athlete_gender_var.set("")
        self.athlete_club_var.set("")
        
    # Event management methods
    def add_event(self):
        if not self.event_number_var.get() or not self.event_distance_var.get():
            messagebox.showerror("Error", "Please fill in required fields")
            return
            
        event_id = self.next_event_id
        self.events[event_id] = {
            'id': event_id,
            'number': int(self.event_number_var.get()),
            'gender': self.event_gender_var.get(),
            'distance': int(self.event_distance_var.get()),
            'stroke': self.event_stroke_var.get(),
            'round': self.event_round_var.get()
        }
        self.next_event_id += 1
        self.refresh_events_display()
        self.refresh_entry_combos()
        self.clear_event_form()
        
    def update_event(self):
        selection = self.events_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select an event to update")
            return
            
        event_id = int(self.events_tree.item(selection[0])['text'])
        self.events[event_id].update({
            'number': int(self.event_number_var.get()),
            'gender': self.event_gender_var.get(),
            'distance': int(self.event_distance_var.get()),
            'stroke': self.event_stroke_var.get(),
            'round': self.event_round_var.get()
        })
        self.refresh_events_display()
        self.refresh_entry_combos()
        
    def delete_event(self):
        selection = self.events_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select an event to delete")
            return
            
        event_id = int(self.events_tree.item(selection[0])['text'])
        if messagebox.askyesno("Confirm", "Delete selected event?"):
            del self.events[event_id]
            self.refresh_events_display()
            self.refresh_entry_combos()
            
    def on_event_select(self, event):
        selection = self.events_tree.selection()
        if selection:
            event_id = int(self.events_tree.item(selection[0])['text'])
            event_data = self.events[event_id]
            
            self.event_number_var.set(str(event_data['number']))
            self.event_gender_var.set(event_data['gender'])
            self.event_distance_var.set(str(event_data['distance']))
            self.event_stroke_var.set(event_data['stroke'])
            self.event_round_var.set(event_data['round'])
            
    def clear_event_form(self):
        self.event_number_var.set("")
        self.event_gender_var.set("")
        self.event_distance_var.set("")
        self.event_stroke_var.set("")
        self.event_round_var.set("TIM")
        
    # Entry management methods
    def add_entry(self):
        athlete_text = self.entry_athlete_var.get()
        event_text = self.entry_event_var.get()
        
        if not athlete_text or not event_text:
            messagebox.showerror("Error", "Please select athlete and event")
            return
            
        # Extract IDs from combo text
        athlete_id = int(athlete_text.split(":")[0])
        event_id = int(event_text.split(":")[0])
        
        entry_id = self.next_entry_id
        self.entries[entry_id] = {
            'id': entry_id,
            'athlete_id': athlete_id,
            'event_id': event_id,
            'entrytime': self.entry_time_var.get() or "NT"
        }
        self.next_entry_id += 1
        self.refresh_entries_display()
        self.clear_entry_form()
        
    def update_entry(self):
        selection = self.entries_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select an entry to update")
            return
            
        entry_id = int(self.entries_tree.item(selection[0])['text'])
        athlete_text = self.entry_athlete_var.get()
        event_text = self.entry_event_var.get()
        
        if athlete_text and event_text:
            athlete_id = int(athlete_text.split(":")[0])
            event_id = int(event_text.split(":")[0])
            
            self.entries[entry_id].update({
                'athlete_id': athlete_id,
                'event_id': event_id,
                'entrytime': self.entry_time_var.get() or "NT"
            })
            self.refresh_entries_display()
        
    def delete_entry(self):
        selection = self.entries_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select an entry to delete")
            return
            
        entry_id = int(self.entries_tree.item(selection[0])['text'])
        if messagebox.askyesno("Confirm", "Delete selected entry?"):
            del self.entries[entry_id]
            self.refresh_entries_display()
            
    def on_entry_select(self, event):
        selection = self.entries_tree.selection()
        if selection:
            entry_id = int(self.entries_tree.item(selection[0])['text'])
            entry_data = self.entries[entry_id]
            
            # Set athlete combo
            athlete = self.athletes[entry_data['athlete_id']]
            athlete_text = f"{entry_data['athlete_id']}: {athlete['lastname']}, {athlete['firstname']}"
            self.entry_athlete_var.set(athlete_text)
            
            # Set event combo
            event_data = self.events[entry_data['event_id']]
            event_text = f"{entry_data['event_id']}: Event {event_data['number']} - {event_data['distance']}m {event_data['stroke']}"
            self.entry_event_var.set(event_text)
            
            self.entry_time_var.set(entry_data['entrytime'])
            
    def clear_entry_form(self):
        self.entry_athlete_var.set("")
        self.entry_event_var.set("")
        self.entry_time_var.set("")
        
    # Result management methods
    def add_result(self):
        athlete_text = self.result_athlete_var.get()
        event_text = self.result_event_var.get()
        
        if not athlete_text or not event_text:
            messagebox.showerror("Error", "Please select athlete and event")
            return
            
        athlete_id = int(athlete_text.split(":")[0])
        event_id = int(event_text.split(":")[0])
        
        result_id = self.next_result_id
        self.results[result_id] = {
            'id': result_id,
            'athlete_id': athlete_id,
            'event_id': event_id,
            'swimtime': self.result_time_var.get() or "NT",
            'place': int(self.result_place_var.get()) if self.result_place_var.get() else 0
        }
        self.next_result_id += 1
        self.refresh_results_display()
        self.clear_result_form()
        
    def update_result(self):
        selection = self.results_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a result to update")
            return
            
        result_id = int(self.results_tree.item(selection[0])['text'])
        athlete_text = self.result_athlete_var.get()
        event_text = self.result_event_var.get()
        
        if athlete_text and event_text:
            athlete_id = int(athlete_text.split(":")[0])
            event_id = int(event_text.split(":")[0])
            
            self.results[result_id].update({
                'athlete_id': athlete_id,
                'event_id': event_id,
                'swimtime': self.result_time_var.get() or "NT",
                'place': int(self.result_place_var.get()) if self.result_place_var.get() else 0
            })
            self.refresh_results_display()
        
    def delete_result(self):
        selection = self.results_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a result to delete")
            return
            
        result_id = int(self.results_tree.item(selection[0])['text'])
        if messagebox.askyesno("Confirm", "Delete selected result?"):
            del self.results[result_id]
            self.refresh_results_display()
            
    def on_result_select(self, event):
        selection = self.results_tree.selection()
        if selection:
            result_id = int(self.results_tree.item(selection[0])['text'])
            result_data = self.results[result_id]
            
            # Set athlete combo
            athlete = self.athletes[result_data['athlete_id']]
            athlete_text = f"{result_data['athlete_id']}: {athlete['lastname']}, {athlete['firstname']}"
            self.result_athlete_var.set(athlete_text)
            
            # Set event combo
            event_data = self.events[result_data['event_id']]
            event_text = f"{result_data['event_id']}: Event {event_data['number']} - {event_data['distance']}m {event_data['stroke']}"
            self.result_event_var.set(event_text)
            
            self.result_time_var.set(result_data['swimtime'])
            self.result_place_var.set(str(result_data['place']))
            
    def clear_result_form(self):
        self.result_athlete_var.set("")
        self.result_event_var.set("")
        self.result_time_var.set("")
        self.result_place_var.set("")
        
    # Display refresh methods
    def refresh_all_displays(self):
        self.refresh_athletes_display()
        self.refresh_events_display()
        self.refresh_entries_display()
        self.refresh_results_display()
        self.refresh_sessions_display()
        self.refresh_entry_combos()
        
    def refresh_athletes_display(self):
        # Clear existing items
        for item in self.athletes_tree.get_children():
            self.athletes_tree.delete(item)
            
        # Add athletes
        for athlete_id, athlete in self.athletes.items():
            self.athletes_tree.insert("", "end", text=str(athlete_id),
                                    values=(athlete['lastname'], athlete['firstname'],
                                           athlete['birthdate'], athlete['gender'], athlete['club']))
                                           
    def refresh_events_display(self):
        # Clear existing items
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)
            
        # Add events
        for event_id, event in self.events.items():
            self.events_tree.insert("", "end", text=str(event_id),
                                   values=(event['number'], event['gender'],
                                          event['distance'], event['stroke'], event['round']))
                                          
    def refresh_entries_display(self):
        # Clear existing items
        for item in self.entries_tree.get_children():
            self.entries_tree.delete(item)
            
        # Add entries
        for entry_id, entry in self.entries.items():
            if entry['athlete_id'] in self.athletes and entry['event_id'] in self.events:
                athlete = self.athletes[entry['athlete_id']]
                event = self.events[entry['event_id']]
                athlete_name = f"{athlete['lastname']}, {athlete['firstname']}"
                event_name = f"Event {event['number']} - {event['distance']}m {event['stroke']}"
                
                self.entries_tree.insert("", "end", text=str(entry_id),
                                       values=(athlete_name, event_name, entry['entrytime']))
                                       
    def refresh_results_display(self):
        # Clear existing items
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
        # Add results
        for result_id, result in self.results.items():
            if result['athlete_id'] in self.athletes and result['event_id'] in self.events:
                athlete = self.athletes[result['athlete_id']]
                event = self.events[result['event_id']]
                athlete_name = f"{athlete['lastname']}, {athlete['firstname']}"
                event_name = f"Event {event['number']} - {event['distance']}m {event['stroke']}"
                
                self.results_tree.insert("", "end", text=str(result_id),
                                       values=(athlete_name, event_name, result['swimtime'], result['place']))
                                       
    def refresh_sessions_display(self):
        # Clear existing items
        for item in self.sessions_tree.get_children():
            self.sessions_tree.delete(item)
            
        # Add sessions
        for session_id, session in self.sessions.items():
            if self.current_meet_id and session['meet_id'] == self.current_meet_id:
                self.sessions_tree.insert("", "end", text=str(session_id),
                                        values=(session['date'], session['daytime'], session['name']))
                                        
    def refresh_entry_combos(self):
        # Update athlete combos
        athlete_values = []
        for athlete_id, athlete in self.athletes.items():
            athlete_values.append(f"{athlete_id}: {athlete['lastname']}, {athlete['firstname']}")
            
        self.entry_athlete_combo['values'] = athlete_values
        self.result_athlete_combo['values'] = athlete_values
        
        # Update event combos
        event_values = []
        for event_id, event in self.events.items():
            event_values.append(f"{event_id}: Event {event['number']} - {event['distance']}m {event['stroke']}")
            
        self.entry_event_combo['values'] = event_values
        self.result_event_combo['values'] = event_values
        
    # Import/Export methods
    def import_athletes_csv(self):
        filename = filedialog.askopenfilename(
            title="Import Athletes CSV",
            filetypes=[("CSV files", "*.csv")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    count = 0
                    for row in reader:
                        athlete_id = self.next_athlete_id
                        self.athletes[athlete_id] = {
                            'id': athlete_id,
                            'lastname': row.get('lastname', ''),
                            'firstname': row.get('firstname', ''),
                            'birthdate': row.get('birthdate', ''),
                            'gender': row.get('gender', ''),
                            'club': row.get('club', '')
                        }
                        self.next_athlete_id += 1
                        count += 1
                    
                    self.refresh_athletes_display()
                    self.refresh_entry_combos()
                    messagebox.showinfo("Success", f"Imported {count} athletes successfully!")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import CSV: {str(e)}")
                
    def import_entries_csv(self):
        filename = filedialog.askopenfilename(
            title="Import Entries CSV",
            filetypes=[("CSV files", "*.csv")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    count = 0
                    for row in reader:
                        athlete_id = int(row.get('athlete_id', 0))
                        event_id = int(row.get('event_id', 0))
                        
                        if athlete_id in self.athletes and event_id in self.events:
                            entry_id = self.next_entry_id
                            self.entries[entry_id] = {
                                'id': entry_id,
                                'athlete_id': athlete_id,
                                'event_id': event_id,
                                'entrytime': row.get('entrytime', 'NT')
                            }
                            self.next_entry_id += 1
                            count += 1
                    
                    self.refresh_entries_display()
                    messagebox.showinfo("Success", f"Imported {count} entries successfully!")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import CSV: {str(e)}")
                
    def export_entries_csv(self):
        filename = filedialog.asksaveasfilename(
            title="Export Entries CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['entry_id', 'athlete_id', 'athlete_name', 'event_id', 'event_description', 'entrytime'])
                    
                    for entry_id, entry in self.entries.items():
                        athlete = self.athletes[entry['athlete_id']]
                        event = self.events[entry['event_id']]
                        athlete_name = f"{athlete['lastname']}, {athlete['firstname']}"
                        event_desc = f"Event {event['number']} - {event['distance']}m {event['stroke']}"
                        
                        writer.writerow([entry_id, entry['athlete_id'], athlete_name,
                                       entry['event_id'], event_desc, entry['entrytime']])
                    
                messagebox.showinfo("Success", "Entries exported successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")
                
    def import_results_csv(self):
        filename = filedialog.askopenfilename(
            title="Import Results CSV",
            filetypes=[("CSV files", "*.csv")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    count = 0
                    for row in reader:
                        athlete_id = int(row.get('athlete_id', 0))
                        event_id = int(row.get('event_id', 0))
                        
                        if athlete_id in self.athletes and event_id in self.events:
                            result_id = self.next_result_id
                            self.results[result_id] = {
                                'id': result_id,
                                'athlete_id': athlete_id,
                                'event_id': event_id,
                                'swimtime': row.get('swimtime', 'NT'),
                                'place': int(row.get('place', 0))
                            }
                            self.next_result_id += 1
                            count += 1
                    
                    self.refresh_results_display()
                    messagebox.showinfo("Success", f"Imported {count} results successfully!")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import CSV: {str(e)}")
                
    def export_results_csv(self):
        filename = filedialog.asksaveasfilename(
            title="Export Results CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['result_id', 'athlete_id', 'athlete_name', 'event_id', 'event_description', 'swimtime', 'place'])
                    
                    for result_id, result in self.results.items():
                        athlete = self.athletes[result['athlete_id']]
                        event = self.events[result['event_id']]
                        athlete_name = f"{athlete['lastname']}, {athlete['firstname']}"
                        event_desc = f"Event {event['number']} - {event['distance']}m {event['stroke']}"
                        
                        writer.writerow([result_id, result['athlete_id'], athlete_name,
                                       result['event_id'], event_desc, result['swimtime'], result['place']])
                    
                messagebox.showinfo("Success", "Results exported successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")
                
    # LENEX file operations
    def save_meet(self):
        if not self.current_meet_id:
            messagebox.showerror("Error", "No meet to save")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Save Meet",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if filename:
            try:
                data = {
                    'meets': self.meets,
                    'athletes': self.athletes,
                    'events': self.events,
                    'entries': self.entries,
                    'results': self.results,
                    'sessions': self.sessions,
                    'current_meet_id': self.current_meet_id,
                    'next_ids': {
                        'meet': self.next_meet_id,
                        'athlete': self.next_athlete_id,
                        'event': self.next_event_id,
                        'entry': self.next_entry_id,
                        'result': self.next_result_id,
                        'session': self.next_session_id
                    }
                }
                
                with open(filename, 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=2)
                    
                messagebox.showinfo("Success", "Meet saved successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save meet: {str(e)}")
                
    def open_meet(self):
        filename = filedialog.askopenfilename(
            title="Open Meet",
            filetypes=[("JSON files", "*.json")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    
                self.meets = {int(k): v for k, v in data.get('meets', {}).items()}
                self.athletes = {int(k): v for k, v in data.get('athletes', {}).items()}
                self.events = {int(k): v for k, v in data.get('events', {}).items()}
                self.entries = {int(k): v for k, v in data.get('entries', {}).items()}
                self.results = {int(k): v for k, v in data.get('results', {}).items()}
                self.sessions = {int(k): v for k, v in data.get('sessions', {}).items()}
                self.current_meet_id = data.get('current_meet_id')
                
                next_ids = data.get('next_ids', {})
                self.next_meet_id = next_ids.get('meet', 1)
                self.next_athlete_id = next_ids.get('athlete', 1)
                self.next_event_id = next_ids.get('event', 1)
                self.next_entry_id = next_ids.get('entry', 1)
                self.next_result_id = next_ids.get('result', 1)
                self.next_session_id = next_ids.get('session', 1)
                
                # Load meet details into form
                if self.current_meet_id and self.current_meet_id in self.meets:
                    meet = self.meets[self.current_meet_id]
                    self.meet_name_var.set(meet.get('name', ''))
                    self.meet_city_var.set(meet.get('city', ''))
                    self.meet_nation_var.set(meet.get('nation', ''))
                    self.meet_course_var.set(meet.get('course', 'LCM'))
                    self.meet_deadline_var.set(meet.get('deadline', ''))
                
                self.refresh_all_displays()
                messagebox.showinfo("Success", "Meet loaded successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open meet: {str(e)}")
                
    def export_lenex(self):
        if not self.current_meet_id:
            messagebox.showerror("Error", "No meet to export")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Export LENEX",
            defaultextension=".lef",
            filetypes=[("LENEX files", "*.lef")]
        )
        if filename:
            try:
                self.create_lenex_file(filename)
                messagebox.showinfo("Success", "LENEX file exported successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export LENEX: {str(e)}")
                
    def create_lenex_file(self, filename):
        # Create root element
        root = ET.Element("LENEX", version="3.0")
        
        # Constructor
        constructor = ET.SubElement(root, "CONSTRUCTOR", name="LENEX Swimming Meet Manager", version="1.0")
        contact = ET.SubElement(constructor, "CONTACT", 
                               name="LENEX Manager User", 
                               email="user@example.com")
        
        # Meets
        meets_elem = ET.SubElement(root, "MEETS")
        
        if self.current_meet_id in self.meets:
            meet_data = self.meets[self.current_meet_id]
            meet_elem = ET.SubElement(meets_elem, "MEET",
                                    city=meet_data.get('city', ''),
                                    course=meet_data.get('course', 'LCM'),
                                    name=meet_data.get('name', ''),
                                    nation=meet_data.get('nation', ''),
                                    timing=meet_data.get('timing', 'MANUAL1'))
            
            if meet_data.get('deadline'):
                meet_elem.set('deadline', meet_data['deadline'])
            
            # Pool
            pool_elem = ET.SubElement(meet_elem, "POOL", lanemax="6", lanemin="1")
            
            # Clubs and Athletes
            clubs_elem = ET.SubElement(meet_elem, "CLUBS")
            club_athletes = {}
            
            # Group athletes by club
            for athlete_id, athlete in self.athletes.items():
                club_name = athlete.get('club', 'Unknown Club')
                if club_name not in club_athletes:
                    club_athletes[club_name] = []
                club_athletes[club_name].append((athlete_id, athlete))
            
            # Create club elements
            for club_name, athletes in club_athletes.items():
                club_elem = ET.SubElement(clubs_elem, "CLUB", name=club_name, nation="SVK")
                athletes_elem = ET.SubElement(club_elem, "ATHLETES")
                
                for athlete_id, athlete in athletes:
                    athlete_elem = ET.SubElement(athletes_elem, "ATHLETE",
                                               athleteid=str(athlete_id),
                                               lastname=athlete.get('lastname', ''),
                                               firstname=athlete.get('firstname', ''),
                                               gender=athlete.get('gender', 'M'))
                    
                    if athlete.get('birthdate'):
                        athlete_elem.set('birthdate', athlete['birthdate'])
                    
                    # Add entries for this athlete
                    athlete_entries = [e for e in self.entries.values() if e['athlete_id'] == athlete_id]
                    if athlete_entries:
                        entries_elem = ET.SubElement(athlete_elem, "ENTRIES")
                        for entry in athlete_entries:
                            entry_elem = ET.SubElement(entries_elem, "ENTRY",
                                                     eventid=str(entry['event_id']),
                                                     entrytime=entry.get('entrytime', 'NT'))
                    
                    # Add results for this athlete
                    athlete_results = [r for r in self.results.values() if r['athlete_id'] == athlete_id]
                    if athlete_results:
                        results_elem = ET.SubElement(athlete_elem, "RESULTS")
                        for result in athlete_results:
                            result_elem = ET.SubElement(results_elem, "RESULT",
                                                      resultid=str(result['id']),
                                                      eventid=str(result['event_id']),
                                                      swimtime=result.get('swimtime', 'NT'))
            
            # Sessions and Events
            sessions_elem = ET.SubElement(meet_elem, "SESSIONS")
            meet_sessions = [s for s in self.sessions.values() if s['meet_id'] == self.current_meet_id]
            
            if meet_sessions:
                session = meet_sessions[0]  # Use first session
            else:
                # Create default session
                session = {
                    'number': 1,
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'daytime': '10:00',
                    'name': 'Session 1'
                }
            
            session_elem = ET.SubElement(sessions_elem, "SESSION",
                                       number=str(session['number']),
                                       date=session['date'])
            
            if session.get('daytime'):
                session_elem.set('daytime', session['daytime'])
            if session.get('name'):
                session_elem.set('name', session['name'])
            
            # Events
            events_elem = ET.SubElement(session_elem, "EVENTS")
            for event_id, event in self.events.items():
                event_elem = ET.SubElement(events_elem, "EVENT",
                                         eventid=str(event_id),
                                         number=str(event['number']),
                                         gender=event.get('gender', 'A'),
                                         round=event.get('round', 'TIM'))
                
                # Swimstyle
                swimstyle_elem = ET.SubElement(event_elem, "SWIMSTYLE",
                                             distance=str(event['distance']),
                                             stroke=event.get('stroke', 'FREE'),
                                             relaycount="1")
        
        # Write XML with Windows-1250 encoding
        tree = ET.ElementTree(root)
        with open(filename, 'wb') as f:
            f.write('<?xml version="1.0" encoding="Windows-1250"?>\n'.encode('windows-1250'))
            tree.write(f, encoding='windows-1250', xml_declaration=False)
            
    def import_lenex(self):
        filename = filedialog.askopenfilename(
            title="Import LENEX",
            filetypes=[("LENEX files", "*.lef"), ("XML files", "*.xml")]
        )
        if filename:
            try:
                self.parse_lenex_file(filename)
                messagebox.showinfo("Success", "LENEX file imported successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import LENEX: {str(e)}")
                
    def parse_lenex_file(self, filename):
        try:
            # Try Windows-1250 encoding first
            with open(filename, 'r', encoding='windows-1250') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Fallback to UTF-8
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
        
        root = ET.fromstring(content)
        
        # Clear existing data
        self.athletes = {}
        self.events = {}
        self.entries = {}
        self.results = {}
        self.sessions = {}
        
        # Parse meets
        meets = root.find('MEETS')
        if meets is not None:
            for meet_elem in meets.findall('MEET'):
                # Create meet
                meet_id = self.next_meet_id
                self.meets[meet_id] = {
                    'id': meet_id,
                    'name': meet_elem.get('name', ''),
                    'city': meet_elem.get('city', ''),
                    'nation': meet_elem.get('nation', ''),
                    'course': meet_elem.get('course', 'LCM'),
                    'deadline': meet_elem.get('deadline', ''),
                    'timing': meet_elem.get('timing', 'MANUAL1')
                }
                self.current_meet_id = meet_id
                self.next_meet_id += 1
                
                # Load meet details into form
                self.meet_name_var.set(self.meets[meet_id]['name'])
                self.meet_city_var.set(self.meets[meet_id]['city'])
                self.meet_nation_var.set(self.meets[meet_id]['nation'])
                self.meet_course_var.set(self.meets[meet_id]['course'])
                self.meet_deadline_var.set(self.meets[meet_id]['deadline'])
                
                # Parse sessions and events
                sessions = meet_elem.find('SESSIONS')
                if sessions is not None:
                    for session_elem in sessions.findall('SESSION'):
                        session_id = self.next_session_id
                        self.sessions[session_id] = {
                            'id': session_id,
                            'meet_id': meet_id,
                            'number': int(session_elem.get('number', 1)),
                            'date': session_elem.get('date', ''),
                            'daytime': session_elem.get('daytime', ''),
                            'name': session_elem.get('name', '')
                        }
                        self.next_session_id += 1
                        
                        # Parse events
                        events = session_elem.find('EVENTS')
                        if events is not None:
                            for event_elem in events.findall('EVENT'):
                                event_id = int(event_elem.get('eventid', self.next_event_id))
                                
                                # Get swimstyle info
                                swimstyle = event_elem.find('SWIMSTYLE')
                                distance = 50
                                stroke = 'FREE'
                                if swimstyle is not None:
                                    distance = int(swimstyle.get('distance', 50))
                                    stroke = swimstyle.get('stroke', 'FREE')
                                
                                self.events[event_id] = {
                                    'id': event_id,
                                    'number': int(event_elem.get('number', event_id)),
                                    'gender': event_elem.get('gender', 'A'),
                                    'distance': distance,
                                    'stroke': stroke,
                                    'round': event_elem.get('round', 'TIM')
                                }
                                
                                if event_id >= self.next_event_id:
                                    self.next_event_id = event_id + 1
                
                # Parse clubs and athletes
                clubs = meet_elem.find('CLUBS')
                if clubs is not None:
                    for club_elem in clubs.findall('CLUB'):
                        club_name = club_elem.get('name', 'Unknown Club')
                        
                        athletes = club_elem.find('ATHLETES')
                        if athletes is not None:
                            for athlete_elem in athletes.findall('ATHLETE'):
                                athlete_id = int(athlete_elem.get('athleteid', self.next_athlete_id))
                                
                                self.athletes[athlete_id] = {
                                    'id': athlete_id,
                                    'lastname': athlete_elem.get('lastname', ''),
                                    'firstname': athlete_elem.get('firstname', ''),
                                    'birthdate': athlete_elem.get('birthdate', ''),
                                    'gender': athlete_elem.get('gender', 'M'),
                                    'club': club_name
                                }
                                
                                if athlete_id >= self.next_athlete_id:
                                    self.next_athlete_id = athlete_id + 1
                                
                                # Parse entries
                                entries = athlete_elem.find('ENTRIES')
                                if entries is not None:
                                    for entry_elem in entries.findall('ENTRY'):
                                        entry_id = self.next_entry_id
                                        event_id = int(entry_elem.get('eventid', 0))
                                        
                                        if event_id in self.events:
                                            self.entries[entry_id] = {
                                                'id': entry_id,
                                                'athlete_id': athlete_id,
                                                'event_id': event_id,
                                                'entrytime': entry_elem.get('entrytime', 'NT')
                                            }
                                            self.next_entry_id += 1
                                
                                # Parse results
                                results = athlete_elem.find('RESULTS')
                                if results is not None:
                                    for result_elem in results.findall('RESULT'):
                                        result_id = int(result_elem.get('resultid', self.next_result_id))
                                        event_id = int(result_elem.get('eventid', 0))
                                        
                                        if event_id in self.events:
                                            self.results[result_id] = {
                                                'id': result_id,
                                                'athlete_id': athlete_id,
                                                'event_id': event_id,
                                                'swimtime': result_elem.get('swimtime', 'NT'),
                                                'place': 0  # Place would need to be calculated
                                            }
                                            
                                            if result_id >= self.next_result_id:
                                                self.next_result_id = result_id + 1
        
        self.refresh_all_displays()


class SessionDialog:
    def __init__(self, parent, title, session_data=None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"400x300+{x}+{y}")
        
        # Form fields
        frame = ttk.LabelFrame(self.dialog, text="Session Details")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Session Number:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.number_var = tk.StringVar(value=str(session_data.get('number', 1)) if session_data else "1")
        ttk.Entry(frame, textvariable=self.number_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(frame, text="Date:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_var = tk.StringVar(value=session_data.get('date', '') if session_data else datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(frame, textvariable=self.date_var, width=15).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(frame, text="(YYYY-MM-DD)").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(frame, text="Start Time:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.daytime_var = tk.StringVar(value=session_data.get('daytime', '') if session_data else "10:00")
        ttk.Entry(frame, textvariable=self.daytime_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(frame, text="(HH:MM)").grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(frame, text="Session Name:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_var = tk.StringVar(value=session_data.get('name', '') if session_data else "")
        ttk.Entry(frame, textvariable=self.name_var, width=30).grid(row=3, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # Wait for dialog to close
        self.dialog.wait_window()
        
    def ok_clicked(self):
        try:
            self.result = {
                'number': int(self.number_var.get()),
                'date': self.date_var.get(),
                'daytime': self.daytime_var.get(),
                'name': self.name_var.get()
            }
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid session number")
            
    def cancel_clicked(self):
        self.dialog.destroy()


def main():
    root = tk.Tk()
    app = LenexManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()