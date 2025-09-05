import logging
import random
import re
from collections import defaultdict
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neural_network import MLPClassifier

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TextGenerator:
    def __init__(self):
        self.phrases = []
        self.word_dict = defaultdict(list)
        self.vectorizer = CountVectorizer()
        self.model = MLPClassifier(hidden_layer_sizes=(100, 50), random_state=42, max_iter=500)
        self.is_trained = False
    
    def preprocess_text(self, text):
        """Предобработка текста: удаление знаков препинания, приведение к нижнему регистру"""
        text = re.sub(r'[^\w\s]', '', text.lower())
        words = text.split()
        return ' '.join(words)
    
    def add_phrases(self, text):
        """Добавление фраз для обучения"""
        lines = text.split('\n')
        processed_lines = [self.preprocess_text(line) for line in lines if line.strip()]
        self.phrases.extend(processed_lines)
        
        # Обновляем словарь слов
        for line in processed_lines:
            words = line.split()
            for i in range(len(words) - 1):
                self.word_dict[words[i]].append(words[i + 1])
        
        # Обучаем модель если набралось достаточно данных
        if len(self.phrases) >= 5:
            self.train_model()
    
    def train_model(self):
        """Обучение нейросетевой модели"""
        if len(self.phrases) < 3:
            return
        
        try:
            # Создаем признаки (bag of words)
            X = self.vectorizer.fit_transform(self.phrases)
            y = list(range(len(self.phrases)))
            
            # Обучаем нейросеть
            self.model.fit(X, y)
            self.is_trained = True
            logger.info(f"Модель обучена на {len(self.phrases)} фразах")
        except Exception as e:
            logger.error(f"Ошибка обучения модели: {e}")
            self.is_trained = False
    
    def generate_word(self, previous_word):
        """Генерация следующего слова на основе предыдущего"""
        if previous_word in self.word_dict and self.word_dict[previous_word]:
            return random.choice(self.word_dict[previous_word])
        return random.choice(list(self.word_dict.keys())) if self.word_dict else "слово"
    
    def generate_text(self, num_lines=10):
        """Генерация текста"""
        if not self.phrases:
            return "нет данных для генерации сначала отправьте phrases txt"
        
        generated_lines = []
        
        for _ in range(num_lines):
            # Случайно выбираем подход
            if self.is_trained and random.random() > 0.4 and len(self.phrases) >= 5:
                # Нейросетевой подход
                try:
                    seed_idx = random.randint(0, len(self.phrases) - 1)
                    seed_vector = self.vectorizer.transform([self.phrases[seed_idx]])
                    
                    # Получаем предсказания
                    probabilities = self.model.predict_proba(seed_vector)[0]
                    top_indices = np.argsort(probabilities)[-2:]
                    
                    # Собираем слова из топовых фраз
                    all_words = []
                    for idx in top_indices:
                        if idx < len(self.phrases):
                            all_words.extend(self.phrases[idx].split())
                    
                    if all_words:
                        # Создаем новую фразу из слов
                        line_length = random.randint(4, 12)
                        line_words = random.sample(all_words, min(line_length, len(all_words)))
                        generated_lines.append(' '.join(line_words))
                        continue
                except Exception as e:
                    logger.warning(f"Нейросетевой подход не сработал: {e}")
            
            # Подход на основе цепей слов
            current_word = random.choice(list(self.word_dict.keys())) if self.word_dict else "текст"
            line_words = [current_word]
            
            line_length = random.randint(4, 15)
            for _ in range(line_length - 1):
                next_word = self.generate_word(current_word)
                line_words.append(next_word)
                current_word = next_word
            
            generated_lines.append(' '.join(line_words))
        
        return '\n'.join(generated_lines)

# Инициализация генератора
text_generator = TextGenerator()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['10 строк', '50 строк', '100 строк', '200 строк', '500 строк']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        'привет отправь мне файл phrases txt с текстом для обучения\n'
        'после обучения выбери сколько строк сгенерировать\n'
        'бот будет генерировать текст без цензуры с маленькими буквами',
        reply_markup=reply_markup
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        document = update.message.document
        if not document.file_name.lower().endswith('.txt'):
            await update.message.reply_text('отправь txt файл')
            return
        
        file = await context.bot.get_file(document.file_id)
        content = await file.download_as_bytearray()
        text = content.decode('utf-8')
        
        text_generator.add_phrases(text)
        await update.message.reply_text(
            f'добавлено {len(text_generator.phrases)} фраз\n'
            f'уникальных слов: {len(text_generator.word_dict)}\n'
            f'модель обучена: {"да" if text_generator.is_trained else "нет"}'
        )
        
    except Exception as e:
        await update.message.reply_text(f'ошибка обработки файла: {str(e)}')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    if any(x in text for x in ['10', '50', '100', '200', '500']):
        try:
            num_lines = int(''.join(filter(str.isdigit, text)))
            
            if num_lines > 500:
                num_lines = 500
            elif num_lines < 10:
                num_lines = 10
                
            await update.message.reply_text(f'генерирую {num_lines} строк...')
            
            generated_text = text_generator.generate_text(num_lines)
            
            # Сохраняем в файл
            with open('gen.txt', 'w', encoding='utf-8') as f:
                f.write(generated_text)
            
            # Отправляем файл
            with open('gen.txt', 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    filename='gen.txt',
                    caption=f'сгенерировано {num_lines} строк\nбез цензуры маленькие буквы'
                )
                
        except Exception as e:
            await update.message.reply_text(f'ошибка генерации: {str(e)}')
    else:
        await update.message.reply_text('выбери количество строк для генерации')

def main():
    """Запуск бота"""
    application = Application.builder().token("8185551392:AAEmWYNcRGVzN0EEEPHicyMjzpWiWWOGgJSs").build()
    
    # Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Бот запускается...")
    application.run_polling()

if __name__ == '__main__':
    main()