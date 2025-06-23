import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import json
import os
from collections import defaultdict

class SchedulingPredictorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Scheduling Predictor Pro")
        self.root.geometry("1400x800")
        
        # Data structures
        self.employees = ['MA-01', 'MA-02', 'MA-03', 'MA-04', 'MA-05', 
                         'MA-06', 'MA-07', 'MA-08', 'MA-09', 'MA-10']
        self.departments = ['Besprechung', 'Etiketten stecken', 'Kassenaufsicht', 
                           'Marktleitung', 'Qualitätssicherung', 'Sonderaufgabe', 
                           'Warenannahme']
        self.months = ['January', 'February', 'March', 'April', 'May']
        
        # Initialize data storage
        self.historical_data = self.initialize_empty_data()
        self.predictions = {}
        
        # Priority weights
        self.priority_weights = {
            'Marktleitung': 1.50,
            'Kassenaufsicht': 1.40,
            'Warenannahme': 1.30,
            'Sonderaufgabe': 1.20,
            'Etiketten stecken': 1.10,
            'Qualitätssicherung': 1.00,
            'Besprechung': 0.90
        }
        
        # Create UI
        self.setup_ui()
        self.load_sample_data()
        
    def initialize_empty_data(self):
        """Initialize empty data structure"""
        data = {}
        for emp in self.employees:
            data[emp] = {}
            for dept in self.departments:
                data[emp][dept] = [0.0] * 5  # 5 months of data
        return data
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create tabs
        self.data_tab = ttk.Frame(self.notebook)
        self.predictions_tab = ttk.Frame(self.notebook)
        self.analytics_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.data_tab, text='📊 Data Entry')
        self.notebook.add(self.predictions_tab, text='🔮 Predictions')
        self.notebook.add(self.analytics_tab, text='📈 Analytics')
        self.notebook.add(self.settings_tab, text='⚙️ Settings')
        
        # Setup individual tabs
        self.setup_data_tab()
        self.setup_predictions_tab()
        self.setup_analytics_tab()
        self.setup_settings_tab()
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_data_tab(self):
        """Setup the data entry tab"""
        # Top controls
        controls_frame = tk.Frame(self.data_tab)
        controls_frame.pack(pady=10)
        
        tk.Button(controls_frame, text="📁 Load Data", command=self.load_data,
                 bg="#4CAF50", fg="white", padx=20, pady=10).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="💾 Save Data", command=self.save_data,
                 bg="#2196F3", fg="white", padx=20, pady=10).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="🔄 Load Sample", command=self.load_sample_data,
                 bg="#FF9800", fg="white", padx=20, pady=10).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="🗑️ Clear All", command=self.clear_data,
                 bg="#f44336", fg="white", padx=20, pady=10).pack(side=tk.LEFT, padx=5)
        
        # Employee and month selection
        selection_frame = tk.Frame(self.data_tab)
        selection_frame.pack(pady=10)
        
        tk.Label(selection_frame, text="Employee:").pack(side=tk.LEFT, padx=5)
        self.employee_var = tk.StringVar(value=self.employees[0])
        self.employee_combo = ttk.Combobox(selection_frame, textvariable=self.employee_var,
                                          values=self.employees, width=15)
        self.employee_combo.pack(side=tk.LEFT, padx=5)
        self.employee_combo.bind('<<ComboboxSelected>>', self.update_data_display)
        
        tk.Label(selection_frame, text="Month:").pack(side=tk.LEFT, padx=20)
        self.month_var = tk.StringVar(value=self.months[0])
        self.month_combo = ttk.Combobox(selection_frame, textvariable=self.month_var,
                                       values=self.months, width=15)
        self.month_combo.pack(side=tk.LEFT, padx=5)
        self.month_combo.bind('<<ComboboxSelected>>', self.update_data_display)
        
        # Data entry frame
        self.data_entry_frame = tk.Frame(self.data_tab)
        self.data_entry_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        # Create data entry grid
        self.create_data_entry_grid()
        
        # Summary frame
        summary_frame = tk.LabelFrame(self.data_tab, text="Monthly Summary", padx=10, pady=10)
        summary_frame.pack(pady=10, padx=20, fill='x')
        
        self.summary_label = tk.Label(summary_frame, text="", font=("Arial", 10))
        self.summary_label.pack()
        
    def create_data_entry_grid(self):
        """Create the data entry grid"""
        # Clear existing widgets
        for widget in self.data_entry_frame.winfo_children():
            widget.destroy()
            
        # Headers
        tk.Label(self.data_entry_frame, text="Department", font=("Arial", 10, "bold"),
                bg="#e0e0e0", relief=tk.RAISED).grid(row=0, column=0, sticky='ew', padx=1, pady=1)
        tk.Label(self.data_entry_frame, text="Hours", font=("Arial", 10, "bold"),
                bg="#e0e0e0", relief=tk.RAISED).grid(row=0, column=1, sticky='ew', padx=1, pady=1)
        tk.Label(self.data_entry_frame, text="Priority", font=("Arial", 10, "bold"),
                bg="#e0e0e0", relief=tk.RAISED).grid(row=0, column=2, sticky='ew', padx=1, pady=1)
        
        # Data entry fields
        self.hour_entries = {}
        row = 1
        
        for dept in self.departments:
            # Department name
            dept_label = tk.Label(self.data_entry_frame, text=dept, anchor='w', padx=10)
            dept_label.grid(row=row, column=0, sticky='ew', padx=1, pady=2)
            
            # Hours entry
            entry = tk.Entry(self.data_entry_frame, width=10, justify='center')
            entry.grid(row=row, column=1, padx=5, pady=2)
            entry.bind('<KeyRelease>', lambda e, d=dept: self.update_hours(d))
            self.hour_entries[dept] = entry
            
            # Priority indicator
            priority = self.get_priority_category(dept)
            color = self.get_priority_color(priority)
            priority_label = tk.Label(self.data_entry_frame, text=priority, 
                                    bg=color, fg='white' if priority == 'CRITICAL' else 'black',
                                    padx=10)
            priority_label.grid(row=row, column=2, sticky='ew', padx=5, pady=2)
            
            row += 1
            
        # Configure grid weights
        self.data_entry_frame.grid_columnconfigure(0, weight=2)
        self.data_entry_frame.grid_columnconfigure(1, weight=1)
        self.data_entry_frame.grid_columnconfigure(2, weight=1)
        
        # Update display with current data
        self.update_data_display()
        
    def setup_predictions_tab(self):
        """Setup the predictions tab"""
        # Controls
        controls_frame = tk.Frame(self.predictions_tab)
        controls_frame.pack(pady=10)
        
        tk.Button(controls_frame, text="🔮 Generate Predictions", 
                 command=self.generate_predictions,
                 bg="#4CAF50", fg="white", padx=20, pady=10, 
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        
        tk.Button(controls_frame, text="📊 Export Predictions", 
                 command=self.export_predictions,
                 bg="#2196F3", fg="white", padx=20, pady=10).pack(side=tk.LEFT, padx=5)
        
        # Create predictions display
        pred_frame = tk.Frame(self.predictions_tab)
        pred_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Treeview for predictions
        columns = ('Employee', 'Department', 'Hours', 'Priority', 'Trend', 'Confidence')
        self.pred_tree = ttk.Treeview(pred_frame, columns=columns, show='headings', height=20)
        
        # Configure columns
        self.pred_tree.heading('Employee', text='Employee')
        self.pred_tree.heading('Department', text='Department')
        self.pred_tree.heading('Hours', text='Predicted Hours')
        self.pred_tree.heading('Priority', text='Priority')
        self.pred_tree.heading('Trend', text='Trend')
        self.pred_tree.heading('Confidence', text='Confidence')
        
        self.pred_tree.column('Employee', width=100)
        self.pred_tree.column('Department', width=150)
        self.pred_tree.column('Hours', width=100)
        self.pred_tree.column('Priority', width=80)
        self.pred_tree.column('Trend', width=80)
        self.pred_tree.column('Confidence', width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(pred_frame, orient=tk.VERTICAL, command=self.pred_tree.yview)
        self.pred_tree.configure(yscrollcommand=scrollbar.set)
        
        self.pred_tree.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        
    def setup_analytics_tab(self):
        """Setup the analytics tab with charts"""
        # Create matplotlib figure
        self.fig = Figure(figsize=(12, 8), dpi=100)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.analytics_tab)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
        
        # Controls
        controls_frame = tk.Frame(self.analytics_tab)
        controls_frame.pack(pady=5)
        
        tk.Button(controls_frame, text="📊 Update Charts", command=self.update_charts,
                 bg="#4CAF50", fg="white", padx=20, pady=10).pack(side=tk.LEFT, padx=5)
        
        tk.Label(controls_frame, text="Chart Type:").pack(side=tk.LEFT, padx=10)
        self.chart_type = tk.StringVar(value="overview")
        chart_options = ["overview", "employee_trends", "department_distribution", "priority_analysis"]
        self.chart_combo = ttk.Combobox(controls_frame, textvariable=self.chart_type,
                                       values=chart_options, width=20)
        self.chart_combo.pack(side=tk.LEFT, padx=5)
        self.chart_combo.bind('<<ComboboxSelected>>', lambda e: self.update_charts())
        
    def setup_settings_tab(self):
        """Setup the settings tab"""
        # Priority weights configuration
        weights_frame = tk.LabelFrame(self.settings_tab, text="Priority Weights Configuration", 
                                    padx=20, pady=20)
        weights_frame.pack(pady=20, padx=20, fill='x')
        
        tk.Label(weights_frame, text="Adjust priority multipliers for each department:",
                font=("Arial", 10)).grid(row=0, column=0, columnspan=3, pady=10)
        
        self.weight_vars = {}
        row = 1
        
        for dept, weight in self.priority_weights.items():
            tk.Label(weights_frame, text=f"{dept}:").grid(row=row, column=0, sticky='w', pady=5)
            
            var = tk.DoubleVar(value=weight)
            self.weight_vars[dept] = var
            
            scale = tk.Scale(weights_frame, from_=0.5, to=2.0, resolution=0.1,
                           orient=tk.HORIZONTAL, variable=var, length=200)
            scale.grid(row=row, column=1, padx=10, pady=5)
            
            tk.Label(weights_frame, textvariable=var, width=5).grid(row=row, column=2, pady=5)
            
            row += 1
            
        tk.Button(weights_frame, text="Apply Changes", command=self.update_weights,
                 bg="#4CAF50", fg="white", padx=20, pady=10).grid(row=row, column=0, 
                                                                  columnspan=3, pady=20)
        
    def update_hours(self, department):
        """Update hours when user types"""
        try:
            employee = self.employee_var.get()
            month_idx = self.months.index(self.month_var.get())
            hours = float(self.hour_entries[department].get() or 0)
            self.historical_data[employee][department][month_idx] = hours
            self.update_summary()
        except ValueError:
            pass
            
    def update_data_display(self, event=None):
        """Update the data display when employee or month changes"""
        employee = self.employee_var.get()
        month_idx = self.months.index(self.month_var.get())
        
        # Update all entry fields
        for dept, entry in self.hour_entries.items():
            hours = self.historical_data[employee][dept][month_idx]
            entry.delete(0, tk.END)
            entry.insert(0, str(hours) if hours > 0 else "")
            
        self.update_summary()
        
    def update_summary(self):
        """Update the summary information"""
        employee = self.employee_var.get()
        month_idx = self.months.index(self.month_var.get())
        
        total_hours = 0
        dept_count = 0
        
        for dept in self.departments:
            hours = self.historical_data[employee][dept][month_idx]
            if hours > 0:
                total_hours += hours
                dept_count += 1
                
        summary_text = f"Total Hours: {total_hours:.2f} | Active Departments: {dept_count} | Average: {total_hours/dept_count if dept_count > 0 else 0:.2f}"
        self.summary_label.config(text=summary_text)
        
    def generate_predictions(self):
        """Generate predictions using the weighted algorithm"""
        self.predictions = {}
        
        # Clear existing predictions
        for item in self.pred_tree.get_children():
            self.pred_tree.delete(item)
            
        for employee, departments in self.historical_data.items():
            self.predictions[employee] = {}
            
            for department, hours in departments.items():
                # Skip if no historical data
                if all(h == 0 for h in hours):
                    continue
                    
                # Calculate weighted moving average
                weights = [1, 1.5, 2, 3, 6]  # Double weight for May
                weighted_sum = sum(h * w for h, w in zip(hours, weights))
                total_weight = sum(weights)
                base_prediction = weighted_sum / total_weight
                
                # Apply priority weight
                priority_weight = self.priority_weights.get(department, 1.0)
                adjusted_prediction = base_prediction * priority_weight
                
                # Calculate trend
                if hours[4] > hours[3]:
                    trend = "📈 Up"
                elif hours[4] < hours[3]:
                    trend = "📉 Down"
                else:
                    trend = "➡️ Stable"
                    
                # Calculate confidence
                active_months = sum(1 for h in hours if h > 0)
                confidence = f"{(active_months / 5 * 100):.0f}%"
                
                # Store prediction
                self.predictions[employee][department] = {
                    'hours': adjusted_prediction,
                    'trend': trend,
                    'confidence': confidence
                }
                
                # Add to tree
                priority = self.get_priority_category(department)
                tag = priority.lower().replace(' ', '_')
                
                self.pred_tree.insert('', 'end', 
                                    values=(employee, department, f"{adjusted_prediction:.2f}",
                                           priority, trend, confidence),
                                    tags=(tag,))
                
        # Configure tags for colors
        self.pred_tree.tag_configure('critical', background='#ffcdd2')
        self.pred_tree.tag_configure('high', background='#fff3cd')
        self.pred_tree.tag_configure('medium', background='#d1ecf1')
        self.pred_tree.tag_configure('low', background='#d4edda')
        
        self.status_bar.config(text="Predictions generated successfully")
        messagebox.showinfo("Success", "Predictions generated for June 2025!")
        
        # Update charts
        self.update_charts()
        
    def update_charts(self):
        """Update analytics charts"""
        self.fig.clear()
        chart_type = self.chart_type.get()
        
        if chart_type == "overview":
            self.create_overview_charts()
        elif chart_type == "employee_trends":
            self.create_employee_trends()
        elif chart_type == "department_distribution":
            self.create_department_distribution()
        elif chart_type == "priority_analysis":
            self.create_priority_analysis()
            
        self.canvas.draw()
        
    def create_overview_charts(self):
        """Create overview charts"""
        # Create 2x2 subplot
        ax1 = self.fig.add_subplot(221)
        ax2 = self.fig.add_subplot(222)
        ax3 = self.fig.add_subplot(223)
        ax4 = self.fig.add_subplot(224)
        
        # 1. Total hours by employee
        employees = []
        total_hours = []
        
        for emp in self.employees:
            hours = sum(sum(self.historical_data[emp][dept]) for dept in self.departments)
            if hours > 0:
                employees.append(emp)
                total_hours.append(hours)
                
        ax1.bar(employees, total_hours, color='skyblue')
        ax1.set_title('Total Hours by Employee (5 months)')
        ax1.set_xlabel('Employee')
        ax1.set_ylabel('Hours')
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. Department workload
        dept_hours = {}
        for dept in self.departments:
            hours = sum(sum(self.historical_data[emp][dept] for emp in self.employees))
            if hours > 0:
                dept_hours[dept] = hours
                
        if dept_hours:
            ax2.pie(dept_hours.values(), labels=dept_hours.keys(), autopct='%1.1f%%')
            ax2.set_title('Department Workload Distribution')
        
        # 3. Monthly trends
        monthly_totals = []
        for month_idx in range(5):
            total = sum(self.historical_data[emp][dept][month_idx] 
                       for emp in self.employees 
                       for dept in self.departments)
            monthly_totals.append(total)
            
        ax3.plot(self.months, monthly_totals, marker='o', linewidth=2, markersize=8)
        ax3.set_title('Total Hours Trend')
        ax3.set_xlabel('Month')
        ax3.set_ylabel('Total Hours')
        ax3.grid(True, alpha=0.3)
        
        # 4. Priority distribution
        priority_hours = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for dept in self.departments:
            priority = self.get_priority_category(dept)
            hours = sum(sum(self.historical_data[emp][dept] for emp in self.employees))
            priority_hours[priority] += hours
            
        colors = ['#ff4444', '#ffaa00', '#0088ff', '#00aa00']
        ax4.bar(priority_hours.keys(), priority_hours.values(), color=colors)
        ax4.set_title('Hours by Priority Level')
        ax4.set_xlabel('Priority')
        ax4.set_ylabel('Total Hours')
        
        self.fig.tight_layout()
        
    def create_employee_trends(self):
        """Create employee trends chart"""
        ax = self.fig.add_subplot(111)
        
        # Plot lines for top 5 employees by total hours
        employee_totals = {}
        for emp in self.employees:
            total = sum(sum(self.historical_data[emp][dept]) for dept in self.departments)
            employee_totals[emp] = total
            
        top_employees = sorted(employee_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for emp, _ in top_employees:
            monthly_hours = []
            for month_idx in range(5):
                hours = sum(self.historical_data[emp][dept][month_idx] for dept in self.departments)
                monthly_hours.append(hours)
            ax.plot(self.months, monthly_hours, marker='o', label=emp, linewidth=2)
            
        ax.set_title('Top 5 Employees - Monthly Hours Trend')
        ax.set_xlabel('Month')
        ax.set_ylabel('Hours')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
    def create_department_distribution(self):
        """Create department distribution chart"""
        ax = self.fig.add_subplot(111)
        
        # Create stacked bar chart
        bottom = np.zeros(len(self.months))
        
        for dept in self.departments:
            monthly_hours = []
            for month_idx in range(5):
                hours = sum(self.historical_data[emp][dept][month_idx] for emp in self.employees)
                monthly_hours.append(hours)
                
            if sum(monthly_hours) > 0:
                ax.bar(self.months, monthly_hours, bottom=bottom, label=dept)
                bottom += np.array(monthly_hours)
                
        ax.set_title('Department Hours Distribution by Month')
        ax.set_xlabel('Month')
        ax.set_ylabel('Hours')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
    def create_priority_analysis(self):
        """Create priority analysis chart"""
        ax1 = self.fig.add_subplot(121)
        ax2 = self.fig.add_subplot(122)
        
        # Priority hours over time
        priority_data = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': []}
        
        for month_idx in range(5):
            monthly_priority = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
            for dept in self.departments:
                priority = self.get_priority_category(dept)
                hours = sum(self.historical_data[emp][dept][month_idx] for emp in self.employees)
                monthly_priority[priority] += hours
                
            for priority in priority_data:
                priority_data[priority].append(monthly_priority[priority])
                
        colors = {'CRITICAL': '#ff4444', 'HIGH': '#ffaa00', 'MEDIUM': '#0088ff', 'LOW': '#00aa00'}
        
        for priority, data in priority_data.items():
            ax1.plot(self.months, data, marker='o', label=priority, 
                    color=colors[priority], linewidth=2)
            
        ax1.set_title('Priority Hours Trend')
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Hours')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Average hours per priority
        avg_hours = {}
        for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            total_hours = 0
            count = 0
            for dept in self.departments:
                if self.get_priority_category(dept) == priority:
                    hours = sum(sum(self.historical_data[emp][dept] for emp in self.employees))
                    total_hours += hours
                    count += 1
            avg_hours[priority] = total_hours / count if count > 0 else 0
            
        ax2.bar(avg_hours.keys(), avg_hours.values(), 
               color=[colors[p] for p in avg_hours.keys()])
        ax2.set_title('Average Hours per Department by Priority')
        ax2.set_xlabel('Priority')
        ax2.set_ylabel('Average Hours')
        
        self.fig.tight_layout()
        
    def get_priority_category(self, department):
        """Get priority category for a department"""
        weight = self.priority_weights.get(department, 1.0)
        if weight >= 1.4:
            return 'CRITICAL'
        elif weight >= 1.3:
            return 'HIGH'
        elif weight >= 1.0:
            return 'MEDIUM'
        else:
            return 'LOW'
            
    def get_priority_color(self, priority):
        """Get color for priority level"""
        colors = {
            'CRITICAL': '#ff4444',
            'HIGH': '#ffaa00',
            'MEDIUM': '#0088ff',
            'LOW': '#00aa00'
        }
        return colors.get(priority, '#666666')
        
    def update_weights(self):
        """Update priority weights from settings"""
        for dept, var in self.weight_vars.items():
            self.priority_weights[dept] = var.get()
            
        # Refresh the data entry grid to show new priorities
        self.create_data_entry_grid()
        
        messagebox.showinfo("Success", "Priority weights updated successfully!")
        
    def load_sample_data(self):
        """Load sample data for demonstration"""
        sample_data = {
            'MA-01': {
                'Besprechung': [0, 0, 0, 0, 0],
                'Etiketten stecken': [0, 0, 0, 0, 0],
                'Kassenaufsicht': [0, 2.50, 0, 0, 0],
                'Marktleitung': [0, 0, 0, 0, 0],
                'Qualitätssicherung': [0, 0, 0, 0, 0],
                'Sonderaufgabe': [0, 0, 0, 0, 0],
                'Warenannahme': [143.25, 139.13, 112.60, 142.73, 141.92]
            },
            'MA-02': {
                'Besprechung': [0, 0, 0, 0, 0],
                'Etiketten stecken': [4.30, 4.27, 0, 0, 4.20],
                'Kassenaufsicht': [115.33, 97.72, 0, 53.05, 114.17],
                'Marktleitung': [20.95, 36.93, 0, 0, 35.07],
                'Qualitätssicherung': [2.00, 0, 0, 0, 0],
                'Sonderaufgabe': [0, 0, 0, 0, 0],
                'Warenannahme': [0, 0, 0, 0, 0]
            },
            'MA-03': {
                'Besprechung': [1.10, 0, 0, 0, 0],
                'Etiketten stecken': [2.18, 2.20, 6.50, 6.55, 4.38],
                'Kassenaufsicht': [92.08, 54.42, 88.52, 87.77, 55.50],
                'Marktleitung': [47.50, 55.72, 66.13, 49.27, 39.40],
                'Qualitätssicherung': [0, 0, 0, 0, 0],
                'Sonderaufgabe': [4.25, 0, 5.50, 4.50, 0],
                'Warenannahme': [0, 0, 9.45, 0, 0]
            },
            'MA-04': {
                'Besprechung': [0, 0, 0, 0, 0],
                'Etiketten stecken': [2.42, 0, 2.45, 2.48, 0],
                'Kassenaufsicht': [12.03, 30.45, 0, 0, 0],
                'Marktleitung': [65.67, 82.65, 84.17, 163.85, 103.13],
                'Qualitätssicherung': [0, 0, 4.50, 0, 0],
                'Sonderaufgabe': [0, 13.52, 0, 0, 0],
                'Warenannahme': [16.05, 6.95, 0, 0, 0]
            },
            'MA-05': {
                'Besprechung': [0, 0, 0, 0, 0],
                'Etiketten stecken': [2.28, 0, 0, 0, 0],
                'Kassenaufsicht': [13.15, 16.88, 0, 0, 0],
                'Marktleitung': [132.37, 44.00, 81.12, 139.28, 161.12],
                'Qualitätssicherung': [0, 0, 0, 0, 0],
                'Sonderaufgabe': [5.10, 4.50, 22.20, 0, 0],
                'Warenannahme': [21.93, 0, 18.03, 0, 0.50]
            },
            'MA-06': {
                'Besprechung': [0, 0, 0, 0, 0],
                'Etiketten stecken': [0, 0, 0, 0, 0],
                'Kassenaufsicht': [6.17, 0, 9.87, 4.13, 0],
                'Marktleitung': [0, 0, 12.92, 0, 0],
                'Qualitätssicherung': [0, 0, 0, 0, 0],
                'Sonderaufgabe': [0, 0, 0, 0, 0],
                'Warenannahme': [0, 0, 0, 0, 0]
            },
            'MA-07': {
                'Besprechung': [0, 0, 0, 0, 0],
                'Etiketten stecken': [0, 2.47, 0, 0, 0],
                'Kassenaufsicht': [0, 0, 0, 0, 0],
                'Marktleitung': [102.58, 75.55, 68.25, 0, 100.78],
                'Qualitätssicherung': [0, 0, 0, 0, 0],
                'Sonderaufgabe': [0, 4.25, 0, 0, 0],
                'Warenannahme': [0.50, 0, 0, 0, 0]
            },
            'MA-08': {
                'Besprechung': [0, 0, 0, 0, 0],
                'Etiketten stecken': [0, 2.37, 0, 0, 0],
                'Kassenaufsicht': [0, 0, 0, 0, 0],
                'Marktleitung': [174.58, 176.15, 163.15, 137.18, 126.10],
                'Qualitätssicherung': [0, 0, 0, 0, 0],
                'Sonderaufgabe': [0, 0, 12.22, 36.22, 13.70],
                'Warenannahme': [0.43, 1.28, 0.82, 0.88, 0]
            },
            'MA-09': {
                'Besprechung': [0, 0, 0, 0, 0],
                'Etiketten stecken': [0, 0, 0, 0, 0],
                'Kassenaufsicht': [0, 0, 0, 0, 0],
                'Marktleitung': [0, 0, 0, 0, 0],
                'Qualitätssicherung': [0, 0, 0, 0, 0],
                'Sonderaufgabe': [0, 0, 0, 0, 0],
                'Warenannahme': [0, 0, 0, 0, 0]
            },
            'MA-10': {
                'Besprechung': [0, 0, 0, 0, 0],
                'Etiketten stecken': [0, 0, 0, 0, 0],
                'Kassenaufsicht': [26.43, 23.98, 0, 5.47, 24.78],
                'Marktleitung': [0, 46.45, 32.68, 80.25, 45.02],
                'Qualitätssicherung': [14.47, 22.12, 23.07, 21.30, 22.32],
                'Sonderaufgabe': [5.07, 10.98, 0, 9.57, 5.33],
                'Warenannahme': [0, 0, 9.17, 0.48, 0.95]
            }
        }
        
        # Update with sample data
        for emp in sample_data:
            if emp in self.historical_data:
                self.historical_data[emp] = sample_data[emp]
                
        self.update_data_display()
        self.status_bar.config(text="Sample data loaded successfully")
        messagebox.showinfo("Success", "Sample data loaded!")
        
    def clear_data(self):
        """Clear all data"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all data?"):
            self.historical_data = self.initialize_empty_data()
            self.update_data_display()
            
            # Clear predictions
            for item in self.pred_tree.get_children():
                self.pred_tree.delete(item)
                
            self.status_bar.config(text="All data cleared")
            
    def save_data(self):
        """Save data to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    with open(filename, 'w') as f:
                        json.dump(self.historical_data, f, indent=2)
                elif filename.endswith('.csv'):
                    # Convert to CSV format
                    rows = []
                    for emp in self.employees:
                        for dept in self.departments:
                            for month_idx, month in enumerate(self.months):
                                hours = self.historical_data[emp][dept][month_idx]
                                if hours > 0:
                                    rows.append({
                                        'Employee': emp,
                                        'Department': dept,
                                        'Month': month,
                                        'Hours': hours
                                    })
                    df = pd.DataFrame(rows)
                    df.to_csv(filename, index=False)
                    
                self.status_bar.config(text=f"Data saved to {os.path.basename(filename)}")
                messagebox.showinfo("Success", "Data saved successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save data: {str(e)}")
                
    def load_data(self):
        """Load data from file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    with open(filename, 'r') as f:
                        loaded_data = json.load(f)
                        
                    # Update historical data
                    for emp in loaded_data:
                        if emp in self.historical_data:
                            self.historical_data[emp] = loaded_data[emp]
                            
                elif filename.endswith('.csv'):
                    df = pd.read_csv(filename)
                    
                    # Clear existing data
                    self.historical_data = self.initialize_empty_data()
                    
                    # Load from CSV
                    for _, row in df.iterrows():
                        emp = row['Employee']
                        dept = row['Department']
                        month = row['Month']
                        hours = row['Hours']
                        
                        if emp in self.employees and dept in self.departments and month in self.months:
                            month_idx = self.months.index(month)
                            self.historical_data[emp][dept][month_idx] = hours
                            
                self.update_data_display()
                self.status_bar.config(text=f"Data loaded from {os.path.basename(filename)}")
                messagebox.showinfo("Success", "Data loaded successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {str(e)}")
                
    def export_predictions(self):
        """Export predictions to file"""
        if not self.predictions:
            messagebox.showwarning("Warning", "No predictions to export. Generate predictions first!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                rows = []
                for employee, departments in self.predictions.items():
                    total_hours = 0
                    for dept, pred_data in departments.items():
                        rows.append({
                            'Employee': employee,
                            'Department': dept,
                            'Predicted Hours': pred_data['hours'],
                            'Priority': self.get_priority_category(dept),
                            'Trend': pred_data['trend'],
                            'Confidence': pred_data['confidence']
                        })
                        total_hours += pred_data['hours']
                        
                    # Add total row
                    rows.append({
                        'Employee': employee,
                        'Department': 'TOTAL',
                        'Predicted Hours': total_hours,
                        'Priority': '',
                        'Trend': '',
                        'Confidence': ''
                    })
                    
                df = pd.DataFrame(rows)
                
                if filename.endswith('.xlsx'):
                    # Create Excel writer with formatting
                    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='Predictions', index=False)
                        
                        # Add summary sheet
                        summary_data = []
                        for emp in self.employees:
                            if emp in self.predictions:
                                total = sum(pred['hours'] for pred in self.predictions[emp].values())
                                summary_data.append({
                                    'Employee': emp,
                                    'Total Predicted Hours': total
                                })
                                
                        summary_df = pd.DataFrame(summary_data)
                        summary_df.to_excel(writer, sheet_name='Summary', index=False)
                        
                else:
                    df.to_csv(filename, index=False)
                    
                self.status_bar.config(text=f"Predictions exported to {os.path.basename(filename)}")
                messagebox.showinfo("Success", "Predictions exported successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export predictions: {str(e)}")

def main():
    root = tk.Tk()
    app = SchedulingPredictorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()