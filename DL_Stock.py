# -*- coding: utf-8 -*-
"""stockproject.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OHjS8ABU_Xvt5e5siaC1dOcwfaprspWO
"""

from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
import numpy as np
import re
import nltk.corpus
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from keras.utils import pad_sequences
from keras.preprocessing.text import Tokenizer
from keras.models import Sequential
from keras.layers import Dense, Embedding,Flatten,LSTM,Bidirectional
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from imblearn.over_sampling import RandomOverSampler
import seaborn as sns
import tensorflow as tf
import joblib

data = pd.read_excel('/content/drive/MyDrive/Colab Notebooks/5_stock_data.xlsx')
data.head()

duplicated_values = data.duplicated().sum()
print( "Data Duplicated: ", duplicated_values)

missing_values = data.isna().sum()
print("Missing Values:")
print(missing_values)

data = data.drop_duplicates()
data

format = r"(@\[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?"
text = data['Text'].astype(str)

cleaned_texts = text.str.replace(format, "", regex=True)

print(cleaned_texts)

stop = stopwords.words('english')
lemmatizer = WordNetLemmatizer()

texts = cleaned_texts.values

def remove_stopwords(text):
    words = word_tokenize(text)
    cleaned_words = [word for word in words if word.lower() not in stop]
    lemmatized_words = [lemmatizer.lemmatize(word) for word in cleaned_words]
    return " ".join(lemmatized_words)

cleaned_stopw = [remove_stopwords(text) for text in texts]
print(cleaned_stopw)

def convert_labels_to_binary(label):
    if label == -1:
        return 0
    elif label == 1:
        return 1
labels = data['Sentiment']
labels = [convert_labels_to_binary(label) for label in labels]

print(cleaned_stopw)
print(labels)

tokenizer = Tokenizer()
tokenizer.fit_on_texts(cleaned_stopw)
tts = tokenizer.texts_to_sequences(cleaned_stopw)
max_length = 50
print("max sentense's length = " , max_length)
X = pad_sequences(tts, maxlen=max_length, padding="post")
print("Sequence Padding at maxlen words, post padding:\n", X)
vocab_size = len(tokenizer.word_index) +1
print("vocab size : ",vocab_size)

oversampler = RandomOverSampler(sampling_strategy='minority')
X_resampled, y_resampled = oversampler.fit_resample(X, labels)
y = np.array(y_resampled )
y

X_train,X_test,y_train,y_test = train_test_split(X_resampled,y,test_size = 0.20,random_state = 42)

model = Sequential()
model.add(Embedding(input_dim=vocab_size, output_dim=128, input_length=50) )
model.add(Flatten())
model.add(Dense(64, activation='relu'))
model.add(Dense(16, activation='relu'))
model.add(Dense(1, activation='sigmoid'))
model.summary()

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=[ 'accuracy' ])
model.fit(X_train, y_train, epochs=20, batch_size=32, validation_split=0.1)

loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test Loss: {loss* 100:.2f}")
print(f"Test Accuracy: {accuracy* 100:.2f}")

from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import matplotlib.pyplot as plt

y_pred = model.predict(X_test)
y_pred = y_pred > 0.5

confusion_mat = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(8, 6))
sns.heatmap(confusion_mat, annot=True, fmt='d', cmap='Blues', xticklabels=['0', '1'], yticklabels=['0', '1'])
plt.xlabel('True')
plt.ylabel('Predicted')
plt.title('Confusion Matrix')
plt.show()

print("Classification Report:")
print(classification_report(y_test, y_pred))

new_text = "Kickers on my watchlist XIDE TIT SOQ PNK CPW BPZ AJ  trade method 1 or method 2, see prev posts"
cleaned_new_text = re.sub(format, "", new_text)
cleaned_new_text = remove_stopwords(cleaned_new_text)

new_text_seq = tokenizer.texts_to_sequences([cleaned_new_text])
new_text_padded = pad_sequences(new_text_seq, maxlen=50, padding="post")

predictions = model.predict(new_text_padded)

predicted_label = 1 if predictions > 0.5 else 0
predicted_label

model.save('deeplearning.h5')
with open('dtokenizer.pkl', 'wb') as file:
    joblib.dump(tokenizer, file)

print(Embedding)