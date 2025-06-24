import numpy as np
import pickle
import re
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split

# تمیز کردن متن ورودی
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s\u0600-\u06FF]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# تولید داده‌های احساسی
happy_texts = [
    "خیلی شادم", "زندگی قشنگه", "حس خوبی دارم", "امروز فوق‌العاده بود", "همه چی عالیه",
    "پر از انرژی‌ام", "از لحظه لحظه زندگی لذت می‌برم", "امید تو دلمه", "خوشبختم", "روزم بی‌نظیر بود"
]

sad_texts = [
    "حالم گرفته‌ست", "احساس پوچی می‌کنم", "دلگیرم", "همه چی بهم ریخته", "امروز روز بدی بود",
    "بی‌انگیزه‌ام", "نمی‌دونم چرا ناراحتم", "حس تنهایی دارم", "همه چی خاکستریه", "خستم"
]

# تولید 600 داده (300 مثبت، 300 منفی)
happy_data = [preprocess_text(t + f" {i}") for i in range(30) for t in happy_texts][:300]
sad_data = [preprocess_text(t + f" {i}") for i in range(30) for t in sad_texts][:300]

all_texts = happy_data + sad_data
labels = [1]*300 + [0]*300

# توکن‌سازی داده‌ها
word_tokenizer = Tokenizer(num_words=2500, oov_token="<UNK>")
word_tokenizer.fit_on_texts(all_texts)
text_sequences = word_tokenizer.texts_to_sequences(all_texts)
padded_texts = pad_sequences(text_sequences, padding='post', maxlen=20)

# ذخیره توکنایزر
with open("word_tokenizer.pkl", "wb") as f:
    pickle.dump(word_tokenizer, f, protocol=pickle.HIGHEST_PROTOCOL)

# تقسیم داده‌ها به آموزشی و آزمایشی
X_train, X_test, y_train, y_test = train_test_split(padded_texts, labels, test_size=0.25, random_state=101)

# ساخت مدل
emotion_model = Sequential([
    Embedding(input_dim=2500, output_dim=80, input_length=20),
    Dropout(0.4),
    LSTM(80, return_sequences=False),
    Dense(1, activation='sigmoid')
])

# کامپایل و آموزش مدل
emotion_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
emotion_model.fit(X_train, np.array(y_train), epochs=25, batch_size=16, validation_split=0.15, verbose=2)

# ذخیره مدل
emotion_model.save("emotion_analyzer.keras")

# تولید پاسخ‌های احساسی
def create_response(mood, confidence):
    if mood == "خوشحال 😊":
        responses = [
            "وای چه حس خوبی! 😄 چی تورو اینقدر شاد کرده؟",
            "عالیه! دوست داری از این حس قشنگ بیشتر بگی؟",
            "این شادی مسریه! 😊 چیزی باعثش شده؟"
        ]
    else:
        responses = [
            "اووه، انگار حالت خوب نیست 😔 چیزی شده؟ بگو شاید کمک کنم.",
            "ناراحت نباش، من اینجام برات 🥺 چی تو دلته؟",
            "اگه بخوای می‌تونی از چیزی که اذیتت می‌کنه بگی..."
        ]
    return f"{np.random.choice(responses)} (اطمینان: {confidence:.2%})"

# چت با کاربر
def interact_with_user():
    print("👋 سلام! من یه ربات تحلیل احساساتم!")
    print("هر وقت خواستی تموم کنی، بنویس 'خروج'")

    with open("word_tokenizer.pkl", "rb") as f:
        tokenizer = pickle.load(f)
    model = load_model("emotion_analyzer.keras")

    user_inputs = []
    mood_scores = []

    while True:
        user_text = input("💬 شما: ").strip()
        if user_text.lower() in ["خروج", "exit", "quit"]:
            break

        user_inputs.append(user_text)
        cleaned_text = preprocess_text(user_text)
        seq = tokenizer.texts_to_sequences([cleaned_text])
        padded_seq = pad_sequences(seq, padding='post', maxlen=20)
        score = model.predict(padded_seq)[0][0]
        mood = "خوشحال 😊" if score > 0.5 else "ناراحت 😞"
        mood_scores.append(score)

        print(f"😎 تحلیل: {mood}")
        print(f"🤖 پاسخ: {create_response(mood, score)}")

    if mood_scores:
        avg_mood = np.mean(mood_scores)
        overall_mood = "خوشحال 😊" if avg_mood > 0.5 else "ناراحت 😞"
        print("\n📈 تحلیل نهایی مکالمه:")
        print(f"🎭 حس کلی شما: {overall_mood} (میانگین امتیاز: {avg_mood:.2%})")
    else:
        print("هیچ متنی وارد نشد! 😐")

# اجرای برنامه
if __name__ == "__main__":
    interact_with_user()