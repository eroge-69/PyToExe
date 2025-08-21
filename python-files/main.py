import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView
import pandas as pd
from datetime import datetime
from PyQt5.QtCore import QTime, QTimer
from PyQt5 import uic
from workers.executor_worker import ExecutorWorker
from PyQt5.QtCore import pyqtSignal
from utils.table_model import pandasModel


class MainWindow(QMainWindow):
    worker_data_sender = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("ui/main.ui", self)
        self.setWindowTitle("Trading Terminal")

        # self.setGeometry(100, 100, 800, 600)
        self.status_bar = self.ui.statusbar_text
        self.showMaximized()
        self.status_bar.hide()
        self.ui.btc_price_label.setText("BTC Price: Waiting for update...")
        self.ui.gold_price_label.setText("XAU Price: Waiting for update...")

        self.executor_worker = ExecutorWorker()
        self.executor_worker.btc_price.connect(self.update_btc_price)
        self.executor_worker.xau_price.connect(self.update_xau_price)
        self.worker_data_sender.connect(
            self.executor_worker.handle_data_from_main_thread)
        self.executor_worker.status.connect(self.update_status)
        self.executor_worker.start()

        self.ui.order_place_btn.clicked.connect(self.place_order)
        self.ui.order_schedule_btn.clicked.connect(self.schedule_order)
        self.ui.refresh_strategies_btn.clicked.connect(
            self.refresh_strategies_in_table)
        self.ui.refresh_schedules_btn.clicked.connect(
            self.refresh_schedules_in_table)
        self.ui.clear_schedule_btn.clicked.connect(self.clear_schedules)
        self.ui.delete_strategy_btn.clicked.connect(self.delete_strategy)
        self.ui.retry_connection_btn.clicked.connect(
            self.retry_connection_with_mt5)

        current_time = QTime.currentTime()
        future_time = current_time.addSecs(60)
        self.ui.time_to_execute.setTime(future_time)
        self.refresh_strategies_in_table()
        self.refresh_schedules_in_table()
        self.ui.use_capital_percent_checkbox.setChecked(False)
        self.ui.use_capital_percent_checkbox.stateChanged.connect(
            self.toggle_capital_percent)
        self.toggle_capital_percent()

    def retry_connection_with_mt5(self):
        print("Retrying connection with MT5...")
        payload = {
            "action": "retry_connection_with_mt5",
            "data": {}
        }
        self.send_data_to_worker(self.worker_data_sender, payload)

    def toggle_capital_percent(self):
        current_state = self.ui.use_capital_percent_checkbox.isChecked()
        if current_state:
            self.ui.lot_size_sb.hide()
            self.ui.volume_label.hide()
            self.ui.percent_cap_label.show()
            self.ui.capital_usage_by_percent_sb.show()
        else:
            self.ui.percent_cap_label.hide()
            self.ui.capital_usage_by_percent_sb.hide()
            self.ui.lot_size_sb.show()
            self.ui.volume_label.show()

    def schedule_order(self):
        print("Scheduling order...")
        payload = {
            "action": "schedule_order",
            "data": {
                "time_to_execute": self.ui.time_to_execute.time().toString("HH:mm:ss"),
                "data": self.get_order_payload()
            }
        }
        self.send_data_to_worker(self.worker_data_sender, payload)

    def clear_schedules(self):
        print("Clearing schedules...")
        try:
            os.remove("scheduled_jobs/jobs.json")
            print("Cleared all schedules.")
        except FileNotFoundError:
            print("No scheduled jobs file found.")
        except Exception as e:
            print(f"Error clearing schedules: {e}")
        finally:
            self.refresh_schedules_in_table()

    def delete_strategy(self):
        if self.strategies_table.currentIndex().row() == -1:
            self.status_bar.setText("Please select a strategy to delete.")
            self.status_bar.setStyleSheet("color: red")
            self.status_bar.show()
            QTimer.singleShot(5000, lambda: self.status_bar.hide())
            return

        selected_row = self.strategies_table.currentIndex().row()
        if selected_row >= 0:
            strategy_id = self.strategies_table.model().data(
                self.strategies_table.model().index(selected_row, 0))
            with open("scheduled_jobs/entry_points.json", "r") as f:
                entry_points = json.load(f)
            if strategy_id in entry_points:
                del entry_points[strategy_id]
                with open("scheduled_jobs/entry_points.json", "w") as f:
                    json.dump(entry_points, f)
                self.status_bar.setText("Strategy deleted successfully.")
                self.status_bar.setStyleSheet("color: green")
                self.status_bar.show()
                QTimer.singleShot(5000, lambda: self.status_bar.hide())
                self.refresh_strategies_in_table()
                self.send_data_to_worker(self.worker_data_sender, {
                    "action": "refresh_strategies",
                })
            else:
                self.status_bar.setText("Strategy not found.")
                self.status_bar.setStyleSheet("color: red")
                self.status_bar.show()
                QTimer.singleShot(5000, lambda: self.status_bar.hide())

    # def fix_timing(self):
    #     self.ui.time_to_execute.setTime(QTime.currentTime())

    def update_btc_price(self, price):
        self.ui.btc_price_label.setText(f"BTC: {price}")

    def update_xau_price(self, price):
        self.ui.gold_price_label.setText(f"XAU: {price}")

    def update_status(self, update):
        if update['event'] == "order_place_update":
            if update['message'].startswith("Error"):
                self.status_bar.setText(update['message'])
                self.status_bar.setStyleSheet("color: red")
                self.status_bar.show()
                QTimer.singleShot(5000, lambda: self.status_bar.hide())
            else:
                self.status_bar.setText(update['message'])
                self.status_bar.setStyleSheet("color: green")
                self.status_bar.show()
                QTimer.singleShot(5000, lambda: self.status_bar.hide())
            try:
                self.refresh_strategies_in_table()
            except Exception as e:
                print(f"Error refreshing strategies: {e}")
            # payload = {
            #     "action": "refresh_strategies",
            # }
            # self.send_data_to_worker(self.worker_data_sender, payload)
        elif update['event'] == "order_schedule_update":
            self.status_bar.setText(update['message'])
            self.status_bar.setStyleSheet("color: blue")
            self.status_bar.show()
            QTimer.singleShot(5000, lambda: self.status_bar.hide())
            self.refresh_schedules_in_table()
        elif update['event'] == "current_capital_update":
            self.ui.available_balance.setText(
                f"Available Capital: {update['capital']}")
        else:
            self.status_bar.setText("Unknown event")
            self.status_bar.setStyleSheet("color: red")
            self.status_bar.show()
            QTimer.singleShot(5000, lambda: self.status_bar.hide())

    def get_order_payload(self):
        current_state = self.ui.use_capital_percent_checkbox.isChecked()
        if current_state:
            payload = {
                "symbol": self.ui.symbol_select_cb.currentText(),
                "capital_percent": self.ui.capital_usage_by_percent_sb.value(),
                "leverage": self.ui.leverage_sb.value(),
                "stop_loss_points": self.ui.stop_loss_points_sb.value(),
                "limit_points": self.ui.limit_points_sb.value(),
            }
        else:
            payload = {
                "symbol": self.ui.symbol_select_cb.currentText(),
                "volume": self.ui.lot_size_sb.value(),
                "stop_loss_points": self.ui.stop_loss_points_sb.value(),
                "limit_points": self.ui.limit_points_sb.value(),
            }
        return payload

    def place_order(self):
        payload = {
            "action": "place_order",
            "data": self.get_order_payload()
        }
        self.send_data_to_worker(self.worker_data_sender, payload)

    def send_data_to_worker(self, worker_sender, data):
        worker_sender.emit(data)

    def table_functions(self):
        self.schedules_table.resizeColumnsToContents()
        self.schedules_table.customContextMenuRequested.connect(
            self.showOptionsContextMenu)
        self.schedules_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section {background-color: black; color: white; border: 1px solid #6c6c6c;}")
        self.schedules_table.setSortingEnabled(True)

    def remove_expired_scheduled_jobs(self):
        current_time = datetime.now()
        try:
            with open("scheduled_jobs/jobs.json", "r") as f:
                scheduled_jobs = json.load(f)
        except FileNotFoundError:
            print("No scheduled jobs found.")
            return
        except json.JSONDecodeError:
            print("Error decoding JSON file.")
            return
        if not scheduled_jobs:
            print("No scheduled jobs found.")
            return

        for job_id, job_info in list(scheduled_jobs.items()):
            scheduled_time = datetime.strptime(job_info['time'], "%Y-%m-%d %H:%M:%S")
            if scheduled_time < current_time:
                del scheduled_jobs[job_id]
                print(f"Removed expired job: {job_id}")
        with open("scheduled_jobs/jobs.json", "w") as f:
            json.dump(scheduled_jobs, f)

    def refresh_schedules_in_table(self):
        self.remove_expired_scheduled_jobs()
        if not os.path.exists("scheduled_jobs/jobs.json"):
            print("No scheduled jobs file found.")
            df = pd.DataFrame(columns=["id", "symbol", "capital_percent",
                                       "stop_loss_points", "time_to_execute"])
        else:
            df = pd.read_json(
                "scheduled_jobs/jobs.json").T.reset_index().rename(columns={"index": "id"})
        if not df.empty:
            df = pd.concat([df.drop(columns=["payload"]),
                           pd.json_normalize(df["payload"])], axis=1)
        else:
            df = pd.DataFrame(columns=["id", "symbol", "capital_percent",
                                       "stop_loss_points", "time_to_execute"])
        self.ui.schedules_table.setModel(pandasModel(df, editable=False))
        self.ui.schedules_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def refresh_strategies_in_table(self):
        try:
            if not os.path.exists("scheduled_jobs/entry_points.json"):
                print("No entry points file found.")
                df = pd.DataFrame(
                    columns=["symbol", "entry_point", "stop_loss_points"])
            else:
                df = pd.read_json(
                    "scheduled_jobs/entry_points.json").T.reset_index().rename(columns={"index": "symbol"})

            self.ui.strategies_table.setModel(pandasModel(df, editable=False))
            self.ui.strategies_table.horizontalHeader(
            ).setSectionResizeMode(QHeaderView.Stretch)
        except Exception as e:
            print(f"Error loading entry points: {e}")
            df = pd.DataFrame(
                columns=["symbol", "entry_point", "stop_loss_points"])
            self.ui.strategies_table.setModel(pandasModel(df, editable=False))
            self.ui.strategies_table.horizontalHeader(
            ).setSectionResizeMode(QHeaderView.Stretch)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
