import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import os
from tkinter import font

class MissileTrajectoryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("نمایش مسیر موشک")
        self.root.geometry("780x650")  # کوچک‌تر شد
        self.root.configure(bg='#2c3e50')
        
        # تنظیم فونت فارسی - کوچک‌تر
        self.persian_font = font.Font(family="Tahoma", size=9)
        self.title_font = font.Font(family="Tahoma", size=12, weight="bold")
        
        self.setup_ui()
        
    def setup_ui(self):
        # فریم اصلی
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)  # padding کوچک‌تر
        
        # عنوان
        title_label = tk.Label(
            main_frame,
            text="Google Earth نمایش مسیر موشک در ",
            font=self.title_font,
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        title_label.pack(pady=(0, 20))  # فاصله کمتر
        
        # فریم ورودی‌ها
        input_frame = tk.LabelFrame(
            main_frame,
            text="مختصات و ارتفاع نقاط",
            font=self.persian_font,
            bg='#34495e',
            fg='#ecf0f1',
            padx=15,
            pady=12
        )
        input_frame.pack(fill='x', pady=(0, 15))
        
        # نقطه شروع
        start_frame = tk.Frame(input_frame, bg='#34495e')
        start_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            start_frame,
            text="🎯 نقطه پرتاب:",
            font=self.persian_font,
            bg='#34495e',
            fg='#e74c3c'
        ).pack(anchor='w')
        
        start_coords_frame = tk.Frame(start_frame, bg='#34495e')
        start_coords_frame.pack(fill='x', pady=(3, 0))
        
        tk.Label(start_coords_frame, text="عرض:", font=self.persian_font, bg='#34495e', fg='#ecf0f1').grid(row=0, column=0, sticky='w')
        self.start_lat = tk.Entry(start_coords_frame, font=self.persian_font, width=11)
        self.start_lat.grid(row=0, column=1, padx=(3, 10))
        self.start_lat.insert(0, "32.452574")
        
        tk.Label(start_coords_frame, text="طول:", font=self.persian_font, bg='#34495e', fg='#ecf0f1').grid(row=0, column=2, sticky='w')
        self.start_lon = tk.Entry(start_coords_frame, font=self.persian_font, width=11)
        self.start_lon.grid(row=0, column=3, padx=(3, 10))
        self.start_lon.insert(0, "51.861803")
        
        tk.Label(start_coords_frame, text="ارتفاع(m):", font=self.persian_font, bg='#34495e', fg='#e67e22').grid(row=0, column=4, sticky='w')
        self.start_altitude = tk.Entry(start_coords_frame, font=self.persian_font, width=8)
        self.start_altitude.grid(row=0, column=5, padx=3)
        self.start_altitude.insert(0, "1640")
        
        # نقطه پایان
        end_frame = tk.Frame(input_frame, bg='#34495e')
        end_frame.pack(fill='x')
        
        tk.Label(
            end_frame,
            text="💥 نقطه هدف:",
            font=self.persian_font,
            bg='#34495e',
            fg='#e74c3c'
        ).pack(anchor='w')
        
        end_coords_frame = tk.Frame(end_frame, bg='#34495e')
        end_coords_frame.pack(fill='x', pady=(3, 0))
        
        tk.Label(end_coords_frame, text="عرض:", font=self.persian_font, bg='#34495e', fg='#ecf0f1').grid(row=0, column=0, sticky='w')
        self.end_lat = tk.Entry(end_coords_frame, font=self.persian_font, width=11)
        self.end_lat.grid(row=0, column=1, padx=(3, 10))
        self.end_lat.insert(0, "31.879814")
        
        tk.Label(end_coords_frame, text="طول:", font=self.persian_font, bg='#34495e', fg='#ecf0f1').grid(row=0, column=2, sticky='w')
        self.end_lon = tk.Entry(end_coords_frame, font=self.persian_font, width=11)
        self.end_lon.grid(row=0, column=3, padx=(3, 10))
        self.end_lon.insert(0, "50.727577")
        
        tk.Label(end_coords_frame, text="ارتفاع(m):", font=self.persian_font, bg='#34495e', fg='#e67e22').grid(row=0, column=4, sticky='w')
        self.end_altitude = tk.Entry(end_coords_frame, font=self.persian_font, width=8)
        self.end_altitude.grid(row=0, column=5, padx=3)
        self.end_altitude.insert(0, "1940")
        
        # تنظیمات پیشرفته - فشرده‌تر
        settings_frame = tk.LabelFrame(
            main_frame,
            text="تنظیمات مسیر و دوربین",
            font=self.persian_font,
            bg='#34495e',
            fg='#ecf0f1',
            padx=15,
            pady=10
        )
        settings_frame.pack(fill='x', pady=(0, 10))
        
        # ردیف اول
        row1 = tk.Frame(settings_frame, bg='#34495e')
        row1.pack(fill='x', pady=(0, 8))
        
        tk.Label(row1, text="ارتفاع max(m):", font=self.persian_font, bg='#34495e', fg='#ecf0f1').grid(row=0, column=0, sticky='w')
        self.max_altitude = tk.Entry(row1, font=self.persian_font, width=10)
        self.max_altitude.grid(row=0, column=1, padx=(3, 20))
        self.max_altitude.insert(0, "50000")
        
        tk.Label(row1, text="نقاط:", font=self.persian_font, bg='#34495e', fg='#ecf0f1').grid(row=0, column=2, sticky='w')
        self.num_points = tk.Entry(row1, font=self.persian_font, width=8)
        self.num_points.grid(row=0, column=3, padx=(3, 20))
        self.num_points.insert(0, "100")
        
        tk.Label(row1, text="رنگ:", font=self.persian_font, bg='#34495e', fg='#ecf0f1').grid(row=0, column=4, sticky='w')
        self.color_var = tk.StringVar(value="قرمز")
        color_combo = ttk.Combobox(row1, textvariable=self.color_var, 
                                  values=["قرمز", "آبی", "سبز", "زرد"], 
                                  font=self.persian_font, width=8, state="readonly")
        color_combo.grid(row=0, column=5, padx=3)
        
        # ردیف دوم
        row2 = tk.Frame(settings_frame, bg='#34495e')
        row2.pack(fill='x', pady=(0, 8))
        
        tk.Label(row2, text="📸 دوربین(km):", font=self.persian_font, bg='#34495e', fg='#3498db').grid(row=0, column=0, sticky='w')
        self.camera_range = tk.Entry(row2, font=self.persian_font, width=10)
        self.camera_range.grid(row=0, column=1, padx=(3, 20))
        self.camera_range.insert(0, "200")
        
        tk.Label(row2, text="ضخامت:", font=self.persian_font, bg='#34495e', fg='#ecf0f1').grid(row=0, column=2, sticky='w')
        self.line_width = tk.Entry(row2, font=self.persian_font, width=8)
        self.line_width.grid(row=0, column=3, padx=(3, 20))
        self.line_width.insert(0, "5")
        
        tk.Label(row2, text="انیمیشن(s):", font=self.persian_font, bg='#34495e', fg='#ecf0f1').grid(row=0, column=4, sticky='w')
        self.animation_duration = tk.Entry(row2, font=self.persian_font, width=8)
        self.animation_duration.grid(row=0, column=5, padx=3)
        self.animation_duration.insert(0, "20")
        
        # چک‌باکس انیمیشن
        row3 = tk.Frame(settings_frame, bg='#34495e')
        row3.pack(fill='x')
        
        self.add_animation = tk.BooleanVar(value=True)
        animation_check = tk.Checkbutton(
            row3,
            text="✅ انیمیشن فعال",
            variable=self.add_animation,
            font=self.persian_font,
            bg='#34495e',
            fg='#ecf0f1',
            selectcolor='#2c3e50'
        )
        animation_check.pack(side='left')
        
        # راهنما کوتاه
        info_short = tk.Label(
            row3,
            text="💡 ارتفاع زمین مهم است",
            font=self.persian_font,
            bg='#34495e',
            fg='#f39c12'
        )
        info_short.pack(side='right')
        
        # فریم دکمه‌ها - فشرده‌تر
        button_frame = tk.Frame(main_frame, bg='#2c3e50')
        button_frame.pack(fill='x', pady=(0, 10))
        
        # دکمه تولید
        generate_btn = tk.Button(
            button_frame,
            text="🚀 تولید KML",
            font=self.persian_font,
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=8,
            command=self.generate_kml,
            cursor='hand2'
        )
        generate_btn.pack(side='left', padx=(0, 8))
        
        # دکمه انتخاب مسیر
        save_path_btn = tk.Button(
            button_frame,
            text="📁 مسیر ذخیره",
            font=self.persian_font,
            bg='#3498db',
            fg='white',
            padx=15,
            pady=8,
            command=self.choose_save_path,
            cursor='hand2'
        )
        save_path_btn.pack(side='left', padx=(0, 8))
        
        # دکمه پیش‌نمایش
        preview_btn = tk.Button(
            button_frame,
            text="👁️ پیش‌نمایش",
            font=self.persian_font,
            bg='#f39c12',
            fg='white',
            padx=15,
            pady=8,
            command=self.preview_coordinates,
            cursor='hand2'
        )
        preview_btn.pack(side='left')
        
        # نمایش مسیر ذخیره
        self.save_path_var = tk.StringVar(value="مسیر: پوشه جاری")
        save_path_label = tk.Label(
            main_frame,
            textvariable=self.save_path_var,
            font=self.persian_font,
            bg='#2c3e50',
            fg='#95a5a6'
        )
        save_path_label.pack(anchor='w')
        
        # منطقه اطلاعات - کوچک‌تر
        info_frame = tk.LabelFrame(
            main_frame,
            text="اطلاعات",
            font=self.persian_font,
            bg='#34495e',
            fg='#ecf0f1',
            padx=10,
            pady=8
        )
        info_frame.pack(fill='both', expand=True)
        
        # متن اطلاعات
        self.info_text = tk.Text(
            info_frame,
            font=self.persian_font,
            bg='#2c3e50',
            fg='#ecf0f1',
            wrap='word',
            height=5  # ارتفاع کمتر
        )
        self.info_text.pack(fill='both', expand=True)
        
        # متن راهنما کوتاه
        initial_info = """🎯 راهنمای سریع:
1️⃣ مختصات و ارتفاع زمین را وارد کنید
2️⃣ فاصله دوربین (50-500 km) و تنظیمات را اعمال کنید  
3️⃣ "تولید KML" کلیک کنید و فایل را در Google Earth باز کنید

✅ بهبودها: ارتفاع زمین (Terrain) + دوربین قابل تنظیم + بدون خطوط عمودی"""
        
        self.info_text.insert('1.0', initial_info)
        self.info_text.config(state='disabled')
        
        # متغیر مسیر ذخیره
        self.save_directory = os.getcwd()
    
    def get_color_code(self, color_name):
        color_codes = {
            "قرمز": "ff0000ff",
            "آبی": "ffff0000", 
            "سبز": "ff00ff00",
            "زرد": "ff00ffff",
            "بنفش": "ffff00ff"
        }
        return color_codes.get(color_name, "ff0000ff")
    
    def choose_save_path(self):
        directory = filedialog.askdirectory(
            title="انتخاب پوشه برای ذخیره فایل KML"
        )
        if directory:
            self.save_directory = directory
            self.save_path_var.set(f"مسیر: {os.path.basename(directory)}")
    
    def preview_coordinates(self):
        try:
            start_lat = float(self.start_lat.get())
            start_lon = float(self.start_lon.get())
            start_alt = float(self.start_altitude.get())
            end_lat = float(self.end_lat.get())
            end_lon = float(self.end_lon.get())
            end_alt = float(self.end_altitude.get())
            camera_range = float(self.camera_range.get())
            
            if camera_range < 50 or camera_range > 500:
                messagebox.showwarning("هشدار", "فاصله دوربین باید بین 50 تا 500 کیلومتر باشد!")
                return
            
            distance = self.haversine_distance(start_lat, start_lon, end_lat, end_lon)
            altitude_diff = end_alt - start_alt
            
            preview_info = f"""📍 پیش‌نمایش:
🎯 پرتاب: {start_lat:.4f}, {start_lon:.4f} | ارتفاع: {start_alt:,}m
💥 هدف: {end_lat:.4f}, {end_lon:.4f} | ارتفاع: {end_alt:,}m
📏 فاصله: {distance/1000:.2f}km | اختلاف ارتفاع: {altitude_diff:+.0f}m
📸 دوربین: {camera_range}km | انیمیشن: {'✅' if self.add_animation.get() else '❌'}
✅ همه اطلاعات صحیح است!"""
            
            self.update_info(preview_info)
            
        except ValueError:
            messagebox.showerror("خطا", "لطفاً همه مقادیر را به درستی وارد کنید!")
    
    def update_info(self, text):
        self.info_text.config(state='normal')
        self.info_text.delete('1.0', tk.END)
        self.info_text.insert('1.0', text)
        self.info_text.config(state='disabled')
    
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 6371000  # شعاع زمین به متر
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    def calculate_bearing(self, lat1, lon1, lat2, lon2):
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lon_rad = math.radians(lon2 - lon1)
        
        y = math.sin(delta_lon_rad) * math.cos(lat2_rad)
        x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon_rad)
        
        bearing_rad = math.atan2(y, x)
        bearing_deg = math.degrees(bearing_rad)
        
        return (bearing_deg + 360) % 360
    
    def calculate_perpendicular_point(self, lat1, lon1, lat2, lon2, distance_km):
        center_lat = (lat1 + lat2) / 2
        center_lon = (lon1 + lon2) / 2
        
        bearing = self.calculate_bearing(lat1, lon1, lat2, lon2)
        perpendicular_bearing = (bearing + 90) % 360
        
        R = 6371
        distance_rad = distance_km / R
        
        center_lat_rad = math.radians(center_lat)
        center_lon_rad = math.radians(center_lon)
        perpendicular_bearing_rad = math.radians(perpendicular_bearing)
        
        new_lat_rad = math.asin(
            math.sin(center_lat_rad) * math.cos(distance_rad) +
            math.cos(center_lat_rad) * math.sin(distance_rad) * math.cos(perpendicular_bearing_rad)
        )
        
        new_lon_rad = center_lon_rad + math.atan2(
            math.sin(perpendicular_bearing_rad) * math.sin(distance_rad) * math.cos(center_lat_rad),
            math.cos(distance_rad) - math.sin(center_lat_rad) * math.sin(new_lat_rad)
        )
        
        new_lat = math.degrees(new_lat_rad)
        new_lon = math.degrees(new_lon_rad)
        
        return new_lat, new_lon
    
    def generate_kml(self):
        try:
            start_lat = float(self.start_lat.get())
            start_lon = float(self.start_lon.get())
            start_alt = float(self.start_altitude.get())
            end_lat = float(self.end_lat.get())
            end_lon = float(self.end_lon.get())
            end_alt = float(self.end_altitude.get())
            max_altitude = float(self.max_altitude.get())
            num_points = int(self.num_points.get())
            line_width = int(self.line_width.get())
            color_code = self.get_color_code(self.color_var.get())
            animation_duration = float(self.animation_duration.get())
            add_animation = self.add_animation.get()
            camera_range = float(self.camera_range.get())
            
            if camera_range < 50 or camera_range > 500:
                messagebox.showerror("خطا", "فاصله دوربین باید بین 50 تا 500 کیلومتر باشد!")
                return
            
            if max_altitude <= max(start_alt, end_alt):
                messagebox.showerror("خطا", "ارتفاع حداکثر باید بیشتر از ارتفاع زمین باشد!")
                return
            
            kml_content = self.create_missile_trajectory_kml(
                start_lat, start_lon, start_alt,
                end_lat, end_lon, end_alt,
                max_altitude, num_points, color_code, line_width,
                animation_duration, add_animation, camera_range
            )
            
            file_path = os.path.join(self.save_directory, "missile_trajectory.kml")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(kml_content)
            
            distance = self.haversine_distance(start_lat, start_lon, end_lat, end_lon)
            
            success_info = f"""✅ فایل KML تولید شد!
📁 {os.path.basename(file_path)}
📏 {distance/1000:.2f}km | 📸 {camera_range}km
🎯 بدون خطوط عمودی اضافی
🌍 با پشتیبانی کامل Terrain"""
            
            self.update_info(success_info)
            
            result = messagebox.askyesno("موفقیت",f"فایل در مسیر زیر ذخیره شد:{file_path}پوشه را باز کنم؟")
            
            if result:
                os.startfile(self.save_directory)
                
        except ValueError:
            messagebox.showerror("خطا", "لطفاً تمام مقادیر را به درستی وارد کنید!")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در تولید فایل: {str(e)}")
    
    def create_missile_trajectory_kml(self, start_lat, start_lon, start_alt,
                                     end_lat, end_lon, end_alt,
                                     max_altitude, num_points, color_code, line_width,
                                     animation_duration, add_animation, camera_range_km):
        
        bearing = self.calculate_bearing(start_lat, start_lon, end_lat, end_lon)
        distance = self.haversine_distance(start_lat, start_lon, end_lat, end_lon)
        
        coordinates = []
        missile_animation = []
        
        for i in range(num_points + 1):
            t = i / num_points
            
            lat = start_lat + t * (end_lat - start_lat)
            lon = start_lon + t * (end_lon - start_lon)
            
            ground_altitude = start_alt + t * (end_alt - start_alt)
            missile_height_above_ground = max_altitude * math.sin(math.pi * t)
            total_altitude = ground_altitude + missile_height_above_ground
            
            coordinates.append(f"{lon},{lat},{total_altitude}")
            
            if add_animation:
                missile_animation.append(f'''
    <gx:AnimatedUpdate>
      <gx:duration>0.1</gx:duration>
      <Update>
        <targetHref/>
        <Change>
          <Placemark targetId="movingMissile">
            <Point>
              <coordinates>{lon},{lat},{total_altitude}</coordinates>
            </Point>
          </Placemark>
        </Change>
      </Update>
    </gx:AnimatedUpdate>
    <gx:Wait>
      <gx:duration>{animation_duration/num_points:.2f}</gx:duration>
    </gx:Wait>''')
        
        distance_km = distance / 1000
        camera_distance = max(distance_km * 0.7, 30)
        
        camera_lat, camera_lon = self.calculate_perpendicular_point(
            start_lat, start_lon, end_lat, end_lon, camera_distance
        )
        
        camera_altitude = (start_alt + end_alt) / 2 + max_altitude * 0.3
        camera_range_meters = camera_range_km * 1000
        
        center_lat = (start_lat + end_lat) / 2
        center_lon = (start_lon + end_lon) / 2
        camera_heading = self.calculate_bearing(camera_lat, camera_lon, center_lat, center_lon)
        
        tour_xml = ""
        if add_animation:
            tour_xml = f'''
    <gx:Tour>
      <name>🚀 انیمیشن موشک - بدون خطوط عمودی</name>
      <description>نمایش مسیر موشک با پشتیبانی کامل Terrain</description>
      <gx:Playlist>
        <gx:FlyTo>
          <gx:duration>5.0</gx:duration>
          <gx:flyToMode>smooth</gx:flyToMode>
          <LookAt>
            <longitude>{center_lon}</longitude>
            <latitude>{center_lat}</latitude>
            <altitude>{camera_altitude}</altitude>
            <heading>{camera_heading}</heading>
            <tilt>70</tilt>
            <range>{camera_range_meters}</range>
            <gx:altitudeMode>absolute</gx:altitudeMode>
          </LookAt>
        </gx:FlyTo>
        
        <gx:Wait>
          <gx:duration>3.0</gx:duration>
        </gx:Wait>
        
        <gx:AnimatedUpdate>
          <gx:duration>0.1</gx:duration>
          <Update>
            <targetHref/>
            <Change>
              <Placemark targetId="movingMissile">
                <visibility>1</visibility>
                <Point>
                  <coordinates>{start_lon},{start_lat},{start_alt}</coordinates>
                </Point>
              </Placemark>
            </Change>
          </Update>
        </gx:AnimatedUpdate>
        
        {''.join(missile_animation)}
        
        <gx:AnimatedUpdate>
          <gx:duration>0.5</gx:duration>
          <Update>
            <targetHref/>
            <Change>
              <Placemark targetId="explosion">
                <visibility>1</visibility>
              </Placemark>
            </Change>
          </Update>
        </gx:AnimatedUpdate>
        
        <gx:AnimatedUpdate>
          <gx:duration>0.1</gx:duration>
          <Update>
            <targetHref/>
            <Change>
              <Placemark targetId="movingMissile">
                <visibility>0</visibility>
              </Placemark>
            </Change>
          </Update>
        </gx:AnimatedUpdate>
        
        <gx:Wait>
          <gx:duration>5.0</gx:duration>
        </gx:Wait>
      </gx:Playlist>
    </gx:Tour>'''
        
        # KML با extrude=0 برای حذف خطوط عمودی
        kml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
  <Document>
    <name>🚀 Missile Trajectory - Clean & Optimized</name>
    <description>مسیر موشک بدون خطوط عمودی - با پشتیبانی کامل Terrain</description>
    
    <Style id="missileTrajectory">
      <LineStyle>
        <color>{color_code}</color>
        <width>{line_width}</width>
      </LineStyle>
      <PolyStyle>
        <fill>0</fill>
        <outline>1</outline>
      </PolyStyle>
    </Style>
    
    <Style id="launchPoint">
      <IconStyle>
        <color>ff00ff00</color>
        <scale>2.0</scale>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/shapes/arrow.png</href>
        </Icon>
      </IconStyle>
      <LabelStyle>
        <color>ff00ff00</color>
        <scale>1.3</scale>
      </LabelStyle>
    </Style>
    
    <Style id="targetPoint">
      <IconStyle>
        <color>ff0000ff</color>
        <scale>2.0</scale>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/shapes/target.png</href>
        </Icon>
      </IconStyle>
      <LabelStyle>
        <color>ff0000ff</color>
        <scale>1.3</scale>
      </LabelStyle>
    </Style>
    
    <Style id="movingMissileStyle">
      <IconStyle>
        <color>ffffff00</color>
        <scale>3.0</scale>
        <heading>{bearing}</heading>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href>
        </Icon>
      </IconStyle>
      <LabelStyle>
        <color>ffffff00</color>
        <scale>1.5</scale>
      </LabelStyle>
    </Style>
    
    <Style id="explosionStyle">
      <IconStyle>
        <color>ff0000ff</color>
        <scale>5.0</scale>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/shapes/explosion.png</href>
        </Icon>
      </IconStyle>
    </Style>
    
    {tour_xml}
    
    <Placemark>
      <name>🚀 نقطه پرتاب</name>
      <description>محل پرتاب موشک - ارتفاع زمین: {start_alt:,}m</description>
      <styleUrl>#launchPoint</styleUrl>
      <Point>
        <coordinates>{start_lon},{start_lat},{start_alt}</coordinates>
        <altitudeMode>absolute</altitudeMode>
      </Point>
    </Placemark>
    
    <Placemark>
      <name>💥 هدف</name>
      <description>نقطه هدف - ارتفاع زمین: {end_alt:,}m</description>
      <styleUrl>#targetPoint</styleUrl>
      <Point>
        <coordinates>{end_lon},{end_lat},{end_alt}</coordinates>
        <altitudeMode>absolute</altitudeMode>
      </Point>
    </Placemark>
    
    <Placemark>
      <name>مسیر پرتابه‌ای - بدون خطوط عمودی</name>
      <description>مسیر موشک با پشتیبانی Terrain
      
فاصله: {distance/1000:.2f}km | دوربین: {camera_range_km}km
ارتفاع max: {max_altitude:,}m | نقاط: {num_points}</description>
      <styleUrl>#missileTrajectory</styleUrl>
      <LineString>
        <extrude>0</extrude>
        <tessellate>0</tessellate>
        <altitudeMode>absolute</altitudeMode>
        <coordinates>
          {" ".join(coordinates)}
        </coordinates>
      </LineString>
    </Placemark>
    
    <Placemark id="movingMissile">
      <name>🚀 موشک</name>
      <description>موشک در حال حرکت</description>
      <visibility>0</visibility>
      <styleUrl>#movingMissileStyle</styleUrl>
      <Point>
        <coordinates>{start_lon},{start_lat},{start_alt}</coordinates>
        <altitudeMode>absolute</altitudeMode>
      </Point>
    </Placemark>
    
    <Placemark id="explosion">
      <name>💥 انفجار</name>
      <description>انفجار در هدف</description>
      <visibility>0</visibility>
      <styleUrl>#explosionStyle</styleUrl>
      <Point>
        <coordinates>{end_lon},{end_lat},{end_alt}</coordinates>
        <altitudeMode>absolute</altitudeMode>
      </Point>
    </Placemark>
    
  </Document>
</kml>'''
        
        return kml_content

# اجرای برنامه
if __name__ == "__main__":
    root = tk.Tk()
    app = MissileTrajectoryGUI(root)
    root.mainloop()
