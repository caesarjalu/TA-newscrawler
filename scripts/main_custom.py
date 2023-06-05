import logging

from newscrawler import *
from textprocessing import *
from stuntingfiltering import *
from firestorehandler import *


def main():
    start_date = (2023, 6, 3)
    end_date = (2023, 6, 4)
    keywords = ["program stunting jawa timur",
                "program stunting jatim",
                "program stunting bangkalan",
                "program stunting banyuwangi",
                "program stunting blitar",
                "program stunting bojonegoro",
                "program stunting bondowoso",
                "program stunting gresik",
                "program stunting jember",
                "program stunting jombang",
                "program stunting kediri",
                "program stunting lamongan",
                "program stunting lumajang",
                "program stunting madiun",
                "program stunting magetan",
                "program stunting malang",
                "program stunting mojokerto",
                "program stunting nganjuk",
                "program stunting ngawi",
                "program stunting pacitan",
                "program stunting pamekasan",
                "program stunting pasuruan",
                "program stunting ponorogo",
                "program stunting probolinggo",
                "program stunting sampang",
                "program stunting sidoarjo",
                "program stunting situbondo",
                "program stunting sumenep",
                "program stunting trenggalek",
                "program stunting tuban",
                "program stunting tulungagung",
                "program stunting batu",
                "program stunting surabaya"]

    logger = logging.getLogger(__name__)  # Create a logger instance
    logger.setLevel(logging.DEBUG)  # Set the logging level to DEBUG
    log_format = '%(asctime)s [%(levelname)s] - %(message)s'
    formatter = logging.Formatter(log_format)  # Create a custom logging format
    # Create a console handler and set the formatter
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    # Create a file handler and set the formatter
    file_handler = logging.FileHandler('../logs/' + str(start_date) + ' - ' + str(end_date) + '.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.propagate = False  # Disable propagation to the root logger
    logger.addHandler(console_handler)  # Add the console handler to the logger
    logger.addHandler(file_handler)  # Add the file handler to the logger

    logger.info("Date: " + str(start_date) + " - " + str(end_date))
    # crawl news
    nc = NewsCrawler(logger, start_date=start_date, end_date=end_date)
    news_df = nc.crawl_news(keywords=keywords)
    if len(news_df.index) == 0:
        return
    # news_df.to_csv('../newsdata/3-4_june_2023_all_news.csv', index=False)  # save to csv
    # pre-process news text and location classification
    tp = TextProcessing(logger)
    processed_df = tp.run(news_df)
    if len(processed_df.index) == 0:
        return
    # filter stunting program news
    sf = StuntingFiltering(logger)
    filtered_df = sf.run(processed_df)
    if len(filtered_df.index) == 0:
        return
    # filtered_df.to_csv('../newsdata/3-4_june_2023_stunting_program_news.csv', index=False)  # save to csv
    # insert data into firestore
    fh = FirestoreHandler(logger, mode="prod")
    fh.insert(filtered_df)


if __name__ == '__main__':
    main()
