#!/usr/bin/env python3
"""
Recipe Nest - A Modern Recipe Management Application
Built with CustomTkinter for a modern desktop experience
"""

import customtkinter as ctk
from ui.auth import AuthManager
from ui.dashboard import DashboardManager
from ui.recipe_manager import RecipeManager
from ui.profile import ProfileManager
from database import initialize_database
from models import session
import os

# Configure CTk appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class RecipeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Recipe Nest - Modern Recipe Management")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        
        # Initialize database
        initialize_database()
        
        # Current user session
        self.current_user = None
        
        # UI Managers
        self.auth_manager = None
        self.dashboard_manager = None
        self.recipe_manager = None
        self.profile_manager = None
        
        # Main layout setup
        self.setup_main_layout()
        self.setup_topbar()
        self.setup_sidebar()
        
        # Start with login screen
        self.show_login_screen()
    
    def setup_main_layout(self):
        """Setup the main application layout"""
        # Top bar for branding and user info
        self.topbar = ctk.CTkFrame(self.root, height=60, fg_color="#1a1a1a")
        self.topbar.pack(fill="x", side="top")
        self.topbar.pack_propagate(False)
        
        # Content area
        self.content_area = ctk.CTkFrame(self.root, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True)
        
        # Sidebar for navigation (hidden initially)
        self.sidebar = ctk.CTkFrame(self.content_area, width=200, fg_color="#2b2b2b")
        
        # Main content frame
        self.main_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)
    
    def setup_topbar(self):
        """Setup the top navigation bar"""
        # Logo and title
        logo_frame = ctk.CTkFrame(self.topbar, fg_color="transparent")
        logo_frame.pack(side="left", padx=20, pady=10)
        
        ctk.CTkLabel(logo_frame, text="🍽️ Recipe Nest", 
                    font=ctk.CTkFont(size=24, weight="bold"), 
                    text_color="#4a9eff").pack(side="left")
        
        # User info (right side)
        self.user_info_frame = ctk.CTkFrame(self.topbar, fg_color="transparent")
        self.user_info_frame.pack(side="right", padx=20, pady=10)
        
        self.username_label = ctk.CTkLabel(self.user_info_frame, text="", 
                                          font=ctk.CTkFont(size=14),
                                          text_color="#b0b0b0")
        self.username_label.pack(side="right")
    
    def setup_sidebar(self):
        """Setup the sidebar navigation"""
        # Navigation buttons
        nav_buttons = [
            ("🏠 Dashboard", self.show_dashboard),
            ("➕ Add Recipe", self.show_add_recipe),
            ("📚 My Recipes", self.show_my_recipes),
            ("🔍 Search Recipes", self.show_search_recipes),
            ("⭐ Favorites", self.show_favorites),
            ("👤 Profile", self.show_profile),
            ("📤 Export/Import", self.show_export_import),
        ]
        
        # Add navigation buttons
        for text, command in nav_buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                height=40,
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                hover_color="#3a3a3a",
                anchor="w"
            )
            btn.pack(fill="x", padx=10, pady=5)
        
        # Logout button at bottom
        ctk.CTkFrame(self.sidebar, height=20, fg_color="transparent").pack(fill="x", pady=10)
        
        self.logout_btn = ctk.CTkButton(
            self.sidebar,
            text="🚪 Logout",
            command=self.logout,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        self.logout_btn.pack(fill="x", padx=10, pady=5)
    
    def clear_main_frame(self):
        """Clear the main content area"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """Show the login/register screen"""
        self.clear_main_frame()
        self.sidebar.pack_forget()
        self.username_label.configure(text="")
        
        if not self.auth_manager:
            self.auth_manager = AuthManager(self.main_frame, self)
        
        self.auth_manager.show_login_screen()
    
    def show_dashboard(self):
        """Show the main dashboard"""
        if not self.current_user:
            self.show_login_screen()
            return
        
        self.clear_main_frame()
        self.sidebar.pack(fill="y", side="left")
        
        if not self.dashboard_manager:
            self.dashboard_manager = DashboardManager(self.main_frame, self)
        
        self.dashboard_manager.show_dashboard()
    
    def show_add_recipe(self):
        """Show the add recipe screen"""
        if not self.current_user:
            self.show_login_screen()
            return
        
        self.clear_main_frame()
        
        if not self.recipe_manager:
            self.recipe_manager = RecipeManager(self.main_frame, self)
        
        self.recipe_manager.show_add_recipe()
    
    def show_my_recipes(self):
        """Show user's recipes"""
        if not self.current_user:
            self.show_login_screen()
            return
        
        self.clear_main_frame()
        
        if not self.recipe_manager:
            self.recipe_manager = RecipeManager(self.main_frame, self)
        
        self.recipe_manager.show_my_recipes()
    
    def show_search_recipes(self):
        """Show recipe search screen"""
        if not self.current_user:
            self.show_login_screen()
            return
        
        self.clear_main_frame()
        
        if not self.recipe_manager:
            self.recipe_manager = RecipeManager(self.main_frame, self)
        
        self.recipe_manager.show_search_recipes()
    
    def show_favorites(self):
        """Show favorite recipes"""
        if not self.current_user:
            self.show_login_screen()
            return
        
        self.clear_main_frame()
        
        if not self.recipe_manager:
            self.recipe_manager = RecipeManager(self.main_frame, self)
        
        self.recipe_manager.show_favorites()
    
    def show_profile(self):
        """Show user profile screen"""
        if not self.current_user:
            self.show_login_screen()
            return
        
        self.clear_main_frame()
        
        if not self.profile_manager:
            self.profile_manager = ProfileManager(self.main_frame, self)
        
        self.profile_manager.show_profile()
    
    def show_export_import(self):
        """Show export/import screen"""
        if not self.current_user:
            self.show_login_screen()
            return
        
        self.clear_main_frame()
        
        if not self.recipe_manager:
            self.recipe_manager = RecipeManager(self.main_frame, self)
        
        self.recipe_manager.show_export_import()
    
    def login_success(self, user):
        """Handle successful login"""
        self.current_user = user
        self.username_label.configure(text=f"Welcome, {user.username}")
        self.show_dashboard()
    
    def logout(self):
        """Handle user logout"""
        self.current_user = None
        self.username_label.configure(text="")
        
        # Clear managers
        self.auth_manager = None
        self.dashboard_manager = None
        self.recipe_manager = None
        self.profile_manager = None
        
        self.show_login_screen()

def main():
    """Main application entry point"""
    root = ctk.CTk()
    app = RecipeApp(root)
    
    # Handle window closing
    def on_closing():
        session.close()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        on_closing()

if __name__ == "__main__":
    main()
