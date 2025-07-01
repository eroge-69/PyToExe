# tugas_gui.py

import sys
import json
from PyQt5.QtWidgets import *

class tgs:
    def __init__(self, n, k, d=False):
        self.n = n
        self.k = k
        self.d = d

    def dt(self):
        return {'n': self.n, 'k': self.k, 'd': self.d}

    @staticmethod
    def fd(dt):
        return tgs(dt['n'], dt['k'], dt['d'])

class mng:
    def __init__(self):
        self.t = []

    def add(self, t):
        self.t.append(t)

    def tg(self, i):
        if i >= 0 and i < len(self.t):
            self.t[i].d = not self.t[i].d

    def all(self):
        return self.t

    def sv(self, fn):
        f = open(fn, 'w')
        json.dump([x.dt() for x in self.t], f)
        f.close()

    def ld(self, fn):
        try:
            f = open(fn, 'r')
            d = json.load(f)
            self.t = [tgs.fd(x) for x in d]
            f.close()
        except:
            pass

class win(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("App")
        self.m = mng()
        self.m.ld('data.json')
        self.ui()
        self.up()

    def ui(self):
        self.v = QVBoxLayout()

        self.inp = QLineEdit()
        self.cat = QComboBox()
        self.cat.addItems(["Kuliah", "Ibu", "Atlet", "Seniman", "Coder"])
        self.btn = QPushButton("Tambah")
        self.lst = QListWidget()
        self.svbtn = QPushButton("Simpan")

        h = QHBoxLayout()
        h.addWidget(self.inp)
        h.addWidget(self.cat)
        h.addWidget(self.btn)

        self.v.addLayout(h)
        self.v.addWidget(self.lst)
        self.v.addWidget(self.svbtn)
        self.setLayout(self.v)

        self.btn.clicked.connect(self.tmbh)
        self.lst.itemClicked.connect(self.cnt)
        self.svbtn.clicked.connect(self.simpen)

    def tmbh(self):
        tx = self.inp.text()
        kt = self.cat.currentText()
        if tx != "":
            t = tgs(tx, kt)
            self.m.add(t)
            self.inp.setText("")
            self.up()

    def cnt(self, it):
        i = self.lst.row(it)
        self.m.tg(i)
        self.up()

    def up(self):
        self.lst.clear()
        for t in self.m.all():
            st = f"[{'X' if t.d else ' '}] {t.n} ({t.k})"
            self.lst.addItem(st)

    def simpen(self):
        self.m.sv('data.json')
        QMessageBox.information(self, "OK", "Disimpan!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = win()
    w.show()
    sys.exit(app.exec_())