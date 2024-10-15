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
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import seaborn as sns
from wordcloud import WordCloud
import nltk

# Membaca kamus sentimen dari file TSV
positive_dict = pd.read_csv('positive-after.tsv', delimiter='\t')
print(len(positive_dict))
negaive_dict = pd.read_csv('negative-after.tsv', delimiter='\t')
print(len(negaive_dict))

# Menggabungkan kedua DataFrame menjadi satu
sentiment_dict = pd.concat([positive_dict, negaive_dict])

# Membuat kamus dari kamus sentimen
sentiment_scores = dict(zip(sentiment_dict['word'], sentiment_dict['weight']))

class DataFrameTable(QDialog):
    def __init__(self, df):
        super().__init__()
        self.setWindowTitle('DataFrame Table')
        
        # Buat QTableWidget untuk menampilkan DataFrame dalam bentuk tabel
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(len(df.columns))
        self.table_widget.setRowCount(len(df))
        self.table_widget.setHorizontalHeaderLabels(df.columns)
        
        # Isi tabel dengan data dari DataFrame
        for i in range(len(df)):
            for j in range(len(df.columns)):
                item = QTableWidgetItem(str(df.iloc[i, j]))
                self.table_widget.setItem(i, j, item)
        
        # Atur layout
        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)
        self.setLayout(layout)

        self.resize(1080, 720)

class InformationWindow(QWidget):
    def __init__(self):
        super().__init__()
        loadUi('infoData.ui', self)  # Memuat desain UI dari file .ui
        self.page = 1  # Atur halaman awal
        self.stackedData.setCurrentIndex(0)
        self.update_page_buttons()
        self.setWindowTitle('Information')  # Set judul jendela
        self.btn_sblm.clicked.connect(self.previous_page)  # Tambahkan koneksi untuk tombol sebelumnya
        self.btn_slnjt.clicked.connect(self.next_page)
        self.crawl_data.setOpenExternalLinks(True)
        #<a href="https://www.youtube.com/watch?v=BxryBUtUqEk">Klik di sini untuk Crawling</a>
    
    def update_page_buttons(self):
        # Fungsi untuk memperbarui status tombol halaman
        self.btn_sblm.setEnabled(self.page > 1)  # Nonaktifkan tombol sebelumnya jika halaman = 1
        self.btn_slnjt.setEnabled(self.page < 3) 

    def previous_page(self):
        # Fungsi untuk menampilkan halaman sebelumnya
        if self.page > 1:
            self.page -= 1
            self.stackedData.setCurrentIndex(self.page - 1)
            self.update_page_buttons()  # Perbarui status tombol setelah perubahan halaman

    def next_page(self):
        # Fungsi untuk menampilkan halaman selanjutnya
        if self.page <= 3:
            self.page += 1
            self.stackedData.setCurrentIndex(self.page - 1)
            self.update_page_buttons()  # Perbarui status tombol setelah perubahan halaman

class testUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(testUI, self).__init__()
        loadUi('test.ui', self)
        self.pageTeks.clicked.connect(self.gantiForm1)
        self.pageData.clicked.connect(self.gantiForm2)
        self.pagePenelitian.clicked.connect(self.gantiForm3)
        self.btn_hasil.clicked.connect(self.displayInputTeks)
        self.btn_inp.clicked.connect(self.inputData)
        self.btn_akurasi.clicked.connect(self.akurasi)
        
        # Membuat widget untuk menampilkan plot
        self.figure = plt.figure(figsize=(4.41, 3.71), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.plot_widget.setLayout(layout)
        self.figure_wordcloud = plt.figure(figsize=(4.61, 3.71), dpi=100)
        self.canvas_wordcloud = FigureCanvas(self.figure_wordcloud)
        layout_wordcloud = QVBoxLayout()
        layout_wordcloud.addWidget(self.canvas_wordcloud)
        self.wordcloud_widget.setLayout(layout_wordcloud)

        self.figure2 = plt.figure(figsize=(5, 4), dpi=100)
        self.canvas2 = FigureCanvas(self.figure2)
        layout2 = QVBoxLayout()
        layout2.addWidget(self.canvas2)
        # self.hasil_diagram.setLayout(layout2)
        # self.figure_wordcloud2 = plt.figure(figsize=(4.61, 3.71), dpi=100)
        # self.canvas_wordcloud2 = FigureCanvas(self.figure_wordcloud2)
        # layout_wordcloud2 = QVBoxLayout()
        # layout_wordcloud2.addWidget(self.canvas_wordcloud2)
        # self.hasil_wc.setLayout(layout_wordcloud2)

        layout = QVBoxLayout()
        layout_wordcloud = QVBoxLayout()
        self.figure_sentiment = plt.figure(figsize=(4.41, 3.71), dpi=100)
        self.canvas_sentiment = FigureCanvas(self.figure_sentiment)
        layout.addWidget(self.canvas_sentiment)
        
        # Widget for evaluation metric plot
        self.figure_evaluation = plt.figure(figsize=(4.61, 3.71), dpi=100)
        self.canvas_evaluation = FigureCanvas(self.figure_evaluation)
        layout_wordcloud.addWidget(self.canvas_evaluation)
        

        
    
    def inputData(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Pilih File CSV", "", "CSV Files (*.csv);;All Files (*)", options=options
        )
        if file_name:
            progress = QProgressDialog("Memproses data...", None, 0, 0)
            progress.setWindowTitle('Loading')
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            QtWidgets.QApplication.processEvents()
            df = pd.read_csv(file_name)  # Tentukan delimiter sebagai titik koma
            df = df.head(20)
            dialog = DataFrameTable(df)  # Buat jendela baru dan tampilkan data DataFrame dalam tabel
            dialog.exec_()  # Tampilkan jendela baru dengan tabel
            progress.close()
            
            progress = QProgressDialog("Memproses data...", None, 0, 0)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            QtWidgets.QApplication.processEvents()
            df = df[['full_text']]
            dialog = DataFrameTable(df)  # Buat jendela baru dan tampilkan data DataFrame dalam tabel
            dialog.exec_()  # Tampilkan jendela baru dengan tabel
            progress.close()

        progress = QProgressDialog("Memproses data...", None, 0, 0)
        progress.setWindowTitle('Loading')
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        QtWidgets.QApplication.processEvents()
        clean = df['full_text'].apply(self.clean_text).values
        df['cleaned-texts'] = clean
        stemmed_texts = [self.stem_text(full_text) for full_text in clean]
        df['stemmed-texts'] = stemmed_texts
        tokenize_texts = [self.tokenizing(stemmed_texts) for stemmed_texts in stemmed_texts]
        df['tokenizing-texts'] = tokenize_texts
        df['pre-process'] = stemmed_texts
        df.to_csv('sentimen-pub-pre-process.csv', index=False)
        dialog = DataFrameTable(df)  # Buat jendela baru dan tampilkan data DataFrame dalam tabel
        dialog.exec_()  # Tampilkan jendela baru dengan tabel
        progress.close()
        
        progress = QProgressDialog("Memproses data...", None, 0, 0)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        QtWidgets.QApplication.processEvents()
        # Menambahkan kolom sentimen ke data
        df['sentiment_score'] = df['pre-process'].apply(self.calculate_sentiment)    
        df['sentiment'] = df['sentiment_score'].apply(self.interpret_sentiment)
        dialog = DataFrameTable(df)  # Buat jendela baru dan tampilkan data DataFrame dalam tabel
        dialog.exec_()  # Tampilkan jendela baru dengan tabel
        # Setelah dataset selesai diproses
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText("Dataset telah selesai diproses. Apakah Anda ingin menyimpannya?")
        msgBox.setWindowTitle("Konfirmasi Penyimpanan")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.Yes)
        response = msgBox.exec()

        if response == QMessageBox.Yes:
            # Meminta lokasi penyimpanan dari pengguna
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Simpan Dataset", "C:/Users/<username>/Downloads/", "CSV Files (*.csv)", options=options
            )

            if file_name:
                # Menyimpan dataset ke lokasi yang dipilih
                df.to_csv(file_name, index=False)
                print(f"Dataset disimpan di: {file_name}")
            else:
                print("Penyimpanan dibatalkan.")
        else:
            print("Dataset tidak disimpan.")
        
        # Menghitung frekuensi masing-masing label
        label_counts = df['sentiment'].value_counts()

        # Menghitung total jumlah data
        total_data = len(df)

        # Menghitung persentase positif, negatif, dan netral
        percentage_positive = (label_counts.get('Positif', 0) / total_data) * 100
        percentage_negative = (label_counts.get('Negatif', 0) / total_data) * 100
        percentage_neutral = (label_counts.get('Netral', 0) / total_data) * 100

        # Menampilkan hasil
        
        pos = f"Persentase Sentimen Positive: {percentage_positive:.2f}% \n \n"
        neg = f"Persentase Sentimen Negative: {percentage_negative:.2f}% \n \n"
        net = f"Persentase Sentimen Neutral: {percentage_neutral:.2f}% \n \n"
        hasil = pos + neg + net
        self.hasil_analisaData.setText(hasil)

        sentiment_labels = ['Positive', 'Negative', 'Neutral']
        percentages = [percentage_positive, percentage_negative, percentage_neutral]  # Misalnya, ubah nilai persentase sesuai data Anda

        self.figure.clear()  # Hapus plot sebelumnya (jika ada)
        ax = self.figure.add_subplot(111)
        ax.bar(sentiment_labels, percentages, color=['green', 'blue', 'red'])
        ax.set_title('Persentase Sentimen')
        ax.set_xlabel('Sentimen')
        ax.set_ylabel('Persentase')
        self.canvas.draw()

# Visualisasi WordCloud
        all_text = ' '.join(df['pre-process'])
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_text)
        self.figure_wordcloud.clear()  # Hapus plot WordCloud sebelumnya (jika ada)
        ax_wordcloud = self.figure_wordcloud.add_subplot(111)
        ax_wordcloud.imshow(wordcloud, interpolation='bilinear')
        ax_wordcloud.axis('off')
        ax_wordcloud.set_title('WordCloud dari Hasil Analisis Sentimen')
        self.canvas_wordcloud.draw()
    
    def save_plot(self):
        # Meminta lokasi penyimpanan dari pengguna
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Simpan Gambar Plot", "", "PNG Files (*.png);;JPEG Files (*.jpg)", options=options
        )

        if file_path:
            # Menyimpan gambar plot sesuai format yang dipilih oleh pengguna
            self.figure.savefig(file_path)
            print(f"Gambar plot disimpan di: {file_path}")
        else:
            print("Penyimpanan gambar plot dibatalkan.")

    def gantiForm1(self):
        self.Stacked1.setCurrentIndex(0)
            
    def gantiForm2(self):
        self.Stacked1.setCurrentIndex(1)
        self.info_window = InformationWindow()
        self.info_window.show()

    def gantiForm3(self):
        self.Stacked1.setCurrentIndex(2)
    
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
    
    def tokenizing(self, text):
        # Membuat token array
        tokens_word = text.split(" ")
        return tokens_word
            
    def calculate_sentiment(self, text):
        words = text.split(" ")
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
    
    def calculate_sentiment_text(self, text):
        words = text
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
            # self.kamusList.setText(f'================================================================= \n\n==Kamus kata== \n\n{info_text}')  # Set teks info ke dalam label hasil
            self.scrollkamus.setText(f'============================================================================================================= \n\n==Kamus kata== \n\n{info_text}')
        else:
            self.scrollkamus.setText("Tidak ada kata dengan bobot sentimen yang ditemukan")  # Teks alternatif jika tidak ada info

    
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
        teks = self.inputText.toPlainText()

        # Clean text
        praproses = self.clean_text(teks)
        praproses_clean = f'Hasil Clean teks : {praproses}\n \n'

        # Stem text
        praproses = self.stem_text(praproses)
        praproses_stem = f'Hasil Stemming teks : {praproses}\n \n'
        
        # token text
        praproses = self.tokenizing(praproses)
        praproses_token = f'Hasil Tokenizing teks : {praproses}\n \n'

        # Calculate sentiment
        praproses = self.calculate_sentiment_text(praproses)
        praproses_sentiment = f'Skor sentimen akhir : {praproses}\n \n'

        # Interpret sentiment
        praproses = self.interpret_sentiment(praproses)
        buzzer = self.buzzer_sentiment(praproses)
        praproses_interpret = f'Hasil analisa adalah: {praproses} atau {buzzer}'

        # Combine all results
        hasil_analisis = praproses_clean + praproses_stem + praproses_token + praproses_sentiment + praproses_interpret

        # Set text in hasil widget
        self.hasil_analisis.setText(hasil_analisis)

    def inputDatasetMentah(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Input data mentah", "", "CSV Files (*.csv);;All Files (*)", options=options
        )
        if file_name:
            progress = QProgressDialog("Memproses data...", None, 0, 0)
            progress.setWindowTitle('Loading')
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            QtWidgets.QApplication.processEvents()
            df = pd.read_csv(file_name)  # Tentukan delimiter sebagai titik koma
            # df = df.head(20)
            dialog = DataFrameTable(df)  # Buat jendela baru dan tampilkan data DataFrame dalam tabel
            dialog.exec_()  # Tampilkan jendela baru dengan tabel
            progress.close()
            
            progress = QProgressDialog("Memproses data...", None, 0, 0)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            QtWidgets.QApplication.processEvents()
            df = df[['full_text']]
            dialog = DataFrameTable(df)  # Buat jendela baru dan tampilkan data DataFrame dalam tabel
            dialog.exec_()  # Tampilkan jendela baru dengan tabel
            progress.close()
        
        progress = QProgressDialog("Memproses data...", None, 0, 0)
        progress.setWindowTitle('Loading')
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        QtWidgets.QApplication.processEvents()
        clean = df['full_text'].apply(self.clean_text).values
        df['cleaned-texts'] = clean
        stemmed_texts = [self.stem_text(full_text) for full_text in clean]
        df['stemmed-texts'] = stemmed_texts
        df['pre-process'] = stemmed_texts
        df.to_csv('sentimen-pub-pre-process.csv', index=False)
        dialog = DataFrameTable(df)  # Buat jendela baru dan tampilkan data DataFrame dalam tabel
        dialog.exec_()  # Tampilkan jendela baru dengan tabel
        progress.close()
        
        progress = QProgressDialog("Memproses data...", None, 0, 0)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        QtWidgets.QApplication.processEvents()
        # Menambahkan kolom sentimen ke data
        df['sentiment_score'] = df['pre-process'].apply(self.calculate_sentiment)    
        df['sentiment'] = df['sentiment_score'].apply(self.interpret_sentiment)
        dialog = DataFrameTable(df)  # Buat jendela baru dan tampilkan data DataFrame dalam tabel
        dialog.exec_()  # Tampilkan jendela baru dengan tabel
        progress.close()

        # Menghitung frekuensi masing-masing label
        label_counts = df['sentiment'].value_counts()

        # Menghitung total jumlah data
        total_data = len(df)

        # Menghitung persentase positif, negatif, dan netral
        percentage_positive = (label_counts.get('Positif', 0) / total_data) * 100
        percentage_negative = (label_counts.get('Negatif', 0) / total_data) * 100
        percentage_neutral = (label_counts.get('Netral', 0) / total_data) * 100

        # Menampilkan hasil
        
        pos = f"Persentase Sentimen Positive: {percentage_positive:.2f}% \n \n"
        neg = f"Persentase Sentimen Negative: {percentage_negative:.2f}% \n \n"
        net = f"Persentase Sentimen Neutral: {percentage_neutral:.2f}% \n \n"
        hasil = pos + neg + net
        self.hasil_persen.setText(hasil)

#         sentiment_labels = ['Positive', 'Negative', 'Neutral']
#         percentages = [percentage_positive, percentage_negative, percentage_neutral]  # Misalnya, ubah nilai persentase sesuai data Anda

#         self.figure2.clear()  # Hapus plot sebelumnya (jika ada)
#         ax = self.figure2.add_subplot(111)
#         ax.bar(sentiment_labels, percentages, color=['green', 'blue', 'red'])
#         ax.set_title('Persentase Sentimen')
#         ax.set_xlabel('Sentimen')
#         ax.set_ylabel('Persentase')
#         self.canvas2.draw()

        

# # Visualisasi WordCloud
        all_text = ' '.join(df['pre-process'])
        wordcloud2 = WordCloud(width=800, height=400, background_color='white').generate(all_text)
        plt.figure(figsize=(10, 8))
        plt.imshow(wordcloud2, interpolation='bilinear')
        plt.axis('off')
        plt.title('WordCloud dari Hasil Analisis Sentimen')
        plt.show()
     
        return df
    
    def inputDatasetAktual(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Input data aktual", "", "CSV Files (*.csv);;All Files (*)", options=options
        )
        if file_name:
            progress = QProgressDialog("Memproses data...", None, 0, 0)
            progress.setWindowTitle('Loading')
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            QtWidgets.QApplication.processEvents()
            df = pd.read_csv(file_name)  # Tentukan delimiter sebagai titik koma
            # df = df.head(20)
            dialog = DataFrameTable(df)  # Buat jendela baru dan tampilkan data DataFrame dalam tabel
            dialog.exec_()  # Tampilkan jendela baru dengan tabel
            progress.close()
            

        return df
    
    def akurasi(self):
        import matplotlib.pyplot as plts
        data1 = self.inputDatasetMentah()
        data2 = self.inputDatasetAktual()
        print(data1.head())
        print(data2.head())

        # Mendefinisikan variabel untuk menyimpan hasil perbandingan
        AA = AB = AC = BA = BB = BC = CA = CB = CC = 0

        # Membandingkan nilai sentimen pada baris yang sama di kedua dataset
        for index, row1 in data1.iterrows():
            sentiment1 = row1['sentiment']
            sentiment2 = data2.iloc[index]['sentiment']
            if sentiment1 == 'Positif':
                if sentiment2 == 'Positif':
                    AA += 1
                elif sentiment2 == 'Negatif':
                    AB += 1
                elif sentiment2 == 'Netral':
                    AC += 1
            elif sentiment1 == 'Negatif':
                if sentiment2 == 'Positif':
                    BA += 1
                elif sentiment2 == 'Negatif':
                    BB += 1
                elif sentiment2 == 'Netral':
                    BC += 1
            elif sentiment1 == 'Netral':
                if sentiment2 == 'Positif':
                    CA += 1
                elif sentiment2 == 'Negatif':
                    CB += 1
                elif sentiment2 == 'Netral':
                    CC += 1

        print("Kelas AA:", AA)
        print("Kelas AB:", AB)
        print("Kelas AC:", AC)
        print("Kelas BA:", BA)
        print("Kelas BB:", BB)
        print("Kelas BC:", BC)
        print("Kelas CA:", CA)
        print("Kelas CB:", CB)
        print("Kelas CC:", CC)

        totalabc = AA + BB + CC
        print(totalabc)
        total = len(data1)
        print(total)

        try:
            Accuracy = (AA + BB + CC) / total
            accuracy_percentage = Accuracy * 100
            Accuracy_text = f'Accuracy : {Accuracy} == {accuracy_percentage:.2f}% \n'
            print(Accuracy_text)
        except ZeroDivisionError:
            Accuracy_text = ("Error: Pembagian dengan nol tidak dapat dilakukan.\n")

        try:
            Precision = ((AA / (AA + AB + AC)) + (BB / (BB + BA + BC)) + (CC / (CC + CA + CB))) / 3
            Precision_percent = Precision * 100
            Precision_text = f'Precision : {Precision} == {Precision_percent:.2f}% \n'
            print(Precision_text)
        except:
            Precision_text = ("Error: Pembagian dengan nol tidak dapat dilakukan. \n")

        try:
            Recall = ((AA / (AA + BA + CA)) + BB / (BB + AB + CB) + (CC / (CC + AC + BC))) / 3
            Recall_percent = Recall * 100
            recall_text = f'Recall :  {Recall} == {Recall_percent:.2f}% \n'
            print(recall_text)
        except:
            recall_text = ("Recall Error: Pembagian dengan nol tidak dapat dilakukan. \n")

        try:
            F1score = (2 * Recall * Precision) / (Recall + Precision)
            F1score_percent = F1score * 100
            F1score_text = f'F1-Score {F1score} == {F1score_percent:.2f}% \n'
            print(F1score_text)
        except:
            F1score_text = ("F1-score Error: Pembagian dengan nol tidak dapat dilakukan. \n")

        self.hasilAkurasi.setText('\n'.join([Accuracy_text, recall_text, Precision_text, F1score_text]))

        # Data sentimen sebelum dan sesudah penambahan kata baru
        sentimen_sebelum = [13.11, 82.91, 3.98]
        sentimen_sesudah = [63.30, 32.62, 4.08]
        labels_sentimen = ['Positif', 'Negatif', 'Netral']

        # Data metrik evaluasi sebelum dan sesudah penambahan kata baru
        metrik_sebelum = [42.03, 37.78, 40.63, 39.15]
        metrik_sesudah = [89.02, 72.17, 78.07, 75.00]
        labels_metrik = ['Akurasi', 'Presisi', 'Recall', 'F1-score']

        # Mengatur lokasi label sumbu x
        x_sentimen = np.arange(len(labels_sentimen))
        x_metrik = np.arange(len(labels_metrik))

        width = 0.35  # Lebar bar

        fig, ax = plts.subplots(1, 2, figsize=(14, 14))

        # Plot untuk distribusi sentimen
        rects1 = ax[0].bar(x_sentimen - width / 2, sentimen_sebelum, width, label='Sebelum')
        rects2 = ax[0].bar(x_sentimen + width / 2, sentimen_sesudah, width, label='Sesudah')

        # Menambahkan label, judul, dan kustomisasi sumbu x
        ax[0].set_ylabel('Persentase (%)')
        ax[0].set_title('Distribusi Sentimen Sebelum dan Sesudah Penambahan Kata Baru')
        ax[0].set_xticks(x_sentimen)
        ax[0].set_xticklabels(labels_sentimen)
        ax[0].legend()

        # Plot untuk metrik evaluasi
        rects3 = ax[1].bar(x_metrik - width / 2, metrik_sebelum, width, label='Sebelum')
        rects4 = ax[1].bar(x_metrik + width / 2, metrik_sesudah, width, label='Sesudah')

        # Menambahkan label, judul, dan kustomisasi sumbu x
        ax[1].set_ylabel('Nilai (%)')
        ax[1].set_title('Metrik Evaluasi Sebelum dan Sesudah Penambahan Kata Baru')
        ax[1].set_xticks(x_metrik)
        ax[1].set_xticklabels(labels_metrik)
        ax[1].legend()

        # Fungsi untuk menambahkan label di atas bar
        def autolabel(rects, ax):
            """Menambahkan label teks di atas setiap bar dalam *rects*, menampilkan tinggi bar."""
            for rect in rects:
                height = rect.get_height()
                ax.annotate(f'{height:.2f}',
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # Offset vertikal 3 poin
                            textcoords="offset points",
                            ha='center', va='bottom')

        # Menerapkan fungsi ke kedua set bar
        autolabel(rects1, ax[0])
        autolabel(rects2, ax[0])
        autolabel(rects3, ax[1])
        autolabel(rects4, ax[1])

        fig.tight_layout()

        plts.show()


app = QtWidgets.QApplication(sys.argv)
window = testUI()
window.setWindowTitle('Aplikasi Prediksi')
window.show()
sys.exit(app.exec_())