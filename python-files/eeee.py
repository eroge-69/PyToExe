import nltk
import random
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download NLTK data (only first time)
nltk.download("punkt")
nltk.download("wordnet")

# Sample corpus for chatbot (you can expand this)
corpus = """
Hello! How can I help you?
I am a chatbot created using NLP.
I can answer questions about programming, Python, and AI.
Python is a popular programming language.
Artificial Intelligence is the simulation of human intelligence by machines.
Machine learning is a subset of AI.
Goodbye! Have a great day.
"""

# Preprocessing
sent_tokens = nltk.sent_tokenize(corpus)  # Break into sentences
lemmer = nltk.stem.WordNetLemmatizer()


def LemTokens(tokens):
    return [lemmer.lemmatize(token.lower()) for token in tokens if token not in string.punctuation]


def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text))


# Response function
def chatbot_response(user_input):
    sent_tokens.append(user_input)  # Add user input to corpus
    vectorizer = TfidfVectorizer(tokenizer=LemNormalize, stop_words="english")
    tfidf = vectorizer.fit_transform(sent_tokens)
    similarity = cosine_similarity(tfidf[-1], tfidf)
    idx = similarity.argsort()[0][-2]  # Most similar response
    flat = similarity.flatten()
    flat.sort()
    score = flat[-2]

    sent_tokens.pop(-1)  # Remove user input from corpus

    if score == 0:
        return "I'm sorry, I don't understand that."
    else:
        return sent_tokens[idx]


# Main loop
print("Chatbot: Hi! I’m your NLP chatbot. Type 'quit' to exit.")
while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        print("Chatbot: Goodbye!")
        break
    print("Chatbot:", chatbot_response(user_input))
