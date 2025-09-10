"""
SysGuard+ — расширенная утилита управления системой (Windows)
Версия: исправленная, рабочая
Требования: Python 3.8+, Windows, pip install psutil
Запуск: python SysGuard_plus_dark_rounded.py
"""

import os
import sys
import threading
import time
import hashlib
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging

# Windows-specific
if os.name != 'nt':
    messagebox.showwarning("Платформа", "Эта программа рассчитана на Windows. Некоторые функции не будут работать.")

try:
    import psutil
except ImportError:
    psutil = None

try:
    import winreg
except ImportError:
    winreg = None

# ----------------- Logging -----------------
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs') if '__file__' in globals() else os.path.join(os.getcwd(),'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'sysguard.log')

logger = logging.getLogger('SysGuard')
logger.setLevel(logging.INFO)
fh = logging.FileHandler(LOG_FILE, encoding='utf-8')
fmt = logging.Formatter('%(asctime)s\t%(levelname)s\t%(message)s')
fh.setFormatter(fmt)
logger.addHandler(fh)

def log_info(msg):
    logger.info(msg)

def export_logs(dest_path):
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as src, open(dest_path, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
        return True, 'Экспорт логов завершён.'
    except Exception as e:
        return False, str(e)

# ----------------- Helpers -----------------
def ensure_psutil():
    if psutil is None:
        messagebox.showerror("Отсутствует psutil",
                             "Модуль psutil не установлен. Установи: pip install psutil и перезапусти программу.")
        return False
    return True

def human_size(bytes_val):
    try:
        bytes_val = float(bytes_val)
    except Exception:
        return str(bytes_val)
    for unit in ['B','KB','MB','GB','TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:3.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} PB"

def sha256_of_file(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
    except Exception:
        return None
    return h.hexdigest()

def run_cmd(cmd):
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True, text=True)
        return out
    except subprocess.CalledProcessError as e:
        return e.output

# ----------------- Autoruns -----------------
def get_startup_folders():
    folders = []
    try:
        folders.append(("HK_STARTUP_CURRENT_USER", os.path.join(os.environ['APPDATA'], r'Microsoft\\Windows\\Start Menu\\Programs\\Startup')))
        folders.append(("HK_STARTUP_ALL_USERS", os.path.join(os.environ.get('PROGRAMDATA', r'C:\\ProgramData'), r'Microsoft\\Windows\\Start Menu\\Programs\\Startup')))
    except Exception:
        pass
    return folders

def list_startup_folder_items(path):
    items = []
    if os.path.exists(path):
        for name in os.listdir(path):
            full = os.path.join(path, name)
            items.append((name, full))
    return items

def read_run_keys():
    entries = []
    if winreg is None:
        return entries
    roots = [
        ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"),
        ("HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", winreg.HKEY_LOCAL_MACHINE, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"),
        ("HKLM\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Run", winreg.HKEY_LOCAL_MACHINE, r"Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Run")
    ]
    for display_name, root_const, subpath in roots:
        try:
            key = winreg.OpenKey(root_const, subpath)
            i = 0
            while True:
                try:
                    val = winreg.EnumValue(key, i)
                    entries.append({
                        'source': display_name,
                        'root_const': root_const,
                        'subpath': subpath,
                        'name': val[0],
                        'value': val[1],
                        'type': val[2]
                    })
                    i += 1
                except OSError:
                    break
        except Exception:
            continue
    return entries

def backup_registry_value(entry):
    if winreg is None:
        return False, "winreg недоступен"
    try:
        root = entry['root_const']
        subpath = entry['subpath']
        name = entry['name']
        val = entry['value']
        vtype = entry['type']
        backup_sub = r"Software\\SysGuardBackup\\" + subpath.replace('Software\\','')
        with winreg.OpenKey(root, subpath, 0, winreg.KEY_READ) as runk:
            with winreg.CreateKeyEx(root, backup_sub, 0, winreg.KEY_WRITE) as bk:
                winreg.SetValueEx(bk, name, 0, vtype, val)
        with winreg.OpenKey(root, subpath, 0, winreg.KEY_WRITE) as runkw:
            try:
                winreg.DeleteValue(runkw, name)
            except FileNotFoundError:
                pass
        log_info(f"Backup autorun: {entry['source']} | {name} -> backup key")
        return True, 'Отключено и сохранено в бекапе.'
    except PermissionError:
        return False, 'Требуются права администратора для изменения реестра.'
    except Exception as e:
        return False, str(e)

def restore_registry_value(entry):
    if winreg is None:
        return False, "winreg недоступен"
    try:
        root = entry['root_const']
        subpath = entry['subpath']
        name = entry['name']
        backup_sub = r"Software\\SysGuardBackup\\" + subpath.replace('Software\\','')
        with winreg.OpenKey(root, backup_sub, 0, winreg.KEY_READ) as bk:
            i = 0
            found = False
            while True:
                try:
                    val = winreg.EnumValue(bk, i)
                    if val[0] == name:
                        with winreg.CreateKeyEx(root, subpath, 0, winreg.KEY_WRITE) as runk:
                            winreg.SetValueEx(runk, name, 0, val[2], val[1])
                        with winreg.OpenKey(root, backup_sub, 0, winreg.KEY_WRITE) as bkw:
                            winreg.DeleteValue(bkw, name)
                        found = True
                        break
                    i += 1
                except OSError:
                    break
        if found:
            log_info(f"Restore autorun: {entry['source']} | {name} restored")
            return True, 'Восстановлено из бекапа.'
        else:
            return False, 'Не найдено в бекапе.'
    except PermissionError:
        return False, 'Требуются права администратора для изменения реестра.'
    except Exception as e:
        return False, str(e)

# ----------------- Services -----------------
def list_services():
    if not ensure_psutil():
        return []
    services = []
    try:
        for s in psutil.win_service_iter():
            try:
                info = s.as_dict()
                services.append(info)
            except Exception:
                continue
    except Exception:
        pass
    return services

def control_service(name, action):
    if action not in ('start','stop'):
        return False, 'Неверное действие'
    cmd = f'sc {action} "{name}"'
    try:
        out = run_cmd(cmd)
        log_info(f"Service {action}: {name} | {out.strip()[:200]}")
        return True, out
    except Exception as e:
        return False, str(e)

# ----------------- Processes -----------------
def list_processes():
    if not ensure_psutil():
        return []
    procs = []
    for p in psutil.process_iter(['pid','name','username','cpu_percent','memory_info','exe','open_files']):
        try:
            mem = p.info.get('memory_info')
            mem_r = mem.rss if mem else 0
            procs.append({
                'pid': p.info['pid'],
                'name': p.info.get('name',''),
                'user': p.info.get('username',''),
                'cpu': p.info.get('cpu_percent',0.0),
                'memory': mem_r,
                'exe': p.info.get('exe','')
            })
        except Exception:
            continue
    return procs

def kill_process(pid):
    if not ensure_psutil():
        return False, 'psutil отсутствует'
    try:
        p = psutil.Process(pid)
        p.terminate()
        log_info(f"Process terminated: PID={pid}")
        return True, 'Процесс завершён'
    except Exception as e:
        return False, str(e)

# ----------------- GUI -----------------
class SysGuardGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SysGuard+ Dark Rounded")
        self.geometry("1080x720")
        self.configure(bg="#121212")
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure("Treeview",
                             background="#1E1E1E",
                             foreground="white",
                             fieldbackground="#1E1E1E",
                             font=('Segoe UI', 10))
        self.style.configure("Treeview.Heading", font=('Segoe UI', 11,'bold'), background="#292929", foreground="white")

        # ----------------- Top Panel -----------------
        self.top_panel = tk.Frame(self, bg="#1E1E1E", height=30)
        self.top_panel.pack(fill='x')
        self.cpu_label = tk.Label(self.top_panel, text="CPU: 0%", bg="#1E1E1E", fg="white")
        self.cpu_label.pack(side='left', padx=10)
        self.ram_label = tk.Label(self.top_panel, text="RAM: 0%", bg="#1E1E1E", fg="white")
        self.ram_label.pack(side='left', padx=10)
        self.proc_search_var = tk.StringVar()
        self.serv_search_var = tk.StringVar()

        self.create_widgets()
        self._start_periodic_updates()

    def create_widgets(self):
        tab_control = ttk.Notebook(self)
        tab_control.pack(expand=1, fill='both')

        # Tabs
        self.tab_processes = ttk.Frame(tab_control)
        self.tab_services = ttk.Frame(tab_control)
        self.tab_autoruns = ttk.Frame(tab_control)
        self.tab_logs = ttk.Frame(tab_control)
        self.tab_multitool = ttk.Frame(tab_control)

        tab_control.add(self.tab_processes, text='Процессы')
        tab_control.add(self.tab_services, text='Сервисы')
        tab_control.add(self.tab_autoruns, text='Автозапуск')
        tab_control.add(self.tab_logs, text='Логи')
        tab_control.add(self.tab_multitool, text='Мультитул')

        # ----------------- Процессы -----------------
        tk.Label(self.tab_processes, text="Поиск процессов:", bg="#121212", fg="white").pack(anchor='nw', padx=10)
        tk.Entry(self.tab_processes, textvariable=self.proc_search_var).pack(anchor='nw', padx=10, pady=2)
        self.proc_tree = ttk.Treeview(self.tab_processes, columns=('PID','Name','CPU','Memory'), show='headings')
        for c in ('PID','Name','CPU','Memory'):
            self.proc_tree.heading(c, text=c)
            self.proc_tree.column(c, width=150)
        self.proc_tree.pack(expand=1, fill='both', padx=10, pady=10)
        btn_kill = tk.Button(self.tab_processes, text="Завершить выбранные процессы", command=self.kill_selected_processes)
        btn_kill.pack(pady=5)

        # ----------------- Сервисы -----------------
        tk.Label(self.tab_services, text="Поиск сервисов:", bg="#121212", fg="white").pack(anchor='nw', padx=10)
        tk.Entry(self.tab_services, textvariable=self.serv_search_var).pack(anchor='nw', padx=10, pady=2)
        self.serv_tree = ttk.Treeview(self.tab_services, columns=('Name','Status','DisplayName'), show='headings')
        for c in ('Name','Status','DisplayName'):
            self.serv_tree.heading(c, text=c)
            self.serv_tree.column(c, width=250)
        self.serv_tree.pack(expand=1, fill='both', padx=10, pady=10)
        btn_start = tk.Button(self.tab_services, text="Запустить", command=lambda: self.control_selected_service('start'))
        btn_stop = tk.Button(self.tab_services, text="Остановить", command=lambda: self.control_selected_service('stop'))
        btn_start.pack(side='left', padx=10, pady=5)
        btn_stop.pack(side='left', padx=10, pady=5)

        # ----------------- Автозапуск -----------------
        self.auto_tree = ttk.Treeview(self.tab_autoruns, columns=('Source','Name','Value'), show='headings')
        for c in ('Source','Name','Value'):
            self.auto_tree.heading(c, text=c)
            self.auto_tree.column(c, width=300)
        self.auto_tree.pack(expand=1, fill='both', padx=10, pady=10)
        btn_disable = tk.Button(self.tab_autoruns, text="Отключить и сохранить в бекапе", command=self.disable_selected_autorun)
        btn_restore = tk.Button(self.tab_autoruns, text="Восстановить из бекапа", command=self.restore_selected_autorun)
        btn_disable.pack(side='left', padx=10, pady=5)
        btn_restore.pack(side='left', padx=10, pady=5)

        # ----------------- Логи -----------------
        self.log_text = tk.Text(self.tab_logs, bg="#1E1E1E", fg="white")
        self.log_text.pack(expand=1, fill='both', padx=10, pady=10)
        btn_export = tk.Button(self.tab_logs, text="Экспортировать логи", command=self.export_logs)
        btn_export.pack(pady=5)

        # ----------------- Мультитул -----------------
        tk.Label(self.tab_multitool, text="SimpleUnlocker: Отключение подозрительных автозапусков", bg="#121212", fg="white").pack(anchor='nw', padx=10, pady=5)
        btn_unlock = tk.Button(self.tab_multitool, text="Отключить все подозрительные автозапуски", command=self.simple_unlocker)
        btn_unlock.pack(pady=10)

    # ----------------- Updates -----------------
    def _start_periodic_updates(self):
        threading.Thread(target=self._update_loop, daemon=True).start()

    def _update_loop(self):
        while True:
            self._update_cpu_ram()
            self._update_processes()
            self._update_services()
            self._update_autoruns()
            self._update_logs()
            time.sleep(2)

    def _update_cpu_ram(self):
        if ensure_psutil():
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            self.cpu_label.config(text=f"CPU: {cpu:.1f}%")
            self.ram_label.config(text=f"RAM: {ram:.1f}%")

    def _update_processes(self):
        if not ensure_psutil():
            return
        procs = list_processes()
        search = self.proc_search_var.get().lower()
        self.proc_tree.delete(*self.proc_tree.get_children())
        for p in procs:
            if search and search not in p['name'].lower():
                continue
            self.proc_tree.insert('', 'end', values=(p['pid'], p['name'], f"{p['cpu']:.1f}%", human_size(p['memory'])))

    def _update_services(self):
        if not ensure_psutil():
            return
        servs = list_services()
        search = self.serv_search_var.get().lower()
        self.serv_tree.delete(*self.serv_tree.get_children())
        for s in servs:
            if search and search not in s['name'].lower() and search not in s.get('display_name','').lower():
                continue
            self.serv_tree.insert('', 'end', values=(s['name'], s['status'], s.get('display_name','')))

    def _update_autoruns(self):
        self.auto_tree.delete(*self.auto_tree.get_children())
        for e in read_run_keys():
            self.auto_tree.insert('', 'end', values=(e['source'], e['name'], e['value']))

    def _update_logs(self):
        try:
            with open(LOG_FILE,'r',encoding='utf-8') as f:
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.END, f.read())
        except Exception:
            pass

    # ----------------- Actions -----------------
    def kill_selected_processes(self):
        sel = self.proc_tree.selection()
        if not sel: return
        results = []
        for s in sel:
            pid = int(self.proc_tree.item(s)['values'][0])
            ok,msg = kill_process(pid)
            results.append(f"PID {pid}: {msg}")
        messagebox.showinfo("Kill processes", "\n".join(results))

    def control_selected_service(self, action):
        sel = self.serv_tree.selection()
        if not sel: return
        name = self.serv_tree.item(sel[0])['values'][0]
        ok,msg = control_service(name, action)
        messagebox.showinfo("Service control", msg)

    def disable_selected_autorun(self):
        sel = self.auto_tree.selection()
        if not sel: return
        idx = self.auto_tree.item(sel[0])['values']
        name = idx[1]
        src = idx[0]
        for e in read_run_keys():
            if e['source']==src and e['name']==name:
                ok,msg = backup_registry_value(e)
                messagebox.showinfo("Autorun disable", msg)
                break

    def restore_selected_autorun(self):
        sel = self.auto_tree.selection()
        if not sel: return
        idx = self.auto_tree.item(sel[0])['values']
        name = idx[1]
        src = idx[0]
        for e in read_run_keys():
            if e['source']==src and e['name']==name:
                ok,msg = restore_registry_value(e)
                messagebox.showinfo("Autorun restore", msg)
                break

    def export_logs(self):
        path = filedialog.asksaveasfilename(title="Сохранить логи", defaultextension=".txt", filetypes=[("Text files","*.txt")])
        if path:
            ok,msg = export_logs(path)
            messagebox.showinfo("Export logs", msg)

    def simple_unlocker(self):
        count = 0
        for e in read_run_keys():
            # Пример: отключаем все автозапуски, которые содержат 'virus' или 'malware' в имени
            if any(k in e['name'].lower() for k in ('virus','malware','bad')):
                ok,msg = backup_registry_value(e)
                if ok:
                    count +=1
        messagebox.showinfo("SimpleUnlocker", f"Отключено {count} подозрительных автозапусков.")

# ----------------- Run -----------------
if __name__ == "__main__":
    app = SysGuardGUI()
    app.mainloop()
