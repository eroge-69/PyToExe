import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy.fft import fft, fftfreq
from scipy.signal import square, sawtooth, chirp

class WaveVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wave Visualizer")

        self.fig = None
        self.ax_time = None
        self.ax_freq = None
        self.canvas = None
        self.toolbar = None

        self.create_widgets()
        self.setup_plot()
        self.update_plot() # Call update_plot after setup_plot

    def create_widgets(self):
        # Use PanedWindow for resizable sidebar
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Control Frame (left pane)
        control_frame = ttk.LabelFrame(self.paned_window, text="Wave Parameters")
        self.paned_window.add(control_frame, weight=1)

        # Plot Frame (right pane)
        self.plot_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.plot_frame, weight=3)

        # Wave Type Selection
        ttk.Label(control_frame, text="Wave Type:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.wave_type = ttk.Combobox(control_frame, 
                                       values=["Analog - Sine Wave", "Analog - Cosine Wave", "Analog - Sawtooth Wave", "Analog - Triangle Wave", "Analog - Composite Sine Wave", 
                                                 "Analog - Gaussian Pulse", "Analog - Composite Gaussian Pulses",
                                                 "Digital - Square Wave", "Digital - Pulse (Single)", "Digital - PWM (Pulse Width Modulation)", "Digital - Composite Square Waves", "Digital - Random Bitstream"],
                                       state="readonly")
        self.wave_type.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.wave_type.set("Analog - Sine Wave") # Default to Analog - Sine
        self.wave_type.bind("<<ComboboxSelected>>", self.on_wave_type_change)

        # Amplitude
        ttk.Label(control_frame, text="Amplitude:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.amplitude_var = tk.StringVar(value="1.0")
        self.amplitude_entry = ttk.Entry(control_frame, textvariable=self.amplitude_var)
        self.amplitude_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.amplitude_var.trace_add("write", self.update_plot_callback)

        # Frequency 1
        ttk.Label(control_frame, text="Frequency 1 (Hz):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.frequency1_var = tk.StringVar(value="5.0")
        self.frequency1_entry = ttk.Entry(control_frame, textvariable=self.frequency1_var)
        self.frequency1_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        self.frequency1_var.trace_add("write", self.update_plot_callback)

        # Frequency 2 (for composite waves)
        ttk.Label(control_frame, text="Frequency 2 (Hz):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.frequency2_var = tk.StringVar(value="15.0")
        self.frequency2_entry = ttk.Entry(control_frame, textvariable=self.frequency2_var)
        self.frequency2_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        self.frequency2_var.trace_add("write", self.update_plot_callback)

        # Phase Offset (in Degrees)
        ttk.Label(control_frame, text="Phase Offset (deg):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.phase_var = tk.StringVar(value="0.0")
        self.phase_entry = ttk.Entry(control_frame, textvariable=self.phase_var)
        self.phase_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.EW)
        self.phase_var.trace_add("write", self.update_plot_callback)

        # Duty Cycle (for digital square/PWM/sawtooth)
        ttk.Label(control_frame, text="Duty Cycle (0-1):").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        self.duty_cycle_var = tk.StringVar(value="0.5")
        self.duty_cycle_entry = ttk.Entry(control_frame, textvariable=self.duty_cycle_var)
        self.duty_cycle_entry.grid(row=5, column=1, padx=5, pady=5, sticky=tk.EW)
        self.duty_cycle_var.trace_add("write", self.update_plot_callback)

        # Duration
        ttk.Label(control_frame, text="Period (s):").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
        self.duration_var = tk.StringVar(value="2.0")
        self.duration_entry = ttk.Entry(control_frame, textvariable=self.duration_var)
        self.duration_entry.grid(row=6, column=1, padx=5, pady=5, sticky=tk.EW)
        self.duration_var.trace_add("write", self.update_plot_callback)

        # Sampling Rate
        ttk.Label(control_frame, text="Sampling Rate (Hz):").grid(row=7, column=0, padx=5, pady=5, sticky=tk.W)
        self.sampling_rate_var = tk.StringVar(value="1000")
        self.sampling_rate_entry = ttk.Entry(control_frame, textvariable=self.sampling_rate_var)
        self.sampling_rate_entry.grid(row=7, column=1, padx=5, pady=5, sticky=tk.EW)
        self.sampling_rate_var.trace_add("write", self.update_plot_callback)

        # View Customization Controls
        view_frame = ttk.LabelFrame(control_frame, text="View Controls")
        view_frame.grid(row=8, column=0, columnspan=2, padx=5, pady=10, sticky=tk.EW)

        self.grid_var = tk.BooleanVar(value=True)
        self.grid_check = ttk.Checkbutton(view_frame, text="Show Grid", variable=self.grid_var, command=self.update_plot)
        self.grid_check.grid(row=0, column=0, columnspan=2, padx=2, pady=2, sticky=tk.W)

        # Initial state of controls
        self.on_wave_type_change()

    def setup_plot(self):
        if self.canvas:
            self.canvas_widget.destroy()
            if self.toolbar: # Destroy old toolbar if it exists
                self.toolbar.destroy()
            plt.close(self.fig)

        self.fig, (self.ax_time, self.ax_freq) = plt.subplots(2, 1, figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame) # Attach to plot_frame
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Add Matplotlib Navigation Toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame) # Attach to plot_frame
        self.toolbar.update()
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)

    def on_wave_type_change(self, *args):
        selected_type = self.wave_type.get()
        # Reset visibility of all controls
        self.frequency2_entry.config(state=tk.DISABLED)
        self.phase_entry.config(state=tk.DISABLED)
        self.duty_cycle_entry.config(state=tk.DISABLED)

        if selected_type in ["Analog - Sine Wave", "Analog - Cosine Wave", "Analog - Sawtooth Wave", "Analog - Triangle Wave"]:
            self.phase_entry.config(state=tk.NORMAL)
            if selected_type in ["Analog - Sawtooth Wave", "Analog - Triangle Wave"]:
                self.duty_cycle_entry.config(state=tk.NORMAL) # Duty cycle for sawtooth/triangle asymmetry
        elif selected_type == "Analog - Composite Sine Wave":
            self.frequency2_entry.config(state=tk.NORMAL)
            self.phase_entry.config(state=tk.NORMAL)
        elif selected_type == "Analog - Gaussian Pulse":
            self.phase_entry.config(state=tk.NORMAL) # For std_dev control
        elif selected_type == "Analog - Composite Gaussian Pulses":
            self.frequency2_entry.config(state=tk.NORMAL) # For second pulse std_dev
            self.phase_entry.config(state=tk.NORMAL) # For first pulse std_dev
        elif selected_type in ["Digital - Square Wave", "Digital - PWM (Pulse Width Modulation)"]:
            self.duty_cycle_entry.config(state=tk.NORMAL)
        elif selected_type == "Digital - Composite Square Waves":
            self.frequency2_entry.config(state=tk.NORMAL)
            self.duty_cycle_entry.config(state=tk.NORMAL)
        elif selected_type in ["Digital - Pulse (Single)", "Digital - Random Bitstream"]:
            pass # No specific extra controls for now
        
        self.update_plot()

    def update_plot_callback(self, *args):
        self.update_plot()

    def get_numeric_value(self, var, default_value, value_type=float):
        try:
            val = var.get()
            if val == "":
                return default_value
            return value_type(val)
        except ValueError:
            return default_value

    def update_plot(self):
        try:
            amplitude = self.get_numeric_value(self.amplitude_var, 1.0)
            frequency1 = self.get_numeric_value(self.frequency1_var, 5.0)
            frequency2 = self.get_numeric_value(self.frequency2_var, 15.0)
            phase_degrees = self.get_numeric_value(self.phase_var, 0.0) # Get phase in degrees
            phase_radians = np.deg2rad(phase_degrees) # Convert to radians
            duty_cycle = self.get_numeric_value(self.duty_cycle_var, 0.5)
            duration = self.get_numeric_value(self.duration_var, 2.0)
            sampling_rate = self.get_numeric_value(self.sampling_rate_var, 1000, int)

            # Input validation for critical parameters
            if sampling_rate <= 0 or duration <= 0:
                print("Input Error: Sampling rate and duration must be positive.")
                return
            if sampling_rate * duration > 1e6: # Limit array size to prevent memory errors
                print(f"Input Error: (Sampling Rate * Duration) is too large ({sampling_rate * duration}). Please reduce sampling rate or duration.")
                return

            t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
            N = len(t)
            xf = fftfreq(N, 1 / sampling_rate)[:N//2]

            selected_type = self.wave_type.get()
            time_signal = np.array([])
            
            # Calculate parameters for display
            period = 1 / frequency1 if frequency1 != 0 else np.inf
            wavelength = "N/A" # Wavelength is context-dependent (speed of wave needed)

            if selected_type == "Analog - Sine Wave":
                time_signal = amplitude * np.sin(2 * np.pi * frequency1 * t + phase_radians)
            elif selected_type == "Analog - Cosine Wave":
                time_signal = amplitude * np.cos(2 * np.pi * frequency1 * t + phase_radians)
            elif selected_type == "Analog - Sawtooth Wave":
                time_signal = amplitude * sawtooth(2 * np.pi * frequency1 * t + phase_radians, width=duty_cycle)
            elif selected_type == "Analog - Triangle Wave":
                time_signal = amplitude * sawtooth(2 * np.pi * frequency1 * t + phase_radians, width=0.5)
            elif selected_type == "Analog - Composite Sine Wave":
                time_signal = amplitude * np.sin(2 * np.pi * frequency1 * t + phase_radians) + \
                              (amplitude/2) * np.sin(2 * np.pi * frequency2 * t + phase_radians + np.pi/4)
            elif selected_type == "Analog - Gaussian Pulse":
                center = duration / 2.0
                std_dev = duration / (phase_degrees / 10 + 10) # Use phase_degrees to control width, avoid division by zero
                time_signal = amplitude * np.exp(-0.5 * ((t - center) / std_dev)**2)
                period = "N/A"; frequency1 = "N/A"; phase_degrees = "N/A"
            elif selected_type == "Analog - Composite Gaussian Pulses":
                center1 = duration / 3.0
                std_dev1 = duration / (phase_degrees / 10 + 10) # Use phase_degrees to control width
                pulse1 = amplitude * np.exp(-0.5 * ((t - center1) / std_dev1)**2)
                
                center2 = 2 * duration / 3.0
                std_dev2 = duration / (frequency2 / 10 + 10) # Use freq2 to control width of second pulse
                pulse2 = (amplitude/2) * np.exp(-0.5 * ((t - center2) / std_dev2)**2)
                time_signal = pulse1 + pulse2
                period = "N/A"; frequency1 = "N/A"; phase_degrees = "N/A"
            elif selected_type == "Digital - Square Wave":
                time_signal = amplitude * square(2 * np.pi * frequency1 * t, duty=duty_cycle)
                time_signal = (time_signal + amplitude) / (2 * amplitude) # Normalize to 0 and 1 if amplitude is not 1
                time_signal = np.round(time_signal) # Make it strictly 0 or 1
            elif selected_type == "Digital - Pulse (Single)":
                time_signal = np.zeros_like(t)
                start_idx = int(0.25 * N)
                end_idx = int(0.75 * N)
                time_signal[start_idx:end_idx] = amplitude
                period = "N/A"; frequency1 = "N/A"; phase_degrees = "N/A"
            elif selected_type == "Digital - PWM (Pulse Width Modulation)":
                time_signal = amplitude * square(2 * np.pi * frequency1 * t, duty=duty_cycle)
                time_signal = (time_signal + amplitude) / (2 * amplitude) # Normalize to 0 and 1
                time_signal = np.round(time_signal) # Make it strictly 0 or 1
            elif selected_type == "Digital - Composite Square Waves":
                square_wave1 = amplitude * square(2 * np.pi * frequency1 * t, duty=duty_cycle)
                square_wave2 = (amplitude/2) * square(2 * np.pi * frequency2 * t, duty=0.25) # Second wave with fixed duty cycle
                time_signal = np.round((square_wave1 + square_wave2 + amplitude) / (2 * amplitude)) # Normalize and round
            elif selected_type == "Digital - Random Bitstream":
                np.random.seed(int(sampling_rate * duration)) # Seed for reproducibility based on params
                bits_per_second = frequency1 if frequency1 > 0 else 1 # Use freq1 as bit rate
                num_bits = int(duration * bits_per_second)
                random_bits = np.random.randint(0, 2, size=num_bits)
                samples_per_bit = int(sampling_rate / bits_per_second)
                time_signal = np.repeat(random_bits, samples_per_bit)[:N]
                if len(time_signal) < N:
                    time_signal = np.pad(time_signal, (0, N - len(time_signal)), 'edge')
                time_signal = time_signal * amplitude # Apply amplitude
                period = "N/A"; frequency1 = "N/A"; phase_degrees = "N/A"
            
            if time_signal.size == 0:
                return

            # Time Domain Plot
            self.ax_time.clear()
            if "Digital" in selected_type:
                self.ax_time.step(t, time_signal, where='post')
            else:
                self.ax_time.plot(t, time_signal)

            self.ax_time.set_title(f"Time Domain ({selected_type})")
            self.ax_time.set_xlabel("Time (s)")
            self.ax_time.set_ylabel("Amplitude")
            self.ax_time.grid(self.grid_var.get())

            # Adaptive Y-axis scaling with padding
            min_val = np.min(time_signal)
            max_val = np.max(time_signal)
            padding = (max_val - min_val) * 0.1 if (max_val - min_val) > 0 else 0.1
            self.ax_time.set_ylim(min_val - padding, max_val + padding)
            self.ax_time.set_xlim(0, duration)

            # Display parameters on plot
            param_text = f"Amp: {amplitude:.2f}\nFreq: {frequency1:.2f} Hz\nPhase: {phase_degrees:.1f} deg\nPeriod: {period:.2f} s"
            if selected_type.startswith("Analog - Nonperiodic") or selected_type.startswith("Digital - Random"):
                param_text = f"Amp: {amplitude:.2f}\nNon-periodic"
            elif selected_type.startswith("Digital - Pulse"):
                param_text = f"Amp: {amplitude:.2f}\nPulse"

            self.ax_time.text(0.02, 0.98, param_text, transform=self.ax_time.transAxes, fontsize=9, verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))

            # Frequency Domain Plot
            yf = fft(time_signal)
            self.ax_freq.clear()
            self.ax_freq.plot(xf, 2.0/N * np.abs(yf[0:N//2]))
            self.ax_freq.set_title(f"Frequency Domain ({selected_type})")
            self.ax_freq.set_xlabel("Frequency (Hz)")
            self.ax_freq.set_ylabel("Magnitude")
            self.ax_freq.grid(self.grid_var.get())

            self.fig.tight_layout()
            self.canvas.draw()

        except Exception as e:
            print(f"An error occurred during plot update: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WaveVisualizerApp(root)
    root.mainloop()

