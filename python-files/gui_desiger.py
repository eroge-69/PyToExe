#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI Designer - Drag and Drop Interface Builder
Ubuntu MATE 24.04.3 LTS kompatibilis
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import json
import os

class DraggableWidget:
    def __init__(self, canvas, widget_type, x, y):
        self.canvas = canvas
        self.widget_type = widget_type
        self.x = x
        self.y = y
        self.selected = False
        self.properties = {
            'text': f'{widget_type}',
            'width': 100,
            'height': 30,
            'bg': 'lightgray',
            'fg': 'black',
            'font': ('Arial', 10),
            'relief': 'raised'
        }
        
        self.create_widget()
        
    def create_widget(self):
        """Widget létrehozása a canvas-on"""
        if self.widget_type == 'Button':
            self.canvas_id = self.canvas.create_rectangle(
                self.x, self.y, self.x + self.properties['width'], self.y + self.properties['height'],
                fill=self.properties['bg'], outline='black', width=2
            )
            self.text_id = self.canvas.create_text(
                self.x + self.properties['width']//2, self.y + self.properties['height']//2,
                text=self.properties['text'], fill=self.properties['fg']
            )
        elif self.widget_type == 'Label':
            self.canvas_id = self.canvas.create_rectangle(
                self.x, self.y, self.x + self.properties['width'], self.y + self.properties['height'],
                fill='white', outline='gray', width=1
            )
            self.text_id = self.canvas.create_text(
                self.x + self.properties['width']//2, self.y + self.properties['height']//2,
                text=self.properties['text'], fill=self.properties['fg']
            )
        elif self.widget_type == 'Entry':
            self.canvas_id = self.canvas.create_rectangle(
                self.x, self.y, self.x + self.properties['width'], self.y + self.properties['height'],
                fill='white', outline='black', width=1
            )
            self.text_id = self.canvas.create_text(
                self.x + 5, self.y + self.properties['height']//2,
                text='', anchor='w', fill=self.properties['fg']
            )
        elif self.widget_type == 'Frame':
            self.canvas_id = self.canvas.create_rectangle(
                self.x, self.y, self.x + self.properties['width'], self.y + self.properties['height'],
                fill='lightgray', outline='darkgray', width=2
            )
            self.text_id = self.canvas.create_text(
                self.x + 5, self.y + 5,
                text=self.properties['text'], anchor='nw', fill=self.properties['fg']
            )
        
        # Event binding
        self.canvas.tag_bind(self.canvas_id, "<Button-1>", self.on_click)
        self.canvas.tag_bind(self.canvas_id, "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind(self.text_id, "<Button-1>", self.on_click)
        self.canvas.tag_bind(self.text_id, "<B1-Motion>", self.on_drag)
        
    def on_click(self, event):
        """Widget kijelölése"""
        self.canvas.master.select_widget(self)
        self.start_x = event.x
        self.start_y = event.y
        
    def on_drag(self, event):
        """Widget húzása"""
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        
        self.canvas.move(self.canvas_id, dx, dy)
        self.canvas.move(self.text_id, dx, dy)
        
        self.x += dx
        self.y += dy
        self.start_x = event.x
        self.start_y = event.y
        
    def select(self):
        """Widget kijelölése"""
        self.selected = True
        self.canvas.itemconfig(self.canvas_id, outline='red', width=3)
        
    def deselect(self):
        """Widget kijelölés megszüntetése"""
        self.selected = False
        color = 'black' if self.widget_type != 'Label' else 'gray'
        width = 2 if self.widget_type != 'Label' else 1
        self.canvas.itemconfig(self.canvas_id, outline=color, width=width)
        
    def update_properties(self):
        """Widget tulajdonságainak frissítése"""
        self.canvas.itemconfig(self.canvas_id, fill=self.properties['bg'])
        self.canvas.itemconfig(self.text_id, text=self.properties['text'], fill=self.properties['fg'])
        
        # Méret frissítése
        coords = self.canvas.coords(self.canvas_id)
        new_x2 = self.x + self.properties['width']
        new_y2 = self.y + self.properties['height']
        self.canvas.coords(self.canvas_id, self.x, self.y, new_x2, new_y2)
        
        # Szöveg pozíció frissítése
        self.canvas.coords(self.text_id, 
                          self.x + self.properties['width']//2, 
                          self.y + self.properties['height']//2)

class GUIDesigner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GUI Designer - Ubuntu MATE 24.04.3")
        self.root.geometry("1200x800")
        
        self.widgets = []
        self.selected_widget = None
        
        self.create_interface()
        
    def create_interface(self):
        """Főablak felület létrehozása"""
        # Menüsor
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fájl", menu=file_menu)
        file_menu.add_command(label="Új", command=self.new_project)
        file_menu.add_command(label="Megnyitás", command=self.open_project)
        file_menu.add_command(label="Mentés", command=self.save_project)
        file_menu.add_separator()
        file_menu.add_command(label="Kód generálás", command=self.generate_code)
        file_menu.add_separator()
        file_menu.add_command(label="Kilépés", command=self.root.quit)
        
        # Főkeret
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Eszköztár (bal oldal)
        self.create_toolbar(main_frame)
        
        # Középső terület - Design canvas
        self.create_canvas(main_frame)
        
        # Tulajdonság panel (jobb oldal)
        self.create_properties_panel(main_frame)
        
    def create_toolbar(self, parent):
        """Eszköztár létrehozása"""
        toolbar_frame = tk.Frame(parent, width=150, bg='lightgray')
        toolbar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        toolbar_frame.pack_propagate(False)
        
        tk.Label(toolbar_frame, text="Elemek", font=('Arial', 12, 'bold'), bg='lightgray').pack(pady=10)
        
        # Widget gombok
        widgets = ['Button', 'Label', 'Entry', 'Frame']
        for widget in widgets:
            btn = tk.Button(toolbar_frame, text=widget, width=15,
                           command=lambda w=widget: self.add_widget(w))
            btn.pack(pady=5)
            
        tk.Label(toolbar_frame, text="Műveletek", font=('Arial', 12, 'bold'), bg='lightgray').pack(pady=(20, 10))
        
        tk.Button(toolbar_frame, text="Törlés", width=15, 
                 command=self.delete_selected).pack(pady=5)
        tk.Button(toolbar_frame, text="Másolás", width=15,
                 command=self.copy_selected).pack(pady=5)
        
    def create_canvas(self, parent):
        """Design canvas létrehozása"""
        canvas_frame = tk.Frame(parent)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas scrollbar-okkal
        self.canvas = tk.Canvas(canvas_frame, bg='white', width=600, height=500)
        
        v_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Grid vonalak
        self.draw_grid()
        
        # Canvas események
        self.canvas.bind("<Button-1>", self.canvas_click)
        
    def create_properties_panel(self, parent):
        """Tulajdonság panel létrehozása"""
        prop_frame = tk.Frame(parent, width=250, bg='lightgray')
        prop_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        prop_frame.pack_propagate(False)
        
        tk.Label(prop_frame, text="Tulajdonságok", font=('Arial', 12, 'bold'), bg='lightgray').pack(pady=10)
        
        # Tulajdonság mezők
        self.prop_vars = {}
        
        # Szöveg
        tk.Label(prop_frame, text="Szöveg:", bg='lightgray').pack(anchor=tk.W, padx=5)
        self.prop_vars['text'] = tk.StringVar()
        tk.Entry(prop_frame, textvariable=self.prop_vars['text']).pack(fill=tk.X, padx=5, pady=2)
        
        # Szélesség
        tk.Label(prop_frame, text="Szélesség:", bg='lightgray').pack(anchor=tk.W, padx=5)
        self.prop_vars['width'] = tk.IntVar()
        tk.Spinbox(prop_frame, from_=10, to=500, textvariable=self.prop_vars['width']).pack(fill=tk.X, padx=5, pady=2)
        
        # Magasság
        tk.Label(prop_frame, text="Magasság:", bg='lightgray').pack(anchor=tk.W, padx=5)
        self.prop_vars['height'] = tk.IntVar()
        tk.Spinbox(prop_frame, from_=10, to=500, textvariable=self.prop_vars['height']).pack(fill=tk.X, padx=5, pady=2)
        
        # Háttér szín
        tk.Label(prop_frame, text="Háttér szín:", bg='lightgray').pack(anchor=tk.W, padx=5)
        bg_frame = tk.Frame(prop_frame, bg='lightgray')
        bg_frame.pack(fill=tk.X, padx=5, pady=2)
        self.prop_vars['bg'] = tk.StringVar()
        tk.Entry(bg_frame, textvariable=self.prop_vars['bg']).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(bg_frame, text="...", width=3, command=self.choose_bg_color).pack(side=tk.RIGHT)
        
        # Szöveg szín
        tk.Label(prop_frame, text="Szöveg szín:", bg='lightgray').pack(anchor=tk.W, padx=5)
        fg_frame = tk.Frame(prop_frame, bg='lightgray')
        fg_frame.pack(fill=tk.X, padx=5, pady=2)
        self.prop_vars['fg'] = tk.StringVar()
        tk.Entry(fg_frame, textvariable=self.prop_vars['fg']).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(fg_frame, text="...", width=3, command=self.choose_fg_color).pack(side=tk.RIGHT)
        
        # Alkalmazás gomb
        tk.Button(prop_frame, text="Alkalmazás", command=self.apply_properties).pack(pady=10)
        
        # Tulajdonság változások figyelése
        for var in self.prop_vars.values():
            var.trace('w', self.on_property_change)
            
    def draw_grid(self):
        """Grid vonalak rajzolása"""
        self.canvas.delete("grid")
        for i in range(0, 1000, 20):
            self.canvas.create_line(i, 0, i, 1000, fill='lightblue', tags="grid")
            self.canvas.create_line(0, i, 1000, i, fill='lightblue', tags="grid")
            
    def add_widget(self, widget_type):
        """Widget hozzáadása a canvas-hoz"""
        x, y = 50 + len(self.widgets) * 20, 50 + len(self.widgets) * 20
        widget = DraggableWidget(self.canvas, widget_type, x, y)
        self.widgets.append(widget)
        self.select_widget(widget)
        
    def select_widget(self, widget):
        """Widget kijelölése"""
        if self.selected_widget:
            self.selected_widget.deselect()
            
        self.selected_widget = widget
        widget.select()
        self.update_properties_panel()
        
    def canvas_click(self, event):
        """Canvas kattintás - kijelölés megszüntetése"""
        if self.selected_widget:
            self.selected_widget.deselect()
            self.selected_widget = None
            self.clear_properties_panel()
            
    def update_properties_panel(self):
        """Tulajdonság panel frissítése a kijelölt widget alapján"""
        if not self.selected_widget:
            return
            
        props = self.selected_widget.properties
        self.prop_vars['text'].set(props['text'])
        self.prop_vars['width'].set(props['width'])
        self.prop_vars['height'].set(props['height'])
        self.prop_vars['bg'].set(props['bg'])
        self.prop_vars['fg'].set(props['fg'])
        
    def clear_properties_panel(self):
        """Tulajdonság panel törlése"""
        for var in self.prop_vars.values():
            if isinstance(var, tk.StringVar):
                var.set('')
            else:
                var.set(0)
                
    def on_property_change(self, *args):
        """Tulajdonság változás kezelése"""
        pass  # Csak nyomon követésre
        
    def apply_properties(self):
        """Tulajdonságok alkalmazása a kijelölt widget-re"""
        if not self.selected_widget:
            return
            
        props = self.selected_widget.properties
        props['text'] = self.prop_vars['text'].get()
        props['width'] = self.prop_vars['width'].get()
        props['height'] = self.prop_vars['height'].get()
        props['bg'] = self.prop_vars['bg'].get()
        props['fg'] = self.prop_vars['fg'].get()
        
        self.selected_widget.update_properties()
        
    def choose_bg_color(self):
        """Háttér szín kiválasztása"""
        color = colorchooser.askcolor(title="Háttér szín kiválasztása")
        if color[1]:
            self.prop_vars['bg'].set(color[1])
            
    def choose_fg_color(self):
        """Szöveg szín kiválasztása"""
        color = colorchooser.askcolor(title="Szöveg szín kiválasztása")
        if color[1]:
            self.prop_vars['fg'].set(color[1])
            
    def delete_selected(self):
        """Kijelölt widget törlése"""
        if self.selected_widget:
            self.canvas.delete(self.selected_widget.canvas_id)
            self.canvas.delete(self.selected_widget.text_id)
            self.widgets.remove(self.selected_widget)
            self.selected_widget = None
            self.clear_properties_panel()
            
    def copy_selected(self):
        """Kijelölt widget másolása"""
        if self.selected_widget:
            widget_type = self.selected_widget.widget_type
            x = self.selected_widget.x + 20
            y = self.selected_widget.y + 20
            new_widget = DraggableWidget(self.canvas, widget_type, x, y)
            new_widget.properties = self.selected_widget.properties.copy()
            new_widget.update_properties()
            self.widgets.append(new_widget)
            self.select_widget(new_widget)
            
    def new_project(self):
        """Új projekt"""
        if messagebox.askokcancel("Új projekt", "Biztosan új projektet kezdesz? A jelenlegi munkád elvész."):
            for widget in self.widgets:
                self.canvas.delete(widget.canvas_id)
                self.canvas.delete(widget.text_id)
            self.widgets.clear()
            self.selected_widget = None
            self.clear_properties_panel()
            
    def save_project(self):
        """Projekt mentése"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON fájlok", ".json"), ("Minden fájl", ".*")]
        )
        
        if filename:
            project_data = []
            for widget in self.widgets:
                data = {
                    'type': widget.widget_type,
                    'x': widget.x,
                    'y': widget.y,
                    'properties': widget.properties
                }
                project_data.append(data)
                
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(project_data, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Mentés", f"Projekt mentve: {filename}")
            except Exception as e:
                messagebox.showerror("Hiba", f"Mentés sikertelen: {str(e)}")
                
    def open_project(self):
        """Projekt megnyitása"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON fájlok", ".json"), ("Minden fájl", ".*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                    
                # Jelenlegi projekt törlése
                self.new_project()
                
                # Widget-ek betöltése
                for data in project_data:
                    widget = DraggableWidget(self.canvas, data['type'], data['x'], data['y'])
                    widget.properties = data['properties']
                    widget.update_properties()
                    self.widgets.append(widget)
                    
                messagebox.showinfo("Betöltés", f"Projekt betöltve: {filename}")
            except Exception as e:
                messagebox.showerror("Hiba", f"Betöltés sikertelen: {str(e)}")
                
    def generate_code(self):
        """Python kód generálása"""
        if not self.widgets:
            messagebox.showwarning("Figyelem", "Nincsenek widget-ek a projektben!")
            return
            
        code = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Generált GUI kód

import tkinter as tk
from tkinter import ttk

class GeneratedGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Generált GUI")
        self.root.geometry("800x600")
        
        self.create_widgets()
        
    def create_widgets(self):
"""

        for i, widget in enumerate(self.widgets):
            w_type = widget.widget_type.lower()
            props = widget.properties
            
            if widget.widget_type == 'Button':
                code += f"""        self.{w_type}_{i} = tk.Button(self.root, 
                                    text="{props['text']}", 
                                    bg="{props['bg']}", 
                                    fg="{props['fg']}")
        self.{w_type}_{i}.place(x={widget.x}, y={widget.y}, 
                               width={props['width']}, height={props['height']})
        
"""
            elif widget.widget_type == 'Label':
                code += f"""        self.{w_type}_{i} = tk.Label(self.root, 
                                   text="{props['text']}", 
                                   bg="{props['bg']}", 
                                   fg="{props['fg']}")
        self.{w_type}_{i}.place(x={widget.x}, y={widget.y}, 
                               width={props['width']}, height={props['height']})
        
"""
            elif widget.widget_type == 'Entry':
                code += f"""        self.{w_type}_{i} = tk.Entry(self.root, 
                                   bg="{props['bg']}", 
                                   fg="{props['fg']}")
        self.{w_type}_{i}.place(x={widget.x}, y={widget.y}, 
                               width={props['width']}, height={props['height']})
        
"""
            elif widget.widget_type == 'Frame':
                code += f"""        self.{w_type}_{i} = tk.Frame(self.root, 
                                   bg="{props['bg']}", 
                                   relief="{props['relief']}")
        self.{w_type}_{i}.place(x={widget.x}, y={widget.y}, 
                               width={props['width']}, height={props['height']})
        
"""

        code += """    def run(self):
        self.root.mainloop()

if _name_ == "_main_":
    app = GeneratedGUI()
    app.run()
"""

        # Kód megjelenítése új ablakban
        code_window = tk.Toplevel(self.root)
        code_window.title("Generált Python kód")
        code_window.geometry("800x600")
        
        text_area = tk.Text(code_window, wrap=tk.WORD)
        scrollbar = tk.Scrollbar(code_window, orient=tk.VERTICAL, command=text_area.yview)
        text_area.configure(yscrollcommand=scrollbar.set)
        
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_area.insert('1.0', code)
        
        # Mentés gomb
        def save_code():
            filename = filedialog.asksaveasfilename(
                defaultextension=".py",
                filetypes=[("Python fájlok", ".py"), ("Minden fájl", ".*")]
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)
                messagebox.showinfo("Mentés", f"Kód mentve: {filename}")
                
        tk.Button(code_window, text="Kód mentése", command=save_code).pack(pady=5)
        
    def run(self):
        """Alkalmazás futtatása"""
        self.root.mainloop()

if _name_ == "_main_":
    designer = GUIDesigner()
    designer.run()
