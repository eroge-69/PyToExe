import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from tkinter import font


class LessonManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Lesson Manager")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        # Data storage - save in same directory as executable
        self.data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lessons_data.json")
        self.lessons = self.load_lessons()

        # Style configuration
        self.setup_styles()

        # Create main interface
        self.create_main_interface()

    def setup_styles(self):
        """Configure modern styling"""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure custom styles
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), background="#f0f0f0")
        style.configure('Modern.TButton', font=('Segoe UI', 10), padding=10)
        style.configure('Delete.TButton', font=('Segoe UI', 9), foreground='red')

    def create_main_interface(self):
        """Create the main lesson management interface"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main container
        main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header with title and + button
        header_frame = tk.Frame(main_frame, bg="#f0f0f0")
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = ttk.Label(header_frame, text="📚 My Lessons", style='Title.TLabel')
        title_label.pack(side=tk.LEFT)

        add_button = tk.Button(
            header_frame,
            text="+ Add Lesson",
            font=('Segoe UI', 10, 'bold'),
            bg="#4CAF50",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.add_lesson
        )
        add_button.pack(side=tk.RIGHT)

        # Lessons container with scrollbar
        self.create_lessons_area(main_frame)

    def create_lessons_area(self, parent):
        """Create scrollable area for lessons"""
        # Frame for canvas and scrollbar
        canvas_frame = tk.Frame(parent, bg="#f0f0f0")
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas and scrollbar
        canvas = tk.Canvas(canvas_frame, bg="#f0f0f0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        self.lessons_frame = tk.Frame(canvas, bg="#f0f0f0")

        self.lessons_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.lessons_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel to canvas
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self.canvas = canvas
        self.display_lessons()

    def display_lessons(self):
        """Display all lessons in the scrollable area"""
        # Clear existing lesson widgets
        for widget in self.lessons_frame.winfo_children():
            widget.destroy()

        if not self.lessons:
            # Empty state
            empty_label = tk.Label(
                self.lessons_frame,
                text="No lessons yet. Click '+ Add Lesson' to get started!",
                font=('Segoe UI', 12),
                fg="#666666",
                bg="#f0f0f0",
                pady=50
            )
            empty_label.pack()
        else:
            for i, lesson in enumerate(self.lessons):
                self.create_lesson_card(lesson, i)

    def create_lesson_card(self, lesson, index):
        """Create a modern card for each lesson"""
        # Card frame with shadow effect
        card_frame = tk.Frame(
            self.lessons_frame,
            bg="white",
            relief=tk.FLAT,
            bd=1,
            highlightbackground="#e0e0e0",
            highlightthickness=1
        )
        card_frame.pack(fill=tk.X, pady=5, padx=5)

        # Card content
        content_frame = tk.Frame(card_frame, bg="white", padx=15, pady=12)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Lesson title and buttons
        top_frame = tk.Frame(content_frame, bg="white")
        top_frame.pack(fill=tk.X)

        lesson_button = tk.Button(
            top_frame,
            text=lesson['name'],
            font=('Segoe UI', 12, 'bold'),
            bg="#2196F3",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            command=lambda idx=index: self.open_lesson(idx)
        )
        lesson_button.pack(side=tk.LEFT)

        # View HTML button
        view_html_button = tk.Button(
            top_frame,
            text="👁️ Preview",
            font=('Segoe UI', 9),
            bg="#9C27B0",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor="hand2",
            command=lambda idx=index: self.preview_lesson(idx)
        )
        view_html_button.pack(side=tk.LEFT, padx=(10, 0))

        # Delete button
        delete_button = tk.Button(
            top_frame,
            text="🗑️ Delete",
            font=('Segoe UI', 9),
            bg="#f44336",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor="hand2",
            command=lambda idx=index: self.delete_lesson(idx)
        )
        delete_button.pack(side=tk.RIGHT)

        # Lesson preview (first 100 chars)
        if lesson['content']:
            preview_text = lesson['content'][:100] + "..." if len(lesson['content']) > 100 else lesson['content']
            preview_label = tk.Label(
                content_frame,
                text=preview_text,
                font=('Segoe UI', 9),
                fg="#666666",
                bg="white",
                wraplength=600,
                justify=tk.LEFT
            )
            preview_label.pack(anchor=tk.W, pady=(8, 0))

    def add_lesson(self):
        """Add a new lesson"""
        name = simpledialog.askstring("New Lesson", "Enter lesson name:")
        if name:
            new_lesson = {
                'name': name,
                'content': ''
            }
            self.lessons.append(new_lesson)
            self.save_lessons()
            self.display_lessons()

    def delete_lesson(self, index):
        """Delete a lesson with confirmation"""
        lesson_name = self.lessons[index]['name']
        if messagebox.askyesno("Delete Lesson", f"Are you sure you want to delete '{lesson_name}'?"):
            del self.lessons[index]
            self.save_lessons()
            self.display_lessons()

    def open_lesson(self, index):
        """Open lesson editor window"""
        lesson = self.lessons[index]

        # Create lesson editor window
        editor_window = tk.Toplevel(self.root)
        editor_window.title(f"Editing: {lesson['name']}")
        editor_window.geometry("900x700")
        editor_window.configure(bg="#f5f5f5")

        # Header with back button and title
        header_frame = tk.Frame(editor_window, bg="#2196F3", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        back_button = tk.Button(
            header_frame,
            text="← Back",
            font=('Segoe UI', 10, 'bold'),
            bg="#1976D2",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2",
            command=editor_window.destroy
        )
        back_button.pack(side=tk.LEFT, padx=15, pady=15)

        title_label = tk.Label(
            header_frame,
            text=lesson['name'],
            font=('Segoe UI', 14, 'bold'),
            fg="white",
            bg="#2196F3"
        )
        title_label.pack(side=tk.LEFT, pady=15)

        # Action buttons
        button_frame = tk.Frame(header_frame, bg="#2196F3")
        button_frame.pack(side=tk.RIGHT, padx=15, pady=10)

        save_button = tk.Button(
            button_frame,
            text="💾 Save",
            font=('Segoe UI', 9, 'bold'),
            bg="#4CAF50",
            fg="white",
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            command=lambda: self.save_lesson_content(index, text_widget, editor_window)
        )
        save_button.pack(side=tk.RIGHT, padx=(10, 0))

        preview_button = tk.Button(
            button_frame,
            text="👁️ Preview",
            font=('Segoe UI', 9, 'bold'),
            bg="#9C27B0",
            fg="white",
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            command=lambda: self.preview_lesson_content(index, text_widget.get('1.0', tk.END).strip())
        )
        preview_button.pack(side=tk.RIGHT)

        # Text editor area
        editor_frame = tk.Frame(editor_window, bg="#f5f5f5", padx=20, pady=20)
        editor_frame.pack(fill=tk.BOTH, expand=True)

        # Text widget with scrollbar
        text_frame = tk.Frame(editor_frame, bg="#f5f5f5")
        text_frame.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(
            text_frame,
            font=('Consolas', 11),
            bg="white",
            fg="#333333",
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=15,
            wrap=tk.WORD,
            undo=True,
            insertbackground="#333333"
        )

        text_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=text_scrollbar.set)

        text_widget.pack(side="left", fill="both", expand=True)
        text_scrollbar.pack(side="right", fill="y")

        # Load existing content
        text_widget.insert('1.0', lesson['content'])

        # Focus on text widget
        text_widget.focus_set()

        # Auto-save functionality
        def auto_save():
            content = text_widget.get('1.0', tk.END).strip()
            self.lessons[index]['content'] = content
            self.save_lessons()
            editor_window.after(30000, auto_save)  # Auto-save every 30 seconds

        auto_save()

    def preview_lesson(self, index):
        """Preview lesson in built-in viewer"""
        lesson = self.lessons[index]
        self.preview_lesson_content(index, lesson['content'])

    def preview_lesson_content(self, index, content):
        """Show lesson content in a built-in HTML-style viewer"""
        lesson = self.lessons[index]

        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title(f"Preview: {lesson['name']}")
        preview_window.geometry("900x700")
        preview_window.configure(bg="#f5f5f5")

        # Header with back button
        header_frame = tk.Frame(preview_window, bg="#9C27B0", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        back_button = tk.Button(
            header_frame,
            text="← Back",
            font=('Segoe UI', 10, 'bold'),
            bg="#7B1FA2",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2",
            command=preview_window.destroy
        )
        back_button.pack(side=tk.LEFT, padx=15, pady=15)

        title_label = tk.Label(
            header_frame,
            text=f"👁️ {lesson['name']}",
            font=('Segoe UI', 14, 'bold'),
            fg="white",
            bg="#9C27B0"
        )
        title_label.pack(side=tk.LEFT, pady=15)

        # Save as HTML button
        save_html_button = tk.Button(
            header_frame,
            text="💾 Save HTML",
            font=('Segoe UI', 9, 'bold'),
            bg="#FF9800",
            fg="white",
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            command=lambda: self.save_html_file(lesson, content)
        )
        save_html_button.pack(side=tk.RIGHT, padx=15, pady=15)

        # Content area with styled display
        content_frame = tk.Frame(preview_window, bg="white", padx=30, pady=30)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Lesson title
        title_display = tk.Label(
            content_frame,
            text=f"📚 {lesson['name']}",
            font=('Segoe UI', 18, 'bold'),
            fg="#333333",
            bg="white",
            anchor="w"
        )
        title_display.pack(fill=tk.X, pady=(0, 20))

        # Separator line
        separator = tk.Frame(content_frame, height=3, bg="#2196F3")
        separator.pack(fill=tk.X, pady=(0, 20))

        # Content display area with scrollbar
        text_frame = tk.Frame(content_frame, bg="white")
        text_frame.pack(fill=tk.BOTH, expand=True)

        content_display = tk.Text(
            text_frame,
            font=('Segoe UI', 12),
            bg="white",
            fg="#333333",
            relief=tk.FLAT,
            bd=0,
            padx=0,
            pady=0,
            wrap=tk.WORD,
            state=tk.DISABLED,
            cursor="arrow"
        )

        content_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=content_display.yview)
        content_display.configure(yscrollcommand=content_scrollbar.set)

        content_display.pack(side="left", fill="both", expand=True)
        content_scrollbar.pack(side="right", fill="y")

        # Format and insert content
        content_display.config(state=tk.NORMAL)
        content_display.delete('1.0', tk.END)

        if content.strip():
            # Format content with better line spacing
            formatted_content = content.replace('\n\n', '\n\n')  # Preserve paragraph breaks
            content_display.insert('1.0', formatted_content)
        else:
            content_display.insert('1.0', "This lesson is empty. Click 'Back' and start editing to add content!")

        content_display.config(state=tk.DISABLED)

        # Footer
        footer_label = tk.Label(
            content_frame,
            text="Generated by Lesson Manager",
            font=('Segoe UI', 9),
            fg="#888888",
            bg="white"
        )
        footer_label.pack(pady=(20, 0))

    def save_html_file(self, lesson, content):
        """Save lesson as HTML file locally"""
        # Create HTML content with modern styling
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{lesson['name']}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #2196F3;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }}
        .content {{
            white-space: pre-wrap;
            font-size: 16px;
            line-height: 1.8;
            color: #444;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #888;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 {lesson['name']}</h1>
        <div class="content">{content}</div>
        <div class="footer">
            Generated by Lesson Manager
        </div>
    </div>
</body>
</html>"""

        # Save HTML file in the same directory as the executable
        safe_filename = "".join(c for c in lesson['name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        html_filename = os.path.join(os.path.dirname(self.data_file), f"{safe_filename}.html")

        try:
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            messagebox.showinfo("HTML Saved", f"HTML file saved as:\n{html_filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save HTML file: {str(e)}")

    def save_lesson_content(self, index, text_widget, window):
        """Save lesson content"""
        content = text_widget.get('1.0', tk.END).strip()
        self.lessons[index]['content'] = content
        self.save_lessons()
        self.display_lessons()
        messagebox.showinfo("Saved", "Lesson saved successfully!")

    def load_lessons(self):
        """Load lessons from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_lessons(self):
        """Save lessons to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.lessons, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")

    def run(self):
        """Start the application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = LessonManager()
    app.run()