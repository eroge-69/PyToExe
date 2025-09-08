import tkinter as tk
from datetime import datetime, time, timedelta

# Specifica orari lavorativi e durata pause
WORK_HOURS = {
    0: [(time(8,30), time(13,0)), (time(14,30), time(18,0))], # Lun
    1: [(time(8,30), time(13,0)), (time(14,30), time(18,0))],
    2: [(time(8,30), time(13,0)), (time(14,30), time(18,0))],
    3: [(time(8,30), time(13,0)), (time(14,30), time(18,0))],
    4: [(time(8,30), time(13,0)), (time(14,30), time(17,0))], # Ven
}
LUNCH_BREAK = (time(13,0), time(14,30))

def is_work_time(now):
    day = now.weekday()
    if day in WORK_HOURS:
        for start, end in WORK_HOURS[day]:
            if start <= now.time() < end:
                return True
    return False

def get_next_work_moment(now):
    # Ritorna il prossimo datetime di inizio fascia lavorativa
    original = now
    for add_days in range(8):
        check_day = (now.weekday() + add_days) % 7
        day = (now + timedelta(days=add_days)).replace(hour=0, minute=0, second=0, microsecond=0)
        if check_day in WORK_HOURS:
            for start, _ in WORK_HOURS[check_day]:
                candidate = day + timedelta(hours=start.hour, minutes=start.minute)
                if candidate > original:
                    return candidate
    return None

def get_time_to_pause(now):
    day = now.weekday()
    if day not in WORK_HOURS:
        # Prossimo giorno lavorativo
        next_start = get_next_work_moment(now)
        return next_start - now if next_start else None

    intervals = WORK_HOURS[day]
    for start, end in intervals:
        if start <= now.time() < end:
            if now.time() < LUNCH_BREAK[0]:
                # Prossima pausa: pranzo
                pause = now.replace(hour=LUNCH_BREAK[0].hour, minute=LUNCH_BREAK[0].minute, second=0, microsecond=0)
                return pause - now
            else:
                # Prossima pausa: fine giornata
                pause = now.replace(hour=end.hour, minute=end.minute, second=0, microsecond=0)
                return pause - now
    # Fuori orario: quanto manca al prossimo istante lavorativo
    next_start = get_next_work_moment(now)
    return next_start - now if next_start else None

def get_time_to_weekend(now):
    # Trova quanti minuti effettivi di lavoro mancano fino a venerdì fine giornata
    left = timedelta()
    cur = now
    count = 0
    while True:
        day = cur.weekday()
        done = (day > 4) or (day == 4 and cur.time() >= time(17,0))
        if done:
            break
        if day in WORK_HOURS:
            for start, end in WORK_HOURS[day]:
                start_dt = cur.replace(hour=start.hour, minute=start.minute, second=0, microsecond=0)
                end_dt = cur.replace(hour=end.hour, minute=end.minute, second=0, microsecond=0)
                # Se siamo in questa fascia o nel futuro
                if cur < end_dt:
                    begin = max(cur, start_dt)
                    stop = end_dt
                    if (day == 4) and (end == time(17,0)):
                        # Taglia a venerdì alle 17:00
                        stop = cur.replace(hour=17, minute=0, second=0, microsecond=0)
                    if begin < stop:
                        left += stop - begin
                    cur = stop
        # Avanza al giorno dopo
        cur = (cur + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return left

def snap_blocks(td):
    minutes = int(td.total_seconds() // 60)
    snaps = -(-minutes // 15) # Arrotonda per eccesso
    return max(0, snaps)

def format_td(td):
    total_seconds = int(td.total_seconds())
    if total_seconds < 0:
        return "00:00"
    hours, rem = divmod(total_seconds, 3600)
    minutes = rem // 60
    return f"{hours:02}:{minutes:02}"

def update_labels():
    now = datetime.now()
    work = is_work_time(now)
    if not work:
        # Blocco valori alla prossima fascia lavorativa
        next_start = get_next_work_moment(now)
        tmp_now = next_start if next_start else now
    else:
        tmp_now = now

    ttp = get_time_to_pause(tmp_now)
    ttw = get_time_to_weekend(tmp_now)

    lbl_snap_pause.config(text=f"SNAP alla pausa: {snap_blocks(ttp)}")
    lbl_snap_we.config(text=f"SNAP al WE: {snap_blocks(ttw)}")
    lbl_time_pause.config(text=f"Tempo alla pausa: {format_td(ttp)}")
    lbl_time_we.config(text=f"Tempo al WE: {format_td(ttw)}")

    root.after(1000, update_labels)

root = tk.Tk()
root.title("SNAP - Time Counter")
root.geometry("320x150")

lbl_snap_pause = tk.Label(root, text="", font=("Arial", 16))
lbl_snap_pause.pack(pady=5)

lbl_snap_we = tk.Label(root, text="", font=("Arial", 16))
lbl_snap_we.pack(pady=5)

lbl_time_pause = tk.Label(root, text="", font=("Arial", 16))
lbl_time_pause.pack(pady=5)

lbl_time_we = tk.Label(root, text="", font=("Arial", 16))
lbl_time_we.pack(pady=5)

update_labels()
root.mainloop()