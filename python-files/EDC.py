import os, threading, tkinter as tk, tempfile, requests, hashlib, base64
from tkinter import filedialog, messagebox, scrolledtext, simpledialog, ttk
from datetime import datetime, timezone
from PIL import Image, ImageTk
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

AES_KEY = b'e3f6a1c28b7e4d9c6f0b2a85d3e19472'

def encrypt_bytes(data: bytes) -> bytes:
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    pad_len = 16 - (len(data) % 16)
    padding = bytes([pad_len] * pad_len)
    padded_data = data + padding
    encrypted = encryptor.update(padded_data) + encryptor.finalize()
    return iv + encrypted

def decrypt_bytes(data: bytes) -> bytes:
    iv = data[:16]
    encrypted = data[16:]
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded = decryptor.update(encrypted) + decryptor.finalize()
    pad_len = padded[-1]
    return padded[:-pad_len]

def encrypt_filename(filename: str) -> str:
    """Encrypts a filename and base64-encodes it for URL/filesystem safety."""
    encrypted_bytes = encrypt_bytes(filename.encode('utf-8'))
    return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')

def decrypt_filename(encrypted_filename: str) -> str:
    """Decypts a base64-encoded, encrypted filename."""
    decoded_bytes = base64.urlsafe_b64decode(encrypted_filename.encode('utf-8'))
    return decrypt_bytes(decoded_bytes).decode('utf-8')

def get_credentials(): return (os.getenv('B2_KEY_ID', '005c3b7673aaf490000000008'), os.getenv('B2_APPLICATION_KEY', 'K005egd8ioCvrXw+/Elo9FsaTLGlmaM'), os.getenv('B2_BUCKET_ID', 'dcd38b47967753da9a8f0419'))

class B2Client:
    def __init__(self, kid, ak, bid):
        self.key_id = kid
        self.app_key = ak
        self.bucket_id = bid
        self.api_url = None
        self.download_url = None
        self.auth_token = None
        self.account_id = None

    def authorize_account(self):
        r = requests.get("https://api.backblazeb2.com/b2api/v2/b2_authorize_account", auth=(self.key_id, self.app_key))
        r.raise_for_status()
        d = r.json()
        self.api_url = d['apiUrl']
        self.download_url = d['downloadUrl']
        self.auth_token = d['authorizationToken']
        self.account_id = d['accountId']

    def get_upload_url(self):
        r = requests.post(f"{self.api_url}/b2api/v2/b2_get_upload_url", headers={'Authorization': self.auth_token}, json={'bucketId': self.bucket_id})
        r.raise_for_status()
        return r.json()

    def sha1_of_bytes(self, data: bytes) -> str:
        sha1 = hashlib.sha1()
        sha1.update(data)
        return sha1.hexdigest()

    def upload_file(self, fpath):
        with open(fpath, 'rb') as f: raw_data = f.read()
        encrypted_data = encrypt_bytes(raw_data)
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(encrypted_data)
            temp_path = tf.name
        try:
            ud = self.get_upload_url()
            original_filename = os.path.basename(fpath)
            encrypted_filename = encrypt_filename(original_filename)
            headers = {'Authorization': ud['authorizationToken'],
                       'X-Bz-File-Name': encrypted_filename,
                       'Content-Type': 'b2/x-auto',
                       'X-Bz-Content-Sha1': self.sha1_of_bytes(encrypted_data)}
            with open(temp_path, 'rb') as f_enc: r = requests.post(ud['uploadUrl'], headers=headers, data=f_enc)
            r.raise_for_status()
            
            response_data = r.json()
            response_data['originalFileName'] = original_filename
            return response_data
        finally: os.unlink(temp_path)

    def list_files(self, max_count=100):
        r = requests.post(f"{self.api_url}/b2api/v2/b2_list_file_versions", headers={'Authorization': self.auth_token}, json={'bucketId': self.bucket_id, 'maxFileCount': max_count})
        r.raise_for_status()
        files = r.json().get('files', [])
        
        for f in files:
            try:
                f['originalFileName'] = decrypt_filename(f['fileName'])
            except Exception as e:
                
                f['originalFileName'] = f['fileName'] + " (error)"
        return files

    def download_file(self, original_fname, dest):
        files = self.list_files(max_count=1000)
        encrypted_fname_to_download = None
        for f in files:
            if f.get('originalFileName') == original_fname:
                encrypted_fname_to_download = f['fileName']
                break

        if not encrypted_fname_to_download:
            raise FileNotFoundError(f"File '{original_fname}' not found on Entropy.")


        if os.path.isdir(dest): dest = os.path.join(dest, original_fname)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        bucket_name = "ntropy"


        url = f"{self.download_url}/file/{bucket_name}/{encrypted_fname_to_download}"
        r = requests.get(url, headers={'Authorization': self.auth_token}, stream=True)
        r.raise_for_status()
        encrypted_data = r.content
        decrypted_data = decrypt_bytes(encrypted_data)
        with open(dest, 'wb') as f: f.write(decrypted_data)
        return dest

    def delete_version(self, original_fname, fid):

        files = self.list_files(max_count=1000)
        encrypted_fname_to_delete = None
        for f in files:
            if f.get('originalFileName') == original_fname and f['fileId'] == fid:
                encrypted_fname_to_delete = f['fileName']
                break

        if not encrypted_fname_to_delete:
            raise FileNotFoundError(f"File '{original_fname}' with ID '{fid}' not found for deletion.")

        r = requests.post(f"{self.api_url}/b2api/v2/b2_delete_file_version", headers={'Authorization': self.auth_token}, json={'fileName': encrypted_fname_to_delete, 'fileId': fid})
        r.raise_for_status()
        return r.json()

def fmt_ts(ms): return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

class NoInternetConnectionError(Exception): pass

class B2GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ENTROPY DATABASE CLIENT")
        self.geometry("1000x700")
        self.configure(bg='#1a1a1a')
        self.current_files = []
        self.last_known_files = []
        self.is_showing_file_list = False
        self.last_refresh_time = None
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._configure_styles()
        self.is_connected_to_internet = True
        self.internet_check_url = "http://www.google.com" # Use a reliable public URL for internet check

        if not self._initial_internet_check(): messagebox.showerror("Bruh", "You cannot use this while offline.")

        kid, ak, bid = get_credentials()
        self.client = B2Client(kid, ak, bid)
        self._build_ui()

        try:
            self.client.authorize_account()
            self.is_connected_to_internet = True
            self._update_status("Connected", '#00ff88')
            self._set_button_state(tk.NORMAL)
            self.list_files(force_refresh=True)
        except requests.exceptions.ConnectionError:
            self.is_connected_to_internet = False
            self._update_status("Disconnected", '#f85149')
            self._set_button_state(tk.DISABLED)
            self._log("Error: No internet connection. Could not connect to Entropy database.", 'error')
            self._log("Entropy is empty, could not retrieve file list.", 'info')
        except Exception as e:
            self.is_connected_to_internet = False
            self._update_status("Disconnected (Error)", '#f85149')
            self._set_button_state(tk.DISABLED)
            self._log(f"Error authorizing account: {e}. Could not connect to Entropy database.", 'error')
            self._log("Entropy is empty, could not retrieve file list.", 'info')

        self._schedule_auto_refresh()

    def _initial_internet_check(self):
        try:
            requests.get(self.internet_check_url, timeout=5)
            return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout): return False
        except Exception as e:
            print(f"Unexpected error during initial internet check: {e}")
            return False

    def _configure_styles(self):
        self.style.configure('Title.TLabel',background='#1a1a1a',foreground='#00ff88',font=('Segoe UI', 24, 'bold'))
        self.style.configure('Subtitle.TLabel',background='#1a1a1a',foreground='#888888',font=('Segoe UI', 10))
        self.style.configure('Modern.TButton',background='#00ff88',foreground='#000000',font=('Segoe UI', 10, 'bold'),borderwidth=0,focuscolor='none',padding=(20, 10))
        self.style.map('Modern.TButton',background=[('active', '#00cc6a'),('pressed', '#009955')])
        self.style.configure('Danger.TButton',background='#ff4444',foreground='white',font=('Segoe UI', 10, 'bold'),borderwidth=0,focuscolor='none',padding=(20, 10))
        self.style.map('Danger.TButton',background=[('active', '#dd3333'),('pressed', '#bb2222')])
        self.style.configure('Secondary.TButton',background='#333333',foreground='white',font=('Segoe UI', 10, 'bold'),borderwidth=0,focuscolor='none',padding=(20, 10))
        self.style.map('Secondary.TButton',background=[('active', '#444444'),('pressed', '#222222')])

    def _build_ui(self):
        main_container = tk.Frame(self, bg='#1a1a1a')
        main_container.pack(fill='both', expand=True, padx=30, pady=30)

        header_frame = tk.Frame(main_container, bg='#1a1a1a')
        header_frame.pack(fill='x', pady=(0, 30))

        title_label = ttk.Label(header_frame, text="ENTROPY DATABASE", style='Title.TLabel')
        title_label.pack(anchor='w')

        self.status_frame = tk.Frame(header_frame, bg='#1a1a1a')
        self.status_frame.pack(anchor='w', pady=(10, 0))
        self.status_indicator = tk.Canvas(self.status_frame, width=12, height=12, bg='#1a1a1a', highlightthickness=0)
        self.status_indicator.pack(side='left')
        self.status_indicator.create_oval(2, 2, 10, 10, fill='#00ff88', outline='')
        self.status_text = ttk.Label(self.status_frame, text="Connecting...", style='Subtitle.TLabel')
        self.status_text.pack(side='left', padx=(8, 0))

        action_frame = tk.Frame(main_container, bg='#1a1a1a')
        action_frame.pack(fill='x', pady=(0, 20))

        button_grid = tk.Frame(action_frame, bg='#1a1a1a')
        button_grid.pack(anchor='center')

        self.upload_btn = ttk.Button(button_grid, text="UPLOAD FILES",command=self.upload_file, style='Modern.TButton')
        self.upload_btn.grid(row=0, column=0, padx=10, pady=5)
        self.download_btn = ttk.Button(button_grid, text="DOWNLOAD",command=self.download_file, style='Secondary.TButton')
        self.download_btn.grid(row=0, column=1, padx=10, pady=5)
        self.view_btn = ttk.Button(button_grid, text="VIEW FILE",command=self.view_file, style='Secondary.TButton')
        self.view_btn.grid(row=1, column=0, padx=10, pady=5)
        self.delete_btn = ttk.Button(button_grid, text="DELETE",command=self.delete_file, style='Danger.TButton')
        self.delete_btn.grid(row=1, column=1, padx=10, pady=5)

        files_frame = tk.Frame(main_container, bg='#1a1a1a')
        files_frame.pack(fill='both', expand=True)

        files_header = tk.Frame(files_frame, bg='#1a1a1a')
        files_header.pack(fill='x', pady=(0, 10))
        files_label = ttk.Label(files_header, text="FILE REPOSITORY",foreground='#00ff88', background='#1a1a1a',font=('Segoe UI', 14, 'bold'))
        files_label.pack(side='left')
        self.last_updated_label = ttk.Label(files_header, text="",foreground='#6e7681', background='#1a1a1a',font=('Segoe UI', 9))
        self.last_updated_label.pack(side='right')

        log_container = tk.Frame(files_frame, bg='#0d1117', relief='flat', bd=1)
        log_container.pack(fill='both', expand=True)

        self.log = scrolledtext.ScrolledText(log_container,
                                             state='disabled',
                                             font=('Consolas', 11),
                                             bg='#0d1117',
                                             fg='#c9d1d9',
                                             insertbackground='#00ff88',
                                             selectbackground='#264f78',
                                             selectforeground='#ffffff',
                                             wrap='none',
                                             padx=15,
                                             pady=15,
                                             relief='flat',
                                             bd=0)
        self.log.pack(fill='both', expand=True)


        scrollbar = self.log.vbar
        scrollbar.configure(bg='#0d1117',troughcolor='#0d1117',activebackground='#484f58',highlightthickness=0,bd=0)

    def _log(self, msg, tag=None):
        self.log.config(state='normal')
        timestamp = datetime.now().strftime('%H:%M:%S')


        if not hasattr(self, '_tags_configured'):
            self.log.tag_config('timestamp', foreground='#6e7681')
            self.log.tag_config('success', foreground='#3fb950')
            self.log.tag_config('error', foreground='#f85149')
            self.log.tag_config('warning', foreground='#d29922')
            self.log.tag_config('info', foreground='#58a6ff')
            self.log.tag_config('header', foreground='#00ff88', font=('Consolas', 11, 'bold'))
            self.log.tag_config('refresh', foreground='#6e7681', font=('Consolas', 10, 'italic'))
            self._tags_configured = True

        if tag is None:
            if msg.startswith('Uploaded:') or msg.startswith('Downloaded to:'): tag = 'success'
            elif msg.startswith('Error:') or msg.startswith('Failed:'): tag = 'error'
            elif msg.startswith('Deleted:'): tag = 'warning'
            elif '═' in msg or msg.startswith('FILENAME'): tag = 'header'
            elif msg.startswith('Updated file list') or msg.startswith('Refreshing'): tag = 'refresh'
            else: tag = 'info'

        self.log.insert('end', f'[{timestamp}] ', 'timestamp')
        self.log.insert('end', msg + '\n', tag)
        self.log.config(state='disabled')
        self.log.see('end')

    def _update_status(self, status, color='#00ff88'):
        self.status_indicator.delete("all")
        self.status_indicator.create_oval(2, 2, 10, 10, fill=color, outline='')
        self.status_text.configure(text=status)

    def _set_button_state(self, state):
        for btn in [self.upload_btn, self.download_btn, self.view_btn, self.delete_btn]: btn.config(state=state)

    def _check_internet_connection(self):
        try:
            requests.get(self.internet_check_url, timeout=5)
            if not self.is_connected_to_internet:
                self.is_connected_to_internet = True
                self._update_status("Connected", '#00ff88')
                self._set_button_state(tk.NORMAL)
                self._log("Connection re-established.", 'info')
                self.list_files(force_refresh=True)
            return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            if self.is_connected_to_internet:
                self.is_connected_to_internet = False
                self._update_status("Disconnected", '#f85149')
                self._set_button_state(tk.DISABLED)
                self._show_file_list_seamlessly([], force_clear=True)
            return False
        except Exception as e:
            if self.is_connected_to_internet:
                self.is_connected_to_internet = False
                self._update_status("Disconnected (Error)", '#f85149')
                self._set_button_state(tk.DISABLED)
                self._show_file_list_seamlessly([], force_clear=True)
            return False

    def _run_threaded(self, fn, *args):
        def wrapped_fn():
            if not self.is_connected_to_internet:
                self.after(0, lambda: self._log("Operation aborted: No internet connection.", 'error'))
                return
            fn(*args)
        threading.Thread(target=wrapped_fn, daemon=True).start()

    def _schedule_auto_refresh(self):
        self._check_internet_connection()
        if self.is_connected_to_internet:
            self.list_files(silent=True, auto_refresh=True)
        self.after(2000, self._schedule_auto_refresh)

    def _files_changed(self, new_files):
        current_set = {(f.get('originalFileName'), f['uploadTimestamp']) for f in self.last_known_files}
        new_set = {(f.get('originalFileName'), f['uploadTimestamp']) for f in new_files}
        return current_set != new_set

    def _show_file_list_seamlessly(self, files, force_clear=False):
        scroll_pos = self.log.vbar.get()[0] if hasattr(self.log, 'vbar') else 0

        if force_clear or not self.is_showing_file_list:
            self.log.config(state='normal')
            self.log.delete('1.0', 'end')
            self.log.config(state='disabled')
        elif self.is_showing_file_list:
            self.log.config(state='normal')
            content = self.log.get('1.0', 'end')
            lines = content.split('\n')
            header_line = -1
            for i, line in enumerate(lines):
                if '═' in line and 'FILENAME' not in line:
                    header_line = i
                    break
            if header_line > 0:
                preserved_content = '\n'.join(lines[:header_line])
                self.log.delete('1.0', 'end')
                self.log.insert('1.0', preserved_content)
                if preserved_content.strip():
                    self.log.insert('end', '\n')
            else:
                self.log.delete('1.0', 'end')
            self.log.config(state='disabled')


        if not files:
            
            if (force_clear or not self.current_files) or (self.is_showing_file_list and not files):
                 if self.is_connected_to_internet:
                     self._log("Entropy is empty, no files found.", 'info')
            self.is_showing_file_list = False
            return


        self.log.config(state='normal')
        self.log.delete('1.0', 'end')
        self.log.config(state='disabled')


        header = "═" * 90
        self._log(header, 'header')
        self._log(f"{'FILENAME':<45}{'SIZE':>12}{'UPLOADED':>25}", 'header')
        self._log(header, 'header')

        for f in files:
            size_mb = f['contentLength'] / (1024 * 1024)
            if size_mb >= 1:
                size_str = f"{size_mb:.1f} MB"
            else:
                size_str = f"{f['contentLength'] / 1024:.1f} KB"

            filename = f.get('originalFileName', f['fileName'])
            display_filename = filename[:43] + '..' if len(filename) > 45 else filename
            self._log(f"{display_filename:<45}{size_str:>12}{fmt_ts(f['uploadTimestamp']):>25}")
        self._log("═" * 90, 'header')
        self._log(f"Total files: {len(files)}", 'info')
        self.is_showing_file_list = True


        if scroll_pos < 0.9:
            self.after(50, lambda: self.log.yview_moveto(scroll_pos))

    def list_files(self, silent=False, auto_refresh=False, force_refresh=False):
        def task():
            if not self.is_connected_to_internet: return
            try:
                files = self.client.list_files()
                files_changed = self._files_changed(files)
                if files_changed or force_refresh:
                    if not silent: self.after(0, lambda: self._update_status("Syncing...", '#d29922'))
                    self.last_known_files = files
                    self.current_files = files
                    self.after(0, lambda: self._show_file_list_seamlessly(files, force_clear=True))
                    self.last_refresh_time = datetime.now()
                    timestamp_str = self.last_refresh_time.strftime('Updated: %H:%M:%S')
                    self.after(0, lambda: self.last_updated_label.configure(text=timestamp_str))
                elif not silent:
                    pass

                if self.is_connected_to_internet:
                    self.after(0, lambda: self._update_status("Connected", '#00ff88'))

            except requests.exceptions.ConnectionError:
                self.is_connected_to_internet = False
                self.after(0, lambda: self._update_status("Disconnected", '#f85149'))
                self.after(0, lambda: self._set_button_state(tk.DISABLED))
                if not silent: self._log("Error: No internet connection. Please check your network.", 'error')
                self.after(0, lambda: self._log("Entropy is empty, could not retrieve file list.", 'info'))
                self.after(0, lambda: self._show_file_list_seamlessly([], force_clear=True))
            except Exception as e:
                self.is_connected_to_internet = False
                self.after(0, lambda: self._update_status("Disconnected (Error)", '#f85149'))
                self.after(0, lambda: self._set_button_state(tk.DISABLED))
                if not silent: self._log(f"Error refreshing file list: {e}", 'error')
                self.after(0, lambda: self._log("Entropy is empty, could not retrieve file list.", 'info'))
                self.after(0, lambda: self._show_file_list_seamlessly([], force_clear=True))

        self._run_threaded(task)

    def upload_file(self):
        if not self.is_connected_to_internet:
            messagebox.showwarning("Disconnected", "Cannot upload files: No internet connection.")
            return
        paths = filedialog.askopenfilenames(title="Select files to upload")
        if not paths: return
        def task():
            self._log(f"Starting upload of {len(paths)} file(s)...", 'info')
            successful = 0
            failed = 0
            for path in paths:
                try:
                    filename = os.path.basename(path)
                    self._log(f"Uploading {filename}...", 'info')
                    r = self.client.upload_file(path)
                    self._log(f"Uploaded: {r['originalFileName']}", 'success')
                    successful += 1
                except requests.exceptions.ConnectionError:
                    self._log(f"Failed: {os.path.basename(path)} - No internet connection.", 'error')
                    failed += 1
                    self.is_connected_to_internet = False
                    self.after(0, lambda: self._update_status("Disconnected", '#f85149'))
                    self.after(0, lambda: self._set_button_state(tk.DISABLED))
                    break
                except Exception as e:
                    self._log(f"Failed: {os.path.basename(path)} - {e}", 'error')
                    failed += 1
            self._log(f"Upload complete: {successful} successful, {failed} failed", 'info')
            if self.is_connected_to_internet:
                self.list_files(force_refresh=True)

        self._run_threaded(task)

    def download_file(self):
        if not self.is_connected_to_internet:
            messagebox.showwarning("Disconnected", "Cannot download files: No internet connection.")
            return
        fname = simpledialog.askstring("Download File", "Enter filename to download:")
        if not fname: return

        dest_dir = filedialog.askdirectory(title="Select destination folder")
        if not dest_dir: return
        def task():
            try:
                self._log(f"Downloading {fname}...", 'info')
                path = self.client.download_file(fname, dest_dir)
                self._log(f"Downloaded to: {path}", 'success')
            except FileNotFoundError:
                self._log(f"Error: File '{fname}' not found.", 'error')
            except requests.exceptions.ConnectionError:
                self._log(f"Error downloading {fname}: No internet connection.", 'error')
                self.is_connected_to_internet = False
                self.after(0, lambda: self._update_status("Disconnected", '#f85149'))
                self.after(0, lambda: self._set_button_state(tk.DISABLED))
            except Exception as e:
                self._log(f"Error downloading {fname}: {e}", 'error')
        self._run_threaded(task)

    def delete_file(self):
        if not self.is_connected_to_internet:
            messagebox.showwarning("Disconnected", "Cannot delete file: No internet connection.")
            return
        fname = simpledialog.askstring("Delete File", "Enter filename to delete:")
        if not fname: return

        def task():
            try:
                files = [f for f in self.client.list_files(max_count=1000) if f.get('originalFileName') == fname]
                if not files:
                    self._log(f"File not found: {fname}", 'error')
                    return
                fid = files[0]['fileId']
                self._log(f"Deleting {fname}...", 'warning')
                self.client.delete_version(fname, fid)
                self._log(f"Deleted: {fname}", 'warning')
                self.list_files(force_refresh=True)
            except requests.exceptions.ConnectionError:
                self._log(f"Error deleting {fname}: No internet connection.", 'error')
                self.is_connected_to_internet = False
                self.after(0, lambda: self._update_status("Disconnected", '#f85149'))
                self.after(0, lambda: self._set_button_state(tk.DISABLED))
            except Exception as e:
                self._log(f"Error deleting {fname}: {e}", 'error')
        self._run_threaded(task)

    def view_file(self):
        if not self.is_connected_to_internet:
            messagebox.showwarning("Disconnected", "No internet connection.")
            return
        fname = simpledialog.askstring("View File", "Enter filename to view (.txt or image):")
        if not fname: return

        text_ext = ['.txt', '.log', '.md', '.py', '.js', '.html', '.css', '.json', '.xml']
        image_ext = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
        ext = os.path.splitext(fname)[1].lower()

        if ext not in text_ext + image_ext:
            messagebox.showwarning("Unsupported File",
                                   f"Can only view text files ({', '.join(text_ext)}) or images ({', '.join(image_ext)}).")
            return

        def task():
            try:
                self._log(f"Loading {fname} for preview...", 'info')
                with tempfile.TemporaryDirectory() as tmpdir:
                    path = self.client.download_file(fname, tmpdir)
                    if ext in text_ext:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        self.after(0, lambda: self._show_text_window(fname, content))
                    else:
                        img = Image.open(path)
                        self.after(0, lambda: self._show_image_window(fname, img))
                    self._log(f"Opened {fname} in viewer", 'success')
            except FileNotFoundError:
                self._log(f"Error: File '{fname}' not found.", 'error')
            except requests.exceptions.ConnectionError:
                self._log(f"Error viewing {fname}: No internet connection.", 'error')
                self.is_connected_to_internet = False
                self.after(0, lambda: self._update_status("Disconnected", '#f85149'))
                self.after(0, lambda: self._set_button_state(tk.DISABLED))
            except Exception as e:
                self._log(f"Error viewing {fname}: {e}", 'error')
        self._run_threaded(task)

    def _show_text_window(self, title, content):
        win = tk.Toplevel(self)
        win.title(f"{title}")
        win.geometry("800x600")
        win.configure(bg='#1a1a1a')

        header = tk.Frame(win, bg='#1a1a1a')
        header.pack(fill='x', padx=20, pady=(20, 10))
        title_label = tk.Label(header, text=title, bg='#1a1a1a', fg='#00ff88',font=('Segoe UI', 16, 'bold'))
        title_label.pack(anchor='w')

        text_frame = tk.Frame(win, bg='#0d1117', relief='flat', bd=1)
        text_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        text = scrolledtext.ScrolledText(text_frame,
                                         font=('Consolas', 11),
                                         bg='#0d1117',
                                         fg='#c9d1d9',
                                         insertbackground='#00ff88',
                                         selectbackground='#264f78',
                                         selectforeground='#ffffff',
                                         padx=15,
                                         pady=15,
                                         relief='flat',
                                         bd=0)
        text.pack(fill='both', expand=True)
        text.insert('1.0', content)
        text.config(state='disabled')

    def _show_image_window(self, title, pil_image):
        win = tk.Toplevel(self)
        win.title(f"{title}")
        win.configure(bg='#1a1a1a')

        max_width, max_height = 900, 700
        w, h = pil_image.size

        
        scale = min(max_width / w, max_height / h, 1)
        if scale < 1:
            pil_image = pil_image.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

        header = tk.Frame(win, bg='#1a1a1a')
        header.pack(fill='x', padx=20, pady=20)
        title_label = tk.Label(header, text=title, bg='#1a1a1a', fg='#00ff88',font=('Segoe UI', 16, 'bold'))
        title_label.pack(anchor='w')
        info_label = tk.Label(header, text=f"Original Dimensions: {w}×{h} pixels",
                              bg='#1a1a1a', fg='#888888', font=('Segoe UI', 10))
        info_label.pack(anchor='w')

        img_frame = tk.Frame(win, bg='#0d1117', relief='flat', bd=1)
        img_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        img_tk = ImageTk.PhotoImage(pil_image)
        label = tk.Label(img_frame, image=img_tk, bg='#0d1117')
        label.image = img_tk
        label.pack(expand=True)

       
        win.geometry(f"{pil_image.width + 40}x{pil_image.height + 120}")


if __name__ == '__main__':
    try:
        app = B2GUI()
        app.mainloop()
    except NoInternetConnectionError:
        pass
    except Exception as e:
        messagebox.showerror("Application Error", f"An unexpected error occurred: {e}")