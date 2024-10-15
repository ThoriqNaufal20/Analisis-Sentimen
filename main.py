import sys
import numpy as np
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import pandas as pd
import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import os
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import nltk

# Membaca kamus sentimen dari file TSV
positive_dict = pd.read_csv('positive.tsv', delimiter='\t')
print(len(positive_dict))
negaive_dict = pd.read_csv('negative.tsv', delimiter='\t')
print(len(negaive_dict))

# Menggabungkan kedua DataFrame menjadi satu
sentiment_dict = pd.concat([positive_dict, negaive_dict])

# Membuat kamus dari kamus sentimen
sentiment_scores = dict(zip(sentiment_dict['word'], sentiment_dict['weight']))

class PrediksiBuzzer(QtWidgets.QMainWindow):
    def __init__(self):
        super(PrediksiBuzzer, self).__init__()
        loadUi('deteksiBuzzer.ui', self)
        self.inputteks.setPlaceholderText("Enter some text here")
        self.ButtonHasil.clicked.connect(self.displayInputTeks)

    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r"\n+", " ", text)
        text = re.sub(r"[^A-Za-z0-9^,]", " ", text)
        text = re.sub(r",", " ", text)
        text = re.sub(r'#\w+', '', text)
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r"@", " ", text)
        text = re.sub(r"\.", " ", text)
        text = re.sub(r"\!", " ", text)
        text = re.sub(r"\/", " ", text)
        text = re.sub(r"\^", " ", text)
        text = re.sub(r"\+", " ", text)
        text = re.sub(r"\-", " ", text)
        text = re.sub(r"\=", " ", text)
        text = re.sub(r"'", " ", text)
        text = re.sub(r"(\d+)(k)", r"\g<1>000", text)
        text = re.sub(r":", " ", text)
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r'https', '', text)
        text = re.sub(r'#\w+', '', text)
        text = re.sub(r'@\w+', '', text)
        return text
    
    def stem_text(self, text):
        factory = StemmerFactory()
        stemmer = factory.create_stemmer()
        words = text.split()
        stemmed_words = [stemmer.stem(word) for word in words]
        stemmed_text = ' '.join(stemmed_words)
        return stemmed_text
    
    def calculate_sentiment(self, text):
        words = text.split()
        score = 0
        sentiment_info = []  # List untuk menyimpan info sentimen
        for word in words:
            if word in sentiment_scores:
                info = f"Kata: {word}, Bobot: {sentiment_scores[word]}"
                print(f"Kata: {word}, Bobot: {sentiment_scores[word]}")
                sentiment_info.append(info)  # Menambah info sentimen ke dalam list
                score += sentiment_scores[word]
        self.show_sentiment_info(sentiment_info)  # Menampilkan info sentimen di GUI
        return score

    def show_sentiment_info(self, info_list):
        if info_list:  # Pastikan info_list tidak kosong
            info_text = '\n'.join(info_list)  # Gabungkan semua info menjadi satu teks dengan baris baru
            self.hasilskor.setText(f'================================================================= \n\n==Kamus kata== \n\n{info_text}')  # Set teks info ke dalam label hasil
        else:
            self.hasilskor.setText("Tidak ada kata dengan bobot sentimen yang ditemukan")  # Teks alternatif jika tidak ada info

    
    def interpret_sentiment(self, score):
        if score > 0:
            return 'Positif'
        elif score < 0:
            return 'Negatif'
        else:
            return 'Netral'

    def buzzer_sentiment(self, sentiment):
        if sentiment == 'Positif':
            return 'Kalimat bukan termasuk buzzer'
        elif sentiment == 'Negatif':
            return 'Kalimat termasuk buzzer'
        else :
            return "Kalimat bersifat netral"

    def displayInputTeks(self):
        teks = self.inputteks.toPlainText()

        # Clean text
        praproses = self.clean_text(teks)
        praproses_clean = f'Hasil Clean teks : {praproses}\n \n'

        # Stem text
        praproses = self.stem_text(praproses)
        praproses_stem = f'Hasil Stemming teks : {praproses}\n \n'

        # Calculate sentiment
        praproses = self.calculate_sentiment(praproses)
        praproses_sentiment = f'Skor sentimen akhir : {praproses}\n \n'

        # Interpret sentiment
        praproses = self.interpret_sentiment(praproses)
        buzzer = self.buzzer_sentiment(praproses)
        praproses_interpret = f'Hasil analisa adalah: {praproses} atau {buzzer}'

        # Combine all results
        hasil_analisis = praproses_clean + praproses_stem + praproses_sentiment + praproses_interpret

        # Set text in hasil widget
        self.hasil.setText(hasil_analisis)


app = QtWidgets.QApplication(sys.argv)
window = PrediksiBuzzer()
window.setWindowTitle('Prediksi Buzzer Politik Menggunakan Lexicon-based')
window.show()
sys.exit(app.exec_())
