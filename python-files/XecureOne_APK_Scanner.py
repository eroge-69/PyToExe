import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from androguard.misc import AnalyzeAPK


def analyze_apk(apk_path):
    a, d, dx = AnalyzeAPK(apk_path)
    results = {}

    # Extract permissions
    permissions = a.get_permissions() or []
    results['permissions'] = permissions

    # Detect dangerous permissions using a curated list
    dangerous_suffixes = {
        'READ_SMS', 'SEND_SMS', 'RECEIVE_SMS',
        'READ_CONTACTS', 'WRITE_CONTACTS', 'GET_ACCOUNTS',
        'READ_CALL_LOG', 'WRITE_CALL_LOG',
        'RECORD_AUDIO', 'CAMERA',
        'ACCESS_FINE_LOCATION', 'ACCESS_COARSE_LOCATION',
        'READ_PHONE_STATE', 'CALL_PHONE', 'ADD_VOICEMAIL', 'USE_SIP', 'PROCESS_OUTGOING_CALLS',
        'READ_EXTERNAL_STORAGE', 'WRITE_EXTERNAL_STORAGE',
        'REQUEST_INSTALL_PACKAGES', 'SYSTEM_ALERT_WINDOW', 'BIND_ACCESSIBILITY_SERVICE',
    }
    dangerous_permissions = [
        p for p in permissions if p.rsplit('.', 1)[-1] in dangerous_suffixes
    ]
    results['dangerous_permissions'] = dangerous_permissions

    # Manifest XML and namespace
    manifest_xml = a.get_android_manifest_xml()
    android_ns = '{http://schemas.android.com/apk/res/android}'

    # App-level flags
    app_info = {'debuggable': None, 'allow_backup': None, 'uses_cleartext_traffic': None}
    if manifest_xml is not None:
        app_el = manifest_xml.find('.//application')
        if app_el is not None:
            dbg_attr = app_el.get(android_ns + 'debuggable')
            app_info['debuggable'] = None if dbg_attr is None else (dbg_attr.lower() == 'true')
            backup_attr = app_el.get(android_ns + 'allowBackup')
            app_info['allow_backup'] = None if backup_attr is None else (backup_attr.lower() == 'true')
            clear_attr = app_el.get(android_ns + 'usesCleartextTraffic')
            app_info['uses_cleartext_traffic'] = None if clear_attr is None else (clear_attr.lower() == 'true')
    results['app_info'] = app_info

    # Exported components collection
    def collect_components(tag_name, type_name):
        items = []
        if manifest_xml is None:
            return items
        for comp in manifest_xml.findall('.//' + tag_name):
            name = comp.get(android_ns + 'name') or comp.get('name')
            exported_attr = comp.get(android_ns + 'exported')
            exported = None if exported_attr is None else (exported_attr.lower() == 'true')
            permission = comp.get(android_ns + 'permission')
            has_intent_filter = comp.find('intent-filter') is not None
            items.append({
                'type': type_name,
                'name': name,
                'exported': exported,
                'permission': permission,
                'has_intent_filter': has_intent_filter,
            })
        return items

    exported_components = []
    exported_components.extend(collect_components('activity', 'activity'))
    exported_components.extend(collect_components('service', 'service'))
    exported_components.extend(collect_components('receiver', 'receiver'))
    exported_components.extend(collect_components('provider', 'provider'))
    results['exported_components'] = exported_components

    # Derive vulnerabilities
    vulnerabilities = []

    def add_vuln(severity, title, detail, recommendation):
        vulnerabilities.append({
            'severity': severity,
            'title': title,
            'detail': detail,
            'recommendation': recommendation,
        })

    if app_info['debuggable'] is True:
        add_vuln(
            'High',
            'Application is debuggable',
            'android:debuggable is set to true in the manifest.',
            'Disable debug builds for production. Remove android:debuggable or set to false.'
        )

    if app_info['allow_backup'] is True:
        add_vuln(
            'Medium',
            'Backup is enabled',
            'android:allowBackup is true which can allow ADB backup of app data.',
            'Set android:allowBackup="false" for production if backups are not intended.'
        )

    if app_info['uses_cleartext_traffic'] is True:
        add_vuln(
            'High',
            'Cleartext traffic allowed',
            'android:usesCleartextTraffic is true which allows HTTP/plaintext traffic.',
            'Disable cleartext traffic or restrict via Network Security Config. Use HTTPS.'
        )

    for perm in dangerous_permissions:
        suffix = perm.rsplit('.', 1)[-1]
        sev = 'High' if suffix in {'RECORD_AUDIO', 'CAMERA', 'READ_SMS', 'SEND_SMS', 'RECEIVE_SMS', 'ACCESS_FINE_LOCATION'} else 'Medium'
        add_vuln(
            sev,
            f'Uses dangerous permission: {suffix}',
            f'The app requests {perm}.',
            'Ensure permission is strictly necessary and guarded by runtime checks.'
        )

    for comp in exported_components:
        exported = comp['exported']
        implicitly_exported = exported is None and comp['has_intent_filter'] is True
        is_exported = (exported is True) or implicitly_exported
        missing_protection = (comp['permission'] is None)
        if is_exported and missing_protection:
            add_vuln(
                'High',
                f"Exported {comp['type']} without permission",
                f"Component {comp['name']} is exported and lacks permission protection.",
                'Set android:exported="false" or add android:permission to restrict access.'
            )

    results['vulnerabilities'] = vulnerabilities
    return results


class APKDeepLensGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('XecureOne x NZT Foundation - APK Security Analyzer')
        self.geometry('980x640')
        self.minsize(860, 560)
        self._configure_style()
        self._build_ui()
        self.apk_path = None

    def _configure_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass
        style.configure('TButton', padding=8)
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'))
        style.configure('Body.TLabel', font=('Segoe UI', 10))
        style.configure('Path.TLabel', foreground='#555')
        style.configure('Danger.Treeview', rowheight=24)

    def _build_ui(self):
        top_frame = ttk.Frame(self, padding=12)
        top_frame.pack(fill='x')

        header = ttk.Label(top_frame, text='XecureOne x NZT Foundation - APK Security Analysis', style='Header.TLabel')
        header.pack(anchor='w')

        # Add subtitle with branding
        subtitle = ttk.Label(top_frame, text='Advanced Android Application Security Assessment Tool', style='Body.TLabel')
        subtitle.pack(anchor='w', pady=(2, 0))

        controls = ttk.Frame(top_frame)
        controls.pack(fill='x', pady=(8, 0))

        pick_btn = ttk.Button(controls, text='Choose APK…', command=self._pick_apk)
        pick_btn.pack(side='left')

        self.path_var = tk.StringVar(value='No file selected')
        path_lbl = ttk.Label(controls, textvariable=self.path_var, style='Path.TLabel')
        path_lbl.pack(side='left', padx=10)

        self.analyze_btn = ttk.Button(controls, text='Analyze', command=self._start_analysis, state='disabled')
        self.analyze_btn.pack(side='right')

        self.progress = ttk.Progressbar(controls, mode='indeterminate', length=180)
        self.progress.pack(side='right', padx=(0, 10))

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill='both', expand=True, padx=12, pady=12)

        # Tab: Vulnerabilities
        self.vuln_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.vuln_tab, text='Vulnerabilities')
        self.vuln_container, self.vuln_tree = self._create_tree(self.vuln_tab, columns=("Severity", "Issue", "Details", "Recommendation"))
        self.vuln_container.pack(fill='both', expand=True)
        self._configure_vuln_tags()

        # Tab: Permissions
        self.perm_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.perm_tab, text='Permissions')
        self.perm_container, self.perm_tree = self._create_tree(self.perm_tab, columns=("Permission",))
        self.perm_container.pack(fill='both', expand=True)

        # Tab: Exported Components
        self.comp_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.comp_tab, text='Components')
        self.comp_container, self.comp_tree = self._create_tree(self.comp_tab, columns=("Type", "Name", "Exported", "Permission"))
        self.comp_container.pack(fill='both', expand=True)

        # Status bar
        self.status_var = tk.StringVar(value='Ready')
        status = ttk.Label(self, textvariable=self.status_var, anchor='w', padding=(12, 6))
        status.pack(fill='x')

    def _create_tree(self, parent, columns):
        container = ttk.Frame(parent)
        tree = ttk.Treeview(container, columns=columns, show='headings', style='Danger.Treeview')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor='w', width=160, stretch=True)
        vsb = ttk.Scrollbar(container, orient='vertical', command=tree.yview)
        hsb = ttk.Scrollbar(container, orient='horizontal', command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        return container, tree

    def _configure_vuln_tags(self):
        # Apply background colors for severity
        self.vuln_tree.tag_configure('High', background='#ffe5e5')
        self.vuln_tree.tag_configure('Medium', background='#fff5e6')
        self.vuln_tree.tag_configure('Low', background='#eef7ff')

    def _pick_apk(self):
        path = filedialog.askopenfilename(
            title='Select APK',
            filetypes=[('Android Packages', '*.apk'), ('All Files', '*.*')]
        )
        if not path:
            return
        self.apk_path = path
        self.path_var.set(path)
        self.analyze_btn.config(state='normal')
        self.status_var.set('APK ready to analyze')

    def _start_analysis(self):
        if not self.apk_path:
            messagebox.showwarning('No file', 'Please choose an APK first.')
            return
        self._clear_results()
        self.progress.start(10)
        self.analyze_btn.config(state='disabled')
        self.status_var.set('Analyzing…')
        threading.Thread(target=self._analyze_thread, daemon=True).start()

    def _analyze_thread(self):
        try:
            results = analyze_apk(self.apk_path)
            self.after(0, lambda: self._populate_results(results))
        except Exception as exc:
            self.after(0, lambda: messagebox.showerror('Analysis error', str(exc)))
        finally:
            self.after(0, self._analysis_done)

    def _analysis_done(self):
        self.progress.stop()
        self.analyze_btn.config(state='normal')
        self.status_var.set('Done')

    def _clear_results(self):
        for tree in (self.vuln_tree, self.perm_tree, self.comp_tree):
            for item in tree.get_children():
                tree.delete(item)

    def _populate_results(self, results):
        # Vulnerabilities
        vulns = results.get('vulnerabilities', [])
        for v in vulns:
            self.vuln_tree.insert('', 'end', values=(v['severity'], v['title'], v['detail'], v['recommendation']), tags=(v['severity'],))
        if not vulns:
            self.vuln_tree.insert('', 'end', values=('Low', 'No critical issues found', 'Static checks did not find high-risk items.', 'Consider dynamic testing too.'), tags=('Low',))

        # Permissions
        for p in sorted(results.get('permissions', [])):
            self.perm_tree.insert('', 'end', values=(p,))

        # Components
        for c in results.get('exported_components', []):
            exported_str = 'Unknown' if c['exported'] is None else ('Yes' if c['exported'] else 'No')
            self.comp_tree.insert('', 'end', values=(c['type'], c['name'], exported_str, c['permission'] or '-'))


def main():
    # If an APK path is provided, run CLI; else launch GUI
    if len(sys.argv) > 1:
        analysis = analyze_apk(sys.argv[1])
        for key, value in analysis.items():
            print(f"{key}: {value}")
    else:
        app = APKDeepLensGUI()
        app.mainloop()


if __name__ == "__main__":
    main()
