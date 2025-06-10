import tkinter as tk  
from tkinter import ttk  
import numpy as np  
import matplotlib.pyplot as plt  
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  
from scipy.special import erfc  

class ModulationApp:  
    def __init__(self, root):  
        self.root = root  
        self.root.title("نمایش صورت فلکی مدولاسیون‌های دیجیتال")  
        self.root.geometry("1200x800")  
        self.create_widgets()  

    def create_widgets(self):  
        main_frame = ttk.Frame(self.root)  
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  

        # کنترل پنل  
        control_frame = ttk.Frame(main_frame)  
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)  

        # لیست مدولاسیون‌ها  
        modulations = [  
            ("BPSK", None),  
            ("QPSK", None),  
            ("MPSK", [4, 8, 16]),  
            ("MQAM", [4, 16, 64]),  
            ("PASK", [2, 4, 8]),  
            ("MFSK", [2, 4, 8]),  
            ("DPSK", [2, 4])  
        ]  

        # ایجاد دکمه‌ها  
        ttk.Label(control_frame, text="انتخاب مدولاسیون:").pack(pady=5)  
        
        for mod, options in modulations:  
            if options is None:  
                btn = ttk.Button(control_frame, text=mod,   
                                command=lambda m=mod: self.plot_constellation(m, None))  
                btn.pack(fill=tk.X, pady=2)  
            else:  
                sub_frame = ttk.Frame(control_frame)  
                sub_frame.pack(fill=tk.X, pady=2)  
                ttk.Label(sub_frame, text=f"{mod}:").pack(side=tk.LEFT)  
                for opt in options:  
                    btn = ttk.Button(sub_frame, text=str(opt), width=3,  
                                    command=lambda m=mod, o=opt: self.plot_constellation(m, o))  
                    btn.pack(side=tk.LEFT, padx=2)  

        # فریم نمودار  
        self.plot_frame = ttk.Frame(main_frame)  
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)  
        
        # ایجاد نمودار  
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 10))  
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)  
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)  

        # نمایش اولیه  
        self.ax1.text(0.5, 0.5, "مدولاسیون مورد نظر را انتخاب کنید",   
                     ha='center', va='center', fontsize=12)  
        self.ax1.axis('off')  
        self.ax2.axis('off')  
        self.canvas.draw()  

    def calculate_ber(self, modulation, M, snr_db):  
        snr = 10 ** (snr_db / 10)  
        
        if modulation == "BPSK":  
            return 0.5 * erfc(np.sqrt(snr))  
        elif modulation == "QPSK":  
            return 0.5 * erfc(np.sqrt(snr))  
        elif modulation == "MPSK":  
            return (1/np.log2(M)) * erfc(np.sqrt(snr * np.log2(M)) * np.sin(np.pi/M))  
        elif modulation == "MQAM":  
            return (4/np.log2(M)) * (1 - 1/np.sqrt(M)) * 0.5 * erfc(np.sqrt(3*snr/(2*(M-1))))  
        elif modulation == "PASK":  
            return (2*(M-1)/M) * 0.5 * erfc(np.sqrt(3*snr/(M**2-1)))  
        elif modulation == "MFSK":  
            return ((M-1)/2) * erfc(np.sqrt(snr/2))  
        elif modulation == "DPSK":  
            if M == 2:  
                return 0.5 * np.exp(-snr)  
            else:  
                return 0.5 * erfc(np.sqrt(snr))  
        return 0  

    def plot_constellation(self, modulation, M):  
        self.ax1.clear()  
        self.ax2.clear()  
        
        # تنظیمات عمومی  
        self.ax1.grid(True, linestyle='--', alpha=0.7)  
        self.ax1.set_xlabel('In-phase (I)')  
        self.ax1.set_ylabel('Quadrature (Q)')  
        self.ax1.set_aspect('equal')  
        
        # تولید نقاط صورت فلکی  
        if modulation == "BPSK":  
            points = [(1, 0), (-1, 0)]  
            colors = ['red', 'blue']  
            title = "BPSK"  
        elif modulation == "QPSK":  
            points = [(1/np.sqrt(2), 1/np.sqrt(2)), (-1/np.sqrt(2), 1/np.sqrt(2)),  
                      (-1/np.sqrt(2), -1/np.sqrt(2)), (1/np.sqrt(2), -1/np.sqrt(2))]  
            colors = ['red', 'green', 'blue', 'purple']  
            title = "QPSK"  
        elif modulation == "MPSK" and M:  
            angles = np.linspace(0, 2*np.pi, M, endpoint=False)  
            points = [(np.cos(a), np.sin(a)) for a in angles]  
            colors = plt.cm.rainbow(np.linspace(0, 1, M))  
            title = f"{M}-PSK"  
        elif modulation == "MQAM" and M:  
            n = int(np.sqrt(M))  
            x = np.linspace(-1, 1, n)  
            y = np.linspace(-1, 1, n)  
            xx, yy = np.meshgrid(x, y)  
            points = list(zip(xx.flatten(), yy.flatten()))  
            colors = plt.cm.rainbow(np.linspace(0, 1, M))  
            title = f"{M}-QAM"  
        elif modulation == "PASK" and M:  
            points = [(i/(M-1), 0) for i in range(M)]  
            colors = plt.cm.rainbow(np.linspace(0, 1, M))  
            title = f"{M}-PASK"  
        elif modulation == "MFSK" and M:  
            points = [(0, i) for i in range(M)]  
            colors = plt.cm.rainbow(np.linspace(0, 1, M))  
            title = f"{M}-FSK"  
        elif modulation == "DPSK" and M:  
            if M == 2:  
                points = [(1, 0), (-1, 0)]  
                colors = ['red', 'blue']  
            else:  
                angles = np.linspace(0, 2*np.pi, M, endpoint=False)  
                points = [(np.cos(a), np.sin(a)) for a in angles]  
                colors = plt.cm.rainbow(np.linspace(0, 1, M))  
            title = f"{M}-DPSK"  
        else:  
            return  

        # رسم صورت فلکی  
        x, y = zip(*points)  
        self.ax1.scatter(x, y, c=colors, s=100, edgecolors='black')  
        self.ax1.set_title(f"Constellation {title}", fontsize=14, pad=20)  
        
        # محاسبه BER و SNR  
        snr_db = np.linspace(0, 20, 100)  
        ber = [self.calculate_ber(modulation, M if M else 2, snr) for snr in snr_db]  
        
        # رسم نمودار BER  
        self.ax2.semilogy(snr_db, ber)  
        self.ax2.grid(True, which="both", ls="--")  
        self.ax2.set_xlabel('SNR (dB)')  
        self.ax2.set_ylabel('Bit Error Rate (BER)')  
        self.ax2.set_title(f"BER vs SNR for {title}")  
        
        # نمایش اطلاعات  
        min_ber = min(ber)  
        optimal_snr = snr_db[np.argmin(ber)]  
        info_text = f"""  
        Modulation: {title}  
        Minimum BER: {min_ber:.2e}  
        Optimal SNR: {optimal_snr:.1f} dB  
        """  
        self.ax2.text(0.02, 0.98, info_text, transform=self.ax2.transAxes,  
                     va='top', ha='left', bbox=dict(facecolor='white', alpha=0.8))  

        # تنظیم محدوده‌ها  
        if modulation not in ["PASK", "MFSK"]:  
            max_val = max(abs(x) for x, y in points) * 1.2  
            self.ax1.set_xlim(-max_val, max_val)  
            self.ax1.set_ylim(-max_val, max_val)  
        
        self.canvas.draw()  

if __name__ == "__main__":  
    root = tk.Tk()  
    app = ModulationApp(root)  
    root.mainloop()
