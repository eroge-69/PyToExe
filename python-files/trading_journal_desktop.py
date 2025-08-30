import os
import shutil
import sqlite3
from datetime import datetime

import pandas as pd
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog, QMessageBox,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableView,
    QComboBox, QCheckBox, QDoubleSpinBox, QTextEdit, QGroupBox,
    QFormLayout, QSplitter
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# ---------------------------
# تنظیمات مسیرها/دیتابیس
# ---------------------------
DB_PATH = "trading_journal.db"
IMG_DIR = "screenshots"
os.makedirs(IMG_DIR, exist_ok=True)

# ---------------------------
# دیتابیس: ساخت جدول در صورت نبود
# ---------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_dt TEXT,
        exit_dt TEXT,
        symbol TEXT,
        side TEXT,
        size REAL,
        entry_price REAL,
        stop_loss REAL,
        take_profit REAL,
        exit_price REAL,
        pnl REAL,
        pnl_pct REAL,
        rr REAL,
        setup TEXT,
        market_cond TEXT,
        entry_emotion TEXT,
        management_notes TEXT,
        exit_reason TEXT,
        followed_plan INTEGER,
        tags TEXT,
        screenshot TEXT
    );
    """)
    conn.commit()
    conn.close()

def load_df():
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM trades ORDER BY datetime(entry_dt) ASC", conn)
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def compute_stats(df: pd.DataFrame):
    stats = {
        "count": 0, "win_rate": 0.0, "avg_win": 0.0, "avg_loss": 0.0,
        "best": 0.0, "worst": 0.0, "expectancy": 0.0, "avg_rr": 0.0,
        "adherence": 0.0, "profit_factor": None, "max_dd": 0.0
    }
    if df is None or df.empty:
        return stats

    wins = df[df["pnl"] > 0]["pnl"]
    losses = df[df["pnl"] <= 0]["pnl"]

    stats["count"] = len(df)
    stats["win_rate"] = (len(wins) / len(df) * 100) if len(df) else 0
    stats["avg_win"] = float(wins.mean()) if not wins.empty else 0.0
    stats["avg_loss"] = float(losses.mean()) if not losses.empty else 0.0
    stats["best"] = float(df["pnl"].max()) if "pnl" in df and not df["pnl"].isna().all() else 0.0
    stats["worst"] = float(df["pnl"].min()) if "pnl" in df and not df["pnl"].isna().all() else 0.0
    stats["avg_rr"] = float(df["rr"].mean()) if "rr" in df and not df["rr"].isna().all() else 0.0
    if "followed_plan" in df:
        try:
            stats["adherence"] = float(df["followed_plan"].mean() * 100)
        except Exception:
            stats["adherence"] = 0.0

    gross_profit = wins.sum() if not wins.empty else 0.0
    gross_loss = losses.sum() if not losses.empty else 0.0
    stats["profit_factor"] = (gross_profit / abs(gross_loss)) if gross_loss != 0 else None

    equity = df["pnl"].fillna(0).cumsum()
    peak = equity.cummax()
    drawdown = equity - peak
    stats["max_dd"] = float(drawdown.min()) if not drawdown.empty else 0.0

    stats["expectancy"] = (
        (stats["win_rate"] / 100.0) * stats["avg_win"]
        + (1 - stats["win_rate"] / 100.0) * stats["avg_loss"]
    )
    return stats

# ---------------------------
# مدل جدول بر پایه Pandas
# ---------------------------
class PandasModel(QStandardItemModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        super().__init__(parent)
        self.set_dataframe(df)

    def set_dataframe(self, df):
        self._df = df.copy() if df is not None else pd.DataFrame()
        self.clear()
        if self._df is None or self._df.empty:
            return
        # ستون‌ها
        self.setColumnCount(len(self._df.columns))
        self.setHorizontalHeaderLabels(list(self._df.columns))
        # ردیف‌ها
        for _, row in self._df.iterrows():
            items = []
            for col in self._df.columns:
                val = row[col]
                items.append(QStandardItem("" if pd.isna(val) else str(val)))
            self.appendRow(items)

    def dataframe(self):
        return self._df.copy()

# ---------------------------
# ویجت نمودار مات‌پلات‌لیب
# ---------------------------
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(5, 3))
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)

    def plot_equity(self, df):
        self.ax.clear()
        if df is None or df.empty:
            self.ax.set_title("Equity Curve (No data)")
            self.draw()
            return
        try:
            df2 = df.copy()
            df2["entry_dt"] = pd.to_datetime(df2["entry_dt"], errors="coerce")
            df2 = df2.sort_values("entry_dt")
            df2["equity"] = df2["pnl"].fillna(0).cumsum()
            self.ax.plot(df2["entry_dt"], df2["equity"], marker="o")
            self.ax.set_title("Equity Curve")
            self.ax.grid(True, alpha=0.3)
        except Exception as e:
            self.ax.text(0.5, 0.5, f"Plot error: {e}", ha="center", va="center", transform=self.ax.transAxes)
        self.draw()

# ---------------------------
# برنامه اصلی
# ---------------------------
class TradingJournalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trading Journal (Desktop)")
        self.resize(1200, 760)

        init_db()
        self.df = load_df()
        self.current_id = None  # رکورد انتخاب‌شده برای ویرایش/حذف

        # ساخت UI مشابه قبل (فیلترها + آمار + نمودار + جدول + فرم)
        # ... (اینجا دقیقاً مثل نسخه‌ی قبلی بساز)

        # دکمه‌ها در فرم
        save_btn = QPushButton("ذخیره معامله")
        save_btn.clicked.connect(self.save_trade)

        edit_btn = QPushButton("ویرایش معامله")
        edit_btn.clicked.connect(self.edit_trade)

        delete_btn = QPushButton("حذف معامله")
        delete_btn.clicked.connect(self.delete_trade)

        form_layout.addRow(save_btn)
        form_layout.addRow(edit_btn)
        form_layout.addRow(delete_btn)

        # جدول
        self.table.clicked.connect(self.on_row_selected)

        self.refresh_all()

    # ---------------------------
    # انتخاب ردیف → پرکردن فرم
    def on_row_selected(self, index: QModelIndex):
        row = self.proxy.mapToSource(index).row()
        if row < 0 or row >= len(self.df):
            return
        rec = self.df.iloc[row]
        self.current_id = rec["id"]

        self.entry_dt.setText(str(rec["entry_dt"] or ""))
        self.exit_dt.setText(str(rec["exit_dt"] or ""))
        self.symbol.setText(str(rec["symbol"] or ""))
        self.side.setCurrentText(str(rec["side"] or "LONG"))
        self.size.setValue(float(rec["size"] or 0))
        self.entry_price.setValue(float(rec["entry_price"] or 0))
        self.exit_price.setValue(float(rec["exit_price"] or 0))
        self.stop_loss.setValue(float(rec["stop_loss"] or 0))
        self.take_profit.setValue(float(rec["take_profit"] or 0))
        self.setup.setText(str(rec["setup"] or ""))
        self.market_cond.setText(str(rec["market_cond"] or ""))
        self.entry_emotion.setText(str(rec["entry_emotion"] or ""))
        self.management_notes.setText(str(rec["management_notes"] or ""))
        self.exit_reason.setText(str(rec["exit_reason"] or ""))
        self.followed_plan.setChecked(bool(rec["followed_plan"]))
        self.tags.setText(str(rec["tags"] or ""))
        self.screenshot_path.setText(str(rec["screenshot"] or ""))

    # ---------------------------
    def edit_trade(self):
        if not self.current_id:
            QMessageBox.warning(self, "انتخاب نشده", "یک معامله از جدول انتخاب کنید.")
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                UPDATE trades SET
                  entry_dt=?, exit_dt=?, symbol=?, side=?, size=?, entry_price=?, stop_loss=?, take_profit=?,
                  exit_price=?, pnl=?, pnl_pct=?, rr=?, setup=?, market_cond=?, entry_emotion=?, management_notes=?,
                  exit_reason=?, followed_plan=?, tags=?, screenshot=?
                WHERE id=?
            """, (
                self.entry_dt.text(), self.exit_dt.text(), self.symbol.text(),
                self.side.currentText(), self.size.value(), self.entry_price.value(),
                self.stop_loss.value(), self.take_profit.value(), self.exit_price.value(),
                0, 0, 0,  # اینجا می‌تونی محاسبات pnl/rr رو مثل save_trade اضافه کنی
                self.setup.text(), self.market_cond.text(), self.entry_emotion.text(),
                self.management_notes.toPlainText(), self.exit_reason.text(),
                1 if self.followed_plan.isChecked() else 0,
                self.tags.text(), self.screenshot_path.text(), self.current_id
            ))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "موفق", "معامله ویرایش شد.")
            self.df = load_df()
            self.refresh_all()
            self.clear_form()
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"ویرایش با خطا مواجه شد:\n{e}")

    # ---------------------------
    def delete_trade(self):
        if not self.current_id:
            QMessageBox.warning(self, "انتخاب نشده", "یک معامله از جدول انتخاب کنید.")
            return
        reply = QMessageBox.question(self, "تأیید حذف", "آیا مطمئنید؟", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("DELETE FROM trades WHERE id=?", (self.current_id,))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "حذف", "معامله حذف شد.")
                self.df = load_df()
                self.refresh_all()
                self.clear_form()
            except Exception as e:
                QMessageBox.warning(self, "خطا", f"حذف با خطا مواجه شد:\n{e}")

    def clear_form(self):
        self.current_id = None
        self.entry_dt.clear(); self.exit_dt.clear(); self.symbol.clear()
        self.size.setValue(0.0); self.entry_price.setValue(0.0); self.exit_price.setValue(0.0)
        self.stop_loss.setValue(0.0); self.take_profit.setValue(0.0)
        self.setup.clear(); self.market_cond.clear(); self.entry_emotion.clear()
        self.management_notes.clear(); self.exit_reason.clear()
        self.followed_plan.setChecked(False); self.tags.clear(); self.screenshot_path.clear()
