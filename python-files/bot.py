import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
import pandas as pd
import tensorflow as tf
from PIL import Image, ImageTk
import io
from ta import add_all_ta_features
from scipy.signal import argrelextrema
import threading

class ChartAnalyzerApp:
    def _init_(self, root):
        self.root = root
        self.root.title("نظام تحليل الشارتات المتقدم")
        self.root.geometry("1200x800")
        
        # نموذج التعرف على الأنماط
        self.pattern_model = self.load_pattern_model()
        self.pattern_names = [
            'رأس وكتفين', 'رأس وكتفين معكوس', 'قمة مزدوجة', 'قاع مزدوج',
            'مثلث صاعد', 'مثلث هابط', 'مثلث متماثل', 'علم صاعد', 'علم هابط',
            'راية صاعدة', 'راية هابطة', 'وتد صاعد', 'وتد هابط'
        ]
        
        # واجهة المستخدم
        self.create_widgets()
        
    def load_pattern_model(self):
        model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3,3), activation='relu', input_shape=(224,224,3)),
            tf.keras.layers.MaxPooling2D((2,2)),
            tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
            tf.keras.layers.MaxPooling2D((2,2)),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(13, activation='softmax')
        ])
        # هنا يجب تحميل الأوزان المدربة مسبقاً
        return model
    
    def create_widgets(self):
        # إطار الصورة
        self.image_frame = ttk.LabelFrame(self.root, text="عرض الشارت")
        self.image_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.image_frame, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # إطار التحكم
        self.control_frame = ttk.Frame(self.root)
        self.control_frame.pack(pady=10, fill=tk.X)
        
        self.load_btn = ttk.Button(self.control_frame, text="تحميل صورة الشارت", command=self.load_image)
        self.load_btn.pack(side=tk.LEFT, padx=5)
        
        self.analyze_btn = ttk.Button(self.control_frame, text="تحليل الشارت", command=self.analyze_image)
        self.analyze_btn.pack(side=tk.LEFT, padx=5)
        
        # إطار النتائج
        self.result_frame = ttk.LabelFrame(self.root, text="نتائج التحليل")
        self.result_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.create_result_tabs()
        
    def create_result_tabs(self):
        self.tab_control = ttk.Notebook(self.result_frame)
        
        # تبويب النمط
        self.pattern_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.pattern_tab, text="نمط الشارت")
        self.create_pattern_tab()
        
        # تبويب التحليل الفني
        self.tech_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tech_tab, text="التحليل الفني")
        self.create_tech_tab()
        
        # تبويب التوصية
        self.trade_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.trade_tab, text="توصيات التداول")
        self.create_trade_tab()
        
        self.tab_control.pack(fill=tk.BOTH, expand=True)
    
    def create_pattern_tab(self):
        self.pattern_label = ttk.Label(self.pattern_tab, text="النمط المحدد: غير معروف")
        self.pattern_label.pack(pady=10)
        
        self.pattern_confidence = ttk.Label(self.pattern_tab, text="مستوى الثقة: 0%")
        self.pattern_confidence.pack(pady=5)
        
        self.pattern_image = tk.Canvas(self.pattern_tab, width=300, height=200, bg='white')
        self.pattern_image.pack(pady=10)
        
    def create_tech_tab(self):
        columns = ('المؤشر', 'القيمة', 'التفسير')
        self.tech_tree = ttk.Treeview(self.tech_tab, columns=columns, show='headings')
        
        for col in columns:
            self.tech_tree.heading(col, text=col)
            self.tech_tree.column(col, width=150)
        
        self.tech_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # بيانات مثال
        self.tech_tree.insert('', 'end', values=('RSI', '42.3', 'محايد'))
        self.tech_tree.insert('', 'end', values=('MACD', '1.23', 'إشارة شراء'))
        
    def create_trade_tab(self):
        self.trade_recommendation = ttk.Label(self.trade_tab, text="التوصية: انتظر")
        self.trade_recommendation.pack(pady=10)
        
        # جدول نقاط الدخول والخروج
        columns = ('النقطة', 'السعر', 'النسبة')
        self.trade_tree = ttk.Treeview(self.trade_tab, columns=columns, show='headings')
        
        for col in columns:
            self.trade_tree.heading(col, text=col)
            self.trade_tree.column(col, width=120)
        
        self.trade_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # معلومات إضافية
        self.risk_label = ttk.Label(self.trade_tab, text="نسبة العائد للمخاطرة: -")
        self.risk_label.pack(pady=5)
        
        self.confidence_label = ttk.Label(self.trade_tab, text="مستوى الثقة: -")
        self.confidence_label.pack(pady=5)
    
    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.image_path = file_path
            self.display_image(file_path)
    
    def display_image(self, path):
        img = Image.open(path)
        img.thumbnail((800, 600))
        self.tk_image = ImageTk.PhotoImage(img)
        
        self.canvas.config(width=self.tk_image.width(), height=self.tk_image.height())
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
    
    def analyze_image(self):
        if not hasattr(self, 'image_path'):
            messagebox.showerror("خطأ", "الرجاء تحميل صورة الشارت أولاً")
            return
        
        # بدء التحليل في خيط منفصل
        threading.Thread(target=self.process_analysis).start()

    def process_analysis(self):
        try:
            # 1. معالجة الصورة
            img = Image.open(self.image_path)
            img_array = np.array(img.resize((224,224)))
            
            # 2. التعرف على النمط
            pattern_idx, confidence = self.detect_pattern(img_array)
            pattern_name = self.pattern_names[pattern_idx]
            
            # 3. تحليل البيانات
            chart_data = self.extract_chart_data(self.image_path)
            technicals = self.technical_analysis(chart_data)
            
            # 4. توليد التوصية
            recommendation = self.generate_recommendation(pattern_name, confidence, technicals)
            
            # 5. عرض النتائج
            self.display_results(pattern_name, confidence, technicals, recommendation)
            
        except Exception as e:
            messagebox.showerror("خطأ في التحليل", str(e))
    
    def detect_pattern(self, img_array):
        img_array = np.expand_dims(img_array, 0) / 255.0
        predictions = self.pattern_model.predict(img_array)
        return np.argmax(predictions[0]), np.max(predictions[0])
    
    def extract_chart_data(self, image_path):
        # هذه دالة مبسطة - في التطبيق الحقيقي تحتاج لمعالجة الصورة بدقة
        return {
            'open': np.random.uniform(100, 200),
            'high': np.random.uniform(200, 300),
            'low': np.random.uniform(50, 100),
            'close': np.random.uniform(100, 200),
            'volume': np.random.uniform(1000, 5000)
        }
    
    def technical_analysis(self, data):
        df = pd.DataFrame([data])
        df = add_all_ta_features(df, open="open", high="high", low="low", 
                                 close="close", volume="volume")
        
        supports, resistances = self.find_support_resistance(df['close'])
        
        return {
            'rsi': df['momentum_rsi'].iloc[-1],
            'macd': df['trend_macd'].iloc[-1],
            'supports': supports,
            'resistances': resistances,
            'stochastic': df['momentum_stoch_rsi'].iloc[-1],  # إضافة Stochastic RSI
            'bollinger_upper': df['volatility_bbh'].iloc[-1],  # إضافة Bollinger Bands
            'bollinger_lower': df['volatility_bbl'].iloc[-1],  # إضافة Bollinger Bands
        }
    
    def find_support_resistance(self, prices, window=5):
        maxima_idx = argrelextrema(prices.values, np.greater, order=window)[0]
        minima_idx = argrelextrema(prices.values, np.less, order=window)[0]
        return prices.iloc[minima_idx].tolist(), prices.iloc[maxima_idx].tolist()
    
    def generate_recommendation(self, pattern, confidence, technicals):
        if confidence > 0.7 and technicals['rsi'] < 40 and 'صاعد' in pattern:
            return {
                'action': 'شراء',
                'entry': technicals['supports'][0],
                'stop_loss': technicals['supports'][0] * 0.98,
                'take_profit': technicals['resistances'][0],
                'confidence': confidence
            }
        elif confidence > 0.7 and technicals['rsi'] > 60 and 'هابط' in pattern:
            return {
                'action': 'بيع',
                'entry': technicals['resistances'][0],
                'stop_loss': technicals['resistances'][0] * 1.02,
                'take_profit': technicals['supports'][0],
                'confidence': confidence
            }
        else:
            return {
                'action': 'انتظر',
                'confidence': confidence
            }
    
    def display_results(self, pattern, confidence, technicals, recommendation):
        self.pattern_label.config(text=f"النمط المحدد: {pattern}")
        self.pattern_confidence.config(text=f"مستوى الثقة: {confidence*100:.1f}%")
        
        self.tech_tree.delete(*self.tech_tree.get_children())
        self.tech_tree.insert('', 'end', values=('RSI', f"{technicals['rsi']:.2f}", 
                              'تشبع بيعي' if technicals['rsi'] < 30 else 'تشبع شرائي' if technicals['rsi'] > 70 else 'محايد'))
        self.tech_tree.insert('', 'end', values=('MACD', f"{technicals['macd']:.2f}", 
                              'إشارة شراء' if technicals['macd'] > 0 else 'إشارة بيع'))
        
        self.tech_tree.insert('', 'end', values=('Stochastic RSI', f"{technicals['stochastic']:.2f}", 
                              'إشارة شراء' if technicals['stochastic'] < 0.2 else 'إشارة بيع' if technicals['stochastic'] > 0.8 else 'محايد'))
        self.tech_tree.insert('', 'end', values=('Bollinger Upper Band', f"{technicals['bollinger_upper']:.2f}", 
                              'مقاومة' if technicals['bollinger_upper'] > technicals['close'][-1] else 'محايد'))
        self.tech_tree.insert('', 'end', values=('Bollinger Lower Band', f"{technicals['bollinger_lower']:.2f}", 
                              'دعم' if technicals['bollinger_lower'] < technicals['close'][-1] else 'محايد'))

        self.trade_recommendation.config(text=f"التوصية: {recommendation['action']}")
        
        self.trade_tree.delete(*self.trade_tree.get_children())
        if recommendation['action'] != 'انتظر':
            self.trade_tree.insert('', 'end', values=('نقطة الدخول', f"{recommendation['entry']:.2f}", '100%'))
            self.trade_tree.insert('', 'end', values=('وقف الخسارة', f"{recommendation['stop_loss']:.2f}", '2% أقل'))
            self.trade_tree.insert('', 'end', values=('هدف الربح', f"{recommendation['take_profit']:.2f}", '5% أعلى'))
            
            rr_ratio = (recommendation['take_profit'] - recommendation['entry']) / \
                      (recommendation['entry'] - recommendation['stop_loss'])
            self.risk_label.config(text=f"نسبة العائد للمخاطرة: {rr_ratio:.2f}:1")
        
        self.confidence_label.config(text=f"مستوى الثقة: {recommendation['confidence']*100:.1f}%")

if _name_ == "_main_":
    root = tk.Tk()
    app = ChartAnalyzerApp(root)
    root.mainloop()