import sys
from PyQt5 import QtWidgets, QtGui, QtCore, QtPrintSupport

# Try to import QPdfDocument from Qt if available
try:
    from PyQt5.QtPdf import QPdfDocument
    QT_PDF_AVAILABLE = True
except ImportError:
    QT_PDF_AVAILABLE = False

# Fallback import for PyMuPDF
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


class QuadrantPreview(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 400)
        self.images = [None] * 4
        self.selected_idx = None  # for click-to-swap
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent, True)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)

        # Soft background
        bg = QtGui.QLinearGradient(0, 0, 0, self.height())
        bg.setColorAt(0.0, QtGui.QColor("#fafbff"))
        bg.setColorAt(1.0, QtGui.QColor("#f2f4f8"))
        painter.fillRect(self.rect(), bg)

        # Card-like surface with rounded corners
        card_rect = self.rect().adjusted(12, 12, -12, -12)
        card_path = QtGui.QPainterPath()
        card_path.addRoundedRect(QtCore.QRectF(card_rect), 14, 14)
        painter.fillPath(card_path, QtGui.QBrush(QtGui.QColor("#ffffff")))
        painter.setPen(QtGui.QPen(QtGui.QColor("#e5e7eb")))
        painter.drawPath(card_path)

        # Inner drawing area
        inset = 18
        draw_rect = card_rect.adjusted(inset, inset, -inset, -inset)

        w = draw_rect.width() // 2
        h = draw_rect.height() // 2

        # Faint quadrant dividers
        div_pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 40), 1)
        painter.setPen(div_pen)
        painter.drawLine(draw_rect.center().x(), draw_rect.top(),
                         draw_rect.center().x(), draw_rect.bottom())
        painter.drawLine(draw_rect.left(), draw_rect.center().y(),
                         draw_rect.right(), draw_rect.center().y())

        # Quadrant borders & images
        pen_default = QtGui.QPen(QtGui.QColor("#d1d5db"), 2)
        pen_sel = QtGui.QPen(QtGui.QColor("#2563eb"), 4)

        for i in range(4):
            x = draw_rect.x() + (i % 2) * w
            y = draw_rect.y() + (i // 2) * h
            rect = QtCore.QRect(x, y, w, h)

            # Rounded corners per quadrant
            r = 10
            path = QtGui.QPainterPath()
            path.addRoundedRect(QtCore.QRectF(rect.adjusted(6, 6, -6, -6)), r, r)
            painter.setPen(pen_sel if self.selected_idx == i else pen_default)
            painter.drawPath(path)

            img = self.images[i]
            if img:
                # Clip to rounded rect for cleaner look
                painter.save()
                clip = QtGui.QPainterPath()
                clip.addRoundedRect(QtCore.QRectF(rect.adjusted(10, 10, -10, -10)), r - 4, r - 4)
                painter.setClipPath(clip)
                scaled = img.scaled(rect.width() - 20, rect.height() - 20,
                                    QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                px = rect.x() + (rect.width() - scaled.width()) // 2
                py = rect.y() + (rect.height() - scaled.height()) // 2
                painter.drawImage(QtCore.QPoint(px, py), scaled)
                painter.restore()
            else:
                # Gentle placeholder hint
                painter.save()
                painter.setPen(QtGui.QPen(QtGui.QColor("#9ca3af")))
                f = painter.font()
                f.setPointSize(f.pointSize() + 1)
                painter.setFont(f)
                hint = f"Quadrant {i+1}"
                painter.drawText(rect, QtCore.Qt.AlignCenter, hint)
                painter.restore()

        # Empty-state helper text
        if not any(self.images):
            painter.save()
            painter.setPen(QtGui.QPen(QtGui.QColor("#6b7280")))
            f = painter.font()
            f.setPointSize(f.pointSize() + 2)
            f.setWeight(QtGui.QFont.DemiBold)
            painter.setFont(f)
            tip = "Use “Load Files…” to place up to 4 PDFs or images"
            painter.drawText(card_rect, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom, tip)
            painter.restore()

        painter.end()

    def mousePressEvent(self, event):
        # Map click to quadrant based on inner draw rect used above
        outer = self.rect().adjusted(12 + 18, 12 + 18, -12 - 18, -12 - 18)
        if outer.width() <= 0 or outer.height() <= 0:
            return
        w = outer.width() // 2
        h = outer.height() // 2

        pos = event.pos()
        if not outer.contains(pos):
            return
        local = pos - outer.topLeft()
        idx = (local.y() // h) * 2 + (local.x() // w)

        if idx < 0 or idx > 3:
            return
        if self.selected_idx is None:
            if self.images[idx] is not None:
                self.selected_idx = idx
        else:
            if idx != self.selected_idx:
                self.images[self.selected_idx], self.images[idx] = \
                    self.images[idx], self.images[self.selected_idx]
            self.selected_idx = None
        self.update()


class QuadrantPrinter(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("A4 Quadrant Printer")

        # Defaults (you can change them in the GUI controls)
        self.render_dpi = 300  # PDF -> image DPI
        self.print_dpi  = 300  # requested printer DPI

        self._apply_theme()
        self._setup_ui()

    # --- Icon helper (robust to older PyQt/Qt builds) ---
    def _std_icon(self, *role_names):
        """
        Return a standard icon for the first available QStyle.StandardPixmap in role_names.
        role_names should be strings like "SP_DialogPrintButton".
        """
        style = self.style()
        for name in role_names:
            role = getattr(QtWidgets.QStyle, name, None)
            if role is not None:
                return style.standardIcon(role)
        # Final fallback
        return style.standardIcon(QtWidgets.QStyle.SP_FileIcon)

    def _apply_theme(self):
        # Consistent, modern base style
        QtWidgets.QApplication.setStyle("Fusion")

        # Window icon with fallback chain
        self.setWindowIcon(self._std_icon(
            "SP_DesktopIcon",
            "SP_ComputerIcon",
            "SP_DriveHDIcon"
        ))

        # Global stylesheet for a clean, rounded, modern look
        self.setStyleSheet("""
            QWidget {
                font-family: "Segoe UI", "Noto Sans", "Helvetica Neue", Arial;
                font-size: 10pt;
                color: #111827;
            }
            QMainWindow {
                background: #f6f7fb;
            }
            QLabel#Heading {
                font-size: 16pt;
                font-weight: 700;
                color: #0f172a;
            }
            QLabel#Subheading {
                color: #64748b;
            }
            QFrame#Card {
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 14px;
            }
            QPushButton {
                background: #111827;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                padding: 8px 14px;
            }
            QPushButton:hover { background: #0f1627; }
            QPushButton:pressed { background: #0b1220; }
            QPushButton:disabled {
                background: #d1d5db; color: #6b7280;
            }
            QPushButton#Ghost {
                background: #eef2ff;
                color: #1e3a8a;
            }
            QSpinBox {
                background: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 4px 8px;
                min-width: 90px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 18px;
                background: transparent;
                border: none;
                padding: 0px;
            }
            QToolTip {
                background-color: #111827;
                color: #ffffff;
                border: 0px;
                padding: 6px 8px;
                border-radius: 6px;
            }
        """)

    def _card(self):
        card = QtWidgets.QFrame()
        card.setObjectName("Card")
        effect = QtWidgets.QGraphicsDropShadowEffect(card)
        effect.setOffset(0, 10)
        effect.setBlurRadius(28)
        effect.setColor(QtGui.QColor(17, 24, 39, 40))  # rgba shadow
        card.setGraphicsEffect(effect)
        return card

    def _setup_ui(self):
        central = QtWidgets.QWidget()
        root = QtWidgets.QVBoxLayout(central)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(16)

        # Header
        header = QtWidgets.QHBoxLayout()
        icon_lbl = QtWidgets.QLabel()
        # Header icon with safe fallbacks
        icon = self._std_icon(
            "SP_FileDialogInfoView",
            "SP_MessageBoxInformation",
            "SP_DialogHelpButton"
        )
        pix = icon.pixmap(28, 28)
        icon_lbl.setPixmap(pix)
        title = QtWidgets.QLabel("A4 Quadrant Printer")
        title.setObjectName("Heading")
        subtitle = QtWidgets.QLabel("Load up to four pages/images • Arrange with a click • Print in neat quadrants")
        subtitle.setObjectName("Subheading")
        title_col = QtWidgets.QVBoxLayout()
        title_col.setSpacing(2)
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        header.addWidget(icon_lbl, 0, QtCore.Qt.AlignTop)
        header.addSpacing(8)
        header.addLayout(title_col)
        header.addStretch()
        root.addLayout(header)

        # Preview inside a card
        preview_card = self._card()
        pv_lay = QtWidgets.QVBoxLayout(preview_card)
        pv_lay.setContentsMargins(12, 12, 12, 12)
        self.preview = QuadrantPreview()
        pv_lay.addWidget(self.preview)
        root.addWidget(preview_card, 1)

        # Controls card
        controls_card = self._card()
        cc = QtWidgets.QGridLayout(controls_card)
        cc.setContentsMargins(16, 16, 16, 16)
        cc.setHorizontalSpacing(14)
        cc.setVerticalSpacing(12)

        # --- Controls row (Render DPI & Print DPI) ---
        render_lbl = QtWidgets.QLabel("Render DPI")
        self.render_dpi_spin = QtWidgets.QSpinBox()
        self.render_dpi_spin.setRange(72, 1200)
        self.render_dpi_spin.setSingleStep(24)
        self.render_dpi_spin.setValue(self.render_dpi)
        self.render_dpi_spin.setToolTip("DPI used when converting PDF pages to images (higher = sharper, slower).")
        self.render_dpi_spin.valueChanged.connect(lambda v: setattr(self, "render_dpi", int(v)))

        print_lbl = QtWidgets.QLabel("Print DPI")
        self.print_dpi_spin = QtWidgets.QSpinBox()
        self.print_dpi_spin.setRange(72, 2400)
        self.print_dpi_spin.setSingleStep(30)
        self.print_dpi_spin.setValue(self.print_dpi)
        self.print_dpi_spin.setToolTip("Requested printer resolution (driver may snap to supported modes).")
        self.print_dpi_spin.valueChanged.connect(lambda v: setattr(self, "print_dpi", int(v)))

        # Buttons row
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.setSpacing(10)
        load_btn = QtWidgets.QPushButton("  Load Files…")
        load_btn.setToolTip("Select up to 4 PDFs or images")
        load_btn.setIcon(self._std_icon(
            "SP_DialogOpenButton",
            "SP_DirOpenIcon",
            "SP_FileDialogStart"
        ))
        load_btn.clicked.connect(self.load_files)

        print_btn = QtWidgets.QPushButton("  Print Preview & Print")
        print_btn.setObjectName("Ghost")
        print_btn.setToolTip("Open print preview and print the arranged quadrants")
        # Fallback chain: some Qt builds don't have SP_DialogPrintButton
        print_btn.setIcon(self._std_icon(
            "SP_DialogPrintButton",
            "SP_DialogApplyButton",
            "SP_DialogOkButton"
        ))
        print_btn.clicked.connect(self.handle_print)

        btn_row.addWidget(load_btn)
        btn_row.addWidget(print_btn)
        btn_row.addStretch()

        # Layout controls into grid (nice alignment)
        cc.addWidget(render_lbl,            0, 0)
        cc.addWidget(self.render_dpi_spin,  0, 1)
        cc.addWidget(print_lbl,             0, 2)
        cc.addWidget(self.print_dpi_spin,   0, 3)
        cc.addLayout(btn_row,               0, 4, 1, 2)
        cc.setColumnStretch(5, 1)

        root.addWidget(controls_card)
        self.setCentralWidget(central)

    def load_files(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        dialog.setNameFilters(["PDF Files (*.pdf)", "Images (*.png *.jpg *.jpeg)"])
        if dialog.exec_():
            paths = dialog.selectedFiles()[:4]
            self.preview.images = [None] * 4
            for i, path in enumerate(paths):
                img = load_image_from_path(path, self.render_dpi)  # <-- use GUI-selected render DPI
                if img:
                    # rotate PDF pages so they display upright
                    if path.lower().endswith('.pdf'):
                        img = img.transformed(QtGui.QTransform().rotate(90))
                    self.preview.images[i] = img
                else:
                    QtWidgets.QMessageBox.warning(self, "Load Error",
                                                  f"Failed to load: {path}")
            self.preview.selected_idx = None
            self.preview.update()

    def handle_print(self):
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        printer.setPageSize(QtPrintSupport.QPrinter.A4)
        printer.setOrientation(QtPrintSupport.QPrinter.Portrait)

        # Apply requested print DPI from GUI
        printer.setResolution(self.print_dpi)

        # allow full-bleed so pageRect() is entire sheet
        printer.setFullPage(True)
        # zero out device margins
        printer.setPageMargins(0, 0, 0, 0, QtPrintSupport.QPrinter.Millimeter)

        preview = QtPrintSupport.QPrintPreviewDialog(printer, self)
        preview.setWindowTitle("Print Preview with Margins")
        preview.paintRequested.connect(self.print_to_printer)
        preview.exec_()

    def print_to_printer(self, printer):
        painter = QtGui.QPainter(printer)
        rect = printer.pageRect()  # now full A4

        # inner margin of 5 mm
        margin_mm = 5
        dpi = printer.resolution()
        margin = int(dpi * margin_mm / 25.4)

        w_half = rect.width() // 2
        h_half = rect.height() // 2

        for i, img in enumerate(self.preview.images):
            if not img:
                continue

            row, col = divmod(i, 2)
            x0 = rect.x() + col * w_half + margin
            y0 = rect.y() + row * h_half + margin
            w   = w_half - 2 * margin
            h   = h_half - 2 * margin

            # scale + center in quadrant
            scaled = img.scaled(w, h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            px = x0 + (w - scaled.width()) // 2
            py = y0 + (h - scaled.height()) // 2

            painter.drawImage(QtCore.QPoint(px, py), scaled)

        painter.end()


def load_image_from_path(path, render_dpi=300):
    """
    Loads an image or rasterizes the first page of a PDF at the given render_dpi.
    """
    # PDF via Qt
    if path.lower().endswith('.pdf') and QT_PDF_AVAILABLE:
        try:
            doc = QPdfDocument()
            status = doc.load(path)
            if status == QPdfDocument.NoError and doc.pageCount() > 0:
                page = doc.page(0)
                return page.renderToImage(resolution=float(render_dpi))
        except Exception:
            pass

    # PDF via PyMuPDF
    if path.lower().endswith('.pdf') and PYMUPDF_AVAILABLE:
        try:
            pdf = fitz.open(path)
            if pdf.page_count > 0:
                page = pdf.load_page(0)
                scale = float(render_dpi) / 72.0  # 72 DPI base
                pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
                fmt = (QtGui.QImage.Format_RGBA8888
                       if pix.alpha else QtGui.QImage.Format_RGB888)
                return QtGui.QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
        except Exception:
            pass

    # Image files
    img = QtGui.QImage(path)
    return img if not img.isNull() else None


if __name__ == '__main__':
    import os
    # --- High-DPI (crisper preview/printing on Windows) ---
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "PassThrough"
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    # ------------------------------------------------------

    app = QtWidgets.QApplication(sys.argv)
    window = QuadrantPrinter()
    window.show()
    sys.exit(app.exec_())
