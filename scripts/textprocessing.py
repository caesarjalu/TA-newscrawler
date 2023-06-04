import re
import string
import pandas as pd
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory, Stemmer, ArrayDictionary
from nltk.tokenize import word_tokenize
from sklearn import feature_extraction


class TextProcessing:
    def __init__(self, logger):
        self.logger = logger
        self.stopword = StopWordRemoverFactory().create_stop_word_remover()  # membuat stopword
        # membuat stemmer
        with open('../resource/city-word.txt', 'r') as f:
            self.loc_tokenize = word_tokenize(f.read())
        stem_word = StemmerFactory().get_words()
        unused_stem = ["pemalang"]
        self.stemmer = Stemmer(ArrayDictionary(stem_word + self.loc_tokenize + unused_stem))

        self.special_loc = ['blitar', 'kediri', 'madiun', 'malang', 'mojokerto', 'pasuruan', 'probolinggo']

    def run(self, news_df):
        df = news_df.loc[:, ['title', 'text']]
        self.logger.debug("Preprocessing...")
        news_df['text_clean'] = df.apply(self.__preprocessing, axis=1)
        # news_df.to_csv('../newsdata/3-4_june_2023_preprocessed_news.csv', index=False)  # save to csv
        self.logger.debug("Counting words for location...")
        df_loc = self.__count_word_freq(news_df.loc[:, ['title', 'text_clean']])
        # df_loc.to_csv('../newsdata/3-4_june_2023_loc_text.csv', index=False)  # save to csv
        news_df['location'] = df_loc.apply(self.__add_location, axis=1)
        filtered_news_df = news_df.loc[news_df['location'].map(len) > 0]
        self.logger.info("Total News in East Java = " + str(len(filtered_news_df)) + " news:")
        for idx in filtered_news_df.index:
            self.logger.info(filtered_news_df['title'][idx] + ' - '
                             + ' '.join(loc for loc in filtered_news_df['location'][idx]))
        return filtered_news_df

    # preprocessing
    def __preprocessing(self, row):
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
            full_text = re.sub(
                "- dinas komunikasi dan informatika provinsi jawa timur|halaman all|– kantor wilayah kementerian agama provinsi jawa tengah|kabar1news|– p2p kemenkes ri|okezone news",
                "", full_text)  # hapus sumber berita pada judul
            full_text = re.sub("baca\s?:.+\n|baca juga\s?:?\n\n?.+\n|baca juga.+\n", "",
                               full_text)  # hapus keyword "baca juga"
            full_text = re.sub(
                "reporter\s?:.+\n|sumber\s?:.+\n|pewarta\s?:.+\n|editor\s?:.+\n|foto\s?:.+\n|copyright|diunggah pada\s?:.+\n",
                "", full_text)  # hapus credit
            full_text = re.sub("advertisement.*\n", "", full_text)  # hapus keyword "advertisement"
            full_text = full_text.replace("\nloading...\n", "")  # hapus keyword "loading..."
            full_text = re.sub(r'(\w|\.)+(\.com|\.id|\.co|\.net)\s?', '', full_text)  # hapus link
            # hapus tanda baca
            for char in string.punctuation:
                full_text = full_text.replace(char, " ")
            full_text = full_text.replace("\n", " ")  # hapus "\n"
            full_text = full_text.strip()  # menghilangkan karakter kosong di awal dan akhir
            full_text = self.stopword.remove(full_text)  # menghilangkan stop word dengan sastrawi
            full_text = self.stemmer.stem(full_text)  # stemming kata menggunakan sastrawi
            token = word_tokenize(full_text)  # tokenizing
            token = list(filter(lambda n: len(n) > 1 and not n.isdigit(),
                                token))  # filter angka dan kata yg hanya mengandung 1 karakter
            return " ".join(token)

    def __count_word_freq(self, df):
        added_loc = ['kota blitar', 'kota kediri', 'kota madiun', 'kota malang', 'kota mojokerto', 'kota pasuruan',
                     'kota probolinggo', 'kabupaten blitar', 'kabupaten kediri', 'kabupaten madiun',
                     'kabupaten malang', 'kabupaten mojokerto', 'kabupaten pasuruan', 'kabupaten probolinggo',
                     'kab blitar', 'kab kediri', 'kab madiun', 'kab malang', 'kab mojokerto', 'kab pasuruan',
                     'kab probolinggo']
        if "batu" in self.loc_tokenize:
            self.loc_tokenize[self.loc_tokenize.index("batu")] = "kota batu"
        locs = self.loc_tokenize + added_loc
        df_loc = self.__add_word_freq(df, 'text_clean', locs)
        return df_loc

    def __add_word_freq(self, data, column, lst_words, freq="count"):
        dtf = data.copy()

        ## query
        self.logger.info("found records:")
        self.logger.info([word + ": " + str(len(dtf[dtf[column].str.contains(word)])) for word in lst_words
                          if len(dtf[dtf[column].str.contains(word)]) > 0])

        ## vectorizer
        lst_grams = [len(word.split(" ")) for word in lst_words]
        if freq == "tfidf":
            vectorizer = feature_extraction.text.TfidfVectorizer(vocabulary=lst_words,
                                                                 ngram_range=(min(lst_grams), max(lst_grams)))
        else:
            vectorizer = feature_extraction.text.CountVectorizer(vocabulary=lst_words,
                                                                 ngram_range=(min(lst_grams), max(lst_grams)))
        dtf_X = pd.DataFrame(vectorizer.fit_transform(dtf[column]).todense(), columns=lst_words)

        ## join
        for word in lst_words:
            dtf[word] = dtf_X[word]
        return dtf

    def __add_location(self, data):
        city_data = data.loc[self.loc_tokenize].astype('int')
        max_val = city_data.max()
        if max_val <= 0 or max_val == None:
            return []
        locations = city_data.eq(max_val)
        if max_val > 2:
            locations = locations.ne(city_data.eq(max_val - 1))
        locations = [x for x in locations.keys() if locations[x] == True and data[x] != 0]
        # memisahkan kota dan kabupaten
        for i in range(len(locations)):
            if locations[i] in self.special_loc:
                kota = 'kota ' + locations[i]
                kabupaten = 'kabupaten ' + locations[i]
                kab = 'kab ' + locations[i]
                # locations[i] = kota if data[kota] > data[kabupaten] else kabupaten
                data_kota = data[kota]
                data_kab = data[kabupaten] + data[kab]
                # if data_kota == data_kab and data_kota > 0 and data_kab > 0:
                if data_kota == data_kab:
                    locations[i] = kota
                    locations.append(kabupaten)
                elif data_kota > data_kab:
                    locations[i] = kota
                    if 2 < data_kota == data_kab + 1:
                        locations.append(kabupaten)
                else:
                    locations[i] = kabupaten
                    if 2 < data_kab == data_kota + 1:
                        locations.append(kota)
        return locations
