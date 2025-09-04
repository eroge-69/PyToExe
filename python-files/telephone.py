import tkinter as tk
from tkinter import messagebox
import threading, time, os, datetime

APP_TITLE = "Tiny Phone Simulator"
LOGFILE = os.path.join(os.path.expanduser("~"), "tiny_phone_log.txt")

class TinyPhone(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.resizable(False, False)
        self.configure(bg='#0b0f14')

        # state
        self.number = tk.StringVar(value='')
        self.status = tk.StringVar(value='Ready')
        self.calling = False
        self.call_start = None
        self.call_timer_job = None
        self.ringing = False
        self.ring_thread = None
        self._build_ui()

        # keyboard bindings
        self.bind_all('<Key>', self._on_key)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        pad = 8
        disp_frame = tk.Frame(self, bg='#001219', bd=2, relief='ridge')
        disp_frame.grid(row=0, column=0, padx=pad, pady=pad, sticky='nsew')
        self.display_label = tk.Label(disp_frame, textvariable=self.number,
                                      width=22, height=2, font=('Courier New', 20, 'bold'),
                                      bg='#011627', fg='#7bedff', anchor='e')
        self.display_label.pack(padx=6, pady=6)

        status_label = tk.Label(disp_frame, textvariable=self.status, font=('Courier New', 10),
                                bg='#001219', fg='#c7f9ff', anchor='w')
        status_label.pack(fill='x', padx=6, pady=(0,6))

        keys = [
            ['1','2','3'],
            ['4','5','6'],
            ['7','8','9'],
            ['*','0','#']
        ]
        kframe = tk.Frame(self, bg='#071422')
        kframe.grid(row=1, column=0, padx=pad, pady=(0,pad))

        btncfg = dict(width=6, height=2, font=('Arial', 14, 'bold'),
                      bg='#0b2833', fg='#dff6ff', activebackground='#114b5f')

        for r, row in enumerate(keys):
            for c, key in enumerate(row):
                b = tk.Button(kframe, text=key, command=lambda k=key: self._press_key(k), **btncfg)
                b.grid(row=r, column=c, padx=6, pady=6)

        action_frame = tk.Frame(self, bg='#071422')
        action_frame.grid(row=2, column=0, padx=pad, pady=(0,pad), sticky='ew')

        call_btn = tk.Button(action_frame, text='Call', command=self._call, bg='#093b2b', fg='#d1ffd6',
                             width=8, height=1, font=('Arial',12,'bold'))
        end_btn = tk.Button(action_frame, text='End', command=self._end_call, bg='#4b0f0f', fg='#ffd6d6',
                             width=8, height=1, font=('Arial',12,'bold'))
        clear_btn = tk.Button(action_frame, text='Clear', command=self._clear, bg='#183a47', fg='#cfeff6',
                              width=8, height=1, font=('Arial',12,'bold'))

        call_btn.pack(side='left', padx=12, pady=6)
        end_btn.pack(side='left', padx=12, pady=6)
        clear_btn.pack(side='left', padx=12, pady=6)

        footer = tk.Label(self, text='Keys: 0-9 * #  •  Enter=Call  •  Esc=End', font=('Arial',9),
                          bg='#0b0f14', fg='#7fb6c8')
        footer.grid(row=3, column=0, pady=(0,8))

    def _press_key(self, k):
        if self.calling:
            return
        cur = self.number.get()
        if len(cur) >= 24:
            return
        self.number.set(cur + k)
        self._flash_display()

    def _on_key(self, event):
        k = event.keysym
        if k in ('Return', 'KP_Enter'):
            self._call()
        elif k == 'Escape':
            self._end_call()
        elif k in ('BackSpace',):
            self._backspace()
        else:
            ch = event.char
            if ch and ch in '0123456789*#':
                self._press_key(ch)

    def _backspace(self):
        if self.calling: return
        cur = self.number.get()
        self.number.set(cur[:-1])
        self._flash_display()

    def _clear(self):
        if self.calling: return
        self.number.set('')
        self.status.set('Ready')

    def _call(self):
        if self.calling:
            return
        num = self.number.get().strip()
        if not num:
            self.status.set('Enter number')
            return
        self.status.set('Dialing...')
        self.ringing = True
        self.ring_thread = threading.Thread(target=self._ring_loop, daemon=True)
        self.ring_thread.start()
        self.after(2000, self._connected)

    def _ring_loop(self):
        while self.ringing:
            try:
                self.bell()
            except Exception:
                pass
            time.sleep(1.2)

    def _connected(self):
        if not self.ringing: return
        self.ringing = False
        self.calling = True
        self.call_start = time.time()
        self.status.set('Connected')
        self._start_call_timer()
        self._log_event('CALL_START', self.number.get())

    def _start_call_timer(self):
        def tick():
            if not self.calling:
                return
            elapsed = int(time.time() - self.call_start)
            m, s = divmod(elapsed, 60)
            self.status.set('In call  %02d:%02d' % (m, s))
            self.call_timer_job = self.after(1000, tick)
        tick()

    def _end_call(self):
        if self.ringing:
            self.ringing = False
        if not self.calling and not self.ringing:
            self.status.set('Ready')
            return
        if self.call_timer_job:
            self.after_cancel(self.call_timer_job)
            self.call_timer_job = None
        if self.calling:
            duration = int(time.time() - self.call_start)
            self._log_event('CALL_END', '%s DURATION=%ds' % (self.number.get(), duration))
        self.calling = False
        self.call_start = None
        self.status.set('Ended')
        self.after(800, lambda: self.number.set(''))

    def _flash_display(self):
        lbl = self.display_label
        orig = lbl['bg']
        lbl.config(bg='#052533')
        self.after(120, lambda: lbl.config(bg=orig))

    def _log_event(self, tag, data):
        ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        try:
            with open(LOGFILE, 'a') as f:
                f.write('%s %s %s\n' % (ts, tag, data))
        except Exception:
            pass

    def _on_close(self):
        self.ringing = False
        self.calling = False
        if self.call_timer_job:
            try: self.after_cancel(self.call_timer_job)
            except Exception: pass
        self.destroy()

def main():
    app = TinyPhone()
    app.mainloop()

if __name__ == '__main__':
    main()