import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import requests
import cv2
import numpy as np
import os
from datetime import datetime
import base64
import json
import threading
import time
import queue
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Set CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

@dataclass
class FruitAnalysisResult:
    """Data class for fruit analysis results"""
    condition: str
    confidence: float
    fruit_type: str
    freshness_score: float
    defects: List[str]
    ripeness: str
    safety: str
    action_required: str
    prevention_tips: List[str]
    storage_advice: str
    disease_identification: str
    local_metrics: Dict
    ai_analysis: Optional[Dict] = None
    timestamp: datetime = None
    image: Optional[np.ndarray] = None
    detailed_analysis: str = ""
    key_observations: List[str] = None
    treatment_options: List[str] = None

class AdvancedFruitAnalyzerUI:
    def __init__(self, api_key):
        self.API_KEY = api_key
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        self.headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': self.API_KEY
        }
        
        # Initialize root window
        self.root = ctk.CTk()
        self.root.title("🍎 Fruit Health Inspector Pro - Advanced Analysis System")
        self.root.geometry("1600x900")
        self.root.minsize(1400, 800)
        
        # Initialize variables
        self.current_image_cv2 = None
        self.current_result = None
        self.comparison_images = {'before': None, 'after': None}
        self.comparison_results = {'before': None, 'after': None}
        self.analysis_history = []
        self.camera_active = False
        
        # Store last analysis for comparison
        self.last_analysis_image = None
        self.last_analysis_result = None
        
        # Initialize UI
        self.setup_ui()
        self.center_window()
        
        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_ui(self):
        """Setup the main UI structure"""
        # Create main container
        self.main_container = ctk.CTkFrame(self.root, fg_color="#0a0a0a")
        self.main_container.pack(fill="both", expand=True)
        
        # Create header
        self.create_header()
        
        # Create main content area with sidebar
        content_frame = ctk.CTkFrame(self.main_container, fg_color="#0a0a0a")
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create sidebar
        self.sidebar = ctk.CTkFrame(content_frame, fg_color="#1a1a1a", width=250)
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))
        self.sidebar.pack_propagate(False)
        
        # Create main view area
        self.main_view = ctk.CTkFrame(content_frame, fg_color="#1a1a1a")
        self.main_view.pack(side="right", fill="both", expand=True)
        
        # Setup sidebar
        self.setup_sidebar()
        
        # Setup initial view
        self.show_analysis_view()
        
    def create_header(self):
        """Create application header"""
        header = ctk.CTkFrame(self.main_container, fg_color="#0f0f0f", height=80)
        header.pack(fill="x", padx=10, pady=(10, 5))
        header.pack_propagate(False)
        
        # Logo and title
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=20, pady=10)
        
        title = ctk.CTkLabel(
            title_frame,
            text="🍎 Fruit Health Inspector Pro",
            font=ctk.CTkFont(family="Arial Black", size=28, weight="bold"),
            text_color="#ffffff"
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="AI-Powered Quality Analysis & Disease Detection System",
            font=ctk.CTkFont(size=14),
            text_color="#888888"
        )
        subtitle.pack(anchor="w")
        
        # Status indicators
        status_frame = ctk.CTkFrame(header, fg_color="transparent")
        status_frame.pack(side="right", padx=20)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="● System Ready",
            font=ctk.CTkFont(size=12),
            text_color="#4CAF50"
        )
        self.status_label.pack()
        
        self.time_label = ctk.CTkLabel(
            status_frame,
            text=datetime.now().strftime("%B %d, %Y | %I:%M %p"),
            font=ctk.CTkFont(size=11),
            text_color="#666666"
        )
        self.time_label.pack()
        
        # Update time
        self.update_time()
        
    def update_time(self):
        """Update time display"""
        if hasattr(self, 'time_label') and self.time_label.winfo_exists():
            self.time_label.configure(text=datetime.now().strftime("%B %d, %Y | %I:%M %p"))
            self.root.after(1000, self.update_time)
            
    def setup_sidebar(self):
        """Setup sidebar navigation"""
        # Sidebar header
        sidebar_header = ctk.CTkLabel(
            self.sidebar,
            text="Navigation",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        )
        sidebar_header.pack(pady=(20, 10))
        
        # Navigation buttons
        nav_buttons = [
            ("🔍 Analysis", self.show_analysis_view),
            ("📊 Comparison", self.show_comparison_view),
            ("📈 History", self.show_history_view),
            ("📋 Reports", self.show_reports_view),
            ("⚙️ Settings", self.show_settings_view),
            ("❓ Help", self.show_help_view)
        ]
        
        self.nav_buttons = {}
        for text, command in nav_buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                font=ctk.CTkFont(size=14, weight="bold"),
                height=45,
                corner_radius=10,
                fg_color="#2a2a2a",
                hover_color="#3a3a3a",
                anchor="w"
            )
            btn.pack(fill="x", padx=15, pady=5)
            self.nav_buttons[text] = btn
            
        # Separator
        sep = ctk.CTkFrame(self.sidebar, fg_color="#333333", height=2)
        sep.pack(fill="x", padx=20, pady=20)
        
        # Quick actions
        quick_label = ctk.CTkLabel(
            self.sidebar,
            text="Quick Actions",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#cccccc"
        )
        quick_label.pack(pady=(0, 10))
        
        # Quick action buttons
        quick_actions = [
            ("📷 Camera", self.quick_camera_capture, "#1e8e3e"),
            ("📁 Load File", self.quick_load_file, "#1976d2"),
            ("💾 Export", self.quick_export, "#9c27b0")
        ]
        
        for text, command, color in quick_actions:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                font=ctk.CTkFont(size=12),
                height=35,
                corner_radius=8,
                fg_color=color,
                hover_color=color
            )
            btn.pack(fill="x", padx=15, pady=3)
            
        # Bottom info
        info_frame = ctk.CTkFrame(self.sidebar, fg_color="#2a2a2a", corner_radius=10)
        info_frame.pack(side="bottom", fill="x", padx=15, pady=15)
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="💡 Tip: Use good lighting\nfor accurate analysis",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
            justify="left"
        )
        info_label.pack(padx=10, pady=10)
        
    def clear_main_view(self):
        """Clear main view area"""
        for widget in self.main_view.winfo_children():
            widget.destroy()
            
    def show_analysis_view(self):
        """Show main analysis view"""
        self.clear_main_view()
        self.highlight_nav_button("🔍 Analysis")
        
        # Create analysis layout
        analysis_container = ctk.CTkFrame(self.main_view, fg_color="#1a1a1a")
        analysis_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Top row - Image and controls
        top_frame = ctk.CTkFrame(analysis_container, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 10))
        
        # Image section
        image_section = ctk.CTkFrame(top_frame, fg_color="#2a2a2a", corner_radius=15, width=500)
        image_section.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Image display
        self.image_frame = ctk.CTkFrame(image_section, fg_color="#000000", corner_radius=10)
        self.image_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.image_label = ctk.CTkLabel(
            self.image_frame,
            text="📷 No Image Loaded\n\nClick buttons below to load an image",
            font=ctk.CTkFont(size=16),
            text_color="#666666"
        )
        self.image_label.pack(fill="both", expand=True)
        
        # Image controls
        controls_frame = ctk.CTkFrame(image_section, fg_color="transparent")
        controls_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        control_buttons = [
            ("📷 Camera", self.capture_from_camera, "#4CAF50"),
            ("📁 File", self.load_from_file, "#2196F3"),
            ("🌐 URL", self.load_from_url, "#FF9800"),
            ("🗑️ Clear", self.clear_image, "#f44336")
        ]
        
        for i, (text, command, color) in enumerate(control_buttons):
            btn = ctk.CTkButton(
                controls_frame,
                text=text,
                command=command,
                font=ctk.CTkFont(size=12, weight="bold"),
                height=35,
                corner_radius=8,
                fg_color=color,
                hover_color=color,
                width=100
            )
            btn.grid(row=0, column=i, padx=5, pady=0)
            
        # Quick info section
        info_section = ctk.CTkFrame(top_frame, fg_color="#2a2a2a", corner_radius=15, width=400)
        info_section.pack(side="right", fill="both", expand=True)
        info_section.pack_propagate(False)
        
        info_title = ctk.CTkLabel(
            info_section,
            text="📊 Quick Overview",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        )
        info_title.pack(pady=(15, 10))
        
        self.quick_info_frame = ctk.CTkFrame(info_section, fg_color="transparent")
        self.quick_info_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Initial message
        self.no_info_label = ctk.CTkLabel(
            self.quick_info_frame,
            text="Load an image and click\n'Analyze' to see results",
            font=ctk.CTkFont(size=14),
            text_color="#666666"
        )
        self.no_info_label.pack(expand=True)
        
        # Analyze button
        self.analyze_button = ctk.CTkButton(
            info_section,
            text="🔬 ANALYZE FRUIT",
            command=self.analyze_current_image,
            font=ctk.CTkFont(size=18, weight="bold"),
            height=60,
            corner_radius=30,
            fg_color="#FF5722",
            hover_color="#FF7043",
            state="disabled"
        )
        self.analyze_button.pack(fill="x", padx=15, pady=(0, 15))
        
        # Bottom row - Detailed results
        results_frame = ctk.CTkFrame(analysis_container, fg_color="#2a2a2a", corner_radius=15)
        results_frame.pack(fill="both", expand=True)
        
        results_title = ctk.CTkLabel(
            results_frame,
            text="📋 Detailed Analysis Results",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        )
        results_title.pack(pady=(15, 10))
        
        # Create notebook for organized results
        self.results_notebook = ctk.CTkTabview(results_frame, fg_color="#333333", corner_radius=10)
        self.results_notebook.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Add tabs
        self.results_notebook.add("🎯 Condition")
        self.results_notebook.add("🦠 Health Status")
        self.results_notebook.add("📊 Metrics")
        self.results_notebook.add("💡 Recommendations")
        self.results_notebook.add("📈 Technical Data")
        
        # Initialize tab contents
        self.init_condition_tab()
        self.init_health_tab()
        self.init_metrics_tab()
        self.init_recommendations_tab()
        self.init_technical_tab()
        
    def init_condition_tab(self):
        """Initialize condition tab"""
        tab = self.results_notebook.tab("🎯 Condition")
        self.condition_content = ctk.CTkScrollableFrame(tab, fg_color="#2a2a2a")
        self.condition_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Placeholder
        placeholder = ctk.CTkLabel(
            self.condition_content,
            text="Fruit condition analysis will appear here",
            font=ctk.CTkFont(size=14),
            text_color="#666666"
        )
        placeholder.pack(pady=50)
        
    def init_health_tab(self):
        """Initialize health status tab"""
        tab = self.results_notebook.tab("🦠 Health Status")
        self.health_content = ctk.CTkScrollableFrame(tab, fg_color="#2a2a2a")
        self.health_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        placeholder = ctk.CTkLabel(
            self.health_content,
            text="Disease and infection analysis will appear here",
            font=ctk.CTkFont(size=14),
            text_color="#666666"
        )
        placeholder.pack(pady=50)
        
    def init_metrics_tab(self):
        """Initialize metrics tab"""
        tab = self.results_notebook.tab("📊 Metrics")
        self.metrics_content = ctk.CTkScrollableFrame(tab, fg_color="#2a2a2a")
        self.metrics_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        placeholder = ctk.CTkLabel(
            self.metrics_content,
            text="Quality metrics and scores will appear here",
            font=ctk.CTkFont(size=14),
            text_color="#666666"
        )
        placeholder.pack(pady=50)
        
    def init_recommendations_tab(self):
        """Initialize recommendations tab"""
        tab = self.results_notebook.tab("💡 Recommendations")
        self.recommendations_content = ctk.CTkScrollableFrame(tab, fg_color="#2a2a2a")
        self.recommendations_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        placeholder = ctk.CTkLabel(
            self.recommendations_content,
            text="Prevention tips and recommendations will appear here",
            font=ctk.CTkFont(size=14),
            text_color="#666666"
        )
        placeholder.pack(pady=50)
        
    def init_technical_tab(self):
        """Initialize technical data tab"""
        tab = self.results_notebook.tab("📈 Technical Data")
        self.technical_content = ctk.CTkScrollableFrame(tab, fg_color="#2a2a2a")
        self.technical_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        placeholder = ctk.CTkLabel(
            self.technical_content,
            text="Technical analysis data will appear here",
            font=ctk.CTkFont(size=14),
            text_color="#666666"
        )
        placeholder.pack(pady=50)
        
    def show_comparison_view(self):
        """Show comparison view with auto-load from analysis"""
        self.clear_main_view()
        self.highlight_nav_button("📊 Comparison")
        
        # Create comparison layout
        comparison_container = ctk.CTkFrame(self.main_view, fg_color="#1a1a1a")
        comparison_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title = ctk.CTkLabel(
            comparison_container,
            text="📊 Fruit Comparison Analysis",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#ffffff"
        )
        title.pack(pady=(10, 20))
        
        # Info message
        if self.last_analysis_image is not None:
            info_label = ctk.CTkLabel(
                comparison_container,
                text="💡 Your last analyzed image has been automatically loaded as 'Before'",
                font=ctk.CTkFont(size=12),
                text_color="#4CAF50"
            )
            info_label.pack(pady=(0, 10))
            
        # Images frame
        images_frame = ctk.CTkFrame(comparison_container, fg_color="transparent")
        images_frame.pack(fill="both", expand=True, padx=20)
        
        # Before section
        before_frame = ctk.CTkFrame(images_frame, fg_color="#2a2a2a", corner_radius=15)
        before_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        before_title = ctk.CTkLabel(
            before_frame,
            text="📸 Before / First Fruit",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4CAF50"
        )
        before_title.pack(pady=(15, 10))
        
        # Before image
        self.before_image_frame = ctk.CTkFrame(before_frame, fg_color="#000000", corner_radius=10, height=300)
        self.before_image_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        self.before_image_frame.pack_propagate(False)
        
        self.before_image_label = ctk.CTkLabel(
            self.before_image_frame,
            text="No image loaded\n\nClick 'Load Image' below",
            font=ctk.CTkFont(size=14),
            text_color="#666666"
        )
        self.before_image_label.pack(expand=True)
        
        # Before controls
        before_btn_frame = ctk.CTkFrame(before_frame, fg_color="transparent")
        before_btn_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        load_before_btn = ctk.CTkButton(
            before_btn_frame,
            text="📁 Load Image",
            command=lambda: self.load_comparison_image('before'),
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35,
            fg_color="#4CAF50",
            corner_radius=8
        )
        load_before_btn.pack(side="left", padx=(0, 5))
        
        use_last_btn = ctk.CTkButton(
            before_btn_frame,
            text="📷 Use Last Analysis",
            command=self.use_last_analysis_as_before,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35,
            fg_color="#FF9800",
            corner_radius=8
        )
        use_last_btn.pack(side="left", padx=5)
        
        analyze_before_btn = ctk.CTkButton(
            before_btn_frame,
            text="🔬 Analyze",
            command=lambda: self.analyze_comparison_image('before'),
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35,
            fg_color="#2196F3",
            corner_radius=8
        )
        analyze_before_btn.pack(side="left", padx=5)
        
        # Before results
        self.before_results_frame = ctk.CTkFrame(before_frame, fg_color="#333333", corner_radius=10)
        self.before_results_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        before_results_placeholder = ctk.CTkLabel(
            self.before_results_frame,
            text="Results will appear here",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        before_results_placeholder.pack(pady=20)
        
        # After section
        after_frame = ctk.CTkFrame(images_frame, fg_color="#2a2a2a", corner_radius=15)
        after_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        after_title = ctk.CTkLabel(
            after_frame,
            text="📸 After / Second Fruit",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FF9800"
        )
        after_title.pack(pady=(15, 10))
        
        # After image
        self.after_image_frame = ctk.CTkFrame(after_frame, fg_color="#000000", corner_radius=10, height=300)
        self.after_image_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        self.after_image_frame.pack_propagate(False)
        
        self.after_image_label = ctk.CTkLabel(
            self.after_image_frame,
            text="No image loaded\n\nClick 'Load Image' below",
            font=ctk.CTkFont(size=14),
            text_color="#666666"
        )
        self.after_image_label.pack(expand=True)
        
        # After controls
        after_btn_frame = ctk.CTkFrame(after_frame, fg_color="transparent")
        after_btn_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        load_after_btn = ctk.CTkButton(
            after_btn_frame,
            text="📁 Load Image",
            command=lambda: self.load_comparison_image('after'),
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35,
            fg_color="#FF9800",
            corner_radius=8
        )
        load_after_btn.pack(side="left", padx=(0, 5))
        
        use_current_btn = ctk.CTkButton(
            after_btn_frame,
            text="📷 Use Current",
            command=self.use_current_image_as_after,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35,
            fg_color="#4CAF50",
            corner_radius=8
        )
        use_current_btn.pack(side="left", padx=5)
        
        analyze_after_btn = ctk.CTkButton(
            after_btn_frame,
            text="🔬 Analyze",
            command=lambda: self.analyze_comparison_image('after'),
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35,
            fg_color="#2196F3",
            corner_radius=8
        )
        analyze_after_btn.pack(side="left", padx=5)
        
        # After results
        self.after_results_frame = ctk.CTkFrame(after_frame, fg_color="#333333", corner_radius=10)
        self.after_results_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        after_results_placeholder = ctk.CTkLabel(
            self.after_results_frame,
            text="Results will appear here",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        after_results_placeholder.pack(pady=20)
        
        # Comparison results section
        comparison_results_frame = ctk.CTkFrame(comparison_container, fg_color="#2a2a2a", corner_radius=15)
        comparison_results_frame.pack(fill="x", padx=20, pady=(20, 0))
        
        comparison_title = ctk.CTkLabel(
            comparison_results_frame,
            text="📊 Comparison Summary",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        )
        comparison_title.pack(pady=(15, 10))
        
        # Compare button
        self.compare_btn = ctk.CTkButton(
            comparison_results_frame,
            text="🔄 COMPARE FRUITS",
            command=self.perform_comparison,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            corner_radius=25,
            fg_color="#9C27B0",
            hover_color="#AB47BC",
            state="disabled"
        )
        self.compare_btn.pack(pady=10)
        
        # Comparison results display
        self.comparison_results_display = ctk.CTkFrame(comparison_results_frame, fg_color="#333333", corner_radius=10)
        self.comparison_results_display.pack(fill="both", expand=True, padx=15, pady=(10, 15))
        
        comparison_placeholder = ctk.CTkLabel(
            self.comparison_results_display,
            text="Load and analyze both images to see comparison",
            font=ctk.CTkFont(size=14),
            text_color="#888888"
        )
        comparison_placeholder.pack(pady=30)
        
        # Auto-load last analysis if available
        if self.last_analysis_image is not None:
            self.use_last_analysis_as_before()
            
    def use_last_analysis_as_before(self):
        """Use the last analyzed image as 'before' image"""
        if self.last_analysis_image is not None and self.last_analysis_result is not None:
            self.comparison_images['before'] = self.last_analysis_image
            self.comparison_results['before'] = self.last_analysis_result
            
            # Display the image
            image_rgb = cv2.cvtColor(self.last_analysis_image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)
            
            # Resize for display
            display_size = (280, 200)
            pil_image.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(pil_image)
            
            # Update label
            self.before_image_label.configure(image=photo, text="")
            self.before_image_label.image = photo
            
            # Display results
            self.display_comparison_result('before', self.last_analysis_result)
            
            # Check if ready to compare
            self.check_comparison_ready()
            
            self.show_notification("✅ Last analysis loaded as 'Before' image", "success")
        else:
            self.show_notification("⚠️ No previous analysis available", "warning")
            
    def use_current_image_as_after(self):
        """Use the current image from analysis tab as 'after' image"""
        if self.current_image_cv2 is not None:
            self.comparison_images['after'] = self.current_image_cv2
            
            # Display the image
            image_rgb = cv2.cvtColor(self.current_image_cv2, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)
            
            # Resize for display
            display_size = (280, 200)
            pil_image.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(pil_image)
            
            # Update label
            self.after_image_label.configure(image=photo, text="")
            self.after_image_label.image = photo
            
            # If we have current result, use it
            if self.current_result is not None:
                self.comparison_results['after'] = self.current_result
                self.display_comparison_result('after', self.current_result)
                self.check_comparison_ready()
            else:
                # Need to analyze
                self.show_notification("📊 Analyzing 'After' image...", "info")
                self.analyze_comparison_image('after')
        else:
            self.show_notification("⚠️ No image loaded in analysis tab", "warning")
            
    def load_comparison_image(self, position):
        """Load image for comparison"""
        file_path = filedialog.askopenfilename(
            title=f"Select {position.capitalize()} Image",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Load image
                image = cv2.imread(file_path)
                if image is not None:
                    self.comparison_images[position] = image
                    
                    # Display image
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(image_rgb)
                    
                    # Resize for display
                    display_size = (280, 200)
                    pil_image.thumbnail(display_size, Image.Resampling.LANCZOS)
                    
                    # Convert to PhotoImage
                    photo = ImageTk.PhotoImage(pil_image)
                    
                    # Update appropriate label
                    if position == 'before':
                        self.before_image_label.configure(image=photo, text="")
                        self.before_image_label.image = photo
                    else:
                        self.after_image_label.configure(image=photo, text="")
                        self.after_image_label.image = photo
                    
                    self.show_notification(f"✅ {position.capitalize()} image loaded", "success")
                    self.check_comparison_ready()
                else:
                    self.show_notification("❌ Failed to load image", "error")
            except Exception as e:
                self.show_notification(f"❌ Error: {str(e)}", "error")
                
    def analyze_comparison_image(self, position):
        """Analyze comparison image"""
        if self.comparison_images[position] is None:
            self.show_notification(f"⚠️ No {position} image loaded", "warning")
            return
            
        # Show progress
        if position == 'before':
            results_frame = self.before_results_frame
        else:
            results_frame = self.after_results_frame
            
        # Clear previous results
        for widget in results_frame.winfo_children():
            widget.destroy()
            
        # Show loading
        loading_label = ctk.CTkLabel(
            results_frame,
            text="🔄 Analyzing...",
            font=ctk.CTkFont(size=12),
            text_color="#4CAF50"
        )
        loading_label.pack(pady=20)
        
        # Perform analysis in thread
        def analyze_thread():
            try:
                # Analyze image
                result = self.perform_fruit_analysis(self.comparison_images[position])
                self.comparison_results[position] = result
                
                # Update UI
                self.root.after(0, lambda: self.display_comparison_result(position, result))
                self.root.after(0, self.check_comparison_ready)
                
            except Exception as e:
                self.root.after(0, lambda: self.show_notification(f"❌ Analysis failed: {str(e)}", "error"))
                
        thread = threading.Thread(target=analyze_thread, daemon=True)
        thread.start()
        
    def display_comparison_result(self, position, result):
        """Display comparison analysis result"""
        if position == 'before':
            results_frame = self.before_results_frame
        else:
            results_frame = self.after_results_frame
            
        # Clear frame
        for widget in results_frame.winfo_children():
            widget.destroy()
            
        # Display results
        # Condition
        condition_color = self.get_condition_color(result.condition)
        condition_label = ctk.CTkLabel(
            results_frame,
            text=result.condition.split(' - ')[0],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=condition_color
        )
        condition_label.pack(pady=(15, 5))
        
        # Metrics
        metrics = [
            (f"🍎 Type: {result.fruit_type}"),
            (f"💯 Confidence: {result.confidence:.0f}%"),
            (f"🌟 Freshness: {result.freshness_score:.0f}%"),
            (f"🏥 Safety: {result.safety}")
        ]
        
        for metric in metrics:
            metric_label = ctk.CTkLabel(
                results_frame,
                text=metric,
                font=ctk.CTkFont(size=11),
                text_color="#cccccc"
            )
            metric_label.pack(pady=2)
            
        # Defects
        if result.defects:
            defect_text = f"⚠️ Issues: {len(result.defects)} found"
            defect_label = ctk.CTkLabel(
                results_frame,
                text=defect_text,
                font=ctk.CTkFont(size=11),
                text_color="#ff9800"
            )
            defect_label.pack(pady=2)
            
    def check_comparison_ready(self):
        """Check if both images are analyzed and ready for comparison"""
        if self.comparison_results['before'] and self.comparison_results['after']:
            self.compare_btn.configure(state="normal")
        else:
            self.compare_btn.configure(state="disabled")
            
    def perform_comparison(self):
        """Perform detailed comparison between two fruits"""
        if not (self.comparison_results['before'] and self.comparison_results['after']):
            self.show_notification("⚠️ Please analyze both images first", "warning")
            return
            
        # Clear comparison display
        for widget in self.comparison_results_display.winfo_children():
            widget.destroy()
            
        before = self.comparison_results['before']
        after = self.comparison
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color="#ffffff"
        
        title.pack(pady=(0, 15))
        
        # Overall change
        overall_frame = ctk.CTkFrame(comparison_frame, fg_color="#444444", corner_radius=10)
        overall_frame.pack(fill="x", pady=10)
        
        # Determine overall change
        freshness_change = after.freshness_score - before.freshness_score
        if freshness_change > 10:
            change_text = "📈 IMPROVED"
            change_color = "#4CAF50"
        elif freshness_change < -10:
            change_text = "📉 DEGRADED"
            change_color = "#f44336"
        else:
            change_text = "➡️ SIMILAR"
            change_color = "#FF9800"
            
        overall_label = ctk.CTkLabel(
            overall_frame,
            text=f"Overall Status: {change_text}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=change_color
        )
        overall_label.pack(pady=15)
        
        # Detailed metrics comparison
        metrics_data = [
            ("Fruit Type", before.fruit_type, after.fruit_type),
            ("Condition", before.condition.split(' - ')[0], after.condition.split(' - ')[0]),
            ("Freshness", f"{before.freshness_score:.0f}%", f"{after.freshness_score:.0f}%"),
            ("Confidence", f"{before.confidence:.0f}%", f"{after.confidence:.0f}%"),
            ("Safety", before.safety, after.safety),
            ("Ripeness", before.ripeness, after.ripeness),
            ("Defects", len(before.defects), len(after.defects))
        ]
        
        # Create comparison table
        table_frame = ctk.CTkFrame(comparison_frame, fg_color="#444444", corner_radius=10)
        table_frame.pack(fill="x", pady=10)
        
        # Table header
        headers = ["Metric", "Before", "After", "Change"]
        for i, header in enumerate(headers):
            header_label = ctk.CTkLabel(
                table_frame,
                text=header,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#ffffff"
            )
            header_label.grid(row=0, column=i, padx=15, pady=10, sticky="w")
            
        # Table rows
        for i, (metric, before_val, after_val) in enumerate(metrics_data, 1):
            # Metric name
            metric_label = ctk.CTkLabel(
                table_frame,
                text=metric,
                font=ctk.CTkFont(size=12),
                text_color="#cccccc"
            )
            metric_label.grid(row=i, column=0, padx=15, pady=5, sticky="w")
            
            # Before value
            before_label = ctk.CTkLabel(
                table_frame,
                text=str(before_val),
                font=ctk.CTkFont(size=12),
                text_color="#888888"
            )
            before_label.grid(row=i, column=1, padx=15, pady=5, sticky="w")
            
            # After value
            after_label = ctk.CTkLabel(
                table_frame,
                text=str(after_val),
                font=ctk.CTkFont(size=12),
                text_color="#888888"
            )
            after_label.grid(row=i, column=2, padx=15, pady=5, sticky="w")
            
            # Change indicator
            if before_val != after_val:
                if isinstance(before_val, (int, float)) and isinstance(after_val, (int, float)):
                    change = after_val - before_val
                    if change > 0:
                        change_text = f"↑ +{change}"
                        change_color = "#4CAF50"
                    else:
                        change_text = f"↓ {change}"
                        change_color = "#f44336"
                else:
                    change_text = "Changed"
                    change_color = "#FF9800"
            else:
                change_text = "Same"
                change_color = "#888888"
                
            change_label = ctk.CTkLabel(
                table_frame,
                text=change_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=change_color
            )
            change_label.grid(row=i, column=3, padx=15, pady=5, sticky="w")
            
        # Recommendations based on comparison
        rec_frame = ctk.CTkFrame(comparison_frame, fg_color="#444444", corner_radius=10)
        rec_frame.pack(fill="x", pady=10)
        
        rec_title = ctk.CTkLabel(
            rec_frame,
            text="💡 Comparison Insights",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff"
        )
        rec_title.pack(pady=(10, 5))
        
        # Generate insights
        insights = self.generate_comparison_insights(before, after)
        for insight in insights:
            insight_label = ctk.CTkLabel(
                rec_frame,
                text=f"• {insight}",
                font=ctk.CTkFont(size=12),
                text_color="#cccccc",
                wraplength=600,
                anchor="w",
                justify="left"
            )
            insight_label.pack(anchor="w", padx=20, pady=3)
            
        rec_frame.pack(pady=(0, 10))
        
        self.show_notification("✅ Comparison completed", "success")
        
    def generate_comparison_insights(self, before, after):
        """Generate insights from comparison"""
        insights = []
        
        # Freshness change
        freshness_diff = after.freshness_score - before.freshness_score
        if freshness_diff < -20:
            insights.append(f"Significant quality deterioration detected ({freshness_diff:.0f}% decrease)")
        elif freshness_diff > 20:
            insights.append(f"Quality has improved significantly ({freshness_diff:.0f}% increase)")
            
        # Defects change
        defect_diff = len(after.defects) - len(before.defects)
        if defect_diff > 0:
            insights.append(f"{defect_diff} new defects have appeared")
        elif defect_diff < 0:
            insights.append(f"{abs(defect_diff)} defects have been resolved")
            
        # Safety change
        if before.safety != after.safety:
            insights.append(f"Safety status changed from {before.safety} to {after.safety}")
            
        # Storage recommendation
        if after.freshness_score < 50:
            insights.append("Immediate action required - fruit quality is poor")
        elif freshness_diff < -10:
            insights.append("Consider using the fruit soon as quality is declining")
            
        # Type change
        if before.fruit_type != after.fruit_type:
            insights.append(f"Note: Comparing different fruit types ({before.fruit_type} vs {after.fruit_type})")
            
        return insights if insights else ["No significant changes detected between samples"]
        
    def show_history_view(self):
        """Show analysis history"""
        self.clear_main_view()
        self.highlight_nav_button("📈 History")
        
        # Create history container
        history_container = ctk.CTkFrame(self.main_view, fg_color="#1a1a1a")
        history_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title = ctk.CTkLabel(
            history_container,
            text="📈 Analysis History",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#ffffff"
        )
        title.pack(pady=(10, 20))
        
        # History list
        history_scroll = ctk.CTkScrollableFrame(history_container, fg_color="#2a2a2a", corner_radius=15)
        history_scroll.pack(fill="both", expand=True, padx=20)
        
        if not self.analysis_history:
            no_history = ctk.CTkLabel(
                history_scroll,
                text="No analysis history yet\n\nYour previous analyses will appear here",
                font=ctk.CTkFont(size=16),
                text_color="#666666"
            )
            no_history.pack(pady=100)
        else:
            # Display history entries
            for i, result in enumerate(reversed(self.analysis_history[-20:])):  # Last 20 entries
                self.create_history_entry(history_scroll, result, i)
                
    def create_history_entry(self, parent, result, index):
        """Create a history entry widget"""
        entry_frame = ctk.CTkFrame(parent, fg_color="#333333", corner_radius=10)
        entry_frame.pack(fill="x", padx=15, pady=8)
        
        # Left side - image thumbnail
        if result.image is not None:
            image_rgb = cv2.cvtColor(result.image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)
            pil_image.thumbnail((80, 80), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(pil_image)
            
            image_label = ctk.CTkLabel(entry_frame, image=photo, text="")
            image_label.image = photo
            image_label.pack(side="left", padx=15, pady=15)
        
        # Middle - details
        details_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
        details_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        # Timestamp
        timestamp_label = ctk.CTkLabel(
            details_frame,
            text=result.timestamp.strftime("%B %d, %Y at %I:%M %p"),
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        timestamp_label.pack(anchor="w", pady=(15, 5))
        
        # Fruit info
        info_text = f"{result.fruit_type} - {result.condition.split(' - ')[0]}"
        info_label = ctk.CTkLabel(
            details_frame,
            text=info_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.get_condition_color(result.condition)
        )
        info_label.pack(anchor="w")
        
        # Metrics
        metrics_text = f"Freshness: {result.freshness_score:.0f}% | Confidence: {result.confidence:.0f}%"
        metrics_label = ctk.CTkLabel(
            details_frame,
            text=metrics_text,
            font=ctk.CTkFont(size=11),
            text_color="#cccccc"
        )
        metrics_label.pack(anchor="w", pady=(5, 15))
        
        # Right side - actions
        actions_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
        actions_frame.pack(side="right", padx=15)
        
        view_btn = ctk.CTkButton(
            actions_frame,
            text="View Details",
            command=lambda r=result: self.view_history_details(r),
            font=ctk.CTkFont(size=11),
            width=100,
            height=30,
            corner_radius=6,
            fg_color="#2196F3"
        )
        view_btn.pack(pady=5)
        
    def view_history_details(self, result):
        """View detailed history entry"""
        # Switch to analysis view and load the result
        self.show_analysis_view()
        
        # Display the historical image
        if result.image is not None:
            self.current_image_cv2 = result.image
            self.display_image_in_analysis(result.image)
            
        # Display the historical results
        self.current_result = result
        self.display_analysis_results(result)
        
    def show_reports_view(self):
        """Show reports view"""
        self.clear_main_view()
        self.highlight_nav_button("📋 Reports")
        
        reports_container = ctk.CTkFrame(self.main_view, fg_color="#1a1a1a")
        reports_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        title = ctk.CTkLabel(
            reports_container,
            text="📋 Export Reports",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#ffffff"
        )
        title.pack(pady=(10, 30))
        
        # Export options
        options_frame = ctk.CTkFrame(reports_container, fg_color="#2a2a2a", corner_radius=15)
        options_frame.pack(padx=50, pady=20)
        
        export_options = [
            ("📄 Generate PDF Report", self.export_pdf_report, "#4CAF50", 
             "Create a comprehensive PDF report of the current analysis"),
            ("📊 Export to Excel", self.export_excel_report, "#2196F3",
             "Export analysis data to Excel spreadsheet"),
            ("🖼️ Save Analysis Image", self.save_analysis_image, "#FF9800",
             "Save the analysis visualization as an image"),
            ("📁 Export JSON Data", self.export_json_data, "#9C27B0",
             "Export raw analysis data in JSON format")
        ]
        
        for text, command, color, description in export_options:
            option_frame = ctk.CTkFrame(options_frame, fg_color="#333333", corner_radius=10)
            option_frame.pack(fill="x", padx=20, pady=10)
            
            btn = ctk.CTkButton(
                option_frame,
                text=text,
                command=command,
                font=ctk.CTkFont(size=16, weight="bold"),
                height=50,
                corner_radius=8,
                fg_color=color,
                hover_color=color,
                anchor="w"
            )
            btn.pack(side="left", padx=15, pady=15)
            
            desc_label = ctk.CTkLabel(
                option_frame,
                text=description,
                font=ctk.CTkFont(size=12),
                text_color="#888888",
                anchor="w"
            )
            desc_label.pack(side="left", padx=(0, 15))
            
    def show_settings_view(self):
        """Show settings view"""
        self.clear_main_view()
        self.highlight_nav_button("⚙️ Settings")
        
        settings_container = ctk.CTkFrame(self.main_view, fg_color="#1a1a1a")
        settings_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        title = ctk.CTkLabel(
            settings_container,
            text="⚙️ Settings",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#ffffff"
        )
        title.pack(pady=(10, 30))
        
        # Settings options
        settings_frame = ctk.CTkScrollableFrame(settings_container, fg_color="#2a2a2a", corner_radius=15)
        settings_frame.pack(fill="both", expand=True, padx=50)
        
        # Appearance settings
        self.create_settings_section(settings_frame, "🎨 Appearance", [
            ("Theme", ["Dark", "Light", "System"], self.change_theme),
            ("Color Scheme", ["Green", "Blue", "Orange"], self.change_color_scheme)
        ])
        
        # Analysis settings
        self.create_settings_section(settings_frame, "🔬 Analysis", [
            ("AI Model", ["Gemini 2.0", "Gemini 1.5"], self.change_ai_model),
            ("Analysis Detail", ["Basic", "Standard", "Detailed"], self.change_analysis_detail)
        ])
        
        # Camera settings
        self.create_settings_section(settings_frame, "📷 Camera", [
            ("Default Camera", ["0", "1", "2"], self.change_camera),
            ("Image Quality", ["Low", "Medium", "High"], self.change_image_quality)
        ])
        
    def create_settings_section(self, parent, title, options):
        """Create a settings section"""
        section_frame = ctk.CTkFrame(parent, fg_color="#333333", corner_radius=10)
        section_frame.pack(fill="x", padx=20, pady=10)
        
        section_title = ctk.CTkLabel(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff"
        )
        section_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        for setting_name, choices, callback in options:
            setting_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
            setting_frame.pack(fill="x", padx=20, pady=10)
            
            label = ctk.CTkLabel(
                setting_frame,
                text=setting_name,
                font=ctk.CTkFont(size=14),
                text_color="#cccccc",
                width=150,
                anchor="w"
            )
            label.pack(side="left")
            
            option_menu = ctk.CTkOptionMenu(
                setting_frame,
                values=choices,
                command=callback,
                width=200,
                height=35,
                corner_radius=8,
                fg_color="#444444",
                button_color="#555555"
            )
            option_menu.pack(side="left", padx=20)
            
    def show_help_view(self):
        """Show help view"""
        self.clear_main_view()
        self.highlight_nav_button("❓ Help")
        
        help_container = ctk.CTkFrame(self.main_view, fg_color="#1a1a1a")
        help_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        title = ctk.CTkLabel(
            help_container,
            text="❓ Help & Guide",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#ffffff"
        )
        title.pack(pady=(10, 30))
        
        # Help content
        help_scroll = ctk.CTkScrollableFrame(help_container, fg_color="#2a2a2a", corner_radius=15)
        help_scroll.pack(fill="both", expand=True, padx=50)
        
        help_sections = [
            ("🚀 Getting Started", [
                "1. Click on 'Analysis' in the sidebar",
                "2. Load a fruit image using Camera, File, or URL",
                "3. Click 'Analyze Fruit' to perform analysis",
                "4. View results in different tabs"
            ]),
            ("📸 Best Practices for Photos", [
                "• Use good lighting - natural light works best",
                "• Place fruit on plain background",
                "• Capture the entire fruit in frame",
                "• Avoid blurry or out-of-focus images",
                "• Show any defects clearly"
            ]),
            ("📊 Understanding Results", [
                "• Green indicators = Good quality",
                "• Yellow indicators = Fair quality, monitor",
                "• Red indicators = Poor quality, take action",
                "• Check all tabs for complete analysis"
            ]),
            ("💡 Tips for Storage", [
                "• Store different fruits separately",
                "• Maintain proper temperature",
                "• Check fruits regularly",
                "• Remove damaged fruits immediately",
                "• Follow AI recommendations"
            ])
        ]
        
        for section_title, content in help_sections:
            section_frame = ctk.CTkFrame(help_scroll, fg_color="#333333", corner_radius=10)
            section_frame.pack(fill="x", padx=20, pady=10)
            
            title_label = ctk.CTkLabel(
                section_frame,
                text=section_title,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#ffffff"
            )
            title_label.pack(anchor="w", padx=20, pady=(15, 10))
            
            for item in content:
                item_label = ctk.CTkLabel(
                    section_frame,
                    text=item,
                    font=ctk.CTkFont(size=13),
                    text_color="#cccccc",
                    anchor="w",
                    justify="left"
                )
                item_label.pack(anchor="w", padx=30, pady=3)
                
            section_frame.pack(pady=(0, 5))
            
    def highlight_nav_button(self, button_text):
        """Highlight the active navigation button"""
        for text, btn in self.nav_buttons.items():
            if text == button_text:
                btn.configure(fg_color="#3a3a3a", text_color="#4CAF50")
            else:
                btn.configure(fg_color="#2a2a2a", text_color="#ffffff")
                
    # Quick action methods
    def quick_camera_capture(self):
        """Quick camera capture"""
        self.show_analysis_view()
        self.capture_from_camera()
        
    def quick_load_file(self):
        """Quick load file"""
        self.show_analysis_view()
        self.load_from_file()
        
    def quick_export(self):
        """Quick export"""
        if self.current_result:
            self.save_analysis_image()
        else:
            self.show_notification("⚠️ No analysis to export", "warning")
            
    # Image handling methods
    def capture_from_camera(self):
        """Capture image from camera"""
        camera_window = ctk.CTkToplevel(self.root)
        camera_window.title("📷 Capture Fruit Image")
        camera_window.geometry("800x600")
        camera_window.transient(self.root)
        
        # Camera frame
        camera_frame = ctk.CTkFrame(camera_window, fg_color="#1a1a1a")
        camera_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Instructions
        instructions = ctk.CTkLabel(
            camera_frame,
            text="Position the fruit in the center and press SPACE or click CAPTURE",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4CAF50"
        )
        instructions.pack(pady=15)
        
        # Video canvas
        self.video_canvas = tk.Canvas(camera_frame, bg="#000000", highlightthickness=0)
        self.video_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Controls
        control_frame = ctk.CTkFrame(camera_frame, fg_color="#2a2a2a", corner_radius=10)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Capture button
        capture_btn = ctk.CTkButton(
            control_frame,
            text="📸 CAPTURE (SPACE)",
            command=self.capture_camera_image,
            font=ctk.CTkFont(size=18, weight="bold"),
            height=50,
            fg_color="#4CAF50",
            hover_color="#45a049",
            corner_radius=25
        )
        capture_btn.pack(pady=15)
        
        # Initialize camera
        self.camera_active = True
        self.camera_window = camera_window
        self.frame_queue = queue.Queue(maxsize=2)
        
        # Bind keys
        camera_window.bind('<space>', lambda e: self.capture_camera_image())
        
        # Start camera thread
        camera_thread = threading.Thread(target=self.camera_worker, daemon=True)
        camera_thread.start()
        
        # Start display update
        self.update_camera_display()
        
        # Handle close
        def on_close():
            self.camera_active = False
            camera_window.destroy()
            
        camera_window.protocol("WM_DELETE_WINDOW", on_close)
        
    def camera_worker(self):
        """Camera worker thread"""
        cap = None
        try:
            if os.name == 'nt':
                cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(0)
                
            if not cap.isOpened():
                return
                
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            while self.camera_active:
                ret, frame = cap.read()
                if ret:
                    # Add overlay
                    frame = self.add_camera_overlay(frame)
                    self.current_frame = frame
                    
                    try:
                        self.frame_queue.put_nowait(frame)
                    except queue.Full:
                        pass
                        
                time.sleep(0.03)
                
        finally:
            if cap:
                cap.release()
                
    def update_camera_display(self):
        """Update camera display"""
        if not self.camera_active or not hasattr(self, 'camera_window'):
            return
            
        try:
            frame = None
            while not self.frame_queue.empty():
                frame = self.frame_queue.get_nowait()
                
            if frame is not None:
                # Convert to PIL
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                
                # Resize to fit canvas
                canvas_width = self.video_canvas.winfo_width()
                canvas_height = self.video_canvas.winfo_height()
                
                if canvas_width > 1 and canvas_height > 1:
                    img = img.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
                    
                # Display
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_canvas.delete("all")
                self.video_canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
                self.video_canvas.image = imgtk
                
        except Exception as e:
            print(f"Display error: {e}")
            
        if self.camera_active:
            self.root.after(30, self.update_camera_display)
            
    def add_camera_overlay(self, frame):
        """Add overlay to camera frame"""
        height, width = frame.shape[:2]
        overlay = frame.copy()
        
        # Center circle
        center_x, center_y = width // 2, height // 2
        cv2.circle(overlay, (center_x, center_y), 100, (0, 255, 0), 3)
        
        # Corner brackets
        bracket_size = 40
        bracket_thickness = 3
        corners = [
            (50, 50), (width-50, 50),
            (50, height-50), (width-50, height-50)
        ]
        
        for i, (x, y) in enumerate(corners):
            if i == 0:  # Top-left
                cv2.line(overlay, (x, y), (x+bracket_size, y), (0, 255, 0), bracket_thickness)
                cv2.line(overlay, (x, y), (x, y+bracket_size), (0, 255, 0), bracket_thickness)
            elif i == 1:  # Top-right
                cv2.line(overlay, (x, y), (x-bracket_size, y), (0, 255, 0), bracket_thickness)
                cv2.line(overlay, (x, y), (x, y+bracket_size), (0, 255, 0), bracket_thickness)
            elif i == 2:  # Bottom-left
                cv2.line(overlay, (x, y), (x+bracket_size, y), (0, 255, 0), bracket_thickness)
                cv2.line(overlay, (x, y), (x, y-bracket_size), (0, 255, 0), bracket_thickness)
            else:  # Bottom-right
                cv2.line(overlay, (x, y), (x-bracket_size, y), (0, 255, 0), bracket_thickness)
                cv2.line(overlay, (x, y), (x, y-bracket_size), (0, 255, 0), bracket_thickness)
                
        # Blend
        return cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
        
    def capture_camera_image(self):
        """Capture current camera frame"""
        if hasattr(self, 'current_frame'):
            self.current_image_cv2 = self.current_frame.copy()
            self.camera_active = False
            
            if hasattr(self, 'camera_window'):
                self.camera_window.destroy()
                
            # Display captured image
            self.display_image_in_analysis(self.current_image_cv2)
            self.analyze_button.configure(state="normal")
            self.show_notification("✅ Image captured successfully!", "success")
            
    def load_from_file(self):
        """Load image from file"""
        file_path = filedialog.askopenfilename(
            title="Select Fruit Image",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            try:
                image = cv2.imread(file_path)
                if image is not None:
                    self.current_image_cv2 = image
                    self.display_image_in_analysis(image)
                    self.analyze_button.configure(state="normal")
                    self.show_notification("✅ Image loaded successfully!", "success")
                else:
                    self.show_notification("❌ Failed to load image", "error")
            except Exception as e:
                self.show_notification(f"❌ Error: {str(e)}", "error")
                
    def load_from_url(self):
        """Load image from URL"""
        dialog = ctk.CTkInputDialog(
            text="Enter image URL:",
            title="Load Image from URL"
        )
        url = dialog.get_input()
        
        if url:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    
                    if image is not None:
                        self.current_image_cv2 = image
                        self.display_image_in_analysis(image)
                        self.analyze_button.configure(state="normal")
                        self.show_notification("✅ Image loaded from URL!", "success")
                    else:
                        self.show_notification("❌ Could not decode image", "error")
                else:
                    self.show_notification(f"❌ Failed to download: {response.status_code}", "error")
            except Exception as e:
                self.show_notification(f"❌ Error: {str(e)}", "error")
                
    def clear_image(self):
        """Clear current image"""
        self.current_image_cv2 = None
        self.current_result = None
        
        # Reset image display
        self.image_label.configure(
            image=None,
            text="📷 No Image Loaded\n\nClick buttons below to load an image"
        )
        
        # Clear quick info
        for widget in self.quick_info_frame.winfo_children():
            widget.destroy()
            
        self.no_info_label = ctk.CTkLabel(
            self.quick_info_frame,
            text="Load an image and click\n'Analyze' to see results",
            font=ctk.CTkFont(size=14),
            text_color="#666666"
        )
        self.no_info_label.pack(expand=True)
        
        # Clear detailed results
        self.clear_all_result_tabs()
        
        # Disable analyze button
        self.analyze_button.configure(state="disabled")
        
    def display_image_in_analysis(self, cv2_image):
        """Display image in analysis view"""
        # Convert to PIL
        image_rgb = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        
        # Calculate display size
        max_width = 450
        max_height = 350
        
        # Resize maintaining aspect ratio
        pil_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(pil_image)
        
        # Update label
        self.image_label.configure(image=photo, text="")
        self.image_label.image = photo
        
    def analyze_current_image(self):
        """Analyze the current image and store for comparison"""
        if self.current_image_cv2 is None:
            self.show_notification("⚠️ No image to analyze", "warning")
            return
            
        # Store current as last analysis before analyzing new
        if self.current_result is not None:
            self.last_analysis_image = self.current_image_cv2.copy()
            self.last_analysis_result = self.current_result
            
        # Update UI
        self.analyze_button.configure(state="disabled", text="🔄 ANALYZING...")
        self.update_status("🔄 Performing analysis...")
        
        # Clear previous results
        self.clear_all_result_tabs()
        
        # Show progress in quick info
        for widget in self.quick_info_frame.winfo_children():
            widget.destroy()
            
        progress_label = ctk.CTkLabel(
            self.quick_info_frame,
            text="🔬 Analyzing fruit...",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4CAF50"
        )
        progress_label.pack(pady=20)
        
        progress_bar = ctk.CTkProgressBar(
            self.quick_info_frame,
            width=250,
            height=20,
            corner_radius=10,
            progress_color="#4CAF50"
        )
        progress_bar.pack(pady=10)
        progress_bar.set(0)
        
        # Perform analysis in thread
        def analysis_thread():
            try:
                # Update progress
                self.root.after(0, lambda: progress_bar.set(0.3))
                self.root.after(0, lambda: progress_label.configure(text="🔍 Analyzing visual features..."))
                
                # Perform analysis
                result = self.perform_fruit_analysis(self.current_image_cv2)
                self.current_result = result
                
                # Add to history
                result.timestamp = datetime.now()
                result.image = self.current_image_cv2.copy()
                self.analysis_history.append(result)
                
                # Update UI
                self.root.after(0, lambda: progress_bar.set(1.0))
                self.root.after(0, lambda: progress_label.configure(text="✅ Analysis complete!"))
                
                # Display results
                self.root.after(500, lambda: self.display_analysis_results(result))
                
            except Exception as e:
                self.root.after(0, lambda: self.show_notification(f"❌ Analysis failed: {str(e)}", "error"))
            finally:
                self.root.after(0, lambda: self.analyze_button.configure(
                    state="normal",
                    text="🔬 ANALYZE FRUIT"
                ))
                self.root.after(0, lambda: self.update_status("● System Ready"))
                
        thread = threading.Thread(target=analysis_thread, daemon=True)
        thread.start()
        
    def display_analysis_results(self, result):
        """Display analysis results in UI - ensuring all tabs have data"""
        # Update quick info
        self.display_quick_info(result)
        
        # Update detailed tabs - make sure all show data
        self.display_condition_details(result)
        self.display_health_details(result)
        self.display_metrics_details(result)
        self.display_recommendations_with_data(result)  # Enhanced method
        self.display_technical_data_with_info(result)   # Enhanced method
        
        # Show notification
        if 'BAD' in result.condition or 'POOR' in result.condition:
            self.show_notification("⚠️ Poor quality detected - take action!", "error")
        elif 'EXCELLENT' in result.condition or 'GOOD' in result.condition:
            self.show_notification("✅ Good quality fruit detected!", "success")
        else:
            self.show_notification("📊 Analysis complete - check results", "info")
            
    def display_quick_info(self, result):
        """Display quick info summary"""
        # Clear frame
        for widget in self.quick_info_frame.winfo_children():
            widget.destroy()
            
        # Condition card
        condition_color = self.get_condition_color(result.condition)
        condition_card = ctk.CTkFrame(
            self.quick_info_frame,
            fg_color=condition_color,
            corner_radius=15
        )
        condition_card.pack(fill="x", padx=10, pady=(10, 15))
        
        condition_text = result.condition.split(' - ')[0]
        condition_label = ctk.CTkLabel(
            condition_card,
            text=condition_text,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#ffffff"
        )
        condition_label.pack(pady=15)
        
        # Key metrics
        metrics_frame = ctk.CTkFrame(self.quick_info_frame, fg_color="#333333", corner_radius=10)
        metrics_frame.pack(fill="x", padx=10, pady=5)
        
        metrics = [
            ("🍎 Type", result.fruit_type),
            ("💯 Confidence", f"{result.confidence:.0f}%"),
            ("🌟 Freshness", f"{result.freshness_score:.0f}%"),
            ("🏥 Safety", result.safety)
        ]
        
        for label, value in metrics:
            metric_frame = ctk.CTkFrame(metrics_frame, fg_color="transparent")
            metric_frame.pack(fill="x", padx=15, pady=5)
            
            label_widget = ctk.CTkLabel(
                metric_frame,
                text=f"{label}:",
                font=ctk.CTkFont(size=12),
                text_color="#888888",
                width=100,
                anchor="w"
            )
            label_widget.pack(side="left")
            
            value_widget = ctk.CTkLabel(
                metric_frame,
                text=value,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#ffffff",
                anchor="w"
            )
            value_widget.pack(side="left")
            
        # Action required
        if 'discard' in result.action_required.lower() or 'immediately' in result.action_required.lower():
            action_card = ctk.CTkFrame(
                self.quick_info_frame,
                fg_color="#f44336",
                corner_radius=10
            )
            action_card.pack(fill="x", padx=10, pady=10)
            
            action_label = ctk.CTkLabel(
                action_card,
                text=f"⚠️ {result.action_required}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#ffffff",
                wraplength=300
            )
            action_label.pack(pady=10)
            
    def display_condition_details(self, result):
        """Display detailed condition information"""
        # Clear content
        for widget in self.condition_content.winfo_children():
            widget.destroy()
            
        # Main condition
        main_frame = ctk.CTkFrame(self.condition_content, fg_color="#333333", corner_radius=10)
        main_frame.pack(fill="x", padx=10, pady=10)
        
        condition_color = self.get_condition_color(result.condition)
        
        # Condition header
        header_frame = ctk.CTkFrame(main_frame, fg_color=condition_color, corner_radius=10)
        header_frame.pack(fill="x", padx=15, pady=15)
        
        condition_label = ctk.CTkLabel(
            header_frame,
            text=result.condition,
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#ffffff"
        )
        condition_label.pack(pady=20)
        
        # Confidence meter
        confidence_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        confidence_frame.pack(pady=15)
        
        conf_label = ctk.CTkLabel(
            confidence_frame,
            text="AI Confidence Score",
            font=ctk.CTkFont(size=14),
            text_color="#888888"
        )
        conf_label.pack()
        
        # Progress bar style confidence
        conf_bar = ctk.CTkProgressBar(
            confidence_frame,
            width=300,
            height=30,
            corner_radius=15,
            progress_color=condition_color
        )
        conf_bar.pack(pady=10)
        conf_bar.set(result.confidence / 100)
        
        conf_percent = ctk.CTkLabel(
            confidence_frame,
            text=f"{result.confidence:.0f}%",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=condition_color
        )
        conf_percent.pack()
        
        # Details
        details_frame = ctk.CTkFrame(main_frame, fg_color="#444444", corner_radius=10)
        details_frame.pack(fill="x", padx=15, pady=15)
        
        details = [
            ("Fruit Type", result.fruit_type),
            ("Ripeness", result.ripeness),
            ("Primary Assessment", result.safety),
            ("Action Required", result.action_required)
        ]
        
        for label, value in details:
            detail_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
            detail_frame.pack(fill="x", padx=20, pady=8)
            
            label_widget = ctk.CTkLabel(
                detail_frame,
                text=f"{label}:",
                font=ctk.CTkFont(size=14),
                text_color="#888888",
                width=150,
                anchor="w"
            )
            label_widget.pack(side="left")
            
            value_widget = ctk.CTkLabel(
                detail_frame,
                text=str(value),
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#ffffff",
                anchor="w"
            )
            value_widget.pack(side="left", padx=20)
            
        # Detailed analysis text
        if result.detailed_analysis:
            analysis_frame = ctk.CTkFrame(main_frame, fg_color="#444444", corner_radius=10)
            analysis_frame.pack(fill="x", padx=15, pady=15)
            
            analysis_title = ctk.CTkLabel(
                analysis_frame,
                text="📝 Detailed Analysis",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#ffffff"
            )
            analysis_title.pack(anchor="w", padx=15, pady=(10, 5))
            
            analysis_text = ctk.CTkLabel(
                analysis_frame,
                text=result.detailed_analysis,
                font=ctk.CTkFont(size=12),
                text_color="#cccccc",
                wraplength=600,
                anchor="w",
                justify="left"
            )
            analysis_text.pack(anchor="w", padx=15, pady=(0, 10))
            
    def display_health_details(self, result):
        """Display health and disease information"""
        # Clear content
        for widget in self.health_content.winfo_children():
            widget.destroy()
            
        # Disease detection
        if result.defects:
            disease_frame = ctk.CTkFrame(self.health_content, fg_color="#3a1515", corner_radius=10)
            disease_frame.pack(fill="x", padx=10, pady=10)
            
            disease_title = ctk.CTkLabel(
                disease_frame,
                text="🦠 Detected Issues",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="#ff6666"
            )
            disease_title.pack(pady=(15, 10))
            
            for defect in result.defects:
                defect_item = ctk.CTkFrame(disease_frame, fg_color="#4a2525", corner_radius=8)
                defect_item.pack(fill="x", padx=15, pady=5)
                
                defect_label = ctk.CTkLabel(
                    defect_item,
                    text=f"⚠️ {defect}",
                    font=ctk.CTkFont(size=14),
                    text_color="#ffaaaa",
                    wraplength=500,
                    anchor="w",
                    justify="left"
                )
                defect_label.pack(anchor="w", padx=15, pady=10)
        else:
            healthy_frame = ctk.CTkFrame(self.health_content, fg_color="#153a15", corner_radius=10)
            healthy_frame.pack(fill="x", padx=10, pady=10)
            
            healthy_label = ctk.CTkLabel(
                healthy_frame,
                text="✅ No significant health issues detected",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#66ff66"
            )
            healthy_label.pack(pady=30)
            
        # Disease identification
        if result.disease_identification and result.disease_identification != "None detected":
            disease_id_frame = ctk.CTkFrame(self.health_content, fg_color="#333333", corner_radius=10)
            disease_id_frame.pack(fill="x", padx=10, pady=10)
            
            id_title = ctk.CTkLabel(
                disease_id_frame,
                text="🔬 Disease Identification",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#ffffff"
            )
            id_title.pack(pady=(15, 10))
            
            id_label = ctk.CTkLabel(
                disease_id_frame,
                text=result.disease_identification,
                font=ctk.CTkFont(size=14),
                text_color="#ff9800",
                wraplength=500
            )
            id_label.pack(pady=(0, 15))
            
        # Safety assessment
        safety_frame = ctk.CTkFrame(self.health_content, fg_color="#333333", corner_radius=10)
        safety_frame.pack(fill="x", padx=10, pady=10)
        
        safety_title = ctk.CTkLabel(
            safety_frame,
            text="🏥 Safety Assessment",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff"
        )
        safety_title.pack(pady=(15, 10))
        
        # Safety indicator
        if "unsafe" in result.safety.lower():
            safety_color = "#ff0000"
            safety_icon = "🚫"
            safety_bg = "#3a1515"
        elif "questionable" in result.safety.lower():
            safety_color = "#ff9800"
            safety_icon = "⚠️"
            safety_bg = "#3a2a15"
        else:
            safety_color = "#00ff00"
            safety_icon = "✅"
            safety_bg = "#153a15"
            
        safety_indicator = ctk.CTkFrame(safety_frame, fg_color=safety_bg, corner_radius=10)
        safety_indicator.pack(padx=15, pady=(0, 15))
        
        safety_text = ctk.CTkLabel(
            safety_indicator,
            text=f"{safety_icon} {result.safety.upper()}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=safety_color
        )
        safety_text.pack(pady=20, padx=30)
        
        # Key observations
        if result.key_observations:
            obs_frame = ctk.CTkFrame(self.health_content, fg_color="#333333", corner_radius=10)
            obs_frame.pack(fill="x", padx=10, pady=10)
            
            obs_title = ctk.CTkLabel(
                obs_frame,
                text="🔍 Key Observations",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#ffffff"
            )
            obs_title.pack(pady=(15, 10))
            
            for obs in result.key_observations[:5]:
                obs_item = ctk.CTkFrame(obs_frame, fg_color="#444444", corner_radius=6)
                obs_item.pack(fill="x", padx=15, pady=3)
                
                obs_label = ctk.CTkLabel(
                    obs_item,
                    text=f"• {obs}",
                    font=ctk.CTkFont(size=12),
                    text_color="#cccccc",
                    wraplength=500,
                    anchor="w",
                    justify="left"
                )
                obs_label.pack(anchor="w", padx=10, pady=5)
                
    def display_metrics_details(self, result):
        """Display quality metrics"""
        # Clear content
        for widget in self.metrics_content.winfo_children():
            widget.destroy()
            
        # Create metrics dashboard
        dashboard_frame = ctk.CTkFrame(self.metrics_content, fg_color="#333333", corner_radius=10)
        dashboard_frame.pack(fill="x", padx=10, pady=10)
        
        dashboard_title = ctk.CTkLabel(
            dashboard_frame,
            text="📊 Quality Metrics Dashboard",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        )
        dashboard_title.pack(pady=(15, 20))
        
        # Metrics grid
        metrics_grid = ctk.CTkFrame(dashboard_frame, fg_color="transparent")
        metrics_grid.pack(padx=20, pady=(0, 20))
        
        metrics = [
            ("🌟 Freshness Score", result.freshness_score, "%", 
             "#00ff00" if result.freshness_score > 75 else "#ff9800" if result.freshness_score > 50 else "#ff0000"),
            ("🦠 Decay Level", result.local_metrics['brown_rot_percentage'], "%",
             "#00ff00" if result.local_metrics['brown_rot_percentage'] < 5 else "#ff9800" if result.local_metrics['brown_rot_percentage'] < 15 else "#ff0000"),
            ("⚫ Black Spots", result.local_metrics['black_spots_percentage'], "%",
             "#00ff00" if result.local_metrics['black_spots_percentage'] < 2 else "#ff9800" if result.local_metrics['black_spots_percentage'] < 10 else "#ff0000"),
            ("🔄 Shape Integrity", result.local_metrics['shape_integrity'], "%",
             "#00ff00" if result.local_metrics['shape_integrity'] > 80 else "#ff9800" if result.local_metrics['shape_integrity'] > 60 else "#ff0000"),
            ("🎨 Color Variance", result.local_metrics['color_variance'], "",
             "#00ff00" if result.local_metrics['color_variance'] < 20 else "#ff9800" if result.local_metrics['color_variance'] < 40 else "#ff0000"),
            ("🖼️ Texture Score", result.local_metrics['texture_score'], "",
             "#00ff00" if result.local_metrics['texture_score'] < 30 else "#ff9800" if result.local_metrics['texture_score'] < 60 else "#ff0000")
        ]
        
        for i, (name, value, unit, color) in enumerate(metrics):
            metric_card = ctk.CTkFrame(metrics_grid, fg_color="#444444", corner_radius=10)
            metric_card.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            
            # Metric name
            name_label = ctk.CTkLabel(
                metric_card,
                text=name,
                font=ctk.CTkFont(size=14),
                text_color="#cccccc"
            )
            name_label.pack(pady=(15, 5))
            
            # Metric value
            value_label = ctk.CTkLabel(
                metric_card,
                text=f"{value:.1f}{unit}",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=color
            )
            value_label.pack(pady=(0, 5))
            
            # Progress bar
            if unit == "%":
                progress = ctk.CTkProgressBar(
                    metric_card,
                    width=150,
                    height=10,
                    corner_radius=5,
                    progress_color=color
                )
                progress.pack(pady=(0, 15))
                progress.set(value / 100)
                
        # Configure grid weights
        metrics_grid.grid_columnconfigure(0, weight=1)
        metrics_grid.grid_columnconfigure(1, weight=1)
        
        # Visualization
        viz_frame = ctk.CTkFrame(self.metrics_content, fg_color="#333333", corner_radius=10)
        viz_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        viz_title = ctk.CTkLabel(
            viz_frame,
            text="📈 Metrics Visualization",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff"
        )
        viz_title.pack(pady=(15, 10))
        
        # Create matplotlib figure
        fig = plt.Figure(figsize=(8, 4), facecolor='#333333')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#333333')
        
        # Radar chart
        categories = ['Freshness', 'No Decay', 'No Spots', 'Shape', 'Color Unity', 'Texture']
        values = [
            result.freshness_score,
            100 - result.local_metrics['brown_rot_percentage'],
            100 - result.local_metrics['black_spots_percentage'],
            result.local_metrics['shape_integrity'],
            100 - min(result.local_metrics['color_variance'], 100),
            100 - min(result.local_metrics['texture_score'], 100)
        ]
        
        # Plot
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False)
        values = np.array(values)
        angles = np.concatenate((angles, [angles[0]]))
        values = np.concatenate((values, [values[0]]))
        
        ax.plot(angles, values, 'o-', linewidth=2, color='#4CAF50')
        ax.fill(angles, values, alpha=0.25, color='#4CAF50')
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, color='white', size=10)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], color='white', size=8)
        ax.grid(True, color='#555555', linestyle='--', alpha=0.5)
        ax.spines['polar'].set_color('#555555')
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=viz_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
    def display_recommendations_with_data(self, result):
        """Display recommendations with real data"""
        # Clear content
        for widget in self.recommendations_content.winfo_children():
            widget.destroy()
            
        # Always create recommendations based on condition
        recommendations = self.generate_recommendations(result)
        
        # Action required
        action_frame = ctk.CTkFrame(
            self.recommendations_content,
            fg_color="#ff6347" if "discard" in result.action_required.lower() else "#444444",
            corner_radius=10
        )
        action_frame.pack(fill="x", padx=10, pady=10)
        
        action_title = ctk.CTkLabel(
            action_frame,
            text="🚨 Immediate Action Required",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        )
        action_title.pack(pady=(15, 10))
        
        action_text = ctk.CTkLabel(
            action_frame,
            text=result.action_required.upper(),
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff",
            wraplength=600
        )
        action_text.pack(pady=(0, 15))
        
        # Prevention tips
        tips_frame = ctk.CTkFrame(self.recommendations_content, fg_color="#1a3a1a", corner_radius=10)
        tips_frame.pack(fill="x", padx=10, pady=10)
        
        tips_title = ctk.CTkLabel(
            tips_frame,
            text="💡 Prevention Tips",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#4CAF50"
        )
        tips_title.pack(pady=(15, 10))
        
        # Use provided tips or generate
        prevention_tips = result.prevention_tips if result.prevention_tips else recommendations['prevention_tips']
        
        for i, tip in enumerate(prevention_tips[:5], 1):
            tip_item = ctk.CTkFrame(tips_frame, fg_color="#2a4a2a", corner_radius=8)
            tip_item.pack(fill="x", padx=15, pady=5)
            
            tip_text = ctk.CTkLabel(
                tip_item,
                text=f"{i}. {tip}",
                font=ctk.CTkFont(size=14),
                text_color="#aaffaa",
                wraplength=550,
                anchor="w",
                justify="left"
            )
            tip_text.pack(anchor="w", padx=15, pady=10)
            
        # Storage advice
        storage_frame = ctk.CTkFrame(self.recommendations_content, fg_color="#333333", corner_radius=10)
        storage_frame.pack(fill="x", padx=10, pady=10)
        
        storage_title = ctk.CTkLabel(
            storage_frame,
            text="📦 Storage Recommendations",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff"
        )
        storage_title.pack(pady=(15, 10))
        
        storage_text = ctk.CTkLabel(
            storage_frame,
            text=result.storage_advice if result.storage_advice else recommendations['storage_advice'],
            font=ctk.CTkFont(size=14),
            text_color="#cccccc",
            wraplength=600,
            justify="left"
        )
        storage_text.pack(padx=20, pady=(0, 15))
        
        # Treatment options
        treatment_options = result.treatment_options if result.treatment_options else recommendations['treatment_options']
        if treatment_options:
            treatment_frame = ctk.CTkFrame(self.recommendations_content, fg_color="#3a3a2a", corner_radius=10)
            treatment_frame.pack(fill="x", padx=10, pady=10)
            
            treatment_title = ctk.CTkLabel(
                treatment_frame,
                text="🏥 Treatment Options",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#FFA500"
            )
            treatment_title.pack(pady=(15, 10))
            
            for treatment in treatment_options:
                treat_label = ctk.CTkLabel(
                    treatment_frame,
                    text=f"→ {treatment}",
                    font=ctk.CTkFont(size=13),
                    text_color="#FFD700",
                    anchor="w",
                    wraplength=550
                )
                treat_label.pack(anchor="w", padx=30, pady=3)
                
            treatment_frame.pack(pady=(0, 10))
            
        # Best practices
        practices_frame = ctk.CTkFrame(self.recommendations_content, fg_color="#2a2a3a", corner_radius=10)
        practices_frame.pack(fill="x", padx=10, pady=10)
        
        practices_title = ctk.CTkLabel(
            practices_frame,
            text="📚 Best Practices",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#9C27B0"
        )
        practices_title.pack(pady=(15, 10))
        
        practices = recommendations['best_practices']
        
        for practice in practices:
            practice_label = ctk.CTkLabel(
                practices_frame,
                text=f"✓ {practice}",
                font=ctk.CTkFont(size=13),
                text_color="#E1BEE7",
                anchor="w",
                wraplength=550
            )
            practice_label.pack(anchor="w", padx=30, pady=3)
            
        practices_frame.pack(pady=(0, 10))
        
    def generate_recommendations(self, result):
        """Generate comprehensive recommendations based on result"""
        condition = result.condition
        
        # Default recommendations for each condition
        recommendations = {
            'prevention_tips': [],
            'storage_advice': '',
            'treatment_options': [],
            'best_practices': []
        }
        
        if 'EXCELLENT' in condition:
            recommendations['prevention_tips'] = [
                "Continue current storage practices",
                "Maintain stable temperature (32-35°F for most fruits)",
                "Keep humidity levels appropriate for fruit type",
                "Check regularly to maintain quality",
                "Handle gently to prevent bruising"
            ]
            recommendations['storage_advice'] = "Store in cool, dry place with good ventilation. This fruit is in excellent condition and should maintain quality for optimal time."
            recommendations['best_practices'] = [
                "Use within optimal timeframe for best taste",
                "Keep away from ethylene-producing fruits",
                "Monitor temperature regularly"
            ]
            
        elif 'GOOD' in condition:
            recommendations['prevention_tips'] = [
                "Monitor daily for any changes",
                "Ensure proper air circulation",
                "Keep away from damaged fruits",
                "Maintain consistent temperature",
                "Use within recommended timeframe"
            ]
            recommendations['storage_advice'] = "Store in refrigerator crisper drawer or cool pantry. Good quality fruit that will last several days with proper care."
            recommendations['best_practices'] = [
                "Check daily for quality changes",
                "Consume within 3-5 days",
                "Separate from overripe fruits"
            ]
            
        elif 'FAIR' in condition:
            recommendations['prevention_tips'] = [
                "Use within 2-3 days maximum",
                "Store separately from other fruits",
                "Check twice daily for deterioration",
                "Consider refrigeration if not already",
                "Remove any developing bad spots"
            ]
            recommendations['storage_advice'] = "Requires immediate attention. Store in refrigerator and use soon. Quality is declining."
            recommendations['treatment_options'] = [
                "Cut away any affected areas before use",
                "Consider cooking or processing",
                "Make juice or smoothies if too soft"
            ]
            recommendations['best_practices'] = [
                "Use in cooked dishes if raw quality declining",
                "Process into preserves or sauces",
                "Freeze for later use in smoothies"
            ]
            
        elif 'POOR' in condition:
            recommendations['prevention_tips'] = [
                "Use immediately or discard",
                "Isolate from healthy fruits",
                "Clean storage area after removal",
                "Review storage practices",
                "Buy smaller quantities in future"
            ]
            recommendations['storage_advice'] = "Do not store. Use immediately if safe or discard. Risk of spreading to other fruits."
            recommendations['treatment_options'] = [
                "Cut away all affected areas generously",
                "Cook thoroughly if using",
                "Consider composting if too damaged"
            ]
            recommendations['best_practices'] = [
                "Inspect all nearby fruits",
                "Sanitize storage area",
                "Adjust buying habits"
            ]
            
        else:  # BAD or INSECT_DAMAGED
            recommendations['prevention_tips'] = [
                "Discard immediately in sealed bag",
                "Clean and sanitize storage area",
                "Check all other stored fruits",
                "Improve storage conditions",
                "Consider pest control if needed"
            ]
            recommendations['storage_advice'] = "DO NOT STORE OR CONSUME. Dispose of immediately to prevent contamination."
            recommendations['treatment_options'] = [
                "Dispose in compost or sealed trash",
                "Do not attempt to salvage",
                "Clean area thoroughly with disinfectant"
            ]
            recommendations['best_practices'] = [
                "Inspect storage area for pests",
                "Review and improve storage methods",
                "Purchase from different source"
            ]
            
        return recommendations
        
    def display_technical_data_with_info(self, result):
        """Display technical data with comprehensive information"""
        # Clear content
        for widget in self.technical_content.winfo_children():
            widget.destroy()
            
        # Analysis summary
        summary_frame = ctk.CTkFrame(self.technical_content, fg_color="#333333", corner_radius=10)
        summary_frame.pack(fill="x", padx=10, pady=10)
        
        summary_title = ctk.CTkLabel(
            summary_frame,
            text="📊 Analysis Summary",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        )
        summary_title.pack(pady=(15, 10))
        
        # Summary data
        summary_data = [
            ("Analysis Timestamp", result.timestamp.strftime("%Y-%m-%d %H:%M:%S") if result.timestamp else datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("Primary Data Source", "AI Analysis" if result.ai_analysis else "Computer Vision"),
            ("Total Defects Found", str(len(result.defects))),
            ("Overall Quality Score", f"{result.freshness_score:.1f}/100"),
            ("Analysis Confidence", f"{result.confidence:.1f}%"),
            ("Fruit Category", result.fruit_type)
        ]
        
        for label, value in summary_data:
            sum_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
            sum_frame.pack(fill="x", padx=20, pady=3)
            
            sum_label = ctk.CTkLabel(
                sum_frame,
                text=f"{label}:",
                font=ctk.CTkFont(size=13),
                text_color="#888888",
                width=200,
                anchor="w"
            )
            sum_label.pack(side="left")
            
            sum_value = ctk.CTkLabel(
                sum_frame,
                text=value,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#ffffff",
                anchor="w"
            )
            sum_value.pack(side="left", padx=20)
            
        # Raw data frame
        data_frame = ctk.CTkFrame(self.technical_content, fg_color="#333333", corner_radius=10)
        data_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        data_title = ctk.CTkLabel(
            data_frame,
            text="📄 Complete Technical Data",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff"
        )
        data_title.pack(pady=(15, 10))
        
        # Create scrollable text widget for JSON data
        json_frame = ctk.CTkTextbox(
            data_frame,
            fg_color="#222222",
            corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=12),
            height=400
        )
        json_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Generate comprehensive technical data
        technical_data = self.generate_technical_data(result)
        
        # Format as JSON
        json_text = json.dumps(technical_data, indent=2)
        json_frame.insert("1.0", json_text)
        json_frame.configure(state="disabled")
        
        # Export buttons
        export_frame = ctk.CTkFrame(data_frame, fg_color="transparent")
        export_frame.pack(pady=(0, 15))
        
        export_json_btn = ctk.CTkButton(
            export_frame,
            text="📥 Export as JSON",
            command=lambda: self.export_technical_data(technical_data, "json"),
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35,
            corner_radius=8,
            fg_color="#2196F3"
        )
        export_json_btn.pack(side="left", padx=5)
        
        export_csv_btn = ctk.CTkButton(
            export_frame,
            text="📊 Export as CSV",
            command=lambda: self.export_technical_data(technical_data, "csv"),
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35,
            corner_radius=8,
            fg_color="#4CAF50"
        )
        export_csv_btn.pack(side="left", padx=5)
        
    def generate_technical_data(self, result):
        """Generate comprehensive technical data"""
        return {
            "analysis_metadata": {
                "timestamp": result.timestamp.isoformat() if result.timestamp else datetime.now().isoformat(),
                "analyzer_version": "2.0",
                "confidence_score": result.confidence,
                "analysis_method": "AI + Computer Vision Hybrid"
            },
            "fruit_identification": {
                "type": result.fruit_type,
                "condition": result.condition,
                "ripeness": result.ripeness,
                "variety": "Standard" if result.fruit_type != "Unknown" else "Unknown"
            },
            "health_assessment": {
                "safety": result.safety,
                "defects_found": result.defects if result.defects else ["None detected"],
                "disease_identification": result.disease_identification,
                "severity_level": self.calculate_severity(result)
            },
            "quality_metrics": {
                "freshness_score": result.freshness_score,
                "brown_rot_percentage": result.local_metrics['brown_rot_percentage'],
                "black_spots_percentage": result.local_metrics['black_spots_percentage'],
                "shape_integrity": result.local_metrics['shape_integrity'],
                "color_variance": result.local_metrics['color_variance'],
                "texture_score": result.local_metrics['texture_score'],
                "overall_quality": self.calculate_overall_quality(result)
            },
            "recommendations": {
                "action_required": result.action_required,
                "storage_advice": result.storage_advice,
                "prevention_tips": result.prevention_tips if result.prevention_tips else self.get_default_prevention_tips(),
                "treatment_options": result.treatment_options if result.treatment_options else [],
                "estimated_shelf_life": self.estimate_shelf_life(result)
            },
            "detailed_observations": {
                "key_observations": result.key_observations if result.key_observations else ["Visual inspection completed"],
                "detailed_analysis": result.detailed_analysis if result.detailed_analysis else "Standard analysis performed",
                "color_assessment": self.assess_color_health(result),
                "surface_analysis": self.analyze_surface_condition(result)
            },
            "ai_analysis_details": result.ai_analysis if result.ai_analysis else {
                "note": "AI analysis data not available",
                "fallback": "Using computer vision only"
            }
        }
        
    def calculate_severity(self, result):
        """Calculate severity level based on condition"""
        if 'BAD' in result.condition or 'DISCARD' in result.condition:
            return "Critical - Immediate disposal required"
        elif 'POOR' in result.condition:
            return "High - Significant quality issues"
        elif 'FAIR' in result.condition:
            return "Moderate - Quality declining"
        elif 'GOOD' in result.condition:
            return "Low - Minor imperfections only"
        else:
            return "None - Excellent quality"
            
    def calculate_overall_quality(self, result):
        """Calculate overall quality percentage"""
        scores = [
            result.freshness_score,
            100 - result.local_metrics['brown_rot_percentage'],
            100 - result.local_metrics['black_spots_percentage'],
            result.local_metrics['shape_integrity']
        ]
        return round(sum(scores) / len(scores), 1)
        
    def estimate_shelf_life(self, result):
        """Estimate remaining shelf life"""
        if 'BAD' in result.condition:
            return "0 days - Discard immediately"
        elif 'POOR' in result.condition:
            return "< 1 day - Use immediately"
        elif 'FAIR' in result.condition:
            return "2-3 days"
        elif 'GOOD' in result.condition:
            return "4-7 days"
        else:
            return "7+ days with proper storage"
            
    def assess_color_health(self, result):
        """Assess color health based on variance"""
        variance = result.local_metrics['color_variance']
        if variance < 20:
            return "Excellent - Uniform and healthy color"
        elif variance < 40:
            return "Good - Minor color variations"
        elif variance < 60:
            return "Fair - Noticeable color inconsistency"
        else:
            return "Poor - Significant color problems"
            
    def analyze_surface_condition(self, result):
        """Analyze surface condition based on texture"""
        texture = result.local_metrics['texture_score']
        if texture < 20:
            return "Smooth and healthy surface"
        elif texture < 40:
            return "Minor surface irregularities"
        elif texture < 60:
            return "Rough or damaged surface"
        else:
            return "Severely compromised surface"
            
    def clear_all_result_tabs(self):
        """Clear all result tab contents"""
        tabs_to_clear = [
            self.condition_content,
            self.health_content,
            self.metrics_content,
            self.recommendations_content,
            self.technical_content
        ]
        
        for tab in tabs_to_clear:
            for widget in tab.winfo_children():
                widget.destroy()
                
                placeholder = ctk.CTkLabel(
                tab,
                text="Perform analysis to see results",
                font=ctk.CTkFont(size=14),
                text_color="#666666"
            )
            placeholder.pack(pady=50)
            
    def perform_fruit_analysis(self, image):
        """Perform comprehensive fruit analysis"""
        # Local analysis
        local_metrics = self.perform_local_analysis(image)
        
        # AI analysis
        ai_result = self.analyze_with_gemini(image)
        
        # Combine results
        if ai_result:
            # Use AI results as primary with enhanced data
            return FruitAnalysisResult(
                condition=self.map_condition(ai_result.get('condition_category', 'FAIR')),
                confidence=ai_result.get('confidence_score', 70),
                fruit_type=ai_result.get('fruit_type', 'Unknown'),
                freshness_score=ai_result.get('freshness_score', local_metrics['freshness_score']),
                defects=ai_result.get('defects_found', []),
                ripeness=ai_result.get('ripeness', 'unknown'),
                safety=ai_result.get('safety_assessment', 'questionable'),
                action_required=ai_result.get('action_required', 'Monitor condition'),
                prevention_tips=ai_result.get('prevention_tips', self.get_default_prevention_tips()),
                storage_advice=ai_result.get('storage_advice', 'Store properly'),
                disease_identification=ai_result.get('disease_identification', 'None detected'),
                local_metrics=local_metrics,
                ai_analysis=ai_result,
                detailed_analysis=ai_result.get('detailed_analysis', ''),
                key_observations=ai_result.get('key_observations', []),
                treatment_options=ai_result.get('treatment_options', [])
            )
        else:
            # Fallback to local analysis
            return self.create_result_from_local(local_metrics)
            
    def get_default_prevention_tips(self):
        """Get default prevention tips"""
        return [
            "Store fruits in cool, dry place with good ventilation",
            "Check fruits daily for signs of decay or damage",
            "Remove any damaged fruits immediately to prevent spread",
            "Maintain proper temperature and humidity levels",
            "Use fruits in order of ripeness (first in, first out)"
        ]
        
    def map_condition(self, ai_condition):
        """Map AI condition to display format"""
        mapping = {
            'EXCELLENT': "🌟 EXCELLENT CONDITION - PREMIUM QUALITY",
            'GOOD': "✅ GOOD CONDITION - FRESH & HEALTHY",
            'FAIR': "⚠️ FAIR CONDITION - MONITOR CLOSELY",
            'POOR': "⚠️ POOR CONDITION - USE IMMEDIATELY",
            'BAD': "🚫 BAD CONDITION - DO NOT CONSUME",
            'INSECT_DAMAGED': "🐛 INSECT DAMAGE - REMOVE FROM BATCH"
        }
        return mapping.get(ai_condition, "❓ UNKNOWN CONDITION")
        
    def create_result_from_local(self, local_metrics):
        """Create result from local analysis only"""
        # Determine condition based on metrics
        bad_score = (local_metrics['brown_rot_percentage'] * 3 + 
                    local_metrics['black_spots_percentage'] * 4)
        freshness = local_metrics['freshness_score']
        
        if bad_score > 25 or freshness < 30:
            condition = "🚫 BAD CONDITION - DO NOT CONSUME"
            action = "Discard immediately"
            safety = "unsafe to eat"
            treatment = ["Dispose of properly in compost", "Clean storage area"]
        elif bad_score > 15 or freshness < 50:
            condition = "⚠️ POOR CONDITION - USE IMMEDIATELY"
            action = "Use within 24 hours or discard"
            safety = "questionable"
            treatment = ["Cut away affected areas", "Use for cooking only"]
        elif bad_score > 8 or freshness < 70:
            condition = "⚠️ FAIR CONDITION - MONITOR CLOSELY"
            action = "Use within 2-3 days"
            safety = "safe if consumed soon"
            treatment = ["Store separately", "Check twice daily"]
        elif freshness > 85 and bad_score < 3:
            condition = "🌟 EXCELLENT CONDITION - PREMIUM QUALITY"
            action = "Enjoy at your convenience"
            safety = "safe to eat"
            treatment = []
        else:
            condition = "✅ GOOD CONDITION - FRESH & HEALTHY"
            action = "Consume normally"
            safety = "safe to eat"
            treatment = []
            
        return FruitAnalysisResult(
            condition=condition,
            confidence=70.0,
            fruit_type="Unknown",
            freshness_score=freshness,
            defects=[],
            ripeness="unknown",
            safety=safety,
            action_required=action,
            prevention_tips=self.get_default_prevention_tips(),
            storage_advice="Store according to fruit type in cool, dry place",
            disease_identification="Visual inspection needed",
            local_metrics=local_metrics,
            detailed_analysis="Analysis based on computer vision metrics only",
            key_observations=[
                f"Freshness score: {freshness:.0f}%",
                f"Decay level: {local_metrics['brown_rot_percentage']:.1f}%",
                f"Black spots: {local_metrics['black_spots_percentage']:.1f}%"
            ],
            treatment_options=treatment
        )
        
    def perform_local_analysis(self, image):
        """Perform local computer vision analysis"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        return {
            'brown_rot_percentage': self.detect_brown_rot(hsv, lab),
            'black_spots_percentage': self.detect_black_spots(hsv, gray),
            'color_variance': self.analyze_color_uniformity(image),
            'texture_score': self.analyze_texture_quality(image),
            'shape_integrity': self.analyze_fruit_shape(image),
            'freshness_score': self.calculate_freshness_score(hsv, lab, image)
        }
        
    def detect_brown_rot(self, hsv_image, lab_image):
        """Detect brown/rot areas"""
        # HSV detection
        brown_lower = np.array([8, 50, 20])
        brown_upper = np.array([20, 255, 200])
        brown_mask = cv2.inRange(hsv_image, brown_lower, brown_upper)
        
        # Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        brown_mask = cv2.morphologyEx(brown_mask, cv2.MORPH_OPEN, kernel)
        
        # Calculate percentage
        total_pixels = hsv_image.shape[0] * hsv_image.shape[1]
        brown_pixels = cv2.countNonZero(brown_mask)
        
        return round((brown_pixels / total_pixels) * 100, 2)
        
    def detect_black_spots(self, hsv_image, gray_image):
        """Detect black spots"""
        # Dark area detection
        black_lower = np.array([0, 0, 0])
        black_upper = np.array([180, 255, 50])
        black_mask = cv2.inRange(hsv_image, black_lower, black_upper)
        
        # Gray threshold
        _, dark_areas = cv2.threshold(gray_image, 30, 255, cv2.THRESH_BINARY_INV)
        
        # Combine masks
        combined = cv2.bitwise_and(black_mask, dark_areas)
        
        # Remove noise
        kernel = np.ones((3, 3), np.uint8)
        combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN, kernel)
        
        # Calculate percentage
        total_pixels = hsv_image.shape[0] * hsv_image.shape[1]
        black_pixels = cv2.countNonZero(combined)
        
        return round((black_pixels / total_pixels) * 100, 2)
        
    def analyze_color_uniformity(self, image):
        """Analyze color uniformity"""
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        l_std = np.std(lab[:,:,0])
        a_std = np.std(lab[:,:,1])
        b_std = np.std(lab[:,:,2])
        
        variance = (l_std * 0.5 + a_std * 0.25 + b_std * 0.25)
        
        return round(variance, 2)
        
    def analyze_texture_quality(self, image):
        """Analyze texture quality"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Laplacian for texture
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        texture_score = laplacian.var()
        
        return round(min(texture_score, 100), 2)
        
    def analyze_fruit_shape(self, image):
        """Analyze fruit shape integrity"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)
            perimeter = cv2.arcLength(largest, True)
            
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                return round(circularity * 100, 2)
                
        return 50.0
        
    def calculate_freshness_score(self, hsv_image, lab_image, bgr_image):
        """Calculate overall freshness score"""
        # Brightness
        brightness = np.mean(lab_image[:,:,0])
        brightness_score = (brightness / 255) * 100
        
        # Saturation
        saturation = np.mean(hsv_image[:,:,1])
        saturation_score = (saturation / 255) * 100
        
        # Combined score
        freshness = (brightness_score * 0.4 + saturation_score * 0.6)
        
        return round(min(freshness, 100), 2)
        
    def analyze_with_gemini(self, image):
        """Analyze with Gemini AI"""
        try:
            image_base64 = self.encode_image_base64(image)
            
            prompt = """You are an expert fruit quality inspector with 20+ years experience. 
            Analyze this fruit image with extreme attention to detail.

CRITICAL INSPECTION PROTOCOL:

1. FRUIT IDENTIFICATION:
   - Identify the exact type and variety of fruit
   - Note any unique characteristics

2. CONDITION ASSESSMENT:
   - Check for any defects, damage, or disease
   - Examine color, texture, and surface condition
   - Look for signs of decay, mold, or insect damage

3. QUALITY CLASSIFICATION (BE STRICT):
   - EXCELLENT: Perfect specimen, no flaws
   - GOOD: Minor cosmetic imperfections only
   - FAIR: Some quality issues but edible
   - POOR: Significant problems, use immediately
   - BAD: Inedible, health risk, discard
   - INSECT_DAMAGED: Clear pest damage

4. DETAILED RECOMMENDATIONS:
   - Specific storage instructions
   - Prevention tips for issues found
   - Treatment options if applicable

RESPOND IN EXACT JSON FORMAT:
{
    "fruit_type": "specific fruit name",
    "condition_category": "EXCELLENT/GOOD/FAIR/POOR/BAD/INSECT_DAMAGED",
    "confidence_score": 85,
    "detailed_analysis": "comprehensive description of condition",
    "defects_found": ["list all defects found"],
    "ripeness": "under-ripe/perfectly-ripe/ripe/overripe/rotten",
    "freshness_score": 75,
    "safety_assessment": "safe/questionable/unsafe to eat",
    "disease_identification": "specific disease if any",
    "key_observations": ["5 most important observations"],
    "prevention_tips": ["5 specific prevention methods"],
    "storage_advice": "detailed storage recommendations",
    "action_required": "immediate action needed",
    "treatment_options": ["ways to treat or use the fruit"]
}"""

            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_base64
                        }}
                    ]
                }]
            }

            response = requests.post(self.gemini_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    
                    # Parse JSON
                    import re
                    json_match = re.search(r'\{.*\}', text, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                        
        except Exception as e:
            print(f"Gemini error: {e}")
            
        return None
        
    def encode_image_base64(self, image):
        """Encode image to base64"""
        _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 90])
        return base64.b64encode(buffer).decode('utf-8')
        
    def get_condition_color(self, condition):
        """Get color for condition"""
        if 'EXCELLENT' in condition:
            return '#00ff00'
        elif 'GOOD' in condition:
            return '#32cd32'
        elif 'FAIR' in condition:
            return '#ffa500'
        elif 'POOR' in condition:
            return '#ff6347'
        elif 'BAD' in condition or 'DISCARD' in condition:
            return '#ff0000'
        elif 'INSECT' in condition:
            return '#8b0000'
        else:
            return '#808080'
            
    def show_notification(self, message, type="info"):
        """Show notification"""
        colors = {
            "success": "#4CAF50",
            "error": "#f44336",
            "warning": "#ff9800",
            "info": "#2196F3"
        }
        
        notification = ctk.CTkFrame(
            self.root,
            fg_color=colors.get(type, "#2196F3"),
            corner_radius=10,
            height=50
        )
        notification.place(relx=0.5, rely=0.95, anchor="s")
        
        label = ctk.CTkLabel(
            notification,
            text=message,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff"
        )
        label.pack(padx=20, pady=10)
        
        # Auto hide
        self.root.after(3000, notification.destroy)
        
    def update_status(self, text):
        """Update status label"""
        if hasattr(self, 'status_label'):
            self.status_label.configure(text=text)
            
    # Export methods
    def export_pdf_report(self):
        """Export PDF report"""
        if not self.current_result:
            self.show_notification("⚠️ No analysis to export", "warning")
            return
            
        # For now, save as image
        self.save_analysis_image()
        self.show_notification("📄 Report saved as image (PDF coming soon)", "info")
        
    def export_excel_report(self):
        """Export Excel report"""
        if not self.current_result:
            self.show_notification("⚠️ No analysis to export", "warning")
            return
            
        # Create CSV data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"fruit_analysis_{timestamp}.csv"
        )
        
        if filename:
            try:
                import csv
                with open(filename, 'w', newline='') as file:
                    writer = csv.writer(file)
                    
                    # Headers
                    writer.writerow(['Metric', 'Value'])
                    
                    # Data
                    data = [
                        ['Analysis Date', datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                        ['Fruit Type', self.current_result.fruit_type],
                        ['Condition', self.current_result.condition],
                        ['Confidence', f"{self.current_result.confidence}%"],
                        ['Freshness Score', f"{self.current_result.freshness_score}%"],
                        ['Safety Assessment', self.current_result.safety],
                        ['Ripeness', self.current_result.ripeness],
                        ['Decay Level', f"{self.current_result.local_metrics['brown_rot_percentage']}%"],
                        ['Black Spots', f"{self.current_result.local_metrics['black_spots_percentage']}%"],
                        ['Shape Integrity', f"{self.current_result.local_metrics['shape_integrity']}%"],
                        ['Action Required', self.current_result.action_required],
                        ['Storage Advice', self.current_result.storage_advice]
                    ]
                    
                    writer.writerows(data)
                    
                    # Add defects
                    writer.writerow([])
                    writer.writerow(['Defects Found'])
                    for defect in self.current_result.defects:
                        writer.writerow(['', defect])
                        
                    # Add prevention tips
                    writer.writerow([])
                    writer.writerow(['Prevention Tips'])
                    for tip in self.current_result.prevention_tips:
                        writer.writerow(['', tip])
                        
                self.show_notification("✅ Excel/CSV report saved successfully!", "success")
                
            except Exception as e:
                self.show_notification(f"❌ Export failed: {str(e)}", "error")
                
    def save_analysis_image(self):
        """Save analysis as image"""
        if not self.current_result:
            self.show_notification("⚠️ No analysis to save", "warning")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialfile=f"fruit_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        )
        
        if filename:
            # Create report image
            self.create_report_image(filename)
            self.show_notification("✅ Report saved successfully!", "success")
            
    def create_report_image(self, filename):
        """Create comprehensive report image"""
        # Create image
        img_width = 1400
        img_height = 2000
        img = Image.new('RGB', (img_width, img_height), color='#0a0a0a')
        draw = ImageDraw.Draw(img)
        
        # Try to load fonts
        try:
            font_title = ImageFont.truetype("arial.ttf", 48)
            font_header = ImageFont.truetype("arial.ttf", 32)
            font_body = ImageFont.truetype("arial.ttf", 24)
            font_small = ImageFont.truetype("arial.ttf", 18)
        except:
            font_title = font_header = font_body = font_small = ImageFont.load_default()
            
        y = 50
        
        # Title
        draw.text((img_width//2, y), "FRUIT QUALITY ANALYSIS REPORT", 
                 font=font_title, fill='white', anchor='mt')
        y += 80
        
        # Date
        draw.text((img_width//2, y), datetime.now().strftime("%B %d, %Y at %I:%M %p"), 
                 font=font_small, fill='#888888', anchor='mt')
        y += 80
        
        # Main image
        if self.current_image_cv2 is not None:
            # Convert and resize
            image_rgb = cv2.cvtColor(self.current_image_cv2, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)
            pil_image.thumbnail((600, 400), Image.Resampling.LANCZOS)
            
            # Center and paste
            x_offset = (img_width - pil_image.width) // 2
            img.paste(pil_image, (x_offset, y))
            y += pil_image.height + 50
            
        # Condition box
        result = self.current_result
        condition_color = self.get_condition_color(result.condition)
        
        # Draw condition background
        draw.rectangle((100, y, img_width-100, y+100), 
                      fill=condition_color, outline='white', width=3)
        draw.text((img_width//2, y+50), result.condition, 
                 font=font_header, fill='white', anchor='mm')
        y += 130
        
        # Key Information
        draw.text((150, y), "KEY INFORMATION", font=font_header, fill='#4CAF50')
        y += 50
        
        info_items = [
            f"Fruit Type: {result.fruit_type}",
            f"AI Confidence: {result.confidence:.0f}%",
            f"Freshness Score: {result.freshness_score:.0f}%",
            f"Safety Assessment: {result.safety}",
            f"Ripeness: {result.ripeness}",
            f"Action Required: {result.action_required}"
        ]
        
        for item in info_items:
            draw.text((200, y), f"• {item}", font=font_body, fill='white')
            y += 35
            
        y += 30
        
        # Quality Metrics
        draw.text((150, y), "QUALITY METRICS", font=font_header, fill='#4CAF50')
        y += 50
        
        metrics = [
            f"Decay Level: {result.local_metrics['brown_rot_percentage']:.1f}%",
            f"Black Spots: {result.local_metrics['black_spots_percentage']:.1f}%",
            f"Shape Integrity: {result.local_metrics['shape_integrity']:.0f}%",
            f"Color Variance: {result.local_metrics['color_variance']:.1f}",
            f"Texture Score: {result.local_metrics['texture_score']:.1f}"
        ]
        
        for metric in metrics:
            draw.text((200, y), f"• {metric}", font=font_body, fill='white')
            y += 35
            
        y += 30
        
        # Defects Found
        if result.defects:
            draw.text((150, y), "DEFECTS DETECTED", font=font_header, fill='#FF0000')
            y += 50
            
            for defect in result.defects[:5]:
                draw.text((200, y), f"⚠️ {defect}", font=font_body, fill='#FF9999')
                y += 35
                
            y += 30
            
        # Prevention Tips
        if result.prevention_tips:
            draw.text((150, y), "PREVENTION TIPS", font=font_header, fill='#4CAF50')
            y += 50
            
            for i, tip in enumerate(result.prevention_tips[:5], 1):
                # Wrap long text
                if len(tip) > 70:
                    tip = tip[:70] + "..."
                draw.text((200, y), f"{i}. {tip}", font=font_body, fill='#90EE90')
                y += 35
                
        # Footer
        y = img_height - 100
        draw.text((img_width//2, y), "Generated by Fruit Health Inspector Pro", 
                 font=font_small, fill='#666666', anchor='mt')
        draw.text((img_width//2, y+30), "AI-Powered Analysis System", 
                 font=font_small, fill='#666666', anchor='mt')
        
        # Save
        img.save(filename, quality=95)
        
    def export_json_data(self):
        """Export JSON data"""
        if not self.current_result:
            self.show_notification("⚠️ No data to export", "warning")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"fruit_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if filename:
            # Use the comprehensive technical data
            export_data = self.generate_technical_data(self.current_result)
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
                
            self.show_notification("✅ Data exported successfully!", "success")
            
    def export_technical_data(self, data, format):
        """Export technical data in specified format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=f"technical_data_{timestamp}.json"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                self.show_notification("✅ Technical data exported as JSON!", "success")
                
        elif format == "csv":
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"technical_data_{timestamp}.csv"
            )
            
            if filename:
                # Flatten the nested structure for CSV
                import csv
                
                with open(filename, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Category', 'Metric', 'Value'])
                    
                    # Flatten the data
                    for category, category_data in data.items():
                        if isinstance(category_data, dict):
                            for key, value in category_data.items():
                                if isinstance(value, list):
                                    writer.writerow([category, key, ', '.join(str(v) for v in value)])
                                else:
                                    writer.writerow([category, key, str(value)])
                        elif isinstance(category_data, list):
                            writer.writerow([category, 'items', ', '.join(str(v) for v in category_data)])
                        else:
                            writer.writerow([category, 'value', str(category_data)])
                            
                self.show_notification("✅ Technical data exported as CSV!", "success")
                
    # Settings methods (placeholders)
    def change_theme(self, theme):
        """Change app theme"""
        ctk.set_appearance_mode(theme.lower())
        
    def change_color_scheme(self, scheme):
        """Change color scheme"""
        self.show_notification(f"Color scheme changed to {scheme}", "info")
        
    def change_ai_model(self, model):
        """Change AI model"""
        self.show_notification(f"AI model changed to {model}", "info")
        
    def change_analysis_detail(self, detail):
        """Change analysis detail level"""
        self.show_notification(f"Analysis detail set to {detail}", "info")
        
    def change_camera(self, camera_id):
        """Change camera device"""
        self.show_notification(f"Camera changed to device {camera_id}", "info")
        
    def change_image_quality(self, quality):
        """Change image quality"""
        self.show_notification(f"Image quality set to {quality}", "info")
        
    def on_closing(self):
        """Handle window closing"""
        self.camera_active = False
        self.root.destroy()
        
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main function"""
    print("\n" + "="*80)
    print("🍎 === FRUIT HEALTH INSPECTOR PRO === 🍊")
    print("Advanced AI-Powered Analysis System")
    print("="*80 + "\n")
    
    # Check dependencies
    try:
        import customtkinter
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call(["pip", "install", "customtkinter", "opencv-python", "pillow", "requests", "numpy", "matplotlib"])
        
    # API key
    API_KEY = "AIzaSyDkC-9tWhMn6XPkkvHwmighHUfY7FrN8wA"
    
    # Run app
    print("🚀 Launching Fruit Health Inspector Pro...")
    print("📊 Features:")
    print("   - Automatic comparison with last analysis")
    print("   - All tabs now show comprehensive data")
    print("   - Enhanced recommendations and technical data")
    print("💡 The comparison tab now auto-loads your last analyzed image!\n")
    
    app = AdvancedFruitAnalyzerUI(API_KEY)
    app.run()

if __name__ == '__main__':
    main()
