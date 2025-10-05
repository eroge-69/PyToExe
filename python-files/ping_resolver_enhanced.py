import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import re
import threading
from typing import Optional
import sys
import locale

class PingResolverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hostname to IP Resolver")
        self.root.geometry("900x650")
        self.root.resizable(True, True)
        
        # Configure grid weights for responsive design
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.create_widgets()
        self.is_processing = False
        
    def create_widgets(self):
        # Title frame
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        title_label = ttk.Label(title_frame, text="Hostname to IP Resolver", 
                                font=('Arial', 14, 'bold'))
        title_label.pack()
        
        info_label = ttk.Label(title_frame, 
                              text="Введите список хостнеймов или импортируйте из лог-файла",
                              font=('Arial', 9))
        info_label.pack()
        
        # Main content frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Left column - Input
        input_frame = ttk.LabelFrame(main_frame, text="Hostnames", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        input_frame.grid_rowconfigure(0, weight=1)
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.input_text = scrolledtext.ScrolledText(input_frame, width=40, height=25, 
                                                     font=('Consolas', 10))
        self.input_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.input_text.insert('1.0', 'pc1.domain.local\npc2.domain.local\npc3.domain.local\nKEFO-OFFICE-03.kf.local')
        
        # Right column - Output
        output_frame = ttk.LabelFrame(main_frame, text="IP Addresses", padding="10")
        output_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, width=40, height=25, 
                                                      font=('Consolas', 10), state='disabled')
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Button frame
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.grid(row=2, column=0)
        
        # First row of buttons
        self.import_button = ttk.Button(button_frame, text="📂 Import from Log", 
                                        command=self.import_from_log)
        self.import_button.pack(side=tk.LEFT, padx=5)
        
        self.resolve_button = ttk.Button(button_frame, text="🔍 Resolve IPs", 
                                         command=self.start_resolution)
        self.resolve_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="🗑️ Clear All", 
                                       command=self.clear_all)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        self.copy_button = ttk.Button(button_frame, text="📋 Copy Results", 
                                      command=self.copy_results)
        self.copy_button.pack(side=tk.LEFT, padx=5)
        
        self.export_button = ttk.Button(button_frame, text="💾 Export to CSV", 
                                        command=self.export_to_csv)
        self.export_button.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W, padding="5")
        status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E))
    
    def import_from_log(self):
        """Import hostnames from log file containing dNSHostName entries"""
        filename = filedialog.askopenfilename(
            title="Выберите лог-файл",
            filetypes=[
                ("Text files", "*.txt"),
                ("Log files", "*.log"),
                ("All files", "*.*")
            ]
        )
        
        if not filename:
            return
        
        try:
            # Try different encodings
            encodings = ['utf-8', 'cp1251', 'cp866', 'latin-1']
            content = None
            
            for encoding in encodings:
                try:
                    with open(filename, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                messagebox.showerror("Ошибка", "Не удалось прочитать файл. Проблема с кодировкой.")
                return
            
            # Extract hostnames from dNSHostName entries
            # Pattern: dNSHostName: HOSTNAME.domain.local
            pattern = r'dNSHostName:\s*([a-zA-Z0-9\-\.]+)'
            matches = re.findall(pattern, content, re.IGNORECASE)
            
            if not matches:
                messagebox.showwarning(
                    "Предупреждение", 
                    "В файле не найдено строк с 'dNSHostName:'\n\n"
                    "Ожидаемый формат:\ndNSHostName: HOSTNAME.domain.local"
                )
                return
            
            # Remove duplicates while preserving order
            unique_hostnames = []
            seen = set()
            for hostname in matches:
                hostname = hostname.strip()
                if hostname and hostname.lower() not in seen:
                    unique_hostnames.append(hostname)
                    seen.add(hostname.lower())
            
            # Clear current input and insert new hostnames
            self.input_text.delete('1.0', tk.END)
            self.input_text.insert('1.0', '\n'.join(unique_hostnames))
            
            # Update status
            self.status_var.set(f"Импортировано {len(unique_hostnames)} хостнеймов из {filename}")
            
            messagebox.showinfo(
                "Успешно", 
                f"Импортировано хостнеймов: {len(unique_hostnames)}\n"
                f"Уникальных: {len(unique_hostnames)}\n\n"
                f"Теперь нажмите 'Resolve IPs' для получения IP-адресов"
            )
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось импортировать файл:\n{e}")
    
    def ping_hostname(self, hostname: str) -> Optional[str]:
        """
        Ping hostname and extract IP address from response
        Returns IP address or None if failed
        """
        try:
            # Detect OS and set appropriate parameters
            import platform
            is_windows = platform.system().lower() == 'windows'
            param = '-n' if is_windows else '-c'
            
            # Set encoding based on OS
            encoding = 'cp866' if is_windows else 'utf-8'
            
            # Run ping command with timeout
            result = subprocess.run(
                ['ping', param, '1', hostname],
                capture_output=True,
                text=True,
                timeout=5,
                encoding=encoding,
                errors='ignore'  # Ignore encoding errors
            )
            
            # Extract IP address from output
            # Pattern for IPv4: xxx.xxx.xxx.xxx
            ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            matches = re.findall(ip_pattern, result.stdout)
            
            if matches:
                # Return first IP found (usually the resolved IP)
                return matches[0]
            else:
                return None
                
        except subprocess.TimeoutExpired:
            return None
        except Exception as e:
            print(f"Error pinging {hostname}: {e}")
            return None
    
    def resolve_hostnames(self):
        """Process all hostnames and resolve to IPs"""
        # Get hostnames from input
        input_content = self.input_text.get('1.0', tk.END)
        hostnames = [line.strip() for line in input_content.split('\n') if line.strip()]
        
        if not hostnames:
            self.status_var.set("Нет хостнеймов для обработки")
            self.is_processing = False
            self.resolve_button.config(state='normal')
            return
        
        # Clear output
        self.output_text.config(state='normal')
        self.output_text.delete('1.0', tk.END)
        
        # Store results for export
        self.results = []
        
        # Process each hostname
        total = len(hostnames)
        for idx, hostname in enumerate(hostnames, 1):
            self.status_var.set(f"Обработка {idx}/{total}: {hostname}")
            self.root.update_idletasks()
            
            ip = self.ping_hostname(hostname)
            
            if ip:
                self.output_text.insert(tk.END, f"{ip}\n")
                self.results.append((hostname, ip))
            else:
                self.output_text.insert(tk.END, f"N/A\n")
                self.results.append((hostname, "N/A"))
            
            self.output_text.see(tk.END)
            self.root.update_idletasks()
        
        self.output_text.config(state='disabled')
        self.status_var.set(f"Завершено: обработано {total} хостнеймов")
        self.is_processing = False
        self.resolve_button.config(state='normal')
    
    def start_resolution(self):
        """Start resolution process in a separate thread"""
        if self.is_processing:
            return
        
        self.is_processing = True
        self.resolve_button.config(state='disabled')
        
        # Run in separate thread to keep GUI responsive
        thread = threading.Thread(target=self.resolve_hostnames, daemon=True)
        thread.start()
    
    def clear_all(self):
        """Clear both input and output fields"""
        self.input_text.delete('1.0', tk.END)
        self.output_text.config(state='normal')
        self.output_text.delete('1.0', tk.END)
        self.output_text.config(state='disabled')
        self.status_var.set("Очищено")
        self.results = []
    
    def copy_results(self):
        """Copy results to clipboard"""
        output_content = self.output_text.get('1.0', tk.END).strip()
        if output_content:
            self.root.clipboard_clear()
            self.root.clipboard_append(output_content)
            self.status_var.set("Результаты скопированы в буфер обмена")
            messagebox.showinfo("Успешно", "Результаты скопированы в буфер обмена!")
        else:
            messagebox.showwarning("Предупреждение", "Нет результатов для копирования")
    
    def export_to_csv(self):
        """Export results to CSV file"""
        if not hasattr(self, 'results') or not self.results:
            messagebox.showwarning("Предупреждение", "Нет результатов для экспорта")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Сохранить результаты"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8-sig') as f:
                    f.write("Hostname,IP Address\n")
                    for hostname, ip in self.results:
                        f.write(f"{hostname},{ip}\n")
                self.status_var.set(f"Экспортировано в {filename}")
                messagebox.showinfo("Успешно", f"Результаты сохранены в:\n{filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

def main():
    root = tk.Tk()
    
    # Set icon if available (optional)
    try:
        # You can add an icon file here
        # root.iconbitmap('icon.ico')
        pass
    except:
        pass
    
    app = PingResolverApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
