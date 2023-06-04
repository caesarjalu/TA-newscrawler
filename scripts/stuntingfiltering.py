import joblib


class StuntingFiltering:
    def __init__(self, logger):
        self.logger = logger

    def run(self, df):
        half_texts = df.loc[:, 'text_clean'].apply(self.__cut_to_half)
        df.loc[:, 'is_stunting_program'] = self.__predict(half_texts)
        df = df.drop(['text_clean'], axis=1)
        stunting_news_df = df.loc[df['is_stunting_program'] == 1]
        self.logger.info("Total Stunting Program News in East Java = " + str(len(stunting_news_df)) + " news:")
        for idx in stunting_news_df.index:
            self.logger.info(stunting_news_df['title'][idx])
        return stunting_news_df

    def __cut_to_half(self, text):
        words = text.split()
        # if len(words) < 300:
        #     return text
        half_index = len(words) // 2 + 1  # add 1 to round up if the length of words is odd
        first_half = ' '.join(words[:half_index])
        return first_half

    def __predict(self, data):
        model = joblib.load('../resource/linear_tfidf_mindf_halftext.joblib')
        self.logger.debug("Predicting Stunting Filter...")
        pred = model.predict(data)
        pred_bool = [bool(i) for i in pred]
        return pred_bool
