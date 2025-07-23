#!/usr/bin/env python3
"""
GUI application for AI-Assisted Qualitative Research Report JSON to Markdown converter.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import re
from collections import defaultdict
from pathlib import Path
from markdownify import markdownify as md


def replace_paper_tags_with_citations(text):
    """
    Replace <Paper ... paperTitle="(...)"> tags with the actual citation text.
    """
    pattern = r'<Paper[^>]+paperTitle="(?P<citation>\([^)]+\))"[^>]*/?>'
    return re.sub(pattern, lambda match: match.group("citation"), text)


def build_citation_map(report_data):
    """
    Build a mapping of citation keys to reference details.
    """
    citation_map = defaultdict(str)
    
    for section in report_data.get("sections", []):
        for citation in section.get("citations", []):
            authors = citation["id"]
            paper = citation["paper"]
            year = paper.get("year", "n.d.")
            title = paper.get("title", "Untitled")
            venue = paper.get("venue", "")
            author_names = ", ".join(a["name"] for a in paper.get("authors", []))
            ref_str = f"{author_names} ({year}). *{title}*. {venue}".strip()
            citation_map[authors] = ref_str
    
    return citation_map


def convert_json_to_markdown(json_data):
    """
    Convert JSON report data to Markdown format.
    """
    citation_map = build_citation_map(json_data)
    
    md_lines = ["# AI-Assisted Qualitative Research Report", ""]
    used_citations = set()
    
    for section in json_data.get("sections", []):
        title = section.get("title", "Untitled Section")
        text = section.get("text", "")
        citations = section.get("citations", [])
        
        # Replace all <Paper ...> tags with the citation text from the 'paperTitle' attribute
        updated_text = replace_paper_tags_with_citations(text)
        
        # Track citation keys for the reference list
        used_citations.update(c["id"] for c in citations)
        
        # Convert the updated text to markdown
        md_lines.append(f"## {title}")
        md_lines.append("")
        md_lines.append(md(updated_text))
        md_lines.append("")
    
    # Append a references section
    if used_citations:
        md_lines.append("---")
        md_lines.append("## References")
        md_lines.append("")
        
        for key in sorted(used_citations):
            ref_entry = citation_map.get(key)
            if ref_entry:
                md_lines.append(f"- {key}: {ref_entry}")
    
    return "\n".join(md_lines)


class ConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI2 Scholar JSON to Markdown Converter")
        self.root.geometry("600x200")
        self.root.resizable(True, False)
        
        self.selected_file = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # File selection section
        ttk.Label(main_frame, text="Select JSON file:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        file_frame.columnconfigure(1, weight=1)
        
        self.select_button = ttk.Button(file_frame, text="Select File...", command=self.select_file)
        self.select_button.grid(row=0, column=0, padx=(0, 10))
        
        self.file_label = ttk.Label(file_frame, text="No file selected", foreground="gray")
        self.file_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Convert button
        self.convert_button = ttk.Button(main_frame, text="Convert to Markdown", 
                                       command=self.convert_file, state="disabled")
        self.convert_button.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="", foreground="blue")
        self.status_label.grid(row=3, column=0, columnspan=2, pady=(10, 0))
    
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_label.config(text=file_path, foreground="black")
            self.convert_button.config(state="normal")
            self.status_label.config(text="")
        else:
            self.selected_file = None
            self.file_label.config(text="No file selected", foreground="gray")
            self.convert_button.config(state="disabled")
    
    def convert_file(self):
        if not self.selected_file:
            return
        
        try:
            # Update status
            self.status_label.config(text="Converting...", foreground="blue")
            self.root.update()
            
            # Load JSON data
            json_path = Path(self.selected_file)
            with open(json_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            # Convert to markdown
            markdown_content = convert_json_to_markdown(report_data)
            
            # Determine output file path
            output_path = json_path.with_suffix('.md')
            
            # Write output
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            # Success message
            self.status_label.config(text=f"Successfully converted to: {output_path}", foreground="green")
            messagebox.showinfo("Success", f"File converted successfully!\n\nOutput saved to:\n{output_path}")
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON file: {str(e)}"
            self.status_label.config(text="Error: Invalid JSON", foreground="red")
            messagebox.showerror("JSON Error", error_msg)
            
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            self.status_label.config(text="Error occurred", foreground="red")
            messagebox.showerror("Error", error_msg)


def main():
    root = tk.Tk()
    app = ConverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()