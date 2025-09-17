import os
from ctypes import byref, c_int16, c_int32, sizeof, Structure, c_uint16
from time import sleep, time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from picosdk.ps2000 import ps2000
from picosdk.functions import assert_pico2000_ok
from picosdk.PicoDeviceEnums import picoEnum

# ---------------- PicoScope helpers ----------------
class TriggerConditions(Structure):
    _fields_ = [('channelA', c_int32), ('channelB', c_int32),
                ('channelC', c_int32), ('channelD', c_int32),
                ('external', c_int32), ('pulseWidthQualifier', c_int32)]
class PwqConditions(Structure):
    _fields_ = [('channelA', c_int32), ('channelB', c_int32),
                ('channelC', c_int32), ('channelD', c_int32),
                ('external', c_int32)]
class TriggerChannelProperties(Structure):
    _fields_ = [("thresholdMajor", c_int16), ("thresholdMinor", c_int16),
                ("hysteresis", c_uint16), ("channel", c_int16),
                ("thresholdMode", c_int16)]

THRESHOLD_DIRECTION = {'PS2000_ADV_RISING': 2, 'PS2000_ADV_NONE': 2, 'PS2000_ABOVE': 0}
PRESAMPLE = 20.0
OVERSAMPLING = 1

def get_timebase(device, wanted_time_interval, samples):
    tb = 1
    t_int = c_int32()
    t_units = c_int16()
    max_samples = c_int32()
    while ps2000.ps2000_get_timebase(device.handle, tb, samples,
                                     byref(t_int), byref(t_units), 1,
                                     byref(max_samples)) == 0 or t_int.value < wanted_time_interval:
        tb += 1
        if tb.bit_length() > sizeof(c_int16) * 8:
            raise RuntimeError("No suitable timebase found")
    return tb

def count_pulses(device, threshold_mv, runtime_sec, samples):
    trig_cond = TriggerConditions(1,0,0,0,0,1)
    assert_pico2000_ok(ps2000.ps2000SetAdvTriggerChannelConditions(device.handle, byref(trig_cond),1))
    delay = int(samples * (1 - PRESAMPLE/100))
    assert_pico2000_ok(ps2000.ps2000SetAdvTriggerDelay(device.handle,0,delay))
    assert_pico2000_ok(ps2000.ps2000SetAdvTriggerChannelDirections(
        device.handle,
        THRESHOLD_DIRECTION['PS2000_ADV_RISING'],
        THRESHOLD_DIRECTION['PS2000_ADV_NONE'],
        THRESHOLD_DIRECTION['PS2000_ADV_NONE'],
        THRESHOLD_DIRECTION['PS2000_ADV_NONE'],
        THRESHOLD_DIRECTION['PS2000_ADV_NONE']))
    adc_threshold = int((threshold_mv/100.0)*32767)
    trig_props = TriggerChannelProperties(
        adc_threshold,0,100,
        ps2000.PS2000_CHANNEL['PS2000_CHANNEL_A'],
        picoEnum.PICO_THRESHOLD_MODE['PICO_LEVEL'])
    assert_pico2000_ok(ps2000.ps2000SetAdvTriggerChannelProperties(
        device.handle, byref(trig_props),1,0))
    pwq_cond = PwqConditions(1,0,0,0,0)
    assert_pico2000_ok(ps2000.ps2000SetPulseWidthQualifier(
        device.handle, byref(pwq_cond),1,
        THRESHOLD_DIRECTION['PS2000_ABOVE'], 100, 0,
        picoEnum.PICO_PULSE_WIDTH_TYPE['PICO_PW_TYPE_GREATER_THAN']))

    tb = get_timebase(device, 100, samples)
    buffer_a = (c_int16 * samples)()
    times = (c_int32 * samples)()
    count = 0
    end_time = time() + runtime_sec
    while time() < end_time:
        assert_pico2000_ok(ps2000.ps2000_run_block(device.handle, samples, tb, OVERSAMPLING, None))
        while ps2000.ps2000_ready(device.handle) == 0:
            sleep(0.001)
        if ps2000.ps2000_get_times_and_values(
            device.handle, byref(times), byref(buffer_a),
            None, None, None, None, 2, samples):
            count += 1
    ps2000.ps2000_stop(device.handle)
    return count

# ---------------- Tkinter App ----------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KRISHNA")
        self.state("zoomed")
        self.attributes("-fullscreen", True)
        self.configure(bg="#e8f0fe")
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.mode = tk.StringVar(value="")
        self.inputs = {}
        self._build_start_screen()

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    # -------- Start Screen --------
    def _build_start_screen(self):
        self.clear_screen()
        tk.Label(self, text="Select Measurement Mode",
                 font=("Helvetica", 26, "bold"),
                 bg="#4a90e2", fg="white", pady=30).pack(fill="x")
        ttk.Button(self, text="Background",
                   command=lambda: self.build_input_screen("Background"),
                   width=25).pack(pady=60)
        ttk.Button(self, text="Source (Unknown)",
                   command=lambda: self.build_input_screen("Source"),
                   width=25).pack(pady=10)

    # -------- Input Screen --------
    def build_input_screen(self, mode):
        self.mode.set(mode)
        self.clear_screen()
        tk.Label(self, text=f"{mode} Measurement Settings",
                 font=("Helvetica", 24, "bold"),
                 bg="#4a90e2", fg="white", pady=20).pack(fill="x")
        frame = tk.Frame(self, bg="#e8f0fe")
        frame.pack(pady=30)

        fields = ["Threshold Voltage (mV)", "Applied Voltage (V)",
                  "Counting Runtime (s)", "Number of Cycles"]
        if mode == "Source":
            fields += ["Source Strength", "Distance from Detector (cm)"]

        self.inputs = {}
        for i, field in enumerate(fields):
            tk.Label(frame, text=field, bg="#e8f0fe",
                     font=("Helvetica", 14)).grid(row=i, column=0, sticky="e", padx=10, pady=8)
            ent = ttk.Entry(frame, width=25)
            ent.grid(row=i, column=1, padx=10, pady=8)
            self.inputs[field] = ent

        nav_frame = tk.Frame(self, bg="#e8f0fe")
        nav_frame.pack(pady=30)
        ttk.Button(nav_frame, text="Back", command=self._build_start_screen).grid(row=0, column=0, padx=20)
        ttk.Button(nav_frame, text="Start Counting", command=self.start_counting).grid(row=0, column=1, padx=20)

    # -------- Counting / Progress Screen --------
    def start_counting(self):
        try:
            threshold_mv = float(self.inputs["Threshold Voltage (mV)"].get())
            applied_voltage = float(self.inputs["Applied Voltage (V)"].get())
            runtime = float(self.inputs["Counting Runtime (s)"].get())
            cycles = int(self.inputs["Number of Cycles"].get())
        except Exception:
            messagebox.showerror("Invalid Input", "Please fill all numeric fields correctly.")
            return

        extras = {}
        if self.mode.get() == "Source":
            extras["Source Strength"] = self.inputs["Source Strength"].get()
            extras["Distance from Detector (cm)"] = self.inputs["Distance from Detector (cm)"].get()

        folder = filedialog.askdirectory(title="Select Folder to Save Results")
        if not folder:
            return

        self.clear_screen()
        tk.Label(self, text="Counting in Progress...",
                 font=("Helvetica", 24, "bold"),
                 bg="#4a90e2", fg="white", pady=20).pack(fill="x")

        progress = tk.Text(self, height=25, width=80, bg="black", fg="lime",
                           font=("Courier", 14))
        progress.pack(pady=20)

        self.update()

        samples = 1024
        results = []
        with ps2000.open_unit() as dev:
            assert_pico2000_ok(ps2000.ps2000_set_channel(
                dev.handle,
                picoEnum.PICO_CHANNEL['PICO_CHANNEL_A'],
                True,
                picoEnum.PICO_COUPLING['PICO_DC'],
                ps2000.PS2000_VOLTAGE_RANGE['PS2000_100MV']
            ))
            for i in range(1, cycles+1):
                c = count_pulses(dev, threshold_mv, runtime, samples)
                results.append(c)
                progress.insert("end", f"Cycle {i}: {c} pulses\n")
                progress.see("end")
                self.update()

        total = sum(results)
        progress.insert("end", f"\nTotal over {cycles} cycles: {total}\n")

        fname = os.path.join(folder, f"{self.mode.get()}_results.txt")
        with open(fname, "w") as f:
            f.write(f"Mode: {self.mode.get()}\n")
            f.write(f"Threshold Voltage (mV): {threshold_mv}\n")
            f.write(f"Applied Voltage (V): {applied_voltage}\n")
            f.write(f"Counting Runtime (s): {runtime}\n")
            f.write(f"Number of Cycles: {cycles}\n")
            for k,v in extras.items():
                f.write(f"{k}: {v}\n")
            f.write("\nCycle counts:\n")
            for i,c in enumerate(results,1):
                f.write(f"Cycle {i}: {c}\n")
            f.write(f"\nTotal: {total}\n")

        # Navigation after finish
        nav = tk.Frame(self, bg="#e8f0fe")
        nav.pack(pady=15)
        ttk.Button(nav, text="Back to Start", command=self._build_start_screen).pack()

        messagebox.showinfo("Done", f"Results saved to:\n{fname}")

# ---------------- Main ----------------
if __name__ == "__main__":
    App().mainloop()
