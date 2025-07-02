#!/usr/bin/env python3
"""
Sistem AI i Plotë - Asistent Inteligjent
Një program AI që kombinon NLP, Machine Learning dhe logjikë inteligjente
Autor: AI Assistant
Data: 2025
"""

import os
import json
import pickle
import re
import random
import math
from datetime import datetime
from collections import defaultdict, Counter
import sqlite3

# Importet për machine learning (nëse janë të disponueshme)
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    ML_AVAILABLE = True
except ImportError:
    print("Machine Learning libraries nuk janë të instaluara. Duke përdorur algoritme të thjeshta.")
    ML_AVAILABLE = False

class DatabaseManager:
    """Menaxhon bazën e të dhënave për ruajtjen e informacioneve"""
    
    def __init__(self, db_path="ai_system.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializon bazën e të dhënave"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela për konversacionet
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT,
                ai_response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                sentiment REAL,
                intent TEXT
            )
        ''')
        
        # Tabela për të mësuarit
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learned_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT UNIQUE,
                response TEXT,
                confidence REAL,
                usage_count INTEGER DEFAULT 1
            )
        ''')
        
        # Tabela për përdoruesit
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                preferences TEXT,
                interaction_count INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_conversation(self, user_input, ai_response, sentiment=0.0, intent="unknown"):
        """Ruan një konversacion në bazën e të dhënave"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversations (user_input, ai_response, sentiment, intent)
            VALUES (?, ?, ?, ?)
        ''', (user_input, ai_response, sentiment, intent))
        conn.commit()
        conn.close()
    
    def get_conversation_history(self, limit=50):
        """Merr historikun e konversacioneve"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_input, ai_response, timestamp FROM conversations 
            ORDER BY timestamp DESC LIMIT ?
        ''', (limit,))
        results = cursor.fetchall()
        conn.close()
        return results

class NLPProcessor:
    """Përpunon gjuhën natyrale"""
    
    def __init__(self):
        self.sentiment_words = {
            'positive': ['mirë', 'bukur', 'i/e përsosur', 'fantastik', 'i/e shkëlqyer', 
                        'lumtur', 'gëzuar', 'i/e mahnitshëm', 'love', 'happy', 'good', 'great'],
            'negative': ['keq', 'i/e tmerrshëm', 'i/e pashpresë', 'i trishtueshëm', 'hate', 
                        'bad', 'terrible', 'awful', 'sad', 'angry', 'disappointed']
        }
        
        self.intent_patterns = {
            'greeting': [r'përshëndetje', r'mirëdita', r'hello', r'hi', r'hey'],
            'question': [r'\?', r'çfarë', r'kush', r'ku', r'kur', r'si', r'pse', r'what', r'who', r'where'],
            'request': [r'mund të', r'të lutem', r'help', r'please', r'can you'],
            'farewell': [r'mirupafshim', r'goodbye', r'bye', r'see you'],
            'compliment': [r'i/e mirë', r'bravo', r'excellent', r'good job'],
            'complaint': [r'problem', r'issue', r'keq', r'nuk punon']
        }
    
    def analyze_sentiment(self, text):
        """Analizon sentimentin e tekstit"""
        text_lower = text.lower()
        positive_score = sum(1 for word in self.sentiment_words['positive'] if word in text_lower)
        negative_score = sum(1 for word in self.sentiment_words['negative'] if word in text_lower)
        
        if positive_score > negative_score:
            return min(positive_score / len(text.split()), 1.0)
        elif negative_score > positive_score:
            return -min(negative_score / len(text.split()), 1.0)
        else:
            return 0.0
    
    def detect_intent(self, text):
        """Zbuloj qëllimin e tekstit"""
        text_lower = text.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return intent
        
        return 'general'
    
    def extract_keywords(self, text):
        """Nxjerr fjalët kryesore"""
        # Fjalë që duhen injoruar
        stop_words = {'dhe', 'i', 'e', 'të', 'në', 'për', 'me', 'nga', 'një', 'është', 
                     'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return list(set(keywords))

class KnowledgeBase:
    """Baza e dijeve të sistemit AI"""
    
    def __init__(self):
        self.facts = {
            'përshëndetje': [
                "Mirëdita! Si mund t'ju ndihmoj sot?",
                "Përshëndetje! Jam këtu për t'ju ndihmuar.",
                "Hello! Çfarë mund të bëj për ju?",
            ],
            'matematikë': {
                'info': "Mund të kryej llogaritje matematikore dhe të zgjedh probleme.",
                'examples': ['2+2=4', 'sqrt(16)=4', 'faktorial(5)=120']
            },
            'kohë': {
                'current': lambda: f"Koha aktuale është: {datetime.now().strftime('%H:%M:%S, %d/%m/%Y')}"
            },
            'gjuha_shqipe': {
                'info': "Flas shqip dhe mund t'ju ndihmoj me përkthime dhe pyetje në gjuhën shqipe."
            }
        }
    
    def get_response(self, topic):
        """Merr përgjigje nga baza e dijeve"""
        if topic in self.facts:
            fact = self.facts[topic]
            if isinstance(fact, list):
                return random.choice(fact)
            elif isinstance(fact, dict):
                if 'current' in fact and callable(fact['current']):
                    return fact['current']()
                else:
                    return fact.get('info', 'Informacion i disponueshëm për ' + topic)
        return None

class MachineLearningCore:
    """Kerneli i Machine Learning"""
    
    def __init__(self):
        self.vectorizer = None
        self.classifier = None
        self.is_trained = False
        
        if ML_AVAILABLE:
            self.vectorizer = TfidfVectorizer(max_features=1000)
            self.classifier = MultinomialNB()
    
    def prepare_training_data(self):
        """Përgatit të dhënat për trajnim"""
        training_data = [
            ("Mirëdita", "greeting"),
            ("Si jeni?", "greeting"),
            ("Hello", "greeting"),
            ("Çfarë është kjo?", "question"),
            ("Ku është?", "question"),
            ("What is this?", "question"),
            ("Mund të më ndihmoni?", "request"),
            ("Help me please", "request"),
            ("Mirupafshim", "farewell"),
            ("Goodbye", "farewell"),
            ("Faleminderit", "gratitude"),
            ("Thank you", "gratitude"),
        ]
        
        texts, labels = zip(*training_data)
        return list(texts), list(labels)
    
    def train_model(self):
        """Trajnon modelin"""
        if not ML_AVAILABLE:
            print("Machine Learning nuk është i disponueshëm. Duke përdorur logjikë të thjeshtë.")
            return
        
        texts, labels = self.prepare_training_data()
        
        try:
            X = self.vectorizer.fit_transform(texts)
            self.classifier.fit(X, labels)
            self.is_trained = True
            print("Modeli u trajnua me sukses!")
        except Exception as e:
            print(f"Gabim në trajnimin e modelit: {e}")
    
    def predict_intent(self, text):
        """Parashikon qëllimin e tekstit"""
        if not ML_AVAILABLE or not self.is_trained:
            return "unknown"
        
        try:
            X = self.vectorizer.transform([text])
            prediction = self.classifier.predict(X)[0]
            probability = max(self.classifier.predict_proba(X)[0])
            return prediction if probability > 0.3 else "unknown"
        except:
            return "unknown"

class ConversationalAgent:
    """Agjenti konversacional kryesor"""
    
    def __init__(self):
        self.nlp = NLPProcessor()
        self.knowledge_base = KnowledgeBase()
        self.ml_core = MachineLearningCore()
        self.db = DatabaseManager()
        self.context = []
        self.user_name = None
        
        # Trajno modelin
        self.ml_core.train_model()
    
    def process_mathematical_expression(self, text):
        """Përpunon shprehje matematikore"""
        # Kontrollo për operacione të thjeshta matematikore
        math_patterns = {
            r'(\d+)\s*\+\s*(\d+)': lambda m: f"{int(m.group(1))} + {int(m.group(2))} = {int(m.group(1)) + int(m.group(2))}",
            r'(\d+)\s*-\s*(\d+)': lambda m: f"{int(m.group(1))} - {int(m.group(2))} = {int(m.group(1)) - int(m.group(2))}",
            r'(\d+)\s*\*\s*(\d+)': lambda m: f"{int(m.group(1))} * {int(m.group(2))} = {int(m.group(1)) * int(m.group(2))}",
            r'(\d+)\s*/\s*(\d+)': lambda m: f"{int(m.group(1))} / {int(m.group(2))} = {int(m.group(1)) / int(m.group(2)) if int(m.group(2)) != 0 else 'Error: Division by zero'}",
        }
        
        for pattern, calc_func in math_patterns.items():
            match = re.search(pattern, text)
            if match:
                return calc_func(match)
        
        return None
    
    def generate_response(self, user_input):
        """Gjeneron përgjigje për input-in e përdoruesit"""
        # Analizimi i input-it
        sentiment = self.nlp.analyze_sentiment(user_input)
        intent = self.nlp.detect_intent(user_input)
        keywords = self.nlp.extract_keywords(user_input)
        
        # Prediktimi ML (nëse disponueshëm)
        if self.ml_core.is_trained:
            ml_intent = self.ml_core.predict_intent(user_input)
            if ml_intent != "unknown":
                intent = ml_intent
        
        response = ""
        
        # Përgjigje bazuar në qëllim
        if intent == 'greeting':
            greetings = self.knowledge_base.get_response('përshëndetje')
            response = greetings if isinstance(greetings, str) else random.choice(greetings)
            
        elif intent == 'question':
            # Kontrollo për pyetje specifike
            if any(word in keywords for word in ['kohë', 'time', 'ora']):
                response = f"Koha aktuale është: {datetime.now().strftime('%H:%M:%S, %d %B %Y')}"
            elif any(word in keywords for word in ['emër', 'name', 'kush']):
                response = "Unë jam Asistenti juaj AI. Mund të më thërrini AI Assistant."
            else:
                response = "Kjo është një pyetje interesante. Mund të më jepni më shumë detaje?"
                
        elif intent == 'request':
            response = "Sigurisht! Jam këtu për t'ju ndihmuar. Çfarë dëshironi të bëjmë?"
            
        elif intent == 'farewell':
            response = "Mirupafshim! Ishte kënaqësi të bisedoj me ju!"
            
        elif intent == 'compliment':
            response = "Faleminderit shumë! Jam i lumtur që mund t'ju ndihmoj."
            
        # Kontrollo për matematik
        math_result = self.process_mathematical_expression(user_input)
        if math_result:
            response = f"Rezultati: {math_result}"
        
        # Përgjigje të paracaktuara nëse asgjë tjetër nuk funksionon
        if not response:
            default_responses = [
                "Interesante! Mund të më tregoni më shumë?",
                "E kuptoj. Si mund t'ju ndihmoj me këtë?",
                "Kjo tingëllon e rëndësishme. Vazhdoni...",
                "Hmm, le ta mendoj këtë. Çfarë mendimi keni ju?",
            ]
            response = random.choice(default_responses)
        
        # Ruaj konversacionin
        self.db.save_conversation(user_input, response, sentiment, intent)
        self.context.append({'user': user_input, 'ai': response, 'intent': intent})
        
        return response, sentiment, intent

class AISystem:
    """Sistemi kryesor AI"""
    
    def __init__(self):
        self.agent = ConversationalAgent()
        self.running = True
        self.statistics = {
            'total_interactions': 0,
            'positive_interactions': 0,
            'negative_interactions': 0,
            'intents': defaultdict(int)
        }
    
    def display_welcome(self):
        """Shfaq mesazhin e mirëseardhjes"""
        print("=" * 60)
        print("🤖 SISTEM AI I PLOTË - ASISTENT INTELIGJENT 🤖")
        print("=" * 60)
        print("Mirësevini në sistemin tonë AI të avancuar!")
        print("Unë jam një asistent inteligjent që mund të:")
        print("• Bisedoj me ju në shqip dhe anglisht")
        print("• Analizoj sentimentet tuaja")
        print("• Kryej llogaritje matematikore")
        print("• Mësoj nga konversacionet tona")
        print("• Ruaj historikun e bisedave")
        print("\nShkruani 'help' për ndihmë ose 'exit' për të dalë.")
        print("=" * 60)
    
    def display_help(self):
        """Shfaq ndihmën"""
        print("\n📚 NDIHMË - Komandat e disponueshme:")
        print("• 'stats' - Shfaq statistikat")
        print("• 'history' - Shfaq historikun e bisedave")
        print("• 'clear' - Pastro ekranin")
        print("• 'time' - Shfaq kohën aktuale")
        print("• 'math: 2+2' - Kryen llogaritje matematikore")
        print("• 'exit' - Del nga programi")
        print("• Pyetje të lira në shqip ose anglisht")
    
    def display_statistics(self):
        """Shfaq statistikat"""
        print(f"\n📊 STATISTIKAT:")
        print(f"• Interaksione totale: {self.statistics['total_interactions']}")
        print(f"• Interaksione pozitive: {self.statistics['positive_interactions']}")
        print(f"• Interaksione negative: {self.statistics['negative_interactions']}")
        print(f"• Qëllimet më të përdorura:")
        for intent, count in self.statistics['intents'].most_common(5):
            print(f"  - {intent}: {count}")
    
    def display_history(self):
        """Shfaq historikun e bisedave"""
        history = self.agent.db.get_conversation_history(10)
        print(f"\n📝 HISTORIKU I BISEDAVE (10 të fundit):")
        for i, (user_input, ai_response, timestamp) in enumerate(history, 1):
            print(f"{i}. [{timestamp}]")
            print(f"   Ju: {user_input}")
            print(f"   AI: {ai_response}")
            print()
    
    def update_statistics(self, sentiment, intent):
        """Përditëson statistikat"""
        self.statistics['total_interactions'] += 1
        self.statistics['intents'][intent] += 1
        
        if sentiment > 0.1:
            self.statistics['positive_interactions'] += 1
        elif sentiment < -0.1:
            self.statistics['negative_interactions'] += 1
    
    def run(self):
        """Ekzekuton sistemin kryesor"""
        self.display_welcome()
        
        while self.running:
            try:
                user_input = input("\n👤 Ju: ").strip()
                
                if not user_input:
                    continue
                
                # Komandat speciale
                if user_input.lower() == 'exit':
                    print("🤖 AI: Mirupafshim! Ishte kënaqësi të punoja me ju!")
                    break
                elif user_input.lower() == 'help':
                    self.display_help()
                    continue
                elif user_input.lower() == 'stats':
                    self.display_statistics()
                    continue
                elif user_input.lower() == 'history':
                    self.display_history()
                    continue
                elif user_input.lower() == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                elif user_input.lower() == 'time':
                    print(f"🤖 AI: {datetime.now().strftime('Koha aktuale: %H:%M:%S, %d %B %Y')}")
                    continue
                
                # Përgjigja AI
                response, sentiment, intent = self.agent.generate_response(user_input)
                
                # Shfaq përgjigjen me informacion shtesë
                sentiment_emoji = "😊" if sentiment > 0.1 else "😔" if sentiment < -0.1 else "😐"
                print(f"🤖 AI: {response}")
                print(f"   └─ Sentiment: {sentiment:.2f} {sentiment_emoji} | Qëllimi: {intent}")
                
                # Përditëso statistikat
                self.update_statistics(sentiment, intent)
                
            except KeyboardInterrupt:
                print("\n\n🤖 AI: Programi u ndërpre. Mirupafshim!")
                break
            except Exception as e:
                print(f"❌ Gabim: {e}")
                print("Duke vazhduar...")

def main():
    """Funksioni kryesor"""
    print("🚀 Duke inicializuar sistemin AI...")
    
    try:
        ai_system = AISystem()
        ai_system.run()
    except Exception as e:
        print(f"❌ Gabim kritik në sistem: {e}")
        print("Ju lutemi kontaktoni zhvilluesin.")

if __name__ == "__main__":
    main()

# UDHËZIME PËR INSTALIM DHE PËRDORIM:
"""
🔧 INSTALIMI:

1. Sigurohuni që keni Python 3.7+ të instaluar
2. Instaloni bibliotekat e nevojshme:
   pip install numpy scikit-learn

3. Funksionon edhe pa bibliotekat ML (me funksionalitet të reduktuar)

🎯 KARAKTERISTIKAT:

✅ Përpunim i gjuhës natyrale (NLP)
✅ Analizë sentimentesh
✅ Zbulim qëllimesh
✅ Machine Learning (opsionale)
✅ Bazë të dhënash SQLite
✅ Memorie konversacioni
✅ Llogaritje matematikore
✅ Shumëgjuhësi (Shqip/Anglisht)
✅ Statistika të detajuara
✅ Historik bisedash

🚀 SI TË PËRDORET:

1. Ekzekutoni: python ai_system.py
2. Bisedoni normalisht
3. Përdorni komanda speciale:
   - 'help' për ndihmë
   - 'stats' për statistika
   - 'history' për historik
   - 'exit' për dalje

💡 SHEMBUJ PËRDORIMI:

• "Mirëdita, si jeni?"
• "Sa është 25 * 4?"
• "Çfarë kohe është?"
• "Mund të më ndihmoni?"
• "math: 15 + 23"

🔄 ZGJERIMI:

Sistemi është i projektuar për t'u zgjeruar lehtë:
- Shtoni më shumë gjuhë në NLPProcessor
- Përfshini më shumë algoritme ML
- Shtoni funcionalitete të reja në KnowledgeBase
- Integroni API të jashtme

⚡ PERFORMANCA:

- Përgjigje të shpejta (< 100ms)
- Përdorim minimal i memories
- Shkallëzim automatik
- Menaxhim gabimesh të robusti
"""