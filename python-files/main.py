# main.py
import tkinter as tk
from gui import SecurityEventEncyclopedia
from data_manager import DataManager
from database import SecurityEventDB

class SecurityEventApp:
    def __init__(self):
        self.db = None
        self.data_manager = None
        self.gui = None
        
    def run(self):
        try:
            # Initialize database
            print("Initializing Security Event Encyclopedia...")
            self.db = SecurityEventDB()
            
            # Initialize data manager
            self.data_manager = DataManager(self.db)
            
            # Load initial data (built-in + custom)
            self.data_manager.load_initial_data()
            
            # Get event counts
            total_count = self.db.get_event_count()
            custom_count = self.db.get_custom_events_count()
            
            print(f"Database ready with {total_count} total events ({custom_count} custom)")
            
            # Create and run GUI - pass both db and data_manager
            root = tk.Tk()
            self.gui = SecurityEventEncyclopedia(root, self.db, self.data_manager)
            
            # Save custom events when application closes
            def on_closing():
                self.data_manager.save_custom_events()
                root.destroy()
            
            root.protocol("WM_DELETE_WINDOW", on_closing)
            root.mainloop()
            
        except Exception as e:
            print(f"Error starting application: {e}")
            import traceback
            traceback.print_exc()
            input("Press Enter to exit...")

def main():
    app = SecurityEventApp()
    app.run()

if __name__ == "__main__":
    main()