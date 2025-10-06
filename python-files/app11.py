import time
import threading
# Multi-cam
import os, json, csv, time, datetime, threading, logging
import cv2
import gradio as gr
from PIL import Image, ImageDraw
from ultralytics import YOLO
import torch

from pathlib import Path  # thêm

ALARM_AUDIO_PATH = Path(r"assets/beep.wav").resolve()

def _play_alarm_static():
    # phát file cố định
    return str(ALARM_AUDIO_PATH) if ALARM_AUDIO_PATH.exists() else gr.updat
def _audio_clear():
    # reset Audio để browser coi là nguồn mới ở lần kế tiếp
    return gr.update(value=None)

def _play_if_cap(info_text):
    # phát khi HUD/info có dấu hiệu crossing/capture/alarm
    s = (info_text or "").lower()
    if ALARM_AUDIO_PATH.exists() and any(k in s for k in ["cap:", "alarm", "siren"]):
        return str(ALARM_AUDIO_PATH)
    return gr.update()


import unicodedata, re
try:
    cv2.setNumThreads(1)
    os.environ.setdefault("OMP_NUM_THREADS", "1")
except Exception:
    pass

# ========= UI/LOG MESSAGES (i18n mini) =========
LANG = "vi"   

_MSGS = {
    "vi": {
        # chung
        "missing_rtsp":      "Cam {cam}: thiếu RTSP.",
        "no_line":           "ERROR: Chưa có line/poly cho cam {cam}.",
        "draw_first":        "Cam {cam}: chưa có line/poly. Hãy vẽ và 'Finish Poly' trước.",
        "starting":          "Cam {cam}: đang khởi động…",
        "run_ok":            "Đã bắt đầu chạy Cam {cam}",
        "load_ok":           "Đã nạp ảnh đầu tiên cho Cam {cam}",
        "reset_ok":          "Đã xoá line/poly cho Cam {cam}",
        # alarm/sms
        "siren_dispatched":  "Đã kích còi+đèn {ms}ms (Cam {cam})",
        "siren_disabled":    "SIREN: đã tắt hoặc thiếu cổng Arduino",
        "alarm_arduino_ok":  "ALARM qua Arduino: OK",
        "alarm_arduino_err": "ALARM qua Arduino: lỗi: {err}",
        "sms_pc_sent":       "SMS A7680C: đã gửi tới {n} số",
        "sms_disabled":      "SMS: tắt hoặc chưa có người nhận",
        "test_sms_done":     "Đã gửi SMS test qua Arduino: OK {ok}/{total} (Cam {cam}). {resp}",
        "no_arduino":        "Chưa bật Arduino hoặc thiếu cổng Arduino (Cam {cam}).",
        "no_recipients":     "Chưa chọn người nhận (Cam {cam}).",
        # errors
        "load_err_open":     "Error: Không mở được nguồn video.",
        "load_err_timeout":  "Error: Quá thời gian chờ frame đầu.",
        "model_err":         "Lỗi nạp model: {err}",
        "tracker_err":       "Lỗi khởi động tracker: {err}",
    },
    "en": {
        "missing_rtsp":      "Cam {cam}: RTSP missing.",
        "no_line":           "ERROR: No line/poly for cam {cam}.",
        "draw_first":        "Cam {cam}: no line/poly. Draw and 'Finish Poly' first.",
        "starting":          "Cam {cam}: starting…",
        "run_ok":            "Cam {cam} started",
        "load_ok":           "Loaded first frame for Cam {cam}",
        "reset_ok":          "Cleared line/poly for Cam {cam}",
        "siren_dispatched":  "Siren+LED dispatched {ms}ms (Cam {cam})",
        "siren_disabled":    "SIREN: disabled or missing Arduino port",
        "alarm_arduino_ok":  "ALARM via Arduino: OK",
        "alarm_arduino_err": "ALARM via Arduino: error: {err}",
        "sms_pc_sent":       "SMS A7680C: sent to {n} recipients",
        "sms_disabled":      "SMS: disabled or no recipients",
        "test_sms_done":     "Test SMS via Arduino: OK {ok}/{total} (Cam {cam}). {resp}",
        "no_arduino":        "Arduino disabled or missing port (Cam {cam}).",
        "no_recipients":     "No recipients selected (Cam {cam}).",
        "load_err_open":     "Error: Could not open source.",
        "load_err_timeout":  "Error: Timeout waiting for first frame.",
        "model_err":         "Error loading model: {err}",
        "tracker_err":       "Error starting tracker: {err}",
    }
}

def T(key: str, **kw) -> str:
    table = _MSGS.get(LANG, _MSGS["vi"])
    tmpl = table.get(key, key)
    try:
        return tmpl.format(**kw)
    except Exception:
        return tmpl


def ascii_safe(text: str) -> str:
    """Loại dấu/Unicode để gửi qua Arduino (GSM 7-bit)."""
    if not isinstance(text, str):
        text = str(text or "")
    # chuẩn hóa & loại tổ hợp dấu
    t = unicodedata.normalize("NFKD", text)
    t = "".join(c for c in t if not unicodedata.combining(c))
    # thay ký tự “lạ” bằng khoảng trắng/nhẹ nhàng
    t = re.sub(r"[^\x20-\x7E]", " ", t)  # giữ ascii in-printable
    return t.strip()


# ---- Arduino serial singletons ----
_ARD_SER = {}   # { "COM6": serial_instance }
_ARD_LOCK = {}  # { "COM6": threading.Lock() }

def _get_lock(port):
    p = str(port)
    if p not in _ARD_LOCK:
        _ARD_LOCK[p] = threading.Lock()
    return _ARD_LOCK[p]

def arduino_write_line(port, baud, line, read_timeout=0.0):
    """Mở (nếu cần) và giữ cổng COM, tắt DTR/RTS tránh reset, ghi 1 dòng, tùy chọn đọc nhanh."""
    import serial
    p = str(port); b = int(baud)
    lk = _get_lock(p)
    with lk:
        ser = _ARD_SER.get(p)
        try:
            # mở 1 lần rồi dùng lại
            if ser is None or not getattr(ser, "is_open", False) or getattr(ser, "baudrate", None) != b:
                if ser is not None:
                    try: ser.close()
                    except Exception: pass
                ser = serial.Serial(p, b, timeout=1, write_timeout=1, rtscts=False, dsrdtr=False)
                try:
                    ser.dtr = False; ser.rts = False  # tránh reset Nano
                except Exception:
                    pass
                try:
                    ser.reset_input_buffer(); ser.reset_output_buffer()
                except Exception:
                    pass
                _ARD_SER[p] = ser
            # ghi 1 dòng
            payload = (line.rstrip("\r\n") + "\n").encode("utf-8", errors="ignore")
            ser.write(payload); ser.flush()
            if read_timeout and read_timeout > 0:
                end_t = time.time() + read_timeout
                buf = b""
                while time.time() < end_t:
                    ch = ser.read(ser.in_waiting or 1)
                    if ch: buf += ch
                    else: time.sleep(0.02)
                return True, buf.decode(errors="ignore")
            return True, "OK"
        except Exception as e:
            try:
                if ser is not None: ser.close()
            except Exception:
                pass
            _ARD_SER.pop(p, None)
            return False, f"Serial error: {e}"


def dispatch_alarm_or_sms(
    cam_idx: int,
    *,
    use_arduino_alarm: bool,
    # Arduino
    arduino_port: str,
    arduino_baud: str,
    arduino_duration_ms: int,
    cooldown_siren_sec: int,
    # A7680C direct COM
    sms_port: str,
    sms_baud: str,
    sms_unicode: bool,
    cooldown_sms_sec: int,
    # payload
    phone_list: list[str],
    text_msg: str
):
    """
    Trả về: (siren_msg, sms_msg, sms_dispatched, dispatched_phones, siren_led_flag)
    - use_arduino_alarm=True: gửi 1 lệnh ALARM để Arduino tự SMS -> còi -> đèn.
    - use_arduino_alarm=False: nếu có sms_port thì gửi SMS trực tiếp qua A7680C; còi/đèn (nếu có Arduino) sẽ chạy rời.
    """
    siren_msg = ""
    sms_msg = ""
    sms_dispatched = False
    dispatched_phones: list[str] = []
    siren_led_flag = "OFF"

    if use_arduino_alarm:
        # 1 lệnh duy nhất: Arduino tự gửi SMS -> còi -> đèn
        # Text cần ASCII-safe cho đường Arduino
        txt = ascii_safe(text_msg or "")
        ok_alarm, resp_alarm = send_alarm_via_arduino(
            arduino_port, arduino_baud, arduino_duration_ms, phone_list, txt, timeout=20.0
        )

        # Ghi SMS log theo từng số (transport=Arduino-ALARM)
        book = _json_load(PHONE_DB_PATH, {})
        reverse = {v: k for k, v in book.items()}
        for ph in (phone_list or []):
            name = reverse.get(ph, "")
            smslog_append(cam_idx, name, ph, ok_alarm, "Arduino-ALARM",
                          arduino_port, arduino_baud, 0, txt, str(resp_alarm))

        sms_msg = f"ALARM via Arduino: {'OK' if ok_alarm else ('ERR ' + str(resp_alarm))}"
        sms_dispatched = True
        dispatched_phones = list(phone_list or [])
        siren_msg = "SIREN+LED: via ALARM"
        siren_led_flag = "SENT"
        return siren_msg, sms_msg, sms_dispatched, dispatched_phones, siren_led_flag

    # use_arduino_alarm = False
    # 1) còi/đèn rời nếu có Arduino
    if (arduino_port or "").strip():
        # không block UI, cooldown do nơi gọi kiểm soát hoặc bắn thẳng 2 lệnh + hẹn tắt LED
        arduino_write_line(arduino_port, arduino_baud, f"SIR:{int(arduino_duration_ms)}")
        arduino_write_line(arduino_port, arduino_baud, "LED:1")
        threading.Thread(
            target=lambda: (
                time.sleep(max(0, int(arduino_duration_ms) / 1000.0)),
                arduino_write_line(arduino_port, arduino_baud, "LED:0")
            ),
            daemon=True
        ).start()
        siren_msg, siren_led_flag = "SIREN+LED: dispatched", "SENT"
    else:
        siren_msg, siren_led_flag = "SIREN: disabled", "OFF"

    # 2) SMS trực tiếp qua A7680C (nếu có cổng)
    if (sms_port or "").strip() and phone_list:
        maybe_send_sms_async_a7680c(True, sms_port, sms_baud,
                                    phone_list, text_msg, sms_unicode,
                                    cooldown_sms_sec, cam_idx)
        sms_msg = f"SMS A7680C: sent to {len(phone_list)} recipients"
        sms_dispatched = True
        dispatched_phones = list(phone_list or [])
    else:
        sms_msg = "SMS: disabled or no recipients"

    return siren_msg, sms_msg, sms_dispatched, dispatched_phones, siren_led_flag



# ============ SMS LOG (CSV) ============
SMS_LOG_PATH = os.getenv("SMS_LOG_PATH", "sms_log.csv")
_smslog_lock = threading.Lock()

def _ensure_smslog_csv():
    if not os.path.exists(SMS_LOG_PATH):
        with open(SMS_LOG_PATH, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["id","ts","cam","recipient_name","recipient_phone","ok",
                        "transport","port","baud","latency_ms","text","resp"])

def smslog_append(cam, name, phone, ok, transport, port, baud, latency_ms, text, resp):
    _ensure_smslog_csv()
    with _smslog_lock:
        rid = int(time.time() * 1000)
        with open(SMS_LOG_PATH, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([
                rid,
                datetime.datetime.now().isoformat(sep=" ", timespec="seconds"),
                str(cam),
                name or "",
                phone or "",
                1 if ok else 0,
                transport, str(port), str(baud),
                int(latency_ms),
                text or "",
                (resp or "")[:200]
            ])

def load_sms_logs():
    _ensure_smslog_csv()
    rows = []
    with open(SMS_LOG_PATH, "r", newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        for r in rd:
            rows.append(r)
    return rows

def filter_sms_logs(rows, query="", cams=None, names=None, status="any",
                    date_from="", date_to=""):
    def ok_status(r):
        if status == "ok":   return r["ok"] in ("1", 1, True, "True")
        if status == "fail": return r["ok"] in ("0", 0, False, "False")
        return True
    def in_cams(r):
        return (not cams) or (str(r["cam"]) in set(map(str, cams)))
    def in_names(r):
        return (not names) or (r.get("recipient_name","") in names)
    def in_time(r):
        if not date_from and not date_to: return True
        try:
            t = datetime.datetime.fromisoformat(r["ts"])
        except Exception:
            return True
        if date_from:
            try:
                if t < datetime.datetime.fromisoformat(date_from): return False
            except Exception: pass
        if date_to:
            try:
                if t > datetime.datetime.fromisoformat(date_to): return False
            except Exception: pass
        return True
    q = (query or "").strip().lower()
    out = []
    for r in rows:
        if not ok_status(r):  continue
        if not in_cams(r):    continue
        if not in_names(r):   continue
        if not in_time(r):    continue
        if q:
            hay = " ".join([r.get("text",""), r.get("resp",""), r.get("recipient_phone","")]).lower()
            if q not in hay: continue
        out.append(r)
    out.sort(key=lambda x: x["ts"], reverse=True)
    return out

def aggregate_sms(rows, by="day"):
    agg = {}
    for r in rows:
        key = ""
        if by == "camera":
            key = f"cam{r['cam']}"
        elif by == "recipient":
            key = r.get("recipient_name") or r.get("recipient_phone") or "unknown"
        else:  # day
            key = (r["ts"] or "")[:10]
        d = agg.setdefault(key, {"total": 0, "ok": 0, "fail": 0})
        d["total"] += 1
        if str(r["ok"]) in ("1", "True", "true"):
            d["ok"] += 1
        else:
            d["fail"] += 1
    rows = [{"key":k, **v} for k,v in agg.items()]
    rows.sort(key=lambda x: x["key"], reverse=True)
    return rows

# ============ ALARM LOG (CSV) ============
ALARM_LOG_PATH = os.getenv("ALARM_LOG_PATH", "alarm_log.csv")
_alarm_lock = threading.Lock()

def _ensure_alarm_csv():
    if not os.path.exists(ALARM_LOG_PATH):
        with open(ALARM_LOG_PATH, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ts","cam","count","track_id","frame","capture_file","siren_led","sms_dispatched","sms_recipients"])

def alarmlog_append(cam, count, track_id, frame_idx, capture_file, siren_led, sms_dispatched, sms_recipients):
    _ensure_alarm_csv()
    with _alarm_lock:
        with open(ALARM_LOG_PATH, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                cam, count, track_id, frame_idx,
                os.path.basename(capture_file) if capture_file else "",
                siren_led, "YES" if sms_dispatched else "NO",
                ";".join(sms_recipients or [])
            ])

def load_alarm_logs():
    _ensure_alarm_csv()
    rows = []
    with open(ALARM_LOG_PATH, "r", newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        for r in rd:
            rows.append(r)
    rows.sort(key=lambda x: x["ts"], reverse=True)
    return rows

# ===========================
# SMS via SIM A7680C (4G/LTE)
# ===========================
try:
    import serial
except Exception:
    serial = None




# ================ Arduino Siren (non-blocking, per-port lock) ================
from collections import defaultdict

def arduino_send_siren_light(port, baud, duration_ms, auto_led_off=True):
    """
    Gửi SIR:<ms> và LED:1 bằng kết nối COM dùng lại (arduino_write_line),
    tránh mở/đóng cổng liên tục gây 'Access is denied'.
    """
    ok1, r1 = arduino_write_line(port, baud, f"SIR:{int(duration_ms)}", read_timeout=0.5)
    ok2, r2 = arduino_write_line(port, baud, "LED:1", read_timeout=0.2)
    if auto_led_off:
        import threading, time as _t
        threading.Thread(
            target=lambda: (_t.sleep(max(0, int(duration_ms)/1000.0)),
                            arduino_write_line(port, baud, "LED:0", read_timeout=0.2)),
            daemon=True
        ).start()
    return (ok1 and ok2), (r1 if ok1 else r1) or (r2 if ok2 else r2)



_arduino_last = {}
_arduino_lock = threading.Lock()
def maybe_trigger_arduino_async(enabled, port, baud, duration_ms, cooldown_sec, cam_idx):
    if not enabled or not port:
        return
    key = f"{port}"
    now = time.time()
    with _arduino_lock:
        if float(cooldown_sec) > 0 and now - _arduino_last.get(key, 0.0) < float(cooldown_sec):
            return
        _arduino_last[key] = now
    def worker():
        ok, msg = arduino_send_siren_light(port, baud, duration_ms, auto_led_off=True)
        logger.info("ARDUINO %s -> %sms ok=%s msg=%s", port, duration_ms, ok, msg)
    threading.Thread(target=worker, daemon=True).start()

def to_ucs2_hex(text):
    """Convert text to UCS2 hex for A7680C"""
    try:
        return text.encode("utf-16-be").hex().upper()
    except Exception:
        return ""

def send_sms_a7680c(port, baud, phone, message, unicode_mode=True, timeout_sec=20.0):
    """Gửi SMS qua SIM A7680C (4G/LTE module) với bắt tay chắc và thời gian chờ linh hoạt."""
    if serial is None:
        return False, "pyserial not installed"

    try:
        ser = serial.Serial(port=str(port), baudrate=int(baud), timeout=2)
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        time.sleep(0.1)
    except Exception as e:
        return False, f"Serial open error: {e}"

    def writeln(cmd, sleep=0.12):
        ser.write((cmd + "\r\n").encode("ascii"))
        ser.flush()
        time.sleep(sleep)

    def read_response(wait_time=2.0):
        end_time = time.time() + wait_time
        buf = b""
        while time.time() < end_time:
            if ser.in_waiting:
                buf += ser.read(ser.in_waiting)
            time.sleep(0.05)
        return buf.decode("ascii", errors="ignore")

    try:
        # 0) Ping nhiều lần nếu cần
        ok = False
        for _ in range(4):
            writeln("AT", 0.15)
            resp = read_response(1.2)
            if "OK" in resp:
                ok = True
                break
        if not ok:
            return False, "Module not responding"

        # 1) Tắt echo + bật lỗi có mã
        writeln("ATE0")
        read_response(0.6)
        writeln("AT+CMEE=2")
        read_response(0.6)

        # 2) SIM & mạng
        writeln("AT+CPIN?")
        resp = read_response(1.5)
        if "READY" not in resp:
            return False, f"SIM not ready: {resp}"

        writeln("AT+CREG?")
        read_response(1.5)  # có thể kiểm tra ",1" hoặc ",5" nếu muốn chặt chẽ hơn
        writeln("AT+CSQ")
        read_response(1.0)

        # 3) Chế độ text & bảng mã
        writeln("AT+CMGF=1")
        read_response(0.8)

        if unicode_mode:
            writeln('AT+CSCS="UCS2"')
            read_response(0.8)
            phone_hex = to_ucs2_hex(phone)
            message_hex = to_ucs2_hex(message)

            writeln(f'AT+CMGS="{phone_hex}"', 0.6)
            resp = read_response(3.5)   # nới thời gian chờ prompt
            if ">" not in resp:
                return False, f"CMGS prompt not received: {resp}"

            ser.write(message_hex.encode("ascii"))
            ser.write(bytes([26]))  # Ctrl+Z
            ser.flush()
        else:
            writeln('AT+CSCS="GSM"')
            read_response(0.8)

            writeln(f'AT+CMGS="{phone}"', 0.6)
            resp = read_response(3.5)
            if ">" not in resp:
                return False, f"CMGS prompt not received: {resp}"

            ser.write(message.encode("latin-1", errors="ignore"))
            ser.write(bytes([26]))
            ser.flush()

        # 4) Chờ phản hồi gửi
        final_resp = read_response(timeout_sec)
        success = ("+CMGS:" in final_resp) or ("OK" in final_resp)
        try:
            ser.close()
        except Exception:
            pass
        return success, final_resp

    except Exception as e:
        try:
            ser.close()
        except Exception:
            pass
        return False, f"SMS send error: {e}"


# Cooldown và async sending
_sms_last = {}
_sms_lock = threading.Lock()

def maybe_send_sms_async_a7680c(enabled, port, baud, phones, text, unicode_mode, cooldown_sec, cam_idx):
    """Gửi SMS async với cooldown cho A7680C"""
    if not enabled or not phones:
        return
    
    key = f"cam{cam_idx}"
    now = time.time()
    with _sms_lock:
        if now - _sms_last.get(key, 0.0) < float(cooldown_sec):
            return
        _sms_last[key] = now

    def worker():
        book = _json_load(PHONE_DB_PATH, {})
        reverse = {v: k for k, v in book.items()}
        
        for ph in phones:
            name = reverse.get(ph, "")
            t0 = time.time()
            ok, resp = send_sms_a7680c(port, baud, ph, text, unicode_mode)
            latency = (time.time() - t0) * 1000.0
            smslog_append(cam_idx, name, ph, ok, "A7680C", port, baud, latency, text, resp)
            logger.info("SMS A7680C->%s ok=%s %.0fms resp=%s", ph, ok, latency, (resp or "")[:120])

    threading.Thread(target=worker, daemon=True).start()


# ===================== SMS via Arduino (forward to A7680C on D8/D9) =====================
_sms_via_arduino_last = 0.0
_sms_via_arduino_lock = threading.Lock()

def send_sms_via_arduino(a_port, a_baud, phone, text, timeout=20.0):
    """Gửi lệnh 'SMS:<phone>:<text>' tới Arduino. Arduino sẽ gửi AT cho A7680C.
       Trả về (ok, message)."""
    if serial is None:
        return False, "pyserial not installed"
    try:
        with serial.Serial(str(a_port), int(a_baud), timeout=1, write_timeout=1) as s:
            payload = f"SMS:{phone}:{text}\n"
            s.write(payload.encode("utf-8", errors="ignore"))
            s.flush()
            # đợi ACK "SMS:OK" hoặc "SMS:ERR"
            end = time.time() + float(timeout)
            buf = b""
            while time.time() < end:
                chunk = s.read(s.in_waiting or 1)
                if chunk:
                    buf += chunk
                    if b"SMS:OK" in buf:
                        return True, "OK"
                    if b"SMS:ERR" in buf:
                        return False, buf.decode(errors="ignore")
                time.sleep(0.05)
            return False, "Arduino no ACK for SMS"
    except Exception as e:
        return False, f"Serial error: {e}"

# --- Single-line ALARM via Arduino (Arduino sẽ tự SMS -> còi -> đèn) ---
# YÊU CẦU: Arduino đã nạp sketch hỗ trợ lệnh:
#   ALARM:<ms>:<phone1,phone2,...>:<text>\n
from collections import defaultdict as _dd
_AL_OPEN = {}                           # Lưu kết nối serial đã mở
_AL_LOCKS = _dd(threading.Lock)         # Khóa cho từng cổng Arduino

def send_alarm_via_arduino(a_port, a_baud, duration_ms, phones_list, text, timeout=25.0):
    phones_csv = ",".join(phones_list or [])
    # Tránh ký tự xuống dòng trong text
    clean_text = (text or "").replace("\r", " ").replace("\n", " ").strip()
    payload = f"ALARM:{int(duration_ms)}:{phones_csv}:{clean_text}"
    ok, resp = arduino_write_line(a_port, a_baud, payload, read_timeout=min(timeout, 2.0))
    return ok, resp


# ================ Phone Registry =========
PHONE_DB_PATH = os.getenv("PHONE_DB_PATH", "phones.json")
_phone_lock = threading.Lock()

def _json_load(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def _json_save(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

def list_phone_names():
    data = _json_load(PHONE_DB_PATH, {})
    return sorted(list(data.keys()))

def get_phone_by_name(name):
    if not name: 
        return ""
    data = _json_load(PHONE_DB_PATH, {})
    return data.get(name.strip(), "")

def upsert_phone(name, phone):
    n, p = (name or "").strip(), (phone or "").strip()
    if not n or not p:
        return False, "Tên/số không hợp lệ"
    with _phone_lock:
        data = _json_load(PHONE_DB_PATH, {})
        data[n] = p
        _json_save(PHONE_DB_PATH, data)
    return True, f"Đã lưu {n} → {p}"

def delete_phone(name):
    n = (name or "").strip()
    with _phone_lock:
        data = _json_load(PHONE_DB_PATH, {})
        if n in data:
            del data[n]
            _json_save(PHONE_DB_PATH, data)
            return True, f"Đã xoá {n}"
    return False, "Không tìm thấy"

def resolve_phones_from_names(names):
    """names: list[str] -> list[str] phone numbers."""
    if not names: 
        return []
    book = _json_load(PHONE_DB_PATH, {})
    out = []
    for n in names:
        ph = book.get((n or "").strip(), "")
        if ph: 
            out.append(ph)
    seen = set()
    res = []
    for ph in out:
        if ph not in seen:
            seen.add(ph)
            res.append(ph)
    return res

# ================ User Management =========
USERS_CSV = os.getenv("USERS_CSV", "users.csv")
_user_lock = threading.RLock()

def ensure_users_csv():
    if not os.path.exists(USERS_CSV):
        with open(USERS_CSV, "w", newline="", encoding="utf-8") as f:
            f.write("admin,1234\n")
    else:
        print(f"DEBUG: users.csv exists, checking permissions...")
        try:
            with open(USERS_CSV, "a", encoding="utf-8") as f:
                pass
            print(f"DEBUG: users.csv is writable")
        except Exception as e:
            print(f"DEBUG: users.csv is not writable: {e}")

def load_users():
    users = {}
    if not os.path.exists(USERS_CSV):
        return users
    try:
        with _user_lock:
            with open(USERS_CSV, "r", newline="", encoding="utf-8") as f:
                rd = csv.reader(f)
                for row in rd:
                    if row and len(row) >= 2 and row[0].strip():
                        users[row[0].strip()] = row[1].strip()
        return users
    except UnicodeDecodeError:
        with _user_lock:
            with open(USERS_CSV, "r", newline="") as f:
                rd = csv.reader(f)
                for row in rd:
                    if row and len(row) >= 2 and row[0].strip():
                        users[row[0].strip()] = row[1].strip()
        return users

def verify_user_plain(username, password):
    users = load_users()
    return users.get((username or "").strip()) == (password or "").strip()

def add_user(username, password):
    """Thêm user mới"""
    u, p = (username or "").strip(), (password or "").strip()
    if not u or not p:
        return False, "Username/password không được trống"
    with _user_lock:
        users = load_users()
        if u in users:
            return False, f"User '{u}' đã tồn tại"
        users[u] = p
        with open(USERS_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            for un, pw in users.items():
                w.writerow([un, pw])
    return True, f"Đã thêm user '{u}'"

def delete_user(username):
    """Xóa user"""
    u = (username or "").strip()
    print(f"DEBUG: Attempting to delete user: '{u}'")
    
    if u == "admin":
        print("DEBUG: Cannot delete admin")
        return False, "Không thể xóa admin"
    
    try:
        with _user_lock:
            users = load_users()
            print(f"DEBUG: Current users before deletion: {list(users.keys())}")
            
            if u not in users:
                print(f"DEBUG: User '{u}' not found in users")
                return False, f"User '{u}' không tồn tại"
            
            del users[u]
            print(f"DEBUG: After deletion, users: {list(users.keys())}")
            
            # Ghi lại file
            try:
                with open(USERS_CSV, "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    for un, pw in users.items():
                        w.writerow([un, pw])
                print(f"DEBUG: File written successfully")
            except Exception as e:
                print(f"DEBUG: Error writing file: {e}")
                return False, f"Lỗi ghi file: {e}"
        
        print(f"DEBUG: User '{u}' deleted successfully")
        return True, f"Đã xóa user '{u}'"
        
    except Exception as e:
        print(f"DEBUG: Error in delete_user: {e}")
        return False, f"Lỗi xóa user: {e}"

def list_users():
    """Lấy danh sách users"""
    users = load_users()
    result = [{"username": u, "password": "***" if u != "admin" else "admin"} for u in users.keys()]
    return result

# ================ Camera Registry =========
CAM_DB_PATH = os.getenv("CAM_DB_PATH", "cameras.json")

def load_cam_db():
    if not os.path.exists(CAM_DB_PATH):
        return []
    try:
        with open(CAM_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

def save_cam_db(cams: list):
    try:
        with open(CAM_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(cams, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def list_camera_names():
    return [c.get("name", "") for c in load_cam_db()]

def get_rtsp_by_name(name: str) -> str:
    key = (name or "").strip().lower()
    for c in load_cam_db():
        if (c.get("name", "") or "").strip().lower() == key:
            return c.get("rtsp", "")
    return ""

def upsert_camera(name: str, rtsp: str):
    name = (name or "").strip()
    rtsp = (rtsp or "").strip()
    if not name or not rtsp:
        return False, "Thiếu tên hoặc RTSP"
    cams = load_cam_db()
    for c in cams:
        if (c.get("name", "") or "").strip().lower() == name.lower():
            c["rtsp"] = rtsp
            save_cam_db(cams)
            return True, f"Đã cập nhật '{name}'"
    cams.append({"name": name, "rtsp": rtsp})
    save_cam_db(cams)
    return True, f"Đã thêm '{name}'"

def delete_camera(name: str):
    key = (name or "").strip().lower()
    cams = load_cam_db()
    new_cams = [c for c in cams if (c.get("name", "") or "").strip().lower() != key]
    if len(new_cams) == len(cams):
        return False, f"Không tìm thấy '{name}'"
    save_cam_db(new_cams)
    return True, f"Đã xóa '{name}'"

def list_cameras():
    """Lấy danh sách cameras"""
    cams = load_cam_db()
    return [{"name": c.get("name", ""), "rtsp": c.get("rtsp", "")} for c in cams]

# ================ Capture Management =========
def ensure_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        pass

def save_capture(image_bgr, capture_dir, count, track_id, source, line_pair, frame_idx):
    """Lưu ảnh .jpg vào capture_dir với tên theo thời gian"""
    ensure_dir(capture_dir)
    ts_iso = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    ts_name = ts_iso.replace("-", "").replace(":", "").replace(" ", "_").replace(".", "_")
    fname = f"{ts_name}_c{count}_id{track_id}_f{frame_idx}.jpg"
    fpath = os.path.join(capture_dir, fname)

    try:
        cv2.imwrite(fpath, image_bgr)
    except Exception as e:
        print("Capture save error:", e)

    # Ghi index.csv
    idx_path = os.path.join(capture_dir, "index.csv")
    try:
        new_file = not os.path.exists(idx_path)
        with open(idx_path, "a", newline="", encoding="utf-8") as f:
            wr = csv.writer(f)
            if new_file:
                wr.writerow(["timestamp", "filename", "count", "track_id", "frame", "source",
                             "p0x", "p0y", "p1x", "p1y"])
            p0 = p1 = None
            if isinstance(line_pair, dict):
                if line_pair.get("type") == "poly":
                    pts = line_pair.get("points") or []
                    if len(pts) >= 2:
                        p0, p1 = pts[0], pts[-1]
                else:
                    p0 = line_pair.get("p0")
                    p1 = line_pair.get("p1")

            wr.writerow([ts_iso, fname, count, track_id, frame_idx, source,
                         (p0[0] if p0 else None), (p0[1] if p0 else None),
                         (p1[0] if p1 else None), (p1[1] if p1 else None)])
    except Exception as e:
        print("Capture index write error:", e)
    return fpath

def search_captures(capture_dir, query_text):
    """Tìm kiếm ảnh trong thư mục"""
    try:
        if not os.path.isdir(capture_dir):
            return []
        files = [os.path.join(capture_dir, fn) for fn in os.listdir(capture_dir)
                 if fn.lower().endswith((".jpg", ".jpeg", ".png"))]
        files.sort(key=lambda p: os.path.basename(p), reverse=True)
        qt = (query_text or "").strip().lower()
        if qt:
            files = [p for p in files if qt in os.path.basename(p).lower()]
        return files[:200]
    except Exception as e:
        print("Search captures error:", e)
        return []

def search_captures_all(base_dir, query_text):
    """Tìm kiếm ảnh trong tất cả thư mục camera"""
    try:
        folders = [base_dir] + [os.path.join(base_dir, f"cam{i}") for i in range(4)]
        all_files = []
        for d in folders:
            all_files.extend(search_captures(d, query_text))
        seen = set()
        result = []
        for p in sorted(all_files, key=lambda p: os.path.basename(p), reverse=True):
            bn = os.path.basename(p)
            if bn in seen:
                continue
            seen.add(bn)
            result.append(p)
        return result[:200]
    except Exception as e:
        print("Search captures all error:", e)
        return []

# ================ Logging =================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app Multicam")

# ================ Device/Model Cache ======
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
_MODEL_CACHE = {}

def load_model(model_name: str):
    if model_name not in _MODEL_CACHE:
        m = YOLO(model=model_name)
        m.to(DEVICE)
        if DEVICE.startswith("cuda"):
            try:
                m.model.half()
                logger.info("Loaded %s on CUDA (FP16)", model_name)
            except Exception:
                logger.info("Loaded %s on CUDA (FP32)", model_name)
        else:
            logger.info("Loaded %s on CPU", model_name)
        _MODEL_CACHE[model_name] = m
    return _MODEL_CACHE[model_name]

# ================ Line / Geometry ===================

# --- Per-camera session state (0..3) ---
# --- Per-camera session state ---
CAM = {
    i: {
        "line": None,            # {'type':'poly', 'points':[(x,y)..], 'base_w':..., 'base_h':...} hoặc line 2 điểm đã scale
        "poly_points": [],       # danh sách điểm đang click vẽ polyline
        "poly_basewh": (None, None),
        "first_frame": None
    } for i in range(4)
}
def extract_first_frame(source):
    try:
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            return None, "Error: Could not open source."
        ok, frame = cap.read()
        cap.release()
        if not ok or frame is None:
            return None, "Error: Could not read the first frame."
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame_rgb), "First frame extracted successfully."
    except Exception as e:
        return None, f"Error: {e}"

def update_poly_click_factory(cam_id):
    def _handler(image, evt: gr.SelectData):
        if image is None:
            return None, "Please load a frame first."
        base_w, base_h = image.size
        CAM[cam_id]["poly_basewh"] = (base_w, base_h)

        pts = CAM[cam_id]["poly_points"]
        pts.append((evt.index[0], evt.index[1]))

        draw = ImageDraw.Draw(image)
        # vẽ nháp các đoạn đỏ
        for i in range(1, len(pts)):
            draw.line([pts[i-1], pts[i]], fill="red", width=2)
        # chấm vàng, chú ý ellipse(x0<=x1, y0<=y1)
        for (x, y) in pts:
            draw.ellipse((x-4, y-4, x+4, y+4), fill="yellow", outline="yellow")
        return image, f"Polyline[{len(pts)}]: {pts[-1]}"
    return _handler

def finish_polyline(cam_id, image):
    if image is None:
        return None, "Load frame first."
    pts = CAM[cam_id]["poly_points"][:]
    if len(pts) < 2:
        return image, "Cần >= 2 điểm."

    base_w, base_h = CAM[cam_id]["poly_basewh"]
    if base_w is None or base_h is None:
        base_w, base_h = image.size
        CAM[cam_id]["poly_basewh"] = (base_w, base_h)

    CAM[cam_id]["line"] = {"type": "poly", "points": pts, "base_w": base_w, "base_h": base_h}

    draw = ImageDraw.Draw(image)
    for i in range(1, len(pts)):
        draw.line([pts[i-1], pts[i]], fill="green", width=2)
    for (x, y) in pts:
        draw.ellipse((x-4, y-4, x+4, y+4), fill="green", outline="green")

    CAM[cam_id]["poly_points"].clear()
    return image, f"Polyline set ({len(pts)} points, base {base_w}x{base_h})"

def _scale_point(pt, from_w, from_h, to_w, to_h):
    x, y = pt
    sx = to_w / float(from_w); sy = to_h / float(from_h)
    return (int(round(x * sx)), int(round(y * sy)))

def _scale_points(pts, from_w, from_h, to_w, to_h):
    return [_scale_point(p, from_w, from_h, to_w, to_h) for p in (pts or [])]

def line_for_frame_cam(cam_id, curr_w, curr_h):
    ls = CAM[cam_id]["line"]
    if ls is None:
        return None

    if ls.get("type") == "poly":
        base_w, base_h = ls["base_w"], ls["base_h"]
        pts = _scale_points(ls.get("points") or [], base_w, base_h, curr_w, curr_h)
        return {"type": "poly", "points": pts, "base_w": curr_w, "base_h": curr_h}

    # nếu là line 2 điểm (nếu còn hỗ trợ)
    base_w, base_h = ls["base_w"], ls["base_h"]
    p0 = _scale_point(ls["p0"], base_w, base_h, curr_w, curr_h)
    p1 = _scale_point(ls["p1"], base_w, base_h, curr_w, curr_h)
    if p0[0] != p1[0]:
        m = (p1[1]-p0[1]) / float(p1[0]-p0[0]); b = p0[1] - m*p0[0]
        return {"type":"slope","m":m,"b":b,"p0":p0,"p1":p1,"base_w":curr_w,"base_h":curr_h}
    else:
        return {"type":"vertical","x":p0[0],"p0":p0,"p1":p1,"base_w":curr_w,"base_h":curr_h}

def reset_line_cam(cam_id):
    CAM[cam_id]["poly_points"].clear()
    CAM[cam_id]["poly_basewh"] = (None, None)
    CAM[cam_id]["line"] = None
    return None, T("reset_ok", cam=cam_id)



# ================ Geometry: segment intersect =========
def segments_intersect(a, b, c, d):
    def ccw(A, B, C):
        return (C[1]-A[1])*(B[0]-A[0]) - (B[1]-A[1])*(C[0]-A[0])
    def on_segment(A, B, C):
        return min(A[0],B[0]) <= C[0] <= max(A[0],B[0]) and min(A[1],B[1]) <= C[1] <= max(A[1],B[1])
    c1 = ccw(a, b, c); c2 = ccw(a, b, d); c3 = ccw(c, d, a); c4 = ccw(c, d, b)
    if (c1*c2 < 0) and (c3*c4 < 0): return True
    if c1 == 0 and on_segment(a,b,c): return True
    if c2 == 0 and on_segment(a,b,d): return True
    if c3 == 0 and on_segment(c,d,a): return True
    if c4 == 0 and on_segment(c,d,b): return True
    return False

# ================ Core processing ====================
def process_video(confidence_threshold=0.35,
                  analysis_ratio=0.30,
                  file_input=None,
                  rtsp_text="",
                  imgsz=384,
                  model_name="yolov8n.pt",
                  debug_overlay=False,
                  fast_render=False,
                  # Capture
                  capture_enabled=True,
                  capture_dir="captures",
                  capture_annotated=True,
                  # Arduino Siren
                  arduino_enabled=False,
                  arduino_port="",
                  arduino_baud="9600",
                  arduino_duration_ms=3000,
                  arduino_cooldown=10,
                  # SMS A7680C
                  sms_enabled=False,
                  sms_port="",
                  sms_baud="9600",
                  sms_unicode=True,
                  sms_cooldown=30,
                  sms_template="CẢNH BÁO: Cam{cam} => Có người vượt tường lúc {time}. Count={count}",
                  sms_recipients_names=None,
                  # cam index
                  cam_idx=0,
                  cam_id=0
                  
                  ):
    """Person-only (class 0). Count when motion segment crosses the user line."""
    if CAM[cam_id]["line"] is None:
        return None, T("no_line", cam=cam_id)

    # Resolve source
    if file_input is not None and hasattr(file_input, "name") and file_input.name:
        source = file_input.name
    elif isinstance(rtsp_text, str) and rtsp_text.strip():
        source = rtsp_text.strip()
    else:
        return None, T("missing_rtsp", cam=cam_id)

    # Resolve recipients
    try:
        phone_list = resolve_phones_from_names(sms_recipients_names or [])
    except Exception:
        phone_list = []


    # Load model
    try:
        model = load_model(model_name)
    except Exception as e:
        return None, T("model_err", err=e)

    # analysis_ratio -> vid_stride
    try:
        analysis_ratio = max(0.05, min(1.0, float(analysis_ratio)))
    except Exception:
        analysis_ratio = 0.30
    vid_stride = max(1, int(round(1.0 / analysis_ratio)))

    classes = [0]
    prev_centroid, last_cross_frame = {}, {}
    min_gap_frames = 10
    count, frame_idx = 0, 0
    ui_update_every = 3
    last_msg = "" 
    
    # Start tracker
    try:
        results_gen = model.track(
            source=source,
            stream=True,
            imgsz=int(imgsz),
            conf=float(confidence_threshold),
            classes=classes,
            device=DEVICE,
            verbose=False,
            persist=True,
            tracker="bytetrack.yaml",
            vid_stride=int(vid_stride)
        )
    except Exception as e:
        return None, T("tracker_err", err=e)

    for res in results_gen:
        frame_idx += 1
        # annotated = res.plot()
        if fast_render and hasattr(res, "orig_img") and res.orig_img is not None:
            annotated = res.orig_img.copy()
        else:
            annotated = res.plot()
        h, w = annotated.shape[:2]


        lp_curr = line_for_frame_cam(cam_id, w, h)
        if lp_curr is None:
            cv2.putText(annotated, T("no_line", cam=cam_id), (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
            yield annotated, f"No/invalid line for cam {cam_id}"
            return None, ""

        is_poly = (lp_curr.get("type") == "poly")
        if is_poly:
            pts = lp_curr.get("points") or []
            for j in range(1, len(pts)):
                cv2.line(annotated, pts[j-1], pts[j], (0,255,0), 2)
        else:
            cv2.line(annotated, lp_curr["p0"], lp_curr["p1"], (0,255,0), 2)
            p_line0, p_line1 = lp_curr["p0"], lp_curr["p1"]

        # counting
        if hasattr(res, "boxes") and res.boxes is not None and res.boxes.id is not None:
            ids = res.boxes.id.int().cpu().tolist()
            xyxy = res.boxes.xyxy.cpu().tolist()
            for tid, box in zip(ids, xyxy):
                x1, y1, x2, y2 = box
                cx, cy = int((x1+x2)/2), int((y1+y2)/2)
                cur_pt = (cx, cy)

                if tid in prev_centroid:
                    prev_pt = prev_centroid[tid]
                    if is_poly:
                        crossed = False
                        for j in range(1, len(pts)):
                            if segments_intersect(prev_pt, cur_pt, pts[j-1], pts[j]):
                                crossed = True
                                break
                    else:
                        crossed = segments_intersect(prev_pt, cur_pt, p_line0, p_line1)
                    if crossed:
                        last_fr = last_cross_frame.get(tid, -10**9)
                        if frame_idx - last_fr >= min_gap_frames:
                            count += 1
                            last_cross_frame[tid] = frame_idx

                            # Capture
                            cap_msg = ""
                            if capture_enabled:
                                try:
                                    frame_to_save = annotated if capture_annotated else (
                                        res.orig_img if hasattr(res, "orig_img") and res.orig_img is not None else annotated
                                    )
                                    saved_path = save_capture(
                                        image_bgr=frame_to_save,
                                        capture_dir=os.path.join(capture_dir, f"cam{cam_id}"),
                                        count=count, track_id=tid, source=str(source),
                                        line_pair=lp_curr, frame_idx=frame_idx
                                    )
                                    cap_msg = f"CAP: {os.path.basename(saved_path)}"
                                except Exception as e:
                                    cap_msg = f"CAP ERR: {e}"
                            # --- Decide path: direct SMS (A7680C COM) or Arduino single-line ALARM ---
                            # --- Decide path & dispatch by single function ---
                            use_arduino_alarm = bool(
                                phone_list
                                and not (sms_port or "").strip()             # nếu KHÔNG cấu hình cổng SMS riêng -> ưu tiên ALARM qua Arduino
                                and arduino_enabled and (arduino_port or "").strip()
                            )

                            ts_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            raw_text = (sms_template or "").format(time=ts_now, count=count, cam=cam_idx)

                            siren_msg, sms_msg, sms_dispatched, dispatched_phones, siren_led_flag = dispatch_alarm_or_sms(
                                cam_idx=cam_idx,
                                use_arduino_alarm=use_arduino_alarm,
                                arduino_port=arduino_port, arduino_baud=arduino_baud, arduino_duration_ms=arduino_duration_ms,
                                cooldown_siren_sec=int(arduino_cooldown or 0),
                                sms_port=sms_port, sms_baud=sms_baud, sms_unicode=bool(sms_unicode), cooldown_sms_sec=int(sms_cooldown or 0),
                                phone_list=phone_list,
                                text_msg=raw_text
                            )
                                
                            # --- Ghi ALARM LOG (sự kiện crossing) ---
                            alarmlog_append(
                                cam=cam_idx, count=count, track_id=tid, frame_idx=frame_idx,
                                capture_file=(saved_path if capture_enabled and 'saved_path' in locals() and saved_path else ""),
                                siren_led=siren_led_flag,
                                sms_dispatched=sms_dispatched,
                                sms_recipients=dispatched_phones,
                            )


                            siren_msg = siren_msg if 'siren_msg' in locals() else ""
                            sms_msg = sms_msg if 'sms_msg' in locals() else ""

                            # --- HUD ngắn gọn ---
                            cap_basename = os.path.basename(saved_path) if capture_enabled and 'saved_path' in locals() and saved_path else ""
                            hud = " | ".join([m for m in [siren_msg, (f"CAP: {cap_basename}" if cap_basename else ""), sms_msg] if m])

                            cv2.putText(annotated, hud[:90], (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)
                            last_msg = hud

                            if debug_overlay:
                                cv2.line(annotated, prev_pt, cur_pt, (255, 255, 0), 2)
                                cv2.circle(annotated, cur_pt, 4, (0, 255, 255), -1)


                prev_centroid[tid] = cur_pt

        # HUD
        (tw, th), _ = cv2.getTextSize(f"COUNT: {count}", cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        margin = 10
        x = (w - tw) // 2; y = th + margin
        cv2.rectangle(annotated, (x - margin, y - th - margin), (x + tw + margin, y + margin), (0,0,0), -1)
        cv2.putText(annotated, f"COUNT: {count}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        if frame_idx % ui_update_every == 0:
            yield annotated, (last_msg or "")
            last_msg = ""


    return None, ""

def build_cam_tile_compact(cam_idx,
                           # shared settings
                           confidence_threshold, analysis_ratio, imgsz, model_name, debug_overlay,fast_render,
                           capture_enabled, capture_dir, capture_annotated,
                           # Arduino
                           arduino_enabled, arduino_port, arduino_baud, arduino_duration_ms, arduino_cooldown,
                           # SMS
                           sms_enabled, sms_port, sms_baud, sms_unicode, sms_cooldown, sms_template):
    """
    Tile gọn: KHÔNG có toolbar cục bộ (Saved / Load / Reset).
    Toolbar chung ở trên sẽ thao tác theo camera đang chọn.
    """
    with gr.Group(elem_classes=["card"]) as tile_group:
        gr.Markdown(f"### Camera {cam_idx}")

        # RTSP riêng của tile
        rtsp  = gr.Textbox(placeholder="rtsp://user:pass@ip:554/...", lines=1, label=None,
                           elem_classes=["rtsp-slim"])

        # Khung ảnh: first để click vẽ line, out để stream khi chạy
        first = gr.Image(type="pil", height=240, visible=False, label=None, elem_classes=["cam-img"])
        out   = gr.Image(streaming=True, height=240, visible=False, label=None, elem_classes=["cam-img"])

        # Thông tin/tin nhắn
        info  = gr.Textbox(label="", interactive=False, elem_classes=["cam-info"])

        # Người nhận SMS riêng cho tile
        sms_to = gr.Dropdown(label="Người nhận SMS",
                             choices=list_phone_names(), multiselect=True, value=None)

        # Nút Run nhỏ trong tile (stream ổn định nhất theo cách bind cố định output)
        run   = gr.Button("Run ▶", elem_classes=["btn-tiny"])

        # --- Sự kiện vẽ line cho tile ---
        first.select(update_poly_click_factory(cam_idx), inputs=[first], outputs=[first, info])


        # --- Precheck trước khi chạy & chuyển first->out ---
        def _precheck(rtsp_str):
            s = (rtsp_str or "").strip()
            if not s:
                return gr.update(), gr.update(), T("missing_rtsp", cam=cam_idx)
            if CAM[cam_idx]["line"] is None:
                return gr.update(), gr.update(), T("draw_first", cam=cam_idx)
            return gr.update(visible=False), gr.update(value=None, visible=True), T("starting", cam=cam_idx)



        run.click(_precheck, inputs=[rtsp], outputs=[first, out, info], concurrency_limit=None, concurrency_id=f"pre_cam_{cam_idx}").then(
            process_video,
            inputs=[
                confidence_threshold, analysis_ratio, gr.State(None), rtsp, imgsz, model_name, debug_overlay, fast_render,
                capture_enabled, capture_dir, capture_annotated,
                # Arduino
                arduino_enabled, arduino_port, arduino_baud, arduino_duration_ms, arduino_cooldown,
                # SMS
                sms_enabled, sms_port, sms_baud, sms_unicode, sms_cooldown, sms_template, sms_to,
                gr.State(cam_idx), gr.State(cam_idx)
            ],
            outputs=[out, info]
        ).then(_audio_clear, inputs=None, outputs=[sfx_alarm]).then(_play_if_cap, inputs=[info], outputs=[sfx_alarm])

        btn_poly_finish = gr.Button("Finish Poly", elem_classes=["btn-tiny"])
        btn_poly_clear  = gr.Button("Clear Poly", elem_classes=["btn-tiny"])

        def _finish(image):
            return finish_polyline(cam_idx, image)

        def _clear():
            CAM[cam_idx]["poly_points"].clear()
            CAM[cam_idx]["line"] = None
            base = CAM[cam_idx]["first_frame"]
            img_out = (base.copy() if base is not None else None)
            return img_out, f"Cleared polyline (cam {cam_idx})."



        btn_poly_finish.click(_finish, inputs=[first], outputs=[first, info])
        btn_poly_clear.click(_clear, inputs=None, outputs=[first, info])


    # Trả về handle để toolbar chung thao tác
    return {
        "group": tile_group,
        "rtsp": rtsp, "first": first, "out": out, "info": info,
        "sms_to": sms_to, "run": run
    }


# ================ Gradio App =========================
ensure_users_csv()
COMPACT_CSS = """
/* luôn scope theo container của Gradio để chắc ăn */
.gradio-container .card{
  border:1px solid #334155; border-radius:10px;
  background:#0f172a; padding:8px; overflow:hidden;
}
.gradio-container .card h3{ margin:0 0 6px 0; color:#e2e8f0; }

/* thanh công cụ & nút nhỏ */
.gradio-container .toolbar{ display:flex; gap:6px; align-items:center; flex-wrap:wrap; }
.gradio-container .toolbar .gr-button,
.gradio-container .btn-tiny .gr-button,
.gradio-container .btn-tiny button{
  padding:4px 10px !important; min-height:28px !important; font-size:12px !important;
}

/* dropdown / textbox gọn */
.gradio-container .drop-slim > div > label,
.gradio-container .rtsp-slim > div > label{ display:none !important; }
.gradio-container .drop-slim .wrap .single-select,
.gradio-container .toolbar .wrap .single-select{
  min-height:28px !important;
}
.gradio-container .rtsp-slim textarea{ min-height:32px !important; font-size:12px !important; }

/* khung ảnh & hộp info mảnh */
.gradio-container .cam-img .label-wrap{ display:none !important; }
.gradio-container .cam-info textarea{ min-height:28px !important; font-size:12px !important; }

/* Lưới 2×2 cho camera tiles — tối ưu cho laptop 15.4" */
.gradio-container .grid-tiles{
  display: grid;
  grid-template-columns: repeat(2, minmax(320px, 1fr));
  gap: 12px;
  align-items: start;
}
/* Ngăn con grid bị min-width đẩy tràn hàng */
.gradio-container .grid-tiles > *{ min-width: 0 !important; }

/* (tuỳ chọn) Chỉ ép 1 cột khi cực hẹp */
@media (max-width: 320px){
  .gradio-container .grid-tiles{ grid-template-columns: 1fr; }
}
#brand-footer {{
  position: fixed; right: 12px; bottom: 10px;
  opacity: .75; font-size: 12px; z-index: 9999;
  pointer-events: none; user-select: none;
}}
#brand-header {{
  margin: 0 0 8px 0; opacity: .9;
}}
"""

AUTHOR   = "© PHẠM QUANG BIỂN"
APP_NAME = f"Hệ thống camera giám sát thông minh — {AUTHOR}"
VERSION  = "v1.0.0"




with gr.Blocks(
    css=COMPACT_CSS,
    title="HỆ THỐNG CAMERA GIÁM SÁT THÔNG MINH",
    analytics_enabled=False,
) as demo:
    gr.Markdown(f"### <span id='brand-header'>{APP_NAME}</span>")
    session_user = gr.State({"ok": False, "username": ""})

    # ---- Login ----
    with gr.Group(visible=True) as login_panel:
        gr.Markdown("HỆ THỐNG CAMERA GIÁM SÁT THÔNG MINH")
        gr.Markdown("### Đăng nhập để sử dụng hệ thống")
        in_user = gr.Textbox(label="Username")
        in_pass = gr.Textbox(label="Password", type="password")
        btn_login = gr.Button("Đăng nhập", variant="primary")
        login_msg = gr.Markdown("")

    # ---- App ----
    with gr.Group(visible=False) as app_panel:
        with gr.Row():
            hello = gr.Markdown("")
            btn_logout = gr.Button("Đăng xuất")

        with gr.Tabs():
            # SETTINGS tab -> dùng Accordion cho gọn
            with gr.Tab("⚙️ Settings"):
                with gr.Accordion("YOLO & Phân tích", open=True):
                    model_name = gr.Dropdown(choices=["yolov8n.pt", "yolo11n.pt"],
                                             value="yolov8n.pt", label="Mô hình YOLO")
                    imgsz = gr.Slider(256, 640, value=384, step=32, label="Kích thước khung")
                    confidence_threshold = gr.Slider(0.05, 0.80, value=0.35, step=0.01, label="Ngưỡng nhạy cảm")
                    analysis_ratio = gr.Slider(0.05, 1.0, value=0.30, step=0.05, label="Tỉ lệ phân tích")
                    debug_overlay = gr.Checkbox(True, label="Debug Overlay")
                    fast_render = gr.Checkbox(True, label="Xử lý nhanh (không đóng khung)")


                with gr.Accordion("Lưu ảnh khi vượt line", open=False):
                    capture_enabled = gr.Checkbox(True, label="Save Image on Crossing")
                    capture_dir = gr.Textbox(value="captures", label="Capture Directory")
                    capture_annotated = gr.Checkbox(True, label="Save Annotated Frame")

                with gr.Accordion("📟 SMS A7680C", open=False):
                    sms_enabled = gr.Checkbox(False, label="Enable SMS (A7680C)")
                    sms_port = gr.Textbox(value="", label="Serial Port (COMx / /dev/ttyUSBx)")
                    sms_baud = gr.Textbox(value="9600", label="Baud Rate (A7680C)")
                    sms_unicode = gr.Checkbox(True, label="Unicode (UCS2)")
                    sms_cooldown = gr.Slider(5, 600, value=30, step=5, label="Cooldown (seconds)")
                    sms_template = gr.Textbox(
                        value="CẢNH BÁO: Cam{cam} => Có người vượt tường lúc {time}. Count={count}",
                        lines=3, label="Message Template"
                    )

                with gr.Accordion("🔔 Arduino", open=False):
                    arduino_enabled = gr.Checkbox(True, label="Bật Arduino")
                    arduino_port = gr.Textbox(value="COM6", label="Arduino Serial Port")
                    arduino_baud = gr.Textbox(value="9600", label="Arduino Baud")
                    arduino_duration_ms = gr.Slider(500, 10000, value=2200, step=50, label="Alarm Duration (ms)")
                    arduino_cooldown = gr.Slider(0, 120, value=6, step=1, label="Alarm Cooldown (s)")

                lang_dd = gr.Dropdown(["vi","en"], value="vi", label="Language")
                def set_lang(l):
                    global LANG
                    LANG = (l or "vi")
                    return T("run_ok", cam=0)  # trả 1 thông điệp ví dụ
                lang_dd.change(set_lang, inputs=[lang_dd], outputs=[hello])


            # CAMERA CONTROL tab
            with gr.Tab("📹 Điều khiển camera"):
                # Toolbar chung: chọn cam + thao tác + ẩn/hiện
                with gr.Row(elem_classes=["toolbar"]):
                    camera_select = gr.Dropdown(
                        choices=[f"Cam{i}" for i in range(4)],
                        value="Cam0", label="Chọn Camera", scale=3
                    )

                    saved_pick = gr.Dropdown(
                        label="Đã lưu", choices=list_camera_names(), value=None, scale=4,
                        elem_classes=["drop-slim"]
                    )
                    btn_saved_refresh = gr.Button("↻", elem_classes=["btn-tiny"])

                    btn_global_load  = gr.Button("Tải", elem_classes=["btn-tiny"])
                    btn_global_reset = gr.Button("Đặt lại", elem_classes=["btn-tiny"])
                    btn_global_siren = gr.Button("🔔 Thử còi", elem_classes=["btn-tiny"])
                    btn_global_sms   = gr.Button("✉️ Thử SMS", elem_classes=["btn-tiny"])
                    btn_global_alarm = gr.Button("🚨 Thử còi/đèn/SMS", elem_classes=["btn-tiny"])

                # Loa ẩn cho tất cả client (mỗi tab trình duyệt một phiên)
                sfx_alarm = gr.Audio(label="Alarm", autoplay=True, interactive=False, visible=False)

                # Checkbox group ẩn/hiện 4 tile
                show_cams = gr.CheckboxGroup(choices=[f"Cam{i}" for i in range(4)],
                                             value=[f"Cam{i}" for i in range(4)],
                                             label="Hiển thị ô Camera")

                # Tạo 4 tile 2×2
                shared_args = (
                    confidence_threshold, analysis_ratio, imgsz, model_name, debug_overlay,fast_render,
                    capture_enabled, capture_dir, capture_annotated,
                    arduino_enabled, arduino_port, arduino_baud, arduino_duration_ms, arduino_cooldown,
                    sms_enabled, sms_port, sms_baud, sms_unicode, sms_cooldown, sms_template
                )
                cam_ui = []
                with gr.Row(equal_height=True) as _row_two_cols:
                    with gr.Column(scale=1, min_width=0):
                        cam_ui.append(build_cam_tile_compact(0, *shared_args))
                        cam_ui.append(build_cam_tile_compact(1, *shared_args))
                    with gr.Column(scale=1, min_width=0):
                        cam_ui.append(build_cam_tile_compact(2, *shared_args))
                        cam_ui.append(build_cam_tile_compact(3, *shared_args))

                # ==== Handlers của toolbar chung ====
                def _idx(sel):
                    try:
                        return int((sel or "Cam0").replace("Cam", ""))
                    except Exception:
                        return 0

                # 1) Refresh danh sách Saved
                def refresh_saved_choices():
                    return gr.update(choices=list_camera_names())
                btn_saved_refresh.click(refresh_saved_choices, None, [saved_pick])

                # 2) Chọn Saved -> đổ RTSP vào cam đang chọn
                def saved_to_rtsp(sel_cam, saved_name):
                    i = _idx(sel_cam)
                    url = get_rtsp_by_name(saved_name) or ""
                    outs = []
                    for k in range(4):
                        outs.append(gr.update(value=url) if k == i else gr.update())
                    return outs

                btn = saved_pick.change if saved_pick else None
                camera_select.change(
                    saved_to_rtsp,
                    inputs=[camera_select, saved_pick],
                    outputs=[cam_ui[0]["rtsp"], cam_ui[1]["rtsp"], cam_ui[2]["rtsp"], cam_ui[3]["rtsp"]],
                )

                saved_pick.change(
                    saved_to_rtsp,
                    inputs=[camera_select, saved_pick],
                    outputs=[cam_ui[0]["rtsp"], cam_ui[1]["rtsp"], cam_ui[2]["rtsp"], cam_ui[3]["rtsp"]],
                )

                # 3) LOAD (toolbar): lấy frame đầu và hiện first, ẩn out cho cam đang chọn
                def global_load(sel, r0, r1, r2, r3, saved_name):
                    i = _idx(sel)
                    rtsps = [r0, r1, r2, r3]
                    s = (rtsps[i] or "").strip()

                    if not s and (saved_name or "").strip():
                        s = (get_rtsp_by_name(saved_name) or "").strip()
                        rtsps[i] = s

                    outs = []
                    if not s:
                        # 4 cam × (first, out, info)
                        for k in range(4):
                            if k == i:
                                outs += [gr.update(value=None, visible=False),
                                         gr.update(visible=False),
                                         T("missing_rtsp", cam=i)]
                            else:
                                outs += [gr.update(), gr.update(), gr.update()]
                    else:
                        img, msg = extract_first_frame(s)
                        CAM[i]["first_frame"] = img.copy() if img is not None else None
                        vis = img is not None
                        for k in range(4):
                            if k == i:
                                outs += [gr.update(value=(img if vis else None), visible=vis),
                                         gr.update(visible=False),
                                         (msg or T("load_ok", cam=i))]
                            else:
                                outs += [gr.update(), gr.update(), gr.update()]

                    # +4 ô RTSP
                    for k in range(4):
                        outs.append(gr.update(value=rtsps[k]) if k == i and rtsps[k] else gr.update())
                    return outs





                btn_global_load.click(
                    global_load,
                    inputs=[camera_select,
                            cam_ui[0]["rtsp"], cam_ui[1]["rtsp"], cam_ui[2]["rtsp"], cam_ui[3]["rtsp"],
                            saved_pick],
                    outputs=[
                        # Cam0
                        cam_ui[0]["first"], cam_ui[0]["out"],  cam_ui[0]["info"],
                        # Cam1
                        cam_ui[1]["first"], cam_ui[1]["out"],  cam_ui[1]["info"],
                        # Cam2
                        cam_ui[2]["first"], cam_ui[2]["out"],  cam_ui[2]["info"],
                        # Cam3
                        cam_ui[3]["first"], cam_ui[3]["out"],  cam_ui[3]["info"],
                        # +4 ô RTSP
                        cam_ui[0]["rtsp"],  cam_ui[1]["rtsp"],  cam_ui[2]["rtsp"],  cam_ui[3]["rtsp"],
                    ],
                )



                # 4) RESET line cho cam đang chọn
                def global_reset(sel):
                    i = _idx(sel)
                    _, txt = reset_line_cam(i)
                    outs = []
                    for k in range(4):
                        if k == i:
                            outs += [gr.update(visible=True), gr.update(visible=False), txt]
                        else:
                            outs += [gr.update(), gr.update(), gr.update()]
                    return outs

                btn_global_reset.click(
                    global_reset, inputs=[camera_select],
                    outputs=[
                        cam_ui[0]["first"], cam_ui[0]["out"], cam_ui[0]["info"],
                        cam_ui[1]["first"], cam_ui[1]["out"], cam_ui[1]["info"],
                        cam_ui[2]["first"], cam_ui[2]["out"], cam_ui[2]["info"],
                        cam_ui[3]["first"], cam_ui[3]["out"], cam_ui[3]["info"],
                    ],
                )

                # 5) Test Siren theo cam đang chọn
                def global_siren(sel, aport, abaud, dur):
                    i = _idx(sel)
                    if not aport:
                        return [ (T("no_arduino", cam=i) if k==i else gr.update()) for k in range(4) ]
                    maybe_trigger_arduino_async(True, aport, abaud, dur, 0, i)
                    return [(T("siren_dispatched", cam=i, ms=dur) if k==i else gr.update()) for k in range(4)]


                btn_global_siren.click(
                    global_siren,
                    inputs=[camera_select, arduino_port, arduino_baud, arduino_duration_ms],
                    outputs=[cam_ui[0]["info"], cam_ui[1]["info"], cam_ui[2]["info"], cam_ui[3]["info"]],
                )

                # 6) Test SMS theo cam đang chọn
                def global_sms(sel, sms_port_i, sms_baud_i, unicode_mode,   # có trong chữ ký cũ, nhưng sẽ bỏ qua
                               to0, to1, to2, to3,
                               a_enabled, a_port, a_baud):
                    # Parse "CamX" -> index i
                    try:
                        i = int(str(sel).replace("Cam", "")) if sel else 0
                    except Exception:
                        i = 0

                    names = [to0, to1, to2, to3][i] or []
                    phones = resolve_phones_from_names(names)
                    outs = ["", "", "", ""]

                    if not (a_enabled and (a_port or "").strip()):
                        outs[i] = T("no_arduino", cam=i); return outs
                        return outs
                    if not phones:
                        outs[i] = T("no_recipients", cam=i); return outs

                        return outs

                    ts  = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    txt = f"TEST SMS: Cam{i} at {ts}"
                    safe_txt = ascii_safe(txt)  # ĐƯỜNG ARDUINO nên ASCII-safe

                    book = _json_load(PHONE_DB_PATH, {})
                    reverse = {v: k for k, v in book.items()}

                    ok_count = 0
                    last_resp = ""
                    for ph in phones:
                        ok, resp = send_sms_via_arduino(a_port, a_baud, ph, safe_txt, timeout=20.0)
                        last_resp = str(resp)
                        smslog_append(i, reverse.get(ph, ""), ph, ok, "Arduino-SMS", a_port, a_baud, 0, safe_txt, last_resp)
                        if ok:
                            ok_count += 1
                        # nhỏ giọt nhẹ để modem không nghẹt (tùy bạn, có thể bỏ nếu Arduino đã tự delay)
                        time.sleep(0.2)

                    outs[i] = T("test_sms_done", cam=i, ok=ok_count, total=len(phones), resp=last_resp)
                    return outs

                btn_global_sms.click(
                    global_sms,
                    inputs=[camera_select, sms_port, sms_baud, sms_unicode,
                            cam_ui[0]["sms_to"], cam_ui[1]["sms_to"], cam_ui[2]["sms_to"], cam_ui[3]["sms_to"],
                            arduino_enabled, arduino_port, arduino_baud],   # <<< THÊM 3 input này
                    outputs=[cam_ui[0]["info"], cam_ui[1]["info"], cam_ui[2]["info"], cam_ui[3]["info"]],
                )


                

                # 7) Test ALARM theo cam đang chọn
                def global_alarm(sel, aport, abaud, dur,
                                 sms_en, sms_port_in, sms_baud_in, unicode_mode,  # có trong chữ ký cũ, nhưng ta sẽ bỏ qua vì chỉ dùng Arduino
                                 to0, to1, to2, to3):
                    # Parse "CamX" -> index i
                    try:
                        i = int(str(sel).replace("Cam", "")) if sel else 0
                    except Exception:
                        i = 0

                    names = [to0, to1, to2, to3][i] or []
                    phones = resolve_phones_from_names(names)
                    outs = ["", "", "", ""]

                    if not (aport or "").strip():
                        outs[i] = T("no_arduino", cam=i); return outs
                        return outs
                    if not phones:
                        outs[i] = T("no_recipients", cam=i); return outs
                        return outs

                    ts  = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    txt = f"TEST ALARM: Cam{i} at {ts}"  # sẽ ascii_safe bên trong dispatcher; bằng tiếng Anh

                    # Chỉ dùng đường ALARM 1 dòng qua Arduino
                    siren_msg, sms_msg, _, _, _ = dispatch_alarm_or_sms(
                        cam_idx=i,
                        use_arduino_alarm=True,                 # <-- ép dùng ALARM Arduino
                        arduino_port=aport,
                        arduino_baud=abaud,
                        arduino_duration_ms=int(dur),
                        cooldown_siren_sec=0,                   # test thì không cần cooldown
                        sms_port="", sms_baud="", sms_unicode=False, cooldown_sms_sec=0,  # không dùng cổng SMS PC
                        phone_list=phones,
                        text_msg=txt
                    )

                    outs[i] = f"{sms_msg} | {siren_msg}"
                    return outs


                btn_global_alarm.click(
                    global_alarm,
                    inputs=[camera_select, arduino_port, arduino_baud, arduino_duration_ms,
                            sms_enabled, sms_port, sms_baud, sms_unicode,
                            cam_ui[0]["sms_to"], cam_ui[1]["sms_to"], cam_ui[2]["sms_to"], cam_ui[3]["sms_to"]],
                    outputs=[cam_ui[0]["info"], cam_ui[1]["info"], cam_ui[2]["info"], cam_ui[3]["info"]],
                ).then(_audio_clear, inputs=None, outputs=[sfx_alarm]).then(_play_alarm_static, inputs=None, outputs=[sfx_alarm])
# Ẩn/hiện các tile theo checkbox
                def toggle_tiles(show_list):
                    show = set(show_list or [])
                    return [
                        gr.update(visible=("Cam0" in show)),
                        gr.update(visible=("Cam1" in show)),
                        gr.update(visible=("Cam2" in show)),
                        gr.update(visible=("Cam3" in show)),
                    ]
                show_cams.change(toggle_tiles, inputs=[show_cams],
                                 outputs=[cam_ui[0]["group"], cam_ui[1]["group"], cam_ui[2]["group"], cam_ui[3]["group"]])


            # Tab 2: User Management
            with gr.Tab("👥 Quản lý người dùng"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Thêm User mới")
                        new_username = gr.Textbox(label="Username")
                        new_password = gr.Textbox(label="Password", type="password")
                        btn_add_user = gr.Button("Thêm User", variant="primary")
                        add_user_msg = gr.Markdown("")
                    
                    with gr.Column():
                        gr.Markdown("### Xóa User")
                        del_username = gr.Dropdown(label="Chọn User để xóa", choices=[u["username"] for u in list_users()])
                        btn_del_user = gr.Button("Xóa User", variant="stop")
                        del_user_msg = gr.Markdown("")
                
                # Danh sách users hiện tại
                gr.Markdown("### Danh sách Users hiện tại")
                users_table = gr.Dataframe(
                    headers=["Username", "Password"],
                    value=[[u["username"], u["password"]] for u in list_users()],
                    interactive=False,
                    row_count=10
                )
                refresh_users_btn = gr.Button("🔄 Làm mới danh sách")
                
                # Đơn giản hóa event handlers
                def add_user_simple(username, password):
                    success, msg = add_user(username, password)
                    return msg
                
                def delete_user_simple(username):
                    if not username:
                        return "Vui lòng chọn user để xóa"
                    success, msg = delete_user(username)
                    return msg
                
                def refresh_all():
                    users_list = list_users()
                    return (
                        gr.update(choices=[u["username"] for u in users_list]),
                        gr.update(value=[[u["username"], u["password"]] for u in users_list])
                    )
                
                # Event handlers đơn giản
                btn_add_user.click(
                    add_user_simple,
                    inputs=[new_username, new_password],
                    outputs=[add_user_msg]
                )
                
                btn_del_user.click(
                    delete_user_simple,
                    inputs=[del_username],
                    outputs=[del_user_msg]
                )
                
                refresh_users_btn.click(
                    refresh_all,
                    inputs=None,
                    outputs=[del_username, users_table]
                )
                
                # Auto refresh sau khi thêm/xóa
                btn_add_user.click(
                    refresh_all,
                    inputs=None,
                    outputs=[del_username, users_table]
                )
                
                btn_del_user.click(
                    refresh_all,
                    inputs=None,
                    outputs=[del_username, users_table]
                )

            # Tab 3: Camera Registry
            with gr.Tab("📹 Đăng ký camera"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Thêm Camera mới")
                        cam_name = gr.Textbox(label="Tên Camera")
                        cam_rtsp = gr.Textbox(label="RTSP URL", placeholder="rtsp://user:pass@ip:554/...")
                        btn_add_cam = gr.Button("Thêm Camera", variant="primary")
                        add_cam_msg = gr.Markdown("")
                    
                    with gr.Column():
                        gr.Markdown("### Xóa Camera")
                        del_cam_name = gr.Dropdown(label="Chọn Camera để xóa", choices=list_camera_names())
                        btn_del_cam = gr.Button("Xóa Camera", variant="stop")
                        del_cam_msg = gr.Markdown("")
                
                # Danh sách cameras hiện tại
                gr.Markdown("### Danh sách Cameras đã đăng ký")
                cameras_table = gr.Dataframe(
                    headers=["Tên Camera", "RTSP URL"],
                    value=[[c["name"], c["rtsp"]] for c in list_cameras()],
                    interactive=False,
                    row_count=10
                )
                refresh_cams_btn = gr.Button("🔄 Làm mới danh sách")
                
                # Events
                def add_cam_and_refresh(name, rtsp):
                    result_msg = upsert_camera(name, rtsp)[1]
                    cams_list = list_cameras()
                    return (
                        result_msg,
                        gr.update(choices=list_camera_names()),
                        gr.update(value=[[c["name"], c["rtsp"]] for c in cams_list])
                    )
                
                def delete_cam_and_refresh(name):
                    result_msg = delete_camera(name)[1]
                    cams_list = list_cameras()
                    return (
                        result_msg,
                        gr.update(choices=list_camera_names()),
                        gr.update(value=[[c["name"], c["rtsp"]] for c in cams_list])
                    )
                
                def refresh_cams():
                    cams_list = list_cameras()
                    return (
                        gr.update(choices=list_camera_names()),
                        gr.update(value=[[c["name"], c["rtsp"]] for c in cams_list])
                    )
                
                btn_add_cam.click(
                    add_cam_and_refresh,
                    inputs=[cam_name, cam_rtsp],
                    outputs=[add_cam_msg, del_cam_name, cameras_table]
                )
                btn_del_cam.click(
                    delete_cam_and_refresh,
                    inputs=[del_cam_name],
                    outputs=[del_cam_msg, del_cam_name, cameras_table]
                )
                refresh_cams_btn.click(
                    refresh_cams,
                    inputs=None,
                    outputs=[del_cam_name, cameras_table]
                )

            # Tab 4: Phone Registry
            with gr.Tab("📱 Đăng ký số điện thoại"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Thêm số điện thoại mới")
                        phone_name = gr.Textbox(label="Tên (vd: Bảo vệ)")
                        phone_number = gr.Textbox(label="Số điện thoại (+84... hoặc 0...)")
                        btn_add_phone = gr.Button("Thêm Số", variant="primary")
                        add_phone_msg = gr.Markdown("")
                    
                    with gr.Column():
                        gr.Markdown("### Xóa số điện thoại")
                        del_phone_name = gr.Dropdown(label="Chọn tên để xóa", choices=list_phone_names())
                        btn_del_phone = gr.Button("Xóa Số", variant="stop")
                        del_phone_msg = gr.Markdown("")
                
                # Danh sách phones hiện tại
                gr.Markdown("### Danh sách số điện thoại đã đăng ký")
                phones_table = gr.Dataframe(
                    headers=["Tên", "Số điện thoại"],
                    value=[[name, get_phone_by_name(name)] for name in list_phone_names()],
                    interactive=False,
                    row_count=10
                )
                refresh_phones_btn = gr.Button("🔄 Làm mới danh sách")
                
                # Events
                def add_phone_and_refresh(name, phone):
                    result_msg = upsert_phone(name, phone)[1]
                    phones_list = [(n, get_phone_by_name(n)) for n in list_phone_names()]
                    return (
                        result_msg,
                        gr.update(choices=list_phone_names()),
                        gr.update(value=phones_list)
                    )
                
                def delete_phone_and_refresh(name):
                    result_msg = delete_phone(name)[1]
                    phones_list = [(n, get_phone_by_name(n)) for n in list_phone_names()]
                    return (
                        result_msg,
                        gr.update(choices=list_phone_names()),
                        gr.update(value=phones_list)
                    )
                
                def refresh_phones():
                    phones_list = [(n, get_phone_by_name(n)) for n in list_phone_names()]
                    return (
                        gr.update(choices=list_phone_names()),
                        gr.update(value=phones_list)
                    )
                
                btn_add_phone.click(
                    add_phone_and_refresh,
                    inputs=[phone_name, phone_number],
                    outputs=[add_phone_msg, del_phone_name, phones_table]
                )
                btn_del_phone.click(
                    delete_phone_and_refresh,
                    inputs=[del_phone_name],
                    outputs=[del_phone_msg, del_phone_name, phones_table]
                )
                refresh_phones_btn.click(
                    refresh_phones,
                    inputs=None,
                    outputs=[del_phone_name, phones_table]
                )

            # Tab 5: SMS Log
            with gr.Tab("📱 Nhật ký SMS"):
                with gr.Row():
                    sms_q = gr.Textbox(label="Tìm kiếm", placeholder="từ khoá trong nội dung / số / phản hồi", lines=1)
                    sms_cams = gr.CheckboxGroup(choices=["0","1","2","3"], value=None, label="Cameras")
                    sms_names = gr.Dropdown(label="Người nhận", choices=list_phone_names(), multiselect=True, value=None)
                    sms_status = gr.Dropdown(choices=["any","ok","fail"], value="any", label="Trạng thái")
                
                with gr.Row():
                    sms_from = gr.Textbox(label="Từ ngày (YYYY-MM-DD)")
                    sms_to = gr.Textbox(label="Đến ngày (YYYY-MM-DD)")
                    sms_search = gr.Button("🔍 Tìm kiếm")
                    sms_group = gr.Dropdown(choices=["day","camera","recipient"], value="day", label="Nhóm theo")
                    sms_agg = gr.Button("📊 Thống kê")
                
                # Bảng kết quả
                sms_table = gr.Dataframe(
                    headers=["Thời gian","Camera","Tên","Số","Trạng thái","Nội dung","Phản hồi"],
                    interactive=False,
                    row_count=10,
                    wrap=True
                )
                sms_agg_table = gr.Dataframe(
                    headers=["Nhóm","Tổng","Thành công","Thất bại"],
                    interactive=False,
                    row_count=10
                )
                
                # Functions
                def _search_sms(q, cams, names, st, d1, d2):
                    rows = filter_sms_logs(load_sms_logs(), q, cams, names, st,
                                           (d1 or "").strip() + (" 00:00:00" if d1 else ""),
                                           (d2 or "").strip() + (" 23:59:59" if d2 else ""))
                    table = [[r["ts"], r["cam"], r.get("recipient_name",""), r.get("recipient_phone",""),
                              "OK" if str(r["ok"]) in ("1","True","true") else "FAIL",
                              r.get("text",""), r.get("resp","")] for r in rows[:500]]
                    return table

                def _aggregate_sms(group_by, q, cams, names, st, d1, d2):
                    rows = filter_sms_logs(load_sms_logs(), q, cams, names, st,
                                           (d1 or "").strip() + (" 00:00:00" if d1 else ""),
                                           (d2 or "").strip() + (" 23:59:59" if d2 else ""))
                    agg = aggregate_sms(rows, by=group_by)
                    table = [[a["key"], a["total"], a["ok"], a["fail"]] for a in agg]
                    return table
                
                # Events
                sms_search.click(
                    _search_sms,
                    inputs=[sms_q, sms_cams, sms_names, sms_status, sms_from, sms_to],
                    outputs=[sms_table]
                )
                sms_agg.click(
                    _aggregate_sms,
                    inputs=[sms_group, sms_q, sms_cams, sms_names, sms_status, sms_from, sms_to],
                    outputs=[sms_agg_table]
                )
                sms_names.change(
                    lambda: gr.update(choices=list_phone_names()),
                    inputs=None,
                    outputs=[sms_names]
                )

            # Tab 6: Capture Gallery
            with gr.Tab("🖼️ Thư viện ảnh bằng chứng "):
                with gr.Row():
                    cap_query = gr.Textbox(label="Tìm kiếm ảnh", placeholder="ví dụ: cam0, 2025-01-01, id3…")
                    cap_refresh = gr.Button("Tìm kiếm / Làm mới")
                    cap_dir = gr.Textbox(value="captures", label="Thư viện ảnh bằng chứng")
                
                cap_gallery = gr.Gallery(
                    columns=6,
                    height=400,
                    show_label=True,
                    elem_id="capture_gallery"
                )
                
                # Events
                cap_refresh.click(
                    lambda d, q: search_captures_all(d, q),
                    inputs=[cap_dir, cap_query],
                    outputs=[cap_gallery]
                )

            # Tab: 🚨 Alarm Log
            with gr.Tab("🚨 Nhật ký cảnh báo"):
                with gr.Row():
                    alarm_refresh = gr.Button("🔄 Làm mới")
                alarm_table = gr.Dataframe(
                    headers=["Thời gian","Camera","Bộ đếm","ID theo dõi","Khung hình","Hình ảnh","Còi/đèn","SMS?","Người nhận"],
                    interactive=False, row_count=10, wrap=True
                )
                def _load_alarm():
                    rows = load_alarm_logs()
                    table = [[r["ts"], r["cam"], r["count"], r["track_id"], r["frame"],
                              r.get("capture_file",""), r.get("siren_led",""), r.get("sms_dispatched",""),
                              r.get("sms_recipients","")] for r in rows[:500]]
                    return table
                alarm_refresh.click(_load_alarm, inputs=None, outputs=[alarm_table])

    gr.HTML(f"<div id='brand-footer'>{AUTHOR} • {VERSION}</div>")
    # ---- Login/Logout events ----
    def do_login(u, p, state):
        if verify_user_plain(u, p):
            state["ok"] = True
            state["username"] = (u or "").strip()
            greet = f"Xin chào {state['username']}. Đăng nhập thành công."
            return (gr.update(visible=False), gr.update(visible=True), {"ok": True, "username": state["username"]}, greet, "")
        return (gr.update(visible=True), gr.update(visible=False), {"ok": False, "username": ""}, "", "Sai tài khoản hoặc mật khẩu.")

    def do_logout(state):
        state["ok"] = False
        state["username"] = ""
        return (gr.update(visible=True), gr.update(visible=False), {"ok": False, "username": ""}, "", "")

    btn_login.click(
        do_login,
        inputs=[in_user, in_pass, session_user],
        outputs=[login_panel, app_panel, session_user, hello, login_msg]
    )
    btn_logout.click(
        do_logout,
        inputs=[session_user],
        outputs=[login_panel, app_panel, session_user, hello, login_msg]
    )


try:
    demo.queue(default_concurrency_limit=None)  
except TypeError:
    demo.queue()               

if __name__ == "__main__":
    demo.launch(
        debug=True,
        share=False,               
        server_name="0.0.0.0",     
        server_port=7860,          
        inbrowser=False
    )