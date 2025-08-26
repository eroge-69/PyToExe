#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
محرك الأتمتة لحل الاستبيانات في موقع Rewarding Ways
"""

import time
import random
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import requests
from bs4 import BeautifulSoup
import json

class HumanBehaviorSimulator:
    """محاكي السلوك البشري لتجنب الكشف"""
    
    @staticmethod
    def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
        """تأخير عشوائي بين الإجراءات"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    @staticmethod
    def human_type(element, text: str, typing_speed: float = 0.1):
        """كتابة نص بسرعة بشرية"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, typing_speed))
    
    @staticmethod
    def human_click(driver, element):
        """نقرة بشرية مع حركة الماوس"""
        actions = ActionChains(driver)
        # حركة الماوس إلى العنصر
        actions.move_to_element(element)
        HumanBehaviorSimulator.random_delay(0.2, 0.5)
        # النقر
        actions.click(element)
        actions.perform()
        HumanBehaviorSimulator.random_delay(0.5, 1.0)
    
    @staticmethod
    def random_scroll(driver):
        """تمرير عشوائي للصفحة"""
        scroll_amount = random.randint(100, 500)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        HumanBehaviorSimulator.random_delay(1.0, 2.0)

class SurveyDetector:
    """كاشف أنواع الاستبيانات والأسئلة"""
    
    @staticmethod
    def detect_question_type(question_element) -> str:
        """تحديد نوع السؤال"""
        try:
            # البحث عن عناصر الإجابة
            radio_buttons = question_element.find_elements(By.XPATH, ".//input[@type='radio']")
            checkboxes = question_element.find_elements(By.XPATH, ".//input[@type='checkbox']")
            text_inputs = question_element.find_elements(By.XPATH, ".//input[@type='text']")
            textareas = question_element.find_elements(By.XPATH, ".//textarea")
            selects = question_element.find_elements(By.XPATH, ".//select")
            
            if radio_buttons:
                return "multiple_choice_single"
            elif checkboxes:
                return "multiple_choice_multiple"
            elif text_inputs:
                return "text_input"
            elif textareas:
                return "text_area"
            elif selects:
                return "dropdown"
            else:
                return "unknown"
        except Exception as e:
            logging.error(f"Error detecting question type: {str(e)}")
            return "unknown"
    
    @staticmethod
    def is_trap_question(question_text: str) -> bool:
        """التحقق من كون السؤال سؤال فخ"""
        trap_patterns = [
            "please select",
            "attention check",
            "quality check",
            "select the",
            "choose the",
            "pick the",
            "اختر",
            "حدد",
            "انتبه",
            "فحص الجودة",
            "اختبار الانتباه"
        ]
        
        question_lower = question_text.lower()
        return any(pattern in question_lower for pattern in trap_patterns)
    
    @staticmethod
    def extract_question_text(question_element) -> str:
        """استخراج نص السؤال"""
        try:
            # البحث عن نص السؤال في عناصر مختلفة
            question_selectors = [
                ".//h1", ".//h2", ".//h3", ".//h4", ".//h5", ".//h6",
                ".//p", ".//div[@class*='question']", ".//span[@class*='question']",
                ".//label", ".//legend"
            ]
            
            for selector in question_selectors:
                elements = question_element.find_elements(By.XPATH, selector)
                for element in elements:
                    text = element.text.strip()
                    if text and len(text) > 10:  # تجاهل النصوص القصيرة جداً
                        return text
            
            # إذا لم نجد نص واضح، نأخذ النص الكامل للعنصر
            return question_element.text.strip()
        except Exception as e:
            logging.error(f"Error extracting question text: {str(e)}")
            return ""

class RewardingWaysAutomation:
    """محرك الأتمتة الرئيسي لموقع Rewarding Ways"""
    
    def __init__(self, user_settings: Dict, db_manager):
        self.user_settings = user_settings
        self.db_manager = db_manager
        self.driver = None
        self.wait = None
        self.is_logged_in = False
        self.current_survey = None
        self.behavior_sim = HumanBehaviorSimulator()
        self.survey_detector = SurveyDetector()
        
        # إضافة محرك التعلم الآلي
        try:
            from ml_engine import MLEngine
            self.ml_engine = MLEngine(db_manager.db_path)
            self.logger.info("تم تحميل محرك التعلم الآلي بنجاح")
        except Exception as e:
            self.logger.warning(f"فشل في تحميل محرك التعلم الآلي: {str(e)}")
            self.ml_engine = None
        
        # إعداد السجلات
        self.logger = logging.getLogger(__name__)
        
        # إحصائيات الجلسة
        self.session_stats = {
            'surveys_attempted': 0,
            'surveys_completed': 0,
            'surveys_failed': 0,
            'total_earnings': 0.0,
            'start_time': datetime.now(),
            'ml_predictions': 0,
            'trap_questions_detected': 0
        }
    
    def setup_driver(self) -> bool:
        """إعداد متصفح Chrome للأتمتة"""
        try:
            chrome_options = Options()
            
            # إعدادات لتجنب الكشف
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # إعدادات إضافية للتخفي
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # لتسريع التحميل
            
            # تشغيل في وضع headless إذا لزم الأمر
            # chrome_options.add_argument("--headless")
            
            # إنشاء الخدمة
            service = Service(ChromeDriverManager().install())
            
            # إنشاء المتصفح
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # إخفاء خصائص الأتمتة
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # إعداد الانتظار
            self.wait = WebDriverWait(self.driver, 10)
            
            # تعيين حجم النافذة
            self.driver.set_window_size(1366, 768)
            
            self.logger.info("تم إعداد المتصفح بنجاح")
            return True
            
        except Exception as e:
            self.logger.error(f"فشل في إعداد المتصفح: {str(e)}")
            return False
    
    def login(self) -> bool:
        """تسجيل الدخول إلى موقع Rewarding Ways"""
        try:
            self.logger.info("بدء عملية تسجيل الدخول...")
            
            # الانتقال إلى صفحة تسجيل الدخول
            self.driver.get("https://rewardingways.com/members/login.php")
            self.behavior_sim.random_delay(2, 4)
            
            # البحث عن حقول تسجيل الدخول
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = self.driver.find_element(By.NAME, "password")
            
            # إدخال بيانات الاعتماد
            self.behavior_sim.human_type(username_field, self.user_settings['username'])
            self.behavior_sim.random_delay(1, 2)
            self.behavior_sim.human_type(password_field, self.user_settings['password'])
            self.behavior_sim.random_delay(1, 2)
            
            # البحث عن زر تسجيل الدخول والنقر عليه
            login_button = self.driver.find_element(By.XPATH, "//input[@type='submit' or @value='Login' or @value='Sign In']")
            self.behavior_sim.human_click(self.driver, login_button)
            
            # انتظار تحميل الصفحة الرئيسية
            self.behavior_sim.random_delay(3, 5)
            
            # التحقق من نجاح تسجيل الدخول
            if "dashboard" in self.driver.current_url.lower() or "member" in self.driver.current_url.lower():
                self.is_logged_in = True
                self.logger.info("تم تسجيل الدخول بنجاح")
                return True
            else:
                self.logger.error("فشل في تسجيل الدخول")
                return False
                
        except TimeoutException:
            self.logger.error("انتهت مهلة الانتظار أثناء تسجيل الدخول")
            return False
        except Exception as e:
            self.logger.error(f"خطأ في تسجيل الدخول: {str(e)}")
            return False
    
    def find_available_surveys(self) -> List[Dict]:
        """البحث عن الاستبيانات المتاحة"""
        try:
            self.logger.info("البحث عن الاستبيانات المتاحة...")
            
            # الانتقال إلى صفحة الاستبيانات
            surveys_url = "https://rewardingways.com/members/surveys.php"
            self.driver.get(surveys_url)
            self.behavior_sim.random_delay(3, 5)
            
            surveys = []
            
            # البحث عن روابط الاستبيانات
            survey_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'survey') or contains(text(), '$')]")
            
            for link in survey_links[:10]:  # أخذ أول 10 استبيانات
                try:
                    survey_text = link.text.strip()
                    survey_url = link.get_attribute('href')
                    
                    # استخراج المبلغ من النص
                    amount = self.extract_amount_from_text(survey_text)
                    
                    if amount > 0 and survey_url:
                        surveys.append({
                            'name': survey_text,
                            'url': survey_url,
                            'amount': amount,
                            'element': link
                        })
                        
                except Exception as e:
                    self.logger.warning(f"خطأ في معالجة رابط الاستبيان: {str(e)}")
                    continue
            
            self.logger.info(f"تم العثور على {len(surveys)} استبيان متاح")
            return surveys
            
        except Exception as e:
            self.logger.error(f"خطأ في البحث عن الاستبيانات: {str(e)}")
            return []
    
    def extract_amount_from_text(self, text: str) -> float:
        """استخراج المبلغ من النص"""
        import re
        
        # البحث عن أنماط المبالغ
        patterns = [
            r'\$(\d+\.?\d*)',  # $1.50
            r'(\d+\.?\d*)\s*\$',  # 1.50$
            r'(\d+\.?\d*)\s*cents?',  # 150 cents
            r'(\d+\.?\d*)\s*points?'  # 150 points
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    amount = float(match.group(1))
                    # تحويل النقاط/السنتات إلى دولارات إذا لزم الأمر
                    if 'cent' in text.lower() or 'point' in text.lower():
                        amount = amount / 100
                    return amount
                except ValueError:
                    continue
        
        return 0.0
    
    def solve_survey(self, survey: Dict) -> bool:
        """حل استبيان محدد"""
        try:
            self.current_survey = survey
            self.session_stats['surveys_attempted'] += 1
            
            self.logger.info(f"بدء حل الاستبيان: {survey['name']}")
            
            # النقر على رابط الاستبيان
            self.behavior_sim.human_click(self.driver, survey['element'])
            self.behavior_sim.random_delay(3, 5)
            
            # التعامل مع النوافذ المنبثقة
            self.handle_popups()
            
            # حل أسئلة الاستبيان
            questions_solved = 0
            max_questions = 50  # حد أقصى لعدد الأسئلة
            
            while questions_solved < max_questions:
                try:
                    # البحث عن السؤال الحالي
                    question_element = self.find_current_question()
                    
                    if not question_element:
                        # ربما انتهى الاستبيان
                        if self.is_survey_completed():
                            self.logger.info("تم إكمال الاستبيان بنجاح")
                            self.session_stats['surveys_completed'] += 1
                            self.session_stats['total_earnings'] += survey['amount']
                            
                            # تسجيل الاستبيان في قاعدة البيانات
                            self.db_manager.log_survey(
                                survey['name'],
                                survey['url'],
                                survey['amount'],
                                'completed',
                                datetime.now(),
                                datetime.now()
                            )
                            
                            return True
                        else:
                            break
                    
                    # حل السؤال
                    if self.solve_question(question_element):
                        questions_solved += 1
                        self.logger.info(f"تم حل السؤال {questions_solved}")
                        self.behavior_sim.random_delay(2, 4)
                    else:
                        self.logger.warning("فشل في حل السؤال")
                        break
                        
                except Exception as e:
                    self.logger.error(f"خطأ في حل السؤال: {str(e)}")
                    break
            
            # إذا وصلنا هنا، فالاستبيان لم يكتمل بنجاح
            self.session_stats['surveys_failed'] += 1
            self.db_manager.log_survey(
                survey['name'],
                survey['url'],
                0.0,
                'failed',
                datetime.now(),
                datetime.now()
            )
            
            return False
            
        except Exception as e:
            self.logger.error(f"خطأ في حل الاستبيان: {str(e)}")
            self.session_stats['surveys_failed'] += 1
            return False
    
    def find_current_question(self):
        """البحث عن السؤال الحالي في الصفحة"""
        question_selectors = [
            "//div[contains(@class, 'question')]",
            "//form//div[contains(@class, 'form-group')]",
            "//fieldset",
            "//div[contains(@id, 'question')]",
            "//div[.//input[@type='radio'] or .//input[@type='checkbox']]"
        ]
        
        for selector in question_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed():
                        return element
            except:
                continue
        
        return None
    
    def solve_question(self, question_element) -> bool:
        """حل سؤال محدد باستخدام التعلم الآلي"""
        try:
            # استخراج نص السؤال
            question_text = self.survey_detector.extract_question_text(question_element)
            
            # تحديد نوع السؤال
            question_type = self.survey_detector.detect_question_type(question_element)
            
            # استخراج الخيارات
            options = self._extract_question_options(question_element, question_type)
            
            self.logger.info(f"نوع السؤال: {question_type}, الخيارات: {len(options)}")
            
            # استخدام محرك التعلم الآلي إذا كان متاحاً
            if self.ml_engine and options:
                ml_result = self.ml_engine.analyze_and_answer(
                    question_text, options, self.user_settings
                )
                
                self.session_stats['ml_predictions'] += 1
                
                if ml_result['trap_analysis']['is_trap']:
                    self.session_stats['trap_questions_detected'] += 1
                    self.logger.warning(f"تم اكتشاف سؤال فخ! الثقة: {ml_result['confidence']:.2f}")
                
                suggested_answer = ml_result['suggested_answer']
                
                if suggested_answer:
                    # تنفيذ الإجابة المقترحة
                    success = self._execute_ml_answer(question_element, question_type, suggested_answer, options)
                    
                    # التعلم من النتيجة
                    if self.ml_engine:
                        result_status = 'success' if success else 'failed'
                        self.ml_engine.learn_from_result(question_text, suggested_answer, result_status)
                    
                    return success
            
            # الرجوع إلى الطريقة التقليدية إذا فشل التعلم الآلي
            self.logger.info("استخدام الطريقة التقليدية لحل السؤال")
            
            # حل السؤال حسب نوعه (الطريقة التقليدية)
            if question_type == "multiple_choice_single":
                return self.solve_multiple_choice_single(question_element, question_text)
            elif question_type == "multiple_choice_multiple":
                return self.solve_multiple_choice_multiple(question_element, question_text)
            elif question_type == "text_input":
                return self.solve_text_input(question_element, question_text)
            elif question_type == "dropdown":
                return self.solve_dropdown(question_element, question_text)
            else:
                self.logger.warning(f"نوع سؤال غير مدعوم: {question_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"خطأ في حل السؤال: {str(e)}")
            return False
    
    def _extract_question_options(self, question_element, question_type: str) -> List[str]:
        """استخراج خيارات السؤال"""
        options = []
        
        try:
            if question_type == "multiple_choice_single":
                radio_buttons = question_element.find_elements(By.XPATH, ".//input[@type='radio']")
                for radio in radio_buttons:
                    try:
                        label = radio.find_element(By.XPATH, "./following-sibling::label")
                        options.append(label.text.strip())
                    except:
                        # محاولة العثور على النص بطريقة أخرى
                        parent = radio.find_element(By.XPATH, "./..")
                        text = parent.text.strip()
                        if text:
                            options.append(text)
            
            elif question_type == "multiple_choice_multiple":
                checkboxes = question_element.find_elements(By.XPATH, ".//input[@type='checkbox']")
                for checkbox in checkboxes:
                    try:
                        label = checkbox.find_element(By.XPATH, "./following-sibling::label")
                        options.append(label.text.strip())
                    except:
                        parent = checkbox.find_element(By.XPATH, "./..")
                        text = parent.text.strip()
                        if text:
                            options.append(text)
            
            elif question_type == "dropdown":
                from selenium.webdriver.support.ui import Select
                selects = question_element.find_elements(By.XPATH, ".//select")
                for select_element in selects:
                    select = Select(select_element)
                    for option in select.options:
                        if option.text.strip():
                            options.append(option.text.strip())
                    break  # أخذ أول قائمة منسدلة فقط
            
        except Exception as e:
            self.logger.error(f"خطأ في استخراج خيارات السؤال: {str(e)}")
        
        return options
    
    def _execute_ml_answer(self, question_element, question_type: str, 
                          suggested_answer: str, options: List[str]) -> bool:
        """تنفيذ الإجابة المقترحة من محرك التعلم الآلي"""
        try:
            if question_type == "multiple_choice_single":
                radio_buttons = question_element.find_elements(By.XPATH, ".//input[@type='radio']")
                
                for i, radio in enumerate(radio_buttons):
                    if i < len(options) and options[i] == suggested_answer:
                        self.behavior_sim.human_click(self.driver, radio)
                        return True
            
            elif question_type == "multiple_choice_multiple":
                checkboxes = question_element.find_elements(By.XPATH, ".//input[@type='checkbox']")
                
                # للأسئلة متعددة الخيارات، قد نحتاج لاختيار عدة خيارات
                # لكن هنا سنختار الخيار المقترح فقط
                for i, checkbox in enumerate(checkboxes):
                    if i < len(options) and options[i] == suggested_answer:
                        self.behavior_sim.human_click(self.driver, checkbox)
                        return True
            
            elif question_type == "text_input":
                text_inputs = question_element.find_elements(By.XPATH, ".//input[@type='text']")
                if text_inputs:
                    self.behavior_sim.human_type(text_inputs[0], suggested_answer)
                    return True
            
            elif question_type == "dropdown":
                from selenium.webdriver.support.ui import Select
                selects = question_element.find_elements(By.XPATH, ".//select")
                
                if selects:
                    select = Select(selects[0])
                    try:
                        select.select_by_visible_text(suggested_answer)
                        return True
                    except:
                        # إذا فشل الاختيار بالنص، جرب بالفهرس
                        for i, option in enumerate(options):
                            if option == suggested_answer:
                                select.select_by_index(i)
                                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"خطأ في تنفيذ الإجابة المقترحة: {str(e)}")
            return False
    
    def solve_multiple_choice_single(self, question_element, question_text: str) -> bool:
        """حل سؤال اختيار من متعدد (إجابة واحدة)"""
        try:
            radio_buttons = question_element.find_elements(By.XPATH, ".//input[@type='radio']")
            
            if not radio_buttons:
                return False
            
            # اختيار إجابة بناءً على المعلومات الشخصية أو عشوائياً
            selected_option = self.select_appropriate_answer(question_text, radio_buttons)
            
            if selected_option:
                self.behavior_sim.human_click(self.driver, selected_option)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"خطأ في حل سؤال الاختيار من متعدد: {str(e)}")
            return False
    
    def solve_multiple_choice_multiple(self, question_element, question_text: str) -> bool:
        """حل سؤال اختيار متعدد (عدة إجابات)"""
        try:
            checkboxes = question_element.find_elements(By.XPATH, ".//input[@type='checkbox']")
            
            if not checkboxes:
                return False
            
            # اختيار عدد عشوائي من الخيارات (1-3)
            num_to_select = random.randint(1, min(3, len(checkboxes)))
            selected_checkboxes = random.sample(checkboxes, num_to_select)
            
            for checkbox in selected_checkboxes:
                if checkbox.is_displayed() and checkbox.is_enabled():
                    self.behavior_sim.human_click(self.driver, checkbox)
                    self.behavior_sim.random_delay(0.5, 1.0)
            
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في حل سؤال الاختيار المتعدد: {str(e)}")
            return False
    
    def solve_text_input(self, question_element, question_text: str) -> bool:
        """حل سؤال إدخال نص"""
        try:
            text_inputs = question_element.find_elements(By.XPATH, ".//input[@type='text']")
            
            if not text_inputs:
                return False
            
            for text_input in text_inputs:
                if text_input.is_displayed() and text_input.is_enabled():
                    # تحديد النص المناسب بناءً على السؤال
                    answer_text = self.generate_text_answer(question_text)
                    self.behavior_sim.human_type(text_input, answer_text)
                    break
            
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في حل سؤال إدخال النص: {str(e)}")
            return False
    
    def solve_dropdown(self, question_element, question_text: str) -> bool:
        """حل سؤال القائمة المنسدلة"""
        try:
            from selenium.webdriver.support.ui import Select
            
            selects = question_element.find_elements(By.XPATH, ".//select")
            
            if not selects:
                return False
            
            for select_element in selects:
                if select_element.is_displayed() and select_element.is_enabled():
                    select = Select(select_element)
                    options = select.options
                    
                    if len(options) > 1:  # تجاهل الخيار الافتراضي
                        # اختيار خيار مناسب
                        selected_option = self.select_dropdown_option(question_text, options)
                        if selected_option:
                            select.select_by_visible_text(selected_option.text)
                            break
            
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في حل سؤال القائمة المنسدلة: {str(e)}")
            return False
    
    def select_appropriate_answer(self, question_text: str, options):
        """اختيار الإجابة المناسبة بناءً على السؤال والمعلومات الشخصية"""
        question_lower = question_text.lower()
        
        # البحث عن كلمات مفتاحية في السؤال
        for i, option in enumerate(options):
            try:
                option_text = option.find_element(By.XPATH, "./following-sibling::label").text.lower()
                
                # مطابقة المعلومات الشخصية
                if 'age' in question_lower or 'عمر' in question_lower:
                    age = self.user_settings.get('age', 25)
                    if str(age) in option_text or self.is_age_range_match(option_text, age):
                        return option
                
                elif 'gender' in question_lower or 'جنس' in question_lower:
                    gender = self.user_settings.get('gender', '').lower()
                    if ('male' in option_text and 'ذكر' in gender) or \
                       ('female' in option_text and 'أنثى' in gender):
                        return option
                
                elif 'city' in question_lower or 'مدينة' in question_lower:
                    city = self.user_settings.get('city', '').lower()
                    if city in option_text:
                        return option
                
            except:
                continue
        
        # إذا لم نجد مطابقة، اختر عشوائياً
        return random.choice(options) if options else None
    
    def is_age_range_match(self, option_text: str, age: int) -> bool:
        """التحقق من مطابقة العمر لنطاق عمري"""
        import re
        
        # البحث عن أنماط النطاقات العمرية
        patterns = [
            r'(\d+)-(\d+)',  # 18-25
            r'(\d+)\s*to\s*(\d+)',  # 18 to 25
            r'under\s*(\d+)',  # under 25
            r'over\s*(\d+)',  # over 65
        ]
        
        for pattern in patterns:
            match = re.search(pattern, option_text)
            if match:
                if 'under' in option_text:
                    max_age = int(match.group(1))
                    return age < max_age
                elif 'over' in option_text:
                    min_age = int(match.group(1))
                    return age > min_age
                else:
                    min_age = int(match.group(1))
                    max_age = int(match.group(2))
                    return min_age <= age <= max_age
        
        return False
    
    def generate_text_answer(self, question_text: str) -> str:
        """توليد إجابة نصية مناسبة"""
        question_lower = question_text.lower()
        
        # إجابات محددة مسبقاً للأسئلة الشائعة
        if 'name' in question_lower or 'اسم' in question_lower:
            return "John Smith"
        elif 'email' in question_lower or 'بريد' in question_lower:
            return "user@example.com"
        elif 'phone' in question_lower or 'هاتف' in question_lower:
            return "+1234567890"
        elif 'zip' in question_lower or 'postal' in question_lower or 'رمز' in question_lower:
            return self.user_settings.get('postal_code', '12345')
        elif 'city' in question_lower or 'مدينة' in question_lower:
            return self.user_settings.get('city', 'New York')
        elif 'country' in question_lower or 'بلد' in question_lower:
            return self.user_settings.get('country', 'United States')
        else:
            # إجابة عامة
            return "Not applicable"
    
    def select_dropdown_option(self, question_text: str, options):
        """اختيار خيار من القائمة المنسدلة"""
        question_lower = question_text.lower()
        
        # البحث عن خيار مناسب
        for option in options[1:]:  # تجاهل الخيار الأول (عادة "اختر...")
            option_text = option.text.lower()
            
            if 'country' in question_lower or 'بلد' in question_lower:
                user_country = self.user_settings.get('country', '').lower()
                if user_country in option_text:
                    return option
            elif 'state' in question_lower or 'ولاية' in question_lower:
                # اختيار ولاية عشوائية
                if any(state in option_text for state in ['california', 'texas', 'new york', 'florida']):
                    return option
        
        # اختيار عشوائي إذا لم نجد مطابقة
        return random.choice(options[1:]) if len(options) > 1 else None
    
    def solve_trap_question(self, question_element, question_text: str) -> bool:
        """حل أسئلة الفخ"""
        try:
            self.logger.info("محاولة حل سؤال فخ")
            
            # البحث عن الإجابة الصحيحة في قاعدة البيانات
            # (سيتم تطوير هذا في المرحلة التالية)
            
            # حل مؤقت: البحث عن كلمات مفتاحية
            question_lower = question_text.lower()
            
            if 'select' in question_lower and 'red' in question_lower:
                # البحث عن الخيار الأحمر
                return self.select_option_by_color(question_element, 'red')
            elif 'choose' in question_lower and 'blue' in question_lower:
                return self.select_option_by_color(question_element, 'blue')
            
            # إذا لم نتمكن من تحديد الإجابة، نختار عشوائياً
            return self.solve_multiple_choice_single(question_element, question_text)
            
        except Exception as e:
            self.logger.error(f"خطأ في حل سؤال الفخ: {str(e)}")
            return False
    
    def select_option_by_color(self, question_element, color: str) -> bool:
        """اختيار خيار بناءً على اللون"""
        try:
            radio_buttons = question_element.find_elements(By.XPATH, ".//input[@type='radio']")
            
            for radio in radio_buttons:
                try:
                    label = radio.find_element(By.XPATH, "./following-sibling::label")
                    if color.lower() in label.text.lower():
                        self.behavior_sim.human_click(self.driver, radio)
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"خطأ في اختيار الخيار بناءً على اللون: {str(e)}")
            return False
    
    def is_survey_completed(self) -> bool:
        """التحقق من إكمال الاستبيان"""
        completion_indicators = [
            "thank you",
            "completed",
            "finished",
            "success",
            "شكرا",
            "مكتمل",
            "انتهى",
            "نجح"
        ]
        
        page_text = self.driver.page_source.lower()
        return any(indicator in page_text for indicator in completion_indicators)
    
    def handle_popups(self):
        """التعامل مع النوافذ المنبثقة"""
        try:
            # التعامل مع النوافذ الجديدة
            if len(self.driver.window_handles) > 1:
                self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # إغلاق التنبيهات
            try:
                alert = self.driver.switch_to.alert
                alert.accept()
            except:
                pass
                
        except Exception as e:
            self.logger.warning(f"خطأ في التعامل مع النوافذ المنبثقة: {str(e)}")
    
    def run_automation_cycle(self) -> Dict:
        """تشغيل دورة أتمتة كاملة"""
        try:
            if not self.setup_driver():
                return {'success': False, 'error': 'فشل في إعداد المتصفح'}
            
            if not self.login():
                return {'success': False, 'error': 'فشل في تسجيل الدخول'}
            
            surveys = self.find_available_surveys()
            
            if not surveys:
                return {'success': True, 'message': 'لا توجد استبيانات متاحة'}
            
            # حل الاستبيانات
            for survey in surveys:
                try:
                    self.solve_survey(survey)
                    self.behavior_sim.random_delay(5, 10)  # انتظار بين الاستبيانات
                except Exception as e:
                    self.logger.error(f"خطأ في حل الاستبيان {survey['name']}: {str(e)}")
                    continue
            
            return {
                'success': True,
                'stats': self.session_stats
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في دورة الأتمتة: {str(e)}")
            return {'success': False, 'error': str(e)}
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def cleanup(self):
        """تنظيف الموارد"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

