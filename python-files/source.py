import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import hashlib
from datetime import datetime # datetime and time are no longer needed as scheduling is removed

class VotingSystem:
    def __init__(self):
        """Initialize the voting system application."""
        self.voting_open = False
        self.votes = {}
        # Start with a default list, expandable up to 32.
        self.candidates = [f"Candidate {i+1}" for i in range(10)]
        self.total_votes = 0
        self.data_file = "voting_data.json"
        self.password_file = "admin_password.json"
        self.log_file = "voting_log.txt"
        self.admin_password_hash = None
        # Removed attributes related to scheduling:
        # self.start_time_str = None
        # self.end_time_str = None
        # self.schedule_after_id = None

        # Create main Tkinter root but keep it hidden.
        self.root = tk.Tk()
        self.root.withdraw()

        # Initialize the system by setting up password and loading data.
        self.setup_password()
        self.load_data()

        # Windows will be managed as Toplevels.
        self.admin_window = None
        self.voter_window = None

        # Create the primary voter interface.
        self.create_voter_window()
        # Removed call to check_scheduled_times()
        # self.check_scheduled_times() # Start checking scheduled times

    def log_event(self, event_message):
        """Logs an event with a timestamp to the log file."""
        try:
            with open(self.log_file, "a") as log_file:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_file.write(f"[{timestamp}] {event_message}\n")
        except IOError as e:
            # Silently fail or print to console to avoid bothering the user
            print(f"Error: Could not write to log file: {e}")

    def hash_password(self, password):
        """Hashes a password for secure storage using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def setup_password(self):
        """
        Sets up the initial administrator password if it doesn't exist,
        or loads it from the password file.
        """
        if os.path.exists(self.password_file):
            try:
                with open(self.password_file, 'r') as f:
                    data = json.load(f)
                    self.admin_password_hash = data.get('password_hash')
                if not self.admin_password_hash:
                    self.create_initial_password()
            except (json.JSONDecodeError, IOError):
                self.create_initial_password()
        else:
            self.create_initial_password()

    def create_initial_password(self):
        """Prompts for and creates the initial administrator password."""
        temp_root = tk.Tk()
        temp_root.withdraw()
        password = simpledialog.askstring(
            "Initial Administrator Setup",
            "Please set a new administrator password:",
            show='*'
        )
        if password:
            self.admin_password_hash = self.hash_password(password)
            self.save_password()
            messagebox.showinfo("Setup Complete", "Administrator password has been set successfully.")
        else:
            messagebox.showerror("Setup Required", "An administrator password is required. The application will now exit.")
            exit()
        temp_root.destroy()

    def save_password(self):
        """Saves the current admin password hash to its file."""
        try:
            with open(self.password_file, 'w') as f:
                json.dump({'password_hash': self.admin_password_hash}, f)
        except IOError as e:
            messagebox.showerror("File Error", f"Could not save password: {str(e)}")

    def verify_password(self, password):
        """Verifies a given password against the stored hash."""
        return self.hash_password(password) == self.admin_password_hash

    def load_data(self):
        """Loads voting data (candidates, votes) from the data file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.candidates = data.get('candidates', self.candidates)
                    self.votes = data.get('votes', {})
                    self.total_votes = data.get('total_votes', 0)
                    self.voting_open = data.get('voting_open', False)
                    # Removed loading of start and end times
                    # self.start_time_str = data.get('start_time')
                    # self.end_time_str = data.get('end_time')
                    # Ensure votes dictionary is complete for all candidates
                    for candidate in self.candidates:
                        self.votes.setdefault(candidate, 0)
            except (json.JSONDecodeError, IOError) as e:
                messagebox.showwarning("Data Load Error", f"Could not load data: {e}. Starting with fresh data.")
                self.reset_votes_logic() # Use fresh data

    def save_data(self):
        """Saves the current voting data to the data file."""
        data_to_save = {
            'candidates': self.candidates,
            'votes': self.votes,
            'total_votes': self.total_votes,
            'voting_open': self.voting_open,
            # Removed saving of start and end times
            # 'start_time': self.start_time_str,
            # 'end_time': self.end_time_str,
        }
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data_to_save, f, indent=4)
        except IOError as e:
            messagebox.showerror("File Error", f"Could not save data: {str(e)}")

    def on_main_window_close(self):
        """Handles the closing of the main application window."""
        # Removed cancellation of schedule_after_id
        # if self.schedule_after_id:
        #     self.root.after_cancel(self.schedule_after_id)
        self.save_data()
        self.root.quit()
        self.root.destroy()

    def create_voter_window(self):
        """Creates and configures the main voter interface window."""
        self.voter_window = tk.Toplevel(self.root)
        self.voter_window.title("Voting System")
        self.voter_window.geometry("700x800")
        self.voter_window.configure(bg='#f0f8ff')
        self.voter_window.protocol("WM_DELETE_WINDOW", self.on_main_window_close)

        # Configure grid weights for dynamic resizing
        self.voter_window.grid_rowconfigure(3, weight=1)
        self.voter_window.grid_columnconfigure(0, weight=1)

        # --- UI Elements ---
        # Header
        header_frame = tk.Frame(self.voter_window, bg='#2c3e50')
        header_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 5))
        tk.Label(header_frame, text="VOTING SYSTEM", font=('Arial', 28, 'bold'), fg='white', bg='#2c3e50').pack(pady=20)

        # Control Frame (Status and Admin Login)
        control_frame = tk.Frame(self.voter_window, bg='#f0f8ff')
        control_frame.grid(row=1, column=0, sticky='ew', padx=20, pady=5)
        control_frame.grid_columnconfigure(0, weight=1)

        self.voter_status_label = tk.Label(control_frame, font=('Arial', 16, 'bold'), bg='#f0f8ff')
        self.voter_status_label.grid(row=0, column=0, pady=10, sticky='w')

        tk.Button(control_frame, text="Admin Login", command=self.admin_login, font=('Arial', 14, 'bold'), bg='#34495e', fg='white', activebackground='#2c3e50', relief='raised', bd=3).grid(row=0, column=1, pady=10, sticky='e')

        # Instructions
        tk.Label(self.voter_window, text="Select one candidate and click 'Cast Vote'", font=('Arial', 14), bg='#f0f8ff', fg='#2c3e50').grid(row=2, column=0, pady=(10, 5), sticky='w', padx=20)

        # Candidates Area
        candidates_main_frame = tk.Frame(self.voter_window, bg='#ffffff', bd=2, relief='sunken')
        candidates_main_frame.grid(row=3, column=0, sticky='nsew', padx=20, pady=10)
        candidates_main_frame.grid_rowconfigure(0, weight=1)
        candidates_main_frame.grid_columnconfigure(0, weight=1)
        self.setup_candidates_area(candidates_main_frame)

        # Vote Button
        tk.Button(self.voter_window, text="CAST VOTE", command=self.cast_vote, font=('Arial', 16, 'bold'), bg='#27ae60', fg='white', activebackground='#2ecc71', height=2, relief='raised', bd=3).grid(row=4, column=0, pady=20)

        self.update_voter_status()
        self.voter_window.deiconify()

    def setup_candidates_area(self, parent):
        """Sets up the scrollable area for displaying candidates."""
        canvas = tk.Canvas(parent, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        self.scrollable_candidates_frame = tk.Frame(canvas, bg='white')

        self.scrollable_candidates_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_candidates_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Bind mouse wheel scrolling for convenience
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
        
        self.selected_candidate = tk.StringVar()
        self.update_candidate_display()

    def update_candidate_display(self):
        """Updates the radio buttons in the voter and admin interfaces."""
        for widget in self.scrollable_candidates_frame.winfo_children():
            widget.destroy()

        self.scrollable_candidates_frame.grid_columnconfigure(0, weight=1)
        for i, candidate in enumerate(self.candidates):
            rb = tk.Radiobutton(
                self.scrollable_candidates_frame,
                text=f"{i+1:2d}. {candidate}",
                variable=self.selected_candidate,
                value=candidate,
                font=('Arial', 12),
                bg='white',
                activebackground='#e8f4fd',
                padx=20, pady=8, anchor='w'
            )
            rb.grid(row=i, column=0, sticky='ew', padx=10, pady=(2, 3))

    def admin_login(self):
        """Handles the administrator login attempt."""
        password = simpledialog.askstring("Administrator Login", "Enter administrator password:", show='*')
        if password and self.verify_password(password):
            self.open_admin_panel()
        elif password is not None:
            messagebox.showerror("Login Failed", "The password you entered is incorrect.")

    def open_admin_panel(self):
        """Opens the administrator panel window."""
        if self.admin_window and self.admin_window.winfo_exists():
            self.admin_window.lift()
            return

        self.admin_window = tk.Toplevel(self.root)
        self.admin_window.title("Administrator Panel")
        self.admin_window.geometry("900x700")
        self.admin_window.configure(bg='#ecf0f1')
        self.admin_window.grid_rowconfigure(1, weight=1)
        self.admin_window.grid_columnconfigure(0, weight=1)

        # Header
        header_frame = tk.Frame(self.admin_window, bg='#34495e')
        header_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 5))
        tk.Label(header_frame, text="ADMINISTRATOR PANEL", font=('Arial', 24, 'bold'), fg='white', bg='#34495e').pack(pady=20)

        # Notebook for tabs
        notebook = ttk.Notebook(self.admin_window)
        notebook.grid(row=1, column=0, sticky='nsew', padx=15, pady=10)
        
        self.create_voting_control_tab(notebook)
        self.create_secure_admin_tab(notebook)

    def create_voting_control_tab(self, notebook):
        """Creates the 'Voting Control' tab in the admin panel."""
        control_frame = ttk.Frame(notebook, padding=20)
        notebook.add(control_frame, text="Voting Control")
        control_frame.grid_columnconfigure(0, weight=1)
        
        # --- Manual Voting Control ---
        manual_section = tk.LabelFrame(control_frame, text="Voting Control", font=('Arial', 16, 'bold'), fg='#2c3e50', padx=20, pady=20)
        manual_section.grid(row=0, column=0, sticky='ew', pady=(10, 20))
        manual_section.grid_columnconfigure(0, weight=1)

        self.master_toggle_btn = tk.Button(manual_section, command=self.toggle_master_voting, font=('Arial', 14, 'bold'), height=2, bd=3, relief='raised')
        self.master_toggle_btn.grid(row=0, column=0, padx=15, pady=10, sticky='ew')

        # Removed Scheduled Voting Control section

        # --- Live Statistics ---
        stats_section = tk.LabelFrame(control_frame, text="Live Statistics", font=('Arial', 16, 'bold'), fg='#2c3e50', padx=20, pady=20)
        stats_section.grid(row=1, column=0, sticky='nsew', pady=10) # Changed row from 2 to 1
        stats_section.grid_columnconfigure(0, weight=1)

        self.total_votes_label = tk.Label(stats_section, text=f"Total Votes Cast: {self.total_votes}", font=('Arial', 18, 'bold'), fg='#2c3e50')
        self.total_votes_label.pack(pady=20)

        self.update_admin_status()

    def create_secure_admin_tab(self, notebook):
        """Creates the 'Secure Administration' tab requiring re-authentication."""
        secure_frame = ttk.Frame(notebook, padding=20)
        notebook.add(secure_frame, text="Secure Administration")
        secure_frame.grid_columnconfigure(0, weight=1)
        secure_frame.grid_rowconfigure(1, weight=1)
        
        # Authentication Section
        auth_section = tk.LabelFrame(secure_frame, text="Secure Access Required", font=('Arial', 16, 'bold'), fg='#c0392b', padx=20, pady=15)
        auth_section.grid(row=0, column=0, sticky='ew', pady=20)
        auth_section.grid_columnconfigure(0, weight=1)
        
        auth_button = tk.Button(auth_section, text="AUTHENTICATE FOR SECURE FUNCTIONS", command=lambda: self.authenticate_secure_admin(parent_frame=secure_frame), font=('Arial', 14, 'bold'), bg='#e67e22', fg='white', bd=3, relief='raised')
        auth_button.pack(pady=15, fill='x', expand=True)

    def authenticate_secure_admin(self, parent_frame):
        """Authenticates user to reveal secure admin functions."""
        password = simpledialog.askstring("Secure Authentication", "Enter administrator password to access secure functions:", show='*')
        if password and self.verify_password(password):
            # Hide the authentication button and show the functions
            for widget in parent_frame.winfo_children():
                widget.destroy()
            self.setup_secure_functions(parent_frame)
            messagebox.showinfo("Access Granted", "Secure functions are now available.")
        elif password is not None:
            messagebox.showerror("Authentication Failed", "Incorrect password.")

    def setup_secure_functions(self, parent_frame):
        """Sets up the UI for secure functions after successful authentication."""
        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_columnconfigure((0,1), weight=1)

        # Detailed Results Section
        results_section = tk.LabelFrame(parent_frame, text="Detailed Vote Results", font=('Arial', 14, 'bold'), fg='#2c3e50', padx=15, pady=15)
        results_section.grid(row=0, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
        results_section.grid_rowconfigure(0, weight=1)
        results_section.grid_columnconfigure(0, weight=1)

        # Results display with scrollbar
        res_canvas = tk.Canvas(results_section, bg='white', highlightthickness=1)
        res_scrollbar = ttk.Scrollbar(results_section, orient="vertical", command=res_canvas.yview)
        self.results_display_frame = tk.Frame(res_canvas, bg='white')
        self.results_display_frame.bind("<Configure>", lambda e: res_canvas.configure(scrollregion=res_canvas.bbox("all")))
        res_canvas.create_window((0, 0), window=self.results_display_frame, anchor="nw")
        res_canvas.configure(yscrollcommand=res_scrollbar.set)
        res_canvas.grid(row=0, column=0, sticky='nsew')
        res_scrollbar.grid(row=0, column=1, sticky='ns')

        # Data Management Section
        data_mgmt_section = tk.LabelFrame(parent_frame, text="Data Management", font=('Arial', 14, 'bold'), fg='#2c3e50', padx=15, pady=15)
        data_mgmt_section.grid(row=1, column=0, sticky='nsew', padx=5, pady=10)
        data_mgmt_section.grid_columnconfigure(0, weight=1)

        tk.Button(data_mgmt_section, text="RESET ALL VOTES", command=self.reset_votes, font=('Arial', 12, 'bold'), bg='#c0392b', fg='white', bd=3, relief='raised').pack(pady=5, fill='x')
        tk.Button(data_mgmt_section, text="Refresh Results", command=self.display_results, font=('Arial', 11)).pack(pady=5, fill='x')

        # System Management Section
        sys_mgmt_section = tk.LabelFrame(parent_frame, text="System Management", font=('Arial', 14, 'bold'), fg='#2c3e50', padx=15, pady=15)
        sys_mgmt_section.grid(row=1, column=1, sticky='nsew', padx=5, pady=10)
        sys_mgmt_section.grid_columnconfigure(0, weight=1)

        tk.Button(sys_mgmt_section, text="MANAGE CANDIDATES", command=self.manage_candidates, font=('Arial', 12, 'bold'), bg='#8e44ad', fg='white', bd=3, relief='raised').pack(pady=5, fill='x')
        tk.Button(sys_mgmt_section, text="Change Admin Password", command=self.change_password, font=('Arial', 11)).pack(pady=5, fill='x')

        self.display_results()

    def cast_vote(self):
        """Handles the logic for a user casting a vote."""
        if not self.voting_open:
            messagebox.showerror("Voting Closed", "We're sorry, the voting period is currently closed.")
            return
        selected = self.selected_candidate.get()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a candidate before casting your vote.")
            return

        self.votes[selected] = self.votes.get(selected, 0) + 1
        self.total_votes += 1
        
        self.save_data()
        self.update_displays()
        
        self.selected_candidate.set("") # Clear selection after voting
        messagebox.showinfo("Vote Recorded", f"Thank you! Your vote for '{selected}' has been successfully recorded.")

    def open_voting(self): # Removed from_schedule parameter
        """Opens the voting period and logs the event."""
        if not self.voting_open:
            self.voting_open = True
            # Removed conditional logging for scheduled opening
            self.log_event("Voting Opened Manually") 
            self.update_all_statuses()
            self.save_data()
            messagebox.showinfo("Voting Opened", "The voting period is now OPEN.")

    def close_voting(self): # Removed from_schedule parameter
        """Closes the voting period and logs the event."""
        if self.voting_open:
            self.voting_open = False
            # Removed conditional logging for scheduled closing
            self.log_event("Voting Closed Manually")
            self.update_all_statuses()
            self.save_data()
            messagebox.showinfo("Voting Closed", "The voting period is now CLOSED.")

    def toggle_master_voting(self):
        """Toggles the voting status immediately and logs the change."""
        self.voting_open = not self.voting_open
        
        # Log the manual override
        if self.voting_open:
            self.log_event("Voting Opened Manually (Override)")
        else:
            self.log_event("Voting Closed Manually (Override)")
            
        self.update_all_statuses()
        self.save_data()
        # Removed clearing scheduled times as scheduling is removed
        # self.start_time_str = None
        # self.end_time_str = None
        # if hasattr(self, 'start_time_entry'):
        #     self.start_time_entry.delete(0, 'end')
        #     self.end_time_entry.delete(0, 'end')

    # Removed set_scheduled_voting method
    # def set_scheduled_voting(self):
    #     """Validates and sets the start and end times for voting."""
    #     start_str = self.start_time_entry.get()
    #     end_str = self.end_time_entry.get()
    #     try:
    #         # Validate format
    #         start_dt = datetime.strptime(start_str, '%H:%M')
    #         end_dt = datetime.strptime(end_str, '%H:%M')
    #         if start_dt >= end_dt:
    #             messagebox.showerror("Invalid Times", "Start time must be before end time.")
    #             return

    #         self.start_time_str = start_str
    #         self.end_time_str = end_str
    #         self.save_data()
    #         messagebox.showinfo("Schedule Set", f"Voting is scheduled to start at {start_str} and end at {end_str}.")
    #         self.check_scheduled_times() # Immediately check status
    #     except ValueError:
    #         messagebox.showerror("Invalid Format", "Please enter times in HH:MM format (e.g., 09:00 or 17:30).")

    # Removed check_scheduled_times method
    # def check_scheduled_times(self):
    #     """Checks if the current time is within the scheduled voting period."""
    #     if self.schedule_after_id: # Cancel previous timer
    #         self.root.after_cancel(self.schedule_after_id)

    #     if self.start_time_str and self.end_time_str:
    #         try:
    #             now = datetime.now().time()
    #             start_time = datetime.strptime(self.start_time_str, '%H:%M').time()
    #             end_time = datetime.strptime(self.end_time_str, '%H:%M').time()

    #             if start_time <= now < end_time:
    #                 self.open_voting(from_schedule=True)
    #             else:
    #                 self.close_voting(from_schedule=True)
    #         except ValueError:
    #             # Handles case where stored time is invalid
    #             pass
        
    #     # Reschedule the check
    #     self.schedule_after_id = self.root.after(5000, self.check_scheduled_times)


    def update_all_statuses(self):
        """Convenience function to update all status labels."""
        self.update_voter_status()
        if self.admin_window and self.admin_window.winfo_exists():
            self.update_admin_status()

    def update_voter_status(self):
        """Updates the status label on the main voter window."""
        if self.voting_open:
            self.voter_status_label.config(text="Voting is OPEN", fg='#27ae60')
        else:
            self.voter_status_label.config(text="Voting is CLOSED", fg='#e74c3c')

    def update_admin_status(self):
        """Updates the status label on the admin panel."""
        if hasattr(self, 'master_toggle_btn') and self.master_toggle_btn.winfo_exists():
            if self.voting_open:
                self.master_toggle_btn.config(text="VOTING IS OPEN (Click to Close)", bg='#27ae60', fg='white')
            else:
                self.master_toggle_btn.config(text="VOTING IS CLOSED (Click to Open)", bg='#e74c3c', fg='white')

    def update_displays(self):
        """Updates vote counts on the admin panel."""
        if hasattr(self, 'total_votes_label') and self.total_votes_label.winfo_exists():
            self.total_votes_label.config(text=f"Total Votes Cast: {self.total_votes}")
        if hasattr(self, 'results_display_frame') and self.results_display_frame.winfo_exists():
            self.display_results()

    def display_results(self):
        """Displays detailed voting results in the secure admin tab."""
        for widget in self.results_display_frame.winfo_children():
            widget.destroy()

        self.results_display_frame.grid_columnconfigure(1, weight=1)

        # Overall total
        tk.Label(self.results_display_frame, text=f"OVERALL TOTAL VOTES: {self.total_votes}", font=('Arial', 14, 'bold'), bg='#3498db', fg='white').grid(row=0, column=0, columnspan=4, sticky='ew', pady=(5, 10), ipady=10)

        # Headers
        headers = ["Rank", "Candidate Name", "Votes", "% of Total"]
        for i, header in enumerate(headers):
            tk.Label(self.results_display_frame, text=header, font=('Arial', 10, 'bold'), bg='white').grid(row=1, column=i, sticky='ew', pady=5)

        sorted_candidates = sorted(self.votes.items(), key=lambda item: item[1], reverse=True)
        
        for i, (candidate, vote_count) in enumerate(sorted_candidates):
            percentage = (vote_count / self.total_votes * 100) if self.total_votes > 0 else 0
            bg_color = '#ecf0f1' if i % 2 == 0 else '#ffffff'
            
            tk.Label(self.results_display_frame, text=f"{i+1}.", font=('Arial', 11), bg=bg_color).grid(row=i+2, column=0, sticky='ew', pady=2)
            tk.Label(self.results_display_frame, text=candidate, font=('Arial', 11), bg=bg_color, anchor='w', padx=10).grid(row=i+2, column=1, sticky='ew', pady=2)
            tk.Label(self.results_display_frame, text=f"{vote_count}", font=('Arial', 11, 'bold'), bg=bg_color).grid(row=i+2, column=2, sticky='ew', pady=2)
            tk.Label(self.results_display_frame, text=f"{percentage:.1f}%", font=('Arial', 11), bg=bg_color).grid(row=i+2, column=3, sticky='ew', pady=2)

    def reset_votes_logic(self):
        """Internal logic to reset votes without GUI interaction."""
        self.votes.clear()
        for candidate in self.candidates:
            self.votes[candidate] = 0
        self.total_votes = 0

    def reset_votes(self):
        """Resets all vote data after re-authentication."""
        password = simpledialog.askstring("Confirm Vote Reset", "This is a critical action. Enter the administrator password to confirm a full vote reset:", show='*')
        if not (password and self.verify_password(password)):
            messagebox.showerror("Authentication Failed", "Incorrect password. Reset operation cancelled.")
            return
        
        if messagebox.askyesno("Final Confirmation", "WARNING: This will permanently delete ALL cast votes and reset counts to zero. This action cannot be undone. Are you absolutely sure?"):
            self.reset_votes_logic()
            self.save_data()
            self.update_displays()
            messagebox.showinfo("Reset Complete", "All voting data has been successfully cleared.")

    def manage_candidates(self):
        """Opens a window to add, edit, or remove candidates."""
        manage_window = tk.Toplevel(self.admin_window)
        manage_window.title("Candidate Management")
        manage_window.geometry("600x700")
        manage_window.transient(self.admin_window)
        manage_window.grab_set()

        tk.Label(manage_window, text="Manage Candidates (Max 32)", font=('Arial', 18, 'bold')).pack(pady=10)
        tk.Label(manage_window, text="Edit names, clear a field to remove, or add new names.").pack(pady=5)
        
        # Frame for entries with a scrollbar
        outer_frame = tk.Frame(manage_window)
        outer_frame.pack(fill='both', expand=True, padx=20, pady=10)
        canvas = tk.Canvas(outer_frame)
        scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        entries = []
        for candidate in self.candidates:
            entry = tk.Entry(scrollable_frame, font=('Arial', 12), width=50)
            entry.insert(0, candidate)
            entry.pack(padx=10, pady=4, fill='x')
            entries.append(entry)

        def add_field():
            if len(entries) < 32:
                entry = tk.Entry(scrollable_frame, font=('Arial', 12), width=50)
                entry.pack(padx=10, pady=4, fill='x')
                entries.append(entry)

        def save_candidates():
            new_candidates = [entry.get().strip() for entry in entries if entry.get().strip()]
            if len(new_candidates) > 32:
                messagebox.showerror("Limit Exceeded", f"You can have a maximum of 32 candidates. You have entered {len(new_candidates)}.")
                return
            if len(new_candidates) != len(set(new_candidates)):
                messagebox.showerror("Duplicate Names", "Candidate names must be unique.")
                return

            self.candidates = new_candidates
            self.reset_votes_logic() # Reset votes as candidates changed
            self.save_data()
            self.update_candidate_display()
            self.update_displays()
            messagebox.showinfo("Success", "Candidate list updated. All votes have been reset.", parent=manage_window)
            manage_window.destroy()

        button_frame = tk.Frame(manage_window)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Add Field", command=add_field).pack(side='left', padx=10)
        tk.Button(button_frame, text="Save Changes", command=save_candidates, font=('Arial', 12, 'bold')).pack(side='left', padx=10)
        tk.Button(button_frame, text="Cancel", command=manage_window.destroy).pack(side='left', padx=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def change_password(self):
        """Opens a dialog to change the administrator password."""
        win = tk.Toplevel(self.admin_window)
        win.title("Change Password")
        win.transient(self.admin_window)
        win.grab_set()

        tk.Label(win, text="Current Password:").grid(row=0, column=0, padx=10, pady=5)
        current_pass = tk.Entry(win, show='*')
        current_pass.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(win, text="New Password:").grid(row=1, column=0, padx=10, pady=5)
        new_pass = tk.Entry(win, show='*')
        new_pass.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(win, text="Confirm New Password:").grid(row=2, column=0, padx=10, pady=5)
        confirm_pass = tk.Entry(win, show='*')
        confirm_pass.grid(row=2, column=1, padx=10, pady=5)

        def do_change():
            if not self.verify_password(current_pass.get()):
                messagebox.showerror("Error", "Current password is not correct.", parent=win)
                return
            if not new_pass.get() or new_pass.get() != confirm_pass.get():
                messagebox.showerror("Error", "New passwords do not match or are empty.", parent=win)
                return
            
            self.admin_password_hash = self.hash_password(new_pass.get())
            self.save_password()
            messagebox.showinfo("Success", "Password changed successfully.", parent=win)
            win.destroy()

        tk.Button(win, text="Change Password", command=do_change).grid(row=3, column=0, columnspan=2, pady=10)

    def run(self):
        """Starts the Tkinter main event loop."""
        self.root.mainloop()

if __name__ == "__main__":
    app = VotingSystem()
    app.run()
