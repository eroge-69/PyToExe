import tkinter as tk

# Create a window
window = tk.Tk()
window.title("Text Display")

# Create a label with some text
label = tk.Label(window, text="Hi!", font=("Arial", 16))
label = tk.Label(window, text="my name is AI Bot! I am somewhat artificial intelligence. I will display some", font=("Arial", 16))
label.pack(pady=20)

import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.datasets import imdb
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Load the IMDB dataset (binary sentiment classification)
vocab_size = 10000  # Only keep top 10k words
(x_train, y_train), (x_test, y_test) = imdb.load_data(num_words=vocab_size)

# Pad sequences to ensure equal length
max_len = 200
x_train = pad_sequences(x_train, maxlen=max_len)
x_test = pad_sequences(x_test, m_

# Run the GUI loop
window.mainloop()


