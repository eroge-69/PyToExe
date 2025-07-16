import customtkinter
import threading
from googletrans import Translator
from PIL import Image, ImageTk
import requests
from gtts import gTTS
import pygame
import io

# --- کلاس اصلی مترجم ---
class TranslatorApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # --- کلید API خود را اینجا قرار دهید ---
        # این کلید را از سایت Pexels دریافت کرده‌اید
        self.PEXELS_API_KEY = "YOUR_PEXELS_API_KEY_HERE"

        # --- تنظیمات اصلی پنجره ---
        self.title("مترجم هوشمند")
        self.geometry("800x600")
        self.resizable(False, False)
        customtkinter.set_appearance_mode("dark")

        # مقداردهی اولیه pygame برای پخش صدا
        pygame.mixer.init()

        # متغیر برای ذخیره فایل صوتی تلفظ
        self.pronunciation_audio = None

        self.create_widgets()

    def create_widgets(self):
        """ساخت تمام ویجت‌های رابط کاربری"""
        self.grid_columnconfigure(0, weight=1)

        # --- فریم ورودی ---
        input_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        input_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        self.entry = customtkinter.CTkEntry(
            input_frame,
            placeholder_text="کلمه فارسی را وارد کنید...",
            font=customtkinter.CTkFont(family="Vazirmatn", size=16),
            height=40
        )
        self.entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.entry.bind("<Return>", self.start_translation_thread)

        self.translate_button = customtkinter.CTkButton(
            input_frame,
            text="ترجمه کن",
            font=customtkinter.CTkFont(family="Vazirmatn", size=14, weight="bold"),
            height=40,
            command=self.start_translation_thread
        )
        self.translate_button.grid(row=0, column=1, sticky="e")

        # --- فریم نتایج ---
        result_frame = customtkinter.CTkFrame(self)
        result_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)
        result_frame.grid_columnconfigure(1, weight=1)
        result_frame.grid_rowconfigure(0, weight=1)

        # --- بخش متنی (چپ) ---
        text_result_frame = customtkinter.CTkFrame(result_frame, fg_color="transparent")
        text_result_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        text_result_frame.grid_columnconfigure(0, weight=1)

        self.translated_word_label = customtkinter.CTkLabel(text_result_frame, text="", font=customtkinter.CTkFont(size=36, weight="bold"))
        self.translated_word_label.pack(pady=(0, 10))

        self.pronounce_button = customtkinter.CTkButton(text_result_frame, text="🔊 تلفظ", state="disabled", command=self.play_pronunciation)
        self.pronounce_button.pack(pady=10)
        
        examples_label = customtkinter.CTkLabel(text_result_frame, text="مثال‌ها:", font=customtkinter.CTkFont(size=16, weight="bold"), anchor="e")
        examples_label.pack(fill="x", pady=(20, 5))

        self.examples_textbox = customtkinter.CTkTextbox(text_result_frame, font=customtkinter.CTkFont(family="Vazirmatn", size=14), wrap="word", state="disabled")
        self.examples_textbox.pack(fill="both", expand=True)

        # --- فلش کارت تصویری (راست) ---
        self.image_label = customtkinter.CTkLabel(result_frame, text="")
        self.image_label.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # --- نوار وضعیت ---
        self.status_label = customtkinter.CTkLabel(self, text="آماده", anchor="e", font=customtkinter.CTkFont(size=12))
        self.status_label.grid(row=2, column=0, padx=20, pady=(5, 10), sticky="ew")

    def start_translation_thread(self, event=None):
        """اجرای فرآیند ترجمه در یک ترد جدا برای جلوگیری از فریز شدن برنامه"""
        word = self.entry.get().strip()
        if not word:
            self.status_label.configure(text="لطفا یک کلمه وارد کنید.")
            return

        self.translate_button.configure(state="disabled", text="...")
        self.status_label.configure(text="در حال جستجو...")
        
        # پاک کردن نتایج قبلی
        self.clear_results()

        thread = threading.Thread(target=self.perform_translation, args=(word,))
        thread.start()

    def perform_translation(self, word):
        """منطق اصلی برای دریافت تمام اطلاعات از API ها"""
        try:
            # 1. ترجمه کلمه
            translator = Translator()
            translation = translator.translate(word, src='fa', dest='en')
            english_word = translation.text.lower()

            # 2. دریافت تصویر
            image_data = self.fetch_image(english_word)

            # 3. دریافت مثال و تلفظ
            examples, audio_data = self.fetch_details(english_word)

            # 4. آپدیت UI در ترد اصلی
            self.after(0, self.update_ui, english_word, examples, image_data, audio_data)

        except Exception as e:
            self.after(0, self.status_label.configure, {"text": f"خطا: {e}"})
        finally:
            self.after(0, self.translate_button.configure, {"state": "normal", "text": "ترجمه کن"})

    def fetch_image(self, query):
        """دریافت تصویر از Pexels API"""
        if self.PEXELS_API_KEY == "YOUR_PEXELS_API_KEY_HERE":
            raise Exception("کلید API برای Pexels تنظیم نشده است!")
        headers = {"Authorization": self.PEXELS_API_KEY}
        url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
        response = requests.get(url, headers=headers)
        if response.status_code == 200 and response.json()['photos']:
            image_url = response.json()['photos'][0]['src']['large']
            image_response = requests.get(image_url)
            return image_response.content
        return None

    def fetch_details(self, word):
        """دریافت مثال از Dictionary API و ساخت تلفظ با gTTS"""
        # دریافت مثال
        examples = "مثالی یافت نشد."
        try:
            response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
            if response.status_code == 200:
                data = response.json()[0]
                definitions = data['meanings'][0]['definitions']
                example_list = [d['example'] for d in definitions if 'example' in d]
                if example_list:
                    examples = "\n\n".join(f"- {ex}" for ex in example_list[:3]) # نمایش 3 مثال
        except Exception:
            pass # اگر مثالی نبود، مهم نیست

        # ساخت تلفظ
        tts = gTTS(text=word, lang='en', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return examples, fp

    def update_ui(self, english_word, examples, image_data, audio_data):
        """به‌روزرسانی تمام ویجت‌ها با اطلاعات جدید"""
        # نمایش کلمه ترجمه شده
        self.translated_word_label.configure(text=english_word.capitalize())

        # نمایش مثال‌ها
        self.examples_textbox.configure(state="normal")
        self.examples_textbox.delete("1.0", "end")
        self.examples_textbox.insert("1.0", examples)
        self.examples_textbox.configure(state="disabled")

        # نمایش تصویر
        if image_data:
            img = Image.open(io.BytesIO(image_data))
            ctk_img = customtkinter.CTkImage(light_image=img, dark_image=img, size=(350, 350))
            self.image_label.configure(image=ctk_img)
        else:
            self.image_label.configure(image=None, text="تصویری یافت نشد")

        # فعال کردن دکمه تلفظ
        self.pronunciation_audio = audio_data
        self.pronounce_button.configure(state="normal")
        
        self.status_label.configure(text="ترجمه با موفقیت انجام شد.")

    def play_pronunciation(self):
        """پخش فایل صوتی تلفظ"""
        if self.pronunciation_audio:
            self.pronunciation_audio.seek(0)
            pygame.mixer.music.load(self.pronunciation_audio)
            pygame.mixer.music.play()

    def clear_results(self):
        """پاک کردن نتایج جستجوی قبلی"""
        self.translated_word_label.configure(text="")
        self.examples_textbox.configure(state="normal")
        self.examples_textbox.delete("1.0", "end")
        self.examples_textbox.configure(state="disabled")
        self.image_label.configure(image=None, text="")
        self.pronounce_button.configure(state="disabled")

# --- اجرای برنامه ---
if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()

