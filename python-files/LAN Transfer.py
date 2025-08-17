#!/usr/bin/env python3
"""
LAN Drop: simple LAN file sender/receiver with GUI and resume.

- Run this on ALL computers you want to transfer between.
- Each instance advertises itself via UDP broadcast and listens for broadcasts.
- Pick a discovered peer in the GUI, add files/folders, and click Send.

Security note: This is unencrypted, unauthenticated LAN transfer intended for trusted home/office networks.
"""

import os
import sys
import json
import time
import uuid
import queue
import math
import socket
import struct
import threading
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

# ---------- Config ----------
APP_MAGIC = "LANXFER1"
DISCOVERY_PORT = 48234
DISCOVERY_INTERVAL = 2.0
TCP_LISTEN_PORT = 0          # 0 = choose a free port automatically
CHUNK_SIZE = 256 * 1024      # 256 KB per chunk (tune if you like)
CONNECT_TIMEOUT = 8
IO_TIMEOUT = 20
RECONNECT_ATTEMPTS = 5
RECONNECT_BACKOFF_BASE = 2.0 # seconds
PEER_EXPIRY = 6.0            # seconds since last beacon to consider stale

def _app_dir() -> Path:
    """Return the folder of the script, or the EXE folder when frozen (PyInstaller)."""
    if getattr(sys, "frozen", False) and hasattr(sys, "executable"):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent

RECEIVE_DIR = _app_dir() / "Received"  # <— PyInstaller-friendly

# ---------- Small helpers ----------
def human_size(n: int) -> str:
    if n is None:
        return "—"
    units = ["B","KB","MB","GB","TB"]
    i = 0
    f = float(n)
    while f >= 1024 and i < len(units)-1:
        f /= 1024.0
        i += 1
    if i == 0:
        return f"{int(f)} {units[i]}"
    return f"{f:.1f} {units[i]}"

def local_ip_guess() -> str:
    # Best-effort way to get a LAN IP without external calls
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def now_ms() -> int:
    return int(time.time() * 1000)

# ---------- Simple framed JSON protocol for commands ----------
def send_json(sock: socket.socket, obj: dict):
    data = json.dumps(obj, separators=(",", ":")).encode("utf-8")
    hdr = struct.pack("!I", len(data))
    sock.sendall(hdr + data)

def recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Socket closed")
        buf += chunk
    return buf

def recv_json(sock: socket.socket) -> dict:
    hdr = recv_exact(sock, 4)
    (length,) = struct.unpack("!I", hdr)
    data = recv_exact(sock, length)
    return json.loads(data.decode("utf-8"))

# ---------- Discovery ----------
@dataclass
class Peer:
    uuid: str
    name: str
    ip: str
    port: int
    last_seen: float

class DiscoveryService:
    def __init__(self, my_uuid: str, my_name: str, tcp_port: int, on_update):
        self.my_uuid = my_uuid
        self.my_name = my_name
        self.tcp_port = tcp_port
        self.on_update = on_update  # callback to refresh UI
        self.ip = local_ip_guess()
        self.peers: Dict[str, Peer] = {}
        self._stop = threading.Event()

    def start(self):
        threading.Thread(target=self._beacon_sender, daemon=True).start()
        threading.Thread(target=self._beacon_listener, daemon=True).start()
        threading.Thread(target=self._reaper, daemon=True).start()

    def stop(self):
        self._stop.set()

    def _beacon_sender(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        payload = {
            "app": APP_MAGIC,
            "uuid": self.my_uuid,
            "name": self.my_name,
            "ip": self.ip,
            "port": self.tcp_port,
        }
        while not self._stop.is_set():
            try:
                payload["port"] = self.tcp_port  # in case it changed
                data = json.dumps(payload).encode("utf-8")
                s.sendto(data, ("255.255.255.255", DISCOVERY_PORT))
            except Exception:
                pass
            self._stop.wait(DISCOVERY_INTERVAL)
        s.close()

    def _beacon_listener(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("", DISCOVERY_PORT))
        except Exception:
            # Fallback if already bound; keep going to avoid crashing
            pass
        s.settimeout(1.0)
        while not self._stop.is_set():
            try:
                data, addr = s.recvfrom(4096)
                obj = json.loads(data.decode("utf-8"))
                if obj.get("app") != APP_MAGIC:
                    continue
                if obj.get("uuid") == self.my_uuid:
                    continue
                ip = obj.get("ip") or addr[0]
                peer = Peer(
                    uuid=obj["uuid"],
                    name=obj.get("name") or obj["uuid"][:8],
                    ip=ip,
                    port=int(obj["port"]),
                    last_seen=time.time(),
                )
                self.peers[peer.uuid] = peer
                self.on_update()
            except socket.timeout:
                pass
            except Exception:
                # Ignore malformed beacons
                pass
        s.close()

    def _reaper(self):
        while not self._stop.is_set():
            changed = False
            now = time.time()
            for k in list(self.peers.keys()):
                if now - self.peers[k].last_seen > PEER_EXPIRY:
                    del self.peers[k]
                    changed = True
            if changed:
                self.on_update()
            self._stop.wait(1.0)

# ---------- Receiver (server) ----------
class ReceiverServer:
    def __init__(self, dest_root: Path, on_event):
        self.dest_root = Path(dest_root)
        self.on_event = on_event
        self._stop = threading.Event()
        self.tcp_port = None
        self._srv_sock = None

    def start(self):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("", TCP_LISTEN_PORT))
        srv.listen(8)
        self._srv_sock = srv
        self.tcp_port = srv.getsockname()[1]
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def stop(self):
        self._stop.set()
        try:
            if self._srv_sock:
                self._srv_sock.close()
        except Exception:
            pass

    def _accept_loop(self):
        while not self._stop.is_set():
            try:
                conn, addr = self._srv_sock.accept()
                conn.settimeout(IO_TIMEOUT)
                threading.Thread(target=self._handle_client, args=(conn, addr), daemon=True).start()
            except OSError:
                break
            except Exception:
                pass

    def _handle_client(self, conn: socket.socket, addr):
        try:
            hello = recv_json(conn)
            if hello.get("cmd") != "HELLO" or hello.get("app") != APP_MAGIC:
                conn.close()
                return
            send_json(conn, {"cmd": "HELLO_ACK", "ok": True})

            session = recv_json(conn)
            if session.get("cmd") != "SESSION":
                conn.close()
                return
            sender_name = session.get("name", "peer")
            session_id = session.get("id", "session")
            root = self.dest_root / f"{sender_name}_{session_id}"
            root.mkdir(parents=True, exist_ok=True)

            while True:
                msg = recv_json(conn)
                if msg.get("cmd") == "FILE":
                    rel = msg["relpath"]
                    total = int(msg["size"])
                    mtime = float(msg.get("mtime", time.time()))
                    safe_rel = Path(rel).as_posix()
                    # Ensure parent dirs
                    dest_final = (root / safe_rel).resolve()
                    # Prevent path traversal
                    if root not in dest_final.parents and dest_final != root:
                        send_json(conn, {"cmd": "ERROR", "reason": "bad path"})
                        return
                    dest_final.parent.mkdir(parents=True, exist_ok=True)
                    dest_part = dest_final.with_suffix(dest_final.suffix + ".part")

                    existing = 0
                    if dest_part.exists():
                        existing = dest_part.stat().st_size
                    elif dest_final.exists():
                        # if already complete file exists with same or smaller size, set existing accordingly
                        ex = dest_final.stat().st_size
                        if ex < total:
                            # We'll resume into .part (rename existing to .part to append)
                            dest_final.replace(dest_part)
                            existing = ex
                        else:
                            existing = total

                    send_json(conn, {"cmd": "READY", "offset": int(existing)})

                    remaining = total - existing
                    if remaining <= 0:
                        # done already
                        self.on_event(("recv_done", {"path": str(dest_final), "size": total}))
                        continue

                    with open(dest_part, "ab", buffering=0) as f:
                        to_read = remaining
                        while to_read > 0:
                            chunk = conn.recv(min(CHUNK_SIZE, to_read))
                            if not chunk:
                                raise ConnectionError("Sender disconnected")
                            f.write(chunk)
                            to_read -= len(chunk)
                    # finalize
                    os.utime(dest_part, (mtime, mtime))
                    dest_part.replace(dest_final)
                    self.on_event(("recv_done", {"path": str(dest_final), "size": total}))

                elif msg.get("cmd") == "BYE":
                    send_json(conn, {"cmd": "BYE_ACK"})
                    break
                else:
                    send_json(conn, {"cmd": "ERROR", "reason": "unknown cmd"})
                    break

        except Exception:
            # Connection ended or error; receiver just drops back to accept loop
            try:
                conn.close()
            except Exception:
                pass

# ---------- Sender ----------
@dataclass
class SendItem:
    abs_path: Path
    relpath: str
    size: int
    mtime: float
    sent: int = 0
    status: str = "queued"  # queued/sending/done/error
    speed_bps: float = 0.0
    last_tick_bytes: int = 0
    last_tick_time: float = field(default_factory=time.time)

class SenderThread(threading.Thread):
    def __init__(self, items: List[SendItem], peer_ip: str, peer_port: int, session_name: str, on_progress):
        super().__init__(daemon=True)
        self.items = items
        self.peer_ip = peer_ip
        self.peer_port = peer_port
        self.session_name = session_name
        self.on_progress = on_progress
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def _connect(self) -> socket.socket:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(CONNECT_TIMEOUT)
        s.connect((self.peer_ip, self.peer_port))
        s.settimeout(IO_TIMEOUT)
        return s

    def _handshake(self, s: socket.socket):
        send_json(s, {"cmd": "HELLO", "app": APP_MAGIC})
        _ = recv_json(s)  # HELLO_ACK
        send_json(s, {"cmd": "SESSION", "name": socket.gethostname(), "id": self.session_name})

    def run(self):
        current_idx = 0
        attempt = 0
        s: Optional[socket.socket] = None

        while current_idx < len(self.items) and not self._stop.is_set():
            try:
                if s is None:
                    s = self._connect()
                    self._handshake(s)

                item = self.items[current_idx]
                if item.status in ("done", "error"):
                    current_idx += 1
                    continue

                item.status = "sending"
                self.on_progress(("update", item))

                # Announce file and get offset
                send_json(s, {"cmd": "FILE", "relpath": item.relpath, "size": item.size, "mtime": item.mtime})
                resp = recv_json(s)
                if resp.get("cmd") != "READY":
                    raise ConnectionError("Receiver not ready")
                offset = int(resp.get("offset", 0))
                item.sent = offset
                self.on_progress(("update", item))

                # Stream the rest
                remaining = item.size - offset
                if remaining > 0:
                    with open(item.abs_path, "rb") as f:
                        if offset:
                            f.seek(offset)
                        item.last_tick_bytes = item.sent
                        item.last_tick_time = time.time()
                        while remaining > 0 and not self._stop.is_set():
                            chunk = f.read(min(CHUNK_SIZE, remaining))
                            if not chunk:
                                break
                            s.sendall(chunk)
                            item.sent += len(chunk)
                            remaining -= len(chunk)
                            # speed calc
                            now = time.time()
                            dt = now - item.last_tick_time
                            if dt >= 0.5:
                                db = item.sent - item.last_tick_bytes
                                item.speed_bps = db / dt if dt > 0 else 0.0
                                item.last_tick_time = now
                                item.last_tick_bytes = item.sent
                                self.on_progress(("update", item))

                # Mark done (receiver finalizes on its side)
                item.speed_bps = 0.0
                item.status = "done"
                self.on_progress(("update", item))
                current_idx += 1
                attempt = 0  # reset after successful file

            except Exception:
                # Connection issue; try to reconnect and resume current file
                if s:
                    try:
                        s.close()
                    except Exception:
                        pass
                    s = None
                attempt += 1
                if attempt > RECONNECT_ATTEMPTS:
                    # Give up on this file, mark error, move on
                    it = self.items[current_idx]
                    it.status = f"error"
                    self.on_progress(("update", it))
                    current_idx += 1
                    attempt = 0
                else:
                    # exponential-ish backoff
                    backoff = RECONNECT_BACKOFF_BASE * min(5, attempt)
                    self.on_progress(("log", f"Connection lost. Retrying in {backoff:.1f}s (attempt {attempt}/{RECONNECT_ATTEMPTS})..."))
                    time.sleep(backoff)

        # try to close gracefully
        try:
            if s:
                send_json(s, {"cmd": "BYE"})
                _ = recv_json(s)
                s.close()
        except Exception:
            pass

# ---------- GUI ----------
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class ScrollableFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.frame = ttk.Frame(canvas)
        self.frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        self._win = canvas.create_window((0, 0), window=self.frame, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(self._win, width=e.width))
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.canvas = canvas

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LAN Drop")
        self.geometry("1000x700")
        try:
            self.iconbitmap(default="")  # optional placeholder
        except Exception:
            pass

        # State
        self.my_uuid = str(uuid.uuid4())
        self.sender_thread: Optional[SenderThread] = None

        # Receiver
        self.event_queue = queue.Queue()
        self.receiver = ReceiverServer(RECEIVE_DIR, on_event=lambda ev: self.event_queue.put(ev))
        self.receiver.start()

        # Discovery
        self.discovery = DiscoveryService(self.my_uuid, socket.gethostname(), tcp_port=self.receiver.tcp_port, on_update=self.refresh_peers)
        self.discovery.start()

        # UI Layout
        self._build_ui()

        # timers
        self.after(300, self._poll_events)
        self.after(1000, self._refresh_peer_table_timer)

        # graceful close
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # --- UI construction ---
    def _build_ui(self):
        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        top = ttk.Frame(root)
        top.pack(fill="x")

        # Left: file selection
        files_frame = ttk.LabelFrame(top, text="Files & Folders to Send", padding=10)
        files_frame.pack(side="left", fill="both", expand=True, padx=(0,10))

        btns = ttk.Frame(files_frame)
        btns.pack(fill="x")
        ttk.Button(btns, text="Add Files", command=self.add_files).pack(side="left")
        ttk.Button(btns, text="Add Folder", command=self.add_folder).pack(side="left", padx=6)
        ttk.Button(btns, text="Remove Selected", command=self.remove_selected).pack(side="left")
        ttk.Button(btns, text="Clear", command=self.clear_list).pack(side="left", padx=6)

        self.file_list = tk.Listbox(files_frame, selectmode=tk.EXTENDED)
        self.file_list.pack(fill="both", expand=True, pady=(8,0))

        # Right: peers
        peers_frame = ttk.LabelFrame(top, text="Discovered Peers (run on the other PC too)", padding=10)
        peers_frame.pack(side="left", fill="both", expand=True)

        cols = ("name","ip","port","seen")
        self.peers_table = ttk.Treeview(peers_frame, columns=cols, show="headings", selectmode="browse", height=10)
        for c,w in zip(cols, (180, 150, 80, 120)):
            self.peers_table.heading(c, text=c.capitalize())
            self.peers_table.column(c, width=w, anchor="center")
        self.peers_table.pack(fill="both", expand=True)
        self.peers_table.bind("<Double-1>", lambda e: self._send_clicked())

        # Middle: send bar
        actions = ttk.Frame(root)
        actions.pack(fill="x", pady=(10,6))
        ttk.Label(actions, text="Session name:").pack(side="left")
        self.session_name_var = tk.StringVar(value=time.strftime("%Y%m%d_%H%M%S"))
        ttk.Entry(actions, textvariable=self.session_name_var, width=20).pack(side="left", padx=6)
        self.send_btn = ttk.Button(actions, text="Send ▶", command=self._send_clicked)
        self.send_btn.pack(side="left", padx=10)
        self.stop_btn = ttk.Button(actions, text="Stop", command=self._stop_clicked, state="disabled")
        self.stop_btn.pack(side="left")

        # Bottom: progress area
        progress_frame = ttk.LabelFrame(root, text="Transfer Progress", padding=10)
        progress_frame.pack(fill="both", expand=True)

        self.progress_area = ScrollableFrame(progress_frame)
        self.progress_area.pack(fill="both", expand=True)

        self.items_widgets: Dict[str, dict] = {}  # key: unique item id -> widgets

        # Log
        self.log_box = tk.Text(root, height=6)
        self.log_box.pack(fill="both", expand=False, pady=(8,0))
        self._log(f"Receiver listening on TCP port {self.receiver.tcp_port} (IP {local_ip_guess()})")
        self._log("Tip: both PCs must run this app to appear in the peers list.")

    # --- File list management ---
    def add_files(self):
        paths = filedialog.askopenfilenames(title="Select files to send")
        for p in paths:
            self._add_path(Path(p))
        self._dedupe_file_list()

    def add_folder(self):
        p = filedialog.askdirectory(title="Select folder to send")
        if p:
            self._add_path(Path(p))
            self._dedupe_file_list()

    def _add_path(self, path: Path):
        self.file_list.insert(tk.END, str(path))

    def remove_selected(self):
        sel = list(self.file_list.curselection())
        sel.reverse()
        for idx in sel:
            self.file_list.delete(idx)

    def clear_list(self):
        self.file_list.delete(0, tk.END)

    def _dedupe_file_list(self):
        items = [self.file_list.get(i) for i in range(self.file_list.size())]
        seen = set()
        self.file_list.delete(0, tk.END)
        for it in items:
            if it not in seen:
                self.file_list.insert(tk.END, it)
                seen.add(it)

    # --- Peers ---
    def refresh_peers(self):
        # Called from discovery threads; schedule on UI thread
        self.after(0, self._refresh_peer_table)

    def _refresh_peer_table(self):
        self.peers_table.delete(*self.peers_table.get_children())
        now = time.time()
        for peer in sorted(self.discovery.peers.values(), key=lambda p: (p.name, p.ip)):
            seen = f"{max(0, now - peer.last_seen):.1f}s ago"
            self.peers_table.insert("", tk.END, iid=peer.uuid, values=(peer.name, peer.ip, peer.port, seen))

    def _refresh_peer_table_timer(self):
        self._refresh_peer_table()
        self.after(1000, self._refresh_peer_table_timer)

    # --- Sending ---
    def _collect_send_items(self) -> List[SendItem]:
        roots = [Path(self.file_list.get(i)) for i in range(self.file_list.size())]
        items: List[SendItem] = []
        for root in roots:
            if root.is_dir():
                base = root.parent
                for dirpath, _, filenames in os.walk(root):
                    for fn in filenames:
                        ap = Path(dirpath) / fn
                        rel = os.path.relpath(ap, base)
                        st = ap.stat()
                        items.append(SendItem(abs_path=ap, relpath=Path(rel).as_posix(), size=st.st_size, mtime=st.st_mtime))
            elif root.is_file():
                ap = root
                rel = root.name  # top-level
                st = ap.stat()
                items.append(SendItem(abs_path=ap, relpath=rel, size=st.st_size, mtime=st.st_mtime))
        # stable order, largest first tends to show speed quickly; but alphabetical is friendlier
        items.sort(key=lambda x: x.relpath.lower())
        return items

    def _selected_peer(self) -> Optional[Peer]:
        sel = self.peers_table.selection()
        if not sel:
            return None
        return self.discovery.peers.get(sel[0])

    def _send_clicked(self):
        if self.sender_thread and self.sender_thread.is_alive():
            messagebox.showinfo("Busy", "A transfer is already in progress.")
            return
        peer = self._selected_peer()
        if not peer:
            messagebox.showwarning("No peer", "Select a peer to send to.")
            return
        if self.file_list.size() == 0:
            messagebox.showwarning("No files", "Add at least one file or folder.")
            return

        items = self._collect_send_items()
        if not items:
            messagebox.showwarning("Nothing to send", "No files found in selection.")
            return

        # Build progress widgets
        for w in self.items_widgets.values():
            w["frame"].destroy()
        self.items_widgets.clear()
        for it in items:
            self._add_progress_row(it)

        self.sender_thread = SenderThread(
            items=items,
            peer_ip=peer.ip,
            peer_port=peer.port,
            session_name=self.session_name_var.get().strip() or time.strftime("%Y%m%d_%H%M%S"),
            on_progress=lambda ev: self.event_queue.put(("send_progress", ev)),
        )
        self.sender_thread.start()
        self.send_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        total_sz = sum(it.size for it in items)
        self._log(f"Sending {len(items)} files ({human_size(total_sz)}) to {peer.name} @ {peer.ip}:{peer.port}")

    def _stop_clicked(self):
        if self.sender_thread:
            self.sender_thread.stop()
        self.send_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self._log("Stopped by user.")

    # --- Progress UI per file ---
    def _add_progress_row(self, item: SendItem):
        frame = ttk.Frame(self.progress_area.frame, padding=(2,4))
        frame.pack(fill="x", expand=True)

        path_lbl = ttk.Label(frame, text=item.relpath, anchor="w")
        path_lbl.pack(fill="x")

        row = ttk.Frame(frame)
        row.pack(fill="x", pady=(2,0))

        size_lbl = ttk.Label(row, width=12, text=human_size(item.size), anchor="w")
        size_lbl.pack(side="left")

        pb = ttk.Progressbar(row, maximum=max(1, item.size), length=500)
        pb.pack(side="left", fill="x", expand=True, padx=8)

        stats_lbl = ttk.Label(row, width=28, anchor="e", text="0% • 0.0 MB/s")
        stats_lbl.pack(side="left")

        status_lbl = ttk.Label(frame, text="queued", foreground="#555")
        status_lbl.pack(anchor="w")

        self.items_widgets[item.relpath] = {
            "frame": frame,
            "pb": pb,
            "stats": stats_lbl,
            "status": status_lbl,
            "size_lbl": size_lbl,
        }

    def _update_progress_row(self, item: SendItem):
        w = self.items_widgets.get(item.relpath)
        if not w:
            return
        w["pb"]["maximum"] = max(1, item.size)
        w["pb"]["value"] = item.sent
        pct = (item.sent / item.size * 100.0) if item.size else 100.0
        mbps = (item.speed_bps / (1024*1024)) if item.speed_bps else 0.0
        w["stats"].configure(text=f"{pct:5.1f}% • {mbps:.1f} MB/s")
        w["status"].configure(text=item.status)

    # --- Event loop from threads ---
    def _poll_events(self):
        try:
            while True:
                ev = self.event_queue.get_nowait()
                self._handle_event(ev)
        except queue.Empty:
            pass
        self.after(150, self._poll_events)

    def _handle_event(self, ev):
        etype, data = ev
        if etype == "recv_done":
            self._log(f"Received: {data['path']} ({human_size(data['size'])})")
        elif etype == "send_progress":
            kind, payload = data
            if kind == "log":
                self._log(payload)
            elif kind == "update":
                self._update_progress_row(payload)
                # when everything done, enable buttons
                if all(w["status"].cget("text") in ("done","error") for w in self.items_widgets.values()):
                    self.send_btn.configure(state="normal")
                    self.stop_btn.configure(state="disabled")
        else:
            # Unknown
            pass

    def _log(self, msg: str):
        ts = time.strftime("%H:%M:%S")
        self.log_box.insert(tk.END, f"[{ts}] {msg}\n")
        self.log_box.see(tk.END)

    def on_close(self):
        try:
            self.discovery.stop()
            self.receiver.stop()
            if self.sender_thread:
                self.sender_thread.stop()
        except Exception:
            pass
        self.destroy()

if __name__ == "__main__":
    try:
        RECEIVE_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    app = App()
    app.mainloop()
