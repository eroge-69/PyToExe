#!/usr/bin/env python3
"""
Local 100-connections tester:
- ایجاد 100 کانکشن از پورت مبدأ متفاوت (محدوده قابل تنظیم) به DEST_HOST:DEST_PORT
- ارسال پیام KEEPALIVE در سطح اپلیکیشن هر KEEP_INTERVAL ثانیه
- کانکشن‌ها تا Ctrl-C باز می‌مانند

اجرا:
    python3 local_conn_tester.py

تذکر: برای اتصال به پورت‌های <1024 ممکن است نیاز به دسترسی root باشد.
"""
import socket
import threading
import time
import signal
import sys
import os

# === تنظیمات قابل تغییر ===
DEST_HOST = "127.0.0.1"
DEST_PORT = 30             # در صورت نیاز به پورت غیرپایین‌تر، مقدار را تغییر بده (مثلاً 3030)
NUM_CONNECTIONS = 100
SOURCE_IP = "127.0.0.1"
SOURCE_PORT_START = 40000  # از این شماره پورت مبدأ شروع می‌کنیم و برای هر کانکشن +1 می‌شه
KEEP_INTERVAL = 30         # ثانیه بین ارسال‌های keepalive در سطح اپلیکیشن
CONNECT_TIMEOUT = 5        # ثانیه برای timeout اتصال
# ===========================

stop_event = threading.Event()
sockets = []     # لیست سوکت‌های باز (برای بستن مرتب در هنگام خروج)
lock = threading.Lock()

def make_bound_socket(src_ip, start_port, dest_host, dest_port, connect_timeout):
    """
    تلاش می‌کند سوکت بسازد، به یک پورت مبدأ آزاد bind کند (از start_port به بعد)
    و به مقصد متصل شود. در صورت موفقیت سوکت را برمی‌گرداند، در غیر اینصورت None.
    """
    p = start_port
    max_port = 65535
    while p <= max_port and not stop_event.is_set():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(connect_timeout)
            # تلاش برای bind به پورت مبدأ مشخص
            s.bind((src_ip, p))
            # فعال کردن TCP keepalive در سطح سوکت (سیستم‌عامل پارامترهای زیر را کنترل می‌کند)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            s.connect((dest_host, dest_port))
            # وصل شد؛ برگشت سوکت و شماره پورت مبدأ
            return s, p
        except Exception as e:
            # اگر bind یا connect موفق نبود، سعی می‌کنیم با پورت بعدی ادامه دهیم
            try:
                s.close()
            except:
                pass
            p += 1
            continue
    return None, None

def conn_worker(idx, src_ip, src_port_candidate, dest_host, dest_port, keep_interval):
    s = None
    used_src_port = None
    try:
        s, used_src_port = make_bound_socket(src_ip, src_port_candidate, dest_host, dest_port, CONNECT_TIMEOUT)
        if not s:
            print(f"[{idx}] failed to create/bind/connect (no ports available from {src_port_candidate} onward)")
            return
        with lock:
            sockets.append(s)
        print(f"[{idx}] connected: {src_ip}:{used_src_port} -> {dest_host}:{dest_port} (fd={s.fileno()})")
        s.settimeout(2.0)
        # حلقه ارسال KEEPALIVE در سطح اپلیکیشن
        while not stop_event.is_set():
            try:
                msg = f"KEEPALIVE from client #{idx}\n".encode()
                s.sendall(msg)
            except (BrokenPipeError, ConnectionResetError):
                print(f"[{idx}] connection closed by peer.")
                break
            except socket.timeout:
                # ادامه می‌دیم (گاهی read/send timeout رخ می‌ده)
                pass
            except Exception as e:
                print(f"[{idx}] socket error: {e}")
                break
            # صبر تا دور بعدی
            stop_event.wait(keep_interval)
    finally:
        try:
            if s:
                try:
                    s.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                s.close()
        except:
            pass
        with lock:
            if s in sockets:
                sockets.remove(s)
        print(f"[{idx}] exiting (src_port={used_src_port})")

def signal_handler(sig, frame):
    print("\n[MAIN] stop requested, shutting down...")
    stop_event.set()

def main():
    # هشدار در مورد پورت‌های کوچک
    if DEST_PORT < 1024 and os.geteuid() != 0:
        print(f"[WARNING] DEST_PORT={DEST_PORT} < 1024 may require root privileges. Run as root or choose a higher port.")
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    threads = []
    for i in range(NUM_CONNECTIONS):
        # هر worker با یک حدس از پورت مبدأ شروع می‌کند ــ این باعث می‌شود پورت‌های مبدأ متفاوت انتخاب شوند
        candidate_start = SOURCE_PORT_START + i
        t = threading.Thread(
            target=conn_worker,
            args=(i+1, SOURCE_IP, candidate_start, DEST_HOST, DEST_PORT, KEEP_INTERVAL),
            daemon=True
        )
        t.start()
        threads.append(t)
        time.sleep(0.01)  # کمی فاصله بین ایجاد کانکشن‌ها تا spike لحظه‌ای کمتر شود

    print(f"[MAIN] started {len(threads)} threads, attempting {NUM_CONNECTIONS} connections to {DEST_HOST}:{DEST_PORT}")
    print("[MAIN] press Ctrl-C to stop and close sockets")

    try:
        while not stop_event.is_set():
            time.sleep(1)
    finally:
        print("[MAIN] closing sockets...")
        with lock:
            for s in list(sockets):
                try:
                    s.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                try:
                    s.close()
                except:
                    pass
            sockets.clear()
        print("[MAIN] waiting threads to exit...")
        for t in threads:
            t.join(timeout=1.0)
        print("[MAIN] done. Exiting.")

if __name__ == "__main__":
    main()
