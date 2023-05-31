import re
import string
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory, Stemmer, ArrayDictionary
from nltk.tokenize import word_tokenize

class TextProcessing:
    def __init__(self):
        self.stopword = StopWordRemoverFactory().create_stop_word_remover()  # membuat stopword
        # membuat stemmer
        with open('../resource/city-word.txt', 'r') as f:
            added_stem = word_tokenize(f.read())
        stem_word = StemmerFactory().get_words()
        unused_stem = ["pemalang"]
        self.stemmer = Stemmer(ArrayDictionary(stem_word + added_stem + unused_stem))

    # preprocessing
    def preprocessing(self, row):
        title = row['title'].lower()
        text = row['text'].lower()
        try:
            if re.match('^' + title, text):
                full_text = text
            else:
                full_text = title + ' ' + text
        except:
            full_text = title + ' ' + text
        finally:
            # hapus keyword tidak penting
            full_text = re.sub("- dinas komunikasi dan informatika provinsi jawa timur|halaman all|– kantor wilayah kementerian agama provinsi jawa tengah|kabar1news|– p2p kemenkes ri|okezone news", "", full_text) # hapus sumber berita pada judul
            full_text = re.sub("baca\s?:.+\n|baca juga\s?:?\n\n?.+\n|baca juga.+\n", "", full_text) # hapus keyword "baca juga"
            full_text = re.sub("reporter\s?:.+\n|sumber\s?:.+\n|pewarta\s?:.+\n|editor\s?:.+\n|foto\s?:.+\n|copyright|diunggah pada\s?:.+\n", "", full_text) # hapus credit
            full_text = re.sub("advertisement.*\n", "", full_text) # hapus keyword "advertisement"
            full_text = full_text.replace("\nloading...\n", "") # hapus keyword "loading..."
            full_text = re.sub(r'(\w|\.)+(\.com|\.id|\.co|\.net)\s?','',full_text) # hapus link
            # hapus tanda baca
            for char in string.punctuation:
                full_text = full_text.replace(char, " ")
            full_text = full_text.replace("\n", " ") # hapus "\n"
            full_text = full_text.strip() # menghilangkan karakter kosong di awal dan akhir
            full_text = self.stopword.remove(full_text) # menghilangkan stop word dengan sastrawi
            full_text = self.stemmer.stem(full_text) # stemming kata menggunakan sastrawi
            token = word_tokenize(full_text) # tokenizing
            token = list(filter(lambda n: len(n) > 1 and not n.isdigit(), token)) # filter angka dan kata yg hanya mengandung 1 karakter
            return " ".join(token)