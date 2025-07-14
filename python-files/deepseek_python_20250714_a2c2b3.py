import sys
import os
import webbrowser
import json
import tempfile
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, QFileDialog,
                             QGroupBox, QListWidget, QListWidgetItem, QTabWidget, QMessageBox,
                             QProgressBar, QCheckBox, QSizePolicy, QFrame)
from PyQt5.QtGui import QPixmap, QIcon, QFont, QPalette, QColor
from PyQt5.QtCore import Qt, QSize

# Sample data for property types and locations
PROPERTY_TYPES = ["شقة", "فيلا", "شاليه", "أرض", "مكتب", "محل تجاري", "عمارة"]
CITIES_EGYPT = ["القاهرة", "الجيزة", "الإسكندرية", "المنصورة", "طنطا", "المنيا", "أسيوط", "سوهاج", "الأقصر", "أسوان"]

class FacebookPublisherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real Estate Auto Publisher - مصر")
        self.setGeometry(100, 100, 900, 700)
        self.setWindowIcon(QIcon(self.create_temp_icon()))
        
        # Initialize Facebook credentials
        self.facebook_connected = False
        self.access_token = None
        self.user_id = None
        self.page_id = None
        self.ad_account_id = None
        
        # Initialize ad data
        self.ad_data = {
            "property_type": "",
            "city": "",
            "area": "",
            "price": "",
            "title": "",
            "description": "",
            "images": []
        }
        
        # Create UI
        self.init_ui()
        
        # Load saved data if exists
        self.load_saved_data()

    def init_ui(self):
        # Create tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create main tabs
        self.tab_connect = self.create_connect_tab()
        self.tab_create = self.create_ad_tab()
        self.tab_publish = self.create_publish_tab()
        
        self.tabs.addTab(self.tab_connect, "ربط الفيسبوك")
        self.tabs.addTab(self.tab_create, "إنشاء الإعلان")
        self.tabs.addTab(self.tab_publish, "النشر والنتائج")
        
        # Set styles
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                background: #e4e6eb;
                padding: 10px 20px;
                border: 1px solid #ccd0d5;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                border-color: #ccd0d5;
            }
            QGroupBox {
                border: 1px solid #dddfe2;
                border-radius: 8px;
                margin-top: 1em;
                padding-top: 10px;
                font-weight: bold;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #4267B2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #365899;
            }
            QPushButton:disabled {
                background-color: #a9b5c9;
            }
            QLineEdit, QTextEdit, QComboBox {
                border: 1px solid #dddfe2;
                border-radius: 4px;
                padding: 5px;
                background: white;
            }
            QListWidget {
                border: 1px solid #dddfe2;
                border-radius: 4px;
                background: white;
            }
            QProgressBar {
                border: 1px solid #dddfe2;
                border-radius: 4px;
                text-align: center;
                background: white;
            }
            QProgressBar::chunk {
                background-color: #42b72a;
            }
        """)

    def create_connect_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        
        # Header
        header = QLabel("ربط حساب الفيسبوك")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #1877f2; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Facebook connection box
        fb_box = QGroupBox("معلومات حساب الفيسبوك")
        fb_layout = QVBoxLayout()
        
        # Connection status
        self.connection_status = QLabel("الحالة: غير متصل")
        self.connection_status.setFont(QFont("Arial", 10))
        self.connection_status.setStyleSheet("color: #f02849; font-weight: bold;")
        fb_layout.addWidget(self.connection_status)
        
        # Email
        email_layout = QHBoxLayout()
        email_label = QLabel("البريد الإلكتروني:")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("أدخل بريدك الإلكتروني لحساب الفيسبوك")
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        fb_layout.addLayout(email_layout)
        
        # Password
        password_layout = QHBoxLayout()
        password_label = QLabel("كلمة المرور:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("أدخل كلمة مرور حساب الفيسبوك")
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        fb_layout.addLayout(password_layout)
        
        # Permissions info
        permissions_label = QLabel("سيطلب البرنامج الأذونات التالية:")
        permissions_label.setFont(QFont("Arial", 9, QFont.Bold))
        fb_layout.addWidget(permissions_label)
        
        permissions_list = QListWidget()
        permissions_list.addItems([
            "إدارة المحتوى على الصفحة",
            "النشر باسم الصفحة",
            "إدارة الإعلانات",
            "الوصول إلى مدير الإعلانات",
            "إدارة الأعمال"
        ])
        permissions_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        permissions_list.setMaximumHeight(120)
        fb_layout.addWidget(permissions_list)
        
        # Connect button
        connect_button = QPushButton("ربط حساب الفيسبوك")
        connect_button.clicked.connect(self.connect_to_facebook)
        fb_layout.addWidget(connect_button)
        
        fb_box.setLayout(fb_layout)
        layout.addWidget(fb_box)
        
        # Page selection
        self.page_box = QGroupBox("إعدادات الصفحة")
        self.page_box.setVisible(False)
        page_layout = QVBoxLayout()
        
        page_label = QLabel("اختر صفحة الفيسبوك للنشر:")
        page_layout.addWidget(page_label)
        
        self.page_combo = QComboBox()
        page_layout.addWidget(self.page_combo)
        
        ad_account_label = QLabel("اختر حساب مدير الإعلانات:")
        page_layout.addWidget(ad_account_label)
        
        self.ad_account_combo = QComboBox()
        page_layout.addWidget(self.ad_account_combo)
        
        save_button = QPushButton("حفظ الإعدادات")
        save_button.clicked.connect(self.save_page_settings)
        page_layout.addWidget(save_button)
        
        self.page_box.setLayout(page_layout)
        layout.addWidget(self.page_box)
        
        tab.setLayout(layout)
        return tab

    def create_ad_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        
        # Header
        header = QLabel("إنشاء الإعلان العقاري")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #1877f2; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Property details
        details_box = QGroupBox("تفاصيل العقار")
        details_layout = QVBoxLayout()
        
        # Property type
        type_layout = QHBoxLayout()
        type_label = QLabel("نوع العقار:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(PROPERTY_TYPES)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        details_layout.addLayout(type_layout)
        
        # Location
        location_layout = QHBoxLayout()
        city_label = QLabel("المدينة:")
        self.city_combo = QComboBox()
        self.city_combo.addItems(CITIES_EGYPT)
        
        area_label = QLabel("المنطقة:")
        self.area_input = QLineEdit()
        self.area_input.setPlaceholderText("اسم المنطقة/الحي")
        
        location_layout.addWidget(city_label)
        location_layout.addWidget(self.city_combo)
        location_layout.addWidget(area_label)
        location_layout.addWidget(self.area_input)
        details_layout.addLayout(location_layout)
        
        # Price
        price_layout = QHBoxLayout()
        price_label = QLabel("السعر (جنيه مصري):")
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("أدخل السعر")
        price_layout.addWidget(price_label)
        price_layout.addWidget(self.price_input)
        details_layout.addLayout(price_layout)
        
        details_box.setLayout(details_layout)
        layout.addWidget(details_box)
        
        # Ad content
        content_box = QGroupBox("محتوى الإعلان")
        content_layout = QVBoxLayout()
        
        # Title
        title_layout = QHBoxLayout()
        title_label = QLabel("عنوان الإعلان:")
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("أدخل عنوان جذاب للإعلان")
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_input)
        content_layout.addLayout(title_layout)
        
        # Description
        desc_label = QLabel("وصف العقار:")
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("أدخل وصفًا تفصيليًا للعقار...")
        self.desc_input.setMinimumHeight(100)
        content_layout.addWidget(desc_label)
        content_layout.addWidget(self.desc_input)
        
        content_box.setLayout(content_layout)
        layout.addWidget(content_box)
        
        # Images
        images_box = QGroupBox("صور العقار")
        images_layout = QVBoxLayout()
        
        # Image list
        self.image_list = QListWidget()
        self.image_list.setIconSize(QSize(80, 80))
        self.image_list.setViewMode(QListWidget.IconMode)
        self.image_list.setResizeMode(QListWidget.Adjust)
        self.image_list.setSpacing(10)
        images_layout.addWidget(self.image_list)
        
        # Buttons
        image_buttons_layout = QHBoxLayout()
        add_image_btn = QPushButton("إضافة صورة")
        add_image_btn.clicked.connect(self.add_image)
        remove_image_btn = QPushButton("إزالة الصورة المحددة")
        remove_image_btn.clicked.connect(self.remove_image)
        image_buttons_layout.addWidget(add_image_btn)
        image_buttons_layout.addWidget(remove_image_btn)
        images_layout.addLayout(image_buttons_layout)
        
        images_box.setLayout(images_layout)
        layout.addWidget(images_box)
        
        # Preview button
        preview_btn = QPushButton("معاينة الإعلان")
        preview_btn.clicked.connect(self.preview_ad)
        preview_btn.setStyleSheet("background-color: #42b72a;")
        layout.addWidget(preview_btn)
        
        tab.setLayout(layout)
        return tab

    def create_publish_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        
        # Header
        header = QLabel("نشر الإعلان")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #1877f2; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Preview section
        self.preview_box = QGroupBox("معاينة الإعلان")
        self.preview_box.setVisible(False)
        preview_layout = QVBoxLayout()
        
        # Preview content
        self.preview_frame = QFrame()
        self.preview_frame.setStyleSheet("background: white; border: 1px solid #dddfe2; border-radius: 8px;")
        preview_frame_layout = QVBoxLayout()
        
        # Images preview
        self.preview_images_layout = QHBoxLayout()
        preview_frame_layout.addLayout(self.preview_images_layout)
        
        # Details
        self.preview_details = QLabel()
        self.preview_details.setStyleSheet("font-size: 14px; padding: 15px;")
        self.preview_details.setWordWrap(True)
        preview_frame_layout.addWidget(self.preview_details)
        
        # Description
        self.preview_desc = QLabel()
        self.preview_desc.setStyleSheet("font-size: 14px; padding: 15px; border-top: 1px solid #dddfe2;")
        self.preview_desc.setWordWrap(True)
        preview_frame_layout.addWidget(self.preview_desc)
        
        self.preview_frame.setLayout(preview_frame_layout)
        preview_layout.addWidget(self.preview_frame)
        
        # Publish options
        options_layout = QHBoxLayout()
        self.publish_page_check = QCheckBox("النشر على صفحة الفيسبوك")
        self.publish_page_check.setChecked(True)
        self.publish_ads_check = QCheckBox("النشر على مدير الإعلانات")
        self.publish_ads_check.setChecked(True)
        options_layout.addWidget(self.publish_page_check)
        options_layout.addWidget(self.publish_ads_check)
        preview_layout.addLayout(options_layout)
        
        self.preview_box.setLayout(preview_layout)
        layout.addWidget(self.preview_box)
        
        # Publish button
        self.publish_btn = QPushButton("نشر الإعلان الآن")
        self.publish_btn.setStyleSheet("background-color: #42b72a; font-size: 16px; padding: 12px;")
        self.publish_btn.clicked.connect(self.publish_ad)
        self.publish_btn.setEnabled(False)
        layout.addWidget(self.publish_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Results section
        self.results_box = QGroupBox("نتائج النشر")
        self.results_box.setVisible(False)
        results_layout = QVBoxLayout()
        
        success_label = QLabel("تم نشر الإعلان بنجاح!")
        success_label.setStyleSheet("color: #42b72a; font-weight: bold; font-size: 16px;")
        results_layout.addWidget(success_label)
        
        results_layout.addWidget(QLabel("روابط الإعلان المنشور:"))
        
        self.page_link_label = QLabel()
        self.page_link_label.setOpenExternalLinks(True)
        results_layout.addWidget(self.page_link_label)
        
        self.ads_link_label = QLabel()
        self.ads_link_label.setOpenExternalLinks(True)
        results_layout.addWidget(self.ads_link_label)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        new_ad_btn = QPushButton("إنشاء إعلان جديد")
        new_ad_btn.clicked.connect(self.create_new_ad)
        buttons_layout.addWidget(new_ad_btn)
        
        open_facebook_btn = QPushButton("فتح الفيسبوك")
        open_facebook_btn.clicked.connect(self.open_facebook)
        buttons_layout.addWidget(open_facebook_btn)
        
        results_layout.addLayout(buttons_layout)
        self.results_box.setLayout(results_layout)
        layout.addWidget(self.results_box)
        
        # Add stretch to push everything up
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab

    def connect_to_facebook(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        
        if not email or not password:
            QMessageBox.warning(self, "بيانات ناقصة", "يرجى إدخال البريد الإلكتروني وكلمة المرور")
            return
        
        # Simulate Facebook connection
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Simulate connection progress
        for i in range(5):
            self.progress_bar.setValue(i * 20)
            QApplication.processEvents()
            
        # Set connection status
        self.facebook_connected = True
        self.connection_status.setText("الحالة: متصل بنجاح")
        self.connection_status.setStyleSheet("color: #42b72a; font-weight: bold;")
        
        # Show page selection
        self.page_box.setVisible(True)
        
        # Populate with sample pages
        self.page_combo.clear()
        self.page_combo.addItems(["صفحة العقارات الخاصة بي", "صفحة عقارات الشركة"])
        
        self.ad_account_combo.clear()
        self.ad_account_combo.addItems(["حساب مدير الإعلانات الشخصي"])
        
        # Enable other tabs
        self.tabs.setTabEnabled(1, True)
        
        self.progress_bar.setValue(100)
        
        # Show success message
        QMessageBox.information(self, "تم الاتصال", "تم ربط حساب الفيسبوك بنجاح!\nتم منح جميع الأذونات المطلوبة.")
        
        # Save credentials
        self.save_facebook_credentials(email)

    def save_page_settings(self):
        selected_page = self.page_combo.currentText()
        selected_ad_account = self.ad_account_combo.currentText()
        
        # Save page and ad account IDs
        self.page_id = "123456789"  # Simulated page ID
        self.ad_account_id = "act_987654321"  # Simulated ad account ID
        
        QMessageBox.information(self, "تم الحفظ", f"تم حفظ إعدادات الصفحة:\nالصفحة: {selected_page}\nحساب الإعلانات: {selected_ad_account}")

    def add_image(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "اختر صور العقار", "", 
            "الصور (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_paths:
            for path in file_paths:
                if len(self.ad_data["images"]) >= 10:
                    QMessageBox.warning(self, "حد الصور", "يمكنك إضافة 10 صور كحد أقصى")
                    break
                
                # Add to data
                self.ad_data["images"].append(path)
                
                # Add to list widget
                item = QListWidgetItem()
                item.setIcon(QIcon(path))
                item.setText(os.path.basename(path))
                self.image_list.addItem(item)

    def remove_image(self):
        selected_items = self.image_list.selectedItems()
        if not selected_items:
            return
        
        for item in selected_items:
            row = self.image_list.row(item)
            self.image_list.takeItem(row)
            del self.ad_data["images"][row]

    def preview_ad(self):
        # Validate inputs
        if not self.validate_ad_data():
            return
        
        # Update ad data
        self.update_ad_data()
        
        # Show preview
        self.preview_box.setVisible(True)
        self.publish_btn.setEnabled(True)
        self.tabs.setCurrentIndex(2)  # Switch to publish tab
        
        # Clear previous preview images
        for i in reversed(range(self.preview_images_layout.count())):
            widget = self.preview_images_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Add images to preview
        for img_path in self.ad_data["images"][:3]:  # Show up to 3 images
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                # Scale image for preview
                pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                img_label = QLabel()
                img_label.setPixmap(pixmap)
                img_label.setAlignment(Qt.AlignCenter)
                img_label.setStyleSheet("border: 1px solid #dddfe2; margin: 5px;")
                self.preview_images_layout.addWidget(img_label)
        
        # Add details to preview
        details_html = f"""
        <div style='font-size: 16px; font-weight: bold; margin-bottom: 10px;'>{self.ad_data['title']}</div>
        <div><b>نوع العقار:</b> {self.ad_data['property_type']}</div>
        <div><b>المكان:</b> {self.ad_data['city']} - {self.ad_data['area']}</div>
        <div style='color: #f02849; font-size: 18px; font-weight: bold; margin-top: 10px;'>
            السعر: {self.ad_data['price']} جنيه مصري
        </div>
        """
        self.preview_details.setText(details_html)
        
        # Add description
        self.preview_desc.setText(self.ad_data['description'])

    def validate_ad_data(self):
        if not self.ad_data["images"]:
            QMessageBox.warning(self, "صور ناقصة", "يرجى إضافة صورة واحدة على الأقل للعقار")
            return False
            
        if not self.title_input.text().strip():
            QMessageBox.warning(self, "عنوان ناقص", "يرجى إدخال عنوان للإعلان")
            return False
            
        if not self.area_input.text().strip():
            QMessageBox.warning(self, "منطقة ناقصة", "يرجى إدخال المنطقة/الحي للعقار")
            return False
            
        try:
            float(self.price_input.text().replace(",", ""))
        except ValueError:
            QMessageBox.warning(self, "سعر غير صالح", "يرجى إدخال سعر صحيح للعقار")
            return False
            
        return True

    def update_ad_data(self):
        self.ad_data = {
            "property_type": self.type_combo.currentText(),
            "city": self.city_combo.currentText(),
            "area": self.area_input.text(),
            "price": "{:,.0f}".format(float(self.price_input.text().replace(",", ""))),
            "title": self.title_input.text(),
            "description": self.desc_input.toPlainText(),
            "images": self.ad_data["images"]
        }

    def publish_ad(self):
        if not self.facebook_connected:
            QMessageBox.warning(self, "غير متصل", "يرجى ربط حساب الفيسبوك أولاً")
            self.tabs.setCurrentIndex(0)
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Simulate publishing process
        steps = [
            ("جاري التحضير للنشر", 10),
            ("جاري تحميل الصور", 30),
            ("جاري إنشاء الإعلان على الصفحة", 60),
            ("جاري إنشاء الإعلان في مدير الإعلانات", 90),
            ("جاري إنشاء الروابط", 100)
        ]
        
        for step, value in steps:
            self.progress_bar.setValue(value)
            self.statusBar().showMessage(step)
            QApplication.processEvents()
            
        # Simulate delay for each step
            QApplication.processEvents()
        
        # Generate results
        page_link = "https://www.facebook.com/123456789/posts/987654321"
        ads_link = "https://business.facebook.com/adsmanager/manage/ads?act=987654321"
        
        # Show results
        self.results_box.setVisible(True)
        self.page_link_label.setText(
            f"<a href='{page_link}'>رابط الإعلان على صفحة الفيسبوك</a>"
        )
        self.ads_link_label.setText(
            f"<a href='{ads_link}'>رابط الإعلان في مدير الإعلانات</a>"
        )
        
        # Save the ad data
        self.save_ad_data()
        
        self.statusBar().showMessage("تم النشر بنجاح!", 5000)

    def create_new_ad(self):
        # Reset the create ad tab
        self.type_combo.setCurrentIndex(0)
        self.city_combo.setCurrentIndex(0)
        self.area_input.clear()
        self.price_input.clear()
        self.title_input.clear()
        self.desc_input.clear()
        
        # Clear images
        self.ad_data["images"] = []
        self.image_list.clear()
        
        # Hide results
        self.results_box.setVisible(False)
        self.preview_box.setVisible(False)
        self.progress_bar.setVisible(False)
        self.publish_btn.setEnabled(False)
        
        # Switch to create tab
        self.tabs.setCurrentIndex(1)

    def open_facebook(self):
        webbrowser.open("https://www.facebook.com")

    def save_facebook_credentials(self, email):
        # In a real app, you would securely store this
        data = {
            "email": email,
            "last_login": datetime.now().isoformat(),
            "page_id": self.page_id,
            "ad_account_id": self.ad_account_id
        }
        
        # Save to temp file (in a real app, use proper secure storage)
        with open(os.path.join(tempfile.gettempdir(), "fb_publisher.json"), "w") as f:
            json.dump(data, f)

    def save_ad_data(self):
        # Save ad data to temp file
        data = {
            "ad": self.ad_data,
            "timestamp": datetime.now().isoformat(),
            "page_link": "https://www.facebook.com/123456789/posts/987654321",
            "ads_link": "https://business.facebook.com/adsmanager/manage/ads?act=987654321"
        }
        
        with open(os.path.join(tempfile.gettempdir(), "fb_ad_data.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    def load_saved_data(self):
        # Try to load saved credentials
        try:
            cred_path = os.path.join(tempfile.gettempdir(), "fb_publisher.json")
            if os.path.exists(cred_path):
                with open(cred_path, "r") as f:
                    data = json.load(f)
                    self.email_input.setText(data.get("email", ""))
                    self.facebook_connected = True
                    self.connection_status.setText("الحالة: جاهز للاتصال")
                    self.connection_status.setStyleSheet("color: #42b72a; font-weight: bold;")
                    self.tabs.setTabEnabled(1, True)
        except:
            pass

    def create_temp_icon(self):
        # Create a temporary icon file
        icon_path = os.path.join(tempfile.gettempdir(), "real_estate_icon.ico")
        return icon_path

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set app font
    font = QFont("Arial", 10)
    app.setFont(font)
    
    window = FacebookPublisherApp()
    window.show()
    sys.exit(app.exec_())