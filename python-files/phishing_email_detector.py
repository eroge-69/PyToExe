pip install auto-py-to-exe

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib
import nltk
import string
from nltk.corpus import stopwords

# Download stopwords
nltk.download('stopwords')

# Load dataset
df = pd.read_csv("emails.csv")
df = df.copy()

# Preprocessing function
def clean_text(text):
    text = str(text).lower()
    text = ''.join([char for char in text if char not in string.punctuation])
    words = text.split()
    words = [word for word in words if word not in stopwords.words('english')]
    return ' '.join(words)

# Apply preprocessing
df['clean_text'] = df['text'].apply(clean_text)

# Vectorize text
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['clean_text'])
y = df['label']

# Split into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = LogisticRegression()
model.fit(X_train, y_train)

# Evaluate the model
predictions = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, predictions))

# Save the model and vectorizer
joblib.dump(model, 'phish_model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')

# Prediction function
def predict_email(text):
    model = joblib.load('phish_model.pkl')
    vectorizer = joblib.load('vectorizer.pkl')
    cleaned = clean_text(text)
    vec = vectorizer.transform([cleaned])
    result = model.predict(vec)[0]
    return "Phishing" if result == 1 else "Safe"

# Example usage
if __name__ == "__main__":
    email = "Verify your PayPal account now"
    print("Prediction:", predict_email(email))
