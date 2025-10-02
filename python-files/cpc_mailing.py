import customtkinter as ctk
from tkinter import filedialog, messagebox, font as tkfont, colorchooser, ttk
import tkinter as tk
import os
import pandas as pd
from tksheet import Sheet
import time
from datetime import datetime
import threading
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.application import MIMEApplication
import re
import json
import keyring
import logging
import socket
from fpdf import FPDF
import csv
import subprocess
import platform
import tempfile
import shutil
from PIL import Image
import io
import hashlib
import requests  # Added for API functionality

# Set up logging for debugging
log_dir = os.path.join(os.path.expanduser("~/.cpc_mailing/data"))
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, "debug.log"),
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class RichTextEditor(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configure grid weights for resizing
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create toolbar
        self.toolbar = ctk.CTkFrame(self, height=50)
        self.toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Create text area with increased height
        self.text_area = tk.Text(self, wrap="word", undo=True, font=("Arial", 12), height=12)
        self.text_area.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Create scrollbar
        self.scrollbar = ttk.Scrollbar(self, command=self.text_area.yview)
        self.scrollbar.grid(row=1, column=1, sticky="ns")
        self.text_area.configure(yscrollcommand=self.scrollbar.set)
        
        # Initialize formatting variables
        self.current_font = "Arial"
        self.current_size = 12
        self.current_color = "#000000"
        self.current_bg = "#FFFFFF"
        
        # Create toolbar buttons
        self.create_toolbar_buttons()
        
        # Configure text tags for formatting
        self.configure_text_tags()
        
        # Bind events
        self.text_area.bind("<KeyRelease>", self.on_key_release)
        self.text_area.bind("<ButtonRelease-1>", self.on_selection_change)
        self.text_area.bind("<<Paste>>", self.on_paste)
        
        # Auto-formatting settings
        self.auto_format = True
        self.auto_format_after_paste = True
        
    def create_toolbar_buttons(self):
        # Font style selector
        self.font_style_var = tk.StringVar(value="Arial")
        self.font_style_selector = ttk.Combobox(
            self.toolbar, textvariable=self.font_style_var,
            values=["Arial", "Calibri", "Times New Roman", "Verdana", "Georgia", "Courier New", "Impact", "Comic Sans MS"],
            width=12, state="readonly"
        )
        self.font_style_selector.grid(row=0, column=0, padx=5)
        self.font_style_selector.bind("<<ComboboxSelected>>", self.change_font_style)
        
        # Font size selector
        self.font_size_var = tk.StringVar(value="12")
        self.font_size_selector = ttk.Combobox(
            self.toolbar, textvariable=self.font_size_var,
            values=["8", "9", "10", "11", "12", "14", "16", "18", "20", "22", "24", "26", "28", "36"],
            width=5, state="readonly"
        )
        self.font_size_selector.grid(row=0, column=1, padx=5)
        self.font_size_selector.bind("<<ComboboxSelected>>", self.change_font_size)
        
        # Bold button
        self.bold_btn = ctk.CTkButton(
            self.toolbar, text="B", width=35, height=35,
            font=("Arial", 12, "bold"), command=self.toggle_bold
        )
        self.bold_btn.grid(row=0, column=2, padx=5)
        
        # Italic button
        self.italic_btn = ctk.CTkButton(
            self.toolbar, text="I", width=35, height=35,
            font=("Arial", 12, "italic"), command=self.toggle_italic
        )
        self.italic_btn.grid(row=0, column=3, padx=5)
        
        # Underline button
        self.underline_btn = ctk.CTkButton(
            self.toolbar, text="U", width=35, height=35,
            font=("Arial", 12, "underline"), command=self.toggle_underline
        )
        self.underline_btn.grid(row=0, column=4, padx=5)
        
        # Font color button
        self.font_color_btn = ctk.CTkButton(
            self.toolbar, text="A", width=35, height=35,
            font=("Arial", 12, "bold"), command=self.change_font_color
        )
        self.font_color_btn.grid(row=0, column=5, padx=5)
        
        # Highlight button
        self.highlight_btn = ctk.CTkButton(
            self.toolbar, text="🖌", width=35, height=35,
            font=("Arial", 12), command=self.change_highlight_color
        )
        self.highlight_btn.grid(row=0, column=6, padx=5)
        
        # Auto-format toggle
        self.auto_format_var = tk.BooleanVar(value=True)
        self.auto_format_btn = ctk.CTkButton(
            self.toolbar, text="Auto-Format", width=100, height=35,
            command=self.toggle_auto_format, fg_color="#28a745"
        )
        self.auto_format_btn.grid(row=0, column=7, padx=5)
        
        # Undo button
        self.undo_btn = ctk.CTkButton(
            self.toolbar, text="↶", width=35, height=35,
            font=("Arial", 14), command=self.undo
        )
        self.undo_btn.grid(row=0, column=8, padx=5)
        
        # Redo button
        self.redo_btn = ctk.CTkButton(
            self.toolbar, text="↷", width=35, height=35,
            font=("Arial", 14), command=self.redo
        )
        self.redo_btn.grid(row=0, column=9, padx=5)
        
        # Reset button
        self.reset_btn = ctk.CTkButton(
            self.toolbar, text="Reset", width=60, height=35,
            command=self.reset_formatting
        )
        self.reset_btn.grid(row=0, column=10, padx=5)
        
        # Add placeholder help button
        self.placeholder_btn = ctk.CTkButton(
            self.toolbar, text="Placeholders", width=100, height=35,
            font=("Arial", 10), command=self.show_placeholder_help,
            fg_color="#6c757d", hover_color="#5a6268"
        )
        self.placeholder_btn.grid(row=0, column=11, padx=5)
        
    def configure_text_tags(self):
        # Configure tags for formatting
        self.text_area.tag_configure("bold", font=(self.current_font, self.current_size, "bold"))
        self.text_area.tag_configure("italic", font=(self.current_font, self.current_size, "italic"))
        self.text_area.tag_configure("underline", font=(self.current_font, self.current_size, "underline"))
        self.text_area.tag_configure("highlight", background=self.current_bg)
        
        # Configure auto-formatting tags
        self.text_area.tag_configure("auto_email", foreground="#1E88E5")
        self.text_area.tag_configure("auto_url", foreground="#1E88E5")
        self.text_area.tag_configure("auto_phone", foreground="#1E88E5")
        
    def toggle_bold(self):
        current_tags = self.text_area.tag_names("sel.first")
        if "bold" in current_tags:
            self.text_area.tag_remove("bold", "sel.first", "sel.last")
        else:
            self.text_area.tag_add("bold", "sel.first", "sel.last")
            
    def toggle_italic(self):
        current_tags = self.text_area.tag_names("sel.first")
        if "italic" in current_tags:
            self.text_area.tag_remove("italic", "sel.first", "sel.last")
        else:
            self.text_area.tag_add("italic", "sel.first", "sel.last")
            
    def toggle_underline(self):
        current_tags = self.text_area.tag_names("sel.first")
        if "underline" in current_tags:
            self.text_area.tag_remove("underline", "sel.first", "sel.last")
        else:
            self.text_area.tag_add("underline", "sel.first", "sel.last")
            
    def change_font_style(self, event=None):
        font_style = self.font_style_var.get()
        self.current_font = font_style
        
        # Update font style for all tags
        self.text_area.tag_configure("bold", font=(font_style, self.current_size, "bold"))
        self.text_area.tag_configure("italic", font=(font_style, self.current_size, "italic"))
        self.text_area.tag_configure("underline", font=(font_style, self.current_size, "underline"))
        
        # Apply to selected text
        if self.text_area.tag_ranges("sel"):
            self.text_area.tag_add("font_style", "sel.first", "sel.last")
            self.text_area.tag_configure("font_style", font=(font_style, self.current_size))
            
    def change_font_size(self, event=None):
        size = int(self.font_size_var.get())
        self.current_size = size
        
        # Update font size for all tags
        self.text_area.tag_configure("bold", font=(self.current_font, size, "bold"))
        self.text_area.tag_configure("italic", font=(self.current_font, size, "italic"))
        self.text_area.tag_configure("underline", font=(self.current_font, size, "underline"))
        
        # Apply to selected text
        if self.text_area.tag_ranges("sel"):
            self.text_area.tag_add("size", "sel.first", "sel.last")
            self.text_area.tag_configure("size", font=(self.current_font, size))
            
    def change_font_color(self):
        color = colorchooser.askcolor(initialcolor=self.current_color)
        if color[1]:
            self.current_color = color[1]
            if self.text_area.tag_ranges("sel"):
                self.text_area.tag_add("color", "sel.first", "sel.last")
                self.text_area.tag_configure("color", foreground=self.current_color)
                
    def change_highlight_color(self):
        color = colorchooser.askcolor(initialcolor=self.current_bg)
        if color[1]:
            self.current_bg = color[1]
            if self.text_area.tag_ranges("sel"):
                self.text_area.tag_add("highlight", "sel.first", "sel.last")
                self.text_area.tag_configure("highlight", background=self.current_bg)
            else:
                messagebox.showinfo("No Selection", "Please select text to highlight.")
                
    def toggle_auto_format(self):
        self.auto_format = not self.auto_format
        self.auto_format_btn.configure(
            fg_color="#28a745" if self.auto_format else "#dc3545",
            text="Auto-Format ON" if self.auto_format else "Auto-Format OFF"
        )
        
    def undo(self):
        try:
            self.text_area.edit_undo()
        except:
            pass
            
    def redo(self):
        try:
            self.text_area.edit_redo()
        except:
            pass
            
    def reset_formatting(self):
        if self.text_area.tag_ranges("sel"):
            # Remove all formatting tags from selected text
            for tag in ["bold", "italic", "underline", "color", "highlight", "size", "font_style"]:
                self.text_area.tag_remove(tag, "sel.first", "sel.last")
        else:
            # If no selection, reset entire text
            self.text_area.tag_remove("bold", "1.0", "end")
            self.text_area.tag_remove("italic", "1.0", "end")
            self.text_area.tag_remove("underline", "1.0", "end")
            self.text_area.tag_remove("color", "1.0", "end")
            self.text_area.tag_remove("highlight", "1.0", "end")
            self.text_area.tag_remove("size", "1.0", "end")
            self.text_area.tag_remove("font_style", "1.0", "end")
            
    def on_key_release(self, event=None):
        # Update button states based on current formatting
        self.update_button_states()
        
        # Auto-format if enabled
        if self.auto_format and self.text_area.tag_ranges("sel"):
            self.apply_auto_formatting()
            
    def on_selection_change(self, event=None):
        # Update button states based on current formatting
        self.update_button_states()
        
    def on_paste(self, event=None):
        # Get the clipboard content
        try:
            clipboard_content = self.clipboard_get()
        except:
            return "break"
        
        # Insert the clipboard content at the current cursor position
        self.text_area.insert("insert", clipboard_content)
        
        # Schedule auto-formatting after paste if enabled
        if self.auto_format and self.auto_format_after_paste:
            self.after(100, self.apply_auto_formatting)
        return "break"  # Prevent default paste behavior
        
    def apply_auto_formatting(self):
        """Apply automatic formatting rules to selected text"""
        if not self.text_area.tag_ranges("sel"):
            return
            
        # Get the start and end indices of the selection
        start_index = self.text_area.index("sel.first")
        end_index = self.text_area.index("sel.last")
        
        # Get the selected text
        selected_text = self.text_area.get(start_index, end_index)
        
        # Remove any existing auto-formatting tags in the selection
        self.text_area.tag_remove("auto_email", start_index, end_index)
        self.text_area.tag_remove("auto_url", start_index, end_index)
        self.text_area.tag_remove("auto_phone", start_index, end_index)
        
        # Rule 1: Capitalize first letter of sentences
        # This is complex to implement without breaking formatting, so we'll skip it for now
        
        # Rule 2: Format email addresses
        email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        for match in re.finditer(email_pattern, selected_text):
            start = match.start(1)
            end = match.end(1)
            start_pos = f"{start_index}+{start}c"
            end_pos = f"{start_index}+{end}c"
            self.text_area.tag_add("auto_email", start_pos, end_pos)
        
        # Rule 3: Format URLs
        url_pattern = r'(https?://[^\s]+)'
        for match in re.finditer(url_pattern, selected_text):
            start = match.start(1)
            end = match.end(1)
            start_pos = f"{start_index}+{start}c"
            end_pos = f"{start_index}+{end}c"
            self.text_area.tag_add("auto_url", start_pos, end_pos)
        
        # Rule 4: Format phone numbers
        phone_pattern = r'(\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'
        for match in re.finditer(phone_pattern, selected_text):
            start = match.start(1)
            end = match.end(1)
            start_pos = f"{start_index}+{start}c"
            end_pos = f"{start_index}+{end}c"
            self.text_area.tag_add("auto_phone", start_pos, end_pos)
        
        # Configure the tags to have the desired appearance
        self.text_area.tag_config("auto_email", foreground="#1E88E5")
        self.text_area.tag_config("auto_url", foreground="#1E88E5")
        self.text_area.tag_config("auto_phone", foreground="#1E88E5")
            
    def update_button_states(self):
        if self.text_area.tag_ranges("sel"):
            # Check if bold is applied to selection
            current_tags = self.text_area.tag_names("sel.first")
            self.bold_btn.configure(
                fg_color="#1E88E5" if "bold" in current_tags else "#2B2B2B"
            )
            
            # Check if italic is applied to selection
            self.italic_btn.configure(
                fg_color="#1E88E5" if "italic" in current_tags else "#2B2B2B"
            )
            
            # Check if underline is applied to selection
            self.underline_btn.configure(
                fg_color="#1E88E5" if "underline" in current_tags else "#2B2B2B"
            )
        else:
            # Reset button states if no selection
            self.bold_btn.configure(fg_color="#2B2B2B")
            self.italic_btn.configure(fg_color="#2B2B2B")
            self.underline_btn.configure(fg_color="#2B2B2B")
    
    def show_placeholder_help(self):
        help_text = (
            "Placeholders Help\n\n"
            "You can use placeholders in your email body and subject that will be replaced with actual data from the recipient's row in the data sheet.\n\n"
            "Available Placeholders:\n"
            "• [{ Mail ID }] - Recipient's email address\n"
            "• [{ Unique Accounts }] - Unique account identifier\n"
            "• [{ Co. Name }] - Company name\n"
            "• [{ CC }] - CC recipients\n\n"
            "Example:\n"
            "If you type: \"Dear [{ Co. Name }],\"\n"
            "And the recipient's company name is \"MNA I & C Groups\",\n"
            "The email will show: \"Dear MNA I & C Groups,\"\n\n"
            "Note: Placeholders are case-sensitive and must match exactly with the column headers in the data sheet."
        )
        messagebox.showinfo("Placeholders Help", help_text)
    
    def get_text(self):
        """Get the plain text content with preserved line breaks"""
        return self.text_area.get("1.0", "end-1c")
    
    def set_text(self, text):
        """Set the text content"""
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", text)
        
        # Apply auto-formatting if enabled
        if self.auto_format:
            self.text_area.tag_add("sel", "1.0", "end")
            self.apply_auto_formatting()
            self.text_area.tag_remove("sel", "1.0", "end")
    
    def get_selected_text(self):
        """Get only the selected text content with fallback to full text"""
        try:
            if self.text_area.tag_ranges("sel"):
                selected_text = self.text_area.get("sel.first", "sel.last")
                return selected_text if selected_text.strip() else self.get_text()
            return self.get_text()
        except Exception as e:
            logging.error(f"Error getting selected text: {e}")
            return self.get_text()
    
    def get_html(self):
        """Convert the rich text to HTML while preserving formatting and line breaks"""
        # Check if there's a selection
        if self.text_area.tag_ranges("sel"):
            return self._get_selection_html()
        else:
            return self._get_full_html()
    
    def _get_full_html(self):
        """Convert the entire text to HTML with email client compatibility and line breaks"""
        html = ""
        text = self.text_area.get("1.0", "end-1c")
        
        # We'll get the ranges for each tag
        tag_ranges = {}
        for tag in ["bold", "italic", "underline", "color", "highlight", "size", "font_style", "auto_email", "auto_url", "auto_phone"]:
            ranges = self.text_area.tag_ranges(tag)
            tag_ranges[tag] = []
            for i in range(0, len(ranges), 2):
                start = ranges[i]
                end = ranges[i+1]
                start_index = self.text_area.index(start)
                end_index = self.text_area.index(end)
                start_char = self._index_to_char(start_index)
                end_char = self._index_to_char(end_index)
                tag_ranges[tag].append((start_char, end_char))
        
        # We'll create a list of style changes per character
        char_tags = [set() for _ in range(len(text))]
        for tag, ranges in tag_ranges.items():
            for start, end in ranges:
                for i in range(start, min(end, len(text))):
                    char_tags[i].add(tag)
        
        # Now, we'll traverse the text and group consecutive characters with the same tags
        i = 0
        while i < len(text):
            current_tags = char_tags[i]
            j = i + 1
            while j < len(text) and char_tags[j] == current_tags:
                j += 1
            
            # Extract the substring
            substring = text[i:j]
            
            # Normalize line endings to \n
            substring = substring.replace('\r\n', '\n').replace('\r', '\n')
            
            # Escape HTML special characters
            substring = substring.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            # Replace newlines with <br> for HTML
            substring = substring.replace('\n', '<br>')
            
            # Build style attributes
            style_attrs = []
            
            # Handle font family
            if "font_style" in current_tags:
                font = self.text_area.tag_cget("font_style", "font")
                if isinstance(font, tuple) and len(font) >= 1:
                    family = font[0]
                    style_attrs.append(f"font-family: '{family}'")
            
            # Handle font size
            if "size" in current_tags:
                font = self.text_area.tag_cget("size", "font")
                if isinstance(font, tuple) and len(font) >= 2:
                    size = font[1]
                    style_attrs.append(f"font-size: {size}pt")
            
            # Handle font color
            if "color" in current_tags:
                color = self.text_area.tag_cget("color", "foreground")
                style_attrs.append(f"color: {color}")
            elif "auto_email" in current_tags or "auto_url" in current_tags or "auto_phone" in current_tags:
                style_attrs.append("color: #1E88E5")
            
            # Handle highlight color
            if "highlight" in current_tags:
                bg_color = self.text_area.tag_cget("highlight", "background")
                style_attrs.append(f"background-color: {bg_color}")
            
            # Apply semantic formatting
            if "bold" in current_tags:
                substring = f"<b>{substring}</b>"
            if "italic" in current_tags:
                substring = f"<i>{substring}</i>"
            if "underline" in current_tags:
                substring = f"<u>{substring}</u>"
            
            # Apply style attributes if any
            if style_attrs:
                style_str = "; ".join(style_attrs)
                substring = f'<span style="{style_str}">{substring}</span>'
            
            html += substring
            i = j
        
        # Wrap with default font and size for better email client compatibility
        default_style = f"font-family: '{self.current_font}'; font-size: {self.current_size}pt; color: {self.current_color};"
        html = f'<div style="{default_style}">{html}</div>'
        
        return html
    
    def _get_selection_html(self):
        """Convert only the selected text to HTML while preserving formatting and line breaks"""
        if not self.text_area.tag_ranges("sel"):
            return ""
        
        start = self.text_area.index("sel.first")
        end = self.text_area.index("sel.last")
        
        # Get the selected text
        selected_text = self.text_area.get(start, end)
        
        # Get the absolute character offset of the start and end in the entire text
        start_char = self._index_to_char(start)
        end_char = self._index_to_char(end)
        
        # Now, for each tag, we'll get the ranges that overlap with [start_char, end_char)
        tag_ranges = {}
        for tag in ["bold", "italic", "underline", "color", "highlight", "size", "font_style", "auto_email", "auto_url", "auto_phone"]:
            ranges = self.text_area.tag_ranges(tag)
            tag_ranges[tag] = []
            for i in range(0, len(ranges), 2):
                tag_start = self._index_to_char(self.text_area.index(ranges[i]))
                tag_end = self._index_to_char(self.text_area.index(ranges[i+1]))
                # Check if this tag range overlaps with [start_char, end_char)
                if tag_end <= start_char or tag_start >= end_char:
                    continue
                # Calculate the overlap
                overlap_start = max(tag_start, start_char)
                overlap_end = min(tag_end, end_char)
                # Convert to relative offsets within the selected text
                rel_start = overlap_start - start_char
                rel_end = overlap_end - start_char
                tag_ranges[tag].append((rel_start, rel_end))
        
        # Now, create a list of sets for each character in the selected text
        char_tags = [set() for _ in range(len(selected_text))]
        for tag, ranges in tag_ranges.items():
            for (rel_start, rel_end) in ranges:
                for i in range(rel_start, min(rel_end, len(selected_text))):
                    char_tags[i].add(tag)
        
        # Now, build the HTML by grouping consecutive characters with the same tags
        html = ""
        i = 0
        while i < len(selected_text):
            current_tags = char_tags[i]
            j = i + 1
            while j < len(selected_text) and char_tags[j] == current_tags:
                j += 1
            
            substring = selected_text[i:j]
            
            # Normalize line endings to \n
            substring = substring.replace('\r\n', '\n').replace('\r', '\n')
            
            # Escape HTML special characters
            substring = substring.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            # Replace newlines with <br> for HTML
            substring = substring.replace('\n', '<br>')
            
            # Build style attributes
            style_attrs = []
            
            # Handle font family
            if "font_style" in current_tags:
                font = self.text_area.tag_cget("font_style", "font")
                if isinstance(font, tuple) and len(font) >= 1:
                    family = font[0]
                    style_attrs.append(f"font-family: '{family}'")
            
            # Handle font size
            if "size" in current_tags:
                font = self.text_area.tag_cget("size", "font")
                if isinstance(font, tuple) and len(font) >= 2:
                    size = font[1]
                    style_attrs.append(f"font-size: {size}pt")
            
            # Handle font color
            if "color" in current_tags:
                color = self.text_area.tag_cget("color", "foreground")
                style_attrs.append(f"color: {color}")
            elif "auto_email" in current_tags or "auto_url" in current_tags or "auto_phone" in current_tags:
                style_attrs.append("color: #1E88E5")
            
            # Handle highlight color
            if "highlight" in current_tags:
                bg_color = self.text_area.tag_cget("highlight", "background")
                style_attrs.append(f"background-color: {bg_color}")
            
            # Apply semantic formatting
            if "bold" in current_tags:
                substring = f"<b>{substring}</b>"
            if "italic" in current_tags:
                substring = f"<i>{substring}</i>"
            if "underline" in current_tags:
                substring = f"<u>{substring}</u>"
            
            # Apply style attributes if any
            if style_attrs:
                style_str = "; ".join(style_attrs)
                substring = f'<span style="{style_str}">{substring}</span>'
            
            html += substring
            i = j
        
        return html
    
    def _index_to_char(self, index):
        """Convert a tkinter text index to a character offset"""
        return int(self.text_area.count("1.0", index, "chars"))

class SignatureSettingsPopup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Signature & Disclaimer Settings")
        self.geometry("600x500")
        self.resizable(False, False)
        self.transient(parent)
        
        # Center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")
        
        # Main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Signature section
        signature_frame = ctk.CTkFrame(self.main_frame)
        signature_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        signature_label = ctk.CTkLabel(signature_frame, text="Signature", font=ctk.CTkFont("Arial", 14, "bold"))
        signature_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Signature toolbar
        signature_toolbar = ctk.CTkFrame(signature_frame, height=40)
        signature_toolbar.pack(fill="x", padx=10, pady=5)
        
        # Font style selector
        self.sig_font_style_var = tk.StringVar(value="Arial")
        self.sig_font_style_selector = ttk.Combobox(
            signature_toolbar, textvariable=self.sig_font_style_var,
            values=["Arial", "Calibri", "Times New Roman", "Verdana", "Georgia", "Courier New"],
            width=12, state="readonly"
        )
        self.sig_font_style_selector.grid(row=0, column=0, padx=5)
        
        # Font size selector
        self.sig_font_size_var = tk.StringVar(value="10")
        self.sig_font_size_selector = ttk.Combobox(
            signature_toolbar, textvariable=self.sig_font_size_var,
            values=["8", "9", "10", "11", "12", "14"], width=5, state="readonly"
        )
        self.sig_font_size_selector.grid(row=0, column=1, padx=5)
        
        # Bold button
        self.sig_bold_btn = ctk.CTkButton(
            signature_toolbar, text="B", width=30, height=30,
            font=("Arial", 10, "bold"), command=self.toggle_sig_bold
        )
        self.sig_bold_btn.grid(row=0, column=2, padx=5)
        
        # Italic button
        self.sig_italic_btn = ctk.CTkButton(
            signature_toolbar, text="I", width=30, height=30,
            font=("Arial", 10, "italic"), command=self.toggle_sig_italic
        )
        self.sig_italic_btn.grid(row=0, column=3, padx=5)
        
        # Underline button
        self.sig_underline_btn = ctk.CTkButton(
            signature_toolbar, text="U", width=30, height=30,
            font=("Arial", 10, "underline"), command=self.toggle_sig_underline
        )
        self.sig_underline_btn.grid(row=0, column=4, padx=5)
        
        # Font color button
        self.sig_font_color_btn = ctk.CTkButton(
            signature_toolbar, text="A", width=30, height=30,
            font=("Arial", 10, "bold"), command=self.change_sig_font_color
        )
        self.sig_font_color_btn.grid(row=0, column=5, padx=5)
        
        # Delete button
        self.sig_delete_btn = ctk.CTkButton(
            signature_toolbar, text="Clear", width=60, height=30,
            font=("Arial", 10), command=self.clear_signature, fg_color="#dc3545"
        )
        self.sig_delete_btn.grid(row=0, column=6, padx=5)
        
        # Auto-save checkbox for signature
        self.sig_auto_save_var = tk.BooleanVar(value=False)
        self.sig_auto_save_check = ctk.CTkCheckBox(
            signature_toolbar, text="Auto-save", variable=self.sig_auto_save_var,
            command=self.check_auto_save
        )
        self.sig_auto_save_check.grid(row=0, column=7, padx=5)
        
        # Signature text area
        self.signature_text = tk.Text(signature_frame, wrap="word", height=6, font=("Arial", 10))
        self.signature_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Signature scrollbar
        sig_scrollbar = ttk.Scrollbar(signature_frame, command=self.signature_text.yview)
        sig_scrollbar.pack(side="right", fill="y")
        self.signature_text.configure(yscrollcommand=sig_scrollbar.set)
        
        # Disclaimer section
        disclaimer_frame = ctk.CTkFrame(self.main_frame)
        disclaimer_frame.pack(fill="both", expand=True)
        
        disclaimer_label = ctk.CTkLabel(disclaimer_frame, text="Disclaimer", font=ctk.CTkFont("Arial", 14, "bold"))
        disclaimer_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Disclaimer toolbar
        disclaimer_toolbar = ctk.CTkFrame(disclaimer_frame, height=40)
        disclaimer_toolbar.pack(fill="x", padx=10, pady=5)
        
        # Font style selector
        self.dis_font_style_var = tk.StringVar(value="Arial")
        self.dis_font_style_selector = ttk.Combobox(
            disclaimer_toolbar, textvariable=self.dis_font_style_var,
            values=["Arial", "Calibri", "Times New Roman", "Verdana", "Georgia", "Courier New"],
            width=12, state="readonly"
        )
        self.dis_font_style_selector.grid(row=0, column=0, padx=5)
        
        # Font size selector
        self.dis_font_size_var = tk.StringVar(value="9")
        self.dis_font_size_selector = ttk.Combobox(
            disclaimer_toolbar, textvariable=self.dis_font_size_var,
            values=["8", "9", "10", "11"], width=5, state="readonly"
        )
        self.dis_font_size_selector.grid(row=0, column=1, padx=5)
        
        # Bold button
        self.dis_bold_btn = ctk.CTkButton(
            disclaimer_toolbar, text="B", width=30, height=30,
            font=("Arial", 10, "bold"), command=self.toggle_dis_bold
        )
        self.dis_bold_btn.grid(row=0, column=2, padx=5)
        
        # Italic button
        self.dis_italic_btn = ctk.CTkButton(
            disclaimer_toolbar, text="I", width=30, height=30,
            font=("Arial", 10, "italic"), command=self.toggle_dis_italic
        )
        self.dis_italic_btn.grid(row=0, column=3, padx=5)
        
        # Underline button
        self.dis_underline_btn = ctk.CTkButton(
            disclaimer_toolbar, text="U", width=30, height=30,
            font=("Arial", 10, "underline"), command=self.toggle_dis_underline
        )
        self.dis_underline_btn.grid(row=0, column=4, padx=5)
        
        # Font color button
        self.dis_font_color_btn = ctk.CTkButton(
            disclaimer_toolbar, text="A", width=30, height=30,
            font=("Arial", 10, "bold"), command=self.change_dis_font_color
        )
        self.dis_font_color_btn.grid(row=0, column=5, padx=5)
        
        # Delete button
        self.dis_delete_btn = ctk.CTkButton(
            disclaimer_toolbar, text="Clear", width=60, height=30,
            font=("Arial", 10), command=self.clear_disclaimer, fg_color="#dc3545"
        )
        self.dis_delete_btn.grid(row=0, column=6, padx=5)
        
        # Auto-save checkbox for disclaimer
        self.dis_auto_save_var = tk.BooleanVar(value=False)
        self.dis_auto_save_check = ctk.CTkCheckBox(
            disclaimer_toolbar, text="Auto-save", variable=self.dis_auto_save_var,
            command=self.check_auto_save
        )
        self.dis_auto_save_check.grid(row=0, column=7, padx=5)
        
        # Disclaimer text area
        self.disclaimer_text = tk.Text(disclaimer_frame, wrap="word", height=6, font=("Arial", 9))
        self.disclaimer_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Disclaimer scrollbar
        dis_scrollbar = ttk.Scrollbar(disclaimer_frame, command=self.disclaimer_text.yview)
        dis_scrollbar.pack(side="right", fill="y")
        self.disclaimer_text.configure(yscrollcommand=dis_scrollbar.set)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(self)
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        save_button = ctk.CTkButton(buttons_frame, text="Save", width=100, command=self.save_settings)
        save_button.pack(side="right", padx=5)
        
        cancel_button = ctk.CTkButton(buttons_frame, text="Cancel", width=100, command=self.destroy)
        cancel_button.pack(side="right", padx=5)
        
        # Load existing settings if any
        self.load_settings()
        
        # Bind events
        self.signature_text.bind("<KeyRelease>", self.on_sig_key_release)
        self.signature_text.bind("<ButtonRelease-1>", self.on_sig_selection_change)
        self.disclaimer_text.bind("<KeyRelease>", self.on_dis_key_release)
        self.disclaimer_text.bind("<ButtonRelease-1>", self.on_dis_selection_change)
        
        # Initialize signature and disclaimer variables
        self.sig_current_font = "Arial"
        self.sig_current_size = 10
        self.sig_current_color = "#000000"
        
        self.dis_current_font = "Arial"
        self.dis_current_size = 9
        self.dis_current_color = "#000000"
        
        # Configure text tags for formatting
        self.configure_sig_text_tags()
        self.configure_dis_text_tags()
        
    def configure_sig_text_tags(self):
        # Configure tags for signature formatting
        self.signature_text.tag_configure("sig_bold", font=(self.sig_current_font, self.sig_current_size, "bold"))
        self.signature_text.tag_configure("sig_italic", font=(self.sig_current_font, self.sig_current_size, "italic"))
        self.signature_text.tag_configure("sig_underline", font=(self.sig_current_font, self.sig_current_size, "underline"))
        self.signature_text.tag_configure("sig_color", foreground=self.sig_current_color)
        
    def configure_dis_text_tags(self):
        # Configure tags for disclaimer formatting
        self.disclaimer_text.tag_configure("dis_bold", font=(self.dis_current_font, self.dis_current_size, "bold"))
        self.disclaimer_text.tag_configure("dis_italic", font=(self.dis_current_font, self.dis_current_size, "italic"))
        self.disclaimer_text.tag_configure("dis_underline", font=(self.dis_current_font, self.dis_current_size, "underline"))
        self.disclaimer_text.tag_configure("dis_color", foreground=self.dis_current_color)
        
    def load_settings(self):
        try:
            settings_file = os.path.join(os.path.expanduser("~/.cpc_mailing/data"), "signature_settings.json")
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.signature_text.insert("1.0", settings.get("signature", ""))
                    self.disclaimer_text.insert("1.0", settings.get("disclaimer", ""))
        except Exception as e:
            logging.error(f"Failed to load signature settings: {e}")
    
    def save_settings(self):
        try:
            settings = {
                "signature": self.signature_text.get("1.0", "end-1c"),
                "disclaimer": self.disclaimer_text.get("1.0", "end-1c")
            }
            
            settings_file = os.path.join(os.path.expanduser("~/.cpc_mailing/data"), "signature_settings.json")
            os.makedirs(os.path.dirname(settings_file), exist_ok=True)
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            
            # Update parent's signature and disclaimer
            self.parent.signature = settings["signature"]
            self.parent.disclaimer = settings["disclaimer"]
            
            # Save to app config as well
            self.parent.save_app_config()
            
            messagebox.showinfo("Success", "Signature and disclaimer settings saved successfully!")
            self.destroy()
        except Exception as e:
            logging.error(f"Failed to save signature settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def check_auto_save(self):
        """Check if both auto-save checkboxes are checked and save settings if they are"""
        if self.sig_auto_save_var.get() and self.dis_auto_save_var.get():
            # Both checkboxes are checked, save settings and close
            self.save_settings()
    
    def clear_signature(self):
        self.signature_text.delete("1.0", "end")
    
    def clear_disclaimer(self):
        self.disclaimer_text.delete("1.0", "end")
    
    def toggle_sig_bold(self):
        current_tags = self.signature_text.tag_names("sel.first")
        if "sig_bold" in current_tags:
            self.signature_text.tag_remove("sig_bold", "sel.first", "sel.last")
        else:
            self.signature_text.tag_add("sig_bold", "sel.first", "sel.last")
    
    def toggle_sig_italic(self):
        current_tags = self.signature_text.tag_names("sel.first")
        if "sig_italic" in current_tags:
            self.signature_text.tag_remove("sig_italic", "sel.first", "sel.last")
        else:
            self.signature_text.tag_add("sig_italic", "sel.first", "sel.last")
    
    def toggle_sig_underline(self):
        current_tags = self.signature_text.tag_names("sel.first")
        if "sig_underline" in current_tags:
            self.signature_text.tag_remove("sig_underline", "sel.first", "sel.last")
        else:
            self.signature_text.tag_add("sig_underline", "sel.first", "sel.last")
    
    def change_sig_font_color(self):
        color = colorchooser.askcolor(initialcolor=self.sig_current_color)
        if color[1]:
            self.sig_current_color = color[1]
            if self.signature_text.tag_ranges("sel"):
                self.signature_text.tag_add("sig_color", "sel.first", "sel.last")
                self.signature_text.tag_configure("sig_color", foreground=self.sig_current_color)
    
    def toggle_dis_bold(self):
        current_tags = self.disclaimer_text.tag_names("sel.first")
        if "dis_bold" in current_tags:
            self.disclaimer_text.tag_remove("dis_bold", "sel.first", "sel.last")
        else:
            self.disclaimer_text.tag_add("dis_bold", "sel.first", "sel.last")
    
    def toggle_dis_italic(self):
        current_tags = self.disclaimer_text.tag_names("sel.first")
        if "dis_italic" in current_tags:
            self.disclaimer_text.tag_remove("dis_italic", "sel.first", "sel.last")
        else:
            self.disclaimer_text.tag_add("dis_italic", "sel.first", "sel.last")
    
    def toggle_dis_underline(self):
        current_tags = self.disclaimer_text.tag_names("sel.first")
        if "dis_underline" in current_tags:
            self.disclaimer_text.tag_remove("dis_underline", "sel.first", "sel.last")
        else:
            self.disclaimer_text.tag_add("dis_underline", "sel.first", "sel.last")
    
    def change_dis_font_color(self):
        color = colorchooser.askcolor(initialcolor=self.dis_current_color)
        if color[1]:
            self.dis_current_color = color[1]
            if self.disclaimer_text.tag_ranges("sel"):
                self.disclaimer_text.tag_add("dis_color", "sel.first", "sel.last")
                self.disclaimer_text.tag_configure("dis_color", foreground=self.dis_current_color)
    
    def on_sig_key_release(self, event=None):
        # Update button states based on current formatting
        self.update_sig_button_states()
    
    def on_sig_selection_change(self, event=None):
        # Update button states based on current formatting
        self.update_sig_button_states()
    
    def on_dis_key_release(self, event=None):
        # Update button states based on current formatting
        self.update_dis_button_states()
    
    def on_dis_selection_change(self, event=None):
        # Update button states based on current formatting
        self.update_dis_button_states()
    
    def update_sig_button_states(self):
        if self.signature_text.tag_ranges("sel"):
            # Check if bold is applied to selection
            current_tags = self.signature_text.tag_names("sel.first")
            self.sig_bold_btn.configure(
                fg_color="#1E88E5" if "sig_bold" in current_tags else "#2B2B2B"
            )
            
            # Check if italic is applied to selection
            self.sig_italic_btn.configure(
                fg_color="#1E88E5" if "sig_italic" in current_tags else "#2B2B2B"
            )
            
            # Check if underline is applied to selection
            self.sig_underline_btn.configure(
                fg_color="#1E88E5" if "sig_underline" in current_tags else "#2B2B2B"
            )
        else:
            # Reset button states if no selection
            self.sig_bold_btn.configure(fg_color="#2B2B2B")
            self.sig_italic_btn.configure(fg_color="#2B2B2B")
            self.sig_underline_btn.configure(fg_color="#2B2B2B")
    
    def update_dis_button_states(self):
        if self.disclaimer_text.tag_ranges("sel"):
            # Check if bold is applied to selection
            current_tags = self.disclaimer_text.tag_names("sel.first")
            self.dis_bold_btn.configure(
                fg_color="#1E88E5" if "dis_bold" in current_tags else "#2B2B2B"
            )
            
            # Check if italic is applied to selection
            self.dis_italic_btn.configure(
                fg_color="#1E88E5" if "dis_italic" in current_tags else "#2B2B2B"
            )
            
            # Check if underline is applied to selection
            self.dis_underline_btn.configure(
                fg_color="#1E88E5" if "dis_underline" in current_tags else "#2B2B2B"
            )
        else:
            # Reset button states if no selection
            self.dis_bold_btn.configure(fg_color="#2B2B2B")
            self.dis_italic_btn.configure(fg_color="#2B2B2B")
            self.dis_underline_btn.configure(fg_color="#2B2B2B")

class SMTPSettingsPopup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("SMTP Configuration")
        self.geometry("450x580")  # Increased height for firewall info
        self.resizable(False, False)
        self.transient(parent)
        
        root_x = parent.winfo_rootx()
        root_y = parent.winfo_rooty()
        root_w = parent.winfo_width()
        root_h = parent.winfo_height()
        self.geometry(f"+{root_x + root_w//2 - 225}+{root_y + root_h//2 - 290}")
        
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas = ctk.CTkCanvas(self.main_frame, highlightthickness=0)
        self.scrollbar = ctk.CTkScrollbar(self.main_frame, orientation="vertical", command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        header = ctk.CTkLabel(self.scrollable_frame, text="SMTP Configuration", 
                             font=ctk.CTkFont("Arial", 16, "bold"),
                             fg_color="#1E3F66", text_color="white", height=40)
        header.pack(fill="x", pady=(0, 20))
        
        self.configs_file = os.path.join(os.path.expanduser("~/.cpc_mailing/data"), "smtp_configs.json")
        self.smtp_configs = self.load_configs()
        self.current_config_index = -1
        
        self.config_dropdown_var = ctk.StringVar()
        self.config_dropdown = ctk.CTkOptionMenu(self.scrollable_frame,
                                               variable=self.config_dropdown_var,
                                               values=["New Configuration"] + list(self.smtp_configs.keys()),
                                               command=self.load_selected_config)
        self.config_dropdown.pack(fill="x", pady=(0, 10))
        
        self.smtp_server_var = ctk.StringVar()
        self.port_var = ctk.StringVar()
        self.email_var = ctk.StringVar()
        self.password_var = ctk.StringVar()
        self.encryption_var = ctk.StringVar(value="TLS")  # Default to TLS
        self.custom_from_var = ctk.StringVar()  # For custom 'From' address
        
        ctk.CTkLabel(self.scrollable_frame, text="SMTP Server:", font=ctk.CTkFont("Arial", 12, "bold")).pack(anchor="w", pady=(5, 2))
        self.smtp_entry = ctk.CTkEntry(self.scrollable_frame, textvariable=self.smtp_server_var, 
                                      placeholder_text="e.g., smtp.gmail.com", height=35)
        self.smtp_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(self.scrollable_frame, text="Port:", font=ctk.CTkFont("Arial", 12, "bold")).pack(anchor="w", pady=(0, 2))
        self.port_entry = ctk.CTkEntry(self.scrollable_frame, textvariable=self.port_var, 
                                      placeholder_text="e.g., 587", height=35)
        self.port_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(self.scrollable_frame, text="Encryption:", font=ctk.CTkFont("Arial", 12, "bold")).pack(anchor="w", pady=(0, 2))
        encryption_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        encryption_frame.pack(fill="x", pady=(0, 10))
        
        self.tls_radio = ctk.CTkRadioButton(encryption_frame, text="TLS (Recommended)", variable=self.encryption_var, value="TLS")
        self.tls_radio.pack(side="left", padx=10)
        
        self.ssl_radio = ctk.CTkRadioButton(encryption_frame, text="SSL", variable=self.encryption_var, value="SSL")
        self.ssl_radio.pack(side="left", padx=10)
        
        ctk.CTkLabel(self.scrollable_frame, text="Username (Email):", font=ctk.CTkFont("Arial", 12, "bold")).pack(anchor="w", pady=(0, 2))
        self.email_entry = ctk.CTkEntry(self.scrollable_frame, textvariable=self.email_var, 
                                       placeholder_text="your.email@gmail.com", height=35)
        self.email_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(self.scrollable_frame, text="Password (App Password):", font=ctk.CTkFont("Arial", 12, "bold")).pack(anchor="w", pady=(0, 2))
        self.password_entry = ctk.CTkEntry(self.scrollable_frame, textvariable=self.password_var, 
                                          show="*", placeholder_text="App specific password", height=35)
        self.password_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(self.scrollable_frame, text="Custom 'From' Address (Optional):", font=ctk.CTkFont("Arial", 12, "bold")).pack(anchor="w", pady=(0, 2))
        self.custom_from_entry = ctk.CTkEntry(self.scrollable_frame, textvariable=self.custom_from_var, 
                                             placeholder_text="sender@otherdomain.com", height=35)
        self.custom_from_entry.pack(fill="x", pady=(0, 15))
        
        # Firewall info section
        firewall_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#fff3cd", corner_radius=8)
        firewall_frame.pack(fill="x", pady=(0, 15))
        
        firewall_label = ctk.CTkLabel(firewall_frame, 
                                    text="🔥 Firewall Information:\n"
                                         "• If using SSL (port 465) fails, try TLS (port 587)\n"
                                         "• Add Python to firewall exceptions\n"
                                         "• Temporarily disable antivirus to test",
                                    font=ctk.CTkFont("Arial", 10), 
                                    text_color="#856404",
                                    justify="left")
        firewall_label.pack(pady=10, padx=10)
        
        security_note = ctk.CTkLabel(self.scrollable_frame, 
                                    text="💡 Password is stored securely using your system's credential manager",
                                    font=ctk.CTkFont("Arial", 9),
                                    text_color="#28a745")
        security_note.pack(anchor="w", pady=(0, 15))
        
        btn_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkButton(btn_frame, text="Test Connection", width=100, 
                     command=self.test_connection, fg_color="#28a745").pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="Save Config", width=100, 
                     command=self.save_smtp_settings).pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="Add New", width=100, 
                     command=self.add_new_config).pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="Delete", width=70, 
                     command=self.delete_config, fg_color="#dc3545").pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="Cancel", width=70, 
                     command=self.destroy, fg_color="#6c757d").pack(side="right", padx=5)
        
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.grab_set()
        
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))
        
        # Auto-detect SMTP settings when email is entered
        self.email_entry.bind("<FocusOut>", lambda e: self.detect_smtp_settings())
        
    def _on_mousewheel(self, event):
        delta = event.delta
        if event.num == 4:
            delta = 120
        elif event.num == 5:
            delta = -120
        self.canvas.yview_scroll(int(-1 * (delta / 120)), "units")
        
    def detect_smtp_settings(self):
        """Auto-detect SMTP settings based on email domain"""
        email = self.email_var.get().strip()
        if not email or '@' not in email:
            return
            
        domain = email.split('@')[-1].lower()
        
        # Common SMTP configurations
        smtp_configs = {
            'gmail.com': {'server': 'smtp.gmail.com', 'port': '587', 'encryption': 'TLS'},
            'yahoo.com': {'server': 'smtp.mail.yahoo.com', 'port': '587', 'encryption': 'TLS'},
            'outlook.com': {'server': 'smtp-mail.outlook.com', 'port': '587', 'encryption': 'TLS'},
            'hotmail.com': {'server': 'smtp-mail.outlook.com', 'port': '587', 'encryption': 'TLS'},
            'rediffmail.com': {'server': 'smtp.rediffmail.com', 'port': '587', 'encryption': 'TLS'},
            'aol.com': {'server': 'smtp.aol.com', 'port': '587', 'encryption': 'TLS'},
            'icloud.com': {'server': 'smtp.mail.me.com', 'port': '587', 'encryption': 'TLS'},
            'mail.com': {'server': 'smtp.mail.com', 'port': '587', 'encryption': 'TLS'},
            'zoho.com': {'server': 'smtp.zoho.com', 'port': '587', 'encryption': 'TLS'},
            'yandex.com': {'server': 'smtp.yandex.com', 'port': '587', 'encryption': 'TLS'},
            'protonmail.com': {'server': 'mail.protonmail.com', 'port': '587', 'encryption': 'TLS'},
            'gmx.com': {'server': 'mail.gmx.com', 'port': '587', 'encryption': 'TLS'},
            'fastmail.com': {'server': 'smtp.fastmail.com', 'port': '587', 'encryption': 'TLS'},
        }
        
        if domain in smtp_configs:
            config = smtp_configs[domain]
            self.smtp_server_var.set(config['server'])
            self.port_var.set(config['port'])
            self.encryption_var.set(config['encryption'])
            
            # Show provider-specific guidance
            if domain in ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'aol.com', 'icloud.com']:
                messagebox.showinfo("App Password Required", 
                    f"For {domain}, you need to use an app password:\n\n"
                    f"1. Go to your account security settings\n"
                    f"2. Enable 2-factor authentication\n"
                    f"3. Generate an app password\n"
                    f"4. Use that password here (not your regular password)")
        
    def load_configs(self):
        try:
            os.makedirs(os.path.dirname(self.configs_file), exist_ok=True)
            if os.path.exists(self.configs_file):
                with open(self.configs_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logging.error(f"Failed to load SMTP configurations: {e}")
            messagebox.showerror("Error", f"Failed to load SMTP configurations: {e}")
            return {}
        
    def save_configs(self):
        try:
            os.makedirs(os.path.dirname(self.configs_file), exist_ok=True)
            with open(self.configs_file, 'w') as f:
                json.dump(self.smtp_configs, f, indent=4)
        except Exception as e:
            logging.error(f"Failed to save SMTP configurations: {e}")
            messagebox.showerror("Error", f"Failed to save SMTP configurations: {e}")
        
    def load_selected_config(self, selection):
        if selection == "New Configuration":
            self.current_config_index = -1
            self.smtp_server_var.set("")
            self.port_var.set("")
            self.email_var.set("")
            self.password_var.set("")
            self.encryption_var.set("TLS")
            self.custom_from_var.set("")
        else:
            self.current_config_index = list(self.smtp_configs.keys()).index(selection)
            config = self.smtp_configs[selection]
            self.smtp_server_var.set(config.get("smtp_server", ""))
            self.port_var.set(config.get("port", ""))
            self.email_var.set(config.get("email", ""))
            self.encryption_var.set(config.get("encryption", "TLS"))
            self.custom_from_var.set(config.get("custom_from", ""))
            password = keyring.get_password("cpc_mailing", selection)
            self.password_var.set(password if password else "")
            
    def add_new_config(self):
        self.current_config_index = -1
        self.config_dropdown_var.set("New Configuration")
        self.smtp_server_var.set("")
        self.port_var.set("")
        self.email_var.set("")
        self.password_var.set("")
        self.encryption_var.set("TLS")
        self.custom_from_var.set("")
        
    def delete_config(self):
        if self.current_config_index == -1:
            messagebox.showwarning("No Selection", "Please select a configuration to delete.")
            return
            
        config_name = list(self.smtp_configs.keys())[self.current_config_index]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the configuration '{config_name}'?"):
            # Remove from keyring
            try:
                keyring.delete_password("cpc_mailing", config_name)
            except:
                pass
                
            # Remove from configs
            del self.smtp_configs[config_name]
            self.save_configs()
            
            # Update dropdown
            self.config_dropdown.configure(values=["New Configuration"] + list(self.smtp_configs.keys()))
            
            # Reset form
            self.add_new_config()
            messagebox.showinfo("Deleted", f"Configuration '{config_name}' has been deleted.")
            
            # If this was the active config in parent, clear it
            if hasattr(self.parent, 'smtp_config') and self.parent.smtp_config and self.parent.smtp_config.get("config_name") == config_name:
                self.parent.smtp_config = None
                self.parent.update_smtp_status()
    
    def test_connection(self):
        smtp_server = self.smtp_server_var.get().strip()
        port_str = self.port_var.get().strip()
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        encryption = self.encryption_var.get()
        
        if not all([smtp_server, port_str, email, password]):
            messagebox.showerror("Missing Information", "Please fill in all required fields before testing.")
            return
        
        try:
            port = int(port_str)
            if not (0 <= port <= 65535):
                raise ValueError("Port number must be between 0 and 65535")
        except ValueError:
            messagebox.showerror("Invalid Port", "Please enter a valid port number (0-65535).")
            return
            
        try:
            if encryption == "SSL":
                # Check if port 465 is being used and warn about firewall issues
                if port == 465:
                    if not messagebox.askyesno("Port 465 Warning", 
                        "Port 465 (SSL) is often blocked by firewalls. Consider using TLS (port 587) instead. Continue with SSL?"):
                        return
                
                server = smtplib.SMTP_SSL(smtp_server, port)
                server.login(email, password)
            else:  # TLS
                server = smtplib.SMTP(smtp_server, port)
                server.starttls()
                server.login(email, password)
            server.quit()
            messagebox.showinfo("Success", "SMTP connection test successful!")
        except smtplib.SMTPAuthenticationError as e:
            error_msg = str(e)
            if "Application-specific password required" in error_msg:
                messagebox.showerror("Authentication Failed", 
                    "This account requires an app password:\n\n"
                    "1. Go to your account security settings\n"
                    "2. Enable 2-factor authentication\n"
                    "3. Generate an app password\n"
                    "4. Use that password instead of your regular password")
            elif "Username and Password not accepted" in error_msg:
                messagebox.showerror("Authentication Failed", 
                    "Incorrect username or password. Please check your credentials.")
            else:
                messagebox.showerror("Authentication Failed", f"SMTP authentication failed: {error_msg}")
        except smtplib.SMTPConnectError as e:
            messagebox.showerror("Connection Failed", 
                f"Could not connect to {smtp_server}:{port}.\n\n"
                "Possible solutions:\n"
                "1. Check the server name and port\n"
                "2. Try a different port (587 for TLS, 465 for SSL)\n"
                "3. Check your firewall/antivirus settings\n"
                "4. Contact your email provider for correct SMTP settings")
        except socket.error as e:
            if "10013" in str(e):
                messagebox.showerror("Connection Failed", 
                    "Access denied (Error 10013). This is likely due to a firewall blocking port 465.\n\n"
                    "Solutions:\n"
                    "1. Try using TLS (port 587) instead of SSL\n"
                    "2. Add Python to firewall exceptions\n"
                    "3. Temporarily disable antivirus software")
            else:
                messagebox.showerror("Connection Failed", f"Socket error: {str(e)}")
        except Exception as e:
            messagebox.showerror("Connection Failed", f"Unexpected error: {str(e)}")
    
    def save_smtp_settings(self):
        if not all([self.smtp_server_var.get().strip(), self.port_var.get().strip(), 
                   self.email_var.get().strip(), self.password_var.get().strip()]):
            messagebox.showwarning("Missing Information", "Please fill in all required fields.")
            return
        
        try:
            port = int(self.port_var.get().strip())
            if not (0 <= port <= 65535):
                raise ValueError("Port number must be between 0 and 65535")
        except ValueError:
            messagebox.showerror("Invalid Port", "Please enter a valid port number (0-65535).")
            return
            
        # Warn about port 465
        if self.encryption_var.get() == "SSL" and port == 465:
            if not messagebox.askyesno("Port 465 Warning", 
                "Port 465 (SSL) is often blocked by firewalls. Consider using TLS (port 587) instead. Continue with SSL?"):
                return
            
        config_name = f"Config_{len(self.smtp_configs) + 1}" if self.current_config_index == -1 else list(self.smtp_configs.keys())[self.current_config_index]
        
        keyring.set_password("cpc_mailing", config_name, self.password_var.get().strip())
        
        self.smtp_configs[config_name] = {
            "smtp_server": self.smtp_server_var.get().strip(),
            "port": self.port_var.get().strip(),
            "email": self.email_var.get().strip(),
            "encryption": self.encryption_var.get(),
            "custom_from": self.custom_from_var.get().strip()
        }
        
        self.save_configs()
        self.config_dropdown.configure(values=["New Configuration"] + list(self.smtp_configs.keys()))
        
        latest_config = self.smtp_configs[config_name].copy()
        latest_config["password"] = self.password_var.get().strip()
        latest_config["config_name"] = config_name
        self.parent.smtp_config = latest_config
        self.parent.update_smtp_status()
        
        messagebox.showinfo("Saved", "SMTP configuration saved successfully!")
        self.grab_release()
        self.destroy()

class APISettingsPopup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("API Configuration")
        self.geometry("450x580")  # Same size as SMTP settings
        self.resizable(False, False)
        self.transient(parent)
        
        root_x = parent.winfo_rootx()
        root_y = parent.winfo_rooty()
        root_w = parent.winfo_width()
        root_h = parent.winfo_height()
        self.geometry(f"+{root_x + root_w//2 - 225}+{root_y + root_h//2 - 290}")
        
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas = ctk.CTkCanvas(self.main_frame, highlightthickness=0)
        self.scrollbar = ctk.CTkScrollbar(self.main_frame, orientation="vertical", command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        header = ctk.CTkLabel(self.scrollable_frame, text="API Configuration", 
                             font=ctk.CTkFont("Arial", 16, "bold"),
                             fg_color="#1E3F66", text_color="white", height=40)
        header.pack(fill="x", pady=(0, 20))
        
        self.configs_file = os.path.join(os.path.expanduser("~/.cpc_mailing/data"), "api_configs.json")
        self.api_configs = self.load_configs()
        self.current_config_index = -1
        
        self.config_dropdown_var = ctk.StringVar()
        self.config_dropdown = ctk.CTkOptionMenu(self.scrollable_frame,
                                               variable=self.config_dropdown_var,
                                               values=["New Configuration"] + list(self.api_configs.keys()),
                                               command=self.load_selected_config)
        self.config_dropdown.pack(fill="x", pady=(0, 10))
        
        self.api_endpoint_var = ctk.StringVar()
        self.api_key_var = ctk.StringVar()
        self.api_method_var = ctk.StringVar(value="POST")  # Default to POST
        self.custom_from_var = ctk.StringVar()  # For custom 'From' address
        
        ctk.CTkLabel(self.scrollable_frame, text="API Endpoint:", font=ctk.CTkFont("Arial", 12, "bold")).pack(anchor="w", pady=(5, 2))
        self.api_endpoint_entry = ctk.CTkEntry(self.scrollable_frame, textvariable=self.api_endpoint_var, 
                                             placeholder_text="e.g., https://api.example.com/send", height=35)
        self.api_endpoint_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(self.scrollable_frame, text="API Key:", font=ctk.CTkFont("Arial", 12, "bold")).pack(anchor="w", pady=(0, 2))
        self.api_key_entry = ctk.CTkEntry(self.scrollable_frame, textvariable=self.api_key_var, 
                                        placeholder_text="Your API key", height=35, show="*")
        self.api_key_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(self.scrollable_frame, text="HTTP Method:", font=ctk.CTkFont("Arial", 12, "bold")).pack(anchor="w", pady=(0, 2))
        method_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        method_frame.pack(fill="x", pady=(0, 10))
        
        self.post_radio = ctk.CTkRadioButton(method_frame, text="POST", variable=self.api_method_var, value="POST")
        self.post_radio.pack(side="left", padx=10)
        
        self.put_radio = ctk.CTkRadioButton(method_frame, text="PUT", variable=self.api_method_var, value="PUT")
        self.put_radio.pack(side="left", padx=10)
        
        ctk.CTkLabel(self.scrollable_frame, text="Custom 'From' Address (Optional):", font=ctk.CTkFont("Arial", 12, "bold")).pack(anchor="w", pady=(0, 2))
        self.custom_from_entry = ctk.CTkEntry(self.scrollable_frame, textvariable=self.custom_from_var, 
                                             placeholder_text="sender@otherdomain.com", height=35)
        self.custom_from_entry.pack(fill="x", pady=(0, 15))
        
        # API info section
        api_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#e1f5fe", corner_radius=8)
        api_frame.pack(fill="x", pady=(0, 15))
        
        api_label = ctk.CTkLabel(api_frame, 
                               text="📡 API Information:\n"
                                    "• Ensure your API endpoint is accessible\n"
                                    "• Verify your API key has necessary permissions\n"
                                    "• Check API documentation for required parameters",
                               font=ctk.CTkFont("Arial", 10), 
                               text_color="#01579b",
                               justify="left")
        api_label.pack(pady=10, padx=10)
        
        security_note = ctk.CTkLabel(self.scrollable_frame, 
                                   text="🔒 API key is stored securely using your system's credential manager",
                                   font=ctk.CTkFont("Arial", 9),
                                   text_color="#28a745")
        security_note.pack(anchor="w", pady=(0, 15))
        
        btn_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkButton(btn_frame, text="Test Connection", width=100, 
                     command=self.test_connection, fg_color="#28a745").pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="Save Config", width=100, 
                     command=self.save_api_settings).pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="Add New", width=100, 
                     command=self.add_new_config).pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="Delete", width=70, 
                     command=self.delete_config, fg_color="#dc3545").pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="Cancel", width=70, 
                     command=self.destroy, fg_color="#6c757d").pack(side="right", padx=5)
        
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.grab_set()
        
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))
        
    def _on_mousewheel(self, event):
        delta = event.delta
        if event.num == 4:
            delta = 120
        elif event.num == 5:
            delta = -120
        self.canvas.yview_scroll(int(-1 * (delta / 120)), "units")
        
    def load_configs(self):
        try:
            os.makedirs(os.path.dirname(self.configs_file), exist_ok=True)
            if os.path.exists(self.configs_file):
                with open(self.configs_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logging.error(f"Failed to load API configurations: {e}")
            messagebox.showerror("Error", f"Failed to load API configurations: {e}")
            return {}
        
    def save_configs(self):
        try:
            os.makedirs(os.path.dirname(self.configs_file), exist_ok=True)
            with open(self.configs_file, 'w') as f:
                json.dump(self.api_configs, f, indent=4)
        except Exception as e:
            logging.error(f"Failed to save API configurations: {e}")
            messagebox.showerror("Error", f"Failed to save API configurations: {e}")
        
    def load_selected_config(self, selection):
        if selection == "New Configuration":
            self.current_config_index = -1
            self.api_endpoint_var.set("")
            self.api_key_var.set("")
            self.api_method_var.set("POST")
            self.custom_from_var.set("")
        else:
            self.current_config_index = list(self.api_configs.keys()).index(selection)
            config = self.api_configs[selection]
            self.api_endpoint_var.set(config.get("api_endpoint", ""))
            self.api_method_var.set(config.get("api_method", "POST"))
            self.custom_from_var.set(config.get("custom_from", ""))
            api_key = keyring.get_password("cpc_mailing_api", selection)
            self.api_key_var.set(api_key if api_key else "")
            
    def add_new_config(self):
        self.current_config_index = -1
        self.config_dropdown_var.set("New Configuration")
        self.api_endpoint_var.set("")
        self.api_key_var.set("")
        self.api_method_var.set("POST")
        self.custom_from_var.set("")
        
    def delete_config(self):
        if self.current_config_index == -1:
            messagebox.showwarning("No Selection", "Please select a configuration to delete.")
            return
            
        config_name = list(self.api_configs.keys())[self.current_config_index]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the configuration '{config_name}'?"):
            # Remove from keyring
            try:
                keyring.delete_password("cpc_mailing_api", config_name)
            except:
                pass
                
            # Remove from configs
            del self.api_configs[config_name]
            self.save_configs()
            
            # Update dropdown
            self.config_dropdown.configure(values=["New Configuration"] + list(self.api_configs.keys()))
            
            # Reset form
            self.add_new_config()
            messagebox.showinfo("Deleted", f"Configuration '{config_name}' has been deleted.")
            
            # If this was the active config in parent, clear it
            if hasattr(self.parent, 'api_config') and self.parent.api_config and self.parent.api_config.get("config_name") == config_name:
                self.parent.api_config = None
                self.parent.update_api_status()
    
    def test_connection(self):
        api_endpoint = self.api_endpoint_var.get().strip()
        api_key = self.api_key_var.get().strip()
        api_method = self.api_method_var.get()
        
        if not all([api_endpoint, api_key]):
            messagebox.showerror("Missing Information", "Please fill in all required fields before testing.")
            return
            
        try:
            # Create a simple test request
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Create a minimal test payload
            test_data = {
                "test": True,
                "message": "API connection test"
            }
            
            if api_method == "POST":
                response = requests.post(api_endpoint, json=test_data, headers=headers, timeout=10)
            else:  # PUT
                response = requests.put(api_endpoint, json=test_data, headers=headers, timeout=10)
                
            if response.status_code in [200, 201, 202]:
                messagebox.showinfo("Success", "API connection test successful!")
            else:
                messagebox.showerror("Connection Failed", 
                    f"API returned status code: {response.status_code}\n"
                    f"Response: {response.text[:200]}...")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Connection Failed", f"API connection failed: {str(e)}")
        except Exception as e:
            messagebox.showerror("Connection Failed", f"Unexpected error: {str(e)}")
    
    def save_api_settings(self):
        if not all([self.api_endpoint_var.get().strip(), self.api_key_var.get().strip()]):
            messagebox.showwarning("Missing Information", "Please fill in all required fields.")
            return
            
        config_name = f"Config_{len(self.api_configs) + 1}" if self.current_config_index == -1 else list(self.api_configs.keys())[self.current_config_index]
        
        keyring.set_password("cpc_mailing_api", config_name, self.api_key_var.get().strip())
        
        self.api_configs[config_name] = {
            "api_endpoint": self.api_endpoint_var.get().strip(),
            "api_method": self.api_method_var.get(),
            "custom_from": self.custom_from_var.get().strip()
        }
        
        self.save_configs()
        self.config_dropdown.configure(values=["New Configuration"] + list(self.api_configs.keys()))
        
        latest_config = self.api_configs[config_name].copy()
        latest_config["api_key"] = self.api_key_var.get().strip()
        latest_config["config_name"] = config_name
        self.parent.api_config = latest_config
        self.parent.update_api_status()
        
        messagebox.showinfo("Saved", "API configuration saved successfully!")
        self.grab_release()
        self.destroy()

class DataSheetWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Mailing Data Entry")
        self.geometry("600x500")
        self.resizable(False, False)
        self.transient(parent)
        self.data_file = os.path.join(os.path.expanduser("~/.cpc_mailing/data"), "mailing_data.csv")
        
        # Create header frame with import button
        header_frame = ctk.CTkFrame(self, height=40, fg_color="#62B956")
        header_frame.pack(fill="x")
        
        header_label = ctk.CTkLabel(header_frame, text="Mailing Data Entry", 
                                   font=ctk.CTkFont("Arial", 14, "bold"),
                                   text_color="black", height=40, anchor="center")
        header_label.pack(side="left", expand=True)
        
        # Import button with icon
        import_btn = ctk.CTkButton(header_frame, text="📥 Import", width=100, height=30,
                                   command=self.import_excel, fg_color="#17a2b8")
        import_btn.pack(side="right", padx=10, pady=5)
        
        self.info_label = ctk.CTkLabel(self, text="", text_color="#1E3F66",
                                       font=ctk.CTkFont("Arial", 11))
        self.info_label.pack(anchor="w", padx=10, pady=5)
        
        sheet_frame = ctk.CTkFrame(self, fg_color="white")
        sheet_frame.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        
        self.sheet = Sheet(sheet_frame,
                           headers=["Mail ID", "Unique Accounts", "Co. Name", "CC"],
                           width=570, height=370, header_background='#1E3F66',
                           header_foreground='white', show_header=True,
                           show_row_index=True, row_height=25, total_columns=4,
                           column_width=140, data_background='white', data_foreground='black',
                           grid_color='#d3d3d3', header_font=('Arial', 10, 'bold'),
                           data_font=('Arial', 10))
        
        self.sheet.enable_bindings((
            "single_select", "arrowkeys", "row_select", "column_select",
            "copy", "cut", "paste", "undo", "edit_cell", "select_all",
            "tab", "shift_tab", "enter", "shift_enter", "ctrl_z", "ctrl_y", "escape", "delete"
        ))
        self.sheet.pack(fill="both", expand=True)
        self.load_data()
        
        btn_frame = ctk.CTkFrame(self, fg_color=None, corner_radius=0)
        btn_frame.pack(pady=10)
        
        add_btn = ctk.CTkButton(btn_frame, text="Row Add", width=100, command=self.add_rows_popup)
        clear_btn = ctk.CTkButton(btn_frame, text="Clear All", width=100, command=self.clear_all)
        save_btn = ctk.CTkButton(btn_frame, text="Save", width=100, command=self.save_data)
        
        add_btn.pack(side="left", padx=5)
        clear_btn.pack(side="left", padx=5)
        save_btn.pack(side="left", padx=5)
        
        self.bind("<Control-n>", lambda e: self.add_rows_popup())
        self.bind("<Control-s>", lambda e: self.save_data())
        
        # Bind Delete key to delete selected cell content
        self.bind("<Delete>", self.delete_selected_cells)
        self.bind("<BackSpace>", self.delete_selected_cells)
        
        # Bind sheet events for better delete handling
        self.sheet.bind("<Delete>", self.delete_selected_cells)
        self.sheet.bind("<BackSpace>", self.delete_selected_cells)
        
        self.sheet.bind("<<SheetModified>>", lambda e: self.auto_save())
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def on_close(self):
        self.parent.data_sheet_window = None
        self.destroy()
        
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                # Force all columns to be read as strings to prevent numeric conversion
                df = pd.read_csv(self.data_file, dtype=str)
                
                # Fix account numbers - remove any decimal points that might have been added
                if "Unique Accounts" in df.columns:
                    df["Unique Accounts"] = df["Unique Accounts"].apply(
                        lambda x: str(x).rstrip('.0') if str(x).endswith('.0') else str(x)
                    )
                
                # Remove blank rows (where Mail ID is empty)
                df = df[df["Mail ID"].str.strip() != ""]
                
                data = df.fillna("").values.tolist()
                while len(data) < 50:
                    data.append(["", "", "", ""])
                self.sheet.set_sheet_data(data[:50])
                self.parent.mailing_data_df = df
                self.parent.data_info_label.configure(text=f"{len(df)} recipients entered")
                self.info_label.configure(text=f"Loaded {len(df)} recipients")
            except Exception as e:
                logging.error(f"Failed to load data: {e}")
                messagebox.showerror("Error", f"Failed to load data: {e}")
                self.sheet.set_sheet_data([["", "", "", ""] for _ in range(50)])
        else:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            self.sheet.set_sheet_data([["", "", "", ""] for _ in range(50)])
            
    def auto_save(self):
        """Auto-save functionality that also updates the change status"""
        try:
            data = self.sheet.get_sheet_data()
            valid_data = []
            for row in data:
                if len(row) >= 1 and row[0].strip():  # Only Mail ID is required
                    valid_data.append(row)
                    
            if valid_data:
                df = pd.DataFrame(valid_data, columns=["Mail ID", "Unique Accounts", "Co. Name", "CC"])
                os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
                df.to_csv(self.data_file, index=False)
                self.info_label.configure(text=f"Auto-saved {len(df)} recipients")
        except Exception as e:
            logging.error(f"Auto-save failed: {e}")
            
    def add_rows_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Add Rows")
        popup.geometry("260x120")
        popup.resizable(False, False)
        popup.overrideredirect(True)
        
        root_x = self.winfo_rootx()
        root_y = self.winfo_rooty()
        root_w = self.winfo_width()
        root_h = self.winfo_height()
        popup.geometry(f"+{root_x + root_w//2 - 130}+{root_y + root_h//2 - 60}")
        
        popup.grab_set()
        ctk.CTkLabel(popup, text="Enter number of rows to add:", font=ctk.CTkFont("Arial", 11)).pack(pady=(15, 5))
        entry_var = ctk.StringVar()
        entry = ctk.CTkEntry(popup, textvariable=entry_var, justify="center", font=ctk.CTkFont("Arial", 11))
        entry.pack(pady=5)
        entry.focus_set()
        
        btn_inner_frame = ctk.CTkFrame(popup, fg_color="white")
        btn_inner_frame.pack(pady=10)
        
        def on_ok():
            val = entry_var.get()
            if not val.isdigit() or int(val) < 1:
                messagebox.showerror("Invalid Input", "Please enter a positive integer.")
                return
            num = int(val)
            data = self.sheet.get_sheet_data()
            for _ in range(num):
                data.append(["", "", "", ""])
            self.sheet.set_sheet_data(data)
            popup.grab_release()
            popup.destroy()
            
        def on_cancel():
            popup.grab_release()
            popup.destroy()
            
        ok_btn = ctk.CTkButton(btn_inner_frame, text="OK", width=70, command=on_ok)
        cancel_btn = ctk.CTkButton(btn_inner_frame, text="Cancel", width=70,
                                   fg_color="#999999", hover_color="#888888", command=on_cancel)
        
        ok_btn.pack(side="left", padx=8)
        cancel_btn.pack(side="left", padx=8)
        
        popup.protocol("WM_DELETE_WINDOW", lambda: None)
        
    def clear_all(self):
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all data?"):
            data = self.sheet.get_sheet_data()
            cleared = [["" for _ in row] for row in data]
            self.sheet.set_sheet_data(cleared)
            df = pd.DataFrame([], columns=["Mail ID", "Unique Accounts", "Co. Name", "CC"])
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            df.to_csv(self.data_file, index=False)
            self.parent.mailing_data_df = None
            self.parent.data_info_label.configure(text="No recipients entered")
            self.info_label.configure(text="Data cleared")
            
    def save_data(self):
        def is_valid_email(email):
            return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email.strip()))
        
        data = self.sheet.get_sheet_data()
        valid_data = []
        invalid_emails = []
        
        # Filter out blank rows (where Mail ID is empty)
        for row in data:
            if len(row) >= 1 and row[0].strip():  # Only Mail ID is required
                if not is_valid_email(row[0]):
                    invalid_emails.append(row[0])
                else:
                    # Make Unique Accounts optional
                    unique_account = str(row[1]).strip() if len(row) > 1 and row[1].strip() else ""
                    company_name = row[2] if len(row) > 2 else ""
                    cc = row[3] if len(row) > 3 else ""
                    
                    valid_data.append([row[0], unique_account, company_name, cc])
        
        if invalid_emails:
            messagebox.showwarning("Invalid Emails", 
                                 f"Invalid email addresses: {', '.join(invalid_emails[:5])}{'...' if len(invalid_emails) > 5 else ''}")
            return
            
        if not valid_data:
            messagebox.showwarning("No Data", "Please enter at least one email address.")
            return
            
        df = pd.DataFrame(valid_data, columns=["Mail ID", "Unique Accounts", "Co. Name", "CC"])
        self.parent.mailing_data_df = df
        self.parent.data_info_label.configure(text=f"{len(df)} recipients entered")
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        try:
            df.to_csv(self.data_file, index=False)
            messagebox.showinfo("Data Saved", f"Successfully saved {len(df)} recipients!")
            self.destroy()
        except Exception as e:
            logging.error(f"Failed to save data: {e}")
            messagebox.showerror("Error", f"Failed to save data: {e}")
    
    def delete_selected_cells(self, event=None):
        """Delete the content of selected cells"""
        try:
            # Get currently selected cells
            selected_boxes = self.sheet.get_selected_boxes()
            
            if not selected_boxes:
                # If no cells are selected, check if there's an active cell
                try:
                    row, col = self.sheet.get_currently_selected()
                    if row is not None and col is not None:
                        # Clear the active cell
                        data = self.sheet.get_sheet_data()
                        if 0 <= row < len(data) and 0 <= col < len(data[row]):
                            data[row][col] = ""
                            self.sheet.set_sheet_data(data)
                            self.auto_save()
                except:
                    pass
                return
                
            # Get current data
            data = self.sheet.get_sheet_data()
            
            # Clear each selected cell
            for box in selected_boxes:
                # Each box is (row_start, col_start, row_end, col_end)
                row_start, col_start, row_end, col_end = box
                
                # Handle single cell selection
                if row_start == row_end and col_start == col_end:
                    if 0 <= row_start < len(data) and 0 <= col_start < len(data[row_start]):
                        data[row_start][col_start] = ""
                # Handle range selection
                else:
                    for row in range(row_start, row_end + 1):
                        for col in range(col_start, col_end + 1):
                            if 0 <= row < len(data) and 0 <= col < len(data[row]):
                                data[row][col] = ""
            
            # Update the sheet with modified data
            self.sheet.set_sheet_data(data)
            
            # Trigger auto-save
            self.auto_save()
            
        except Exception as e:
            logging.error(f"Error deleting cell content: {e}")
            messagebox.showerror("Error", f"Failed to delete cell content: {str(e)}")
    
    def import_excel(self):
        """Import data from Excel file with improved data handling and automatic duplicate removal"""
        file_path = filedialog.askopenfilename(
            title="Import Excel File",
            filetypes=[
                ("Excel Files", "*.xlsx *.xls"),
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            ]
        )
        
        if not file_path:
            return
            
        try:
            # Read Excel or CSV file
            if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                df = pd.read_excel(file_path, dtype=str)  # Force all columns as strings
            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path, dtype=str)  # Force all columns as strings
            else:
                messagebox.showerror("Invalid File", "Please select a valid Excel or CSV file.")
                return
                
            # Check if required columns exist
            required_columns = ["Mail ID", "Unique Accounts", "Co. Name", "CC"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                messagebox.showerror("Missing Columns", 
                                   f"The following required columns are missing: {', '.join(missing_columns)}\n\n"
                                   f"Please ensure your Excel file has these columns: {', '.join(required_columns)}")
                return
                
            # Clean data - replace NaN with empty strings
            df = df.fillna("")
            
            # Remove blank first row if present
            if df.iloc[0].isnull().all() or (df.iloc[0] == "").all():
                df = df.iloc[1:].reset_index(drop=True)
            
            # Fix account numbers - remove any decimal points that might have been added
            if "Unique Accounts" in df.columns:
                df["Unique Accounts"] = df["Unique Accounts"].apply(
                    lambda x: str(x).rstrip('.0') if str(x).endswith('.0') else str(x)
                )
            
            # Remove entirely empty rows
            df = df[~df.apply(lambda row: all(str(cell).strip() == "" for cell in row), axis=1)]
            
            # Get current data
            current_data = self.sheet.get_sheet_data()
            
            # Convert current data to DataFrame
            current_df = pd.DataFrame(current_data, columns=required_columns)
            
            # Combine data
            combined_df = pd.concat([current_df, df], ignore_index=True)
            
            # Automatically remove duplicates based on Mail ID
            original_count = len(combined_df)
            combined_df = combined_df.drop_duplicates(subset=["Mail ID"], keep="first")
            duplicates_removed = original_count - len(combined_df)
            
            # Convert back to list format for sheet
            data = combined_df.values.tolist()
            
            # Ensure we have at least 50 rows
            while len(data) < 50:
                data.append(["", "", "", ""])
                
            # Update sheet
            self.sheet.set_sheet_data(data[:50])
            
            # Update parent DataFrame
            self.parent.mailing_data_df = combined_df
            self.parent.data_info_label.configure(text=f"{len(combined_df)} recipients entered")
            
            # Save to file
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            combined_df.to_csv(self.data_file, index=False)
            
            # Show message with duplicate removal info
            message = f"Successfully imported {len(df)} recipients.\n"
            if duplicates_removed > 0:
                message += f"Removed {duplicates_removed} duplicate entries.\n"
            message += f"Total recipients: {len(combined_df)}"
            
            messagebox.showinfo("Import Successful", message)
            
        except Exception as e:
            logging.error(f"Failed to import Excel file: {e}")
            messagebox.showerror("Import Error", f"Failed to import Excel file: {str(e)}")

class MailStatusMonitor(ctk.CTkToplevel):
    def __init__(self, parent, mailing_data_df, pdf_files, single_attachment=None):
        super().__init__(parent)
        self.parent = parent
        self.mailing_data_df = mailing_data_df
        self.pdf_files = pdf_files  # Store the PDF files
        self.single_attachment = single_attachment  # Store the single attachment path
        self.title("Mail Status Monitor")
        self.geometry("700x500")
        self.resizable(False, False)
        self.transient(parent)
        
        self.total_messages = 0
        self.delivered_count = 0
        self.sending_count = 0
        self.failed_count = 0
        self.is_paused = False
        self.is_cancelled = False
        self.message_index = 0
        self.log_entries = []  # Store log entries for export
        
        # Track sent emails to prevent duplicates
        self.sent_emails = set()  # (email, attachment_hash) tuples
        self.attachment_mode = "folder" if pdf_files else "single" if single_attachment else "none"
        
        self.create_widgets()
        
    def create_widgets(self):
        self.header = ctk.CTkLabel(self, text="Live Mailing Status Notification",
                                  font=ctk.CTkFont("Arial", 14, "bold"),
                                  fg_color="#2563eb", text_color="white", height=40)
        self.header.pack(fill="x")
        
        self.toolbar = ctk.CTkFrame(self, fg_color="#e5e7eb")
        self.toolbar.pack(fill="x", pady=5)
        
        self.status_counts = ctk.CTkLabel(self.toolbar, text="",
                                        fg_color="#e5e7eb", text_color="black", anchor="w",
                                        font=ctk.CTkFont("Arial", 12))
        self.status_counts.pack(side="left", padx=10)
        
        self.export_btn = ctk.CTkButton(self.toolbar, text="Export", width=80,
                                      command=self.export_log, fg_color="#28a745")
        self.export_btn.pack(side="right", padx=5)
        
        self.pause_btn = ctk.CTkButton(self.toolbar, text="Pause", width=80,
                                      command=self.toggle_pause, fg_color="#ffc107")
        self.pause_btn.pack(side="right", padx=5)
        
        self.cancel_btn = ctk.CTkButton(self.toolbar, text="Cancel", width=80,
                                       command=self.cancel_sending, fg_color="#dc3545")
        self.cancel_btn.pack(side="right", padx=5)
        
        self.clear_btn = ctk.CTkButton(self.toolbar, text="Clear Log", width=80,
                                      command=self.clear_log)
        self.clear_btn.pack(side="right", padx=5)
        
        self.progress_frame = ctk.CTkFrame(self, fg_color="#f8f9fa")
        self.progress_frame.pack(fill="x", padx=10, pady=5)
        
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="Progress: 0%", 
                                          font=ctk.CTkFont("Arial", 11))
        self.progress_label.pack(side="left", padx=10)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, mode="determinate")
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=10)
        self.progress_bar.set(0)
        
        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.log = ctk.CTkTextbox(self.log_frame, state='disabled', wrap="word",
                                 height=320, font=ctk.CTkFont("Courier New", 10))
        self.log.pack(fill="both", expand=True, side="left")
        
        log_scroll = ctk.CTkScrollbar(self.log_frame, command=self.log.yview)
        log_scroll.pack(side="right", fill="y")
        self.log.configure(yscrollcommand=log_scroll.set)
        
        self.footer = ctk.CTkLabel(self, text="System Active | Last update: Just now",
                                  font=ctk.CTkFont("Arial", 10), fg_color="#f9fafb")
        self.footer.pack(fill="x", padx=10, pady=5)
        
        self.update_counts()
        
    def log_message(self, icon, message, detail):
        self.after(0, lambda: self._log_message(icon, message, detail))
        
    def _log_message(self, icon, message, detail):
        current_datetime = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        text = f"{icon} [{current_datetime}] {message}\n    → {detail}\n\n"
        
        # Store log entry for export
        self.log_entries.append({
            "datetime": current_datetime,
            "icon": icon,
            "message": message,
            "detail": detail
        })
        
        self.log.configure(state='normal')
        self.log.insert("end", text)
        self.log.see("end")
        self.log.configure(state='disabled')
        
    def update_counts(self):
        text = f"Total: {self.total_messages} | Delivered: {self.delivered_count} | Sending: {self.sending_count} | Failed: {self.failed_count}"
        self.status_counts.configure(text=text)
        current_datetime = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        self.footer.configure(text=f"System Active | Last update: {current_datetime}")
        
        if self.total_messages > 0:
            progress = (self.delivered_count + self.failed_count) / self.total_messages
            self.progress_bar.set(progress)
            self.progress_label.configure(text=f"Progress: {int(progress * 100)}%")
        
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.pause_btn.configure(text="Resume" if self.is_paused else "Pause")
        self.log_message("⏸️" if self.is_paused else "▶️", 
                       "Mailing paused" if self.is_paused else "Mailing resumed",
                       "Process is " + ("paused" if self.is_paused else "running"))
        
    def cancel_sending(self):
        if messagebox.askyesno("Confirm Cancel", "Are you sure you want to cancel the mailing process?"):
            self.is_cancelled = True
            self.log_message("⚠️", "Cancelling...", "Mailing process is being cancelled.")
            self.pause_btn.configure(state="disabled")
            self.cancel_btn.configure(state="disabled")
            
    def clear_log(self):
        self.log.configure(state='normal')
        self.log.delete("1.0", "end")
        self.log.configure(state='disabled')
        self.total_messages = 0
        self.delivered_count = 0
        self.sending_count = 0
        self.failed_count = 0
        self.message_index = 0
        self.log_entries = []  # Clear stored log entries
        self.update_counts()
        
    def export_to_txt(self, file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("AutoMail Pro - Mailing Log\n")
            f.write("=" * 50 + "\n\n")
            
            for entry in self.log_entries:
                f.write(f"[{entry['datetime']}] {entry['icon']} {entry['message']}\n")
                f.write(f"    → {entry['detail']}\n\n")
                
            # Add summary at the end
            f.write("\n" + "=" * 50 + "\n")
            f.write("SUMMARY\n")
            f.write("=" * 50 + "\n")
            f.write(f"Total Messages: {self.total_messages}\n")
            f.write(f"Delivered: {self.delivered_count}\n")
            f.write(f"Failed: {self.failed_count}\n")
            if self.total_messages > 0:
                success_rate = (self.delivered_count / self.total_messages) * 100
                f.write(f"Success Rate: {success_rate:.2f}%\n")
                
    def export_to_csv(self, file_path):
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Date & Time", "Status", "Message", "Details"])
            
            for entry in self.log_entries:
                writer.writerow([
                    entry['datetime'],
                    entry['icon'],
                    entry['message'],
                    entry['detail']
                ])
                
            # Add summary row
            writer.writerow([])
            writer.writerow(["SUMMARY"])
            writer.writerow(["Total Messages", self.total_messages])
            writer.writerow(["Delivered", self.delivered_count])
            writer.writerow(["Failed", self.failed_count])
            if self.total_messages > 0:
                success_rate = (self.delivered_count / self.total_messages) * 100
                writer.writerow(["Success Rate", f"{success_rate:.2f}%"])
                
    def export_to_pdf(self, file_path):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "AutoMail Pro - Mailing Log", 0, 1, 'C')
            pdf.ln(10)
            
            pdf.set_font("Arial", '', 12)
            
            for entry in self.log_entries:
                # Handle special characters by encoding to latin-1 and replacing unsupported characters
                def safe_text(text):
                    return text.encode('latin-1', 'replace').decode('latin-1')
                
                datetime_str = safe_text(entry['datetime'])
                icon_str = safe_text(entry['icon'])
                message_str = safe_text(entry['message'])
                detail_str = safe_text(entry['detail'])
                
                # Write datetime and status icon
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(0, 6, f"[{datetime_str}] {icon_str} {message_str}", 0, 1)
                
                # Write detail with indentation
                pdf.set_font("Arial", '', 10)
                pdf.cell(10, 6, "", 0, 0)
                pdf.multi_cell(0, 6, f"→ {detail_str}")
                pdf.ln(2)
            
            # Add summary
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 6, "SUMMARY", 0, 1)
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 6, f"Total Messages: {self.total_messages}", 0, 1)
            pdf.cell(0, 6, f"Delivered: {self.delivered_count}", 0, 1)
            pdf.cell(0, 6, f"Failed: {self.failed_count}", 0, 1)
            if self.total_messages > 0:
                success_rate = (self.delivered_count / self.total_messages) * 100
                pdf.cell(0, 6, f"Success Rate: {success_rate:.2f}%", 0, 1)
                
            pdf.output(file_path, 'F')
        except Exception as e:
            logging.error(f"PDF export failed: {str(e)}")
            raise Exception(f"PDF export failed: {str(e)}")
    
    def generate_export_files(self, base_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"mailing_log_{timestamp}"
        
        txt_path = os.path.join(base_path, f"{base_filename}.txt")
        csv_path = os.path.join(base_path, f"{base_filename}.csv")
        pdf_path = os.path.join(base_path, f"{base_filename}.pdf")
        
        self.export_to_txt(txt_path)
        self.export_to_csv(csv_path)
        
        # Try to generate PDF, but don't fail if it doesn't work
        try:
            self.export_to_pdf(pdf_path)
        except Exception as e:
            logging.warning(f"PDF generation failed, but continuing with other formats: {e}")
        
        # Return only the files that were successfully created
        file_paths = []
        if os.path.exists(txt_path):
            file_paths.append(txt_path)
        if os.path.exists(csv_path):
            file_paths.append(csv_path)
        if os.path.exists(pdf_path):
            file_paths.append(pdf_path)
        
        return file_paths
    
    def send_export_email(self, to_email, cc_email, file_paths):
        # Check if we're using SMTP or API
        if self.parent.smtp_api_toggle.get() == "SMTP":
            smtp_config = getattr(self.parent, 'smtp_config', None)
            if not smtp_config:
                messagebox.showerror("SMTP Error", "SMTP configuration not found.")
                return False
            
            smtp_server = smtp_config.get("smtp_server", "")
            port_str = smtp_config.get("port", "")
            sender_email = smtp_config.get("email", "")
            sender_password = smtp_config.get("password", "")
            encryption = smtp_config.get("encryption", "TLS")
            custom_from = smtp_config.get("custom_from", "")
            
            try:
                port = int(port_str)
            except ValueError:
                messagebox.showerror("Error", "Invalid SMTP port.")
                return False
            
            try:
                if encryption == "SSL":
                    server = smtplib.SMTP_SSL(smtp_server, port)
                    server.login(sender_email, sender_password)
                else:  # TLS
                    server = smtplib.SMTP(smtp_server, port)
                    server.starttls()
                    server.login(sender_email, sender_password)
                
                # Create message
                msg = MIMEMultipart('mixed')
                
                from_address = custom_from if custom_from else sender_email
                msg['From'] = from_address
                if custom_from:
                    msg['Sender'] = sender_email
                    msg['Reply-To'] = sender_email
                
                msg['To'] = to_email
                if cc_email:
                    msg['Cc'] = cc_email
                msg['Subject'] = "AutoMail Pro - Export Log"
                
                # Add body
                body = "Dear Sir/Ma'am,\n\nPlease find the attached export files for your reference.\n\nThis is an auto-generated email, sent after all emails have been successfully delivered."
                msg.attach(MIMEText(body, 'plain'))
                
                # Attach files
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        filename = os.path.basename(file_path)
                        with open(file_path, 'rb') as f:
                            part = MIMEApplication(f.read(), Name=filename)
                        part['Content-Disposition'] = f'attachment; filename="{filename}"'
                        msg.attach(part)
                    else:
                        logging.warning(f"Attachment file not found: {file_path}")
                
                recipients = [to_email]
                if cc_email:
                    recipients.extend([addr.strip() for addr in cc_email.split(',') if addr.strip()])
                
                server.sendmail(sender_email, recipients, msg.as_string())
                server.quit()
                return True
            except Exception as e:
                logging.error(f"Failed to send export email: {e}")
                messagebox.showerror("Error", f"Failed to send email: {str(e)}")
                return False
        
        else:  # API mode
            api_config = getattr(self.parent, 'api_config', None)
            if not api_config:
                messagebox.showerror("API Error", "API configuration not found.")
                return False
            
            api_endpoint = api_config.get("api_endpoint", "")
            api_key = api_config.get("api_key", "")
            api_method = api_config.get("api_method", "POST")
            custom_from = api_config.get("custom_from", "")
            
            try:
                # Create message
                msg = MIMEMultipart('mixed')
                
                from_address = custom_from if custom_from else "api@automailpro.com"
                msg['From'] = from_address
                msg['To'] = to_email
                if cc_email:
                    msg['Cc'] = cc_email
                msg['Subject'] = "AutoMail Pro - Export Log"
                
                # Add body
                body = "Dear Sir/Ma'am,\n\nPlease find the attached export files for your reference.\n\nThis is an auto-generated email, sent after all emails have been successfully delivered."
                msg.attach(MIMEText(body, 'plain'))
                
                # Attach files
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        filename = os.path.basename(file_path)
                        with open(file_path, 'rb') as f:
                            part = MIMEApplication(f.read(), Name=filename)
                        part['Content-Disposition'] = f'attachment; filename="{filename}"'
                        msg.attach(part)
                    else:
                        logging.warning(f"Attachment file not found: {file_path}")
                
                # Prepare API request
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                # Create email data
                email_data = {
                    "from": from_address,
                    "to": to_email,
                    "cc": cc_email if cc_email else None,
                    "subject": "AutoMail Pro - Export Log",
                    "body": body,
                    "attachments": []
                }
                
                # Add attachments to email data
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        filename = os.path.basename(file_path)
                        with open(file_path, 'rb') as f:
                            file_content = f.read()
                            # Encode as base64 for JSON
                            import base64
                            file_b64 = base64.b64encode(file_content).decode('utf-8')
                            email_data["attachments"].append({
                                "filename": filename,
                                "content": file_b64
                            })
                
                # Send API request
                if api_method == "POST":
                    response = requests.post(api_endpoint, json=email_data, headers=headers, timeout=30)
                else:  # PUT
                    response = requests.put(api_endpoint, json=email_data, headers=headers, timeout=30)
                
                if response.status_code in [200, 201, 202]:
                    return True
                else:
                    logging.error(f"API returned status code: {response.status_code}")
                    logging.error(f"Response: {response.text}")
                    return False
            except Exception as e:
                logging.error(f"Failed to send export email via API: {e}")
                messagebox.showerror("Error", f"Failed to send email: {str(e)}")
                return False
    
    def export_log(self):
        if not self.log_entries:
            messagebox.showwarning("No Data", "No log data to export.")
            return
        
        # Create the export dialog
        export_dialog = ctk.CTkToplevel(self)
        export_dialog.title("Export Options")
        export_dialog.geometry("400x150")
        export_dialog.resizable(False, False)
        export_dialog.transient(self)
        export_dialog.grab_set()
        
        # Center the dialog
        export_dialog.update_idletasks()
        width = export_dialog.winfo_width()
        height = export_dialog.winfo_height()
        x = (export_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (export_dialog.winfo_screenheight() // 2) - (height // 2)
        export_dialog.geometry(f"+{x}+{y}")
        
        main_frame = ctk.CTkFrame(export_dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text="Do you want to send the export via email?",
                    font=ctk.CTkFont("Arial", 12)).pack(pady=10)
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack()
        
        user_choice = {"value": None}
        
        def on_yes():
            user_choice["value"] = "email"
            export_dialog.destroy()
        
        def on_no():
            user_choice["value"] = "download"
            export_dialog.destroy()
        
        def on_both():
            user_choice["value"] = "both"
            export_dialog.destroy()
        
        ctk.CTkButton(button_frame, text="Yes", width=80, command=on_yes).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="No", width=80, command=on_no).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Both", width=80, command=on_both).pack(side="left", padx=5)
        
        export_dialog.wait_window()
        
        choice = user_choice["value"]
        if choice is None:
            return  # User closed the dialog
        
        # Show progress dialog
        progress_dialog = ctk.CTkToplevel(self)
        progress_dialog.title("Exporting")
        progress_dialog.geometry("300x100")
        progress_dialog.resizable(False, False)
        progress_dialog.transient(self)
        progress_dialog.grab_set()
        
        # Center the progress dialog
        progress_dialog.update_idletasks()
        width = progress_dialog.winfo_width()
        height = progress_dialog.winfo_height()
        x = (progress_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (progress_dialog.winfo_screenheight() // 2) - (height // 2)
        progress_dialog.geometry(f"+{x}+{y}")
        
        progress_label = ctk.CTkLabel(progress_dialog, text="Generating export files...")
        progress_label.pack(pady=20)
        
        # Update the UI
        self.update()
        
        try:
            if choice == "download":
                # Save to desktop
                desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
                file_paths = self.generate_export_files(desktop_path)
                progress_dialog.destroy()
                messagebox.showinfo("Success", f"Files saved to your desktop in PDF, TXT, and CSV formats.")
            
            elif choice == "email":
                # Show email entry popup
                progress_dialog.destroy()
                email_dialog = ctk.CTkToplevel(self)
                email_dialog.title("Send Export via Email")
                email_dialog.geometry("400x200")
                email_dialog.resizable(False, False)
                email_dialog.transient(self)
                email_dialog.grab_set()
                
                # Center the dialog
                email_dialog.update_idletasks()
                width = email_dialog.winfo_width()
                height = email_dialog.winfo_height()
                x = (email_dialog.winfo_screenwidth() // 2) - (width // 2)
                y = (email_dialog.winfo_screenheight() // 2) - (height // 2)
                email_dialog.geometry(f"+{x}+{y}")
                
                main_frame = ctk.CTkFrame(email_dialog)
                main_frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                ctk.CTkLabel(main_frame, text="To (required):", font=ctk.CTkFont("Arial", 12)).pack(anchor="w")
                to_entry = ctk.CTkEntry(main_frame, width=300)
                to_entry.pack(pady=(0, 10))
                
                ctk.CTkLabel(main_frame, text="CC (optional):", font=ctk.CTkFont("Arial", 12)).pack(anchor="w")
                cc_entry = ctk.CTkEntry(main_frame, width=300)
                cc_entry.pack(pady=(0, 20))
                
                button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
                button_frame.pack()
                
                def on_send():
                    to_email = to_entry.get().strip()
                    cc_email = cc_entry.get().strip()
                    
                    if not to_email:
                        messagebox.showwarning("Missing Information", "Please enter a recipient email.")
                        return
                    
                    # Validate email format
                    if not re.match(r"[^@]+@[^@]+\.[^@]+", to_email):
                        messagebox.showwarning("Invalid Email", "Please enter a valid recipient email.")
                        return
                    
                    if cc_email and not all(re.match(r"[^@]+@[^@]+\.[^@]+", email.strip()) for email in cc_email.split(',')):
                        messagebox.showwarning("Invalid CC Email", "Please enter valid CC email addresses.")
                        return
                    
                    # Generate files in a temporary directory
                    temp_dir = tempfile.mkdtemp()
                    try:
                        # Show progress dialog
                        progress_dialog = ctk.CTkToplevel(email_dialog)
                        progress_dialog.title("Sending")
                        progress_dialog.geometry("300x100")
                        progress_dialog.resizable(False, False)
                        progress_dialog.transient(email_dialog)
                        progress_dialog.grab_set()
                        
                        # Center the progress dialog
                        progress_dialog.update_idletasks()
                        width = progress_dialog.winfo_width()
                        height = progress_dialog.winfo_height()
                        x = (progress_dialog.winfo_screenwidth() // 2) - (width // 2)
                        y = (progress_dialog.winfo_screenheight() // 2) - (height // 2)
                        progress_dialog.geometry(f"+{x}+{y}")
                        
                        progress_label = ctk.CTkLabel(progress_dialog, text="Generating and sending files...")
                        progress_label.pack(pady=20)
                        
                        # Update the UI
                        self.update()
                        
                        file_paths = self.generate_export_files(temp_dir)
                        if self.send_export_email(to_email, cc_email, file_paths):
                            progress_dialog.destroy()
                            email_dialog.destroy()
                            messagebox.showinfo("Success", "Email sent successfully with all file formats.")
                        else:
                            progress_dialog.destroy()
                            messagebox.showerror("Error", "Failed to send email.")
                    finally:
                        # Clean up temporary files
                        shutil.rmtree(temp_dir, ignore_errors=True)
                
                def on_cancel():
                    email_dialog.destroy()
                
                ctk.CTkButton(button_frame, text="Send", width=80, command=on_send).pack(side="left", padx=5)
                ctk.CTkButton(button_frame, text="Cancel", width=80, command=on_cancel).pack(side="left", padx=5)
                
                email_dialog.wait_window()
            
            elif choice == "both":
                # First, save to desktop
                desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
                file_paths = self.generate_export_files(desktop_path)
                
                # Then, show email entry popup
                progress_dialog.destroy()
                email_dialog = ctk.CTkToplevel(self)
                email_dialog.title("Send Export via Email")
                email_dialog.geometry("400x200")
                email_dialog.resizable(False, False)
                email_dialog.transient(self)
                email_dialog.grab_set()
                
                # Center the dialog
                email_dialog.update_idletasks()
                width = email_dialog.winfo_width()
                height = email_dialog.winfo_height()
                x = (email_dialog.winfo_screenwidth() // 2) - (width // 2)
                y = (email_dialog.winfo_screenheight() // 2) - (height // 2)
                email_dialog.geometry(f"+{x}+{y}")
                
                main_frame = ctk.CTkFrame(email_dialog)
                main_frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                ctk.CTkLabel(main_frame, text="To (required):", font=ctk.CTkFont("Arial", 12)).pack(anchor="w")
                to_entry = ctk.CTkEntry(main_frame, width=300)
                to_entry.pack(pady=(0, 10))
                
                ctk.CTkLabel(main_frame, text="CC (optional):", font=ctk.CTkFont("Arial", 12)).pack(anchor="w")
                cc_entry = ctk.CTkEntry(main_frame, width=300)
                cc_entry.pack(pady=(0, 20))
                
                button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
                button_frame.pack()
                
                def on_send():
                    to_email = to_entry.get().strip()
                    cc_email = cc_entry.get().strip()
                    
                    if not to_email:
                        messagebox.showwarning("Missing Information", "Please enter a recipient email.")
                        return
                    
                    # Validate email format
                    if not re.match(r"[^@]+@[^@]+\.[^@]+", to_email):
                        messagebox.showwarning("Invalid Email", "Please enter a valid recipient email.")
                        return
                    
                    if cc_email and not all(re.match(r"[^@]+@[^@]+\.[^@]+", email.strip()) for email in cc_email.split(',')):
                        messagebox.showwarning("Invalid CC Email", "Please enter valid CC email addresses.")
                        return
                    
                    # Show progress dialog
                    progress_dialog = ctk.CTkToplevel(email_dialog)
                    progress_dialog.title("Sending")
                    progress_dialog.geometry("300x100")
                    progress_dialog.resizable(False, False)
                    progress_dialog.transient(email_dialog)
                    progress_dialog.grab_set()
                    
                    # Center the progress dialog
                    progress_dialog.update_idletasks()
                    width = progress_dialog.winfo_width()
                    height = progress_dialog.winfo_height()
                    x = (progress_dialog.winfo_screenwidth() // 2) - (width // 2)
                    y = (progress_dialog.winfo_screenheight() // 2) - (height // 2)
                    progress_dialog.geometry(f"+{x}+{y}")
                    
                    progress_label = ctk.CTkLabel(progress_dialog, text="Sending files...")
                    progress_label.pack(pady=20)
                    
                    # Update the UI
                    self.update()
                    
                    if self.send_export_email(to_email, cc_email, file_paths):
                        progress_dialog.destroy()
                        email_dialog.destroy()
                        messagebox.showinfo("Success", "Email sent successfully with all file formats. Files are also saved to your desktop.")
                    else:
                        progress_dialog.destroy()
                        messagebox.showerror("Error", "Failed to send email. Files are saved to your desktop.")
                
                def on_cancel():
                    email_dialog.destroy()
                
                ctk.CTkButton(button_frame, text="Send", width=80, command=on_send).pack(side="left", padx=5)
                ctk.CTkButton(button_frame, text="Cancel", width=80, command=on_cancel).pack(side="left", padx=5)
                
                email_dialog.wait_window()
        except Exception as e:
            progress_dialog.destroy()
            logging.error(f"Export failed: {e}")
            messagebox.showerror("Error", f"Export failed: {str(e)}")
        
    def save_eml_file(self, msg, email, subject):
        """Save the sent email as an .eml file"""
        try:
            # Create directory for sent emails if it doesn't exist
            sent_emails_dir = os.path.join(os.path.expanduser("~/.cpc_mailing/sent_emails"))
            os.makedirs(sent_emails_dir, exist_ok=True)
            
            # Generate a unique filename based on timestamp and recipient
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Clean email address to use in filename
            clean_email = re.sub(r'[^\w\-_.@]', '_', email)
            filename = f"{timestamp}_{clean_email}.eml"
            file_path = os.path.join(sent_emails_dir, filename)
            
            # Write the email content to the file
            with open(file_path, 'wb') as f:
                f.write(msg.as_bytes())
            
            return file_path
        except Exception as e:
            logging.error(f"Failed to save .eml file: {e}")
            return None
        
    def get_attachment_hash(self, file_path):
        """Generate a hash for the attachment file to track duplicates"""
        if not file_path or not os.path.exists(file_path):
            return "no_attachment"
        
        # Use file path and size for hashing
        file_stat = os.stat(file_path)
        hash_data = f"{file_path}_{file_stat.st_size}_{file_stat.st_mtime}"
        return hashlib.md5(hash_data.encode()).hexdigest()
    
    def validate_email_format(self, email):
        """Comprehensive email validation"""
        if not email or '@' not in email:
            return False
        
        username, domain = email.split('@', 1)
        
        # Validate username part
        if not re.match(r'^[a-zA-Z0-9._%+-]+$', username):
            return False
        
        # Validate domain part
        if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', domain):
            return False
        
        # Check for common typos in domain
        common_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'rediffmail.com']
        for common in common_domains:
            if domain.replace('.', '').replace('-', '') == common.replace('.', '').replace('-', ''):
                return True  # Close enough, likely a typo
        
        return True
    
    def process_emails(self):
        def worker():
            # Check if we're using SMTP or API
            if self.parent.smtp_api_toggle.get() == "SMTP":
                smtp_config = getattr(self.parent, 'smtp_config', None)
                if not smtp_config:
                    self.log_message("⚠️", "SMTP Configuration Error", "Please configure SMTP settings.")
                    return
                    
                smtp_server = smtp_config.get("smtp_server", "")
                port_str = smtp_config.get("port", "")
                sender_email = smtp_config.get("email", "")
                sender_password = smtp_config.get("password", "")
                encryption = smtp_config.get("encryption", "TLS")
                custom_from = smtp_config.get("custom_from", "")
                
                if not all([smtp_server, port_str, sender_email, sender_password]):
                    self.log_message("⚠️", "SMTP Configuration Error", "Please fill in all SMTP settings.")
                    return
                    
                try:
                    port = int(port_str)
                    if not (0 <= port <= 65535):
                        raise ValueError("Port number must be between 0 and 65535")
                except ValueError:
                    self.log_message("⚠️", "Invalid Port", "Please enter a valid port number (0-65535).")
                    return
                    
                try:
                    if encryption == "SSL":
                        # Check if port 465 is being used and warn about firewall issues
                        if port == 465:
                            self.log_message("⚠️", "Using SSL on Port 465", 
                                           "This port is often blocked by firewalls. If connection fails, try TLS (port 587).")
                        
                        server = smtplib.SMTP_SSL(smtp_server, port, timeout=30)
                        server.login(sender_email, sender_password)
                    else:  # TLS
                        server = smtplib.SMTP(smtp_server, port, timeout=30)
                        server.starttls()
                        server.login(sender_email, sender_password)
                    self.log_message("✅", "SMTP Connected", f"Successfully connected to {smtp_server}")
                except ValueError:
                    self.log_message("⚠️", "Invalid Port", "Port is not a valid integer.")
                    return
                except smtplib.SMTPAuthenticationError:
                    self.log_message("⚠️", "Authentication Failed", "Check your email and password. For Gmail/Outlook, use an app password.")
                    return
                except socket.timeout:
                    self.log_message("⚠️", "Connection Timeout", 
                                    f"Connection to {smtp_server}:{port} timed out. Check network and firewall settings.")
                    return
                except socket.error as e:
                    if "10013" in str(e):
                        self.log_message("⚠️", "Firewall Blocking Port", 
                                       "Access denied (Error 10013). This is likely due to a firewall blocking port 465.\n\n"
                                       "Solutions:\n"
                                       "1. Try using TLS (port 587) instead of SSL\n"
                                       "2. Add Python to firewall exceptions\n"
                                       "3. Temporarily disable antivirus software")
                    else:
                        self.log_message("⚠️", "Socket Error", f"Socket error: {str(e)}")
                    return
                except smtplib.SMTPException as e:
                    self.log_message("⚠️", "SMTP Connection Failed", f"SMTP Error: {str(e)}")
                    return
                except Exception as e:
                    self.log_message("⚠️", "SMTP Connection Failed", f"Unexpected error: {str(e)}")
                    return
            else:  # API mode
                api_config = getattr(self.parent, 'api_config', None)
                if not api_config:
                    self.log_message("⚠️", "API Configuration Error", "Please configure API settings.")
                    return
                    
                api_endpoint = api_config.get("api_endpoint", "")
                api_key = api_config.get("api_key", "")
                api_method = api_config.get("api_method", "POST")
                custom_from = api_config.get("custom_from", "")
                
                if not all([api_endpoint, api_key]):
                    self.log_message("⚠️", "API Configuration Error", "Please fill in all API settings.")
                    return
                    
                self.log_message("✅", "API Ready", f"Using {api_method} method with endpoint: {api_endpoint[:30]}...")
                
            try:
                # Process each recipient
                for index, row in self.mailing_data_df.iterrows():
                    if self.is_cancelled:
                        self.log_message("⚠️", "Cancelled", "Mailing process was cancelled by user.")
                        break
                        
                    if self.is_paused:
                        while self.is_paused and not self.is_cancelled:
                            time.sleep(0.5)
                        if self.is_cancelled:
                            continue
                        
                    email = row['Mail ID']
                    sap_id = str(row['Unique Accounts']).strip()  # Unique account identifier
                    cc = row['CC'] if pd.notna(row['CC']) and row['CC'].strip() else ""
                    company_name = row['Co. Name'] if pd.notna(row['Co. Name']) else ""
                    
                    self.total_messages += 1
                    self.sending_count += 1
                    
                    # Validate email format
                    if not self.validate_email_format(email):
                        self.log_message("⚠️", f"Invalid email format: {email}", 
                                       "Email address is not in a valid format")
                        self.sending_count -= 1
                        self.failed_count += 1
                        self.update_counts()
                        continue
                    
                    # Determine attachment based on mode
                    attachment_path = None
                    attachment_info = ""
                    
                    if self.attachment_mode == "folder":
                        # Folder mode: attachment is mandatory
                        if sap_id and self.pdf_files:
                            # Look for PDF that matches the unique account ID
                            for pdf_file in self.pdf_files:
                                filename = os.path.splitext(os.path.basename(pdf_file))[0]
                                if sap_id.lower() in filename.lower():
                                    attachment_path = pdf_file
                                    break
                            
                            if attachment_path:
                                attachment_info = f"✓ PDF attached: {os.path.basename(attachment_path)}"
                            else:
                                # Exact message as required
                                attachment_info = "this mail ID attachment missing based on unique account"
                                self.log_message("⚠️", f"Skipping {email}", attachment_info)
                                self.sending_count -= 1
                                self.failed_count += 1
                                self.update_counts()
                                continue
                        else:
                            attachment_info = f"⚠️ No unique account ID provided"
                            self.log_message("⚠️", f"Skipping {email}", attachment_info)
                            self.sending_count -= 1
                            self.failed_count += 1
                            self.update_counts()
                            continue
                    
                    elif self.attachment_mode == "single":
                        # Single file mode: attach the selected file to all
                        if self.single_attachment and os.path.exists(self.single_attachment):
                            attachment_path = self.single_attachment
                            attachment_info = f"✓ File attached: {os.path.basename(attachment_path)}"
                        else:
                            attachment_info = f"⚠️ Selected file not found"
                            self.log_message("⚠️", f"Skipping {email}", attachment_info)
                            self.sending_count -= 1
                            self.failed_count += 1
                            self.update_counts()
                            continue
                    
                    else:
                        # No attachment mode
                        attachment_info = "No attachment"
                    
                    # Check for duplicates
                    attachment_hash = self.get_attachment_hash(attachment_path)
                    duplicate_key = (email, attachment_hash)
                    
                    if duplicate_key in self.sent_emails:
                        self.log_message("⚠️", f"Skipping {email}", 
                                       f"Duplicate: already sent to this recipient with this attachment")
                        self.sending_count -= 1
                        self.failed_count += 1
                        self.update_counts()
                        continue
                    
                    self.log_message("📧", f"Email queued for {email}", attachment_info)
                    self.update_counts()
                    
                    try:
                        # Create placeholder map for subject and body
                        placeholder_map = {
                            "[{ Mail ID }]": email,
                            "[{ Unique Accounts }]": sap_id,
                            "[{ Co. Name }]": company_name,
                            "[{ CC }]": cc
                        }
                        
                        # Process subject with placeholders
                        subject = self.parent.subject_entry.get().strip()
                        for placeholder, value in placeholder_map.items():
                            subject = subject.replace(placeholder, str(value))
                        
                        # Get both plain text and HTML from rich text editor
                        if self.parent.rich_text_editor.text_area.tag_ranges("sel"):
                            body_text = self.parent.rich_text_editor.get_selected_text()
                            body_html = self.parent.rich_text_editor.get_html()
                        else:
                            body_text = self.parent.rich_text_editor.get_text()
                            body_html = self.parent.rich_text_editor.get_html()
                        
                        # Replace placeholders in email body
                        for placeholder, value in placeholder_map.items():
                            body_text = body_text.replace(placeholder, str(value))
                            body_html = body_html.replace(placeholder, str(value))
                        
                        # Add signature and disclaimer if they exist
                        if self.parent.signature:
                            body_text += f"\n\n{self.parent.signature}"
                            body_html += f"<br><br>{self.parent.signature.replace('\n', '<br>')}"
                        
                        if self.parent.disclaimer:
                            body_text += f"\n\n{self.parent.disclaimer}"
                            body_html += f"<br><br>{self.parent.disclaimer.replace('\n', '<br>')}"
                        
                        # Check if we're using SMTP or API
                        if self.parent.smtp_api_toggle.get() == "SMTP":
                            # Create the root message with mixed type
                            msg = MIMEMultipart('mixed')
                            
                            # Use custom From address if provided, otherwise use the authenticated email
                            from_address = custom_from if custom_from else sender_email
                            msg['From'] = from_address
                            
                            # Add Sender header to prevent spoofing issues when using custom From
                            if custom_from:
                                msg['Sender'] = sender_email
                                msg['Reply-To'] = sender_email
                            
                            msg['To'] = email
                            if cc:
                                msg['Cc'] = cc
                            
                            # Add Date header
                            msg['Date'] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
                            
                            # Add Message-ID header
                            msg['Message-ID'] = f"<{datetime.now().strftime('%Y%m%d%H%M%S')}@{sender_email.split('@')[-1]}>"
                            
                            # Add essential headers to improve deliverability
                            msg['X-Priority'] = '3'  # Normal priority
                            msg['X-Mailer'] = 'AutoMail Pro'
                            msg['MIME-Version'] = '1.0'
                            
                            # Set subject
                            msg['Subject'] = subject
                            
                            # Create the alternative part for the body
                            alt_msg = MIMEMultipart('alternative')
                            msg.attach(alt_msg)
                            
                            # Attach the plain text and HTML to the alternative part
                            # Use UTF-8 encoding for better international support
                            plain_text_part = MIMEText(body_text, 'plain', 'utf-8')
                            alt_msg.attach(plain_text_part)
                            
                            html_part = MIMEText(body_html, 'html', 'utf-8')
                            alt_msg.attach(html_part)
                            
                            # Add attachment if available
                            if attachment_path and os.path.exists(attachment_path):
                                filename = os.path.basename(attachment_path)
                                file_ext = os.path.splitext(filename)[1].lower()
                                
                                with open(attachment_path, 'rb') as attachment:
                                    if file_ext == '.pdf':
                                        part = MIMEApplication(attachment.read(), _subtype="pdf")
                                    elif file_ext in ['.jpg', '.jpeg']:
                                        part = MIMEApplication(attachment.read(), _subtype="jpeg")
                                    elif file_ext == '.png':
                                        part = MIMEApplication(attachment.read(), _subtype="png")
                                    elif file_ext == '.txt':
                                        part = MIMEApplication(attachment.read(), _subtype="plain")
                                    else:
                                        part = MIMEApplication(attachment.read())
                                    
                                    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                                    msg.attach(part)
                            
                            recipients = [email]
                            if cc:
                                recipients.extend([addr.strip() for addr in cc.split(',') if addr.strip()])
                                
                            # Enhanced email sending with better error handling for all domains
                            try:
                                server.sendmail(sender_email, recipients, msg.as_string())
                                
                                # Save the sent email as .eml file
                                eml_file_path = self.save_eml_file(msg, email, msg['Subject'])
                                
                                # Track sent email to prevent duplicates
                                self.sent_emails.add(duplicate_key)
                                
                                self.sending_count -= 1
                                self.delivered_count += 1
                                
                                self.log_message("✓", f"Email delivered to {email}",
                                               attachment_info + 
                                               (f"\n    → Saved as: {os.path.basename(eml_file_path)}" if eml_file_path else ""))
                            except smtplib.SMTPRecipientsRefused as e:
                                # Handle recipient refused error (happens with some domains)
                                self.sending_count -= 1
                                self.failed_count += 1
                                self.log_message("⚠️", f"Failed to send to {email}",
                                               f"Recipient refused: {str(e)}")
                                logging.error(f"Recipient refused for {email}: {str(e)}")
                            except smtplib.SMTPDataError as e:
                                # Handle data error (can happen with some email providers)
                                self.sending_count -= 1
                                self.failed_count += 1
                                self.log_message("⚠️", f"Failed to send to {email}",
                                               f"Data error: {str(e)}")
                                logging.error(f"Data error for {email}: {str(e)}")
                            except smtplib.SMTPHeloError as e:
                                # Handle HELO error (can happen with some email providers)
                                self.sending_count -= 1
                                self.failed_count += 1
                                self.log_message("⚠️", f"Failed to send to {email}",
                                               f"HELO error: {str(e)}")
                                logging.error(f"HELO error for {email}: {str(e)}")
                            except smtplib.SMTPException as e:
                                # General SMTP exception
                                self.sending_count -= 1
                                self.failed_count += 1
                                self.log_message("⚠️", f"Failed to send to {email}",
                                               f"SMTP error: {str(e)}")
                                logging.error(f"SMTP error for {email}: {str(e)}")
                        else:  # API mode
                            # Prepare API request
                            headers = {
                                "Authorization": f"Bearer {api_key}",
                                "Content-Type": "application/json"
                            }
                            
                            # Create email data
                            email_data = {
                                "from": custom_from if custom_from else "api@automailpro.com",
                                "to": email,
                                "cc": cc if cc else None,
                                "subject": subject,
                                "body_text": body_text,
                                "body_html": body_html
                            }
                            
                            # Add attachment if available
                            if attachment_path and os.path.exists(attachment_path):
                                filename = os.path.basename(attachment_path)
                                with open(attachment_path, 'rb') as attachment:
                                    file_content = attachment.read()
                                    # Encode as base64 for JSON
                                    import base64
                                    file_b64 = base64.b64encode(file_content).decode('utf-8')
                                    email_data["attachment"] = {
                                        "filename": filename,
                                        "content": file_b64
                                    }
                            
                            # Send API request
                            try:
                                if api_method == "POST":
                                    response = requests.post(api_endpoint, json=email_data, headers=headers, timeout=30)
                                else:  # PUT
                                    response = requests.put(api_endpoint, json=email_data, headers=headers, timeout=30)
                                
                                if response.status_code in [200, 201, 202]:
                                    # Track sent email to prevent duplicates
                                    self.sent_emails.add(duplicate_key)
                                    
                                    self.sending_count -= 1
                                    self.delivered_count += 1
                                    
                                    self.log_message("✓", f"Email delivered to {email}",
                                                   attachment_info)
                                else:
                                    self.sending_count -= 1
                                    self.failed_count += 1
                                    self.log_message("⚠️", f"Failed to send to {email}",
                                                   f"API returned status code: {response.status_code}")
                                    logging.error(f"API error for {email}: {response.status_code} - {response.text}")
                            except requests.exceptions.RequestException as e:
                                self.sending_count -= 1
                                self.failed_count += 1
                                self.log_message("⚠️", f"Failed to send to {email}",
                                               f"API request failed: {str(e)}")
                                logging.error(f"API request failed for {email}: {str(e)}")
                        
                    except Exception as e:
                        self.sending_count -= 1
                        self.failed_count += 1
                        self.log_message("⚠️", f"Failed to send to {email}",
                                       f"Error: {str(e)}")
                        logging.error(f"Failed to send to {email}: {str(e)}")
                        
                    self.update_counts()
                    time.sleep(1.0)  # Increased delay to avoid rate limiting
                    
                if not self.is_cancelled:
                    self.log_message("✅", "Mailing campaign completed",
                                   f"All {self.total_messages} emails processed")
                    self.pause_btn.configure(state="disabled")
                    self.cancel_btn.configure(state="disabled")
                    
            except Exception as e:
                self.log_message("⚠️", "Process Error", f"Unexpected error: {str(e)}")
                logging.error(f"Process Error: {str(e)}")
            finally:
                # Close SMTP connection if using SMTP
                if self.parent.smtp_api_toggle.get() == "SMTP":
                    try:
                        server.quit()
                    except:
                        pass
                    
        threading.Thread(target=worker, daemon=True).start()

class CPCMailingSystem(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AutoMail Pro")
        self.geometry("750x700")  # Increased height for larger body text field
        self.minsize(700, 650)
        self.selected_folder_path = None  # For folder selection
        self.selected_file_path = None  # For single file selection
        self.pdf_files = []  # Will store PDFs from selected folder
        self.mailing_data_df = None
        self.data_sheet_window = None
        self.smtp_config = None
        self.api_config = None
        self.signature = ""  # Store signature text
        self.disclaimer = ""  # Store disclaimer text
        self.app_config_file = os.path.join(os.path.expanduser("~/.cpc_mailing/data"), "app_config.json")
        self.load_app_config()
        self.load_signature_disclaimer()  # Load signature and disclaimer settings
        
        # Handle window close event
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Header frame
        header_frame = ctk.CTkFrame(self, height=40, fg_color="#0b3c8c")
        header_frame.pack(fill="x", side="top")
        
        help_button = ctk.CTkButton(header_frame, text="Help (F1)", width=80, height=30,
                                    command=self.show_help, fg_color="#0b3c8c", text_color="white")
        help_button.pack(side="left", padx=5, pady=5)
        
        # Add logout button to header
        logout_button = ctk.CTkButton(header_frame, text="Logout", width=80, height=30,
                                     command=self.logout, fg_color="#dc3545", text_color="white")
        logout_button.pack(side="right", padx=5, pady=5)
        
        header_label = ctk.CTkLabel(header_frame, text="AutoMail Pro",
                                    font=ctk.CTkFont(size=16, weight="bold"), text_color="white")
        header_label.pack(pady=7)
        
        # Main content frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Configuration frame with toggle between SMTP and API
        config_frame = ctk.CTkFrame(main_frame)
        config_frame.pack(fill="x", pady=(0, 10))
        
        # Toggle switch for SMTP/API
        self.smtp_api_toggle = ctk.StringVar(value="SMTP")
        toggle_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        toggle_frame.pack(side="left", padx=5)
        
        smtp_radio = ctk.CTkRadioButton(toggle_frame, text="SMTP", variable=self.smtp_api_toggle, value="SMTP",
                                      command=self.update_config_display)
        smtp_radio.pack(side="left", padx=5)
        
        api_radio = ctk.CTkRadioButton(toggle_frame, text="API", variable=self.smtp_api_toggle, value="API",
                                      command=self.update_config_display)
        api_radio.pack(side="left", padx=5)
        
        # Configuration button
        self.config_button = ctk.CTkButton(config_frame, text="Configure SMTP", width=130, height=35,
                                         command=self.open_config_settings, fg_color="#28a745")
        self.config_button.pack(side="left", padx=5)
        
        # Configuration status
        self.config_status = ctk.CTkLabel(config_frame, text="Not configured", text_color="#dc3545")
        self.config_status.pack(side="left", padx=5)
        
        # Top row with send button, subject entry, and attachment selection
        top_row = ctk.CTkFrame(main_frame)
        top_row.pack(fill="x", pady=(0, 10))
        
        self.send_button = ctk.CTkButton(top_row, text="Send", width=80, height=35, 
                                        command=self.send_emails, fg_color="#007bff")
        self.send_button.pack(side="left")
        
        self.subject_entry = ctk.CTkEntry(top_row, placeholder_text="Subject", height=35)
        self.subject_entry.pack(side="left", fill="x", expand=True, padx=10)
        
        # Attachment Selection - same row as subject
        attachment_frame = ctk.CTkFrame(top_row)
        attachment_frame.pack(side="right", padx=5)
        
        self.attachment_status_label = ctk.CTkLabel(attachment_frame, text="No attachment or folder selected", 
                                                  font=ctk.CTkFont("Arial", 10))
        self.attachment_status_label.pack(side="left", padx=5)
        
        self.attachment_select_button = ctk.CTkButton(attachment_frame, text="Select Attachment/Folder", width=150, height=35,
                                                    command=self.select_attachment_or_folder)
        self.attachment_select_button.pack(side="left")
        
        # Body text label
        body_label = ctk.CTkLabel(main_frame, text="Body Text", font=ctk.CTkFont("Arial", 12, "bold"))
        body_label.pack(anchor="w")
        
        # Rich text editor with larger size
        self.rich_text_editor = RichTextEditor(main_frame)
        self.rich_text_editor.pack(fill="both", expand=True, pady=(5, 10))
        
        # Mailing data frame
        mailing_data_frame = ctk.CTkFrame(main_frame)
        mailing_data_frame.pack(fill="x", pady=(0, 10))
        
        mailing_data_label = ctk.CTkLabel(mailing_data_frame, text="Mailing Data", 
                                         font=ctk.CTkFont("Arial", 12, "bold"))
        mailing_data_label.pack(side="left")
        
        self.data_entry_button = ctk.CTkButton(mailing_data_frame, text="Recipients DATA", width=100,
                                             command=self.open_data_sheet, fg_color="#17a2b8")
        self.data_entry_button.pack(side="right")
        
        self.data_info_label = ctk.CTkLabel(mailing_data_frame, text="No recipients entered")
        self.data_info_label.pack(side="right", padx=10)
        
        # Sent emails frame
        sent_emails_frame = ctk.CTkFrame(main_frame)
        sent_emails_frame.pack(fill="x", pady=(0, 10))
        
        sent_emails_label = ctk.CTkLabel(sent_emails_frame, text="Sent Emails (.eml)", 
                                       font=ctk.CTkFont("Arial", 12, "bold"))
        sent_emails_label.pack(side="left")
        
        self.sent_emails_button = ctk.CTkButton(sent_emails_frame, text="Open Folder", width=100,
                                             command=self.open_sent_emails_folder, fg_color="#6f42c1")
        self.sent_emails_button.pack(side="right")
        
        self.sent_emails_count_label = ctk.CTkLabel(sent_emails_frame, text="0 emails")
        self.sent_emails_count_label.pack(side="right", padx=10)
        
        # Footer frame for branding
        footer_frame = ctk.CTkFrame(self, height=40, fg_color="#1E3F66")
        footer_frame.pack(fill="x", side="bottom")
        
        powered_by_label_shadow = ctk.CTkLabel(footer_frame, text="Powered by MNA",
                                               font=ctk.CTkFont(size=14, weight="bold"),
                                               text_color="#0a2240")
        powered_by_label_shadow.place(relx=0.5, rely=0.5, anchor="center", x=2, y=2)
        
        powered_by_label = ctk.CTkLabel(footer_frame, text="Powered by MNA",
                                        font=ctk.CTkFont(size=14, weight="bold"),
                                        text_color="#62B956")
        powered_by_label.place(relx=0.5, rely=0.5, anchor="center")
        
        self.bind("<F1>", lambda e: self.show_help())
        self.bind("<Control-Return>", lambda e: self.send_emails())
        self.bind("<F2>", lambda e: self.open_signature_settings())
        
        # Update status labels if paths were previously selected
        if self.selected_folder_path:
            self.load_pdf_files_from_folder()
            self.update_attachment_status()
        if self.selected_file_path:
            self.update_attachment_status()
        
        self.update_config_display()
        self.update_sent_emails_count()
        
        # Show message if no config is present
        if not self.smtp_config and not self.api_config:
            self.show_no_config_message()
        
    def load_signature_disclaimer(self):
        """Load signature and disclaimer settings from file"""
        try:
            settings_file = os.path.join(os.path.expanduser("~/.cpc_mailing/data"), "signature_settings.json")
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.signature = settings.get("signature", "")
                    self.disclaimer = settings.get("disclaimer", "")
        except Exception as e:
            logging.error(f"Failed to load signature/disclaimer settings: {e}")
    
    def show_no_config_message(self):
        """Show a message when no configuration is present"""
        info_frame = ctk.CTkFrame(self, fg_color="#fff3cd", border_color="#ffc107", border_width=2)
        info_frame.place(relx=0.5, rely=0.3, anchor="center", relwidth=0.8)
        
        info_label = ctk.CTkLabel(info_frame, 
                                 text="⚠️ No Configuration Found\n\nPlease click 'Configure SMTP' or 'Configure API' to set up your email server before sending emails.",
                                 font=ctk.CTkFont("Arial", 12), text_color="#856404", justify="center")
        info_label.pack(pady=15, padx=10)
        
        close_btn = ctk.CTkButton(info_frame, text="Got it", width=80, 
                                 command=lambda: info_frame.destroy())
        close_btn.pack(pady=(0, 10))
        
    def load_app_config(self):
        try:
            os.makedirs(os.path.dirname(self.app_config_file), exist_ok=True)
            if os.path.exists(self.app_config_file):
                with open(self.app_config_file, 'r') as f:
                    config = json.load(f)
                    self.selected_folder_path = config.get("selected_folder_path", None)
                    self.selected_file_path = config.get("selected_file_path", None)
                    if self.selected_folder_path:
                        self.selected_folder_path = self.selected_folder_path.replace(os.sep, '/')
                        logging.debug(f"Loaded selected_folder_path: {self.selected_folder_path}")
        except Exception as e:
            logging.error(f"Failed to load app configuration: {e}")
            messagebox.showerror("Error", f"Failed to load app configuration: {e}")
            
    def save_app_config(self):
        try:
            os.makedirs(os.path.dirname(self.app_config_file), exist_ok=True)
            config = {
                "selected_folder_path": self.selected_folder_path,
                "selected_file_path": self.selected_file_path
            }
            with open(self.app_config_file, 'w') as f:
                json.dump(config, f, indent=4)
            logging.debug(f"Saved app config: {config}")
        except Exception as e:
            logging.error(f"Failed to save app configuration: {e}")
            messagebox.showerror("Error", f"Failed to save app configuration: {e}")
        
    def update_config_display(self):
        """Update the configuration display based on the selected mode"""
        if self.smtp_api_toggle.get() == "SMTP":
            self.config_button.configure(text="Configure SMTP")
            self.update_smtp_status()
        else:
            self.config_button.configure(text="Configure API")
            self.update_api_status()
            
    def update_smtp_status(self):
        if self.smtp_config:
            custom_from = self.smtp_config.get("custom_from", "")
            if custom_from:
                display_text = f"Configured: {custom_from} (via {self.smtp_config.get('email', '')})"
            else:
                display_text = f"Configured: {self.smtp_config.get('email', '')}"
            self.config_status.configure(text=display_text, text_color="#28a745")
        else:
            self.config_status.configure(text="Not configured", text_color="#dc3545")
            
    def update_api_status(self):
        if self.api_config:
            custom_from = self.api_config.get("custom_from", "")
            if custom_from:
                display_text = f"Configured: {custom_from}"
            else:
                display_text = f"Configured: {self.api_config.get('api_endpoint', '')[:30]}..."
            self.config_status.configure(text=display_text, text_color="#28a745")
        else:
            self.config_status.configure(text="Not configured", text_color="#dc3545")
            
    def update_sent_emails_count(self):
        """Update the count of sent emails"""
        sent_emails_dir = os.path.join(os.path.expanduser("~/.cpc_mailing/sent_emails"))
        if os.path.exists(sent_emails_dir):
            try:
                eml_files = [f for f in os.listdir(sent_emails_dir) if f.lower().endswith('.eml')]
                count = len(eml_files)
                self.sent_emails_count_label.configure(text=f"{count} email{'s' if count != 1 else ''}")
            except Exception as e:
                logging.error(f"Failed to count .eml files: {e}")
                self.sent_emails_count_label.configure(text="Count error")
        else:
            self.sent_emails_count_label.configure(text="0 emails")
            
    def open_config_settings(self):
        """Open the appropriate configuration settings based on the toggle"""
        if self.smtp_api_toggle.get() == "SMTP":
            SMTPSettingsPopup(self)
            self.after(100, self.update_smtp_status)
        else:
            APISettingsPopup(self)
            self.after(100, self.update_api_status)
        
    def open_signature_settings(self):
        """Open signature and disclaimer settings popup"""
        SignatureSettingsPopup(self)
        
    def on_close(self):
        """Handle window close event"""
        if messagebox.askyesno("Confirm Exit", "Are you sure you want to exit the application?"):
            self.reset_session_data()
            self.quit()
            self.destroy()
        
    def reset_session_data(self):
        """Reset session data (folder/file selection and data sheet) but keep SMTP config"""
        # Reset selected folder and file
        self.selected_folder_path = None
        self.selected_file_path = None
        self.pdf_files = []
        
        # Update UI
        self.update_attachment_status()
        
        # Clear mailing data
        self.mailing_data_df = None
        self.data_info_label.configure(text="No recipients entered")
        
        # Delete the mailing data CSV file if it exists
        data_file = os.path.join(os.path.expanduser("~/.cpc_mailing/data"), "mailing_data.csv")
        if os.path.exists(data_file):
            try:
                os.remove(data_file)
                logging.info("Mailing data file deleted on logout/close")
            except Exception as e:
                logging.error(f"Failed to delete mailing data file: {e}")
        
        # Update app config to remove folder/file paths
        self.save_app_config()
        
    def logout(self):
        """Logout functionality to clear session data but keep SMTP configurations"""
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout? This will clear your current session data but keep your configurations."):
            try:
                # Reset session data (folder/file selection and data sheet)
                self.reset_session_data()
                
                # Show success message
                messagebox.showinfo("Logout Successful", "Your session data has been cleared. Configurations are preserved.")
                
                # Quit the application
                self.quit()
                self.destroy()
                
            except Exception as e:
                logging.error(f"Error during logout: {e}")
                messagebox.showerror("Logout Error", f"An error occurred during logout: {str(e)}")
        
    def show_help(self):
        # Create a scrollable help window
        help_window = ctk.CTkToplevel(self)
        help_window.title("Help - AutoMail Pro")
        help_window.geometry("420x500")
        help_window.resizable(True, True)
        help_window.transient(self)
        help_window.grab_set()
        
        # Center the window
        help_window.update_idletasks()
        width = help_window.winfo_width()
        height = help_window.winfo_height()
        x = (help_window.winfo_screenwidth() // 2) - (width // 2)
        y = (help_window.winfo_screenheight() // 2) - (height // 2)
        help_window.geometry(f"+{x}+{y}")
        
        # Create header
        header = ctk.CTkLabel(help_window, text="AutoMail Pro - Quick Guide", 
                             font=ctk.CTkFont("Arial", 16, "bold"),
                             fg_color="#0b3c8c", text_color="white", height=40)
        header.pack(fill="x")
        
        # Create main content frame with scrollbar
        main_frame = ctk.CTkFrame(help_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar
        canvas = ctk.CTkCanvas(main_frame, highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(main_frame, orientation="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add help content
        help_content = (
            "1. Configuration:\n"
            "   • Toggle between SMTP and API using the radio buttons\n"
            "   • Click 'Configure SMTP' to set up your email server\n"
            "   • Use app-specific passwords for Gmail/Outlook\n"
            "   • Choose between TLS (port 587) or SSL (port 465)\n"
            "   • If using SSL (port 465) fails with 'Access denied':\n"
            "     - Try TLS (port 587) instead\n"
            "     - Check firewall/antivirus settings\n"
            "     - Add exception for Python in firewall\n"
            "   • Optionally set a custom 'From' address\n"
            "   • Test connection before saving\n"
            "   • Click 'Configure API' to set up API endpoint\n"
            "   • Enter API endpoint URL and API key\n"
            "   • Choose HTTP method (POST or PUT)\n"
            "   • Test connection before saving\n\n"
            "2. Signature & Disclaimer Settings:\n"
            "   • Press F2 to open Signature & Disclaimer settings\n"
            "   • Create and format your signature text\n"
            "   • Add a disclaimer text with formatting options\n"
            "   • Both will be automatically added to the bottom of your emails\n"
            "   • Check 'Auto-save' for both to save and close automatically\n\n"
            "3. Prepare Email:\n"
            "   • Enter subject line (supports placeholders like [{ Unique Accounts }])\n"
            "   • Write email body text using the rich text editor\n"
            "   • Format text with font style, size, bold, italic, underline, color, and highlight\n"
            "   • Enable Auto-Format to automatically apply formatting rules\n\n"
            "4. Smart Attachment Selection:\n"
            "   • Click 'Select Attachment/Folder' to choose:\n"
            "     - A folder: Each file is treated as an attachment for matching accounts\n"
            "     - A single file: Same file attached to all emails\n"
            "     - No selection: Send without attachments\n\n"
            "5. Enter Recipient Data:\n"
            "   • Click 'Recipients DATA' to open the data sheet\n"
            "   • Add recipient emails (required)\n"
            "   • Unique Accounts is optional (only needed for PDF matching)\n"
            "   • Auto-saves as you type\n\n"
            "6. Use Placeholders:\n"
            "   • Click 'Placeholders' in the toolbar to see available placeholders\n"
            "   • Use placeholders like [{ Co. Name }] in your email body and subject\n"
            "   • They will be replaced with actual data from the data sheet\n"
            "   • Example: \"Dear [{ Co. Name }],\" becomes \"Dear MNA I & C Groups,\"\n"
            "   • Subject example: \"Monthly Statement for Account [{ Unique Accounts }]\"\n\n"
            "7. Send Emails:\n"
            "   • Click 'Send' to start mailing\n"
            "   • Monitor progress in the status window\n"
            "   • Export the log to text, CSV, or PDF format\n"
            "   • Pause/Resume or cancel if needed\n\n"
            "8. Export Log:\n"
            "   • Click 'Export' to open export options\n"
            "   • Choose to send via email, download to desktop, or both\n"
            "   • If sending via email, enter recipient and optional CC\n"
            "   • Files will be attached in PDF, TXT, and CSV formats\n\n"
            "9. Sent Emails (.eml):\n"
            "   • Each sent email is saved as an .eml file\n"
            "   • Click 'Open Folder' to access these files\n"
            "   • .eml files can be opened in any email client (Gmail, Outlook, Thunderbird, etc.)\n"
            "   • Useful for audit purposes and record keeping\n\n"
            "10. Logout:\n"
            "   • Click 'Logout' to clear session data\n"
            "   • This will reset folder/file selection and clear data sheet\n"
            "   • Configurations will be preserved\n\n"
            "Smart Attachment Logic:\n"
            "• Folder selected: Each file in the folder is attached to matching accounts\n"
            "• Single file selected: Same file attached to all emails\n"
            "• No selection: Email sent without attachments\n"
            "• If attachment is missing for a recipient, that email is skipped\n\n"
            "Keyboard Shortcuts:\n"
            "• F1: Help\n"
            "• F2: Signature & Disclaimer Settings\n"
            "• Ctrl+Enter: Send emails\n"
            "• Ctrl+S: Save data (in data sheet)\n"
            "• Ctrl+N: Add rows (in data sheet)\n"
            "• Delete/Backspace: Delete selected cell content (in data sheet)\n\n"
            "Rich Text Editor Features:\n"
            "• Font style selection (Arial, Calibri, etc.)\n"
            "• Font size selection (8-36pt)\n"
            "• Bold, Italic, Underline formatting\n"
            "• Text color and highlight color\n"
            "• Auto-Format: Automatically applies formatting rules\n"
            "• Line breaks are preserved in the email\n"
            "• Undo/Redo functionality\n"
            "• Reset formatting\n\n"
            "Selection Feature:\n"
            "• Select only a portion of text to send just that part\n"
            "• Formatting of the selected text will be preserved\n\n"
            "Duplicate Prevention:\n"
            "• The system tracks sent emails to prevent duplicates\n"
            "• Duplicates are automatically removed when importing data"
        )
        
        help_label = ctk.CTkLabel(scrollable_frame, text=help_content, 
                                font=ctk.CTkFont("Arial", 11), justify="left")
        help_label.pack(padx=10, pady=10, anchor="w")
        
        # Close button
        close_btn = ctk.CTkButton(help_window, text="Close", width=100, 
                                command=help_window.destroy,
                                fg_color="#3182ce", hover_color="#2c5282")
        close_btn.pack(pady=10)
        
        # Bind mouse wheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        
    def load_pdf_files_from_folder(self):
        """Load all PDF files from the selected folder"""
        if not self.selected_folder_path or not os.path.exists(self.selected_folder_path):
            return
            
        try:
            all_files = os.listdir(self.selected_folder_path)
            logging.debug(f"All files in folder: {all_files}")
            self.pdf_files = [
                os.path.join(self.selected_folder_path, f) for f in all_files
                if f.lower().endswith('.pdf')
            ]
            pdf_count = len(self.pdf_files)
            logging.debug(f"Found {pdf_count} PDF(s): {self.pdf_files}")
            
            # If no PDFs found in folder, inform user
            if pdf_count == 0:
                result = messagebox.askyesno("No PDFs Found", 
                                           f"No PDF files found in the selected folder.\n\n"
                                           f"Do you want to send emails without attachments?")
                if not result:
                    # User doesn't want to send without attachments
                    self.selected_folder_path = None
                    self.pdf_files = []
                    self.save_app_config()
                    self.update_attachment_status()
                    return
        except Exception as e:
            logging.error(f"Error accessing folder {self.selected_folder_path}: {e}")
            messagebox.showerror("Error", f"Failed to access folder {self.selected_folder_path}: {e}")
            self.pdf_files = []
            self.selected_folder_path = None
            self.save_app_config()
            self.update_attachment_status()
        
    def update_attachment_status(self):
        """Update the attachment status label with current selection"""
        if self.selected_folder_path:
            folder_name = os.path.basename(self.selected_folder_path)
            pdf_count = len(self.pdf_files)
            self.attachment_status_label.configure(text=f"Folder: {folder_name} ({pdf_count} PDFs)")
        elif self.selected_file_path:
            filename = os.path.basename(self.selected_file_path)
            self.attachment_status_label.configure(text=f"File: {filename}")
        else:
            self.attachment_status_label.configure(text="No attachment or folder selected")
        
    def select_attachment_or_folder(self):
        """Smart selector for both files and folders"""
        # Create a popup with two options: File and Folder
        popup = ctk.CTkToplevel(self)
        popup.title("Select Attachment or Folder")
        popup.geometry("300x150")
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()
        
        # Center the popup
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f"+{x}+{y}")
        
        label = ctk.CTkLabel(popup, text="Choose selection type:", font=ctk.CTkFont("Arial", 12))
        label.pack(pady=10)
        
        button_frame = ctk.CTkFrame(popup)
        button_frame.pack(pady=10)
        
        def select_file():
            popup.destroy()
            file_path = filedialog.askopenfilename(
                title="Select File",
                initialdir=os.path.expanduser("~"),
                filetypes=[
                    ("All Files", "*.*"),
                    ("PDF Files", "*.pdf"),
                    ("CSV Files", "*.csv"),
                    ("Excel Files", "*.xlsx"),
                    ("Image Files", "*.jpg *.jpeg *.png"),
                    ("Text Files", "*.txt")
                ]
            )
            if file_path:
                self.selected_file_path = file_path
                self.selected_folder_path = None
                self.pdf_files = []
                self.save_app_config()
                self.update_attachment_status()
        
        def select_folder():
            popup.destroy()
            folder_path = filedialog.askdirectory(
                title="Select Folder",
                initialdir=os.path.expanduser("~")
            )
            if folder_path:
                self.selected_folder_path = folder_path
                self.selected_file_path = None
                self.load_pdf_files_from_folder()
                self.save_app_config()
                self.update_attachment_status()
        
        ctk.CTkButton(button_frame, text="Select File", command=select_file, width=100).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Select Folder", command=select_folder, width=100).pack(side="left", padx=10)
        
    def open_data_sheet(self):
        if self.data_sheet_window and self.data_sheet_window.winfo_exists():
            messagebox.showwarning("Warning", "Data Sheet is already open!")
        else:
            self.data_sheet_window = DataSheetWindow(self)
            
    def open_sent_emails_folder(self):
        """Open the folder containing sent .eml files"""
        sent_emails_dir = os.path.join(os.path.expanduser("~/.cpc_mailing/sent_emails"))
        
        # Create directory if it doesn't exist
        os.makedirs(sent_emails_dir, exist_ok=True)
        
        # Open the folder in the system's file explorer
        try:
            if platform.system() == "Windows":
                os.startfile(sent_emails_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", sent_emails_dir])
            else:  # Linux
                subprocess.run(["xdg-open", sent_emails_dir])
        except Exception as e:
            logging.error(f"Failed to open sent emails folder: {e}")
            messagebox.showerror("Error", f"Failed to open folder: {str(e)}")
            
    def validate_email_domain(self, email):
        """Validate email domain and provide specific guidance"""
        domain = email.split('@')[-1].lower()
        
        # Common domains with specific requirements
        domain_requirements = {
            'gmail.com': "Requires app password if 2FA is enabled",
            'yahoo.com': "Requires app password if 2FA is enabled",
            'outlook.com': "May require app password for third-party apps",
            'hotmail.com': "May require app password for third-party apps",
            'rediffmail.com': "Check SMTP settings in Rediffmail account",
        }
        
        if domain in domain_requirements:
            return domain_requirements[domain]
        return "Check with your email provider for SMTP settings"
    
    def send_emails(self):
        if self.mailing_data_df is None or self.mailing_data_df.empty:
            messagebox.showwarning("No Mailing Data", "Please enter and save mailing data before sending emails.")
            return
            
        subject = self.subject_entry.get().strip()
        if not subject:
            messagebox.showwarning("No Subject", "Please enter a subject for the email.")
            return
            
        # Get text from rich text editor with improved selection handling
        try:
            # First check if there's any text at all
            full_text = self.rich_text_editor.get_text()
            
            # If there's no text at all, show warning
            if not full_text.strip():
                messagebox.showwarning("No Body", "Please enter body text for the email.")
                return
                
            # Now handle selection vs. full text
            if self.rich_text_editor.text_area.tag_ranges("sel"):
                selected_text = self.rich_text_editor.get_selected_text()
                # Use selected text only if it's not empty, otherwise use full text
                body_text = selected_text if selected_text.strip() else full_text
                body_html = self.rich_text_editor.get_html()
            else:
                body_text = full_text
                body_html = self.rich_text_editor.get_html()
                
            # Final check to ensure we have content
            if not body_text.strip():
                messagebox.showwarning("No Body", "Please enter body text for the email.")
                return
                
        except Exception as e:
            logging.error(f"Error getting text from editor: {e}")
            messagebox.showerror("Error", f"Failed to get email body: {str(e)}")
            return
            
        # Check if we have the appropriate configuration
        if self.smtp_api_toggle.get() == "SMTP":
            if not hasattr(self, 'smtp_config') or not self.smtp_config:
                messagebox.showwarning("No SMTP Config", "Please configure SMTP settings before sending emails.")
                return
        else:  # API mode
            if not hasattr(self, 'api_config') or not self.api_config:
                messagebox.showwarning("No API Config", "Please configure API settings before sending emails.")
                return
            
        # Pass pdf_files and single_attachment to MailStatusMonitor
        status_monitor = MailStatusMonitor(self, self.mailing_data_df, self.pdf_files, self.selected_file_path)
        status_monitor.process_emails()
        
        # Update sent emails count after sending is complete
        self.after(1000, self.update_sent_emails_count)

if __name__ == "__main__":
    app = CPCMailingSystem()
    app.mainloop()