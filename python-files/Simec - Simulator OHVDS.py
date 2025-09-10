import tkinter as tk
from tkinter import messagebox
import socket
import threading
import queue
import random
import time
from datetime import datetime


class ThreadSafeLogger:
    def __init__(self, text_widget: tk.Text, poll_interval_ms: int = 100):
        self._queue = queue.Queue()
        self._text_widget = text_widget
        self._poll_interval_ms = poll_interval_ms

    def log(self, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._queue.put(f"[{timestamp}] {message}\n")

    def poll(self):
        try:
            while True:
                msg = self._queue.get_nowait()
                self._text_widget.insert(tk.END, msg)
                self._text_widget.see(tk.END)
        except queue.Empty:
            pass


class ClientHandler(threading.Thread):
    def __init__(self, conn: socket.socket, addr, server: "RobustTcpServer"):
        super().__init__(daemon=True)
        self.conn = conn
        self.addr = addr
        self.server = server
        self._send_lock = threading.Lock()
        self._running = threading.Event()
        self._running.set()

    def run(self):
        try:
            while self._running.is_set():
                try:
                    data = self.conn.recv(4096)
                except socket.timeout:
                    continue
                except OSError:
                    break
                if not data:
                    break
                try:
                    text = data.decode("utf-8", errors="replace")
                except Exception:
                    text = str(data)
                self.server.logger.log(f"Received: {text}")
        except Exception as e:
            self.server.logger.log(f"Client {self.addr} error: {e}")
        finally:
            self.close()

    def send(self, data: str) -> bool:
        try:
            with self._send_lock:
                self.conn.sendall(data.encode("utf-8"))
            return True
        except Exception as e:
            self.server.logger.log(f"Send failed to {self.addr}: {e}")
            self.close()
            return False

    def close(self):
        if self._running.is_set():
            self._running.clear()
            try:
                self.conn.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                self.conn.close()
            except Exception:
                pass
            with self.server.client_lock:
                if self.addr in self.server.client:
                    self.server.client.pop(self.addr, None)
            self.server.logger.log(f"{self.addr} disconnected")


class RobustTcpServer:
    def __init__(self, logger: ThreadSafeLogger, host: str = "0.0.0.0"):
        self.logger = logger
        self.host = host

        self._server_socket = None
        self._server_thread = None
        self._stop_event = threading.Event()

        self.client = {}
        self.client_lock = threading.Lock()

        self._transit_lock = threading.Lock()
        self._transit_id = 0

        self._heartbeat_thread = None
        self._heartbeat_stop = threading.Event()

    def start(self, port: int):
        if self._server_thread and self._server_thread.is_alive():
            self.logger.log("Server already running.")
            return False

        try:
            port = int(port)
            if port < 1 or port > 65535:
                raise ValueError("Port out of range")
        except Exception as e:
            self.logger.log(f"Invalid port: {e}")
            return False

        try:
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind((self.host, port))
            self._server_socket.listen()
            self._server_socket.settimeout(1.0)
        except Exception as e:
            self.logger.log(f"Failed to bind/listen: {e}")
            if self._server_socket:
                try:
                    self._server_socket.close()
                except Exception:
                    pass
                self._server_socket = None
            return False

        self._stop_event.clear()
        self._heartbeat_stop.clear()
        self._server_thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._server_thread.start()

        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()

        self.logger.log(f"Server started on {self.host}:{port}")
        return True

    def _accept_loop(self):
        while not self._stop_event.is_set():
            try:
                conn, addr = self._server_socket.accept()
            except socket.timeout:
                continue
            except OSError:
                break

            with self.client_lock:
                if self.client:
                    try:
                        conn.sendall(b"BUSY\n")
                    except Exception:
                        pass
                    try:
                        conn.close()
                    except Exception:
                        pass
                    self.logger.log(f"{addr} attempted to connect but server busy.")
                else:
                    try:
                        conn.settimeout(1.0)
                    except Exception:
                        pass
                    handler = ClientHandler(conn, addr, self)
                    self.client[addr] = handler
                    handler.start()
                    self.logger.log(f"{addr} connected")

        self.logger.log("Server accept loop ended")
        self._cleanup_clients()
        try:
            if self._server_socket:
                self._server_socket.close()
        except Exception:
            pass
        self._server_socket = None

    def _cleanup_clients(self):
        with self.client_lock:
            clients = list(self.client.values())
        for c in clients:
            try:
                c.close()
            except Exception:
                pass

    def stop(self):
        if not (self._server_thread and self._server_thread.is_alive()):
            self.logger.log("Server not running.")
        self.logger.log("Stopping server...")
        self._stop_event.set()
        self._heartbeat_stop.set()

        try:
            if self._server_socket:
                self._server_socket.close()
        except Exception as e:
            self.logger.log(f"Error closing server socket: {e}")

        self._cleanup_clients()

        if self._server_thread:
            self._server_thread.join(timeout=1.0)
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=1.0)

        self.logger.log("Server stopped.")

    def _heartbeat_loop(self):
        while not self._heartbeat_stop.is_set():
            now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            msg = f"<HBT|1|{now}>"
            self.send_to_first(msg)
            time.sleep(30.0)

    def send_to_first(self, data: str) -> bool:
        with self.client_lock:
            if not self.client:
                return False
            handler = next(iter(self.client.values()))
        return handler.send(data)

    def broadcast(self, data: str) -> bool:
        sent_any = False
        with self.client_lock:
            handlers = list(self.client.values())
        for h in handlers:
            ok = h.send(data)
            sent_any = sent_any or ok
        return sent_any

    def increment_transit(self) -> int:
        with self._transit_lock:
            self._transit_id += 1
            return self._transit_id


class Simulation(threading.Thread):
    def __init__(self, server: RobustTcpServer, logger: ThreadSafeLogger, min_interval: float = 5.0, max_interval: float = 40.0):
        super().__init__(daemon=True)
        self.server = server
        self.logger = logger
        self._stop_event = threading.Event()
        self.min_interval = float(min_interval)
        self.max_interval = float(max_interval)

    def run(self):
        self.logger.log("Simulation started")
        try:
            while not self._stop_event.is_set():
                now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                altitude = random.choice([1000, 1500, 1700, 1900, 2100, 2500])
                alarm = random.choice([0, 1])
                transit_id = self.server.increment_transit()
                message = f"<V_E|1|{transit_id}|1|20|{now}|10|{altitude}|2000|4500|0|0|0|0|0|0|0|0|0|0|0|0|{alarm}>"
                if self.server.broadcast(message):
                    self.logger.log(f"Simulation sent: {message}")
                else:
                    self.logger.log("Simulation: no client connected")
                interval = random.uniform(self.min_interval, self.max_interval)
                if self._stop_event.wait(interval):
                    break
        finally:
            self.logger.log("Simulation stopped")

    def stop(self):
        self._stop_event.set()


def create_app():
    root = tk.Tk()
    root.title("Simulator OHVDS - SIMEC")
    root.geometry("625x425")
    root.resizable(False, False)

    bg_color = "#f0f8ff"
    font = ("Helvetica", 12)

    root.configure(bg=bg_color)

    left_frame = tk.Frame(root, bg=bg_color, width=400, height=400, relief="solid", bd=1, highlightbackground="black")
    left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nswe")

    tk.Label(left_frame, text="Laser", font=("Helvetica", 16, "bold"), bg=bg_color).grid(row=0, column=0, columnspan=3, pady=10, sticky="nswe")

    tk.Label(left_frame, text="Port:", font=font, bg=bg_color).grid(row=1, column=0, padx=10, pady=5, sticky="e")
    port_entry = tk.Entry(left_frame, relief="flat", highlightthickness=1, highlightbackground="#cccccc", highlightcolor="#0078d7", font=font, width=20)
    port_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    tk.Label(left_frame, text="Message:", font=font, bg=bg_color).grid(row=2, column=0, padx=10, pady=5, sticky="ne")
    message_text = tk.Text(left_frame, relief="flat", highlightthickness=1, highlightbackground="#cccccc", highlightcolor="#0078d7", font=font, width=35, height=5)
    message_text.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    tk.Label(left_frame, text="Console:", font=font, bg=bg_color).grid(row=3, column=0, padx=10, pady=5, sticky="ne")
    console_text = tk.Text(left_frame, relief="flat", highlightthickness=1, highlightbackground="#cccccc", highlightcolor="#0078d7", font=font, width=35, height=7)
    console_text.grid(row=3, column=1, padx=10, pady=5, sticky="w")

    logger = ThreadSafeLogger(console_text)
    server = RobustTcpServer(logger)

    def poll_logger():
        logger.poll()
        root.after(100, poll_logger)

    root.after(100, poll_logger)

    sim_holder = {"sim": None}

    def start_server_command():
        port = port_entry.get().strip()
        if not port:
            messagebox.showwarning("Warning", "Port field must be filled.")
            return
        try:
            port_val = int(port)
            if not (1 <= port_val <= 65535):
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Warning", "Port must be a number between 1 and 65535.")
            return

        started = server.start(port_val)
        if started:
            port_entry.configure(state="disabled")
            start_button.configure(state="disabled")
        else:
            messagebox.showerror("Error", "Could not start server. Check logs in Console.")

    start_button = tk.Button(left_frame, text="Start Server", font=font, command=start_server_command, bg="white", fg="black", relief="solid", bd=1, highlightbackground="black", highlightthickness=2)
    start_button.grid(row=5, column=0, padx=10, pady=10, sticky="w")

    def send_command():
        user_msg = message_text.get("1.0", tk.END).strip()
        if not user_msg:
            messagebox.showwarning("Warning", "Message field must be filled.")
            return
        if len(user_msg) > 4000:
            messagebox.showwarning("Warning", "Message too long (max 4000 chars).")
            return

        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        altitude = random.choice([1000, 1500, 1700, 1900, 2100, 2500])
        transit_id = server.increment_transit()
        clase = random.choice([100, 200, 401, 501])

        formatted = ("<V_E|1|" + str(transit_id) + "|1|20|" + now + "|10|" + str(altitude) + "|2000|4500|0|0|" + str(clase)
                     + "|0|0|0|0|0|0|0|0|0|" + user_msg + ">")

        ok = server.send_to_first(formatted)
        if ok:
            logger.log(f"Sent: {formatted}")
        else:
            logger.log("No client connected. Message not sent.")

    send_button = tk.Button(left_frame, text="Send", font=font, command=send_command, bg="white", fg="black", relief="solid", bd=1, highlightbackground="black", highlightthickness=2)
    send_button.grid(row=5, column=1, padx=10, pady=10, sticky="")

    def stop_server_command():
        server.stop()
        port_entry.configure(state="normal")
        start_button.configure(state="normal")
        logger.log("Server stopped by user.")

    stop_button = tk.Button(left_frame, text="Stop Server", font=font, command=stop_server_command, bg="white", fg="black", relief="solid", bd=1, highlightbackground="black", highlightthickness=2)
    stop_button.grid(row=5, column=2, padx=10, pady=10, sticky="e")

    def start_simulation_command():
        sim = sim_holder.get("sim")
        if sim and sim.is_alive():
            logger.log("Simulation already running.")
            return
        sim = Simulation(server, logger)
        sim_holder["sim"] = sim
        sim.start()
        logger.log("Simulation thread started.")

    start_sim_button = tk.Button(left_frame, text="Start Simulation", font=font, command=start_simulation_command, bg="white", fg="black", relief="solid", bd=1, highlightbackground="black", highlightthickness=2)
    start_sim_button.grid(row=1, column=2, padx=10, pady=10, sticky="e")

    def stop_simulation_command():
        sim = sim_holder.get("sim")
        if sim and sim.is_alive():
            sim.stop()
            logger.log("Requested simulation stop (will stop shortly).")
        else:
            logger.log("Simulation is not running.")

    stop_sim_button = tk.Button(left_frame, text="Stop Simulation", font=font, command=stop_simulation_command, bg="white", fg="black", relief="solid", bd=1, highlightbackground="black", highlightthickness=2)
    stop_sim_button.grid(row=2, column=2, padx=10, pady=10, sticky="e")

    def on_exit():
        if messagebox.askokcancel("Quit", "Do you really want to quit?"):
            sim = sim_holder.get("sim")
            if sim and sim.is_alive():
                sim.stop()
            server.stop()
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_exit)

    root.mainloop()


def caducidad():
    fecha_limite = datetime(2026, 1, 1)
    fecha_actual = datetime.now()
    return fecha_actual < fecha_limite


if __name__ == "__main__":
    if caducidad():
        create_app()
