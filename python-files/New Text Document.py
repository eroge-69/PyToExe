import sys, os, csv, hashlib, datetime
from collections import defaultdict, OrderedDict

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QDialog, QFormLayout, QComboBox, QDateEdit, QGridLayout, QGroupBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from PyQt5.QtChart import (
    QChart, QChartView, QPieSeries,
    QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis,
    QLineSeries
)

USERS_FILE = "users.csv"

# ----------------- User System -----------------
class UserSystem:
    def __init__(self):
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, "w", newline='', encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=["username", "password_hash"]).writeheader()

    def _hash(self, pw: str) -> str:
        return hashlib.sha256(pw.encode()).hexdigest()

    def register(self, username, password) -> bool:
        users = self._load()
        if not username or not password or username in users:
            return False
        with open(USERS_FILE, "a", newline='', encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=["username","password_hash"]).writerow(
                {"username": username, "password_hash": self._hash(password)}
            )
        return True

    def login(self, username, password) -> bool:
        users = self._load()
        return username in users and users[username] == self._hash(password)

    def _load(self):
        users = {}
        with open(USERS_FILE, newline='', encoding="utf-8") as f:
            for row in csv.DictReader(f):
                users[row["username"]] = row["password_hash"]
        return users

# ----------------- Accounting Core -----------------
class Accounting:
    def __init__(self, username):
        self.username = username
        self.filename = f"accounts_{username}.csv"
        self.fields = ["date","account","amount","category","description"]
        self.transactions = []
        self._load()

    def _load(self):
        if os.path.exists(self.filename):
            with open(self.filename, newline='', encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    r["amount"] = float(r["amount"])
                    self.transactions.append(r)

    def _save(self):
        with open(self.filename, "w", newline='', encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=self.fields)
            w.writeheader()
            w.writerows(self.transactions)

    def add(self, account, amount, category, description=""):
        self.transactions.append({
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "account": account,
            "amount": float(amount),
            "category": category,
            "description": description
        })
        self._save()

    # -------- helpers for reports --------
    def accounts(self):
        return sorted({t["account"] for t in self.transactions})

    def categories(self):
        return sorted({t["category"] for t in self.transactions})

    def balances(self):
        bal = defaultdict(float)
        for t in self.transactions:
            bal[t["account"]] += t["amount"]
        return dict(bal)

    def filter(self, start=None, end=None, account=None, category=None):
        def to_dt(s):
            return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M")
        out = []
        for t in self.transactions:
            dt = to_dt(t["date"])
            if start and dt < start: continue
            if end and dt > end: continue
            if account and t["account"] != account: continue
            if category and t["category"] != category: continue
            out.append(t)
        return out

    def daily_net(self, start, end, account=None, category=None):
        """dict: 'YYYY-MM-DD' -> net amount that day"""
        tx = self.filter(start, end, account, category)
        # create all dates in range
        day = start.date()
        end_day = end.date()
        days = []
        while day <= end_day:
            days.append(day.strftime("%Y-%m-%d"))
            day += datetime.timedelta(days=1)
        net = OrderedDict((d, 0.0) for d in days)
        for t in tx:
            day_key = t["date"][:10]
            if day_key in net:
                net[day_key] += t["amount"]
        return net

    def expenses_by_category(self, start, end, account=None):
        tx = self.filter(start, end, account, None)
        cat = defaultdict(float)
        for t in tx:
            if t["amount"] < 0:
                cat[t["category"]] += -t["amount"]
        return dict(cat)

# ----------------- UI -----------------
class LoginWindow(QWidget):
    def __init__(self, usersys):
        super().__init__()
        self.users = usersys
        self.setWindowTitle("ورود به سیستم حسابداری")
        self.setGeometry(450, 250, 360, 220)
        self._build()

    def _build(self):
        lay = QVBoxLayout()
        title = QLabel("سیستم حسابداری")
        title.setFont(QFont("Vazirmatn", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        lay.addWidget(title)

        self.user = QLineEdit(); self.user.setPlaceholderText("نام کاربری")
        self.passw = QLineEdit(); self.passw.setPlaceholderText("رمز عبور"); self.passw.setEchoMode(QLineEdit.Password)

        btns = QHBoxLayout()
        login = QPushButton("ورود"); reg = QPushButton("ثبت‌نام")
        login.clicked.connect(self._login); reg.clicked.connect(self._register)

        lay.addWidget(self.user); lay.addWidget(self.passw)
        btns.addWidget(login); btns.addWidget(reg)
        lay.addLayout(btns)
        self.setLayout(lay)

    def _login(self):
        if self.users.login(self.user.text().strip(), self.passw.text()):
            self.main = MainWindow(self.user.text().strip())
            self.main.show()
            self.close()
        else:
            QMessageBox.warning(self, "خطا", "نام کاربری یا رمز عبور اشتباه است.")

    def _register(self):
        if self.users.register(self.user.text().strip(), self.passw.text()):
            QMessageBox.information(self, "موفق", "ثبت‌نام انجام شد. حالا وارد شوید.")
        else:
            QMessageBox.warning(self, "خطا", "نام کاربری تکراری یا اطلاعات نامعتبر.")

class MainWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.acc = Accounting(username)

        self.setWindowTitle(f"داشبورد حسابداری – {username}")
        self.setGeometry(220, 120, 1000, 650)
        self._build()

    # ---------- UI Layout ----------
    def _build(self):
        root = QVBoxLayout()
        header = QLabel(f"خوش آمدید، {self.username}")
        header.setFont(QFont("Vazirmatn", 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        root.addWidget(header)

        # Controls
        ctrl = QGridLayout()
        gb = QGroupBox("فیلترها")
        gb.setLayout(ctrl)

        self.cb_account = QComboBox(); self._refresh_accounts()
        self.cb_account.insertItem(0, "همه حساب‌ها"); self.cb_account.setCurrentIndex(0)

        self.cb_category = QComboBox(); self._refresh_categories()
        self.cb_category.insertItem(0, "همه دسته‌ها"); self.cb_category.setCurrentIndex(0)

        self.date_from = QDateEdit(calendarPopup=True)
        self.date_to   = QDateEdit(calendarPopup=True)
        today = QDate.currentDate()
        self.date_to.setDate(today)
        self.date_from.setDate(today.addMonths(-1))
        self.date_from.setDisplayFormat("yyyy-MM-dd")
        self.date_to.setDisplayFormat("yyyy-MM-dd")

        self.btn_refresh = QPushButton("به‌روزرسانی داشبورد")
        self.btn_refresh.clicked.connect(self.refresh_dashboard)

        self.btn_add_income = QPushButton("➕ ثبت درآمد")
        self.btn_add_expense = QPushButton("➖ ثبت هزینه")
        self.btn_add_income.clicked.connect(lambda: self._quick_add(+1))
        self.btn_add_expense.clicked.connect(lambda: self._quick_add(-1))

        ctrl.addWidget(QLabel("حساب:"), 0, 0); ctrl.addWidget(self.cb_account, 0, 1)
        ctrl.addWidget(QLabel("دسته:"), 0, 2); ctrl.addWidget(self.cb_category, 0, 3)
        ctrl.addWidget(QLabel("از تاریخ:"), 1, 0); ctrl.addWidget(self.date_from, 1, 1)
        ctrl.addWidget(QLabel("تا تاریخ:"), 1, 2); ctrl.addWidget(self.date_to, 1, 3)
        ctrl.addWidget(self.btn_refresh, 0, 4, 2, 1)
        ctrl.addWidget(self.btn_add_income, 0, 5)
        ctrl.addWidget(self.btn_add_expense, 1, 5)

        root.addWidget(gb)

        # Charts area
        charts = QGridLayout()
        self.chart_pie   = QChartView()
        self.chart_bar   = QChartView()
        self.chart_line  = QChartView()
        self._style_chartview(self.chart_pie)
        self._style_chartview(self.chart_bar)
        self._style_chartview(self.chart_line)

        charts.addWidget(self.chart_pie, 0, 0)
        charts.addWidget(self.chart_bar, 0, 1)
        charts.addWidget(self.chart_line, 1, 0, 1, 2)
        root.addLayout(charts)

        self.setLayout(root)
        self.refresh_dashboard()

    def _style_chartview(self, view: QChartView):
        view.setRenderHint(view.renderHints())
        view.setMinimumHeight(260)
        view.setRubberBand(QChartView.RectangleRubberBand)

    def _refresh_accounts(self):
        self.cb_account.clear()
        for a in self.acc.accounts():
            self.cb_account.addItem(a)

    def _refresh_categories(self):
        self.cb_category.clear()
        for c in self.acc.categories():
            self.cb_category.addItem(c)

    # ---------- Actions ----------
    def _quick_add(self, sign: int):
        # Simple inline dialog-free add using input boxes
        from PyQt5.QtWidgets import QInputDialog
        account, ok = QInputDialog.getText(self, "نام حساب", "مثل: Cash یا Bank")
        if not ok or not account: return
        amount, ok = QInputDialog.getDouble(self, "مبلغ", "مبلغ:", decimals=2)
        if not ok: return
        category, ok = QInputDialog.getText(self, "دسته‌بندی", "مثل: فروش / خرید / اجاره")
        if not ok or not category: return
        desc, ok = QInputDialog.getText(self, "توضیح (اختیاری)", "توضیح:")
        if not ok: desc = ""
        self.acc.add(account, sign * abs(amount), category, desc)
        QMessageBox.information(self, "ثبت شد", "تراکنش ذخیره شد.")
        self._refresh_accounts(); self._refresh_categories()
        self.refresh_dashboard()

    def refresh_dashboard(self):
        # Collect filters
        acc_filter = None if self.cb_account.currentIndex() == 0 else self.cb_account.currentText()
        cat_filter = None if self.cb_category.currentIndex() == 0 else self.cb_category.currentText()
        start_dt = datetime.datetime.combine(self.date_from.date().toPyDate(), datetime.time.min)
        end_dt   = datetime.datetime.combine(self.date_to.date().toPyDate(), datetime.time.max)

        # --- Pie: balances by account (overall; not filtered by date to نشان موجودی لحظه‌ای) ---
        self._draw_pie(self.acc.balances())

        # --- Bar: expenses by category in range (filtered) ---
        expenses = self.acc.expenses_by_category(start_dt, end_dt, acc_filter)
        # اگر کاربر دسته خاصی انتخاب کرده، فقط همان را نمایش دهیم
        if cat_filter:
            expenses = {k:v for k,v in expenses.items() if k == cat_filter}
        self._draw_bar(expenses, title="هزینه‌ها به تفکیک دسته در بازه انتخابی")

        # --- Line: daily net trend in range (filtered) ---
        net = self.acc.daily_net(start_dt, end_dt, acc_filter, cat_filter)
        self._draw_line(net, title="روند خالص روزانه (درآمد − هزینه)")

    # ---------- Chart Drawers ----------
    def _draw_pie(self, balances: dict):
        series = QPieSeries()
        if not balances:
            series.append("بدون داده", 1)
        else:
            # فیلتر صفرها برای خوانایی
            nonzero = {k:v for k,v in balances.items() if abs(v) > 1e-9}
            if not nonzero:
                series.append("صفر", 1)
            else:
                for acc, bal in nonzero.items():
                    series.append(acc, bal)

        chart = QChart()
        chart.setTitle("سهم موجودی حساب‌ها")
        chart.addSeries(series)
        chart.legend().setAlignment(Qt.AlignRight)
        self.chart_pie.setChart(chart)

    def _draw_bar(self, expenses: dict, title=""):
        chart = QChart()
        chart.setTitle(title if title else "Bar")
        if not expenses:
            series = QBarSeries()
            s = QBarSet("هیچ")
            s << 0
            series.append(s)
            chart.addSeries(series)
            axisX = QBarCategoryAxis(); axisX.append(["بدون داده"])
            axisY = QValueAxis(); axisY.setRange(0, 1)
            chart.addAxis(axisX, Qt.AlignBottom); chart.addAxis(axisY, Qt.AlignLeft)
            series.attachAxis(axisX); series.attachAxis(axisY)
        else:
            categories = list(expenses.keys())
            values = list(expenses.values())
            s = QBarSet("هزینه")
            for v in values: s << v
            series = QBarSeries(); series.append(s)
            chart.addSeries(series)
            axisX = QBarCategoryAxis(); axisX.append(categories)
            axisY = QValueAxis(); axisY.applyNiceNumbers()
            chart.addAxis(axisX, Qt.AlignBottom); chart.addAxis(axisY, Qt.AlignLeft)
            series.attachAxis(axisX); series.attachAxis(axisY)
        chart.legend().setVisible(False)
        self.chart_bar.setChart(chart)

    def _draw_line(self, daily_net: OrderedDict, title=""):
        chart = QChart(); chart.setTitle(title if title else "Line")
        series = QLineSeries()
        labels = []
        if not daily_net:
            series.append(0, 0)
            labels = ["بدون داده"]
            maxy = 1
        else:
            maxy = 0
            for idx, (day, val) in enumerate(daily_net.items()):
                series.append(float(idx), float(val))
                labels.append(day)
                maxy = max(maxy, abs(val))
        chart.addSeries(series)
        # X as categories (indices -> labels)
        axisX = QBarCategoryAxis(); axisX.append(labels if labels else ["بدون داده"])
        axisY = QValueAxis()
        axisY.applyNiceNumbers()
        if maxy == 0:
            axisY.setRange(-1, 1)
        chart.addAxis(axisX, Qt.AlignBottom); chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisX); series.attachAxis(axisY)
        chart.legend().setVisible(False)
        self.chart_line.setChart(chart)

# ----------------- App Entry -----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    users = UserSystem()
    win = LoginWindow(users)
    win.show()
    sys.exit(app.exec_())
