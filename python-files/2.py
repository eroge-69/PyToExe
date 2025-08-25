import customtkinter as ctk
from PIL import Image, ImageTk
import os
import tkinter as tk
from tkinter import messagebox, colorchooser
import sys

def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f'Error in {func.__name__}: {str(e)}')
            sys.exit(1)
    return wrapper

class CTkColorPicker(ctk.CTkFrame):
    def __init__(self, master, width=300, height=40, fg_color=None, text_color=None,
                 border_width=2, border_color=None, corner_radius=8, bg_color=None,
                 font=("Inter", 16), selected_color="#7F48FF", preview_size=30, **kwargs):
        super().__init__(master, width=width, height=height, fg_color=fg_color,
                        border_width=border_width, border_color=border_color,
                        corner_radius=corner_radius, bg_color=bg_color)

        # Store properties
        self.width = width
        self.height = height
        self.font = font
        self.text_color = text_color
        self.selected_color = selected_color
        self.preview_size = preview_size
        self._callback = None
        
        # Create color preview with border
        preview_container = ctk.CTkFrame(
            self,
            width=preview_size + 4,
            height=preview_size + 4,
            fg_color="transparent",
            border_width=2,
            border_color=border_color or "#404040",
            corner_radius=(preview_size + 4)//2
        )
        preview_container.place(x=10, y=height/2, anchor="w")
        
        self.preview_frame = ctk.CTkFrame(
            preview_container,
            width=preview_size,
            height=preview_size,
            fg_color=selected_color,
            corner_radius=preview_size//2
        )
        self.preview_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Make both frames clickable
        preview_container.bind("<Button-1>", self._show_color_dialog)
        self.preview_frame.bind("<Button-1>", self._show_color_dialog)
        
        # Add hover effect
        def on_enter(e):
            preview_container.configure(border_color=self.selected_color)
        def on_leave(e):
            preview_container.configure(border_color=border_color or "#404040")
            
        preview_container.bind("<Enter>", on_enter)
        preview_container.bind("<Leave>", on_leave)
        self.preview_frame.bind("<Enter>", on_enter)
        self.preview_frame.bind("<Leave>", on_leave)
        
        # Create hex color entry with label
        hex_label = ctk.CTkLabel(
            self,
            text="Hex:",
            font=font,
            text_color=text_color,
            width=30
        )
        hex_label.place(x=preview_size + 25, y=height/2, anchor="w")
        
        self.hex_entry = ctk.CTkEntry(
            self,
            width=90,
            height=height-8,
            font=font,
            fg_color=fg_color or "transparent",
            text_color=text_color,
            placeholder_text="#RRGGBB",
            border_width=1,
            corner_radius=4
        )
        self.hex_entry.place(x=preview_size + 65, y=height/2, anchor="w")
        self.hex_entry.insert(0, selected_color)
        self.hex_entry.bind("<Return>", self._on_hex_change)
        self.hex_entry.bind("<FocusOut>", self._on_hex_change)
        
        # Create RGB labels with better spacing
        rgb_frame = ctk.CTkFrame(self, fg_color="transparent")
        rgb_frame.place(x=preview_size + 170, y=height/2, anchor="w")
        
        rgb_values = self._hex_to_rgb(selected_color)
        self.rgb_labels = []
        
        for i, (label, value) in enumerate([("R", rgb_values[0]), ("G", rgb_values[1]), ("B", rgb_values[2])]):
            label_container = ctk.CTkFrame(rgb_frame, fg_color="transparent")
            label_container.grid(row=0, column=i, padx=5)
            
            ctk.CTkLabel(
                label_container,
                text=label,
                font=(font[0], font[1]-2),
                text_color=text_color,
                width=15
            ).pack(side="left")
            
            rgb_label = ctk.CTkLabel(
                label_container,
                text=str(value),
                font=font,
                text_color=text_color,
                width=30
            )
            rgb_label.pack(side="left")
            self.rgb_labels.append(rgb_label)
        
        # Add pick color button
        pick_button = ctk.CTkButton(
            self,
            text="Pick",
            width=60,
            height=height-8,
            font=(font[0], font[1]-2),
            fg_color=border_color or "#404040",
            hover_color=selected_color,
            corner_radius=4,
            command=lambda: self._show_color_dialog(None)
        )
        pick_button.place(x=width-70, y=height/2, anchor="w")
        
    def _show_color_dialog(self, event=None):
        color = colorchooser.askcolor(color=self.selected_color)
        if color[1]:
            self.set_color(color[1])
            if self._callback:
                self._callback(color[1])
    
    def _on_hex_change(self, event=None):
        hex_color = self.hex_entry.get()
        if self._is_valid_hex(hex_color):
            self.set_color(hex_color)
            if self._callback:
                self._callback(hex_color)
    
    def _is_valid_hex(self, color):
        if not color.startswith("#"):
            color = f"#{color}"
        try:
            _ = tuple(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
            return True
        except ValueError:
            return False
    
    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _rgb_to_hex(self, rgb):
        return "#{:02x}{:02x}{:02x}".format(*rgb)
    
    def set_color(self, color):
        if not color.startswith("#"):
            color = f"#{color}"
        
        if self._is_valid_hex(color):
            self.selected_color = color
            self.preview_frame.configure(fg_color=color)
            self.hex_entry.delete(0, "end")
            self.hex_entry.insert(0, color)
            
            rgb_values = self._hex_to_rgb(color)
            for label, value in zip(self.rgb_labels, rgb_values):
                label.configure(text=str(value))
    
    def get_color(self):
        return self.selected_color
    
    def bind_color_change(self, callback):
        self._callback = callback

class CTkSearchBar(ctk.CTkFrame):
    def __init__(self, master, width=300, height=40, placeholder_text="Search...", 
                 font=("Inter", 16), fg_color=None, text_color=None, border_width=2,
                 border_color=None, corner_radius=20, bg_color=None, icon_size=20,
                 icon_color=None, hover_color=None, **kwargs):
        super().__init__(master, width=width, height=height, fg_color=fg_color,
                        border_width=border_width, border_color=border_color,
                        corner_radius=corner_radius, bg_color=bg_color)

        # Store properties
        self.width = width
        self.height = height
        self.font = font
        self.text_color = text_color
        self.icon_size = icon_size
        self.icon_color = icon_color
        self.hover_color = hover_color
        
        # Create search icon
        self.icon_label = ctk.CTkLabel(
            self,
            text="🔍",
            font=("Inter", icon_size),
            text_color=icon_color,
            width=icon_size + 10
        )
        self.icon_label.place(x=10, y=height/2, anchor="w")
        
        # Create entry field
        self.entry = ctk.CTkEntry(
            self,
            width=width - icon_size - 40,
            height=height - 4,
            font=font,
            fg_color="transparent",
            text_color=text_color,
            placeholder_text=placeholder_text,
            border_width=0
        )
        self.entry.place(x=icon_size + 20, y=height/2, anchor="w")
        
        # Create clear button (hidden by default)
        self.clear_button = ctk.CTkLabel(
            self,
            text="✕",
            font=("Inter", icon_size-4),
            text_color=icon_color,
            width=icon_size,
            cursor="hand2"
        )
        self.clear_button.place(x=width - 25, y=height/2, anchor="e")
        self.clear_button.bind("<Button-1>", self._clear_search)
        self.clear_button.configure(fg_color="transparent")
        
        # Bind events
        self.entry.bind("<KeyRelease>", self._on_text_change)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
    def _on_text_change(self, event=None):
        if self.entry.get():
            self.clear_button.configure(fg_color="transparent")
        else:
            self.clear_button.configure(fg_color="transparent")
            
    def _clear_search(self, event=None):
        self.entry.delete(0, "end")
        self._on_text_change()
        
    def _on_enter(self, event=None):
        if self.hover_color:
            self.configure(fg_color=self.hover_color)
            
    def _on_leave(self, event=None):
        if self.hover_color:
            self.configure(fg_color=self._fg_color)
            
    def get(self):
        return self.entry.get()
        
    def set(self, text):
        self.entry.delete(0, "end")
        self.entry.insert(0, text)
        self._on_text_change()

class ExportedApp(ctk.CTk):
    @handle_error
    def __init__(self):
        super().__init__()
        self._initialize_widgets()
        self._create_widgets()
        self._place_widgets()

    @handle_error
    def _initialize_widgets(self):
        # Configure window
        self.title('teste')
        self.geometry('800x600')
        self.resizable(1, 1)
        ctk.set_appearance_mode('dark')
        ctk.set_widget_scaling(1.0)

        # Initialize widget variables
        self.widget_d0e5d533 = None
        self.widget_520bf144 = None
        self.widget_ff0407d2 = None
        self.widget_43265c9d = None
        self.widget_df880beb = None
        self.widget_a61be722 = None
        self.widget_c91d22b3 = None
        self.widget_346a0146 = None
        self.widget_7762d06a = None
        self.widget_63ccde62 = None

    @handle_error
    def _create_widgets(self):
        # Create widgets
        self.widget_d0e5d533 = ctk.CTkFrame(self, width=800.0, height=600.0, fg_color='#232323', border_width=3.0927835051546393, corner_radius=0.0, border_color='#404040', bg_color='#232323')
        self.widget_d0e5d533.place(x=0.0, y=0.0)
        self.widget_520bf144 = ctk.CTkSlider(self, width=160, height=16, from_=0, to=100, number_of_steps=100, fg_color='#FF6B6B', progress_color='#FF4F4F', border_color='#FF3535')
        self.widget_520bf144.place(x=28.0, y=491.5)
        self.widget_ff0407d2 = ctk.CTkSwitch(self, text='Switch', width=100, height=32, fg_color='#FF6B6B', text_color='black', border_color='#FF3535')
        self.widget_ff0407d2.place(x=28.0, y=442.5)
        self.widget_43265c9d = ctk.CTkProgressBar(self, width=300, height=20, progress_color='#7F48FF', fg_color='#2B2B2B', border_color='#404040', border_width=2, corner_radius=8, bg_color='#2B2B2B')
        self.widget_43265c9d.place(x=219.0, y=528.5)
        self.widget_df880beb = CTkSearchBar(self, width=300, height=40, fg_color='#2B2B2B', text_color='#FFFFFF', placeholder_text='Search...', border_width=2, corner_radius=20, border_color='#404040', font=('Inter', 16), icon_size=20, icon_color='#B3B3B3', hover_color='#2D2D2D', bg_color='#2B2B2B')
        self.widget_df880beb.place(x=230.0, y=19.5)
        self.widget_a61be722 = ctk.CTkEntry(self, width=300, height=40, fg_color='#2B2B2B', text_color='#FFFFFF', placeholder_text='Enter text', border_width=2, corner_radius=8, border_color='#404040', font=('Inter', 16), bg_color='#2B2B2B')
        self.widget_a61be722.place(x=163.0, y=321.5)
        self.widget_c91d22b3 = ctk.CTkButton(self, text='Button', width=200, height=40, fg_color='#7F48FF', hover_color='#6B3CD9', text_color='#FFFFFF', border_width=0, corner_radius=8, font=('Inter', 16), bg_color='#1A1A1A')
        self.widget_c91d22b3.place(x=0.0, y=19.5)
        self.widget_346a0146 = ctk.CTkEntry(self, width=300, height=40, fg_color='#2B2B2B', text_color='#FFFFFF', placeholder_text='Enter text', border_width=2, corner_radius=8, border_color='#404040', font=('Inter', 16), bg_color='#2B2B2B')
        self.widget_346a0146.place(x=163.0, y=402.5)
        self.widget_7762d06a = ctk.CTkTextbox(self, width=300, height=200, fg_color='#2B2B2B', text_color='#FFFFFF', border_width=2, corner_radius=8, border_color='#404040', wrap='word', font=('Inter', 16), bg_color='#2B2B2B')
        self.widget_7762d06a.insert('1.0', 'Enter text here...')
        self.widget_7762d06a.place(x=200.0, y=71.5)
        self.widget_63ccde62 = ctk.CTkLabel(self, width=200, height=200, text='No Image')
        self.widget_63ccde62.place(x=543.0, y=19.5)

    @handle_error
    def _place_widgets(self):
        # Place widgets
        self.widget_d0e5d533.place(x=0.0, y=0.0)
        self.widget_520bf144.place(x=28.0, y=491.5)
        self.widget_ff0407d2.place(x=28.0, y=442.5)
        self.widget_43265c9d.place(x=219.0, y=528.5)
        self.widget_df880beb.place(x=230.0, y=19.5)
        self.widget_a61be722.place(x=163.0, y=321.5)
        self.widget_c91d22b3.place(x=0.0, y=19.5)
        self.widget_346a0146.place(x=163.0, y=402.5)
        self.widget_7762d06a.place(x=200.0, y=71.5)
        self.widget_63ccde62.place(x=543.0, y=19.5)

if __name__ == '__main__':
    app = ExportedApp()
    app.mainloop()
