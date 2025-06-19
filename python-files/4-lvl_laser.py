import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
import numpy as np
from scipy.integrate import solve_ivp

# Fixed parameters
h = 6.626e-34    # Planck constant (J·s)
c = 3e8          # Speed of light (m/s)
lambda_laser = 1064e-9  # Wavelength (m)
v = c / lambda_laser  # Transition frequency (Hz)
hv = h * v       # Photon energy (J)
sigma = 2.8e-23    # Cross-section (m²)
B32 = sigma / hv  # m³/(J·s)
k_B = 1.381e-23       # J/K
T = 300             # K

A32 = ((8 * np.pi * hv**3) / c**3) * B32

class LaserSimulator:
    def __init__(self):
        self.fig = plt.figure(figsize=(20, 8))
        plt.subplots_adjust(left=0.1, bottom=0.4, top=0.9, hspace=0.4)
        
        # Create axes for plots
        self.ax1 = plt.subplot2grid((3, 1), (0, 0))
        self.ax2 = plt.subplot2grid((3, 1), (1, 0))
        self.ax3 = plt.subplot2grid((3, 1), (2, 0))
        
        # Initialize with empty plots
        self.line1, = self.ax1.plot([], [], lw=2)
        self.line2, = self.ax2.plot([], [], lw=2)
        self.line3, = self.ax3.plot([], [], lw=2)
        
        # Add radio buttons for simulation type
        self.rax = plt.axes([0.02, 0.92, 0.25, 0.07])
        self.radio = RadioButtons(self.rax, ('Cavity', 'Stimulated Emission', 'Without Stimulated Emission'))
        
        # Add parameter sliders
        self.axcolor = 'green'
        self.slider_axes = [
            plt.axes([0.25, 0.25, 0.65, 0.03], facecolor=self.axcolor),
            plt.axes([0.25, 0.20, 0.65, 0.03], facecolor=self.axcolor),
            plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=self.axcolor),
            plt.axes([0.25, 0.10, 0.65, 0.03], facecolor=self.axcolor),
            plt.axes([0.25, 0.05, 0.65, 0.03], facecolor=self.axcolor)
        ]
        
        self.sliders = [
            Slider(ax=ax, label=label, valmin=min_val, valmax=max_val, valinit=init_val)
            for ax, label, min_val, max_val, init_val in zip(
                self.slider_axes,
                ['P (s⁻¹)', 'γ₄₃ (s⁻¹)', 'γ₃₂ (s⁻¹)', 'γ₂₁ (s⁻¹)', 'N_total'],
                [1e6, 1e6, 1e3, 1e6, 1e18],
                [1e10, 1e9, 1e7, 1e9, 1e24],
                [5e8, 5e7, 5e5, 5e7, 1e20]
            )
        ]
        
        # Add zoom slider
        self.zoom_ax = plt.axes([0.35, 0.33, 0.3, 0.01], facecolor=self.axcolor)
        self.zoom_slider = Slider(
            ax=self.zoom_ax,
            label='Zoom (time range %)',
            valmin=1,
            valmax=100,
            valinit=100,
            valfmt='%0.0f%%'
        )
        
        # Add reset buttons
        self.reset_ax = plt.axes([0.02, 0.20, 0.1, 0.04])
        self.reset_btn = Button(self.reset_ax, 'Reset Params', color=self.axcolor)
        
        self.reset_zoom_ax = plt.axes([0.02, 0.25, 0.1, 0.04])
        self.reset_zoom_btn = Button(self.reset_zoom_ax, 'Reset Zoom', color=self.axcolor)
        
        # Store full time ranges for each simulation
        self.full_t_cavity = None
        self.full_t_stim = None
        self.full_t_relax = None
        
        # Connect events
        for slider in self.sliders:
            slider.on_changed(self.update)
        self.zoom_slider.on_changed(self.update_zoom)
        self.radio.on_clicked(self.update)
        self.reset_btn.on_clicked(self.reset_sliders)
        self.reset_zoom_btn.on_clicked(self.reset_zoom)
        
        # Initial update
        self.update(None)
    
    def reset_sliders(self, event):
        for slider in self.sliders:
            slider.reset()
    
    def reset_zoom(self, event):
        self.zoom_slider.reset()
        self.update_zoom(None)
    
    def get_params(self):
        return [slider.val for slider in self.sliders]
    
    def get_zoom_factor(self):
        return self.zoom_slider.val / 100.0
    
    def update_zoom(self, event):
        zoom_factor = self.get_zoom_factor()
        sim_type = self.radio.value_selected
        
        if sim_type == 'Cavity' and self.full_t_cavity is not None:
            full_t = self.full_t_cavity
            t_range = (full_t[0], full_t[0] + (full_t[-1] - full_t[0]) * zoom_factor)
            self.ax1.set_xlim(t_range)
            self.ax2.set_xlim(t_range)
            self.ax3.set_xlim(t_range)
        elif sim_type == 'Stimulated Emission' and self.full_t_stim is not None:
            full_t = self.full_t_stim
            t_range = (full_t[0], full_t[0] + (full_t[-1] - full_t[0]) * zoom_factor)
            self.ax1.set_xlim(t_range)
            self.ax2.set_xlim(t_range)
        elif sim_type == 'Without Stimulated Emission' and self.full_t_relax is not None:
            full_t = self.full_t_relax
            t_range = (full_t[0], full_t[0] + (full_t[-1] - full_t[0]) * zoom_factor)
            self.ax1.set_xlim(t_range)
            self.ax2.set_xlim(t_range)
            self.ax3.set_xlim(t_range)
        
        self.fig.canvas.draw_idle()
    
    def cavity_simulation(self, P, gamma43, gamma32, gamma21, N_total):
        # Cavity parameters
        R = 0.99
        L = 0.10
        n = 1.82
        tau = (2 * n * L) / (c * (1 - R**2))
        alpha = 1 / tau
        
        t_span = (0, 0.1e-4)
        t_eval = np.linspace(*t_span, 1000)  # Increased points for smoother zoom
        t_us = t_eval * 1e6
        self.full_t_cavity = t_us
        
        def laser_system(t, y):
            N1, N2, N3, N4, I = y
            dN4 = P * N1 - gamma43 * N4
            dN3 = gamma43 * N4 - (B32 * (N3 - N2) * (I / c)) - gamma32 * N3 - A32 * N3
            dN2 = (B32 * (N3 - N2) * (I / c)) - gamma21 * N2 + gamma32 * N3 + A32 * N3
            dN1 = gamma21 * N2 - P * N1
            dI = (B32 * hv * (N3 - N2) * I) - (alpha * I) + (c * hv * A32 * N3)
            return [dN1, dN2, dN3, dN4, dI]
        
        y0 = [N_total, 0, 0, 0, 0]
        sol = solve_ivp(laser_system, t_span, y0, t_eval=t_eval, method='LSODA', rtol=1e-8, atol=1e-10)
        
        I = sol.y[4]
        ratio = np.where(sol.y[1] > 0, sol.y[2] / sol.y[1], np.nan)
        inversion = sol.y[2] - sol.y[1]
        
        return t_us, I, ratio, inversion
    
    def stimulated_simulation(self, P, gamma43, gamma32, gamma21, N_total):
        t_span = (0, 0.1e-4)
        t_eval = np.linspace(*t_span, 1000)  # Increased points for smoother zoom
        t_ns = t_eval * 1e9
        self.full_t_stim = t_ns
        
        def laser_system(t, y):
            N1, N2, N3, N4, I = y
            dN4 = P * N1 - gamma43 * N4
            dN3 = gamma43 * N4 - gamma32 * N3 - B32 * (N3 - N2) * I
            dN2 = gamma32 * N3 + B32 * (N3 - N2) * I - gamma21 * N2
            dN1 = gamma21 * N2 - P * N1
            dI = h * v * B32 * (N3 - N2) * I
            return [dN1, dN2, dN3, dN4, dI]
        
        y0 = [N_total, 0, 0, 0, 1e-6]
        sol = solve_ivp(laser_system, t_span, y0, t_eval=t_eval, method='BDF', rtol=1e-8, atol=1e-10)
        
        N3 = sol.y[2]
        N2 = sol.y[1]
        I = sol.y[4]
        
        return t_ns, N3, N2, I
    
    def relaxation_simulation(self, P, gamma43, gamma32, gamma21, N_total):
        E21 = 1.17 * 1.602e-19  # J
        gamma12 = gamma21 * np.exp(-E21/(k_B*T))
        
        t_span = (0, 100e-3)
        t_eval = np.linspace(*t_span, 1000)  # Increased points for smoother zoom
        t_us = t_eval * 1e6
        self.full_t_relax = t_us
        
        def rates(t, y):
            N1, N2, N3, N4 = y
            dN4 = P*N1 - gamma43*N4
            dN3 = gamma43*N4 - gamma32*N3
            dN2 = gamma32*N3 + gamma12*N1 - gamma21*N2
            dN1 = gamma21*N2 - gamma12*N1 - P*N1
            return [dN1, dN2, dN3, dN4]
        
        y0 = [N_total, 0.0, 0.0, 0.0]
        sol = solve_ivp(rates, t_span, y0, t_eval=t_eval, method='BDF')
        
        N1, N2, N3, N4 = sol.y
        ratio = N3 / N2
        
        return t_us, N1, N4, N3, N2, ratio
    
    def update(self, event):
        P, gamma43, gamma32, gamma21, N_total = self.get_params()
        sim_type = self.radio.value_selected
        
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        
        if sim_type == 'Cavity':
            t, I, ratio, inversion = self.cavity_simulation(P, gamma43, gamma32, gamma21, N_total)
            
            self.ax1.plot(t, I, color='purple', lw=2)
            self.ax1.set_ylabel('Intensity (W/m²)')
            self.ax1.set_title('Laser Intensity vs Time')
            self.ax1.grid(True)
            
            self.ax2.plot(t, ratio, color='teal', lw=2)
            self.ax2.axhline(1, linestyle='--', color='gray', label='1')
            self.ax2.set_ylabel('N3 / N2')
            self.ax2.legend()
            self.ax2.set_title('Population Ratio vs Time')
            self.ax2.grid(True)
            
            self.ax3.plot(t, inversion, color='green', lw=2)
            self.ax3.set_xlabel('Time (µs)')
            self.ax3.set_ylabel('N3 - N2')
            self.ax3.set_title('Population Inversion vs Time')
            self.ax3.grid(True)
            
        elif sim_type == 'Stimulated Emission':
            t, N3, N2, I = self.stimulated_simulation(P, gamma43, gamma32, gamma21, N_total)
            
            self.ax1.plot(t, N3, label="N₃ (upper laser level)", linewidth=2)
            self.ax1.plot(t, N2, label="N₂ (lower laser level)", linewidth=2)
            self.ax1.set_ylabel("Population (atoms/m³)")
            self.ax1.set_title("Populations N₃ and N₂ vs. Time")
            self.ax1.legend()
            self.ax1.grid(True)
            
            self.ax2.plot(t, I, label="Intensity I", color="darkgreen", linewidth=2)
            self.ax2.set_xlabel("Time (ns)")
            self.ax2.set_ylabel("Intensity (arb. units)")
            self.ax2.set_title("Laser Intensity vs. Time (Stimulated Only)")
            self.ax2.grid(True)
            
            self.ax3.axis('off')
            
        elif sim_type == 'Without Stimulated Emission':
            t, N1, N4, N3, N2, ratio = self.relaxation_simulation(P, gamma43, gamma32, gamma21, N_total)
            
            self.ax1.plot(t, N1, label='N1')
            self.ax1.plot(t, N4, label='N4')
            self.ax1.set_ylabel('Population')
            self.ax1.set_title('N1 and N4 vs Time')
            self.ax1.legend()
            self.ax1.grid(True)
            
            self.ax2.plot(t, N3, label='N3')
            self.ax2.plot(t, N2, label='N2')
            self.ax2.set_ylabel('Population')
            self.ax2.set_title('N3 and N2 vs Time')
            self.ax2.legend()
            self.ax2.grid(True)
            
            self.ax3.plot(t, ratio, label='N3/N2')
            self.ax3.axhline(1, linestyle='--', color='gray', label='1')
            self.ax3.set_xlabel('Time (µs)')
            self.ax3.set_ylabel('N3/N2')
            self.ax3.set_title('Ratio N3/N2 vs Time')
            self.ax3.legend()
            self.ax3.grid(True)
        
        # Apply zoom after updating plots
        self.update_zoom(None)
        self.fig.canvas.draw_idle()

# Run the simulator
simulator = LaserSimulator()
plt.show()