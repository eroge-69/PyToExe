import time
import webbrowser
import random
import sys
import os
from datetime import datetime

class RickRollSimulator:
    def __init__(self):
        self.score = 0
        self.username = ""
        self.start_time = None
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def type_effect(self, text, delay=0.03):
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()
    
    def loading_animation(self, duration=3, message="Yükleniyor"):
        print(f"\n{message} [", end="")
        for i in range(duration * 2):
            print("█", end="", flush=True)
            time.sleep(0.5)
        print("] Tamamlandı!")
    
    def print_banner(self):
        banner = """
╔══════════════════════════════════════════════╗
║           🐍 PYTHON MASTER TEST 🐍           ║
║        Resmi Python Sertifika Programı       ║
╚══════════════════════════════════════════════╝
        """
        print(banner)
    
    def introduction(self):
        self.clear_screen()
        self.print_banner()
        self.type_effect("🤖 Hoş geldiniz! Ben Python Asistanı Pythia.")
        time.sleep(1)
        
        self.username = input("\n🎯 Lütfen adınızı girin: ").strip() or "Değerli Kullanıcı"
        self.type_effect(f"\n✨ Merhaba {self.username}! Python becerilerinizi değerlendireceğiz.")
        self.type_effect("📊 Test sonucuna göre resmi sertifika kazanacaksınız!")
        
        input("\n⏎ Devam etmek için ENTER tuşuna basın...")
    
    def question_1_math(self):
        self.clear_screen()
        print("🧮 TEST 1: Matematiksel Mantık")
        print("=" * 40)
        
        a, b = random.randint(10, 50), random.randint(5, 20)
        correct_answer = a + b
        
        self.type_effect(f"\nSoru: {a} + {b} = ?")
        self.type_effect("Bu temel matematik becerilerinizi test eder...")
        
        try:
            answer = int(input("\n🎯 Cevabınız: "))
            if answer == correct_answer:
                self.type_effect("✅ Mükemmel! Doğru cevap!")
                self.score += 10
            else:
                self.type_effect(f"❌ Yanlış! Doğru cevap: {correct_answer}")
        except:
            self.type_effect("⚠️ Geçersiz giriş! Puan verilemedi.")
        
        self.loading_animation(2, "Sonuçlar kaydediliyor")
    
    def question_2_programming(self):
        self.clear_screen()
        print("💻 TEST 2: Programlama Bilgisi")
        print("=" * 40)
        
        # ✅ SORULAR BURADA TANIMLANDI
        questions = [
            {
                "question": "Python'da liste oluşturmak için hangi semboller kullanılır?",
                "options": ["A) ()", "B) {}", "C) []", "D: <>"],
                "correct": "C"
            },
            {
                "question": "'Hello World' yazdırmak için hangi komut kullanılır?",
                "options": ["A) console.log()", "B) print()", "C) echo", "D) System.out.println()"],
                "correct": "B"
            }
        ]
        
        q = random.choice(questions)
        self.type_effect(f"\n{q['question']}")
        
        for option in q['options']:
            print(f"   {option}")
        
        answer = input("\n🎯 Cevabınız (A/B/C/D): ").upper().strip()
        
        if answer == q['correct']:
            self.type_effect("✅ Bravo! Python bilginiz harika!")
            self.score += 15
        else:
            self.type_effect(f"❌ Maalesef yanlış! Doğru cevap: {q['correct']}")
        
        self.loading_animation(2, "Analiz ediliyor")
    
    def question_3_logic(self):
        self.clear_screen()
        print("🎲 TEST 3: Mantık Bulmacası")
        print("=" * 40)
        
        self.type_effect("\n2, 3, 5, 8, 13, ?")
        self.type_effect("Bu serideki sonraki sayıyı bulun...")
        
        correct_answer = 21  # Fibonacci
        
        try:
            answer = int(input("\n🎯 Cevabınız: "))
            if answer == correct_answer:
                self.type_effect("✅ İnanılmaz! Matematiksel sezginiz müthiş!")
                self.score += 20
            else:
                self.type_effect(f"❌ Yaklaştınız! Doğru cevap: {correct_answer} (Fibonacci)")
        except:
            self.type_effect("⚠️ Sayı girmelisiniz!")
        
        self.loading_animation(3, "Zeka seviyesi ölçülüyor")
    
    def fake_certificate_generation(self):
        self.clear_screen()
        print("📊 TEST SONUÇLARI")
        print("=" * 40)
        
        total_possible = 45
        percentage = (self.score / total_possible) * 100
        
        self.type_effect(f"\n👤 Katılımcı: {self.username}")
        self.type_effect(f"📈 Puanınız: {self.score}/{total_possible}")
        self.type_effect(f"📊 Başarı Oranı: %{percentage:.1f}")
        
        time.sleep(2)
        
        # Dramatik efekt
        print("\n" + "🎭" * 20)
        self.type_effect("🎉 TEBRİKLER! Tüm testleri tamamladınız!", 0.05)
        
        if percentage >= 80:
            self.type_effect("🏆 SEVİYE: PYTHON UZMANI", 0.1)
        elif percentage >= 50:
            self.type_effect("🥈 SEVİYE: PYTHON GELİŞTİRİCİ", 0.1)
        else:
            self.type_effect("🎯 SEVİYE: PYTHON ADAYI", 0.1)
        
        print("🎭" * 20)
        
        time.sleep(2)
        self.type_effect("\n🎁 Ödülünüz hazırlanıyor...", 0.1)
        self.loading_animation(5, "Resmi sertifika oluşturuluyor")
    
    def the_rickroll(self):
        self.clear_screen()
        
        # Dramatik geri sayım
        print("🎊 ÖDÜL AÇILIYOR 🎊")
        print("=" * 35)
        
        for i in range(5, 0, -1):
            print(f"⏰ {i}...")
            time.sleep(1)
        
        self.clear_screen()
        
        # Rickroll ASCII art
        rick_art = """
        ╔══════════════════════════════════════════╗
        ║                🎵 SÜRPRİZ! 🎵            ║
        ║                                          ║
        ║        🤠 RICK ASTLEY SUNAR!            ║
        ║                                          ║
        ║    🎶 Never Gonna Give You Up 🎶        ║
        ║                                          ║
        ║    We're no strangers to love...        ║
        ║    You know the rules and so do I...    ║
        ║                                          ║
        ║        🎭 BU BİR RICKROLL! 🎭           ║
        ╚══════════════════════════════════════════╝
        """
        print(rick_art)
        
        # Şarkı sözleri efekti
        lyrics = [
            "Never gonna give you up...",
            "Never gonna let you down...", 
            "Never gonna run around and desert you...",
            "Never gonna make you cry...",
            "Never gonna say goodbye...",
            "Never gonna tell a lie and hurt you...",
            f"\n😄 Şaka yaptık {self.username}! İyi eğlenceler!"
        ]
        
        for line in lyrics:
            self.type_effect(line, 0.08)
            time.sleep(2)
        
        # YouTube'u aç
        self.type_effect("\n🎬 Video açılıyor...", 0.05)
        time.sleep(2)
        
        try:
            webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ&autoplay=1")
        except:
            self.type_effect("❌ Tarayıcı açılamadı, manuel olarak ziyaret edin:")
            self.type_effect("📺 https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
    def run(self):
        self.start_time = datetime.now()
        
        try:
            self.introduction()
            self.question_1_math()
            self.question_2_programming() 
            self.question_3_logic()
            self.fake_certificate_generation()
            self.the_rickroll()
            
        except KeyboardInterrupt:
            self.type_effect("\n\n❌ Program kapatıldı. Bir dahaki sefere! 👋")
        except Exception as e:
            self.type_effect(f"\n\n⚠️ Bir hata oluştu: {e}")

if __name__ == "__main__":
    simulator = RickRollSimulator()
    simulator.run()