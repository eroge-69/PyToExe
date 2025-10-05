import wx
import subprocess
import sys
import os
import threading

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Nakshatra Launcher", size=(700, 500))

        panel = wx.Panel(self)
        hbox = wx.BoxSizer(wx.HORIZONTAL)  # Horizontal: left (buttons) + center (output)

        # --- LEFT SIDE BUTTONS ---
        vbox_buttons = wx.BoxSizer(wx.VERTICAL)

        # KP Calculations button
        btn_kp = wx.Button(panel, label="KP Calculations", size=(150, 40))
        btn_kp.Bind(wx.EVT_BUTTON, lambda evt: self.run_script("Run_file_calcution all.py"))
        vbox_buttons.Add(btn_kp, 0, wx.ALL, 5)

        # Nakshatra Data button
        btn_nakshatra = wx.Button(panel, label="Results_moon_star_lord", size=(150, 40))
        btn_nakshatra.Bind(wx.EVT_BUTTON, lambda evt: self.run_script("gui_results_moon_star_lord.py"))
        vbox_buttons.Add(btn_nakshatra, 0, wx.ALL, 5)

        # Nakshatra Data button
        btn_nakshatra = wx.Button(panel, label="Nakshatra Data", size=(150, 40))
        btn_nakshatra.Bind(wx.EVT_BUTTON, lambda evt: self.run_script("gui_nakshatra_nadi_data.py"))
        vbox_buttons.Add(btn_nakshatra, 0, wx.ALL, 5)

        hbox.Add(vbox_buttons, 0, wx.EXPAND | wx.ALL, 10)

        # --- CENTER AREA: OUTPUT + PROGRESS ---
        vbox_center = wx.BoxSizer(wx.VERTICAL)

        # Progress Bar
        self.gauge = wx.Gauge(panel, range=100, size=(400, 25), style=wx.GA_HORIZONTAL)
        vbox_center.Add(self.gauge, 0, wx.ALL | wx.CENTER, 5)

        # Output Text
        self.output_ctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(400, 350))
        vbox_center.Add(self.output_ctrl, 1, wx.ALL | wx.EXPAND, 5)

        hbox.Add(vbox_center, 1, wx.EXPAND | wx.ALL, 10)

        panel.SetSizer(hbox)
        self.Show()

    def run_script(self, filename):
        """Run a Python file in background thread with progress + logs"""
        script_path = os.path.join(os.getcwd(), filename)
        if not os.path.exists(script_path):
            wx.MessageBox(f"File not found:\n{script_path}", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Reset UI
        self.output_ctrl.Clear()
        self.gauge.SetValue(0)

        # Threading so GUI won’t freeze
        def worker():
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # Simulate progress bar and capture output
            progress = 0
            for line in iter(process.stdout.readline, ''):
                wx.CallAfter(self.output_ctrl.AppendText, line)
                progress = min(progress + 5, 95)
                wx.CallAfter(self.gauge.SetValue, progress)

            process.stdout.close()
            process.wait()

            # Finish progress
            wx.CallAfter(self.gauge.SetValue, 100)

        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()
