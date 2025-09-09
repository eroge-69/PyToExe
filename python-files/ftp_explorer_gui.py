"""
ftp_explorer_gui.py

Tkinter GUI FTP Explorer for mobile FTP server.
Defaults (auto-connect):
    host=192.168.144.64
    port=2221
    user=android
    passwd=android

Features:
 - Tree view of remote files/folders (lazy-load on expand)
 - Refresh current node
 - Download selected file to a user-chosen local folder (button)
 - Status bar and basic logging
 - Manual connect controls to change host/port/credentials

Run:
    python ftp_explorer_gui.py

Only Python standard library required (tested on Python 3.9+).
"""

import ftplib
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
import time

DEFAULT_HOST = "192.168.144.64"
DEFAULT_PORT = 2221
DEFAULT_USER = "android"
DEFAULT_PASS = "android"

# Helper: run a function in a background thread
def run_bg(fn):
    t = threading.Thread(target=fn, daemon=True)
    t.start()
    return t

class FTPClientWrapper:
    def __init__(self):
        self.ftp = None
        self.lock = threading.Lock()

    def connect(self, host, port, user, passwd, timeout=10):
        with self.lock:
            if self.ftp:
                try:
                    self.ftp.quit()
                except Exception:
                    pass
                self.ftp = None
            ftp = ftplib.FTP()
            ftp.connect(host, port, timeout=timeout)
            ftp.login(user, passwd)
            ftp.set_pasv(True)
            self.ftp = ftp
            return True

    def close(self):
        with self.lock:
            if self.ftp:
                try:
                    self.ftp.quit()
                except Exception:
                    try:
                        self.ftp.close()
                    except Exception:
                        pass
            self.ftp = None

    def pwd(self):
        with self.lock:
            return self.ftp.pwd()

    def listdir(self, path):
        """Return list of (name, is_dir) for the given path."""
        with self.lock:
            ftp = self.ftp
            # attempt MLSD
            items = []
            try:
                lines = []
                ftp.retrlines(f"MLSD {path}" if path != "" else "MLSD", lines.append)
                for line in lines:
                    # format: key1=value;key2=value; ... name
                    try:
                        meta, name = line.rsplit(' ', 1)
                        attrs = {}
                        for kv in meta.split(';'):
                            if '=' in kv:
                                k,v = kv.split('=',1)
                                attrs[k.lower()] = v
                        is_dir = attrs.get('type','') == 'dir'
                        items.append((name, is_dir))
                    except Exception:
                        # fallback
                        pass
                if items:
                    return items
            except Exception:
                # MLSD not supported or failed
                pass

            # Fallback: use NLST and test cwd to detect dirs (best-effort)
            try:
                names = ftp.nlst(path) if path else ftp.nlst()
            except Exception:
                # Some servers require cwd then nlst()
                try:
                    cur = ftp.pwd()
                    ftp.cwd(path)
                    names = ftp.nlst()
                    ftp.cwd(cur)
                except Exception:
                    names = []

            # names may be full paths or base names
            cleaned = []
            for n in names:
                base = os.path.basename(n.rstrip('/'))
                if base == '':
                    continue
                # heuristic: try cwd into it
                is_dir = False
                cur = None
                try:
                    cur = ftp.pwd()
                    ftp.cwd(n)
                    is_dir = True
                    ftp.cwd(cur)
                except Exception:
                    # not a dir
                    if cur:
                        try:
                            ftp.cwd(cur)
                        except Exception:
                            pass
                cleaned.append((base, is_dir))
            return cleaned

    def download(self, remote_path, local_path, progress_cb=None):
        with self.lock:
            ftp = self.ftp
            dirname = os.path.dirname(local_path)
            if dirname and not os.path.isdir(dirname):
                os.makedirs(dirname, exist_ok=True)
            total = 0
            try:
                # try to get size
                try:
                    total = ftp.size(remote_path)
                except Exception:
                    total = None

                with open(local_path + '.part', 'wb') as f:
                    def cb(data):
                        f.write(data)
                        if progress_cb:
                            progress_cb(len(data))
                    ftp.retrbinary(f"RETR {remote_path}", cb)
                os.replace(local_path + '.part', local_path)
                return True
            except Exception as e:
                # cleanup
                try:
                    if os.path.exists(local_path + '.part'):
                        os.remove(local_path + '.part')
                except Exception:
                    pass
                raise


class FTPExplorerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('FTP Mobile Explorer')
        self.geometry('900x600')

        self.client = FTPClientWrapper()

        self._build_ui()

        # attempt auto-connect
        self.host_var.set(DEFAULT_HOST)
        self.port_var.set(str(DEFAULT_PORT))
        self.user_var.set(DEFAULT_USER)
        self.pass_var.set(DEFAULT_PASS)
        run_bg(self.auto_connect)

    def _build_ui(self):
        # top frame: connection controls
        top = ttk.Frame(self)
        top.pack(fill='x', padx=6, pady=6)

        ttk.Label(top, text='Host:').pack(side='left')
        self.host_var = tk.StringVar(); ttk.Entry(top, textvariable=self.host_var, width=15).pack(side='left', padx=4)
        ttk.Label(top, text='Port:').pack(side='left')
        self.port_var = tk.StringVar(); ttk.Entry(top, textvariable=self.port_var, width=6).pack(side='left', padx=4)
        ttk.Label(top, text='User:').pack(side='left')
        self.user_var = tk.StringVar(); ttk.Entry(top, textvariable=self.user_var, width=10).pack(side='left', padx=4)
        ttk.Label(top, text='Pass:').pack(side='left')
        self.pass_var = tk.StringVar(); ttk.Entry(top, textvariable=self.pass_var, width=10, show='*').pack(side='left', padx=4)
        self.connect_btn = ttk.Button(top, text='Connect', command=self.on_connect)
        self.connect_btn.pack(side='left', padx=6)
        ttk.Button(top, text='Disconnect', command=self.on_disconnect).pack(side='left')
        ttk.Button(top, text='Refresh', command=self.on_refresh).pack(side='left', padx=6)

        # main splitter
        main = ttk.Panedwindow(self, orient='horizontal')
        main.pack(fill='both', expand=True, padx=6, pady=6)

        # tree view
        leftframe = ttk.Frame(main)
        main.add(leftframe, weight=1)

        self.tree = ttk.Treeview(leftframe)
        ysb = ttk.Scrollbar(leftframe, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(leftframe, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.pack(fill='both', expand=True, side='left')
        ysb.pack(side='right', fill='y')
        xsb.pack(side='bottom', fill='x')

        self.tree.heading('#0', text='Remote files/folders', anchor='w')
        self.tree.bind('<<TreeviewOpen>>', self.on_node_expand)
        self.tree.bind('<Button-3>', self.on_right_click)

        # right panel: details + actions
        rightframe = ttk.Frame(main, width=260)
        main.add(rightframe, weight=0)

        ttk.Label(rightframe, text='Selected:').pack(anchor='w', padx=6, pady=(6,0))
        self.selected_var = tk.StringVar()
        ttk.Entry(rightframe, textvariable=self.selected_var, state='readonly').pack(fill='x', padx=6)

        ttk.Button(rightframe, text='Download Selected File', command=self.on_download_clicked).pack(fill='x', padx=6, pady=6)
        ttk.Button(rightframe, text='Open Selected Folder (remote)', command=self.on_open_remote_folder).pack(fill='x', padx=6)

        ttk.Separator(rightframe).pack(fill='x', pady=8, padx=6)
        ttk.Label(rightframe, text='Log:').pack(anchor='w', padx=6)
        self.log = tk.Text(rightframe, height=10, state='disabled')
        self.log.pack(fill='both', expand=True, padx=6, pady=6)

        # status bar
        self.status_var = tk.StringVar(value='Not connected')
        status = ttk.Label(self, textvariable=self.status_var, relief='sunken', anchor='w')
        status.pack(fill='x', side='bottom')

    def log_msg(self, msg):
        t = time.strftime('%H:%M:%S')
        self.log.configure(state='normal')
        self.log.insert('end', f'[{t}] {msg}\n')
        self.log.see('end')
        self.log.configure(state='disabled')

    def set_status(self, text):
        self.status_var.set(text)

    def auto_connect(self):
        self.set_status('Auto-connecting...')
        try:
            host = self.host_var.get() or DEFAULT_HOST
            port = int(self.port_var.get() or DEFAULT_PORT)
            user = self.user_var.get() or DEFAULT_USER
            passwd = self.pass_var.get() or DEFAULT_PASS
            self.client.connect(host, port, user, passwd)
            self.set_status(f'Connected to {host}:{port}')
            self.log_msg(f'Connected to {host}:{port}')
            # populate root
            self.populate_root()
        except Exception as e:
            self.set_status('Auto-connect failed')
            self.log_msg(f'Auto-connect failed: {e}')

    def on_connect(self):
        def _connect():
            try:
                host = self.host_var.get() or DEFAULT_HOST
                port = int(self.port_var.get() or DEFAULT_PORT)
                user = self.user_var.get() or DEFAULT_USER
                passwd = self.pass_var.get() or DEFAULT_PASS
                self.client.connect(host, port, user, passwd)
                self.set_status(f'Connected to {host}:{port}')
                self.log_msg(f'Connected to {host}:{port}')
                self.populate_root()
            except Exception as e:
                messagebox.showerror('Connect failed', str(e))
                self.set_status('Connect failed')
                self.log_msg(f'Connect failed: {e}')
        run_bg(_connect)

    def on_disconnect(self):
        run_bg(self.client.close)
        self.tree.delete(*self.tree.get_children())
        self.set_status('Disconnected')
        self.log_msg('Disconnected')

    def on_refresh(self):
        # refresh selected node or root
        sel = self.tree.selection()
        if sel:
            node = sel[0]
            self.refresh_node(node)
        else:
            self.populate_root()

    def populate_root(self):
        self.tree.delete(*self.tree.get_children())
        # insert root as '/' with iid '/'
        root_iid = '/'
        self.tree.insert('', 'end', iid=root_iid, text='/', values=('/',), tags=('dir',))
        # add dummy child to make it expandable
        self.tree.insert(root_iid, 'end', iid=root_iid + '__dummynode', text='loading...')

    def on_node_expand(self, event):
        node = self.tree.focus()
        run_bg(lambda: self.load_children(node))

    def load_children(self, node):
        try:
            # path stored as iid itself (we use full path concatenation)
            path = self._node_to_path(node)
            self.set_status(f'Listing {path} ...')
            self.log_msg(f'Listing {path}')
            items = self.client.listdir(path if path != '/' else '')
            # clear dummy
            children = self.tree.get_children(node)
            for c in children:
                if c.endswith('__dummynode'):
                    self.tree.delete(c)
            # insert items
            for name, is_dir in items:
                # ensure unique iid: join parent and name
                if path == '/' or path == '':
                    child_path = f"/{name}"
                else:
                    child_path = f"{path.rstrip('/')}/{name}"
                iid = child_path
                if self.tree.exists(iid):
                    continue
                tag = 'dir' if is_dir else 'file'
                self.tree.insert(node, 'end', iid=iid, text=name, tags=(tag,))
                # if dir add dummy
                if is_dir:
                    self.tree.insert(iid, 'end', iid=iid + '__dummynode', text='loading...')
            self.set_status('Listed ' + path)
        except Exception as e:
            self.log_msg(f'Error listing {node}: {e}')
            self.set_status('List error')

    def refresh_node(self, node):
        # remove its children and re-add dummy then expand
        for c in self.tree.get_children(node):
            self.tree.delete(c)
        self.tree.insert(node, 'end', iid=node + '__dummynode', text='loading...')
        run_bg(lambda: self.load_children(node))

    def _node_to_path(self, node):
        # our iids are full paths like '/dir/sub'
        if node == '/':
            return '/'
        return node

    def on_right_click(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        self.tree.selection_set(iid)
        self.selected_var.set(self._node_to_path(iid))
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label='Download', command=self.on_download_clicked)
        menu.add_command(label='Refresh', command=lambda: self.refresh_node(iid))
        menu.post(event.x_root, event.y_root)

    def on_download_clicked(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo('No selection', 'Select a file to download')
            return
        iid = sel[0]
        # check if directory
        if 'dir' in self.tree.item(iid, 'tags'):
            messagebox.showinfo('Not a file', 'Selected item is a directory. Use "Open Selected Folder (remote)" then select files.')
            return
        remote_path = self._node_to_path(iid)
        # ask for local destination folder
        dest_dir = filedialog.askdirectory(title='Select destination folder')
        if not dest_dir:
            return
        local_name = os.path.basename(remote_path)
        local_path = os.path.join(dest_dir, local_name)

        def _download():
            bytes_done = 0
            def progress_cb(n):
                nonlocal bytes_done
                bytes_done += n
                self.set_status(f'Downloading {local_name} — {bytes_done} bytes...')
            try:
                self.log_msg(f'Starting download: {remote_path} -> {local_path}')
                self.client.download(remote_path.lstrip('/'), local_path, progress_cb=progress_cb)
                self.log_msg('Download complete: ' + local_path)
                self.set_status('Download complete')
                messagebox.showinfo('Downloaded', f'Downloaded to:\n{local_path}')
            except Exception as e:
                self.log_msg('Download failed: ' + str(e))
                self.set_status('Download failed')
                messagebox.showerror('Error', str(e))

        run_bg(_download)

    def on_open_remote_folder(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo('No selection', 'Select a folder to open')
            return
        iid = sel[0]
        if 'file' in self.tree.item(iid, 'tags'):
            iid = os.path.dirname(self._node_to_path(iid)) or '/'
        # expand node
        self.tree.see(iid)
        self.tree.selection_set(iid)
        self.refresh_node(iid)

if __name__ == '__main__':
    app = FTPExplorerGUI()
    app.mainloop()
