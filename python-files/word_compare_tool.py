#!/usr/bin/env python3
"""
Word Document Comparison Tool - CustomTkinter Version
A GUI application for comparing Word documents with batch processing and track changes reporting.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import List, Tuple, Optional
import traceback
import tempfile
import shutil
import time
from datetime import datetime, timedelta

import customtkinter as ctk
from python_redlines.engines import XmlPowerToolsEngine

# Set CustomTkinter appearance
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class WordCompareApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Word Document Comparison Tool")
        self.root.geometry("900x700")
        
        # Variables
        self.original_path = tk.StringVar()
        self.revised_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.prefix = tk.StringVar(value="comparison_")
        self.track_changes = tk.BooleanVar(value=True)
        self.open_folder = tk.BooleanVar(value=True)
        
        self.comparison_pairs = []
        
        # Timing variables
        self.start_time = None
        self.total_processing_time = 0
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create the main GUI widgets"""
        
        # Main title
        title_label = ctk.CTkLabel(
            self.root, 
            text="Word Document Comparison Tool", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # File selection frame
        file_frame = ctk.CTkFrame(self.root)
        file_frame.pack(fill="x", padx=20, pady=10)
        
        # Original document
        ctk.CTkLabel(file_frame, text="Original Document:", font=ctk.CTkFont(size=14)).grid(
            row=0, column=0, sticky="w", padx=10, pady=10
        )
        self.original_entry = ctk.CTkEntry(file_frame, textvariable=self.original_path, width=400)
        self.original_entry.grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkButton(
            file_frame, 
            text="Browse", 
            command=self.browse_original,
            width=100
        ).grid(row=0, column=2, padx=10, pady=10)
        
        # Revised document
        ctk.CTkLabel(file_frame, text="Revised Document:", font=ctk.CTkFont(size=14)).grid(
            row=1, column=0, sticky="w", padx=10, pady=10
        )
        self.revised_entry = ctk.CTkEntry(file_frame, textvariable=self.revised_path, width=400)
        self.revised_entry.grid(row=1, column=1, padx=10, pady=10)
        ctk.CTkButton(
            file_frame, 
            text="Browse", 
            command=self.browse_revised,
            width=100
        ).grid(row=1, column=2, padx=10, pady=10)
        
        # Output directory
        ctk.CTkLabel(file_frame, text="Output Directory:", font=ctk.CTkFont(size=14)).grid(
            row=2, column=0, sticky="w", padx=10, pady=10
        )
        self.output_entry = ctk.CTkEntry(file_frame, textvariable=self.output_path, width=400)
        self.output_entry.grid(row=2, column=1, padx=10, pady=10)
        ctk.CTkButton(
            file_frame, 
            text="Browse", 
            command=self.browse_output,
            width=100
        ).grid(row=2, column=2, padx=10, pady=10)
        
        # Action buttons frame
        action_frame = ctk.CTkFrame(self.root)
        action_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            action_frame, 
            text="Add to Batch", 
            command=self.add_to_batch,
            width=120
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            action_frame, 
            text="Compare Single", 
            command=self.compare_single,
            width=120
        ).pack(side="left", padx=10, pady=10)
        
        # Batch processing frame
        batch_frame = ctk.CTkFrame(self.root)
        batch_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            batch_frame, 
            text="Batch Processing Queue:", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # Batch list
        self.batch_listbox = tk.Listbox(
            batch_frame, 
            height=8,
            bg="#2b2b2b",
            fg="white",
            selectbackground="#1f538d"
        )
        self.batch_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Batch control buttons
        batch_control_frame = ctk.CTkFrame(batch_frame)
        batch_control_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            batch_control_frame, 
            text="Remove Selected", 
            command=self.remove_from_batch,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            batch_control_frame, 
            text="Clear All", 
            command=self.clear_batch,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            batch_control_frame, 
            text="Process Batch", 
            command=self.process_batch,
            width=120
        ).pack(side="left", padx=5)
        
        # Options frame
        options_frame = ctk.CTkFrame(self.root)
        options_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            options_frame, 
            text="Options:", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=5)
        
        options_inner_frame = ctk.CTkFrame(options_frame)
        options_inner_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkCheckBox(
            options_inner_frame, 
            text="Enable Track Changes Mode", 
            variable=self.track_changes
        ).pack(side="left", padx=10, pady=5)
        
        ctk.CTkCheckBox(
            options_inner_frame, 
            text="Open Output Folder After Completion", 
            variable=self.open_folder
        ).pack(side="left", padx=10, pady=5)
        
        prefix_frame = ctk.CTkFrame(options_frame)
        prefix_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(prefix_frame, text="Output File Prefix:").pack(side="left", padx=10, pady=5)
        ctk.CTkEntry(prefix_frame, textvariable=self.prefix, width=200).pack(side="left", padx=10, pady=5)
        
        # Progress frame
        progress_frame = ctk.CTkFrame(self.root)
        progress_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            progress_frame, 
            text="Progress:", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame, width=400)
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(progress_frame, text="Status: Ready")
        self.status_label.pack(pady=5)
        
        # Timing label
        self.timing_label = ctk.CTkLabel(progress_frame, text="")
        self.timing_label.pack(pady=2)
        
        # Log frame
        log_frame = ctk.CTkFrame(self.root)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            log_frame, 
            text="Log:", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=5)
        
        self.log_text = tk.Text(
            log_frame, 
            height=6,
            bg="#2b2b2b",
            fg="white",
            wrap=tk.WORD
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Control buttons
        control_frame = ctk.CTkFrame(self.root)
        control_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            control_frame, 
            text="About", 
            command=self.show_about,
            width=100
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            control_frame, 
            text="Exit", 
            command=self.root.quit,
            width=100
        ).pack(side="right", padx=10, pady=10)
        
        # Initial log message
        self.log_message("Word Document Comparison Tool started.")
        self.log_message("Select documents to compare or add them to batch processing queue.")
    
    def browse_original(self):
        """Browse for original document"""
        filename = filedialog.askopenfilename(
            title="Select Original Document",
            filetypes=[("Word Documents", "*.docx"), ("All Files", "*.*")]
        )
        if filename:
            self.original_path.set(filename)
    
    def browse_revised(self):
        """Browse for revised document"""
        filename = filedialog.askopenfilename(
            title="Select Revised Document",
            filetypes=[("Word Documents", "*.docx"), ("All Files", "*.*")]
        )
        if filename:
            self.revised_path.set(filename)
    
    def browse_output(self):
        """Browse for output directory"""
        dirname = filedialog.askdirectory(title="Select Output Directory")
        if dirname:
            self.output_path.set(dirname)
    
    def log_message(self, message: str):
        """Add a message to the log"""
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_status(self, status: str):
        """Update the status label"""
        self.status_label.configure(text=f'Status: {status}')
        self.root.update_idletasks()
    
    def update_timing(self, message: str):
        """Update the timing label"""
        self.timing_label.configure(text=message)
        self.root.update_idletasks()
    
    def format_time(self, seconds: float) -> str:
        """Format seconds into a readable time string"""
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.1f}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            remaining_seconds = seconds % 60
            return f"{hours}h {minutes}m {remaining_seconds:.1f}s"
    
    def update_progress(self, value: float):
        """Update the progress bar (value between 0 and 1)"""
        self.progress_bar.set(value)
        self.root.update_idletasks()
    
    def validate_files(self, original_path: str, revised_path: str) -> bool:
        """Validate that the selected files exist and are .docx files"""
        if not original_path or not revised_path:
            messagebox.showerror('Error', 'Please select both original and revised documents.')
            return False
        
        # Convert to absolute paths
        original_path = os.path.abspath(original_path)
        revised_path = os.path.abspath(revised_path)
        
        if not os.path.exists(original_path):
            messagebox.showerror('Error', f'Original document not found: {original_path}')
            return False
        
        if not os.path.exists(revised_path):
            messagebox.showerror('Error', f'Revised document not found: {revised_path}')
            return False
        
        if not original_path.lower().endswith('.docx'):
            messagebox.showerror('Error', 'Original document must be a .docx file.')
            return False
        
        if not revised_path.lower().endswith('.docx'):
            messagebox.showerror('Error', 'Revised document must be a .docx file.')
            return False
        
        return True
    
    def compare_documents(self, original_path: str, revised_path: str, output_path: str) -> bool:
        """Compare two Word documents and create a redlined version"""
        temp_dir = None
        comparison_start_time = time.time()
        
        try:
            # Convert to absolute paths
            original_path = os.path.abspath(original_path)
            revised_path = os.path.abspath(revised_path)
            output_path = os.path.abspath(output_path)
            
            self.log_message(f'Comparing: {os.path.basename(original_path)} vs {os.path.basename(revised_path)}')
            self.log_message(f'Started at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            self.log_message(f'Original path: {original_path}')
            self.log_message(f'Revised path: {revised_path}')
            self.log_message(f'Output path: {output_path}')
            
            # Create temporary directory for processing
            temp_dir = tempfile.mkdtemp()
            self.log_message(f'Using temp directory: {temp_dir}')
            
            # Copy files to temp directory with simple names
            copy_start_time = time.time()
            temp_original = os.path.join(temp_dir, 'original.docx')
            temp_revised = os.path.join(temp_dir, 'revised.docx')
            temp_output = os.path.join(temp_dir, 'output.docx')
            
            shutil.copy2(original_path, temp_original)
            shutil.copy2(revised_path, temp_revised)
            copy_time = time.time() - copy_start_time
            
            self.log_message(f'File copy completed in {self.format_time(copy_time)}')
            
            # Verify temp files exist
            if not os.path.exists(temp_original):
                raise FileNotFoundError(f'Failed to create temp original file: {temp_original}')
            if not os.path.exists(temp_revised):
                raise FileNotFoundError(f'Failed to create temp revised file: {temp_revised}')
            
            # Use python-redlines XmlPowerToolsEngine to compare documents
            engine_start_time = time.time()
            wrapper = XmlPowerToolsEngine()
            
            # Change to temp directory for processing
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Run the redline comparison with temp files
                self.log_message('Running document comparison engine...')
                result = wrapper.run_redline('DocumentComparer', temp_original, temp_revised)
                engine_time = time.time() - engine_start_time
                self.log_message(f'Comparison engine completed in {self.format_time(engine_time)}')
                
                # Change back to original directory
                os.chdir(original_cwd)
                
                # The result is a tuple with bytes at element 0
                if result and len(result) > 0:
                    # Write result to temp output first
                    output_start_time = time.time()
                    with open(temp_output, 'wb') as f:
                        f.write(result[0])
                    
                    # Copy from temp to final output location
                    shutil.copy2(temp_output, output_path)
                    output_time = time.time() - output_start_time
                    
                    total_time = time.time() - comparison_start_time
                    
                    if os.path.exists(output_path):
                        self.log_message(f'Output file created in {self.format_time(output_time)}')
                        self.log_message(f'Total comparison time: {self.format_time(total_time)}')
                        self.log_message(f'Comparison completed: {output_path}')
                        return True
                    else:
                        self.log_message(f'Error: Output file was not created: {output_path}')
                        return False
                else:
                    self.log_message('Error: No result returned from comparison engine')
                    return False
                    
            except Exception as e:
                # Make sure we change back to original directory
                os.chdir(original_cwd)
                raise e
                
        except Exception as e:
            total_time = time.time() - comparison_start_time
            error_msg = f'Error comparing documents: {str(e)}'
            self.log_message(error_msg)
            self.log_message(f'Failed after {self.format_time(total_time)}')
            self.log_message(f'Exception type: {type(e).__name__}')
            self.log_message(f'Traceback: {traceback.format_exc()}')
            messagebox.showerror('Error', error_msg)
            return False
        finally:
            # Clean up temp directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    self.log_message(f'Warning: Could not clean up temp directory: {str(e)}')
    
    def add_to_batch(self):
        """Add a comparison pair to the batch queue"""
        original = self.original_path.get()
        revised = self.revised_path.get()
        
        if self.validate_files(original, revised):
            pair = (original, revised)
            if pair not in self.comparison_pairs:
                self.comparison_pairs.append(pair)
                display_text = f'{os.path.basename(original)} vs {os.path.basename(revised)}'
                self.batch_listbox.insert(tk.END, display_text)
                self.log_message(f'Added to batch: {display_text}')
            else:
                messagebox.showinfo('Info', 'This comparison pair is already in the batch queue.')
    
    def remove_from_batch(self):
        """Remove selected items from the batch queue"""
        selected_indices = self.batch_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo('Info', 'Please select an item to remove.')
            return
        
        # Remove in reverse order to maintain indices
        for index in reversed(selected_indices):
            if 0 <= index < len(self.comparison_pairs):
                removed_pair = self.comparison_pairs.pop(index)
                self.batch_listbox.delete(index)
                self.log_message(f'Removed from batch: {os.path.basename(removed_pair[0])} vs {os.path.basename(removed_pair[1])}')
    
    def clear_batch(self):
        """Clear all items from the batch queue"""
        self.comparison_pairs.clear()
        self.batch_listbox.delete(0, tk.END)
        self.log_message('Batch queue cleared.')
    
    def process_batch(self):
        """Process all items in the batch queue"""
        if not self.comparison_pairs:
            messagebox.showinfo('Info', 'No items in batch queue.')
            return
        
        output_dir = self.output_path.get()
        if not output_dir:
            messagebox.showerror('Error', 'Please select an output directory.')
            return
        
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                messagebox.showerror('Error', f'Could not create output directory: {str(e)}')
                return
        
        # Run in separate thread to prevent GUI freezing
        thread = threading.Thread(target=self._process_batch_worker, args=(output_dir,), daemon=True)
        thread.start()
    
    def _process_batch_worker(self, output_dir: str):
        """Worker function for batch processing"""
        total_pairs = len(self.comparison_pairs)
        successful_comparisons = 0
        prefix = self.prefix.get()
        
        # Start timing
        batch_start_time = time.time()
        self.total_processing_time = 0
        
        self.update_status('Processing batch...')
        self.update_timing('Starting batch processing...')
        self.log_message(f'Starting batch processing of {total_pairs} document pairs')
        self.log_message(f'Batch started at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        
        for i, (original_path, revised_path) in enumerate(self.comparison_pairs):
            # Update progress
            progress = i / total_pairs
            self.update_progress(progress)
            
            # Update timing display
            if i > 0:
                elapsed_time = time.time() - batch_start_time
                avg_time_per_comparison = elapsed_time / i
                estimated_remaining = avg_time_per_comparison * (total_pairs - i)
                
                self.update_timing(
                    f'Processing {i+1}/{total_pairs} | '
                    f'Elapsed: {self.format_time(elapsed_time)} | '
                    f'ETA: {self.format_time(estimated_remaining)}'
                )
            else:
                self.update_timing(f'Processing {i+1}/{total_pairs}...')
            
            # Generate output filename
            original_name = Path(original_path).stem
            revised_name = Path(revised_path).stem
            output_filename = f'{prefix}{original_name}_vs_{revised_name}_comparison.docx'
            output_path = os.path.join(output_dir, output_filename)
            
            # Perform comparison
            comparison_start = time.time()
            if self.compare_documents(original_path, revised_path, output_path):
                successful_comparisons += 1
                comparison_time = time.time() - comparison_start
                self.total_processing_time += comparison_time
                self.log_message(f'✓ Comparison {i+1} completed in {self.format_time(comparison_time)}')
            else:
                comparison_time = time.time() - comparison_start
                self.total_processing_time += comparison_time
                self.log_message(f'✗ Comparison {i+1} failed after {self.format_time(comparison_time)}')
        
        # Final progress update
        self.update_progress(1.0)
        
        # Calculate final timing statistics
        total_batch_time = time.time() - batch_start_time
        avg_time_per_comparison = total_batch_time / total_pairs if total_pairs > 0 else 0
        
        # Summary message
        summary = f'Batch processing completed. {successful_comparisons}/{total_pairs} comparisons successful.'
        timing_summary = (
            f'Total batch time: {self.format_time(total_batch_time)} | '
            f'Average per comparison: {self.format_time(avg_time_per_comparison)}'
        )
        
        self.log_message('=' * 60)
        self.log_message('BATCH PROCESSING SUMMARY')
        self.log_message(f'Completed at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        self.log_message(f'Total comparisons: {total_pairs}')
        self.log_message(f'Successful: {successful_comparisons}')
        self.log_message(f'Failed: {total_pairs - successful_comparisons}')
        self.log_message(f'Total processing time: {self.format_time(total_batch_time)}')
        self.log_message(f'Average time per comparison: {self.format_time(avg_time_per_comparison)}')
        self.log_message('=' * 60)
        
        self.update_status('Batch processing completed')
        self.update_timing(timing_summary)
        
        # Show completion message
        detailed_summary = f'{summary}\n\n{timing_summary}'
        self.root.after(0, lambda: messagebox.showinfo('Batch Complete', detailed_summary))
        
        # Open output folder if requested
        if self.open_folder.get():
            self.open_output_folder(output_dir)
    
    def compare_single(self):
        """Compare a single pair of documents"""
        original = self.original_path.get()
        revised = self.revised_path.get()
        output_dir = self.output_path.get()
        
        if not self.validate_files(original, revised):
            return
        
        if not output_dir:
            messagebox.showerror('Error', 'Please select an output directory.')
            return
        
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                messagebox.showerror('Error', f'Could not create output directory: {str(e)}')
                return
        
        # Run in separate thread to prevent GUI freezing
        thread = threading.Thread(target=self._compare_single_worker, args=(original, revised, output_dir), daemon=True)
        thread.start()
    
    def _compare_single_worker(self, original_path: str, revised_path: str, output_dir: str):
        """Worker function for single comparison"""
        prefix = self.prefix.get()
        
        # Generate output filename
        original_name = Path(original_path).stem
        revised_name = Path(revised_path).stem
        output_filename = f'{prefix}{original_name}_vs_{revised_name}_comparison.docx'
        output_path = os.path.join(output_dir, output_filename)
        
        # Start timing
        single_start_time = time.time()
        
        self.update_status('Comparing documents...')
        self.update_timing('Starting comparison...')
        self.update_progress(0.1)
        
        # Show live timing updates
        def update_live_timing():
            elapsed = time.time() - single_start_time
            self.update_timing(f'Elapsed: {self.format_time(elapsed)}')
            if elapsed < 300:  # Stop after 5 minutes to avoid infinite updates
                self.root.after(1000, update_live_timing)
        
        # Start live timing updates
        self.root.after(1000, update_live_timing)
        
        self.update_progress(0.5)
        
        if self.compare_documents(original_path, revised_path, output_path):
            total_time = time.time() - single_start_time
            self.update_progress(1.0)
            self.update_status('Comparison completed')
            self.update_timing(f'Completed in {self.format_time(total_time)}')
            
            # Show completion message
            message = (
                f'Comparison completed successfully!\n'
                f'Processing time: {self.format_time(total_time)}\n'
                f'Output saved to: {output_path}'
            )
            self.root.after(0, lambda: messagebox.showinfo('Comparison Complete', message))
            
            # Open output folder if requested
            if self.open_folder.get():
                self.open_output_folder(output_dir)
        else:
            total_time = time.time() - single_start_time
            self.update_progress(0)
            self.update_status('Comparison failed')
            self.update_timing(f'Failed after {self.format_time(total_time)}')
    
    def open_output_folder(self, output_dir: str):
        """Open the output folder in file explorer"""
        try:
            if sys.platform == 'win32':
                os.startfile(output_dir)
            elif sys.platform == 'darwin':
                os.system(f'open "{output_dir}"')
            else:
                os.system(f'xdg-open "{output_dir}"')
        except Exception as e:
            self.log_message(f'Could not open output folder: {str(e)}')
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Word Document Comparison Tool v1.0

This application compares Word documents and generates 
a redlined version showing the differences with track changes.

Features:
• Single document comparison
• Batch processing
• Track changes mode
• Automatic output file naming

Built with:
• Python
• CustomTkinter
• Python-Redlines

Created for document comparison and analysis."""
        
        messagebox.showinfo('About Word Compare Tool', about_text)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        app = WordCompareApp()
        app.run()
    except Exception as e:
        messagebox.showerror('Application Error', f'Application error: {str(e)}\n\n{traceback.format_exc()}')

if __name__ == '__main__':
    main()