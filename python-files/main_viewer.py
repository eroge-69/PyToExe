import sys
import os
import json # برای ذخیره و بازیابی وضعیت
import numpy as np
import pyvista as pv
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QVBoxLayout, QWidget, QToolBar,
    QStatusBar, QDockWidget, QListWidget, QListWidgetItem, QCheckBox,
    QPushButton, QHBoxLayout, QLabel, QFormLayout, QColorDialog, QSlider,
    QGroupBox # برای گروه‌بندی کنترل‌ها در پنل‌ها
)
from PySide6.QtGui import QAction, QIcon, QColor
from PySide6.QtCore import Qt, QSize, QSettings # QSettings برای ذخیره چیدمان UI

# --- پیکربندی اولیه PyVista ---
pv.set_plot_theme("document") # تم مناسب برای اسکرین‌شات و نمایش
pv.set_backend("qt") # اطمینان از استفاده از بک‌اند Qt برای PyVista

class ModelManager:
    """
    کلاسی برای مدیریت متمرکز مدل‌های بارگذاری شده، وضعیت آن‌ها (مانند نمایش یا عدم نمایش، رنگ)،
    و عملیات مرتبط با آن‌ها مانند افزودن، حذف و برش.
    """
    def __init__(self, plotter):
        self.plotter = plotter
        self.models = {}  # دیکشنری برای نگهداری اطلاعات هر مدل: {model_id: model_data}

    def add_model(self, file_path):
        """
        یک مدل جدید را از مسیر فایل داده شده بارگذاری کرده و به صحنه اضافه می‌کند.
        اطلاعات مدل شامل مسیر، آبجکت actor، مش PyVista، وضعیت نمایش و نام را برمی‌گرداند.
        """
        try:
            mesh = pv.read(file_path)
            model_id = file_path  # استفاده از مسیر فایل به عنوان شناسه یکتا برای سادگی
            default_color = '#CCCCCC'  # رنگ پیش‌فرض برای مدل‌ها
            
            # افزودن مش به صحنه با استفاده از PyVista plotter
            actor = self.plotter.add_mesh(
                mesh, 
                name=model_id,       # نام برای شناسایی actor
                style='surface',     # نمایش به صورت سطح
                color=default_color,
                show_edges=False,    # عدم نمایش لبه‌ها به طور پیش‌فرض
                rgba=True            # فعال کردن شفافیت در صورت وجود در متریال مدل
            )
            
            # ذخیره اطلاعات مدل
            model_data = {
                'path': file_path,
                'actor': actor,          # مرجع به PyVista actor
                'mesh': mesh,            # مرجع به PyVista mesh
                'visible': True,         # وضعیت نمایش اولیه
                'name': os.path.basename(file_path), # نام فایل برای نمایش
                'original_color': default_color,     # رنگ اصلی برای بازگردانی پس از هایلایت
                'is_highlighted': False  # وضعیت هایلایت بودن
            }
            self.models[model_id] = model_data
            self.plotter.reset_camera() # تنظیم مجدد دوربین برای نمایش مدل جدید
            return model_id, model_data
        except Exception as e:
            print(f"خطا در بارگذاری مدل {file_path}: {e}")
            return None, None

    def get_model_by_actor(self, actor):
        """مدل را بر اساس آبجکت actor آن در صحنه پیدا می‌کند."""
        for model_id, model_data in self.models.items():
            if model_data['actor'] == actor:
                return model_id, model_data
        return None, None

    def remove_model(self, model_id):
        """یک مدل را از صحنه و لیست مدیریت داخلی حذف می‌کند."""
        if model_id in self.models:
            self.plotter.remove_actor(self.models[model_id]['actor']) # حذف از صحنه PyVista
            del self.models[model_id] # حذف از دیکشنری داخلی
            return True
        return False

    def set_visibility(self, model_id, visible):
        """وضعیت نمایش (مرئی/نامرئی) یک مدل را تنظیم می‌کند."""
        if model_id in self.models:
            self.models[model_id]['actor'].SetVisibility(visible)
            self.models[model_id]['visible'] = visible
            self.plotter.render() # رندر مجدد صحنه برای اعمال تغییرات

    def clip_all_models(self, plane):
        """یک صفحه برش (clipping plane) را به تمام مدل‌های مرئی در صحنه اعمال می‌کند."""
        for model_data in self.models.values():
            if model_data['visible']:
                # هر actor یک mapper دارد که مسئول رندر کردن آن است. صفحات برش به mapper اعمال می‌شوند.
                model_data['actor'].mapper.add_clipping_plane(plane)

    def clear_all_clipping(self):
        """تمام صفحات برش اعمال شده را از تمام مدل‌ها حذف می‌کند."""
        for actor in self.plotter.actors.values(): # دسترسی به تمام actor های موجود در صحنه
             if hasattr(actor, 'mapper') and actor.mapper is not None:
                actor.mapper.remove_all_clipping_planes()
        self.plotter.render()


class MainWindow(QMainWindow):
    """
    پنجره اصلی برنامه نمایشگر سه‌بعدی که تمام رابط کاربری و منطق برنامه را در خود جای داده است.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("نمایشگر حرفه‌ای سه‌بعدی (v2.0 - نهایی)")
        self.setGeometry(50, 50, 1800, 1000) # موقعیت و اندازه اولیه پنجره
        
        # --- مدیریت وضعیت‌های مختلف برنامه ---
        self.current_mode = 'navigation'  # حالت‌های ممکن: 'navigation', 'measure', 'slicing', 'selection'
        self.measurement_points = []      # نقاط انتخاب شده برای اندازه‌گیری
        self.measurement_actors = []      # actor های مربوط به اندازه‌گیری (نقاط، خط، برچسب)
        self.slicing_widget = None        # ویجت تعاملی برش PyVista
        self.selected_model_id = None     # شناسه مدل انتخاب شده برای نمایش مشخصات

        # --- ساختار اصلی رابط کاربری ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0) # حذف حاشیه اضافی
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # --- راه‌اندازی نمایشگر سه‌بعدی PyVista و مدیر مدل ---
        self.plotter = pv.QtInteractor(self.central_widget) # جاسازی PyVista در Qt
        self.layout.addWidget(self.plotter.interactor)
        self.model_manager = ModelManager(self.plotter)

        # --- راه‌اندازی بخش‌های مختلف برنامه ---
        self.setup_scene()                  # تنظیمات اولیه صحنه
        self.create_toolbar()               # نوار ابزار اصلی
        self.create_scene_controls_dock()   # پنل کنترل صحنه
        self.create_properties_dock()       # پنل مشخصات مدل
        self.create_models_dock()           # پنل مدیریت مدل‌ها
        
        # --- تب‌بندی پنل‌های کناری برای سازماندهی بهتر ---
        self.tabifyDockWidget(self.props_dock, self.scene_controls_dock)
        self.props_dock.raise_() # پنل مشخصات به طور پیش‌فرض در بالا نمایش داده شود
        
        # --- بازیابی چیدمان پنجره از اجرای قبلی با استفاده از QSettings ---
        self.settings = QSettings("MyCompany", "3DViewerApp") # نام شرکت و برنامه برای ذخیره تنظیمات
        self.restoreGeometry(self.settings.value("mainWindowGeometry", self.saveGeometry()))
        self.restoreState(self.settings.value("mainWindowState", self.saveState()))

        self.status_bar.showMessage("آماده. یک پروژه را بارگذاری کنید یا مدل جدیدی باز کنید.")

    def setup_scene(self):
        """تنظیمات اولیه صحنه سه‌بعدی مانند پس‌زمینه، نور، شبکه و محورها را انجام می‌دهد."""
        self.plotter.set_background('darkgrey') # رنگ پس‌زمینه پیش‌فرض
        
        # نگهداری یک مرجع به نور اصلی صحنه برای کنترل آن
        # PyVista به طور پیش‌فرض یک نور headlight اضافه می‌کند.
        self.main_light = pv.Light(light_type='headlight', intensity=1.0)
        self.plotter.add_light(self.main_light)
        
        self.grid_actor = self.plotter.add_grid(name='grid', color='#888888') # شبکه کف
        self.plotter.show_axes() # نمایش محورهای مختصات
        self.plotter.enable_shadows() # فعال‌سازی سایه‌ها
        self.plotter.enable_anti_aliasing('ssaa') # فعال‌سازی anti-aliasing برای لبه‌های نرم‌تر
        
        # فعال‌سازی قابلیت کلیک برای انتخاب نقطه (برای اندازه‌گیری)
        self.plotter.enable_surface_picking(callback=self._handle_picked_point, show_point=False, left_clicking=True)
        # فعال‌سازی قابلیت کلیک برای انتخاب آبجکت کامل (actor) (برای نمایش مشخصات)
        self.plotter.enable_actor_picking(callback=self._handle_actor_picked, left_clicking=True)

    def create_toolbar(self):
        """نوار ابزار اصلی برنامه را با دکمه‌های عملیاتی ایجاد می‌کند."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # --- دکمه‌های مربوط به پروژه و فایل ---
        save_action = QAction(QIcon.fromTheme("document-save"), "ذخیره پروژه", self)
        save_action.setStatusTip("ذخیره وضعیت فعلی برنامه در یک فایل پروژه")
        save_action.triggered.connect(self._save_state)
        toolbar.addAction(save_action)

        load_action = QAction(QIcon.fromTheme("document-open"), "بارگذاری پروژه", self)
        load_action.setStatusTip("بارگذاری یک فایل پروژه ذخیره شده")
        load_action.triggered.connect(self._load_state)
        toolbar.addAction(load_action)
        toolbar.addSeparator()
        
        open_action = QAction(QIcon.fromTheme("list-add"), "افزودن مدل...", self) # آیکون استاندارد برای افزودن
        open_action.setStatusTip("بارگذاری یک یا چند فایل مدل سه‌بعدی جدید")
        open_action.triggered.connect(self.open_model_files)
        toolbar.addAction(open_action)
        
        reset_view_action = QAction(QIcon.fromTheme("view-refresh"), "بازنشانی دید", self)
        reset_view_action.setStatusTip("تنظیم مجدد دوربین به حالت پیش‌فرض برای نمایش تمام مدل‌ها")
        reset_view_action.triggered.connect(self.plotter.reset_camera)
        toolbar.addAction(reset_view_action)
        toolbar.addSeparator()
        
        # --- دکمه‌های مربوط به حالت‌های تعاملی برنامه ---
        self.select_action = QAction(QIcon.fromTheme("edit-select"), "انتخاب / مشخصات", self)
        self.select_action.setCheckable(True) # دکمه قابل انتخاب/لغو انتخاب
        self.select_action.setStatusTip("ورود به حالت انتخاب مدل برای نمایش مشخصات")
        self.select_action.triggered.connect(self._toggle_mode) # اتصال به تابع مدیریت حالت
        toolbar.addAction(self.select_action)
        
        self.measure_action = QAction(QIcon.fromTheme("draw-path"), "اندازه‌گیری", self)
        self.measure_action.setCheckable(True)
        self.measure_action.setStatusTip("ورود به حالت اندازه‌گیری فاصله بین دو نقطه")
        self.measure_action.triggered.connect(self._toggle_mode)
        toolbar.addAction(self.measure_action)
        
        self.slice_action = QAction(QIcon.fromTheme("transform-crop"), "برش", self) # آیکون استاندارد برای برش
        self.slice_action.setCheckable(True)
        self.slice_action.setStatusTip("فعال/غیرفعال کردن ویجت برش تعاملی مدل")
        self.slice_action.triggered.connect(self._toggle_mode)
        toolbar.addAction(self.slice_action)
        toolbar.addSeparator()
        
        # --- دکمه مربوط به پاک‌سازی ---
        clear_measure_action = QAction(QIcon.fromTheme("edit-clear"), "پاک کردن اندازه‌ها", self)
        clear_measure_action.setStatusTip("حذف تمام خطوط و نقاط اندازه‌گیری از صحنه")
        clear_measure_action.triggered.connect(self._clear_measurements)
        toolbar.addAction(clear_measure_action)

    # --- بخش ذخیره و بازیابی وضعیت کامل برنامه ---
    def _save_state(self):
        """تمام وضعیت فعلی برنامه (مدل‌ها، اندازه‌گیری‌ها، تنظیمات صحنه، دوربین) را در یک فایل JSON ذخیره می‌کند."""
        file_path, _ = QFileDialog.getSaveFileName(self, "ذخیره پروژه", "", "Python 3D Viewer Project (*.p3dv)")
        if not file_path: return

        # جمع‌آوری داده‌های اندازه‌گیری به صورت صحیح
        measurement_points_data = []
        i = 0
        # هر اندازه‌گیری شامل 4 actor است: نقطه اول، نقطه دوم، خط، برچسب
        while i < len(self.measurement_actors):
            if i + 1 < len(self.measurement_actors): # اطمینان از وجود دو نقطه
                p1_actor = self.measurement_actors[i] # این باید یک مش کره باشد
                p2_actor = self.measurement_actors[i+1] # این هم یک مش کره
                if hasattr(p1_actor, 'center') and hasattr(p2_actor, 'center'):
                     measurement_points_data.append({'p1': p1_actor.center.tolist(), 'p2': p2_actor.center.tolist()})
            i += 4 # حرکت به مجموعه بعدی اندازه‌گیری (2 نقطه + 1 خط + 1 برچسب)
        
        state_data = {
            'models': [{'path': data['path'], 'visible': data['visible']} for data in self.model_manager.models.values()],
            'measurements': measurement_points_data,
            'camera': self.plotter.camera.to_dict(), # PyVista امکان ذخیره وضعیت دوربین را می‌دهد
            'scene_settings': {
                'background_color': self.plotter.background_color.name if self.plotter.background_color else 'darkgrey',
                'light_intensity': self.main_light.intensity if self.main_light else 1.0,
                'light_color': self.main_light.color if self.main_light else (1.0, 1.0, 1.0),
                'grid_visible': self.grid_actor.GetVisibility() if self.grid_actor else True,
                'axes_visible': self.plotter.axes_widget.GetEnabled() if self.plotter.axes_widget else True
            }
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=4)
            self.status_bar.showMessage(f"پروژه با موفقیت در {file_path} ذخیره شد.", 5000)
        except Exception as e:
            self.status_bar.showMessage(f"خطا در ذخیره پروژه: {e}", 5000)
            print(f"Save state error: {e}")

    def _load_state(self):
        """وضعیت برنامه را از یک فایل پروژه (.p3dv) بارگذاری می‌کند."""
        file_path, _ = QFileDialog.getOpenFileName(self, "بارگذاری پروژه", "", "Python 3D Viewer Project (*.p3dv)")
        if not file_path: return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                state_data = json.load(f)

            self._clear_all_scene() # پاک کردن کامل صحنه فعلی قبل از بارگذاری

            # بارگذاری مدل‌ها
            for model_info in state_data.get('models', []):
                self.load_model(model_info['path']) # این متد مدل را به model_manager و لیست UI اضافه می‌کند
                # تنظیم وضعیت نمایش پس از بارگذاری
                if model_info['path'] in self.model_manager.models:
                    self.model_manager.set_visibility(model_info['path'], model_info['visible'])
                    # به‌روزرسانی چک‌باکس در لیست UI
                    for i in range(self.model_list_widget.count()):
                        item = self.model_list_widget.item(i)
                        widget = self.model_list_widget.itemWidget(item)
                        # شناسه مدل (مسیر فایل) در tooltip لیبل ذخیره شده است
                        if widget.layout().itemAt(1).widget().toolTip() == model_info['path']:
                            checkbox = widget.layout().itemAt(0).widget()
                            checkbox.setChecked(model_info['visible'])
                            break
            
            # بازسازی اندازه‌گیری‌ها
            for meas_info in state_data.get('measurements', []):
                p1 = np.array(meas_info['p1']); p2 = np.array(meas_info['p2'])
                self._create_measurement_actors(p1, p2) # تابع کمکی برای ایجاد مجدد actor های اندازه‌گیری

            # بازیابی تنظیمات صحنه
            settings = state_data.get('scene_settings', {})
            self.plotter.set_background(settings.get('background_color', 'darkgrey'))
            if self.main_light:
                self.main_light.intensity = settings.get('light_intensity', 1.0)
                self.main_light.color = settings.get('light_color', (1.0, 1.0, 1.0))
            self.grid_checkbox.setChecked(settings.get('grid_visible', True)) # این تابع _toggle_grid را فراخوانی می‌کند
            self.axes_checkbox.setChecked(settings.get('axes_visible', True)) # این تابع _toggle_axes را فراخوانی می‌کند
            if self.main_light:
                self.light_intensity_slider.setValue(int(self.main_light.intensity * 100))

            # بازیابی وضعیت دوربین
            if 'camera' in state_data:
                self.plotter.camera.from_dict(state_data['camera'])

            self.status_bar.showMessage(f"پروژه {os.path.basename(file_path)} با موفقیت بارگذاری شد.", 5000)

        except Exception as e:
            self.status_bar.showMessage(f"خطا در بارگذاری پروژه: {e}", 5000)
            print(f"Load state error: {e}")

    def _clear_all_scene(self):
        """تمام محتویات صحنه (مدل‌ها، اندازه‌گیری‌ها) و لیست‌های UI مربوطه را پاک می‌کند."""
        self._clear_measurements()
        
        model_ids_to_remove = list(self.model_manager.models.keys())
        for model_id in model_ids_to_remove:
            self.model_manager.remove_model(model_id) # این از صحنه هم حذف می‌کند
        self.model_list_widget.clear() # پاک کردن لیست UI مدل‌ها
        
        self.selected_model_id = None
        self._update_properties_panel(None) # پاک کردن پنل مشخصات
        
        self.plotter.render()
        print("صحنه به طور کامل پاک شد.")
    
    # --- تابع کمکی برای ایجاد مجدد اِلِمان‌های بصری یک اندازه‌گیری ---
    def _create_measurement_actors(self, p1_coords, p2_coords):
        """
        با گرفتن مختصات دو نقطه، اِلِمان‌های بصری (دو کره، یک خط و یک برچسب فاصله)
        را برای یک اندازه‌گیری ایجاد کرده و به صحنه و لیست measurement_actors اضافه می‌کند.
        """
        p1 = np.array(p1_coords)
        p2 = np.array(p2_coords)
        
        # ایجاد کره‌ها برای نمایش نقاط
        point1_actor = self.plotter.add_mesh(pv.Sphere(radius=0.01, center=p1), color='red', render=False)
        point2_actor = self.plotter.add_mesh(pv.Sphere(radius=0.01, center=p2), color='red', render=False)
        
        # ایجاد خط بین نقاط
        line_actor = self.plotter.add_lines(np.array([p1, p2]), color='yellow', width=5, render=False)
        
        # محاسبه و نمایش فاصله
        distance = np.linalg.norm(p2 - p1)
        label_actor = self.plotter.add_point_labels(
            (p1 + p2) / 2, # موقعیت برچسب در وسط خط
            [f"{distance:.3f} متر"], 
            font_size=20, 
            shape=None, # عدم نمایش شکل پس‌زمینه برای برچسب
            text_color='yellow',
            render=False
        )
        # افزودن تمام actor های ایجاد شده به لیست برای مدیریت بعدی (مانند پاک کردن)
        self.measurement_actors.extend([point1_actor, point2_actor, line_actor, label_actor])
        self.plotter.render()


    # --- بخش مدیریت پنل‌های کناری (Docks) ---
    def create_scene_controls_dock(self):
        """پنل کناری برای کنترل تنظیمات بصری صحنه (پس‌زمینه، نور، راهنماها) را ایجاد می‌کند."""
        self.scene_controls_dock = QDockWidget("تنظیمات صحنه", self)
        container_widget = QWidget() # ویجت نگهدارنده برای چیدمان
        main_layout = QVBoxLayout(container_widget)
        
        # گروه کنترل‌های پس‌زمینه
        bg_group = QGroupBox("پس‌زمینه")
        bg_layout = QVBoxLayout(bg_group)
        change_bg_btn = QPushButton("تغییر رنگ پس‌زمینه")
        change_bg_btn.clicked.connect(self._change_background_color)
        bg_layout.addWidget(change_bg_btn)
        
        # گروه کنترل‌های نورپردازی
        light_group = QGroupBox("نورپردازی")
        light_layout = QFormLayout(light_group) # QFormLayout برای نمایش لیبل-مقدار مناسب است
        self.light_intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.light_intensity_slider.setRange(0, 200) # محدوده برای شدت نور (0.0 تا 2.0)
        self.light_intensity_slider.setValue(100)    # مقدار اولیه (معادل 1.0)
        self.light_intensity_slider.valueChanged.connect(self._update_light_intensity)
        change_light_color_btn = QPushButton("تغییر رنگ نور")
        change_light_color_btn.clicked.connect(self._change_light_color)
        light_layout.addRow("شدت نور:", self.light_intensity_slider)
        light_layout.addRow(change_light_color_btn)
        
        # گروه کنترل‌های اِلِمان‌های راهنما
        helpers_group = QGroupBox("اِلِمان‌های راهنما")
        helpers_layout = QFormLayout(helpers_group)
        self.grid_checkbox = QCheckBox(); self.grid_checkbox.setChecked(True)
        self.grid_checkbox.toggled.connect(self._toggle_grid_visibility) # نام متد اصلاح شد
        self.axes_checkbox = QCheckBox(); self.axes_checkbox.setChecked(True)
        self.axes_checkbox.toggled.connect(self._toggle_axes_visibility) # نام متد اصلاح شد
        helpers_layout.addRow("نمایش شبکه (Grid):", self.grid_checkbox)
        helpers_layout.addRow("نمایش محورها (Axes):", self.axes_checkbox)

        main_layout.addWidget(bg_group)
        main_layout.addWidget(light_group)
        main_layout.addWidget(helpers_group)
        main_layout.addStretch() # فضای خالی در پایین پنل
        
        self.scene_controls_dock.setWidget(container_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.scene_controls_dock)

    def create_properties_dock(self):
        """پنل کناری برای نمایش مشخصات فنی و هندسی مدل انتخاب شده را ایجاد می‌کند."""
        self.props_dock = QDockWidget("مشخصات قطعه", self)
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        self.prop_labels = {
            "نام فایل": QLabel("---"), "تعداد نقاط": QLabel("---"),
            "تعداد سلول‌ها": QLabel("---"), "حافظه مصرفی": QLabel("---"),
            "حجم": QLabel("---"), "ابعاد (X)": QLabel("---"),
            "ابعاد (Y)": QLabel("---"), "ابعاد (Z)": QLabel("---"),
        }
        for label_text, label_widget in self.prop_labels.items():
            form_layout.addRow(label_text, label_widget)
        self.props_dock.setWidget(form_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.props_dock) # در ابتدا کنار پنل تنظیمات صحنه

    def create_models_dock(self):
        """پنل کناری برای مدیریت (نمایش، مخفی کردن، حذف) مدل‌های بارگذاری شده را ایجاد می‌کند."""
        self.models_dock = QDockWidget("مدل‌های بارگذاری شده", self)
        self.models_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea) # اجازه جابجایی
        self.model_list_widget = QListWidget() # لیست برای نمایش مدل‌ها
        self.models_dock.setWidget(self.model_list_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.models_dock) # در ابتدا سمت راست پنجره

    # --- بخش منطق و کنترلرها برای UI و تعاملات ---
    def _change_background_color(self):
        """پنجره انتخاب رنگ را برای تغییر رنگ پس‌زمینه صحنه باز می‌کند."""
        color = QColorDialog.getColor() # باز کردن دیالوگ استاندارد انتخاب رنگ Qt
        if color.isValid(): # اگر کاربر رنگی را انتخاب کرد و OK زد
            self.plotter.set_background(color.name()) # اعمال رنگ به PyVista
            
    def _update_light_intensity(self, value):
        """شدت نور اصلی صحنه را بر اساس مقدار اسلایدر به‌روز می‌کند."""
        if self.main_light:
            intensity = value / 100.0 # تبدیل مقدار اسلایدر (0-200) به محدوده شدت (0.0-2.0)
            self.main_light.intensity = intensity
            self.plotter.render()

    def _change_light_color(self):
        """پنجره انتخاب رنگ را برای تغییر رنگ نور اصلی صحنه باز می‌کند."""
        current_color_qcolor = QColor.fromRgbF(*self.main_light.color) if self.main_light else Qt.GlobalColor.white
        color = QColorDialog.getColor(current_color_qcolor)
        if color.isValid() and self.main_light:
            # رنگ Qt به فرمت RGB float (0-1) که PyVista استفاده می‌کند، تبدیل می‌شود
            self.main_light.color = color.getRgbF()[:3] # فقط مقادیر R, G, B
            self.plotter.render()
            
    def _toggle_grid_visibility(self, state): # نام متد اصلاح شد
        """نمایش یا مخفی کردن شبکه کف صحنه."""
        if self.grid_actor: self.grid_actor.SetVisibility(state)
            
    def _toggle_axes_visibility(self, state): # نام متد اصلاح شد
        """نمایش یا مخفی کردن محورهای مختصات."""
        if self.plotter.axes_widget: self.plotter.axes_widget.SetEnabled(state)

    def _toggle_mode(self, checked):
        """
        مدیریت مرکزی برای تعویض بین حالت‌های مختلف برنامه (ناوبری، انتخاب، اندازه‌گیری، برش).
        تنها یک حالت می‌تواند در هر زمان فعال باشد.
        """
        sender_action = self.sender() # دکمه‌ای که این تابع را فراخوانی کرده
        action_to_mode_map = {
            self.select_action: 'selection',
            self.measure_action: 'measure',
            self.slice_action: 'slicing'
        }
        
        # اگر دکمه‌ای فعال شد
        if checked:
            new_mode = action_to_mode_map[sender_action]
            self.current_mode = new_mode
            
            # غیرفعال کردن سایر دکمه‌های حالت
            for action_button, mode_name in action_to_mode_map.items():
                if action_button is not sender_action:
                    action_button.setChecked(False)
            
            # غیرفعال کردن تعاملات پیش‌فرض دوربین برای حالت‌های خاص
            self.plotter.disable_camera_interaction()
            
            # اگر حالت برش نبود و ویجت برش فعال بود، آن را پاک کن
            if self.slicing_widget and new_mode != 'slicing':
                self.plotter.clear_plane_widgets()
                self.model_manager.clear_all_clipping() # حذف برش از مدل‌ها
                self.slicing_widget = None
            
            # اگر حالت جدید برش بود، ویجت برش را اضافه کن
            if new_mode == 'slicing':
                self.slicing_widget = self.plotter.add_plane_widget(self._handle_slice_interaction, interaction_event='always')
            
            self.status_bar.showMessage(f"حالت فعال: {self.current_mode}")

        # اگر دکمه‌ای غیرفعال شد (کاربر آن را لغو کرد)
        else:
            # اگر هیچ دکمه حالتی فعال نباشد، به حالت ناوبری برگرد
            if not any(action.isChecked() for action in action_to_mode_map.keys()):
                self.current_mode = 'navigation'
                self.plotter.enable_camera_interaction() # فعال کردن مجدد کنترل دوربین
                if self.slicing_widget: # اگر ویجت برش فعال بود، آن را پاک کن
                    self.plotter.clear_plane_widgets()
                    self.model_manager.clear_all_clipping()
                    self.slicing_widget = None
                self.status_bar.showMessage("حالت ناوبری")
            # اگر دکمه دیگری هنوز فعال است، حالت برنامه تغییر نمی‌کند (این حالت معمولاً رخ نمی‌دهد چون دکمه‌ها را مدیریت می‌کنیم)

    def _handle_actor_picked(self, actor):
        """
        callback برای انتخاب یک آبجکت کامل (actor) در صحنه.
        این تابع زمانی فراخوانی می‌شود که کاربر در حالت 'selection' روی یک مدل کلیک کند.
        """
        if self.current_mode != 'selection': return

        # ابتدا هایلایت مدل قبلی (اگر وجود داشت) را بردار
        if self.selected_model_id and self.selected_model_id in self.model_manager.models:
            previous_model_data = self.model_manager.models[self.selected_model_id]
            if previous_model_data['is_highlighted']:
                previous_model_data['actor'].prop.color = previous_model_data['original_color']
                previous_model_data['is_highlighted'] = False
        
        self.selected_model_id = None # پاک کردن انتخاب قبلی
        
        # اگر روی یک actor کلیک شده باشد
        if actor:
            model_id, model_data = self.model_manager.get_model_by_actor(actor)
            if model_id: # اگر actor متعلق به یکی از مدل‌های مدیریت شده ما باشد
                self.selected_model_id = model_id
                model_data['actor'].prop.color = 'yellow' # رنگ هایلایت
                model_data['is_highlighted'] = True
                self.status_bar.showMessage(f"قطعه انتخاب شد: {model_data['name']}")
                self._update_properties_panel(model_data) # به‌روزرسانی پنل مشخصات
        else: # اگر روی فضای خالی کلیک شده باشد
            self.status_bar.showMessage("هیچ قطعه‌ای انتخاب نشده است.")
            self._update_properties_panel(None) # پاک کردن پنل مشخصات

    def _update_properties_panel(self, model_data):
        """پنل مشخصات را با اطلاعات مدل انتخاب شده به‌روز می‌کند."""
        if model_data and model_data['mesh']:
            mesh = model_data['mesh']
            bounds = mesh.bounds # محدوده‌های مدل (min_x, max_x, min_y, max_y, min_z, max_z)
            size = (bounds[1]-bounds[0], bounds[3]-bounds[2], bounds[5]-bounds[4]) # ابعاد در هر محور
            
            self.prop_labels["نام فایل"].setText(model_data['name'])
            self.prop_labels["تعداد نقاط"].setText(f"{mesh.n_points:,}") # فرمت با جداکننده هزارگان
            self.prop_labels["تعداد سلول‌ها"].setText(f"{mesh.n_cells:,}")
            self.prop_labels["حافظه مصرفی"].setText(f"{mesh.actual_memory_size / 1024:.2f} کیلوبایت")
            # حجم فقط برای سطوح بسته (manifold) معتبر است
            self.prop_labels["حجم"].setText(f"{mesh.volume:.4f}" if mesh.is_manifold else "N/A (سطح باز)")
            self.prop_labels["ابعاد (X)"].setText(f"{size[0]:.3f}")
            self.prop_labels["ابعاد (Y)"].setText(f"{size[1]:.3f}")
            self.prop_labels["ابعاد (Z)"].setText(f"{size[2]:.3f}")
        else: # اگر مدلی انتخاب نشده باشد، تمام لیبل‌ها را پاک کن
            for label_widget in self.prop_labels.values():
                label_widget.setText("---")

    def _handle_picked_point(self, point):
        """
        callback برای انتخاب یک نقطه روی سطح یک مدل.
        این تابع زمانی فراخوانی می‌شود که کاربر در حالت 'measure' روی یک مدل کلیک کند.
        """
        if self.current_mode != 'measure' or not point: return # فقط در حالت اندازه‌گیری و با کلیک معتبر
        
        self.measurement_points.append(np.array(point)) # ذخیره نقطه انتخاب شده
        
        # نمایش بصری نقطه اول
        if len(self.measurement_points) == 1:
            self.status_bar.showMessage("نقطه اول انتخاب شد. برای انتخاب نقطه دوم کلیک کنید.")
            # ایجاد یک کره کوچک برای نمایش نقطه اول (به measurement_actors اضافه نمی‌شود چون موقتی است یا در _create_measurement_actors مدیریت می‌شود)
            # self.plotter.add_mesh(pv.Sphere(radius=0.01, center=self.measurement_points[0]), color='red') 
        
        # اگر دو نقطه انتخاب شده باشد، اندازه‌گیری را انجام بده
        elif len(self.measurement_points) == 2:
            p1 = self.measurement_points[0]
            p2 = self.measurement_points[1]
            self._create_measurement_actors(p1, p2) # ایجاد اِلِمان‌های بصری اندازه‌گیری
            
            distance = np.linalg.norm(p2 - p1)
            self.status_bar.showMessage(f"فاصله محاسبه شد: {distance:.3f} متر. برای اندازه‌گیری جدید کلیک کنید.")
            self.measurement_points = [] # آماده برای اندازه‌گیری بعدی
            
    def _clear_measurements(self):
        """تمام اِلِمان‌های بصری مربوط به اندازه‌گیری (نقاط، خطوط، برچسب‌ها) را از صحنه پاک می‌کند."""
        for actor_to_remove in self.measurement_actors:
            self.plotter.remove_actor(actor_to_remove, render=False) # حذف بدون رندر فوری
        self.plotter.render() # یکبار رندر در انتها
        self.measurement_actors = [] # لیست actor ها را خالی کن
        self.measurement_points = [] # لیست نقاط انتخاب شده را خالی کن
        self.status_bar.showMessage("تمام اندازه‌گیری‌ها پاک شدند.", 3000)

    def _handle_slice_interaction(self, plane_actor_or_mesh): # نام متد اصلاح شد
        """
        callback برای ویجت برش PyVista. این تابع هر بار که کاربر صفحه برش را حرکت می‌دهد، فراخوانی می‌شود.
        plane_actor_or_mesh می‌تواند خود actor ویجت صفحه باشد یا مشی که از برش حاصل می‌شود.
        ما به آبجکت plane نیاز داریم که از ویجت بدست می‌آید.
        """
        if self.current_mode == 'slicing' and self.slicing_widget:
            # خود ویجت یک آبجکت plane را نگهداری نمی‌کند، بلکه پارامترهای آن را می‌توان خواند
            # یا می‌توان از مش برش داده شده برای استخراج plane استفاده کرد اگر ویجت این امکان را بدهد
            # برای سادگی، فرض می‌کنیم PyVista به طور خودکار برش را روی مدل‌ها اعمال می‌کند
            # یا ما باید از پارامترهای plane_actor_or_mesh برای ایجاد یک pv.Plane استفاده کنیم.
            # در نسخه جدید PyVista، add_plane_widget مستقیماً یک pv.Plane را به callback می‌دهد.
            if isinstance(plane_actor_or_mesh, pv.Plane):
                 self.model_manager.clip_all_models(plane_actor_or_mesh)
            # else:
                # اگر خود plane object مستقیماً داده نشد، باید آن را از ویجت یا مش استخراج کنیم
                # print("Slice callback needs a pv.Plane object.")
            
    def open_model_files(self):
        """پنجره استاندارد انتخاب فایل برای افزودن یک یا چند مدل جدید را باز می‌کند."""
        file_paths, _ = QFileDialog.getOpenFileNames(self, "افزودن مدل(ها) به صحنه", "", 
                                                   "3D Models (*.glb *.gltf *.obj *.stl *.ply *.vtk *.vtp *.vtu)")
        if file_paths: # اگر کاربر فایلی را انتخاب کرده باشد
            for file_path in file_paths:
                self.load_model(file_path)

    def load_model(self, file_path):
        """یک مدل را از مسیر داده شده بارگذاری کرده و آن را به لیست UI اضافه می‌کند."""
        self.status_bar.showMessage(f"در حال بارگذاری: {os.path.basename(file_path)}...")
        model_id, model_data = self.model_manager.add_model(file_path) # مدل به مدیر اضافه می‌شود
        if model_id and model_data: # اگر بارگذاری موفقیت‌آمیز بود
            self.add_model_to_list_widget(model_id, model_data['name']) # به لیست UI هم اضافه کن
        else: # اگر خطایی در بارگذاری رخ داد
            self.status_bar.showMessage(f"خطا در بارگذاری مدل {os.path.basename(file_path)}", 5000)

    def add_model_to_list_widget(self, model_id, model_name):
        """
        یک آیتم سفارشی (شامل چک‌باکس، نام مدل و دکمه حذف) برای نمایش مدل
        در لیست QListWidget ایجاد می‌کند.
        """
        item = QListWidgetItem(self.model_list_widget) # یک آیتم جدید در لیست
        custom_widget = QWidget() # ویجت سفارشی برای قرارگیری درون آیتم
        layout = QHBoxLayout(custom_widget) # چیدمان افقی برای اجزا
        layout.setContentsMargins(5, 2, 5, 2) # حاشیه‌های داخلی

        checkbox = QCheckBox() # چک‌باکس برای کنترل نمایش مدل
        checkbox.setChecked(True) # به طور پیش‌فرض نمایش داده شود
        # اتصال سیگنال تغییر وضعیت چک‌باکس به تابع مدیریت نمایش مدل
        checkbox.stateChanged.connect(
            lambda state, current_model_id=model_id: self.model_manager.set_visibility(current_model_id, state == Qt.CheckState.Checked)
        )
        
        label = QLabel(model_name) # لیبل برای نمایش نام مدل
        label.setToolTip(model_id) # نمایش مسیر کامل فایل با نگه داشتن ماوس روی نام
        
        remove_btn = QPushButton("حذف") # دکمه برای حذف مدل
        remove_btn.setFixedSize(QSize(40, 24)) # اندازه ثابت برای دکمه
        # اتصال سیگنال کلیک دکمه به تابع حذف مدل
        remove_btn.clicked.connect(
            lambda _, current_model_id=model_id, current_list_item=item: self.remove_model_handler(current_model_id, current_list_item)
        )
        
        layout.addWidget(checkbox)
        layout.addWidget(label)
        layout.addStretch() # فضای خالی برای هل دادن دکمه حذف به سمت راست
        layout.addWidget(remove_btn)
        
        custom_widget.setLayout(layout)
        item.setSizeHint(custom_widget.sizeHint()) # اندازه آیتم لیست بر اساس ویجت سفارشی
        
        self.model_list_widget.addItem(item) # افزودن آیتم به لیست
        self.model_list_widget.setItemWidget(item, custom_widget) # قرار دادن ویجت سفارشی در آیتم

    def remove_model_handler(self, model_id, list_item):
        """یک مدل را از لیست UI و همچنین از مدیر مدل (و صحنه) حذف می‌کند."""
        if self.model_manager.remove_model(model_id): # اگر حذف از مدیر موفقیت‌آمیز بود
            row = self.model_list_widget.row(list_item) # گرفتن ردیف آیتم در لیست
            self.model_list_widget.takeItem(row) # حذف آیتم از لیست UI
            self.status_bar.showMessage(f"مدل '{os.path.basename(model_id)}' حذف شد.", 3000)
            if self.selected_model_id == model_id: # اگر مدل حذف شده، مدل انتخاب شده فعلی بود
                self.selected_model_id = None
                self._update_properties_panel(None) # پنل مشخصات را پاک کن

    def closeEvent(self, event):
        """
        این متد زمانی فراخوانی می‌شود که کاربر قصد بستن پنجره اصلی را دارد.
        ما از آن برای ذخیره چیدمان فعلی UI (موقعیت و اندازه پنجره و پنل‌ها) استفاده می‌کنیم.
        """
        self.settings.setValue("mainWindowGeometry", self.saveGeometry())
        self.settings.setValue("mainWindowState", self.saveState())
        QMainWindow.closeEvent(self, event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
