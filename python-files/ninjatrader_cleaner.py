#!/usr/bin/env python3
"""
NinjaTrader Performance Optimizer
A utility to clean NinjaTrader cache and database folders to improve performance.

This tool safely removes temporary files while preserving important data like
Message, Replay, and Snapshot folders.
"""

import os
import shutil
import tkinter as tk
from tkinter import messagebox, ttk
import logging
from pathlib import Path
from datetime import datetime
import sys
from typing import List, Tuple, Optional


class NinjaTraderCleaner:
    """Main class for NinjaTrader cleanup operations."""
    
    def __init__(self):
        self.ninjatrader_path = None
        self.log_file = None
        self.setup_logging()
        self.find_ninjatrader_folder()
    
    def setup_logging(self) -> None:
        """Set up logging configuration."""
        log_filename = f"ninjatrader_cleaner_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.log_file = log_filename
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        logging.info("NinjaTrader Cleaner started")
    
    def find_ninjatrader_folder(self) -> bool:
        """
        Locate the NinjaTrader folder in the user's Documents directory.
        
        Returns:
            bool: True if found, False otherwise
        """
        # Common paths where NinjaTrader might be installed
        possible_paths = [
            Path.home() / "Documents" / "NinjaTrader 8",
            Path.home() / "Documents" / "NinjaTrader",
            Path.home() / "My Documents" / "NinjaTrader 8",
            Path.home() / "My Documents" / "NinjaTrader",
        ]
        
        for path in possible_paths:
            if path.exists() and path.is_dir():
                self.ninjatrader_path = path
                logging.info(f"Found NinjaTrader folder at: {path}")
                return True
        
        # Try to find any NinjaTrader folder in Documents
        docs_path = Path.home() / "Documents"
        if docs_path.exists():
            for item in docs_path.iterdir():
                if item.is_dir() and "ninjatrader" in item.name.lower():
                    self.ninjatrader_path = item
                    logging.info(f"Found NinjaTrader folder at: {item}")
                    return True
        
        logging.error("NinjaTrader folder not found in Documents directory")
        return False
    
    def get_folders_to_clean(self) -> List[Tuple[Path, str]]:
        """
        Get list of folders that will be cleaned.
        
        Returns:
            List of tuples containing (folder_path, description)
        """
        if not self.ninjatrader_path:
            return []
        
        folders_to_clean = []
        
        # Main Cache folder
        cache_folder = self.ninjatrader_path / "Cache"
        if cache_folder.exists():
            folders_to_clean.append((cache_folder, "Main Cache folder"))
        
        # Database subfolders
        db_folder = self.ninjatrader_path / "db"
        if db_folder.exists():
            subfolders = ["Cache", "Day", "Minute", "Tick"]
            for subfolder in subfolders:
                subfolder_path = db_folder / subfolder
                if subfolder_path.exists():
                    folders_to_clean.append((subfolder_path, f"Database {subfolder} folder"))
        
        return folders_to_clean
    
    def get_protected_folders(self) -> List[str]:
        """
        Get list of folders that should NOT be cleaned.
        
        Returns:
            List of folder names that are protected
        """
        return ["Message", "Replay", "Snapshot"]
    
    def clean_folder(self, folder_path: Path) -> Tuple[bool, str, int]:
        """
        Clean a single folder by removing all its contents.
        
        Args:
            folder_path: Path to the folder to clean
            
        Returns:
            Tuple of (success, message, files_removed)
        """
        try:
            if not folder_path.exists():
                return False, f"Folder does not exist: {folder_path}", 0
            
            if not folder_path.is_dir():
                return False, f"Path is not a directory: {folder_path}", 0
            
            files_removed = 0
            errors = []
            
            # Count items before removal for logging
            items = list(folder_path.iterdir())
            total_items = len(items)
            
            for item in items:
                try:
                    if item.is_file():
                        item.unlink()
                        files_removed += 1
                    elif item.is_dir():
                        shutil.rmtree(item)
                        files_removed += 1
                except Exception as e:
                    errors.append(f"Failed to remove {item}: {str(e)}")
            
            if errors:
                error_msg = "; ".join(errors[:3])  # Show first 3 errors
                if len(errors) > 3:
                    error_msg += f" (and {len(errors) - 3} more errors)"
                return False, f"Partial success: {error_msg}", files_removed
            
            logging.info(f"Successfully cleaned {folder_path}: removed {files_removed} items")
            return True, f"Successfully removed {files_removed} items", files_removed
            
        except Exception as e:
            error_msg = f"Error cleaning {folder_path}: {str(e)}"
            logging.error(error_msg)
            return False, error_msg, 0
    
    def perform_cleanup(self, progress_callback=None) -> Tuple[bool, str, dict]:
        """
        Perform the complete cleanup operation.
        
        Args:
            progress_callback: Optional callback for progress updates
            
        Returns:
            Tuple of (success, message, detailed_results)
        """
        if not self.ninjatrader_path:
            return False, "NinjaTrader folder not found", {}
        
        folders_to_clean = self.get_folders_to_clean()
        if not folders_to_clean:
            return False, "No folders found to clean", {}
        
        results = {}
        total_files_removed = 0
        successful_cleanups = 0
        
        logging.info(f"Starting cleanup of {len(folders_to_clean)} folders")
        
        for i, (folder_path, description) in enumerate(folders_to_clean):
            if progress_callback:
                progress_callback(i + 1, len(folders_to_clean), f"Cleaning {description}...")
            
            success, message, files_removed = self.clean_folder(folder_path)
            results[description] = {
                'success': success,
                'message': message,
                'files_removed': files_removed,
                'path': str(folder_path)
            }
            
            if success:
                successful_cleanups += 1
                total_files_removed += files_removed
            
            logging.info(f"{description}: {message}")
        
        # Final summary
        if successful_cleanups == len(folders_to_clean):
            summary = f"✅ Cleanup completed successfully!\n\nRemoved {total_files_removed} files and folders from {successful_cleanups} locations."
            logging.info(f"Cleanup completed: {total_files_removed} items removed from {successful_cleanups} folders")
            return True, summary, results
        elif successful_cleanups > 0:
            summary = f"⚠️ Partial cleanup completed.\n\nSuccessfully cleaned {successful_cleanups} out of {len(folders_to_clean)} folders.\nRemoved {total_files_removed} files and folders."
            logging.warning(f"Partial cleanup: {successful_cleanups}/{len(folders_to_clean)} folders cleaned")
            return False, summary, results
        else:
            summary = f"❌ Cleanup failed.\n\nNo folders could be cleaned successfully."
            logging.error("Cleanup failed: no folders could be cleaned")
            return False, summary, results


class NinjaTraderCleanerGUI:
    """GUI interface for the NinjaTrader cleaner."""
    
    def __init__(self):
        self.cleaner = NinjaTraderCleaner()
        self.root = tk.Tk()
        self.setup_gui()
    
    def setup_gui(self) -> None:
        """Set up the GUI components."""
        self.root.title("NinjaTrader Performance Optimizer")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="NinjaTrader Performance Optimizer",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        status_frame.columnconfigure(0, weight=1)
        
        # NinjaTrader folder status
        if self.cleaner.ninjatrader_path:
            status_text = f"✅ NinjaTrader folder found:\n{self.cleaner.ninjatrader_path}"
            status_color = "green"
        else:
            status_text = "❌ NinjaTrader folder not found in Documents directory"
            status_color = "red"
        
        self.status_label = ttk.Label(status_frame, text=status_text, foreground=status_color)
        self.status_label.grid(row=0, column=0, sticky="ew")
        
        # Folders to clean frame
        folders_frame = ttk.LabelFrame(main_frame, text="Folders to Clean", padding="10")
        folders_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        folders_frame.columnconfigure(0, weight=1)
        
        folders_to_clean = self.cleaner.get_folders_to_clean()
        if folders_to_clean:
            folders_text = "\n".join([f"• {desc}: {path}" for path, desc in folders_to_clean])
        else:
            folders_text = "No folders found to clean"
        
        folders_label = ttk.Label(folders_frame, text=folders_text, justify=tk.LEFT)
        folders_label.grid(row=0, column=0, sticky="ew")
        
        # Protected folders info
        protected_frame = ttk.LabelFrame(main_frame, text="Protected Folders (Will NOT be cleaned)", padding="10")
        protected_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        protected_frame.columnconfigure(0, weight=1)
        
        protected_folders = self.cleaner.get_protected_folders()
        protected_text = "These folders will remain untouched:\n" + "\n".join([f"• {folder}" for folder in protected_folders])
        
        protected_label = ttk.Label(protected_frame, text=protected_text, foreground="blue")
        protected_label.grid(row=0, column=0, sticky="ew")
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame, 
            variable=self.progress_var, 
            maximum=100, 
            mode='determinate'
        )
        self.progress_bar.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        
        # Progress label
        self.progress_label = ttk.Label(main_frame, text="Ready to clean")
        self.progress_label.grid(row=5, column=0, pady=(0, 20))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=6, column=0, sticky="ew")
        buttons_frame.columnconfigure(1, weight=1)
        
        # Clean button
        self.clean_button = ttk.Button(
            buttons_frame,
            text="🧹 Clean NinjaTrader",
            command=self.start_cleanup,
            style='Accent.TButton'
        )
        self.clean_button.grid(row=0, column=0, padx=(0, 10))
        
        # View log button
        self.log_button = ttk.Button(
            buttons_frame,
            text="📄 View Log",
            command=self.view_log
        )
        self.log_button.grid(row=0, column=2)
        
        # Disable clean button if NinjaTrader not found
        if not self.cleaner.ninjatrader_path:
            self.clean_button.config(state='disabled')
    
    def progress_callback(self, current: int, total: int, message: str) -> None:
        """Update progress bar and label."""
        progress = (current / total) * 100
        self.progress_var.set(progress)
        self.progress_label.config(text=message)
        self.root.update_idletasks()
    
    def start_cleanup(self) -> None:
        """Start the cleanup process with confirmation."""
        folders_to_clean = self.cleaner.get_folders_to_clean()
        if not folders_to_clean:
            messagebox.showerror("Error", "No folders found to clean!")
            return
        
        # Confirmation dialog
        folder_list = "\n".join([f"• {desc}" for _, desc in folders_to_clean])
        confirm_message = (
            f"This will permanently delete files from the following locations:\n\n"
            f"{folder_list}\n\n"
            f"Protected folders (Message, Replay, Snapshot) will NOT be touched.\n\n"
            f"Are you sure you want to continue?"
        )
        
        if not messagebox.askyesno("Confirm Cleanup", confirm_message):
            return
        
        # Disable button during cleanup
        self.clean_button.config(state='disabled')
        self.progress_var.set(0)
        
        try:
            # Perform cleanup
            success, message, results = self.cleaner.perform_cleanup(self.progress_callback)
            
            # Show results
            if success:
                messagebox.showinfo("Cleanup Complete", message)
            else:
                messagebox.showwarning("Cleanup Issues", message)
            
            # Show detailed results if requested
            if messagebox.askyesno("View Details", "Would you like to view detailed results?"):
                self.show_detailed_results(results)
                
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n\n{str(e)}")
        finally:
            # Re-enable button and reset progress
            self.clean_button.config(state='normal')
            self.progress_var.set(0)
            self.progress_label.config(text="Ready to clean")
    
    def show_detailed_results(self, results: dict) -> None:
        """Show detailed cleanup results in a new window."""
        details_window = tk.Toplevel(self.root)
        details_window.title("Cleanup Details")
        details_window.geometry("700x400")
        
        # Create text widget with scrollbar
        frame = ttk.Frame(details_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(frame, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add results to text widget
        details_text = "CLEANUP RESULTS\n" + "="*50 + "\n\n"
        
        for folder_desc, result in results.items():
            status_icon = "✅" if result['success'] else "❌"
            details_text += f"{status_icon} {folder_desc}\n"
            details_text += f"   Path: {result['path']}\n"
            details_text += f"   Result: {result['message']}\n"
            details_text += f"   Files removed: {result['files_removed']}\n\n"
        
        text_widget.insert(tk.END, details_text)
        text_widget.config(state=tk.DISABLED)
    
    def view_log(self) -> None:
        """Open the log file for viewing."""
        if self.cleaner.log_file and os.path.exists(self.cleaner.log_file):
            try:
                # Try to open with default system application
                import platform
                if platform.system() == "Windows":
                    import subprocess
                    subprocess.run(["cmd", "/c", "start", "", self.cleaner.log_file], shell=True)
                elif platform.system() == "Darwin":
                    import subprocess
                    subprocess.run(["open", self.cleaner.log_file])
                else:
                    import subprocess
                    subprocess.run(["xdg-open", self.cleaner.log_file])
            except Exception as e:
                messagebox.showinfo("Log File", f"Log file location:\n{self.cleaner.log_file}\n\nCouldn't open automatically: {str(e)}")
        else:
            messagebox.showwarning("Log File", "Log file not found or not created yet.")
    
    def run(self) -> None:
        """Start the GUI application."""
        self.root.mainloop()


def main():
    """Main entry point for the application."""
    try:
        app = NinjaTraderCleanerGUI()
        app.run()
    except Exception as e:
        # Fallback error handling
        print(f"Critical error: {e}")
        try:
            import tkinter.messagebox as mb
            mb.showerror("Critical Error", f"Application failed to start:\n\n{str(e)}")
        except:
            print("Failed to show error dialog")


if __name__ == "__main__":
    main()