import pandas as pd
import logging
from ast import literal_eval

from firestorehandler import *


def main():
    logger = logging.getLogger(__name__)  # Create a logger instance
    logger.setLevel(logging.DEBUG)  # Set the logging level to DEBUG
    log_format = '%(asctime)s [%(levelname)s] - %(message)s'
    formatter = logging.Formatter(log_format)  # Create a custom logging format
    # Create a console handler and set the formatter
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.propagate = False  # Disable propagation to the root logger
    logger.addHandler(console_handler)  # Add the console handler to the logger

    path = '../newsdata/2023-06-05.csv'
    df = pd.read_csv(path, parse_dates=['published_date'],
                     converters={"location": literal_eval})
    print(df.dtypes)
    fh = FirestoreHandler(logger, mode="prod")
    fh.insert(df)


if __name__ == '__main__':
    main()
