import sys
import mysql.connector
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class DynamicChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Wykres
        self.canvas = FigureCanvas(Figure(figsize=(6, 4)))
        self.layout.addWidget(self.canvas)
        self.ax = self.canvas.figure.add_subplot(111)
        self.ax.set_title("Strumień wody i ciepło")
        self.ax.set_xlabel("Czas (S)")
        self.ax.set_ylabel("JED")

        # Dane
        self.max_points = 3600  # np. ostatnie 120 sekund
        self.x_data = list(range(self.max_points))
        self.v_data = [0] * self.max_points
        self.q_data = [0] * self.max_points
        self.T1_data = [0] * self.max_points
        self.T2_data = [0] * self.max_points

        # Linie
        self.line_v, = self.ax.plot(self.x_data, self.v_data, label="V [L/min]/10")
        self.line_q, = self.ax.plot(self.x_data, self.q_data, label="Q [kW]")
        self.line_T1, = self.ax.plot(self.x_data, self.T1_data, label="T1")
        self.line_T2, = self.ax.plot(self.x_data, self.T2_data, label="T2")
        self.ax.legend()

        # Pobranie danych
        self.load_last_hour_data()

        # Timer do aktualizacji co 1 sekundę
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_chart)
        self.timer.start(1000)

    def fetch_last_statistic(self):
        """Pobranie ostatniego wiersza ze statystyk z bazy"""
        try:
            conn = mysql.connector.connect(
                host="100.122.37.58",
                user="dacz",
                password="dacz",
                database="Q_meter"
            )
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Vm3h, QkWh, T1, T2
                FROM statistic
                ORDER BY lp DESC
                LIMIT 1
            """)
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            if result:
                return result[0], result[1], result[2], result[3]
            else:
                return 0, 0, 0, 0
        except mysql.connector.Error as err:
            print(f"Błąd bazy danych: {err}")
            return 0, 0, 0, 0

    def load_last_hour_data(self):
        """Pobranie ostatnich 3600 rekordów z bazy danych"""
        try:
            conn = mysql.connector.connect(
                host="100.122.37.58",
                user="dacz",
                password="dacz",
                database="Q_meter"
            )
            cursor = conn.cursor()

            # Pobranie ostatnich 3600 rekordów i posortowanie rosnąco po datatime
            cursor.execute("""
                SELECT lp, Vm3h, QkWh, T1, T2
                FROM (
                    SELECT lp, Vm3h, QkWh, T1, T2
                    FROM statistic
                    ORDER BY lp DESC
                    LIMIT 3600
                ) AS last_records
                ORDER BY lp ASC
            """)
            results = cursor.fetchall()
            cursor.close()
            conn.close()

            # Czyszczenie danych
            self.v_data = []
            self.q_data = []
            self.T1_data = []
            self.T2_data = []

            # Wypełnianie danymi (ostatnie self.max_points rekordów)
            for row in results[-self.max_points:]:
                _, v, q, T1, T2 = row
                self.v_data.append(v / 10)
                self.q_data.append(q)
                self.T1_data.append(T1)
                self.T2_data.append(T2)

            # Uzupełnienie zerami, jeśli mniej niż self.max_points
            missing = self.max_points - len(self.v_data)
            if missing > 0:
                self.v_data = [0] * missing + self.v_data
                self.q_data = [0] * missing + self.q_data
                self.T1_data = [0] * missing + self.T1_data
                self.T2_data = [0] * missing + self.T2_data

        except mysql.connector.Error as err:
            print(f"Błąd bazy danych: {err}")

    def update_chart(self):
        # Pobranie danych z bazy
        v, q, T1, T2 = self.fetch_last_statistic()

        # Aktualizacja danych
        self.v_data.append(v / 10)
        self.v_data.pop(0)
        self.q_data.append(q)
        self.q_data.pop(0)
        self.T1_data.append(T1)
        self.T1_data.pop(0)
        self.T2_data.append(T2)
        self.T2_data.pop(0)

        # Aktualizacja wykresu
        self.line_v.set_ydata(self.v_data)
        self.line_q.set_ydata(self.q_data)
        self.line_T1.set_ydata(self.T1_data)
        self.line_T2.set_ydata(self.T2_data)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DynamicChart()
    window.show()
    sys.exit(app.exec())
