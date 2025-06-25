import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import random
import time

class BetterThanZipBomb:
    def __init__(self, root):
        self.root = root
        self.root.title("BetterThanZipBomb")
        self.root.geometry("500x220")
        self.root.resizable(False, False)
        
        # Create communication queue
        self.progress_queue = queue.Queue()
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure("TProgressbar", thickness=20)
        
        # Create UI elements
        self.create_widgets()
        
        # Operation control flag
        self.cancelled = False
        self.generation_active = False

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Warning label with red text
        self.warning_label = tk.Label(
            main_frame, 
            text="This program will probably do horrible things to your computer. Are you sure you want to continue?",
            fg="red",  # Bright red text
            font=("Arial", 10, "bold"),
            wraplength=460,
            justify="center"
        )
        self.warning_label.pack(pady=(0, 15))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            main_frame,
            orient="horizontal",
            length=400,
            mode="determinate"
        )
        self.progress_bar.pack(pady=5)
        
        # Progress label
        self.progress_label = ttk.Label(
            main_frame, 
            text="Waiting to start...",
            font=("Arial", 9)
        )
        self.progress_label.pack(pady=5)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=15)
        
        # Destroy Computer button with rainbow effect
        self.destroy_button = tk.Button(
            button_frame,
            text="DESTROY COMPUTER",
            command=self.start_generation,
            width=20,
            height=2,
            font=("Arial", 12, "bold"),
            fg="white",
            bg="black",
            activeforeground="white",
            activebackground="black",
            bd=0,
            relief="flat"
        )
        self.destroy_button.pack(side=tk.LEFT, padx=5)
        
        # Start rainbow animation
        self.animate_button()
        
        # Cancel button
        self.cancel_button = ttk.Button(
            button_frame,
            text="I CHANGED MY MIND",
            command=self.cancel_operation,
            state=tk.DISABLED,
            width=20
        )
        self.cancel_button.pack(side=tk.LEFT, padx=5)

    def animate_button(self):
        """Create rainbow animation effect for the destroy button"""
        if hasattr(self, 'destroy_button') and self.destroy_button.winfo_exists():
            # Generate random rainbow color
            colors = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#4B0082', '#9400D3']
            color = random.choice(colors)
            
            # Apply color to button
            self.destroy_button.config(
                fg=color,
                activeforeground=color
            )
            
            # Schedule next color change
            self.root.after(300, self.animate_button)

    def start_generation(self):
        """Start generation in background thread"""
        if self.generation_active:
            return
            
        self.generation_active = True
        self.destroy_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.progress_label.config(text="Initializing doomsday sequence... 0.0%")
        self.cancelled = False
        
        # Display final warning
        response = messagebox.askyesno(
            "FINAL WARNING", 
            "This will generate a 3,000,001-item recursive file that will likely:\n\n"
            "1. Consume all available RAM\n"
            "2. Fill your storage drive\n"
            "3. Crash your system\n"
            "4. Cause physical damage to hardware\n"
            "5. Summon digital demons\n\n"
            "Are you absolutely sure you want to continue?",
            icon="warning"
        )
        
        if not response:
            self.cancel_operation()
            return
        
        # Start worker thread
        self.thread = threading.Thread(target=self.generate_list)
        self.thread.daemon = True
        self.thread.start()
        
        # Start progress monitoring
        self.monitor_progress()

    def cancel_operation(self):
        """Cancel the generation operation"""
        self.cancelled = True
        self.generation_active = False
        self.cancel_button.config(state=tk.DISABLED)
        self.progress_label.config(text="Operation cancelled")
        self.destroy_button.config(state=tk.NORMAL)

    def update_progress(self, progress):
        """Update progress bar and label"""
        self.progress_bar.config(value=progress)
        self.progress_label.config(text=f"System destruction: {progress:.6f}%")
        self.root.update_idletasks()

    def monitor_progress(self):
        """Check queue and update UI"""
        try:
            while True:
                # Get progress from queue
                progress = self.progress_queue.get_nowait()
                
                if progress == "error":
                    # Handle memory error
                    messagebox.showerror("CRITICAL FAILURE", "Your computer surrendered! Insufficient memory")
                    self.reset_interface()
                    return
                
                self.update_progress(progress)
                
                # Operation completed
                if progress >= 100:
                    self.progress_label.config(text="DESTRUCTION COMPLETE!")
                    self.cancel_button.config(state=tk.DISABLED)
                    messagebox.showinfo(
                        "MISSION ACCOMPLISHED", 
                        "Your computer has been successfully destroyed!\n\n"
                        "File: recursive_armageddon.txt\n"
                        "Size: INFINITY bytes (approximately)"
                    )
                    self.generation_active = False
                    return
                    
        except queue.Empty:
            pass
        
        # Continue monitoring if operation is running
        if self.thread.is_alive() and not self.cancelled:
            self.root.after(100, self.monitor_progress)
        else:
            self.reset_interface()

    def reset_interface(self):
        """Reset UI to initial state"""
        self.destroy_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.progress_bar.config(value=0)
        self.generation_active = False

    def generate_list(self):
        """Generate recursive list items - THE DOOMSDAY DEVICE"""
        try:
            # Create apocalyptic output file
            with open("recursive_armageddon.txt", "w", encoding="utf-8") as file:
                current_item = "1. This is the first step of your computer's annihilation"
                
                # Total items: 3,000,001 (THREE MILLION)
                total_items = 3000001
                
                for i in range(1, total_items + 1):
                    if self.cancelled:
                        return
                    
                    # Write current item
                    file.write(f'{i}. "{current_item}"\n')
                    
                    # Prepare next item
                    current_item = f'{i}. "{current_item}"'
                    
                    # Update progress every 10000 items (more efficient)
                    if i % 10000 == 0:
                        progress = (i / total_items) * 100
                        self.progress_queue.put(progress)
            
            # Signal completion
            self.progress_queue.put(100.0)
            
        except MemoryError:
            self.progress_queue.put("error")
        except Exception as e:
            messagebox.showerror("UNEXPECTED FAILURE", f"The destruction failed: {str(e)}")
        finally:
            self.generation_active = False

if __name__ == "__main__":
    root = tk.Tk()
    app = BetterThanZipBomb(root)
    root.mainloop()
