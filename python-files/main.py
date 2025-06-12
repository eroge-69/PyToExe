import sys
import mysql.connector
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QToolTip
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
from matplotlib.figure import Figure
import matplotlib.dates as mdates


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.fig.subplots_adjust(bottom=0.2)

        # Store user-set limits for x (and optionally y)
        self._xlim = None
        self._ylim = None

        # Connect interaction events
        self.mpl_connect("motion_notify_event", self.on_hover)
        self.mpl_connect("button_press_event", self.on_press)
        self.mpl_connect("button_release_event", self.on_release)
        self.mpl_connect("motion_notify_event", self.on_motion)
        self.mpl_connect("scroll_event", self.on_scroll)

        self._is_panning = False
        self._last_mouse_x = None

    def on_hover(self, event):
        # Show tooltip with time and y-value at cursor
        if event.xdata and event.ydata:
            x = mdates.num2date(event.xdata).strftime("%Y-%m-%d %H:%M:%S")
            y = f"{event.ydata:.2f}"
            QToolTip.showText(event.guiEvent.globalPos(), f"Time: {x}\nValue: {y}")

    def on_press(self, event):
        if event.button == 1:  # Left click starts pan
            self._is_panning = True
            self._last_mouse_x = event.xdata

    def on_release(self, event):
        if self._is_panning:
            self._is_panning = False
            self._last_mouse_x = None

    def on_motion(self, event):
        if self._is_panning and event.xdata is not None and self._last_mouse_x is not None:
            dx = self._last_mouse_x - event.xdata
            xlim = self.ax.get_xlim()
            new_xlim = (xlim[0] + dx, xlim[1] + dx)
            self.ax.set_xlim(new_xlim)
            self._xlim = new_xlim
            self.draw()

    def on_scroll(self, event):
        if event.xdata is None:
            return
        xlim = self.ax.get_xlim()
        xdata = event.xdata
        # Zoom factor: scroll up (step>0) zoom in, scroll down zoom out
        scale_factor = 0.8 if event.step > 0 else 1.2
        new_width = (xlim[1] - xlim[0]) * scale_factor
        relx = (xdata - xlim[0]) / (xlim[1] - xlim[0])
        new_xlim = [xdata - new_width * relx, xdata + new_width * (1 - relx)]
        self.ax.set_xlim(new_xlim)
        self._xlim = new_xlim
        self.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live MySQL: Steam Temp & Tank Level")
        self.setGeometry(100, 100, 1000, 600)

        self.canvas = MplCanvas(self)
        toolbar = NavigationToolbar2QT(self.canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Auto-refresh timer
        self.timer = QTimer()
        self.timer.setInterval(5000)  # refresh every 5 seconds
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

        # Initial plot
        self.update_plot()

    def update_plot(self):
        try:
            conn = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="admin",
                database="noon_sugar_mills"
            )
            # Select both Steam_Temp and Steam_Pressure
            query = "SELECT Atime, Steam_Temp, Steam_Pressure FROM Sugar_Data ORDER BY Atime"
            df = pd.read_sql(query, conn)
            conn.close()

            if df.empty:
                return

            df.sort_values(by="Atime", inplace=True)

            ax = self.canvas.ax
            ax.clear()
            # Plot both series
            ax.plot(df["Atime"], df["Steam_Temp"], color="darkred", label="Steam Temp")
            ax.plot(df["Atime"], df["Steam_Pressure"], color="darkblue", label="Steam_Pressure")

            ax.set_title("Steam Temperature & Steam Pressure Over Time")
            ax.set_xlabel("Timestamp")
            ax.set_ylabel("Value")
            ax.grid(True)
            ax.legend()

            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.tick_params(axis='x', rotation=45)

            # Reapply stored x-limits if user has zoomed/panned
            if self.canvas._xlim is not None:
                try:
                    ax.set_xlim(self.canvas._xlim)
                except Exception:
                    pass
            # If desired, also store/apply y-limits similarly by extending MplCanvas

            self.canvas.draw()

        except Exception as e:
            print("❌ Error fetching data:", e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
