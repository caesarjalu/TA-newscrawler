from newscrawler import *
from textprocessing import *


def main():
    nc = NewsCrawler()
    news_df = nc.crawl_custom_date(keyword="program stunting jawa timur", start_date=(2022, 12, 1), end_date=(2022, 12, 31), max_results=5)
    df = news_df.loc[:, ['title', 'text']]
    tp = TextProcessing()
    print("Preprocessing...")
    df['text_clean'] = df.apply(tp.preprocessing, axis=1)
    print(df['text_clean'])


if __name__ == '__main__':
    main()
