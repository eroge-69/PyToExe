"""
Advanced Junk Cleaner - Python GUI (PySimpleGUI)

Features:
- Scan common junk locations (User Temp, Windows Temp, Prefetch, SoftwareDistribution Downloads)
- Preview files and total size before deletion
- Option to empty Recycle Bin (uses Windows API)
- Select which categories to clean
- Progress log and progress bar
- Admin check and warning
- Ignore-list support (skip selected files/folders)
- Scheduling support (create Windows Task Scheduler entry for auto-clean)
- Detailed file explorer view for scanned junk files

How to run:
1. Install requirements:
   pip install PySimpleGUI
2. Run as Administrator for best results (right-click -> Run as administrator):
   python Advanced_Junk_Cleaner.py

To bundle to EXE (optional):
   pip install pyinstaller
   pyinstaller --onefile --noconsole --icon=youricon.ico Advanced_Junk_Cleaner.py

IMPORTANT SAFETY NOTES:
- This tool deletes files permanently. Use Preview and uncheck any folders you don't trust.
- Do NOT add system directories other than the entries included (Prefetch, Windows Temp) unless you know what you're doing.

"""

import os
import sys
import threading
import time
import shutil
import ctypes
from pathlib import Path
import traceback

try:
    import PySimpleGUI as sg
except Exception:
    sg = None

# ---------------------------- Utilities ----------------------------

def is_windows_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T','P']:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}P{suffix}"

# Folders we will scan by default
DEFAULT_LOCATIONS = {
    'User Temp': lambda: Path(os.getenv('TEMP') or Path.home() / 'AppData' / 'Local' / 'Temp'),
    'Windows Temp': lambda: Path(r'C:\Windows\Temp'),
    'Prefetch': lambda: Path(r'C:\Windows\Prefetch'),
    'Windows Update Download Cache': lambda: Path(r'C:\Windows\SoftwareDistribution\Download'),
}

IGNORE_LIST = set()  # paths to skip

# ---------------------------- Scanning / Deleting ----------------------------

def scan_paths(selected_keys, window=None, stop_event=None):
    result = {}
    for key in selected_keys:
        if stop_event and stop_event.is_set():
            break
        try:
            base = DEFAULT_LOCATIONS[key]()
        except Exception:
            base = None
        if not base or not base.exists():
            result[key] = {'count': 0, 'size': 0, 'examples': [], 'files': []}
            continue

        total_size = 0
        total_count = 0
        examples = []
        files_list = []

        for root, dirs, files in os.walk(base, topdown=True):
            for f in files:
                try:
                    fp = Path(root) / f
                    if any(str(fp).startswith(ig) for ig in IGNORE_LIST):
                        continue
                    total_count += 1
                    try:
                        size = fp.stat().st_size
                        total_size += size
                    except Exception:
                        size = 0
                    if len(examples) < 10:
                        examples.append(str(fp))
                    files_list.append((str(fp), size))
                except Exception:
                    pass
            if stop_event and stop_event.is_set():
                break

        result[key] = {'count': total_count, 'size': total_size, 'examples': examples, 'files': files_list}
        if window:
            window.write_event_value('-SCAN-UPDATE-', (key, result[key]))
    return result


def delete_paths(selected_keys, window=None, stop_event=None):
    summary = {}
    for key in selected_keys:
        if stop_event and stop_event.is_set():
            break
        try:
            base = DEFAULT_LOCATIONS[key]()
        except Exception:
            base = None
        deleted = 0
        freed = 0
        errors = 0
        if base and base.exists():
            for root, dirs, files in os.walk(base, topdown=False):
                if stop_event and stop_event.is_set():
                    break
                for f in files:
                    try:
                        fp = Path(root) / f
                        if any(str(fp).startswith(ig) for ig in IGNORE_LIST):
                            continue
                        size = fp.stat().st_size if fp.exists() else 0
                        fp.unlink()
                        deleted += 1
                        freed += size
                        if window:
                            window.write_event_value('-DELETE-LOG-', f"Deleted: {fp}")
                    except Exception as e:
                        errors += 1
                for d in dirs:
                    try:
                        dp = Path(root) / d
                        if dp.exists() and not any(dp.iterdir()):
                            dp.rmdir()
                    except Exception:
                        pass
        summary[key] = {'deleted': deleted, 'freed': freed, 'errors': errors}
    return summary

# Recycle bin empty using Shell API
def empty_recycle_bin(window=None):
    try:
        flags = 0x00000001 | 0x00000002
        res = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, flags)
        if window:
            window.write_event_value('-DELETE-LOG-', 'Recycle Bin emptied (Windows API returned: %s)' % res)
        return True
    except Exception as e:
        if window:
            window.write_event_value('-DELETE-LOG-', f'Failed to empty Recycle Bin: {e}')
        return False

# ---------------------------- GUI ----------------------------

def build_window():
    if sg is None:
        raise RuntimeError('PySimpleGUI is not installed. Run: pip install PySimpleGUI')

    sg.theme('DarkBlue3')

    left_col = [[sg.Text('Select categories to scan / clean:', font=('Any', 12, 'bold'))]]
    for k in DEFAULT_LOCATIONS.keys():
        left_col.append([sg.Checkbox(k, key=f'-CHK-{k}-', default=True)])
    left_col.append([sg.HorizontalSeparator()])
    left_col.append([sg.Checkbox('Also empty Recycle Bin', key='-CHK-RECYCLE-', default=True)])

    control_col = [
        [sg.Button('Scan', key='-SCAN-'), sg.Button('Clean', key='-CLEAN-', button_color=('white','firebrick3'))],
        [sg.Button('Stop', key='-STOP-', disabled=True)],
        [sg.Button('Add Ignore Path', key='-ADD-IGNORE-'), sg.Button('View Ignore List', key='-VIEW-IGNORE-')],
        [sg.Button('Schedule Auto-Clean', key='-SCHEDULE-')],
        [sg.Text('Progress:'), sg.ProgressBar(100, orientation='h', size=(30, 12), key='-PROG-')],
    ]

    right_col = [
        [sg.Text('Scan Results:', font=('Any', 12, 'bold'))],
        [sg.Multiline('', size=(70, 15), key='-RESULTS-', autoscroll=True, disabled=True)],
        [sg.Text('Detailed Files:'), sg.Listbox([], size=(70,10), key='-FILELIST-', enable_events=True)],
    ]

    layout = [
        [sg.Column(left_col, vertical_alignment='top'), sg.VerticalSeparator(), sg.Column([[sg.Column(control_col)], [sg.Column(right_col)]])],
        [sg.Text('Log:', font=('Any', 11, 'bold'))],
        [sg.Multiline('', size=(100, 8), key='-LOG-', autoscroll=True, disabled=True)],
        [sg.Text('Status: Not started', key='-STATUS-')]
    ]

    return sg.Window('Advanced Junk Cleaner', layout, finalize=True, resizable=True)

# ---------------------------- Scheduler ----------------------------

def create_scheduled_task():
    try:
        task_name = 'AdvancedJunkCleaner_Auto'
        exe_path = sys.executable
        script_path = Path(__file__).resolve()
        command = f'schtasks /Create /SC DAILY /TN {task_name} /TR "\"{exe_path}\" \"{script_path}\" --auto-clean" /F'
        os.system(command)
        sg.popup_ok('Scheduled Task created: Daily auto-clean at default time.', title='Scheduler')
    except Exception as e:
        sg.popup_error(f'Failed to create scheduled task: {e}')

# ---------------------------- Controller ----------------------------

class CleanerController:
    def __init__(self, window):
        self.window = window
        self.worker = None
        self.stop_event = threading.Event()

    def get_selected_categories(self):
        keys = []
        for k in DEFAULT_LOCATIONS.keys():
            if self.window[f'-CHK-{k}-'].get():
                keys.append(k)
        return keys

    def do_scan(self):
        self.stop_event.clear()
        keys = self.get_selected_categories()
        self.window['-STATUS-'].update('Scanning...')
        self.window['-SCAN-'].update(disabled=True)
        self.window['-STOP-'].update(disabled=False)
        self.worker = threading.Thread(target=self._scan_task, args=(keys,))
        self.worker.start()

    def _scan_task(self, keys):
        try:
            results = scan_paths(keys, window=self.window, stop_event=self.stop_event)
            self.window.write_event_value('-SCAN-DONE-', results)
        except Exception as e:
            self.window.write_event_value('-ERROR-', str(e))

    def do_clean(self):
        if not is_windows_admin():
            sg.popup_ok('Warning: For full cleaning (Windows folders & Recycle Bin) run this program as Administrator.', title='Admin required')
        confirm = sg.popup_yes_no('This will permanently delete files in the selected locations. Continue?', title='Confirm Cleanup')
        if confirm != 'Yes':
            return
        self.stop_event.clear()
        keys = self.get_selected_categories()
        self.window['-STATUS-'].update('Cleaning...')
        self.window['-CLEAN-'].update(disabled=True)
        self.window['-STOP-'].update(disabled=False)
        self.worker = threading.Thread(target=self._clean_task, args=(keys,))
        self.worker.start()

    def _clean_task(self, keys):
        try:
            summary = delete_paths(keys, window=self.window, stop_event=self.stop_event)
            if self.window['-CHK-RECYCLE-'].get():
                empty_recycle_bin(window=self.window)
            self.window.write_event_value('-CLEAN-DONE-', summary)
        except Exception as e:
            tb = traceback.format_exc()
            self.window.write_event_value('-ERROR-', f"Exception: {e}\n{tb}")

    def stop(self):
        self.stop_event.set()
        self.window['-STATUS-'].update('Stopping...')

# ---------------------------- Main ----------------------------

def main():
    if sg is None:
        print('PySimpleGUI not installed. Run: pip install PySimpleGUI')
        sys.exit(1)

    if '--auto-clean' in sys.argv:
        delete_paths(DEFAULT_LOCATIONS.keys())
        empty_recycle_bin()
        return

    window = build_window()
    controller = CleanerController(window)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == '-SCAN-':
            window['-RESULTS-'].update('')
            window['-LOG-'].update('')
            controller.do_scan()
        elif event == '-STOP-':
            controller.stop()
        elif event == '-SCAN-UPDATE-':
            key, info = values['-SCAN-UPDATE-']
            window['-RESULTS-'].print(f"{key}: {info['count']} files, {sizeof_fmt(info['size'])}")
            if info['files']:
                window['-FILELIST-'].update([f"{f} ({sizeof_fmt(sz)})" for f, sz in info['files'][:50]])
        elif event == '-SCAN-DONE-':
            results = values['-SCAN-DONE-']
            window['-RESULTS-'].print('\nScan completed. Summary:')
            total_files = 0
            total_size = 0
            for k, v in results.items():
                window['-RESULTS-'].print(f"{k}: {v['count']} files, {sizeof_fmt(v['size'])}")
                total_files += v['count']
                total_size += v['size']
            window['-RESULTS-'].print(f"\nTotal: {total_files} files, {sizeof_fmt(total_size)}")
            window['-STATUS-'].update('Scan completed')
            window['-SCAN-'].update(disabled=False)
            window['-STOP-'].update(disabled=True)
        elif event == '-CLEAN-':
            controller.do_clean()
        elif event == '-DELETE-LOG-':
            window['-LOG-'].print(values['-DELETE-LOG-'])
        elif event == '-CLEAN-DONE-':
            summary = values['-CLEAN-DONE-']
            window['-LOG-'].print('\nCleanup finished. Summary:')
            total_deleted = 0
            total_freed = 0
            for k, v in summary.items():
                window['-LOG-'].print(f"{k}: deleted {v['deleted']} files, freed {sizeof_fmt(v['freed'])}, errors: {v['errors']}")
                total_deleted += v['deleted']
                total_freed += v['freed']
            window['-LOG-'].print(f"\nTotal deleted: {total_deleted} files, Total freed: {sizeof_fmt(total_freed)}")
            window['-STATUS-'].update('Cleaning completed')
            window['-CLEAN-'].update(disabled=False)
            window['-STOP-'].update(disabled=True)
        elif event == '-ERROR-':
            window['-LOG-'].print('\nERROR: ' + str(values['-ERROR-']))
            window['-STATUS-'].update('Error')
            window['-SCAN-'].update(disabled=False)
            window['-CLEAN-'].update(disabled=False)
            window['-STOP-'].update(disabled=True)
        elif event == '-ADD-IGNORE-':
            path = sg.popup_get_file('Select file or folder to ignore', no_window=True)
            if path:
                IGNORE_LIST.add(path)
                sg.popup_ok(f'Added to ignore list: {path}')
        elif event == '-VIEW-IGNORE-':
            if IGNORE_LIST:
                sg.popup_ok("Ignore List:\n" + "\n".join(IGNORE_LIST))
            else:
                sg.popup_ok('Ignore list is empty.')
        elif event == '-SCHEDULE-':
            create_scheduled_task()

    window.close()

if __name__ == '__main__':
    main()
