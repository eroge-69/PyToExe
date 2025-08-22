#!/usr/bin/env python3
"""
Refactored Business Management Application
A multi-panel Tkinter application for managing customers, distributors, and financial data.
"""

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import ttk, simpledialog, font as tkfont, messagebox
from typing import List, Dict, Optional, Callable, Any

# Suppress all console output for EXE version
if getattr(sys, 'frozen', False):
    # Running as EXE - suppress all print output
    import io
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()


class Config:
    """Application configuration constants."""
    DATA_FILE = "app_data.json"
    
    # Colors
    BG_COLOR = "#e8ebf0"  # Darker professional background
    LIGHT_BLUE = "#C3C3C9"
    LIGHTER_ALT = "#d6eaf8"
    HEADER_BG = "#424040"
    SELECTED_BG = "#357ABD"
    PANEL_BG = "#C3C3C9"  # Same as LIGHT_BLUE for panels
    BORDER_COLOR = "#424040"  # Same as HEADER_BG for borders
    
    # Space box styling for button containers
    SPACE_BOX_BG = "#d4d8dc"      # Slightly lighter than panel for contrast
    SPACE_BOX_BORDER = "#9ca3af"  # Softer border color
    SPACE_BOX_SHADOW = "#a8aeb6"  # Shadow color for depth
    
    # Blinking colors for incomplete rows
    PENDING_COLOR_1 = "#ff0000"  # Bright red
    PENDING_COLOR_2 = "#fed7d7"  # Light red/pink
    
    # Fonts
    DEFAULT_FONT_SIZE = 11
    BUTTON_FONT_SIZE = 10
    
    @staticmethod
    def get_data_file_path():
        """Get the full path to the data file. Try exe folder, else fallback to Documents."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(script_dir, Config.DATA_FILE)
        try:
            # Try to write a test file in the exe folder
            test_path = os.path.join(script_dir, "_write_test.tmp")
            with open(test_path, "w") as f:
                f.write("test")
            os.remove(test_path)
            return data_path
        except Exception:
            # Fallback to Documents
            from pathlib import Path
            docs = str(Path.home() / "Documents")
            fallback_path = os.path.join(docs, Config.DATA_FILE)
            print(f"Warning: Cannot write to exe folder. Saving data to {fallback_path}")
            return fallback_path


class AutocompleteEntryInline(tk.Entry):
    """Enhanced Entry widget with autocomplete functionality."""
    
    def __init__(self, autocomplete_list: List[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.autocomplete_list = autocomplete_list
        self.var = self["textvariable"] = tk.StringVar()
        self.var.trace("w", self.changed)
        self.suggestion = ''
        self.user_text = ''
        self._setup_bindings()

    def _setup_bindings(self):
        """Setup key bindings for autocomplete functionality."""
        self.bind("<KeyRelease>", self.complete)
        self.bind("<Return>", self._on_return)
        self.bind("<Tab>", self._on_tab)
        self.bind("<Right>", self._on_right)

    def changed(self, name, index, mode):
        """Called when text variable changes."""
        pass

    def complete(self, event=None):
        """Provide autocomplete suggestions."""
        current_text = self.get()
        self.user_text = current_text
        
        if not current_text:
            self.suggestion = ''
            self.config(fg="black")
            return
            
        # Only suggest if user has typed at least 2 characters
        if len(current_text) < 2:
            self.suggestion = ''
            self.config(fg="black")
            return
            
        matches = [x for x in self.autocomplete_list 
                  if x.lower().startswith(current_text.lower())]
        
        if matches:
            match = matches[0]
            if match.lower() != current_text.lower():
                # Show the suggestion visually
                if match.lower().startswith(current_text.lower()):
                    self.suggestion = match
                    
                    # Show the completion visually
                    self.delete(0, tk.END)
                    self.insert(0, match)
                    self.icursor(len(current_text))
                    self.select_range(len(current_text), tk.END)
                    self.config(fg="black")
                else:
                    self.suggestion = ''
                    self.config(fg="black")
            else:
                self.suggestion = match
                self.config(fg="black")
                self.select_clear()
        else:
            self.suggestion = ''
            self.config(fg="black")
            self.select_clear()

    def _on_return(self, event=None):
        """Handle Return key press."""
        if self.suggestion:
            self.select_clear()
            self.icursor(tk.END)
        if hasattr(self, "after_selection_callback"):
            self.after_selection_callback(move_right=True)
        return "break"

    def _on_tab(self, event=None):
        """Handle Tab key press."""
        # If there's a suggestion available, accept it
        if self.suggestion:
            self.select_clear()
            self.icursor(tk.END)
        
        # Then trigger the move to next cell
        if hasattr(self, "after_selection_callback"):
            self.after_selection_callback(move_right=True)
        return "break"

    def _on_right(self, event=None):
        """Handle Right arrow key press."""
        # If there's a suggestion and the cursor is at the end of user text, accept it
        if self.suggestion and self.index(tk.INSERT) == len(self.user_text):
            self.select_clear()
            self.icursor(tk.END)
            return "break"
        # Otherwise, let the normal right arrow behavior happen
        return None


class TreeManager:
    """Manages a Treeview widget with common functionality."""
    
    def __init__(self, parent, columns: List[str], height: int = 20, tree_name: str = ""):
        self.parent = parent
        self.columns = columns.copy()
        self.tree = None
        self.scrollbar = None
        self.tree_name = tree_name
        self.column_widths = {}
        self.column_alignments = {}  # Track column alignments
        self.blink_state = False  # For blinking animation
        self.blink_job = None     # Store blink timer job
        self._setup_tree(height)
        
    def _setup_tree(self, height: int):
        """Initialize the treeview widget."""
        # Use special style for tree2, tree4, default for others
        if self.tree_name == "tree2":
            tree_style = "Tree2.Treeview"
        elif self.tree_name == "tree4":
            tree_style = "Tree4.Treeview"
        else:
            tree_style = "Treeview"
        
        self.tree = ttk.Treeview(
            self.parent, 
            columns=self.columns,
            show="headings", 
            height=height, 
            style=tree_style,
            selectmode="extended"  # Allow multiple row selection
        )
        
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=86)
            
        self.scrollbar = ttk.Scrollbar(
            self.parent, 
            orient="vertical", 
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        # Bind column resize event
        self.tree.bind("<Button-1>", self._on_column_resize_start)
        self.tree.bind("<ButtonRelease-1>", self._on_column_resize_end)
        
    def _on_column_resize_start(self, event):
        """Handle start of column resize."""
        # Check if we're over a column separator
        region = self.tree.identify_region(event.x, event.y)
        if region == "separator":
            self._resize_start_widths = {}
            for i, col in enumerate(self.columns):
                col_id = f"#{i + 1}"
                self._resize_start_widths[col] = self.tree.column(col_id, "width")
                
    def _on_column_resize_end(self, event):
        """Handle end of column resize and save new widths."""
        if hasattr(self, '_resize_start_widths'):
            # Check if any widths changed
            changed = False
            for i, col in enumerate(self.columns):
                col_id = f"#{i + 1}"
                current_width = self.tree.column(col_id, "width")
                if col in self._resize_start_widths:
                    if current_width != self._resize_start_widths[col]:
                        changed = True
                        self.column_widths[col] = current_width
                        
            # Trigger autosave if widths changed
            if changed and hasattr(self, '_app_reference'):
                # Use after_idle to ensure the resize is complete
                self._app_reference.root.after_idle(self._app_reference._autosave_column_widths)
                
    def set_app_reference(self, app):
        """Set reference to the main application for autosaving."""
        self._app_reference = app
                
    def set_column_widths(self, widths: Dict[str, int]):
        """Set column widths from saved data."""
        self.column_widths = widths.copy()
        for i, col in enumerate(self.columns):
            col_id = f"#{i + 1}"
            if col in widths:
                self.tree.column(col_id, width=widths[col])
                
    def get_column_widths(self) -> Dict[str, int]:
        """Get current column widths."""
        current_widths = {}
        for i, col in enumerate(self.columns):
            col_id = f"#{i + 1}"
            current_widths[col] = self.tree.column(col_id, "width")
        return current_widths
        
    def pack_tree(self, **kwargs):
        """Pack the tree and scrollbar with optimized spacing."""
        # Pack scrollbar but don't show it initially
        self.scrollbar.pack(side="right", fill="y")
        # Pack tree with minimal padding for tight fit
        self.tree.pack(fill="both", expand=True, padx=2, pady=2, **kwargs)
        
        # Configure scrollbar to show only when needed
        self._configure_auto_scrollbar()
        
    def _configure_auto_scrollbar(self):
        """Configure scrollbar to show only when content exceeds visible area."""
        def on_tree_configure(event=None):
            # Get the bbox of all items
            children = self.tree.get_children()
            if children:
                # Calculate total content height
                total_height = len(children) * 32  # Assuming row height of 32
                visible_height = self.tree.winfo_height()
                
                # Show/hide scrollbar based on content
                if total_height > visible_height:
                    if not self.scrollbar.winfo_viewable():
                        self.scrollbar.pack(side="right", fill="y", before=self.tree)
                else:
                    if self.scrollbar.winfo_viewable():
                        self.scrollbar.pack_forget()
            else:
                # No content, hide scrollbar
                if self.scrollbar.winfo_viewable():
                    self.scrollbar.pack_forget()
        
        # Bind to tree configure and map events
        self.tree.bind("<Configure>", on_tree_configure)
        self.tree.bind("<Map>", on_tree_configure)
        
        # Also update when data changes
        self._update_scrollbar_visibility = on_tree_configure
        
    def apply_gridlines(self):
        """Apply alternating row colors and handle blinking for incomplete rows."""
        try:
            for i, row in enumerate(self.tree.get_children()):
                values = self.tree.item(row, "values")
                
                # Check if row is complete (all columns have data) - only for tree1
                if self.tree_name == "tree1" and len(values) > 0:
                    num_columns = len(self.columns)
                    values_to_check = values[:num_columns] if len(values) >= num_columns else values
                    
                    is_complete = all(str(v).strip() for v in values_to_check)
                    
                    if not is_complete and any(str(v).strip() for v in values_to_check):
                        # Row has some data but is incomplete - make it blink
                        tag = "pending_blink"
                        self.tree.item(row, tags=(tag,))
                    else:
                        # Row is complete or completely empty - use normal colors
                        tag = "evenrow" if i % 2 == 0 else "oddrow"
                        self.tree.item(row, tags=(tag,))
                else:
                    # Not tree1 or different logic - use normal alternating colors
                    tag = "evenrow" if i % 2 == 0 else "oddrow"
                    self.tree.item(row, tags=(tag,))
                    
            # Configure tag colors
            self.tree.tag_configure("evenrow", background=Config.LIGHT_BLUE)
            self.tree.tag_configure("oddrow", background=Config.LIGHTER_ALT)
            self.tree.tag_configure("pending_blink", background=Config.PENDING_COLOR_1)
            
            # Start blinking animation for tree1 if there are pending rows
            if self.tree_name == "tree1":
                self._start_blinking_if_needed()
                
            # Update scrollbar visibility
            if hasattr(self, '_update_scrollbar_visibility'):
                self.tree.after_idle(self._update_scrollbar_visibility)
                
        except Exception as e:
            print(f"apply_gridlines error: {e}")
            
    def _start_blinking_if_needed(self):
        """Start blinking animation if there are incomplete rows."""
        # Check if there are any pending rows
        has_pending = False
        for row in self.tree.get_children():
            if "pending_blink" in self.tree.item(row, "tags"):
                has_pending = True
                break
                
        if has_pending and not self.blink_job:
            self._blink_pending_rows()
        elif not has_pending and self.blink_job:
            self._stop_blinking()
            
    def _blink_pending_rows(self):
        """Toggle colors for pending rows to create blinking effect."""
        try:
            # Toggle blink state
            self.blink_state = not self.blink_state
            
            # Set color based on blink state
            if self.blink_state:
                color = Config.PENDING_COLOR_1  # Bright red
            else:
                color = Config.PENDING_COLOR_2  # Light red/pink
                
            self.tree.tag_configure("pending_blink", background=color)
            
            # Schedule next blink
            if hasattr(self, '_app_reference') and self._app_reference:
                self.blink_job = self._app_reference.root.after(500, self._blink_pending_rows)
                
        except Exception as e:
            print(f"_blink_pending_rows error: {e}")
            
    def _stop_blinking(self):
        """Stop the blinking animation."""
        if self.blink_job and hasattr(self, '_app_reference') and self._app_reference:
            self._app_reference.root.after_cancel(self.blink_job)
            self.blink_job = None
            self.blink_state = False
            
    def get_data(self) -> List[tuple]:
        """Get all data from the tree."""
        return [self.tree.item(row, "values") for row in self.tree.get_children()]
        
    def set_data(self, data: List[tuple]):
        """Set data in the tree."""
        self.tree.delete(*self.tree.get_children())
        for row in data:
            self.tree.insert("", "end", values=row)
        self.apply_gridlines()
        
        # Update scrollbar visibility after data change
        if hasattr(self, '_update_scrollbar_visibility'):
            self.tree.after_idle(self._update_scrollbar_visibility)
        
    def update_column_name(self, index: int, new_name: str):
        """Update a column name."""
        if 0 <= index < len(self.columns):
            self.columns[index] = new_name
            col_id = f"#{index + 1}"
            self.tree.heading(col_id, text=new_name)


class DriveSelectionPopup:
    """Popup for selecting the flash drive to monitor."""
    
    def __init__(self, parent=None):
        self.selected_drive = None
        self.popup = None
        self.parent = parent
        
    def get_available_drives(self):
        """Get list of available drives on Windows (A: to H: only for speed)."""
        drives = []
        try:
            # Only check A: to H: for speed
            for letter in 'ABCDEFGH':
                drive_path = f"{letter}:\\"
                if os.path.exists(drive_path):
                    try:
                        # Try to get drive type using subprocess
                        result = subprocess.run(
                            ['wmic', 'logicaldisk', 'where', f'caption="{letter}:"', 'get', 'drivetype'],
                            capture_output=True, text=True, timeout=3
                        )
                        # DriveType 2 = Removable disk (USB/Flash drive)
                        if '2' in result.stdout:
                            drives.append(f"{letter}:")
                        elif os.path.ismount(drive_path):  # Fallback check
                            drives.append(f"{letter}:")
                    except:
                        # If wmic fails, just check if it's accessible
                        try:
                            os.listdir(drive_path)
                            drives.append(f"{letter}:")
                        except:
                            pass
        except Exception as e:
            print(f"Error getting drives: {e}")
            # Fallback - just return A: to H:
            for letter in 'ABCDEFGH':
                drive_path = f"{letter}:\\"
                if os.path.exists(drive_path):
                    drives.append(f"{letter}:")
        return drives
        
    def show(self):
        """Show the drive selection dialog with smooth styling."""
        # Create a temporary root for the popup to avoid blank window
        if self.parent is None:
            self.popup = tk.Tk()
            self.popup.withdraw()  # Hide initially to prevent blank window flash
        else:
            self.popup = tk.Toplevel(self.parent)
        self.popup.title("")
        self.popup.configure(bg="#e8ebf0")  # Softer background
        self.popup.resizable(False, False)
        
        # Make sure popup is independent of parent positioning
        if self.parent is not None:
            self.popup.transient()  # Remove parent dependency for positioning
        
        # Smooth window styling
        try:
            self.popup.attributes('-topmost', True)
            self.popup.after(100, lambda: self.popup.attributes('-topmost', False))
        except:
            pass
            
        # Center the window perfectly on screen
        self.popup.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.popup.winfo_screenwidth()
        screen_height = self.popup.winfo_screenheight()
        
        # Calculate center position
        window_width = 400
        window_height = 280
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set geometry with calculated position
        self.popup.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Now show the window after everything is configured
        if self.parent is None:
            self.popup.deiconify()  # Show the window now that it's ready
        
        # Ensure window is visible and focused
        self.popup.lift()
        self.popup.focus_force()
        
        # Subtle header frame
        header_frame = tk.Frame(self.popup, bg="#d4d8dc", height=45)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Softer title
        title_label = tk.Label(
            header_frame,
            text="Παρακολούθηση USB",
            bg="#d4d8dc",
            fg="#424040",
            font=("Segoe UI", 12, "bold")
        )
        title_label.pack(expand=True)
        
        # Main content frame
        content_frame = tk.Frame(self.popup, bg="#e8ebf0")
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Softer instructions
        info_label = tk.Label(
            content_frame,
            text="Επιλέξτε USB συσκευή για παρακολούθηση. Η εφαρμογή θα\nκλείσει αυτόματα όταν αφαιρεθεί η επιλεγμένη συσκευή.",
            bg="#e8ebf0",
            fg="#424040",
            font=("Segoe UI", 9),
            justify="center"
        )
        info_label.pack(pady=(0, 12))
        
        # Drive list
        drives = self.get_available_drives()
        
        if not drives:
            # Subtle no drives found message
            no_drives_frame = tk.Frame(content_frame, bg="#f0d7a8", relief="flat", bd=0)
            no_drives_frame.pack(fill="x", pady=(0, 10))
            
            no_drives_label = tk.Label(
                no_drives_frame,
                text="Δεν βρέθηκαν USB συσκευές",
                bg="#f0d7a8",
                fg="#6b5b47",
                font=("Segoe UI", 10)
            )
            no_drives_label.pack(pady=10)
            
            # Subtle skip button
            skip_btn = tk.Button(
                content_frame,
                text="Συνέχεια Χωρίς Παρακολούθηση",
                command=self._skip_monitoring,
                font=("Segoe UI", 10),
                bg="#9ca3af",
                fg="white",
                activebackground="#6b7280",
                activeforeground="white",
                relief="flat",
                bd=0,
                cursor="hand2",
                padx=15,
                pady=6
            )
            skip_btn.pack(pady=8)
        else:
            # Subtle drive selection frame
            drives_frame = tk.LabelFrame(
                content_frame, 
                text="Διαθέσιμες Συσκευές", 
                bg="#e8ebf0", 
                fg="#424040",
                font=("Segoe UI", 9),
                relief="flat",
                bd=1
            )
            drives_frame.pack(fill="x", pady=(0, 12))
            
            # Drive selection
            self.drive_var = tk.StringVar()
            
            for i, drive in enumerate(drives):
                rb = tk.Radiobutton(
                    drives_frame,
                    text=f"Drive {drive}",
                    variable=self.drive_var,
                    value=drive,
                    bg="#e8ebf0",
                    fg="#424040",
                    selectcolor="#C3C3C9",
                    font=("Segoe UI", 10),
                    activebackground="#d4d8dc",
                    activeforeground="#424040",
                    cursor="hand2"
                )
                rb.pack(anchor="w", padx=10, pady=4)
                
            # Set first drive as default
            if drives:
                self.drive_var.set(drives[0])
            
            # Subtle buttons frame
            btn_frame = tk.Frame(content_frame, bg="#e8ebf0")
            btn_frame.pack(fill="x", pady=(8, 0))
            
            # Subtle confirm button
            confirm_btn = tk.Button(
                btn_frame,
                text="Επιβεβαίωση Επιλογής",
                command=self._confirm_selection,
                font=("Segoe UI", 10),
                bg="#8ab4d8",
                fg="white",
                activebackground="#7aa3c7",
                activeforeground="white",
                relief="flat",
                bd=0,
                cursor="hand2",
                padx=15,
                pady=6
            )
            confirm_btn.pack(side="left", padx=(0, 8))
            
            # Subtle skip button
            skip_btn = tk.Button(
                btn_frame,
                text="Παράλειψη Παρακολούθησης",
                command=self._skip_monitoring,
                font=("Segoe UI", 10),
                bg="#9ca3af",
                fg="white",
                activebackground="#6b7280",
                activeforeground="white",
                relief="flat",
                bd=0,
                cursor="hand2",
                padx=15,
                pady=6
            )
            skip_btn.pack(side="left")
        
        # Make dialog modal
        if self.parent:
            self.popup.transient(self.parent)
            self.popup.grab_set()
        
        # Handle window close
        self.popup.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Wait for selection
        self.popup.mainloop()
        
        # Return both drive selection and root window (for reuse)
        root_to_return = self.popup if self.parent is None else None
        return self.selected_drive, root_to_return
        
    def _confirm_selection(self):
        """Confirm drive selection."""
        if hasattr(self, 'drive_var'):
            self.selected_drive = self.drive_var.get()
        # Don't destroy if it's a root window (will be reused)
        if self.parent is not None:
            self.popup.destroy()
        else:
            # It's a root window - just quit the mainloop
            self.popup.quit()
        
    def _skip_monitoring(self):
        """Skip drive monitoring."""
        self.selected_drive = None
        # Don't destroy if it's a root window (will be reused)
        if self.parent is not None:
            self.popup.destroy()
        else:
            # It's a root window - just quit the mainloop
            self.popup.quit()
        
    def _on_close(self):
        """Handle window close."""
        self.selected_drive = None
        # Don't destroy if it's a root window (will be reused)
        if self.parent is not None:
            self.popup.destroy()
        else:
            # It's a root window - just quit the mainloop
            self.popup.quit()


class PopupDialog:
    """Base class for popup dialogs."""
    
    _active_popups = {}  # Class variable to track active popups
    
    def __init__(self, parent, title: str, width: int = 400, height: int = 300, relative_widget=None):
        self.parent = parent
        self.popup = None
        self.title = title
        self.width = width
        self.height = height
        self.relative_widget = relative_widget
        self.popup_id = self.__class__.__name__  # Unique ID based on class name
        
    def show(self):
        """Show the popup dialog."""
        # Check if this type of popup is already open
        if self.popup_id in PopupDialog._active_popups:
            existing_popup = PopupDialog._active_popups[self.popup_id]
            if existing_popup and existing_popup.winfo_exists():
                existing_popup.lift()  # Bring existing popup to front
                existing_popup.focus_set()
                return
            else:
                # Remove dead reference
                del PopupDialog._active_popups[self.popup_id]
        
        if self.popup and self.popup.winfo_exists():
            self.popup.lift()
            return
            
        self.popup = tk.Toplevel(self.parent)
        self.popup.title("")
        
        # Professional modern styling
        self.popup.configure(bg="#e8ebf0")  # Softer background matching main app
        self.popup.resizable(False, False)
        
        # Add window icon styling (remove default window decorations for cleaner look)
        try:
            self.popup.attributes('-topmost', True)  # Keep on top initially
            self.popup.after(100, lambda: self.popup.attributes('-topmost', False))  # Then allow normal behavior
        except:
            pass
            
        # Subtle border effect
        self.popup.configure(relief="flat", bd=0)
        
        # Register this popup as active
        PopupDialog._active_popups[self.popup_id] = self.popup
        
        # Setup content first to calculate proper size
        self._setup_content()
        
        # Position popup near the relative widget if provided
        if self.relative_widget:
            self._position_above_widget()
        else:
            self._center_popup()
        
        self.popup.protocol("WM_DELETE_WINDOW", self._on_close)
        
    def _center_popup(self):
        """Center the popup on the parent window."""
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width - self.width) // 2
        y = parent_y + (parent_height - self.height) // 2
        
        self.popup.geometry(f"{self.width}x{self.height}+{x}+{y}")
    
    def _position_above_widget(self):
        """Position popup above the relative widget."""
        if not self.relative_widget:
            self._center_popup()
            return
            
        try:
            # Get the position of the relative widget
            widget_x = self.relative_widget.winfo_rootx()
            widget_y = self.relative_widget.winfo_rooty()
            widget_width = self.relative_widget.winfo_width()
            
            # Update popup to calculate actual size after content is added
            self.popup.update_idletasks()
            
            # Get actual popup dimensions
            actual_width = self.popup.winfo_reqwidth()
            actual_height = self.popup.winfo_reqheight()
            
            # Position popup above the widget, centered horizontally
            popup_x = widget_x + (widget_width - actual_width) // 2
            popup_y = widget_y - actual_height - 10  # 10px gap above the button
            
            # Ensure popup doesn't go off screen
            screen_width = self.parent.winfo_screenwidth()
            screen_height = self.parent.winfo_screenheight()
            
            if popup_x < 10:
                popup_x = 10
            elif popup_x + actual_width > screen_width - 10:
                popup_x = screen_width - actual_width - 10
                
            if popup_y < 10:
                # If not enough space above, position below instead
                popup_y = widget_y + self.relative_widget.winfo_height() + 10
                
            self.popup.geometry(f"{actual_width}x{actual_height}+{popup_x}+{popup_y}")
            
        except tk.TclError:
            # Fallback to center if positioning fails
            self._center_popup()
        
    def _setup_content(self):
        """Override in subclasses to setup popup content."""
        pass
        
    def _on_close(self):
        """Handle popup close."""
        # Remove from active popups when closing
        if self.popup_id in PopupDialog._active_popups:
            del PopupDialog._active_popups[self.popup_id]
        
        if self.popup:
            self.popup.destroy()
            self.popup = None


class DistributorPopup(PopupDialog):
    """Popup for adding distributors."""
    
    def __init__(self, parent, tree_manager: TreeManager, on_confirm: Callable = None, relative_widget=None):
        super().__init__(parent, "", 380, 180, relative_widget)
        self.tree_manager = tree_manager
        self.on_confirm = on_confirm
        
    def _setup_content(self):
        """Setup the subtle distributor popup content."""
        # Subtle header section
        header_frame = tk.Frame(self.popup, bg="#d4d8dc", height=40)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="Νέος Διανομέας",
            bg="#d4d8dc",
            fg="#424040",
            font=("Segoe UI", 11, "bold")
        )
        title_label.pack(expand=True)
        
        # Content frame
        content_frame = tk.Frame(self.popup, bg="#e8ebf0")
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Subtle label
        tk.Label(
            content_frame,
            text="Όνομα Διανομέα:",
            bg="#e8ebf0",
            fg="#424040",
            font=("Segoe UI", 9),
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        # Subtle entry with soft border
        entry_frame = tk.Frame(content_frame, bg="#C3C3C9", relief="flat", bd=1)
        entry_frame.pack(fill="x", pady=(0, 12))
        
        self.entry = tk.Entry(
            entry_frame,
            font=("Segoe UI", 10),
            bg="#C3C3C9",
            fg="#424040",
            insertbackground="#424040",
            relief="flat",
            bd=0
        )
        self.entry.pack(fill="both", padx=8, pady=5)
        
        # Subtle buttons
        button_frame = tk.Frame(content_frame, bg="#e8ebf0")
        button_frame.pack(fill="x")
        
        tk.Button(
            button_frame,
            text="Προσθήκη Διανομέα",
            command=self._confirm,
            font=("Segoe UI", 9),
            bg="#8ab4d8",
            fg="white",
            activebackground="#7aa3c7",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=12,
            pady=6
        ).pack(pady=10)
        
        # Focus the entry field
        self.entry.focus_set()
        
    def _confirm(self):
        """Handle confirm button."""
        name = self.entry.get().strip()
        if name:
            self.tree_manager.tree.insert("", "end", values=(name, "0.00€"))
            if self.on_confirm:
                self.on_confirm()
        self._on_close()


class AddRowPopup(PopupDialog):
    """Popup for adding rows to a tree."""
    
    def __init__(self, parent, columns: List[str], on_confirm: Callable = None, relative_widget=None):
        super().__init__(parent, "", 330, 400, relative_widget)
        self.columns = columns
        self.on_confirm = on_confirm
        self.entries = []
        
    def _setup_content(self):
        """Setup the subtle new customer popup content."""
        # Subtle header section
        header_frame = tk.Frame(self.popup, bg="#d4d8dc", height=40)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="Νέος Πελάτης",
            bg="#d4d8dc",
            fg="#424040",
            font=("Segoe UI", 11, "bold")
        )
        title_label.pack(expand=True)
        
        # Content frame
        content_frame = tk.Frame(self.popup, bg="#e8ebf0")
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Create entry fields for each column
        for label_text in self.columns:
            # Subtle label
            tk.Label(
                content_frame,
                text=label_text + ":",
                bg="#e8ebf0",
                fg="#424040",
                font=("Segoe UI", 9),
                anchor="w"
            ).pack(fill="x", pady=(0, 3))
            
            # Subtle entry with soft border
            entry_frame = tk.Frame(content_frame, bg="#C3C3C9", relief="flat", bd=1)
            entry_frame.pack(fill="x", pady=(0, 8))
            
            entry = tk.Entry(
                entry_frame,
                font=("Segoe UI", 10),
                bg="#C3C3C9",
                fg="#424040",
                insertbackground="#424040",
                relief="flat",
                bd=0
            )
            entry.pack(fill="both", padx=8, pady=4)
            self.entries.append(entry)
            
        # Subtle button
        button_frame = tk.Frame(content_frame, bg="#e8ebf0")
        button_frame.pack(fill="x", pady=(8, 0))
        
        tk.Button(
            button_frame,
            text="Προσθήκη Πελάτη",
            command=self._confirm,
            font=("Segoe UI", 9),
            bg="#8ab4d8",
            fg="white",
            activebackground="#7aa3c7",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=12,
            pady=6
        ).pack(pady=8)
        
        # Focus the first entry field
        if self.entries:
            self.entries[0].focus_set()
        
    def _confirm(self):
        """Handle confirm button."""
        values = [e.get().strip() for e in self.entries]
        if self.on_confirm:
            self.on_confirm(values)
        self._on_close()


class AddColumnPopup(PopupDialog):
    """Popup for choosing which box to add columns to."""
    
    def __init__(self, parent, app_reference, relative_widget=None):
        self.app_reference = app_reference
        # Start with minimal size, will be adjusted after content
        super().__init__(parent, "", 50, 50, relative_widget)
        
    def _setup_content(self):
        """Setup the subtle add column popup content."""
        # Subtle header section
        header_frame = tk.Frame(self.popup, bg="#d4d8dc", height=40)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="Νέα Στήλη",
            bg="#d4d8dc",
            fg="#424040",
            font=("Segoe UI", 11, "bold")
        )
        title_label.pack(expand=True)
        
        # Content frame
        content_frame = tk.Frame(self.popup, bg="#e8ebf0")
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Subtle instruction label
        instruction_label = tk.Label(
            content_frame,
            text="Επιλέξτε κουτί:",
            font=("Segoe UI", 9),
            bg="#e8ebf0",
            fg="#424040"
        )
        instruction_label.pack(pady=(0, 8))
        
        # Box selection buttons
        boxes = [
            ("Κουτί 1", "tree1"),
            ("Κουτί 2", "tree2"), 
            ("Κουτί 3", "tree3"),
            ("Κουτί 4", "tree4")
        ]
        
        button_frame = tk.Frame(content_frame, bg="#e8ebf0")
        button_frame.pack(fill="x")
        
        for i, (display_name, tree_name) in enumerate(boxes):
            btn = tk.Button(
                button_frame,
                text=display_name,
                command=lambda t=tree_name: self._add_column_to_box(t),
                font=("Segoe UI", 9),
                bg="#8ab4d8",
                fg="white",
                activebackground="#7aa3c7",
                activeforeground="white",
                relief="flat",
                bd=0,
                cursor="hand2",
                padx=12,
                pady=4
            )
            btn.pack(pady=3, fill="x")
        
    def _add_column_to_box(self, tree_name):
        """Add a column to the specified tree."""
        # Ask for column name
        column_name = simpledialog.askstring(
            "Νέα Στήλη",
            f"Όνομα νέας στήλης για {tree_name.upper()}:",
            parent=self.popup
        )
        
        if column_name and column_name.strip():
            self.app_reference._add_column_to_tree(tree_name, column_name.strip())
            self._on_close()


class RemoveColumnPopup(PopupDialog):
    """Popup for choosing which box to remove columns from."""
    
    def __init__(self, parent, app_reference, relative_widget=None):
        self.app_reference = app_reference
        # Start with minimal size, will be adjusted after content
        super().__init__(parent, "", 50, 50, relative_widget)
        
    def _setup_content(self):
        """Setup the content of the remove column popup."""
        # Header with subtle background
        header = tk.Frame(self.popup, bg="#d4d8dc", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_label = tk.Label(
            header,
            text="Αφαίρεση Στήλης",
            font=("Segoe UI", 6, "bold"),
            bg="#d4d8dc",
            fg="#2c3e50"
        )
        header_label.pack(expand=True)
        
        # Main content area
        content_frame = tk.Frame(self.popup, bg="#e8ebf0")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Select box label
        select_label = tk.Label(
            content_frame,
            text="Επιλέξτε κουτί:",
            font=("Segoe UI", 11, "bold"),
            bg="#e8ebf0",
            fg="#2c3e50"
        )
        select_label.pack(anchor="w", pady=(5, 8))
        
        # Box selection buttons
        boxes = [
            ("Κουτί 1", "tree1"),
            ("Κουτί 2", "tree2"),
            ("Κουτί 3", "tree3"),
            ("Κουτί 4", "tree4")
        ]
        
        button_added = False
        for i, (display_name, tree_name) in enumerate(boxes):
            # Check if tree has columns that can be removed
            tree_manager = self.app_reference.tree_managers[tree_name]
            if len(tree_manager.columns) > 1:  # Only show if more than 1 column
                btn = tk.Button(
                    content_frame,
                    text=display_name,
                    command=lambda t=tree_name: self._remove_column_from_box(t),
                    font=("Segoe UI", 11),
                    bg="#8ab4d8",
                    fg="#2c3e50",
                    activebackground="#7ba7d1",
                    activeforeground="#2c3e50",
                    relief="flat",
                    bd=0,
                    cursor="hand2",
                    width=15,
                    pady=8
                )
                btn.pack(pady=3)
                button_added = True
        
        # If no buttons were added, show a message
        if not button_added:
            no_columns_label = tk.Label(
                content_frame,
                text="Δεν υπάρχουν στήλες\nπρος αφαίρεση",
                font=("Segoe UI", 10),
                bg="#e8ebf0",
                fg="#666",
                justify="center"
            )
            no_columns_label.pack(pady=10)
        
    def _remove_column_from_box(self, tree_name):
        """Remove a column from the specified tree."""
        tree_manager = self.app_reference.tree_managers[tree_name]
        
        if len(tree_manager.columns) <= 1:
            messagebox.showwarning(
                "Προειδοποίηση",
                "Δεν μπορείτε να αφαιρέσετε την τελευταία στήλη!",
                parent=self.popup
            )
            return
            
        # Show column selection popup
        column_popup = tk.Toplevel(self.popup)
        column_popup.title("")
        column_popup.configure(bg="#e8ebf0")
        column_popup.resizable(False, False)
        column_popup.transient(self.popup)
        column_popup.grab_set()
        
        # Header
        header = tk.Frame(column_popup, bg="#d4d8dc", height=40)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_label = tk.Label(
            header,
            text="Επιλογή Στήλης",
            font=("Segoe UI", 12, "bold"),
            bg="#d4d8dc",
            fg="#2c3e50"
        )
        header_label.pack(expand=True)
        
        # Main content container
        content_frame = tk.Frame(column_popup, bg="#e8ebf0")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Select column label
        select_label = tk.Label(
            content_frame,
            text="Επιλέξτε στήλη:",
            font=("Segoe UI", 10, "bold"),
            bg="#e8ebf0",
            fg="#2c3e50"
        )
        select_label.pack(anchor="w", pady=(0, 5))
        
        # Column buttons
        for i, column_name in enumerate(tree_manager.columns):
            btn = tk.Button(
                content_frame,
                text=f"{i+1}. {column_name}",
                command=lambda idx=i: self._confirm_remove_column(tree_name, idx, column_popup),
                font=("Segoe UI", 10),
                bg="#8ab4d8",
                fg="#2c3e50",
                activebackground="#7ba7d1",
                activeforeground="#2c3e50",
                relief="flat",
                bd=0,
                cursor="hand2",
                width=20,
                pady=6
            )
            btn.pack(pady=2)
            
        # Cancel button
        cancel_btn = tk.Button(
            content_frame,
            text="Άκυρο",
            command=column_popup.destroy,
            font=("Segoe UI", 10, "bold"),
            bg="#8ab4d8",
            fg="#2c3e50",
            activebackground="#7ba7d1",
            activeforeground="#2c3e50",
            relief="flat",
            bd=0,
            cursor="hand2",
            width=12,
            pady=6
        )
        cancel_btn.pack(pady=(10, 0))
        
        # Update size and position after adding content
        column_popup.update_idletasks()
        
        # Center the popup relative to the parent popup
        x = self.popup.winfo_x() + (self.popup.winfo_width() - column_popup.winfo_reqwidth()) // 2
        y = self.popup.winfo_y() + (self.popup.winfo_height() - column_popup.winfo_reqheight()) // 2
        column_popup.geometry(f"+{x}+{y}")
        
    def _confirm_remove_column(self, tree_name, column_index, column_popup):
        """Confirm and remove the selected column."""
        self.app_reference._remove_column_from_tree(tree_name, column_index)
        column_popup.destroy()
        self._on_close()


class DataManager:
    """Manages application data persistence."""
    
    @staticmethod
    def _get_script_file_path():
        """Get the data file path in the same directory as the script."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, Config.DATA_FILE)
    
    @staticmethod
    def save_all_data(data: Dict[str, Any]):
        """Save all application data to a single JSON file in the same directory as the program."""
        file_path = DataManager._get_script_file_path()
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Create a temporary file first
            temp_file = file_path + ".tmp"
            
            # Write to temporary file first
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # If temporary file was written successfully, replace the original
            if os.path.exists(file_path):
                # Remove read-only attribute if it exists
                try:
                    os.chmod(file_path, 0o666)
                except:
                    pass
            
            # Replace the original file with the temporary file
            if os.path.exists(temp_file):
                os.replace(temp_file, file_path)
            
            return True
        except Exception as e:
            print(f"Error saving to {file_path}: {e}")
            # Clean up temporary file if it exists
            temp_file_cleanup = file_path + ".tmp"
            if os.path.exists(temp_file_cleanup):
                try:
                    os.remove(temp_file_cleanup)
                except:
                    pass
            print("Please check file permissions or run as administrator")
            return False
            
    @staticmethod
    def load_all_data() -> Dict[str, Any]:
        """Load all application data from the JSON file in the same directory as the program."""
        file_path = DataManager._get_script_file_path()
        
        try:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading from {file_path}: {e}")
        
        print(f"No data file found at: {file_path}")
        return {}
            
    @staticmethod
    def save_data(data: Dict[str, Any]):
        """Save tree data (legacy method for compatibility)."""
        # Load existing data
        all_data = DataManager.load_all_data()
        
        # Update tree data
        all_data.update(data)
        
        # Save back
        return DataManager.save_all_data(all_data)
            
    @staticmethod
    def load_data() -> Dict[str, Any]:
        """Load tree data (legacy method for compatibility)."""
        all_data = DataManager.load_all_data()
        
        # Extract only tree-related data for backward compatibility
        tree_data = {}
        for key in ['tree1', 'tree2', 'tree3', 'tree4', 'columns1', 'columns2', 'columns3', 'columns4']:
            if key in all_data:
                tree_data[key] = all_data[key]
        
        return tree_data
            
    @staticmethod
    def save_geometry(geometry: str):
        """Save window geometry."""
        DataManager._save_simple_data("geometry", geometry)
            
    @staticmethod
    def load_geometry() -> Optional[str]:
        """Load window geometry."""
        return DataManager._load_simple_data("geometry")
        
    @staticmethod
    def save_column_widths(tree_widths: Dict[str, Dict[str, int]]):
        """Save column widths for all trees."""
        DataManager._save_simple_data("column_widths", tree_widths)
            
    @staticmethod
    def load_column_widths() -> Dict[str, Dict[str, int]]:
        """Load column widths for all trees."""
        return DataManager._load_simple_data("column_widths", {})
    
    @staticmethod
    def save_column_alignments(tree_alignments: Dict[str, Dict[int, str]]):
        """Save column alignments for all trees."""
        DataManager._save_simple_data("column_alignments", tree_alignments)
            
    @staticmethod
    def load_column_alignments() -> Dict[str, Dict[int, str]]:
        """Load column alignments for all trees."""
        return DataManager._load_simple_data("column_alignments", {})
    
    @staticmethod
    def _save_simple_data(key: str, value: Any):
        """Helper method to save a single data value."""
        try:
            # Load existing data
            all_data = DataManager.load_all_data()
            
            # Update the value
            all_data[key] = value
            
            # Save back
            DataManager.save_all_data(all_data)
        except Exception as e:
            print(f"Error saving {key}: {e}")
            
    @staticmethod
    def _load_simple_data(key: str, default: Any = None):
        """Helper method to load a single data value."""
        try:
            all_data = DataManager.load_all_data()
            return all_data.get(key, default)
        except Exception as e:
            print(f"Error loading {key}: {e}")
            return default


class PrintPreviewDialog:
    """Print preview dialog window."""
    
    def __init__(self, parent, content: str):
        self.parent = parent
        self.content = content
        self.preview_window = None
        
    def show(self):
        """Show the print preview dialog."""
        self.preview_window = tk.Toplevel(self.parent)
        self.preview_window.title("")
        self.preview_window.configure(bg="#e8ebf0")
        self.preview_window.geometry("700x600")
        
        # Center the window
        self.preview_window.transient(self.parent)
        self.preview_window.grab_set()
        
        # Create the preview content
        self._setup_preview_content()
        
        # Create buttons
        self._setup_buttons()
        
        # Position window relative to parent
        self._center_window()
        
    def _setup_preview_content(self):
        """Setup the preview content area."""
        # Header
        header = tk.Frame(self.preview_window, bg="#d4d8dc", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_label = tk.Label(
            header,
            text="Προεπισκόπηση Εκτύπωσης",
            font=("Segoe UI", 16, "bold"),
            bg="#d4d8dc",
            fg="#2c3e50"
        )
        header_label.pack(expand=True)
        
        # Instructions for editing
        instructions_label = tk.Label(
            self.preview_window,
            text="Μπορείτε να επεξεργαστείτε το κείμενο πριν την εκτύπωση (Ctrl+A: Επιλογή όλων)",
            font=("Segoe UI", 10),
            bg="#e8ebf0",
            fg="#666"
        )
        instructions_label.pack(pady=8)
        
        # Content frame with scrollbar
        content_frame = tk.Frame(self.preview_window, bg="#e8ebf0")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Text widget with scrollbar - EDITABLE
        self.text_widget = tk.Text(
            content_frame,
            wrap="word",
            bg="white",
            fg="black",
            font=("Courier New", 11),
            relief="sunken",
            bd=2,
            state="normal",  # Keep editable
            insertbackground="black",  # Cursor color
            selectbackground="#3582c4",  # Selection color
            selectforeground="white"
        )
        
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and text widget
        scrollbar.pack(side="right", fill="y")
        self.text_widget.pack(side="left", fill="both", expand=True)
        
        # Insert content
        self.text_widget.insert("1.0", self.content)
        # Keep it editable - don't disable it
        
        # Add keyboard shortcuts for better editing experience
        self.text_widget.bind("<Control-a>", self._select_all)
        self.text_widget.bind("<Control-A>", self._select_all)
        
        # Focus on text widget for immediate editing
        self.text_widget.focus_set()
        
    def _select_all(self, event=None):
        """Select all text in the text widget."""
        self.text_widget.tag_add("sel", "1.0", "end")
        return "break"  # Prevent default behavior
        
    def _setup_buttons(self):
        """Setup the dialog buttons."""
        button_frame = tk.Frame(self.preview_window, bg="#e8ebf0")
        button_frame.pack(fill="x", padx=30, pady=(10, 30))
        
        # Reset button (restore original content)
        reset_btn = tk.Button(
            button_frame,
            text="Επαναφορά",
            command=self._reset_content,
            font=("Segoe UI", 10, "bold"),
            bg="#8ab4d8",
            fg="#2c3e50",
            activebackground="#7ba7d1",
            activeforeground="#2c3e50",
            width=12,
            pady=8,
            relief="flat",
            bd=0,
            cursor="hand2"
        )
        reset_btn.pack(side="left", padx=(0, 10))
        
        # Print button
        print_btn = tk.Button(
            button_frame,
            text="Εκτύπωση",
            command=self._confirm_print,
            font=("Segoe UI", 10, "bold"),
            bg="#8ab4d8",
            fg="#2c3e50",
            activebackground="#7ba7d1",
            activeforeground="#2c3e50",
            width=18,
            pady=8,
            relief="flat",
            bd=0,
            cursor="hand2"
        )
        print_btn.pack(side="left", padx=(0, 15))
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Άκυρο",
            command=self._cancel_print,
            font=("Segoe UI", 10, "bold"),
            bg="#8ab4d8",
            fg="#2c3e50",
            activebackground="#7ba7d1",
            activeforeground="#2c3e50",
            width=18,
            pady=8,
            relief="flat",
            bd=0,
            cursor="hand2"
        )
        cancel_btn.pack(side="left")
        
    def _reset_content(self):
        """Reset the text widget to original content."""
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", self.content)
        self.text_widget.focus_set()
        
    def _center_window(self):
        """Center the preview window on the parent."""
        self.preview_window.update_idletasks()
        
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        window_width = self.preview_window.winfo_width()
        window_height = self.preview_window.winfo_height()
        
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        self.preview_window.geometry(f"+{x}+{y}")
        
    def _confirm_print(self):
        """Confirm and proceed with printing using the edited content."""
        # Get the edited content from the text widget
        edited_content = self.text_widget.get("1.0", "end-1c")  # Get all text except final newline
        self.preview_window.destroy()
        PrintManager._execute_print(edited_content)
        
    def _cancel_print(self):
        """Cancel printing and close preview."""
        self.preview_window.destroy()


class PrintManager:
    """Handles printing functionality."""
    
    @staticmethod
    def print_data(tree1_data, tree2_data, tree3_data, tree4_data, parent_window):
        """Show print preview before printing data from multiple trees."""
        content = PrintManager._prepare_content(tree1_data, tree2_data, tree3_data, tree4_data)
        
        if not content.strip():
            messagebox.showinfo("Box1/Box2/Box3/Box4", "Δεν υπάρχουν δεδομένα.")
            return
            
        # Show print preview
        preview = PrintPreviewDialog(parent_window, content)
        preview.show()
    
    @staticmethod
    def _prepare_content(tree1_data, tree2_data, tree3_data, tree4_data):
        """Prepare content for printing."""
        content = "=== ΑΝΑΦΟΡΑ ΔΕΔΟΜΕΝΩΝ ===\n\n"
        
        # Add Box1 data
        box1_has_data = False
        box1_row_count = 0
        content += "ΠΕΛΑΤΕΣ/ΠΑΡΑΓΓΕΛΙΕΣ:\n"
        content += "-" * 40 + "\n"
        
        for values in tree1_data:
            if any(str(v).strip() for v in values):
                box1_has_data = True
                box1_row_count += 1
                customer = values[0] if values[0] else "N/A"
                quantity = values[1] if values[1] else "N/A"
                price = values[2] if values[2] else "N/A"
                distributor = values[3] if values[3] else "N/A"
                content += f"Πελάτης: {customer}, Ποσότητα: {quantity}, Τιμή: {price}, Διανομέας: {distributor}\n"
        
        if not box1_has_data:
            content += "Δεν υπάρχουν δεδομένα\n"
        content += "\n"
        
        # Add Box2 data
        box2_has_data = False
        content += "ΔΙΑΝΟΜΕΙΣ/ΤΑΜΕΙΟ:\n"
        content += "-" * 40 + "\n"
        
        for values in tree2_data:
            if any(str(v).strip() for v in values):
                box2_has_data = True
                distributor = values[0] if values[0] else "N/A"
                amount = values[1] if values[1] else "N/A"
                content += f"Διανομέας: {distributor}, Ταμείο: {amount}\n"
        
        if not box2_has_data:
            content += "Δεν υπάρχουν δεδομένα\n"
        content += "\n"
        
        # Add Box3 data
        box3_has_data = False
        content += "ΒΑΣΗ ΠΕΛΑΤΩΝ:\n"
        content += "-" * 40 + "\n"
        
        for values in tree3_data:
            if any(str(v).strip() for v in values):
                box3_has_data = True
                customer = values[0] if values[0] else "N/A"
                quantity = values[1] if values[1] else "N/A"
                price = values[2] if values[2] else "N/A"
                distributor = values[3] if values[3] else "N/A"
                content += f"Πελάτης: {customer}, Ποσότητα: {quantity}, Τιμή: {price}, Διανομέας: {distributor}\n"
        
        if not box3_has_data:
            content += "Δεν υπάρχουν δεδομένα\n"
        content += "\n"
        
        # Add Box4 data
        box4_has_data = False
        content += "ΕΣΟΔΑ/ΕΞΟΔΑ:\n"
        content += "-" * 40 + "\n"
        
        for values in tree4_data:
            if any(str(v).strip() for v in values):
                box4_has_data = True
                income = values[0] if values[0] else "N/A"
                expense = values[1] if values[1] else "N/A"
                content += f"Έσοδα: {income}, Έξοδα: {expense}\n"
        
        if not box4_has_data:
            content += "Δεν υπάρχουν δεδομένα\n"
        content += "\n"
        
        # Add summary
        content += "=" * 50 + "\n"
        content += f"Σύνολο Παραγγελιών: {box1_row_count}\n"
        content += "=" * 50 + "\n"
        content += f"Ημερομηνία εκτύπωσης: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        
        return content
    
    @staticmethod
    def _execute_print(content):
        """Execute the actual printing."""
        try:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix='.txt', mode='w', encoding='utf-8'
            ) as tmpfile:
                tmpfile.write(content)
                filename = tmpfile.name
                
            if sys.platform == "win32":
                os.startfile(filename, "print")
            elif sys.platform == "darwin":
                os.system(f'lpr "{filename}"')
            else:
                os.system(f'xdg-open "{filename}"')
                
            messagebox.showinfo(
                "Εκτύπωση",
                "Άνοιξε το παράθυρο εκτύπωσης. Ελέγξτε τις ρυθμίσεις εκτυπωτή σας."
            )
        except Exception as e:
            messagebox.showerror("Σφάλμα εκτύπωσης", f"Δεν ήταν δυνατή η εκτύπωση: {e}")


class BusinessApp:
    """Main application class."""
    
    def __init__(self):
        # Show drive selection popup first
        drive_popup = DriveSelectionPopup()
        self.monitored_drive, popup_root = drive_popup.show()
        
        # Use the popup's root window if available, otherwise create new one
        if popup_root:
            self.root = popup_root
            # Clear the popup content and reconfigure for main app
            for widget in self.root.winfo_children():
                widget.destroy()
        else:
            self.root = tk.Tk()
            
        self.tree_managers = {}
        self.popups = {}
        self.all_tree3_items = []
        self.resize_job = None
        self.drive_monitor_active = False
        
        # Undo/Redo system
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo_steps = 20
        
        self._setup_window()
        self._setup_styles()
        self._setup_ui()
        self._setup_bindings()
        self._setup_tree_references()
        self._load_data()
        # Load column widths and alignments after UI is fully initialized
        self.root.after_idle(self._load_column_widths)
        self.root.after_idle(self._load_column_alignments)
        
        # Start drive monitoring if a drive was selected
        if self.monitored_drive:
            self._start_drive_monitoring()
            
    def _start_drive_monitoring(self):
        """Start monitoring the selected drive."""
        self.drive_monitor_active = True
        
        def monitor_drive():
            while self.drive_monitor_active:
                try:
                    if not os.path.exists(f"{self.monitored_drive}\\"):
                        # Drive was removed - close application immediately
                        self.root.after(0, self._close_application_due_to_drive_removal)
                        break
                    time.sleep(1)  # Check every 1 second
                except Exception as e:
                    print(f"Drive monitoring error: {e}")
                    time.sleep(2)  # Wait longer on error
                    
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=monitor_drive, daemon=True)
        monitor_thread.start()
        
    def _close_application_due_to_drive_removal(self):
        """Close application immediately when monitored drive is removed."""
        # Stop drive monitoring
        self.drive_monitor_active = False
        
        # Force close the application immediately without warning
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
        
        # Force exit if GUI doesn't close properly
        os._exit(0)
        
    def _setup_window(self):
        """Setup main window properties."""
        self.root.title("Businest")
        self.root.geometry("1200x800")
        self.root.configure(bg=Config.BG_COLOR)
        self.root.resizable(False, False)
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            
    def _setup_styles(self):
        """Setup fonts and styles."""
        try:
            self.main_font = tkfont.Font(family="Noto Sans", size=Config.DEFAULT_FONT_SIZE, weight="bold")
        except tk.TclError:
            self.main_font = tkfont.Font(family="Arial", size=Config.DEFAULT_FONT_SIZE, weight="bold")
            
        self.btn_font = tkfont.Font(
            family=self.main_font.actual("family"), 
            size=Config.BUTTON_FONT_SIZE, 
            weight="bold"
        )
        
        # Create a bigger font for headers
        self.header_font = tkfont.Font(
            family=self.main_font.actual("family"), 
            size=Config.DEFAULT_FONT_SIZE + 2,
            weight="bold"
        )
        
        # Create a font for tree2 rows (slightly smaller)
        self.tree2_font = tkfont.Font(
            family="Helvetica", 
            size=13,
            weight="bold"
        )
        
        # Unified professional button style
        self.btn_style = {
            "font": self.btn_font,
            "bg": "#2c3e50",
            "fg": "white",
            "activebackground": "#34495e",
            "activeforeground": "white",
            "width": 16,
            "height": 1,
            "relief": "flat",
            "bd": 0,
            "cursor": "hand2",
            "padx": 8,
            "pady": 4
        }
        
        # Create uniform button style like tree1 buttons (smaller font, consistent styling)
        self.btn_style_uniform = {
            "font": tkfont.Font(
                family=self.btn_font.actual("family"), 
                size=10,  # Smaller font for compact fit
                weight="bold"
            ),
            "bg": "#34495e",        # Slightly darker for better contrast in space box
            "fg": "white",
            "activebackground": "#2c3e50",
            "activeforeground": "white",
            "width": 16,
            "height": 1,
            "relief": "flat",
            "bd": 0,
            "cursor": "hand2",
            "padx": 8,
            "pady": 4
        }
        
        # Setup ttk styles
        style = ttk.Style(self.root)
        style.theme_use("default")
        
        # Default treeview style
        style.configure("Treeview",
                       background=Config.LIGHT_BLUE,
                       rowheight=32,
                       foreground="black",
                       fieldbackground=Config.LIGHT_BLUE,
                       font=('Helvetica', 12, 'bold'),
                       borderwidth=0,      # Remove cell borders
                       relief="flat")      # Flat relief for no borders
                       
        # Bigger headers for all treeviews
        style.configure("Treeview.Heading",
                       background=Config.HEADER_BG,
                       foreground="white",
                       font=self.header_font)
        
        # Special style for tree2 with thinner rows
        style.configure("Tree2.Treeview",
                       background=Config.LIGHT_BLUE,
                       rowheight=28,  # Reduced row height for tighter spacing
                       foreground="black",
                       fieldbackground=Config.LIGHT_BLUE,
                       font=self.tree2_font)
        
        # Headers for tree2 (same as default but ensuring it applies)
        style.configure("Tree2.Treeview.Heading",
                       background=Config.HEADER_BG,
                       foreground="white",
                       font=self.header_font)
        
        # Special style for tree4 with thinner rows
        style.configure("Tree4.Treeview",
                       background=Config.LIGHT_BLUE,
                       rowheight=24,  # Thinner rows for compact display
                       foreground="black",
                       fieldbackground=Config.LIGHT_BLUE,
                       font=('Helvetica', 11, 'bold'))
        
        # Headers for tree4
        style.configure("Tree4.Treeview.Heading",
                       background=Config.HEADER_BG,
                       foreground="white",
                       font=self.header_font)
                       
        style.map("Treeview",
                 background=[('selected', Config.SELECTED_BG)],
                 foreground=[('selected', 'white')])
        
        style.map("Tree2.Treeview",
                 background=[('selected', Config.SELECTED_BG)],
                 foreground=[('selected', 'white')])
        
        style.map("Tree4.Treeview",
                 background=[('selected', Config.SELECTED_BG)],
                 foreground=[('selected', 'white')])
                 
    def _setup_ui(self):
        """Setup the user interface."""
        self._create_tree1_panel()
        self._create_tree2_4_panel()
        self._create_tree3_panel()
        
    def _create_tree1_panel(self):
        """Create the first tree panel (customers/orders) with modern styling."""
        # Outer shadow frame - matching other boxes
        self.shadow_frame1 = tk.Frame(
            self.root,
            bg="#e8e8e8",
            relief="flat",
            bd=0,
            width=430
        )
        self.shadow_frame1.pack(side="left", fill="both", expand=False, padx=8, pady=8)
        self.shadow_frame1.pack_propagate(False)
        
        # Main frame container - matching other boxes
        frame1_container = tk.Frame(
            self.shadow_frame1, 
            bg=Config.BG_COLOR,
            relief="flat",
            bd=0,
            highlightbackground="#d0d0d0",
            highlightthickness=1
        )
        frame1_container.pack(fill="both", expand=True, padx=(0, 1), pady=(0, 1))
        
        # Inner frame for tree content
        frame1 = tk.Frame(
            frame1_container, 
            bg=Config.BG_COLOR,
            relief="flat",
            bd=0,
            highlightbackground="#d0d0d0",
            highlightthickness=1
        )
        frame1.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Create tree manager with modern styling
        columns1 = ["Πελάτης", "Ποσότητα", "Τιμή", "Διανομέας"]
        self.tree_managers['tree1'] = TreeManager(frame1, columns1, tree_name="tree1")
        self.tree_managers['tree1'].pack_tree()
        
        # Initialize with empty rows
        for _ in range(20):
            empty_values = tuple("" for _ in range(len(columns1)))
            self.tree_managers['tree1'].tree.insert("", "end", values=empty_values)
        self.tree_managers['tree1'].apply_gridlines()
        
        # Create modern space box container for buttons with enhanced styling
        space_box_outer = tk.Frame(frame1, bg=Config.SPACE_BOX_SHADOW, relief="flat", bd=0)
        space_box_outer.pack(fill="x", padx=8, pady=(8, 8))
        
        # Inner space box with rounded appearance simulation
        space_box_inner = tk.Frame(
            space_box_outer, 
            bg=Config.SPACE_BOX_BG,
            relief="flat",
            bd=0,
            highlightbackground=Config.SPACE_BOX_BORDER,
            highlightthickness=1
        )
        space_box_inner.pack(fill="x", padx=2, pady=2)
        
        # Create buttons frame inside the space box
        btns_frame = tk.Frame(space_box_inner, bg=Config.SPACE_BOX_BG)
        btns_frame.pack(fill="x", padx=12, pady=8)
        
        # Configure grid columns for even distribution (5 buttons + 2 counters = 7 elements)
        for i in range(5):  # 5 buttons get equal weight
            btns_frame.grid_columnconfigure(i, weight=1, uniform="buttons")
        btns_frame.grid_columnconfigure(5, weight=0)  # Pending counter takes minimal space
        btns_frame.grid_columnconfigure(6, weight=0)  # Total counter takes minimal space
        
        # Row 0: All buttons in a single row with even distribution
        tk.Button(
            btns_frame, 
            text="Undo",
            command=self._undo_action, 
            **self.btn_style_uniform
        ).grid(row=0, column=0, padx=2, sticky="ew")
        
        tk.Button(
            btns_frame, 
            text="Redo",
            command=self._redo_action, 
            **self.btn_style_uniform
        ).grid(row=0, column=1, padx=2, sticky="ew")
        
        tk.Button(
            btns_frame, 
            text="Clean",
            command=self._clear_tree1, 
            **self.btn_style_uniform
        ).grid(row=0, column=2, padx=2, sticky="ew")
        
        self.add_column_btn = tk.Button(
            btns_frame, 
            text="+",
            command=self._show_add_column_popup, 
            **self.btn_style_uniform
        )
        self.add_column_btn.grid(row=0, column=3, padx=2, sticky="ew")
        
        self.remove_column_btn = tk.Button(
            btns_frame, 
            text="-",
            command=self._show_remove_column_popup, 
            **self.btn_style_uniform
        )
        self.remove_column_btn.grid(row=0, column=4, padx=2, sticky="ew")
        
        # Pending rows counter (blinking rows) - shows on the left
        self.tree1_pending_label = tk.Label(
            btns_frame,
            text="0",
            font=tkfont.Font(
                family=self.btn_font.actual("family"), 
                size=10,  # Same font size as buttons
                weight="bold"
            ),
            bg="#e74c3c",  # Red background to indicate pending/incomplete
            fg="#ffffff",
            anchor="center",
            relief="flat",
            bd=0,      # No border like buttons
            width=4,   # Compact width
            height=1,  # Same height as buttons
            padx=8,    # Match button padding
            pady=4     # Match button padding
        )
        self.tree1_pending_label.grid(row=0, column=5, padx=(8, 2), sticky="ew")
        
        # Add tooltip for pending counter
        try:
            from tkinter import messagebox
            def show_pending_tooltip(event):
                # Simple tooltip - using status or creating basic one
                pass
            self.tree1_pending_label.bind("<Button-3>", show_pending_tooltip)  # Right-click for info
        except:
            pass  # Skip tooltip if not available
        
        # Total row count display - matches button height and appearance exactly
        self.tree1_count_label = tk.Label(
            btns_frame,
            text="0",
            font=tkfont.Font(
                family=self.btn_font.actual("family"), 
                size=10,  # Same font size as buttons
                weight="bold"
            ),
            bg="#34495e",  # Slightly different shade to distinguish
            fg="#ffffff",
            anchor="center",
            relief="flat",
            bd=0,      # No border like buttons
            width=4,   # Compact width
            height=1,  # Same height as buttons
            padx=8,    # Match button padding
            pady=4     # Match button padding
        )
        self.tree1_count_label.grid(row=0, column=6, padx=(2, 0), sticky="ew")
        
    def _create_tree2_4_panel(self):
        """Create the middle panel with tree2 (distributors) and tree4 (finances)."""
        # Outer shadow frame
        self.shadow_frame2 = tk.Frame(
            self.root,
            bg="#e8e8e8",
            relief="flat",
            bd=0,
            width=287
        )
        self.shadow_frame2.pack(side="left", fill="both", expand=False, padx=8, pady=8)
        self.shadow_frame2.pack_propagate(False)
        
        self.tree2_4_frame = tk.Frame(
            self.shadow_frame2, 
            bg=Config.BG_COLOR,
            relief="flat",
            bd=0,
            highlightbackground="#d0d0d0",
            highlightthickness=1
        )
        self.tree2_4_frame.pack(fill="both", expand=True, padx=(0, 1), pady=(0, 1))
        
        # Tree2 - Distributors
        columns2 = ["ΔΙΑΝΟΜΕΑΣ", "ΤΑΜΕΙΟ"]
        self.tree_managers['tree2'] = TreeManager(self.tree2_4_frame, columns2, height=12, tree_name="tree2")
        self.tree_managers['tree2'].pack_tree()
        
        # Add default distributors
        for name in ["ΓΙΑΝΝΗΣ", "ΝΙΚΟΣ", "ΜΑΡΙΑ"]:
            self.tree_managers['tree2'].tree.insert("", "end", values=(name, "0.00€"))
            
        # Create modern space box container for tree2 buttons
        space_box_outer2 = tk.Frame(self.tree2_4_frame, bg=Config.SPACE_BOX_SHADOW, relief="flat", bd=0)
        space_box_outer2.pack(fill="x", padx=8, pady=(8, 4))
        
        # Inner space box with rounded appearance simulation
        space_box_inner2 = tk.Frame(
            space_box_outer2, 
            bg=Config.SPACE_BOX_BG,
            relief="flat",
            bd=0,
            highlightbackground=Config.SPACE_BOX_BORDER,
            highlightthickness=1
        )
        space_box_inner2.pack(fill="x", padx=2, pady=2)
        
        # Tree2 buttons - balanced three-column layout with equal sizing
        btn_frame2 = tk.Frame(space_box_inner2, bg=Config.SPACE_BOX_BG)
        btn_frame2.pack(fill="x", padx=12, pady=8)
        
        # Configure grid columns to be equal width
        btn_frame2.grid_columnconfigure(0, weight=1, uniform="buttons")
        btn_frame2.grid_columnconfigure(1, weight=1, uniform="buttons") 
        btn_frame2.grid_columnconfigure(2, weight=1, uniform="buttons")
        
        # Left button - uses grid for equal distribution
        self.add_distributor_btn = tk.Button(
            btn_frame2, 
            text="Διανομέας",
            command=self._add_distributor, 
            **self.btn_style_uniform
        )
        self.add_distributor_btn.grid(row=0, column=0, padx=2, sticky="ew")
        
        # Center frame for flash drive - equal width with buttons
        center_frame = tk.Frame(btn_frame2, bg=Config.SPACE_BOX_BG)
        center_frame.grid(row=0, column=1, padx=4, sticky="ew")
        
        # Drive monitoring status - centered in middle frame
        if self.monitored_drive:
            self.drive_status_label = tk.Label(
                center_frame,
                text=f"USB: {self.monitored_drive}",
                font=("Courier New", 10, "bold"),
                bg="#2c3e50",  # Match button background for consistency
                fg="#00ff00",  # Bright green text for USB status
                relief="flat",
                bd=0,
                padx=8,
                pady=4
            )
            self.drive_status_label.pack(expand=True)
        
        # Right button - equal width with left button
        tk.Button(
            btn_frame2, 
            text="PRINT",
            command=self._print_data, 
            **self.btn_style_uniform
        ).grid(row=0, column=2, padx=2, sticky="ew")
        
        # Tree4 - Finances - reduced spacing
        # Outer shadow frame for tree4
        shadow_frame4 = tk.Frame(
            self.tree2_4_frame,
            bg="#e8e8e8",  # Very subtle shadow
            relief="flat",
            bd=0
        )
        shadow_frame4.pack(fill="x", pady=(6, 0), padx=1)
        
        frame4 = tk.Frame(
            shadow_frame4, 
            bg=Config.BG_COLOR,
            relief="flat",
            bd=0,
            highlightbackground="#d0d0d0",
            highlightthickness=1
        )
        frame4.pack(fill="x", padx=(0, 1), pady=(0, 1))
        
        columns4 = ["ΕΣΟΔΑ", "ΕΞΟΔΑ"]
        self.tree_managers['tree4'] = TreeManager(frame4, columns4, height=13, tree_name="tree4")
        
        self.tree_managers['tree4'].pack_tree()
        
        # Initialize tree4 with empty rows
        for _ in range(10):
            self.tree_managers['tree4'].tree.insert("", "end", values=("", ""))
        self.tree_managers['tree4'].apply_gridlines()
        
    def _create_tree3_panel(self):
        """Create the third tree panel (customer database)."""
        # Outer shadow frame
        self.shadow_frame3_super = tk.Frame(
            self.root,
            bg="#e8e8e8",
            relief="flat",
            bd=0,
            width=430
        )
        self.shadow_frame3_super.pack(side="left", fill="both", expand=False, padx=8, pady=8)
        self.shadow_frame3_super.pack_propagate(False)
        
        self.frame3_super = tk.Frame(
            self.shadow_frame3_super, 
            bg=Config.BG_COLOR,
            relief="flat",
            bd=0,
            highlightbackground="#d0d0d0",
            highlightthickness=1
        )
        self.frame3_super.pack(fill="both", expand=True, padx=(0, 1), pady=(0, 1))
        
        frame3 = tk.Frame(
            self.frame3_super, 
            bg=Config.BG_COLOR,
            relief="flat",
            bd=0,
            highlightbackground="#d0d0d0",
            highlightthickness=1
        )
        frame3.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        
        # Search entry
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            frame3,
            textvariable=self.search_var,
            bg="#eaf6fb",
            fg="black",
            insertbackground="black",
            font=self.main_font
        )
        search_entry.pack(fill="x", pady=(0, 3))
        self.search_var.trace_add("write", self._update_tree3_display)
        
        # Tree3
        columns3 = ["Πελάτης", "Ποσότητα", "Τιμή", "Διανομέας"]
        self.tree_managers['tree3'] = TreeManager(frame3, columns3, tree_name="tree3")
        
        self.tree_managers['tree3'].pack_tree()
        
        # Create modern space box container for tree3 controls
        space_box_outer3 = tk.Frame(frame3, bg=Config.SPACE_BOX_SHADOW, relief="flat", bd=0)
        space_box_outer3.pack(fill="x", padx=8, pady=(8, 8))
        
        # Inner space box with rounded appearance simulation
        space_box_inner3 = tk.Frame(
            space_box_outer3, 
            bg=Config.SPACE_BOX_BG,
            relief="flat",
            bd=0,
            highlightbackground=Config.SPACE_BOX_BORDER,
            highlightthickness=1
        )
        space_box_inner3.pack(fill="x", padx=2, pady=2)
        
        # Bottom controls - tighter layout
        controls_frame = tk.Frame(space_box_inner3, bg=Config.SPACE_BOX_BG)
        controls_frame.pack(fill="x", padx=12, pady=8)
        
        self.add_row_btn3 = tk.Button(
            controls_frame, 
            text="Νέος Πελάτης", 
            command=self._add_row_tree3,
            **self.btn_style_uniform
        )
        self.add_row_btn3.pack(side="left", pady=3, padx=(0, 3))
        
        # Toggle button - Professional style with X (minimal width, same height)
        self.x_btn = tk.Button(
            controls_frame, 
            text="X", 
            command=self._toggle_tree2_4,
            font=self.btn_style_uniform["font"],
            bg=self.btn_style_uniform["bg"],
            fg=self.btn_style_uniform["fg"],
            activebackground=self.btn_style_uniform["activebackground"],
            activeforeground=self.btn_style_uniform["activeforeground"],
            relief=self.btn_style_uniform["relief"],
            width=3,
            height=self.btn_style_uniform["height"],
            bd=self.btn_style_uniform["bd"],
            cursor=self.btn_style_uniform["cursor"],
            padx=self.btn_style_uniform["padx"],
            pady=self.btn_style_uniform["pady"]
        )
        self.x_btn.pack(side="left", pady=3, padx=(3, 3))
        
        # Saved notification - positioned between buttons, hidden by default
        self.saved_notification_label = tk.Label(
            controls_frame,
            text="",  # Empty by default - invisible
            font=("Courier New", 8, "bold"),  # Same font size as time display
            bg="#000000",  # Black background like Unix terminal
            fg="#000000",  # Black text to make it invisible by default
            relief="ridge",  # Raised border to match buttons
            bd=2,  # Thicker border like buttons
            highlightthickness=1,  # Add highlight border
            highlightbackground="#2c3e50",  # Match button border color
            highlightcolor="#34495e",  # Match button active color
            width=8,  # Same width as time display
            height=1,   # Match button height - same as X button
            padx=4,     # Adjusted padding 
            pady=2      # Adjusted padding
        )
        # Pack it with fixed spacing
        self.saved_notification_label.pack(side="left", padx=(10, 5), pady=3)
        
        # Time display label - positioned next to saved notification
        self.time_label = tk.Label(
            controls_frame,
            text="",
            font=("Courier New", 8, "bold"),  # Changed font size to 8
            bg="#000000",  # Black background like Unix terminal
            fg="#00ff00",  # Green text like terminal
            relief="ridge",  # Raised border to match other elements
            bd=2,  # Thicker border like buttons
            highlightthickness=1,  # Add highlight border
            highlightbackground="#2c3e50",  # Match button border color
            highlightcolor="#34495e",  # Match button active color
            width=8,  # Same width as saved notification for "HH:MM:SS"
            height=1,   # Match button height
            padx=4,     # Adjusted padding 
            pady=2      # Adjusted padding
        )
        self.time_label.pack(side="left", padx=(5, 10), pady=3)
        
        # Start the time update
        self._update_time()

    def _setup_bindings(self):
        """Setup event bindings."""
        self.root.bind("<Configure>", self._on_window_configure)
        
        # Tree editing bindings
        self.tree_managers['tree1'].tree.bind("<Double-1>", self._edit_tree1_cell)
        # Add backup single-click with Ctrl for easier editing
        self.tree_managers['tree1'].tree.bind("<Control-Button-1>", self._edit_tree1_cell)
        
        self.tree_managers['tree3'].tree.bind("<Double-1>", self._edit_tree3_cell)
        self.tree_managers['tree4'].tree.bind("<Double-1>", self._edit_tree4_cell)
        
        # Delete key bindings
        self.tree_managers['tree1'].tree.bind("<Delete>", self._delete_selected_tree1_key)
        self.tree_managers['tree2'].tree.bind("<Delete>", self._delete_selected_tree2)
        self.tree_managers['tree3'].tree.bind("<Delete>", self._delete_selected_tree3)
        
        # Click outside to deselect - bind to main window
        self.root.bind("<Button-1>", self._on_window_click)
        
        # Make headers renamable
        self._make_header_renamable('tree1')
        self._make_header_renamable('tree2')
        self._make_header_renamable('tree3')
        self._make_header_renamable('tree4')
    
    def _update_time(self):
        """Update the time display every second."""
        import datetime
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        if hasattr(self, 'time_label'):
            self.time_label.config(text=current_time)
        # Schedule the next update
        self.root.after(1000, self._update_time)
        
    def _setup_tree_references(self):
        """Setup references from tree managers to main app for autosaving."""
        for tree_manager in self.tree_managers.values():
            tree_manager.set_app_reference(self)
        
    def _make_header_renamable(self, tree_name: str):
        """Make tree headers interactive: left-click to cycle alignment, right-click to rename."""
        tree = self.tree_managers[tree_name].tree
        
        def on_header_left_click(event):
            region = tree.identify_region(event.x, event.y)
            if region != "heading":
                return
                
            col_id = tree.identify_column(event.x)
            col_index = int(col_id.replace("#", "")) - 1
            
            # Cycle through alignments: center -> left -> right -> center
            current_alignment = self.tree_managers[tree_name].column_alignments.get(col_index, "center")
            
            if current_alignment == "center":
                new_alignment = "w"  # left
            elif current_alignment == "w":
                new_alignment = "e"  # right
            else:  # "e" (right)
                new_alignment = "center"
            
            # Update the column alignment
            tree.column(col_id, anchor=new_alignment)
            self.tree_managers[tree_name].column_alignments[col_index] = new_alignment
            
            # Save alignment changes
            self._autosave_column_alignments()
        
        def on_header_right_click(event):
            region = tree.identify_region(event.x, event.y)
            if region != "heading":
                return
                
            col_id = tree.identify_column(event.x)
            col_index = int(col_id.replace("#", "")) - 1
            old_name = self.tree_managers[tree_name].columns[col_index]
            
            new_name = simpledialog.askstring(
                "Μετονομασία Κεφαλίδας",
                f"Νέο όνομα για τη στήλη '{old_name}':",
                parent=self.root,
                initialvalue=tree.heading(col_id, "text")
            )
            
            if new_name and new_name.strip() and new_name != tree.heading(col_id, "text"):
                self.tree_managers[tree_name].update_column_name(col_index, new_name)
                self._autosave()
                
        tree.bind("<Button-1>", on_header_left_click)
        tree.bind("<Button-3>", on_header_right_click)
        
    def _on_window_configure(self, event=None):
        """Handle window resize with debouncing."""
        if self.resize_job:
            self.root.after_cancel(self.resize_job)
        self.resize_job = self.root.after(200, self._redraw_gridlines)
        
        # Save geometry
        if event and event.widget == self.root:
            DataManager.save_geometry(self.root.winfo_geometry())
            
    def _redraw_gridlines(self):
        """Redraw gridlines for all trees."""
        for tree_manager in self.tree_managers.values():
            tree_manager.apply_gridlines()
            
    def _on_window_click(self, event):
        """Handle clicks on the main window to deselect tree items."""
        # Get the widget that was clicked
        clicked_widget = event.widget
        
        # Check if the click was on a tree or its scrollbar
        is_tree_click = False
        for tree_manager in self.tree_managers.values():
            if (clicked_widget == tree_manager.tree or 
                clicked_widget == tree_manager.scrollbar or
                str(clicked_widget).startswith(str(tree_manager.tree)) or
                str(clicked_widget).startswith(str(tree_manager.scrollbar))):
                is_tree_click = True
                break
        
        # If not a tree click, deselect all tree selections
        if not is_tree_click:
            for tree_manager in self.tree_managers.values():
                if tree_manager.tree.selection():
                    tree_manager.tree.selection_remove(tree_manager.tree.selection())
            
    def _ensure_one_empty_row_tree1(self):
        """Ensure tree1 always has at least one empty row at the end."""
        tree = self.tree_managers['tree1'].tree
        children = tree.get_children()
        
        # Get the number of columns for tree1
        num_columns = len(self.tree_managers['tree1'].columns)
        empty_values = tuple("" for _ in range(num_columns))
        
        if children:
            last_row = children[-1]
            values = tree.item(last_row, "values")
            if any(str(v).strip() for v in values):
                tree.insert("", "end", values=empty_values)
                self._redraw_gridlines()
        else:
            tree.insert("", "end", values=empty_values)
            self._redraw_gridlines()
            
    def _update_sumif(self):
        """Update the SUMIF-like calculations in tree2.
        Uses position-based logic that works regardless of header names."""
        tree1 = self.tree_managers['tree1'].tree
        tree2 = self.tree_managers['tree2'].tree
        
        # Calculate sums by distributor - position-based (index 2=price, index 3=distributor)
        sums = {}
        for row in tree1.get_children():
            values = tree1.item(row, "values")
            try:
                # Column 3 (index 2) is always the price column
                price = float(values[2]) if len(values) > 2 and values[2] else 0.0
            except (ValueError, IndexError):
                price = 0.0
                
            # Column 4 (index 3) is always the distributor column  
            distributor = values[3] if len(values) > 3 and values[3] else ""
            if distributor:
                sums[distributor] = sums.get(distributor, 0.0) + price
                
        # Update tree2 with calculated sums - position-based (column 1=distributor, column 2=total)
        for row in tree2.get_children():
            values = tree2.item(row, "values")
            # Column 1 (index 0) is distributor name in tree2
            dist = values[0] if len(values) > 0 else ""
            total = sums.get(dist, 0.0)
            # Column 2 (index 1) is total amount in tree2 - use position-based column reference
            tree2.set(row, f"#{2}", f"{total:.2f}€")
            
        # Update blinking for tree1 incomplete rows
        self.tree_managers['tree1'].apply_gridlines()
            
    def _update_box1_linecount(self):
        """Update the line count display for tree1."""
        tree = self.tree_managers['tree1'].tree
        count = 0
        for row in tree.get_children():
            values = tree.item(row, "values")
            if any(str(v).strip() for v in values):
                count += 1
        # Update the tree1 count label
        if hasattr(self, 'tree1_count_label'):
            self.tree1_count_label.config(text=str(count))
        
        # Update the pending count label
        self._update_pending_count()
    
    def _update_pending_count(self):
        """Update the pending (blinking) row count display."""
        if hasattr(self, 'tree1_pending_label'):
            tree = self.tree_managers['tree1'].tree
            items = tree.get_children()
            # Exclude the last (automated) row from pending count
            items_to_check = items[:-1] if len(items) > 0 else []
            pending_count = 0
            for item in items_to_check:
                values = tree.item(item, 'values')
                if any(str(value).strip() == "" for value in values):
                    pending_count += 1
            self.tree1_pending_label.config(text=str(pending_count))
        
    def _get_distributors(self) -> List[str]:
        """Get list of distributors from tree2."""
        tree = self.tree_managers['tree2'].tree
        return [tree.item(row, "values")[0] for row in tree.get_children()]
        
    def _get_customers(self) -> List[str]:
        """Get sorted list of unique customers from tree3."""
        customers = set()
        for row in self.all_tree3_items:
            if row and row[0].strip():
                customers.add(row[0])
        return sorted(customers)
        
    def _edit_tree_cell(self, event, tree_name):
        """Generic handler for cell editing across all trees."""
        tree = self.tree_managers[tree_name].tree
        region = tree.identify("region", event.x, event.y)
        if region != "cell":
            return
            
        rowid = tree.identify_row(event.y)
        column = tree.identify_column(event.x)
        
        # Ensure we have a valid row and column
        if not rowid or not column:
            return
            
        col_index = int(column.replace("#", "")) - 1
        
        # Clear any existing selection to avoid conflicts
        tree.selection_remove(tree.selection())
        
        self._create_cell_editor(tree, rowid, col_index, tree_name)
        
    def _edit_tree1_cell(self, event):
        """Handle cell editing for tree1."""
        self._edit_tree_cell(event, 'tree1')
        
    def _edit_tree3_cell(self, event):
        """Handle cell editing for tree3."""
        self._edit_tree_cell(event, 'tree3')
        
    def _edit_tree4_cell(self, event):
        """Handle cell editing for tree4."""
        self._edit_tree_cell(event, 'tree4')
        
    def _create_cell_editor(self, tree, rowid, col_index, tree_name):
        """Create an inline cell editor."""
        try:
            x, y, width, height = tree.bbox(rowid, f"#{col_index + 1}")
        except ValueError:
            return  # Row not visible
            
        # Use position-based column reference instead of column name
        value = tree.set(rowid, f"#{col_index + 1}")
        
        # Create appropriate entry widget
        entry = self._create_entry_widget(tree, col_index, tree_name)
        
        # Place and setup the entry widget
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, value)
        entry.focus()
        
        # Setup save callback
        def save_and_cleanup(new_value=None, move_to_next=False):
            self._save_cell_edit(entry, tree, rowid, col_index, tree_name, new_value, move_to_next)
        
        # Bind events
        self._bind_entry_events(entry, tree_name, save_and_cleanup)
    
    def _create_entry_widget(self, tree, col_index, tree_name):
        """Create the appropriate entry widget based on tree and column."""
        if tree_name == 'tree1':
            # Column 1 (index 0) - Customer column with autocomplete from tree3
            if col_index == 0:
                autocomplete_list = self._get_customers()
                entry = AutocompleteEntryInline(autocomplete_list, tree, font=self.main_font)
                entry.after_selection_callback = lambda move_right=False: entry._save_callback(move_to_next=move_right)
                return entry
            # Column 4 (index 3) - Distributor column with autocomplete from tree2
            elif col_index == 3:
                autocomplete_list = self._get_distributors()
                entry = AutocompleteEntryInline(autocomplete_list, tree, font=self.main_font)
                entry.after_selection_callback = lambda move_right=False: entry._save_callback(move_to_next=move_right)
                return entry
        
        # Default: regular text entry for all other cases
        return tk.Entry(tree, font=self.main_font)
    
    def _bind_entry_events(self, entry, tree_name, save_callback):
        """Bind events to the entry widget."""
        if tree_name == 'tree1':
            entry.bind("<Return>", lambda e: save_callback(move_to_next=True))
        else:
            entry.bind("<Return>", lambda e: save_callback())
        entry.bind("<Escape>", lambda e: entry.destroy())
        entry.bind("<FocusOut>", lambda e: save_callback())
        
        # Store the save callback for autocomplete widgets
        if hasattr(entry, 'after_selection_callback'):
            entry._save_callback = save_callback
    
    def _save_cell_edit(self, entry, tree, rowid, col_index, tree_name, new_value=None, move_to_next=False):
        """Save the cell edit and handle post-edit operations."""
        # Save state for undo before making changes
        self._save_state_for_undo()
        
        if new_value is None:
            new_value = entry.get()
        entry.destroy()
        
        # Use position-based column reference instead of column name
        tree.set(rowid, f"#{col_index + 1}", new_value)
        
        # Handle tree-specific updates
        if tree_name == 'tree1':
            self._update_sumif()
            self._ensure_one_empty_row_tree1()
            self._update_box1_linecount()
        elif tree_name == 'tree3':
            self._update_tree3_data_from_display()
            
        self._autosave()
        self._redraw_gridlines()
        
        # Move to next cell if requested (only for tree1)
        if move_to_next and tree_name == 'tree1':
            self._move_to_next_cell(tree, rowid, col_index, tree_name)
    
    def _move_to_next_cell(self, tree, rowid, col_index, tree_name):
        """Move to the next cell for editing."""
        columns = self.tree_managers[tree_name].columns
        next_col = (col_index + 1) % len(columns)
        
        if next_col == 0:  # If we've wrapped around, move to next row
            next_row = tree.next(rowid)
            if next_row:
                self._create_cell_editor(tree, next_row, next_col, tree_name)
            else:
                # If no next row, create one and move to it
                empty_values = tuple("" for _ in range(len(columns)))
                tree.insert("", "end", values=empty_values)
                children = tree.get_children()
                if children:
                    self._create_cell_editor(tree, children[-1], next_col, tree_name)
        else:
            # Move to next column in same row
            self._create_cell_editor(tree, rowid, next_col, tree_name)
        
    def _update_tree3_data_from_display(self):
        """Update tree3 data list from display."""
        tree = self.tree_managers['tree3'].tree
        self.all_tree3_items.clear()
        for row in tree.get_children():
            values = list(tree.item(row, "values"))
            self.all_tree3_items.append(values)
            
    def _update_tree3_display(self, *args):
        """Update tree3 display based on search term."""
        search_term = self.search_var.get().lower()
        tree = self.tree_managers['tree3'].tree
        
        tree.delete(*tree.get_children())
        filtered_items = []
        
        for item in sorted(self.all_tree3_items, key=lambda x: x[0].lower() if x and x[0] else ""):
            if any(search_term in str(field).lower() for field in item):
                filtered_items.append(item)
                
        for item in filtered_items:
            tree.insert("", "end", values=item)
            
        self.tree_managers['tree3'].apply_gridlines()
        
    def _delete_selected_tree1(self):
        """Delete selected rows from tree1."""
        tree = self.tree_managers['tree1'].tree
        all_rows = tree.get_children()
        selected = tree.selection()
        
        if not selected:
            return
        
        # Save state for undo
        self._save_state_for_undo()
            
        # Prevent deleting all rows - always keep at least one empty row
        if len(selected) >= len(all_rows):
            selected = selected[:len(all_rows) - 1] if len(all_rows) > 1 else []
            
        if len(all_rows) - len(selected) < 1:
            return
            
        # Delete selected items
        for item in selected:
            try:
                tree.delete(item)
            except tk.TclError:
                pass  # Item may have already been deleted
        
        self._update_sumif()
        self._ensure_one_empty_row_tree1()
        self._update_box1_linecount()
        self._autosave()
        self._redraw_gridlines()
        
    def _delete_selected_tree1_key(self, event=None):
        """Delete selected rows from tree1 using Delete key."""
        self._delete_selected_tree1()
        
    def _clear_tree1(self):
        """Clear all data from tree1 except last row."""
        # Save state for undo
        self._save_state_for_undo()
        
        tree = self.tree_managers['tree1'].tree
        all_rows = tree.get_children()
        
        for i, item in enumerate(all_rows):
            if i == len(all_rows) - 1:
                tree.item(item, values=("", "", "", ""))
            else:
                tree.delete(item)
                
        self._update_sumif()
        self._ensure_one_empty_row_tree1()
        self._update_box1_linecount()
        self._autosave()
        self._redraw_gridlines()
        
    def _add_tree1_row(self):
        """Add a new empty row to tree1."""
        # Save state for undo
        self._save_state_for_undo()
        
        tree = self.tree_managers['tree1'].tree
        num_columns = len(self.tree_managers['tree1'].columns)
        empty_values = tuple("" for _ in range(num_columns))
        tree.insert("", "end", values=empty_values)
        
        self._redraw_gridlines()
        self._autosave()
        
    def _remove_tree1_row(self):
        """Remove the last row from tree1 (unless it's the only row)."""
        # Save state for undo
        self._save_state_for_undo()
        
        tree = self.tree_managers['tree1'].tree
        all_rows = tree.get_children()
        
        # Don't remove if there's only one row or no rows
        if len(all_rows) <= 1:
            return
            
        # Remove the last row
        last_row = all_rows[-1]
        tree.delete(last_row)
        
        self._update_sumif()
        self._ensure_one_empty_row_tree1()
        self._update_box1_linecount()
        self._autosave()
        self._redraw_gridlines()
        
    def _show_add_column_popup(self):
        """Show popup to choose which box to add columns to."""
        popup = AddColumnPopup(self.root, self, relative_widget=self.add_column_btn)
        popup.show()
        
    def _show_remove_column_popup(self):
        """Show popup to choose which box to remove columns from."""
        popup = RemoveColumnPopup(self.root, self, relative_widget=self.remove_column_btn)
        popup.show()
        
    def _add_column_to_tree(self, tree_name, column_name):
        """Add a new column to the specified tree."""
        # Save state for undo
        self._save_state_for_undo()
        
        tree_manager = self.tree_managers[tree_name]
        tree = tree_manager.tree
        
        # Add to columns list
        tree_manager.columns.append(column_name)
        
        # Reconfigure all columns from scratch
        new_cols = [f"#{i+1}" for i in range(len(tree_manager.columns))]
        tree.configure(columns=new_cols)
        
        # Reset all column headers (including existing ones)
        for i, col_name in enumerate(tree_manager.columns):
            col_id = f"#{i+1}"
            tree.heading(col_id, text=col_name)
            
            # Get saved alignment or default to center
            saved_alignment = tree_manager.column_alignments.get(i, "center")
            tree.column(col_id, anchor=saved_alignment, width=100, minwidth=50)
        
        # Apply special styling for tree2 if needed
        if tree_name == "tree2":
            tree.configure(style="Tree2.Treeview")
        
        # Add empty values to existing rows for the new column
        for row in tree.get_children():
            current_values = list(tree.item(row, "values"))
            current_values.append("")  # Add empty value for new column
            tree.item(row, values=current_values)
            
        self._redraw_gridlines()
        self._autosave()
        
    def _remove_column_from_tree(self, tree_name, column_index):
        """Remove a column from the specified tree."""
        tree_manager = self.tree_managers[tree_name]
        tree = tree_manager.tree
        
        if len(tree_manager.columns) <= 1:
            messagebox.showwarning(
                "Προειδοποίηση",
                "Δεν μπορείτε να αφαιρέσετε την τελευταία στήλη!",
                parent=self.root
            )
            return
            
        # Save state for undo
        self._save_state_for_undo()
        
        # Remove from columns list
        tree_manager.columns.pop(column_index)
        
        # Update alignments - shift alignments for columns after the removed one
        new_alignments = {}
        for col_idx, alignment in tree_manager.column_alignments.items():
            if col_idx < column_index:
                # Keep alignments for columns before the removed one
                new_alignments[col_idx] = alignment
            elif col_idx > column_index:
                # Shift alignments for columns after the removed one
                new_alignments[col_idx - 1] = alignment
        tree_manager.column_alignments = new_alignments
        
        # Remove values from all rows for the deleted column
        for row in tree.get_children():
            current_values = list(tree.item(row, "values"))
            if column_index < len(current_values):
                current_values.pop(column_index)
                tree.item(row, values=current_values)
        
        # Reconfigure the treeview columns
        new_cols = [f"#{i+1}" for i in range(len(tree_manager.columns))]
        tree.configure(columns=new_cols)
        
        # Reset all column headers
        for i, col_name in enumerate(tree_manager.columns):
            col_id = f"#{i+1}"
            tree.heading(col_id, text=col_name)
            
            # Get saved alignment or default to center
            saved_alignment = tree_manager.column_alignments.get(i, "center")
            tree.column(col_id, anchor=saved_alignment, width=100, minwidth=50)
        
        # Apply special styling for tree2 if needed
        if tree_name == "tree2":
            tree.configure(style="Tree2.Treeview")
            
        self._redraw_gridlines()
        self._autosave()
        
    def _delete_selected_tree3(self, event=None):
        """Delete selected rows from tree3."""
        tree = self.tree_managers['tree3'].tree
        selected = tree.selection()
        
        if not selected:
            return
        
        # Save state for undo
        self._save_state_for_undo()
        
        for item in selected:
            try:
                values = list(tree.item(item, "values"))
                if values in self.all_tree3_items:
                    self.all_tree3_items.remove(values)
            except Exception:
                pass  # Item may have already been processed
                
        self._update_tree3_display()
        self._autosave()
        
    def _add_distributor(self):
        """Show add distributor popup."""
        popup = DistributorPopup(
            self.root, 
            self.tree_managers['tree2'], 
            self._autosave,
            relative_widget=self.add_distributor_btn
        )
        popup.show()
        
    def _delete_selected_tree2(self, event=None):
        """Delete selected distributors using Delete key."""
        tree = self.tree_managers['tree2'].tree
        selected = tree.selection()
        
        if not selected:
            return
            
        # Save state for undo
        self._save_state_for_undo()
        
        # Delete selected distributors
        for item in selected:
            tree.delete(item)
            
        self._redraw_gridlines()
        self._autosave()
        
    def _add_row_tree3(self):
        """Show add row popup for tree3."""
        popup = AddRowPopup(
            self.root, 
            self.tree_managers['tree3'].columns,
            self._on_tree3_row_added,
            relative_widget=self.add_row_btn3
        )
        popup.show()
        
    def _on_tree3_row_added(self, values):
        """Handle new row added to tree3."""
        self.all_tree3_items.append(values)
        self._update_tree3_display()
        self._autosave()
        
    def _toggle_tree2_4(self):
        """Toggle visibility of tree2_4_frame and its shadow frame."""
        if self.shadow_frame2.winfo_ismapped():
            # Hide the entire shadow frame (which contains tree2_4_frame)
            self.shadow_frame2.pack_forget()
            self.x_btn.config(bg="#e94f4f", text="X")
            
            # Make box1 and box3 expand evenly to fill the space
            self.shadow_frame1.pack_configure(expand=True)
            self.shadow_frame3_super.pack_configure(expand=True)
        else:
            # First, reset box1 and box3 to fixed width
            self.shadow_frame1.pack_configure(expand=False)
            self.shadow_frame3_super.pack_configure(expand=False)
            
            # Show the shadow frame in its original position with fixed width
            # Pack it before the tree3 shadow frame
            self.shadow_frame2.pack(side="left", fill="both", expand=False, padx=8, pady=8, before=self.shadow_frame3_super)
            self.shadow_frame2.pack_propagate(False)  # Maintain fixed width
            self.x_btn.config(bg="#2c3e50", text="X")
            
    def _print_data(self):
        """Print data from trees 1, 2, 3, and 4."""
        tree1_data = self.tree_managers['tree1'].get_data()
        tree2_data = self.tree_managers['tree2'].get_data()
        tree3_data = self.tree_managers['tree3'].get_data()
        tree4_data = self.tree_managers['tree4'].get_data()
        
        PrintManager.print_data(tree1_data, tree2_data, tree3_data, tree4_data, self.root)
        
    def _save_state_for_undo(self):
        """Save current state for undo functionality."""
        current_state = {
            'tree1': self.tree_managers['tree1'].get_data(),
            'tree2': self.tree_managers['tree2'].get_data(),
            'tree3': self.all_tree3_items.copy(),
            'tree4': self.tree_managers['tree4'].get_data(),
        }
        
        # Add to undo stack
        self.undo_stack.append(current_state)
        
        # Limit undo stack size
        if len(self.undo_stack) > self.max_undo_steps:
            self.undo_stack.pop(0)
            
        # Clear redo stack when new action is performed
        self.redo_stack.clear()
        
    def _undo_action(self):
        """Undo the last action."""
        if not self.undo_stack:
            return
            
        # Save current state to redo stack
        current_state = {
            'tree1': self.tree_managers['tree1'].get_data(),
            'tree2': self.tree_managers['tree2'].get_data(),
            'tree3': self.all_tree3_items.copy(),
            'tree4': self.tree_managers['tree4'].get_data(),
        }
        self.redo_stack.append(current_state)
        
        # Restore previous state
        previous_state = self.undo_stack.pop()
        self._restore_state(previous_state)
        
    def _redo_action(self):
        """Redo the last undone action."""
        if not self.redo_stack:
            return
            
        # Save current state to undo stack
        current_state = {
            'tree1': self.tree_managers['tree1'].get_data(),
            'tree2': self.tree_managers['tree2'].get_data(),
            'tree3': self.all_tree3_items.copy(),
            'tree4': self.tree_managers['tree4'].get_data(),
        }
        self.undo_stack.append(current_state)
        
        # Restore redo state
        redo_state = self.redo_stack.pop()
        self._restore_state(redo_state)
        
    def _restore_state(self, state):
        """Restore application state."""
        # Restore tree1
        self.tree_managers['tree1'].set_data(state['tree1'])
        
        # Restore tree2
        self.tree_managers['tree2'].set_data(state['tree2'])
        
        # Restore tree3
        self.all_tree3_items = state['tree3'].copy()
        self._update_tree3_display()
        
        # Restore tree4
        self.tree_managers['tree4'].set_data(state['tree4'])
        
        # Update all related displays
        self._update_sumif()
        self._update_box1_linecount()
        self._redraw_gridlines()
        
    def _autosave(self):
        """Auto-save all data with retry mechanism."""
        data = {
            'tree1': self.tree_managers['tree1'].get_data(),
            'tree2': self.tree_managers['tree2'].get_data(),
            'tree3': self.all_tree3_items,
            'tree4': self.tree_managers['tree4'].get_data(),
            'columns1': self.tree_managers['tree1'].columns,
            'columns2': self.tree_managers['tree2'].columns,
            'columns3': self.tree_managers['tree3'].columns,
            'columns4': self.tree_managers['tree4'].columns,
        }
        
        # Retry saving up to 3 times with delays
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if DataManager.save_data(data):
                    # Update saved notification (already visible between buttons)
                    if hasattr(self, 'saved_notification_label'):
                        self.saved_notification_label.config(text="SAVED", fg="#00ff00")
                        self.root.after(2000, lambda: self._reset_saved_notification())
                    break
                else:
                    if attempt < max_retries - 1:
                        # Wait a bit before retrying
                        self.root.after(100 * (attempt + 1), lambda: None)
                    else:
                        # Show error notification next to X button
                        if hasattr(self, 'saved_notification_label'):
                            self.saved_notification_label.config(
                                text="SAVE ERROR", 
                                bg="#660000",  # Dark red background 
                                fg="#ff6666"   # Light red text
                            )
                            self.saved_notification_label.pack(side="left", pady=3, padx=(3, 0))  # Show next to X button
                            self.root.after(3000, lambda: self._reset_saved_notification())
            except Exception as e:
                print(f"Autosave attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    if hasattr(self, 'saved_notification_label'):
                        self.saved_notification_label.config(
                            text="SAVE ERROR", 
                            bg="#660000",  # Dark red background
                            fg="#ff6666"   # Light red text
                        )
                        self.saved_notification_label.pack(side="left", pady=3, padx=(3, 0))  # Show next to X button
                        self.root.after(3000, lambda: self._reset_saved_notification())
                        
        # Also save column widths and alignments
        self._autosave_column_widths()
        self._autosave_column_alignments()
            
    def _load_data(self):
        """Load all data from file."""
        data = DataManager.load_data()
        
        if not data:
            self._ensure_one_empty_row_tree1()
            self._update_box1_linecount()
            return
            
        # Restore column names
        for tree_name in ['tree1', 'tree2', 'tree3', 'tree4']:
            if f'columns{tree_name[-1]}' in data:
                columns = data[f'columns{tree_name[-1]}']
                tree_manager = self.tree_managers[tree_name]
                tree = tree_manager.tree
                
                # Update columns list
                tree_manager.columns = columns.copy()
                
                # Reconfigure treeview with correct number of columns
                new_cols = [f"#{i+1}" for i in range(len(columns))]
                tree.configure(columns=new_cols)
                
                # Reset all column headers
                for idx, col_name in enumerate(columns):
                    col_id = f"#{idx + 1}"
                    tree.heading(col_id, text=col_name)
                    
                    # Get saved alignment or default to center
                    saved_alignment = tree_manager.column_alignments.get(idx, "center")
                    tree.column(col_id, anchor=saved_alignment, width=86, minwidth=50)
                
                # Apply special styling for tree2 if needed
                if tree_name == "tree2":
                    tree.configure(style="Tree2.Treeview")
                    
        # Restore data
        if 'tree1' in data:
            self.tree_managers['tree1'].set_data(data['tree1'])
            
        if 'tree2' in data:
            self.tree_managers['tree2'].set_data(data['tree2'])
            
        if 'tree3' in data:
            self.all_tree3_items = data['tree3']
            self._update_tree3_display()
            
        if 'tree4' in data:
            self.tree_managers['tree4'].set_data(data['tree4'])
            
        self._ensure_one_empty_row_tree1()
        self._update_sumif()
        self._update_box1_linecount()
        
    def _autosave_column_widths(self):
        """Auto-save column widths for all trees."""
        tree_widths = {}
        for tree_name, tree_manager in self.tree_managers.items():
            tree_widths[tree_name] = tree_manager.get_column_widths()
        DataManager.save_column_widths(tree_widths)
        
    def _autosave_column_alignments(self):
        """Auto-save column alignments for all trees."""
        tree_alignments = {}
        for tree_name, tree_manager in self.tree_managers.items():
            tree_alignments[tree_name] = tree_manager.column_alignments.copy()
        DataManager.save_column_alignments(tree_alignments)
        
    def _hide_saved_notification(self):
        """Hide the saved notification label (legacy method - now just resets)."""
        self._reset_saved_notification()
        
    def _reset_saved_notification(self):
        """Reset the saved notification label to invisible state."""
        if hasattr(self, 'saved_notification_label'):
            # Reset to invisible state (black text on black background)
            self.saved_notification_label.config(
                text="",
                bg="#000000",  # Black background
                fg="#000000"   # Black text (invisible)
            )
        
    def _load_column_widths(self):
        """Load column widths for all trees."""
        tree_widths = DataManager.load_column_widths()
        
        # Set default widths for trees that don't have saved widths
        default_widths = {
            'tree3': {"Πελάτης": 250, "Ποσότητα": 80, "Τιμή": 120, "Διανομέας": 180},
            'tree4': {"ΕΣΟΔΑ": 100, "ΕΞΟΔΑ": 100}
        }
        
        for tree_name, tree_manager in self.tree_managers.items():
            if tree_name in tree_widths:
                # Use saved widths
                tree_manager.set_column_widths(tree_widths[tree_name])
            elif tree_name in default_widths:
                # Use default widths for specific trees
                tree_manager.set_column_widths(default_widths[tree_name])
        
    def _load_column_alignments(self):
        """Load column alignments for all trees."""
        tree_alignments = DataManager.load_column_alignments()
        
        for tree_name, tree_manager in self.tree_managers.items():
            if tree_name in tree_alignments:
                # Apply saved alignments
                alignments = tree_alignments[tree_name]
                tree_manager.column_alignments = alignments.copy()
                
                # Apply the alignments to the actual tree columns
                for col_index, alignment in alignments.items():
                    col_id = f"#{col_index + 1}"
                    try:
                        tree_manager.tree.column(col_id, anchor=alignment)
                    except tk.TclError:
                        # Column might not exist yet, skip
                        pass
        
    def run(self):
        """Run the application."""
        try:
            self.root.mainloop()
        finally:
            # Stop drive monitoring when application closes
            self.drive_monitor_active = False
            
    def _on_closing(self):
        """Handle application closing."""
        # Save column widths and alignments before closing
        self._autosave_column_widths()
        self._autosave_column_alignments()

        # Stop drive monitoring
        self.drive_monitor_active = False

        # Stop any blinking animations
        for tree_manager in self.tree_managers.values():
            if hasattr(tree_manager, 'blink_job') and tree_manager.blink_job:
                self.root.after_cancel(tree_manager.blink_job)
                tree_manager.blink_job = None

        self.root.destroy()


def main():
    """Main entry point."""
    app = BusinessApp()
    app.run()


if __name__ == "__main__":
    main()
